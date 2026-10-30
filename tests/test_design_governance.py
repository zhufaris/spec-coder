import unittest
from pathlib import Path
from test_stage_loading import skill_text

from tests.design_contracts import (
    bounded_gate_1_transition,
    classify_design,
    initial_design_review,
)


ROOT = Path(__file__).resolve().parents[1]


class DesignGovernanceContractTests(unittest.TestCase):
    def test_design_coder_owns_bounded_route_without_required_brainstorming(self):
        design = skill_text(ROOT / "skills" / "design-coder" / "SKILL.md")
        compatibility = (ROOT / "references" / "upstream-compatibility.md").read_text()
        workflow = (ROOT / "references" / "workflow-contract.md").read_text()

        self.assertNotIn("must compose `brainstorming`", design)
        self.assertNotIn(
            "interactive `design-coder`: `brainstorming`",
            compatibility,
        )
        self.assertIn("bounded", design.lower())
        self.assertIn("one Gate 1", design)
        self.assertIn("Gate 2", design)
        self.assertIn("Gate 3", design)
        self.assertIn("Markdown remains the sole authority", workflow)

    def test_classification_requires_complete_bounded_evidence(self):
        bounded = dict(
            existing_seam=True,
            coherent_outcome=True,
            new_subsystem=False,
            new_public_interface_shape=False,
            cross_context_consistency_rule=False,
            unresolved_load_bearing_architecture=False,
        )
        self.assertEqual(classify_design(**bounded), "bounded")

        for field in bounded:
            with self.subTest(field=field):
                uncertain = {**bounded, field: None}
                self.assertEqual(classify_design(**uncertain), "architectural")

        for field in (
            "new_subsystem",
            "new_public_interface_shape",
            "cross_context_consistency_rule",
            "unresolved_load_bearing_architecture",
        ):
            with self.subTest(architectural_field=field):
                architectural = {**bounded, field: True}
                self.assertEqual(
                    classify_design(**architectural),
                    "architectural",
                )

        self.assertEqual(classify_design(), "architectural")

    def test_bounded_interactive_route_has_one_gate_and_no_authority_leak(self):
        self.assertEqual(
            initial_design_review(
                mode="interactive",
                classification="bounded",
                grounded_recommendations=1,
            ),
            "bounded-gate-1",
        )
        self.assertEqual(
            bounded_gate_1_transition("recommended"),
            "workspace-preparation-then-gate-2",
        )
        self.assertEqual(
            bounded_gate_1_transition("nonrecommended"),
            "design-elaboration-then-gate-1",
        )
        self.assertEqual(bounded_gate_1_transition("reject"), "stop")
        with self.assertRaises(ValueError):
            bounded_gate_1_transition("unknown")

    def test_architectural_and_autonomous_routes_remain_conservative(self):
        self.assertEqual(
            initial_design_review(
                mode="interactive",
                classification="architectural",
                grounded_recommendations=1,
            ),
            "architectural-alternative-selection",
        )
        self.assertEqual(
            initial_design_review(
                mode="autonomous",
                classification="bounded",
                grounded_recommendations=1,
            ),
            "autonomous-grounded-recommendation",
        )
        self.assertEqual(
            initial_design_review(
                mode="autonomous",
                classification="architectural",
                grounded_recommendations=2,
            ),
            "stop-no-unique-grounded-recommendation",
        )
        self.assertEqual(
            initial_design_review(mode="interactive"),
            "architectural-alternative-selection",
        )
        with self.assertRaises(ValueError):
            initial_design_review(mode="unknown")

    def test_playbook_obligations_inform_design_without_bypassing_gates(self):
        design = skill_text(ROOT / "skills" / "design-coder" / "SKILL.md")
        self.assertIn("selected playbook's entry evidence", design)
        self.assertIn("design obligations", design)
        self.assertIn("probes never approve a", design)
        for gate in ("Gate 1", "Gate 2", "Gate 3"):
            self.assertIn(gate, design)


if __name__ == "__main__":
    unittest.main()
