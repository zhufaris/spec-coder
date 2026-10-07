---
name: delivery-coder
description: Review and verify a completed spec-coder plan before declaring delivery. Use after all planned tickets are committed, or to resume final review, repair, and full-suite verification of an approved specification.
---

# Delivery Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Use the `code-review` review method only through a route compatible with the review mode below, then invoke `verification-before-completion`; route behavior repairs through `tdd-coder`.

Apply the [subagent routing contract](../../references/subagent-routing-contract.md). Delivery delegates review by default to exactly two independent, read-only direct layer-2 reviewers: one Standards reviewer and one Spec reviewer. Each direct-child brief must include the literal `delegation_allowed = false`, say that the reviewer **must not spawn** or delegate directly or indirectly (including through another skill, workflow, tool or agent), prohibit edits/staging/commits, and provide complete inputs, explicit exclusions, the expected evidence, and the return format. Both briefs require the shared **Worker Progress Heartbeat** / `ProgressSnapshot` when proactive child-to-main messaging is available: report at start, every 45-60 seconds while active, on phase change, before and after a long command, and immediately on blocker, failure, or completion. If a reviewer needs another specialist or more decomposition, it returns its evidence and blocker to main.

Each reviewer collects bounded evidence for its assigned axis. The active main agent remains accountable: main authors the final Standards/Spec conclusions. Reviewer output is evidence only: main retains scope and attribution decisions, repair judgment, integration review, fresh verification, delivery aggregation, commit authority, and every completion claim.

Read and apply the [domain design contract](../../references/domain-design-contract.md) to verify scenario/invariant coverage and architecture evidence separately.

Read the [worked examples](../../references/domain-design-examples.md) when reviewing rule ownership, consistency guarantees, type leakage or disproportionate abstractions.

## Input

The approved or autonomously selected specification and plan, completed ticket
commits, current diff and Git history, repository instructions, domain language,
architecture decisions, and authoritative verification commands. Autonomous
selection does not reduce review scope or fresh-verification requirements.

## Output

Findings ordered by severity, TDD-backed repair commits when needed, fresh evidence from the full applicable suite, and a completion report that identifies commits, checks, and any residual risks.

## Review Execution

Choose the review mode before starting either axis:

- With eligible spawn capability and no applicable opt-out, directly brief the two reviewers. The **Standards reviewer** receives the repository instructions, current status, cumulative task diff, relevant history and verification conventions; it checks correctness, security, performance, error handling, test quality, repository standards and unintended scope. The **Spec reviewer** receives the approved specification and plan, completed ticket commits, cumulative task diff, domain and architecture decisions and test evidence; it checks acceptance criteria, public contracts, scenario/invariant coverage, dependency direction, architecture evidence and scope fidelity. Keep the axes independent and require findings ordered by severity with concrete file/line evidence and any uncertainty.
- A **review-specific opt-out** or **request-wide opt-out** selects main-local review for both the Standards axis and Spec axis and forbids direct or indirect spawning for the affected scope. Main performs the same two independent passes with the same inputs, checks and findings-first output described above.
- When spawn unavailable and delegated review was not explicitly required, record the unavailable capability and use that same main-local two-axis review.
- When spawn unavailable and delegated review was explicitly required, stop with a concrete Host-capability blocker; do not silently substitute local review.
- When spawn exists but no direct-child slot is currently available, wait
  through the Host mechanism and recompute capacity. Do not turn temporary
  capacity exhaustion into local fallback or a delegated review wave.

Delegated mode prepares exactly two distinct direct layer-2 briefs, one with
`axis = standards` and one with `axis = spec`. Both briefs are read-only, carry
`delegation_allowed = false`, and state `must_not_spawn = true`; neither
reviewer may delegate directly or indirectly. Each must use the shared
`ProgressSnapshot` reporting schedule above when proactive messaging is
available. Before or at dispatch, main records `heartbeat-ready` when proactive
messaging is available or `heartbeat-capability-unavailable` when it is not;
the unavailable state preserves the selected delegation decision. While
waiting, an ordinary no-message observation is `awaiting-heartbeat`. Only a
Host wait timeout or missed interval is `heartbeat-overdue`; it still means no
message only and does not create a failure or blocker or grant interruption,
takeover, promotion, or local fallback authority. Main-only completion
authority, diff acceptance, and fresh verification remain unchanged.
Nondelegated modes prepare no reviewer brief.

