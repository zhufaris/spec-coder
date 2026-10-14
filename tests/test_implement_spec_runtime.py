import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text()


class ImplementSpecRuntimeContractTests(unittest.TestCase):
    def test_orchestrator_enters_one_executor_and_loads_all_runtime_owners(self):
        orchestrator = read("skills/spec-coder/SKILL.md").lower()
        for anchor in (
            "authority-and-provenance",
            "executor-entry",
            "task-graph-and-ready-frontier",
            "adaptive-workspace",
            "ticket-tdd-handoff",
            "main-only-result-integration",
            "recovery",
            "completion-handoff",
            "forbidden-external-effects",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn(
                    "../../references/implement-spec-execution-contract.md#" + anchor,
                    orchestrator,
                )
        self.assertIn("native implement-spec executor", orchestrator)
        self.assertIn("every", orchestrator)
        self.assertIn("singleton", orchestrator)
        self.assertNotIn("execution profile", orchestrator)
        self.assertNotIn("large-spec", orchestrator)

    def test_tdd_remains_one_ticket_engine_inside_executor(self):
        tdd = read("skills/tdd-coder/SKILL.md").lower()
        self.assertIn("implement-spec-execution-contract.md#ticket-tdd-handoff", tdd)
        self.assertIn("implement-spec-execution-contract.md#main-only-result-integration", tdd)
        self.assertIn("one selected ticket", tdd)
        self.assertIn("main", tdd)
        self.assertIn("delegation_allowed = false", tdd)

    def test_routing_and_briefs_preserve_frontier_base_and_two_layers(self):
        routing = read("references/subagent-routing-contract.md").lower()
        brief = read("references/worker-brief-template.md").lower()
        for phrase in (
            "native implement-spec executor",
            "earliest incomplete",
            "at most four",
            "no implement-spec wrapper agent",
            "no merger subagent",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, routing)
        for phrase in (
            "authoritative workspace",
            "recorded wave base",
            "delegation_allowed = false",
            "must_not_spawn = true",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, brief)

    def test_worktree_adapter_prepares_only_approved_executor_isolation(self):
        worktrees = read("skills/using-git-worktrees/SKILL.md").lower()
        self.assertIn("implement-spec-execution-contract.md#adaptive-workspace", worktrees)
        self.assertIn("authoritative workspace", worktrees)
        self.assertIn("integration", worktrees)
        self.assertIn("recorded wave base", worktrees)
        self.assertIn("reopen gate 3", worktrees)
        self.assertIn("must not delete worktrees", worktrees)

    def test_orchestrator_interface_describes_whole_plan_execution(self):
        metadata = read("skills/spec-coder/agents/openai.yaml").lower()
        self.assertIn("task graph", metadata)
        self.assertIn("native implement-spec executor", metadata)


if __name__ == "__main__":
    unittest.main()
