# Native implement-spec execution contract

This is the single owner for native execution after Gate 3. It is a contract, not a public skill or a second workflow profile. Every approved or autonomously selected plan, including a singleton plan, uses this executor.

## Authority and provenance

`plan-coder` remains authoritative for the approved specification, ticket graph, durable waves, workspace/base inputs, isolation decision, ticket ownership, and verification seams. `spec-coder` owns this executor; upstream manual-only implement-spec material is provenance only and is never invoked. There is no execution profile, size threshold, or alternative path.

Only active main schedules work, accepts evidence, attributes changes, performs fresh integrated verification, creates ticket commits, advances checkboxes, and hands the completed plan to delivery. The agent tree has two layers: direct implementers receive `delegation_allowed = false`. There is no implement-spec wrapper agent and no merger subagent.

## Executor entry

Enter `native-implement-spec` only when Gate 3 approves a nonempty ticket graph. A rejected or unavailable Gate 3 stops at `stop-gate-3`; an approved empty graph stops at `stop-empty-task-graph`. Positive graph cardinality always selects the same native executor, so one ticket is a degenerate task graph.

The executable oracle is `enter_implement_spec_executor` in `tests/forward_contracts.py`. It validates the Gate 3 fact and graph count; it intentionally has no profile or threshold input.

## Task graph and ready frontier

The earliest durable wave with an unchecked ticket is the only live frontier. Within it, select tickets in approved order only when dependencies are complete, delegation/local eligibility holds, ownership and semantic conflicts are safe, and live capacity permits. At most four direct implementers run together. A later wave never fills unused capacity in an earlier wave.

`select_planned_wave_batch` is the executable oracle for this selection. It retains the existing durable-wave validation, dependency, capacity, isolation, and explicit-parallel-request rules rather than duplicating them here.

## Adaptive workspace

Safe serial execution reuses the Gate-3-approved authoritative workspace. Parallel mutation or any approved isolation requirement needs an approved and available integration/isolation workspace prepared from the recorded wave base. Unsafe serial execution may use that same approved, available integration workspace; otherwise the executor reopens Gate 3. Missing, stale, conflicting, or unavailable required isolation never weakens the approved constraint.

`select_executor_workspace` is the deterministic selection oracle: `reuse-authoritative`, `prepare-integration`, or `reopen-gate-3`. It has no profile input and does not create, modify, or delete a worktree.

## Ticket TDD handoff

For each selected ticket, main enters one `tdd-coder` lifecycle and establishes Red or structural-preservation evidence. Main may directly brief one layer-2 implementer with the approved ticket, recorded wave base, ownership boundary, and verification seam. The implementer returns an attributable diff and evidence; it does not stage, commit, update plan state, or delegate.

## Main-only result integration

Workers begin from the recorded wave base and return complete task-owned results. Main integrates one accepted result at a time into the authoritative workspace, verifies it freshly, then commits exactly that accepted ticket and advances its checkbox before recomputing the frontier. A base mismatch, overlap, unclean transfer, unexplained diff, or failed verification follows the existing serial requeue/reassess rule.

`integrate_wave_result` is the executable oracle for acceptance; this contract does not duplicate its evidence checks.

## Recovery

Recover only from the approved graph and waves, recorded workspace/base facts, ticket checkboxes, accepted commits, returned attributable results, and current Git state. Recompute the earliest incomplete frontier after verified main integration. Do not treat transient worker handles, a stale provisional workspace, or unaccepted sibling advancement as plan progress. A missing or unsafe workspace/isolation fact reopens Gate 3 rather than inventing a fallback workflow.

## Completion handoff

When every approved ticket is checked and its accepted commit is present, `spec-coder` hands the cumulative accepted range and authoritative workspace to `delivery-coder`. Delivery independently reviews and freshly verifies the cumulative plan. Only delivery has terminal workflow completion authority.

## Forbidden external effects

The executor must not push. It must not create or ready a pull request. It must not close external tickets. It must not merge into the original branch. It must not install. It must not delete worktrees. These actions, including worktree disposition, require separately authorized handling outside the executor.
