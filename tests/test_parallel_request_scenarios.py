"""Executable prompt-contract scenarios, not a Host scheduler implementation."""

import unittest

from forward_contracts import (
    decide_parallel_dispatch, integrate_wave_result, select_planned_wave_batch,
)


class ParallelRequestScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.tickets = [
            {"id": ticket_id, "mode": "delegate", "dependencies": set(), "conflicts": set()}
            for ticket_id in ("T1", "T2", "T3")
        ]
        self.waves = (("T1", "T2"), ("T3",))

    def select(self, **overrides):
        options = dict(
            completed_ids=set(),
            host_available_slots=4,
            isolated=False,
            parallel_request="preferred",
        )
        options.update(overrides)
        batch = select_planned_wave_batch(self.tickets, self.waves, **options)
        current = next((wave for wave in self.waves if set(wave) - options["completed_ids"]), ())
        eligible = [ticket for ticket in self.tickets
                    if ticket["id"] in current and ticket["id"] not in options["completed_ids"]
                    and ticket.get("dependency_ready", True)
                    and ticket.get("delegation_eligible", True)]
        mode, reason = decide_parallel_dispatch(
            eligible_count=len(eligible),
            mutation_required=any(not ticket.get("read_only", False) for ticket in eligible),
            host_available_slots=options["host_available_slots"],
            isolated=options["isolated"],
            parallel_request=options["parallel_request"],
            isolation_blocker=options.get("isolation_blocker"),
        )
        return batch, {"mode": mode, "reason": reason}

    def test_mutation_prepares_isolation_before_dispatch_then_runs_current_wave(self):
        batch, evidence = self.select()
        self.assertEqual(batch, ())
        self.assertEqual(evidence["mode"], "prepare-isolation")
        batch, evidence = self.select(isolated=True)
        self.assertEqual(batch, (("T1", "delegate"), ("T2", "delegate")))
        self.assertEqual(evidence["mode"], "parallel")

    def test_unavailable_isolation_explains_ordinary_serial_fallback(self):
        batch, evidence = self.select(isolation_blocker="native allocation denied by workspace constraint")
        self.assertEqual(batch, (("T1", "delegate"),))
        self.assertEqual(evidence["mode"], "serial")
        self.assertIn("native allocation denied", evidence["reason"])

    def test_parallel_only_unavailable_isolation_blocks_instead_of_serializing(self):
        batch, evidence = self.select(
            parallel_request="required", isolation_blocker="no permitted isolated location"
        )
        self.assertEqual(batch, ())
        self.assertEqual(evidence["mode"], "block")
        self.assertIn("no permitted isolated location", evidence["reason"])

    def test_strict_parallel_waits_for_temporary_slots_then_dispatches(self):
        for slots in (0, 1):
            with self.subTest(slots=slots):
                batch, evidence = self.select(
                    parallel_request="required", host_available_slots=slots, isolated=True
                )
                self.assertEqual(batch, ())
                self.assertEqual(evidence["mode"], "wait")
        batch, evidence = self.select(parallel_request="required", isolated=True, host_available_slots=2)
        self.assertEqual(len(batch), 2)
        self.assertEqual(evidence["mode"], "parallel")

    def test_ordinary_request_reports_capacity_shrink_and_zero_slots_wait(self):
        batch, evidence = self.select(host_available_slots=1)
        self.assertEqual(batch, (("T1", "delegate"),))
        self.assertEqual(evidence["mode"], "serial")
        self.assertIn("capacity", evidence["reason"])
        batch, evidence = self.select(host_available_slots=0)
        self.assertEqual(batch, ())
        self.assertEqual(evidence["mode"], "wait")

    def test_read_only_workers_parallelize_without_mutation_isolation(self):
        for ticket in self.tickets:
            ticket["read_only"] = True
        batch, evidence = self.select(parallel_request="required")
        self.assertEqual(batch, (("T1", "delegate"), ("T2", "delegate")))
        self.assertEqual(evidence["mode"], "parallel")

    def test_one_mutating_worker_still_requires_isolation_in_a_mixed_batch(self):
        self.tickets[0]["read_only"] = True
        batch, evidence = self.select()
        self.assertEqual(batch, ())
        self.assertEqual(evidence["mode"], "prepare-isolation")

    def test_strict_request_does_not_pull_later_wave_to_replace_singleton(self):
        batch, evidence = self.select(completed_ids={"T1"}, isolated=True, parallel_request="required")
        self.assertEqual(batch, ())
        self.assertEqual(evidence["mode"], "block")
        self.assertIn("current planned wave", evidence["reason"])

    def test_not_ready_or_ineligible_members_do_not_make_parallel_batch(self):
        for field in ("dependency_ready", "delegation_eligible"):
            with self.subTest(field=field):
                self.tickets[1][field] = False
                batch, evidence = self.select(isolated=True, parallel_request="required")
                self.assertEqual(batch, ())
                self.assertEqual(evidence["mode"], "block")
                del self.tickets[1][field]

    def test_conflicts_and_oversized_waves_remain_invalid(self):
        self.tickets[0]["conflicts"] = {"T2"}
        with self.assertRaises(ValueError):
            self.select(isolated=True)
        self.tickets[0]["conflicts"] = set()
        self.tickets.extend({"id": name, "mode": "delegate"} for name in ("T4", "T5"))
        self.waves = (("T1", "T2", "T3", "T4", "T5"),)
        with self.assertRaises(ValueError):
            self.select(isolated=True)

    def test_unknown_request_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            self.select(parallel_request="parallel-ish")
        with self.assertRaises(ValueError):
            decide_parallel_dispatch(
                eligible_count=2, mutation_required=True, host_available_slots=2,
                isolated=True, parallel_request="parallel-ish",
            )

    def test_rejected_results_reassess_request_before_any_serial_recovery(self):
        common = dict(
            base_matches=True, accepted_sibling_advancement=False,
            ownership_disjoint=True, transfer_clean=True,
            diff_explained=True, verification_passes=True,
        )
        for request in ("preferred", "required"):
            self.assertEqual(integrate_wave_result(**common, parallel_request=request), "accept")
            for failed_field in ("base_matches", "ownership_disjoint", "transfer_clean", "diff_explained", "verification_passes"):
                with self.subTest(request=request, failed_field=failed_field):
                    failed = {**common, failed_field: False}
                    self.assertEqual(
                        integrate_wave_result(**failed, parallel_request=request),
                        "reassess-parallel",
                    )
            batch, evidence = self.select(parallel_request=request, isolation_blocker="recovery isolation unavailable")
            self.assertEqual(evidence["mode"], "block" if request == "required" else "serial")
            self.assertEqual(bool(batch), request == "preferred")


if __name__ == "__main__":
    unittest.main()
