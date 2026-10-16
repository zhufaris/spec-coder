# Repository Setup Contract

This contract governs the manually invoked `setup-coder`. Setup is one-time and
idempotent, not a stage in the fixed spec-coder coding workflow.

## Scope and authority

Default to the target repository's root `AGENTS.md` managed block and the two
exact root `.gitignore` entries `/.worktrees/` and `/.cache/`. Repository-local
setup is portable and reviewable. Reading parent or user-global instructions is allowed
for precedence/conflict evidence, but a global file may change only after an
explicit global request, a separate exact diff, and separate approval.

Do not install the plugin or dependencies. Do not modify an upstream skill or
change invocation metadata. Do not create a worktree. Do not create a
specification. Do not create a ticket. Do not stage. Do not commit or push. Do
not persist the setup report. Do not create a private setup state or
`.spec-coder` configuration file.

Read-only inspection of `.spec-coder/model-routing.toml` is allowed. Validate it
against the subagent routing contract and report the model routing policy as
absent, valid with its `minimum_tier`, or invalid with conservative
`inherit-main` behavior. Absence is optional and does not lower readiness;
invalid content is a `WARNING`. Setup must not create or edit this repository
policy or either trusted user mapping path.

The approved `AGENTS.md` managed-region update and the two exact root
`.gitignore` entries are onboarding mutations, not coding artifacts or
implementation changes. They may therefore run outside the fixed coding phase
order and before a project baseline. Their exact authority, byte-preservation,
approval, and concurrent-base checks do not permit any other pre-baseline write
or arbitrary `.gitignore` normalization, deletion, or reordering.

## Capability assessment

Use the live Host catalog, not disk presence or enabled-plugin state alone.
For each external capability required by a workflow stage, record:

- name and owning stage;
- Host visibility;
- model invocation eligibility;
- material input/output compatibility;
- required or optional classification;
- evidence and remediation.

`disable-model-invocation: true` is a hard boundary. Never bypass it through a
wrapper, file read, config edit, rename, or subagent. Bundled plugin skills must
also be visible and model-callable after installation. Missing required
capability yields `BLOCKED`; an optional path gap yields `WARNING`.

## Managed block state

The canonical base is `assets/agents-snippet.md` with exactly these markers:

```text
<!-- spec-coder:start -->
<!-- spec-coder:end -->
```

Classify:

| State | Meaning | Action |
| --- | --- | --- |
| `absent` | Neither marker exists | Propose file creation or byte-preserving insertion |
| `current` | Exactly one ordered pair contains current generated content | Zero diff; no write |
| `stale` | Exactly one ordered pair contains older valid content | Propose replacing only that block |
| `malformed` | Missing endpoint, reversed order, or nested markers | `BLOCKED`; no guessed repair |
| `duplicated` | More than one start/end pair or block | `BLOCKED`; no guessed repair |

Apply classification precedence before content comparison:

1. missing endpoint, unbalanced or unequal start/end counts, reversed order, or
   nested markers -> `malformed`;
2. two or more complete, ordered, disjoint pairs -> `duplicated`;
3. one complete ordered pair -> compare generated content for `current` or
   `stale`;
4. no markers -> `absent`.

Preserve content outside a valid managed block byte-for-byte, including
comments, spacing, line endings, and final newline state. A generated repository
verification subsection belongs inside the same managed block; do not create a
second authority or marker family.

For an existing marker-free file that ends in a line terminator, append the
managed block. If it has content but no final line terminator, place the managed
block before the existing bytes; do not add a terminator to user-owned content.
For an absent or empty file, write only the canonical managed block.

Unchanged inputs must produce zero diff. Repeated setup must not append another
block or reorder user content.

## Repository-local isolation roots

Alongside the managed block, setup owns only the exact root `.gitignore`
patterns `/.worktrees/` and `/.cache/`. It obtains their current/proposed facts
from Workspace Policy; it does not reinterpret equivalent-looking patterns,
remove duplicates, or modify any other ignore rule.

Classify the selected `.gitignore` target as absent, current, or partial:

| State | Meaning | Action |
| --- | --- | --- |
| `absent` | No root `.gitignore` exists | Propose a file containing only the missing generated entries |
| `current` | Both exact root entries are present | Zero diff; no write |
| `partial` | One or both exact root entries are absent | Propose only the missing entries, preserving all existing bytes |

For existing content ending in a line terminator, append only the missing exact
entries in their canonical order. If existing content has no final line
terminator, prepend the missing generated entries without terminating,
normalizing, or otherwise changing the user-owned bytes. This rule applies even
when the other root entry is already present. A missing file may be created.

The isolation-root proposal is idempotent: once its exact entries are present,
the next setup run is a zero-diff no-op. It remains separate from marker
classification: malformed or duplicated `AGENTS.md` markers block the complete
onboarding mutation rather than allowing a `.gitignore`-only write.

