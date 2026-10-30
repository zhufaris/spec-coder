---
name: grill-coder
description: Interrogate a coding request in conservative dependency-aware question rounds while lazily recording confirmed domain language and qualifying architecture decisions in repository docs. Use for the with-doc discovery phase of spec-coder or when a coding plan needs evidence-backed requirements stress-testing before design.
---

# Grill Coder

Compatibility entry. Validate input/authority; execute the required stage SOP.

## Required Reading

Every entry, including standalone invocation and resume, requires these owners; reuse only current sections.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).

- [Stage procedure](../../playbooks/stages/discovery.md#procedure).

## Conditional Reading

- **Selected Task Playbook:** validate the supplied [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection). Consume its step without rerouting. Missing orchestrated handoffs return to router; standalone/resume reconstruct a missing handoff from `conditional_references` step only. Apply [Empirical facts and human decisions](../../references/task-playbook-contract.md#empirical-facts-and-human-decisions).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

A coding request, its singular `TaskPlaybookSelection`, plus a selected workspace (safe path/mode/base, accounted
initial changes, and required capabilities) for read-only discovery, the
current repository, existing specifications, applicable `GLOSSARY.md` or
`GLOSSARY-MAP.md`, ADRs, and relevant implementation evidence.

## Output

A dependency-ordered set of confirmed decisions covering purpose, users,
scope, invariants, edge cases, operational constraints, failure behavior, and
measurable success. Return the selected or prepared workspace evidence, every changed
glossary/ADR path, and unresolved branches to `design-coder`. Keep ordinary
scope, interface, acceptance, and implementation decisions in conversation for
the later specification; persist only qualifying domain language or ADRs.

## Process

Execute the required SOP with validated input. Main may delegate under routing authority; children must not spawn.

## Stop Conditions

Stop and report the current decision state when:

- the user asks to stop;
- selected workspace evidence is absent, unsafe, or lacks a required
  capability;
- preparation required for a qualifying write is absent or stale and has been
  returned to `spec-coder` orchestration with a resume point, or preparation is
  failing or uncertain and has been returned without permitting a write;
- `grilling` or `domain-modeling` is absent, manual-only, or materially
  incompatible;
- glossary/ADR ownership overlaps user work or cannot be established safely;
- repository evidence contradicts a load-bearing assumption;
- a required product or business decision has no authorized owner;
- the next useful action is design rather than further questioning.

On normal completion, hand the confirmed decisions and changed document paths
to `design-coder` without starting design in the same response. Never fall back
to no-doc discovery merely to bypass a capability or ownership blocker.
