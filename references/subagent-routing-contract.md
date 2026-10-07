# Subagent Routing Contract

This contract governs default delegation eligibility, safe execution-wave
selection, and model selection for direct subagents. It is normative for every
spec-coder stage that delegates work. It does not create a workflow stage,
bundled skill, persisted routing state, or permission boundary.

## Worker Progress Heartbeat

Every suite-owned direct child must report a Host-neutral `ProgressSnapshot` as
conversational observation evidence when proactive child-to-main messaging is
available. The snapshot has exactly these required
nonempty string fields: `ticket_or_axis`, `worker_handle`, `phase`,
`active_command`, `progress_evidence`, `verification_state`, `blocker`, and
timezone-aware ISO `observed_at`. Valid phases are `starting`, `working`,
`verifying`, `blocked`, and `completed`; valid verification states are
`not-started`, `running`, `passed`, and `failed`. `active_command` and
`blocker` use the explicit string `none` when not applicable.

Before a direct child is dispatched, or at dispatch, main records whether
proactive heartbeat capability is available. A ready capability records
`heartbeat-ready`; an unavailable capability records
`heartbeat-capability-unavailable`. Capability-unavailable is non-blocking and
preserves the existing delegation decision. Recording capability only after
dispatch is invalid.

Workers send a starting snapshot, another every 45-60 seconds while active,
and an immediate snapshot on phase change, before and after a long command, and
on blocker, failure, or completion. A short attempt need only send its start
and terminal snapshots. The Host adapter may provide the child-to-main
message path; the shared contract does not name a tool or process API.

The main agent records only the latest valid snapshot in conversation. Invalid
snapshots are rejected and cannot replace a prior valid observation. A Host
wait timeout or missed interval is reported as `heartbeat-overdue`; an ordinary
no-message observation without either condition is `awaiting-heartbeat`. If the Host cannot provide
proactive child-to-main messaging, report
`heartbeat-capability-unavailable` and preserve the existing delegation
decision. Both outcomes have execution effect `none`; a terminal snapshot is
provisional, and completion authority remains `main-only` after artifact
inspection and fresh verification.

Heartbeat evidence never creates a wave, promotion, local fallback,
interruption, reassignment, takeover, failure, blocker, or automatic stall
classification. It is observability only and does not alter the authority and
recovery rules below.

## Authority

Workflow Orchestration owns task classification, delegation safety, promotion,
and verification. The live Host owns available provider/model identifiers,
context-fork restrictions, and the subagent tool interface. A target repository
may only raise the minimum tier; it never maps models or grants authority.

The complete agent tree has at most two layers: layer 1 is the active main
agent and layer 2 contains only its direct subagents. Only the active main agent
may spawn or delegate. Every direct-child task brief must state
`delegation_allowed = false`; a child has no authority to create another child
or transfer work indirectly through a skill, workflow, tool, or other agent.
If a child needs further delegation, it must return its evidence and blocker to
the active main agent before any other agent is created.

The active main agent retains scope decisions, approval interpretation,
user-change attribution, commit ownership, delivery aggregation, and completion
claims. These are `main-only` responsibilities even when a strong model is
available. Subagent output is evidence, not authorization. When the Host can
deny child spawn tools, main uses that restriction as defense in depth. This
contract remains authoritative when the Host cannot provide such enforcement;
do not claim portable sandbox isolation.

## Tiers

Use the ordered tiers:

```text
economy < standard < strong < inherit-main
```

- `economy`: bounded mechanical/read-only work and narrow, reversible approved
  implementation with a deterministic verification seam.
- `standard`: normal TDD, diagnosis, testing, and review-evidence subtasks.
- `strong`: complex advisory architecture, security, cross-module review, or
  difficult debugging. It does not acquire main-only authority.
- `main-only`: do not delegate the responsibility at any configured tier.

A delegable task must have complete grounded input, explicit exclusions,
bounded and reversible scope, and a result or verification seam the main agent
can independently inspect.

## Delegation Eligibility and Execution Mode