The upstream `code-review` skill is compatible only when it can preserve the selected mode and the two-layer limit. In a review/request opt-out or spawn-unavailable local fallback, main **must not invoke** `code-review` if it would itself delegate, spawn children or otherwise violate the opt-out. Instead, main performs the equivalent Standards axis and Spec axis checks spelled out above. Do not claim that the Host enforces the no-delegation instruction when it does not; the brief remains authoritative.

## Process

1. Confirm every ticket checkbox is complete and inspect the selected workspace/mode, branch, recorded initial changes, Git log, and cumulative task diff. In-place execution is valid; preserve unrelated user changes and distinguish them from ticket-owned edits.
2. Execute the selected review mode for both the Standards and Spec axes. Report findings before conclusions. Main inspects all returned or locally collected evidence and authors the final Standards/Spec conclusions; reviewer success never grants approval, repair, fresh-verification, commit, delivery or completion authority.
3. Check acceptance criteria, domain language, public contracts, dependency direction, Clean Architecture boundaries, error handling, security, and unintended scope. Map each in-scope scenario/invariant to completed tickets and actual test evidence. Verify context/model ownership, shared rule placement, and applicable atomicity/conflict, idempotency and recovery guarantees. Verify architecture separately with dependency checks or documented imports, exposed types and assembly; plan checkboxes and green sequential tests alone are insufficient. Check that simple CRUD/query work has not acquired unjustified abstractions or lost access controls.
4. Route behavior defects through `tdd-coder`: add or correct a failing test, observe Red, implement the minimum repair, run affected checks, and create a separate atomic commit. Perform structural refactoring only while behavior tests remain green.
5. Repeat review until no unresolved blocking findings remain. Do not conceal accepted residual risks.
6. Invoke `verification-before-completion` and freshly run every applicable full test suite, lint, type-check, build, and repository-specific validation command. Do not rely on earlier output or a ticket-level subset.
7. Inspect final status and commit history against recorded initial changes. Confirm each task change is represented by an atomic commit and no unrelated change entered those commits. Preserve any user-staged work that predated the task; its presence is not itself a delivery failure.
8. Report the delivered specification, commits, fresh evidence, resolved findings, and residual risks. Claim completion only when all required checks pass.

If delegated evidence fails, is uncertain, lacks required support or crosses its boundary, preserve the chosen route and attempt evidence and return to the active main agent. Only main may promote once by creating an inherited-main layer-2 promotion sibling with `delegation_allowed = false`, read-only/no-edit/no-stage/no-commit limits, and the shared Worker Progress Heartbeat / `ProgressSnapshot` reporting requirement. A review child cannot create its replacement. Heartbeat capability unavailable preserves delegation; heartbeat overdue or a wait timeout is no message only and cannot itself trigger promotion, failure, blocker, interruption, takeover, or local fallback. Do not cycle through configured tiers, and never treat apparent subagent success as approval or completion authority.

Do not push, create a pull request, publish external tickets, amend pre-existing commits, or make external changes without separate explicit authorization.

Apply the contract's [implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery) review requirements to applicable domain and persistence changes. Map approved decisions to actual behavior, mapping and dependency evidence across affected entry paths; a model inventory or renamed operation is not enforcement evidence.

## Stop Conditions

Stop without claiming completion when:

- the specification, plan, or expected commits are missing or inconsistent;
- review finds a design assumption invalid, in which case return to `design-coder` and reopen approval;
- any behavior repair has not completed the `tdd-coder` loop;
- any full-suite command fails or cannot be run;
- changes cannot be safely attributed or separated in the selected workspace;
- the same blocking condition occurs three consecutive times.

Preserve the failing command, output, finding, workspace/mode, branch, initial user changes, and current plan state so the workflow can resume safely.
