# Upstream Compatibility

This compatibility contract applies to spec-coder `0.9.0`.

## Task Playbook compatibility and pstack boundary

`spec-coder` internally selects exactly one Task Playbook (Feature, Bug Fix,
Refactor, Performance, Skill Change, Workflow Eval, or Generic) from observed
task evidence. The selected task owns its SOP and composes stage procedures; it preserves the
fixed stage order, Gate 1/2/3, one native implement-spec executor, two layers,
and the nine public model-callable skills. Its detailed contract is
[Task Playbook contract](./task-playbook-contract.md).

Cursor `pstack` at `cursor/plugins` commit
`1ba91fc25c0977741dd0e267849e6234b037ed0a` is MIT provenance only and **not a dependency**. Spec-coder neither vendors nor invokes pstack, poteto-mode,
pstack agents, Cursor controls, or pstack model identifiers. No pstack
installation, configuration, model setup, or runtime dependency is required;
the existing Host compatibility and model-routing rules remain authoritative.

The plugin owns specification synthesis and ticket decomposition through `plan-coder` and its bundled [specification](./specification-template.md) and [ticket](./ticket-template.md) templates. Other stages compose installed, model-callable skills by capability and name.

## Capability Map

- `grilling` and `domain-modeling` -> `grill-coder`
- interactive and autonomous `design-coder`: native conservative
  classification, approach comparison, and Gate routing plus `domain-modeling`,
  `codebase-design`, and `clean-architecture` when applicable
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

Only request-scoped `autonomous=true` enables autonomy. `design-coder` owns
classification, grounded alternatives, presentation, and Gate routing; neither
mode invokes `brainstorming`. Use `domain-modeling`, `codebase-design`, and
`clean-architecture` when applicable.

Before delegation, confirm upstream skills are Host-visible, model-callable,
and I/O-compatible. Disk/plugin presence is insufficient;
`disable-model-invocation: true` is a hard boundary. Never bypass restriction
through reads, wrappers, configuration/frontmatter edits, or subagents.

Matt Pocock `grill-with-docs`, `to-spec`, `to-tickets`, and `implement-spec`,
plus local `grill-me-with-doc`, are manual-only and excluded. Matt
`implement-spec` is provenance only, not a dependency; native `plan-coder` and the
native implement-spec executor own planning and post-Gate-3 scheduling. Do not
install, modify, wrap, or require them. Users may invoke them outside this
orchestration; they are not workflow dependencies.

`grill-coder` directly composes model-callable `grilling` and `domain-modeling`.
Its decision-tree rounds contain at most three dependency-ready independent
questions; scope, domain meaning/ownership, core invariants, architecture, and
known/unknown coupling remain serial. It assigns stable IDs/recommendations,
handles partial/ambiguous answers conservatively, and keeps repository-fact
investigation agent-owned without emulating a with-doc wrapper.

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

Version `0.9.0` exposes nine bundled skills. Optional model routing is not a required Host model dependency and never switches the active main model (the
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

## Context ownership compatibility

The normal `spec-coder` entry has three common owners: the workflow envelope,
compatibility check, and verification lifecycle. Route selection, gate
transitions, delegation/dispatch, executor recovery, and workspace preparation
load only at their named conditional trigger, preserving compatibility without
loading every detailed contract on each entry.

The shared Task SOP scaffold belongs to the Task Playbook contract; Task files
retain route-specific deltas. The workflow contract owns executor entry and
handoff, the routing contract owns detailed executor and delegation, and the
implementation stage owns one-ticket lifecycle evidence. This is a public
ownership map, not a replacement for the linked contracts.

## Three-layer instruction ownership

`principles/` owns triggered judgment rules, `playbooks/tasks/` owns task SOPs,
and `playbooks/stages/` owns reusable stage procedures. The nine public Skills
remain compatible entrypoints or action capabilities; a stage entry references
its procedure instead of duplicating it. Calls to capability Skills do not
automatically create subagents. Keep `principles/` and `playbooks/` in every
local or installed bundle. Pstack remains provenance only.
