"""Deterministic, read-only workspace policy facts.

The functions in this module accept explicit inputs and return JSON-ready
values.  They deliberately do not create worktrees, write ignore files, or
perform recovery actions.  The command-line adapter supplies Git and file
observations so callers can test the policy without ambient process state.
"""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import asdict, dataclass
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

GENERATED_IGNORE_ENTRIES = (b"/.worktrees/\n", b"/.cache/\n")


class PolicyBlocker(ValueError):
    """An observation that must fail closed rather than be guessed."""

    def __init__(self, reason: str, **details: object) -> None:
        super().__init__(reason)
        self.reason = reason
        self.details = details

    def as_json(self) -> dict[str, object]:
        return {"status": "blocked", "reason": self.reason, **self.details}


@dataclass(frozen=True)
class WorkspaceFacts:
    repository: str
    source_worktree: str
    build_cache: str
    ignore: dict[str, str]

    def as_json(self) -> dict[str, object]:
        return {"status": "accepted", **asdict(self)}


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
        raise PolicyBlocker("git-observation-unavailable", repository=str(repo)) from exc


def physical_repository(repo: str | os.PathLike[str]) -> Path:
    """Return a physical Git worktree root, rejecting nested directories."""
    try:
        root = Path(repo).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker("repository-unavailable", repository=os.fspath(repo)) from exc
    if not root.is_dir():
        raise PolicyBlocker("repository-not-directory", repository=str(root))
    observed = _run_git(root, "rev-parse", "--show-toplevel")
    if observed.returncode:
        raise PolicyBlocker("repository-not-git", repository=str(root))
    try:
        top_level = Path(os.fsdecode(observed.stdout).strip()).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker("repository-identity-unavailable", repository=str(root)) from exc
    if top_level != root:
        raise PolicyBlocker(
            "repository-not-worktree-root", repository=str(root), worktree_root=str(top_level)
        )
    return root


