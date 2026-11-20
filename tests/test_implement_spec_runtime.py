import unittest
from pathlib import Path
from test_stage_loading import skill_text


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return skill_text(ROOT / relative)


class ImplementSpecRuntimeContractTests(unittest.TestCase):
    def test_implementation_consumes_one_ticket_handoff_and_returns_evidence(self):
        implementation = " ".join(
            read("playbooks/stages/implementation.md").lower().split()
        )
        for phrase in (
            "one executor-issued ticket handoff",
            "one-ticket red/green lifecycle",
            "complete task-owned diff",
            "exact commands and results",
            "return its evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, implementation)

        for forbidden_authority in (
            "apply delegation eligibility",
            "assemble the worker brief",
            "promotion sibling",
            "create one conventional commit",
            "update the durable plan checkbox",
            "capacity evaluation",
        ):
            with self.subTest(forbidden_authority=forbidden_authority):
                self.assertNotIn(forbidden_authority, implementation)

    def test_implementation_links_to_every_executor_safety_owner(self):
        implementation = read("playbooks/stages/implementation.md").lower()
        for owner in (
            "../../references/workflow-contract.md#native-implement-spec-executor",
            "../../references/subagent-routing-contract.md#detailed-executor-and-delegation-authority",
            "../../references/subagent-routing-contract.md#worker-progress-heartbeat",
            "../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode",
            "../../references/subagent-routing-contract.md#execution-waves",
            "../../references/subagent-routing-contract.md#attempt-evidence-and-promotion",
            "../../references/subagent-routing-contract.md#result-integration",
        ):
            with self.subTest(owner=owner):
                self.assertIn(owner, implementation)

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
        implementation = read("playbooks/stages/implementation.md").lower()
        routing = read("references/subagent-routing-contract.md").lower()
        self.assertIn("workflow-contract.md#native-implement-spec-executor", tdd)
        self.assertIn("subagent-routing-contract.md#execution-waves", tdd)
        self.assertIn("subagent-routing-contract.md#result-integration", tdd)
        self.assertIn("one unblocked ticket", implementation)
        self.assertIn("main-only", implementation)
        self.assertIn("delegation_allowed = false", routing)
        self.assertIn("approved `build cache`", implementation)
        self.assertIn("authoritative workspace", implementation)

    def test_tdd_public_entry_returns_evidence_without_mutation_authority(self):
        tdd = (ROOT / "skills/tdd-coder/SKILL.md").read_text().lower()
        for phrase in (
            "one executor-issued unblocked vertical ticket",
            "red-green/structural evidence",
            "return provisional evidence",
            "main owns acceptance",
            "durable plan advancement",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, tdd)
        for contradiction in (
            "atomic commit, and plan-state update",
            "one ticket-only conventional commit",
            "synchronized plan state",
            "do not mark the ticket complete or commit unless",
        ):
            with self.subTest(contradiction=contradiction):
                self.assertNotIn(contradiction, tdd)

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

    def test_main_only_acceptance_commit_and_completion_live_outside_ticket_lifecycle(self):
        workflow = read("references/workflow-contract.md").lower()
        routing = read("references/subagent-routing-contract.md").lower()
        implementation = read("playbooks/stages/implementation.md").lower()

        for phrase in ("acceptance", "staging", "commits", "completion"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, workflow)
        self.assertIn("main integrates one result at a time", routing)
        for forbidden in (
            "accept a result",
            "completion claim",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, implementation)

    def test_result_integration_orders_commit_checkbox_then_frontier(self):
        routing = read("references/subagent-routing-contract.md").lower()
        result_integration = routing.split("## result integration", 1)[1]
        result_integration = result_integration.split("\n## ", 1)[0]
        result_integration = " ".join(result_integration.split())
        self.assertIn(
            "for every result—main-local, serialized direct, or parallel",
            result_integration,
        )
        commit = result_integration.index("creates its atomic commit")
        checkbox = result_integration.index("updates that ticket's durable checkbox")
        frontier = result_integration.index(
            "recomputes the earliest incomplete ready frontier"
        )
        self.assertLess(commit, checkbox)
        self.assertLess(checkbox, frontier)

        implementation = read("playbooks/stages/implementation.md").lower()
        self.assertNotIn("creates its atomic commit", implementation)
        self.assertNotIn("updates that ticket's durable checkbox", implementation)

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

    def test_playbook_selection_changes_proof_not_executor_topology(self):
        workflow = read("references/workflow-contract.md").lower()
        orchestrator = read("skills/spec-coder/SKILL.md").lower()
        tdd = read("skills/tdd-coder/SKILL.md").lower()
        self.assertLess(
            workflow.index("task playbook selection"),
            workflow.index("run `grill-coder`"),
        )
        self.assertIn("one native implement-spec executor", workflow)
        self.assertNotIn("execution profile", orchestrator)
        self.assertIn("selected `red_or_pin`", tdd)


if __name__ == "__main__":
    unittest.main()
