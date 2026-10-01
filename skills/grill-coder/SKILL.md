---
name: grill-coder
description: Interrogate a coding request one consequential question at a time, always recommending a default answer, until requirements, boundaries, risks, and success criteria are explicit. Use for the discovery phase of spec-coder or when a coding plan needs requirements stress-testing before design.
---

# Grill Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Use the installed `grilling` skill for the interview method; this skill adds coding-specific evidence, output, and workspace constraints.

## Input

A coding request plus the current repository, existing specifications, `GLOSSARY.md`, ADRs, and relevant implementation evidence.

## Output

A dependency-ordered set of confirmed decisions covering purpose, users, scope, invariants, edge cases, operational constraints, failure behavior, and measurable success. Keep the result in conversation context for `design-coder`. In an already isolated worktree, durable terminology or qualifying architecture decisions may also update their established documents.

## Process

1. Inspect repository evidence before asking what the code or existing documents already answer.
2. Build a private decision tree and start with the decision that constrains the most downstream choices.
3. Ask exactly one question at a time.
4. Include a clear recommendation and one-sentence reason with every material question. The user may accept it by replying `default`.
5. Absorb each answer before choosing the next branch. Clarify an ambiguous answer with one focused follow-up.
6. Challenge fuzzy or conflicting domain terms, but defer detailed architecture to `design-coder`.
7. Finish when every load-bearing decision is confirmed, explicitly deferred, or out of scope.

Do not modify the user's original checkout. Before isolation exists, collect decisions in the conversation rather than writing project files. Do not write implementation code, create a branch, publish an issue, or imply that later approval gates have passed.

## Stop Conditions

Stop and report the current decision state when:

- the user asks to stop;
- repository evidence contradicts a load-bearing assumption;
- a required product or business decision has no authorized owner;
- the next useful action is design rather than further questioning.

On normal completion, hand the confirmed decisions to `design-coder` without starting design in the same response.
