---
name: plan-coder
description: Prepare an approved or autonomously selected coding design for implementation by revalidating a prepared workspace and green baseline, writing a local specification, and creating dependency-aware implementation tickets. Use after Gate 1 approval or autonomous selection, or to resume planning from a selected design.
---

# Plan Coder

Compatibility entry. Validate input/authority; execute the required stage SOP.

Use the [specification template](../../references/specification-template.md) and [ticket template](../../references/ticket-template.md).

## Required Reading

Every entry, including standalone invocation and resume, requires these owners; reuse only current sections.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Design content and specification mapping](../../references/domain-design-contract.md#design-content-and-specification-mapping), [Ticket decomposition](../../references/domain-design-contract.md#ticket-decomposition).
- [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests).
- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).
- [Planning reuse interface](../../references/verification-contract.md#planning-reuse-interface).
- [Command interface](../../references/artifact-format.md#command-interface), [Findings and compatibility](../../references/artifact-format.md#findings-and-compatibility).
- [Active Markdown and markers](../../references/artifact-format.md#active-markdown-and-markers), [Specification grammar](../../references/artifact-format.md#specification-grammar), [Plan grammar](../../references/artifact-format.md#plan-grammar).

- [Stage procedure](../../playbooks/stages/planning.md#procedure).

## Conditional Reading

- **Selected Task Playbook:** validate the approved [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection). Consume its step without rerouting. Missing orchestrated handoffs return to router; standalone/resume reconstruct a missing handoff from `conditional_references` step only.
- **Verification fallback:** for standalone entry, resume, malformed or uncertain observations/records, or a `rerun` result, load [CLI and explicit observations](../../references/verification-contract.md#cli-and-explicit-observations), [Capture and record schema](../../references/verification-contract.md#capture-and-record-schema), [Comparison and exit behavior](../../references/verification-contract.md#comparison-and-exit-behavior), and [Worked invocation](../../references/verification-contract.md#worked-invocation), then establish the required verification freshly.
- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

A Gate 1-approved or autonomously selected design with its singular
`TaskPlaybookSelection`, a prepared workspace with
its preflight evidence, the target repository and project instructions, and any
existing `spec-coder` artifacts.

## Output

A freshly revalidated prepared workspace and recorded rationale (in place or
isolated), accounted-for initial changes, current green baseline evidence, a
reviewed local specification, and an approved or autonomously selected
dependency-aware task graph. Before Gate 3, that graph records the authoritative
workspace, recorded wave base, isolation requirement, permitted
integration/isolation preparation, durable waves, ticket ownership and seams so
the native implement-spec executor has complete approved inputs to begin
implementation.

## Process

Execute the required SOP with validated input. Main may delegate under routing authority; children must not spawn.

## Stop Conditions

Stop when:

- the selected design is missing or internally inconsistent;
- prepared workspace evidence is missing, stale, or invalid and must return to
  workspace preflight;
- no safe workspace can be used under the user's constraints, overlapping
  changes cannot be separated safely, or fresh baseline verification fails;
- interactive Gate 2 specification review is pending;
- interactive Gate 3 ticket approval or implementation authorization is pending;
- a bundled planning template is missing or inconsistent with the selected design, or required isolation depends on unavailable/incompatible `using-git-worktrees` and no permitted safe alternative exists.

After Gate 3, hand the approved or autonomously selected nonempty task graph and
durable planned waves to the native implement-spec executor. They describe safe
formation of the current execution wave; plan-coder does not schedule workers or
prescribe a production scheduler.
