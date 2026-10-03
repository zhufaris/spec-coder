"""Deterministic oracles for forward-testing the prompt contracts.

These helpers do not implement setup or worktree operations. They make the
contracts' state transitions executable so scenarios test outcomes rather than
only the presence of prose headings.
"""

from typing import Dict, Iterable, Optional, Tuple


READY = "READY"
WARNING = "WARNING"
BLOCKED = "BLOCKED"


def _markers(canonical: bytes):
    lines = canonical.splitlines(keepends=True)
    return lines[0].rstrip(b"\r\n"), lines[-1].rstrip(b"\r\n")


def _exact_line_positions(content: bytes, marker: bytes):
    positions = []
    offset = 0
    for line in content.splitlines(keepends=True):
        if line.rstrip(b"\r\n") == marker:
            positions.append(offset)
        offset += len(line)
    return positions


def classify_managed_block(content: bytes, canonical: bytes) -> str:
    start, end = _markers(canonical)
    starts = _exact_line_positions(content, start)
    ends = _exact_line_positions(content, end)

    if not starts and not ends:
        return "absent"
    if len(starts) != len(ends) or not starts:
        return "malformed"
    sequence = [kind for _, kind in sorted(
        [(position, "start") for position in starts]
        + [(position, "end") for position in ends]
    )]
    if sequence != [kind for _ in starts for kind in ("start", "end")]:
        return "malformed"
    if len(starts) > 1:
        return "duplicated"

    block_end = ends[0] + len(end)
    if content[block_end : block_end + 2] == b"\r\n":
        block_end += 2
    elif content[block_end : block_end + 1] == b"\n":
        block_end += 1
    actual = content[starts[0] : block_end]
    return "current" if actual == canonical else "stale"


def propose_setup(content: bytes, canonical: bytes) -> Optional[Tuple[bytes, bytes]]:
    state = classify_managed_block(content, canonical)
    if state == "current":
        return None
    if state in ("malformed", "duplicated"):
        raise ValueError("unsafe marker state")
    if state == "absent":
        if not content or content.endswith((b"\n", b"\r\n")):
            return content, content + canonical
        return content, canonical + content

    start, end = _markers(canonical)
    begin = _exact_line_positions(content, start)[0]
    finish = _exact_line_positions(content, end)[0] + len(end)
    if content[finish : finish + 2] == b"\r\n":
        finish += 2
    elif content[finish : finish + 1] == b"\n":
        finish += 1
    return content, content[:begin] + canonical + content[finish:]


def apply_approved_setup(
    proposal: Tuple[bytes, bytes], current: bytes
) -> Tuple[str, Optional[bytes]]:
    before, after = proposal
    if current != before:
        return BLOCKED, None
    return READY, after


def aggregate_status(statuses: Iterable[str]) -> str:
    values = set(statuses)
    if BLOCKED in values:
        return BLOCKED
    if WARNING in values:
        return WARNING
    return READY


def render_review_snapshot(snapshot: Dict[str, object], width: int) -> str:
    required = (
        "approval_kind",
        "artifact",
        "decisions",
        "blockers",
        "approval_effect",
        "next_stage",
    )
    missing = [field for field in required if field not in snapshot]
    if missing:
        raise ValueError("missing ReviewSnapshot fields: " + ", ".join(missing))
    fields = [
        str(snapshot["approval_kind"]),
        str(snapshot["artifact"]),
        "; ".join(snapshot["decisions"]),
        "; ".join(snapshot["blockers"]) or "no blocker",
        str(snapshot["approval_effect"]),
        str(snapshot["next_stage"]),
    ]
    if sum(len(field) for field in fields) + 20 > width:
        return " -> ".join(fields)
    return " | ".join(fields)


def choose_isolation_route(
    *,
    linked_candidate: bool,
    superproject: bool,
    candidate_safe: bool,
    native_available: bool,
    local_ignore_status: int,
) -> str:
    if linked_candidate and not superproject:
        return "reuse-linked" if candidate_safe else "linked-conflict"
    if native_available:
        return "native"
    if local_ignore_status == 0:
        return "git-local"
    if local_ignore_status == 1:
        return "preflight-mutation-free-location"
    return "blocked-ignore-verification"


def route_new_discovery(
    *, workspace_safe: bool, baseline_green: bool, capabilities_ready: bool = True
) -> str:
    if not capabilities_ready:
        return "stop-capability"
    if not workspace_safe:
        return "stop-workspace"
    if not baseline_green:
        return "stop-baseline"
    return "start-grill"


def route_planning_workspace(
    *, prepared: bool, ownership_valid: bool, baseline_fresh: bool
) -> str:
    if not prepared or not ownership_valid or not baseline_fresh:
        return "return-preflight"
    return "write-specification"


def route_discovery_document(
    *,
    prepared: bool,
    ownership_safe: bool,
    confirmed: bool,
    decision_kind: str,
    adr_qualifies: bool,
) -> str:
    if not prepared:
        return "stop-preflight"
    if not confirmed:
        return "no-document-write"
    destination = None
    if decision_kind == "term":
        destination = "update-glossary"
    elif decision_kind == "architecture" and adr_qualifies:
        destination = "update-adr"
    if destination is None:
        return "no-document-write"
    if not ownership_safe:
        return "stop-ownership"
    return destination
