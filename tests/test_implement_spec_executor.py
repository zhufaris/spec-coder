import unittest
from pathlib import Path
from test_stage_loading import skill_text

from forward_contracts import (
    enter_implement_spec_executor,
    integrate_wave_result,
    recover_executor_progress,
    select_executor_workspace,
    select_planned_wave_batch,
)


ROOT = Path(__file__).resolve().parents[1]


class UnifiedImplementSpecExecutorTests(unittest.TestCase):
    def ticket(self, ticket_id, *, dependencies=(), read_only=False):
        return {
            "id": ticket_id,
            "mode": "delegate",
            "dependencies": set(dependencies),
            "conflicts": set(),
            "read_only": read_only,
        }

    def test_singleton_and_multi_ticket_plans_enter_the_same_executor(self):
        self.assertEqual(
            enter_implement_spec_executor(gate3_approved=True, ticket_count=1),
            "native-implement-spec",
        )
        self.assertEqual(
            enter_implement_spec_executor(gate3_approved=True, ticket_count=8),
            "native-implement-spec",
        )

    def test_executor_requires_gate_three_and_a_nonempty_task_graph(self):
        self.assertEqual(
            enter_implement_spec_executor(gate3_approved=False, ticket_count=1),
            "stop-gate-3",
        )
        self.assertEqual(
            enter_implement_spec_executor(gate3_approved=True, ticket_count=0),
            "stop-empty-task-graph",
        )

    def test_workspace_reuses_safe_serial_and_reopens_for_unmet_isolation(self):
        self.assertEqual(
            select_executor_workspace(
                serial_safe=True,
                parallel_mutation=False,
                isolation_required=False,
                integration_approved=False,
                isolation_available=False,
                recorded_base_matches=True,
                workspace_fresh=True,
                workspace_conflict=False,
            ),
            "reuse-authoritative",
        )
        self.assertEqual(
            select_executor_workspace(
                serial_safe=True,
                parallel_mutation=True,
                isolation_required=False,
                integration_approved=True,
                isolation_available=True,
                recorded_base_matches=True,
                workspace_fresh=True,
                workspace_conflict=False,
            ),
            "prepare-integration",
        )
        self.assertEqual(
            select_executor_workspace(
                serial_safe=True,
                parallel_mutation=True,
                isolation_required=False,
                integration_approved=False,
                isolation_available=True,
                recorded_base_matches=True,
                workspace_fresh=True,
                workspace_conflict=False,
            ),
            "reopen-gate-3",
        )
        self.assertEqual(
            select_executor_workspace(
                serial_safe=False,
                parallel_mutation=False,
                isolation_required=True,
                integration_approved=True,
                isolation_available=False,
                recorded_base_matches=True,
                workspace_fresh=True,
                workspace_conflict=False,
            ),
            "reopen-gate-3",
        )

    def test_workspace_reopens_gate_three_for_wrong_stale_or_conflicting_base(self):
        valid = dict(
            serial_safe=True,
            parallel_mutation=False,
            isolation_required=False,
            integration_approved=False,
            isolation_available=False,
            recorded_base_matches=True,
            workspace_fresh=True,
            workspace_conflict=False,
        )
        for field, value in (
            ("recorded_base_matches", False),
            ("workspace_fresh", False),
            ("workspace_conflict", True),
        ):
            with self.subTest(field=field):
                self.assertEqual(
                    select_executor_workspace(**{**valid, field: value}),
                    "reopen-gate-3",
                )

    def test_recovery_requires_checkbox_accepted_commit_and_current_git(self):
        progress = recover_executor_progress(
            ticket_ids=("T1", "T2", "T3", "T4", "T5"),
            checked_ids={"T1", "T2", "T4"},
            accepted_commits={
                "T1": "c1",
                "T3": "c3",
                "T4": "c4",
                "T5": "c5",
            },
            current_git_commits={"c1", "c3"},
        )

        self.assertEqual(progress["completed"], ("T1",))
        self.assertEqual(progress["inconsistent"], ("T2", "T3", "T4", "T5"))

    def test_ready_frontier_stays_in_earliest_wave_and_caps_at_four(self):
        tickets = [self.ticket(ticket_id) for ticket_id in ("T1", "T2", "T3", "T4")]
        tickets.append(self.ticket("T5", dependencies=("T1", "T2", "T3", "T4")))
        waves = (("T1", "T2", "T3", "T4"), ("T5",))

        self.assertEqual(
            select_planned_wave_batch(
                tickets,
                waves,
                completed_ids=set(),
                host_available_slots=8,
                isolated=True,
                parallel_request="preferred",
            ),
            (("T1", "delegate"), ("T2", "delegate"), ("T3", "delegate"), ("T4", "delegate")),
        )
        self.assertEqual(
            select_planned_wave_batch(
                tickets,
                waves,
                completed_ids={"T1", "T2", "T3", "T4"},
                host_available_slots=8,
                isolated=True,
            ),
            (("T5", "delegate"),),
        )

    def test_main_accepts_results_only_with_integrated_evidence(self):
        accepted = dict(
            base_matches=True,
            accepted_sibling_advancement=False,
            ownership_disjoint=True,
            transfer_clean=True,
            diff_explained=True,
            verification_passes=True,
        )
        self.assertEqual(integrate_wave_result(**accepted), "accept")
        for failed_field in (
            "base_matches",
            "ownership_disjoint",
            "transfer_clean",
            "diff_explained",
            "verification_passes",
        ):
            with self.subTest(failed_field=failed_field):
                evidence = {**accepted, failed_field: False}
                self.assertEqual(
                    integrate_wave_result(**evidence),
                    "requeue-serialized",
                )

    def test_contract_forbids_wrapper_merger_and_automatic_external_effects(self):
        workflow = (ROOT / "references/workflow-contract.md").read_text().lower()
        routing = (ROOT / "references/subagent-routing-contract.md").read_text().lower()
        delivery = skill_text(ROOT / "skills/delivery-coder/SKILL.md").lower()
        for phrase in (
            "no implement-spec wrapper agent",
            "no merger subagent",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, routing)
        for phrase in (
            "must not push",
            "must not install",
            "must not delete worktrees",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, workflow)
        for phrase in (
            "do not push",
            "create a pull request",
            "publish external tickets",
            "merge an original branch",
            "install",
            "delete worktrees",
        ):
            with self.subTest(delivery_effect=phrase):
                self.assertIn(phrase, delivery)


if __name__ == "__main__":
    unittest.main()
