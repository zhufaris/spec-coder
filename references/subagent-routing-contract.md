# Subagent Routing Contract

This contract governs optional model selection for spawned subagents. It is
normative for every spec-coder stage that delegates work. It does not create a
workflow stage, bundled skill, persisted routing state, or permission boundary.

## Authority

Workflow Orchestration owns task classification, delegation safety, promotion,
and verification. The live Host owns available provider/model identifiers,
context-fork restrictions, and the subagent tool interface. A target repository
may only raise the minimum tier; it never maps models or grants authority.

The active main agent retains scope decisions, approval interpretation,
user-change attribution, commit ownership, delivery aggregation, and completion
claims. These are `main-only` responsibilities even when a strong model is
available. Subagent output is evidence, not authorization.

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

## Configuration

Read trusted user mappings from:

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
duplicate tables. Invalid trusted configuration produces a warning and routes
to `inherit-main`; do not guess or rewrite it.

An optional repository policy lives at `.spec-coder/model-routing.toml`:

```toml
version = 1
minimum_tier = "standard"
```

It permits exactly `version` and `minimum_tier`. The minimum is `economy`,
`standard`, `strong`, or `inherit-main`. Any provider/model value, unknown
field, invalid value, unsupported version, or malformed TOML conservatively
routes to `inherit-main` with a warning. Repository policy can never lower the
workflow classification. Do not create or edit either configuration without
separate exact-diff authorization.

Model names above are examples, not required capabilities or stable aliases.
Do not install a model or edit Host configuration to satisfy an optional route.

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
send a self-contained task brief with evidence, mutation scope, exclusions,
verification seam, and expected output. Never use a subagent to bypass
`disable-model-invocation`, permissions, sandbox rules, or external-mutation
authority.

## Attempt Evidence and Promotion

A configured subagent result is provisional until the main agent inspects the
actual artifact or diff and freshly runs the applicable verification. Apparent
success does not authorize a gate, commit, or completion claim.

After a real delegated attempt fails, expresses uncertainty, lacks required
evidence, or crosses its boundary, preserve the original task, chosen route,
output, failure evidence, and verification state. Promote exactly once and
directly to an inherited-main subagent. Do not cycle through other configured
tiers after an attempt. Further failure follows the normal workflow blocker or
TDD repair path; promotion neither widens scope nor creates an approval gate.

## Stage Responsibilities

- `spec-coder` owns general classification, live Host compatibility, and
  promotion.
- `tdd-coder` may delegate only within an approved ticket and keeps Red-Green,
  diff review, affected verification, attribution, and commit ownership.
- `delivery-coder` may delegate bounded evidence collection but keeps final
  Standards/Spec findings, repair judgment, integration review, and completion.
- Other stages may consume advisory evidence but cannot weaken this contract's
  tier floors or main-only responsibilities.

If no subagent is useful, continue locally. Model routing is an optimization,
not a requirement to delegate.
