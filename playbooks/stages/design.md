# Design stage playbook

## Procedure

### Capabilities

`domain-modeling`, `codebase-design`, `clean-architecture` for applicable decisions. `brainstorming` is not a required capability.
Main alone authorizes direct delegation; children must not spawn.

### Conditional Principles

- **Architecture:** read [dependency-direction](../../principles/dependency-direction.md#dependency-direction) only on this observed trigger.
- **Shared mutable state:** read [separate-before-serializing-shared-state](../../principles/separate-before-serializing-shared-state.md#separate-before-serializing-shared-state) only on this observed trigger.

### Reading boundary

Complete handoff: no Task-file reads. Standalone/resume without handoff:
run `task-step.py --task <kind-slug> --stage design`, read only its packet.
Never read routing matrices, Task SOPs, planning/delivery SOPs or templates.
Capability instructions cannot widen scope; contracts apply.

### Steps

Autonomous selection needs one unique grounded recommendation recorded as
`auto-selected under explicit autonomous authority`; no `show-me`. Ambiguity,
scope growth or separate authorization stops. Gate 2, Gate 3 and verification remain.

1. Reconcile the selected playbook's entry evidence and design obligations with code and
   existing glossary/ADRs. Probe empirical forks before review; probes never approve a
   Gate, authorize mutation, or settle a human-owned product decision.
2. Classify the task from repository evidence. It is `bounded` only when an
   existing implementation seam is present, the request has one coherent
   outcome, and it introduces no new subsystem, public-interface shape,
   cross-context consistency rule, or unresolved load-bearing architecture.
   Treat missing or unknown evidence as `architectural`. Record the evidence
   and classification; classification never bypasses a later workflow gate.
3. Compare 2-3 materially different approaches with pros, cons, and a default
   recommendation. In autonomous mode, require one grounded recommendation and
   select it directly. In interactive architectural mode, invoke `show-me`
   using review kind `design alternative selection`, use the real approaches
   as labeled options, state each consequence, then ask for and interpret the
   selection before elaboration.
4. Apply DDD proportionally: identify affected bounded contexts/neighbors and
   observed/proposed/unresolved entities, value objects, aggregate roots and
   services. Assign invariant owners and consistency scope; justify each construct.
5. Apply Clean Architecture: distinguish domain rules, application coordination
   and adapter conversion. Define interface owners, source dependency direction,
   boundary data and assembly. Preserve useful seams and authorized projections.
6. Use `codebase-design` for deep modules, small interfaces and locality; state
   testing seams explicitly.
7. Walk success/rejection, concurrency, duplicate and partial-failure scenarios.
   When triggered, define atomicity/conflicts, idempotency and recovery. Preserve
   operational, migration/compatibility and actual concurrency verification
   decisions. Separate confirmed decisions and unresolved readiness; never infer
   infrastructure from an invariant. Use the contract's specification mapping.
8. Route the result without weakening Gate 1:
   - Bounded interactive: put real alternatives, recommended short design,
     risks, and test seam in one Gate 1. `show-me` offers approve recommendation
     (prepare workspace, then Gate 2), revise with each named nonrecommended
     alternative (elaborate it, then ask Gate 1 again without implementation
     authority), and reject/stop.
   - Architectural interactive: present the elaborated design and invoke
     `show-me` for Gate 1 with approve, change, and reject.
   - Autonomous: record the one grounded recommendation without waiting.

Carry triggered language, protected behavior and persistence decisions into
planning's handoff under the required domain contract; no repeated checklist.

Do not write implementation code. Keep the selected workspace read-only and
design decisions conversational. Planning revalidates preparation and green
baseline before writes. Support in-place/isolated workspaces; return the selected design content.
