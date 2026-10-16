import unittest

from forward_contracts import render_review_snapshot, requires_human_review


def snapshot(options, approval_kind="Gate 1"):
    return {
        "approval_kind": approval_kind,
        "artifact": "design.md",
        "decisions": ["Use shared review options"],
        "blockers": [],
        "approval_effect": "authorize the next stage",
        "next_stage": "planning",
        "excluded_authority": ["push to remote"],
        "review_options": options,
    }


APPROVE_CHANGE_REJECT = [
    {"label": "A", "choice": "Approve and continue", "consequence": "Start planning"},
    {"label": "B", "choice": "Request changes", "consequence": "Revise and re-review"},
    {"label": "C", "choice": "Reject and stop", "consequence": "Stop this change"},
]


class HumanReviewOptionTests(unittest.TestCase):
    def test_authorization_review_renders_every_choice_and_consequence(self) -> None:
        rendered = render_review_snapshot(snapshot(APPROVE_CHANGE_REJECT), width=80)

        for option in APPROVE_CHANGE_REJECT:
            self.assertIn(f'{option["label"]}: {option["choice"]}', rendered)
            self.assertIn(option["consequence"], rendered)

    def test_design_alternative_selection_is_a_distinct_review_kind(self) -> None:
        alternatives = [
            {"label": "A", "choice": "Shared contract", "consequence": "Central enforcement"},
            {"label": "B", "choice": "Per-skill rules", "consequence": "Local flexibility"},
        ]

        rendered = render_review_snapshot(
            snapshot(alternatives, approval_kind="design alternative selection"),
            width=80,
        )

        self.assertIn("design alternative selection", rendered)
        self.assertIn("A: Shared contract", rendered)
        self.assertIn("B: Per-skill rules", rendered)

    def test_bounded_gate_one_carries_recommended_and_revision_routes(self) -> None:
        options = [
            {
                "label": "A",
                "choice": "Approve recommended design and continue",
                "consequence": "Prepare workspace and continue to Gate 2",
            },
            {
                "label": "B",
                "choice": "Revise using adapter-local alternative",
                "consequence": "Elaborate that alternative and ask Gate 1 again",
            },
            {
                "label": "C",
                "choice": "Reject and stop",
                "consequence": "Stop this change",
            },
        ]

        rendered = render_review_snapshot(snapshot(options), width=80)

        for option in options:
            self.assertIn(f'{option["label"]}: {option["choice"]}', rendered)
            self.assertIn(option["consequence"], rendered)

    def test_missing_too_few_or_too_many_options_are_rejected(self) -> None:
        missing = snapshot(APPROVE_CHANGE_REJECT)
        del missing["review_options"]

        with self.assertRaises(ValueError):
            render_review_snapshot(missing, width=80)
        with self.assertRaises(ValueError):
            render_review_snapshot(snapshot(APPROVE_CHANGE_REJECT[:1]), width=80)
        with self.assertRaises(ValueError):
            render_review_snapshot(
                snapshot(APPROVE_CHANGE_REJECT + [
                    {"label": "D", "choice": "Defer", "consequence": "Pause"},
                    {"label": "E", "choice": "Escalate", "consequence": "Return to discovery"},
                ]),
                width=80,
            )

    def test_duplicate_or_incomplete_options_are_rejected(self) -> None:
        invalid_sets = [
            [
                {"label": "A", "choice": "Approve", "consequence": "Continue"},
                {"label": "A", "choice": "Reject", "consequence": "Stop"},
            ],
            [
                {"label": "", "choice": "Approve", "consequence": "Continue"},
                {"label": "B", "choice": "Reject", "consequence": "Stop"},
            ],
            [
                {"label": "A", "choice": "", "consequence": "Continue"},
                {"label": "B", "choice": "Reject", "consequence": "Stop"},
            ],
            [
                {"label": "A", "choice": "Approve", "consequence": ""},
                {"label": "B", "choice": "Reject", "consequence": "Stop"},
            ],
        ]

        for options in invalid_sets:
            with self.subTest(options=options), self.assertRaises(ValueError):
                render_review_snapshot(snapshot(options), width=80)

    def test_ungrounded_or_non_review_snapshot_fields_are_rejected(self) -> None:
        invalid_snapshots = []
        for field in ("artifact", "approval_effect", "next_stage"):
            invalid = snapshot(APPROVE_CHANGE_REJECT)
            invalid[field] = ""
            invalid_snapshots.append(invalid)
        empty_decisions = snapshot(APPROVE_CHANGE_REJECT)
        empty_decisions["decisions"] = []
        invalid_snapshots.append(empty_decisions)
        ordinary = snapshot(APPROVE_CHANGE_REJECT, approval_kind="status")
        invalid_snapshots.append(ordinary)

        for invalid in invalid_snapshots:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                render_review_snapshot(invalid, width=80)

    def test_materially_identical_or_authority_widening_options_are_rejected(self) -> None:
        identical = [
            {"label": "A", "choice": "Approve", "consequence": "Continue"},
            {"label": "B", "choice": "Approve", "consequence": "Continue"},
        ]
        widening = [
            {"label": "A", "choice": "Approve", "consequence": "Continue"},
            {
                "label": "B",
                "choice": "Approve and push to remote",
                "consequence": "Publish the unreviewed commit",
            },
        ]

        with self.assertRaises(ValueError):
            render_review_snapshot(snapshot(identical), width=80)
        with self.assertRaises(ValueError):
            render_review_snapshot(snapshot(widening), width=80)

    def test_authorization_review_requires_approve_change_and_reject_intents(self) -> None:
        incomplete = [
            {"label": "A", "choice": "Approve and continue", "consequence": "Start planning"},
            {"label": "C", "choice": "Reject and stop", "consequence": "Stop this change"},
        ]

        for approval_kind in ("Gate 1", "Gate 2", "Gate 3", "reopened gate", "named mutation"):
            with self.subTest(approval_kind=approval_kind), self.assertRaises(ValueError):
                render_review_snapshot(
                    snapshot(incomplete, approval_kind=approval_kind), width=80
                )

    def test_ordinary_interactions_bypass_human_review_options(self) -> None:
        for interaction in ("status", "clarification", "read-only report"):
            with self.subTest(interaction=interaction):
                self.assertFalse(requires_human_review(interaction))

        for interaction in (
            "design alternative selection",
            "Gate 1",
            "reopened gate",
            "named mutation",
        ):
            with self.subTest(interaction=interaction):
                self.assertTrue(requires_human_review(interaction))


if __name__ == "__main__":
    unittest.main()
