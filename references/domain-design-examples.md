# Domain Design Examples

Use these examples to apply the [domain design contract](./domain-design-contract.md). They illustrate decisions; do not copy their models or mechanisms into a project without evidence.

## Contents

- [Context map and local models](#context-map-and-local-models)
- [Rule placement and services](#rule-placement-and-services)
- [Invitation actions, values and policies](#invitation-actions-values-and-policies)
- [Concurrent cancellation and shipment](#concurrent-cancellation-and-shipment)
- [Refund timeouts and duplicates](#refund-timeouts-and-duplicates)
- [Dependencies and boundary data](#dependencies-and-boundary-data)
- [Small changes and queries](#small-changes-and-queries)
- [From decisions to a ticket](#from-decisions-to-a-ticket)

## Context map and local models

Suppose evidence shows Ordering owns fulfilment decisions and Billing owns payment/refund records. A monolith can contain both contexts. State whether each name and relationship is observed, proposed, or unresolved.

```text
Ordering                                  Billing
Order cancellation                        Refund settlement
      |                                         |
      +-- refund request (approved contract) --->+
      +<-- outcome (approved contract) -----------+
```

The arrows say nothing about HTTP versus events. Delivery guarantees and recovery must be decided separately. "Cancelled" in Ordering need not mean "refunded" in Billing.

An example model description, conditional on the business rules:

| Context | Relevant model | Responsibility |
| --- | --- | --- |
| Ordering | Order entity and aggregate root; OrderLine entities if line identity matters | Maintain shipment/cancellation exclusion and any approved line invariants |
| Ordering | Address value object, if needed by the scenario | Validate and compare address values; omit for a cancellation-only change if irrelevant |
| Ordering | CancelOrder application use case | Coordinate loading, domain behavior, conditional persistence and the agreed refund interaction |
| Billing | Refund entity/root, if refunds have independent identity and lifecycle | Track the approved refund state transitions and amount rules |
| Billing | Money value object | Amount/currency validity and value equality |
| Billing | RequestRefund application use case and provider adapter | Coordinate domain decisions and provider protocol conversion |

For each aggregate, explain which invariants require atomic consistency. Do not infer that every line, shipment, payment and refund belongs to one aggregate because database joins connect them. A foreign ID is a relationship, not permission to mutate another context's entity. Explain identifier mappings and translation at the consumer's integration seam.

If a term differs between observed code and the approved model, retain that distinction and scope the needed migration. Do not label all historical table names as the new ubiquitous language.

## Rule placement and services

For a rule owned by an order, an operation such as `Order.cancel()` or a domain function over an order can decide whether cancellation is legal. An HTTP controller and a worker invoke that same behavior through their use case. A shared rule should not be duplicated in both entry points.

The CancelOrder application use case coordinates loading, the domain operation, the transaction and the approved interaction with Billing. It does not reproduce the eligibility policy. A payment adapter converts internal requests/results to and from a provider's protocol.

A domain service is warranted when a named domain operation does not naturally belong to a single entity/value object: for example, an approved refund-allocation policy across payment allocations. Describe its rule, input and output before creating it. Do not introduce `OrderService` merely to move all behavior off Order, or assume every application use case needs a matching domain service.

## Invitation actions, values and policies

Suppose the approved rules say only the recipient can accept a pending, unexpired workspace invitation; refusal leaves it unchanged. Extract the business verb **accept**, states **pending/accepted/revoked**, recipient role and expiry constraint. An invitation's "active" means pending and unexpired; Billing's "active subscription" means paid. Preserve those context-specific meanings, not a shared `is_active` policy.

An `Invitation.accept(actor, now, eligibility)` operation, or an equivalent domain function, protects the transition. HTTP and the batch job use the same rule. A generic `update_status` that can still write `accepted` directly is a bypass, even if the new method has good tests. Restrict that entry path or route its applicable behavior through the approved operation, accounting for existing callers.

If the domain explicitly defines EmailAddress equality as case-sensitive in the local part and case-insensitive in the domain, normalization must preserve that distinction. Trim surrounding whitespace if approved, reject embedded whitespace, and expose an immutable valid value. Do not infer lowercasing the whole address or recipient identity from email equality. Identity matching remains a separate supplied rule.

If workspace-plan eligibility varies independently and is reused by preview and acceptance, name an eligibility policy and define its result and how the operation enforces it. Keep a simple expiry predicate with the invitation unless it has its own reason to vary. The policy is not a spec-coder specification document. If plan eligibility rules are missing, identify that gap and affected readiness instead of inventing a permission rule.

Keep existing public `status` fields/values when compatibility is required; internal vocabulary can improve through explicit mapping. Verify the domain operation's allowed/rejected transitions, value equality/normalization, relevant bypass paths, and preview/execution consistency at the agreed interfaces. A spec preserves these decisions and compatibility limits; a vertical acceptance ticket references them and includes the rejection/bypass evidence, rather than merely requesting an Invitation class.

## Concurrent cancellation and shipment

Invariant: an order cannot be both shipped and cancelled. Sequential checks in two handlers can both read an unshipped order and both succeed.

If the approved persistence design uses optimistic versions, both operations must participate in conditional updates. On conflict, define whether the use case reloads and re-evaluates, rejects, or retries under a bounded policy. Versioning is one option, not a universal requirement; locking or an atomic state transition may fit another repository.

Test the approved interleaving: two operations read the same version, one wins, the other cannot commit an incompatible transition. Verify the losing observable result and persisted outcome through agreed test seams. A fake that serializes every request cannot establish the production concurrency guarantee; use the appropriate existing adapter/integration seam for the atomicity mechanism.

The domain owns the rule; the application/persistence collaboration enforces the selected concurrency guarantee. A domain method's precondition alone is insufficient.

## Refund timeouts and duplicates

Suppose cancellation commits but the refund provider times out after possibly accepting the request. Repeating an unkeyed provider call can create a second refund even if local request handling is deduplicated.

Before implementation, decide:

- Which participant owns the operation identity and duplicate response?
- How is that identity retained and passed across retries? What guarantees does the provider actually offer?
- What does the caller see while the result is uncertain, and who reconciles it?
- What is retriable, terminal, or compensatable under the business contract?

Record unresolved answers and affected tickets. Do not select a queue/outbox/saga to fill a gap in business semantics. A local domain event does not automatically become a durable, versioned integration event.

## Dependencies and boundary data

An illustrative source dependency rule:

```text
HTTP / worker --> application --> domain
provider adapter --> internally owned refund interface
composition module --> concrete adapters + application
```

The application can call an injected provider adapter at runtime without importing that concrete adapter in its policy. Define the interface around the consumer's required operation and errors, using existing seams where possible.

| Symptom | Evidence and correction to investigate |
| --- | --- |
| Order accepts an ORM session | Persistence lifetime and types have reached the domain; inspect the signature and move persistence coordination to the approved module |
| A use case constructs a payment SDK client | Concrete dependency assembly is mixed with policy; inspect construction/imports and assemble at the appropriate outer module |
| Internal result is the provider's response object | Inspect type and error leakage; translate to the approved internal result where the protocol is adapted |
| HTTP and worker duplicate eligibility predicates | Identify the authoritative domain rule and make both paths use it; verify each relevant entry path |
| Every class gains a matching interface | Identify the actual seam and protected responsibility; remove unjustified pass-through abstractions |

Green business tests do not prove these dependency rules. Use existing architecture/import tooling or record before/after source evidence including exposed types and assembly. For a structural-only repair, preserve behavior checks; do not manufacture a failing business outcome.

## Small changes and queries

A display-label correction can say: "Update the order-history label in its existing view; no domain state, model or interface changes; verify rendered wording." It needs no new context, aggregate or port.

A read-only order summary may use an existing authorized query module returning a projection. Explain access/tenant filtering and applicable business constraints. Do not force aggregate loading merely because the write path uses one, and do not bypass authorization under the label of a projection.

## From decisions to a ticket

After the above contracts are approved, a cancellation capability ticket references the applicable scenarios, invariants, context/model responsibilities, conditional-write interface and refund contract. Its acceptance covers the approved successful, rejected, concurrent and duplicate outcomes, plus relevant architecture evidence.

It introduces only supporting abstractions needed by that increment. Avoid separate tickets for "all entities", "all services" and "all repositories". A ticket may cross Ordering and Billing if the interaction is decided and the increment is independently verifiable. It must not be marked ready while refund timeout recovery or another required decision is unresolved.
