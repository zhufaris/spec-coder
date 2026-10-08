"""Deterministic oracles for forward-testing the prompt contracts.

These helpers do not implement setup or worktree operations. They make the
contracts' state transitions executable so scenarios test outcomes rather than
only the presence of prose headings.
"""

import re
import tomllib
from collections.abc import Mapping
from datetime import datetime
from types import MappingProxyType
from typing import Dict, Iterable, Optional, Tuple


READY = "READY"
WARNING = "WARNING"
BLOCKED = "BLOCKED"
ROUTING_TIERS = ("economy", "standard", "strong")
HUMAN_REVIEW_KINDS = {
    "design alternative selection",
    "gate 1",
    "gate 2",
    "gate 3",
    "reopened gate",
    "named mutation",
}
AUTHORIZATION_REVIEW_KINDS = {
    "gate 1",
    "gate 2",
    "gate 3",
    "reopened gate",
    "named mutation",
}
AUTONOMOUS_REVIEW_KINDS = {
    "design-alternative-selection",
    "gate-1",
    "gate-2",
    "gate-3",
    "reopened-in-scope-gate",
}
AUTHORIZATION_INTENT_TOKENS = {
    "approve": {"approve", "approves", "approved", "approving"},
    "change": {
        "change",
        "changes",
        "changed",
        "changing",
        "revise",
        "revises",
        "revised",
        "revising",
    },
    "reject": {"reject", "rejects", "rejected", "rejecting"},
}


# Host-neutral worker progress heartbeat contract.  These helpers intentionally
# return immutable observation facts and observational outcomes only; they do not grant
# dispatch, interruption, promotion, or completion authority.
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
PROGRESS_PHASES = {"starting", "working", "verifying", "blocked", "completed"}
VERIFICATION_STATES = {"not-started", "running", "passed", "failed"}


def resolve_autonomy_mode(
    *, explicit_user_choice: bool | None, source: str | None
) -> str:
    """Resolve request-scoped autonomy without inferring or persisting it."""
    if explicit_user_choice is None:
        return "interactive"
    if not isinstance(explicit_user_choice, bool):
        raise ValueError("explicit_user_choice must be a boolean or None")
    if not explicit_user_choice:
        return "interactive"
    if source != "current-user-request":
        raise ValueError("autonomous mode requires the current user request")
    return "autonomous"


def decide_approval_route(
    *,
    autonomy_mode: str,
    review_kind: str,
    grounded_recommendations: int,
    unresolved_load_bearing: bool = False,
    scope_expansion: bool = False,
    separate_authority_required: bool = False,
) -> str:
    """Select the review route without widening request-scoped authority."""
    if autonomy_mode not in {"interactive", "autonomous"}:
        raise ValueError("unsupported autonomy mode")
    if isinstance(grounded_recommendations, bool) or not isinstance(
        grounded_recommendations, int
    ):
        raise ValueError("grounded_recommendations must be an integer")
    if autonomy_mode == "interactive":
        return "request-human-review"
    if unresolved_load_bearing:
        return "stop-unresolved-decision"
    if (
        scope_expansion
        or separate_authority_required
        or review_kind == "named-mutation"
    ):
        return "request-human-review"
    if review_kind not in AUTONOMOUS_REVIEW_KINDS:
        return "request-human-review"
    if grounded_recommendations != 1:
        return "stop-no-unique-recommendation"
    return "auto-select-recommended"


