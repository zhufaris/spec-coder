import ast
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.spec_coder_checks.affected import (
    build_affected_commands,
    execute_affected_commands,
)


ROOT = Path(__file__).resolve().parents[1]


def _imports_forward_contracts(source):
    """Return whether source contains a direct import of forward_contracts."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        (
            isinstance(node, ast.Import)
            and any(alias.name == "forward_contracts" for alias in node.names)
        )
        or (
            isinstance(node, ast.ImportFrom)
            and node.module == "forward_contracts"
        )
        for node in ast.walk(tree)
    )


def _is_scenarios_fixture_path(node):
    if isinstance(node, ast.Constant):
        return node.value == "tests/fixtures/scenarios.md"
    parts = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not isinstance(node.right, ast.Constant) or not isinstance(
            node.right.value, str
        ):
            return False
        parts.append(node.right.value)
        node = node.left
    return isinstance(node, ast.Name) and node.id == "ROOT" and tuple(
        reversed(parts)
    ) == ("tests", "fixtures", "scenarios.md")


def _reads_scenarios_fixture(source):
    """Return whether source reads the narrow scenarios fixture through supported shapes."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in {"read", "read_text"}
            and len(node.args) == 1
            and _is_scenarios_fixture_path(node.args[0])
        ):
            return True
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "read_text"
            and _is_scenarios_fixture_path(node.func.value)
        ):
            return True
    return False


