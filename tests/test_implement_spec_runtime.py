import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text()


class ImplementSpecRuntimeContractTests(unittest.TestCase):
    def test_orchestrator_enters_one_executor_and_loads_all_runtime_owners(self):
        orchestrator = read("skills/spec-coder/SKILL.md").lower()
        for owner in (
            "../../references/workflow-contract.md#stage-runtime-envelope",
            "../../references/workflow-contract.md#native-implement-spec-executor",
            "../../references/subagent-routing-contract.md#execution-waves",
            "../../references/subagent-routing-contract.md#result-integration",
        ):
            with self.subTest(owner=owner):
                self.assertIn(owner, orchestrator)
        self.assertIn("native implement-spec executor", orchestrator)
        self.assertIn("every", orchestrator)
        self.assertIn("singleton", orchestrator)
        self.assertNotIn("execution profile", orchestrator)
        self.assertNotIn("large-spec", orchestrator)

    def test_tdd_remains_one_ticket_engine_inside_executor(self):
        tdd = read("skills/tdd-coder/SKILL.md").lower()
        self.assertIn("workflow-contract.md#native-implement-spec-executor", tdd)
        self.assertIn("subagent-routing-contract.md#execution-waves", tdd)
        self.assertIn("subagent-routing-contract.md#result-integration", tdd)
        self.assertIn("one selected ticket", tdd)
        self.assertIn("main", tdd)
        self.assertIn("delegation_allowed = false", tdd)
        self.assertIn("this workspace's approved `build cache`", tdd)
        self.assertIn("isolated worker", tdd)

    def test_delivery_preserves_the_approved_build_cache(self):
        delivery = read("skills/delivery-coder/SKILL.md").lower()
        self.assertIn("that workspace's approved canonical cache", delivery)
        self.assertIn("baseline and integration", delivery)
        self.assertIn("never falls back to `/tmp`", delivery)

    def test_tdd_entry_and_exit_cannot_bypass_the_executor(self):
        tdd = read("skills/tdd-coder/SKILL.md").lower()
        brief = read("references/worker-brief-template.md").lower()
        self.assertIn("executor-issued", tdd)
        self.assertIn("native implement-spec executor", tdd)
        self.assertNotIn("use after plan-coder authorization", tdd)
        self.assertIn("return to the native implement-spec executor", tdd)
        self.assertNotIn(
            "select the next unblocked ticket, or hand off to `delivery-coder`",
            tdd,
        )
        self.assertNotIn("standalone tdd", brief)
        self.assertIn("executor-issued tdd", brief)

    def test_atomic_commit_precedes_checkbox_and_frontier_recomputation(self):
        tdd = read("skills/tdd-coder/SKILL.md").lower()
        commit = tdd.index("create one conventional commit")
        checkbox = tdd.index("update the durable plan checkbox")
        return_to_executor = tdd.index("return to the native implement-spec executor")
        self.assertLess(commit, checkbox)
        self.assertLess(checkbox, return_to_executor)

    def test_reopened_gate_three_revalidates_changed_scheduling_inputs(self):
        workflow = read("references/workflow-contract.md").lower()
        orchestrator = read("skills/spec-coder/SKILL.md").lower()
        ticket = read("references/ticket-template.md").lower()

        for content in (workflow, ticket):
            with self.subTest(document=content[:30]):
                self.assertIn("post-gate-3", content)
                self.assertIn("check-artifacts.py --phase plan", content)
                self.assertIn("active", content)
                self.assertIn("returned result", content)
                self.assertIn("ownership", content)
                self.assertIn("recorded base", content)
                self.assertIn("wave", content)
                self.assertIn("frontier", content)
                self.assertIn("fourth gate", content)

        self.assertIn("post-gate-3", orchestrator)
        self.assertIn(
            "workflow-contract.md#reopened-gate-3-scheduling-barrier",
            orchestrator,
        )
        self.assertIn("fourth gate", orchestrator)
        self.assertNotIn("check-artifacts.py --phase plan", orchestrator)

        for stopped_action in (
            "dispatch",
            "result acceptance",
            "staging",
            "commit",
            "checkbox advancement",
        ):
            with self.subTest(stopped_action=stopped_action):
                self.assertIn(stopped_action, workflow)

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
            "build cache:",
            ".cache/<branch>/target",
            "delegation_allowed = false",
            "must_not_spawn = true",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, brief)

    def test_worktree_adapter_prepares_only_approved_executor_isolation(self):
        worktrees = read("skills/using-git-worktrees/SKILL.md").lower()
        self.assertIn("workflow-contract.md#workspace-selection", worktrees)
        self.assertIn("workflow-contract.md#recovery", worktrees)
        self.assertIn("subagent-routing-contract.md#execution-waves", worktrees)
        self.assertIn("authoritative workspace", worktrees)
        self.assertIn("integration", worktrees)
        self.assertIn("recorded wave base", worktrees)
        self.assertIn("reopen gate 3", worktrees)
        self.assertIn("must not delete worktrees", worktrees)

    def test_orchestrator_interface_describes_whole_plan_execution(self):
        metadata = read("skills/spec-coder/agents/openai.yaml").lower()
        self.assertIn("task graph", metadata)
        self.assertIn("native implement-spec executor", metadata)

    def test_tdd_interface_requires_executor_issued_ticket(self):
        metadata = read("skills/tdd-coder/agents/openai.yaml").lower()
        self.assertIn("executor-issued", metadata)
        self.assertNotIn("next unblocked ticket", metadata)


if __name__ == "__main__":
    unittest.main()
