# Design stage playbook

## Procedure

### Capabilities

`domain-modeling`, `codebase-design`, and `clean-architecture` for applicable decisions. `brainstorming` is not a required capability.
Main alone authorizes direct delegation; children must not spawn.

### Conditional Principles

- **Architecture:** read [dependency-direction](../../principles/dependency-direction.md#dependency-direction) only on this observed trigger.

### Steps

Autonomous classification/design requires one unique grounded recommendation,
recorded as `auto-selected under explicit autonomous authority` without
`show-me`. Stop for ambiguity, unresolved load-bearing decisions, scope growth,
or separate authorization. Gate 2, Gate 3, TDD, review, verification and effect
authority remain unchanged.

1. Reconcile confirmed requirements and the selected playbook's entry evidence
   and design obligations with code, `GLOSSARY.md`, architecture documents and
   ADRs. Run bounded empirical probes before review; probes never approve a
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
4. Apply DDD adaptively using the contract's observed triggers. Describe affected bounded contexts and necessary neighbors, distinguish observed/proposed/unresolved models, and explain applicable entities, value objects, aggregate roots and services. Assign invariant ownership and consistency scope; justify each construct rather than requiring a complete class inventory.
5. Apply Clean Architecture proportionally: distinguish domain rules, application coordination and adapter conversion; define interface ownership, source dependency direction, crossing data and concrete dependency assembly where protection is needed. Preserve existing useful seams and scoped legacy migration; allow appropriate authorized query projections.
6. Use `codebase-design` to keep modules deep, interfaces small, and locality high. Prefer existing seams; define any new testing seams explicitly.
7. Walk concrete success, rejection, and relevant concurrency, duplicate and partial-failure scenarios through the domain model and module interfaces together. Define atomicity/conflict outcomes, idempotency ownership and recovery responsibilities only on this observed trigger. Cover operational constraints, migration/compatibility and verification, including evidence for actual concurrency mechanisms. Separate confirmed decisions from open questions and identify affected readiness; do not infer infrastructure from an invariant. Return results with stable references where useful using the contract's specification mapping.
8. Route the result without weakening Gate 1:
   - Bounded interactive: put real alternatives, recommended short design,
     risks, and test seam in one Gate 1. `show-me` offers approve recommendation
     (prepare workspace, then Gate 2), revise with each named nonrecommended
     alternative (elaborate it, then ask Gate 1 again without implementation
     authority), and reject/stop.
   - Architectural interactive: present the elaborated design and invoke
     `show-me` for Gate 1 with approve, change, and reject.
   - Autonomous: record the one grounded recommendation without waiting.

For modeling triggers, include decisions from [language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [protected behavior](../../references/domain-design-contract.md#protect-behavior-and-valid-values), and [persistence](../../references/domain-design-contract.md#aggregate-persistence-semantics) in planning's handoff; report selected decisions and unresolved readiness, not another checklist.

Do not write implementation code. Use the selected workspace read-only. Before planning writes
or a qualifying glossary/ADR write, preparation must establish a green baseline.
Keep design decisions conversational until planning revalidates that evidence.
Support in-place or isolated workspaces; return the selected design content for synthesis.
