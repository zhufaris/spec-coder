---
name: plan-coder
description: Prepare an approved coding design for implementation by choosing a safe in-place or isolated workspace, proving a green baseline, writing a local specification, and creating dependency-aware implementation tickets. Use after design-coder approval or to resume planning from an approved design.
---

# Plan Coder

Follow the shared [workflow contract](../../references/workflow-contract.md), including its workspace selection rules. This skill owns specification synthesis and vertical-ticket decomposition. Use the plugin's [specification template](../../references/specification-template.md) and [ticket template](../../references/ticket-template.md); no external planning skill is required. Use `using-git-worktrees` only if isolation is selected.

Read and apply the [domain design contract](../../references/domain-design-contract.md) during both synthesis and decomposition. Preserve its decisions in the local templates, scaling detail to the task.

Read the [worked examples](../../references/domain-design-examples.md) when translating context/model responsibilities, consistency requirements or interactions into verifiable slices.

## Input

A Gate 1-approved design, the target repository, its project instructions, and any existing `spec-coder` artifacts.

## Output

A selected safe workspace and recorded rationale (in place or isolated), accounted-for initial changes, fresh green baseline evidence, a reviewed local specification, an approved dependency-aware ticket plan, and explicit authorization to begin implementation.

## Process

1. Inspect Git state, staged/unstaged/untracked changes, current branch, worktrees, user preference and concurrent work. Apply the workflow contract's workspace selection: reuse safe isolation, work in place when ownership/interference permit it, or choose isolation where needed. Explain the choice without an extra approval prompt; invoke compatible `using-git-worktrees` and prefer native tools only on the isolation path. Record initial changes and protect unrelated work; unavailable optional tooling alone is not a blocker for safe in-place work.
2. Prepare dependencies using repository conventions, then run the applicable baseline tests, lint, type checks, and build.
3. Stop with the exact commands and output when the baseline is not green.
4. Synthesize the approved design to write the specification at `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` using the local specification template. Preserve approved outcomes, model/architecture decisions and testing seams; do not conduct a new interview or invent missing decisions. Record workspace mode, reason, branch, starting revision and relevant initial changes in the artifact. Keep it local.
5. Before Gate 2, reconcile approved scenarios, affected context maps and model responsibilities, invariants, consistency/interaction decisions, dependency rules, and testing seams against their specification locations. Resolve omissions; return new design decisions to `design-coder` rather than inventing entities, services or recovery policies. Present the written specification and stop at Gate 2 until the user approves it.
6. After specification approval, create vertical tickets using the local ticket template: each increment delivers a complete observable capability through the necessary modules and fits one agent context window. Include real blocking edges, acceptance criteria and references to the approved contexts/model elements, rules, interfaces, consistency/interaction constraints and verification. Do not copy the whole model or split mechanically by layers. A ticket can span business contexts under an approved interaction contract. Store tickets as checkboxes in one plan at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`.
7. Mirror the durable ticket plan into the runtime plan with at most one item in progress. The Markdown plan remains authoritative.
8. Before Gate 3, check that all in-scope scenarios/invariants have responsible tickets, every ticket traces to approved decisions, blockers are real prerequisites, and each increment is independently verifiable. Name unresolved load-bearing decisions and affected tickets; resolve them through design/specification rather than assuming them or marking affected tickets ready. Independent approved slices need not be blocked by an unrelated open decision. Present the ticket set and stop at Gate 3 until the user approves it and authorizes implementation.

Creating an external issue, publishing to an issue tracker, pushing a branch, or opening a pull request always requires separate explicit authorization.

At the existing Gate 2/3 checks, preserve applicable business actions, rejected/bypass outcomes, value validity/equality, policy ownership and terminology migration constraints. Carry them into specification sections and ticket references/acceptance, not a second model inventory. For affected persistence, also preserve aggregate/repository and restoration semantics, round-trip and post-load behavior checks, and unresolved legacy-data decisions. Resolve missing decisions through the existing return paths.

## Stop Conditions

Stop when:

- the approved design is missing or internally inconsistent;
- no safe workspace can be used under the user's constraints, or overlapping changes cannot be separated safely;
- dependency setup or baseline verification fails;
- Gate 2 specification review is pending;
- Gate 3 ticket approval or implementation authorization is pending;
- a bundled planning template is missing or inconsistent with the approved design, or required isolation depends on unavailable/incompatible `using-git-worktrees` and no permitted safe alternative exists.

After Gate 3, hand the first unblocked ticket to `tdd-coder`.
