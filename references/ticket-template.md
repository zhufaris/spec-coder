# Local Vertical-Ticket Template

This is a spec-coder resource used directly by `plan-coder` after specification approval. Decompose the approved specification into a local plan at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`. Apply the [domain design contract](./domain-design-contract.md); do not require an external planning skill or issue tracker.

## Plan structure

Reference the approved specification and selected workspace, record the starting revision/baseline and approval status, then list tickets and final delivery checks. Use stable ticket IDs and one completion checkbox per ticket as the authoritative progress record. The runtime plan mirrors those checkboxes with **one active execution wave** at most; wave membership and Host handles remain conversational and are reconstructed from unchecked tickets plus committed Git on resume.

For each ticket, include:

| Field | Content |
| --- | --- |
| Title and completion checkbox | A concise delivered capability, e.g. `- [ ] T1: Cancel an eligible order` |
| What to build | Observable outcome and scope; a complete path through only the necessary modules |
| Spec references | Approved scenarios, invariants and architecture decisions this ticket implements |
| Dependencies | IDs of tickets that supply a genuinely required capability or contract; otherwise None |
| Delegation eligibility | Grounded inputs, bounded/reversible scope, independently inspectable seam, and any main-only authority or credential that makes the ticket ineligible |
| Delegation mode | Default direct worker, main-local, required delegation, or an applicable request/ticket opt-out, including the reason |
| Ownership and implementation path | Relevant contexts/model elements, enforcing modules, interfaces, allowed boundary data and consistency/failure constraints; reference rather than copy the model |
| Mutation ownership | Exact allowed files/modules and the result-transfer boundary |
| Exclusions | Files, responsibilities, authority, and unrelated changes outside the ticket |
| Isolation | Whether mutation is read-only, serial/shared, or requires real per-worker Host/task or Git isolation, including the wave base when applicable |
| Concurrency conflicts | Known ownership overlap, semantic conflicts, and tickets that cannot share a parallel wave |
| Verification seam | Independently inspectable focused evidence plus affected checks and separate dependency/preservation evidence |
| Host capacity | Capacity assumptions for delegation; live capacity is rechecked when a wave is formed rather than persisted as fact |
| Direct-child boundary | Every child brief states `delegation_allowed = false`; children do not spawn directly or indirectly, stage, or commit. Require the shared Worker Progress Heartbeat / `ProgressSnapshot` when proactive messaging is available: start, every 45-60 seconds while active, phase change, before/after a long command, and blocker/failure/completion. `heartbeat-capability-unavailable` preserves delegation; `heartbeat-overdue` or a wait timeout means no message only and never grants failure, blocker, interrupt, takeover, promotion, or local fallback authority. Completion authority remains main-only. |
| Acceptance criteria and verification | Applicable success/rejection/concurrency/duplicate/recovery outcomes and the verification seam used to prove them |
| Blocked by | IDs of tickets that supply a genuinely required capability or contract; otherwise None |

These fields are scheduling inputs, not a production scheduler or a persisted
workflow aggregate. A general `ExecutionWave` contains currently
dependency-ready work and may be a one-ticket main-local wave. Delegated wave
selection considers only delegation-eligible, ownership-safe tickets, is capped
by live Host capacity and the suite wave limit, and requires real isolation for
every mutating worker when parallel. Without real isolation, use serialized
direct workers. A main-local ticket never overlaps delegated mutation.

For relevant domain changes, references and acceptance preserve the approved business actions, refusal/bypass outcomes, value validity/equality, policy responsibilities and terminology compatibility. When persistence is affected, include aggregate save/load, controlled restoration, post-load behavior and applicable conflict verification. Keep these requirements within the capability slice, rather than separate tickets for model classes or a copied domain inventory.

## Slicing rules

- Keep each increment independently meaningful and verifiable within one agent context window. A business bounded context is not an agent context window.
- Slice by business capability or use-case increment. Introduce only supporting entities, services and adapters needed for that increment; do not create separate "all entities", "all services" and "all repositories" tickets.
- Preserve all guarantees needed for the slice to be correct. A happy-path ticket cannot postpone required concurrency or recovery behavior and still count as a complete capability. Combine work or choose a different boundary when necessary.
- A cross-context ticket is valid when participant ownership, interaction data, consistency and failure behavior are decided and the result is independently verifiable.
- Separate a prerequisite refactor only when it enables independently green delivery; describe unchanged outcomes and preservation evidence. For a wide mechanical migration, consider expand, migrate and contract steps that each retain passing checks. If safe increments cannot be found, revisit the design or plan an appropriately sized indivisible change; do not promise knowingly failing intermediate commits.
- Add only real blocking edges. Shared files or preferred execution order alone are not functional dependencies. Check for cycles and references to missing ticket IDs.

## Gate 3 review

Check coverage in both directions: every in-scope scenario/invariant has a responsible ticket, and every ticket traces to approved behavior and architecture. Resolve invalid blockers, excessive size and missing verification. Check every ticket's delegation eligibility and mode, mutation ownership and exclusions, dependencies, isolation need, concurrency conflicts, verification seam, Host-capacity requirement, real-isolation requirement, and `delegation_allowed = false` child boundary. Name unresolved load-bearing decisions and affected tickets; do not mark them implementation-ready. Independent approved slices need not wait on unrelated open decisions.

For every delegated ticket, the direct-child brief also references the shared
Worker Progress Heartbeat / `ProgressSnapshot` contract. It requires the
reporting schedule above only when proactive child-to-main messaging is
available; it does not promise a Host implementation. Heartbeat snapshots are
transient observation evidence, so their absence cannot update durable plan
state or transfer any main-only completion, diff, or verification authority.

Present the ticket set, deliverables, dependencies, and proposed wave shape for approval and implementation authorization. Adjust granularity within the approved design when needed. After approval, hand the dependency and wave inputs to the main orchestrator; update checkboxes only after each ticket's required checks pass, and retain atomic commits. Publishing tickets externally is a separate authorized action.
