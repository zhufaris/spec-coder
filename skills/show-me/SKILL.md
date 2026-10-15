---
name: show-me
description: Render a compact inline ASCII review map and labeled options immediately before a spec-coder suite skill asks for a human decision. Use for design alternative selection, Gate 1, Gate 2, Gate 3, reopened gates, exact mutation authorization, and other suite-owned review requests; it presents supplied evidence but never grants approval.
---

# Show Me

Apply the required approval owner sections below.
This is a narrow approval-review adaptation of
[`mbailey/show-me`](https://github.com/mbailey/show-me), not its terminal,
editor, browser, or screen-observation toolset. See the repository's
`THIRD_PARTY_NOTICES.md` for provenance and license terms.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities).
- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope).

## Conditional Reading

- **Reopened gate or mutation:** apply the corresponding required Review snapshot fields; no additional document or approval authority is inferred.

## Input

A `ReviewSnapshot` from the owning stage, with all required and applicable
conditional fields from Review snapshot. Require concrete artifact/diff facts;
return incomplete or contradictory inputs without silently filling them.

## Output

Write a compact ASCII review map and every labeled option directly in the
conversation, followed by a short factual summary if needed. Preserve every
material risk and blocker. Render each option as
`<label>: <choice> (<consequence>)` or an equivalent form containing the full
choice and consequence. The owning skill presents the authoritative artifact
or diff and asks the explicit question after the map.

## Process

1. Validate all fields and options against Review snapshot, including normalized
   label/choice uniqueness, canonical authorization intents and any excluded
   authority. Preserve uncertainty; deterministic checks do not prove grounding.
2. Select the smallest useful flow, tree, or dependency map. Use 3-7 main nodes
   and target at most 80 columns.
3. Include the approval effect, next stage, every review option, and any
   nonempty excluded-authority boundary. For a reopened gate, show the prior
   approval, changed fact, affected decision, and return path.
4. Render with plain ASCII characters. If the normal layout would be unclear or
   too wide, use the contract's linear fallback and retain every option.
5. Return control to the owning skill. It asks and interprets the labeled
   choice. Do not phrase the visualization as approval, select an option, or
   infer approval from the request to visualize it.

Do not create a file, start a process, open a browser or editor, observe a
screen, run an external executable, or persist approval state.

## Stop Conditions

Return to the owning skill without rendering a misleading map when:

- a required snapshot field is absent;
- review options are missing, outside the 2-4 range, incomplete, duplicate, or
  contradictory;
- a decision, blocker, or mutation scope is missing evidence or is not grounded
  in the authoritative artifact or diff;
- the supplied facts contradict the authoritative artifact or diff;
- the request is ordinary status, discovery, clarification, or read-only
  reporting rather than a suite-owned human review.

Name the missing or conflicting field. The owning skill must correct the
snapshot before requesting approval; it must not silently omit visualization.
A grounded but unresolved blocker is review evidence, not a missing field:
render it visibly, use the linear fallback when needed, and then return control
without resolving it.
