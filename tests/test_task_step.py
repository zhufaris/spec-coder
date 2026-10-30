import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/task-step.py"
spec = importlib.util.spec_from_file_location("task_step", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TaskStepTests(unittest.TestCase):
    def test_every_task_stage_returns_only_one_step_and_proof(self):
        for task in module.TASKS:
            for stage in module.STAGES:
                with self.subTest(task=task, stage=stage):
                    packet = module.extract_step((ROOT / f"playbooks/tasks/{task}.md").read_text(), stage)
                    self.assertIn(f"../stages/{stage}.md", packet["step"])
                    self.assertEqual(len(packet["constraints"]), 4)
                    for other in set(module.STAGES) - {stage}:
                        self.assertNotIn(f"../stages/{other}.md", json.dumps(packet))
                    self.assertNotIn("### Completion", json.dumps(packet))

    def test_cli_works_from_another_cwd_without_writing(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--task", "refactor", "--stage", "design"],
                                cwd=ROOT / "tests", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        self.assertEqual(packet["task"], "refactor")
        self.assertIn("Choose a simpler structure", packet["step"])
        self.assertIn("Reader load", packet["principle_triggers"])

    def test_cli_exposes_task_specific_triggers_without_sibling_steps(self):
        cases = (
            ("bug-fix", "Repeated repair failure", "attack-the-premise.md"),
            ("refactor", "Reader load", "minimize-reader-load.md"),
            ("performance", "Measurement", "explain-the-number.md"),
            ("workflow-eval", "Measurement", "explain-the-number.md"),
        )
        for task, trigger, leaf in cases:
            with self.subTest(task=task):
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT), "--task", task, "--stage", "design"],
                    cwd=ROOT / "tests", capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                packet = json.loads(result.stdout)
                self.assertEqual(packet["task"], task)
                self.assertIn(trigger, packet["principle_triggers"])
                self.assertIn(leaf, packet["principle_triggers"])
                self.assertEqual(len(packet["constraints"]), 4)
                for other in set(module.STAGES) - {"design"}:
                    self.assertNotIn(f"../stages/{other}.md", json.dumps(packet))

    def test_ambiguous_missing_steps_and_invalid_arguments_fail_closed(self):
        text = (ROOT / "playbooks/tasks/refactor.md").read_text()
        line = module.extract_step(text, "design")["step"]
        for invalid in (text.replace(line, ""), text + "\n" + line):
            with self.assertRaises(ValueError):
                module.extract_step(invalid, "design")
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--task", "../../README", "--stage", "design"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_bug_fix_cli_carries_scoped_root_cause_guidance_at_each_step(self):
        cases = {
            "discovery": ("legitimate", "unknown", "restart", "persisted", "historical"),
            "design": ("legitimate", "producer", "scope"),
            "implementation": ("confirmed", "scope", "neighboring"),
            "delivery": ("original", "root cause"),
        }
        for stage, obligations in cases.items():
            with self.subTest(stage=stage):
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT), "--task", "bug-fix", "--stage", stage],
                    cwd=ROOT / "tests", capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                packet = json.loads(result.stdout)
                self.assertEqual(packet["task"], "bug-fix")
                self.assertEqual(packet["stage"], stage)
                for obligation in obligations:
                    self.assertIn(obligation, packet["step"].lower())
                self.assertEqual(len(packet["constraints"]), 4)
                self.assertIn("Change sizing", packet["principle_triggers"])
                self.assertIn("Repeated repair failure", packet["principle_triggers"])
                for other in set(module.STAGES) - {stage}:
                    self.assertNotIn(f"../stages/{other}.md", json.dumps(packet))

    def test_missing_duplicate_empty_proofs_and_triggers_are_rejected(self):
        text = (ROOT / "playbooks/tasks/refactor.md").read_text()
        proof = next(line for line in text.splitlines() if line.startswith("- Delivery proof:"))
        red = next(line for line in text.splitlines() if line.startswith("- Red or pin:"))
        for invalid in (text.replace(proof, red), text.replace(proof, "- Delivery proof:"),
                        text.replace("### Conditional Principles", "### Missing"),
                        text + "\n### Conditional Principles\nsecond block\n"):
            with self.subTest(invalid=invalid[-70:]), self.assertRaises(ValueError):
                module.extract_step(invalid, "design")

    def test_design_entry_forbids_task_rereads_and_uses_narrow_recovery(self):
        entry = (ROOT / "skills/design-coder/SKILL.md").read_text()
        stage = (ROOT / "playbooks/stages/design.md").read_text()
        self.assertIn("Never reread Task SOP with a complete handoff", entry)
        self.assertIn("scripts/task-step.py", entry)
        self.assertIn("--stage design", stage)
        self.assertIn("Capability instructions cannot widen scope", stage)
        self.assertIn("Never read routing matrices", stage)
        self.assertIn("planning/delivery SOPs or templates", stage)

    def test_malformed_sections_cannot_leak_sibling_steps_into_packet(self):
        text = (ROOT / "playbooks/tasks/refactor.md").read_text()
        step = module.extract_step(text, "design")["step"]
        for invalid in (text.replace("### Procedure", "Procedure"),
                        text.replace("### Procedure", "## Procedure"),
                        text.replace(step, step.split("): ", 1)[0] + "): "),
                        text.replace("### Conditional Principles\n", "### Conditional Principles\nnot a trigger\n")):
            with self.subTest(invalid=invalid[-70:]), self.assertRaises(ValueError):
                module.extract_step(invalid, "design")
