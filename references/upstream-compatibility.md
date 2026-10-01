# Upstream Compatibility

The plugin owns specification synthesis and ticket decomposition through `plan-coder` and its bundled [specification](./specification-template.md) and [ticket](./ticket-template.md) templates. Other stages compose installed, model-callable skills by capability and name.

## Capability Map

- `grilling` -> `grill-coder`
- `brainstorming`, `domain-modeling`, `codebase-design`, and `clean-architecture` -> `design-coder`
- `using-git-worktrees` -> `plan-coder` only when the isolation path is selected
- `tdd` -> `tdd-coder`
- `code-review` and `verification-before-completion` -> `delivery-coder`

## Reference Snapshots

These source snapshots identify the integration's provenance, not proof that every skill in them is model-callable or currently compatible. Apply the live checks below.

- Superpowers `v6.4.1`, official release archive SHA-256 `68719cba868f04218953d88c1f036e232ced6edd8d72f5570bbc4b79cdaf7b10`.
- `mattpocock/skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `4e97a9a3ed6517312da2a554304ea28609946dc1132816bea68029cef581e68b`.
- `nathankim0/clean-architecture-skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `6e37f8c68e0798b73fad2ce9639f81dafe6c1b0987c13b3e77b67647bab30804`.

## Compatibility Check

Before a stage delegates, confirm that each required upstream skill is visible in the current Host skill catalog, permitted for model invocation, and materially compatible with the expected input/output contract. Disk presence, plugin enablement and configuration overrides are not proof of invocation eligibility. Inspect the selected entry's metadata when needed: `disable-model-invocation: true` is a hard boundary even if the file can be read. If the catalog entry or invocation eligibility is absent, do not execute that skill indirectly through file reads, renamed wrappers, configuration changes, edited frontmatter or subagents.

The current Matt Pocock `to-spec` and `to-tickets` entries are manual-only and intentionally excluded from the capability map. They are not dependencies of spec-coder 0.2.1. Users may invoke them manually outside this orchestration; do not require their installation, modify their flags, or ask the user to run them to complete native planning.

The initial orchestrator check must defer `using-git-worktrees` until workspace selection; its absence must not block safe in-place work. On the isolation path, check visibility, invocation eligibility and compatibility before using it. If unavailable, apply the workflow contract's workspace selection rules, including explicit user preferences, instead of silently reproducing the missing skill.

The shared workflow contract owns workspace selection and approval policy. Compose upstream mechanics within that policy: choosing to create or skip a worktree is a routine task decision, not an extra approval gate. Both modes retain baseline and Git safety requirements.

For an actually required capability, stop on incompatibility and report the stage, selected skill, visibility/metadata evidence and unmet contract. Report manual-only, absent and materially incompatible capabilities distinctly. Do not silently reproduce remembered upstream behavior or substitute a similarly named skill. Native planning uses its own bundled contract unconditionally; it is not a fallback for invoking a restricted upstream skill.
