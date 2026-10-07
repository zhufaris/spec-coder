---
name: tdd-coder
description: Implement one approved, unblocked vertical ticket through an evidence-backed Red-Green loop, affected verification, plan-state update, and atomic commit. Use after plan-coder authorization or to resume a partially completed spec-coder ticket.
---

# TDD Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Compose the installed `tdd` skill at the public testing seams already selected in the specification and ticket plan.

Route implementation work through the [subagent routing contract](../../references/subagent-routing-contract.md). This skill delegates eligible implementation work by default to one direct layer-2 child, even when the execution wave contains one ticket. A delegated implementation must remain inside the approved or autonomously selected ticket, be bounded and reversible, and expose an explicit verification seam. Ambiguous scope, missing context, high-risk mutation, attribution, and commit ownership remain with the main agent.

Read and apply the [domain design contract](../../references/domain-design-contract.md) to resolve ticket constraints and distinguish behavior verification from dependency verification.

Read the [worked examples](../../references/domain-design-examples.md) when implementing rules, concurrency mechanisms or cross-context failures at the approved testing seams.

## Input

One unblocked ticket whose dependencies are complete, its acceptance criteria,
the approved or autonomously selected design and its testing seams, the selected
safe workspace with accounted-for initial changes, and green baseline evidence.
The workspace may be in place or isolated; autonomous selection does not relax
ticket readiness or verification.

## Output

Observed Red and Green evidence for behavior changes, preservation and dependency evidence for structural work, passing affected checks, a checked-off durable ticket, a synchronized runtime plan, and one atomic Conventional Commit containing only that ticket's files.

## Process

1. Confirm the handed-off ticket belongs to the Gate-3-approved or autonomously selected durable planned wave
   and the current planned wave is the earliest incomplete one. Confirm all
   of its blockers are complete. Verify the selected workspace, recorded wave
   base, and initial changes; preserve unrelated work in either mode. The
   runtime wave may contain other ownership-safe tickets, but this invocation
   owns only its one selected ticket and must not pull later-wave work forward.
2. Re-read the relevant specification, domain language, ADRs, ticket acceptance criteria, and existing test patterns. Resolve scenario/invariant and architecture references, affected contexts/model elements, enforcing owners, boundary data, atomicity/conflict and recovery semantics. Resolve missing decisions before implementation. If acceptance requires only structural preservation or dependency repair, use the structural path below instead of steps 3-6; mixed tickets still require behavior Red-Green for changed outcomes.
3. Write one behavior-focused test through an approved public seam for an applicable scenario or invariant.
4. Run that focused test and have main observe the expected failure as behavior
   Red. If it passes unexpectedly or fails for an unrelated reason, correct the
   test setup before implementation. For structural-only work, main instead
   establishes the structural preservation and dependency evidence required by
   the path below; do not manufacture a behavior Red.
5. After main owns that evidence, delegate eligible implementation work by
   default. Main supplies the complete approved boundary, exclusions, recorded
   wave base, mutation ownership, verification seam, and
   `delegation_allowed = false`. The direct child writes the minimum implementation
   needed for Green. Place rules in the approved domain modules, coordination in
   application modules, and external conversion in adapters. It must not spawn
   or delegate directly or indirectly, and workers must not stage or commit. If
   it needs decomposition or another agent, it returns its evidence and blocker
   to main. The brief requires the shared **Worker Progress Heartbeat** /
   `ProgressSnapshot` when proactive child-to-main messaging is available; main
   records that capability **before or at dispatch**:
   starting, every 45-60 seconds while active, on phase change, before and
   after a long command, and immediately on blocker, failure, or completion.
   `heartbeat-capability-unavailable` preserves delegation. A
   `heartbeat-overdue` means a wait timeout or missed interval; an ordinary observation is
   `awaiting-heartbeat` and neither grants failure, blocker, interrupt, takeover, promotion, or local
   fallback authority; main-only diff acceptance, fresh verification, and
   completion authority remain unchanged. Main-local behavior remains the path
   for ineligible work, an applicable opt-out, or recorded spawn-unavailable
   fallback; explicitly
   required delegation follows the routing contract's blocker outcome. Do not
   anticipate later tickets.
6. Run the focused test. Repeat steps 3-6 one behavior at a time until all applicable ticket scenarios and invariants have test evidence, including existing tests where sufficient. Include approved concurrent interleavings, duplicates and partial failures when relevant; a sequential fake alone does not prove a persistence concurrency guarantee. Then run the affected checks: relevant test modules, lint, type checks, and build steps defined by the repository.
7. Main inspects the complete task-owned diff, attributes every change, and
   freshly verifies the focused behavior or structural evidence plus all
   affected checks in the authoritative integrated state. Then perform a
   lightweight self-review for scope, duplication, naming, domain consistency,
   and accidental architecture violations. Check rule ownership across entry
   points and verify source dependencies, exposed boundary types and assembly
   with existing tooling or a concrete source review; child-local or passing
   behavior tests alone do not establish integrated Green or dependency
   compliance.
8. Update the durable plan checkbox and runtime mirror only after the affected checks pass.
9. Inspect the diff against recorded initial changes, stage explicit paths owned by the ticket, and inspect the entire proposed commit for user-owned hunks or previously staged unrelated files. Apply the shared Git safety rules, using a verified path-scoped commit or isolation when necessary to preserve unrelated staged work. Create one Conventional Commit whose subject describes the delivered behavior.
10. Select the next unblocked ticket, or hand off to `delivery-coder` when none remain.

A failed, uncertain, evidence-poor or boundary-crossing delegated attempt is not retried across configured tiers. Preserve its route, output and verification state and return to the active main agent. Only main may promote once by creating an inherited-main layer-2 promotion sibling whose brief includes `delegation_allowed = false`, must not stage or commit, and the same Worker Progress Heartbeat / `ProgressSnapshot` reporting requirements with capability recorded **before or at dispatch**; the failed child never creates its replacement. Heartbeat capability unavailable preserves delegation; heartbeat overdue is a wait timeout or missed interval, and an ordinary awaiting-heartbeat observation cannot itself trigger promotion, repair, or local fallback. A second failure follows this skill's normal repair or stop conditions.

Never use `git add -A`. Never stage unrelated user changes, amend a commit that predates the ticket, skip or weaken a failing test, or broaden scope without returning to the appropriate approval gate.

Apply the contract's [implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery) requirements for relevant domain and persistence changes. Test approved behavior through its public seams, name tests after domain outcomes, and collect the separate mapping/dependency evidence required there; do not substitute class or method-name assertions.

## Structural verification path

For an approved behavior-preserving refactor or dependency-only repair, record the unchanged outcomes and baseline behavior checks. Keep those checks green during structural edits. If a dependency check exposes the violation, observe its failure before repair and its success after repair. Where no such tooling exists, record concrete before/after module/import review evidence. Finish with all affected checks and resume step 7. Do not manufacture a behavior failure for unchanged outcomes; new behavior requires the normal Red-Green path.

## Stop Conditions

Stop and preserve evidence when:

- no approved unblocked ticket exists;
- the selected workspace is unsafe or changes cannot be attributed/separated from user-owned work;
- a behavior change cannot demonstrate Red for the intended reason, or structural work lacks preservation/dependency evidence;
- implementation evidence invalidates the approved design;
- an affected verification command fails after diagnosis;
- the same blocking condition occurs three consecutive times.

Do not mark the ticket complete or commit unless every ticket-level check is green.
