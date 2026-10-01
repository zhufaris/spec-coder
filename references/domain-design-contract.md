# Domain Design Contract

Carry one scenario-driven design through specification, tickets, implementation, and delivery. DDD clarifies meaning, rules, and ownership; Clean Architecture clarifies module interfaces and source dependency direction. Apply both while synthesizing and slicing, rather than treating architecture as a completed preliminary checklist.

This reference adapts the existing upstream templates inside spec-coder. Keep the workflow contract's stages, artifact locations, and three approval gates. The approved specification is the design authority; tickets reference their relevant decisions instead of maintaining another copy of the model.

## Scale to the observed problem

- For a small change, use a short description of behavior, affected ownership/interface, and verification. Do not require identifiers, a glossary, or architecture layers without a need.
- For multiple interacting rules, give scenarios, invariants, and architecture decisions stable references such as `SCN-1`, `INV-1`, and `ARCH-1`, or unambiguous section anchors. Preserve references during decomposition.
- For multiple business contexts or external systems, record state ownership, interaction data, consistency expectations, and failure/recovery semantics. An unresolved load-bearing decision is a question for design, not an implementation default.
- Introduce aggregates, ports, adapters, and domain events only where actual constraints justify them. Reuse existing modules and public seams; no fixed four-layer directory structure is required.

## Design content and specification mapping

In `design-coder`, start from concrete success, rejection, and relevant retry scenarios. Work out their domain rules and architecture together. Distinguish confirmed decisions, evidence from existing code, and unresolved questions.

Use the existing `to-spec` headings. Put the following content in their indicated sections; a small task can express several rows in one paragraph.

| Design content | Placement in the upstream specification | Preserve |
| --- | --- | --- |
| User scenarios | User Stories; Implementation Decisions / Behavior & Failure Modes | Triggers, observable outcomes, rejection and relevant retry behavior |
| Domain model | Implementation Decisions / Domain Model | Canonical terms, invariants, state/transition ownership and consistency boundaries |
| Architecture | Implementation Decisions / Architecture | Module responsibilities, public interfaces, source dependency direction and boundary data |
| Verification | Testing Decisions | Scenario/invariant to public test seam; separate evidence for dependency rules |
| Limits and unresolved decisions | Out of Scope; Further Notes | Explicit exclusions, open questions, and the decisions they block |

Record an interface's preconditions, outputs, and failure semantics, not just a method name. Describe architecture by module responsibility rather than a list of directories. Runtime calls may go out to an adapter while source dependencies point toward an internally owned interface.

Before Gate 2, reconcile every relevant approved scenario, invariant, ownership decision, dependency rule, and testing seam with its specification location. Fix omissions. If synthesis reveals a new business or architecture decision, return to `design-coder` and reopen the affected gate; `to-spec` must not invent it. Ordinary wording corrections do not create a new design gate.

## Ticket decomposition

Use `to-tickets` to select the smallest independently verifiable business capability or use-case increment. Each ticket fits one agent context window; this is a sizing limit, not a requirement to stay in one DDD bounded context.

Within the existing ticket format, retain these fields (combine them for small tasks):

| Field | Required content |
| --- | --- |
| What to build | User-observable outcome and explicit scope |
| Spec references | Relevant scenarios, invariants, and architecture decisions; anchors or concise descriptions are enough |
| Ownership and implementation path | Responsible modules/contexts, necessary interfaces, allowed boundary data and failure semantics, referencing the spec |
| Acceptance criteria and verification | Success/rejection/retry examples as applicable, public test seams, and dependency checks relevant to this slice |
| Blocked by | Only tickets that supply a genuinely required capability or agreed interface; otherwise None |

Walk the use case across the necessary implementation parts. Do not create one ticket for all entities, another for all use cases, and another for all adapters. The first business slice introduces only the supporting abstractions it needs. A prerequisite refactor is separate only if necessary for independently green delivery, with its preservation checks explained. Retain upstream expand-contract handling for wide mechanical migrations.

A ticket may span business contexts when it is a coherent verifiable increment and the specification defines each participant's ownership, interaction contract, consistency, and failure behavior. Split only where increments remain independently meaningful; do not mandate a separate orchestration ticket.

Before Gate 3, check coverage in both directions: every in-scope scenario and invariant has a responsible ticket, and each ticket traces to approved behavior and architecture constraints. Check real blocking edges and testability. Never label a ticket implementation-ready while its load-bearing decisions remain open. Return to design for changed assumptions or to specification synthesis for omissions; ordinary ticket sizing changes remain in planning. Add these checks to the existing gate, not another approval round.

## Implementation and delivery

In `tdd-coder`, resolve a ticket's spec references before writing Red. Translate its applicable scenarios and invariants into behavior tests at approved public seams; keep the responsible module's rules and source dependency constraints visible during Green. A dangling reference or missing behavioral decision must be resolved before implementation.

Behavior tests establish outcomes, not source dependency direction. Use existing import/lint/architecture checks when available; otherwise record a concrete dependency review with module/import evidence. Do not introduce test-only ports just to make a layer diagram look complete.

For behavior-preserving refactors or dependency-only repairs, use `tdd-coder`'s structural verification path: preserve green behavior checks and verify the structural change with a failing-to-passing dependency check or concrete before/after source review. Mixed tickets still require behavior Red-Green for changed outcomes. No business-test failure is required for an unchanged business outcome.

In `delivery-coder`, map each in-scope scenario/invariant to completed tickets and actual test evidence. Verify architecture decisions separately against dependency checks or documented source review. Checked plan boxes alone are insufficient. Missing implementation returns to ticket TDD; missing or invalidated design returns to the relevant design/specification gate.

## Example: cancel an order

Given an approved cancellation/refund contract: Orders owns cancellation, Payments owns refunds; shipped orders refuse cancellation (`INV-1`), duplicates produce no extra refund (`INV-2`), and Order domain code cannot import the payment SDK (`ARCH-1`).

A cancellation ticket references these decisions, records the path from the existing cancellation use case through Order and the approved refund interface, and tests observable success, shipped refusal, and duplicate behavior at the appropriate public seams. The payment adapter implements the external SDK interaction. Delivery checks the SDK import rule separately from the behavior tests.

If the design has not decided delivery guarantees or retry ownership between Orders and Payments, record the gap and return to design before finalizing affected tickets. The invariant alone does not choose a queue, an outbox, a transaction strategy, or a deduplication owner.
