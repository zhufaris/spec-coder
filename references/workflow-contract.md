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

Write target-project artifacts only after a safe isolated worktree exists:

- specification: `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md`;
- durable ticket plan: `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`;
- domain terminology: root `GLOSSARY.md`, only when terms change;
- architecture decisions: `docs/adr/`, only for decisions that are hard to reverse, surprising without context, and based on a real trade-off.

The plan is the task-status source of truth. Mirror it in the runtime plan with at most one item in progress. Do not create a private workflow-state file.

## Default Routing

Use `spec-coder` by default for requests that create or change code. Do not automatically route read-only explanation, status, investigation, or review requests through it. Honor an explicit `skip spec-coder` or `directly modify` request while continuing to obey all other applicable instructions and skills.

## Git Safety

- Preserve the user's original checkout and its uncommitted work.
- Prefer a native worktree facility; reuse existing safe isolation.
- Use `feat/<slug>` for features and `fix/<slug>` for fixes.
- Establish a green baseline before writing target-project artifacts.
- Stage explicit ticket-owned paths; never use `git add -A`.
- Create one atomic Conventional Commit per completed ticket.
- Do not amend commits predating the active ticket.
- Do not push, open a pull request, or publish external tickets without separate authorization.

## Failure Transitions

- Diagnose behavior, lint, type, and build failures within the current ticket and return through `tdd-coder`.
- Return to `design-coder` when evidence invalidates an architectural assumption.
- Stop before implementation on a failing baseline.
- Stop after the same blocking condition occurs three consecutive times.
- Preserve the worktree, branch, failing command, output, and current ticket state whenever stopping.
- Never delete tests, weaken assertions, suppress failures, or force a commit to manufacture success.

## Recovery

Inspect the current branch and worktree, approved specification, plan checkboxes, Git log, and fresh verification output. Select the earliest incomplete phase supported by that evidence. Re-run the verification at the inferred boundary before continuing, and never trust an old success claim.

## Verification Layers

For behavior changes, use the Red-Green sequence below. For approved behavior-preserving refactors or dependency-only repairs, substitute the structural verification path in `tdd-coder` for steps 1-2: green baseline and preservation checks, plus dependency-check or before/after source-review evidence. Mixed work still needs Red-Green for changed behavior. Both paths require affected checks, review, and full verification.

1. Observe a focused test fail for the intended reason.
2. Make the focused test pass with the minimum implementation.
3. Run affected tests, lint, type checks, and builds before the ticket commit.
4. Review the complete diff against the specification, domain language, architecture, and tickets.
5. Run the full applicable repository suite freshly before claiming completion.
