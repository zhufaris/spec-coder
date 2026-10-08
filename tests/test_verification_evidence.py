"""Exercise baseline evidence through the installed CLI and real Git workspaces."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "scripts" / "verification-evidence.py"


class VerificationEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Evidence Test")
        (self.repo / "source.py").write_text("value = 1\n")
        self.git("add", "source.py")
        self.git("commit", "-qm", "fixture")
        self.artifact = self.repo / "spec.md"
        self.artifact.write_text("# Active specification\n")
        self.counter = self.repo / "counter.txt"
        self.command = [sys.executable, "-c", "from pathlib import Path; p=Path('counter.txt'); p.write_text(str(int(p.read_text())+1) if p.exists() else '1'); print('BASELINE VISIBLE')"]
        self.context = [
            "--repo", str(self.repo), "--cwd", str(self.repo),
            "--request", "current-request-1", "--artifact", str(self.artifact),
            "--exclude-output", "counter.txt",
            "--toolchain", json.dumps({"python": sys.version}),
            "--dependencies", json.dumps({"installed": "stdlib-only", "external": "none"}),
            "--environment", "{}",
        ]

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True).stdout

    def invoke(self, operation, command=None, context=None):
        return subprocess.run(
            [sys.executable, str(CLI), operation, *(self.context if context is None else context), "--", *(self.command if command is None else command)],
            cwd=self.repo, capture_output=True, text=True,
        )

    def embed(self, record):
        self.artifact.write_text("# Active specification\n\n```spec-coder-verification\n" + json.dumps(record) + "\n```\n")

    def capture(self, command=None):
        result = self.invoke("capture", command=command)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.embed(record)
        return record, result

    def assert_rerun(self, result):
        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "rerun")
        self.assertTrue(payload["reasons"])
        return payload

    def changed_context(self, option, value):
        context = self.context.copy()
        context[context.index(option) + 1] = value
        return context

    def test_unknown_dependency_context_runs_baseline_but_never_reuses_it(self):
        for value in [{}, {"installed": "unknown", "external": "none"}, {"installed": "stdlib-only"}]:
            with self.subTest(value=value):
                context = self.changed_context("--dependencies", json.dumps(value))
                result = self.invoke("capture", context=context)
                payload = self.assert_rerun(result)
                self.assertIn("BASELINE VISIBLE", result.stderr)
                self.embed(payload)
                self.assert_rerun(self.invoke("check", context=context))
        self.assertEqual(self.counter.read_text(), "3")

    def test_unknown_environment_capture_runs_baseline_but_never_reuses_it(self):
        values = ["unknown", "unconfirmed", "unavailable", "?", " Unknown (not inspected) "]
        for count, value in enumerate(values, 1):
            with self.subTest(value=value):
                context = self.changed_context("--environment", json.dumps({"APP_CONFIG": value}))
                result = self.invoke("capture", context=context)
                payload = self.assert_rerun(result)
                self.assertEqual(payload["exit_code"], 0)
                self.assertIn("environment observation is unknown", " ".join(payload["reasons"]))
                self.assertIn("BASELINE VISIBLE", result.stderr)
                self.assertEqual(self.counter.read_text(), str(count))
                self.embed(payload)
                self.assert_rerun(self.invoke("check", context=context))
                self.assertEqual(self.counter.read_text(), str(count), "check must not run the baseline")

    def test_unknown_environment_check_rejects_previously_captured_records(self):
        record, _ = self.capture()
        for value in ["unknown", "unconfirmed", "unavailable", "?", " Unknown (not inspected) "]:
            with self.subTest(value=value):
                environment = {"APP_CONFIG": value}
                # Older captures could declare success despite uncertain environment observations.
                record["context"]["environment"] = environment
                self.embed(record)
                context = self.changed_context("--environment", json.dumps(environment))
                payload = self.assert_rerun(self.invoke("check", context=context))
                self.assertIn("environment observation is unknown", " ".join(payload["reasons"]))
                self.assertEqual(self.counter.read_text(), "1", "check must not run the baseline")

    def test_known_and_empty_environment_observations_are_reusable(self):
        for count, environment in enumerate([{}, {"APP_CONFIG": "production"}, {"APP_CONFIG": ""}], 1):
            with self.subTest(environment=environment):
                context = self.changed_context("--environment", json.dumps(environment))
                result = self.invoke("capture", context=context)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(result.stdout)
                self.assertEqual(record["status"], "captured")
                self.assertEqual(record["exit_code"], 0)
                self.embed(record)
                checked = self.invoke("check", context=context)
                self.assertEqual(checked.returncode, 0, checked.stderr)
                self.assertEqual(json.loads(checked.stdout)["status"], "reusable")
                self.assertEqual(self.counter.read_text(), str(count), "check must not run the baseline")

    def test_malformed_or_incomplete_records_are_never_reusable(self):
        record, _ = self.capture()
        invalid = [None, [], {}, {**record, "context": []},
                   {**record, "observed_at": ""}, {**record, "exit_code": False},
                   {**record, "status": "rerun"}, {**record, "before": []}]
        for missing in record:
            invalid.append({key: value for key, value in record.items() if key != missing})
        for value in invalid:
            with self.subTest(record=value):
                self.embed(value)
                result = self.invoke("check")
                self.assert_rerun(result)
                self.assertNotIn("Traceback", result.stderr)
        self.artifact.write_text("```spec-coder-verification\n{bad json\n```\n")
        self.assert_rerun(self.invoke("check"))
        self.assertEqual(self.counter.read_text(), "1")

    def test_exclusions_cannot_hide_tracked_source_or_broad_paths(self):
        (self.repo / "README.md").write_text("# Ordinary source documentation\n")
        self.git("add", "README.md")
        cases = [
            self.changed_context("--artifact", "README.md"),
            self.changed_context("--artifact", "source.py"),
            self.changed_context("--exclude-output", "source.py"),
            self.changed_context("--exclude-output", "."),
            self.changed_context("--exclude-output", "*.py"),
            self.changed_context("--exclude-output", "../elsewhere"),
            self.changed_context("--exclude-output", ".git/index"),
        ]
        for context in cases:
            with self.subTest(context=context):
                self.counter.unlink(missing_ok=True)
                self.assert_rerun(self.invoke("capture", context=context))
                self.assertFalse(self.counter.exists(), "unsafe input must be rejected before execution")

    def test_tracked_active_artifact_marker_allows_document_only_edits(self):
        self.artifact.write_text("<!-- spec-coder:artifact-v1 spec -->\n# Active spec\n")
        self.git("add", "spec.md")
        record, _ = self.capture()
        self.artifact.write_text("<!-- spec-coder:artifact-v1 spec -->\n" + self.artifact.read_text() + "\nA planning note.\n")
        result = self.invoke("check")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.counter.read_text(), "1")

    def test_failed_interrupted_or_missing_commands_emit_nonreusable_records(self):
        commands = [
            [sys.executable, "-c", "raise SystemExit(7)"],
            [sys.executable, "-c", "import os, signal; os.kill(os.getppid(), signal.SIGINT)"],
            [str(self.repo / "missing-command")],
        ]
        for command in commands:
            with self.subTest(command=command):
                payload = self.assert_rerun(self.invoke("capture", command=command))
                self.assertEqual(payload["version"], 1)
                self.assertNotEqual(payload["exit_code"], 0)
                self.embed(payload)
                self.assert_rerun(self.invoke("check", command=command))
        self.assertFalse(self.counter.exists())

    def test_command_that_changes_inputs_cannot_produce_reusable_evidence(self):
        command = [sys.executable, "-c", "from pathlib import Path; Path('source.py').write_text('changed')"]
        payload = self.assert_rerun(self.invoke("capture", command=command))
        self.assertEqual(payload["exit_code"], 0)
        self.assertIn("workspace inputs changed during baseline execution", payload["reasons"])
        self.embed(payload)
        self.assert_rerun(self.invoke("check", command=command))

    def test_staged_untracked_modes_and_lock_inputs_invalidate(self):
        self.capture()
        (self.repo / "source.py").write_text("staged version\n")
        self.git("add", "source.py")
        (self.repo / "source.py").write_text("value = 1\n")
        self.assert_rerun(self.invoke("check"))
        self.git("reset", "-q", "HEAD", "source.py")
        self.assertEqual(self.invoke("check").returncode, 0)
        for name in ["new_source.py", "package-lock.json"]:
            path = self.repo / name
            path.write_text("new input\n")
            self.assert_rerun(self.invoke("check"))
            path.unlink()
        source = self.repo / "source.py"
        source.chmod(0o755)
        self.assert_rerun(self.invoke("check"))
        source.chmod(0o644)
        self.assertEqual(self.invoke("check").returncode, 0)

    def test_internal_symlink_identity_and_target_content_invalidate(self):
        link = self.repo / "alias.py"
        link.symlink_to("source.py")
        self.capture()
        (self.repo / "same.py").write_text("value = 1\n")
        link.unlink()
        link.symlink_to("same.py")
        self.assert_rerun(self.invoke("check"))

    def test_external_broken_and_submodule_inputs_are_uncertain(self):
        external = Path(self.temp.name + "-external")
        external.write_text("external state")
        self.addCleanup(external.unlink)
        link = self.repo / "external-link"
        for target in [external, self.repo / "missing"]:
            link.symlink_to(target)
            payload = self.assert_rerun(self.invoke("capture"))
            self.assertIn("BASELINE VISIBLE", self.invoke("capture").stderr)
            self.embed(payload)
            self.assert_rerun(self.invoke("check"))
            link.unlink()
        head = self.git("rev-parse", "HEAD").strip()
        self.git("update-index", "--add", "--cacheinfo", "160000," + head + ",module")
        payload = self.assert_rerun(self.invoke("capture"))
        self.embed(payload)
        self.assert_rerun(self.invoke("check"))

    def test_broken_external_parent_symlink_is_unknown_even_when_ignored(self):
        folder = self.repo / "folder"
        folder.mkdir()
        (folder / "source.py").write_text("tracked input")
        self.git("add", "folder/source.py")
        shutil.rmtree(folder)
        folder.symlink_to(self.repo.parent / (self.repo.name + "-missing-external"))
        (self.repo / ".gitignore").write_text("folder\n")
        payload = self.assert_rerun(self.invoke("capture"))
        self.embed(payload)
        self.assert_rerun(self.invoke("check"))

    def test_replaced_physical_repository_is_a_different_workspace(self):
        self.capture()
        old = Path(self.temp.name + "-original")
        self.repo.rename(old)
        self.addCleanup(shutil.rmtree, old)
        shutil.copytree(old, self.repo)
        self.assert_rerun(self.invoke("check"))

    def test_records_have_explicit_identity_and_multiple_commands_are_independent(self):
        first, _ = self.capture()
        second_command = [sys.executable, "-c", "print('second baseline')"]
        second, _ = self.capture(command=second_command)
        self.assertNotEqual(first["record_id"], second["record_id"])
        self.embed(first)
        with self.artifact.open("a") as stream:
            stream.write("\n```spec-coder-verification\n" + json.dumps(second) + "\n```\n")
        for command, record in [(self.command, first), (second_command, second)]:
            result = self.invoke("check", command=command)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(json.loads(result.stdout)["record_id"], record["record_id"])
        self.assertEqual(self.counter.read_text(), "1")

    def test_fenced_examples_and_malformed_unclosed_records_do_not_count(self):
        record, _ = self.capture()
        block = self.artifact.read_text()
        self.artifact.write_text("````markdown\n" + block + "````\n")
        self.assert_rerun(self.invoke("check"))
        self.artifact.write_text(block + "\n```spec-coder-verification\n{")
        self.assert_rerun(self.invoke("check"))
        self.artifact.write_text(block.replace('"version": 1', '"version": 0, "version": 1'))
        self.assert_rerun(self.invoke("check"))

    def test_changed_declared_context_and_command_require_rerun(self):
        self.capture()
        for option, value in [
            ("--request", "resumed-request"),
            ("--toolchain", '{"python":"different-version"}'),
            ("--dependencies", '{"installed":"changed-environment","external":"none"}'),
            ("--environment", '{"FEATURE":"enabled"}'),
        ]:
            with self.subTest(option=option):
                payload = self.assert_rerun(self.invoke("check", context=self.changed_context(option, value)))
                self.assertIn(option[2:], " ".join(payload["reasons"]))
        self.assert_rerun(self.invoke("check", command=[sys.executable, "-c", "print('different')"]))
        self.assertEqual(self.counter.read_text(), "1")

    def test_check_is_read_only_and_document_commands_are_never_executed(self):
        record, _ = self.capture()
        record["context"]["command"] = ["sh", "-c", "touch DO_NOT_RUN"]
        self.embed(record)
        contents = self.artifact.read_bytes()
        index = (self.repo / ".git" / "index").read_bytes()
        status = self.git("status", "--porcelain=v1", "--untracked-files=all")
        self.assert_rerun(self.invoke("check"))
        self.assertEqual(self.artifact.read_bytes(), contents)
        self.assertEqual((self.repo / ".git" / "index").read_bytes(), index)
        self.assertEqual(self.git("status", "--porcelain=v1", "--untracked-files=all"), status)
        self.assertFalse((self.repo / "DO_NOT_RUN").exists())
        self.assertEqual(self.counter.read_text(), "1")

    def test_capture_passes_command_arguments_without_shell_expansion(self):
        command = [sys.executable, "-c", "import sys; print(sys.argv[1])", "$(touch DO_NOT_RUN); $HOME *"]
        _, result = self.capture(command=command)
        self.assertIn("$(touch DO_NOT_RUN); $HOME *", result.stderr)
        self.assertFalse((self.repo / "DO_NOT_RUN").exists())

    def test_unknown_toolchain_and_request_are_not_reusable(self):
        for option, value in [("--toolchain", "{}"), ("--request", "unknown"), ("--dependencies", '{"installed":"unknown (not inspected)","external":"none"}')]:
            with self.subTest(option=option, value=value):
                result = self.invoke("capture", context=self.changed_context(option, value))
                self.assert_rerun(result)
                self.assertIn("BASELINE VISIBLE", result.stderr)

    def test_commented_records_and_inactive_artifact_markers_are_rejected(self):
        record, _ = self.capture()
        block = self.artifact.read_text()
        self.artifact.write_text("<!-- example\n" + block + "\n-->\n")
        self.assert_rerun(self.invoke("check"))
        readme = self.repo / "README.md"
        self.git("add", "source.py")
        for wrapped in ["```markdown\n{marker}\n```", "<!-- example\n{marker}\n-->"]:
            readme.write_text(wrapped.format(marker="<!-- spec-coder:artifact-v1 spec -->"))
            self.git("add", "README.md")
            before = self.counter.read_text()
            self.assert_rerun(self.invoke("capture", context=self.changed_context("--artifact", "README.md")))
            self.assertEqual(self.counter.read_text(), before)

    def test_missing_unreadable_or_malformed_artifacts_do_not_hit(self):
        record, _ = self.capture()
        block = self.artifact.read_text()
        self.artifact.unlink()
        self.assert_rerun(self.invoke("check"))
        self.artifact.write_bytes(b"\xff")
        self.assert_rerun(self.invoke("check"))
        self.artifact.write_text(block + block.replace("spec-coder-verification", "spec-coder-verification extra"))
        self.assert_rerun(self.invoke("check"))
        self.assertEqual(self.counter.read_text(), "1")

    def test_unreadable_files_never_yield_reusable_evidence(self):
        source = self.repo / "source.py"
        source.chmod(0)
        self.addCleanup(source.chmod, 0o644)
        if os.access(source, os.R_OK):
            self.skipTest("current OS user can bypass file read permissions")
        payload = self.assert_rerun(self.invoke("capture"))
        self.assertTrue(any("unreadable" in reason for reason in payload["reasons"]))
        self.embed(payload)
        self.assert_rerun(self.invoke("check"))
        self.assertEqual(self.counter.read_text(), "1")

    def test_unchanged_baseline_is_reused_without_running_command_and_source_change_reruns(self):
        record, capture = self.capture()
        self.assertIn("BASELINE VISIBLE", capture.stderr)
        self.assertEqual(record["version"], 1)
        self.assertEqual(self.counter.read_text(), "1")
        unchanged = self.invoke("check")
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        self.assertEqual(json.loads(unchanged.stdout)["status"], "reusable")
        self.assertEqual(self.counter.read_text(), "1", "check must never execute the supplied or recorded command")
        (self.repo / "source.py").write_text("value = 2\n")
        changed = self.invoke("check")
        self.assertEqual(changed.returncode, 1, changed.stderr)
        self.assertEqual(json.loads(changed.stdout)["status"], "rerun")
        self.assertTrue(json.loads(changed.stdout)["reasons"])
        self.assertEqual(self.counter.read_text(), "1")


if __name__ == "__main__":
    unittest.main()