class AffectedValidationTests(unittest.TestCase):
    def build(self, *paths):
        return build_affected_commands(
            repo=ROOT,
            paths=paths,
            python_bin="/observed/python3",
            validator="/observed/quick_validate.py",
        )

    def test_narrow_skill_change_selects_contract_tests_validator_and_diff(self):
        commands = self.build("skills/tdd-coder/SKILL.md")
        joined = "\n".join(" ".join(command["argv"]) for command in commands)
        self.assertIn("test_contracts", joined)
        self.assertIn("test_stage_loading", joined)
        self.assertIn("test_implement_spec_runtime", joined)
        self.assertIn("/observed/quick_validate.py skills/tdd-coder", joined)
        self.assertEqual(commands[-1]["argv"], ("git", "diff", "--check"))

    def test_shared_routing_change_expands_deterministically(self):
        commands = self.build("references/subagent-routing-contract.md")
        joined = "\n".join(" ".join(command["argv"]) for command in commands)
        for module in (
            "test_default_subagent_execution",
            "test_parallel_request_scenarios",
            "test_implement_spec_runtime",
        ):
            self.assertIn(module, joined)
        for skill in ("spec-coder", "tdd-coder", "delivery-coder"):
            self.assertIn(f"/observed/quick_validate.py skills/{skill}", joined)
        keys = [(command["argv"], command["cwd"]) for command in commands]
        self.assertEqual(len(keys), len(set(keys)))

    def test_worker_brief_owner_maps_to_all_direct_consumers(self):
        commands = self.build("references/worker-brief-template.md")
        joined = "\n".join(" ".join(command["argv"]) for command in commands)
        for module in (
            "test_worker_heartbeat",
            "test_default_subagent_execution",
            "test_implement_spec_runtime",
            "test_stage_loading",
        ):
            self.assertIn(module, joined)
        self.assertEqual(commands[-1]["argv"], ("git", "diff", "--check"))

    def test_changed_test_selects_itself_without_full_suite(self):
        commands = self.build("tests/test_worker_heartbeat.py")
        joined = "\n".join(" ".join(command["argv"]) for command in commands)
        self.assertIn("test_worker_heartbeat", joined)
        self.assertNotIn("test_*.py", joined)

    def test_forward_contracts_maps_exactly_to_static_importers(self):
        commands = self.build("tests/forward_contracts.py")
        selected = {
            Path(command["argv"][-1]).stem
            for command in commands
            if command["kind"] == "unittest"
        }
        importers = {
            path.stem
            for path in (ROOT / "tests").glob("test_*.py")
            if _imports_forward_contracts(path.read_text())
        }
        self.assertEqual(selected, importers)
        self.assertEqual(commands[-1]["argv"], ("git", "diff", "--check"))

    def test_scenarios_fixture_maps_to_its_two_consumers(self):
        commands = self.build("tests/fixtures/scenarios.md")
        selected = {
            Path(command["argv"][-1]).stem
            for command in commands
            if command["kind"] == "unittest"
        }
        consumers = {
            path.stem
            for path in (ROOT / "tests").glob("test_*.py")
            if path.name != "test_affected_validation.py"
            and _reads_scenarios_fixture(path.read_text())
        }
        self.assertEqual(selected, consumers)
        self.assertEqual(commands[-1]["argv"], ("git", "diff", "--check"))

    def test_static_consumer_detection_covers_supported_source_shapes(self):
        self.assertTrue(_imports_forward_contracts("import forward_contracts\n"))
        self.assertTrue(
            _imports_forward_contracts("from forward_contracts import READY\n")
        )
        self.assertFalse(_imports_forward_contracts("name = 'forward_contracts'\n"))
        self.assertTrue(
            _reads_scenarios_fixture(
                'content = read("tests/fixtures/scenarios.md")\n'
            )
        )
        self.assertTrue(
            _reads_scenarios_fixture(
                'content = read_text(ROOT / "tests" / "fixtures" / "scenarios.md")\n'
            )
        )
        self.assertFalse(
            _reads_scenarios_fixture(
                'commands = self.build("tests/fixtures/scenarios.md")\n'
            )
        )

    def test_paths_must_exist_inside_repository(self):
        for path in ("../outside.py", "/etc/passwd", "missing.py"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.build(path)

    def test_execution_uses_argument_vectors_and_stops_on_failure(self):
        commands = self.build("tests/test_worker_heartbeat.py")
        calls = []

        def runner(argv, **kwargs):
            calls.append((tuple(argv), kwargs))
            code = 7 if len(calls) == 2 else 0
            return subprocess.CompletedProcess(argv, code)

        result = execute_affected_commands(commands, runner=runner)
        self.assertEqual(result["exit_code"], 7)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(result["planned_commands"]), len(commands))
        self.assertEqual(len(result["results"]), 2)
        for argv, kwargs in calls:
            self.assertIsInstance(argv, tuple)
            self.assertFalse(kwargs.get("shell", False))

    def test_public_cli_is_bundled(self):
        self.assertTrue((ROOT / "scripts/validate-affected.py").is_file())

    def test_validator_runs_through_selected_python(self):
        commands = self.build("skills/tdd-coder/SKILL.md")
        validator = next(
            command for command in commands if command["kind"] == "skill-validator"
        )
        self.assertEqual(
            validator["argv"][:2],
            ("/observed/python3", "/observed/quick_validate.py"),
        )

    def test_shared_owner_groups_select_proportional_checks(self):
        mapper = (ROOT / "scripts" / "spec_coder_checks" / "affected.py").read_text()
        self.assertIn('"references/task-playbook-contract.md"', mapper)
        cases = {
            "references/workflow-contract.md": (
                "test_runtime_envelope",
                "test_stage_loading",
            ),
            "references/ticket-template.md": (
                "test_implement_spec_planning",
                "test_workflow_tool_integration",
            ),
            "references/verification-contract.md": ("test_verification_evidence",),
            "references/domain-design-contract.md": ("test_contracts",),
            "references/approval-review-contract.md": (
                "test_human_review_options",
                "test_forward_scenarios",
            ),
            "references/upstream-compatibility.md": (
                "test_contracts",
                "test_autonomous_workflow",
                "test_stage_loading",
            ),
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                joined = "\n".join(
                    " ".join(command["argv"]) for command in self.build(path)
                )
                for token in expected:
                    self.assertIn(token, joined)
                self.assertNotIn("test_*.py", joined)

    def test_task_playbook_owner_paths_select_contract_checks(self):
        paths = (
            "references/task-playbook-contract.md",
            "tests/task_playbook_contracts.py",
            "tests/fixtures/task-playbook-scenarios.md",
            "THIRD_PARTY_NOTICES.md",
        )
        if not all((ROOT / path).is_file() for path in paths):
            self.skipTest("relocated legacy bundle omits T1 task-playbook owner paths")
        for path in paths:
            with self.subTest(path=path):
                joined = "\n".join(
                    " ".join(command["argv"]) for command in self.build(path)
                )
                self.assertIn("test_task_playbooks", joined)
                self.assertNotIn("test_*.py", joined)

    def test_each_public_skill_selects_its_validator(self):
        for stage in (
            "spec-coder",
            "grill-coder",
            "design-coder",
            "plan-coder",
            "tdd-coder",
            "delivery-coder",
            "setup-coder",
            "show-me",
            "using-git-worktrees",
        ):
            with self.subTest(stage=stage):
                commands = self.build(f"skills/{stage}/SKILL.md")
                validators = [
                    command for command in commands
                    if command["kind"] == "skill-validator"
                ]
                self.assertEqual(len(validators), 1)
                self.assertEqual(validators[0]["argv"][-1], f"skills/{stage}")

    def test_worktree_skill_routes_legacy_contract_and_policy_checks(self):
        joined = "\n".join(
            " ".join(command["argv"])
            for command in self.build("skills/using-git-worktrees/SKILL.md")
        )
        for module in (
            "test_contracts",
            "test_exact_base_worktree",
            "test_workspace_policy",
        ):
            with self.subTest(module=module):
                self.assertIn(module, joined)

    def test_mapper_and_public_docs_select_owned_contract_checks(self):
        cases = {
            "scripts/validate-affected.py": "test_affected_validation",
            "scripts/spec_coder_checks/affected.py": "test_affected_validation",
            "tests/design_contracts.py": "test_design_governance",
            "README.md": "test_contracts",
            "INSTALL.md": "test_contracts",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                joined = "\n".join(
                    " ".join(command["argv"]) for command in self.build(path)
                )
                self.assertIn(expected, joined)

    def test_setup_contract_and_generated_snippet_select_setup_consumers(self):
        for path in (
            "references/setup-contract.md",
            "assets/agents-snippet.md",
        ):
            with self.subTest(path=path):
                joined = "\n".join(
                    " ".join(command["argv"]) for command in self.build(path)
                )
                self.assertIn("test_contracts", joined)
                self.assertIn("test_forward_scenarios", joined)
                self.assertNotIn("test_*.py", joined)

    def test_progress_snapshot_bundle_selects_its_focused_suite(self):
        for path in (
            "scripts/progress-snapshot.py",
            "scripts/spec_coder_checks/progress.py",
            "tests/test_progress_snapshot.py",
        ):
            with self.subTest(path=path):
                joined = "\n".join(
                    " ".join(command["argv"]) for command in self.build(path)
                )
                self.assertIn("test_progress_snapshot", joined)

    def test_unmapped_existing_path_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            source = repository / "src/app.py"
            source.parent.mkdir()
            source.write_text("print('unmapped')\n")
            with self.assertRaisesRegex(ValueError, "unmapped affected path"):
                build_affected_commands(
                    repo=repository,
                    paths=("src/app.py",),
                    python_bin="/observed/python3",
                    validator="/observed/quick_validate.py",
                )


if __name__ == "__main__":
    unittest.main()
