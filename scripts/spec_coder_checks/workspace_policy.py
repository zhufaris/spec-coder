"""Pure workspace-policy rules over explicit observations.

This inner module never observes Git or the filesystem.  Adapters supply
physical paths, file bytes, and Git command results; the rules return frozen
facts whose ``as_json`` methods materialize the public compact JSON shapes.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import posixpath


GENERATED_IGNORE_ENTRIES = (b"/.worktrees/\n", b"/.cache/\n")
GENERATED_ROOTS = (".worktrees/", ".cache/")


class PolicyBlocker(ValueError):
    """An explicit observation that must fail closed rather than be guessed."""

    def __init__(self, reason: str, **details: object) -> None:
        super().__init__(reason)
        self.reason = reason
        self.details = tuple(details.items())

    def as_json(self) -> dict[str, object]:
        return {"status": "blocked", "reason": self.reason, **dict(self.details)}


@dataclass(frozen=True)
class WorkspacePaths:
    source_worktree: str
    build_cache: str


@dataclass(frozen=True)
class WorkspaceFacts:
    repository: str
    source_worktree: str
    build_cache: str
    ignore: tuple[tuple[str, str], ...]

    def as_json(self) -> dict[str, object]:
        return {
            "status": "accepted",
            "repository": self.repository,
            "source_worktree": self.source_worktree,
            "build_cache": self.build_cache,
            "ignore": dict(self.ignore),
        }


@dataclass(frozen=True)
class AllocationFacts:
    repository: str
    workspace: str
    actual_head: str
    recorded_base: str

    def as_json(self) -> dict[str, object]:
        return {
            "status": "accepted",
            "repository": self.repository,
            "workspace": self.workspace,
            "actual_head": self.actual_head,
            "recorded_base": self.recorded_base,
        }


@dataclass(frozen=True)
class IgnoreProposal:
    gitignore_exists: bool
    missing_entries: tuple[str, ...]
    changed: bool
    original_sha256: str
    proposed_sha256: str
    proposed_bytes_base64: str

    def as_json(self) -> dict[str, object]:
        return {
            "status": "accepted",
            "gitignore_exists": self.gitignore_exists,
            "missing_entries": list(self.missing_entries),
            "changed": self.changed,
            "original_sha256": self.original_sha256,
            "proposed_sha256": self.proposed_sha256,
            "proposed_bytes_base64": self.proposed_bytes_base64,
        }


def validate_branch(branch: str, returncode: int, stdout: str) -> tuple[str, ...]:
    """Apply Git-native and path-safety rules to an explicit Git observation."""
    if not isinstance(branch, str) or not branch:
        raise PolicyBlocker("invalid-branch", branch=branch)
    if returncode != 0 or stdout.strip() != branch:
        raise PolicyBlocker("invalid-branch", branch=branch)
    segments = tuple(branch.split("/"))
    if (
        not segments
        or any(not segment or segment in {".", ".."} for segment in segments)
        or any("\\" in segment or segment.startswith("~") for segment in segments)
    ):
        raise PolicyBlocker("unsafe-branch-path", branch=branch)
    return segments


def classify_ignore(returncode: int) -> str:
    """Classify the documented ``git check-ignore -q`` return codes."""
    if returncode == 0:
        return "ignored"
    if returncode == 1:
        return "not-ignored"
    return "uncertain"


def workspace_paths(
    repository: str,
    branch: str,
    branch_returncode: int,
    branch_stdout: str,
    observed_source_worktree: str,
    observed_build_cache: str,
) -> WorkspacePaths:
    """Validate physical generated paths derived by an outer adapter."""
    segments = validate_branch(branch, branch_returncode, branch_stdout)
    expected_source = posixpath.join(repository, ".worktrees", *segments)
    expected_cache = posixpath.join(repository, ".cache", *segments, "target")
    if (
        observed_source_worktree != expected_source
        or observed_build_cache != expected_cache
    ):
        raise PolicyBlocker("workspace-path-escapes-repository", branch=branch)
    return WorkspacePaths(expected_source, expected_cache)


def inspect(
    repository: str,
    branch: str,
    branch_returncode: int,
    branch_stdout: str,
    observed_source_worktree: str,
    observed_build_cache: str,
    ignore_returncodes: tuple[tuple[str, int], ...],
) -> WorkspaceFacts:
    paths = workspace_paths(
        repository,
        branch,
        branch_returncode,
        branch_stdout,
        observed_source_worktree,
        observed_build_cache,
    )
    observed_codes = dict(ignore_returncodes)
    observations = tuple(
        (root, classify_ignore(observed_codes.get(root, 2))) for root in GENERATED_ROOTS
    )
    if any(state == "uncertain" for _, state in observations):
        raise PolicyBlocker(
            "ignore-observation-uncertain",
            repository=repository,
            ignore=dict(observations),
        )
    return WorkspaceFacts(
        repository,
        paths.source_worktree,
        paths.build_cache,
        observations,
    )


def validate_allocation_path(
    repository: str,
    branch: str,
    branch_returncode: int,
    branch_stdout: str,
    observed_source_worktree: str,
    observed_build_cache: str,
    workspace: str,
    workspace_is_directory: bool,
) -> WorkspacePaths:
    """Validate allocation path/type before any workspace Git observation."""
    paths = workspace_paths(
        repository,
        branch,
        branch_returncode,
        branch_stdout,
        observed_source_worktree,
        observed_build_cache,
    )
    if workspace != paths.source_worktree:
        raise PolicyBlocker(
            "allocation-path-mismatch",
            workspace=workspace,
            expected_workspace=paths.source_worktree,
        )
    if not workspace_is_directory:
        raise PolicyBlocker("allocation-not-directory", workspace=workspace)
    return paths


def validate_allocation(
    repository: str,
    branch: str,
    branch_returncode: int,
    branch_stdout: str,
    observed_source_worktree: str,
    observed_build_cache: str,
    workspace: str,
    workspace_is_directory: bool,
    repository_common_git_directory: str,
    workspace_common_git_directory: str,
    actual_head: str,
    recorded_base: str,
) -> AllocationFacts:
    """Validate an allocation using only explicit physical and Git facts."""
    validate_allocation_path(
        repository,
        branch,
        branch_returncode,
        branch_stdout,
        observed_source_worktree,
        observed_build_cache,
        workspace,
        workspace_is_directory,
    )
    if workspace_common_git_directory != repository_common_git_directory:
        raise PolicyBlocker(
            "allocation-repository-mismatch",
            workspace=workspace,
            repository=repository,
        )
    if not actual_head:
        raise PolicyBlocker("allocation-head-unavailable", workspace=workspace)
    if not isinstance(recorded_base, str) or not recorded_base or actual_head != recorded_base:
        raise PolicyBlocker(
            "allocation-base-mismatch",
            workspace=workspace,
            actual_head=actual_head,
            recorded_base=recorded_base,
        )
    return AllocationFacts(repository, workspace, actual_head, recorded_base)


def cache_branch(repository: str, build_cache: str) -> str:
    """Return the branch encoded by a canonical physical cache reservation."""
    if not isinstance(build_cache, str) or not build_cache.strip():
        raise PolicyBlocker("build-cache-missing", build_cache=build_cache)
    if not posixpath.isabs(build_cache) or posixpath.normpath(build_cache) != build_cache:
        raise PolicyBlocker("build-cache-noncanonical", build_cache=build_cache)
    prefix = repository.rstrip("/") + "/"
    if not build_cache.startswith(prefix):
        raise PolicyBlocker("build-cache-outside-repository", build_cache=build_cache)
    relative = build_cache[len(prefix):]
    parts = tuple(relative.split("/"))
    if len(parts) < 3 or parts[0] != ".cache" or parts[-1] != "target":
        raise PolicyBlocker("build-cache-shape", build_cache=build_cache)
    return "/".join(parts[1:-1])


def validate_cache_reservation(
    repository: str,
    build_cache: str,
    resolved_build_cache: str,
    branch_returncode: int,
    branch_stdout: str,
    ignore_returncode: int,
    *,
    current_branch_returncode: int | None = None,
    current_branch_stdout: str | None = None,
) -> str:
    """Apply shared cache, branch, path, and ignore policy to observations."""
    branch = cache_branch(repository, build_cache)
    if resolved_build_cache != build_cache:
        raise PolicyBlocker("build-cache-noncanonical", build_cache=build_cache)
    segments = validate_branch(branch, branch_returncode, branch_stdout)
    expected = posixpath.join(repository, ".cache", *segments, "target")
    if build_cache != expected:
        raise PolicyBlocker(
            "build-cache-path-mismatch",
            build_cache=build_cache,
            expected_build_cache=expected,
        )
    ignore = classify_ignore(ignore_returncode)
    if ignore == "not-ignored":
        raise PolicyBlocker("build-cache-not-ignored", build_cache=build_cache)
    if ignore == "uncertain":
        raise PolicyBlocker("build-cache-ignore-uncertain", build_cache=build_cache)
    if current_branch_returncode is not None:
        current = (current_branch_stdout or "").strip()
        if current_branch_returncode != 0 or not current:
            raise PolicyBlocker("current-branch-unavailable")
        current_segments = tuple(current.split("/"))
        if any(not segment or segment in {".", ".."} for segment in current_segments):
            raise PolicyBlocker("current-branch-unavailable")
        expected_current = posixpath.join(
            repository, ".cache", *current_segments, "target"
        )
        if build_cache != expected_current:
            raise PolicyBlocker(
                "build-cache-current-branch-mismatch",
                build_cache=build_cache,
                expected_build_cache=expected_current,
            )
    return build_cache


def _has_exact_entry(content: bytes, entry: bytes) -> bool:
    target = entry.rstrip(b"\n")
    return any(line.rstrip(b"\r\n") == target for line in content.splitlines(keepends=True))


def propose_ignore(content: bytes | None) -> IgnoreProposal:
    """Return an exact, non-mutating ignore proposal preserving user bytes."""
    exists = content is not None
    original = content if content is not None else b""
    missing = tuple(
        entry for entry in GENERATED_IGNORE_ENTRIES if not _has_exact_entry(original, entry)
    )
    additions = b"".join(missing)
    if not additions:
        proposed = original
    elif not original or original.endswith((b"\n", b"\r")):
        proposed = original + additions
    else:
        proposed = additions + original
    return IgnoreProposal(
        exists,
        tuple(entry.decode("ascii") for entry in missing),
        proposed != original,
        hashlib.sha256(original).hexdigest(),
        hashlib.sha256(proposed).hexdigest(),
        base64.b64encode(proposed).decode("ascii"),
    )
