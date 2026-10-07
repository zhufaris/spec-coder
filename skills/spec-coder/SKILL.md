---
name: spec-coder
description: Orchestrate code-changing requests through requirements grilling, design, workspace-aware planning, ticket-level TDD, review, and verified delivery. Use by default for feature, bug-fix, refactor, or other implementation requests; do not auto-trigger for read-only explanation, status, investigation, or review, and honor explicit requests to skip spec-coder or directly modify.
---

# Spec Coder

Follow the shared [workflow contract](../../references/workflow-contract.md) and verify the installed capabilities listed in [upstream compatibility](../../references/upstream-compatibility.md) before delegating stages. Route subagent work through the [subagent routing contract](../../references/subagent-routing-contract.md).

All initial and reopened approval gates use bundled `show-me` under the shared
approval review contract. The stage that owns the gate supplies grounded facts,
presents the complete artifact, asks the explicit question, and interprets the
answer; visualization never owns approval.

## Input

A new coding request, or a repository containing partial spec-coder artifacts from an interrupted workflow.

## Output

A prepared workspace, approved specification, approved vertical-ticket plan,
one atomic commit per completed ticket, review results, fresh verification
evidence, and a final delivery report produced through `delivery-coder`.

## Process

1. Inspect repository instructions, Git status, current branch, worktrees, relevant specifications and plans, plan checkboxes, and Git log before changing anything.
2. Verify required local and upstream skills are visible in the current Host catalog, permitted for model invocation and materially compatible for the selected path. A file on disk or an enabled plugin is insufficient; respect `disable-model-invocation: true` without attempting indirect invocation. Planning is native to `plan-coder` and needs its bundled templates, not external planning skills. Defer the bundled optional `using-git-worktrees` path until workspace selection; safe in-place work does not invoke it. Stop for other unavailable required capabilities with specific evidence rather than approximating them.
   Before spawning a subagent, classify the bounded task as economy, standard,
   strong, or main-only; apply trusted user mappings and any repository minimum;
   inspect the live Host catalog/tool interface; and inherit the main model when
   no safe compatible override exists. A configured route never transfers
   approval, attribution, commit, delivery, or completion authority. Only the
   active main agent may spawn. Every direct-child brief must include
   `delegation_allowed = false` and prohibit indirect delegation through skills,
   workflows, tools, or other agents. Apply a supported Host child-tool denial
   as defense in depth; otherwise rely on the contract without claiming sandbox
   enforcement. A child that needs delegation must return evidence and its
   blocker to main, which alone may create a layer-2 sibling. Every direct-child
   brief also requires the shared **Worker Progress Heartbeat** /
   `ProgressSnapshot` policy when proactive child-to-main messaging is
   available: report at start, every 45-60 seconds while active, on phase
   change, before and after a long command, and immediately on blocker,
   failure, or completion. `heartbeat-capability-unavailable` preserves the
   delegation decision; `heartbeat-overdue` or a Host wait timeout means no
   message only, never a failure, blocker, interrupt, takeover, promotion, or
   local fallback authority. A snapshot never changes main-only diff
   acceptance, fresh verification, or completion authority.
3. Classify the request:
   - For a new request, complete workspace preflight under the shared contract:
     account for initial changes, select safe in-place or isolated execution,
     prepare dependencies, and observe a fresh green baseline. Use bundled
     `using-git-worktrees` only if isolation is selected. Keep the prepared
     workspace evidence in conversation, then start `grill-coder`.
   - For resumed work, infer the earliest incomplete phase from durable artifacts and fresh verification at the inferred boundary. Never maintain a private workflow-state file.
4. Run the fixed stage order:
   1. `grill-coder` consumes the prepared workspace and exposes hidden requirements, boundaries, constraints, and acceptance signals.
   2. `design-coder` compares 2-3 approaches and stops for explicit approval of the selected design.
   3. `plan-coder` revalidates the prepared workspace, user-change ownership,
      and baseline freshness, writes the local specification, stops for
      specification approval, decomposes it into vertical tickets, then stops
      for ticket approval and implementation authorization.
   4. After Gate 3, form and run the dependency-aware execution wave described
      below. `tdd-coder` executes each wave member through Red-Green or the
      approved structural path, affected checks, a plan-checkbox update, and an
      atomic commit. Repeat with freshly computed waves until all tickets are
      complete.
   5. `delivery-coder` performs findings-first review, routes repairs back through TDD, runs the full applicable suite, and alone may produce the terminal completion claim.
