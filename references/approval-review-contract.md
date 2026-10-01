# Approval Review Contract

This contract is normative whenever a spec-coder suite skill asks a human to
approve an artifact or authorize a mutation. The owning skill keeps approval
authority and invokes bundled `show-me` only as a presentation adapter.

## Review snapshot

Supply these fields from the authoritative artifact or exact proposed mutation:

- **approval kind**: Gate 1, Gate 2, Gate 3, reopened gate, or named mutation;
- **artifact or exact proposed mutation**: the design/specification/tickets or
  the target and bounded change being authorized;
- **key decisions**: the smallest set needed to understand the request;
- **risks or blockers**: every material risk, blocker, or unresolved limit;
- **approval effect**: what the approval authorizes and what remains excluded;
- **next stage**: the immediate workflow transition after approval.

Conditional fields are part of the same snapshot:

- **reopened gate**: prior approval, changed fact, affected decision, and the
  returned gate. The returned gate names where renewed approval is requested;
  `next stage` names what follows if it is granted.
- **mutation authorization**: exact diff or replacement bytes, target, changed
  region, preserved region, safety guard, and consequence. A statement such as
  "apply the displayed diff" is incomplete when the diff is not supplied.

`show-me` must not invent a missing value. It returns the incomplete snapshot
to the owning skill for correction.

## Rendering

- Render directly in the conversation using plain ASCII characters.
- Use the smallest useful flow, tree, or dependency map with 3-7 main nodes.
- Target at most 80 columns. Wrap the supporting prose instead of compressing
  away a risk, blocker, boundary, or effect.
- Put the explicit approval question outside the diagram, after the
  authoritative artifact or diff and the review map.
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
source of truth. `show-me` does not grant approval, record approval, change
scope, resolve a blocker, or add a workflow gate.

This local skill must not require tmux. It must not require Neovim. It must not
require browser integration and must not require browser availability. It must
not require external executable support and must not require external executable
availability.
It creates no file or process and opens no UI.

Ordinary clarification, status, read-only inspection, and blocker reporting do
not require an approval map. Work already authorized by Gate 3, including TDD
and the ticket's atomic commit, does not introduce another approval request.

## Owning-skill responsibilities

The owning skill:

1. selects grounded snapshot facts;
2. presents or links the complete artifact or exact diff;
3. invokes bundled `show-me` before asking;
4. asks an explicit approval question;
5. interprets the human answer under the workflow contract;
6. records the transition in existing workflow artifacts where applicable.

For a mutation authorization, identify the exact target, exact diff or
replacement bytes, changed region, preserved region, safety guard, and
consequence of approval. A diagram never widens the mutation authority shown in
the diff.
