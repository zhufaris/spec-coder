import unittest
from pathlib import Path

from forward_contracts import decide_approval_route, resolve_autonomy_mode


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").lower()


class AutonomousModeOracleTests(unittest.TestCase):
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
            "must not invoke `brainstorming`",
            "unique grounded recommendation",
            "auto-selected under explicit autonomous authority",
        ):
            with self.subTest(design_phrase=phrase):
                self.assertIn(phrase, design)
        self.assertIn("interactive path", design)
        self.assertIn("compose `brainstorming`", design)

        for phrase in (
            "gate 2",
            "gate 3",
            "does not wait",
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


if __name__ == "__main__":
    unittest.main()
