---
name: show-me
description: Render a compact inline ASCII review map immediately before a spec-coder suite skill asks for approval. Use for Gate 1, Gate 2, Gate 3, reopened gates, exact mutation authorization, and other suite-owned approval requests; it presents supplied evidence but never grants approval.
---

# Show Me

Follow the shared [approval review contract](../../references/approval-review-contract.md).
This is a narrow approval-review adaptation of
[`mbailey/show-me`](https://github.com/mbailey/show-me), not its terminal,
editor, browser, or screen-observation toolset. See the repository's
`THIRD_PARTY_NOTICES.md` for provenance and license terms.

## Input

A `ReviewSnapshot` supplied by the skill that owns the approval:

- approval kind;
- artifact or exact proposed mutation;
- key decisions;
- risks or blockers;
- approval effect;
- next stage.

For a reopened gate, also require the prior approval, changed fact, affected
decision, and returned gate; the returned gate is distinct from the next stage
that follows renewed approval. For mutation authorization, require the exact
diff or replacement bytes, not a reference to an absent proposal.

Use facts already established by the authoritative artifact, exact diff, or
owning stage. Do not re-decide or silently complete missing facts.

## Output

Write a compact ASCII review map directly in the conversation, followed by a
short factual summary if needed. Preserve every material risk and blocker. The
owning skill presents the authoritative artifact or diff and asks the explicit
approval question after the map.

## Process

1. Validate that all `ReviewSnapshot` fields are present and grounded in the
   artifact or mutation under review.
2. Select the smallest useful flow, tree, or dependency map. Use 3-7 main nodes
   and target at most 80 columns.
3. Include the approval effect and next stage. For a reopened gate, show the
   prior approval, changed fact, affected decision, and return path.
4. Render with plain ASCII characters. If the normal layout would be unclear or
   too wide, use the contract's linear fallback.
5. Return control to the owning skill. Do not phrase the visualization as
   approval and do not infer approval from the request to visualize it.

Do not create a file, start a process, open a browser or editor, observe a
screen, run an external executable, or persist approval state.

## Stop Conditions

Return to the owning skill without rendering a misleading map when:

- a required snapshot field is absent;
- a decision, blocker, or mutation scope is missing evidence or is not grounded
  in the authoritative artifact or diff;
- the supplied facts contradict the authoritative artifact or diff;
- the request is ordinary status, discovery, or clarification rather than an
  approval request.

Name the missing or conflicting field. The owning skill must correct the
snapshot before requesting approval; it must not silently omit visualization.
A grounded but unresolved blocker is review evidence, not a missing field:
render it visibly, use the linear fallback when needed, and then return control
without resolving it.
