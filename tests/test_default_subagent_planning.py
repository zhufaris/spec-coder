import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class DefaultSubagentPlanningContractTests(unittest.TestCase):
    def test_runtime_mirror_tracks_one_active_wave_not_one_active_ticket(self) -> None:
        workflow = read("references/workflow-contract.md").lower()
        planner = read("skills/plan-coder/SKILL.md").lower()
        ticket_template = read("references/ticket-template.md").lower()

        for text in (workflow, planner, ticket_template):
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

        for phrase in (
            "before or at dispatch",
            "awaiting-heartbeat",
            "missed interval",
        ):
            with self.subTest(heartbeat_phrase=phrase):
                self.assertIn(phrase, template)

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
