import unittest

from forward_contracts import (
    BLOCKED,
    READY,
    WARNING,
    aggregate_status,
    apply_approved_setup,
    classify_managed_block,
    choose_isolation_route,
    propose_setup,
    render_review_snapshot,
)


START = b"<!-- spec-coder:start -->"
END = b"<!-- spec-coder:end -->"
CANONICAL = START + b"\nmanaged\n" + END + b"\n"


class SetupForwardScenarios(unittest.TestCase):
    def test_first_setup_then_no_op_rerun_preserves_existing_bytes(self) -> None:
        original = b"# Existing\r\n\r\nKeep this.\r\n"
        proposal = propose_setup(original, CANONICAL)
        before, after = proposal

        self.assertEqual(before, original)
        self.assertTrue(after.startswith(original))
        self.assertEqual(classify_managed_block(after, CANONICAL), "current")
        self.assertIsNone(propose_setup(after, CANONICAL))

    def test_first_setup_preserves_existing_final_newline_state(self) -> None:
        original = b"# Existing without final newline"
        _, after = propose_setup(original, CANONICAL)

        self.assertTrue(after.startswith(CANONICAL))
        self.assertTrue(after.endswith(original))
        self.assertFalse(after.endswith(b"\n"))

    def test_stale_replacement_preserves_marker_external_bytes(self) -> None:
        original = b"prefix\n" + START + b"\nold\n" + END + b"\nsuffix\n"
        proposal = propose_setup(original, CANONICAL)

        self.assertEqual(proposal[1], b"prefix\n" + CANONICAL + b"suffix\n")

    def test_malformed_and_duplicate_markers_block_without_a_proposal(self) -> None:
        malformed = b"prefix\n" + START + b"\nmissing end\n"
        nested = START + b"\n" + START + b"\n" + END + b"\n" + END + b"\n"
        later_nested = CANONICAL + nested
        duplicated = CANONICAL + CANONICAL

        self.assertEqual(classify_managed_block(malformed, CANONICAL), "malformed")
        self.assertEqual(classify_managed_block(nested, CANONICAL), "malformed")
        self.assertEqual(classify_managed_block(later_nested, CANONICAL), "malformed")
        self.assertEqual(classify_managed_block(duplicated, CANONICAL), "duplicated")
        with self.assertRaises(ValueError):
            propose_setup(malformed, CANONICAL)
        with self.assertRaises(ValueError):
            propose_setup(duplicated, CANONICAL)

    def test_marker_text_embedded_in_user_lines_is_not_a_managed_boundary(self) -> None:
        original = b"prefix " + START + b" suffix\nquoted " + END + b" text\n"

        self.assertEqual(classify_managed_block(original, CANONICAL), "absent")
        proposal = propose_setup(original, CANONICAL)
        self.assertTrue(proposal[1].startswith(original))
        self.assertTrue(proposal[1].endswith(CANONICAL))

    def test_concurrent_change_invalidates_approved_setup(self) -> None:
        proposal = propose_setup(b"base\n", CANONICAL)

        result = apply_approved_setup(proposal, b"base\nconcurrent\n")

        self.assertEqual(result[0], BLOCKED)
        self.assertIsNone(result[1])

    def test_required_blocker_dominates_safe_local_update(self) -> None:
        content = b"base\n"
        proposal = propose_setup(content, CANONICAL)
        applied = apply_approved_setup(proposal, content)

        self.assertEqual(applied[1], proposal[1])
        self.assertEqual(aggregate_status([READY, BLOCKED]), BLOCKED)
        self.assertEqual(aggregate_status([READY, WARNING]), WARNING)


class ApprovalForwardScenarios(unittest.TestCase):
    def test_grounded_unresolved_blocker_is_visible_in_linear_fallback(self) -> None:
        rendered = render_review_snapshot(
            {
                "approval_kind": "Gate 2",
                "artifact": "spec.md",
                "decisions": ["repository-local setup"],
                "blockers": ["Required capability is unresolved"],
                "approval_effect": "authorize ticket planning",
                "next_stage": "Gate 3",
            },
            width=40,
        )

        self.assertIn("Required capability is unresolved", rendered)
        self.assertIn("Gate 2 -> spec.md", rendered)
        self.assertIn("-> Gate 3", rendered)

    def test_missing_or_ungrounded_snapshot_data_stops_rendering(self) -> None:
        with self.assertRaises(ValueError):
            render_review_snapshot({"approval_kind": "Gate 1"}, width=80)


class WorktreeForwardScenarios(unittest.TestCase):
    def test_existing_linked_worktree_precedes_native_and_git_creation(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=False,
            candidate_safe=True,
            native_available=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "reuse-linked")

    def test_unsafe_linked_worktree_returns_conflict_without_nested_creation(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "linked-conflict")

    def test_submodule_does_not_count_as_linked_worktree(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=True,
            candidate_safe=True,
            native_available=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "native")

    def test_native_precedes_git_fallback(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "native")

    def test_unignored_local_path_returns_to_planning_for_mutation_free_path(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=False,
            local_ignore_status=1,
        )
        self.assertEqual(route, "plan-mutation-free-location")


if __name__ == "__main__":
    unittest.main()
