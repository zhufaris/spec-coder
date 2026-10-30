import unittest
from pathlib import Path
from test_stage_loading import skill_text

from task_playbook_eval_contracts import (
    CandidateRun,
    Environment,
    JudgePacket,
    LifecycleViolation,
    Verdict,
    VerdictEvidence,
    assert_candidate_run,
    assert_equivalent_environments,
    assert_judge_packet,
    assert_lifecycle,
    assert_organic_prompt,
    author_verdict,
    make_judge_packet,
)


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return skill_text(ROOT / relative).lower()


class TaskPlaybookEvalTests(unittest.TestCase):
    def test_delivery_loads_blinded_eval_only_for_selected_playbooks(self):
        delivery = read("skills/delivery-coder/SKILL.md")
        self.assertIn(
            "task-playbook-contract.md#blinded-evaluation-constraints",
            delivery,
        )
        self.assertIn("skill change", delivery)
        self.assertIn("workflow eval", delivery)
        self.assertIn("deterministic", delivery)

    def test_routing_and_worker_brief_define_direct_candidate_and_judge_roles(self):
        routing = read("references/subagent-routing-contract.md")
        brief = read("references/worker-brief-template.md")
        self.assertIn("## workflow eval execution", routing)
        for phrase in (
            "workflow eval candidate",
            "blinded judge",
            "direct layer-2",
            "delegation_allowed = false",
            "must_not_spawn = true",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, routing + "\n" + brief)
        self.assertIn("main", routing)
        self.assertNotIn("eval wrapper agent", routing)

    def test_eval_oracle_and_organic_scenarios_are_bundled(self):
        for relative in (
            "tests/task_playbook_eval_contracts.py",
            "tests/fixtures/task-playbook-eval-scenarios.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

        fixture = read("tests/fixtures/task-playbook-eval-scenarios.md")
        for leaked_word in ("eval", "test", "judge", "benchmark", "candidate", "arena"):
            with self.subTest(leaked_word=leaked_word):
                self.assertNotIn(leaked_word, fixture)

    def test_deterministic_failure_dominates_comparison_quality(self):
        evidence = VerdictEvidence(
            selected_playbook="Skill Change",
            deterministic_green=False,
            all_outputs_read_by_main=True,
            available_transcripts_read_by_main=True,
            evidence_conclusive=True,
            candidate_at_least_equal=True,
        )
        self.assertEqual(Verdict.KEEP_PARENT, author_verdict(evidence))

    def test_inconclusive_or_conflicting_evidence_keeps_parent(self):
        baseline = dict(
            selected_playbook="Workflow Eval",
            deterministic_green=True,
            all_outputs_read_by_main=True,
            available_transcripts_read_by_main=True,
            candidate_at_least_equal=True,
        )
        self.assertEqual(
            Verdict.KEEP_PARENT,
            author_verdict(VerdictEvidence(**baseline, evidence_conclusive=False)),
        )
        self.assertEqual(
            Verdict.KEEP_PARENT,
            author_verdict(
                VerdictEvidence(
                    **baseline,
                    evidence_conclusive=True,
                    evidence_conflicting=True,
                )
            ),
        )

    def test_conclusive_non_regressing_evidence_can_accept_candidate(self):
        evidence = VerdictEvidence(
            selected_playbook="Workflow Eval",
            deterministic_green=True,
            all_outputs_read_by_main=True,
            available_transcripts_read_by_main=True,
            evidence_conclusive=True,
            candidate_at_least_equal=True,
        )
        self.assertEqual(Verdict.ACCEPT_CANDIDATE, author_verdict(evidence))

    def test_prompt_leakage_is_rejected(self):
        assert_organic_prompt("Repair the routing defect and preserve approval authority.")
        with self.assertRaises(LifecycleViolation):
            assert_organic_prompt("Run this benchmark and tell the judge which answer wins.")

    def test_wrong_sequence_is_rejected(self):
        correct = (
            "deterministic-green",
            "prepare-equivalent-environments",
            "dispatch-direct-candidates",
            "collect-all-candidates",
            "dispatch-direct-blinded-judge",
            "collect-judge",
            "main-inspect-all-evidence",
            "main-verdict",
        )
        assert_lifecycle(correct, use_judge=True)
        with self.assertRaises(LifecycleViolation):
            assert_lifecycle(
                correct[:3] + correct[4:6] + (correct[3],) + correct[6:],
                use_judge=True,
            )

    def test_nested_delegation_is_rejected(self):
        assert_candidate_run(CandidateRun(handle="direct", output="bounded evidence"))
        with self.assertRaises(LifecycleViolation):
            assert_candidate_run(
                CandidateRun(handle="nested", output="untrusted", spawned_children=1)
            )

    def test_judge_identity_exposure_is_rejected(self):
        packet = make_judge_packet(
            outputs=("first", "second"),
            private_rubric="quality",
        )
        assert_judge_packet(packet)
        with self.assertRaises(LifecycleViolation):
            assert_judge_packet(
                JudgePacket(
                    outputs=(("Parent", "first"), ("Candidate", "second")),
                    rubric="quality",
                )
            )

    def test_environments_must_be_equivalent_and_sanitized(self):
        parent = Environment("parent", "abc", "same")
        candidate = Environment("candidate", "abc", "same")
        assert_equivalent_environments(parent, candidate)
        with self.assertRaises(LifecycleViolation):
            assert_equivalent_environments(
                parent,
                Environment("candidate", "def", "same"),
            )

    def test_candidate_facing_role_body_does_not_disclose_comparison_identity(self):
        brief = (ROOT / "references/worker-brief-template.md").read_text().lower()
        role_field = next(
            line for line in brief.splitlines() if line.startswith("role: {")
        )
        self.assertIn("task respondent", role_field)
        self.assertNotIn("workflow eval candidate", role_field)
        body = brief.split("- **workflow eval candidate:**", 1)[1].split(
            "- **blinded judge:**", 1
        )[0]
        self.assertIn("role: task respondent", body)
        for forbidden in (
            "eval",
            "evaluation",
            "test",
            "judge",
            "benchmark",
            "candidate",
            "arena",
            "parent",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
