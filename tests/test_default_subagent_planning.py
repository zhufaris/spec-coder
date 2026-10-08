import unittest
from pathlib import Path
from test_stage_loading import instruction_text


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return instruction_text(ROOT / relative)


class DefaultSubagentPlanningContractTests(unittest.TestCase):
    def test_runtime_mirror_tracks_one_active_wave_not_one_active_ticket(self) -> None:
        workflow = read("references/workflow-contract.md").lower()
        planner = read("skills/plan-coder/SKILL.md").lower()
        ticket_template = read("references/ticket-template.md").lower()
        routing = read("references/subagent-routing-contract.md").lower()

        for text in (workflow, planner, ticket_template, routing):
            self.assertIn("one active execution wave", text)
            self.assertNotIn("at most one active ticket", text)
            self.assertNotIn("at most one item in progress", text)

    def test_ticket_template_records_every_wave_safety_input(self) -> None:
        template = read("references/ticket-template.md").lower()

        for phrase in (
            "delegation mode",
            "mutation ownership",
            "exclusions",
            "isolation",
            "concurrency conflicts",
            "verification seam",
            "delegation_allowed = false",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, template)

        for owner in (
            "./worker-brief-template.md#common-brief",
            "./subagent-routing-contract.md#worker-progress-heartbeat",
            "./subagent-routing-contract.md#worker-brief-assembly",
        ):
            with self.subTest(owner=owner):
                self.assertIn(owner, template)

    def test_planner_checks_wave_coverage_and_safe_parallel_ownership(self) -> None:
        planner = read("skills/plan-coder/SKILL.md").lower()

        for phrase in (
            "delegation eligibility",
            "mutation ownership",
            "host capacity",
            "real isolation",
            "one active execution wave",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planner)

    def test_to_ticket_persists_explicit_wave_membership_before_gate_three(self) -> None:
        workflow = read("references/workflow-contract.md").lower()
        planner = read("skills/plan-coder/SKILL.md").lower()
        ticket_template = read("references/ticket-template.md").lower()
        routing = read("references/subagent-routing-contract.md").lower()

        for text in (workflow, planner, ticket_template, routing):
            for phrase in (
                "every ticket exactly once",
                "planned wave",
                "durable",
                "gate 3",
            ):
                with self.subTest(document=text[:30], phrase=phrase):
                    self.assertIn(phrase, text)

        self.assertIn("## wave w1", ticket_template)
        self.assertIn("scheduling order is not a functional dependency", ticket_template)
        self.assertNotIn("wave membership and host handles remain conversational", planner)
        self.assertNotIn("form an immutable conceptual `executionwave` from currently", routing)

    def test_worktree_adapter_returns_recoverable_per_worker_isolation(self) -> None:
        worktrees = read("skills/using-git-worktrees/SKILL.md").lower()

        for phrase in (
            "per-worker",
            "wave base",
            "recovery handle",
            "accepted or explicitly discarded",
            "unaccounted",
            "user-owned",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, worktrees)
        self.assertIn("optional", worktrees)
        self.assertIn("do not delete", worktrees)


if __name__ == "__main__":
    unittest.main()
