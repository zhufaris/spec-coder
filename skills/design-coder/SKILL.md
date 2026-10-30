---
name: design-coder
description: Turn confirmed coding requirements into an approved or autonomously selected design by comparing alternatives and applying adaptive domain modeling, deep-module design, Clean Architecture, and explicit testing seams. Use after grill-coder or whenever a coding change needs architecture decisions before planning.
---

# Design Coder

Compatibility entry. Validate input/authority; execute the required stage SOP.

## Required Reading

Every entry, including standalone invocation and resume, requires these owners; reuse only current sections.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Design content and specification mapping](../../references/domain-design-contract.md#design-content-and-specification-mapping).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).

- [Stage procedure](../../playbooks/stages/design.md#procedure).

## Conditional Reading

- **Selected Task Playbook:** validate the supplied [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection). Consume its step without rerouting. Missing orchestrated handoffs return to router; standalone/resume reconstruct a missing handoff from `conditional_references` step only. Apply [Empirical facts and human decisions](../../references/task-playbook-contract.md#empirical-facts-and-human-decisions).
- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

Confirmed requirements and selected `TaskPlaybookSelection` from `grill-coder`, repository evidence, domain language, ADRs, and constraints to preserve.

## Output

An approved or autonomously selected design in conversation context. It
identifies the chosen approach, affected bounded contexts and relevant local
models, canonical domain language, enforcing owners, invariants,
consistency/interaction semantics, module responsibilities, public interfaces,
dependency direction, boundary data, testing seams, acceptance criteria, and
out-of-scope behavior.

## Process

Execute the required SOP with validated input. Main may delegate under routing authority; children must not spawn.

## Stop Conditions

Stop when:

- an architectural interactive user has not selected an approach, or the
  autonomous path lacks one unique grounded recommendation;
- a domain or architecture decision requires an unavailable owner;
- the proposed design contradicts repository evidence;
- the design changes the agreed scope;
- interactive Gate 1 has been reached and explicit approval is pending.

After approval or autonomous selection, hand off to `plan-coder`; do not create
a worktree or begin implementation from this stage.
