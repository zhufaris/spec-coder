"""Pure durable-wave checks, shared by the artifact CLI and forward scenarios."""
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class WaveFinding:
    rule: str
    message: str
    ticket_id: str | None = None
    wave_index: int | None = None


def inspect_waves(tickets, waves):
    """Return all structural findings; never schedule or modify a ticket.

    Tickets are mappings with id, mode, dependencies, conflicts and optional
    normalized ownership paths. Waves are ordered iterables of ticket IDs.
    """
    findings = []

    def add(rule, message, ticket_id=None, wave_index=None):
        findings.append(WaveFinding(rule, message, ticket_id, wave_index))

    by_id = {}
    for ticket in tickets:
        ticket_id = ticket.get("id")
        if not isinstance(ticket_id, str) or not ticket_id:
            add("ticket.invalid-id", "ticket IDs must be nonempty strings")
            continue
        if ticket_id in by_id:
            add("ticket.duplicate-id", "ticket IDs must be unique", ticket_id)
            continue
        by_id[ticket_id] = ticket
        if ticket.get("mode") not in {"delegate", "local", "main-local"}:
            add("ticket.invalid-mode", "ticket execution mode must be delegate, local, or main-local", ticket_id)

    membership = {}
    normalized = tuple(tuple(wave) for wave in waves)
    for index, wave in enumerate(normalized):
        if not wave:
            add("wave.empty", "planned waves cannot be empty", wave_index=index)
        if len(wave) > 4:
            add("wave.capacity", "planned waves contain at most four tickets", wave_index=index)
        known = []
        for ticket_id in wave:
            if not isinstance(ticket_id, str) or ticket_id not in by_id:
                add("wave.unknown-member", f"planned wave contains unknown ticket {ticket_id!r}", wave_index=index)
                continue
            if ticket_id in membership:
                add("wave.duplicate-member", f"{ticket_id} must appear exactly once", ticket_id, index)
            else:
                membership[ticket_id] = index
            known.append(ticket_id)
        if len(wave) != 1 and any(by_id[t].get("mode") in {"local", "main-local"} for t in known):
            add("wave.local-singleton", "a main-local ticket must be a singleton planned wave", wave_index=index)
        for left, right in combinations(dict.fromkeys(known), 2):
            for a in by_id[left].get("ownership", ()):
                for b in by_id[right].get("ownership", ()):
                    if a == b or a.startswith(b + "/") or b.startswith(a + "/"):
                        add("wave.ownership-overlap", f"{left} ({a}) and {right} ({b}) have overlapping mutation ownership", right, index)

    for ticket_id in by_id.keys() - membership.keys():
        add("wave.missing-member", f"{ticket_id} must appear exactly once in a planned wave", ticket_id)

    edges = {}
    for ticket_id, ticket in by_id.items():
        for field, prefix in (("dependencies", "dependency"), ("conflicts", "conflict")):
            values = ticket.get(field, ())
            if not isinstance(values, (set, frozenset, tuple, list)) or any(not isinstance(v, str) for v in values):
                add(f"{prefix}.invalid", f"ticket {field} must be an iterable of IDs", ticket_id)
                values = ()
            if field == "dependencies":
                edges[ticket_id] = tuple(v for v in values if v in by_id)
            for other in values:
                if other not in by_id:
                    add(f"{prefix}.unknown", f"{ticket_id} references unknown {prefix} {other}", ticket_id)
                elif ticket_id in membership and other in membership:
                    if field == "dependencies" and membership[other] >= membership[ticket_id]:
                        add("dependency.earlier-wave", f"{ticket_id} dependency {other} must be in an earlier planned wave", ticket_id)
                    if field == "conflicts" and membership[other] == membership[ticket_id]:
                        add("wave.declared-conflict", f"conflicting tickets {ticket_id} and {other} cannot share a planned wave", ticket_id)

    # Iterative depth-first traversal keeps very long valid plans off Python's
    # recursion limit and reports back edges even when another edge is unknown.
    state = {}
    for start in by_id:
        if state.get(start):
            continue
        state[start] = 1
        stack = [(start, iter(edges.get(start, ())))]
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                state[node] = 2
                stack.pop()
            elif state.get(child) == 1:
                add("dependency.cycle", f"dependency cycle includes {node} -> {child}", node)
            elif not state.get(child):
                state[child] = 1
                stack.append((child, iter(edges.get(child, ()))))
    return findings


def validate_planned_waves(tickets, waves):
    """Preserve the forward-oracle API: normalized tuple or ValueError."""
    normalized = tuple(tuple(wave) for wave in waves)
    findings = inspect_waves(tickets, normalized)
    if findings:
        raise ValueError(findings[0].message)
    return normalized
