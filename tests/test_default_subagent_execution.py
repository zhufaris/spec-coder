import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").lower()


class DefaultSubagentExecutionContractTests(unittest.TestCase):
    def test_orchestrator_forms_default_dependency_aware_waves(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")

        for phrase in (
            "dependency-aware execution wave",
            "delegates by default",
            "host capacity",
            "at most four",
            "real isolation",
            "serialized direct workers",
            "one active execution wave",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, orchestrator)
        self.assertNotIn("executes exactly one unblocked ticket at a time", orchestrator)
        self.assertNotIn("at most one active ticket", orchestrator)

    def test_tdd_handoff_keeps_red_or_structural_evidence_with_main(self) -> None:
        tdd = read("skills/tdd-coder/SKILL.md")

        for phrase in (
            "delegates eligible implementation work by default",
            "behavior red",
            "structural preservation",
            "delegation_allowed = false",
            "must not stage or commit",
            "freshly verifies",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, tdd)
        self.assertNotIn("route optional delegated work", tdd)

    def test_main_integrates_same_base_results_sequentially(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")

        for phrase in (
            "recorded wave base",
            "complete task-owned diff",
            "one result at a time",
            "accepted sibling",
            "ownership overlap",
            "later serialized",
            "fresh verification",
            "atomic commit",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, orchestrator)

    def test_opt_out_capacity_and_spawn_failures_have_distinct_outcomes(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")

        for phrase in (
            "opt-out",
            "stop new dispatch",
            "temporary capacity",
            "wait",
            "spawn unavailable",
            "local fallback",
            "explicitly required",
            "blocker",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, orchestrator)


if __name__ == "__main__":
    unittest.main()
