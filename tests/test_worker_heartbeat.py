import unittest

from forward_contracts import (
    heartbeat_report_due,
    observe_worker_progress,
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


class ProgressSnapshotValidationTests(unittest.TestCase):
    def test_accepts_complete_immutable_progress_fact(self) -> None:
        original = dict(VALID_SNAPSHOT)

        validated = validate_progress_snapshot(original)

        self.assertEqual(validated, VALID_SNAPSHOT)
        self.assertIsNot(validated, original)
        self.assertEqual(original, VALID_SNAPSHOT)

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


class HeartbeatScheduleTests(unittest.TestCase):
    def test_periodic_report_becomes_due_in_the_approved_window(self) -> None:
        self.assertFalse(heartbeat_report_due(seconds_since_report=44))
        self.assertTrue(heartbeat_report_due(seconds_since_report=45))
        self.assertTrue(heartbeat_report_due(seconds_since_report=60))

    def test_transition_command_boundary_and_terminal_reports_are_immediate(self) -> None:
        self.assertTrue(
            heartbeat_report_due(seconds_since_report=1, phase_changed=True)
        )
        self.assertTrue(
            heartbeat_report_due(seconds_since_report=1, command_boundary=True)
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


if __name__ == "__main__":
    unittest.main()
