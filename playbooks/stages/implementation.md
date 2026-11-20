# Implementation stage playbook

## Procedure

### Capabilities

`tdd` at public seams, native affected checks, task-owned diff review, and
evidence return. This playbook does not orchestrate executor.

### Conditional Principles

- **Behavior preservation:** read [preserve-observable-behavior](../../principles/preserve-observable-behavior.md#preserve-observable-behavior) only on this observed trigger.

### Scope and authority

This stage consumes one executor-issued ticket handoff and runs a one-ticket
Red/Green lifecycle, or the structural verification path for an approved
behavior-preserving change. It implements one unblocked ticket only and must
return its evidence, then return to the native implement-spec executor.

The [native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor)
owns entry and handoff. The [detailed executor and delegation authority](../../references/subagent-routing-contract.md#detailed-executor-and-delegation-authority)
is the sole detailed owner of [heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat),
[delegation eligibility and execution mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode),
[execution waves](../../references/subagent-routing-contract.md#execution-waves),
[attempt promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion),
and [result integration](../../references/subagent-routing-contract.md#result-integration).
It must not select waves or dispatch siblings. It must not
integrate, accept, stage, or commit a result. Main-only acceptance, commit, plan
advancement, and completion remain outside this playbook.
The main agent retains commit ownership: this lifecycle does not stage explicit paths,
create a conventional commit, or use `git add -A`.

### Steps

1. Validate the issued handoff without recomputing executor decisions. It must
   identify one Gate-3-approved or autonomously selected unblocked vertical ticket
   from an approved or autonomously selected durable planned wave, its
   specification and TaskPlaybookSelection references, authoritative workspace,
   recorded base, relevant initial changes, approved `Build cache`, selected
   `red_or_pin`, and `delivery_proof`. Missing or conflicting input returns a
   blocker to the native executor; never select replacement work.
2. Re-read only that ticket's specification references, domain language, ADRs,
   tests, and selected task step. Resolve the referenced decisions and
   boundaries before editing. Confirm the approved build-cache reservation can
   be configured repository-natively; never substitute `/tmp`.
3. Apply the selected `red_or_pin`. For changed behavior, write the outcome
   reproduction and run the focused test to observe the expected failure as
   Behavior Red for the intended reason. If it passes unexpectedly or fails
   for another reason, correct the test setup first. For structural-only work,
   use the path below instead of manufacturing a behavior failure.
4. Make the minimum implementation for Green within the ticket's approved
   domain, application, or adapter boundary. Do not anticipate another ticket or
   broaden the approved scope.
5. Run the focused test and repeat one behavior at a time until the applicable
   success, rejection, concurrency, duplicate, and partial-failure scenarios
   have evidence. Sequential fakes do not prove concurrency guarantees.
6. Run `scripts/validate-affected.py --repo <authoritative-repository> --path
   <task-owned-path>` for every supported spec-coder path. Arbitrary repositories
   use repository-native checks. The mapper rejects missing or unmapped paths; for a deleted or
   pre-rename path, pass an existing post-change owner or test path. Record the
   exact commands and results. Affected verification grants no acceptance,
   commit, or completion authority.
7. Inspect the complete task-owned diff against the recorded base and initial
   changes. Attribute every changed and untracked path, review scope,
   duplication, naming, domain consistency, rule ownership, dependency
   direction, boundary types, and assembly, and preserve all unrelated work.
8. Return base identity, the complete task-owned diff, changed and untracked
   paths, Behavior Red/Green or structural preservation evidence, exact
   commands and results, findings, and blockers. Do not modify a durable plan,
   stage files, or create a commit; the executor performs main-owned fresh
   integration verification and acceptance.

Never clean, stash, reset, switch branches over, stage, commit, or amend user
work. Never skip or weaken a failing test, suppress a finding, or broaden scope
without returning to the appropriate approval gate.

Apply the contract's [implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery) requirements for relevant domain and persistence changes. Test selected behavior through its public seams, name tests after domain outcomes, and collect the separate mapping/dependency evidence required there; do not substitute class or method-name assertions.

### Structural verification path

For an approved behavior-preserving refactor or dependency-only repair, record
the unchanged outcomes and baseline behavior checks. Keep those checks green
during structural edits. If a dependency check exposes the violation, observe
its failure before repair and its success after repair. Where no such tooling
exists, record concrete before/after module or import review evidence. Finish
with all affected checks and return the same complete evidence described in
step 8. Do not manufacture a behavior failure for unchanged outcomes; new
behavior requires the normal Red/Green path.