Dependency readiness and delegation eligibility are separate decisions. An
approved ticket is delegation-eligible when its inputs are grounded, its scope
is bounded and reversible, the main agent has an independently inspectable
verification seam, and it carries no main-only authority or credentials. Every
dependency-ready eligible ticket delegates to one direct child by default,
including a wave containing only one ticket.

An explicit request-, ticket-, or review-scoped opt-out selects local execution
for exactly that scope and forbids both direct and indirect spawning there.
Opt-out is conversational, prospective, and request-scoped: do not write it to
repository or user configuration. It stops new dispatch and promotion in the
affected scope; already dispatched work follows the normal main-owned
inspection and acceptance rules unless the user separately requests safe
cancellation or discard.

Select the execution mode in this order:

1. A ticket whose dependencies are not ready remains `pending` and is not
   dispatched. This check precedes opt-out and delegation eligibility; a
   pending ticket never becomes `local` or `block`.
2. An applicable opt-out selects `local` for a dependency-ready ticket.
3. A delegation-ineligible ticket selects `local`; if delegation
   was explicitly required for that scope, select `block` instead.
4. Absent Host spawn capability selects `local` with the reason recorded; if
   delegation was explicitly required, select `block` instead.
5. Spawn capability with zero currently available direct-child slots selects
   `wait`; use the Host wait/resume mechanism and recompute live capacity.
6. Otherwise, select `delegate`.

Model routing is evaluated separately after delegation eligibility. An
`inherit-main` route, missing mapping, invalid optional mapping fallback, or
unavailable optional override does not turn eligible work into local work. An
unavailable explicitly required model remains a concrete routing conflict.

## Execution Waves

After Gate 3, form an immutable conceptual `ExecutionWave` from currently
dependency-ready tickets in approved plan order. If the next ready ticket is
main-local, it forms a one-ticket wave and never overlaps delegated mutation.
For a delegated wave, consider only delegation-eligible tickets and greedily
preserve approved plan order while excluding any candidate that declares a
mutation conflict with a selected ticket, or that a selected ticket declares a
conflict with. A delegated wave contains at most `min(4, live Host available
direct-child slots)` tickets.

Parallel mutation additionally requires real Host/task workspace isolation.
When isolation is unavailable, a delegated wave contains at most one ticket;
continue default delegation through serialized direct workers. Apparent path
disjointness in one shared workspace is not sufficient isolation. Recompute
dependencies, ownership conflicts, isolation, and capacity only after the main
agent has accounted for returned results and advanced accepted plan state.

There is at most one active execution wave. Wave membership and transient Host
handles remain conversational evidence; the approved plan checkboxes and
committed Git state remain durable. Do not create a scheduler database, private
state file, or persistent opt-out record.

Only tickets whose computed mode is `local` or `delegate` form an execution
wave. A `wait`, `block`, `pending`, or unknown outcome forms no wave and grants
no dispatch authority.

If an opt-out arrives during a delegated run, stop new dispatch and promotion.
Keep integrated commits attributed, inspect returned attributable results
before disposition, and leave undispatched tickets stopped. Cancellation or
discard still requires a separately safe disposition; after attribution, the
remaining affected execution is main-local.

## Configuration

The plugin ships its trusted default mapping at:

```text
config/model-routing.toml
```

The bundled file uses schema version 1 and maps `economy` to
`trae` / `GPT-5.6-Luna`, `standard` to `trae` / `GPT-5.6-Terra`, and
`strong` to `trae` / `GPT-5.6-Sol`. If the bundled file is missing or invalid,
route conservatively to `inherit-main`.

An optional trusted user mapping is read from:

```text
$XDG_CONFIG_HOME/spec-coder/model-routing.toml
~/.config/spec-coder/model-routing.toml  # when XDG_CONFIG_HOME is unset
```

Schema version 1 maps any subset of the three tiers:

```toml
version = 1

[tiers.economy]
provider = "trae"
model = "GPT-5.6-Luna"
```

