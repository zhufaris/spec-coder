import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def section(path, heading):
    text = (ROOT / path).read_text()
    marker = f"## {heading}\n"
    if marker not in text:
        raise AssertionError(f"missing section {heading} in {path}")
    body = text.split(marker, 1)[1]
    return body.split("\n## ", 1)[0]


class RuntimeEnvelopeOwnerTests(unittest.TestCase):
    def test_runtime_envelope_owns_only_common_stage_invariants(self):
        envelope = section("references/workflow-contract.md", "Stage Runtime Envelope")
        for phrase in (
            "phase",
            "gate",
            "authoritative workspace",
            "recorded base",
            "initial changes",
            "artifact",
            "main-only",
            "fresh verification",
            "external effect",
            "failure",
            "recovery",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, envelope.lower())
        for detail in (
            "aggregate persistence",
            "model routing",
            "45-60 seconds",
            "review snapshot",
        ):
            with self.subTest(detail=detail):
                self.assertNotIn(detail, envelope.lower())

    def test_workflow_owns_native_executor_entry_and_handoff(self):
        executor = section("references/workflow-contract.md", "Native implement-spec executor")
        for phrase in (
            "every gate 3",
            "singleton",
            "tdd-coder",
            "delivery-coder",
            "must not push",
            "must not install",
            "must not delete worktrees",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, executor.lower())

    def test_routing_remains_the_only_frontier_and_result_owner(self):
        routing = (ROOT / "references/subagent-routing-contract.md").read_text().lower()
        for heading in ("## execution waves", "## result integration"):
            self.assertIn(heading, routing)
        for phrase in (
            "earliest incomplete",
            "at most four",
            "main integrates one result at a time",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, routing)

    def test_old_executor_reference_is_removed_after_direct_owner_migration(self):
        self.assertFalse(
            (ROOT / "references/implement-spec-execution-contract.md").is_file()
        )

    def test_reopened_gate_three_fail_closed_statuses_live_in_canonical_owner(self):
        barrier = section(
            "references/workflow-contract.md", "Reopened Gate 3 scheduling barrier"
        ).lower()
        stage = (ROOT / "skills" / "spec-coder" / "SKILL.md").read_text().lower()

        for phrase in ("unsupported", "unavailable"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, barrier)
        self.assertNotIn("failed/unsupported/unavailable", stage)


if __name__ == "__main__":
    unittest.main()
