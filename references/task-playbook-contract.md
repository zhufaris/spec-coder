# Task Playbook Contract

## Purpose and unchanged workflow

This is the canonical owner of task-playbook selection and task-specific
evidence obligations. It changes evidence obligations only. It does not change
the fixed `grill-coder -> design-coder -> plan-coder -> tdd-coder ->
delivery-coder` stages, Gate 1, Gate 2, Gate 3, the one native implement-spec
executor, the two-layer execution tree, or the nine public skills.

The selected playbook is conversational guidance for the current request. It
does not create a scheduler, a loader manifest, generated source, a durable
state file, or an alternate executor.

## TaskPlaybookSelection

Every coding request has exactly one `TaskPlaybookSelection` with these fields:

| Field | Meaning |
| --- | --- |
| `kind` | One singular playbook kind from the route matrix. |
| `entry_evidence` | Observed request and repository facts that justify the route and rule out plausible alternatives. |
| `design_obligations` | Task-specific questions that must be resolved at the existing discovery/design seams. |
| `red_or_pin` | The required failing reproduction, behavior pin, or measured baseline before implementation. |
| `delivery_proof` | The proof delivery verifies on the actual affected path. |
| `conditional_references` | Exactly one direct link to the selected kind anchor below; stages dereference that value and never infer or load sibling kinds. |

## Route precedence and one-selection rule

Selection is evidence-backed, deterministic, and singular. Inspect bounded
repository evidence before classifying. Apply the first supported route below;
when evidence is missing or contradictory, select `Generic` or stop for an
unresolved load-bearing human decision. Never merge playbooks.

1. **Workflow Eval** — a standalone, requested behavioral comparison or
   evaluation is controlling.
2. **Skill Change** — a change to skill instructions, frontmatter, or skill
   behavior is controlling when it is not merely an implementation detail of a
   product feature.
3. **Bug Fix** — an observed defect and matching reproduction/control surface
   are controlling, even when the repair changes behavior.
4. **Performance** — a repeatable measured latency, throughput, memory, or
   resource objective and a comparable baseline are controlling.
5. **Refactor** — structure changes while current externally observable
   behavior is explicitly preserved.
6. **Feature** — deliberate new user-visible behavior, data shape, or interface
   capability is controlling.
7. **Generic** — safe coding work not supported by a more specific route.

An ambiguous request does not infer a Feature, Bug Fix, or Performance route
from keywords alone. The entry evidence records the observed fact, the chosen
route, and why a nearby route does not control it.

## Evidence and proof matrix

This index names the available kinds; each linked subsection is the sole source
of its evidence and proof obligations. A selection links exactly one subsection.

- [Feature](#feature-playbook)
- [Bug Fix](#bug-fix-playbook)
- [Refactor](#refactor-playbook)
- [Performance](#performance-playbook)
- [Skill Change](#skill-change-playbook)
- [Workflow Eval](#workflow-eval-playbook)
- [Generic](#generic-playbook)

### Feature playbook

- Entry and design: name the user-visible outcome, data shape, and interface seam.
- Red or pin: a failing outcome-level example or acceptance test.
- Delivery proof: the affected entry path satisfies the outcome and compatibility checks.

### Bug Fix playbook

- Entry and design: reproduce the symptom and identify root cause on the matching surface.
- Red or pin: a failing reproduction of the reported defect.
- Delivery proof: the reproduction is green and neighboring behavior remains covered.

### Refactor playbook

- Entry and design: state preserved behavior and the reader-load or structure objective.
- Red or pin: pin current behavior before structural work.
- Delivery proof: pins are equivalent and the structural simplification is inspectable.

### Performance playbook

- Entry and design: record a repeatable baseline, limiting mechanism, environment, and comparable measure.
- Red or pin: the before-measurement baseline.
- Delivery proof: comparable before and after measurements prove the target without regression.

### Skill Change playbook

- Entry and design: state Host boundary and public surface: visibility, callability, disable-model-invocation, frontmatter, triggers, and direct link; preserve deterministic-contract obligations.
- Red or pin: deterministic contract checks before behavior comparison.
- Delivery proof: deterministic checks are green and the required blinded evaluation is non-regressing.

### Workflow Eval playbook

- Entry and design: state Parent/Candidate scope, sanitized environment, anonymous rubric, and deterministic prerequisites.
- Red or pin: mandatory deterministic Green for the evaluated candidate.
- Delivery proof: blinded comparison is non-regressing; inconclusive evidence keeps Parent.

### Generic playbook

- Entry and design: state the narrow affected seam and ordinary existing obligations.
- Red or pin: the existing task-appropriate Red or pin.
- Delivery proof: existing delivery verification on the affected path.

## Empirical facts and human decisions

An open fork that can be resolved by a bounded probe of behavior, output,
timing, layout, routing, or evaluation is agent-owned: run the probe and record
its evidence before asking for review. Product preference, scope boundary,
domain meaning, irreversible action, mutation authorization, and Gate approval
are human-owned. A probe cannot bypass Gate 1/2/3, authorize mutation, or turn
an unresolved product decision into an implementation default.

## Conversational TODO boundary

The selected playbook's exact phase steps and explicit skip reasons may appear
as conversational TODOs. They guide progress in this trace only and are not
durable authority. Specification decisions, durable wave membership, plan
checkboxes, committed Git, Gate approvals, and main-only acceptance retain
their existing owners. A conversational TODO cannot dispatch work, promote an
evaluation, approve a Gate, authorize a mutation, or recover scheduling state.

## Conditional loading intent

Normal routing exposes the selected playbook anchor only; unselected playbooks
add no runtime context. Conditional references are loaded only on their
triggered path and remain within the existing normal aggregate context budget.
No task-specific prose may recreate a public routing skill or duplicate these
kind anchors in a stage owner.

## Blinded evaluation constraints

Only Skill Change and Workflow Eval may require a blinded Parent/Candidate
comparison, and only after all mandatory deterministic checks are green.
Parent and Candidate use equivalent sanitized isolated environments and organic
prompts. The judge receives anonymous outputs and a private rubric. Main reads
candidate outputs and available workspace-local transcript evidence and owns
the verdict. Any deterministic failure, authority/Gate/dependency/artifact or
context-budget regression rejects the Candidate regardless of judge preference;
inconclusive or conflicting evidence keeps Parent. This protocol does not add a
wrapper agent, a merger agent, or a third execution layer.

## Pstack provenance and nondependency

The route separation and task-specific proof concepts are adapted from Cursor
pstack at <https://github.com/cursor/plugins/tree/main/pstack>, commit
`1ba91fc25c0977741dd0e267849e6234b037ed0a`, under MIT; the notice is recorded
in `THIRD_PARTY_NOTICES.md`. Pstack is provenance, not a dependency:
spec-coder does not vendor or invoke pstack, `poteto-mode`, pstack agents,
Cursor controls, or pstack model identifiers. Existing Host compatibility and
model routing remain authoritative.
