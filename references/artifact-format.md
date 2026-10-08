# Supported artifact format

The read-only `scripts/check-artifacts.py` command checks actual local Markdown
specifications and plans. Markdown remains authoritative; parsed objects and
findings are transient. The checker never approves a gate, changes a checkbox,
schedules a worker, runs a document command, writes an artifact, or commits.

## Command interface

Use Python 3.11 or later (the existing suite environment), without additional
packages. Delivery checks also require local Git. Resolve the bundled script
relative to the plugin installation; paths to documents and `--repo` are resolved
against the caller's working directory. The script works from another project's
working directory.

```sh
python3 /path/to/spec-coder/scripts/check-artifacts.py \
  --phase spec --spec docs/spec-coder/specs/example.md
python3 /path/to/spec-coder/scripts/check-artifacts.py \
  --phase plan --spec docs/spec-coder/specs/example.md \
  --plan docs/spec-coder/plans/example.md --json
python3 /path/to/spec-coder/scripts/check-artifacts.py \
  --phase delivery --spec docs/spec-coder/specs/example.md \
  --plan docs/spec-coder/plans/example.md --repo /path/to/project --json
```

`--phase` and `--spec` are required. `--plan` is required for plan and delivery.
`--repo` defaults to the current working directory and is used only to inspect
local commit references during delivery. It does not select a document or execute
a test. Omit `--json` for `path:line: rule: message` findings.

| Exit | Status | Meaning |
| --- | --- | --- |
| 0 | `passed` | The requested supported structural checks passed. |
| 1 | `findings` | Supported documents have validation findings. |
| 2 | `unsupported` | A document lacks exactly one supported marker or has a malformed/version/type mismatch. |
| 2 | `unusable` | A required path is missing, unreadable, not a regular file, or not UTF-8. |

Invalid CLI arguments also exit 2 with argparse usage diagnostics on stderr.
For valid CLI arguments, `--json` emits one object on stdout:

```json
{
  "status": "findings",
  "phase": "plan",
  "findings": [
    {
      "rule": "wave.missing-member",
      "path": "/absolute/path/plan.md",
      "line": 8,
      "message": "T1 must appear exactly once in a planned wave"
    }
  ]
}
```

`rule`, `path`, `line` and `message` are present in every finding. Lines are
one-based; a missing document-level element uses line 1. A missing CLI plan path
uses an empty path. Rule identifiers are machine-readable; messages are for
humans. Unsupported/unusable input stops dependent checking and never reports
partial validation as passing.

