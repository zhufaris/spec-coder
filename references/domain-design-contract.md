# Domain Design Contract

Carry one scenario-driven design through specification, tickets, implementation, and delivery. DDD clarifies meaning, rules, and ownership; Clean Architecture clarifies module interfaces and source dependency direction. Apply both while synthesizing and slicing, rather than treating architecture as a completed preliminary checklist.

This reference governs spec-coder's native planning templates. Keep the workflow
contract's stages, artifact locations, and three approval gates. Interactive approval or autonomous selection
makes the specification the design authority;
tickets reference its relevant decisions instead of maintaining another copy of
the model. Autonomous selection changes only the review transition, not the
domain and architecture evidence required in the artifact.

## Contents

- [Scale to the observed problem](#scale-to-the-observed-problem)
- [Discover and evolve domain language](#discover-and-evolve-domain-language)
- [Bounded contexts and their models](#bounded-contexts-and-their-models)
- [Protect behavior and valid values](#protect-behavior-and-valid-values)
- [Aggregate persistence semantics](#aggregate-persistence-semantics)
- [Consistency and interaction contracts](#consistency-and-interaction-contracts)
- [Architecture that can be verified](#architecture-that-can-be-verified)
- [Design content and specification mapping](#design-content-and-specification-mapping)
- [Ticket decomposition](#ticket-decomposition)
- [Implementation and delivery](#implementation-and-delivery)

## Scale to the observed problem

Choose modeling depth from observed evidence and name overlapping triggers. A
small change may need one paragraph, not template-driven identifiers,
glossaries, entities, services, or layers. The later modeling/persistence checks
apply only to affected behavior. Simple normalization or an authorized query
may remain in existing modules without new value objects, policies, events, or
repositories, while preserving access/tenant checks, input constraints, and
observable rejection. Revisit depth when evidence adds a rule or interaction.

| Observed trigger | Required decisions |
| --- | --- |
| CRUD, field, display | Meaning, owner, constraints, result, verification |
| Rules or state transitions | Invariants, enforcement/state owners, allowed/rejected transitions |
| Concurrency or retries | Atomicity/conflict, idempotency identity/owner, losing/duplicate outcome |
| Multiple contexts/external semantics | Local models, translation/data, consistency/recovery owners |
| Framework, persistence, SDK coupling | Interface owner, dependencies, conversion, assembly |

Give scenarios, invariants, and architecture decisions stable references such
as `SCN-1`, `INV-1`, and `ARCH-1`, preserve them during decomposition, and use
the [worked examples](./domain-design-examples.md) for ambiguous ownership.

## Discover and evolve domain language

Derive nouns, actions, states, roles, and constraints from requirements, tests,
API/UI behavior, code, domain meaning, and observable outcomes—not database
names alone. Read existing `GLOSSARY-MAP.md` and context glossaries. Before
assuming, record ambiguous/contradictory terms, their contexts, and affected
decisions.

Use one term for one meaning across code, tests, interfaces, and user errors;
name context-specific meanings and translations. Record settled language via
the glossary workflow, but keep implementation decisions in the specification.
A rename must identify public contracts, consumers, compatibility/translation,
and migration. Internal-model approval never implicitly authorizes renaming a
public field or status.

## Bounded contexts and their models

Describe only affected **Bounded Contexts** and interaction-relevant neighbors.
A context owns coherent language/model; it is not inherently a folder, table,
team, deployment, or microservice. Justify boundaries by meaning, rules, or
ownership; one context may suffice. Separate evidence-backed **observed**,
**proposed**, and **unresolved** elements and contradictions. Legacy leakage is
not approval for a constraint or unrelated redesign. In the specification,
combine small-task rows and explain ambiguous omissions.

| Model content | Explain |
| --- | --- |
| Context | Purpose/language, authoritative state, exclusions, neighbors |
| Entity | Identity, lifecycle, behavior; cross-context identity mapping |
| Value object | Meaning, equality, immutability, valid construction |
| Aggregate/root, if needed | Members, protected invariants, rule-based consistency boundary |
| Domain service/policy, if needed | Named decision/operation, inputs/results/rules/collaborators and enforcing caller |
| Application use case | Coordination, transactions/interactions, references to authoritative rules |
| Repository/port/event, if needed | Served capability/owner, semantics, insufficiency of existing interfaces |

Give each significant invariant an enforcing module and observable seam. Choose
the simplest suitable entity, value object, aggregate, or function/service;
logical roles need not be classes. Avoid service-per-use-case,
repository-per-table, passive-record/god-service, and interface-per-class
designs. Preserve simple CRUD when no richer rule exists.

## Protect behavior and valid values

- Express rule-bearing changes as domain actions with preconditions, results and rejection behavior: for example, `accept_invitation` rather than unrestricted `update_status`. Entity methods or domain functions are both valid. Find all relevant entry paths, including generic updates, jobs and deserialization; renaming a method does not prevent callers from bypassing its rules. Distinguish business decisions from application coordination and adapter conversion.
- Define value-object equality and normalization from business meaning, not convenience. Keep values immutable and replace them through valid construction. Where the language permits, use types and controlled construction to make invalid states unrepresentable; otherwise enforce the equivalent invariant through the module's interface. External conversion must preserve these rules. A data wrapper without protected meaning is not useful modeling.
- Extract a policy when a decision has an independent business name, varies independently or is reused. Keep a simple condition in its natural owner when extraction adds no value. State how the authoritative operation applies the policy so preview and execution do not acquire divergent rules. A DDD Specification is a decision predicate, not the spec-coder specification document; avoid using the shared name ambiguously. Do not require a policy class hierarchy or generic rule engine.
- Name domain events after meaningful facts that have occurred. Define which successful transition produces a fact and how rejection behaves when events are part of the approved design; do not add events as generic callbacks merely because a model has state.

## Aggregate persistence semantics

Apply this section when a change affects an aggregate or its persistence mapping. Keep the aggregate as small as the invariants requiring atomic consistency allow. Protect its internal mutations through the root's behavior interface; do not expose mutable children that can bypass those rules. Relationships and joins do not justify absorbing other contexts' records into the aggregate.

Define repositories as collection-like access to the aggregates the use case actually needs, hiding storage shape. Specify identity, absence, save/load results and applicable conditional-write semantics. Reuse existing interfaces; do not create a repository per table or force read-only projections through the write model. Persistence metadata can belong to an enclosing persistence contract rather than the business entity, but required conflict information must survive the round trip.

Restore persisted identity, value meaning, lifecycle state and applicable concurrency information through controlled reconstitution. Preserve intrinsic validity without replaying public business commands, emitting new business facts or rerunning today's creation/eligibility rules on legitimate historical state. Distinguish current transition preconditions from structural validity; define how malformed or incompatible stored values are reported or migrated instead of silently supplying lost currency, version or other business data.

Verify with the appropriate existing adapter/integration seam: save, load, then exercise a domain operation and inspect the observable result. Include identity, value equality/constraints, state and relevant child behavior or version semantics. A field-copy assertion or an always-successful fake is insufficient for actual mapping/atomicity guarantees. Test the approved conflicting interleaving separately when concurrency matters; green sequential round trips alone do not prove it.

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

In `design-coder`, derive domain rules and architecture together from success,
rejection, and relevant retry scenarios. Separate confirmed decisions, code
evidence, and unresolved questions. Use the bundled [specification
template](./specification-template.md); small tasks may combine rows.

| Design content | Placement in the local specification | Preserve |
| --- | --- | --- |
| Scenarios | User Stories; Behavior & Failure Modes | Triggers, outcomes, rejection/retry |
| Domain | Domain Model | Contexts, terms/actions/values, policies, owners, invariants/boundaries |
| Architecture | Architecture | Responsibilities, interfaces, dependencies, assembly/boundary data |
| Verification | Testing Decisions | Public seams, persistence behavior, separate dependency evidence |
| Limits | Out of Scope; Further Notes | Exclusions, open decisions and blocked work |
| Language | Compatibility & Migration | Meaning/name changes, consumers, compatibility/migration |

Record interface preconditions, outputs, and failures—not only method names.
Tickets preserve applicable action/value/policy decisions, rejections, and
bypass paths. Describe module responsibilities and remember that runtime calls
may target an adapter while source dependencies point inward.

Before Gate 2, map every relevant scenario, model responsibility, invariant,
interaction/dependency decision, and test seam into the specification. Fix
omissions. New business/architecture decisions return to `design-coder` and
reopen the gate; synthesis cannot invent entities, services, or recovery.
Wording-only corrections do not create a gate.

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

When persistence is affected, preserve the approved aggregate/repository and reconstitution semantics in the specification and ticket acceptance. Implementation and delivery require actual mapping and post-load behavior evidence at the appropriate seam, including intrinsic value validity, protected child state and applicable conflict information. A missing stored value or unspecified legacy migration is a decision to resolve, not permission to guess a default.

Behavior tests establish outcomes, not source dependency direction. Use existing import/lint/architecture checks when available; otherwise record a concrete dependency review with module/import evidence. Do not introduce test-only ports just to make a layer diagram look complete.

For behavior-preserving refactors or dependency-only repairs, use `tdd-coder`'s structural verification path: preserve green behavior checks and verify the structural change with a failing-to-passing dependency check or concrete before/after source review. Mixed tickets still require behavior Red-Green for changed outcomes. No business-test failure is required for an unchanged business outcome.

In `delivery-coder`, map each in-scope scenario/invariant to completed tickets and actual test evidence. Verify applicable context/model ownership, rule placement across entry points, atomicity/conflict handling and recovery behavior. Verify architecture separately against dependency checks or documented import/type/assembly review. Checked plan boxes or green sequential tests alone are insufficient. Missing implementation returns to ticket TDD; missing or invalidated design returns to the relevant design/specification gate.

## Example: cancel an order

Given an approved cancellation/refund contract: Orders owns cancellation, Payments owns refunds; shipped orders refuse cancellation (`INV-1`), duplicates produce no extra refund (`INV-2`), and Order domain code cannot import the payment SDK (`ARCH-1`).

A cancellation ticket references these decisions, records the path from the existing cancellation use case through Order and the approved refund interface, and tests observable success, shipped refusal, and duplicate behavior at the appropriate public seams. The payment adapter implements the external SDK interaction. Delivery checks the SDK import rule separately from the behavior tests.

If the design has not decided delivery guarantees or retry ownership between Orders and Payments, record the gap and return to design before finalizing affected tickets. The invariant alone does not choose a queue, an outbox, a transaction strategy, or a deduplication owner.

## Reference provenance

The language-discovery, protected-action, value-object and policy guidance draws on [engineering-review-board's Domain-Driven Design guidance](https://github.com/nledford/engineering-review-board/blob/main/skills/domain-driven-design/SKILL.md), consulted 2026-10-01. It is reference material, not an installed capability or a dependency on that repository's similarly named skills. Apply the local workflow, approval and verification contracts.
