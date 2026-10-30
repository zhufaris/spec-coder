# Delivery stage playbook

## Procedure

### Capabilities

`code-review` in the selected mode and `verification-before-completion`; native full checks and artifact validation.
Main alone authorizes direct delegation; children must not spawn.

### Conditional Principles

- **Completion:** read [verify-real-outcome](../../principles/verify-real-outcome.md#verify-the-real-outcome) only on this observed trigger.

### Steps

1. Confirm all tickets complete; inspect the authoritative workspace, mode,
   branch, initial changes, history, and executor-supplied cumulative accepted
   range/diff.
   Preserve and distinguish unrelated work, including in-place execution.
   Validate the supplied `TaskPlaybookSelection` and current-step handoff.
   Reconstruct missing proof from its `conditional_references` only on standalone
   entry; never reroute or load sibling tasks.
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

- **Completion:** read [implementation and delivery](../../references/domain-design-contract.md#implementation-and-delivery)
to applicable domain/persistence changes. Map decisions to behavior, mapping,
and dependency evidence; inventories or renamed operations prove no enforcement.

### Review Execution

Load the routing owner's [Review Execution](../../references/subagent-routing-contract.md#review-execution)
and choose the review mode before either axis. In delegated mode assemble two
complete reviewer briefs with separate Standards and Spec inputs; in local mode
perform both independent passes. The upstream `code-review` method must preserve
the selected mode and child limits.
