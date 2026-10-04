"""Deterministic oracles for forward-testing the prompt contracts.

These helpers do not implement setup or worktree operations. They make the
contracts' state transitions executable so scenarios test outcomes rather than
only the presence of prose headings.
"""

import tomllib
from typing import Dict, Iterable, Optional, Tuple


READY = "READY"
WARNING = "WARNING"
BLOCKED = "BLOCKED"
ROUTING_TIERS = ("economy", "standard", "strong")


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
) -> Tuple[str, Optional[str], Optional[str]]:
    if classified_tier == "main-only":
        return "main-only", None, None
    if classified_tier not in ROUTING_TIERS:
        return "main-only", None, None

    if required_model is not None and (
        not override_supported or required_model not in available_models
    ):
        return "required-model-conflict", required_model[0], required_model[1]

    mapping = parse_user_model_mapping(user_config)
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
