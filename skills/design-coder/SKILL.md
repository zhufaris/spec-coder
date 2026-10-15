---
name: design-coder
description: Turn confirmed coding requirements into an approved or autonomously selected design by comparing alternatives and applying adaptive domain modeling, deep-module design, Clean Architecture, and explicit testing seams. Use after grill-coder or whenever a coding change needs architecture decisions before planning.
---

# Design Coder

Apply the required owner sections below.
The interactive path must compose `brainstorming`, `domain-modeling`,
`codebase-design`, and `clean-architecture`; do not copy or weaken their rules.
The autonomous path must not invoke `brainstorming` because its hard human
approval gate is incompatible with explicit no-wait authority. It natively
compares approaches while still composing `domain-modeling`, `codebase-design`,
and `clean-architecture`.

Apply the required domain sections to the selected approach. Approach selection
precedes design elaboration and remains separate from Gate 1. Both transitions
follow Approval Gates and, when human review is needed, the approval contract.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Design content and specification mapping](../../references/domain-design-contract.md#design-content-and-specification-mapping).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).

## Conditional Reading

- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

Confirmed requirements from `grill-coder`, repository evidence, existing domain language and ADRs, and constraints that the design must preserve.

## Output

An approved or autonomously selected design in conversation context. It
identifies the chosen approach, affected bounded contexts and relevant local
models, canonical domain language, enforcing owners, invariants,
consistency/interaction semantics, module responsibilities, public interfaces,
dependency direction, boundary data, testing seams, acceptance criteria, and
out-of-scope behavior.

## Process

In the autonomous path, steps 2-3 and 8 require a unique grounded recommendation.
Select it without invoking `show-me` or waiting for human
review, and record `auto-selected under explicit autonomous authority`. Stop
instead when the recommendation is missing or ambiguous, a load-bearing
decision remains unresolved, the scope expands, or separate authorization is
required. The interactive path remains unchanged.

1. Reconcile the confirmed requirements with the current code, `GLOSSARY.md`, architecture documents, and ADRs.
2. Present 2-3 materially different approaches with pros, cons, and a default
   recommendation. On the interactive path, invoke `show-me` using review kind
   `design alternative selection`; use those real approaches as its 2-3
   labeled options and state the consequence of selecting each one. On the
   autonomous path, select the unique grounded recommendation directly.
3. On the interactive path, after `show-me` returns control, ask the user to
   select a labeled approach, interpret the answer, and wait for a selection
   before elaborating it. On the autonomous path, record the auto-selection and
   elaborate it without waiting.
4. Apply DDD adaptively using the contract's observed triggers. Describe affected bounded contexts and necessary neighbors, distinguish observed/proposed/unresolved models, and explain applicable entities, value objects, aggregate roots and services. Assign invariant ownership and consistency scope; justify each construct rather than requiring a complete class inventory.
5. Apply Clean Architecture proportionally: distinguish domain rules, application coordination and adapter conversion; define interface ownership, source dependency direction, crossing data and concrete dependency assembly where protection is needed. Preserve existing useful seams and scoped legacy migration; allow appropriate authorized query projections.
6. Use `codebase-design` to keep modules deep, interfaces small, and locality high. Prefer existing seams; define any new testing seams explicitly.
7. Walk concrete success, rejection, and relevant concurrency, duplicate and partial-failure scenarios through the domain model and module interfaces together. Define atomicity/conflict outcomes, idempotency ownership and recovery responsibilities when triggered. Cover operational constraints, migration/compatibility and verification, including evidence for actual concurrency mechanisms. Separate confirmed decisions from open questions and identify affected readiness; do not infer infrastructure from an invariant. Return results with stable references where useful using the contract's specification mapping.
8. Present the complete elaborated design. On the interactive path, separately
   invoke `show-me` under the approval review contract for Gate 1 with labeled
   approve and continue, request changes, and reject and stop options, then ask
   and interpret the explicit Gate 1 choice. On the autonomous path, record the
   unique grounded recommendation without `show-me` or waiting. Gate 1 remains
   separate from approach selection.

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

- the interactive user has not selected an approach, or the autonomous path
  lacks one unique grounded recommendation;
- a domain or architecture decision requires an unavailable owner;
- the proposed design contradicts repository evidence;
- the design changes the agreed scope;
- interactive Gate 1 has been reached and explicit approval is pending.

After approval or autonomous selection, hand off to `plan-coder`; do not create
a worktree or begin implementation from this stage.
