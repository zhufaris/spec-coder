import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.spec_coder_checks.progress import build_progress_snapshot


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "progress-snapshot.py"


class ProgressSnapshotPolicyTests(unittest.TestCase):
    def test_fixed_clock_builds_existing_eight_field_value(self) -> None:
        fixed = datetime(2026, 10, 15, 12, 34, 56, tzinfo=timezone.utc)
        snapshot = build_progress_snapshot(
            ticket_or_axis="T1",
            worker_handle="/root/worker",
            phase="working",
            active_command="none",
            progress_evidence="quoted \"value\" and 中文",
            verification_state="running",
            blocker="none",
            clock=lambda: fixed,
        )
        self.assertEqual(
            tuple(snapshot),
            (
                "ticket_or_axis",
                "worker_handle",
                "phase",
                "active_command",
                "progress_evidence",
                "verification_state",
                "blocker",
                "observed_at",
            ),
        )
        self.assertEqual(snapshot["observed_at"], "2026-10-15T12:34:56Z")
        with self.assertRaises(TypeError):
            snapshot["phase"] = "blocked"

    def test_builder_rejects_blank_fields_invalid_states_and_naive_clock(self) -> None:
        arguments = {
            "ticket_or_axis": "T1",
            "worker_handle": "/root/worker",
            "phase": "working",
            "active_command": "none",
            "progress_evidence": "evidence",
            "verification_state": "running",
            "blocker": "none",
        }
        for overrides in (
            {"blocker": "  "},
            {"phase": "handoff"},
            {"verification_state": "successful-ish"},
            {"phase": "completed", "verification_state": "running"},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                build_progress_snapshot(**{**arguments, **overrides})
        with self.assertRaises(ValueError):
            build_progress_snapshot(
                **arguments, clock=lambda: datetime(2026, 10, 15, 12, 34, 56)
            )


class ProgressSnapshotCLITests(unittest.TestCase):
    def command(self, *extra: str) -> list[str]:
        return [
            sys.executable,
            str(CLI),
            "--ticket-or-axis",
            "T1",
            "--worker-handle",
            "/root/worker",
            "--phase",
            "working",
            "--active-command",
            "none",
            "--progress-evidence",
            "line 1\nline 2 中文",
            "--verification-state",
            "running",
            "--blocker",
            "none",
            *extra,
        ]

    def test_cli_emits_one_compact_canonical_line(self) -> None:
        before = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as temporary:
            sentinel = Path(temporary) / "user-owned.txt"
            sentinel.write_text("preserve me\n")
            before_files = {path.name: path.read_bytes() for path in Path(temporary).iterdir()}
            result = subprocess.run(
                self.command(), cwd=temporary, capture_output=True, text=True
            )
            after_files = {path.name: path.read_bytes() for path in Path(temporary).iterdir()}
        after = datetime.now(timezone.utc)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(len(result.stdout.splitlines()), 1)
        prefix = "ProgressSnapshot "
        self.assertTrue(result.stdout.startswith(prefix))
        payload = json.loads(result.stdout[len(prefix):])
        self.assertEqual(payload["ticket_or_axis"], "T1")
        self.assertEqual(payload["progress_evidence"], "line 1\nline 2 中文")
        observed = datetime.fromisoformat(
            payload["observed_at"].replace("Z", "+00:00")
        )
        self.assertLessEqual(before, observed)
        self.assertLessEqual(observed, after)
        self.assertEqual(before_files, after_files)

    def test_invalid_terminal_and_observed_at_override_emit_no_stdout(self) -> None:
        completed_running = self.command()
        completed_running[completed_running.index("working")] = "completed"
        for command in (
            completed_running,
            [*self.command(), "--observed-at", "2026-10-15T00:00:00Z"],
        ):
            with self.subTest(command=command):
                result = subprocess.run(
                    command, cwd="/tmp", capture_output=True, text=True
                )
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotEqual(result.stderr, "")

    def test_cli_escapes_controls_and_preserves_unicode(self) -> None:
        result = subprocess.run(
            self.command("--progress-evidence", "tab\tcontrol 中文"),
            cwd="/tmp",
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertIn("\\t", result.stdout)
        self.assertEqual(
            json.loads(result.stdout.removeprefix("ProgressSnapshot "))[
                "progress_evidence"
            ],
            "tab\tcontrol 中文",
        )


if __name__ == "__main__":
    unittest.main()
