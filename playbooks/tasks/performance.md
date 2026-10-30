# Performance task playbook

## Performance playbook

- Entry and design: repeatable baseline, limiter, environment, comparable measure.
- Phase steps: comparable measurement at existing discovery/design/affected-path verification seams.
- Skip reasons: baseline controls: omit outcome Red unless behavior changes; retain fixed stages, Gates, verification, authority.
- Red or pin: before-measurement baseline.
- Delivery proof: comparable before/after proves target without regression.

### Conditional Principles

- **Measurement:** read [explain-the-number](../../principles/explain-the-number.md#explain-the-number) only when observed; otherwise skip the leaf.

### Procedure

1. [Discovery](../stages/discovery.md#procedure): Measure a repeatable baseline and identify the limiter on the actual entry path.
2. [Design](../stages/design.md#procedure): Choose a measured hypothesis under unchanged correctness constraints.
3. [Planning](../stages/planning.md#procedure): Record environment, measure, target and regression checks.
4. [Implementation](../stages/implementation.md#procedure): Apply one bounded change; compare equivalent before/after measurements.
5. [Delivery](../stages/delivery.md#procedure): Prove end-to-end improvement without correctness regression and report limitations.

### Completion

The task owns step order and route-specific proof; stage playbooks own local actions. Preserve the fixed stages and approval contracts. A failing step returns to its stage owner; an invalid design returns to design. Record an explicit skip reason only for inapplicable task-specific work. No step grants external effects or nested delegation.
