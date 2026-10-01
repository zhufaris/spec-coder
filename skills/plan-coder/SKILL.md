---
name: plan-coder
description: Prepare an approved coding design for implementation by establishing isolation, proving a green baseline, writing a local specification, and creating dependency-aware implementation tickets. Use after design-coder approval or to resume planning from an approved design.
---

# Plan Coder

Follow the shared [workflow contract](../../references/workflow-contract.md). Compose `using-git-worktrees`, `to-spec`, and `to-tickets` in the order below; do not let their publication defaults bypass this skill's local-artifact and approval rules.

Read and apply the [domain design contract](../../references/domain-design-contract.md) during both synthesis and decomposition. Keep the upstream specification and ticket headings; embed domain and architecture content within them.

Read the [worked examples](../../references/domain-design-examples.md) when translating context/model responsibilities, consistency requirements or interactions into verifiable slices.

## Input

A Gate 1-approved design, the target repository, its project instructions, and any existing `spec-coder` artifacts.

## Output

A safe isolated branch and worktree, fresh green baseline evidence, a reviewed local specification, an approved dependency-aware ticket plan, and explicit authorization to begin implementation.

## Process

1. Inspect Git state. Reuse an existing safe isolated worktree; otherwise use the native worktree facility to create `feat/<slug>` or `fix/<slug>`. Preserve the original checkout and its uncommitted files.
2. Prepare dependencies using repository conventions, then run the applicable baseline tests, lint, type checks, and build.
3. Stop with the exact commands and output when the baseline is not green.
4. Use `to-spec` to write the specification at `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md`. Adapt its publication target to this local file; do not publish externally.
5. Before Gate 2, reconcile approved scenarios, affected context maps and model responsibilities, invariants, consistency/interaction decisions, dependency rules, and testing seams against their specification locations. Resolve omissions; return new design decisions to `design-coder` rather than inventing entities, services or recovery policies. Present the written specification and stop at Gate 2 until the user approves it.
6. Use `to-tickets` to create vertical tickets with explicit blocking edges, user-visible deliverables, acceptance criteria, and scope that fits one agent context window. Each ticket references relevant contexts/model elements, rules, implementation path, consistency/interaction constraints, boundary data and verification without copying the whole model. A ticket can span business contexts under an approved interaction contract. Store tickets as checkboxes at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`.
7. Mirror the durable ticket plan into the runtime plan with at most one item in progress. The Markdown plan remains authoritative.
8. Before Gate 3, check that all in-scope scenarios/invariants have responsible tickets, every ticket traces to approved decisions, blockers are real prerequisites, and each increment is independently verifiable. Name unresolved load-bearing decisions and affected tickets; resolve them through design/specification rather than assuming them or marking affected tickets ready. Independent approved slices need not be blocked by an unrelated open decision. Present the ticket set and stop at Gate 3 until the user approves it and authorizes implementation.

Creating an external issue, publishing to an issue tracker, pushing a branch, or opening a pull request always requires separate explicit authorization.

## Stop Conditions

Stop when:

- the approved design is missing or internally inconsistent;
- safe worktree isolation cannot be established;
- dependency setup or baseline verification fails;
- Gate 2 specification review is pending;
- Gate 3 ticket approval or implementation authorization is pending;
- `to-spec`, `to-tickets`, or `using-git-worktrees` is unavailable or incompatible.

After Gate 3, hand the first unblocked ticket to `tdd-coder`.
