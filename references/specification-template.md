# Local Specification Template

This is a spec-coder resource used directly by `plan-coder`. Synthesize confirmed design decisions; do not require an external skill, tracker configuration, or publication to create this document. Apply the [domain design contract](./domain-design-contract.md).

Write to `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` after safe workspace selection and a passing baseline. For resumed work, reconcile the existing approved specification instead of replacing it. Preserve stable references. Scale content to the task; short paragraphs can cover small changes.

## Document outline

Use the following headings in the generated specification:

### Problem Statement

Describe the observed user problem and relevant evidence. Separate current behavior from the intended change.

### Solution

State the selected design and observable result. Include scope and relevant compatibility requirements.

### User Stories

Describe actors, triggers, successful outcomes and relevant rejection, concurrency, duplicate or recovery scenarios. Give interacting scenarios stable references; avoid a long invented inventory for a narrow task.

### Implementation Decisions

Preserve decisions already made in design. Use subsections where useful:

- **Domain Model:** affected bounded contexts, local language, authoritative state, applicable entities/value objects/aggregates/services, invariant ownership and consistency boundaries. Label observed, proposed and unresolved elements accurately.
- **Architecture:** module responsibilities, interfaces and their preconditions/results/errors, source dependency direction, data conversion and dependency assembly.
- **Behavior & Failure Modes:** state transitions, atomicity/conflict outcomes, idempotency, interaction guarantees and recovery owners as applicable.
- **Compatibility & Migration:** approved compatibility constraints and necessary transition steps.

Describe responsibilities and contracts rather than prescribing every class or method. Refer to evidence without turning a transient file layout into the design. Do not invent a domain service, port, event or recovery policy during synthesis.

### Testing Decisions

Map applicable scenarios/invariants to approved public testing seams and prior test patterns. State observable evidence for relevant interleavings, failure and recovery behavior. Record dependency/import/type/assembly evidence separately from outcome tests. For structural-only changes, identify preservation checks and structural evidence. Return a newly required testing seam to design rather than silently selecting it.

### Out of Scope

List meaningful exclusions and deferred work. Avoid implied obligations outside the selected design.

### Further Notes

Record workspace mode, rationale, branch, starting revision, relevant initial changes and fresh baseline evidence. Identify unresolved decisions, the owner if known, and which work they block. Keep artifact-specific approval status here if useful; do not create a private state file.

## Gate 2 review

Reconcile the approved design against the document: scenarios, context/model responsibilities, invariants, consistency/interaction decisions, interfaces, dependencies and verification. Correct omissions and dangling references. Return genuinely new or invalidated design decisions to design; ordinary wording corrections remain synthesis.

Present the written specification for approval before writing its ticket set. No tracker publication or manual-only upstream invocation is part of this step.
