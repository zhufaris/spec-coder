# Upstream Compatibility

This compatibility contract applies to spec-coder `0.4.0`.

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
- `using-git-worktrees` is a local optional isolation adapter invoked during
  workspace preflight only after the isolation path is selected. It prefers native
  Host worktree tools and needs no external skill package.
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
0.4.0. Users may invoke them manually outside this orchestration; do not require
their installation, modify their flags, rename/wrap them, or ask the user to
run them to complete the native workflow. `grill-coder` instead composes the
model-callable `grilling` and `domain-modeling` primitives directly.

## Optional Host Model Routing

Version `0.4.0` still exposes exactly nine bundled skills. Three-tier subagent
routing (`economy`, `standard`, and `strong`) is an orchestration optimization.
It is not a required upstream skill and not a required Host model dependency. Provider/model names in
the user configuration are examples and must be checked against the live Host
catalog and subagent tool interface before each override.

Trusted mappings live at `$XDG_CONFIG_HOME/spec-coder/model-routing.toml`, with
`~/.config/spec-coder/model-routing.toml` as the fallback path. Repository
`.spec-coder/model-routing.toml` policy may only raise `minimum_tier`; it cannot
name providers/models or lower a workflow classification. Missing tier mappings
or unavailable candidates in a valid configuration fall upward through
`economy`, `standard`, `strong`, then `inherit-main`. An invalid user mapping or
repository policy goes directly to `inherit-main` with a warning; it is never
guessed or partially reused. See the authoritative
[subagent routing contract](./subagent-routing-contract.md) for selection and
failure rules.

Routing never switches the active main model. `main-only` responsibilities stay
with the main agent. A failed or boundary-crossing delegated attempt promotes
directly once to inherited main and does not cycle through configured tiers.
Model routing cannot bypass `disable-model-invocation`, permissions, sandbox,
Git ownership, or external-mutation boundaries.

The initial orchestrator check defers the bundled `using-git-worktrees` path
until workspace selection. Its mechanics are irrelevant to safe in-place work.
On the isolation path, confirm the bundled skill is visible/model-callable and
inspect native tool availability before using Git fallback. A native tool
failure or safe-fallback failure returns to the workflow contract's workspace
rules; never silently override an explicit isolation requirement.

The shared workflow contract owns workspace selection and approval policy. Compose upstream mechanics within that policy: choosing to create or skip a worktree is a routine task decision, not an extra approval gate. Both modes retain baseline and Git safety requirements.

For an actually required capability, stop on incompatibility and report the stage, selected skill, visibility/metadata evidence and unmet contract. Report manual-only, absent and materially incompatible capabilities distinctly. Do not silently reproduce remembered upstream behavior or substitute a similarly named skill. Native planning uses its own bundled contract unconditionally; it is not a fallback for invoking a restricted upstream skill.
