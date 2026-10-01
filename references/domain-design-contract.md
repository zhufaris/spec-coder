# Domain Design Contract

Carry one scenario-driven design through specification, tickets, implementation, and delivery. DDD clarifies meaning, rules, and ownership; Clean Architecture clarifies module interfaces and source dependency direction. Apply both while synthesizing and slicing, rather than treating architecture as a completed preliminary checklist.

This reference governs spec-coder's native planning templates. Keep the workflow contract's stages, artifact locations, and three approval gates. The approved specification is the design authority; tickets reference their relevant decisions instead of maintaining another copy of the model.

## Contents

- [Scale to the observed problem](#scale-to-the-observed-problem)
- [Discover and evolve domain language](#discover-and-evolve-domain-language)
- [Bounded contexts and their models](#bounded-contexts-and-their-models)
- [Protect behavior and valid values](#protect-behavior-and-valid-values)
- [Consistency and interaction contracts](#consistency-and-interaction-contracts)
- [Architecture that can be verified](#architecture-that-can-be-verified)
- [Design content and specification mapping](#design-content-and-specification-mapping)
- [Ticket decomposition](#ticket-decomposition)
- [Implementation and delivery](#implementation-and-delivery)

## Scale to the observed problem

Inspect evidence before selecting modeling depth. Explain which triggers apply; they can overlap. Use a short paragraph for a small change. Do not require identifiers, a glossary, entities, services, or architecture layers merely to fill a template.

| Observed trigger | Required decisions |
| --- | --- |
| Simple CRUD, field or display change | Business meaning, responsible module, input constraints, observable result and verification |
| Interacting rules or significant state transitions | Invariants, enforcing model, state ownership, allowed and rejected transitions |
| Concurrent writes or repeated requests | Atomicity/conflict mechanism, idempotency identity and owner, losing/duplicate outcome |
| Multiple business contexts or external semantics | Context map, local models, translation, interaction data, consistency and recovery responsibilities |
| Framework, persistence or SDK coupling | Interface ownership, source dependencies, data conversion and concrete dependency assembly |

Give interacting scenarios, invariants, and architecture decisions stable references such as `SCN-1`, `INV-1`, and `ARCH-1`, or unambiguous section anchors. Preserve them during decomposition. Read the [worked examples](./domain-design-examples.md) when applying a trigger or resolving ambiguous model/service responsibilities.

## Discover and evolve domain language

Extract nouns, business actions, states, roles and constraints from requirements, tests, API/UI behavior and existing code. Use domain-expert meaning and observable behavior as evidence; database names alone do not define the model. Check an existing `GLOSSARY-MAP.md` and its context glossaries when present. Record ambiguous terms and contradictions between the code and requested behavior, their context, and the decisions they affect before encoding assumptions.

Use consistent domain terms in code, tests, interfaces and user-relevant errors where they describe the same concept. The same word can mean different things in different contexts; name those meanings and any translation explicitly. Capture settled terminology through the existing glossary workflow and workspace rules; keep implementation decisions in the specification, not the glossary.

When improving a misleading name, identify affected public contracts, consumers and migration constraints. Keep public compatibility when required, with explicit boundary translation where needed. When a breaking change is approved, describe its scoped migration rather than retaining a misleading abstraction indefinitely. Do not infer permission to rename a public field or status from approval of an internal model.

## Bounded contexts and their models

Describe the affected **Bounded Contexts** and only the neighbors needed to explain interactions. A bounded context owns a coherent model and language; it is not automatically a folder, table, team, deployment unit, or microservice. Justify a boundary with differences in meaning, rules, or ownership. One context can suffice.

For an existing system, separate **observed**, **proposed**, and **unresolved** model elements using code/specification evidence. Identify contradictions and the affected decisions. Do not turn observed legacy leakage into an approved constraint or expand a local change into an unrelated redesign.

Within the existing specification, provide a compact description for each relevant context. Combine rows for small tasks; omit inapplicable constructs with a brief reason when their absence could be ambiguous.

| Model content | Explain |
| --- | --- |
| Context purpose and language | Capabilities, local term meanings, authoritative state, exclusions and relationships with neighbors |
| Entity | Business identity, lifecycle, state transitions and behavior; identity across contexts needs an explicit mapping |
| Value object | Value meaning, equality, immutability and valid construction; avoid wrapping every primitive without a domain reason |
| Aggregate and root, when needed | Root, included entities/value objects, protected invariants and consistency boundary; justify from rules that must hold together, not joins |
| Domain service, when needed | A named business operation that does not naturally belong to one entity/value object; inputs, results, rules and collaborators |
| Policy / DDD Specification, when needed | A named business decision with independent meaning, variation or reuse; inputs, result, enforcing caller and why a local condition is insufficient |
| Application service / use case | Coordination of domain operations, transactions and external interactions; reference the authoritative domain rule instead of duplicating it |
| Repositories, ports and events, when needed | The actual capability and owner they serve, contract semantics and why existing interfaces are insufficient |

Give every significant invariant an authoritative enforcing module and an observable behavior seam. Use an entity, value object, aggregate, or domain function/service as appropriate; logical roles need not become separate classes. Do not create a service per use case, a repository per table, passive records plus a generic service containing every rule, or an interface for every class. Preserve simple CRUD where there is no richer rule to model.

## Protect behavior and valid values

- Express rule-bearing changes as domain actions with preconditions, results and rejection behavior: for example, `accept_invitation` rather than unrestricted `update_status`. Entity methods or domain functions are both valid. Find all relevant entry paths, including generic updates, jobs and deserialization; renaming a method does not prevent callers from bypassing its rules. Distinguish business decisions from application coordination and adapter conversion.
- Define value-object equality and normalization from business meaning, not convenience. Keep values immutable and replace them through valid construction. Where the language permits, use types and controlled construction to make invalid states unrepresentable; otherwise enforce the equivalent invariant through the module's interface. External conversion must preserve these rules. A data wrapper without protected meaning is not useful modeling.
- Extract a policy when a decision has an independent business name, varies independently or is reused. Keep a simple condition in its natural owner when extraction adds no value. State how the authoritative operation applies the policy so preview and execution do not acquire divergent rules. A DDD Specification is a decision predicate, not the spec-coder specification document; avoid using the shared name ambiguously. Do not require a policy class hierarchy or generic rule engine.
- Name domain events after meaningful facts that have occurred. Define which successful transition produces a fact and how rejection behaves when events are part of the approved design; do not add events as generic callbacks merely because a model has state.

## Consistency and interaction contracts

- For each concurrently mutable invariant, identify the atomic operation or conflict detection mechanism, its consistency scope, and the observable losing outcome. A precondition check followed by an unprotected write cannot by itself guarantee the invariant. Test the relevant interleaving, not only sequential success.
- For repeated operations, define idempotency identity, the owning participant, the duplicate result, and relevant persistence/retention semantics. Local deduplication does not establish exactly-once external effects.
- For context interactions, identify producer/consumer, command or event meaning, boundary data, identifiers and translation ownership. Distinguish local domain events from integration events with external compatibility obligations. Do not share a mutable domain entity across contexts by default.
- Specify synchronous/asynchronous interaction and distinguish local atomicity from cross-context consistency. Cover relevant intermediate states, timeout ambiguity, retries, deduplication, reconciliation/compensation, terminal outcomes and who drives recovery.
- Choose queues, outboxes or sagas only when required guarantees and constraints justify them. An invariant does not select infrastructure. If a load-bearing decision is unresolved, identify the decision, owner if known, and affected readiness; do not guess it during specification synthesis or implementation.

## Architecture that can be verified

Define the module responsible for each rule, the public interface, allowed crossing data, actual source dependency direction, and where concrete dependencies are assembled. Runtime control flow and source dependencies can point in different directions.

- Keep business judgments in the responsible domain module; HTTP handlers, jobs and application use cases should invoke it rather than each implement the same rule. Application coordination and adapter translation remain distinct responsibilities.
- Describe required interfaces in the language of the internal consumer: inputs, outputs, preconditions, error semantics and ordering constraints. Explain who owns the interface and where an adapter satisfies it. Reuse useful seams; do not invent ports merely to complete a diagram or facilitate mocks.
- Identify where HTTP, ORM and SDK representations are converted. Check imports, exposed types, constructors and configuration requirements for external semantics leaking into core policy. A function, class or package can provide the needed module; names and folder layout do not prove dependency compliance.
- Allow read-only projections through an existing query module without loading an aggregate where appropriate; preserve authorization, tenancy and applicable business constraints. Do not route every read through a write model.
- For legacy violations, explain the specific deviation, target and migration scope. Preserve behavior during structural repairs; do not silently permit new leakage or undertake an unrelated whole-system refactor.

## Design content and specification mapping

In `design-coder`, start from concrete success, rejection, and relevant retry scenarios. Work out their domain rules and architecture together. Distinguish confirmed decisions, evidence from existing code, and unresolved questions.

Use the bundled [specification template](./specification-template.md). Put the following content in the indicated sections; a small task can express several rows in one paragraph.

| Design content | Placement in the local specification | Preserve |
| --- | --- | --- |
| User scenarios | User Stories; Implementation Decisions / Behavior & Failure Modes | Triggers, observable outcomes, rejection and relevant retry behavior |
| Domain model | Implementation Decisions / Domain Model | Affected contexts, canonical terms, actions, valid values, justified policies, enforcing owners, invariants and consistency boundaries |
| Architecture | Implementation Decisions / Architecture | Domain/application/adapter responsibilities, public interfaces, source dependency direction, assembly and boundary data |
| Verification | Testing Decisions | Scenario/invariant to public test seam; separate evidence for dependency rules |
| Limits and unresolved decisions | Out of Scope; Further Notes | Explicit exclusions, open questions, and the decisions they block |
| Language evolution | Implementation Decisions / Compatibility & Migration | Changed meanings/names, affected public consumers, compatibility constraints and approved migration scope |

Record an interface's preconditions, outputs, and failure semantics, not just a method name. Preserve applicable action/VO/policy decisions in ticket references and acceptance examples, including rejected operations and bypass paths. Describe architecture by module responsibility rather than a list of directories. Runtime calls may go out to an adapter while source dependencies point toward an internally owned interface.

Before Gate 2, reconcile every relevant approved scenario, context/model responsibility, invariant, consistency/interaction decision, dependency rule, and testing seam with its specification location. Fix omissions. If synthesis reveals a new business or architecture decision, return to `design-coder` and reopen the affected gate; specification synthesis must not invent entities, services or recovery policies. Ordinary wording corrections do not create a new design gate.

## Ticket decomposition

Use the bundled [ticket template](./ticket-template.md) to select the smallest independently verifiable business capability or use-case increment. Each ticket fits one agent context window; this is a sizing limit, not a requirement to stay in one DDD bounded context.

Within the existing ticket format, retain these fields (combine them for small tasks):

| Field | Required content |
| --- | --- |
| What to build | User-observable outcome and explicit scope |
| Spec references | Relevant scenarios, invariants, and architecture decisions; anchors or concise descriptions are enough |
| Ownership and implementation path | Affected contexts, responsible model elements/modules, invariants, necessary interfaces and consistency/interaction constraints, referencing the spec rather than copying the full model |
| Acceptance criteria and verification | Success/rejection/concurrency/retry examples as applicable, public test seams, and dependency checks relevant to this slice |
| Blocked by | Only tickets that supply a genuinely required capability or agreed interface; otherwise None |

Walk the use case across the necessary implementation parts. Do not create one ticket for all entities, another for all use cases, and another for all adapters. The first business slice introduces only the supporting abstractions it needs. A prerequisite refactor is separate only if necessary for independently green delivery, with its preservation checks explained. Use the local ticket template's expand-contract guidance for wide mechanical migrations while keeping required checks green.

A ticket may span business contexts when it is a coherent verifiable increment and the specification defines each participant's ownership, interaction contract, consistency, and failure behavior. Split only where increments remain independently meaningful; do not mandate a separate orchestration ticket.

Before Gate 3, check coverage in both directions: every in-scope scenario and invariant has a responsible ticket, and each ticket traces to approved behavior, model responsibilities and architecture constraints. Check real blocking edges and testability. Never label an affected ticket implementation-ready while its load-bearing decisions remain open; name the missing decision and affected tickets without blocking unrelated approved slices. Return to design for changed assumptions or to specification synthesis for omissions; ordinary ticket sizing changes remain in planning. Add these checks to the existing gate, not another approval round.

## Implementation and delivery

In `tdd-coder`, resolve a ticket's spec references before writing Red. Identify the contexts/model elements that own the rules and the approved concurrency/interaction semantics. Translate applicable success, rejection, interleaving, duplicate and partial-failure scenarios into behavior tests at approved public seams. During Green, place rules in their enforcing modules and preserve source dependency constraints. A dangling reference or missing behavioral decision must be resolved before implementation.

For applicable modeling changes, verify business actions and rejection outcomes, value construction/equality, independently meaningful policies and relevant bypass paths through public behavior interfaces. Use domain behavior in test names. Delivery checks that these guarantees and context-specific language survive all affected entry paths and approved compatibility mappings; model names alone are not evidence.

Behavior tests establish outcomes, not source dependency direction. Use existing import/lint/architecture checks when available; otherwise record a concrete dependency review with module/import evidence. Do not introduce test-only ports just to make a layer diagram look complete.

For behavior-preserving refactors or dependency-only repairs, use `tdd-coder`'s structural verification path: preserve green behavior checks and verify the structural change with a failing-to-passing dependency check or concrete before/after source review. Mixed tickets still require behavior Red-Green for changed outcomes. No business-test failure is required for an unchanged business outcome.

In `delivery-coder`, map each in-scope scenario/invariant to completed tickets and actual test evidence. Verify applicable context/model ownership, rule placement across entry points, atomicity/conflict handling and recovery behavior. Verify architecture separately against dependency checks or documented import/type/assembly review. Checked plan boxes or green sequential tests alone are insufficient. Missing implementation returns to ticket TDD; missing or invalidated design returns to the relevant design/specification gate.

## Example: cancel an order

Given an approved cancellation/refund contract: Orders owns cancellation, Payments owns refunds; shipped orders refuse cancellation (`INV-1`), duplicates produce no extra refund (`INV-2`), and Order domain code cannot import the payment SDK (`ARCH-1`).

A cancellation ticket references these decisions, records the path from the existing cancellation use case through Order and the approved refund interface, and tests observable success, shipped refusal, and duplicate behavior at the appropriate public seams. The payment adapter implements the external SDK interaction. Delivery checks the SDK import rule separately from the behavior tests.

If the design has not decided delivery guarantees or retry ownership between Orders and Payments, record the gap and return to design before finalizing affected tickets. The invariant alone does not choose a queue, an outbox, a transaction strategy, or a deduplication owner.

## Reference provenance

The language-discovery, protected-action, value-object and policy guidance draws on [engineering-review-board's Domain-Driven Design guidance](https://github.com/nledford/engineering-review-board/blob/main/skills/domain-driven-design/SKILL.md), consulted 2026-10-01. It is reference material, not an installed capability or a dependency on that repository's similarly named skills. Apply the local workflow, approval and verification contracts.
