---
name: tdd-coder
description: Implement one executor-issued unblocked vertical ticket through an evidence-backed Red-Green loop, affected verification, atomic commit, and plan-state update. Use only from the native implement-spec executor with a validated or reconstructed executor-issued handoff.
---

# TDD Coder

Apply the required owner sections below. Compose the installed `tdd` skill at the public testing seams already selected in the specification and ticket plan.

This skill delegates eligible implementation work by default within one
approved or autonomously selected bounded ticket and its verification seam.
The main agent retains Red-Green, attribution and commit ownership. Apply the
required routing and domain sections before implementation.
Each executor-issued lifecycle owns one selected ticket only.
It is one unblocked ticket lifecycle, not a plan-selection entry point.
Each gate-3-approved executor-issued handoff authorizes one approved or autonomously selected ticket: one approved or autonomously selected unblocked vertical ticket in an approved or autonomously selected durable planned wave.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Phase Order](../../references/workflow-contract.md#phase-order), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Workspace Selection](../../references/workflow-contract.md#workspace-selection), [Git Safety](../../references/workflow-contract.md#git-safety), [Artifact Contract](../../references/workflow-contract.md#artifact-contract), [Verification Layers](../../references/workflow-contract.md#verification-layers).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery).

- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle), [Delivery evidence](../../references/artifact-format.md#delivery-evidence).
- [Ticket TDD handoff](../../references/implement-spec-execution-contract.md#ticket-tdd-handoff) and [Main-only result integration](../../references/implement-spec-execution-contract.md#main-only-result-integration).

## Conditional Reading

- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route or dispatching any child, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Configuration](../../references/subagent-routing-contract.md#configuration), [Route Selection](../../references/subagent-routing-contract.md#route-selection), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

One executor-issued unblocked ticket whose dependencies are complete, its
acceptance criteria, the approved or autonomously selected design and its
testing seams, the selected safe workspace with accounted-for initial changes,
and green baseline evidence. The handoff records Gate-3 approval, the durable
wave/frontier, selected ticket identity, recorded wave base, and workspace
decision. It identifies one approved or autonomously selected unblocked vertical
ticket. A direct or resumed invocation must validate or reconstruct that
executor-issued handoff from those records before work; it must not turn a plan
authorization into a plan-to-TDD bypass. The workspace may be in place or
isolated; autonomous selection does not relax ticket readiness or verification.

## Output

Observed Red and Green evidence for behavior changes, preservation and dependency evidence for structural work, passing affected checks, one atomic Conventional Commit containing only that ticket's files, its recorded commit evidence, and then a checked-off durable ticket with a synchronized runtime plan.

## Process

1. Validate the executor-issued handoff: confirm its approved or autonomously selected durable planned wave, Gate-3 approval, selected ticket identity, and
   recorded frontier reconstruct to the current earliest incomplete wave. Confirm
   all blockers are complete. Verify the selected workspace, recorded wave base,
   and initial changes; preserve unrelated work in either mode. If a direct or
   resumed invocation cannot reconstruct these executor facts, stop and return
   the missing or conflicting evidence to the native implement-spec executor;
   never select a ticket from a plan independently. The runtime wave may contain
   other ownership-safe tickets, but this invocation owns only one selected
   ticket and must not pull later-wave work forward. It is one lifecycle inside
   the native executor: main owns Red or structural evidence, authoritative
   integration, fresh verification, commits, and plan advancement. A direct
   implementer brief states `delegation_allowed = false` and cannot delegate or
   integrate sibling work.
2. Re-read the relevant specification, domain language, ADRs, ticket acceptance criteria, and existing test patterns. Resolve scenario/invariant and architecture references, affected contexts/model elements, enforcing owners, boundary data, atomicity/conflict and recovery semantics. Resolve missing decisions before implementation. If acceptance requires only structural preservation or dependency repair, use the structural path below instead of steps 3-6; mixed tickets still require behavior Red-Green for changed outcomes.
3. Write one behavior-focused test through a selected public seam for an applicable scenario or invariant.
4. Run that focused test and have main observe the expected failure as behavior
   Red. If it passes unexpectedly or fails for an unrelated reason, correct the
   test setup before implementation. For structural-only work, main instead
   establishes the structural preservation and dependency evidence required by
   the path below; do not manufacture a behavior Red.
5. After main owns the Red or structural evidence, apply Delegation Eligibility
   and Execution Mode, then assemble the worker brief with the implementation
   role. The child writes the minimum implementation for Green at the selected
   domain/application/adapter boundaries. Do not anticipate later tickets.
6. Run the focused test. Repeat steps 3-6 one behavior at a time until all applicable ticket scenarios and invariants have test evidence, including existing tests where sufficient. Include selected concurrent interleavings, duplicates and partial failures when relevant; a sequential fake alone does not prove a persistence concurrency guarantee. Then run the affected checks: relevant test modules, lint, type checks, and build steps defined by the repository.
7. Main inspects the complete task-owned diff, attributes every change, and
   freshly verifies the focused behavior or structural evidence plus all
   affected checks in the authoritative integrated state. Then perform a
   lightweight self-review for scope, duplication, naming, domain consistency,
   and accidental architecture violations. Check rule ownership across entry
   points and verify source dependencies, exposed boundary types and assembly
   with existing tooling or a concrete source review; child-local or passing
   behavior tests alone do not establish integrated Green or dependency
   compliance. Planning baseline reuse never satisfies this fresh integration
   check; record actual verification commands/results in the ticket under the
   artifact-format delivery evidence contract.
8. Inspect the diff against recorded initial changes, stage explicit paths owned by the ticket, and inspect the entire proposed commit for user-owned hunks or previously staged unrelated files. Apply the shared Git safety rules, using a verified path-scoped commit or isolation when necessary to preserve unrelated staged work. Create one Conventional Commit whose subject describes the delivered behavior. Only after it succeeds, append its actual commit ID and commit evidence to the ticket evidence.
9. After the commit evidence is recorded, update the durable plan checkbox and runtime mirror. Never record a checked state before that accepted commit exists.
10. Return to the native implement-spec executor for fresh frontier, workspace, and capacity evaluation. This lifecycle never selects another ticket or directly hands work to `delivery-coder`.

For a failed or uncertain delegated attempt, use Attempt Evidence and Promotion;
only main can create the promotion sibling using the complete common brief.

Never use `git add -A`. Never stage unrelated user changes, amend a commit that predates the ticket, skip or weaken a failing test, or broaden scope without returning to the appropriate approval gate.

Apply the contract's [implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery) requirements for relevant domain and persistence changes. Test selected behavior through its public seams, name tests after domain outcomes, and collect the separate mapping/dependency evidence required there; do not substitute class or method-name assertions.

## Structural verification path

For an approved behavior-preserving refactor or dependency-only repair, record the unchanged outcomes and baseline behavior checks. Keep those checks green during structural edits. If a dependency check exposes the violation, observe its failure before repair and its success after repair. Where no such tooling exists, record concrete before/after module/import review evidence. Finish with all affected checks and resume step 7. Do not manufacture a behavior failure for unchanged outcomes; new behavior requires the normal Red-Green path.

## Stop Conditions

Stop and preserve evidence when:

- no approved or autonomously selected unblocked ticket exists in a valid executor-issued handoff, or that handoff cannot be validated or reconstructed;
- the selected workspace is unsafe or changes cannot be attributed/separated from user-owned work;
- a behavior change cannot demonstrate Red for the intended reason, or structural work lacks preservation/dependency evidence;
- implementation evidence invalidates the selected design;
- an affected verification command fails after diagnosis;
- the same blocking condition occurs three consecutive times.

Do not mark the ticket complete or commit unless every ticket-level check is green.
