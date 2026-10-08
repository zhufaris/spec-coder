---
name: plan-coder
description: Prepare an approved or autonomously selected coding design for implementation by revalidating a prepared workspace and green baseline, writing a local specification, and creating dependency-aware implementation tickets. Use after Gate 1 approval or autonomous selection, or to resume planning from a selected design.
---

# Plan Coder

Apply the required owner sections below, including workspace selection. This skill owns specification synthesis and vertical-ticket decomposition. Use the plugin's [specification template](../../references/specification-template.md) and [ticket template](../../references/ticket-template.md); no external planning skill is required. Use `using-git-worktrees` only if isolation is selected.

Preserve the required domain decisions during synthesis and decomposition.
Apply Approval Gates for interactive and autonomous Gate 2/3 transitions.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Phase Order](../../references/workflow-contract.md#phase-order), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Workspace Selection](../../references/workflow-contract.md#workspace-selection), [Git Safety](../../references/workflow-contract.md#git-safety), [Artifact Contract](../../references/workflow-contract.md#artifact-contract).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Design content and specification mapping](../../references/domain-design-contract.md#design-content-and-specification-mapping), [Ticket decomposition](../../references/domain-design-contract.md#ticket-decomposition).
- [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests).

- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).
- [CLI and explicit observations](../../references/verification-contract.md#cli-and-explicit-observations), [Capture and record schema](../../references/verification-contract.md#capture-and-record-schema), [Comparison and exit behavior](../../references/verification-contract.md#comparison-and-exit-behavior), [Worked invocation](../../references/verification-contract.md#worked-invocation).
- [Command interface](../../references/artifact-format.md#command-interface), [Findings and compatibility](../../references/artifact-format.md#findings-and-compatibility).
- [Active Markdown and markers](../../references/artifact-format.md#active-markdown-and-markers), [Specification grammar](../../references/artifact-format.md#specification-grammar), [Plan grammar](../../references/artifact-format.md#plan-grammar).

## Conditional Reading

- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

A Gate 1-approved or autonomously selected design, a prepared workspace with
its preflight evidence, the target repository and project instructions, and any
existing `spec-coder` artifacts.

## Output

A freshly revalidated prepared workspace and recorded rationale (in place or
isolated), accounted-for initial changes, current green baseline evidence, a
reviewed local specification, an approved or autonomously selected
dependency-aware ticket plan, and authority to begin implementation.

## Process

1. Validate the prepared workspace evidence from orchestration: absolute path,
   mode and rationale, branch, starting revision, relevant initial changes,
   dependency preparation, and baseline commands/output. Re-inspect Git state,
   worktrees, ownership, user preference, and concurrent work. If evidence is
   missing, stale, unsafe, or no longer matches scope, return to workspace
   preflight rather than silently selecting another workspace. The bundled
   `using-git-worktrees` remains the isolation mechanic when preflight is
   re-entered; safe in-place work does not invoke it.
2. Revalidate dependency/environment readiness and current-request provenance.
   For the same uninterrupted request only, retain each observed capture record
   in the active artifact after the first green baseline, then run bundled
   `scripts/verification-evidence.py check` with its currently expected command
   and observations. Identify every reused `record_id`; every required baseline
   command must qualify. Missing, rejected or uncertain evidence reruns that
   command freshly with the reason recorded. Standalone entry without current
   evidence and every resume run fresh baselines. Use the verification contract
   for capture, exits and record replacement; never copy a prior request ID.
3. Stop with the exact commands and output and return to workspace preflight
   when ownership is unsafe or the baseline is not green.
4. Synthesize the approved or autonomously selected design to write the specification at `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` using the local specification template. Preserve selected outcomes, model/architecture decisions and testing seams; do not conduct a new interview or invent missing decisions. Record workspace mode, reason, branch, starting revision and relevant initial changes in the artifact. Keep it local.
5. Run bundled `scripts/check-artifacts.py --phase spec --spec <absolute-spec>`
   on the written specification before Gate 2. Resolve findings, or follow the
   explicit unsupported-format/manual-review path; never call unsupported input
   a pass. Structural success does not approve decisions. Before Gate 2, reconcile selected scenarios, affected context maps and model responsibilities, invariants, consistency/interaction decisions, dependency rules, and testing seams against their specification locations. Resolve omissions; return new design decisions to `design-coder` rather than inventing entities, services or recovery policies. In the interactive path, present the written specification, invoke `show-me`, and stop at Gate 2 until the user approves it. In the autonomous path, record the unique grounded recommendation and continue without waiting.
6. After specification approval or autonomous selection, create vertical tickets using the local ticket template: each increment delivers a complete observable capability through the necessary modules and fits one agent context window. Include real blocking edges, acceptance criteria and references to the selected contexts/model elements, rules, interfaces, consistency/interaction constraints and verification. For every ticket, also record dependencies, delegation eligibility, delegation mode and any opt-out, mutation ownership and exclusions, isolation need, concurrency conflicts, an independently inspectable verification seam, Host capacity assumptions, whether real isolation is required, and the mandatory direct-child boundary `delegation_allowed = false`. Do not copy the whole model or split mechanically by layers. A ticket can span business contexts under a selected interaction contract. Store tickets as checkboxes in one plan at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`, then write explicit durable planned-wave sections before Gate 3 under
   Execution Waves. Scheduling order is not a functional dependency.
7. Validate the plan using Execution Waves and Explicit Parallel Requests:
   retain one active execution wave, real isolation for parallel mutation,
   durable membership and recovery from checkboxes plus committed Git state.
8. Run bundled `scripts/check-artifacts.py --phase plan --spec <absolute-spec>
   --plan <absolute-plan>` before Gate 3; resolve findings under the same format
   contract. Before Gate 3, reconcile decision coverage and ticket readiness under the
   domain contract's Ticket decomposition section. Check delegation eligibility,
   mutation ownership, exclusions, dependencies, isolation, concurrency conflicts,
   verification seams and Host capacity. Validate the durable partition under
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

After Gate 3, hand the approved or autonomously selected durable planned waves back to the main
orchestrator. They describe safe formation of the current execution wave; they
do not prescribe a production scheduler.
