---
name: plan-coder
description: Prepare an approved coding design for implementation by revalidating a prepared workspace and green baseline, writing a local specification, and creating dependency-aware implementation tickets. Use after design-coder approval or to resume planning from an approved design.
---

# Plan Coder

Follow the shared [workflow contract](../../references/workflow-contract.md), including its workspace selection rules. This skill owns specification synthesis and vertical-ticket decomposition. Use the plugin's [specification template](../../references/specification-template.md) and [ticket template](../../references/ticket-template.md); no external planning skill is required. Use `using-git-worktrees` only if isolation is selected.

Read and apply the [domain design contract](../../references/domain-design-contract.md) during both synthesis and decomposition. Preserve its decisions in the local templates, scaling detail to the task.

Read the [worked examples](../../references/domain-design-examples.md) when translating context/model responsibilities, consistency requirements or interactions into verifiable slices.

Read the [approval review contract](../../references/approval-review-contract.md).
Before asking at Gate 2 or Gate 3, invoke bundled `show-me` with the artifact,
decisions, material risks/blockers, approval effect, and immediate next stage.
The ASCII map supplements the complete specification or ticket set and the
explicit approval question.

## Input

A Gate 1-approved design, a prepared workspace with its preflight evidence, the
target repository and project instructions, and any existing `spec-coder`
artifacts.

## Output

A freshly revalidated prepared workspace and recorded rationale (in place or
isolated), accounted-for initial changes, fresh green baseline evidence, a
reviewed local specification, an approved dependency-aware ticket plan, and
explicit authorization to begin implementation.

## Process

1. Validate the prepared workspace evidence from orchestration: absolute path,
   mode and rationale, branch, starting revision, relevant initial changes,
   dependency preparation, and baseline commands/output. Re-inspect Git state,
   worktrees, ownership, user preference, and concurrent work. If evidence is
   missing, stale, unsafe, or no longer matches scope, return to workspace
   preflight rather than silently selecting another workspace. The bundled
   `using-git-worktrees` remains the isolation mechanic when preflight is
   re-entered; safe in-place work does not invoke it.
2. Revalidate dependency readiness and run the applicable baseline tests, lint,
   type checks, and build freshly enough to support specification writing.
3. Stop with the exact commands and output and return to workspace preflight
   when ownership is unsafe or the baseline is not green.
4. Synthesize the approved design to write the specification at `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` using the local specification template. Preserve approved outcomes, model/architecture decisions and testing seams; do not conduct a new interview or invent missing decisions. Record workspace mode, reason, branch, starting revision and relevant initial changes in the artifact. Keep it local.
5. Before Gate 2, reconcile approved scenarios, affected context maps and model responsibilities, invariants, consistency/interaction decisions, dependency rules, and testing seams against their specification locations. Resolve omissions; return new design decisions to `design-coder` rather than inventing entities, services or recovery policies. Present the written specification, invoke `show-me`, and stop at Gate 2 until the user approves it.
6. After specification approval, create vertical tickets using the local ticket template: each increment delivers a complete observable capability through the necessary modules and fits one agent context window. Include real blocking edges, acceptance criteria and references to the approved contexts/model elements, rules, interfaces, consistency/interaction constraints and verification. For every ticket, also record dependencies, delegation eligibility, delegation mode and any opt-out, mutation ownership and exclusions, isolation need, concurrency conflicts, an independently inspectable verification seam, Host capacity assumptions, whether real isolation is required, and the mandatory direct-child boundary `delegation_allowed = false`. Do not copy the whole model or split mechanically by layers. A ticket can span business contexts under an approved interaction contract. Store tickets as checkboxes in one plan at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`.
7. Mirror the durable ticket plan into the runtime plan with at most **one active execution wave**, not one active ticket. The Markdown checkboxes remain authoritative. Keep wave members, execution modes, workspace/recovery handles, and live Host capacity conversational; create no private state file. On resume, re-evaluate unchecked tickets from committed Git state instead of restoring a stale transient wave.
8. Before Gate 3, check that all in-scope scenarios/invariants have responsible tickets, every ticket traces to approved decisions, blockers are real prerequisites, and each increment is independently verifiable. Check the recorded delegation eligibility and mode, applicable opt-out, mutation ownership and exclusions, dependencies, isolation need, concurrency conflicts, verification seam, live Host capacity requirement, real isolation for parallel mutation, and `delegation_allowed = false` boundary. A main-local ticket must be a one-ticket wave and cannot overlap delegated mutation. Parallel delegated candidates must be dependency-ready and ownership-safe, fit live Host capacity and the suite wave cap, and have real per-worker isolation. If real isolation is unavailable, plan serialized direct workers rather than parallel shared-workspace mutation or an automatic local fallback. Name unresolved load-bearing decisions and affected tickets; resolve them through design/specification rather than assuming them or marking affected tickets ready. Independent approved slices need not be blocked by an unrelated open decision. Present the ticket set and proposed wave/dependency shape, invoke `show-me`, and stop at Gate 3 until the user approves it and authorizes implementation.

Creating an external issue, publishing to an issue tracker, pushing a branch, or opening a pull request always requires separate explicit authorization.

At the existing Gate 2/3 checks, reconcile the approved decisions covered by the contract's [language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [protected-behavior](../../references/domain-design-contract.md#protect-behavior-and-valid-values), and [persistence](../../references/domain-design-contract.md#aggregate-persistence-semantics) sections against their specification locations and ticket references/acceptance. Do not create a second model inventory; resolve missing decisions through the existing return paths.

## Stop Conditions

Stop when:

- the approved design is missing or internally inconsistent;
- prepared workspace evidence is missing, stale, or invalid and must return to
  workspace preflight;
- no safe workspace can be used under the user's constraints, overlapping
  changes cannot be separated safely, or fresh baseline verification fails;
- Gate 2 specification review is pending;
- Gate 3 ticket approval or implementation authorization is pending;
- a bundled planning template is missing or inconsistent with the approved design, or required isolation depends on unavailable/incompatible `using-git-worktrees` and no permitted safe alternative exists.

After Gate 3, hand the approved dependency and wave inputs back to the main
orchestrator. They describe safe formation of the next execution wave; they do
not prescribe or persist a production scheduler.
