import json
import re
import unittest
from pathlib import Path

from forward_contracts import (
    heartbeat_report_due,
    observe_worker_progress,
    prepare_heartbeat_dispatch,
    validate_progress_snapshot,
)


VALID_SNAPSHOT = {
    "ticket_or_axis": "T1",
    "worker_handle": "worker-1",
    "phase": "working",
    "active_command": "python -m unittest tests.test_worker_heartbeat",
    "progress_evidence": "added the focused heartbeat validation test",
    "verification_state": "running",
    "blocker": "none",
    "observed_at": "2026-10-07T10:00:00Z",
}

WORKER_BRIEF = Path(__file__).resolve().parents[1] / "references" / "worker-brief-template.md"


class ProgressSnapshotValidationTests(unittest.TestCase):
    def test_worker_brief_exposes_one_canonical_json_envelope(self) -> None:
        text = WORKER_BRIEF.read_text()
        matches = re.findall(r"(?m)^ProgressSnapshot (\{.*\})$", text)
        self.assertEqual(len(matches), 1)
        template = json.loads(matches[0])
        self.assertEqual(set(template), set(VALID_SNAPSHOT))
        candidate = {**template, **VALID_SNAPSHOT}
        self.assertEqual(dict(validate_progress_snapshot(candidate)), VALID_SNAPSHOT)
        self.assertIn("replace every", text.lower())
        self.assertIn("send-time", text.lower())
        self.assertIn("do not copy", text.lower())
        self.assertIn("terminal snapshot", text.lower())
        self.assertIn("phase to `completed`", text.lower())
        self.assertIn("never `handoff`", text.lower())

    def test_accepts_complete_immutable_progress_fact(self) -> None:
        original = dict(VALID_SNAPSHOT)

        validated = validate_progress_snapshot(original)

        self.assertEqual(validated, VALID_SNAPSHOT)
        self.assertIsNot(validated, original)
        self.assertEqual(original, VALID_SNAPSHOT)
        with self.assertRaises(TypeError):
            validated["phase"] = "blocked"

    def test_rejects_missing_extra_or_empty_fields(self) -> None:
        missing = dict(VALID_SNAPSHOT)
        missing.pop("blocker")
        extra = {**VALID_SNAPSHOT, "percent_complete": 50}
        empty = {**VALID_SNAPSHOT, "progress_evidence": "  "}

        for candidate in (missing, extra, empty):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    validate_progress_snapshot(candidate)

    def test_rejects_unknown_states_and_malformed_observation_time(self) -> None:
        candidates = (
            {**VALID_SNAPSHOT, "phase": "stalled"},
            {**VALID_SNAPSHOT, "verification_state": "successful-ish"},
            {**VALID_SNAPSHOT, "observed_at": "sometime later"},
            {**VALID_SNAPSHOT, "observed_at": "2026-10-07T10:00:00"},
        )

        for candidate in candidates:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    validate_progress_snapshot(candidate)

    def test_completed_snapshot_requires_terminal_verification_state(self) -> None:
        for verification_state in ("not-started", "running"):
            with self.subTest(verification_state=verification_state):
                with self.assertRaises(ValueError):
                    validate_progress_snapshot(
                        {
                            **VALID_SNAPSHOT,
                            "phase": "completed",
                            "verification_state": verification_state,
                        }
                    )
        for verification_state in ("passed", "failed"):
            candidate = {
                **VALID_SNAPSHOT,
                "phase": "completed",
                "verification_state": verification_state,
            }
            self.assertEqual(dict(validate_progress_snapshot(candidate)), candidate)


class HeartbeatScheduleTests(unittest.TestCase):
    def test_periodic_report_becomes_due_in_the_approved_window(self) -> None:
        self.assertFalse(heartbeat_report_due(seconds_since_report=44))
        self.assertTrue(heartbeat_report_due(seconds_since_report=45))
        self.assertTrue(heartbeat_report_due(seconds_since_report=60))

    def test_transition_command_boundaries_and_terminal_reports_are_immediate(self) -> None:
        self.assertTrue(
            heartbeat_report_due(seconds_since_report=1, phase_changed=True)
        )
        for command_boundary in ("before-command", "after-command"):
            with self.subTest(command_boundary=command_boundary):
                self.assertTrue(
                    heartbeat_report_due(
                        seconds_since_report=1,
                        command_boundary=command_boundary,
                    )
                )
        with self.assertRaises(ValueError):
            heartbeat_report_due(
                seconds_since_report=1,
                command_boundary="during-command",
            )
        self.assertTrue(heartbeat_report_due(seconds_since_report=1, terminal=True))

    def test_start_is_immediate_and_negative_elapsed_time_is_invalid(self) -> None:
        self.assertTrue(heartbeat_report_due(seconds_since_report=0, starting=True))
        with self.assertRaises(ValueError):
            heartbeat_report_due(seconds_since_report=-1)


