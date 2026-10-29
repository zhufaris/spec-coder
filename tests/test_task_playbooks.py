import unittest
from pathlib import Path

from task_playbook_contracts import (
    PlaybookKind,
    conversational_todo_is_authority,
    is_human_decision,
    requires_empirical_probe,
    select_playbook,
)


ROOT = Path(__file__).resolve().parents[1]


class TaskPlaybookContractTests(unittest.TestCase):
    def test_canonical_contract_and_scenarios_are_bundled(self):
        for relative in (
            "references/task-playbook-contract.md",
            "tests/fixtures/task-playbook-scenarios.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_pstack_provenance_is_recorded(self):
        notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
        self.assertIn("cursor/plugins", notice)
        self.assertIn("MIT License", notice)
        self.assertIn("Copyright (c) 2026 Lauren Tan", notice)

    def test_route_oracle_covers_each_singular_kind_and_proof_fields(self):
        cases = {
            PlaybookKind.FEATURE: {"new-user-outcome"},
            PlaybookKind.BUG_FIX: {"reproduced-defect"},
            PlaybookKind.REFACTOR: {"behavior-preserving"},
            PlaybookKind.PERFORMANCE: {"repeatable-performance-baseline"},
            PlaybookKind.SKILL_CHANGE: {"skill-instruction-change"},
            PlaybookKind.WORKFLOW_EVAL: {"standalone-evaluation"},
            PlaybookKind.GENERIC: set(),
        }
        for expected, facts in cases.items():
            with self.subTest(kind=expected):
                selection = select_playbook(request="change", facts=facts)
                self.assertEqual(selection.kind, expected)
                self.assertTrue(selection.entry_evidence)
                self.assertTrue(selection.design_obligations)
                self.assertTrue(selection.red_or_pin)
                self.assertTrue(selection.delivery_proof)
                self.assertTrue(selection.conditional_references)

    def test_ambiguous_fallback_and_precedence_never_combine_playbooks(self):
        ambiguous = select_playbook(request="make export better", facts=set())
        self.assertEqual(ambiguous.kind, PlaybookKind.GENERIC)
        selected = select_playbook(
            request="fix a slow skill", facts={"reproduced-defect", "skill-instruction-change"}
        )
        self.assertEqual(selected.kind, PlaybookKind.SKILL_CHANGE)
        self.assertIsInstance(selected.kind, PlaybookKind)

    def test_empirical_probe_and_todo_authority_boundaries(self):
        for probe in ("behavior", "output", "timing", "layout", "routing", "evaluation"):
            self.assertTrue(requires_empirical_probe(probe))
            self.assertFalse(is_human_decision(probe))
        for decision in ("preference", "scope", "domain meaning", "irreversible action", "authorization", "gate approval"):
            self.assertTrue(is_human_decision(decision))
            self.assertFalse(requires_empirical_probe(decision))
        self.assertFalse(conversational_todo_is_authority())

    def test_contract_has_stable_anchors_and_fixture_is_complete(self):
        contract = (ROOT / "references/task-playbook-contract.md").read_text()
        for anchor in (
            "## TaskPlaybookSelection",
            "## Route precedence and one-selection rule",
            "## Evidence and proof matrix",
            "## Empirical facts and human decisions",
            "## Conversational TODO boundary",
            "## Conditional loading intent",
            "## Blinded evaluation constraints",
            "## Pstack provenance and nondependency",
        ):
            self.assertIn(anchor, contract)
        fixture = (ROOT / "tests/fixtures/task-playbook-scenarios.md").read_text()
        for heading in ("Feature", "Bug Fix", "Refactor", "Performance", "Skill Change", "Workflow Eval", "Generic", "Ambiguous"):
            self.assertIn("## " + heading, fixture)


if __name__ == "__main__":
    unittest.main()
