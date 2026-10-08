# Spec Coder Workflow Contract

This file is normative for every skill in the plugin. A stage may add stricter safeguards but must not weaken these rules.

## Phase Order

Run `grill-coder`, `design-coder`, `plan-coder`, `tdd-coder`, and `delivery-coder` in that order. `spec-coder` routes a new request to the first stage and a resumed request to the earliest incomplete stage.

For a new request, complete workspace preflight before entering that fixed stage
order. Select a safe in-place or isolated workspace, account for initial user
changes, prepare dependencies, and establish a fresh green baseline. Keep the
resulting prepared workspace evidence in conversation until the specification
records it. Preflight is orchestration, not a public stage or approval gate.

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

Every suite-owned human review follows the
[approval review contract](./approval-review-contract.md): the owning skill
invokes bundled `show-me` before asking and supplies 2-4 grounded, materially
distinct labeled options with their consequences. Authorization reviews use
approve and continue, request changes, and reject and stop. Genuine choices
use their real alternatives; neither fake choices nor options that widen the
shown authority are allowed. The owning skill asks and interprets the answer;
`show-me` only validates and renders the review and never approves anything.

This requirement covers design alternative selection, Gate 1, Gate 2, Gate 3,
a reopened gate, and a named mutation authorization. Design alternative
selection remains the existing pre-Gate approach choice and is distinct from
Gate 1; it does not add a fourth gate. Ordinary status, clarification,
read-only reporting or inspection, and already authorized work are not human
review interactions and do not generate review options.

In the interactive path, stop for explicit user approval after:

1. the selected design;
2. the written specification;
3. the vertical ticket set and authorization to implement it.

Approval applies only to the artifact presented at that gate. A scope or architecture change reopens the relevant gate. After the third gate, in-scope TDD, verification, and atomic commits proceed without another confirmation.

Before asking at Gate 1, Gate 2, or Gate 3, the owning stage must follow the
[approval review contract](./approval-review-contract.md) and invoke bundled
`show-me`. Supply the artifact or exact proposed mutation, key decisions,
risks/blockers, approval effect, next stage, and review options. Present the
authoritative artifact or diff and the ASCII review map before the explicit
approval question; the map does not grant approval.

A reopened gate uses the same review contract and must show the prior approval,
changed fact, affected decision, and returned gate. Any other suite-owned
mutation authorization follows the same rule. Ordinary clarification, status,
read-only checks, and work already authorized by Gate 3 are not additional
approval requests.

## Artifact Contract

Write coding-workflow target-project artifacts only after workspace preflight
selects a safe workspace, accounts for initial changes, and establishes a fresh
green baseline. The workspace can be the current checkout or a linked worktree:

- specification: `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md`;
- durable ticket plan: `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`;
- domain terminology: root `GLOSSARY.md`, only when terms change;
- architecture decisions: `docs/adr/`, only for decisions that are hard to reverse, surprising without context, and based on a real trade-off.

The plan checkboxes are the task-status source of truth. Before Gate 3, the
plan must persist explicit durable planned-wave sections in order. Every ticket exactly once
is required, each planned wave contains at most four tickets,
dependencies point only to earlier waves, no intra-wave conflict exists, and a
main-local ticket is a singleton wave. Interactive Gate 3 approves both the
ticket set and the planned wave membership/order; autonomous Gate 3 records
their unique grounded recommendation. Scheduling order is not a functional dependency.

Runtime has at most **one active execution wave**, not one active ticket. It
forms a live dispatch batch only from the current earliest incomplete planned
wave: live capacity may shrink the batch; isolation and capacity fallback follow
[Explicit Parallel Requests](./subagent-routing-contract.md#explicit-parallel-requests),
but runtime must not regroup membership or pull a ticket from a later planned
wave. Keep execution modes and Host/recovery handles in conversation only. Do
not create a private workflow-state file. On resume, use durable wave
membership with unchecked tickets and committed Git state; do not invent a new
wave from stale conversational handles.

## Default Routing

Use `spec-coder` by default for requests that create or change code. Do not automatically route read-only explanation, status, investigation, or review requests through it. Honor an explicit `skip spec-coder` or `directly modify` request while continuing to obey all other applicable instructions and skills.

## Worker Progress Heartbeat

Every suite-owned direct-child brief consumes the shared **Worker Progress
Heartbeat** / `ProgressSnapshot` policy in the
[subagent routing contract](./subagent-routing-contract.md). When proactive
child-to-main messaging is available, require the child to report a valid
snapshot at start, every 45-60 seconds while active, on each phase change,
before and after a long command, and immediately on blocker, failure, or
completion. A short attempt reports start and terminal state without inventing
a periodic update. The brief preserves the literal `delegation_allowed = false`
and the child must not stage or commit; a reviewer also remains read-only.

Main records proactive heartbeat capability **before or at dispatch**. A
capability-unavailable record is non-blocking and preserves delegation; it is
not valid to record capability only after dispatch.

`heartbeat-capability-unavailable` records that proactive messaging is absent
but preserves the existing delegation decision and final-return behavior.
`heartbeat-overdue` means a Host wait timed out or a reporting interval was
missed; `awaiting-heartbeat` is an ordinary observation without either
condition. Neither outcome creates a failure or blocker and
neither grants interruption, takeover, promotion, local fallback, or other
authority. Snapshots are conversational evidence only: main-only completion
authority, diff acceptance, and fresh verification remain unchanged.

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
  isolation. Apply the explicit parallel request policy before serial fallback;
  do not make worktrees mandatory merely because delegation is used.
- Both modes require the same baseline, approvals, ownership checks, TDD and atomic commits. Do not delete or relocate an existing worktree merely because isolation is optional.

The prepared workspace evidence includes the absolute workspace, mode and
rationale, branch, starting revision, relevant initial changes, dependency
preparation, and fresh baseline commands/output. `plan-coder` consumes this
evidence and revalidates ownership, interference, and baseline freshness before
writing the specification. Missing, stale, or invalid evidence returns to
workspace preflight; planning does not silently choose a second workspace.

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
