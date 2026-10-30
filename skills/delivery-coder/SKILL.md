---
name: delivery-coder
description: Review and verify a completed spec-coder plan before declaring delivery. Use after all planned tickets are committed, or to resume final review, repair, and full-suite verification of an approved or autonomously selected specification.
---

# Delivery Coder

Compatibility entry. Validate input/authority; execute the required stage SOP.

## Required Reading

Every entry, including standalone invocation and resume, requires these owners; reuse only current sections.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery).
- [Review Execution](../../references/subagent-routing-contract.md#review-execution).

- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).
- [Command interface](../../references/artifact-format.md#command-interface), [Findings and compatibility](../../references/artifact-format.md#findings-and-compatibility).
- [Delivery evidence](../../references/artifact-format.md#delivery-evidence).

- [Stage procedure](../../playbooks/stages/delivery.md#procedure).

## Conditional Reading

- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Selected Task Playbook:** validate the approved [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection). Consume its step without rerouting. Missing orchestrated handoffs return to router; standalone/resume reconstruct a missing handoff from `conditional_references` step only. Freshly verify `delivery_proof`.
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route or dispatching any child, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Configuration](../../references/subagent-routing-contract.md#configuration), [Route Selection](../../references/subagent-routing-contract.md#route-selection), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Blinded evaluation lifecycle:** after mandatory deterministic Green, and
  only when the approved selection is **Skill Change** or **Workflow Eval**,
  load [Blinded evaluation constraints](../../references/task-playbook-contract.md#blinded-evaluation-constraints),
  [Workflow Eval Execution](../../references/subagent-routing-contract.md#workflow-eval-execution),
  and the candidate/judge role additions in the worker brief. Other playbooks
  do not load or run this comparison. It does not replace either review axis,
  fresh verification, or artifact checking.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

The approved or autonomously selected `TaskPlaybookSelection`, specification
and plan, completed ticket commits, current diff and Git history, repository
instructions, domain language, architecture decisions, and authoritative
verification commands. Autonomous selection does not reduce review scope or
fresh-verification requirements.

## Output

Severity-ordered findings, TDD-backed repairs, fresh full-suite evidence, and a
completion report naming commits, checks and residual risks.

## Process

Execute the required SOP with validated input. Main may delegate under routing authority; children must not spawn.

## Stop Conditions

Stop without claiming completion when:

- the specification, plan, or expected commits are missing or inconsistent;
- review finds a design assumption invalid, in which case return to `design-coder` and reopen approval;
- any behavior repair has not completed the `tdd-coder` loop;
- any full-suite command fails or cannot be run;
- changes cannot be safely attributed or separated in the selected workspace;
- the same blocking condition occurs three consecutive times.

Preserve the failing command/output, finding, workspace, branch, initial changes,
and plan state for safe resume.
