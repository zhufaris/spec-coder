---
name: spec-coder
description: Orchestrate code-changing requests through requirements grilling, design, isolated planning, ticket-level TDD, review, and verified delivery. Use by default for feature, bug-fix, refactor, or other implementation requests; do not auto-trigger for read-only explanation, status, investigation, or review, and honor explicit requests to skip spec-coder or directly modify.
---

# Spec Coder

Follow the shared [workflow contract](../../references/workflow-contract.md) and verify the installed capabilities listed in [upstream compatibility](../../references/upstream-compatibility.md) before delegating stages.

## Input

A new coding request, or a repository containing partial spec-coder artifacts from an interrupted workflow.

## Output

An approved specification, approved vertical-ticket plan, one atomic commit per completed ticket, review results, fresh verification evidence, and a final delivery report produced through `delivery-coder`.

## Process

1. Inspect repository instructions, Git status, current branch, worktrees, relevant specifications and plans, plan checkboxes, and Git log before changing anything.
2. Verify every required local and upstream skill is installed and materially compatible. Stop with a compatibility error rather than approximating a missing capability.
3. Classify the request:
   - For a new request, start with `grill-coder`.
   - For resumed work, infer the earliest incomplete phase from durable artifacts and fresh verification at the inferred boundary. Never maintain a private workflow-state file.
4. Run the fixed stage order:
   1. `grill-coder` exposes hidden requirements, boundaries, constraints, and acceptance signals.
   2. `design-coder` compares 2-3 approaches and stops for explicit approval of the selected design.
   3. `plan-coder` creates or reuses safe isolation, establishes a green baseline, writes the local specification, stops for specification approval, decomposes it into vertical tickets, then stops for ticket approval and implementation authorization.
   4. `tdd-coder` executes exactly one unblocked ticket at a time through Red-Green, affected checks, a plan-checkbox update, and an atomic commit. Repeat until all tickets are complete.
   5. `delivery-coder` performs findings-first review, routes repairs back through TDD, runs the full applicable suite, and alone may produce the terminal completion claim.
5. Keep the durable plan checkboxes as task-state truth and mirror them in the runtime plan with at most one active ticket.
6. Reopen the affected approval gate whenever scope or architecture changes. Return to `design-coder` when implementation evidence invalidates an approved assumption.
7. Stop after the same blocking condition occurs three consecutive times, preserving the exact evidence and resume point.

The three human gates are design approval, written-specification approval, and ticket-set approval plus implementation authorization. After the third gate, proceed autonomously within the approved scope through TDD, review, verification, and commits.

## Stop Conditions

Stop and report the recoverable state when:

- a required local or upstream skill is missing or incompatible;
- no safe isolated worktree can be created or reused;
- baseline verification fails before implementation;
- an approval gate is pending or reopened;
- the worktree contains unexplained changes;
- the same blocker occurs three consecutive times;
- `delivery-coder` cannot obtain fresh verification evidence from all required checks.

Never push, create a pull request, publish external tickets, stage unrelated changes, or claim completion outside `delivery-coder` without separate explicit authorization.
