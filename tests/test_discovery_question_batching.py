import unittest

from forward_contracts import apply_discovery_round, select_discovery_question_batch


class DiscoveryQuestionBatchingTests(unittest.TestCase):
    def question(
        self,
        question_id,
        *,
        dependencies=(),
        risk="ordinary",
        coupling_keys=(),
    ):
        return {
            "id": question_id,
            "dependencies": dependencies,
            "risk": risk,
            "coupling_keys": coupling_keys,
        }

    def test_independent_ready_frontier_batches_in_tree_order_with_cap(self):
        questions = [
            self.question("Q1", coupling_keys=("audience",)),
            self.question("Q2", coupling_keys=("latency",)),
            self.question("Q3", coupling_keys=("retention",)),
            self.question("Q4", coupling_keys=("locale",)),
        ]

        self.assertEqual(
            select_discovery_question_batch(questions, confirmed_ids=set()),
            ("Q1", "Q2", "Q3"),
        )

    def test_unsettled_dependency_waits_for_a_later_round(self):
        questions = [
            self.question("Q1", coupling_keys=("scope",)),
            self.question(
                "Q2", dependencies=("Q1",), coupling_keys=("delivery",)
            ),
            self.question("Q3", coupling_keys=("locale",)),
        ]

        self.assertEqual(
            select_discovery_question_batch(questions, confirmed_ids=set()),
            ("Q1", "Q3"),
        )
        self.assertEqual(
            select_discovery_question_batch(questions, confirmed_ids={"Q1"}),
            ("Q2", "Q3"),
        )

    def test_high_risk_overlap_and_unknown_coupling_serialize(self):
        high_risk = [
            self.question("Q1", risk="high", coupling_keys=("domain-owner",)),
            self.question("Q2", coupling_keys=("locale",)),
        ]
        overlapping = [
            self.question("Q1", coupling_keys=("scope",)),
            self.question("Q2", coupling_keys=("scope",)),
            self.question("Q3", coupling_keys=("locale",)),
        ]
        unknown = [
            self.question("Q1", coupling_keys=None),
            self.question("Q2", coupling_keys=("locale",)),
        ]

        self.assertEqual(select_discovery_question_batch(high_risk, set()), ("Q1",))
        self.assertEqual(select_discovery_question_batch(overlapping, set()), ("Q1",))
        self.assertEqual(select_discovery_question_batch(unknown, set()), ("Q1",))

    def test_later_coupling_keeps_the_already_safe_frontier_prefix(self):
        questions = [
            self.question("Q1", coupling_keys=("audience",)),
            self.question("Q2", coupling_keys=("latency",)),
            self.question("Q3", coupling_keys=("latency",)),
            self.question("Q4", coupling_keys=("locale",)),
        ]

        self.assertEqual(
            select_discovery_question_batch(questions, confirmed_ids=set()),
            ("Q1", "Q2"),
        )

    def test_partial_and_ambiguous_answers_preserve_only_explicit_decisions(self):
        result = apply_discovery_round(
            ("Q1", "Q2", "Q3"),
            {"Q1": "default", "Q2": "maybe"},
            ambiguous_ids={"Q2"},
        )

        self.assertEqual(result["confirmed"], ("Q1",))
        self.assertEqual(result["unresolved"], ("Q2", "Q3"))
        self.assertEqual(result["serial_follow_up"], "Q2")

    def test_bare_default_cannot_confirm_a_multi_question_round(self):
        result = apply_discovery_round(
            ("Q1", "Q2"),
            {},
            bare_default=True,
        )

        self.assertEqual(result["confirmed"], ())
        self.assertEqual(result["unresolved"], ("Q1", "Q2"))
        self.assertEqual(result["serial_follow_up"], "Q1")


if __name__ == "__main__":
    unittest.main()
