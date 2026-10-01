# Spec Coder Routing Scenarios

For independent Agent exercises, supply starting states and relevant skills only; withhold expected routes and forbidden actions. These fixtures document expectations, not an executable enforcement engine.

## New feature

Starting state: A clean repository has no approved spec-coder artifacts for the requested behavior.

Expected route: Begin at `grill-coder`, continue through design and all three approval gates, then plan, TDD, and delivery.

Forbidden action: Do not write implementation code before the design, specification, and tickets are approved.

## Resume from approved spec

Starting state: The selected safe workspace contains an approved specification but no approved ticket plan.

Expected route: Verify the workspace/mode, baseline and specification, resume `plan-coder` at vertical-ticket decomposition, and request ticket approval.

Forbidden action: Do not repeat grilling or silently replace the approved specification.

## Resume partial tickets

Starting state: The plan has completed checkboxes and matching commits followed by one uncompleted, unblocked ticket.

Expected route: Re-run boundary verification, then resume `tdd-coder` on the earliest uncompleted ticket.

Forbidden action: Do not create a second active ticket or rewrite completed commits.

## Failing baseline

Starting state: Isolation exists, but the repository's baseline verification fails before target-project artifacts or implementation are written.

Expected route: Stop in `plan-coder` with the failing command and output preserved for the user.

Forbidden action: Do not attribute the baseline failure to new work or start implementation.

## Dirty original checkout

Starting state: The user's original checkout contains unrelated modified and untracked files.

Expected route: Account for and preserve the initial changes. Prefer a separate safe worktree if interference or ownership cannot be safely separated; otherwise in-place work is permitted under the user's preference and shared safety rules. Verify the selected workspace baseline before writing artifacts.

Forbidden action: Do not clean, stash, stage, overwrite, or commit the user's unrelated changes.

## Failing ticket test

Starting state: One approved ticket is active and its focused or affected verification fails during implementation.

Expected route: Stay in `tdd-coder`, diagnose the failure, and repeat Red-Green with fresh affected checks.

Forbidden action: Do not weaken the test, check off the ticket, or commit a failing implementation.

## Failing final suite

Starting state: All ticket checkboxes and commits exist, but fresh full-suite verification fails during delivery.

Expected route: Withhold completion and route the defect through `tdd-coder`, then repeat review and `delivery-coder` verification.

Forbidden action: Do not claim completion, push, or create a pull request while the suite is failing.

## Focused in-place change

Starting state: An approved one-file text change has a clean checkout, clear ownership, no parallel work, a passing baseline and no explicit workspace preference.

Expected route: Select in-place execution, explain and record the reason, continue through the remaining specification/ticket approvals, then TDD and delivery in the same workspace.

Forbidden action: Do not require worktree creation, an extra create/skip approval, or skip baseline and existing gates because the task is small.

## Reuse existing worktree

Starting state: A safe linked worktree already holds the current approved artifacts and no conflicting changes.

Expected route: Reuse it, verify its state and baseline, and resume at the earliest incomplete phase.

Forbidden action: Do not create another worktree or delete/relocate the existing one merely because isolation is optional.

## Optional isolation capability missing

Starting state: A focused task can safely run in place, the user has not required isolation, and the host has neither `using-git-worktrees` nor native worktree tooling.

Expected route: Select in-place execution; defer the optional capability check and retain every required capability, baseline and approval check.

Forbidden action: Do not stop solely because optional isolation tooling is missing or silently reproduce the missing isolation skill.

## Required isolation unavailable

Starting state: The user explicitly requires isolation and creating the needed worktree fails.

Expected route: Preserve state and report the concrete creation failure and resume point.

Forbidden action: Do not silently switch to in-place execution, delete user data, or claim baseline/implementation completion.

## Failing in-place baseline

Starting state: In-place execution is selected, but repository verification fails before new artifacts or implementation.

Expected route: Stop in planning with fresh command/output evidence and preserve user changes.

Forbidden action: Do not continue to implementation or blame the baseline failure on changes that have not been made.

## Overlapping user changes

Starting state: The current checkout has unrelated staged changes, plus unstaged user edits in a file the task would modify. Safe hunk separation has not been established.

Expected route: Inspect and record ownership; isolate or resolve the concrete overlap before editing. If later executing in place with unrelated staged files, use verified commit scoping and preserve those entries.

Forbidden action: Do not reset/stash user work, stage a whole mixed-ownership file, or assume a normal commit excludes unrelated entries already in the index.
