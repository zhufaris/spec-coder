# Spec Coder Skill Suite Design

**Status:** Approved

**Date:** 2026-10-01

## Purpose

Build a reusable TraeCode skill suite that turns an initial coding request into reviewed, tested, committed work. The suite must make recommendations by default, preserve explicit human approval gates, use lightweight domain-driven design and Clean Architecture checks, and leave durable artifacts that allow a later session to resume.

The suite extends current upstream skills instead of copying their full instructions. Matt Pocock skills provide requirements interrogation, domain modeling, specification synthesis, vertical ticket decomposition, TDD, and code review. Superpowers provides design exploration, isolated worktrees, and evidence-based completion verification.

## Goals

- Provide one default entry point named `spec-coder`.
- Make `spec-coder` the user-level default for requests that create or change code.
- Keep each phase independently invocable through a skill ending in `-coder`.
- Recommend a default answer for every material decision.
- Prevent implementation before the required design and execution approvals.
- Use lightweight DDD and Clean Architecture by default, escalating only when the domain warrants it.
- Create an isolated branch and worktree before writing project artifacts.
- Implement vertical tickets through test-first cycles and atomic commits.
- Require fresh full-suite evidence before declaring the workflow complete.
- Resume from durable project artifacts and Git rather than a private workflow state file.

## Non-goals

- Forking or embedding complete copies of upstream skills.
- Requiring tactical DDD patterns for every change.
- Automatically publishing GitHub issues, pushing branches, or opening pull requests.
- Maintaining a separate `.spec-coder/state.yaml` state machine.
- Modifying uncommitted files in the user's original workspace.
- Using subagents by default.

## Packaging

Create a version-controlled local plugin at:

```text
/data00/home/feiyu.zhu/work/spec-coder/
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   ├── spec-coder/
│   │   └── SKILL.md
│   ├── grill-coder/
│   │   └── SKILL.md
│   ├── design-coder/
│   │   └── SKILL.md
│   ├── plan-coder/
│   │   └── SKILL.md
│   ├── tdd-coder/
│   │   └── SKILL.md
│   └── delivery-coder/
│       └── SKILL.md
├── references/
    ├── workflow-contract.md
    └── upstream-compatibility.md
└── assets/
    └── global-agents-snippet.md
```

Each `SKILL.md` is a thin adapter. It defines that phase's trigger, inputs, outputs, gates, and failure behavior, then composes installed upstream skills by name. Shared cross-phase invariants live in `references/workflow-contract.md`. Verified upstream names and versions live in `references/upstream-compatibility.md`.

Only frontmatter fields supported by the local TraeCode validator may be used. In particular, the wrappers must not copy Matt Pocock's unsupported `disable-model-invocation` field.

## Global Default Routing

Installing and enabling a plugin makes its skills visible but does not force a skill to run. To make `spec-coder` the default coding workflow, installation also adds the canonical text from `assets/global-agents-snippet.md` to the user-level `~/.trae/AGENTS.md`.

The rule applies by default to requests that create or change code, including features, bug fixes, behavioral changes, and refactors. It does not apply automatically to read-only explanation, status, investigation, or review requests. A user may explicitly say `skip spec-coder` or `directly modify` to bypass this suite; normal higher-priority instructions and other applicable skills still apply.

The installer must update a clearly delimited managed section idempotently and preserve unrelated global instructions. Marketplace `INSTALLED_BY_DEFAULT` is not used because it controls distribution policy rather than runtime skill selection.

## Workflow

```text
spec-coder
  |
  +-- grill-coder
  |     Close consequential requirement decisions one at a time.
  |
  +-- design-coder
  |     Compare 2-3 approaches and shape the selected design with
  |     lightweight DDD, Clean Architecture, and agreed test seams.
  |
  +-- Gate 1: user confirms the design
  |
  +-- plan-coder
  |     Create isolated branch/worktree and verify the baseline.
  |     Persist the approved spec and ask the user to review it.
  |     Decompose it into vertical tickets and request execution approval.
  |
  +-- Gate 2: user confirms the written spec
  |
  +-- Gate 3: user confirms tickets and authorizes implementation
  |
  +-- tdd-coder, repeated for each unblocked ticket
  |     Red -> Green -> affected checks -> atomic commit.
  |
  +-- delivery-coder
        Review -> repair through TDD if needed -> full verification
        -> final commit when needed -> completion report.
```

The three explicit approval gates are:

1. Selection and confirmation of the proposed design.
2. Review of the written specification.
3. Review of the ticket breakdown and authorization to start implementation.

