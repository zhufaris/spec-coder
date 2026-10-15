import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.spec_coder_checks.affected import (
    build_affected_commands,
    execute_affected_commands,
)


ROOT = Path(__file__).resolve().parents[1]


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

    def test_changed_test_selects_itself_without_full_suite(self):
        commands = self.build("tests/test_worker_heartbeat.py")
        joined = "\n".join(" ".join(command["argv"]) for command in commands)
        self.assertIn("test_worker_heartbeat", joined)
        self.assertNotIn("test_*.py", joined)

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
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                joined = "\n".join(
                    " ".join(command["argv"]) for command in self.build(path)
                )
                for token in expected:
                    self.assertIn(token, joined)
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

    def test_mapper_and_public_docs_select_owned_contract_checks(self):
        cases = {
            "scripts/validate-affected.py": "test_affected_validation",
            "scripts/spec_coder_checks/affected.py": "test_affected_validation",
            "README.md": "test_contracts",
            "INSTALL.md": "test_contracts",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                joined = "\n".join(
                    " ".join(command["argv"]) for command in self.build(path)
                )
                self.assertIn(expected, joined)

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
