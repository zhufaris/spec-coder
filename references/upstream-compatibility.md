# Upstream Compatibility

This compatibility contract applies to spec-coder `0.5.0`.

The plugin owns specification synthesis and ticket decomposition through `plan-coder` and its bundled [specification](./specification-template.md) and [ticket](./ticket-template.md) templates. Other stages compose installed, model-callable skills by capability and name.

## Capability Map

- `grilling` and `domain-modeling` -> `grill-coder`
- `brainstorming`, `domain-modeling`, `codebase-design`, and `clean-architecture` -> `design-coder`
- `tdd` -> `tdd-coder`
- `code-review` and `verification-before-completion` -> `delivery-coder`

## Bundled Capabilities

- `show-me` is a local approval-review adapter used before every suite-owned
  approval request. It is model-callable with the plugin and does not require
  an external show-me package, tmux, editor, browser, or executable.
- `using-git-worktrees` is a local optional isolation adapter invoked after an
  isolation path is selected during workspace preflight or for approved
  post-Gate-3 per-worker isolation. It prefers native Host worktree tools and
  needs no external skill package.
- `setup-coder` is a local manually invoked repository-onboarding adapter. It
  reports external capability compatibility but never installs or rewrites an
  upstream skill.

## Reference Snapshots

These source snapshots identify the integration's provenance, not proof that every skill in them is model-callable or currently compatible. Apply the live checks below.

- Superpowers `v6.4.1`, official release archive SHA-256 `68719cba868f04218953d88c1f036e232ced6edd8d72f5570bbc4b79cdaf7b10`.
- `mattpocock/skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `4e97a9a3ed6517312da2a554304ea28609946dc1132816bea68029cef581e68b`.
- `nathankim0/clean-architecture-skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `6e37f8c68e0798b73fad2ce9639f81dafe6c1b0987c13b3e77b67647bab30804`.

## Compatibility Check

Before a stage delegates, confirm that each required upstream skill is visible in the current Host skill catalog, permitted for model invocation, and materially compatible with the expected input/output contract. Disk presence, plugin enablement and configuration overrides are not proof of invocation eligibility. Inspect the selected entry's metadata when needed: `disable-model-invocation: true` is a hard boundary even if the file can be read. If the catalog entry or invocation eligibility is absent, do not execute that skill indirectly through file reads, renamed wrappers, configuration changes, edited frontmatter or subagents.

The current Matt Pocock `grill-with-docs`, `to-spec`, and `to-tickets` entries,
and the locally installed `grill-me-with-doc`, are manual-only and intentionally
excluded from the capability map. They are not dependencies of spec-coder
0.5.0. Users may invoke them manually outside this orchestration; do not require
their installation, modify their flags, rename/wrap them, or ask the user to
run them to complete the native workflow. `grill-coder` instead composes the
model-callable `grilling` and `domain-modeling` primitives directly.

## Default Delegation and Review Compatibility

Every eligible approved ticket uses default delegation to one direct worker,
including a wave with only one ticket. A request-wide opt-out, ticket-specific
opt-out, or review-specific opt-out selects main-local execution only for that
scope and prohibits direct and indirect spawning there. Delegation eligibility
requires dependency readiness, grounded inputs, bounded reversible scope, an
independently inspectable seam, and no main-only authority or credentials.

One dependency-aware execution wave is active at a time. A parallel wave has
at most four ownership-safe tickets, never exceeds live Host direct-child
capacity, and requires real Host/task workspace isolation. When isolation is
not available, delegation continues through serialized direct workers; path
disjointness inside one shared workspace is not isolation. When spawn
unavailable, main records the reason and runs the same workflow locally unless
delegation was explicitly required, in which case the missing capability is a
blocker.

Delivery uses exactly two independent direct reviewers by default. One gathers
evidence for the Standards axis and one for the Spec axis; main owns the final
findings and conclusions. The upstream `code-review` skill is a review method,
not authority to change the selected execution mode. Under a request-wide or
review-specific opt-out, or when spawn is unavailable and delegated review was
not explicitly required, main performs equivalent independent Standards and
Spec passes locally. It must not invoke upstream `code-review` if that path
would spawn children or otherwise violate the local mode. When spawn is
unavailable and delegated review was explicitly required, delivery stops with
a concrete Host-capability blocker.

All suite-owned approvals and mutation reviews use bundled `show-me` to present
two to four grounded, materially distinct choices and their consequences.
Presentation does not grant approval or expand authority.

## Optional Host Model Routing

Version `0.5.0` exposes exactly nine bundled skills. The trusted plugin-owned
bundled defaults use schema version 1 and map `economy` to `trae` /
`GPT-5.6-Luna`, `standard` to `trae` / `GPT-5.6-Terra`, and `strong` to `trae` /
`GPT-5.6-Sol`. They require no initial configuration. Three-tier subagent
routing is an orchestration optimization, not a required upstream skill and
not a required Host model dependency. Provider/model identifiers must be
checked against the live Host catalog and subagent tool interface before each
override.

An optional trusted user mapping lives at
`$XDG_CONFIG_HOME/spec-coder/model-routing.toml`, with
`~/.config/spec-coder/model-routing.toml` as the fallback path. A valid user
file completely replaces the bundle rather than merging with it. An invalid
user file warns and selects `inherit-main`; it does not fall back to the
bundle. Setup must show an exact diff and receive explicit approval before
creating or editing user-owned configuration. Repository
`.spec-coder/model-routing.toml` policy may only raise `minimum_tier`; it cannot
name providers/models or lower a workflow classification. Missing tier mappings
or unavailable candidates in a valid configuration fall upward through
`economy`, `standard`, `strong`, then `inherit-main`. An invalid user mapping or
repository policy goes directly to `inherit-main` with a warning; it is never
guessed or partially reused. See the authoritative
[subagent routing contract](./subagent-routing-contract.md) for selection and
failure rules.

Routing never switches the active main model; it remains the current
Agent/session model. The complete agent tree has at most two layers, and only
the active main agent may spawn or delegate. Every direct-child brief states
`delegation_allowed = false`; a child returns further delegation needs to main
instead of using a skill, workflow, tool, or agent indirectly. A failed or
boundary-crossing delegated attempt may be promoted only when main creates an
inherited-main layer-2 sibling. It does not cycle through configured tiers.

If the live Host can deny spawn tools to a child, main uses that capability as
defense in depth. The portable contract does not require such a feature and is
not Host-level sandbox isolation. Model routing cannot bypass
`disable-model-invocation`, permissions, sandbox, Git ownership, or
external-mutation boundaries.

The initial orchestrator check defers the bundled `using-git-worktrees` path
until workspace selection. Its mechanics are irrelevant to safe in-place work.
On the isolation path, confirm the bundled skill is visible/model-callable and
inspect native tool availability before using Git fallback. A native tool
failure or safe-fallback failure returns to the workflow contract's workspace
rules; never silently override an explicit isolation requirement.

The shared workflow contract owns workspace selection and approval policy. Compose upstream mechanics within that policy: choosing to create or skip a worktree is a routine task decision, not an extra approval gate. Both modes retain baseline and Git safety requirements.

For an actually required capability, stop on incompatibility and report the stage, selected skill, visibility/metadata evidence and unmet contract. Report manual-only, absent and materially incompatible capabilities distinctly. Do not silently reproduce remembered upstream behavior or substitute a similarly named skill. Native planning uses its own bundled contract unconditionally; it is not a fallback for invoking a restricted upstream skill.
