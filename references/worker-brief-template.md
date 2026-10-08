# Worker Brief Template

## Assembly

Main assembles this template before **every** direct-child dispatch, including
standalone TDD, both delivery review axes and a promotion sibling. Its normative
sources are [Authority](./subagent-routing-contract.md#authority),
[Worker Progress Heartbeat](./subagent-routing-contract.md#worker-progress-heartbeat),
[Review Execution](./subagent-routing-contract.md#review-execution) and
[Attempt Evidence and Promotion](./subagent-routing-contract.md#attempt-evidence-and-promotion).
Read those sections, resolve every field below from current evidence, and send
the common brief plus the selected role additions as actual text. For promotion,
include both the original implementation/reviewer role and the promotion additions. A link to this
file is not a brief. Never depend on inherited conversation. Missing task inputs,
ownership or verification expectations must be resolved before dispatch.

## Common brief

Copy this block, replacing braces with concrete task evidence. These constraints
are included in the outgoing message, even in a fresh child context.

```text
Task: {ticket ID or review axis; exact requested bounded outcome}
Role: {implementation | reviewer | promotion; promotion retains original role}
Workspace: {absolute validated path; always use this path, not an inherited cwd}
Base: {recorded revision and relevant initial user changes}
Inputs: {approved/autonomously selected decisions and authority, acceptance
         criteria, relevant source/artifact contents and exact paths}
Mutation ownership: {explicit allowed files/modules; none for reviewer}
Exclusions: {out-of-scope files, behaviors, effects and other workers' ownership}
Verification seam: {commands, prerequisites, expected results and evidence
                    main already owns, including Red or structural baseline}
Return: base identity; complete task-owned diff and all changed/untracked paths;
        commands actually run with results; findings with file/line evidence;
        unresolved uncertainty/blockers. Do not claim checks you did not run.

Limits: delegation_allowed = false; must_not_spawn = true.
You must not spawn or delegate directly or indirectly through any skill,
workflow, tool or other agent. If decomposition or another agent is needed,
return evidence and the blocker to main. You must not stage or commit, alter
plan checkboxes, approve gates, expand scope, publish, install, or claim workflow
completion. Preserve unrelated and sibling work. Main alone owns acceptance,
attribution, Red/structural evidence, fresh integrated verification, staging,
atomic commits, delivery conclusions and completion authority. Your result is
provisional evidence, never approval. Do not infer Host sandbox enforcement.

Heartbeat capability: {heartbeat-ready | heartbeat-capability-unavailable},
recorded by main before or at dispatch.
When ready, send ProgressSnapshot at start, every 45-60 seconds while active,
on phase change, before and after a long command, and immediately on blocker,
failure or completion. A short attempt sends start and terminal state.
Required nonempty string fields: ticket_or_axis, worker_handle, phase,
active_command, progress_evidence, verification_state, blocker, observed_at.
phase: starting | working | verifying | blocked | completed.
verification_state: not-started | running | passed | failed.
active_command and blocker: use none when absent.
observed_at: actual timezone-aware ISO time.
Message destination/method: {main handle and supported proactive messaging path}.
If capability is unavailable, preserve delegation and return final evidence.
Heartbeat is observation only: awaiting-heartbeat is ordinary no-message;
heartbeat-overdue means a Host wait timeout or missed interval. Neither grants
failure/blocker classification, interruption, takeover, promotion, local
fallback or completion authority. Main rejects invalid snapshots and retains
only the latest valid observation in conversation.
```

## Role additions

Append the applicable role text, resolving its inputs:

- **Implementation:** implement only the selected ticket after main owns behavior
  Red or approved structural preservation evidence. Keep unchanged checks green;
  run the selected focused/affected commands and return the full owned diff.
  Do not anticipate later tickets. Main freshly verifies the accepted integrated
  state and owns checkbox updates and the atomic commit.
- **Reviewer:** read-only; no edits, no staging, no commits. `axis = {standards |
  spec}`. Standards receives repository instructions, status, cumulative diff,
  relevant history and verification conventions; checks correctness, security,
  performance, error handling, test quality, repository standards and scope.
  Spec receives approved/autonomously selected specification and plan, ticket
  commits, cumulative diff, domain/architecture decisions and test evidence;
  checks acceptance, public contracts, scenario/invariant coverage, dependency
  direction, architecture evidence and scope fidelity. Return findings ordered
  by severity with concrete file/line support and uncertainties. Remain on the
  assigned independent axis; main authors final Standards/Spec conclusions.
- **Promotion:** include original task and role, route, output, actual failure or
  uncertainty, missing evidence and verification state. Main may create exactly
  one inherited-main layer-2 promotion sibling after a real failed, uncertain,
  evidence-poor or boundary-crossing attempt. Retain all original ownership and
  role restrictions (a promoted reviewer is read-only). Do not cycle configured
  tiers, create a replacement or widen scope; further failure returns to main's
  normal repair/stop path. Heartbeat delay alone never authorizes promotion.
