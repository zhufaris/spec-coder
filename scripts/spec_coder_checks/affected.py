"""Deterministic, explicit-path checks for a narrow spec-coder change.

This module deliberately does not inspect ``git diff`` or the working tree to
discover ownership. Its caller supplies every owned path, which is validated
before a stable path-to-check mapping is constructed.
"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import subprocess


_SKILL_CHECKS = {
    "spec-coder": (
        "test_runtime_envelope",
        "test_stage_loading",
        "test_implement_spec_executor",
        "test_implement_spec_runtime",
    ),
    "grill-coder": (
        "test_contracts",
        "test_discovery_question_batching",
        "test_stage_loading",
    ),
    "design-coder": ("test_contracts", "test_stage_loading"),
    "plan-coder": (
        "test_implement_spec_planning",
        "test_stage_loading",
        "test_workflow_tool_integration",
    ),
    "tdd-coder": (
        "test_contracts",
        "test_stage_loading",
        "test_implement_spec_runtime",
    ),
    "delivery-coder": (
        "test_contracts",
        "test_default_subagent_delivery",
        "test_implement_spec_runtime",
    ),
    "setup-coder": ("test_contracts", "test_forward_scenarios"),
    "show-me": ("test_human_review_options", "test_stage_loading"),
    "using-git-worktrees": (
        "test_contracts",
        "test_exact_base_worktree",
        "test_forward_scenarios",
        "test_implement_spec_runtime",
        "test_workspace_policy",
    ),
}
_OWNER_CHECKS = {
    "references/workflow-contract.md": (
        "test_runtime_envelope",
        "test_stage_loading",
        "test_implement_spec_executor",
        "test_implement_spec_runtime",
    ),
    "references/setup-contract.md": (
        "test_contracts",
        "test_forward_scenarios",
    ),
    "assets/agents-snippet.md": (
        "test_contracts",
        "test_forward_scenarios",
    ),
    "references/subagent-routing-contract.md": (
        "test_default_subagent_execution",
        "test_parallel_request_scenarios",
        "test_implement_spec_runtime",
    ),
    "references/artifact-format.md": (
        "test_artifact_checker",
        "test_implement_spec_planning",
        "test_workflow_tool_integration",
    ),
    "scripts/check-artifacts.py": (
        "test_artifact_checker",
        "test_workflow_tool_integration",
    ),
    "scripts/spec_coder_checks/artifacts.py": (
        "test_artifact_checker",
        "test_workflow_tool_integration",
    ),
    "scripts/spec_coder_checks/waves.py": (
        "test_artifact_checker",
        "test_implement_spec_executor",
        "test_parallel_request_scenarios",
    ),
    "references/specification-template.md": (
        "test_artifact_checker",
        "test_workflow_tool_integration",
    ),
    "references/ticket-template.md": (
        "test_implement_spec_planning",
        "test_workflow_tool_integration",
    ),
    "references/worker-brief-template.md": (
        "test_worker_heartbeat",
        "test_default_subagent_execution",
        "test_implement_spec_runtime",
        "test_stage_loading",
    ),
    "references/verification-contract.md": (
        "test_verification_evidence",
        "test_workflow_tool_integration",
    ),
    "scripts/verification-evidence.py": (
        "test_verification_evidence",
        "test_workflow_tool_integration",
    ),
    "scripts/spec_coder_checks/evidence.py": (
        "test_verification_evidence",
        "test_workflow_tool_integration",
    ),
    "scripts/validate-affected.py": ("test_affected_validation",),
    "scripts/spec_coder_checks/affected.py": ("test_affected_validation",),
    "scripts/workspace-policy.py": ("test_workspace_policy",),
    "scripts/spec_coder_checks/workspace_policy.py": ("test_workspace_policy",),
    "scripts/progress-snapshot.py": ("test_progress_snapshot",),
    "scripts/task-step.py": ("test_task_step", "test_three_layer_architecture", "test_stage_loading"),
    "scripts/spec_coder_checks/progress.py": ("test_progress_snapshot",),
    "tests/forward_contracts.py": (
        "test_autonomous_workflow",
        "test_discovery_question_batching",
        "test_exact_base_worktree",
        "test_forward_scenarios",
        "test_human_review_options",
        "test_implement_spec_executor",
        "test_parallel_request_scenarios",
        "test_worker_heartbeat",
    ),
    "tests/design_contracts.py": ("test_design_governance",),
    "tests/fixtures/scenarios.md": (
        "test_autonomous_workflow",
        "test_contracts",
    ),
    "README.md": ("test_contracts",),
    "INSTALL.md": ("test_contracts",),
    "references/approval-review-contract.md": (
        "test_human_review_options",
        "test_forward_scenarios",
    ),
    "references/domain-design-contract.md": ("test_contracts",),
    "references/domain-design-examples.md": ("test_contracts",),
    "references/task-playbook-contract.md": (
        "test_task_playbooks",
        "test_affected_validation",
    ),
    "tests/task_playbook_contracts.py": ("test_task_playbooks",),
    "tests/fixtures/task-playbook-scenarios.md": ("test_task_playbooks",),
    "tests/task_playbook_eval_contracts.py": ("test_task_playbook_eval",),
    "tests/fixtures/task-playbook-eval-scenarios.md": ("test_task_playbook_eval",),
    "THIRD_PARTY_NOTICES.md": ("test_task_playbooks",),
    "references/upstream-compatibility.md": (
        "test_contracts",
        "test_autonomous_workflow",
        "test_stage_loading",
    ),
}
_SHARED_ROUTING_CHECKS = (
    "test_default_subagent_execution",
    "test_parallel_request_scenarios",
    "test_implement_spec_runtime",
)
_SHARED_ROUTING_SKILLS = ("spec-coder", "tdd-coder", "delivery-coder")
_ROUTING_PATH = "references/subagent-routing-contract.md"


# Explicit owners: task SOPs, stage SOPs, and triggered principles ship with the bundle.
for _task in ("feature", "bug-fix", "refactor", "performance", "skill-change", "workflow-eval", "generic"):
    _OWNER_CHECKS[f"playbooks/tasks/{_task}.md"] = ("test_three_layer_architecture", "test_task_playbooks", "test_stage_loading")
for _stage, _skill in (("discovery", "grill-coder"), ("design", "design-coder"), ("planning", "plan-coder"), ("implementation", "tdd-coder"), ("delivery", "delivery-coder")):
    _OWNER_CHECKS[f"playbooks/stages/{_stage}.md"] = tuple(dict.fromkeys((*_SKILL_CHECKS[_skill], "test_three_layer_architecture", "test_stage_loading")))
for _principle in ("subtract-before-add", "model-the-domain", "dependency-direction", "verify-real-outcome", "preserve-observable-behavior", "protect-human-authority", "guard-context", "encode-lessons", "attack-the-premise", "explain-the-number", "minimize-reader-load"):
    _OWNER_CHECKS[f"principles/{_principle}.md"] = ("test_three_layer_architecture", "test_stage_loading")

def _physical_repo(repo: Path) -> Path:
    root = Path(repo).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("--repo must be an existing directory")
    return root


def _safe_paths(repo: Path, paths: Iterable[str]) -> tuple[str, ...]:
    """Validate paths then return normalized repository-relative names."""
    normalized = set()
    for raw in paths:
        if not isinstance(raw, str) or not raw:
            raise ValueError("paths must be nonempty repository-relative strings")
        candidate = Path(raw)
        raw_parts = raw.split("/")
        if (
            candidate.is_absolute()
            or any(part in {"", ".", "..", ".git"} for part in raw_parts)
            or any(part in {".git"} for part in candidate.parts)
        ):
            raise ValueError(
                "paths must be exact repository-relative paths without traversal"
            )
        if any(any(char in part for char in "*?[]") for part in candidate.parts):
            raise ValueError("paths must not contain glob syntax")
        location = repo / candidate
        try:
            resolved = location.resolve(strict=True)
            relative = resolved.relative_to(repo)
        except (OSError, RuntimeError, ValueError) as exc:
            raise ValueError(
                "path must exist inside the physical repository: " + raw
            ) from exc
        probe = repo
        for part in candidate.parts:
            probe = probe / part
            if probe.is_symlink():
                raise ValueError("path must not traverse a symlink: " + raw)
        normalized.add(relative.as_posix())
    if not normalized:
        raise ValueError("at least one explicit path is required")
    return tuple(sorted(normalized))


def build_affected_commands(
    repo: Path, paths: Iterable[str], python_bin: str, validator: str
) -> tuple[dict, ...]:
    """Build stable subprocess vectors for explicitly supplied paths only."""
    root = _physical_repo(repo)
    safe_paths = _safe_paths(root, paths)
    modules: set[str] = set()
    skills: set[str] = set()

    for path in safe_paths:
        parts = Path(path).parts
        matched = False
        if len(parts) >= 2 and parts[0] == "skills" and parts[1] in _SKILL_CHECKS:
            skill = parts[1]
            modules.update(_SKILL_CHECKS[skill])
            skills.add(skill)
            matched = True
        owner_checks = _OWNER_CHECKS.get(path, ())
        if owner_checks:
            modules.update(owner_checks)
            matched = True
        if path == _ROUTING_PATH:
            modules.update(_SHARED_ROUTING_CHECKS)
            skills.update(_SHARED_ROUTING_SKILLS)
            matched = True
        if (
            len(parts) == 2
            and parts[0] == "tests"
            and parts[1].startswith("test_")
            and parts[1].endswith(".py")
        ):
            modules.add(Path(parts[1]).stem)
            matched = True
        if not matched:
            raise ValueError("unmapped affected path: " + path)

    commands = [
        {
            "argv": (
                python_bin,
                "-B",
                "-m",
                "unittest",
                "discover",
                "-v",
                "-s",
                "tests",
                "-p",
                module + ".py",
            ),
            "cwd": str(root),
            "kind": "unittest",
        }
        for module in sorted(modules)
    ]
    commands.extend(
        {
            "argv": (python_bin, validator, "skills/" + skill),
            "cwd": str(root),
            "kind": "skill-validator",
        }
        for skill in sorted(skills)
    )
    commands.append(
        {"argv": ("git", "diff", "--check"), "cwd": str(root), "kind": "diff-check"}
    )
    return tuple(commands)


def execute_affected_commands(commands, runner=subprocess.run) -> dict:
    """Run vectors in order, recording each result and stopping on failure."""
    planned_commands = [
        {**command, "argv": list(tuple(command["argv"]))} for command in commands
    ]
    recorded_commands = []
    results = []
    exit_code = 0
    for command in commands:
        argv = tuple(command["argv"])
        cwd = command["cwd"]
        recorded_commands.append({**command, "argv": list(argv)})
        try:
            completed = runner(
                argv, cwd=cwd, shell=False, capture_output=True, text=True
            )
            code = completed.returncode
            result = {"argv": list(argv), "cwd": cwd, "exit_code": code}
            if getattr(completed, "stdout", None):
                result["stdout"] = completed.stdout
            if getattr(completed, "stderr", None):
                result["stderr"] = completed.stderr
        except OSError as exc:
            code = 1
            result = {
                "argv": list(argv),
                "cwd": cwd,
                "exit_code": code,
                "error": str(exc),
            }
        results.append(result)
        if code:
            exit_code = code
            break
    return {
        "exit_code": exit_code,
        "planned_commands": planned_commands,
        "commands": recorded_commands,
        "results": results,
    }
