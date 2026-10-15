# Spec Coder Workflow Contract

This file is normative for every skill in the plugin. A stage may add stricter safeguards but must not weaken these rules.

## Stage Runtime Envelope

Every stage enters under the current phase and Gate authority, using the
authoritative workspace, its recorded base, and accounted initial changes.
Only the artifact contract authorizes workflow artifacts. Main-only authority
covers acceptance, staging, commits, and completion. Baseline, resume,
integrated acceptance, and delivery use fresh verification under the
verification lifecycle; separately authorized external effects remain
prohibited until authorized. On failure, preserve the evidence and return
through the applicable failure or recovery rule. The detailed sections below
elaborate these common invariants.

## Native implement-spec executor

Every Gate 3-approved or autonomously selected nonempty plan, including a
singleton, enters the native implement-spec executor. It hands each ticket to
a `tdd-coder` lifecycle and, after the accepted plan is complete, hands off to
`delivery-coder`. It does not own frontier, integration, or worktree mechanics.
The executor must not push, must not install, and must not delete worktrees.

## Phase Order

Run `grill-coder`, `design-coder`, `plan-coder`, `tdd-coder`, and `delivery-coder` in that order. `spec-coder` routes a new request to the first stage and a resumed request to the earliest incomplete stage. After every Gate 3 approval or autonomous selection, every plan enters the native implement-spec executor. The executor schedules the approved task graph as per-ticket `tdd-coder` lifecycles before handing the completed cumulative accepted range to `delivery-coder`; it is orchestration within the fixed five-stage order, not another public stage.

For a new request, select a safe in-place or isolated workspace before entering
that fixed stage order. Account for initial user changes and required
capabilities, then retain the selected workspace evidence in conversation.
`grill-coder` and `design-coder` may inspect that selected workspace read-only.
Prepare dependencies and establish a fresh green baseline before the first
qualifying `GLOSSARY.md` or ADR write, or after Gate 1 before planning if
discovery made no qualifying write. Keep the resulting prepared workspace
evidence in conversation until the specification records it. Failed or
uncertain preparation stops before target-project writes. Selection and
preparation are orchestration, not public stages or approval gates.

Each stage may also be invoked independently when its stated input already exists. It must validate that input instead of silently recreating an earlier phase.

## Domain and Architecture Continuity

Apply the [domain design contract](./domain-design-contract.md) from discovery through delivery. Discovery surfaces missing meanings/owners; design explains affected bounded contexts, applicable entities/value objects/aggregates/services, invariants, consistency and interfaces. Native `plan-coder` preserves those decisions and dependency evidence in the bundled [specification](./specification-template.md) and [ticket](./ticket-template.md) templates. Gate 2 checks preservation; Gate 3 checks ticket coverage and readiness. These checks use the existing gates. Ticket size is one agent context window, not necessarily one business bounded context. Use the [worked examples](./domain-design-examples.md) for model responsibilities, concurrency, integration and proportionality.

## Approval Gates

The workflow accepts a request-scoped `autonomous=true` parameter. The default is false.
Only an explicit choice in the current user request can enable it. Never infer
or persist autonomous authority from repository or global
configuration, `AGENTS.md`, conversation history, a prior session, or a
subagent. An explicit false choice or revocation returns subsequent decisions
to the interactive path.

Interactive mode retains the human reviews below. In autonomous mode, design
alternative selection and Gate 1, Gate 2, and Gate 3 do not request human
review or invoke `show-me`: each requires exactly one unique grounded
recommendation, which the owning stage records as
`auto-selected under explicit autonomous authority` rather than user-approved.
The same rule applies to an in-scope reopened gate. Missing or ambiguous
recommendations and unresolved
load-bearing domain or architecture decisions stop the workflow.

Autonomous mode does not widen scope or mutation authority. Scope expansion,
a named mutation, setup's exact-diff authorization, and any action requiring
separate authorization still request human review. This includes push,
installation, external publication, user or repository configuration changes,
credentials, destructive actions, and other independently protected effects.
The mode still produces the design, specification, tickets, durable planned
waves, self-check evidence, TDD, review, verification, and atomic commits.

