# Feature task playbook

## Feature playbook

- Entry and design: user-visible outcome, data shape, interface seam.
- Phase steps: outcome acceptance at existing discovery/design/affected-path verification seams.
- Skip reasons: outcome controls: omit pins/baselines; retain fixed stages, Gates, verification, authority.
- Red or pin: failing outcome example or acceptance test.
- Delivery proof: entry path proves outcome and compatibility.

### Conditional Principles

- **Domain behavior:** read [model-the-domain](../../principles/model-the-domain.md#model-the-domain) only when observed; otherwise skip the leaf.

### Procedure

1. [Discovery](../stages/discovery.md#procedure): Confirm the user outcome, data shape, acceptance and public seam.
2. [Design](../stages/design.md#procedure): Compare domain/interface decisions and select an approved design.
3. [Planning](../stages/planning.md#procedure): Preserve acceptance and interfaces in the specification and vertical tasks.
4. [Implementation](../stages/implementation.md#procedure): Prove a failing outcome, implement it and check affected consumers.
5. [Delivery](../stages/delivery.md#procedure): Verify the actual entry path, compatibility and fresh full evidence.

### Completion

The task owns step order and route-specific proof; stage playbooks own local actions. Preserve the fixed stages and approval contracts. A failing step returns to its stage owner; an invalid design returns to design. Record an explicit skip reason only for inapplicable task-specific work. No step grants external effects or nested delegation.
