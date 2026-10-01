---
name: design-coder
description: Turn confirmed coding requirements into a user-approved design by comparing alternatives and applying adaptive domain modeling, deep-module design, Clean Architecture, and explicit testing seams. Use after grill-coder or whenever a coding change needs architecture decisions before planning.
---

# Design Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Compose `brainstorming`, `domain-modeling`, `codebase-design`, and `clean-architecture`; do not copy or weaken their rules.

Read and apply the [domain design contract](../../references/domain-design-contract.md) to carry scenario, invariant, ownership, and architecture decisions into the specification.

Read the [worked examples](../../references/domain-design-examples.md) for applicable modeling triggers, service responsibilities, concurrency and dependency decisions.

Before requesting Gate 1 approval, read the
[approval review contract](../../references/approval-review-contract.md) and
invoke bundled `show-me` with the selected design, key decisions, material
risks/blockers, approval effect, and the `plan-coder` handoff. The ASCII map
supplements the complete design and explicit approval question.

## Input

Confirmed requirements from `grill-coder`, repository evidence, existing domain language and ADRs, and constraints that the design must preserve.

## Output

An approved design in conversation context. It identifies the chosen approach, affected bounded contexts and relevant local models, canonical domain language, enforcing owners, invariants, consistency/interaction semantics, module responsibilities, public interfaces, dependency direction, boundary data, testing seams, acceptance criteria, and out-of-scope behavior.

## Process

1. Reconcile the confirmed requirements with the current code, `GLOSSARY.md`, architecture documents, and ADRs.
2. Present 2-3 materially different approaches with pros, cons, and a default recommendation.
3. Wait for the user to select an approach before elaborating it.
4. Apply DDD adaptively using the contract's observed triggers. Describe affected bounded contexts and necessary neighbors, distinguish observed/proposed/unresolved models, and explain applicable entities, value objects, aggregate roots and services. Assign invariant ownership and consistency scope; justify each construct rather than requiring a complete class inventory.
5. Apply Clean Architecture proportionally: distinguish domain rules, application coordination and adapter conversion; define interface ownership, source dependency direction, crossing data and concrete dependency assembly where protection is needed. Preserve existing useful seams and scoped legacy migration; allow appropriate authorized query projections.
6. Use `codebase-design` to keep modules deep, interfaces small, and locality high. Prefer existing seams; define any new testing seams explicitly.
7. Walk concrete success, rejection, and relevant concurrency, duplicate and partial-failure scenarios through the domain model and module interfaces together. Define atomicity/conflict outcomes, idempotency ownership and recovery responsibilities when triggered. Cover operational constraints, migration/compatibility and verification, including evidence for actual concurrency mechanisms. Separate confirmed decisions from open questions and identify affected readiness; do not infer infrastructure from an invariant. Return results with stable references where useful using the contract's specification mapping.
8. Present the complete design, invoke `show-me` under the approval review
   contract, and stop at Gate 1 for explicit approval.

When the modeling triggers apply, include the decisions required by the contract's [language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [protected behavior](../../references/domain-design-contract.md#protect-behavior-and-valid-values), and [persistence](../../references/domain-design-contract.md#aggregate-persistence-semantics) sections in the design handed to planning. Keep the stage's output focused on approved decisions and unresolved readiness, not a repeated contract checklist.

Do not write implementation code. During an orchestrated run, keep project artifacts in conversation until `plan-coder` selects a safe workspace and establishes a green baseline. In-place and isolated workspaces are both supported. Return the approved design content for specification synthesis.

## Stop Conditions

Stop when:

- the user has not selected an approach;
- a domain or architecture decision requires an unavailable owner;
- the proposed design contradicts repository evidence;
- the design changes the agreed scope;
- Gate 1 has been reached and explicit approval is pending.

After approval, hand off to `plan-coder`; do not create a worktree or begin implementation from this stage.
