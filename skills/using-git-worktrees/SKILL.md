---
name: using-git-worktrees
description: Prepare an optional isolated Git workspace after plan-coder has selected isolation. Use to reuse existing linked worktrees, prefer native Host worktree tools, or safely fall back to git worktree without owning dependency setup, baseline verification, or workspace policy.
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

An explicit isolation selection from `plan-coder`, the target Git repository,
the intended branch/feature slug, current Git state, user workspace preferences,
and the available native Host worktree tools. This capability is optional and
must not be invoked for an approved in-place path.

## Output

Return one of:

- an existing linked worktree path and branch or detached HEAD state;
- a newly created isolated path and branch through a native Host tool;
- a newly created path and branch through the Git fallback;
- a concrete blocker/failure for `plan-coder` to resolve under workspace policy.

Report the mechanism used and any cleanup handle. `plan-coder` owns dependency
preparation and baseline verification after this skill returns.

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
it to `plan-coder`. Reuse it only when the supplied state establishes that its
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

Return the native isolated path to `plan-coder`. Do not run dependency setup or
tests here.

### 3. Use Git fallback only without a native tool

Choose a project-local location in this order:

1. an explicit repository/user preference;
2. existing `.worktrees/`;
3. existing `worktrees/`;
4. `.worktrees/` at the repository root.

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
project-local location, present the exact diff and an ASCII mutation review
through `show-me`, then obtain explicit approval. Even after approval, create
nothing and do not apply or commit the diff inside this support skill. Return an
`approved mutation pending` result to `plan-coder`, including the approved
bytes and inspected base. Planning must either select a location that needs no
repository mutation or establish an explicitly owned, committed `.gitignore`
base before invoking this skill again. This prevents an uncommitted change from
being stranded in the original checkout or omitted from the new worktree.

If approval is declined, return the conflict to `plan-coder` for a safe
alternative. Do not create a commit or continue on the unignored path.

After validating the path and branch name, create the fallback:

```bash
git worktree add <absolute-path> -b <branch-name>
```

Never interpolate an unvalidated environment variable, glob, or command
substitution into the target path. Preserve every existing worktree and user
branch.

### 4. Return control to planning

Report the absolute path, branch/detached state, mechanism, and relevant cleanup
handle. Plan-coder owns dependency preparation and baseline verification. It
also owns the decision to continue, choose another safe workspace, or stop.

If native or Git creation fails because of a sandbox or permission denial,
report the exact failure. Do not silently switch to in-place execution; only
`plan-coder` can select that path under the approved constraints.

## Stop Conditions

Stop and preserve actual state when:

- the selected path overlaps an existing worktree or user-owned directory;
- an existing linked-worktree candidate has unresolved ownership, changes, or
  task overlap;
- isolation was required but neither native tooling nor a safe Git fallback is
  available;
- the project-local directory is unignored and its mutation is not approved;
- an approved `.gitignore` mutation is not yet part of an explicitly owned,
  committed base;
- branch creation would overwrite or conflict with existing state;
- a sandbox, permission, or Git error prevents creation;
- cleanup ownership or a native tool result is ambiguous.

Do not delete, relocate, prune, or forcibly unlock an existing worktree. Do not
install dependencies, run the project baseline, stage files, or create a commit.
