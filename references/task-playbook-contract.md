# Task Playbook Contract

## Purpose and unchanged workflow

This is the canonical owner of task selection and handoff. Task playbooks own
complete SOPs; stage playbooks own reusable procedures; Principles guide
judgment, and Skills expose concrete capabilities or compatibility entries. It does not change
the fixed `grill-coder -> design-coder -> plan-coder -> tdd-coder ->
delivery-coder` stages, Gate 1, Gate 2, Gate 3, the one native implement-spec
executor, the two-layer execution tree, or the nine public skills.

The selected playbook is conversational guidance for the current request. It
does not create a scheduler, a loader manifest, generated source, a durable
state file, or an alternate executor.

## Shared task SOP scaffold

Every selected Task SOP supplies exactly five short numbered stage deltas in
the fixed `grill-coder -> design-coder -> plan-coder -> tdd-coder -> delivery-coder` sequence. Its route-specific entry/design evidence, phase
proof, skip reason, Red or pin, delivery proof, and conditional Principle
triggers refine that sequence; they do not replace a stage, Gate, verification
requirement, or the native implement-spec executor.

Record an explicit skip reason only for inapplicable route-specific work. A
skip never removes a fixed stage, Gate, required verification, or another
route's proof obligation. The task owns step order and route-specific proof;
stage playbooks own local actions. A failing task delta returns to its stage
owner; an invalid design returns to design. No task step grants external
effects or nested delegation.

### Completion scaffold

Complete the selected route only after its five stage deltas preserve the
fixed sequence and its route-specific delivery proof is recorded at the
delivery stage. This scaffold is common to every task; task files must not
repeat it.

## TaskPlaybookSelection

Every coding request has exactly one `TaskPlaybookSelection`: `kind` is its
single route; `entry_evidence` records choosing/rejected-route facts;
`design_obligations` names existing-seam questions; `red_or_pin` is the
pre-implementation failure, pin, or baseline; `delivery_proof` proves the
affected path; `conditional_references` is exactly one direct selected-anchor
link, dereferenced alone with sibling kinds excluded.

## Route precedence and one-selection rule

Selection is evidence-backed, deterministic, and singular. Inspect bounded
repository evidence before classifying. Apply the first supported route below;
when evidence is missing or contradictory, select `Generic` or stop for an
unresolved load-bearing human decision. Never merge playbooks.

1. **Workflow Eval** ([SOP](../playbooks/tasks/workflow-eval.md#workflow-eval-playbook)) — a standalone, requested behavioral comparison or
   evaluation is controlling.
2. **Skill Change** ([SOP](../playbooks/tasks/skill-change.md#skill-change-playbook)) — a change to skill instructions, frontmatter, or skill
   behavior is controlling when it is not merely an implementation detail of a
   product feature.
3. **Bug Fix** ([SOP](../playbooks/tasks/bug-fix.md#bug-fix-playbook)) — an observed defect and matching reproduction/control surface
   are controlling, even when the repair changes behavior.
4. **Performance** ([SOP](../playbooks/tasks/performance.md#performance-playbook)) — a repeatable measured latency, throughput, memory, or
   resource objective and a comparable baseline are controlling.
5. **Refactor** ([SOP](../playbooks/tasks/refactor.md#refactor-playbook)) — structure changes while current externally observable
   behavior is explicitly preserved.
6. **Feature** ([SOP](../playbooks/tasks/feature.md#feature-playbook)) — deliberate new user-visible behavior, data shape, or interface
   capability is controlling.
7. **Generic** ([SOP](../playbooks/tasks/generic.md#generic-playbook)) — safe coding work not supported by a more specific route.

An ambiguous request does not infer a Feature, Bug Fix, or Performance route
from keywords alone. The entry evidence records the observed fact, the chosen
route, and why a nearby route does not control it.

## Evidence and proof matrix

Task SOPs live in separate files; this is navigation only. Select one file and copy its procedure before execution.

### Feature playbook

Read [Feature SOP](../playbooks/tasks/feature.md#feature-playbook); do not load sibling tasks.

### Bug Fix playbook

Read [Bug Fix SOP](../playbooks/tasks/bug-fix.md#bug-fix-playbook); do not load sibling tasks.

### Refactor playbook

Read [Refactor SOP](../playbooks/tasks/refactor.md#refactor-playbook); do not load sibling tasks.

### Performance playbook

Read [Performance SOP](../playbooks/tasks/performance.md#performance-playbook); do not load sibling tasks.

### Skill Change playbook

Read [Skill Change SOP](../playbooks/tasks/skill-change.md#skill-change-playbook); do not load sibling tasks.

### Workflow Eval playbook

Read [Workflow Eval SOP](../playbooks/tasks/workflow-eval.md#workflow-eval-playbook); do not load sibling tasks.

### Generic playbook

Read [Generic SOP](../playbooks/tasks/generic.md#generic-playbook); do not load sibling tasks.

## Empirical facts and human decisions

An open fork that can be resolved by a bounded probe of behavior, output,
timing, layout, routing, or evaluation is agent-owned: run the probe and record
its evidence before asking for review. Product preference, scope boundary,
domain meaning, irreversible action, mutation authorization, and Gate approval
are human-owned. A probe cannot bypass Gate 1/2/3, authorize mutation, or turn
an unresolved product decision into an implementation default.

## Conversational TODO boundary

The selected task file's numbered procedure, phase steps and explicit skip reasons must appear
as conversational TODOs. They guide progress in this trace only and are not
durable authority. Specification decisions, durable wave membership, plan
checkboxes, committed Git, Gate approvals, and main-only acceptance retain
their existing owners. A conversational TODO cannot dispatch work, promote an
evaluation, approve a Gate, authorize a mutation, or recover scheduling state.

## Conditional loading intent

The router reads the selected task once and passes the current step, proof
obligations and applicable principle constraints to each stage. A standalone
stage reconstructs that handoff from approved artifacts and, only when missing,
runs `python3 <plugin>/scripts/task-step.py --task <kind-slug> --stage <stage>`
and reads only the returned step packet. A complete handoff forbids Task-file
reads. Never reroute or read the matrix/sibling tasks for stage execution.
The handoff carries the selected kind, current stage and step, proof obligations,
and observed principle triggers. Missing or conflicting orchestrated inputs
return to the router; standalone entry or resume may reconstruct the selected
step from approved artifacts. The handoff is conversational, not durable state.


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
