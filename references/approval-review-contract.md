# Approval Review Contract

This contract is normative whenever a spec-coder suite skill asks a human to
select a design alternative, approve an artifact, or authorize a mutation.
The owning skill keeps approval authority and invokes bundled `show-me` only
as a presentation adapter.

This contract applies when a human review is requested. Under an explicit,
request-scoped `autonomous=true` choice, design alternative selection and Gate
1, Gate 2, Gate 3, or an in-scope reopened gate do not create a human review:
the owning skill may instead select exactly one unique grounded recommendation
and record `auto-selected under explicit autonomous authority`. Missing or
ambiguous recommendations and unresolved load-bearing decisions stop. Scope
expansion, named mutations, setup exact-diff approval, and every other action
requiring separate authorization remain human reviews governed by this
contract; autonomous mode never widens their authority.

## Review snapshot

Supply these fields from the authoritative artifact or exact proposed mutation:

- **approval kind**: design alternative selection, Gate 1, Gate 2, Gate 3,
  reopened gate, or named mutation. Design alternative selection is a review
  kind before design elaboration; it is distinct from Gate 1 and adds no gate;
- **artifact or exact proposed mutation**: the design/specification/tickets or
  the target and bounded change being authorized;
- **key decisions**: the smallest set needed to understand the request;
- **risks or blockers**: every material risk, blocker, or unresolved limit;
- **approval effect**: what the approval authorizes and what remains excluded;
- **next stage**: the immediate workflow transition after approval;
- **excluded authority** (optional): a list of nonempty phrases grounded in the
  authoritative artifact or exact proposed mutation. It records actions that
  remain outside the requested authority so the supplied options can be
  checked for scope widening;
- **review options**: 2-4 grounded, materially distinct entries. Every entry
  has a unique label, a choice, and the consequence of making that choice.

For an authorization question, use the normal choices approve and continue,
request changes, and reject and stop, adapting their consequences to the
artifact or mutation. For a genuine decision such as design approach
selection, show the real alternatives and their actual consequences instead
of disguising approve/change/reject as competing approaches. Do not add fake
choices merely to reach the minimum count. No option may authorize work beyond,
or widen the scope of, the artifact, diff, or other authority shown for review.

For Gate 1, Gate 2, Gate 3, a reopened gate, or a named mutation, the supplied
option choices must collectively carry all three canonical authorization
intents: approve, change/revise, and reject. The deterministic oracle checks
case-normalized word tokens in `choice` against the canonical tokens and their
ordinary verb inflections; consequences do not substitute for a missing
choice intent. This is a lexical completeness check, not semantic inference.
Design alternative selection is exempt because its choices are the real
alternatives rather than authorization outcomes.

Conditional fields are part of the same snapshot:

- **reopened gate**: prior approval, changed fact, affected decision, and the
  returned gate. The returned gate names where renewed approval is requested;
  `next stage` names what follows if it is granted.
- **mutation authorization**: exact diff or replacement bytes, target, changed
  region, preserved region, safety guard, and consequence. A statement such as
  "apply the displayed diff" is incomplete when the diff is not supplied.

`show-me` must not invent a missing value or resolve contradictory option
data. It returns the incomplete or contradictory snapshot to the owning skill
for correction.
A deterministic rendering oracle validates structural completeness and
contradictions in supplied fields. It does not infer semantic grounding beyond
those authoritative fields. When `excluded authority` is nonempty, render it
so the boundary remains visible; reject an option whose combined choice and
consequence contains one of those phrases after trimming and case
normalization.
A grounded but unresolved blocker is a present value, not an incomplete
snapshot: it must remain visible in the normal layout or linear fallback.

## Rendering

- Render directly in the conversation using plain ASCII characters.
- Use the smallest useful flow, tree, or dependency map with 3-7 main nodes.
- Target at most 80 columns. Wrap the supporting prose instead of compressing
  away a risk, blocker, boundary, or effect.
- Put the explicit approval question outside the diagram, after the
  authoritative artifact or diff and the review map.
- Render every review option as `<label>: <choice> (<consequence>)` or an
  equivalent form that contains the complete choice and consequence. A narrow
  layout may put options on separate lines or append them to the linear
  fallback; it must not omit them.
- When a normal layout does not fit, use a linear fallback:

```text
[artifact] -> [decisions] -> [risks] -> [approval effect] -> [next stage]
```

A reopened gate must show:

```text
[prior approval] -> [changed fact] -> [affected decision] -> [returned gate]
```

## Authority and safety

The ASCII map is supplemental. The authoritative artifact or diff remains the
source of truth. `show-me` does not grant approval, infer approval, choose an
option, record approval, change scope, resolve a blocker, or add a workflow
gate.

This local skill must not require tmux. It must not require Neovim. It must not
require browser integration and must not require browser availability. It must
not require external executable support and must not require external executable
availability.
It creates no file or process and opens no UI.

Ordinary clarification, status, read-only reporting or inspection, and blocker
reporting do not require review options or an approval map. Work already
authorized by Gate 3, including TDD and the ticket's atomic commit, does not
introduce another approval request.

## Owning-skill responsibilities

The owning skill:

1. selects grounded snapshot facts and 2-4 valid review options;
2. presents or links the complete artifact or exact diff;
3. invokes bundled `show-me` before asking;
4. asks an explicit question using the displayed labeled options;
5. interprets the human's selected option under the workflow contract;
6. records the transition in existing workflow artifacts where applicable.

For a mutation authorization, identify the exact target, exact diff or
replacement bytes, changed region, preserved region, safety guard, and
consequence of approval. A diagram never widens the mutation authority shown in
the diff.
