import subprocess
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


if __name__ == "__main__":
    unittest.main()
