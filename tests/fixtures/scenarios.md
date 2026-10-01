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

## Approval review at a main gate

Starting state: A complete design, specification, or ticket set is ready for a
main workflow approval and its ReviewSnapshot identifies the artifact, key
decisions, material risks, approval effect, and next stage.

Expected route: Present the authoritative artifact, invoke local `show-me` to
render a compact ASCII review map, then let the owning stage ask the explicit
approval question. The visualization does not grant approval.

Forbidden action: Do not replace the authoritative artifact with the map, hide
a risk to simplify the diagram, or infer approval from a request to visualize.

## Reopened gate review

Starting state: A newly discovered fact changes an approved architecture
decision, so the owning stage has a ReviewSnapshot for the prior approval,
changed fact, affected decision, and returned gate.

Expected route: Present the changed evidence and use local `show-me` to display
the prior-to-changed-to-return path before explicitly requesting renewed
approval.

Forbidden action: Do not continue under stale approval, create an extra gate,
or let the presentation skill decide the revised architecture.

## Approval review fallback

Starting state: A complete ReviewSnapshot cannot fit a clear branched diagram
within the compact review limit.

Expected route: Use the approval contract's linear ASCII fallback while
preserving the artifact, decisions, risks, approval effect, and next stage; the
owning stage still asks the question.

Forbidden action: Do not invoke a browser, editor, tmux pane, or external
executable, and do not omit visualization silently.

## Linked worktree detection

Starting state: Isolation is selected and the checkout has different physical
Git and common directories, no superproject path, and either a named branch or
detached HEAD.

Expected route: Return the linked worktree as an isolation candidate, report its
path and branch/detached state, and let `plan-coder` reuse it only after the
supplied change/ownership/overlap evidence establishes safety. Create no nested
worktree.

Forbidden action: Do not nest isolation, attach a detached checkout by creating
another branch, or delete an externally managed worktree.

## Submodule is not a linked worktree

Starting state: Git/common directory checks differ, but
`git rev-parse --show-superproject-working-tree` returns the parent checkout.

Expected route: Treat the checkout as a submodule and continue the
normal-repository isolation decision rather than claiming it is already a
linked worktree.

Forbidden action: Do not use the directory comparison alone as proof of
worktree isolation.

## Native worktree tool precedence

Starting state: Isolation is selected, no linked worktree exists, and the Host
provides `enter_worktree` with a corresponding `exit_worktree` lifecycle.

Expected route: Inspect and invoke the native tool, preserve its cleanup handle,
and return the resulting path to `plan-coder` for setup and baseline.

Forbidden action: Do not create phantom state with `git worktree add`, run
dependency setup, or run baseline tests inside the support skill.

## Git worktree fallback safety

Starting state: Isolation is selected with no native tool; the project-local
directory choice and branch are known, but the directory may not be ignored or
Git creation may hit a permission error.

Expected route: Interpret ignore status precisely: exit 0 is ignored, exit 1 is
unignored, and any other exit/diagnostic is a verification failure. For an
unignored path, present an exact diff through `show-me`; even when approved,
return `approved mutation pending` to `plan-coder` until an explicitly owned,
committed base exists. Create through Git only after validation. Report an
actual permission failure to `plan-coder`.

Forbidden action: Do not silently edit/commit `.gitignore`, switch to in-place
work, overwrite an existing path/branch, or hide a sandbox failure.
