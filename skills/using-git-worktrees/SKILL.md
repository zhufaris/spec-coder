---
name: using-git-worktrees
description: Prepare an optional isolated Git workspace after workspace preflight selects isolation or for approved post-Gate-3 per-worker isolation. Use to reuse existing linked worktrees, prefer native Host worktree tools, or safely fall back to git worktree without owning dependency setup, baseline verification, or workspace policy.
---

# Using Git Worktrees

Follow the shared [workflow contract](../../references/workflow-contract.md) and
its optional workspace-selection policy. Before requesting any safety mutation,
follow the [approval review contract](../../references/approval-review-contract.md)
and invoke bundled `show-me`.

This skill adapts the official
[`obra/superpowers`](https://github.com/obra/superpowers) implementation. See
`THIRD_PARTY_NOTICES.md` for provenance and MIT terms.

## Input

An explicit isolation selection from workspace preflight, or a main-orchestrator
request for per-worker isolation in an approved parallel execution wave; the
target Git repository; the intended branch/feature slug; current Git state;
user workspace preferences; and the available native Host worktree tools. This
capability is optional in general and must not be invoked merely because the
primary workspace is in place or because serial delegation is selected. An
approved parallel-wave isolation request is the explicit exception; worktrees
must never be claimed as mandatory for serial delegation.

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
the checkout is already a linked-worktree candidate. Create nothing and return
it to the requesting orchestrator. Reuse it only when the supplied state establishes that its
changes, ownership, starting revision, and task overlap are safe; otherwise
report the concrete conflict.

Report a named branch normally. Report detached HEAD explicitly as externally
managed isolation; do not create another worktree merely to attach it. If the
superproject command returns a path, this is a submodule, not proof of a linked
worktree; continue with the normal-repository path.

### 2. Prefer native Host tools

Inspect the live tool definitions rather than guessing their arguments. If
`enter_worktree` is available, use it before any `git worktree add` fallback and
retain the corresponding `exit_worktree` cleanup handle/instructions. Native
tools own placement, branch creation, and harness lifecycle. Do not create
parallel Git worktree state the Host cannot manage.

Return the native isolated path to the requesting orchestrator. Do not run
dependency setup or tests here.

For a main-requested parallel wave, request one native isolated workspace per
worker from the same recorded wave base. Validate and return each worker's
actual path, branch/detached state, mechanism, and recovery handle separately.
If the Host cannot prove real per-worker isolation, return that fact so main can
serialize direct workers; do not treat paths in one shared checkout as isolated.

### 3. Use Git fallback only without a native tool

Choose a fallback location in this order:

1. an explicit repository/user preference;
2. existing `.worktrees/`;
3. existing `worktrees/`;
4. a new sibling location outside the repository, named from the repository and
   feature slug.

Before creating a project-local worktree, verify the selected directory is
ignored:

```bash
git check-ignore -q .worktrees
git check-ignore -q worktrees
```

Interpret the exit status exactly: `0` means ignored; `1` means definitively not
ignored; any other exit status or fatal diagnostic is a verification failure.
Report a verification failure without proposing an ignore mutation.

For exit `1`, do not edit `.gitignore` silently. If the user still requires the
project-local location, return the conflict to workspace preflight during
initial selection, or to the requesting main orchestrator for a post-Gate-3
wave. Do not request or apply a `.gitignore` mutation before the project
baseline. The orchestrator must select a mutation-free location, such as the
validated sibling fallback, or stop on the explicit location constraint. Do not
create a commit or continue on the unignored path. A sibling path must be
absent, have a validated physical parent, and not overlap the repository,
another worktree, or a user-owned directory.

After validating the path and branch name, create the fallback:

```bash
git worktree add <absolute-path> -b <branch-name> <wave-base>
```

Never interpolate an unvalidated environment variable, glob, or command
substitution into the target path. Preserve every existing worktree and user
branch.

For a main-requested parallel wave, repeat this validation independently for
each per-worker fallback and verify that every checkout starts at the recorded
wave base. Use collision-free branches and paths. Return partial allocation
results and their recovery handles if a later allocation fails; never erase a
successfully allocated workspace to hide a partial failure.

### 4. Return control to the requesting orchestrator

Report the wave base, absolute path, branch/detached state, mechanism, and
recovery handle. The orchestrator owns dependency preparation and baseline
verification. It also owns the decision to continue, choose another safe
workspace, serialize a wave, or stop.

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
- isolation was required but neither native tooling nor a safe Git fallback is
  available;
- the project-local directory is unignored and the requesting orchestrator has
  not selected a mutation-free location;
- branch creation would overwrite or conflict with existing state;
- a sandbox, permission, or Git error prevents creation;
- cleanup ownership or a native tool result is ambiguous.

Do not delete, relocate, prune, or forcibly unlock an existing worktree. Do not
install dependencies, run the project baseline, stage files, or create a commit.
