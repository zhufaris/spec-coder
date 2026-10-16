---
name: using-git-worktrees
description: Prepare an optional isolated Git workspace after workspace preflight selects isolation or for selected post-Gate-3 per-worker isolation. Reuse safe linked worktrees, prefer compatible native tooling, then use an exact-base Git fallback.
---

# Using Git Worktrees

This optional isolation adapter preserves the `obra/superpowers` provenance in
`THIRD_PARTY_NOTICES.md`. It adapts selection; workspace policy owns path,
ignore, and allocation facts.

## Required Reading

On every entry, including standalone invocation and resume, load [Stage Runtime
Envelope](../../references/workflow-contract.md#stage-runtime-envelope),
[Workspace Selection](../../references/workflow-contract.md#workspace-selection),
[Git Safety](../../references/workflow-contract.md#git-safety), [Failure
Transitions](../../references/workflow-contract.md#failure-transitions),
[Recovery](../../references/workflow-contract.md#recovery), [Explicit Parallel
Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests),
[Execution Waves](../../references/subagent-routing-contract.md#execution-waves),
and [Result Integration](../../references/subagent-routing-contract.md#result-integration).

## Conditional Reading

Before a suite-owned human review, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot),
[Rendering](../../references/approval-review-contract.md#rendering), [Authority
and safety](../../references/approval-review-contract.md#authority-and-safety),
and [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities),
then invoke `show-me`.

## Input

An explicit preflight isolation selection, or a main request for Gate-3-approved
integration/per-worker isolation at the recorded wave base; repository, branch,
current state, user location constraints, and live native-worktree definitions.
Do not invoke for an in-place workspace or merely because serial delegation is
selected. A selected parallel execution wave requires real isolation. Treat it
as a selected parallel-wave isolation request: every worker needs distinct real
isolation; read-only workers do not.

## Output

Return a safe existing linked-worktree candidate, a native or Git allocation,
or a concrete blocker. Each accepted allocation reports its absolute path,
branch/detached state, mechanism, recorded wave base, and recovery handle.
The authoritative workspace remains main-owned. Main/orchestrator owns allocation
and cleanup authority; workspace preflight owns dependency preparation and
baseline verification.
If a required isolated allocation cannot be proven at the base,
return evidence for the main to reopen Gate 3 under its policy; do not invent
a serial substitute.

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

Resolve Git/common directories physically. Differing directories with an empty
superproject value indicate a linked-worktree candidate; retain it only when
ownership, changes, starting revision, and overlap are safe. A named branch is
normal; report detached HEAD as externally managed isolation. A superproject
path indicates a submodule, not a linked worktree. For parallel allocation,
never assign the main workspace or one candidate to two mutating workers.

### 2. Inspect workspace policy

Before choosing native or Git allocation, ask the policy adapter for allocation
facts from any caller cwd:

```bash
python3 <repo>/scripts/workspace-policy.py inspect --repo <repo> --branch <branch-name>
```

Proceed only on `status: accepted`; consume its physical repository,
`source_worktree`, `build_cache`, branch/path validity, and ignore facts. On any
other status, preserve the observed policy result and return the conflict to
workspace preflight without reclassifying it.
Do not restate, invoke, or reinterpret the policy's raw Git probe/exit
algorithm; do not propose an `.gitignore` mutation, a
sibling or mutation-free location, or `/tmp`. `/tmp` is only disposable small
files, never durable source, cache, workflow artifacts, verification evidence,
or recovery state.

### 3. Prefer a compatible native allocation

Inspect live definitions rather than guessing. `enter_worktree` is compatible
only when it pins both the recorded base and policy-returned `source_worktree`;
otherwise it is incompatible. Retain the `exit_worktree` recovery handle. For a
parallel wave, validate and report each worker independently; paths in one
shared checkout are not isolation.

### 4. Fall back to exact-base Git

Only when native allocation is unavailable or incompatible and the approved
branch/location/permissions permit it, use the accepted policy facts:

```bash
git worktree add <source-worktree> -b <branch-name> <wave-base>
```

Never interpolate an unvalidated variable, glob, or substitution. Preserve
existing worktrees and user branches. Before accepting every native or Git allocation,
use the same policy adapter:

```bash
python3 <repo>/scripts/workspace-policy.py validate-allocation --repo <repo> --branch <branch-name> --workspace <allocated-path> --recorded-base <wave-base>
```

It validates physical identity, canonical path, and actual `HEAD`; on a
blocker, return the allocated path, actual state when supplied, recorded base,
and recovery handle without cleanup. If no safe exact-base fallback exists,
return `blocked-no-compatible-isolation`.

### 5. Return recovery control

Return the facts to the requester, which decides continuation, safe
serialization, capacity wait, or stop under the routing contract. Retain an
isolated workspace and recovery handle until its result is accepted or explicitly discarded.
Loss, cancellation, or opt-out never authorizes cleanup.
Cleanup requires main's explicit authority after a fresh clean/ownership check:
do not delete, relocate, prune, unlock, or overwrite unaccounted or user-owned
state. Report sandbox, permission, or Git failures exactly; do not silently
switch to in-place execution. This adapter never installs dependencies, runs a
baseline, stages files, or creates a commit; do not create a commit.

## Stop Conditions

Preserve state and return a blocker for unsafe candidate ownership/overlap,
incompatible native plus unsafe Git fallback, unignored/uncertain generated
roots, branch conflicts, creation failures, or ambiguous cleanup/native output.
Worktree isolation remains optional for serial work. Must not delete worktrees
without separate disposition authority.
