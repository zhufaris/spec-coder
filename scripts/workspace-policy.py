#!/usr/bin/env python3
"""Read-only JSON interface for deterministic workspace policy facts."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from spec_coder_checks import workspace_policy as policy  # noqa: E402


PolicyBlocker = policy.PolicyBlocker


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            ("git", "-C", os.fspath(repo), *args),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise PolicyBlocker(
            "git-observation-unavailable", repository=str(repo)
        ) from exc


def _physical_repository(value: str) -> Path:
    try:
        root = Path(value).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker("repository-unavailable", repository=value) from exc
    if not root.is_dir():
        raise PolicyBlocker("repository-not-directory", repository=str(root))
    observed = _run_git(root, "rev-parse", "--show-toplevel")
    if observed.returncode:
        raise PolicyBlocker("repository-not-git", repository=str(root))
    try:
        top_level = Path(os.fsdecode(observed.stdout).strip()).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker(
            "repository-identity-unavailable", repository=str(root)
        ) from exc
    if top_level != root:
        raise PolicyBlocker(
            "repository-not-worktree-root",
            repository=str(root),
            worktree_root=str(top_level),
        )
    return root


def _branch_observation(root: Path, branch: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return _run_git(root, "check-ref-format", "--branch", branch)
    except PolicyBlocker as blocker:
        if blocker.reason == "git-observation-unavailable":
            raise PolicyBlocker(
                "branch-validation-unavailable", branch=branch
            ) from blocker
        raise


def _generated_paths(
    root: Path, branch: str, branch_result: subprocess.CompletedProcess[bytes]
) -> tuple[Path, Path]:
    segments = policy.validate_branch(
        branch,
        branch_result.returncode,
        os.fsdecode(branch_result.stdout),
    )
    try:
        source = root.joinpath(".worktrees", *segments).resolve(strict=False)
        cache = root.joinpath(".cache", *segments, "target").resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker("workspace-path-unavailable", branch=branch) from exc
    return source, cache


def _inspect(repository: str, branch: str) -> policy.WorkspaceFacts:
    root = _physical_repository(repository)
    branch_result = _branch_observation(root, branch)
    source, cache = _generated_paths(root, branch, branch_result)
    ignore_returncodes = tuple(
        (generated, _run_git(root, "check-ignore", "-q", "--", generated).returncode)
        for generated in policy.GENERATED_ROOTS
    )
    return policy.inspect(
        str(root),
        branch,
        branch_result.returncode,
        os.fsdecode(branch_result.stdout),
        str(source),
        str(cache),
        ignore_returncodes,
    )


def _common_git_directory(worktree: Path) -> Path:
    result = _run_git(worktree, "rev-parse", "--git-common-dir")
    if result.returncode:
        raise PolicyBlocker(
            "allocation-git-identity-unavailable", workspace=str(worktree)
        )
    value = Path(os.fsdecode(result.stdout).strip())
    if not value.is_absolute():
        value = worktree / value
    try:
        return value.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker(
            "allocation-git-identity-unavailable", workspace=str(worktree)
        ) from exc


def _validate_allocation(
    repository: str, branch: str, workspace: str, recorded_base: str
) -> policy.AllocationFacts:
    root = _physical_repository(repository)
    branch_result = _branch_observation(root, branch)
    source, cache = _generated_paths(root, branch, branch_result)
    try:
        actual = Path(workspace).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker(
            "allocation-workspace-unavailable", workspace=workspace
        ) from exc
    policy.validate_allocation_path(
        str(root),
        branch,
        branch_result.returncode,
        os.fsdecode(branch_result.stdout),
        str(source),
        str(cache),
        str(actual),
        actual.is_dir(),
    )
    repository_common = _common_git_directory(root)
    workspace_common = _common_git_directory(actual)
    head = _run_git(actual, "rev-parse", "HEAD")
    actual_head = os.fsdecode(head.stdout).strip()
    if head.returncode:
        actual_head = ""
    return policy.validate_allocation(
        str(root),
        branch,
        branch_result.returncode,
        os.fsdecode(branch_result.stdout),
        str(source),
        str(cache),
        str(actual),
        actual.is_dir(),
        str(repository_common),
        str(workspace_common),
        actual_head,
        recorded_base,
    )


def _propose_ignore(repository: str) -> dict[str, object]:
    root = _physical_repository(repository)
    ignore_file = root / ".gitignore"
    try:
        if ignore_file.is_symlink():
            resolved_ignore = ignore_file.resolve(strict=True)
            resolved_ignore.relative_to(root)
            if not resolved_ignore.is_file():
                raise PolicyBlocker(
                    "gitignore-not-regular-file", repository=str(root)
                )
            content = resolved_ignore.read_bytes()
        else:
            content = ignore_file.read_bytes() if ignore_file.exists() else None
    except PolicyBlocker:
        raise
    except ValueError as exc:
        raise PolicyBlocker(
            "gitignore-symlink-escapes-repository", repository=str(root)
        ) from exc
    except OSError as exc:
        raise PolicyBlocker(
            "gitignore-symlink-unavailable", repository=str(root)
        ) from exc
    return {"repository": str(root), **policy.propose_ignore(content).as_json()}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subcommands.add_parser("inspect")
    inspect_parser.add_argument("--repo", required=True)
    inspect_parser.add_argument("--branch", required=True)
    allocation = subcommands.add_parser("validate-allocation")
    allocation.add_argument("--repo", required=True)
    allocation.add_argument("--branch", required=True)
    allocation.add_argument("--workspace", "--path", dest="workspace", required=True)
    allocation.add_argument("--recorded-base", required=True)
    proposal = subcommands.add_parser("propose-ignore")
    proposal.add_argument("--repo", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect":
            result = _inspect(args.repo, args.branch).as_json()
        elif args.command == "validate-allocation":
            result = _validate_allocation(
                args.repo, args.branch, args.workspace, args.recorded_base
            ).as_json()
        else:
            result = _propose_ignore(args.repo)
    except PolicyBlocker as blocker:
        print(json.dumps(blocker.as_json(), ensure_ascii=False, separators=(",", ":")))
        return 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
