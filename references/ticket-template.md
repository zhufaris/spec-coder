# Local Vertical-Ticket Template

This is a spec-coder resource used directly by `plan-coder` after specification approval or autonomous Gate 2 selection. Decompose the selected specification into a local plan at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`. Apply the [domain design contract](./domain-design-contract.md); do not require an external planning skill or issue tracker.

## Copyable v1 skeleton

This example pairs with the specification template's status-command example.
Replace illustrative content with actual selected decisions and ownership; keep
[Plan grammar](./artifact-format.md#plan-grammar), one checkbox heading per ticket
and explicit wave membership. It passes draft checking without fabricated
execution or commit evidence. Draft success is not implementation authorization.

```markdown
# Status command plan

<!-- spec-coder:artifact-v1 plan -->

## Workspace and authority

Name the native implement-spec executor and record the selected specification
path, authoritative workspace, recorded wave base, isolation requirement,
permitted integration/isolation preparation, baseline evidence, durable waves,
blocking edges, and Gate 2/3 decisions here before implementation.

## Wave W1: `T1`

### - [ ] T1: Report local readiness

| Field | Content |
| --- | --- |
| What to build | A read-only command that reports ready after checks pass. |
| Spec references | SCN-1, INV-1 |
| Dependencies | None |
| Delegation eligibility | Bounded local command with subprocess output and file-preservation checks. |
| Delegation mode | Default direct worker |
| Mutation ownership | status.py, tests/test_status.py |
| Exclusions | Remote health probes and automatic repairs. |
| Isolation | Serial worker; main validates the authoritative workspace, recorded wave base, and isolation requirement before dispatch. |
| Concurrency conflicts | None |
| Verification seam | Public command output, exit status and unchanged project files. |
| Host capacity | One direct-child slot; recheck live capacity before dispatch. |
| Direct-child boundary | delegation_allowed = false; assemble common brief and implementation role before dispatch. |
| Acceptance criteria and verification | Command reports ready, exits zero and leaves project files unchanged; verify through subprocess execution and file comparison. |

## Final delivery checks

