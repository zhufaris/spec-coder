---
name: spec-coder
description: Orchestrate code-changing requests through requirements grilling, design, workspace-aware planning, ticket-level TDD, review, and verified delivery. Use by default for feature, bug-fix, refactor, or other implementation requests; do not auto-trigger for read-only explanation, status, investigation, or review, and honor explicit requests to skip spec-coder or directly modify.
---

# Spec Coder

Validate Host capabilities.

## Required Reading

Every entry, including standalone invocation and resume:

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).
- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).

## Conditional Reading

Load triggered sections before acting.

- **Selected Task Playbook:** [scaffold](../../references/task-playbook-contract.md#shared-task-sop-scaffold), [selection](../../references/task-playbook-contract.md#route-precedence-and-one-selection-rule), [TODOs](../../references/task-playbook-contract.md#conversational-todo-boundary); dereference one route, never siblings.
- **Gate transition:** [gates](../../references/workflow-contract.md#approval-gates), [failures](../../references/workflow-contract.md#failure-transitions).
- **Human review:** [snapshot](../../references/approval-review-contract.md#review-snapshot), [rendering](../../references/approval-review-contract.md#rendering), [safety](../../references/approval-review-contract.md#authority-and-safety), [duties](../../references/approval-review-contract.md#owning-skill-responsibilities), [authority](../../principles/protect-human-authority.md#protect-human-authority), then bundled `show-me`.
- **Workspace selection:** in-place, isolation, or resume: [owner](../../references/workflow-contract.md#workspace-selection).
- **Delegation:** [authority](../../references/subagent-routing-contract.md#authority), [tiers](../../references/subagent-routing-contract.md#tiers), [eligibility](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [configuration](../../references/subagent-routing-contract.md#configuration), [route](../../references/subagent-routing-contract.md#route-selection).
- **Dispatch assembly:** before a child, [waves](../../references/subagent-routing-contract.md#execution-waves), [parallel](../../references/subagent-routing-contract.md#explicit-parallel-requests), [heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [brief](../../references/subagent-routing-contract.md#worker-brief-assembly), [promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [duties](../../references/subagent-routing-contract.md#stage-responsibilities), [integration](../../references/subagent-routing-contract.md#result-integration), template [assembly](../../references/worker-brief-template.md#assembly), [common](../../references/worker-brief-template.md#common-brief), [roles](../../references/worker-brief-template.md#role-additions).
- **Isolation:** when selected, invoke bundled `using-git-worktrees`; Host loads it.
- **Executor handoff and recovery:** before post-Gate-3/resume, including main-local: [executor](../../references/workflow-contract.md#native-implement-spec-executor), [recovery](../../references/workflow-contract.md#recovery), [waves](../../references/subagent-routing-contract.md#execution-waves), [integration](../../references/subagent-routing-contract.md#result-integration).
- **Workspace preparation:** [observations](../../references/verification-contract.md#cli-and-explicit-observations), [capture](../../references/verification-contract.md#capture-and-record-schema), [comparison](../../references/verification-contract.md#comparison-and-exit-behavior), [invocation](../../references/verification-contract.md#worked-invocation).

## Input

Coding request or resume.

## Output

Approved or autonomously selected vertical-ticket plan and specification; verified delivery in approved or autonomously selected durable planned wave order, with main-owned commits.

## Process

1. Select one **Selected Task Playbook**; TODOs remain non-authorizing.
2. Load **Workspace selection** before choosing in-place, **Isolation**, or **Resume**; account for changes/capabilities; record mode/path/base.
3. Run `grill-coder`, `design-coder`, `plan-coder`, `tdd-coder`, `delivery-coder` in order with **Gate transition**; start read-only, prepare dependencies/baseline before writes, stop on failure.
4. After Gate 3 every plan, including a singleton, enters the native implement-spec executor under **Executor handoff and recovery**; each ticket gets `tdd-coder`; main freshly verifies, accepts, commits, advances. Trigger **Dispatch assembly** and **Isolation** only when needed.
5. `delivery-coder` alone completes.
6. Return invalid architecture to design, expanded scope to review, and scheduling changes to the [reopened barrier](../../references/workflow-contract.md#reopened-gate-3-scheduling-barrier); no fourth gate.

## Stop Conditions

See loaded owners.