def validate_branch(branch: str) -> tuple[str, ...]:
    """Validate the Git ref using Git, then make it safe to map to a path."""
    if not isinstance(branch, str) or not branch:
        raise PolicyBlocker("invalid-branch", branch=branch)
    try:
        checked = subprocess.run(
            ("git", "check-ref-format", "--branch", branch),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise PolicyBlocker("branch-validation-unavailable", branch=branch) from exc
    if checked.returncode:
        raise PolicyBlocker("invalid-branch", branch=branch)
    segments = tuple(branch.split("/"))
    if (
        not segments
        or any(not segment or segment in {".", ".."} for segment in segments)
        or any("\\" in segment or segment.startswith("~") for segment in segments)
    ):
        raise PolicyBlocker("unsafe-branch-path", branch=branch)
    return segments


def workspace_paths(repository: Path, branch: str) -> tuple[Path, Path]:
    """Derive canonical durable paths after Git-native branch validation."""
    segments = validate_branch(branch)
    source = repository.joinpath(".worktrees", *segments).resolve(strict=False)
    cache = repository.joinpath(".cache", *segments, "target").resolve(strict=False)
    try:
        source.relative_to(repository)
        cache.relative_to(repository)
    except ValueError as exc:
        raise PolicyBlocker("workspace-path-escapes-repository", branch=branch) from exc
    return source, cache


def ignore_observations(repository: Path) -> dict[str, str]:
    """Observe exactly the two generated roots, never infer ignore state."""
    observations: dict[str, str] = {}
    for root in (".worktrees/", ".cache/"):
        result = _run_git(repository, "check-ignore", "-q", "--", root)
        if result.returncode == 0:
            state = "ignored"
        elif result.returncode == 1:
            state = "not-ignored"
        else:
            state = "uncertain"
        observations[root] = state
    return observations


def inspect(repository: str | os.PathLike[str], branch: str) -> WorkspaceFacts:
    root = physical_repository(repository)
    source, cache = workspace_paths(root, branch)
    observations = ignore_observations(root)
    if "uncertain" in observations.values():
        raise PolicyBlocker(
            "ignore-observation-uncertain", repository=str(root), ignore=observations
        )
    return WorkspaceFacts(str(root), str(source), str(cache), observations)


def _common_git_directory(worktree: Path) -> Path:
    result = _run_git(worktree, "rev-parse", "--git-common-dir")
    if result.returncode:
        raise PolicyBlocker("allocation-git-identity-unavailable", workspace=str(worktree))
    value = Path(os.fsdecode(result.stdout).strip())
    if not value.is_absolute():
        value = worktree / value
    try:
        return value.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker("allocation-git-identity-unavailable", workspace=str(worktree)) from exc


def validate_allocation(
    repository: str | os.PathLike[str], branch: str, workspace: str | os.PathLike[str], recorded_base: str
) -> dict[str, object]:
    """Accept only a physical, canonical worktree at the recorded commit."""
    root = physical_repository(repository)
    expected, _ = workspace_paths(root, branch)
    try:
        actual = Path(workspace).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PolicyBlocker("allocation-workspace-unavailable", workspace=os.fspath(workspace)) from exc
    if actual != expected:
        raise PolicyBlocker(
            "allocation-path-mismatch", workspace=str(actual), expected_workspace=str(expected)
        )
    if not actual.is_dir():
        raise PolicyBlocker("allocation-not-directory", workspace=str(actual))
    if _common_git_directory(actual) != _common_git_directory(root):
        raise PolicyBlocker("allocation-repository-mismatch", workspace=str(actual), repository=str(root))
    head = _run_git(actual, "rev-parse", "HEAD")
    actual_head = os.fsdecode(head.stdout).strip()
    if head.returncode or not actual_head:
        raise PolicyBlocker("allocation-head-unavailable", workspace=str(actual))
    if not isinstance(recorded_base, str) or not recorded_base or actual_head != recorded_base:
        raise PolicyBlocker(
            "allocation-base-mismatch",
            workspace=str(actual),
            actual_head=actual_head,
            recorded_base=recorded_base,
        )
    return {
        "status": "accepted",
        "repository": str(root),
        "workspace": str(actual),
        "actual_head": actual_head,
        "recorded_base": recorded_base,
    }


def _has_exact_entry(content: bytes, entry: bytes) -> bool:
    target = entry.rstrip(b"\n")
    return any(line.rstrip(b"\r\n") == target for line in content.splitlines(keepends=True))


def propose_ignore(content: bytes | None) -> dict[str, object]:
    """Return an exact, non-mutating ignore proposal preserving user bytes."""
    exists = content is not None
    original = content if content is not None else b""
    missing = tuple(entry for entry in GENERATED_IGNORE_ENTRIES if not _has_exact_entry(original, entry))
    additions = b"".join(missing)
    if not additions:
        proposed = original
    elif not original or original.endswith((b"\n", b"\r")):
        proposed = original + additions
    else:
        # Appending would turn the user's final pattern into a new pattern;
        # generated entries therefore precede a no-final-terminator file.
        proposed = additions + original
    return {
        "status": "accepted",
        "gitignore_exists": exists,
        "missing_entries": [os.fsdecode(entry) for entry in missing],
        "changed": proposed != original,
        "original_sha256": hashlib.sha256(original).hexdigest(),
        "proposed_sha256": hashlib.sha256(proposed).hexdigest(),
        "proposed_bytes_base64": base64.b64encode(proposed).decode("ascii"),
    }


def propose_ignore_for_repository(repository: str | os.PathLike[str]) -> dict[str, object]:
    root = physical_repository(repository)
    ignore_file = root / ".gitignore"
    try:
        if ignore_file.is_symlink():
            resolved_ignore = ignore_file.resolve(strict=True)
            resolved_ignore.relative_to(root)
            if not resolved_ignore.is_file():
                raise PolicyBlocker("gitignore-not-regular-file", repository=str(root))
            content = resolved_ignore.read_bytes()
        else:
            content = ignore_file.read_bytes() if ignore_file.exists() else None
    except PolicyBlocker:
        raise
    except ValueError as exc:
        raise PolicyBlocker("gitignore-symlink-escapes-repository", repository=str(root)) from exc
    except OSError as exc:
        raise PolicyBlocker("gitignore-symlink-unavailable", repository=str(root)) from exc
    return {"repository": str(root), **propose_ignore(content)}
