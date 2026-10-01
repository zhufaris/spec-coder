# Spec Coder Routing Scenarios

## New feature

Starting state: A clean repository has no approved spec-coder artifacts for the requested behavior.

Expected route: Begin at `grill-coder`, continue through design and all three approval gates, then plan, TDD, and delivery.

Forbidden action: Do not write implementation code before the design, specification, and tickets are approved.

## Resume from approved spec

Starting state: The isolated worktree contains an approved specification but no approved ticket plan.

Expected route: Verify the worktree and specification, resume `plan-coder` at vertical-ticket decomposition, and request ticket approval.

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

Expected route: Preserve it and have `plan-coder` create or reuse a separate safe worktree before writing artifacts.

Forbidden action: Do not clean, stash, stage, overwrite, or commit the user's unrelated changes.

## Failing ticket test

Starting state: One approved ticket is active and its focused or affected verification fails during implementation.

Expected route: Stay in `tdd-coder`, diagnose the failure, and repeat Red-Green with fresh affected checks.

Forbidden action: Do not weaken the test, check off the ticket, or commit a failing implementation.

## Failing final suite

Starting state: All ticket checkboxes and commits exist, but fresh full-suite verification fails during delivery.

Expected route: Withhold completion and route the defect through `tdd-coder`, then repeat review and `delivery-coder` verification.

Forbidden action: Do not claim completion, push, or create a pull request while the suite is failing.