The [specification template](./specification-template.md#copyable-v1-skeleton)
and [ticket template](./ticket-template.md#copyable-v1-skeleton) contain paired,
copyable examples exercised by real CLI integration tests. Replace illustrative
task data before use; never prefill actual verification results or commit IDs.
The stages invoke spec/plan checks at the existing Gate 2/3 boundaries and
delivery checks alongside fresh full-suite execution, without adding a gate.

## Active Markdown and markers

Each document contains exactly one standalone marker of the matching kind:

```markdown
<!-- spec-coder:artifact-v1 spec -->
```

```markdown
<!-- spec-coder:artifact-v1 plan -->
```

Markers in ordinary inline prose are examples, not declarations. A standalone
marker candidate with trailing junk, the wrong kind/version, or a duplicate
marker returns `unsupported`. The tool does not normalize or write the document.

Backtick and tilde fences with at least three fence characters and up to three
leading spaces are supported. A closer must use the same character, at least as
many characters, and only trailing whitespace. Shorter fences and the other
fence character stay inside the example. An unclosed fence produces a finding.
HTML comments other than standalone artifact markers are inactive; an unclosed
comment produces a finding. Put declarations on their own lines, outside code
fences/comments, blockquotes, lists, and indented code examples. The grammar below
is intentionally bounded; arbitrary Markdown variants are not interchangeable.

A `spec-coder-verification` fenced JSON block may hold baseline evidence in either
document. This checker ignores its payload just like other fenced content. Use
the [verification contract](./verification-contract.md) and evidence CLI to
check baseline reuse; an artifact-format pass cannot establish that decision.

## Specification grammar

A specification has these exact level-two headings, each once:

- `## Problem Statement`
- `## Solution`
- `## User Stories`
- `## Implementation Decisions`
- `## Testing Decisions`
- `## Out of Scope`
- `## Further Notes`

Additional sections and prose are allowed. In-scope decisions are actual
level-three through level-six headings with a stable ID and nonempty title:

```markdown
### SCN-1: An operator checks a plan
### INV-1: Checking never changes inputs
### ARCH-1: A local command checks Markdown
```

IDs are `SCN-`, `INV-`, or `ARCH-` followed by a positive decimal integer without
leading zeros. IDs are unique across the specification. All defined IDs are
in scope for coverage; keep deferred ideas as ordinary prose in Out of Scope.
No fixed count or category inventory is required, and a narrow task need not
invent architecture or domain decisions.

Declare internal references using `References: SCN-1, INV-1` or
`Spec references: SCN-1, INV-1` on a standalone line, or a two-column table row
named `References` or `Spec references`. Every reference must resolve. Use `None`
for an explicitly empty list. List members may each use one balanced pair of
backticks. Duplicate members and malformed lists produce findings. Ordinary
prose mentions are not guessed to be references.

## Plan grammar

A plan has one authoritative checkbox heading per ticket and explicit wave
membership in ordered level-two sections:

```markdown
## Wave W1: `T1`, `T2`

### - [ ] T1: Implement a capability

| Field | Content |
| --- | --- |
| Spec references | SCN-1, INV-1, ARCH-1 |
| Dependencies | None |
| Delegation mode | Default direct worker |
| Mutation ownership | src/check.py, tests/test_check.py |
| Concurrency conflicts | None |
| Acceptance criteria and verification | Valid input passes; assert CLI exits and findings with temporary Markdown fixtures. |

### - [ ] T2: Implement another capability

| Field | Content |
| --- | --- |
| Spec references | SCN-1 |
| Dependencies | None |
| Delegation mode | Default direct worker |
| Mutation ownership | src/other/ |
| Concurrency conflicts | None |
| Acceptance criteria | Invalid input produces a source-located finding. |
| Verification | Run the focused CLI fixture test. |
```

Tickets use `T` plus a positive integer without leading zeros. `[x]` and `[X]`
mean complete; `[ ]` means incomplete. Nonempty titles and unique IDs are
required. Wave IDs use `W` plus a positive integer and are unique; textual order
is execution order (numeric labels need not be contiguous). Membership is a
comma-separated ticket-ID list on the wave heading, not inferred from the ticket
heading's position. `None` parses as an empty wave and therefore produces a
finding. Every ticket must occur exactly once, with at most four per wave.

Ticket fields are two-column Markdown table rows under the ticket heading,
until the next level-one through level-three heading. Field names are
case-insensitive. Use one row per field and escape literal pipes as `\|`; no
multiline cells are supported. Additional fields such as implementation notes,
exclusions, isolation and verification seams are allowed. Required fields are:

| Field | Contract |
| --- | --- |
| Spec references | Comma-separated defined decision IDs, or `None` when there are no applicable defined IDs. All in-scope decisions need at least one ticket. |
| Dependencies | Comma-separated ticket IDs, or `None`; IDs must exist, dependencies must be acyclic and in earlier waves. |
| Delegation mode | `Default direct worker`, `required delegation`, or `delegate` map to delegate; `main-local`, `local`, or `opt-out` require a singleton wave. An optional reason follows a semicolon. |
| Mutation ownership | Comma-separated exact repository-relative file/module-directory paths, or `None` for no mutation. |
| Concurrency conflicts | Comma-separated ticket IDs, or `None`; referenced IDs must exist and cannot share a wave, even if declared in only one direction. |
| Acceptance criteria and verification | Nonempty acceptance and verification prose; alternatively supply both `Acceptance criteria` and `Verification`. `None` is not accepted. |

An optional `Blocked by` field must agree with `Dependencies`. Empty fields,
`TODO`, `TBD` and `N/A` placeholders are findings. A plan has at least one ticket
and one wave. Draft plan checks permit incomplete checkboxes.

Ownership paths are lexical declarations, independent of whether future files
exist. Use `src/file.py`, `README.md` or `src/module/` (directory trailing slash
is optional when the declaration contains a slash). One balanced backtick pair
per path is allowed. A trailing slash is normalized for comparison. Equal paths
and ancestor/descendant paths overlap; siblings such as `src/a.py` and
`src/a.py.extra` do not. Matching uses case-sensitive POSIX path spelling.

Absolute paths, `.`/`..` components, empty components, home expansion, backslashes,
whitespace, glob syntax, braces and bare ambiguous module names produce
`ownership.ambiguous`. Resolve them into explicit paths before claiming no
conflict. The checker does not discover symlink aliases, case-insensitive
filesystem aliases, undeclared ownership or semantic business conflicts; review
those independently. An ambiguous declaration is a finding even in a singleton
wave, not evidence of disjoint ownership.

## Delivery evidence

Delivery runs all spec/plan checks, requires completed ticket checkboxes, and
requires these additional per-ticket rows:

```markdown
| Verification commands | python3 -m unittest discover -s tests -p test_check.py |
| Verification results | Exit 0; 12 tests passed; observed by main. |
| Commits | a1b2c3d |
```

The commit above is illustrative and only passes if it resolves locally. Supply
one or more comma-separated hexadecimal commit identifiers of 7–64 characters;
one balanced backtick pair per ID is allowed. Named refs, revision operators,
options and command substitutions are rejected. Each ID must resolve to a
commit through bounded local `git rev-parse --verify --end-of-options` inspection.
Unknown objects, blob IDs and unavailable Git inspection produce findings.
The checker never runs the `Verification commands` cell.

Commands/results must be present and nonempty, but are recorded claims: the
checker does not parse shell syntax, authenticate results, prove success,
freshness, attribution or that a command actually ran. A local commit ID also
does not prove the ticket was implemented. Main still reviews diffs/history,
observes fresh affected/full verification, and decides delivery under the
[workflow contract](./workflow-contract.md).

## Findings and compatibility

Stable rule families are `format.*` and `input.*` for unsupported/unusable
artifacts, `spec.*`/`decision.*` for definitions, `field.*`/`reference.*` for
fields and references, `coverage.uncovered`, `ticket.*`, `dependency.*`,
`conflict.*`, `ownership.*`, `wave.*`, and `delivery.*`.

Representative actionable rules include `decision.duplicate-id`,
`reference.unknown`, `dependency.cycle`, `dependency.earlier-wave`,
`dependency.blocked-by-mismatch`, `wave.duplicate-member`,
`wave.missing-member`, `wave.capacity`, `wave.local-singleton`,
`wave.declared-conflict`, `wave.ownership-overlap`, `delivery.incomplete`,
`delivery.invalid-commit`, and `delivery.unknown-commit`.

Historical unmarked documents remain authoritative but are unsupported by this
checker. Review manually or normalize their formatting when that change is in
scope, preserving decisions, evidence and approval state. Merely adding the
marker does not convert unsupported declaration styles into valid v1 syntax.
No bulk migration or extra approval gate is implied by a format correction.
The checker proves structural consistency only; it cannot infer missing business
decisions or establish that prose or implementation satisfies an invariant.

The reusable wave implementation is `scripts/spec_coder_checks/waves.py`.
`inspect_waves(tickets, waves)` returns source-independent findings;
`validate_planned_waves(tickets, waves)` preserves the existing normalized-tuple
or `ValueError` API. The test helper delegates to this implementation, with no
second copy of the partition/dependency/conflict rules.
