---
name: spec-coder
description: Orchestrate code-changing requests through requirements grilling, design, workspace-aware planning, ticket-level TDD, review, and verified delivery. Use by default for feature, bug-fix, refactor, or other implementation requests; do not auto-trigger for read-only explanation, status, investigation, or review, and honor explicit requests to skip spec-coder or directly modify.
---

# Spec Coder

Validate Host capabilities before invocation or dispatch.

## Required Reading

Every entry, including standalone invocation and resume, uses this common envelope.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).
- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).

## Conditional Reading

- **Selected Task Playbook:** before discovery, load [Shared task SOP scaffold](../../references/task-playbook-contract.md#shared-task-sop-scaffold), [Route precedence and one-selection rule](../../references/task-playbook-contract.md#route-precedence-and-one-selection-rule), and [Conversational TODO boundary](../../references/task-playbook-contract.md#conversational-todo-boundary); then dereference the one exact `conditional_references` link, never siblings.
- **Gate transition:** before Gate 1, Gate 2, Gate 3, or a reopened Gate 3 transition, load [Approval Gates](../../references/workflow-contract.md#approval-gates) and [Failure Transitions](../../references/workflow-contract.md#failure-transitions).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and apply [human authority](../../principles/protect-human-authority.md#protect-human-authority) before bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Configuration](../../references/subagent-routing-contract.md#configuration), and [Route Selection](../../references/subagent-routing-contract.md#route-selection).
- **Dispatch assembly:** before dispatching any child, load [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Isolation:** when selected or needed for a parallel mutation request, invoke bundled `using-git-worktrees`; Host loads it.
- **Executor handoff and recovery:** before post-Gate-3 entry or resumed frontier selection, load [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor), [Recovery](../../references/workflow-contract.md#recovery), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), and [Result Integration](../../references/subagent-routing-contract.md#result-integration), even for main-local or no-dispatch execution.
- **Workspace preparation:** before preparing dependencies or capturing the fresh baseline, load [CLI and explicit observations](../../references/verification-contract.md#cli-and-explicit-observations), [Capture and record schema](../../references/verification-contract.md#capture-and-record-schema), [Comparison and exit behavior](../../references/verification-contract.md#comparison-and-exit-behavior), and [Worked invocation](../../references/verification-contract.md#worked-invocation).

## Layers

Select one Task SOP, its Stage SOP, and triggered Principles. Contracts own
permissions and formats; Stage Skills are compatibility entries, not SOP owners.

## Input

A coding request or interrupted workflow.

## Output

A selected read-only workspace and a prepared workspace before writes; an approved or autonomously selected specification and approved or autonomously selected vertical-ticket plan; one atomic commit per completed ticket, review, fresh verification evidence, and a `delivery-coder` report.

## Process

1. Inspect bounded request and repository facts: current branch, plan checkboxes,
   Git log, worktree, and artifacts.
   Under **Selected Task Playbook**, choose one `TaskPlaybookSelection`; record
   evidence, nearby rejected routes, and its phase steps and skip reasons as
   non-authorizing conversational TODOs. Respect Host compatibility and
   `disable-model-invocation: true`.
2. Account for initial changes and select a safe workspace. Record its path,
   mode, base, changes, and capabilities. Invoke **Isolation** only if selected.
   Start `grill-coder` read-only. Prepare dependencies and establish the fresh
   green baseline with `verification-evidence.py` before a target-project write;
   failure stops writes. Resume
   at the earliest incomplete phase under
   **Executor handoff and recovery**.
3. Follow the selected Task Playbook sequence through `grill-coder`,
   `design-coder`, `plan-coder`, implementation, and delivery. Apply **Gate
   transition**; Skills never reconstruct another task procedure.
4. After Gate 3, load **Executor handoff and recovery**. Every nonempty plan,
   including a singleton, enters the native implement-spec executor. Follow
   approved or autonomously selected durable planned wave order through the
   dependency-aware execution wave's earliest incomplete ready frontier. Each
   ticket gets one `tdd-coder`
   lifecycle; main accepts, freshly verifies, commits, and advances serially.
   Load **Dispatch assembly** only before child dispatch and **Isolation** for an
   isolated worker; no implement-spec wrapper or merger subagent exists.
5. After all tickets, invoke `delivery-coder` for findings-first review, repairs,
   fresh full verification, and the only terminal completion claim.
6. Invalid architecture returns to `design-coder`. Apply **Gate transition**;
   scope expansion needs human review. Approved post-Gate-3 scheduling-input
   changes use the [Reopened Gate 3 scheduling barrier](../../references/workflow-contract.md#reopened-gate-3-scheduling-barrier);
   unchanged inputs bypass it and no fourth gate exists.
7. After three identical blockers, preserve exact evidence and the resume point.

## Approved Ticket Execution Waves

**Dispatch assembly** owns waves, base, frontier, and briefs.

## Stop Conditions

Stop with recoverable state when:

- a capability required for the selected path is missing or incompatible;
- no safe workspace can be selected under the user's constraints;
- workspace safety, preparation, or baseline verification fails before a write;
- an interactive approval gate is pending, or a reopened autonomous gate lacks
  a unique grounded recommendation;
- changes cannot be attributed or separated from user work;
- the same blocker occurs three consecutive times;
- `delivery-coder` cannot obtain fresh verification evidence from all required checks.

Never push, create a pull request, publish external tickets, stage unrelated changes, or claim completion outside `delivery-coder` without separate explicit authorization.