Main reviews acceptance and commits, freshly executes the full applicable suite,
and checks delivery evidence before claiming completion.
```

Keep the active baseline record in the existing specification or plan following
[Authority and lifecycle](./verification-contract.md#authority-and-lifecycle).
Moving it to another artifact changes the exclusion context and requires fresh
capture; do not rewrite captured context to manufacture a hit.
After actual ticket verification and main's accepted commit, add
`Verification commands`, `Verification results` and `Commits` rows using
[Delivery evidence](./artifact-format.md#delivery-evidence). Never prefill results
or commit IDs. `--phase plan` allows unchecked tickets; `--phase delivery`
requires completion and recorded evidence but does not authenticate claims.

## Plan structure

Name the native implement-spec executor. Reference the selected specification and
authoritative workspace, record the recorded wave base, isolation requirement,
permitted integration/isolation preparation, starting revision/baseline, blocking
edges, and approval or autonomous-selection status, then list tickets, explicit
durable planned waves, and final delivery checks. Use stable ticket IDs and one
completion checkbox per ticket as the authoritative progress record. The runtime
plan has **one active execution wave** at most, selected from the approved or autonomously selected planned wave order;
Host and recovery handles remain conversational.

## Wave W1: `T1`, `T2`

Write one such explicit section for every planned wave before Gate 3, in execution
order, with its member ticket IDs and any recorded execution/isolation notes.
Every ticket exactly once is required across the durable planned waves; each wave has
at most four tickets. Dependencies must point only to earlier waves. Tickets in
the same wave have no ownership or semantic concurrency conflict, and a
main-local ticket is a singleton wave. Scheduling order is not a functional dependency:
record a dependency only when a ticket supplies a genuinely required
capability or contract.

For each ticket, include:

| Field | Content |
| --- | --- |
| Title and completion checkbox | A concise delivered capability, e.g. `### - [ ] T1: Cancel an eligible order` |
| What to build | Observable outcome and scope; a complete path through only the necessary modules |
| Spec references | Comma-separated approved decision IDs, e.g. SCN-1, INV-1; None only when no defined ID applies |
| Dependencies | IDs of tickets that supply a genuinely required capability or contract; otherwise None |
| Delegation eligibility | Grounded inputs, bounded/reversible scope, independently inspectable seam, and any main-only authority or credential that makes the ticket ineligible |
| Delegation mode | Default direct worker, main-local, required delegation, or an applicable request/ticket opt-out, including the reason |
| Ownership and implementation path | Relevant contexts/model elements, enforcing modules, interfaces, allowed boundary data and consistency/failure constraints; reference rather than copy the model |
| Mutation ownership | Comma-separated repository-relative files/directories, e.g. src/status.py, tests/; no globs or ambiguous module names |
| Exclusions | Files, responsibilities, authority, and unrelated changes outside the ticket |
| Isolation | Whether mutation is read-only, serial/shared, or requires real per-worker Host/task or Git isolation; record the isolation requirement and recorded wave base when applicable |
| Concurrency conflicts | Comma-separated IDs of tickets with ownership overlap or semantic conflicts that cannot share a wave; otherwise None |
| Verification seam | Independently inspectable focused evidence plus `scripts/validate-affected.py --repo <repository> --path <task-owned-path>` (repeat `--path` for every main-supplied task-owned path), with separate dependency/preservation evidence |
| Host capacity | Capacity assumptions for delegation; live capacity is rechecked when a wave is formed rather than persisted as fact |
| Direct-child boundary | `delegation_allowed = false`; main assembles the [common brief](./worker-brief-template.md#common-brief) and applicable role additions as actual outgoing content, including ownership, no indirect delegation/staging/commits and the shared heartbeat contract. |
| Acceptance criteria and verification | Applicable success/rejection/concurrency/duplicate/recovery outcomes and the verification seam used to prove them |
| Blocked by | IDs of tickets that supply a genuinely required capability or contract; otherwise None |

These fields and the planned-wave sections are scheduling inputs, not a
production scheduler or a persisted workflow aggregate. The durable plan fixes
membership and order; runtime forms a live dispatch batch only from the current
earliest incomplete planned wave. Delegated dispatch is capped by live Host
capacity and the suite wave limit, and requires real isolation for every
mutating worker when parallel. Apply
[Explicit Parallel Requests](./subagent-routing-contract.md#explicit-parallel-requests)
before isolation or capacity fallback. Runtime may shrink or serialize that wave
only as that policy permits, and must not regroup it
or pull tickets from a later planned wave. Resume reads durable wave membership,
checkboxes, and committed Git state; it does not invent new waves.

For ticket verification, main supplies the authoritative repository with
`--repo` and every attributed task-owned path with a repeated `--path` to the
bundled `scripts/validate-affected.py`. Record the exact focused and affected
commands and their results in delivery evidence. This ticket-level selection
does not replace the separate fresh full verification required at baseline and
delivery, and it does not grant acceptance, commit, or completion authority.

For relevant domain changes, references and acceptance preserve the approved business actions, refusal/bypass outcomes, value validity/equality, policy responsibilities and terminology compatibility. When persistence is affected, include aggregate save/load, controlled restoration, post-load behavior and applicable conflict verification. Keep these requirements within the capability slice, rather than separate tickets for model classes or a copied domain inventory.

## Slicing rules

- Keep each increment independently meaningful and verifiable within one agent context window. A business bounded context is not an agent context window.
- Slice by business capability or use-case increment. Introduce only supporting entities, services and adapters needed for that increment; do not create separate "all entities", "all services" and "all repositories" tickets.
- Preserve all guarantees needed for the slice to be correct. A happy-path ticket cannot postpone required concurrency or recovery behavior and still count as a complete capability. Combine work or choose a different boundary when necessary.
- A cross-context ticket is valid when participant ownership, interaction data, consistency and failure behavior are decided and the result is independently verifiable.
- Separate a prerequisite refactor only when it enables independently green delivery; describe unchanged outcomes and preservation evidence. For a wide mechanical migration, consider expand, migrate and contract steps that each retain passing checks. If safe increments cannot be found, revisit the design or plan an appropriately sized indivisible change; do not promise knowingly failing intermediate commits.
- Add only real blocking edges. Shared files or preferred execution order alone are not functional dependencies. Check for cycles and references to missing ticket IDs.

## Gate 3 review

Run bundled `check-artifacts.py --phase plan --spec <absolute-spec> --plan
<absolute-plan>` and resolve findings under [Findings and compatibility](./artifact-format.md#findings-and-compatibility).
Check coverage in both directions: every in-scope scenario/invariant has a responsible ticket, and every ticket traces to approved behavior and architecture. Resolve invalid blockers, excessive size and missing verification. Check every ticket's delegation eligibility and mode, mutation ownership and exclusions, dependencies, isolation need, concurrency conflicts, verification seam, Host-capacity requirement, real-isolation requirement, and `delegation_allowed = false` child boundary. Name unresolved load-bearing decisions and affected tickets; do not mark them implementation-ready. Independent approved slices need not wait on unrelated open decisions.

For every dispatch, main loads [Worker Progress Heartbeat](./subagent-routing-contract.md#worker-progress-heartbeat)
and [Worker Brief Assembly](./subagent-routing-contract.md#worker-brief-assembly),
then supplies the complete common brief and role additions. The routing owner
defines reporting capability/schedule and observation-only authority.

Present the ticket set, deliverables, dependencies, blocking edges, authoritative
workspace, recorded wave base, isolation requirement, permitted
integration/isolation preparation, and durable planned-wave membership/order for
Gate 3 review and implementation authority. Interactive Gate 3 approves the
workspace/isolation inputs with both the ticket set and wave layout. Autonomous Gate 3 selects
one unique grounded recommendation, records
`auto-selected under explicit autonomous authority`, and continues without
human waiting or `show-me`. Adjust granularity within the selected design when
needed. After approval or autonomous selection, hand the planned waves to the
main orchestrator; update checkboxes only after each ticket's required checks
pass, and retain atomic commits. Publishing tickets externally is a separate
authorized action.
