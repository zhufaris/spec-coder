"""Exercise published workflow resources through the bundled public CLIs."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_stage_loading import required_links, section

ROOT = Path(__file__).resolve().parents[1]


def template_document(name, kind, resource_root=ROOT):
    """Extract the template's copyable artifact, not a test-owned grammar oracle."""
    text = (resource_root / "references" / name).read_text()
    examples = re.findall(r"(?ms)^```markdown\n(.*?)^```\s*$", text)
    documents = [example for example in examples
                 if f"<!-- spec-coder:artifact-v1 {kind} -->" in example]
    if len(documents) != 1:
        raise AssertionError(f"{name} needs one copyable v1 {kind} skeleton")
    return documents[0]


class PublishedWorkflowIntegration(unittest.TestCase):
    def test_relocated_bundle_capture_reuse_invalidation_and_fresh_delivery(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            bundle = base / "plugin"
            # Marketplace's local source is the distributable repository root.
            marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
            source = ROOT / marketplace["plugins"][0]["source"]["path"]
            tracked = subprocess.run(["git", "ls-files", "-z"], cwd=source,
                                     check=True, capture_output=True, text=True).stdout
            for relative in filter(None, tracked.split("\0")):
                if not (source / relative).is_file():
                    continue
                destination = bundle / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / relative, destination)
            self.assertFalse((bundle / "docs").exists())
            self.assertEqual(json.loads((bundle / ".codex-plugin/plugin.json").read_text())["version"], "0.7.0")
            self.assertEqual(len(list((bundle / "skills").glob("*/SKILL.md"))), 9)
            subprocess.run(["git", "init", "-q"], cwd=bundle, check=True)

            relocated_affected = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(bundle / "scripts/validate-affected.py"),
                    "--repo",
                    str(bundle),
                    "--path",
                    "tests/test_affected_validation.py",
                ],
                cwd=base,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                relocated_affected.returncode,
                0,
                relocated_affected.stdout + relocated_affected.stderr,
            )
            affected_report = json.loads(relocated_affected.stdout)
            self.assertEqual(affected_report["exit_code"], 0)
            self.assertTrue(
                any(
                    "test_affected_validation.py" in command["argv"]
                    for command in affected_report["planned_commands"]
                )
            )

            relocated_snapshot = subprocess.run(
                [
                    sys.executable,
                    str(bundle / "scripts/progress-snapshot.py"),
                    "--ticket-or-axis",
                    "T1",
                    "--worker-handle",
                    "relocated-worker",
                    "--phase",
                    "completed",
                    "--active-command",
                    "none",
                    "--progress-evidence",
                    "relocation check 中文",
                    "--verification-state",
                    "passed",
                    "--blocker",
                    "none",
                ],
                cwd=base,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                relocated_snapshot.returncode,
                0,
                relocated_snapshot.stdout + relocated_snapshot.stderr,
            )
            self.assertEqual(relocated_snapshot.stderr, "")
            self.assertEqual(len(relocated_snapshot.stdout.splitlines()), 1)
            self.assertEqual(
                json.loads(relocated_snapshot.stdout.removeprefix("ProgressSnapshot "))[
                    "worker_handle"
                ],
                "relocated-worker",
            )
            self.assertFalse(
                any(path.name == "__pycache__" for path in bundle.rglob("*")),
                "emitter must not write bytecode into its own bundle",
            )

            target = base / "project"
            target.mkdir()
            def run(arguments):
                return subprocess.run(arguments, cwd=target, capture_output=True, text=True)

            def git(*arguments):
                result = run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                              "-c", "core.hooksPath=/dev/null", *arguments])
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout.strip()

            git("init", "-q")
            (target / ".gitignore").write_text("/docs/\n")
            (target / "status.py").write_text('print("ready")\n')
            shutil.copy2(ROOT / "tests/fixtures/artifacts/verify_status.py", target / "verify.py")
            git("add", ".gitignore", "status.py", "verify.py")
            git("commit", "-qm", "test: prepare disposable status fixture")
            spec = target / "docs/spec.md"
            plan = target / "docs/plan.md"
            command = [sys.executable, "-B", "verify.py"]
            context = ["--repo", str(target), "--cwd", str(target),
                       "--request", "observed-request", "--artifact", str(spec),
                       "--exclude-output", "verification-count.txt",
                       "--toolchain", json.dumps({"python": sys.executable + " " + sys.version}),
                       "--dependencies", '{"installed":"stdlib-only fixture","external":"none"}',
                       "--environment", "{}", "--", *command]
            evidence_cli = [sys.executable, "-B", str(bundle / "scripts/verification-evidence.py")]
            count = lambda: int((target / "verification-count.txt").read_text())

            def evidence(operation, arguments=context):
                result = run([*evidence_cli, operation, *arguments])
                return result, json.loads(result.stdout)

            # The first baseline executes before target artifacts exist.
            captured, record = evidence("capture")
            self.assertEqual(captured.returncode, 0, captured.stderr + captured.stdout)
            self.assertIn("status verification passed", captured.stderr)
            self.assertFalse(spec.exists())
            self.assertEqual(count(), 1)
            spec.parent.mkdir()
            spec_text = template_document("specification-template.md", "spec", bundle)
            def retain(observation):
                spec.write_text(spec_text + "\n```spec-coder-verification\n" +
                                json.dumps(observation) + "\n```\n")

            retain(record)
            checked, report = evidence("check")
            self.assertEqual(checked.returncode, 0, checked.stdout)
            self.assertEqual(report["status"], "reusable")
            self.assertEqual(report["record_id"], record["record_id"])
            self.assertEqual(count(), 1, "planning comparison must not execute baseline")

            (target / "status.py").write_text('print("ready")\n# accepted source change\n')
            rejected, report = evidence("check")
            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(report["status"], "rerun")
            self.assertTrue(report["reasons"])
            self.assertEqual(count(), 1)
            fresh, record = evidence("capture")
            self.assertEqual(fresh.returncode, 0, fresh.stdout)
            retain(record)
            self.assertEqual(count(), 2)

            resumed_context = list(context)
            resumed_context[resumed_context.index("--request") + 1] = "resumed-request"
            rejected, report = evidence("check", resumed_context)
            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(report["status"], "rerun")
            fresh, record = evidence("capture", resumed_context)
            self.assertEqual(fresh.returncode, 0, fresh.stdout)
            retain(record)
            self.assertEqual(count(), 3)

            # Integration and final verification actually execute; no reuse oracle.
            integrated = run(command)
            self.assertEqual(integrated.returncode, 0, integrated.stderr)
            self.assertEqual(count(), 4)
            git("add", "status.py")
            git("commit", "-qm", "test: accept disposable status change")
            commit = git("rev-parse", "HEAD")
            final = run(command)
            self.assertEqual(final.returncode, 0, final.stderr)
            self.assertEqual(count(), 5)
            completed = template_document("ticket-template.md", "plan", bundle).replace("[ ] T1:", "[x] T1:")
            completed = completed.replace("## Final delivery checks", (
                "| Verification commands | " + " ".join(command) + " |\n"
                "| Verification results | Exit 0; " + final.stdout.strip() + " |\n"
                "| Commits | " + commit + " |\n\n## Final delivery checks"))
            plan.write_text(completed)
            result = run([sys.executable, "-B", str(bundle / "scripts/check-artifacts.py"),
                          "--phase", "delivery", "--spec", str(spec), "--plan", str(plan),
                          "--repo", str(target), "--json"])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "passed")
            self.assertEqual(count(), 5, "structural delivery checking never executes recorded commands")

            uncertain_context = list(resumed_context)
            uncertain_context[uncertain_context.index("--dependencies") + 1] = (
                '{"installed":"unknown","external":"none"}')
            uncertain, record = evidence("capture", uncertain_context)
            self.assertEqual(uncertain.returncode, 1)
            self.assertEqual(record["exit_code"], 0, "cache unavailability is not baseline failure")
            self.assertEqual(record["status"], "rerun")
            self.assertTrue(record["reasons"])
            self.assertEqual(count(), 6)

    def test_legacy_artifact_is_explicitly_unsupported(self):
        with tempfile.TemporaryDirectory() as temporary:
            legacy = Path(temporary) / "legacy.md"
            legacy.write_text("# Earlier specification\nUnmarked historical decisions.\n")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/check-artifacts.py"),
                                     "--phase", "spec", "--spec", str(legacy), "--json"],
                                    cwd=temporary, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "unsupported")

    def test_published_templates_pass_draft_cli_and_reject_unfinished_delivery(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            spec = target / "spec.md"
            plan = target / "plan.md"
            spec.write_text(template_document("specification-template.md", "spec"))
            plan.write_text(template_document("ticket-template.md", "plan"))
            for phase, expected_exit in (("spec", 0), ("plan", 0), ("delivery", 1)):
                with self.subTest(phase=phase):
                    result = subprocess.run(
                        [sys.executable, "-B", str(ROOT / "scripts/check-artifacts.py"),
                         "--phase", phase, "--spec", str(spec), "--plan", str(plan),
                         "--repo", str(target), "--json"],
                        cwd=target, capture_output=True, text=True)
                    self.assertEqual(result.returncode, expected_exit, result.stdout + result.stderr)
                    report = json.loads(result.stdout)
                    if phase == "delivery":
                        self.assertIn("delivery.incomplete", {f["rule"] for f in report["findings"]})
                    else:
                        self.assertEqual(report["status"], "passed", report)

    def test_standalone_stages_load_tool_owners_and_name_their_phase_action(self):
        actions = {
            "spec-coder": ("verification-evidence.py", "capture"),
            "plan-coder": ("verification-evidence.py", "check-artifacts.py", "--phase spec", "--phase plan"),
            "tdd-coder": ("fresh",),
            "delivery-coder": ("check-artifacts.py", "--phase delivery", "fresh"),
        }
        for stage, expected in actions.items():
            with self.subTest(stage=stage):
                path = ROOT / "skills" / stage / "SKILL.md"
                links = required_links(path)
                self.assertIn("../../references/verification-contract.md#authority-and-lifecycle", links)
                if stage in {"plan-coder", "delivery-coder"}:
                    self.assertIn("../../references/artifact-format.md#command-interface", links)
                process = section(path.read_text(), "process")
                for action in expected:
                    self.assertIn(action, process)


if __name__ == "__main__":
    unittest.main()
