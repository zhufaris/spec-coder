---
name: setup-coder
description: Audit and initialize a target Git repository for spec-coder through an idempotent repository-local AGENTS.md managed block, Host capability checks, verification-command discovery, exact-diff approval, and READY/WARNING/BLOCKED reporting. Use when a user explicitly asks to set up or onboard a repository; do not run before every coding task.
---

# Setup Coder

Apply the required owner sections below. Setup follows its own exact-diff
authorization and read-only routing-policy audit.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Repository Setup](../../references/workflow-contract.md#repository-setup).
- [Configuration](../../references/subagent-routing-contract.md#configuration).
- [Capability Map](../../references/upstream-compatibility.md#capability-map), [Compatibility Check](../../references/upstream-compatibility.md#compatibility-check).

## Conditional Reading

- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Setup audit or mutation:** load the complete [setup contract](../../references/setup-contract.md) before auditing or proposing bytes.

## Input

The target Git repository (default: current repository), the current Host skill
catalog and invocation metadata, repository instructions/build evidence, and an
explicit requested scope. Default scope is repository-local. Global scope is
valid only after an explicit global request and separate exact-diff approval.

## Output

Return a conversational `SetupReport` containing:

- absolute target and scope;
- aggregate `READY`, `WARNING`, or `BLOCKED` status;
- required and optional capability evidence with affected stages;
- managed-block state and applied/proposed/no-op result;
- read-only model routing policy state and effective safety fallback;
- verification commands, their sources, and `executed` or `discovered` state;
- blockers, warnings, remediation, and confirmation of forbidden side effects.

Do not persist the setup report or create a private state/configuration file.

## Process

1. Confirm the target is a readable Git repository. Inspect its root
   `AGENTS.md`, relevant parent/global instructions, Git status, current branch,
   and existing worktrees without changing them.
2. Audit every bundled and external capability required by the workflow. For
   external skills, current Host visibility, model invocation eligibility, and
   material compatibility are all required. Treat
   `disable-model-invocation: true` as a hard `BLOCKED` boundary. Record
   optional gaps as `WARNING`; do not install or rewrite another skill.
3. Inspect `.spec-coder/model-routing.toml` read-only when present. Report an
   absent policy as optional, a valid `minimum_tier`, or an invalid policy with
   its conservative `inherit-main` fallback. Never create or edit the user or
   repository model routing configuration during setup.
4. Read the canonical [AGENTS snippet](../../assets/agents-snippet.md) and
   classify the target block as `absent`, `current`, `stale`, `malformed`, or
   `duplicated` under the setup contract. A current block is a zero diff no-op.
   Malformed or duplicated markers block automatic mutation.
5. Discover verification commands from repository evidence in the contract's
   precedence order. Execute only safe, already available commands; otherwise
   label them `discovered`. Do not install dependencies. Do not invent a
   command to make setup appear complete.
6. For an absent or stale valid block, create an exact diff that preserves all
   marker-external bytes. Include a concise verification subsection only when
   durable repository instructions are absent and the command evidence is
   trustworthy. Present the diff and mutation `ReviewSnapshot` through
   `show-me`, then ask for explicit approval.
7. Immediately before writing, re-read the target and prove an unchanged base.
   If it changed, invalidate approval and produce a new proposal. Apply only the
   approved diff, then re-read and verify the managed block and surrounding
   bytes.
8. Aggregate checks as `BLOCKED > WARNING > READY` and report concrete evidence
   and remediation. Safe local configuration may complete before an unrelated
   blocker is reported, but the final status must remain `BLOCKED`.

Report evidence that cannot be established as `not assessable from supplied
evidence`; do not invent an owner, command, status, or stage. An absent/stale
required local block awaiting or denied approval is `BLOCKED`. A safe completed
update with only discovered-but-unexecuted verification is `WARNING`.

Do not create a worktree, specification, ticket, glossary, ADR, setup config,
stage, commit, install, push, PR, or external issue. Do not modify global
configuration under repository-local scope.

## Stop Conditions

Stop without a configuration write when:

- the target is not a readable Git repository;
- managed markers are malformed, nested, reversed, or duplicated;
- the exact diff is not approved;
- the target differs from the approved base at apply time;
- the requested global scope was not explicit or separately authorized;
- a required capability is missing, manual-only, or materially incompatible
  after all independently safe checks and approved repository-local
  configuration are complete (or no such configuration is possible);
- file ownership, permissions, or overlapping user changes make attribution
  unsafe.

Preserve the target, base evidence, proposed diff, capability result, and resume
point. Never turn a warning or blocker into `READY` to finish setup.
