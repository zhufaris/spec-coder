"""Pure, deterministic test oracle for the Task Playbook Contract.

This models contract routes and evidence; it is not runtime scheduler state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PlaybookKind(str, Enum):
    FEATURE = "Feature"
    BUG_FIX = "Bug Fix"
    REFACTOR = "Refactor"
    PERFORMANCE = "Performance"
    SKILL_CHANGE = "Skill Change"
    WORKFLOW_EVAL = "Workflow Eval"
    GENERIC = "Generic"


@dataclass(frozen=True)
class TaskPlaybookSelection:
    kind: PlaybookKind
    entry_evidence: tuple[str, ...]
    design_obligations: tuple[str, ...]
    red_or_pin: str
    delivery_proof: str
    conditional_references: tuple[str, ...]


_PROOFS = {
    PlaybookKind.FEATURE: ("outcome, data shape, interface seam", "failing outcome example", "affected entry path proves outcome"),
    PlaybookKind.BUG_FIX: ("symptom and matching root cause surface", "failing reproduction", "reproduction green with neighboring coverage"),
    PlaybookKind.REFACTOR: ("preserved behavior and structural objective", "behavior pin", "equivalent pins and inspectable simplification"),
    PlaybookKind.PERFORMANCE: ("repeatable baseline and limiting mechanism", "before measurement", "comparable before/after measurement"),
    PlaybookKind.SKILL_CHANGE: ("Host boundary and deterministic contracts", "deterministic contract checks", "green checks and non-regressing blinded evaluation"),
    PlaybookKind.WORKFLOW_EVAL: ("sanitized Parent/Candidate comparison", "mandatory deterministic Green", "non-regressing blinded comparison"),
    PlaybookKind.GENERIC: ("narrow affected seam", "existing task-appropriate Red or pin", "existing affected-path verification"),
}


def select_playbook(*, request: str, facts: set[str]) -> TaskPlaybookSelection:
    """Return exactly one selection using the contract's evidence precedence."""
    lower = request.lower()
    if "standalone-evaluation" in facts:
        kind = PlaybookKind.WORKFLOW_EVAL
    elif "skill-instruction-change" in facts:
        kind = PlaybookKind.SKILL_CHANGE
    elif "reproduced-defect" in facts:
        kind = PlaybookKind.BUG_FIX
    elif "repeatable-performance-baseline" in facts:
        kind = PlaybookKind.PERFORMANCE
    elif "behavior-preserving" in facts:
        kind = PlaybookKind.REFACTOR
    elif "new-user-outcome" in facts:
        kind = PlaybookKind.FEATURE
    else:
        kind = PlaybookKind.GENERIC
    obligation, red_or_pin, delivery_proof = _PROOFS[kind]
    evidence = tuple(sorted(facts)) or ("no route-controlling repository fact",)
    nearby = "ambiguous request" if not facts and lower else "route precedence applied"
    return TaskPlaybookSelection(
        kind=kind,
        entry_evidence=evidence + (nearby,),
        design_obligations=(obligation,),
        red_or_pin=red_or_pin,
        delivery_proof=delivery_proof,
        conditional_references=("#evidence-and-proof-matrix",),
    )


def requires_empirical_probe(question: str) -> bool:
    return question in {"behavior", "output", "timing", "layout", "routing", "evaluation"}


def is_human_decision(question: str) -> bool:
    return question in {"preference", "scope", "domain meaning", "irreversible action", "authorization", "gate approval"}


def conversational_todo_is_authority() -> bool:
    """TODOs are trace-local guidance, never a workflow authority."""
    return False
