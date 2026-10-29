---
name: delivery-coder
description: Review and verify a completed spec-coder plan before declaring delivery. Use after all planned tickets are committed, or to resume final review, repair, and full-suite verification of an approved or autonomously selected specification.
---

# Delivery Coder

Apply the owners below. Route `code-review` through the selected review mode,
invoke `verification-before-completion`, and return behavior repairs to `tdd-coder`.

Apply the required Review Execution policy before either axis. Reviewers
collect bounded evidence; main authors the final Standards/Spec conclusions
and retains repair judgment, delivery aggregation and every completion claim.

## Required Reading

On every entry, including standalone invocation and resume, load these owner
sections before acting. Links are requirements, not background references.

- [Stage Runtime Envelope](../../references/workflow-contract.md#stage-runtime-envelope), [Approval Gates](../../references/workflow-contract.md#approval-gates), [Failure Transitions](../../references/workflow-contract.md#failure-transitions), [Native implement-spec executor](../../references/workflow-contract.md#native-implement-spec-executor).
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
- **Selected Task Playbook:** validate the approved [TaskPlaybookSelection](../../references/task-playbook-contract.md#taskplaybookselection), then dereference only its exact `conditional_references` anchor for every kind, never a sibling kind anchor. Freshly verify its `delivery_proof` on the actual affected path.
- **Human review:** before any suite-owned decision request, load [Review snapshot](../../references/approval-review-contract.md#review-snapshot), [Rendering](../../references/approval-review-contract.md#rendering), [Authority and safety](../../references/approval-review-contract.md#authority-and-safety), [Owning-skill responsibilities](../../references/approval-review-contract.md#owning-skill-responsibilities) and invoke bundled `show-me`; skip this rendering path when no human review is requested.
- **Delegation:** before deciding a worker route or dispatching any child, load [Authority](../../references/subagent-routing-contract.md#authority), [Tiers](../../references/subagent-routing-contract.md#tiers), [Delegation Eligibility and Execution Mode](../../references/subagent-routing-contract.md#delegation-eligibility-and-execution-mode), [Execution Waves](../../references/subagent-routing-contract.md#execution-waves), [Explicit Parallel Requests](../../references/subagent-routing-contract.md#explicit-parallel-requests), [Configuration](../../references/subagent-routing-contract.md#configuration), [Route Selection](../../references/subagent-routing-contract.md#route-selection), [Worker Progress Heartbeat](../../references/subagent-routing-contract.md#worker-progress-heartbeat), [Worker Brief Assembly](../../references/subagent-routing-contract.md#worker-brief-assembly), [Attempt Evidence and Promotion](../../references/subagent-routing-contract.md#attempt-evidence-and-promotion), [Stage Responsibilities](../../references/subagent-routing-contract.md#stage-responsibilities), [Result Integration](../../references/subagent-routing-contract.md#result-integration), and [Assembly](../../references/worker-brief-template.md#assembly), [Common brief](../../references/worker-brief-template.md#common-brief), [Role additions](../../references/worker-brief-template.md#role-additions). Supply actual brief content even when the child inherits no context.
- **Blinded evaluation lifecycle:** after mandatory deterministic Green, and
  only when the approved selection is **Skill Change** or **Workflow Eval**,
  load [Blinded evaluation constraints](../../references/task-playbook-contract.md#blinded-evaluation-constraints),
  [Workflow Eval Execution](../../references/subagent-routing-contract.md#workflow-eval-execution),
  and the candidate/judge role additions in the worker brief. Other playbooks
  do not load or run this comparison. It does not replace either review axis,
  fresh verification, or artifact checking.
- **Model examples:** when resolving domain ownership, concurrency, persistence or cross-context failures, read [worked examples](../../references/domain-design-examples.md); apply the required domain sections only to their observed triggers.

## Input

The approved or autonomously selected `TaskPlaybookSelection`, specification
and plan, completed ticket commits, current diff and Git history, repository
instructions, domain language, architecture decisions, and authoritative
verification commands. Autonomous selection does not reduce review scope or
fresh-verification requirements.

## Output

Severity-ordered findings, TDD-backed repairs, fresh full-suite evidence, and a
completion report naming commits, checks and residual risks.

## Review Execution

Load the routing owner's [Review Execution](../../references/subagent-routing-contract.md#review-execution)
and choose the review mode before either axis. In delegated mode assemble two
complete reviewer briefs with separate Standards and Spec inputs; in local mode
perform both independent passes. The upstream `code-review` method must preserve
the selected mode and child limits.

## Process

1. Confirm all tickets complete; inspect the authoritative workspace, mode,
   branch, initial changes, history, and executor-supplied cumulative accepted
   range/diff.
   Preserve and distinguish unrelated work, including in-place execution.
   Validate the selected `TaskPlaybookSelection` and dereference only its exact
   `conditional_references` anchor; do not load sibling kind anchors.
2. Run both review axes in the selected mode, findings first. Main inspects all
   evidence and authors final Standards/Spec conclusions; reviewers never gain
   approval, repair, verification, commit, delivery, or completion authority.
3. Check acceptance, domain/public contracts, dependency direction, errors,
   security, scope, and access controls. Map scenarios/invariants to tickets and
   tests. Verify applicable ownership, atomicity, idempotency, recovery, and
   architecture through dependency evidence or imports, exposed types, and
   assembly; checkboxes and sequential Green are insufficient.
4. Route behavior defects through `tdd-coder` Red-Green, affected checks, and a
   repair commit. Refactor structure only while behavior stays Green.
5. Repeat review until no unresolved blocking findings remain. Do not conceal accepted residual risks.
6. Invoke `verification-before-completion`; freshly run every applicable full test
   suite, lint, type check, build, and repository validation on the authoritative
   range. Keep that workspace's approved canonical cache from baseline and integration;
   configuration failure blocks and never falls back to `/tmp`.
   Earlier or subset evidence cannot substitute.
7. Run bundled `scripts/check-artifacts.py --phase delivery --spec <absolute-spec>
   --plan <absolute-plan> --repo <absolute-workspace>` against actual artifacts.
   Resolve findings or report unsupported history and manual review. This proves
   neither execution, attribution, nor freshness. Inspect status/history against
   initial changes; require atomic task commits without unrelated hunks while
   preserving pre-existing user staging.
8. Freshly verify the selected anchor's `delivery_proof` on the actual affected
   path. For a selected Skill Change or Workflow Eval, and only after steps 6-7 are
   deterministic Green, execute the blinded comparison constraints and routing
   lifecycle. Main reads every candidate output and all available
   workspace-local transcript evidence, authors the fail-closed verdict, and
   retains Parent on inconclusive or conflicting evidence. Any test, Gate,
   authority, dependency, artifact, or context-budget regression rejects
   Candidate regardless of judge preference. No comparison result can weaken a
   deterministic check or authorize repair, promotion, or completion.
9. Report the delivered specification, commits, fresh evidence, resolved findings, and residual risks. Claim completion only when all required checks pass.

Failed or uncertain delegated evidence returns to main under Attempt Evidence
and Promotion; a promotion reviewer remains read-only.

The executor handoff and external-effect boundary remain: without separate
authority, do not push, create a pull request, publish external tickets, amend
prior commits, merge an original branch, install, delete worktrees, or change
external state.

Apply [implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery)
to applicable domain/persistence changes. Map decisions to behavior, mapping,
and dependency evidence; inventories or renamed operations prove no enforcement.

## Stop Conditions

Stop without claiming completion when:

- the specification, plan, or expected commits are missing or inconsistent;
- review finds a design assumption invalid, in which case return to `design-coder` and reopen approval;
- any behavior repair has not completed the `tdd-coder` loop;
- any full-suite command fails or cannot be run;
- changes cannot be safely attributed or separated in the selected workspace;
- the same blocking condition occurs three consecutive times.

Preserve the failing command/output, finding, workspace, branch, initial changes,
and plan state for safe resume.
