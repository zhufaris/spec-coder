# Domain Design Application Scenarios

Use these read-only simulations to evaluate skill behavior. Contract tests check link integrity and packaged references; they do not prove an agent preserves design meaning. Load the four design/planning/implementation/delivery wrappers and their shared references. Keep local design notes out of the evaluator's input.

## Cancellation with missing delivery semantics

Input: Orders owns cancellation/shipment; Payments owns refunds. A customer can cancel an unshipped paid order. A shipped order refuses with unchanged state. Repeated cancellation creates no duplicate refund. Order domain code cannot import the payment SDK. Existing seams are the cancellation use case and refund adapter. Produce a compact spec and two or three tickets under time pressure. The delivery/retry contract between Orders and Payments has not been decided.

Expected application:
- Map scenario, invariants, ownership and dependency constraints into Implementation Decisions; keep test seams and dependency evidence in Testing Decisions.
- Preserve references from specification to tickets; do not silently assign idempotency or retry ownership based only on the invariant.
- Identify missing delivery semantics and return affected decisions to design; do not call dependent tickets implementation-ready.
- Separate SDK import evidence from outcome tests.

## Fully defined interaction across contexts

Input: An approved specification defines the same cancellation scenario, including participant ownership, interaction data, consistency expectations and failure/recovery semantics. The complete change fits one agent context window and is independently verifiable. Propose a ticket shape.

Expected application:
- A coherent ticket may cross the Orders and Payments contexts and carry both participants' contracts.
- Do not interpret one agent context window as one DDD bounded context.
- Do not require a separate orchestration ticket or a ticket for every architecture layer.

## Pressure to split by layers

Input: A proposed plan has tickets for all entities, all use cases, all repositories and all adapters. No independently verifiable capability is delivered until the final ticket. Convert it into a useful plan.

Expected application:
- Slice by a business capability or use-case increment, including only the supporting abstractions it needs.
- Each blocker supplies a real prerequisite. A separate prefactor requires a reason and preservation checks.
- Use the upstream expand-contract exception only for an actual wide mechanical migration.

## Small display-label correction

Input: One existing view shows the wrong label. No business rules or interfaces change. Apply the workflow at appropriate scale.

Expected application:
- Short behavior, affected module and verification descriptions are sufficient.
- Do not invent a bounded context, aggregate, port, glossary or stable IDs.
- Apply existing gates; do not introduce extra approval rounds for the continuity checks.

## Dangling invariant reference at implementation

Input: A ready ticket cites INV-4, but that invariant is absent from the approved specification. The current acceptance test passes and the ticket is urgent.

Expected application:
- Resolve the reference and missing decision before implementing or checking off the ticket.
- A design change returns to design, a specification omission to synthesis, and an ordinary implementation defect to the current ticket's TDD.

## Green behavior tests with an architecture violation

Input: All cancellation tests pass, but the Order domain imports the payment SDK despite an approved prohibition.

Expected application:
- Delivery reports the unmet architecture decision; plan checkboxes and green behavior tests do not establish compliance.
- Repair under the existing TDD/review loop and record dependency-tool or module/import review evidence.
- For a dependency-only repair, preserve green behavior checks and show the failing dependency check turn green, or record concrete before/after import review when no tooling exists. Do not demand an artificial business-test failure. If outcomes also change, use behavior Red-Green for those outcomes.
