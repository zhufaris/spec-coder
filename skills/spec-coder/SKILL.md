---
name: spec-coder
description: Orchestrate code-changing requests through requirements grilling, design, workspace-aware planning, ticket-level TDD, review, and verified delivery. Use by default for feature, bug-fix, refactor, or other implementation requests; do not auto-trigger for read-only explanation, status, investigation, or review, and honor explicit requests to skip spec-coder or directly modify.
---

# Spec Coder

Validate Host capabilities.

## Required Reading

Every entry; standalone invocation and resume:

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).
- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).

## Conditional Reading

Load triggered sections before acting.

- **Selected Task Playbook:** [scaffold](../../references/task-playbook-contract.md#shared-task-sop-scaffold), [selection](../../references/task-playbook-contract.md#route-precedence-and-one-selection-rule), [TODOs](../../references/task-playbook-contract.md#conversational-todo-boundary); dereference one `conditional_references` link, never siblings.
- **Gate transition:** [gates](../../references/workflow-contract.md#approval-gates), [failures](../../references/workflow-contract.md#failure-transitions).
- **Human review:** [snapshot](../../references/approval-review-contract.md#review-snapshot), [rendering](../../references/approval-review-contract.md#rendering), [safety](../../references/approval-review-contract.md#authority-and-safety), [duties](../../references/approval-review-contract.md#owning-skill-responsibilities), [authority](../../principles/protect-human-authority.md#protect-human-authority), then bundled `show-me`.
- **Workspace selection:** in-place, isolation, or resume: [owner](../../references/workflow-contract.md#workspace-selection).
- **Delegation:** [authority](../../references/subagent-routing-contract.md#authority), [tiers](../../references/subagent-routing-contract.md#tiers), [eligibility](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [configuration](../../references/subagent-routing-contract.md#configuration), [route](../../references/subagent-routing-contract.md#route-selection).
- **Dispatch assembly:** before dispatch, [waves](../../references/subagent-routing-contract.md#execution-waves), [parallel](../../references/subagent-routing-contract.md#explicit-parallel-requests), [heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [brief](../../references/subagent-routing-contract.md#worker-brief-assembly), [promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [duties](../../references/subagent-routing-contract.md#stage-responsibilities), [integration](../../references/subagent-routing-contract.md#result-integration), template [assembly](../../references/worker-brief-template.md#assembly), [common](../../references/worker-brief-template.md#common-brief), [roles](../../references/worker-brief-template.md#role-additions).
- **Isolation:** when selected, invoke bundled `using-git-worktrees`; Host loads it.
- **Executor handoff and recovery:** post-Gate-3/resume (main-local included): [executor](../../references/workflow-contract.md#native-implement-spec-executor), [recovery](../../references/workflow-contract.md#recovery), [waves](../../references/subagent-routing-contract.md#execution-waves), [integration](../../references/subagent-routing-contract.md#result-integration).
- **Workspace preparation:** [observations](../../references/verification-contract.md#cli-and-explicit-observations), [capture](../../references/verification-contract.md#capture-and-record-schema), [comparison](../../references/verification-contract.md#comparison-and-exit-behavior), [invocation](../../references/verification-contract.md#worked-invocation).

## Input

Coding request or resume.

## Output

Approved or autonomously selected specification; approved or autonomously selected vertical-ticket plan; verified delivery in approved or autonomously selected durable planned wave order.

## Process

1. Select one **Selected Task Playbook**; record nearby rejected routes, phase steps and skip reasons as non-authorizing TODOs.
2. Load **Workspace selection** before choosing in-place, **Isolation**, or **Resume**; account for changes/capabilities; record mode/path/base.
3. Run `grill-coder`, `design-coder`, `plan-coder`, `tdd-coder`, `delivery-coder` with **Gate transition**; start read-only; prepare dependencies; use `verification-evidence.py capture` before writes.
4. Gate 3 enters the native implement-spec executor (singleton included) under **Executor handoff and recovery**. Main runs each dependency-aware execution wave ticket through `tdd-coder`, freshly verifies, accepts, commits, advances; **Dispatch assembly**/**Isolation** when needed.
5. `delivery-coder` alone completes.
6. Invalid architecture returns to design; scope expansion requires review; scheduling uses the [barrier](../../references/workflow-contract.md#reopened-gate-3-scheduling-barrier); no fourth gate.

## Stop Conditions

See loaded owners.
