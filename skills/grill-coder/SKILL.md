---
name: grill-coder
description: Interrogate a coding request in conservative dependency-aware question rounds while lazily recording confirmed domain language and qualifying architecture decisions in repository docs. Use for the with-doc discovery phase of spec-coder or when a coding plan needs evidence-backed requirements stress-testing before design.
---

# Grill Coder

Apply the required owner sections below.
Compose the installed, model-callable `grilling` skill for the interview method
and `domain-modeling` for glossary/ADR discipline. Both capabilities are
required. Do not call, wrap, rename, or emulate manual-only `grill-with-docs` or
`grill-me-with-doc`; their presence on disk is not invocation eligibility.

Use the [domain design contract](../../references/domain-design-contract.md) to identify terminology conflicts, missing rule/state owners, and relevant concurrency or failure scenarios. Read the [worked examples](../../references/domain-design-examples.md) when the business meanings or responsibilities are unclear; defer detailed model selection to design.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Phase Order](../../references/workflow-contract.md#phase-order), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Workspace Selection](../../references/workflow-contract.md#workspace-selection), [Git Safety](../../references/workflow-contract.md#git-safety), [Artifact Contract](../../references/workflow-contract.md#artifact-contract).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language).
- [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).

## Conditional Reading

- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

A coding request plus a prepared workspace, its fresh preflight evidence, the
current repository, existing specifications, applicable `GLOSSARY.md` or
`GLOSSARY-MAP.md`, ADRs, and relevant implementation evidence.

## Output

A dependency-ordered set of confirmed decisions covering purpose, users,
scope, invariants, edge cases, operational constraints, failure behavior, and
measurable success. Return the prepared workspace evidence, every changed
glossary/ADR path, and unresolved branches to `design-coder`. Keep ordinary
scope, interface, acceptance, and implementation decisions in conversation for
the later specification; persist only qualifying domain language or ADRs.

## Process

1. Validate the prepared workspace evidence: selected path/mode, branch,
   starting revision, accounted initial changes, dependency readiness, and
   fresh green baseline. Re-inspect relevant ownership before any document
   write. Missing or stale evidence returns to workspace preflight.
2. Inspect implementation evidence, the applicable glossary map/glossary and
   ADRs before asking what the repository already answers.
3. Build a private decision tree and work it in dependency-ready frontier
   rounds, preserving decision-tree order. Ask up to three mutually independent
   questions whose prerequisites are settled, then recompute the frontier after
   each response. Do not ask a question whose answer depends on another open
   question in the same round.
4. Keep a question serial when its answer controls scope, domain meaning or
   ownership, a core invariant, or an architecture trade-off that could reshape
   another question's meaning, options, recommendation, or necessity. Unknown
   or overlapping coupling is serial as well. A repository fact remains
   agent-owned: inspect it as a prerequisite only for its downstream question
   without blocking unrelated ready frontier items.
5. Give every question a stable `Qn` ID, applicable options, and its own clear
   recommendation with a one-sentence reason. The user may accept one
   recommendation with `Qn: default`; never interpret one bare `default` as an
   answer to a multi-question round. A recommendation is not a confirmed
   decision.
6. Absorb only explicit, unambiguous individual answers. Confirm answered IDs,
   leave omitted IDs unresolved, and ask ambiguity as one focused serial
   follow-up before recomputing the next frontier. Only an explicit,
   unambiguous user answer establishes a confirmed decision.
7. After each confirmed decision, classify its durable destination:
   - canonical domain terminology, context-specific meaning, or an invariant
     updates the applicable `GLOSSARY.md` through `domain-modeling`;
   - an architecture decision updates or creates an ADR only when it is
     hard to reverse, surprising without context, and the result of a real trade-off;
   - scope, interface, acceptance, and ephemeral implementation choices stay in
     conversation for design/specification and produce no document write.
8. Immediately before a qualifying write, prove that the target is task-owned
   or safely separable from initial/user changes. Create glossary or ADR files
   lazily. Preserve existing definitions and explain compatibility before a
   confirmed replacement. On overlapping or ambiguous ownership, make no write
   and stop with the decision, target, conflict, and resume point.
9. Challenge fuzzy or conflicting terms, distinguish affected contexts'
   meanings and state owners, and probe relevant transitions, concurrent
   requests, retries and partial failures. Defer detailed entities, services
   and architecture selection to `design-coder`.
10. Finish when every load-bearing decision is confirmed, explicitly deferred,
   or out of scope. Report settled decisions, changed documentation paths,
   unresolved branches, prepared workspace evidence, and the recommended next
   action.

During discovery, apply the contract's [language guidance](../../references/domain-design-contract.md#discover-and-evolve-domain-language). Return the evidence-backed ambiguities, context-specific meanings and compatibility decisions that constrain design; do not select a model merely from database names.

Protect unrelated work in the user's original checkout. A prepared workspace
may be in place or isolated. Never write before workspace selection and a green
baseline. Do not write implementation code, create a branch, commit, publish an
issue, or imply that later approval gates have passed. If no confirmed decision
qualifies for a glossary or ADR, perform no document write.

## Stop Conditions

Stop and report the current decision state when:

- the user asks to stop;
- prepared workspace evidence is absent, stale, failing, or unsafe;
- `grilling` or `domain-modeling` is absent, manual-only, or materially
  incompatible;
- glossary/ADR ownership overlaps user work or cannot be established safely;
- repository evidence contradicts a load-bearing assumption;
- a required product or business decision has no authorized owner;
- the next useful action is design rather than further questioning.

On normal completion, hand the confirmed decisions and changed document paths
to `design-coder` without starting design in the same response. Never fall back
to no-doc discovery merely to bypass a capability or ownership blocker.
