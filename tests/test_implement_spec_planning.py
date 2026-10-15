import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text()


class ImplementSpecPlanningContractTests(unittest.TestCase):
    def test_plan_coder_hands_every_gate_three_plan_to_one_executor(self):
        plan = read("skills/plan-coder/SKILL.md").lower()
        self.assertIn("workflow-contract.md#native-implement-spec-executor", plan)
        self.assertIn("workflow-contract.md#stage-runtime-envelope", plan)
        self.assertIn("subagent-routing-contract.md#execution-waves", plan)
        self.assertIn("every", plan)
        self.assertIn("native implement-spec executor", plan)
        self.assertIn("singleton", plan)
        self.assertNotIn("execution profile", plan)
        self.assertNotIn("large-spec", plan)

    def test_ticket_template_records_executor_workspace_and_frontier_inputs(self):
        template = read("references/ticket-template.md").lower()
        for phrase in (
            "native implement-spec executor",
            "authoritative workspace",
            "recorded wave base",
            "isolation requirement",
            "durable wave",
            "blocking edges",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, template)
        self.assertNotIn("execution profile", template)

    def test_gate_three_approves_workspace_inputs_without_becoming_scheduler(self):
        plan = read("skills/plan-coder/SKILL.md").lower()
        for phrase in (
            "authoritative workspace",
            "recorded wave base",
            "isolation requirement",
            "gate 3",
            "does not schedule",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, plan)


if __name__ == "__main__":
    unittest.main()
