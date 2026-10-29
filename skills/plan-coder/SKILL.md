---
name: plan-coder
description: Prepare an approved or autonomously selected coding design for implementation by revalidating a prepared workspace and green baseline, writing a local specification, and creating dependency-aware implementation tickets. Use after Gate 1 approval or autonomous selection, or to resume planning from a selected design.
---

# Plan Coder

Apply the owners below. This stage synthesizes the specification and vertical
tickets, compiling every Gate-3 graph, including a singleton, for the native
implement-spec executor without scheduling. Use the bundled [specification
template](../../references/specification-template.md) and [ticket
template](../../references/ticket-template.md); invoke `using-git-worktrees`
only for selected isolation.

Preserve the required domain decisions during synthesis and decomposition.
Apply Approval Gates for interactive and autonomous Gate 2/3 transitions.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Design content and specification mapping](../../references/domain-design-contract.md#design-content-and-specification-mapping), [Ticket decomposition](../../references/domain-design-contract.md#ticket-decomposition).
- [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests).
- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).
- [Planning reuse interface](../../references/verification-contract.md#planning-reuse-interface).
- [Command interface](../../references/artifact-format.md#command-interface), [Findings and compatibility](../../references/artifact-format.md#findings-and-compatibility).
- [Active Markdown and markers](../../references/artifact-format.md#active-markdown-and-markers), [Specification grammar](../../references/artifact-format.md#specification-grammar), [Plan grammar](../../references/artifact-format.md#plan-grammar).

## Conditional Reading

- **Selected Task Playbook:** validate the approved [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection), then dereference only its one actual `conditional_references` link.
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

1. Validate workspace path, mode/rationale, branch, base, initial changes,
   dependency preparation and baseline output; re-inspect Git, ownership and
   concurrency. Missing, stale or unsafe evidence returns to preparation.
   `using-git-worktrees` remains isolation-only.
2. Revalidate dependency/environment readiness, current-request provenance, and
   that the prepared baseline is green before any target-project write. Keep
   main-observed capture JSON in conversation at this point; do not run `check`
   against a nonexistent artifact or weaken the green-baseline write boundary.
3. Stop with exact commands/output and return to workspace preparation/prepared
   evidence when ownership is unsafe or the baseline is not green.
4. Write the specification by synthesizing the approved or autonomously
   selected design into `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` with the local template.
   Preserve the selection's `kind`, `entry_evidence`, `design_obligations`,
   `red_or_pin`, `delivery_proof` and selected `conditional_references`, plus
   outcomes, architecture decisions and testing seams;
   do not conduct a new interview or invent decisions. Record workspace mode,
   rationale, branch, starting revision and relevant initial changes locally.
   Include every exact main-observed baseline capture record in the specification.
5. Apply Planning reuse interface against the written specification: run its
   compact non-executing `verification-evidence.py check` for every required
   record, confirm current provenance and dependency/environment observations,
   and require `reusable` plus the matching `record_id`. Standalone, resume,
   malformed or uncertain evidence, and `rerun` load Verification fallback and
   establish fresh verification. Stop and return to workspace preparation when
   any required baseline is not green.
6. Run bundled `scripts/check-artifacts.py --phase spec --spec <absolute-spec>`
   before Gate 2. Resolve findings or follow its unsupported-format/manual-review
   path; structural success does not approve decisions. Reconcile selected
   scenarios, context/model responsibilities, invariants, interaction decisions,
   dependency rules and testing seams against specification locations. Return
   missing decisions to `design-coder`, never invent entities, services or
   recovery policy. Interactively present the specification with `show-me` and
   stop at Gate 2; autonomously record the unique grounded recommendation.
7. After specification approval or autonomous selection, create vertical tickets
   with the local template as observable, context-window-sized increments. Each
   ticket carries the applicable selection reference, `red_or_pin`, and
   `delivery_proof`. Include
   blocking edges, acceptance, selected-context/model/rule/interface/interaction
   references and verification. Record dependencies, delegation eligibility/mode
   or opt-out, ownership/exclusions, isolation/concurrency, verification seam,
   capacity, real-isolation requirement and `delegation_allowed = false`. Do not
   copy the model or split mechanically; selected interaction can span contexts.
   Store checkbox tickets in `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md` and
   durable planned waves under Execution Waves; order is not dependency.
8. Before Gate 3, compile the nonempty graph for the native implement-spec
   executor: ownership, seams, capacity, authoritative workspace, wave base, isolation,
   permitted preparation, durable waves and blockers. A singleton is the same
   graph; planning records inputs but never schedules workers.
9. Under Execution Waves and Explicit Parallel Requests, retain one active
   wave, real isolation for parallel mutation, and recovery from checkboxes plus
   committed Git state.
10. Run bundled `scripts/check-artifacts.py --phase plan --spec <absolute-spec>
   --plan <absolute-plan> --repo <absolute-workspace>` before Gate 3; resolve findings under the same format
   contract. Before Gate 3, reconcile decision coverage and ticket readiness under the
   domain contract's Ticket decomposition section. Check delegation eligibility,
   mutation ownership, exclusions, dependencies, isolation, concurrency conflicts,
   verification seams and Host capacity. Review and approve the authoritative
   workspace, recorded wave base, isolation requirement, permitted
   integration/isolation preparation, task graph, durable-wave membership/order,
   and blocking edges with the tickets. Validate the durable partition under
   Execution Waves. Resolve load-bearing omissions through design/specification;
   independent selected slices need not wait for an unrelated open decision.
   Present the full ticket set and wave membership/order. In interactive mode,
   invoke `show-me` and wait for explicit implementation authorization; in
   autonomous mode record the unique grounded recommendation without waiting.

Creating an external issue, publishing to an issue tracker, pushing a branch, or opening a pull request always requires separate explicit authorization.

At the existing Gate 2/3 checks, reconcile the selected decisions covered by the contract's [language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [protected-behavior](../../references/domain-design-contract.md#protect-behavior-and-valid-values), and [persistence](../../references/domain-design-contract.md#aggregate-persistence-semantics) sections against their specification locations and ticket references/acceptance. Do not create a second model inventory; resolve missing decisions through the existing return paths.

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
