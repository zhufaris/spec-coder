import ast
import json
import base64
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "workspace-policy.py"
sys.path.insert(0, str(ROOT / "scripts"))


class WorkspacePolicyCliTests(unittest.TestCase):
    def run_cli(self, *arguments, cwd=None, env=None):
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
        )

    def test_policy_core_has_no_git_or_filesystem_adapters(self):
        module_path = ROOT / "scripts" / "spec_coder_checks" / "workspace_policy.py"
        source = module_path.read_text()
        tree = ast.parse(source)
        imported = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )

        self.assertTrue({"subprocess", "pathlib"}.isdisjoint(imported))
        self.assertNotIn("read_bytes", source)
        self.assertNotIn("subprocess.run", source)

        cli = CLI.read_text()
        self.assertIn("subprocess.run", cli)
        self.assertIn("read_bytes", cli)

    def test_inspect_returns_repository_local_paths_and_ignore_facts(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            (repo / ".gitignore").write_text("/.worktrees/\n/.cache/\n")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

            result = self.run_cli(
                "inspect", "--repo", str(repo), "--branch", "feat/api", cwd=Path(temporary)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            facts = json.loads(result.stdout)
            self.assertEqual(facts["status"], "accepted")
            self.assertEqual(
                facts["source_worktree"],
                str(repo / ".worktrees" / "feat" / "api"),
            )
            self.assertEqual(
                facts["build_cache"],
                str(repo / ".cache" / "feat" / "api" / "target"),
            )
            self.assertEqual(facts["ignore"][".worktrees/"], "ignored")
            self.assertEqual(facts["ignore"][".cache/"], "ignored")

    def test_invalid_git_ref_is_a_structured_policy_blocker(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            result = self.run_cli("inspect", "--repo", str(repo), "--branch", "feat//bad")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["reason"], "invalid-branch")

    def test_missing_repository_is_a_structured_policy_blocker(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing"
            result = self.run_cli(
                "inspect", "--repo", str(missing), "--branch", "feat/api"
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["reason"], "repository-unavailable")

    def test_argparse_error_exits_two_without_success_json(self):
        result = self.run_cli("inspect", "--branch", "feat/api")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("usage:", result.stderr)
        self.assertNotIn('"status":"accepted"', result.stderr)

    def test_symlinked_repository_argument_reports_physical_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            (repo / ".gitignore").write_text("/.worktrees/\n/.cache/\n")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            link = Path(temporary) / "repo-link"
            link.symlink_to(repo, target_is_directory=True)
            result = self.run_cli("inspect", "--repo", str(link), "--branch", "feat/api")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["repository"], str(repo))

    def test_generated_workspace_symlinks_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for generated in (".worktrees", ".cache"):
                with self.subTest(generated=generated):
                    repo = root / ("repo-" + generated.removeprefix("."))
                    repo.mkdir()
                    (repo / ".gitignore").write_text("/.worktrees/\n/.cache/\n")
                    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
                    outside = root / ("outside-" + generated.removeprefix("."))
                    outside.mkdir()
                    (repo / generated).symlink_to(outside, target_is_directory=True)
                    result = self.run_cli(
                        "inspect", "--repo", str(repo), "--branch", "feat/api"
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["reason"],
                        "workspace-path-escapes-repository",
                    )

    def test_real_cli_uncertain_git_ignore_observation_blocks_inspection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            (repo / ".gitignore").write_text("/.worktrees/\n/.cache/\n")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            adapter_dir = root / "bin"
            adapter_dir.mkdir()
            adapter = adapter_dir / "git"
            real_git = shutil.which("git")
            self.assertIsNotNone(real_git)
            adapter.write_text(
                "#!/usr/bin/env python3\n"
                "import os, sys\n"
                f"real_git = {real_git!r}\n"
                "if 'check-ignore' in sys.argv[1:]:\n"
                "    raise SystemExit(128)\n"
                "os.execv(real_git, [real_git, *sys.argv[1:]])\n"
            )
            adapter.chmod(0o755)
            env = dict(os.environ)
            env["PATH"] = str(adapter_dir) + os.pathsep + env["PATH"]
            result = self.run_cli(
                "inspect",
                "--repo",
                str(repo),
                "--branch",
                "feat/api",
                env=env,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["reason"], "ignore-observation-uncertain")
            self.assertEqual(payload["ignore"][".worktrees/"], "uncertain")

    def test_proposal_prepends_when_existing_bytes_lack_a_terminator(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            original = "user-pattern".encode("utf-8") + bytes([0xE9])
            (repo / ".gitignore").write_bytes(original)
            result = self.run_cli("propose-ignore", "--repo", str(repo))
            self.assertEqual(result.returncode, 0, result.stderr)
            proposal = json.loads(result.stdout)
            self.assertEqual(
                base64.b64decode(proposal["proposed_bytes_base64"]),
                b"/.worktrees/\n/.cache/\n" + original,
            )
            self.assertEqual((repo / ".gitignore").read_bytes(), original)

    def test_proposal_blocks_outside_and_dangling_gitignore_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            outside = root / "outside-ignore"
            outside.write_bytes(b"outside\n")
            ignore = repo / ".gitignore"
            ignore.symlink_to(outside)
            escaped = self.run_cli("propose-ignore", "--repo", str(repo))
            self.assertEqual(escaped.returncode, 1)
            self.assertEqual(json.loads(escaped.stdout)["reason"], "gitignore-symlink-escapes-repository")
            ignore.unlink()
            ignore.symlink_to(root / "missing-ignore")
            dangling = self.run_cli("propose-ignore", "--repo", str(repo))
            self.assertEqual(dangling.returncode, 1)
            self.assertEqual(json.loads(dangling.stdout)["reason"], "gitignore-symlink-unavailable")

    def test_validate_allocation_requires_canonical_path_and_exact_head(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            (repo / ".gitignore").write_text("/.worktrees/\n/.cache/\n")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "policy@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Policy"], cwd=repo, check=True)
            (repo / "tracked").write_text("tracked\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "initial"], cwd=repo, check=True)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True).stdout.strip()
            workspace = repo / ".worktrees" / "feat" / "api"
            subprocess.run(["git", "worktree", "add", "-q", "-b", "feat/api", str(workspace), head], cwd=repo, check=True)
            accepted = self.run_cli("validate-allocation", "--repo", str(repo), "--branch", "feat/api", "--workspace", str(workspace), "--recorded-base", head)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            blocked = self.run_cli("validate-allocation", "--repo", str(repo), "--branch", "feat/api", "--workspace", str(workspace), "--recorded-base", "not-the-head")
            self.assertEqual(blocked.returncode, 1)
            self.assertEqual(json.loads(blocked.stdout)["reason"], "allocation-base-mismatch")


if __name__ == "__main__":
    unittest.main()
