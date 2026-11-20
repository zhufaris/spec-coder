---
name: tdd-coder
description: Implement one executor-issued unblocked vertical ticket through evidence-backed Red-Green or structural verification and return provisional evidence. Use only from the native implement-spec executor with a validated or reconstructed handoff.
---

# TDD Coder

Compatibility entry. Validate input/authority; execute the required stage SOP.

## Required Reading

Every entry requires these owners, including standalone invocation and resume; reuse current sections.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery).

- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle), [Delivery evidence](../../references/artifact-format.md#delivery-evidence).
- [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Result Integration](../../references/subagent-routing-contract.md#result-integration).

- [Stage procedure](../../playbooks/stages/implementation.md#procedure).

## Conditional Reading

- **Selected Task Playbook:** validate the executor-issued [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection). Consume its step without rerouting. Never reread Task SOP with a complete handoff. Missing orchestrated handoffs return to router; standalone/resume reconstruct a missing handoff from `conditional_references` step only using `python3 <plugin>/scripts/task-step.py --task <kind-slug> --stage <stage>`. Read only its output, never the Task file or routing matrix.
- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route or dispatching any child, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Configuration](../../references/subagent-routing-contract.md#configuration), [Route Selection](../../references/subagent-routing-contract.md#route-selection), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

One executor-issued unblocked ticket with complete dependencies, acceptance
criteria, approved or autonomously selected design, testing seams, safe
workspace, accounted initial changes, and green baseline evidence. The handoff
identifies one approved or autonomously selected unblocked vertical ticket from
the current planned wave and records Gate-3 approval, the approved or
autonomously selected durable planned wave, frontier, ticket, recorded wave
base, workspace, and build cache. Direct or resumed entry validates or
reconstructs this handoff; plan authorization never bypasses the executor.

## Output

Red-Green/structural evidence, affected checks, complete task-owned diff, exact
commands and results, findings, and blockers; return provisional evidence to
the native implement-spec executor.

## Process

Execute the required SOP with validated input and return evidence. Main may
delegate under routing authority; children must not spawn. Main owns acceptance,
fresh integration verification, staging, commit, durable plan advancement, and
completion.

## Stop Conditions

Stop and preserve evidence when:

- no approved or autonomously selected unblocked ticket exists in a valid executor-issued handoff, or that handoff cannot be validated or reconstructed;
- the selected workspace is unsafe or changes cannot be attributed/separated from user-owned work;
- a behavior change cannot demonstrate Red for the intended reason, or structural work lacks preservation/dependency evidence;
- implementation evidence invalidates the selected design;
- an affected verification command fails after diagnosis;
- the same blocking condition occurs three consecutive times.

Stop without staging, committing, changing a durable checkbox, or claiming
completion. Preserve and return evidence even when ticket-level checks are green.
