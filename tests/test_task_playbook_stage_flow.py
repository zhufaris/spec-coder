import unittest
from pathlib import Path

from task_playbook_contracts import PlaybookKind, select_playbook


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text().lower()


class TaskPlaybookStageFlowTests(unittest.TestCase):
    def test_core_stages_link_the_selected_playbook_owner(self):
        expected = {
            "spec-coder": (
                "task-playbook-contract.md#route-precedence-and-one-selection-rule",
                "task-playbook-contract.md#conversational-todo-boundary",
            ),
            "grill-coder": (
                "task-playbook-contract.md#taskplaybookselection",
                "task-playbook-contract.md#empirical-facts-and-human-decisions",
            ),
            "design-coder": (
                "task-playbook-contract.md#taskplaybookselection",
                "task-playbook-contract.md#empirical-facts-and-human-decisions",
            ),
            "plan-coder": (
                "task-playbook-contract.md#taskplaybookselection",
            ),
            "tdd-coder": (
                "task-playbook-contract.md#taskplaybookselection",
            ),
            "delivery-coder": (
                "task-playbook-contract.md#taskplaybookselection",
            ),
        }
        for stage, links in expected.items():
            content = read(f"skills/{stage}/SKILL.md")
            for link in links:
                with self.subTest(stage=stage, link=link):
                    self.assertIn(link, content)

    def test_selection_precedes_the_fixed_phase_order_without_a_second_executor(self):
        workflow = read("references/workflow-contract.md")
        self.assertIn("task playbook selection", workflow)
        self.assertIn("before entering", workflow)
        self.assertIn("fixed stage order", workflow)
        self.assertIn("one native implement-spec executor", workflow)
        self.assertNotIn("execution profile", read("skills/spec-coder/SKILL.md"))

    def test_orchestrator_metadata_names_task_playbook_selection(self):
        metadata = read("skills/spec-coder/agents/openai.yaml")
        self.assertIn("task playbook", metadata)

    def test_each_route_preserves_its_fields_at_existing_stage_seams(self):
        cases = {
            PlaybookKind.FEATURE: {"new-user-outcome"},
            PlaybookKind.BUG_FIX: {"reproduced-defect"},
            PlaybookKind.REFACTOR: {"behavior-preserving"},
            PlaybookKind.PERFORMANCE: {"repeatable-performance-baseline"},
            PlaybookKind.SKILL_CHANGE: {"skill-instruction-change"},
            PlaybookKind.WORKFLOW_EVAL: {"standalone-evaluation"},
            PlaybookKind.GENERIC: set(),
        }
        for kind, facts in cases.items():
            with self.subTest(kind=kind):
                selection = select_playbook(request="change", facts=facts)
                self.assertEqual(selection.kind, kind)
                self.assertEqual(len(selection.conditional_references), 1)
                self.assertIn(kind.value.lower().replace(" ", "-") + "-playbook", selection.conditional_references[0])

        spec = read("skills/spec-coder/SKILL.md")
        grill = read("skills/grill-coder/SKILL.md")
        design = read("skills/design-coder/SKILL.md")
        plan = read("skills/plan-coder/SKILL.md")
        tdd = read("skills/tdd-coder/SKILL.md")
        delivery = read("skills/delivery-coder/SKILL.md")
        for token in ("entry_evidence", "design_obligations"):
            self.assertIn(token, grill)
        self.assertIn("design obligations", design)
        for token in ("kind", "entry_evidence", "design_obligations", "red_or_pin", "delivery_proof", "conditional_references"):
            self.assertIn(token, plan)
        for token in ("red_or_pin", "delivery_proof"):
            self.assertIn(token, tdd)
        for token in ("delivery_proof", "conditional_references"):
            self.assertIn(token, delivery)
        self.assertIn("nearby rejected routes", spec)
        self.assertIn("phase steps", spec)
        self.assertIn("skip reasons", spec)
        for stage in (spec, grill, design, plan, tdd, delivery):
            self.assertIn("conditional_references", stage)
            self.assertNotIn("task-playbook-contract.md#evidence-and-proof-matrix", stage)

    def test_empirical_probes_do_not_widen_gate_or_mutation_authority(self):
        grill = read("skills/grill-coder/SKILL.md")
        design = read("skills/design-coder/SKILL.md")
        self.assertIn("bounded probes", grill)
        for boundary in ("probes never approve a", "authorize mutation", "human-owned product decision"):
            self.assertIn(boundary, design)


if __name__ == "__main__":
    unittest.main()
