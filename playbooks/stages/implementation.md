# Implementation stage playbook

## Procedure

### Capabilities

`tdd` at public seams; native affected checks and Git for a verified atomic commit.
Main alone authorizes direct delegation; children must not spawn.

### Conditional Principles

- **Behavior preservation:** read [preserve-observable-behavior](../../principles/preserve-observable-behavior.md#preserve-observable-behavior) only on this observed trigger.

### Scope and authority

This stage delegates eligible implementation work by default within one
approved or autonomously selected bounded ticket and its verification seam.
Main retains Red-Green, attribution, and commit ownership. Each executor-issued
lifecycle owns one selected ticket, never plan selection. Its Gate-3-approved
handoff authorizes one approved or autonomously selected unblocked vertical ticket
in an approved or autonomously selected durable planned wave.
It remains one unblocked ticket lifecycle.

### Steps

1. Validate the executor-issued handoff: approved durable wave, Gate-3 approval,
   selected ticket, earliest incomplete frontier, completed blockers, workspace,
   wave base and initial changes. Missing/conflicting facts return to the native
   implement-spec executor; never select independently. This invocation owns
   one selected ticket and cannot pull work forward. Main owns Red/structural
   evidence, integration, fresh verification, commits and plan advancement.
   Direct briefs state `delegation_allowed = false` and forbid sibling work.
2. Re-read the specification, ticket, `TaskPlaybookSelection`, domain language,
   ADRs and tests. Confirm the ticket preserves the selected `red_or_pin` and
   `delivery_proof`; resolve referenced decisions and boundaries. Structural-only work uses its path
   below; mixed tickets still require Red-Green for changed outcomes.
   Confirm the ticket and brief share this workspace's approved `Build cache`.
   Main-local work keeps the authoritative reservation; an isolated worker keeps
   its approved branch reservation. Configure it repository-natively or block
   with evidence, never substitute `/tmp`.
3. Apply the selected `red_or_pin`: write the outcome reproduction for changed
   behavior, pin current behavior for a refactor, or capture the comparable
   baseline required by the playbook. Do not substitute a different route's Red.
4. Run that focused test and have main observe the expected failure as behavior
   Red. If it passes unexpectedly or fails for an unrelated reason, correct the
   test setup before implementation. For structural-only work, main instead
   establishes the structural preservation and dependency evidence required by
   the path below; do not manufacture a behavior Red.
5. After main owns the Red or structural evidence, apply Delegation Eligibility
   and Execution Mode, then assemble the worker brief with the implementation
   role. The child writes the minimum implementation for Green at the selected
   domain/application/adapter boundaries. Do not anticipate later tickets.
6. Run the focused test and repeat one behavior at a time until applicable
   scenarios/invariants have evidence. Cover relevant concurrency, duplicates
   and partial failures; sequential fakes do not prove concurrency guarantees.
   Use `scripts/validate-affected.py --repo <authoritative-repository> --path
   <task-owned-path>` only for supported spec-coder paths, repeating every supplied path;
   arbitrary repositories use native checks. The mapper rejects missing or
   unmapped paths. For a deleted/pre-rename path, pass an
   existing post-change owner or test path. Record commands/results. Affected verification remains
   separate from the fresh full suite and grants no acceptance or completion.
7. Main inspects the complete task-owned diff, attributes every change, and
   freshly verifies the focused behavior or structural evidence plus all
   affected checks in the authoritative integrated state using that workspace's
   approved build-cache reservation. Then perform a
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

### Structural verification path

For an approved behavior-preserving refactor or dependency-only repair, record the unchanged outcomes and baseline behavior checks. Keep those checks green during structural edits. If a dependency check exposes the violation, observe its failure before repair and its success after repair. Where no such tooling exists, record concrete before/after module/import review evidence. Finish with all affected checks and resume step 7. Do not manufacture a behavior failure for unchanged outcomes; new behavior requires the normal Red-Green path.
