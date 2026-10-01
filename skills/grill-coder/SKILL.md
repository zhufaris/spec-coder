---
name: grill-coder
description: Interrogate a coding request one consequential question at a time, always recommending a default answer, until requirements, boundaries, risks, and success criteria are explicit. Use for the discovery phase of spec-coder or when a coding plan needs requirements stress-testing before design.
---

# Grill Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Use the installed `grilling` skill for the interview method; this skill adds coding-specific evidence, output, and workspace constraints.

Use the [domain design contract](../../references/domain-design-contract.md) to identify terminology conflicts, missing rule/state owners, and relevant concurrency or failure scenarios. Read the [worked examples](../../references/domain-design-examples.md) when the business meanings or responsibilities are unclear; defer detailed model selection to design.

## Input

A coding request plus the current repository, existing specifications, `GLOSSARY.md`, ADRs, and relevant implementation evidence.

## Output

A dependency-ordered set of confirmed decisions covering purpose, users, scope, invariants, edge cases, operational constraints, failure behavior, and measurable success. Keep the result in conversation context for `design-coder`. If a safe workspace and green baseline are already established, durable terminology or qualifying architecture decisions may also update their established documents under the workspace's ownership rules.

## Process

1. Inspect repository evidence before asking what the code or existing documents already answer.
2. Build a private decision tree and start with the decision that constrains the most downstream choices.
3. Ask exactly one question at a time.
4. Include a clear recommendation and one-sentence reason with every material question. The user may accept it by replying `default`.
5. Absorb each answer before choosing the next branch. Clarify an ambiguous answer with one focused follow-up.
6. Challenge fuzzy or conflicting domain terms, distinguish affected contexts' meanings and state owners, and probe relevant transitions, concurrent requests, retries and partial failures. Inspect existing behavior before asking. Defer detailed entities, services and architecture selection to `design-coder`.
7. Finish when every load-bearing decision is confirmed, explicitly deferred, or out of scope.

During discovery, extract business nouns, actions, states, roles and constraints from requirements, tests, API/UI behavior and code. Use context glossaries when present; record conflicting meanings and evidence. Clarify public compatibility constraints before proposing terminology changes. Follow the contract's language-discovery guidance without selecting a model merely from database names.

Protect unrelated work in the user's original checkout. Before workspace selection and a green baseline, collect decisions in conversation rather than writing project files. A prepared workspace may be in place or isolated. Do not write implementation code, create a branch, publish an issue, or imply that later approval gates have passed.

## Stop Conditions

Stop and report the current decision state when:

- the user asks to stop;
- repository evidence contradicts a load-bearing assumption;
- a required product or business decision has no authorized owner;
- the next useful action is design rather than further questioning.

On normal completion, hand the confirmed decisions to `design-coder` without starting design in the same response.
