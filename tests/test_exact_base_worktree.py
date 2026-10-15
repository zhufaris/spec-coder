import unittest
from pathlib import Path

from forward_contracts import choose_isolation_route, git_worktree_add_args


ROOT = Path(__file__).resolve().parents[1]


class ExactBaseWorktreeTests(unittest.TestCase):
    def route(self, **overrides):
        inputs = {
            "linked_candidate": False,
            "superproject": False,
            "candidate_safe": False,
            "native_available": True,
            "native_can_pin_recorded_base": True,
            "git_fallback_safe": True,
            "local_ignore_status": 0,
        }
        inputs.update(overrides)
        return choose_isolation_route(**inputs)

    def test_compatible_native_is_selected(self):
        self.assertEqual(self.route(), "native")

    def test_incompatible_native_uses_safe_exact_base_git_fallback(self):
        self.assertEqual(
            self.route(native_can_pin_recorded_base=False),
            "git-local",
        )
        self.assertEqual(
            git_worktree_add_args(
                absolute_path="/tmp/spec-coder-t4",
                branch_name="feat/spec-coder-t4",
                wave_base="recorded-base-123",
            )[-1],
            "recorded-base-123",
        )

    def test_incompatible_native_and_unsafe_git_returns_blocker(self):
        self.assertEqual(
            self.route(
                native_can_pin_recorded_base=False,
                git_fallback_safe=False,
            ),
            "blocked-no-compatible-isolation",
        )

    def test_skill_requires_capability_and_post_allocation_base_validation(self):
        skill_path = ROOT / "skills/using-git-worktrees/SKILL.md"
        skill = skill_path.read_text().lower()
        self.assertIn(
            "../../references/workflow-contract.md#stage-runtime-envelope",
            skill,
        )
        for phrase in (
            "native availability",
            "recorded base",
            "validate",
            "actual",
            "incompatible",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)


if __name__ == "__main__":
    unittest.main()
