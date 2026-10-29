import unittest
from pathlib import Path
from test_stage_loading import instruction_text

from forward_contracts import decide_approval_route, resolve_autonomy_mode
from task_playbook_contracts import PlaybookKind, select_playbook
from task_playbook_eval_contracts import (
    CandidateRun,
    Environment,
    assert_candidate_run,
    assert_equivalent_environments,
    assert_lifecycle,
    assert_organic_prompt,
)


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return instruction_text(ROOT / relative).lower()


class AutonomousModeOracleTests(unittest.TestCase):
    def test_playbooks_preserve_gate_authority_and_external_effect_boundary(self) -> None:
        selected = select_playbook(
            request="Revise the repository skill's directly linked guidance.",
            facts={"skill-instruction-change"},
        )
        self.assertEqual(selected.kind, PlaybookKind.SKILL_CHANGE)
        for gate in ("gate-1", "gate-2", "gate-3"):
            with self.subTest(mode="interactive", gate=gate):
                self.assertEqual(
                    decide_approval_route(
                        autonomy_mode="interactive",
                        review_kind=gate,
                        grounded_recommendations=1,
                    ),
                    "request-human-review",
                )
            with self.subTest(mode="autonomous", gate=gate):
                self.assertEqual(
                    decide_approval_route(
                        autonomy_mode="autonomous",
                        review_kind=gate,
                        grounded_recommendations=1,
                    ),
                    "auto-select-recommended",
                )
        self.assertEqual(
            decide_approval_route(
                autonomy_mode="autonomous",
                review_kind="named-mutation",
                grounded_recommendations=1,
            ),
            "request-human-review",
        )

    def test_workflow_eval_uses_organic_direct_children_without_topology_widening(self) -> None:
        selected = select_playbook(
            request="Compare the two workflow outputs for the requested policy.",
            facts={"standalone-evaluation"},
        )
        self.assertEqual(selected.kind, PlaybookKind.WORKFLOW_EVAL)
        assert_organic_prompt("Compare the two workflow outputs for the requested policy.")
        assert_equivalent_environments(
            Environment("parent", "base", "inputs"),
            Environment("candidate", "base", "inputs"),
        )
        assert_candidate_run(CandidateRun(handle="direct-child", output="bounded result"))
        assert_lifecycle(
            (
                "deterministic-green",
                "prepare-equivalent-environments",
                "dispatch-direct-candidates",
                "collect-all-candidates",
                "dispatch-direct-blinded-judge",
                "collect-judge",
                "main-inspect-all-evidence",
                "main-verdict",
            ),
            use_judge=True,
        )

    def test_autonomous_mode_requires_current_user_request_authority(self) -> None:
        self.assertEqual(
            resolve_autonomy_mode(explicit_user_choice=None, source=None),
            "interactive",
        )
        self.assertEqual(
            resolve_autonomy_mode(
                explicit_user_choice=False,
                source="current-user-request",
            ),
            "interactive",
        )
        self.assertEqual(
            resolve_autonomy_mode(
                explicit_user_choice=True,
                source="current-user-request",
            ),
            "autonomous",
        )

        for source in (
            "repository-config",
            "global-config",
            "agents.md",
            "prior-session",
            "subagent",
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                resolve_autonomy_mode(explicit_user_choice=True, source=source)

    def test_autonomous_mode_selects_one_grounded_recommendation_at_three_gates(self) -> None:
        for review_kind in (
            "design-alternative-selection",
            "gate-1",
            "gate-2",
            "gate-3",
            "reopened-in-scope-gate",
        ):
            with self.subTest(review_kind=review_kind):
                self.assertEqual(
                    decide_approval_route(
                        autonomy_mode="autonomous",
                        review_kind=review_kind,
                        grounded_recommendations=1,
                    ),
                    "auto-select-recommended",
                )

    def test_interactive_mode_keeps_human_review(self) -> None:
        for review_kind in (
            "design-alternative-selection",
            "gate-1",
            "gate-2",
            "gate-3",
        ):
            with self.subTest(review_kind=review_kind):
                self.assertEqual(
                    decide_approval_route(
                        autonomy_mode="interactive",
                        review_kind=review_kind,
                        grounded_recommendations=1,
                    ),
                    "request-human-review",
                )

    def test_autonomous_mode_never_invents_or_widens_authority(self) -> None:
        common = {
            "autonomy_mode": "autonomous",
            "review_kind": "gate-1",
            "grounded_recommendations": 1,
        }
        self.assertEqual(
            decide_approval_route(**common, unresolved_load_bearing=True),
            "stop-unresolved-decision",
        )
        self.assertEqual(
            decide_approval_route(**{**common, "grounded_recommendations": 0}),
            "stop-no-unique-recommendation",
        )
        self.assertEqual(
            decide_approval_route(**{**common, "grounded_recommendations": 2}),
            "stop-no-unique-recommendation",
        )
        self.assertEqual(
            decide_approval_route(**common, scope_expansion=True),
            "request-human-review",
        )
        self.assertEqual(
            decide_approval_route(**common, separate_authority_required=True),
            "request-human-review",
        )
        self.assertEqual(
            decide_approval_route(
                autonomy_mode="autonomous",
                review_kind="named-mutation",
                grounded_recommendations=1,
            ),
            "request-human-review",
        )


class AutonomousModeContractTests(unittest.TestCase):
    def test_orchestrator_and_workflow_define_request_scoped_authority(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")
        workflow = read("references/workflow-contract.md")

        for document in (orchestrator, workflow):
            for phrase in (
                "autonomous=true",
                "default is false",
                "current user request",
                "request-scoped",
                "auto-selected under explicit autonomous authority",
                "scope expansion",
                "separate authorization",
            ):
                with self.subTest(document=document[:30], phrase=phrase):
                    self.assertIn(phrase, document)

    def test_design_and_planning_skip_only_the_three_suite_gates(self) -> None:
        design = read("skills/design-coder/SKILL.md")
        planner = read("skills/plan-coder/SKILL.md")

        for phrase in (
            "autonomous path",
            "unique grounded recommendation",
            "auto-selected under explicit autonomous authority",
        ):
            with self.subTest(design_phrase=phrase):
                self.assertIn(phrase, design)
        self.assertIn("interactive path", design)
        self.assertIn("not a required capability", design)
        self.assertIn("gate 2", design)
        self.assertIn("gate 3", design)

        for phrase in (
            "gate 2",
            "gate 3",
            "do not request human",
            "auto-selected under explicit autonomous authority",
            "durable planned wave",
        ):
            with self.subTest(planner_phrase=phrase):
                self.assertIn(phrase, planner)

    def test_published_docs_explain_autonomous_mode_and_exclusions(self) -> None:
        published = "\n".join((read("README.md"), read("INSTALL.md")))

        for phrase in (
            "autonomous=true",
            "request-scoped",
            "default is false",
            "gate 1",
            "gate 2",
            "gate 3",
            "recommended",
            "push",
            "install",
            "scope expansion",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, published)

    def test_published_docs_limit_show_me_to_human_reviews(self) -> None:
        readme = read("README.md")
        install = read("INSTALL.md")

        for document in (readme, install):
            with self.subTest(document=document[:30]):
                self.assertIn("interactive gate", document)
                self.assertIn("autonomous selection", document)
                self.assertIn("does not invoke `show-me`", document)

    def test_domain_templates_and_delivery_accept_autonomously_selected_artifacts(self) -> None:
        domain_contract = read("references/domain-design-contract.md")
        specification_template = read("references/specification-template.md")
        ticket_template = read("references/ticket-template.md")
        delivery = read("skills/delivery-coder/SKILL.md")
        tdd = read("skills/tdd-coder/SKILL.md")

        self.assertIn("interactive approval or autonomous selection", domain_contract)
        self.assertIn("autonomous gate 2", specification_template)
        self.assertIn("autonomous gate 3", ticket_template)
        self.assertIn("approved or autonomously selected specification and plan", delivery)
        self.assertIn("approved or autonomously selected design", tdd)

    def test_execution_handoff_accepts_autonomously_selected_tickets_and_waves(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")
        tdd = read("skills/tdd-coder/SKILL.md")
        ticket_template = read("references/ticket-template.md")
        routing = read("references/subagent-routing-contract.md")
        compatibility = read("references/upstream-compatibility.md")
        tdd_metadata = read("skills/tdd-coder/agents/openai.yaml")

        self.assertIn("approved or autonomously selected specification", orchestrator)
        self.assertIn(
            "approved or autonomously selected vertical-ticket plan",
            orchestrator,
        )

        self.assertIn(
            "approved or autonomously selected durable planned wave order",
            orchestrator,
        )
        self.assertIn(
            "approved or autonomously selected order",
            orchestrator,
        )
        self.assertIn(
            "approved or autonomously selected durable planned wave",
            tdd,
        )
        self.assertIn("approved or autonomously selected ticket", tdd)
        self.assertIn(
            "approved or autonomously selected unblocked vertical ticket",
            tdd,
        )
        self.assertIn(
            "no approved or autonomously selected unblocked ticket exists",
            tdd,
        )
        self.assertNotIn("no approved unblocked ticket exists", tdd)
        self.assertIn(
            "specification approval or autonomous gate 2 selection",
            ticket_template,
        )
        self.assertIn(
            "approved or autonomously selected planned wave order",
            ticket_template,
        )
        for phrase in (
            "approved or autonomously selected ticket is delegation-eligible",
            "approved or autonomously selected ticket plan",
            "interactive gate 3 approves",
            "autonomous gate 3 selects",
            "approved or autonomously selected order",
            "selected plan checkboxes",
            "within an approved or autonomously selected ticket",
        ):
            with self.subTest(routing_phrase=phrase):
                self.assertIn(phrase, routing)
        self.assertNotIn("approved ticket is delegation-eligible", routing)
        self.assertNotIn("only within an approved ticket", routing)
        self.assertIn(
            "every eligible approved or autonomously selected ticket",
            compatibility,
        )
        self.assertIn("interactive gate 3 approves", compatibility)
        self.assertIn("autonomous gate 3 selects", compatibility)
        self.assertNotIn("every eligible approved ticket", compatibility)
        self.assertIn(
            "implement one approved or autonomously selected ticket",
            tdd_metadata,
        )
        self.assertNotIn("implement one approved ticket", tdd_metadata)
        self.assertNotIn(
            "approved specification, approved vertical-ticket plan",
            orchestrator,
        )

    def test_scenario_fixture_keeps_autonomy_explicit_and_narrow(self) -> None:
        scenarios = read("tests/fixtures/scenarios.md")

        for phrase in (
            "explicit autonomous=true",
            "skip only the human waiting steps",
            "do not infer autonomous authority",
            "separate authorization",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, scenarios)

    def test_stage_entry_resume_and_delivery_surfaces_accept_autonomous_artifacts(self) -> None:
        design = read("skills/design-coder/SKILL.md")
        planner = read("skills/plan-coder/SKILL.md")
        planner_metadata = read("skills/plan-coder/agents/openai.yaml")
        specification = read("references/specification-template.md")
        workflow = read("references/workflow-contract.md")
        delivery = read("skills/delivery-coder/SKILL.md")
        compatibility = read("references/upstream-compatibility.md")
        worktree = read("skills/using-git-worktrees/SKILL.md")

        design_frontmatter = design.split("---", 2)[1]
        planner_frontmatter = planner.split("---", 2)[1]
        delivery_frontmatter = delivery.split("---", 2)[1]

        self.assertIn("approved or autonomously selected design", design_frontmatter)
        self.assertIn("return the selected design content", design)
        self.assertNotIn("return the approved design content", design)

        for phrase in (
            "approved or autonomously selected coding design",
            "gate 1 approval or autonomous selection",
            "selected design is missing",
            "inconsistent with the selected design",
        ):
            with self.subTest(planner_phrase=phrase):
                self.assertIn(phrase, planner)
        self.assertIn(
            "approved or autonomously selected coding design",
            planner_frontmatter,
        )
        self.assertNotIn("the approved design is missing", planner)
        self.assertIn("approved or autonomously selected design", planner_metadata)

        self.assertIn("existing approved or autonomously selected specification", specification)
        self.assertIn("reconcile the selected design", specification)
        self.assertNotIn("reconcile the approved design", specification)

        self.assertIn("approved or autonomously selected specification", workflow)
        self.assertIn("authorized in-place work", workflow)
        self.assertNotIn("approved in-place work", workflow)

        self.assertIn(
            "approved or autonomously selected specification",
            delivery_frontmatter,
        )
        self.assertIn("approved or autonomously selected specification and plan", delivery)
        self.assertNotIn("receives the approved specification and plan", delivery)

        self.assertIn("suite-owned human approvals", compatibility)
        self.assertIn("autonomous selection does not invoke `show-me`", compatibility)
        self.assertNotIn("all suite-owned approvals and mutation reviews", compatibility)

        self.assertIn("selected post-gate-3 per-worker isolation", worktree)
        self.assertIn("selected parallel execution wave", worktree)
        self.assertIn("selected parallel-wave isolation request", worktree)
        self.assertNotIn("approved post-gate-3 per-worker isolation", worktree)
        self.assertNotIn("approved parallel execution wave", worktree)


if __name__ == "__main__":
    unittest.main()