After Gate 3, ordinary in-scope implementation, verification, and atomic commits proceed automatically. A scope or architecture change reopens the relevant gate.

## Skill Contracts

### `spec-coder`

The orchestrator detects whether the request is new or resumable, identifies the earliest incomplete phase, and invokes the corresponding stage skill. It owns sequencing and gates but does not duplicate phase-specific methods.

For recovery, inspect the current branch and worktree, specification, plan checkboxes, Git log, and fresh test results. Do not introduce a private state file.

### `grill-coder`

Compose Matt Pocock's `grilling` behavior. Inspect the repository before asking questions. Ask exactly one consequential question at a time and include a recommended answer with a short reason. Close hidden requirements, boundary conditions, operational constraints, failure behavior, and success criteria.

During an orchestrated run before workspace isolation, retain confirmed decisions in conversation context without editing the user's original checkout. When invoked independently inside an already safe worktree, it may update an existing glossary or ADR for explicitly confirmed durable decisions.

### `design-coder`

Compose Superpowers `brainstorming`, Matt Pocock `domain-modeling` and `codebase-design`, and the installed `clean-architecture` skill.

Present two or three materially different approaches with pros, cons, and a recommendation. For the selected approach, define only the domain and architecture concepts needed by the change:

- canonical domain terms and meanings;
- business boundaries and invariants;
- use cases and externally visible behavior;
- module boundaries and public seams;
- dependency direction and required ports/adapters;
- data crossing boundaries;
- testing seams and acceptance criteria.

Do not require bounded contexts, aggregates, repositories, value objects, or domain events unless the domain complexity justifies them. Do not write implementation code. Return an approved design to `plan-coder`; do not write project files before isolation exists.

### `plan-coder`

Prepare execution in this fixed order:

1. Detect an existing isolated worktree and reuse it when safe.
2. Otherwise create a native isolated worktree and a `feat/<slug>` or `fix/<slug>` branch.
3. Install or prepare project dependencies using repository conventions.
4. Run the repository's baseline tests. Stop if the baseline is not green.
5. Compose Matt Pocock `to-spec` to write the approved design locally.
6. Ask the user to review the written specification.
7. Compose Matt Pocock `to-tickets` to produce dependency-aware vertical slices.
8. Ask the user to approve the ticket set and authorize implementation.

`plan-coder` adapts `to-spec` and `to-tickets` to local files by default. Publishing to an external issue tracker requires an explicit request.

### `tdd-coder`

Select exactly one ticket whose blockers are complete. Use the testing seams already approved in the spec and plan, then compose Matt Pocock `tdd`:

1. Write one behavior-focused failing test.
2. Run it and observe the expected failure.
3. Write the minimum implementation needed to pass.
4. Run the focused test and affected module checks.
5. Perform a lightweight self-review.
6. Stage only files owned by the ticket.
7. Mark the ticket complete and create one Conventional Commit.

Do not use `git add -A`, amend user commits, skip failing tests, or broaden the ticket silently.

### `delivery-coder`

Compose Matt Pocock `code-review` and Superpowers `verification-before-completion`. Review the completed change against the spec, approved domain terms, dependency rules, ticket acceptance criteria, and actual diff.

Behavior defects return to a TDD cycle. Structural improvements are allowed only under passing behavior tests and within the approved scope. After review, run the full repository test, lint, type-check, and build commands that apply. Commit review fixes atomically when needed. Never push or open a pull request without a separate explicit request.

## Project Artifacts

By default, each target project receives two primary files:

```text
docs/spec-coder/
├── specs/YYYY-MM-DD-<slug>.md
└── plans/YYYY-MM-DD-<slug>.md
```

The specification contains the problem, scope, user-visible solution, considered approaches, chosen architecture, relevant domain model, boundaries, interfaces, testing seams, acceptance criteria, and out-of-scope items.

The plan contains vertical tickets, blocking edges, acceptance criteria, checkboxes, affected areas, validation commands, and resulting commit identifiers. It is the durable task status source. TraeCode's runtime plan mirrors it and keeps at most one item in progress.

Create or update root `GLOSSARY.md` only when new or changed domain terms need durable definitions. Create an ADR under `docs/adr/` only when a decision is hard to reverse, surprising without context, and based on a real trade-off.

## Git and Commit Policy

- Do not alter uncommitted work in the user's original checkout.
- Prefer the platform's native worktree mechanism.
- Reuse an existing isolated worktree when safe.
- Use `feat/<slug>` for features and `fix/<slug>` for fixes.
- Stop before implementation when baseline verification fails.
- Create one atomic Conventional Commit per completed ticket.
- Stage explicit ticket-owned paths only.
- Do not amend commits that predate the active ticket.
- Do not push, create a PR, or publish issues without explicit authorization.

