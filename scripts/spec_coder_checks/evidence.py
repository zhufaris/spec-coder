"""Versioned observations, build-cache policy, and baseline comparison."""
from datetime import datetime
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess

from . import workspace_policy


def parse_json(text):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON field: " + key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique_pairs)


def markdown_regions(text):
    """Yield active lines and fenced blocks, ignoring surrounding HTML comments."""
    fence = None
    language = ""
    payload = []
    in_comment = False
    for line in text.splitlines():
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line):
                yield "fence", language, "\n".join(payload)
                fence = None
            else:
                payload.append(line)
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if re.fullmatch(r"<!-- spec-coder:artifact-v1 (spec|plan) -->", line):
            yield "line", "", line
            continue
        if "<!--" in line:
            in_comment = "-->" not in line.split("<!--", 1)[1]
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            fence, language = match[1], match[2].strip()
            if language.startswith("spec-coder-verification") and language != "spec-coder-verification":
                raise ValueError("malformed spec-coder-verification fence label")
            payload = []
        else:
            yield "line", "", line
    if fence is not None and language == "spec-coder-verification":
        raise ValueError("unclosed spec-coder-verification record")


def is_active_artifact(text):
    return any(kind == "line" and re.fullmatch(r"<!-- spec-coder:artifact-v1 (spec|plan) -->", content)
               for kind, _, content in markdown_regions(text))


def read_records(text):
    records = [parse_json(content) for kind, language, content in markdown_regions(text)
               if kind == "fence" and language == "spec-coder-verification"]
    if not records:
        raise ValueError("missing spec-coder-verification record")
    return records


def unknown(value):
    return not isinstance(value, str) or not value.strip() or value.strip() == "?" or bool(re.search(r"\b(unknown|unconfirmed|unavailable)\b", value, re.IGNORECASE))


