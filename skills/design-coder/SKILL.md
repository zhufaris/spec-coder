---
name: design-coder
description: Turn confirmed coding requirements into an approved or autonomously selected design by comparing alternatives and applying adaptive domain modeling, deep-module design, Clean Architecture, and explicit testing seams. Use after grill-coder or whenever a coding change needs architecture decisions before planning.
---

# Design Coder

Follow the shared [workflow contract](../../references/workflow-contract.md).
The interactive path must compose `brainstorming`, `domain-modeling`,
`codebase-design`, and `clean-architecture`; do not copy or weaken their rules.
The autonomous path must not invoke `brainstorming` because its hard human
approval gate is incompatible with explicit no-wait authority. It natively
compares approaches while still composing `domain-modeling`, `codebase-design`,
and `clean-architecture`.

Read and apply the [domain design contract](../../references/domain-design-contract.md) to carry scenario, invariant, ownership, and architecture decisions into the specification.

Read the [worked examples](../../references/domain-design-examples.md) for applicable modeling triggers, service responsibilities, concurrency and dependency decisions.

For interactive approach selection before design elaboration, invoke bundled
`show-me` with approval kind `design alternative selection` and 2-3 real
approaches, each labeled with its actual consequence. Return control and let
`design-coder` ask and interpret the selection. The autonomous path instead
uses the unique grounded recommendation. This is not Gate 1 and does not add a
gate.

Before requesting interactive Gate 1 approval, read the
[approval review contract](../../references/approval-review-contract.md) and
invoke bundled `show-me` with the selected design, key decisions, material
risks/blockers, approval effect, the `plan-coder` handoff, and the labeled
approve and continue, request changes, and reject and stop options. The ASCII
map supplements the complete design and explicit approval question.

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

Do not write implementation code. During an orchestrated run, use the safe workspace and green baseline prepared before discovery; keep non-domain project artifacts in conversation until `plan-coder` revalidates that evidence. In-place and isolated workspaces are both supported. Return the selected design content for specification synthesis.

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
