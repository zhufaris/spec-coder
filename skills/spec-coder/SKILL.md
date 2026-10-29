---
name: spec-coder
description: Orchestrate code-changing requests through requirements grilling, design, workspace-aware planning, ticket-level TDD, review, and verified delivery. Use by default for feature, bug-fix, refactor, or other implementation requests; do not auto-trigger for read-only explanation, status, investigation, or review, and honor explicit requests to skip spec-coder or directly modify.
---

# Spec Coder

Coordinate stages under the owners below; validate Host capabilities before
invocation or dispatch.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Recovery](../../references/workflow-contract.md#recovery), [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).

- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).
- [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Result Integration](../../references/subagent-routing-contract.md#result-integration).

## Conditional Reading

- **Selected Task Playbook:** before entering discovery, load [Route precedence and one-selection rule](../../references/task-playbook-contract.md#route-precedence-and-one-selection-rule) and [Conversational TODO boundary](../../references/task-playbook-contract.md#conversational-todo-boundary); then dereference the selection's one exact `conditional_references` link, never its sibling kind anchors.
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route or dispatching any child, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Configuration](../../references/subagent-routing-contract.md#configuration), [Route Selection](../../references/subagent-routing-contract.md#route-selection), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Isolation:** when selected or needed for a parallel mutation request, invoke bundled `using-git-worktrees`.
- **Workspace preparation:** before preparing dependencies or capturing the fresh baseline, load [CLI and explicit observations](../../references/verification-contract.md#cli-and-explicit-observations), [Capture and record schema](../../references/verification-contract.md#capture-and-record-schema), [Comparison and exit behavior](../../references/verification-contract.md#comparison-and-exit-behavior), and [Worked invocation](../../references/verification-contract.md#worked-invocation).

## Input

A new coding request, or a repository containing partial spec-coder artifacts from an interrupted workflow.

## Output

A selected workspace for read-only discovery and design, then a prepared
workspace before target-project writes, an approved or autonomously selected specification,
approved or autonomously selected vertical-ticket plan,
one atomic commit per completed ticket, review results, fresh verification
evidence, and a final delivery report produced through `delivery-coder`.

## Process

1. Inspect the request, repository instructions and bounded repository facts,
   including current branch, plan checkboxes, Git log, worktree state and
   relevant artifacts. Select exactly one
   `TaskPlaybookSelection`, record the evidence and nearby rejected routes,
   then copy its exact phase steps and explicit skip reasons into conversational
   TODOs. Those TODOs guide progress but grant no authority. Check Host
   compatibility and respect `disable-model-invocation: true`.
2. Account for initial changes and select a safe workspace, invoking
   `using-git-worktrees` only for isolation. Record path, mode, base, changes
   and capabilities; start `grill-coder` and design read-only. Before a qualifying
   GLOSSARY/ADR write, or after Gate 1 before planning, prepare dependencies and
   establish the fresh green baseline with
   `scripts/verification-evidence.py capture` for each explicit command.
   Keep stdout JSON conversational, checking child `exit_code` separately.
   Failed or uncertain preparation stops all target-project writes. On resume,
   infer the earliest incomplete phase and verify freshly under Recovery.
3. Run `grill-coder` for confirmed requirements, then `design-coder` for 2-3
   alternatives and Gate 1. Run `plan-coder` for workspace revalidation,
   specification/Gate 2 and vertical tickets with durable waves/Gate 3.
   Apply Approval Gates to each interactive or autonomous transition.
4. After Gate 3, execute the approved or autonomously selected durable planned wave order through one dependency-aware execution wave. Every nonempty plan,
   including a singleton, enters the native implement-spec executor. Main runs the earliest durable-wave ready frontier
   (at most four direct implementers), recomputing after each accepted result.
   Each ticket gets one `tdd-coder` Red-Green or structural lifecycle and the
   required assembled brief. Main alone accepts, freshly verifies, commits and
   advances each ticket. No implement-spec wrapper or merger subagent exists.
5. When all tickets are complete, invoke `delivery-coder` for findings-first
   review, TDD repairs and fresh full verification. Only that stage produces
   the terminal completion claim.
6. Return to `design-coder` when evidence invalidates architecture. Apply
   Approval Gates to in-scope autonomous reconsideration; scope expansion needs
   human review. For approved post-Gate-3 scheduling-input changes, return
   immediately under the canonical [Reopened Gate 3 scheduling
   barrier](../../references/workflow-contract.md#reopened-gate-3-scheduling-barrier),
   which owns the halt, renewed plan/approval, artifact check, result accounting,
   compatibility, and frontier reconstruction. Unchanged inputs bypass it; no
   fourth gate is created.
7. Stop after the same blocking condition occurs three consecutive times and
   preserve exact evidence and the resume point.

## Approved Ticket Execution Waves

Apply [Execution Waves](../../references/subagent-routing-contract.md#execution-waves),
[Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests)
and [Result Integration](../../references/subagent-routing-contract.md#result-integration).
The native implement-spec executor preserves durable membership, applies the
recorded wave base and adaptive workspace decision, and recomputes the earliest
incomplete frontier after each accepted result. Use the common brief for every
dispatch, including a main-created promotion sibling.

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
