# Workflow Eval task playbook

## Workflow Eval playbook

- Entry and design: Parent/Candidate scope, sanitized environment, anonymous rubric, deterministic prerequisites.
- Phase steps: deterministic prerequisites at existing seams, then separately triggered blinded Parent/Candidate evaluation.
- Skip reasons: omit target mutation absent repair; blinded evaluation required; retain fixed stages, Gates, verification, authority.
- Red or pin: mandatory deterministic Green for candidate.
- Delivery proof: non-regressing blinded comparison; inconclusive keeps Parent.

### Conditional Principles

- **Measurement:** read [explain-the-number](../../principles/explain-the-number.md#explain-the-number) only when observed; otherwise skip the leaf.

### Procedure

1. [Discovery](../stages/discovery.md#procedure): Define the comparison question and equivalent sanitized inputs without exposing run identity.
2. [Design](../stages/design.md#procedure): Select private criteria and compatible execution boundaries.
3. [Planning](../stages/planning.md#procedure): Record the comparison scope and deterministic prerequisites; no automatic promotion.
4. [Implementation](../stages/implementation.md#procedure): Confirm deterministic Green before direct read-only runs; collect all outputs.
5. [Delivery](../stages/delivery.md#procedure): Inspect raw evidence and blinded findings; inconclusive or conflicting evidence keeps Parent.

### Completion

The task owns step order and route-specific proof; stage playbooks own local actions. Preserve the fixed stages and approval contracts. A failing step returns to its stage owner; an invalid design returns to design. Record an explicit skip reason only for inapplicable task-specific work. No step grants external effects or nested delegation.