5. Keep the durable plan checkboxes as task-state truth and mirror them in the
   runtime plan with one active execution wave at most. Wave membership, modes,
   and Host handles remain conversational; checkboxes and committed Git are the
   authoritative durable state.
6. Reopen the affected approval gate whenever scope or architecture changes.
   Show the prior approval, changed fact, affected decision, and return path
   through `show-me` before requesting renewed approval. Return to
   `design-coder` when implementation evidence invalidates an approved
   assumption.
7. Stop after the same blocking condition occurs three consecutive times, preserving the exact evidence and resume point.

The three human gates are design approval, written-specification approval, and ticket-set approval plus implementation authorization. After the third gate, proceed autonomously within the approved scope through TDD, review, verification, and commits.

## Approved Ticket Execution Waves

From the approved ticket inputs, the active main agent schedules one active
dependency-aware execution wave. Recompute dependency readiness, delegation
eligibility, mutation ownership, isolation, and live Host capacity before each
wave. Eligible work delegates by default, including when only one eligible
ticket exists. Preserve approved plan order and admit at most four direct
workers, never more than the Host's currently available direct-child slots.
Tickets with incomplete dependencies or conflicting ownership cannot share a
wave.

Parallel mutation requires real isolation for every worker at the recorded wave
base; disjoint paths in a shared checkout are not isolation. Without real
isolation, keep default delegation but use serialized direct workers. Every
child is a direct layer-2 worker whose brief includes
`delegation_allowed = false`, prohibits direct or indirect delegation, and says
that workers must not stage or commit. The active main agent retains gate and
scope decisions, behavior Red or structural preservation/dependency evidence,
diff acceptance, attribution, fresh verification, staging, atomic commits,
delivery aggregation, and completion authority.

Each worker brief requires the shared Worker Progress Heartbeat /
`ProgressSnapshot` reporting schedule: starting, 45-60 seconds while active,
phase change, pre/post long command, and blocker/failure/completion whenever
proactive messaging is available. The same requirement applies to a
main-created promotion sibling. A capability-unavailable observation preserves
delegation and an overdue heartbeat or wait timeout records no message only;
neither authorizes failure classification, interruption, takeover, promotion,
or local execution.

Apply execution outcomes distinctly. An applicable opt-out means local
execution and no spawning in that scope. A mid-run opt-out requires main to
stop new dispatch and promotion prospectively. Account for already-dispatched
results under the normal inspection and acceptance rules, and report accepted
commits rather than automatically reverting them. Spawn unavailable selects a
recorded local fallback when safe, but is a blocker when delegation was
explicitly required. If spawn exists but temporary capacity is zero, wait
through the Host mechanism and recompute rather than falling back locally.
Noneligible work runs locally when safe, or is a blocker when delegation was
explicitly required.
An `inherit-main` route, missing optional mapping, or optional-model fallback
still uses delegation; model routing does not convert eligible work to local
execution.

For a parallel wave, every child starts from the recorded wave base and returns
its base identity, complete task-owned diff, and verification evidence. Main
integrates one result at a time into the authoritative workspace. Advancement
past the recorded base is acceptable only when every intervening change is an
accepted sibling result with proven disjoint ownership. A base mismatch,
transfer conflict, ownership overlap, unexplained diff, or failed fresh
verification rejects that parallel result and leaves its ticket unchecked for
later serialized execution from the authoritative base. Dependents do not
unblock until the accepted ticket has passed fresh verification, updated its
durable checkbox, and received its atomic commit.

## Stop Conditions

Stop and report the recoverable state when:

- a capability required for the selected path is missing or incompatible;
- no safe workspace can be selected under the user's constraints;
- workspace preflight or baseline verification fails before discovery;
- an approval gate is pending or reopened;
- changes cannot be safely attributed or separated from user-owned work in the selected workspace;
- the same blocker occurs three consecutive times;
- `delivery-coder` cannot obtain fresh verification evidence from all required checks.

Never push, create a pull request, publish external tickets, stage unrelated changes, or claim completion outside `delivery-coder` without separate explicit authorization.
