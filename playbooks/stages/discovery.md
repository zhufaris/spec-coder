# Discovery stage playbook

## Procedure

### Capabilities

`grilling` for interviews; `domain-modeling` for qualifying glossary/ADR work.
Main alone authorizes direct delegation; children must not spawn.

### Conditional Principles

- **Domain language:** read [model-the-domain](../../principles/model-the-domain.md#model-the-domain) only on this observed trigger.

### Steps

1. Validate the selected workspace evidence: selected path/mode, branch,
   starting revision, accounted initial changes, and required capabilities.
   Perform discovery read-only from that state. Workspace preparation remains
   owned by `spec-coder` orchestration. When a confirmed decision first requires
   a qualifying document write and prepared evidence is absent or stale, make
   no write: return the decision, target, and resume point to orchestration for
   dependency preparation and a fresh green baseline, then resume `grill-coder`
   with that prepared evidence. Failed or uncertain preparation also stops
   before the write and returns its evidence to orchestration for disposition.
2. Inspect implementation evidence, the applicable glossary/ADR owners, and
   the selected playbook's `entry_evidence` before asking what the repository
   already answers. Collect its `design_obligations`; resolve empirical forks
   with bounded probes, while leaving preferences, scope, authority and Gates
   to their human owners.
3. Work a private decision tree through its dependency-ready frontier. Ask up to three
   independent ready questions, recomputing after each response;
   dependent questions never share a round.
4. Keep scope, meaning/ownership, invariants, architecture trade-offs and
   unknown coupling serial. Inspect agent-owned repository facts as downstream
   prerequisites without blocking unrelated ready items.
5. Give every question a stable `Qn` ID, applicable options, and its own clear
   recommendation with a one-sentence reason. The user may accept one
   recommendation with `Qn: default`; never interpret one bare `default` as an
   answer to a multi-question round. A recommendation is not a confirmed
   decision.
6. Only explicit, unambiguous individual answers confirm decisions. Preserve
   omitted IDs and resolve ambiguity with one serial follow-up.
7. After each confirmed decision, classify its durable destination:
   - canonical domain terminology, context-specific meaning, or an invariant
     updates the applicable `GLOSSARY.md` through `domain-modeling`;
   - an architecture decision updates or creates an ADR only when it is
     hard to reverse, surprising without context, and the result of a real trade-off;
   - scope, interface, acceptance, and ephemeral implementation choices stay in
     conversation for design/specification and produce no document write.
8. Immediately before a qualifying write, require prepared workspace evidence
   (dependency readiness and a fresh green baseline), then prove that the
   target is task-owned or safely separable from initial/user changes. Create
   glossary or ADR files lazily. Preserve existing definitions and explain
   compatibility before a confirmed replacement. If preparation evidence is
   absent or stale, return to `spec-coder` orchestration without owning CLI or
   capture mechanics; after green preparation, resume at this write. If
   orchestration reports failed or uncertain preparation, or ownership overlaps
   or remains ambiguous, make no write and stop with the decision, target,
   conflict, and resume point.
9. Challenge fuzzy or conflicting terms, distinguish affected contexts'
   meanings and state owners, and probe relevant transitions, concurrent
   requests, retries and partial failures. Defer detailed entities, services
   and architecture selection to `design-coder`.
10. Finish when every load-bearing decision is confirmed, explicitly deferred,
   or out of scope. Report settled decisions, changed documentation paths,
   unresolved branches, prepared workspace evidence, and the recommended next
   action.

During discovery, apply the contract's [language guidance](../../references/domain-design-contract.md#discover-and-evolve-domain-language). Return the evidence-backed ambiguities, context-specific meanings and compatibility decisions that constrain design; do not select a model merely from database names.

Protect unrelated work in the original checkout. In-place or isolated selection permits read-only
discovery; writes require a prepared green baseline. Do not write implementation code, create
branches, commit, publish, or imply later Gate approval. Without a qualifying
glossary/ADR decision, write no document.