class WorkerProgressObservationTests(unittest.TestCase):
    def test_valid_snapshot_updates_observation_without_execution_authority(self) -> None:
        observation = observe_worker_progress(
            previous_snapshot=None,
            incoming_snapshot=VALID_SNAPSHOT,
            heartbeat_capability=True,
            wait_timed_out=False,
        )

        self.assertEqual(observation["status"], "observed")
        self.assertEqual(observation["snapshot"], VALID_SNAPSHOT)
        self.assertEqual(observation["execution_effect"], "none")
        self.assertEqual(observation["completion_authority"], "main-only")
        with self.assertRaises(TypeError):
            observation["snapshot"]["phase"] = "blocked"

    def test_timeout_is_only_overdue_and_preserves_last_valid_snapshot(self) -> None:
        observation = observe_worker_progress(
            previous_snapshot=VALID_SNAPSHOT,
            incoming_snapshot=None,
            heartbeat_capability=True,
            wait_timed_out=True,
        )

        self.assertEqual(observation["status"], "heartbeat-overdue")
        self.assertEqual(observation["snapshot"], VALID_SNAPSHOT)
        self.assertEqual(observation["execution_effect"], "none")
        self.assertNotIn(
            observation["status"],
            {"failed", "blocked", "stalled", "interrupt", "takeover"},
        )

    def test_ordinary_no_message_window_is_not_overdue(self) -> None:
        observation = observe_worker_progress(
            previous_snapshot=VALID_SNAPSHOT,
            incoming_snapshot=None,
            heartbeat_capability=True,
            wait_timed_out=False,
        )

        self.assertEqual(observation["status"], "awaiting-heartbeat")
        self.assertEqual(observation["snapshot"], VALID_SNAPSHOT)
        self.assertEqual(observation["execution_effect"], "none")

    def test_missed_interval_is_overdue_without_execution_authority(self) -> None:
        observation = observe_worker_progress(
            previous_snapshot=VALID_SNAPSHOT,
            incoming_snapshot=None,
            heartbeat_capability=True,
            wait_timed_out=False,
            interval_missed=True,
        )

        self.assertEqual(observation["status"], "heartbeat-overdue")
        self.assertEqual(observation["snapshot"], VALID_SNAPSHOT)
        self.assertEqual(observation["execution_effect"], "none")

    def test_missing_capability_is_explicit_and_preserves_delegation(self) -> None:
        observation = observe_worker_progress(
            previous_snapshot=None,
            incoming_snapshot=None,
            heartbeat_capability=False,
            wait_timed_out=False,
        )

        self.assertEqual(observation["status"], "heartbeat-capability-unavailable")
        self.assertEqual(observation["delegation_effect"], "preserve")
        self.assertEqual(observation["execution_effect"], "none")

    def test_invalid_snapshot_does_not_mutate_previous_observation(self) -> None:
        previous = dict(VALID_SNAPSHOT)
        invalid = {**VALID_SNAPSHOT, "phase": "stalled"}

        with self.assertRaises(ValueError):
            observe_worker_progress(
                previous_snapshot=previous,
                incoming_snapshot=invalid,
                heartbeat_capability=True,
                wait_timed_out=False,
            )

        self.assertEqual(previous, VALID_SNAPSHOT)


class HeartbeatDispatchTests(unittest.TestCase):
    def test_capability_is_recorded_before_or_at_dispatch(self) -> None:
        for dispatch_timing in ("before-dispatch", "at-dispatch"):
            with self.subTest(dispatch_timing=dispatch_timing):
                self.assertEqual(
                    prepare_heartbeat_dispatch(
                        heartbeat_capability=True,
                        dispatch_timing=dispatch_timing,
                    ),
                    "heartbeat-ready",
                )
                self.assertEqual(
                    prepare_heartbeat_dispatch(
                        heartbeat_capability=False,
                        dispatch_timing=dispatch_timing,
                    ),
                    "heartbeat-capability-unavailable",
                )

    def test_capability_cannot_be_recorded_only_after_dispatch(self) -> None:
        with self.assertRaises(ValueError):
            prepare_heartbeat_dispatch(
                heartbeat_capability=False,
                dispatch_timing="after-dispatch",
            )


if __name__ == "__main__":
    unittest.main()
