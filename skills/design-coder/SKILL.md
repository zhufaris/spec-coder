---
name: design-coder
description: Turn confirmed coding requirements into a user-approved design by comparing alternatives and applying adaptive domain modeling, deep-module design, Clean Architecture, and explicit testing seams. Use after grill-coder or whenever a coding change needs architecture decisions before planning.
---

# Design Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Compose `brainstorming`, `domain-modeling`, `codebase-design`, and `clean-architecture`; do not copy or weaken their rules.

Read and apply the [domain design contract](../../references/domain-design-contract.md) to carry scenario, invariant, ownership, and architecture decisions into the specification.

## Input

Confirmed requirements from `grill-coder`, repository evidence, existing domain language and ADRs, and constraints that the design must preserve.

## Output

An approved design in conversation context. It identifies the chosen approach, canonical domain language, business invariants, module boundaries, public interfaces, dependency direction, boundary-crossing data, testing seams, acceptance criteria, and out-of-scope behavior.

## Process

1. Reconcile the confirmed requirements with the current code, `GLOSSARY.md`, architecture documents, and ADRs.
2. Present 2-3 materially different approaches with pros, cons, and a default recommendation.
3. Wait for the user to select an approach before elaborating it.
4. Apply DDD adaptively: always sharpen domain language and invariants, but introduce bounded contexts, aggregates, value objects, repositories, or domain events only when observed complexity justifies them.
5. Apply Clean Architecture proportionally: define dependency direction, ports and adapters only where boundaries need protection, and simple data crossing those boundaries.
6. Use `codebase-design` to keep modules deep, interfaces small, and locality high. Prefer existing seams; define any new testing seams explicitly.
7. Walk concrete success, rejection, and relevant retry scenarios through the domain model and module interfaces together. Cover error handling, operational constraints, migration or compatibility concerns, and verification strategy. Separate confirmed decisions from open questions; give interacting rules stable references when useful. Return these results using the domain design contract's specification mapping.
8. Present the complete design and stop at Gate 1 for explicit approval.

Do not write implementation code. During an orchestrated run, do not write project artifacts before `plan-coder` establishes a safe isolated worktree. Return the approved design content for specification synthesis.

## Stop Conditions

Stop when:

- the user has not selected an approach;
- a domain or architecture decision requires an unavailable owner;
- the proposed design contradicts repository evidence;
- the design changes the agreed scope;
- Gate 1 has been reached and explicit approval is pending.

After approval, hand off to `plan-coder`; do not create a worktree or begin implementation from this stage.
