---
name: design-coder
description: Turn confirmed coding requirements into an approved or autonomously selected design by comparing alternatives and applying adaptive domain modeling, deep-module design, Clean Architecture, and explicit testing seams. Use after grill-coder or whenever a coding change needs architecture decisions before planning.
---

# Design Coder

Apply the owners below. This stage owns intent reflection, conservative
classification, alternatives, presentation, and Gate routing, composing
`domain-modeling`, `codebase-design`, and `clean-architecture` when applicable.
`brainstorming` is not a required capability.

Apply the required domain sections to the selected approach. A bounded
interactive task combines alternatives and design approval into one Gate 1;
an architectural interactive task keeps approach selection separate from Gate
1. Both routes follow Approval Gates and, when human review is needed, the
approval contract.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Design content and specification mapping](../../references/domain-design-contract.md#design-content-and-specification-mapping).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).

## Conditional Reading

- **Selected Task Playbook:** validate the supplied [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection), then dereference only its one actual `conditional_references` link; also apply [Empirical facts and human decisions](../../references/task-playbook-contract.md#empirical-facts-and-human-decisions).
- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

Confirmed requirements and selected `TaskPlaybookSelection` from `grill-coder`, repository evidence, domain language, ADRs, and constraints to preserve.

## Output

An approved or autonomously selected design in conversation context. It
identifies the chosen approach, affected bounded contexts and relevant local
models, canonical domain language, enforcing owners, invariants,
consistency/interaction semantics, module responsibilities, public interfaces,
dependency direction, boundary data, testing seams, acceptance criteria, and
out-of-scope behavior.

## Process

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
7. Walk concrete success, rejection, and relevant concurrency, duplicate and partial-failure scenarios through the domain model and module interfaces together. Define atomicity/conflict outcomes, idempotency ownership and recovery responsibilities when triggered. Cover operational constraints, migration/compatibility and verification, including evidence for actual concurrency mechanisms. Separate confirmed decisions from open questions and identify affected readiness; do not infer infrastructure from an invariant. Return results with stable references where useful using the contract's specification mapping.
8. Route the result without weakening Gate 1:
   - Bounded interactive: put real alternatives, recommended short design,
     risks, and test seam in one Gate 1. `show-me` offers approve recommendation
     (prepare workspace, then Gate 2), revise with each named nonrecommended
     alternative (elaborate it, then ask Gate 1 again without implementation
     authority), and reject/stop.
   - Architectural interactive: present the elaborated design and invoke
     `show-me` for Gate 1 with approve, change, and reject.
   - Autonomous: record the one grounded recommendation without waiting.

When the modeling triggers apply, include the decisions required by the contract's [language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [protected behavior](../../references/domain-design-contract.md#protect-behavior-and-valid-values), and [persistence](../../references/domain-design-contract.md#aggregate-persistence-semantics) sections in the design handed to planning. Keep the stage's output focused on selected decisions and unresolved readiness, not a repeated contract checklist.

Do not write implementation code. During an orchestrated run, use the selected
safe workspace read-only through discovery and design. After Gate 1, prepare
dependencies and establish a green baseline before `plan-coder` writes the
specification (or earlier when a qualifying glossary/ADR write is needed).
Keep non-domain project artifacts in conversation until `plan-coder`
revalidates that prepared evidence. In-place and isolated workspaces are both
supported. Return the selected design content for specification synthesis.

## Stop Conditions

Stop when:

- an architectural interactive user has not selected an approach, or the
  autonomous path lacks one unique grounded recommendation;
- a domain or architecture decision requires an unavailable owner;
- the proposed design contradicts repository evidence;
- the design changes the agreed scope;
- interactive Gate 1 has been reached and explicit approval is pending.

After approval or autonomous selection, hand off to `plan-coder`; do not create
a worktree or begin implementation from this stage.
