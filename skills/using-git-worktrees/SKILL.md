---
name: using-git-worktrees
description: Prepare an optional isolated Git workspace after workspace preflight selects isolation or for selected post-Gate-3 per-worker isolation. Use to reuse existing linked worktrees, prefer native Host worktree tools, or safely fall back to git worktree without owning dependency setup, baseline verification, or workspace policy.
---

# Using Git Worktrees

Apply the required owner sections and conditional human-review path below.

This skill adapts the official
[`obra/superpowers`](https://github.com/obra/superpowers) implementation. See
`THIRD_PARTY_NOTICES.md` for provenance and MIT terms.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Workspace Selection](../../references/workflow-contract.md#workspace-selection), [Git Safety](../../references/workflow-contract.md#git-safety), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Recovery](../../references/workflow-contract.md#recovery).
- [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), and [Result Integration](../../references/subagent-routing-contract.md#result-integration).

## Conditional Reading

- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Parallel worker allocation:** also load [Execution Waves](../../references/subagent-routing-contract.md#execution-waves) and [Result Integration](../../references/subagent-routing-contract.md#result-integration) before preparing per-worker workspaces.

## Input

An explicit isolation selection from workspace preflight, or a main-orchestrator
request from the native implement-spec executor for Gate-3-approved integration
or per-worker isolation from the recorded wave base; the
target Git repository; the intended branch/feature slug; current Git state;
user workspace preferences; and the available native Host worktree tools. This
capability is optional in general and must not be invoked merely because the
primary workspace is in place or because serial delegation is selected. A
selected parallel-wave isolation request for a selected parallel execution wave
is the explicit exception; worktrees
must never be claimed as mandatory for serial delegation.

Main selects that preparation under
[Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests)
before serial fallback for a user parallel request. An in-place main workspace
does not prevent isolated workers; read-only workers need no mutation isolation.

## Output

Return one of:

- an existing linked worktree path and branch or detached HEAD state;
- a newly created isolated path and branch through a native Host tool;
- a newly created path and branch through the Git fallback;
- a concrete blocker/failure for orchestration to resolve under workspace policy.

For every allocated worker, report the recorded wave base, absolute path,
branch or detached state, isolation mechanism, and recovery handle. The main
orchestrator owns allocation and cleanup authorization. Workspace preflight
owns dependency preparation and baseline verification for initial workspace
selection; this adapter never takes over either responsibility.

For executor work, prepare only the Gate-3-approved integration/isolation
selection. The authoritative workspace may be reused only when that approved
fact remains safe. If required isolation cannot be proven available and based
on the recorded wave base, return the evidence so main can reopen Gate 3; do
not invent a serial substitute for a required constraint.

## Process

### 1. Detect existing isolation

Run read-only detection first:

```bash
git rev-parse --git-dir
git rev-parse --git-common-dir
git rev-parse --show-superproject-working-tree
git branch --show-current
git rev-parse --show-toplevel
```

Resolve the Git directory and common directory to physical absolute paths. If
they differ and `git rev-parse --show-superproject-working-tree` returns empty,
the checkout is already a linked-worktree candidate. For initial workspace
selection, create nothing and return it to the requesting orchestrator.
Reuse it only when the supplied state establishes that its
changes, ownership, starting revision, and task overlap are safe; otherwise
report the concrete conflict.

For per-worker parallel allocation, a linked main workspace is not the completed
allocation. Retain safe existing candidates, then continue to the preparation
steps below for remaining workers. Each concurrent mutating worker needs a
distinct validated workspace; never assign the same candidate to two workers or
share the main workspace while main is mutating it. Return a candidate conflict
without blocking preparation of other permitted workspaces.

Report a named branch normally. Report detached HEAD explicitly as externally
managed isolation; do not create another worktree merely to attach it. If the
superproject command returns a path, this is a submodule, not proof of a linked
worktree; continue with the normal-repository path.

### 2. Select only a recorded-base- and path-compatible native Host tool

Inspect live definitions rather than guessing arguments. Native availability
and compatibility differ: `enter_worktree` must explicitly pin both the
approved recorded base and exact repository-local source path
`<repo>/.worktrees/<branch>`. Otherwise it is incompatible; use the safe
exact-base Git fallback. Retain its `exit_worktree` recovery handle; do not
create parallel Git state the Host cannot manage.

For a main-requested parallel wave, request one native isolated workspace per
worker from the same recorded wave base. Validate and return each worker's
actual path, branch/detached state, mechanism, and recovery handle separately.
If the Host cannot prove real per-worker isolation, return that concrete blocker
so main can apply the explicit parallel request policy; do not treat paths in
one shared checkout as isolated.

### 3. Use a safe exact-base Git fallback when native is unavailable or incompatible

Use this fallback only after the native route is unavailable or incompatible,
and only when location, branch, permissions, and the recorded base are safe and
approved. If native is incompatible and no safe Git fallback exists, return the
`blocked-no-compatible-isolation` blocker without attempting native allocation.

Obtain the only durable fallback facts through the bundled read-only policy
adapter, from any caller cwd:

```bash
python3 <repo>/scripts/workspace-policy.py inspect --repo <repo> --branch <branch-name>
```

Proceed only when its compact JSON has `status: accepted`; use its
`source_worktree`, `build_cache`, and exact ignore observations. Do not
reimplement branch, physical-repository, path, or ignore rules in this prompt.
The adapter never creates or cleans a worktree. Its canonical facts are:

- source worktree: `<repo>/.worktrees/<branch>`;
- build cache: `<repo>/.cache/<branch>/target`.

Preserve valid slash-separated segments; reject empty/absolute branches, empty
segments, traversal (`.` or `..`), backslashes, whitespace/control, home
expansion, or paths escaping the physical repository. No new sibling or `/tmp`
source/cache fallback; `/tmp` is only disposable small files, not resume or
recovery state.

Before creating any new durable worktree, require `ignored` for both exact
roots in the policy's `ignore` object. A `not-ignored` observation returns
`blocked-local-policy-unignored`; `uncertain` returns
`blocked-ignore-verification`. Do not propose an ignore mutation.

The adapter, not this stage, owns the underlying compatibility probes:

```bash
git -C <repo> check-ignore -q .worktrees/
git -C <repo> check-ignore -q .cache/
```

Inside the adapter, `0` means ignored and `1` means definitively not ignored;
other outcomes are uncertain. These commands and exit rules are documented for
compatibility evidence only. Do not invoke or reinterpret them in this skill;
consume the adapter's JSON facts.

For exit `1`, do not silently edit `.gitignore`; return the conflict to workspace
preflight or post-Gate-3 main. Do not mutate it before baseline, create a
commit, or continue on an unignored/uncertain path; do not create a commit or
escape derived paths through a sibling or `/tmp` mutation-free location.

After validating the path and branch name, create the fallback:

```bash
git worktree add <repo>/.worktrees/<branch> -b <branch-name> <wave-base>
```

Never interpolate an unvalidated environment variable, glob, or command
substitution into the target path. Preserve every existing worktree and user
branch.

For every native or Git allocation, serial or parallel, use the same adapter
before acceptance:

```bash
python3 <repo>/scripts/workspace-policy.py validate-allocation --repo <repo> --branch <branch-name> --workspace <allocated-path> --recorded-base <wave-base>
```

It validates physical repository identity, canonical path, and actual `HEAD`.
On its blocker result, return the allocated path, actual `HEAD` when supplied,
recorded base, and recovery handle; do not continue or clean up. Use
collision-free paths and preserve partial results.

### 4. Return control to the requesting orchestrator

Report the wave base, absolute path, branch/detached state, mechanism, and
recovery handle. The orchestrator owns dependency preparation and baseline
verification. It also owns the decision to continue, choose another safe
workspace, serialize a wave when the explicit parallel request policy permits,
wait for capacity, or stop.

Retain each recovery handle and isolated workspace until its result is
accepted or explicitly discarded. Child loss, cancellation, or a mid-run
opt-out does not authorize cleanup: return the attributable handle to main so
the result can be recovered, inspected, or later continued serially. Cleanup
requires main's explicit authorization after a fresh clean/ownership check. Do
not delete, unlock, relocate, or prune an unaccounted workspace or a workspace
containing user-owned changes. If ownership or disposition is ambiguous,
preserve it and report the blocker.

If native or Git creation fails because of a sandbox or permission denial,
report the exact failure. Do not silently switch to in-place execution; the
requesting orchestrator must choose the permitted fallback under the approved
constraints.

## Stop Conditions

Stop and preserve actual state when:

- the selected path overlaps an existing worktree or user-owned directory;
- an existing linked-worktree candidate has unresolved ownership, changes, or
  task overlap;
- isolation was required but no native tool can explicitly pin the recorded base
  and exact repository-local source path and no safe exact-base Git fallback is
  available;
- either repository-local generated root is unignored or its ignore status is
  uncertain;
- branch creation would overwrite or conflict with existing state;
- a sandbox, permission, or Git error prevents creation;
- cleanup ownership or a native tool result is ambiguous.

Must not delete worktrees without separate disposition authority. Do not delete,
relocate, prune, or forcibly unlock an existing worktree. Do not
install dependencies, run the project baseline, stage files, or create a commit.
