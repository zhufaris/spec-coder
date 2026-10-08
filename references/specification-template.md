# Local Specification Template

This is a spec-coder resource used directly by `plan-coder`. Synthesize confirmed design decisions; do not require an external skill, tracker configuration, or publication to create this document. Apply the [domain design contract](./domain-design-contract.md).

Write to `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` after safe workspace selection and a passing baseline. For resumed work, reconcile the existing approved or autonomously selected specification instead of replacing it. Preserve stable references. Scale content to the task; short paragraphs can cover small changes.

## Copyable v1 skeleton

Copy this fenced example as a starting document, replacing its illustrative
status-command decisions with the selected design. Keep the marker, level-two
headings and stable decision-ID syntax from [Specification grammar](./artifact-format.md#specification-grammar).
The example is executable input for `check-artifacts.py --phase spec`, not an
approved design or verification record. Add only decisions the task needs.

```markdown
# Status command

<!-- spec-coder:artifact-v1 spec -->

## Problem Statement

An operator needs a local command to report readiness.

## Solution

Provide a read-only status command that prints ready after its checks pass.

## User Stories

### SCN-1: An operator requests readiness

The command prints ready and exits successfully when checks pass.

## Implementation Decisions

### INV-1: Status leaves project files unchanged

Readiness observation must not mutate the project.

## Testing Decisions

References: SCN-1, INV-1

Invoke the command, assert its output and exit status, and compare project files.

## Out of Scope

Remote health probes and automatic repairs are excluded.

## Further Notes

Record actual workspace, approval and baseline observations here during planning.
```

Keep baseline JSON exactly as emitted by `verification-evidence.py capture` in
`spec-coder-verification` fences under Further Notes, following
[Capture and record schema](./verification-contract.md#capture-and-record-schema).
Do not fabricate a record or copy illustrative evidence. First preflight may
name this future artifact without creating it; retain JSON in conversation until
the baseline passes. Planning reuse requires the same uninterrupted request and
main's current observations, as defined by
[Authority and lifecycle](./verification-contract.md#authority-and-lifecycle).

## Document outline

Use these exact level-two headings in the generated specification. The level-three
headings below explain their content; the copyable skeleton shows actual output:

### Problem Statement

Describe the observed user problem and relevant evidence. Separate current behavior from the intended change.

### Solution

State the selected design and observable result. Include scope and relevant compatibility requirements.

### User Stories

Describe actors, triggers, successful outcomes and relevant rejection, concurrency, duplicate or recovery scenarios. Give interacting scenarios stable references; avoid a long invented inventory for a narrow task.

### Implementation Decisions

Preserve decisions already made in design. Use subsections where useful:

- **Domain Model:** affected bounded contexts, local language, authoritative state, applicable entities/value objects/aggregates/services, invariant ownership and consistency boundaries. Include relevant business actions, valid value construction/equality/immutability and justified policies. Label observed, proposed and unresolved elements accurately; distinguish a DDD Specification predicate from this document.
- **Architecture:** module responsibilities, interfaces and their preconditions/results/errors, source dependency direction, data conversion and dependency assembly.
- **Behavior & Failure Modes:** state transitions, atomicity/conflict outcomes, idempotency, interaction guarantees and recovery owners as applicable.
- **Compatibility & Migration:** approved compatibility constraints and necessary transition steps, including changed domain terms, public names/values, affected consumers and translation when relevant.

Describe responsibilities and contracts rather than prescribing every class or method. Refer to evidence without turning a transient file layout into the design. Do not invent a domain service, port, event or recovery policy during synthesis.

When aggregate persistence is affected, preserve approved root/mutation boundaries, repository save/load/conflict semantics and controlled reconstitution in the decisions above. Distinguish intrinsic validity from current transition eligibility; identify missing historical data and required migration decisions.

### Testing Decisions

Map applicable scenarios/invariants to approved public testing seams and prior test patterns. Include relevant action/refusal and bypass outcomes, value construction/equality and policy behavior. For persistence changes, preserve approved round-trip and post-load behavior checks at existing adapter/integration seams, including state, value and applicable version semantics. State observable evidence for relevant interleavings, failure and recovery behavior. Record dependency/import/type/assembly evidence separately from outcome tests. For structural-only changes, identify preservation checks and structural evidence. Return a newly required testing seam to design rather than silently selecting it.

### Out of Scope

List meaningful exclusions and deferred work. Avoid implied obligations outside the selected design.

### Further Notes

Record workspace mode, rationale, branch, starting revision, relevant initial changes and observed baseline evidence (identify reused record IDs when eligible). Identify unresolved decisions, the owner if known, and which work they block. Keep artifact-specific approval status here if useful; do not create a private state file.

## Gate 2 review

Run the bundled checker with `--phase spec --spec <absolute-spec>` and resolve
structural findings under [Findings and compatibility](./artifact-format.md#findings-and-compatibility).
Then reconcile the selected design against the document: scenarios, context/model responsibilities, invariants, consistency/interaction decisions, interfaces, dependencies and verification. Correct omissions and dangling references. Return genuinely new or invalidated design decisions to design; ordinary wording corrections remain synthesis.

In the interactive path, present the written specification for approval before
writing its ticket set. For autonomous Gate 2, require one unique grounded
recommendation, record `auto-selected under explicit autonomous authority`, and
continue without human waiting or `show-me`. A missing or ambiguous
recommendation or unresolved load-bearing decision stops; no tracker
publication or manual-only upstream invocation is part of either path.
