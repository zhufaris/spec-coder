"""Pure orchestration oracle for blinded task-playbook comparisons.

The oracle models ordering, disclosure, and fail-closed verdict rules. It does
not dispatch agents, read configuration, or persist workflow state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


ELIGIBLE_PLAYBOOKS = frozenset({"Skill Change", "Workflow Eval"})
FORBIDDEN_PROMPT_WORDS = frozenset(
    {"eval", "evaluation", "test", "judge", "benchmark", "candidate", "arena"}
)


class Verdict(str, Enum):
    KEEP_PARENT = "keep-parent"
    ACCEPT_CANDIDATE = "accept-candidate"


class LifecycleViolation(ValueError):
    """Raised when a proposed comparison would cross an orchestration fence."""


@dataclass(frozen=True)
class Environment:
    name: str
    base_revision: str
    inputs_digest: str
    isolated: bool = True
    sanitized: bool = True


@dataclass(frozen=True)
class CandidateRun:
    handle: str
    output: str
    direct_layer: int = 2
    delegation_allowed: bool = False
    must_not_spawn: bool = True
    spawned_children: int = 0


@dataclass(frozen=True)
class JudgePacket:
    outputs: tuple[tuple[str, str], ...]
    rubric: str
    direct_layer: int = 2
    delegation_allowed: bool = False
    must_not_spawn: bool = True
    identity_labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerdictEvidence:
    selected_playbook: str
    deterministic_green: bool
    gate_regression: bool = False
    authority_regression: bool = False
    dependency_regression: bool = False
    artifact_regression: bool = False
    context_budget_regression: bool = False
    all_outputs_read_by_main: bool = False
    available_transcripts_read_by_main: bool = False
    evidence_conclusive: bool = False
    evidence_conflicting: bool = False
    candidate_at_least_equal: bool = False
    critical_regression: bool = False


_BASE_SEQUENCE = (
    "deterministic-green",
    "prepare-equivalent-environments",
    "dispatch-direct-candidates",
    "collect-all-candidates",
)
_JUDGE_SEQUENCE = ("dispatch-direct-blinded-judge", "collect-judge")
_FINAL_SEQUENCE = ("main-inspect-all-evidence", "main-verdict")


def assert_eligible(selected_playbook: str, *, deterministic_green: bool) -> None:
    if selected_playbook not in ELIGIBLE_PLAYBOOKS:
        raise LifecycleViolation("selected playbook does not authorize workflow evaluation")
    if not deterministic_green:
        raise LifecycleViolation("mandatory deterministic checks must be green first")


def assert_equivalent_environments(
    parent: Environment, candidate: Environment
) -> None:
    if parent.name == candidate.name:
        raise LifecycleViolation("parent and candidate environments must be distinct")
    if not all(
        (parent.isolated, candidate.isolated, parent.sanitized, candidate.sanitized)
    ):
        raise LifecycleViolation("both environments must be isolated and sanitized")
    if (parent.base_revision, parent.inputs_digest) != (
        candidate.base_revision,
        candidate.inputs_digest,
    ):
        raise LifecycleViolation(
            "parent and candidate environments must have equivalent inputs"
        )


def assert_organic_prompt(prompt: str) -> None:
    words = {word.strip(".,:;!?()[]{}'\"").lower() for word in prompt.split()}
    leaked = sorted(words & FORBIDDEN_PROMPT_WORDS)
    if leaked:
        raise LifecycleViolation(f"comparison vocabulary leaked into organic prompt: {leaked}")


def assert_candidate_run(run: CandidateRun) -> None:
    if (
        run.direct_layer != 2
        or run.delegation_allowed
        or not run.must_not_spawn
        or run.spawned_children
    ):
        raise LifecycleViolation("candidate must be a direct no-spawn layer-2 child")


def make_judge_packet(*, outputs: tuple[str, ...], private_rubric: str) -> JudgePacket:
    if len(outputs) < 2 or not private_rubric.strip():
        raise LifecycleViolation("anonymous outputs and a private rubric are required")
    return JudgePacket(
        outputs=tuple(
            (f"Output {chr(65 + index)}", output)
            for index, output in enumerate(outputs)
        ),
        rubric=private_rubric,
    )


def assert_judge_packet(packet: JudgePacket) -> None:
    identity_text = " ".join(
        (*packet.identity_labels, *(label for label, _ in packet.outputs))
    ).lower()
    if "parent" in identity_text or "candidate" in identity_text:
        raise LifecycleViolation("judge packet exposes parent/candidate identity")
    if len(packet.outputs) < 2 or not packet.rubric.strip():
        raise LifecycleViolation("judge packet requires anonymous outputs and private rubric")
    if (
        packet.direct_layer != 2
        or packet.delegation_allowed
        or not packet.must_not_spawn
    ):
        raise LifecycleViolation("judge must be a direct no-spawn layer-2 child")


def assert_lifecycle(events: tuple[str, ...], *, use_judge: bool) -> None:
    expected = (
        _BASE_SEQUENCE + (_JUDGE_SEQUENCE if use_judge else ()) + _FINAL_SEQUENCE
    )
    if events != expected:
        raise LifecycleViolation("workflow evaluation events are out of sequence")


def author_verdict(evidence: VerdictEvidence) -> Verdict:
    """Return Candidate only when every deterministic and evidentiary fence holds."""
    if evidence.selected_playbook not in ELIGIBLE_PLAYBOOKS:
        return Verdict.KEEP_PARENT
    deterministic_regression = any(
        (
            not evidence.deterministic_green,
            evidence.gate_regression,
            evidence.authority_regression,
            evidence.dependency_regression,
            evidence.artifact_regression,
            evidence.context_budget_regression,
        )
    )
    evidence_failure = any(
        (
            not evidence.all_outputs_read_by_main,
            not evidence.available_transcripts_read_by_main,
            not evidence.evidence_conclusive,
            evidence.evidence_conflicting,
            not evidence.candidate_at_least_equal,
            evidence.critical_regression,
        )
    )
    if deterministic_regression or evidence_failure:
        return Verdict.KEEP_PARENT
    return Verdict.ACCEPT_CANDIDATE