Every suite-owned human review consumes the [approval review contract](./approval-review-contract.md#review-snapshot),
[rendering](./approval-review-contract.md#rendering), [authority and safety](./approval-review-contract.md#authority-and-safety),
and [owning-skill responsibilities](./approval-review-contract.md#owning-skill-responsibilities).
Invoke bundled `show-me` before asking; it presents the ASCII review map and
never owns approval. Design alternative selection precedes Gate 1 and adds no gate.

In the interactive path, stop for explicit user approval after:

1. the selected design;
2. the written specification;
3. the vertical ticket set and authorization to implement it.

Approval applies only to the artifact presented at that gate. A scope or architecture change reopens the relevant gate. After the third gate, in-scope TDD, verification, and atomic commits proceed without another confirmation.

A reopened gate follows the same approval contract and identifies the prior
approval, changed fact, affected decision and returned gate. Ordinary
clarification, status, read-only checks and already authorized work create no
additional approval request.

## Artifact Contract

Write coding-workflow target-project artifacts only after the workspace is
prepared: it was safely selected with initial changes accounted for, then had
its dependencies prepared and fresh green baseline established. A selected
workspace alone authorizes read-only discovery and design, not a target-project
write. The workspace can be the current checkout or a linked worktree:

- specification: `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md`;
- durable ticket plan: `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`;
- domain terminology: root `GLOSSARY.md`, only when terms change;
- architecture decisions: `docs/adr/`, only for decisions that are hard to reverse, surprising without context, and based on a real trade-off.

The plan checkboxes are the task-status source of truth. Before Gate 3,
persist durable planned-wave membership and order. Gate 3 approves the ticket
set and wave layout (or records their autonomous selection).
[Execution Waves](./subagent-routing-contract.md#execution-waves) owns the
partition and runtime rules, including every ticket exactly once and one active execution wave. Load it when creating, executing or recovering a plan. Keep
Host/recovery handles conversational; never create a private workflow-state file.

New specifications and plans use the versioned Markdown markers and grammar in
[Supported artifact format](./artifact-format.md#active-markdown-and-markers),
emitted by the bundled templates. Run the read-only artifact checker on actual
files before Gate 2 (`spec`), Gate 3 (`plan`) and final delivery (`delivery`).
Resolve findings and explicitly report unsupported historical documents under
[Findings and compatibility](./artifact-format.md#findings-and-compatibility);
manual review is not a checker pass. Structural success never grants approval
or establishes business correctness. Markdown remains the sole authority.

## Default Routing

Use `spec-coder` by default for requests that create or change code. Do not automatically route read-only explanation, status, investigation, or review requests through it. Honor an explicit `skip spec-coder` or `directly modify` request while continuing to obey all other applicable instructions and skills.

## Worker Progress Heartbeat

For every direct child, load [Worker Progress Heartbeat](./subagent-routing-contract.md#worker-progress-heartbeat)
and [Worker Brief Assembly](./subagent-routing-contract.md#worker-brief-assembly).
These own ProgressSnapshot reporting, heartbeat-overdue observations, and the
unchanged main-only completion authority.

## Repository Setup

`setup-coder` is a manually invoked, idempotent onboarding capability; it is not
part of the fixed coding phase order. Follow the [setup contract](./setup-contract.md)
for repository-local `AGENTS.md` management, capability assessment,
verification-command discovery, mutation approval, concurrency protection, and
`READY`/`WARNING`/`BLOCKED` reporting. Setup does not create coding artifacts or
a worktree and does not install, stage, commit, push, or persist private state.
Its exact-diff `AGENTS.md` update is an onboarding mutation and not a coding
artifact or implementation change, so it may occur without coding-workflow
workspace preflight or a green project baseline. Setup's own authority,
byte-preservation, approval, and concurrent-change checks are the safety
boundary; this exception does not authorize any other pre-baseline write.

## Workspace Selection

Worktree creation is optional. Inspect the user's preference, existing worktrees, task scope, concurrent work, branch state, and staged/unstaged/untracked changes before choosing where to work.

- Reuse an existing safe worktree. Otherwise, focused work with clear ownership and no interference can run **in place**. Prefer isolation for parallel work, disruptive experiments or branch changes, or unrelated changes that cannot be safely separated.
- Respect an explicit workspace preference. Choose and explain the mode as a routine planning decision without adding a create/skip approval gate. If the requested mode cannot be used safely, report the actual conflict rather than silently overriding it.
- Record the workspace, branch, starting revision, relevant initial changes, chosen mode and reason in the specification/plan once it exists. Keep the choice in conversation before that; create no private state file.
- During new-request workspace preflight, invoke the bundled `using-git-worktrees` only for the isolation path and prefer native tooling. Failure of optional isolation mechanics is not itself a blocker if orchestration can select safe in-place work consistently with user instructions. If isolation is necessary or explicitly required and unavailable, preserve state and report the blocker.
- Worktree isolation remains optional for serial delegation. When the main
  orchestrator requests a parallel mutation wave, however, each worker must
  receive real Host/task isolation or a separately validated Git worktree at
  the recorded wave base. File disjointness inside one shared checkout is not
  isolation. Apply [Explicit Parallel Requests](./subagent-routing-contract.md#explicit-parallel-requests) before serial fallback;
  do not make worktrees mandatory merely because delegation is used.
- Both modes require the same baseline, approvals, ownership checks, TDD and atomic commits. Do not delete or relocate an existing worktree merely because isolation is optional.

Selected workspace evidence includes the absolute workspace, mode and
rationale, branch, starting revision, relevant initial changes, and required
capability assessment. It authorizes only read-only discovery and design.
Prepared workspace evidence extends the selected evidence with dependency
preparation and fresh baseline commands/output. `plan-coder` consumes prepared
evidence and revalidates ownership, interference, and baseline freshness before
writing the specification. Missing, stale, failed, or uncertain prepared
evidence returns to workspace preparation; planning does not silently choose a
second workspace or write a target-project artifact.

## Git Safety

- Preserve unrelated changes in the user's original checkout. In-place execution permits only task-owned edits; record existing staged, unstaged and untracked work before editing.
- Do not clean, stash, reset, change branches over, stage or commit unrelated user work to make a workspace usable. For overlapping edits, establish that they can be safely separated; otherwise isolate or resolve the concrete conflict before editing.
- If creating a branch, use `feat/<slug>` for features and `fix/<slug>` for fixes. Branch creation is not a prerequisite for safe in-place execution; respect repository branch rules.
- Establish a green baseline before writing target-project artifacts; selection
  alone permits only read-only discovery and design.
- Stage explicit ticket-owned paths; never use `git add -A`.
- Inspect the complete proposed commit, not just the latest staging command. If unrelated entries are already staged, use a verified path-scoped commit that preserves them, or isolate the task. Path scoping alone cannot separate user and agent edits to the same file; never include such user hunks without authorization.
- Create one atomic Conventional Commit per completed ticket.
- Do not amend commits predating the active ticket.
- Do not push, open a pull request, or publish external tickets without separate authorization.

## Failure Transitions

- Diagnose behavior, lint, type, and build failures within the current ticket and return through `tdd-coder`.
- Return to `design-coder` when evidence invalidates an architectural assumption.
- Stop before target-project writes on failed or uncertain workspace
  preparation, preserving the selected workspace and preparation evidence.
- Stop after the same blocking condition occurs three consecutive times.
- Preserve the selected workspace, branch, initial user changes, failing command, output, and current ticket state whenever stopping.
- Never delete tests, weaken assertions, suppress failures, or force a commit to manufacture success.

## Recovery

Inspect the current workspace/mode and branch, recorded initial changes,
approved or autonomously selected specification, plan checkboxes, Git log, and fresh verification
output. Select the earliest incomplete phase supported by that evidence;
authorized in-place work does not need a worktree on resume. Reconstruct the
current planned wave from durable wave membership, unchecked tickets, and
committed Git rather than a private state file or stale conversational handles.
Re-run verification at the inferred boundary and never trust an old success
claim.

## Verification Layers

For behavior changes, use the Red-Green sequence below. For approved behavior-preserving refactors or dependency-only repairs, substitute the structural verification path in `tdd-coder` for steps 1-2: green baseline and preservation checks, plus dependency-check or before/after source-review evidence. Mixed work still needs Red-Green for changed behavior. Both paths require affected checks, review, and full verification.

1. Observe a focused test fail for the intended reason.
2. Make the focused test pass with the minimum implementation.
3. Run affected tests, lint, type checks, and builds before the ticket commit.
4. Review the complete diff against the specification, domain language, architecture, and tickets.
5. Run the full applicable repository suite freshly before claiming completion.

[Authority and lifecycle](./verification-contract.md#authority-and-lifecycle)
owns baseline capture/reuse: first workspace preparation executes, same-request planning may
reuse every required matching record, and resume, integrated-ticket checks and
delivery remain fresh. Capture JSON can stay in conversation until the green
baseline permits artifact writes. Neither tool authenticates main observation
or authorizes stage/commit/completion. Follow the CLI contracts for exact inputs,
uncertainty and exit handling.
