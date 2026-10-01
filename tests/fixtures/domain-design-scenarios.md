# Domain Design Application Scenarios

Use these read-only simulations to evaluate skill behavior. Contract tests check link integrity and packaged references; they do not prove an agent preserves design meaning. Load the relevant discovery/design/planning/implementation/delivery wrappers and their shared references. Give evaluators only the task input and skill artifacts, not this file's expected application or local design notes. Keep evaluation evidence in the local plan.

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

## Concurrent cancellation and shipment

Input: In a monolith, Ordering owns order shipment/cancellation; Billing owns payments and refunds. HTTP and a worker can both cancel an order. Ordering cancellation and Billing refund completion have different meanings. Existing persistence uses optimistic row versions. Cancellation and shipment can race. Sketch the affected context models and verification. Refund timeout recovery/deduplication ownership has not been decided.

Expected application:
- Explain affected contexts and local models, identity/lifecycle and justified aggregate boundaries, without turning contexts into mandatory services or inventories of every table.
- Identify one authoritative rule shared by the entry points, distinguish domain behavior from application coordination and adapter conversion.
- Explain that both transitions must participate in the approved atomic/conflict mechanism, define losing outcomes and test the actual relevant interleaving.
- Preserve uncertainty about refund recovery; distinguish observed version columns from a proposed use of them and return unresolved business decisions to design.

## Provider accepts a repeated refund

Input: The provider may accept a refund then time out. The local HTTP handler deduplicates requests in memory, but a worker retries after process restart. Propose the necessary specification content.

Expected application:
- Identify operation identity, durable deduplication and retention, ownership across local/provider retries, uncertain state, reconciliation and caller-visible results as decisions to settle.
- Do not claim exactly-once effects from local deduplication or infer a queue/outbox as the answer.

## Distinguish domain and application services

Input: A proposed design uses an Order record, an OrderService containing all eligibility rules and database operations, and controllers/workers that copy the eligibility predicate. Explain an appropriate model for a nontrivial cancellation rule.

Expected application:
- Put authoritative behavior in an appropriate domain module, allowing entity methods or domain functions rather than mandating classes.
- Reserve domain services for named operations not naturally owned by an entity/value object; distinguish use-case orchestration and persistence/provider adapters.
- Verify relevant entry paths use the shared rule.

## Types leak despite clean import layout

Input: The domain package has no direct infrastructure import, but Order.cancel accepts an ORM session and returns an SDK response passed in by an application module. Behavior tests are green. Review it against an approved ban on infrastructure semantics in domain interfaces.

Expected application:
- Inspect exposed types and semantics as well as direct imports; identify actual leakage and the responsible conversion/coordination seams.
- Require separate structural evidence while preserving green behavior; do not accept folder naming as proof.

## Authorized read projection

Input: A tenant-scoped order-history query already enforces authorization in its query module and returns a summary projection. A proposal would hydrate every Order aggregate and add a repository interface solely to follow four layers. Evaluate it.

Expected application:
- Allow the existing projection if it preserves required access and business constraints.
- Reject unjustified hydration/interfaces without dismissing tenant and authorization rules.

## Existing model conflicts with target

Input: Legacy code has a shared mutable Customer ORM object used by Billing and Support. Their definitions of active customer differ. The approved task only changes Support's eligibility display, and the developer proposes a system-wide split into microservices. Describe scope and model evidence.

Expected application:
- Separate observed storage/model coupling from proposed bounded-context semantics.
- Explain local language and affected ownership/translation; scope any necessary migration to the feature and surface unresolved contract choices.
- Do not endorse leakage as target architecture or prescribe a whole-system deployment redesign.

## Invitation language, actions and policies

Input (use this text verbatim; provide only it and the skill/reference artifacts to the evaluator):

```text
Use the supplied domain-design-contract and worked examples to propose a compact model, public operations and verification for this change; state what an eventual specification and vertical ticket must preserve. Return advice only; do not edit project files.

A workspace Invitation has an ID, recipient identity, workspace ID, expires_at and status pending/accepted/revoked. Only its recipient may accept a pending invitation before expires_at; all refusals leave state unchanged. Both HTTP and a batch job accept invitations. The existing shared update_status(id, status) writes any state with no business checks. Code calls an invitation active when pending and unexpired; Billing calls a subscription active when paid. Public clients already use the invitation status field and must remain compatible. The invitation contains a recipient EmailAddress with case-sensitive local part and case-insensitive domain; whitespace around input is trimmed, embedded whitespace is invalid. A separate eligibility decision varies by workspace plan and is reused by acceptance and preview; the simple expiry check is not independently variable. The team's proposed design calls both rules Specification and renames the public status values immediately. Explain choices and unresolved points using these facts, without inventing a new business rule.
```