def validate_progress_snapshot(snapshot: Mapping[str, object]) -> Mapping[str, object]:
    """Validate and copy one immutable worker observation fact."""
    if not isinstance(snapshot, Mapping):
        raise ValueError("snapshot must be a mapping")
    keys = set(snapshot)
    required = set(PROGRESS_SNAPSHOT_FIELDS)
    missing = required - keys
    extra = keys - required
    if missing:
        raise ValueError("missing ProgressSnapshot fields: " + ", ".join(sorted(missing)))
    if extra:
        raise ValueError("unknown ProgressSnapshot fields: " + ", ".join(sorted(extra)))

    for field in PROGRESS_SNAPSHOT_FIELDS:
        value = snapshot[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a nonempty string")
    if snapshot["phase"] not in PROGRESS_PHASES:
        raise ValueError("unsupported progress phase")
    if snapshot["verification_state"] not in VERIFICATION_STATES:
        raise ValueError("unsupported verification state")

    observed_at = snapshot["observed_at"]
    try:
        parsed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError("observed_at must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("observed_at must include a timezone")
    return MappingProxyType(dict(snapshot))


def prepare_heartbeat_dispatch(
    *, heartbeat_capability: bool, dispatch_timing: str
) -> str:
    """Record heartbeat readiness before or at a direct-child dispatch."""
    if dispatch_timing not in {"before-dispatch", "at-dispatch"}:
        raise ValueError("heartbeat capability must be recorded before or at dispatch")
    return (
        "heartbeat-ready"
        if heartbeat_capability
        else "heartbeat-capability-unavailable"
    )


def heartbeat_report_due(
    seconds_since_report: float,
    *,
    starting: bool = False,
    phase_changed: bool = False,
    command_boundary: str | None = None,
    terminal: bool = False,
) -> bool:
    """Return whether a worker heartbeat is due at an event or 45 seconds."""
    if seconds_since_report < 0:
        raise ValueError("seconds_since_report cannot be negative")
    if command_boundary not in {None, "before-command", "after-command"}:
        raise ValueError("unsupported command boundary")
    return bool(
        starting
        or phase_changed
        or command_boundary is not None
        or terminal
        or seconds_since_report >= 45
    )


def observe_worker_progress(
    *,
    previous_snapshot: Mapping[str, object] | None,
    incoming_snapshot: Mapping[str, object] | None,
    heartbeat_capability: bool,
    wait_timed_out: bool,
    interval_missed: bool = False,
) -> Dict[str, object]:
    """Record transient observation evidence without execution side effects."""
    previous = (
        validate_progress_snapshot(previous_snapshot)
        if previous_snapshot is not None
        else None
    )
    # Validate first, so invalid evidence can never replace a valid observation.
    incoming = (
        validate_progress_snapshot(incoming_snapshot)
        if incoming_snapshot is not None
        else None
    )
    if incoming is not None:
        status = "observed"
        snapshot = incoming
    elif not heartbeat_capability:
        status = "heartbeat-capability-unavailable"
        snapshot = previous
    elif wait_timed_out or interval_missed:
        status = "heartbeat-overdue"
        snapshot = previous
    else:
        status = "awaiting-heartbeat"
        snapshot = previous
    result: Dict[str, object] = {
        "status": status,
        "snapshot": snapshot,
        "execution_effect": "none",
        "completion_authority": "main-only",
    }
    if status == "heartbeat-capability-unavailable":
        result["delegation_effect"] = "preserve"
    return result


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
        "review_options",
    )
    missing = [field for field in required if field not in snapshot]
    if missing:
        raise ValueError("missing ReviewSnapshot fields: " + ", ".join(missing))

    raw_approval_kind = snapshot["approval_kind"]
    if not isinstance(raw_approval_kind, str):
        raise ValueError("approval_kind must name a suite-owned human review")
    approval_kind = raw_approval_kind.strip()
    if approval_kind.casefold() not in HUMAN_REVIEW_KINDS:
        raise ValueError("approval_kind must name a suite-owned human review")

    scalar_fields = ("artifact", "approval_effect", "next_stage")
    normalized_scalars = {}
    for field in scalar_fields:
        value = snapshot[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a nonempty string")
        normalized_scalars[field] = value.strip()

    raw_decisions = snapshot["decisions"]
    if not isinstance(raw_decisions, (list, tuple)) or not raw_decisions:
        raise ValueError("decisions must be a nonempty list or tuple")
    if any(
        not isinstance(decision, str) or not decision.strip()
        for decision in raw_decisions
    ):
        raise ValueError("decisions must contain only nonempty strings")
    decisions = tuple(decision.strip() for decision in raw_decisions)

    raw_blockers = snapshot["blockers"]
    if not isinstance(raw_blockers, (list, tuple)):
        raise ValueError("blockers must be a list or tuple")
    if any(
        not isinstance(blocker, str) or not blocker.strip()
        for blocker in raw_blockers
    ):
        raise ValueError("blockers must contain only nonempty strings")
    blockers = tuple(blocker.strip() for blocker in raw_blockers)

    raw_excluded_authority = snapshot.get("excluded_authority", ())
    if not isinstance(raw_excluded_authority, (list, tuple)):
        raise ValueError("excluded_authority must be a list or tuple")
    if any(
        not isinstance(phrase, str) or not phrase.strip()
        for phrase in raw_excluded_authority
    ):
        raise ValueError("excluded_authority must contain only nonempty strings")
    excluded_authority = tuple(
        phrase.strip() for phrase in raw_excluded_authority
    )
    normalized_excluded_authority = tuple(
        phrase.casefold() for phrase in excluded_authority
    )

    raw_options = snapshot["review_options"]
    if not isinstance(raw_options, (list, tuple)) or not 2 <= len(raw_options) <= 4:
        raise ValueError("review_options must contain 2-4 entries")

    option_fields = {"label", "choice", "consequence"}
    options = []
    normalized_labels = set()
    normalized_pairs = set()
    for option in raw_options:
        if not isinstance(option, Mapping) or set(option) != option_fields:
            raise ValueError(
                "each review option must contain exactly label, choice, and consequence"
            )
        values = {field: option[field] for field in option_fields}
        if any(
            not isinstance(value, str) or not value.strip()
            for value in values.values()
        ):
            raise ValueError("review option fields must be nonempty strings")
        label = values["label"].strip()
        normalized_label = label.casefold()
        if normalized_label in normalized_labels:
            raise ValueError("review option labels must be unique")
        normalized_labels.add(normalized_label)

        choice = values["choice"].strip()
        consequence = values["consequence"].strip()
        normalized_pair = (choice.casefold(), consequence.casefold())
        if normalized_pair in normalized_pairs:
            raise ValueError("review options must be materially distinct")
        normalized_pairs.add(normalized_pair)

        combined_option = f"{choice} {consequence}".casefold()
        if any(
            phrase in combined_option for phrase in normalized_excluded_authority
        ):
            raise ValueError("review option widens the supplied authority")
        options.append(
            f"{label}: {choice} ({consequence})"
        )

    if approval_kind.casefold() in AUTHORIZATION_REVIEW_KINDS:
        choice_tokens = {
            token
            for option in raw_options
            for token in re.findall(r"[a-z0-9]+", option["choice"].casefold())
        }
        missing_intents = [
            intent
            for intent, accepted_tokens in AUTHORIZATION_INTENT_TOKENS.items()
            if choice_tokens.isdisjoint(accepted_tokens)
        ]
        if missing_intents:
            raise ValueError(
                "authorization review options must express approve, "
                "change/revise, and reject intents"
            )

    fields = [
        approval_kind,
        normalized_scalars["artifact"],
        "; ".join(decisions),
        "; ".join(blockers) or "no blocker",
        normalized_scalars["approval_effect"],
        normalized_scalars["next_stage"],
        *(
            ["excluded authority: " + "; ".join(excluded_authority)]
            if excluded_authority
            else []
        ),
        *options,
    ]
    if sum(len(field) for field in fields) + 20 > width:
        return " -> ".join(fields)
    return " | ".join(fields)


def requires_human_review(interaction_kind: str) -> bool:
    """Return whether a suite-owned interaction needs review options."""
    if not isinstance(interaction_kind, str):
        return False
    return interaction_kind.strip().casefold() in HUMAN_REVIEW_KINDS


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


def decide_execution_mode(
    *,
    dependency_ready: bool,
    grounded_inputs: bool,
    bounded: bool,
    reversible: bool,
    verification_seam: bool,
    main_only: bool,
    opt_out: bool,
    spawn_available: bool,
    available_slots: int,
    delegation_required: bool,
) -> str:
    if not dependency_ready:
        return "pending"
    if opt_out:
        return "local"

    delegation_eligible = (
        grounded_inputs
        and bounded
        and reversible
        and verification_seam
        and not main_only
    )
    if not delegation_eligible:
        return "block" if delegation_required else "local"
    if not spawn_available:
        return "block" if delegation_required else "local"
    if available_slots <= 0:
        return "wait"
    return "delegate"


def select_execution_wave(
    tickets: Iterable[Dict[str, object]],
    *,
    host_available_slots: int,
    isolated: bool,
) -> Tuple[Tuple[str, str], ...]:
    """Select the next ready local or delegated execution wave in plan order."""
    ready = tuple(ticket for ticket in tickets if ticket.get("dependency_ready"))
    if not ready:
        return ()

    first = ready[0]
    first_mode = str(first.get("mode", "local"))
    if first_mode == "local":
        return ((str(first["id"]), first_mode),)
    if first_mode != "delegate":
        return ()

    delegated_candidates = tuple(
        {
            **ticket,
            "delegation_eligible": (
                ticket.get("mode") == "delegate"
                and ticket.get("delegation_eligible", True)
            ),
        }
        for ticket in ready
    )
    selected = select_delegated_wave(
        delegated_candidates,
        host_available_slots=host_available_slots,
        isolated=isolated,
    )
    return tuple((ticket_id, "delegate") for ticket_id in selected)


def validate_planned_waves(
    tickets: Iterable[Dict[str, object]], waves: Iterable[Iterable[str]]
) -> Tuple[Tuple[str, ...], ...]:
    """Validate the durable, Gate-3-approved partition of implementation tickets."""
    ticket_list = tuple(tickets)
    tickets_by_id: Dict[str, Dict[str, object]] = {}
    for ticket in ticket_list:
        ticket_id = ticket.get("id")
        if not isinstance(ticket_id, str) or not ticket_id:
            raise ValueError("ticket IDs must be nonempty strings")
        if ticket_id in tickets_by_id:
            raise ValueError("ticket IDs must be unique")
        if ticket.get("mode") not in {"delegate", "local", "main-local"}:
            raise ValueError("ticket execution mode must be delegate, local, or main-local")
        tickets_by_id[ticket_id] = ticket

    normalized_waves = tuple(tuple(wave) for wave in waves)
    membership: Dict[str, int] = {}
    for wave_index, wave in enumerate(normalized_waves):
        if not wave:
            raise ValueError("planned waves cannot be empty")
        if len(wave) > 4:
            raise ValueError("planned waves contain at most four tickets")
        for ticket_id in wave:
            if not isinstance(ticket_id, str) or ticket_id not in tickets_by_id:
                raise ValueError("planned waves cannot contain unknown tickets")
            if ticket_id in membership:
                raise ValueError("every ticket must appear exactly once")
            membership[ticket_id] = wave_index

        main_local_ids = [
            ticket_id
            for ticket_id in wave
            if tickets_by_id[ticket_id].get("mode") in {"local", "main-local"}
        ]
        if main_local_ids and len(wave) != 1:
            raise ValueError("a main-local ticket must be a singleton planned wave")

    if set(membership) != set(tickets_by_id):
        raise ValueError("every ticket must appear exactly once")

    for ticket_id, ticket in tickets_by_id.items():
        wave_index = membership[ticket_id]
        dependencies = ticket.get("dependencies", set())
        conflicts = ticket.get("conflicts", set())
        if not isinstance(dependencies, (set, frozenset, tuple, list)):
            raise ValueError("ticket dependencies must be an iterable of IDs")
        if not isinstance(conflicts, (set, frozenset, tuple, list)):
            raise ValueError("ticket conflicts must be an iterable of IDs")
        for dependency_id in dependencies:
            if dependency_id not in tickets_by_id:
                raise ValueError("ticket dependency is unknown")
            if membership[dependency_id] >= wave_index:
                raise ValueError("dependencies must be in earlier planned waves")
        for conflict_id in conflicts:
            if conflict_id not in tickets_by_id:
                raise ValueError("ticket conflict is unknown")
            if membership[conflict_id] == wave_index:
                raise ValueError("conflicting tickets cannot share a planned wave")

    return normalized_waves


def decide_parallel_dispatch(
    *,
    eligible_count: int,
    mutation_required: bool,
    host_available_slots: int,
    isolated: bool,
    parallel_request: str = "none",
    isolation_blocker: Optional[str] = None,
) -> Tuple[str, str]:
    """Model request policy; a blocker records failed or prohibited preparation."""
    if parallel_request not in {"none", "preferred", "required"}:
        raise ValueError("parallel request must be none, preferred, or required")
    if eligible_count == 0:
        return "block", "no eligible members in current planned wave"
    if parallel_request == "required" and eligible_count < 2:
        return "block", "fewer than two eligible members in current planned wave"
    if host_available_slots <= 0:
        return "wait", "temporary Host capacity is zero"
    if eligible_count < 2:
        return "serial", "only one eligible member in current planned wave"
    if host_available_slots < 2:
        mode = "wait" if parallel_request == "required" else "serial"
        return mode, "temporary Host capacity is below two slots"
    if mutation_required and not isolated:
        if parallel_request == "none":
            return "serial", "real mutation isolation unavailable"
        if not isolation_blocker:
            return "prepare-isolation", "attempt permitted per-worker isolation before fallback"
        mode = "block" if parallel_request == "required" else "serial"
        return mode, isolation_blocker
    return "parallel", "eligible current-wave members have capacity and safe workspaces"


def select_planned_wave_batch(
    tickets: Iterable[Dict[str, object]],
    waves: Iterable[Iterable[str]],
    *,
    completed_ids: set[str],
    host_available_slots: int,
    isolated: bool,
    parallel_request: str = "none",
    isolation_blocker: Optional[str] = None,
) -> Tuple[Tuple[str, str], ...]:
    """Select only the live dispatch batch from the earliest incomplete planned wave."""
    if parallel_request not in {"none", "preferred", "required"}:
        raise ValueError("parallel request must be none, preferred, or required")
    ticket_list = tuple(tickets)
    planned_waves = validate_planned_waves(ticket_list, waves)
    tickets_by_id = {str(ticket["id"]): ticket for ticket in ticket_list}
    if not completed_ids.issubset(tickets_by_id):
        raise ValueError("completed IDs must belong to the planned ticket set")

    current_wave = next(
        (wave for wave in planned_waves if any(ticket_id not in completed_ids for ticket_id in wave)),
        (),
    )
    remaining = tuple(
        ticket_id for ticket_id in current_wave if ticket_id not in completed_ids
    )
    if not remaining:
        return ()

    first_ticket = tickets_by_id[remaining[0]]
    first_mode = str(first_ticket.get("mode", "local"))
    if first_mode in {"local", "main-local"}:
        if parallel_request == "required":
            return ()
        return ((remaining[0], "local"),)
    if first_mode != "delegate":
        return ()

    eligible = tuple(
        tickets_by_id[ticket_id] for ticket_id in remaining
        if tickets_by_id[ticket_id].get("dependency_ready", True)
        and tickets_by_id[ticket_id].get("delegation_eligible", True)
        and set(tickets_by_id[ticket_id].get("dependencies", ())).issubset(completed_ids)
    )
    mode, _ = decide_parallel_dispatch(
        eligible_count=len(eligible),
        mutation_required=any(not ticket.get("read_only", False) for ticket in eligible),
        host_available_slots=host_available_slots,
        isolated=isolated,
        parallel_request=parallel_request,
        isolation_blocker=isolation_blocker,
    )
    if mode not in {"serial", "parallel"}:
        return ()
    limit = 1 if mode == "serial" else min(4, host_available_slots)
    return tuple((str(ticket["id"]), "delegate") for ticket in eligible[:limit])


def git_worktree_add_args(
    *, absolute_path: str, branch_name: str, wave_base: str
) -> Tuple[str, ...]:
    return (
        "git",
        "worktree",
        "add",
        absolute_path,
        "-b",
        branch_name,
        wave_base,
    )


def integrate_wave_result(
    *,
    base_matches: bool,
    accepted_sibling_advancement: bool,
    ownership_disjoint: bool,
    transfer_clean: bool,
    diff_explained: bool,
    verification_passes: bool,
    parallel_request: str = "none",
) -> str:
    if parallel_request not in {"none", "preferred", "required"}:
        raise ValueError("parallel request must be none, preferred, or required")
    valid_base = base_matches or accepted_sibling_advancement
    safe_result = (
        ownership_disjoint
        and transfer_clean
        and diff_explained
        and verification_passes
    )
    if valid_base and safe_result:
        return "accept"
    return "requeue-serialized" if parallel_request == "none" else "reassess-parallel"


def apply_mid_run_opt_out(
    *,
    integrated_commits: Iterable[str],
    returned_attributable_results: Iterable[str],
    undispatched_tickets: Iterable[str],
) -> Dict[str, object]:
    return {
        "integrated": tuple(integrated_commits),
        "inspect_before_disposition": tuple(returned_attributable_results),
        "stopped_before_dispatch": tuple(undispatched_tickets),
        "promotion": "stopped",
        "cancellation_or_discard": "requires-safe-disposition",
        "remaining_execution": "main-local-after-attribution",
    }


def decide_workspace_disposition(
    *, result_disposition: str, ownership_clean: bool, user_owned_changes: bool
) -> str:
    disposed = result_disposition in {"accepted", "explicitly-discarded"}
    if disposed and ownership_clean and not user_owned_changes:
        return "cleanup-authorized"
    return "retain-recovery-handle"


def choose_delivery_review_mode(
    *,
    opt_out: bool,
    spawn_available: bool,
    delegation_required: bool,
    available_slots: int = 1,
) -> str:
    if opt_out:
        return "main-local-two-axis"
    if not spawn_available:
        return "block" if delegation_required else "main-local-two-axis"
    if available_slots <= 0:
        return "wait"
    return "delegate-standards-and-spec"


def prepare_delivery_review_briefs(mode: str) -> Tuple[Dict[str, object], ...]:
    if mode != "delegate-standards-and-spec":
        return ()
    return tuple(
        {
            "axis": axis,
            "layer": 2,
            "read_only": True,
            "delegation_allowed": False,
            "must_not_spawn": True,
        }
        for axis in ("standards", "spec")
    )


def select_delegated_wave(
    tickets: Iterable[Dict[str, object]],
    *,
    host_available_slots: int,
    isolated: bool,
) -> Tuple[str, ...]:
    limit = min(4, max(0, host_available_slots))
    if not isolated:
        limit = min(limit, 1)

    candidates = tuple(tickets)
    conflicts_by_id = {
        str(ticket["id"]): set(ticket.get("conflicts", set()))
        for ticket in candidates
    }
    selected = []
    for ticket in candidates:
        if len(selected) >= limit:
            break
        if not ticket.get("dependency_ready") or not ticket.get(
            "delegation_eligible"
        ):
            continue

        ticket_id = str(ticket["id"])
        ticket_conflicts = conflicts_by_id[ticket_id]
        if any(
            selected_id in ticket_conflicts
            or ticket_id in conflicts_by_id[selected_id]
            for selected_id in selected
        ):
            continue
        selected.append(ticket_id)

    return tuple(selected)


def parse_user_model_mapping(
    content: Optional[bytes],
) -> Optional[Dict[str, Tuple[str, str]]]:
    if content is None:
        return {}
    try:
        parsed = tomllib.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    if (
        set(parsed) != {"version", "tiers"}
        or type(parsed["version"]) is not int
        or parsed["version"] != 1
    ):
        return None
    tiers = parsed["tiers"]
    if not isinstance(tiers, dict) or not set(tiers).issubset(ROUTING_TIERS):
        return None

    mapping: Dict[str, Tuple[str, str]] = {}
    for tier, entry in tiers.items():
        if not isinstance(entry, dict) or set(entry) != {"provider", "model"}:
            return None
        provider = entry["provider"]
        model = entry["model"]
        if not isinstance(provider, str) or not provider.strip():
            return None
        if not isinstance(model, str) or not model.strip():
            return None
        mapping[tier] = (provider, model)
    return mapping


def parse_repository_routing_policy(
    content: Optional[bytes],
) -> Tuple[str, bool]:
    if content is None:
        return "economy", True
    try:
        parsed = tomllib.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return "inherit-main", False
    allowed = {"economy", "standard", "strong", "inherit-main"}
    if set(parsed) != {"version", "minimum_tier"}:
        return "inherit-main", False
    minimum_tier = parsed["minimum_tier"]
    if (
        type(parsed["version"]) is not int
        or parsed["version"] != 1
        or not isinstance(minimum_tier, str)
        or minimum_tier not in allowed
    ):
        return "inherit-main", False
    return minimum_tier, True


def route_configured_subagent(
    *,
    classified_tier: str,
    user_config: Optional[bytes],
    repository_policy: Optional[bytes],
    available_models: set[Tuple[str, str]],
    override_supported: bool,
    required_model: Optional[Tuple[str, str]] = None,
    excluded_models: Optional[set[Tuple[str, str]]] = None,
    user_minimum_tier: Optional[str] = None,
    bundled_config: Optional[bytes] = None,
) -> Tuple[str, Optional[str], Optional[str]]:
    if classified_tier == "main-only":
        return "main-only", None, None
    if classified_tier not in ROUTING_TIERS:
        return "main-only", None, None

    if required_model is not None and (
        not override_supported or required_model not in available_models
    ):
        return "required-model-conflict", required_model[0], required_model[1]

    mapping = parse_user_model_mapping(
        bundled_config if user_config is None else user_config
    )
    repository_minimum, policy_valid = parse_repository_routing_policy(
        repository_policy
    )
    allowed_user_minimums = {*ROUTING_TIERS, "inherit-main"}
    user_minimum_valid = (
        user_minimum_tier is None or user_minimum_tier in allowed_user_minimums
    )
    inheritance_required = (
        repository_minimum == "inherit-main"
        or user_minimum_tier == "inherit-main"
    )
    if mapping is None or not policy_valid or not user_minimum_valid:
        if required_model is not None:
            return "required-model-conflict", required_model[0], required_model[1]
        return "inherit-main", None, None
    if inheritance_required:
        if required_model is not None:
            return "required-model-conflict", required_model[0], required_model[1]
        return "inherit-main", None, None
    if not override_supported:
        return "inherit-main", None, None

    tier_index = {tier: index for index, tier in enumerate(ROUTING_TIERS)}
    effective = max(
        tier_index[classified_tier],
        tier_index[repository_minimum],
        tier_index[user_minimum_tier] if user_minimum_tier else 0,
    )
    excluded = excluded_models or set()

    if required_model is not None:
        for tier in ROUTING_TIERS[effective:]:
            if mapping.get(tier) == required_model and required_model not in excluded:
                return tier, required_model[0], required_model[1]
        return "required-model-conflict", required_model[0], required_model[1]

    for tier in ROUTING_TIERS[effective:]:
        candidate = mapping.get(tier)
        if (
            candidate is not None
            and candidate in available_models
            and candidate not in excluded
        ):
            return tier, candidate[0], candidate[1]
    return "inherit-main", None, None


def route_delegated_work(
    *,
    work_kind: str,
    bounded: bool,
    reversible: bool,
    verification_seam: bool,
    user_config: Optional[bytes],
    repository_policy: Optional[bytes],
    available_models: set[Tuple[str, str]],
    override_supported: bool,
) -> Tuple[str, Optional[str], Optional[str]]:
    if not bounded or not reversible or not verification_seam:
        classified_tier = "main-only"
    elif work_kind in {"bounded-mechanical", "bounded-read-only"}:
        classified_tier = "economy"
    elif work_kind in {
        "ticket-implementation",
        "diagnosis",
        "test-evidence",
        "review-evidence",
    }:
        classified_tier = "standard"
    elif work_kind in {
        "complex-advisory-review",
        "architecture-options",
        "security-analysis",
        "cross-module-analysis",
    }:
        classified_tier = "strong"
    else:
        classified_tier = "main-only"

    return route_configured_subagent(
        classified_tier=classified_tier,
        user_config=user_config,
        repository_policy=repository_policy,
        available_models=available_models,
        override_supported=override_supported,
    )


def evaluate_delegated_attempt(
    *, outcome: str, main_verified: bool, already_promoted: bool
) -> str:
    if outcome == "success":
        return "evidence-accepted" if main_verified else "await-main-verification"
    if outcome in {"failed", "uncertain", "lacks-evidence", "boundary-crossing"}:
        return "stop-after-promotion" if already_promoted else "promote-inherit-main"
    return "stop-invalid-attempt-outcome"


def prepare_subagent_spawn(
    *,
    caller_layer: int,
    caller_may_delegate: bool,
    host_can_deny_child_spawn: bool,
) -> Tuple[str, Optional[int], Optional[bool]]:
    if caller_layer != 1 or not caller_may_delegate:
        return "return-to-main", None, None
    guard = "host" if host_can_deny_child_spawn else "contract"
    return f"spawn-direct-{guard}-guarded", 2, False