Each present tier requires exactly nonempty string `provider` and `model`
fields. Reject unsupported versions, unknown top-level fields, unknown tiers,
unknown tier fields, partial pairs, non-string values, malformed TOML, and
duplicate tables. When no user file is present, use the bundled mapping. When
a user file is present, it completely replaces the bundled mapping; do not
merge missing tiers from the bundle. An invalid user file produces a warning
and routes to `inherit-main`; never fall back to the bundle, guess, or rewrite
the user file.

Mapping-source precedence is therefore: a present user file exclusively,
otherwise the plugin-owned bundled file, otherwise `inherit-main`. Repository
policy and current-session constraints only raise or restrict the resulting
route; they are not mapping sources.

An optional repository policy lives at `.spec-coder/model-routing.toml`:

```toml
version = 1
minimum_tier = "standard"
```

It permits exactly `version` and `minimum_tier`. The minimum is `economy`,
`standard`, `strong`, or `inherit-main`. Any provider/model value, unknown
field, invalid value, unsupported version, or malformed TOML conservatively
routes to `inherit-main` with a warning. Repository policy can never lower the
workflow classification. A target repository cannot map provider/model pairs.

Setup and installation may distribute or replace the plugin-owned bundled
file as part of the plugin payload, but must not create, edit, or rewrite the
user mapping or repository policy. Do not create or edit either optional
configuration without separate exact-diff authorization.

The bundled model identifiers are routing defaults, not guaranteed Host
capabilities or stable aliases. Do not install a model or edit Host
configuration to satisfy an optional route.

## Route Selection

1. Classify the task as economy, standard, strong, or main-only.
2. For a delegable task, take the stronger of its classification and repository
   minimum. A current-session user instruction may raise it or require main
   inheritance, but cannot lower the safety floor or transfer main-only work.
3. Inspect the live Host catalog and subagent tool definition. Do not trust a
   stale model list or assume an override signature.
4. Starting at the effective tier, use the first configured provider/model pair
   that is currently available and compatible:

```text
economy -> standard -> strong -> inherit-main
standard -> strong -> inherit-main
strong -> inherit-main
```

5. If an explicit user-required model is unavailable or below the effective
   tier, report the concrete conflict instead of silently substituting it. An
   excluded model is skipped.
6. If explicit override is absent or sufficient grounded context cannot be
   transferred to the child, use `inherit-main`. This is not a blocker.

When the Host requires a fresh or limited-history child for a model override,
the active main agent sends a self-contained task brief with evidence, mutation
scope, exclusions, verification seam, expected output, and the literal
`delegation_allowed = false`. Before spawning, use a Host option that denies
child spawn/delegation tools when one is actually supported. Absence of that
option does not block a contract-guarded direct child or expand its authority.
Never use a subagent to bypass `disable-model-invocation`, permissions, sandbox
rules, or external-mutation authority.

## Attempt Evidence and Promotion

A configured subagent result is provisional until the main agent inspects the
actual artifact or diff and freshly runs the applicable verification. Apparent
success does not authorize a gate, commit, or completion claim.

After a real delegated attempt fails, expresses uncertainty, lacks required
evidence, or crosses its boundary, preserve the original task, chosen route,
output, failure evidence, and verification state. Promotion is main-owned: the
active main agent may promote exactly once by creating an inherited-main
layer-2 sibling with `delegation_allowed = false`. The failed child must return
to main and cannot create its replacement. Do not cycle through other
configured tiers after an attempt. Further failure follows the normal workflow
blocker or TDD repair path; promotion neither widens scope nor creates an
approval gate.

## Stage Responsibilities

- `spec-coder` owns general classification, live Host compatibility, and
  promotion.
- `tdd-coder` delegates eligible work only within an approved ticket and keeps
  Red-Green, diff review, affected verification, attribution, and commit
  ownership.
- `delivery-coder` delegates eligible bounded evidence collection by default
  but keeps final Standards/Spec findings, repair judgment, integration review,
  and completion.
- Other stages may consume advisory evidence but cannot weaken this contract's
  tier floors or main-only responsibilities.

Ineligible work, applicable opt-out scopes, and spawn-unavailable fallback run
locally when safe. Model routing chooses the child route; it does not make
eligible default delegation optional.
