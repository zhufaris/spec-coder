# Upstream Compatibility

The plugin composes installed skills by capability and name. It does not copy their full instructions.

## Capability Map

- `grilling` -> `grill-coder`
- `brainstorming`, `domain-modeling`, `codebase-design`, and `clean-architecture` -> `design-coder`
- `to-spec` and `to-tickets` -> `plan-coder`
- `using-git-worktrees` -> `plan-coder` only when the isolation path is selected
- `tdd` -> `tdd-coder`
- `code-review` and `verification-before-completion` -> `delivery-coder`

## Validated Baseline

- Superpowers `v6.4.1`, official release archive SHA-256 `68719cba868f04218953d88c1f036e232ced6edd8d72f5570bbc4b79cdaf7b10`.
- `mattpocock/skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `4e97a9a3ed6517312da2a554304ea28609946dc1132816bea68029cef581e68b`.
- `nathankim0/clean-architecture-skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `6e37f8c68e0798b73fad2ce9639f81dafe6c1b0987c13b3e77b67647bab30804`.

## Compatibility Check

Before a stage delegates, confirm that the upstream skills required for the selected path are visible in the current Codex skill catalog. Treat renamed, missing, or materially changed input/output contracts as incompatibilities. The initial orchestrator check must defer `using-git-worktrees` until workspace selection; its absence must not block safe in-place work. On the isolation path, check it before using it. If unavailable, apply the workflow contract's workspace selection rules, including explicit user preferences, instead of silently reproducing the missing skill.

The shared workflow contract owns workspace selection and approval policy. Compose upstream mechanics within that policy: choosing to create or skip a worktree is a routine task decision, not an extra approval gate. Both modes retain baseline and Git safety requirements.

On incompatibility, stop and report the missing capability and the validated baseline above. Do not silently reproduce remembered upstream behavior or substitute a similarly named skill.
