# Refactor task playbook

## Refactor playbook

- Entry and design: preserved behavior and reader-load/structure objective.
- Phase steps: preservation pins and structural inspection at existing design/verification seams.
- Skip reasons: preservation controls: omit outcome Red, use pin; retain fixed stages, Gates, verification, authority.
- Red or pin: pin current behavior before structural work.
- Delivery proof: equivalent pins and inspectable simplification.

### Conditional Principles

- **Behavior preservation:** read [preserve-observable-behavior](../../principles/preserve-observable-behavior.md#preserve-observable-behavior) only when observed; otherwise skip the leaf.

### Procedure

1. [Discovery](../stages/discovery.md#procedure): Identify public callers and pin current outputs, errors, precedence and effects.
2. [Design](../stages/design.md#procedure): Choose a simpler structure while preserving the observable contract.
3. [Planning](../stages/planning.md#procedure): Record preservation checks, dependency constraints and bounded increments.
4. [Implementation](../stages/implementation.md#procedure): Keep pins green while simplifying; use structural evidence instead of outcome Red.
5. [Delivery](../stages/delivery.md#procedure): Verify equivalent behavior and inspectable simplification plus fresh full checks.

### Completion

The task owns step order and route-specific proof; stage playbooks own local actions. Preserve the fixed stages and approval contracts. A failing step returns to its stage owner; an invalid design returns to design. Record an explicit skip reason only for inapplicable task-specific work. No step grants external effects or nested delegation.
