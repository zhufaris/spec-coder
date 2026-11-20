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

- **Selected Task Playbook:** before entering discovery, load [Route precedence and one-selection rule](../../references/task-playbook-contract.md#route-precedence-and-one-selection-rule) and [Conversational TODO boundary](../../references/task-playbook-contract.md#conversational-todo-boundary); then dereference the selection's one exact `conditional_references` link, never its sibling kind anchors.
- **Gate transition:** before Gate 1, Gate 2, Gate 3, or a reopened Gate 3 transition, load [Approval Gates](../../references/workflow-contract.md#approval-gates) and [Failure Transitions](../../references/workflow-contract.md#failure-transitions).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and apply [human authority](../../principles/protect-human-authority.md#protect-human-authority) before bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Configuration](../../references/subagent-routing-contract.md#configuration), and [Route Selection](../../references/subagent-routing-contract.md#route-selection).
- **Dispatch assembly:** before dispatching any child, load [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Isolation:** when selected or needed for a parallel mutation request, invoke bundled `using-git-worktrees`; Host loads it.
- **Executor handoff and recovery:** before entering the native executor after Gate 3 or reconstructing a resumed executor path, load [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor) and [Recovery](../../references/workflow-contract.md#recovery).
- **Workspace preparation:** before preparing dependencies or capturing the fresh baseline, load [CLI and explicit observations](../../references/verification-contract.md#cli-and-explicit-observations), [Capture and record schema](../../references/verification-contract.md#capture-and-record-schema), [Comparison and exit behavior](../../references/verification-contract.md#comparison-and-exit-behavior), and [Worked invocation](../../references/verification-contract.md#worked-invocation).

## Layers

Select one Task SOP, its Stage SOP, and triggered Principles. Contracts own
permissions and formats; Stage Skills are compatibility entries, not SOP owners.

## Input

A coding request or interrupted workflow.

## Output

A selected read-only workspace and a prepared workspace before writes; an approved or autonomously selected specification and approved or autonomously selected vertical-ticket plan; one atomic commit per completed ticket, review, fresh verification evidence, and a `delivery-coder` report.

## Process

1. Inspect the request, repository instructions and bounded repository facts,
   including current branch, plan checkboxes, Git log, worktree state and
   relevant artifacts. Under **Selected Task Playbook**, select exactly one
   `TaskPlaybookSelection`, record the evidence and nearby rejected routes,
   then copy its numbered task procedure, phase steps and explicit skip reasons into conversational
   TODOs. Those TODOs guide progress but grant no authority. Check Host
   compatibility and respect `disable-model-invocation: true`.
2. Account for initial changes and select a safe workspace, invoking
   **Isolation** only when selected. Record path, mode, base, changes
   and capabilities; start `grill-coder` and design read-only. Before a qualifying
   GLOSSARY/ADR write, or after Gate 1 before planning, prepare dependencies and
   establish the fresh green baseline with
   `scripts/verification-evidence.py capture` for each explicit command.
   Keep stdout JSON conversational, checking child `exit_code` separately.
   Failed or uncertain preparation stops all target-project writes. On resume,
   infer the earliest incomplete phase under **Executor handoff and recovery**.
3. Follow the selected Task Playbook's explicit stage sequence. Stage SOPs use `grill-coder`, `design-coder`, and `plan-coder` entries,
   then implementation and delivery. Apply
   **Gate transition** to each interactive or autonomous transition; neither
   router nor capability Skills reconstruct another task procedure.
4. After Gate 3, load **Executor handoff and recovery**; every nonempty plan, including a singleton, enters the native implement-spec executor.
   Follow approved or autonomously selected durable planned wave order through
   one dependency-aware execution wave and its earliest incomplete ready frontier,
   at most four direct implementers. Each ticket gets one `tdd-coder` lifecycle;
   main accepts, freshly verifies, commits, and advances it serially. No
   implement-spec wrapper or merger subagent exists. Before child dispatch,
   load **Dispatch assembly**; load **Isolation** for an isolated worker.
5. When all tickets are complete, invoke `delivery-coder` for findings-first
   review, TDD repairs and fresh full verification. Only that stage produces
   the terminal completion claim.
6. Return to `design-coder` when evidence invalidates architecture. Apply
   **Gate transition** to in-scope autonomous reconsideration; scope expansion needs
   human review. For approved post-Gate-3 scheduling-input changes, return
   immediately under the canonical [Reopened Gate 3 scheduling
   barrier](../../references/workflow-contract.md#reopened-gate-3-scheduling-barrier),
   which owns the halt, renewed plan/approval, artifact check, result accounting,
   compatibility, and frontier reconstruction. Unchanged inputs bypass it; no
   fourth gate is created.
7. Stop after the same blocking condition occurs three consecutive times and
   preserve exact evidence and the resume point.

## Approved Ticket Execution Waves

**Dispatch assembly** owns waves, base, frontier, and briefs.

## Stop Conditions

Stop and report the recoverable state when:

- a capability required for the selected path is missing or incompatible;
- no safe workspace can be selected under the user's constraints;
- selected-workspace safety or capability assessment fails before discovery;
- workspace preparation or baseline verification fails before a target-project
  write;
- an interactive approval gate is pending, or a reopened autonomous gate lacks
  a unique grounded recommendation;
- changes cannot be safely attributed or separated from user-owned work in the selected workspace;
- the same blocker occurs three consecutive times;
- `delivery-coder` cannot obtain fresh verification evidence from all required checks.

Never push, create a pull request, publish external tickets, stage unrelated changes, or claim completion outside `delivery-coder` without separate explicit authorization.
