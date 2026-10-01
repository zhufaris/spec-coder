# Local Vertical-Ticket Template

This is a spec-coder resource used directly by `plan-coder` after specification approval. Decompose the approved specification into a local plan at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`. Apply the [domain design contract](./domain-design-contract.md); do not require an external planning skill or issue tracker.

## Plan structure

Reference the approved specification and selected workspace, record the starting revision/baseline and approval status, then list tickets and final delivery checks. Use stable ticket IDs and one completion checkbox per ticket as the authoritative progress record. The runtime plan mirrors those checkboxes with at most one active ticket.

For each ticket, include:

| Field | Content |
| --- | --- |
| Title and completion checkbox | A concise delivered capability, e.g. `- [ ] T1: Cancel an eligible order` |
| What to build | Observable outcome and scope; a complete path through only the necessary modules |
| Spec references | Approved scenarios, invariants and architecture decisions this ticket implements |
| Ownership and implementation path | Relevant contexts/model elements, enforcing modules, interfaces, allowed boundary data and consistency/failure constraints; reference rather than copy the model |
| Acceptance criteria and verification | Applicable success/rejection/concurrency/duplicate/recovery outcomes, approved public test seams, affected checks and separate dependency evidence |
| Blocked by | IDs of tickets that supply a genuinely required capability or contract; otherwise None |

For relevant domain changes, references and acceptance preserve the approved business actions, refusal/bypass outcomes, value validity/equality, policy responsibilities and terminology compatibility. Keep these requirements within the capability slice, rather than separate tickets for model classes or a copied domain inventory.

## Slicing rules

- Keep each increment independently meaningful and verifiable within one agent context window. A business bounded context is not an agent context window.
- Slice by business capability or use-case increment. Introduce only supporting entities, services and adapters needed for that increment; do not create separate "all entities", "all services" and "all repositories" tickets.
- Preserve all guarantees needed for the slice to be correct. A happy-path ticket cannot postpone required concurrency or recovery behavior and still count as a complete capability. Combine work or choose a different boundary when necessary.
- A cross-context ticket is valid when participant ownership, interaction data, consistency and failure behavior are decided and the result is independently verifiable.
- Separate a prerequisite refactor only when it enables independently green delivery; describe unchanged outcomes and preservation evidence. For a wide mechanical migration, consider expand, migrate and contract steps that each retain passing checks. If safe increments cannot be found, revisit the design or plan an appropriately sized indivisible change; do not promise knowingly failing intermediate commits.
- Add only real blocking edges. Shared files or preferred execution order alone are not functional dependencies. Check for cycles and references to missing ticket IDs.

## Gate 3 review

Check coverage in both directions: every in-scope scenario/invariant has a responsible ticket, and every ticket traces to approved behavior and architecture. Resolve invalid blockers, excessive size and missing verification. Name unresolved load-bearing decisions and affected tickets; do not mark them implementation-ready. Independent approved slices need not wait on unrelated open decisions.

Present the ticket set, deliverables and dependencies for approval and implementation authorization. Adjust granularity within the approved design when needed. Hand the first approved unblocked ticket to `tdd-coder`; update checkboxes only after its required checks pass, and retain atomic commits. Publishing tickets externally is a separate authorized action.
