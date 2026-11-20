# Bug Fix task playbook

## Bug Fix playbook

- Entry and design: reproduced symptom and root cause on matching surface.
- Phase steps: reproduction/root-cause evidence at existing discovery/design/affected-path verification seams.
- Skip reasons: defect controls: omit new-outcome/baseline duties; retain fixed stages, Gates, verification, authority.
- Red or pin: failing reported-defect reproduction.
- Delivery proof: reproduction green; neighboring behavior covered.

### Conditional Principles

- **Change sizing:** read [subtract-before-add](../../principles/subtract-before-add.md#subtract-before-adding) only when observed; otherwise skip the leaf.
- **Repeated repair failure:** read [attack-the-premise](../../principles/attack-the-premise.md#attack-the-premise) only when observed; otherwise skip the leaf.

### Procedure

1. [Discovery](../stages/discovery.md#procedure): Capture and reproduce the exact reported entry path and first incorrect behavior; determine from the actual contract whether the observed state is legitimate, collect evidence when it is unknown, and for restart-only symptoms inspect persisted configuration, caches, locks, and serialized state without automatic cleanup; preserve cleanup or recovery authorization and do not infer historical legitimacy from a name or current creation eligibility.
2. [Design](../stages/design.md#procedure): Choose the smallest root-cause repair: supply missing handling for legitimate state, or trace the earliest producer or wrong transition of illegitimate state rather than hide it with retries, swallowed errors, clamps, or defaults; keep unknown judgment evidence-backed and define the approved repair scope.
3. [Planning](../stages/planning.md#procedure): Carry the original reproduction identity into task acceptance and proof.
4. [Implementation](../stages/implementation.md#procedure): Observe reproduction Red; minimally repair only the confirmed root cause and matching fault instances within approved scope, preserving legitimate validation and neighboring behavior without an unlimited sweep.
5. [Delivery](../stages/delivery.md#procedure): Rerun the original public path on integrated code to verify the root cause repair; generic Green cannot replace it.