def _git(repository, *arguments):
    try:
        return subprocess.run(
            ["git", "--no-optional-locks", "-C", os.fspath(repository), *arguments],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError("build cache Git observation unavailable: " + str(error))


@dataclass(frozen=True)
class CacheObservations:
    repository: str
    build_cache: str
    resolved_build_cache: str
    branch_returncode: int
    branch_stdout: str
    ignore_returncode: int
    current_branch_returncode: int | None = None
    current_branch_stdout: str | None = None


def observe_cache_reservation(repository, value, *, current_branch=False):
    """Collect physical/Git observations without deciding cache policy."""
    try:
        worktree = Path(repository).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError("physical repository is unavailable: " + str(error))
    top = _git(worktree, "rev-parse", "--show-toplevel")
    common = _git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if top.returncode or common.returncode:
        raise ValueError("physical repository identity is unavailable")
    try:
        top_path = Path(top.stdout.strip()).resolve(strict=True)
        common_path = Path(common.stdout.strip()).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError("physical repository identity is unavailable: " + str(error))
    if worktree != top_path:
        raise ValueError("repository must name the Git worktree root")
    physical = common_path.parent if common_path.name == ".git" else top_path
    try:
        branch_name = workspace_policy.cache_branch(str(physical), value)
        resolved = Path(value).resolve(strict=False)
        relative = Path(value).relative_to(physical)
    except (OSError, RuntimeError) as error:
        raise ValueError("Build cache physical path is unavailable: " + str(error))
    except workspace_policy.PolicyBlocker as blocker:
        raise ValueError(cache_policy_error(blocker))
    branch = _git(top_path, "check-ref-format", "--branch", branch_name)
    ignored = _git(top_path, "check-ignore", "-q", "--", os.fspath(relative))
    current = (
        _git(top_path, "symbolic-ref", "--quiet", "--short", "HEAD")
        if current_branch
        else None
    )
    return CacheObservations(
        str(physical),
        value,
        str(resolved),
        branch.returncode,
        branch.stdout,
        ignored.returncode,
        current.returncode if current is not None else None,
        current.stdout if current is not None else None,
    )


def cache_policy_error(blocker):
    messages = {
        "build-cache-missing": "Build cache must be an explicit absolute path",
        "build-cache-noncanonical": (
            "Build cache must be canonical and must not contain symlinks or "
            "non-canonical components"
        ),
        "build-cache-outside-repository": (
            "Build cache must stay inside the physical repository"
        ),
        "build-cache-shape": (
            "Build cache must match <physical-repo>/.cache/<branch>/target"
        ),
        "invalid-branch": "Build cache branch is not a valid Git branch",
        "unsafe-branch-path": "Build cache branch is not a safe path",
        "build-cache-path-mismatch": (
            "Build cache must match <physical-repo>/.cache/<branch>/target"
        ),
        "build-cache-not-ignored": "Build cache reservation is not Git-ignored",
        "build-cache-ignore-uncertain": "Build cache ignore status is unavailable",
        "current-branch-unavailable": "current workspace branch identity is unavailable",
    }
    if blocker.reason == "build-cache-current-branch-mismatch":
        return "Build cache must equal " + dict(blocker.details)["expected_build_cache"]
    return messages.get(blocker.reason, blocker.reason)


def apply_cache_policy(observations):
    try:
        return workspace_policy.validate_cache_reservation(
            observations.repository,
            observations.build_cache,
            observations.resolved_build_cache,
            observations.branch_returncode,
            observations.branch_stdout,
            observations.ignore_returncode,
            current_branch_returncode=observations.current_branch_returncode,
            current_branch_stdout=observations.current_branch_stdout,
        )
    except workspace_policy.PolicyBlocker as blocker:
        raise ValueError(cache_policy_error(blocker))


def validate_plan_build_cache(repository, value):
    """Accept any canonical ignored reservation for a Git-valid ticket branch."""
    return apply_cache_policy(observe_cache_reservation(repository, value))


def validate_build_cache(repository, value):
    """Accept only the current workspace branch's safe cache reservation."""
    return apply_cache_policy(
        observe_cache_reservation(repository, value, current_branch=True)
    )


def context_reasons(context):
    reasons = []
    if unknown(context.get("request")):
        reasons.append("current request identity is unknown")
    for name in ["toolchain", "dependencies", "environment"]:
        value = context.get(name)
        if not isinstance(value, dict):
            reasons.append(name + " observations must be a JSON object")
            continue
        if name != "environment" and not value:
            reasons.append(name + " observations are unknown")
        for key, observation in value.items():
            if not key or (unknown(observation) and not (name == "environment" and observation == "")):
                reasons.append(name + " observation is unknown or invalid: " + key)
        if name == "dependencies" and not {"installed", "external"}.issubset(value):
            reasons.append("dependencies require explicit installed and external observations")
    return reasons


def compare(record, context, current):
    if not isinstance(record, dict) or type(record.get("version")) is not int or record["version"] != 1:
        return ["malformed or unsupported verification record"]
    required = {"context", "before", "after", "exit_code", "observed_at", "status", "reasons", "record_id"}
    if not required.issubset(record):
        return ["incomplete verification record"]
    if not isinstance(record["record_id"], str) or not re.fullmatch(r"[0-9a-f]{32}", record["record_id"]):
        return ["missing or invalid record identity"]
    if not isinstance(record["context"], dict) or (record["exit_code"] is not None and type(record["exit_code"]) is not int) or not isinstance(record["reasons"], list) or not all(isinstance(reason, str) for reason in record["reasons"]):
        return ["malformed verification record"]
    try:
        if not isinstance(record["observed_at"], str) or datetime.fromisoformat(record["observed_at"]).tzinfo is None:
            raise ValueError("missing timezone")
    except ValueError:
        return ["invalid observation time"]
    reasons = context_reasons(context)
    if record["status"] != "captured" or record["reasons"]:
        reasons.append("record does not declare a stable successful capture")
    if record["exit_code"] != 0:
        reasons.append("baseline command did not succeed")
    for key in sorted(set(record["context"]) | set(context)):
        if record["context"].get(key) != context.get(key):
            reasons.append("declared execution context changed: " + key)
    if record["before"] != record["after"]:
        reasons.append("workspace inputs changed during baseline execution")
    for snapshot in [record["before"], record["after"], current]:
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get("inputs"), dict) or not isinstance(snapshot.get("uncertainty"), list) or not all(isinstance(reason, str) for reason in snapshot["uncertainty"]):
            reasons.append("malformed workspace observation")
        elif snapshot["uncertainty"]:
            reasons.extend(snapshot["uncertainty"])
    if record["after"] != current:
        reasons.append("workspace inputs changed since baseline")
    return list(dict.fromkeys(reasons))
