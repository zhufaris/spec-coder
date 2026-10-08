# Upstream Compatibility

This compatibility contract applies to spec-coder `0.5.0`.

The plugin owns specification synthesis and ticket decomposition through `plan-coder` and its bundled [specification](./specification-template.md) and [ticket](./ticket-template.md) templates. Other stages compose installed, model-callable skills by capability and name.

## Capability Map

- `grilling` and `domain-modeling` -> `grill-coder`
- interactive `design-coder`: `brainstorming`, `domain-modeling`,
  `codebase-design`, and `clean-architecture`
- autonomous `design-coder`: native approach comparison plus
  `domain-modeling`, `codebase-design`, and `clean-architecture`; it must not
  invoke upstream `brainstorming` because that skill's hard human-approval gate
  is incompatible with an explicitly authorized no-wait path
- `tdd` -> `tdd-coder`
- `code-review` and `verification-before-completion` -> `delivery-coder`

## Bundled Capabilities

- `show-me` is a local approval-review adapter used before every suite-owned
  approval request. It is model-callable with the plugin and does not require
  an external show-me package, tmux, editor, browser, or executable.
- `using-git-worktrees` is a local optional isolation adapter invoked after an
  isolation path is selected during workspace preflight or for selected
  post-Gate-3 per-worker isolation. It prefers native Host worktree tools and
  needs no external skill package.
- `setup-coder` is a local manually invoked repository-onboarding adapter. It
  reports external capability compatibility but never installs or rewrites an
  upstream skill.

The bundle also contains `scripts/verification-evidence.py`,
`scripts/check-artifacts.py` and their `scripts/spec_coder_checks/` modules.
These are Python 3.11+ standard-library CLIs, not additional public skills or an
external planning package. Git is required for workspace evidence and delivery
commit inspection. Keep scripts and modules together and resolve their absolute
paths from the plugin root, independently of target-project cwd. Follow
[Verification evidence](./verification-contract.md#cli-and-explicit-observations)
and [Artifact checking](./artifact-format.md#command-interface). Missing baseline
capture/check tooling falls back to fresh project verification with the reason;
missing artifact tooling must be reported as unavailable, never a structural
pass. Historical unmarked artifacts follow the explicit manual-review path.

## Reference Snapshots

These source snapshots identify the integration's provenance, not proof that every skill in them is model-callable or currently compatible. Apply the live checks below.

- Superpowers `v6.4.1`, official release archive SHA-256 `68719cba868f04218953d88c1f036e232ced6edd8d72f5570bbc4b79cdaf7b10`.
- `mattpocock/skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `4e97a9a3ed6517312da2a554304ea28609946dc1132816bea68029cef581e68b`.
- `nathankim0/clean-architecture-skills` `main` snapshot downloaded 2026-10-01, archive SHA-256 `6e37f8c68e0798b73fad2ce9639f81dafe6c1b0987c13b3e77b67647bab30804`.

## Compatibility Check

The autonomous path is enabled only by explicit request-scoped
`autonomous=true` authority. It does not bypass an upstream hard gate by
rewriting, wrapping, or indirectly executing that upstream skill. In
particular, autonomous `design-coder` performs its own grounded comparison and
must not invoke `brainstorming`; the interactive path continues to compose it.
Both paths continue to use `domain-modeling`, `codebase-design`, and
`clean-architecture`.

Before a stage delegates, confirm that each required upstream skill is visible in the current Host skill catalog, permitted for model invocation, and materially compatible with the expected input/output contract. Disk presence, plugin enablement and configuration overrides are not proof of invocation eligibility. Inspect the selected entry's metadata when needed: `disable-model-invocation: true` is a hard boundary even if the file can be read. If the catalog entry or invocation eligibility is absent, do not execute that skill indirectly through file reads, renamed wrappers, configuration changes, edited frontmatter or subagents.

The current Matt Pocock `grill-with-docs`, `to-spec`, and `to-tickets` entries,
and the locally installed `grill-me-with-doc`, are manual-only and intentionally
excluded from the capability map. They are not dependencies of spec-coder
0.5.0. Users may invoke them manually outside this orchestration; do not require
their installation, modify their flags, rename/wrap them, or ask the user to
run them to complete the native workflow. `grill-coder` instead composes the
model-callable `grilling` and `domain-modeling` primitives directly.

## Default Delegation and Review Compatibility

Every eligible approved or autonomously selected ticket delegates by default.
The [routing contract](./subagent-routing-contract.md#delegation-eligibility-and-execution-mode)
owns eligibility, scoped opt-outs and capability/capacity outcomes. Planning uses
[Execution Waves](./subagent-routing-contract.md#execution-waves): interactive Gate 3 approves
the durable layout and autonomous Gate 3 selects its grounded recommendation.
Apply [Explicit Parallel Requests](./subagent-routing-contract.md#explicit-parallel-requests)
for isolation preparation and fallback; serial delegation does not require worktrees.

Delivery's [Review Execution](./subagent-routing-contract.md#review-execution)
owns independent Standards and Spec axes and local/delegated review selection.
An upstream review method must preserve that selected mode and two-layer limit;
never invoke a delegating method under an opt-out or from a child. Main owns
final findings and fresh verification.

Suite-owned human approvals consume the [approval review contract](./approval-review-contract.md#review-snapshot).
Autonomous selection does not invoke `show-me`; authority is determined by
[Approval Gates](./workflow-contract.md#approval-gates), not presentation.

## Optional Host Model Routing

Version `0.5.0` exposes nine bundled skills. Optional model routing is not a required Host model dependency and never switches the active main model (the
current Agent/session model). Load [Configuration](./subagent-routing-contract.md#configuration)
and [Route Selection](./subagent-routing-contract.md#route-selection) before a
route decision; these own bundled defaults, user precedence and repository floors.
The live Host determines usable identifiers and overrides. Loading these rules
does not authorize configuration changes or installation.

[Authority](./subagent-routing-contract.md#authority) owns two-layer/no-indirect-
delegation limits; these are not Host-level sandbox isolation.
[Attempt Evidence and Promotion](./subagent-routing-contract.md#attempt-evidence-and-promotion)
owns provisional results and main-created promotion. Use the complete
[worker brief](./worker-brief-template.md#assembly) even without inherited context.

Defer optional `using-git-worktrees` until isolation is selected. Confirm live
invocation eligibility, prefer native tools, and return failures to the
[workspace policy](./workflow-contract.md#workspace-selection). Do not silently
override explicit isolation requirements or introduce a worktree approval gate.

For a required capability, stop on incompatibility with its stage, selected
skill, visibility/metadata evidence and unmet contract. Distinguish manual-only,
absent and incompatible capabilities. Do not reproduce remembered upstream
behavior, substitute a similarly named skill or bypass a restricted entry.
Native planning is always bundled, not a fallback for restricted upstream skills.
