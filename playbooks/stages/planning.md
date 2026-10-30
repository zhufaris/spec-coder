# Planning stage playbook

## Procedure

### Capabilities

Bundled specification/ticket templates and `check-artifacts.py`; `using-git-worktrees` only for selected isolation.
Main alone authorizes direct delegation; children must not spawn.

### Conditional Principles

- **Context pressure:** read [guard-context](../../principles/guard-context.md#guard-the-context) only on this observed trigger.

### Steps

1. Validate workspace path, mode/rationale, branch, base, initial changes,
   dependency preparation and baseline output; re-inspect Git, ownership and
   concurrency. Missing, stale or unsafe evidence returns to preparation.
   `using-git-worktrees` remains isolation-only.
2. Revalidate dependency/environment readiness, current-request provenance, and
   that the prepared baseline is green before any target-project write. Keep
   main-observed capture JSON in conversation at this point; do not run `check`
   against a nonexistent artifact or weaken the green-baseline write boundary.
3. Stop with exact commands/output and return to workspace preparation/prepared
   evidence when ownership is unsafe or the baseline is not green.
4. Write the specification by synthesizing the approved or autonomously
   selected design into `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` with the local template.
   Preserve the selection's `kind`, `entry_evidence`, `design_obligations`,
   `red_or_pin`, `delivery_proof` and selected `conditional_references`, plus
   outcomes, architecture decisions and testing seams;
   do not conduct a new interview or invent decisions. Record workspace mode,
   rationale, branch, starting revision and relevant initial changes locally.
   Include every exact main-observed baseline capture record in the specification.
5. Apply Planning reuse interface against the written specification: run its
   compact non-executing `verification-evidence.py check` for every required
   record, confirm current provenance and dependency/environment observations,
   and require `reusable` plus the matching `record_id`. Standalone, resume,
   malformed or uncertain evidence, and `rerun` load Verification fallback and
   establish fresh verification. Stop and return to workspace preparation when
   any required baseline is not green.
6. Run bundled `scripts/check-artifacts.py --phase spec --spec <absolute-spec>`
   before Gate 2. Resolve findings or follow its unsupported-format/manual-review
   path; structural success does not approve decisions. Reconcile selected
   scenarios, context/model responsibilities, invariants, interaction decisions,
   dependency rules and testing seams against specification locations. Return
   missing decisions to `design-coder`, never invent entities, services or
   recovery policy. Interactively present the specification with `show-me` and
   stop at Gate 2; autonomously record the unique grounded recommendation.
7. After specification approval or autonomous selection, create vertical tickets
   with the local template as observable, context-window-sized increments. Each
   ticket carries the applicable selection reference, `red_or_pin`, and
   `delivery_proof`. Include
   blocking edges, acceptance, selected-context/model/rule/interface/interaction
   references and verification. Record dependencies, delegation eligibility/mode
   or opt-out, ownership/exclusions, isolation/concurrency, verification seam,
   capacity, real-isolation requirement and `delegation_allowed = false`. Do not
   copy the model or split mechanically; selected interaction can span contexts.
   Store checkbox tickets in `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md` and
   durable planned waves under Execution Waves; order is not dependency.
8. Before Gate 3, compile the nonempty graph for the native implement-spec
   executor: ownership, seams, capacity, authoritative workspace, wave base, isolation,
   permitted preparation, durable waves and blockers. A singleton is the same
   graph; planning records inputs but never schedules workers.
9. Under Execution Waves and Explicit Parallel Requests, retain one active
   wave, real isolation for parallel mutation, and recovery from checkboxes plus
   committed Git state.
10. Run bundled `scripts/check-artifacts.py --phase plan --spec <absolute-spec>
   --plan <absolute-plan> --repo <absolute-workspace>` before Gate 3; resolve findings under the same format
   contract. Before Gate 3, reconcile decision coverage and ticket readiness under the
   domain contract's Ticket decomposition section. Check delegation eligibility,
   mutation ownership, exclusions, dependencies, isolation, concurrency conflicts,
   verification seams and Host capacity. Review and approve the authoritative
   workspace, recorded wave base, isolation requirement, permitted
   integration/isolation preparation, task graph, durable-wave membership/order,
   and blocking edges with the tickets. Validate the durable partition under
   Execution Waves. Resolve load-bearing omissions through design/specification;
   independent selected slices need not wait for an unrelated open decision.
   Present the full ticket set and wave membership/order. In interactive mode,
   invoke `show-me` and wait for explicit implementation authorization; in
   autonomous mode record the unique grounded recommendation without waiting.

Creating an external issue, publishing to an issue tracker, pushing a branch, or opening a pull request always requires separate explicit authorization.

At the existing Gate 2/3 checks, reconcile the selected decisions covered by the contract's [language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [protected-behavior](../../references/domain-design-contract.md#protect-behavior-and-valid-values), and [persistence](../../references/domain-design-contract.md#aggregate-persistence-semantics) sections against their specification locations and ticket references/acceptance. Do not create a second model inventory; resolve missing decisions through the existing return paths.
