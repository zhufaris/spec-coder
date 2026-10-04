---
name: delivery-coder
description: Review and verify a completed spec-coder plan before declaring delivery. Use after all planned tickets are committed, or to resume final review, repair, and full-suite verification of an approved specification.
---

# Delivery Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Compose `code-review` first, then `verification-before-completion`; route behavior repairs through `tdd-coder`.

Route optional delegated work through the [subagent routing contract](../../references/subagent-routing-contract.md). Subagents may collect bounded evidence or provide strong advisory analysis, but the main agent owns Standards/Spec findings, repair judgment, integration review, fresh verification, delivery aggregation, and every completion claim.

Read and apply the [domain design contract](../../references/domain-design-contract.md) to verify scenario/invariant coverage and architecture evidence separately.

Read the [worked examples](../../references/domain-design-examples.md) when reviewing rule ownership, consistency guarantees, type leakage or disproportionate abstractions.

## Input

The approved specification and plan, completed ticket commits, current diff and Git history, repository instructions, domain language, architecture decisions, and authoritative verification commands.

## Output

Findings ordered by severity, TDD-backed repair commits when needed, fresh evidence from the full applicable suite, and a completion report that identifies commits, checks, and any residual risks.

## Process

1. Confirm every ticket checkbox is complete and inspect the selected workspace/mode, branch, recorded initial changes, Git log, and cumulative task diff. In-place execution is valid; preserve unrelated user changes and distinguish them from ticket-owned edits.
2. Run `code-review` against both the specification and repository standards. Report findings before conclusions. Bounded review-evidence collection may use a configured tier only with complete inputs, explicit exclusions and a verification seam; the main agent inspects the evidence and authors the final Standards/Spec conclusions.
3. Check acceptance criteria, domain language, public contracts, dependency direction, Clean Architecture boundaries, error handling, security, and unintended scope. Map each in-scope scenario/invariant to completed tickets and actual test evidence. Verify context/model ownership, shared rule placement, and applicable atomicity/conflict, idempotency and recovery guarantees. Verify architecture separately with dependency checks or documented imports, exposed types and assembly; plan checkboxes and green sequential tests alone are insufficient. Check that simple CRUD/query work has not acquired unjustified abstractions or lost access controls.
4. Route behavior defects through `tdd-coder`: add or correct a failing test, observe Red, implement the minimum repair, run affected checks, and create a separate atomic commit. Perform structural refactoring only while behavior tests remain green.
5. Repeat review until no unresolved blocking findings remain. Do not conceal accepted residual risks.
6. Invoke `verification-before-completion` and freshly run every applicable full test suite, lint, type-check, build, and repository-specific validation command. Do not rely on earlier output or a ticket-level subset.
7. Inspect final status and commit history against recorded initial changes. Confirm each task change is represented by an atomic commit and no unrelated change entered those commits. Preserve any user-staged work that predated the task; its presence is not itself a delivery failure.
8. Report the delivered specification, commits, fresh evidence, resolved findings, and residual risks. Claim completion only when all required checks pass.

If delegated evidence fails, is uncertain, lacks required support or crosses its boundary, preserve the chosen route and attempt evidence for Workflow Orchestration to promote once directly to inherited main. Do not cycle through configured tiers, and never treat apparent subagent success as approval or completion authority.

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
