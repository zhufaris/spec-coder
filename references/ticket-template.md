# Local Vertical-Ticket Template

`plan-coder` uses this local v1 template after specification approval or autonomous Gate 2 selection. Write the plan at
`docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`; use the [domain design
contract](./domain-design-contract.md), not an external planner or tracker.

## Copyable v1 skeleton

Replace examples with selected facts. Keep [plan grammar](./artifact-format.md#plan-grammar),
one checkbox heading per ticket, and explicit wave membership. A draft may pass
structural checking without invented execution/commit evidence; it is not
implementation authority.

```markdown
# Status command plan

<!-- spec-coder:artifact-v1 plan -->

## Workspace and authority

Name the native implement-spec executor; record selected specification,
authoritative workspace, recorded wave base, isolation requirement, permitted
integration/isolation preparation, starting revision/baseline, blocking edges,
durable waves, and Gate 2/3 decision.

## Wave W1: `T1`

### - [ ] T1: Report local readiness

| Field | Content |
| --- | --- |
| What to build | Read-only ready command after checks pass. |
| Spec references | SCN-1, INV-1 |
| Dependencies | None |
| Blocked by | None |
| Delegation eligibility | Bounded, reversible command with inspectable seam. |
| Delegation mode | Default direct worker |
| Ownership and implementation path | Status command and its public interface. |
| Mutation ownership | status.py, tests/test_status.py |
| Exclusions | Remote probes and automatic repairs. |
| Isolation | Serial worker; main validates authoritative workspace, recorded wave base, and isolation requirement before dispatch. |
| Concurrency conflicts | None |
| Verification seam | Public output, exit status, unchanged files. |
| Host capacity | One direct-child slot; recheck before dispatch. |
| Build cache | /absolute/physical/repository/.cache/feat/status-command/target |
| Direct-child boundary | delegation_allowed = false; main sends the common brief and implementation role. |
| Acceptance criteria and verification | Reports ready, exits zero, leaves files unchanged. |

## Final delivery checks

Main reviews acceptance, commits, runs the full applicable suite freshly, and
checks delivery evidence before claiming completion.
```

Keep the active baseline record in the existing specification or plan under
[Authority and lifecycle](./verification-contract.md#authority-and-lifecycle).
Moving it changes exclusion context and needs fresh capture. After actual
verification and main's accepted commit, add `Verification commands`,
`Verification results`, and `Commits` rows per [Delivery
evidence](./artifact-format.md#delivery-evidence); never prefill them.

## Plan structure and fields

Use stable ticket IDs, one authoritative checkbox per ticket, explicit durable
planned waves, and final delivery checks. At runtime there is one active execution wave,
selected only from approved or autonomously selected planned wave order; handles remain conversational. Every ticket exactly once;
waves have at most four members, dependencies point to earlier waves, same-wave
tickets have no ownership/semantic conflict, and main-local work is singleton.
Scheduling order is not a functional dependency.

Generated plans use one table row for every required field. The explanatory
table below groups related descriptions only; it does not change artifact grammar.

| Field | Required record |
| --- | --- |
| What to build; Spec references; Dependencies; Blocked by | Observable slice, approved IDs, and only genuine capability blockers; otherwise None. |
| Delegation eligibility; Delegation mode | Grounded bounded/reversible scope and inspectable seam; state main-only/credential limits, required delegation, or request/ticket opt-out. |
| Ownership and implementation path; Mutation ownership; Exclusions | Relevant context/interface/constraints, repository-relative owned files or directories (no globs), and out-of-scope files/responsibilities/authority. |
| Isolation; Concurrency conflicts; Host capacity | Read-only/serial/real Host-task-or-Git isolation, recorded wave base when applicable, conflicting IDs, and live-capacity assumption. |
| Verification seam | Inspectable focused evidence. For supported spec-coder paths use `scripts/validate-affected.py --repo <repository> --path <task-owned-path>` for every supplied path; arbitrary projects use repository-native affected tests/lint/type/build. For deleted or renamed paths, attribute the change and pass an existing post-change owner or test path plus preservation evidence. |
| Build cache | Scheduling input: every mutating ticket gets canonical `<physical-repo>/.cache/<branch>/target`, configured repository-native; `Mutation ownership: None` requires `Build cache: None`. Unsafe values remain located checker findings. Before Gate 3 resolve each ticket branch's exact ignored cache; read-only work requires `None`. |
| Direct-child boundary | `delegation_allowed = false`; main assembles [common brief](./worker-brief-template.md#common-brief) and role additions, including no indirect delegation/staging/commits and the routing-owned [Worker Progress Heartbeat](./subagent-routing-contract.md#worker-progress-heartbeat) / [Worker Brief Assembly](./subagent-routing-contract.md#worker-brief-assembly). |
| Acceptance criteria and verification | Success, refusal/bypass, concurrency/duplicate/recovery outcomes and the seam proving them. |

The plan is not a production scheduler. The durable plan fixes membership/order;
runtime forms a capacity-limited batch only from its earliest incomplete wave.
Parallel mutation needs real isolation; apply [Explicit Parallel
Requests](./subagent-routing-contract.md#explicit-parallel-requests) before
fallback. Runtime may shrink or serialize only as that owner permits, never
regroup or pull later-wave tickets. Resume reads membership, checkboxes, and
committed Git state, not invented waves.

An approved post-Gate-3 change to ownership, dependencies/blockers, conflicts,
delegation mode, isolation, authoritative workspace/base, or wave
membership/order stops dispatch, result acceptance, staging, commit, and
checkbox advancement. Persist renewed approval, run
`check-artifacts.py --phase plan --spec <absolute-spec> --plan <absolute-plan> --repo <absolute-workspace>`,
account for active/returned results, verify ownership, recorded base, and wave compatibility,
and reconstruct the frontier. Missing renewal/checker evidence or incompatible
results remain stopped; ordinary evidence/checkbox updates do not create a
fourth gate.

## Slicing rules

- Keep each independently meaningful, verifiable increment within one agent context window; slice business capability, not technical layers.
- Include all correctness guarantees for that capability; do not defer required concurrency or recovery behind a happy path.
- Cross-context slices name participant ownership, interaction data, consistency, failure behavior, and an independent seam.
- Separate a refactor only when it can be green independently; wide migrations may expand, migrate, then contract. Otherwise revisit design or use an indivisible slice.
- Add only real blocking edges; shared files/preferred order are not dependencies. Check cycles and missing IDs.

## Gate 3 readiness

Run the exact plan checker command above and resolve [findings](./artifact-format.md#findings-and-compatibility). Check bidirectional scenario/invariant coverage, ownership/exclusions, eligibility/mode, isolation/conflicts, seam, cache, capacity, and child boundary; unresolved load-bearing decisions are not ready. Present ticket set, deliverables, dependencies, blocking edges, workspace/base/isolation inputs, permitted preparation, and durable planned-wave membership/order. Interactive Gate 3 approves them; autonomous Gate 3 records `auto-selected under explicit autonomous authority`. Afterward main hands waves to the executor, updates a checkbox only after required checks pass, and retains atomic commits. External ticket publication needs separate authority.