Expected application:
- Distinguish Invitation activity from Billing activity and preserve public status compatibility. Identify undefined plan eligibility rules and affected decisions.
- Use a shared protected acceptance operation for HTTP and batch; identify the unrestricted update bypass and unchanged state on refusal.
- Explain immutable EmailAddress construction, approved normalization/equality and the distinction from recipient identity.
- Justify the shared variable eligibility policy, retain simple expiry with its owner, and distinguish DDD Specification from the workflow document.
- Carry these constraints into specification and vertical-ticket acceptance without inventing the missing policy rules.

## Aggregate persistence and post-load behavior

Input (use this text verbatim; provide only it and the skill/reference artifacts to the evaluator):

```text
Use the supplied domain-design-contract and worked examples to propose a compact model and verification strategy; state what a specification and vertical ticket must preserve. Return advice only; do not edit project files.

An Order has identity, lines and a Money total (amount and currency). Cancel is allowed only before shipment; a cancelled order refuses shipment. The approved persistence mechanism uses optimistic versions for competing cancellation and shipment. The adapter has save(order) and load(id); its current mapper restores total as a decimal without currency, discards the version, and attaches publicly mutable line objects. Current tests check only saved ID and numeric amount using an in-memory fake. Loading a cancelled order then calling ship must still refuse. Existing integration tests can use the actual database adapter in an isolated transaction. A developer proposes putting payment/refund/provider history into the Order aggregate because tables join, adding repositories per table, and reconstructing by replaying public business commands. Identify responsibilities, necessary verification and decisions still missing.
```

Expected application:
- Keep the aggregate boundary justified by invariants, protect child mutations and reject repositories per table.
- Identify lost Money currency and version as semantic defects; preserve intrinsic validity, identity and state, using controlled reconstitution without replaying business commands.
- Use the existing real adapter to verify round trips and post-load shipping refusal; separately verify approved version conflicts and losing outcomes.
- Identify missing conflict response, historical currency/version data or migration decisions instead of inventing defaults.
- Carry restoration and mapping checks into specification/ticket acceptance and preserve separate architecture evidence.

## Normalized saved-search name without extra models

Input (use this text verbatim; provide only it and the skill/reference artifacts to the evaluator):

```text
Use the supplied domain-design-contract and worked examples to propose a compact design and a candidate vertical ticket. Return advice only; do not edit project files.

An existing tenant-scoped saved-search screen can rename a search and list names. A name must be nonempty after trimming and at most 80 characters. Existing query and update modules already enforce authentication, tenant ownership and those validations. The requested change is to trim surrounding whitespace before applying the existing checks and show the normalized name. No lifecycle, cross-context interaction, competing business rules or concurrent-write guarantee changes are requested. A proposal adds SavedSearchAggregate, SearchNamePolicy, a new repository interface, domain events and four mandatory layers. Give a proportionate implementation and verification plan using existing seams.
```

Expected application:
- Reuse existing update/query seams, normalize before the existing nonempty/80-character checks, and display the persisted normalized result.
- Preserve authentication/tenant checks and unchanged state on invalid input.
- Reject unjustified aggregate, policy, repository, event and four-layer additions.
- Keep the specification and vertical ticket compact, with observable acceptance and the same workflow approval gates.

## Transfer to dispatch manifest planning

Input (use this text verbatim; give only it and the named references/templates, not this rubric or other evaluation artifacts):

```text
Use the supplied domain-design-contract, examples and native specification/ticket templates to draft concise specification sections and one candidate vertical ticket for these confirmed design decisions. This is an advice exercise; do not modify a repository or treat the candidate as approved for implementation.

A dispatch Manifest owns sealing, with immutable Weight(amount, unit) values that compare by both fields; allowed units are kg and lb, and amounts must be positive. No unit conversion is approved. Only an open manifest may be sealed by its assigned dispatcher. The destination-specific capacity policy is independently variable and reused by a preview; its existing implementation is authoritative. Failed sealing leaves the manifest open. HTTP and a scheduled job must use the same sealing rules. Dispatch calls a manifest ready when open with complete items; Compliance calls a permit ready when approved. External clients must keep their current ready/status fields. A generic patch handler can write sealed directly. Persistence currently restores weights as bare numbers and exposes the items list for direct mutation. The approved design routes writes through protected root operations, uses a repository returning manifest plus optimistic version, and rejects stale saves without retry; existing database adapter tests provide isolated transactions. Loading historical sealed manifests must not rerun seal or create new notifications. Your output should carry the supplied decisions into model/architecture/verification sections and candidate ticket acceptance; do not invent capacity rules or permission semantics beyond the supplied decisions.
```

Expected application:
- Preserve local meanings and public compatibility; prevent patch/child mutation bypasses through the supplied root operations.
- Preserve immutable Weight identity-by-value without inventing conversions or inferring that bare numbers contain units.
- Keep capacity policy authoritative and shared while leaving lifecycle/actor guards with the manifest operation.
- Specify controlled restoration with no new notifications, version-envelope conditional save, stale rejection and actual adapter round-trip/post-load behavior checks.
- Carry these decisions through specification sections and a candidate vertical ticket, name any missing storage-data decision, and do not claim implementation approval or executed tests.
