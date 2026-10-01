# Spec Coder Workflow Contract

This file is normative for every skill in the plugin. A stage may add stricter safeguards but must not weaken these rules.

## Phase Order

Run `grill-coder`, `design-coder`, `plan-coder`, `tdd-coder`, and `delivery-coder` in that order. `spec-coder` routes a new request to the first stage and a resumed request to the earliest incomplete stage.

Each stage may also be invoked independently when its stated input already exists. It must validate that input instead of silently recreating an earlier phase.

## Domain and Architecture Continuity

Apply the [domain design contract](./domain-design-contract.md) from discovery through delivery. Discovery surfaces missing meanings/owners; design explains affected bounded contexts, applicable entities/value objects/aggregates/services, invariants, consistency and interfaces. Preserve those decisions and dependency evidence in the existing `to-spec` and `to-tickets` templates. Gate 2 checks preservation; Gate 3 checks ticket coverage and readiness. These checks use the existing gates. Ticket size is one agent context window, not necessarily one business bounded context. Use the [worked examples](./domain-design-examples.md) for model responsibilities, concurrency, integration and proportionality.

## Approval Gates

Stop for explicit user approval after:

1. the selected design;
2. the written specification;
3. the vertical ticket set and authorization to implement it.

Approval applies only to the artifact presented at that gate. A scope or architecture change reopens the relevant gate. After the third gate, in-scope TDD, verification, and atomic commits proceed without another confirmation.

## Artifact Contract

Write target-project artifacts only after `plan-coder` selects a safe workspace and establishes a green baseline. The workspace can be the current checkout or a linked worktree:

- specification: `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md`;
- durable ticket plan: `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`;
- domain terminology: root `GLOSSARY.md`, only when terms change;
- architecture decisions: `docs/adr/`, only for decisions that are hard to reverse, surprising without context, and based on a real trade-off.

The plan is the task-status source of truth. Mirror it in the runtime plan with at most one item in progress. Do not create a private workflow-state file.

## Default Routing

Use `spec-coder` by default for requests that create or change code. Do not automatically route read-only explanation, status, investigation, or review requests through it. Honor an explicit `skip spec-coder` or `directly modify` request while continuing to obey all other applicable instructions and skills.

## Workspace Selection

Worktree creation is optional. Inspect the user's preference, existing worktrees, task scope, concurrent work, branch state, and staged/unstaged/untracked changes before choosing where to work.

- Reuse an existing safe worktree. Otherwise, focused work with clear ownership and no interference can run **in place**. Prefer isolation for parallel work, disruptive experiments or branch changes, or unrelated changes that cannot be safely separated.
- Respect an explicit workspace preference. Choose and explain the mode as a routine planning decision without adding a create/skip approval gate. If the requested mode cannot be used safely, report the actual conflict rather than silently overriding it.
- Record the workspace, branch, starting revision, relevant initial changes, chosen mode and reason in the existing specification/plan once the baseline passes. Keep the choice in conversation before that; create no private state file.
- Invoke `using-git-worktrees` only for the isolation path and prefer native tooling. Absence/failure of optional isolation tooling is not itself a blocker if safe in-place work is available and consistent with user instructions. If isolation is necessary or explicitly required and unavailable, preserve state and report the blocker.
- Both modes require the same baseline, approvals, ownership checks, TDD and atomic commits. Do not delete or relocate an existing worktree merely because isolation is optional.

## Git Safety

- Preserve unrelated changes in the user's original checkout. In-place execution permits only task-owned edits; record existing staged, unstaged and untracked work before editing.
- Do not clean, stash, reset, change branches over, stage or commit unrelated user work to make a workspace usable. For overlapping edits, establish that they can be safely separated; otherwise isolate or resolve the concrete conflict before editing.
- If creating a branch, use `feat/<slug>` for features and `fix/<slug>` for fixes. Branch creation is not a prerequisite for safe in-place execution; respect repository branch rules.
- Establish a green baseline before writing target-project artifacts.
- Stage explicit ticket-owned paths; never use `git add -A`.
- Inspect the complete proposed commit, not just the latest staging command. If unrelated entries are already staged, use a verified path-scoped commit that preserves them, or isolate the task. Path scoping alone cannot separate user and agent edits to the same file; never include such user hunks without authorization.
- Create one atomic Conventional Commit per completed ticket.
- Do not amend commits predating the active ticket.
- Do not push, open a pull request, or publish external tickets without separate authorization.

## Failure Transitions

- Diagnose behavior, lint, type, and build failures within the current ticket and return through `tdd-coder`.
- Return to `design-coder` when evidence invalidates an architectural assumption.
- Stop before implementation on a failing baseline.
- Stop after the same blocking condition occurs three consecutive times.
- Preserve the selected workspace, branch, initial user changes, failing command, output, and current ticket state whenever stopping.
- Never delete tests, weaken assertions, suppress failures, or force a commit to manufacture success.

## Recovery

Inspect the current workspace/mode and branch, recorded initial changes, approved specification, plan checkboxes, Git log, and fresh verification output. Select the earliest incomplete phase supported by that evidence; approved in-place work does not need a worktree on resume. Re-run verification at the inferred boundary and never trust an old success claim.

## Verification Layers

For behavior changes, use the Red-Green sequence below. For approved behavior-preserving refactors or dependency-only repairs, substitute the structural verification path in `tdd-coder` for steps 1-2: green baseline and preservation checks, plus dependency-check or before/after source-review evidence. Mixed work still needs Red-Green for changed behavior. Both paths require affected checks, review, and full verification.

1. Observe a focused test fail for the intended reason.
2. Make the focused test pass with the minimum implementation.
3. Run affected tests, lint, type checks, and builds before the ticket commit.
4. Review the complete diff against the specification, domain language, architecture, and tickets.
5. Run the full applicable repository suite freshly before claiming completion.
