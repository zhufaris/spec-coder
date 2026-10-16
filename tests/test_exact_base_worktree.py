import unittest
import subprocess
import tempfile
from pathlib import Path

from forward_contracts import (
    choose_isolation_route,
    git_worktree_add_args,
    repository_workspace_paths,
    validate_worktree_allocation,
)


ROOT = Path(__file__).resolve().parents[1]


class ExactBaseWorktreeTests(unittest.TestCase):
    def route(self, **overrides):
        inputs = {
            "linked_candidate": False,
            "superproject": False,
            "candidate_safe": False,
            "native_available": True,
            "native_can_pin_recorded_base": True,
            "native_can_pin_repository_path": True,
            "git_fallback_safe": True,
            "worktree_ignore_status": 0,
            "cache_ignore_status": 0,
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
                absolute_path="/repo/.worktrees/feat/spec-coder-t4",
                branch_name="feat/spec-coder-t4",
                wave_base="recorded-base-123",
            )[-1],
            "recorded-base-123",
        )

    def test_repository_paths_preserve_valid_branch_segments(self):
        self.assertEqual(
            repository_workspace_paths("/repo", "feat/api"),
            (
                "/repo/.worktrees/feat/api",
                "/repo/.cache/feat/api/target",
            ),
        )

    def test_repository_paths_reject_unsafe_branch_values(self):
        for branch in (
            "",
            "/absolute",
            "../escape",
            "feat/../escape",
            "feat//api",
            "feat\\api",
            "feat api",
            "~user/branch",
        ):
            with self.subTest(branch=branch), self.assertRaises(ValueError):
                repository_workspace_paths("/repo", branch)

    def test_repository_paths_require_an_absolute_physical_root(self):
        for repo_root in ("", "relative/repo", "~user/repo"):
            with self.subTest(repo_root=repo_root), self.assertRaises(ValueError):
                repository_workspace_paths(repo_root, "feat/api")

    def test_repository_paths_normalize_a_symlinked_physical_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            physical = Path(temporary) / "repo"
            physical.mkdir()
            linked = Path(temporary) / "repo-link"
            linked.symlink_to(physical, target_is_directory=True)

            self.assertEqual(
                repository_workspace_paths(str(linked), "feat/api"),
                (
                    str(physical / ".worktrees/feat/api"),
                    str(physical / ".cache/feat/api/target"),
                ),
            )

    def test_ignore_probes_are_anchored_when_called_from_a_subdirectory(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            (repo / ".gitignore").write_text("/.worktrees/\n/.cache/\n")
            (repo / "tests").mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

            for generated_root in (".worktrees/", ".cache/"):
                with self.subTest(generated_root=generated_root):
                    result = subprocess.run(
                        ["git", "-C", str(repo), "check-ignore", "-q", generated_root],
                        cwd=repo / "tests",
                    )
                    self.assertEqual(result.returncode, 0)

    def test_every_allocation_validates_actual_head_before_acceptance(self):
        self.assertEqual(
            validate_worktree_allocation(
                actual_head="recorded-base-123",
                recorded_base="recorded-base-123",
            ),
            "accept",
        )
        self.assertEqual(
            validate_worktree_allocation(
                actual_head="unexpected-head",
                recorded_base="recorded-base-123",
            ),
            "blocked-base-mismatch",
        )

    def test_native_must_pin_the_repository_local_source_path(self):
        self.assertEqual(
            self.route(native_can_pin_repository_path=False),
            "git-local",
        )

    def test_both_generated_roots_must_be_ignored(self):
        self.assertEqual(
            self.route(worktree_ignore_status=1),
            "blocked-local-policy-unignored",
        )
        self.assertEqual(
            self.route(cache_ignore_status=1),
            "blocked-local-policy-unignored",
        )
        self.assertEqual(
            self.route(cache_ignore_status=2),
            "blocked-ignore-verification",
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