## Verification Strategy

Use layered verification:

1. **Red evidence:** the new focused test fails for the intended reason.
2. **Green evidence:** the focused test passes after the minimum implementation.
3. **Ticket gate:** affected tests, lint, type checks, and builds pass before the ticket commit.
4. **Review gate:** the implementation matches the spec, domain language, architecture boundaries, and accepted ticket scope.
5. **Final gate:** the full applicable repository suite passes freshly before completion is claimed.

Tests must observe behavior through approved public seams. Do not test private implementation details or use tautological expectations.

## Failure and Recovery

- Diagnose ordinary test, lint, type, and build failures within the current ticket and retry through TDD.
- Stop and return to design when a discovered fact invalidates an architectural assumption.
- Stop on a failing baseline and report the pre-existing evidence.
- Stop after the same blocking condition occurs three consecutive times.
- Preserve the worktree, branch, logs, failing command, and current ticket state when stopping.
- Never delete tests, weaken assertions, suppress failures, or force a commit to manufacture a green result.

On resume, derive state from Git plus the specification and plan. Re-run the verification relevant to the inferred boundary before continuing; do not trust stale success output.

## Upstream Responsibilities

The wrappers depend on capabilities, not copied prose:

| Capability | Preferred upstream |
|---|---|
| Sequential requirements interrogation | Matt Pocock `grilling` |
| Alternative exploration and approval gates | Superpowers `brainstorming` |
| Domain language and ADR discipline | Matt Pocock `domain-modeling` |
| Module interfaces and testing seams | Matt Pocock `codebase-design` |
| Specification synthesis | Matt Pocock `to-spec` |
| Vertical ticket decomposition | Matt Pocock `to-tickets` |
| Test-first implementation | Matt Pocock `tdd` |
| Code review | Matt Pocock `code-review` |
| Worktree isolation | Superpowers `using-git-worktrees` |
| Evidence before completion | Superpowers `verification-before-completion` |
| Dependency direction and boundary crossing | `clean-architecture` |

The compatibility reference must record that the design was validated against Superpowers `v6.4.1`, the 2026-10-01 snapshot of `mattpocock/skills` `main`, and the matching 2026-10-01 snapshot of `nathankim0/clean-architecture-skills` `main`. If an upstream skill disappears or materially changes its contract, `spec-coder` must stop with a compatibility error rather than silently approximating it.

## Acceptance Criteria

- The plugin exposes exactly six skills: `spec-coder`, `grill-coder`, `design-coder`, `plan-coder`, `tdd-coder`, and `delivery-coder`.
- The plugin is installed and enabled at user scope, and the global AGENTS rule selects `spec-coder` by default for code-changing requests.
- Read-only requests do not automatically enter `spec-coder`, and an explicit user opt-out is honored.
- Every skill name ends in `-coder`.
- Each skill has one explicit input, output, stop condition, and upstream dependency set.
- Every material question generated by `grill-coder` includes a default recommendation.
- `design-coder` compares two or three approaches and applies adaptive DDD/Clean Architecture checks.
- No project artifact is written to the user's original checkout before an isolated workspace exists.
- `plan-coder` creates or reuses isolation, proves a green baseline, writes the spec, and creates vertical tickets.
- `tdd-coder` records observed Red and Green evidence before an atomic ticket commit.
- `delivery-coder` cannot claim completion without fresh full-suite verification.
- The workflow never pushes, opens a PR, or publishes external tickets without explicit authorization.
- A new session can identify the next phase from project documents and Git without private workflow state.

## Skill-Suite Validation

Validate the implementation with:

1. `quick_validate.py` for all six skill directories.
2. Static checks that every named upstream skill exists and every local reference resolves.
3. A temporary fixture Git repository exercising:
   - a complete new-feature flow;
   - recovery from an existing approved spec;
   - recovery from partially completed tickets;
   - a failing baseline;
   - a dirty original checkout;
   - a failing ticket test;
   - a final full-suite failure.
4. Assertions that no scenario pushes, changes the original branch, commits after failed verification, or creates external issues.
5. An idempotency check that applying the managed global AGENTS section twice produces one unchanged section and preserves unrelated instructions.

Forward-testing with subagents is not part of the default implementation because the approved workflow is single-session. It may be proposed separately if future validation needs an independent behavioral evaluation.