## Verification command discovery

Use evidence in this order:

1. `AGENTS.md` and other authoritative repository instructions;
2. `README` and `CONTRIBUTING` documentation;
3. `Makefile`, package scripts, language manifests, and repository task files;
4. CI workflow commands as corroboration, accounting for CI-only secrets and
   environment.

Existing durable instructions remain authoritative. Do not duplicate their
commands in the managed block. When durable guidance is absent, the optional
generated subsection uses exactly this placement and form immediately before
the end marker:

```text
## Repository verification

- test: `<exact command>`
- lint: `<exact command>`
- type-check: `<exact command>`
- build: `<exact command>`
```

Omit kinds without trustworthy evidence. Keep the fixed order above, one entry
per kind, exact command bytes from the selected source, no trailing spaces, and
one final newline before `<!-- spec-coder:end -->`. These generated bytes are
part of `current`/`stale` comparison. Conflicting or unverified evidence remains
a report `WARNING` and is not embedded.

Mark commands `executed` only with fresh observed output. Mark safe commands
that were not run, or commands requiring missing environment/credentials, as
`discovered`. Do not install dependencies or execute clearly destructive,
credential-bound, external-production, or disproportionally expensive checks
merely to change the label.

## Mutation protocol

For `AGENTS.md` file absence, an absent or stale valid block, or an absent or
partial selected `.gitignore` target:

1. retain the exact inspected base bytes and SHA-256 digest for every selected
   target (`AGENTS.md` and `.gitignore`);
2. compute the exact per-target diff or replacement bytes, retaining the
   proposed digest, changed regions, and byte-for-byte preserved regions;
3. supply `show-me` one `ReviewSnapshot` naming every selected target, its
   base/proposed digest, changed/preserved regions, exact mutation, all-approved-targets
   re-read safety guard, risk/consequence, approval effect, and next stage;
4. show the authoritative diff and ask explicitly;
5. immediately before the first write, re-read all approved targets and require
   every base digest to be unchanged;
6. on any drift, block all writes, invalidate approval, and produce a new
   multi-target proposal rather than merging or overwriting;
7. apply only the approved bytes;
8. re-read and verify both generated content and every target's preserved bytes.

A concurrent change invalidates approval. Do not merge or overwrite it under
the old authorization; produce a new proposal. If an apply fails after a prior
target changed, report the exact partial apply (target, observed digest, and
which targets remain unapplied), retain the user-visible failure evidence, and
offer an idempotent rerun against fresh bases. Do not roll back user files. Its
`BLOCKED` state clears only after a fresh base, a new exact proposal, and new
approval. Approval of repository-local content never authorizes global content.

Under repository-local scope, inspect applicable parent/global instructions for
precedence evidence but do not mutate them. A stale compatible global managed
block is informational when the current repository-local block unambiguously
governs this repository. A material conflict is `WARNING` when local precedence
is clear and `BLOCKED` only when precedence is unresolved and the global rule
can change current-repository behavior. Report which condition applies.

## Status aggregation

Aggregate with `BLOCKED > WARNING > READY`:

- `READY`: all required capabilities pass, the repository-local block is
  current after any approved change, and no warning remains.
- `WARNING`: the workflow is usable but optional capability, verification
  execution, or non-conflicting evidence is incomplete.
- `BLOCKED`: required capability or invocation eligibility is missing, marker
  state is unsafe, the target changed after approval, or required access/scope
  authority is absent.

An absent or stale required repository-local block with pending approval is
`BLOCKED` while its exact mutation awaits approval and remains `BLOCKED` if
approval is declined. After an approved successful update,
discovered-but-unexecuted verification may leave the aggregate at `WARNING`.

Completing an independently safe configuration change does not erase a blocker.
Declining a proposed write leaves it unapplied and reports the actual state; it
does not create implicit approval or a false ready result.

## Report

Return in conversation only:

```text
Setup target: <absolute repository path>
Scope: repository-local | explicit global
Status: READY | WARNING | BLOCKED

Capabilities:
- <name>: <status> (<evidence>; affected stage)

Routing:
- AGENTS.md: current | proposed | updated | blocked
- model routing policy: absent | valid minimum=<tier> | invalid -> inherit-main

Verification:
- <kind>: <command> [source; executed | discovered]

Warnings/Blockers:
- <evidence and remediation, or none>

Forbidden side effects performed: none
```

Do not persist the setup report. On rerun, derive status from fresh evidence.
When the supplied/repository evidence cannot establish a capability owner,
command, marker state, or verification result, report `not assessable from
supplied evidence` and continue only with independent safe checks. Never fill a
report field by inference merely to make the report complete.
