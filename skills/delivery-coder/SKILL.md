---
name: delivery-coder
description: Review and verify a completed spec-coder plan before declaring delivery. Use after all planned tickets are committed, or to resume final review, repair, and full-suite verification of an approved or autonomously selected specification.
---

# Delivery Coder

Apply the required owner sections below. Use the `code-review` review method only through a route compatible with the review mode below, then invoke `verification-before-completion`; route behavior repairs through `tdd-coder`.

Apply the required Review Execution policy before either axis. Reviewers
collect bounded evidence; main authors the final Standards/Spec conclusions
and retains repair judgment, delivery aggregation and every completion claim.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Phase Order](../../references/workflow-contract.md#phase-order), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Workspace Selection](../../references/workflow-contract.md#workspace-selection), [Git Safety](../../references/workflow-contract.md#git-safety), [Artifact Contract](../../references/workflow-contract.md#artifact-contract), [Verification Layers](../../references/workflow-contract.md#verification-layers).
- [Scale to the observed problem](../../references/domain-design-contract.md#scale-to-the-observed-problem), [Discover and evolve domain language](../../references/domain-design-contract.md#discover-and-evolve-domain-language), [Bounded contexts and their models](../../references/domain-design-contract.md#bounded-contexts-and-their-models), [Implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery).
- [Review Execution](../../references/subagent-routing-contract.md#review-execution).

- [Authority and lifecycle](../../references/verification-contract.md#authority-and-lifecycle).
- [Command interface](../../references/artifact-format.md#command-interface), [Findings and compatibility](../../references/artifact-format.md#findings-and-compatibility).
- [Delivery evidence](../../references/artifact-format.md#delivery-evidence).

## Conditional Reading

- **Architecture:** when module boundaries, dependency direction, interfaces or assembly are designed or changed, load [Architecture that can be verified](../../references/domain-design-contract.md#architecture-that-can-be-verified).
- **Interactions:** when concurrency, cross-context collaboration, retries or partial failures are relevant, load [Consistency and interaction contracts](../../references/domain-design-contract.md#consistency-and-interaction-contracts).
- **Persistence:** when aggregate updates, repository boundaries or persistence mechanisms are affected, load [Aggregate persistence semantics](../../references/domain-design-contract.md#aggregate-persistence-semantics).
- **Domain behavior:** when rules, invariants, lifecycle or valid-value constraints are affected, load [Protect behavior and valid values](../../references/domain-design-contract.md#protect-behavior-and-valid-values).
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route or dispatching any child, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Configuration](../../references/subagent-routing-contract.md#configuration), [Route Selection](../../references/subagent-routing-contract.md#route-selection), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

The approved or autonomously selected specification and plan, completed ticket
commits, current diff and Git history, repository instructions, domain language,
architecture decisions, and authoritative verification commands. Autonomous
selection does not reduce review scope or fresh-verification requirements.

## Output

Findings ordered by severity, TDD-backed repair commits when needed, fresh evidence from the full applicable suite, and a completion report that identifies commits, checks, and any residual risks.

## Review Execution

Load the routing owner's [Review Execution](../../references/subagent-routing-contract.md#review-execution)
and choose the review mode before either axis. In delegated mode assemble two
complete reviewer briefs with separate Standards and Spec inputs; in local mode
perform both independent passes. The upstream `code-review` method must preserve
the selected mode and child limits.

## Process

1. Confirm every ticket checkbox is complete and inspect the selected workspace/mode, branch, recorded initial changes, Git log, and cumulative task diff. In-place execution is valid; preserve unrelated user changes and distinguish them from ticket-owned edits.
2. Execute the selected review mode for both the Standards and Spec axes. Report findings before conclusions. Main inspects all returned or locally collected evidence and authors the final Standards/Spec conclusions; reviewer success never grants approval, repair, fresh-verification, commit, delivery or completion authority.
3. Check acceptance criteria, domain language, public contracts, dependency direction, Clean Architecture boundaries, error handling, security, and unintended scope. Map each in-scope scenario/invariant to completed tickets and actual test evidence. Verify context/model ownership, shared rule placement, and applicable atomicity/conflict, idempotency and recovery guarantees. Verify architecture separately with dependency checks or documented imports, exposed types and assembly; plan checkboxes and green sequential tests alone are insufficient. Check that simple CRUD/query work has not acquired unjustified abstractions or lost access controls.
4. Route behavior defects through `tdd-coder`: add or correct a failing test, observe Red, implement the minimum repair, run affected checks, and create a separate atomic commit. Perform structural refactoring only while behavior tests remain green.
5. Repeat review until no unresolved blocking findings remain. Do not conceal accepted residual risks.
6. Invoke `verification-before-completion` and freshly run every applicable full test suite, lint, type-check, build, and repository-specific validation command. Do not rely on earlier output or a ticket-level subset.
7. Run bundled `scripts/check-artifacts.py --phase delivery --spec <absolute-spec>
   --plan <absolute-plan> --repo <absolute-workspace>` against actual artifacts.
   Resolve findings or explicitly report unsupported historical format and
   manual review. This checks recorded structure and local commit identities,
   never proof of execution, attribution or freshness; step 6 remains required.
   Inspect final status and commit history against recorded initial changes. Confirm each task change is represented by an atomic commit and no unrelated change entered those commits. Preserve any user-staged work that predated the task; its presence is not itself a delivery failure.
8. Report the delivered specification, commits, fresh evidence, resolved findings, and residual risks. Claim completion only when all required checks pass.

If delegated evidence fails or is uncertain, preserve the attempt and return to
main under Attempt Evidence and Promotion. A promotion reviewer retains the
reviewer role's read-only limits in its assembled brief.

Do not push, create a pull request, publish external tickets, amend pre-existing commits, or make external changes without separate explicit authorization.

Apply the contract's [implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery) review requirements to applicable domain and persistence changes. Map approved decisions to actual behavior, mapping and dependency evidence across affected entry paths; a model inventory or renamed operation is not enforcement evidence.

## Stop Conditions

Stop without claiming completion when:

- the specification, plan, or expected commits are missing or inconsistent;
- review finds a design assumption invalid, in which case return to `design-coder` and reopen approval;
- any behavior repair has not completed the `tdd-coder` loop;
- any full-suite command fails or cannot be run;
- changes cannot be safely attributed or separated in the selected workspace;
- the same blocking condition occurs three consecutive times.

Preserve the failing command, output, finding, workspace/mode, branch, initial user changes, and current plan state so the workflow can resume safely.
