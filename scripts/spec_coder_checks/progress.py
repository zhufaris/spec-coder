"""Build canonical worker-progress snapshots without external side effects."""
from __future__ import annotations

from collections.abc import Callable
from types import MappingProxyType
from datetime import datetime, timezone


PROGRESS_SNAPSHOT_FIELDS = (
    "ticket_or_axis",
    "worker_handle",
    "phase",
    "active_command",
    "progress_evidence",
    "verification_state",
    "blocker",
    "observed_at",
)
PROGRESS_PHASES = frozenset({"starting", "working", "verifying", "blocked", "completed"})
VERIFICATION_STATES = frozenset({"not-started", "running", "passed", "failed"})


def _required_string(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _observed_at(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime):
        raise ValueError("clock must return a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def build_progress_snapshot(
    *,
    ticket_or_axis: str,
    worker_handle: str,
    phase: str,
    active_command: str,
    progress_evidence: str,
    verification_state: str,
    blocker: str,
    clock: Callable[[], datetime] | None = None,
) -> MappingProxyType:
    """Return the sole ordered, canonical ProgressSnapshot mapping.

    ``observed_at`` is intentionally derived only at emission time.  Callers
    may inject ``clock`` for deterministic tests, but cannot provide a time.
    """
    values = {
        "ticket_or_axis": _required_string("ticket_or_axis", ticket_or_axis),
        "worker_handle": _required_string("worker_handle", worker_handle),
        "phase": _required_string("phase", phase),
        "active_command": _required_string("active_command", active_command),
        "progress_evidence": _required_string("progress_evidence", progress_evidence),
        "verification_state": _required_string(
            "verification_state", verification_state
        ),
        "blocker": _required_string("blocker", blocker),
    }
    if values["phase"] not in PROGRESS_PHASES:
        raise ValueError("unsupported progress phase")
    if values["verification_state"] not in VERIFICATION_STATES:
        raise ValueError("unsupported verification state")
    if (
        values["phase"] == "completed"
        and values["verification_state"] not in {"passed", "failed"}
    ):
        raise ValueError("completed snapshots require passed or failed verification")

    observed_at = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if clock is None
        else _observed_at(clock)
    )
    return MappingProxyType(
        {
            field: values[field] if field in values else observed_at
            for field in PROGRESS_SNAPSHOT_FIELDS
        }
    )
