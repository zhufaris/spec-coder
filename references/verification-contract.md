# Verification evidence contract

## Authority and lifecycle

Baseline evidence is an observation, not an approval, a completion claim or a
replacement for review. Main runs the first preflight baseline and observes its
actual command/result. During that same uninterrupted request, planning may
reuse each required command's matching record. Main identifies the reused
`record_id` and confirms the declared build-cache, dependency and environment
observations remain current. A successful subset never substitutes for all
required commands.

Resume/new execution contexts run their baseline freshly. Integrated-ticket
checks run freshly on the accepted integrated state. Delivery runs the full
applicable suite freshly. Neither a planning cache hit nor a worker's result
satisfies those requirements. Missing tools, uncertain inputs or rejected
records fall back to the real project verification command with the reason
reported. The tool does not dispatch a fallback, approve gates, modify tickets,
stage, commit or contact a service.

## Planning reuse interface

On normal `plan-coder` entry, the prepared baseline's exact capture JSON remains
in conversation until the green baseline permits target-project writes. Main
first writes the specification with every exact capture record that it directly
observed in this uninterrupted request. It then makes an exact, non-executing
`verification-evidence.py check` against that artifact for each baseline with
the same command and observations. Continue only when every check is `reusable`
with `record_id`; partial success never qualifies.

```text
python3 /absolute/plugin/scripts/verification-evidence.py check --repo REPO \
  --cwd CWD --request REQUEST --artifact ARTIFACT \
  [--exclude-output OUTPUT ...] --toolchain JSON --dependencies JSON \
  --environment JSON --build-cache ABSOLUTE_CACHE -- COMMAND ...
```

All values and the command vector after `--` exactly match the established
baseline; repeat `--exclude-output` for each exact generated output.

Writing the record does not make it eligible: main must still confirm its
current-request provenance and reaffirm that the declared dependency and
environment observations remain current. The check neither runs a project
command nor authorizes retry. For standalone,
resume, malformed/uncertain record or observation, or `rerun`, load
**Verification fallback** in `plan-coder` and establish verification freshly
under the complete CLI, schema, comparison/exit, and invocation owners.

## CLI and explicit observations

Use Python 3 and Git, with no package installation. Resolve the script from the
plugin installation; it imports its own bundled modules regardless of the target
project's current directory:

```text
python3 /absolute/plugin/scripts/verification-evidence.py capture|check \
  --repo /absolute/physical/repository \
  --cwd /absolute/physical/repository/working-directory \
  --request CURRENT_UNINTERRUPTED_REQUEST_ID \
  --artifact docs/spec-coder/specs/active.md \
  [--exclude-output exact-generated-file ...] \
  --toolchain '{"python":"observed executable and version"}' \
  --dependencies '{"installed":"observed installed state","external":"none"}' \
  --environment '{"RELEVANT_NONSECRET_VARIABLE":"observed value"}' \
  --build-cache /absolute/physical/repository/.cache/branch/target \
  -- command argument ...
```

| Input | Contract |
| --- | --- |
| `--repo` | Physical Git worktree root; it must exist. |
| `--cwd` | Existing directory inside that worktree; command execution occurs here. |
| `--request` | Main's identity for the current uninterrupted request. Change it on resume; never recover a cache hit by copying an old identity. |
| `--artifact` | One exact active Markdown specification or plan inside the repository. Relative paths resolve from `--repo`, not `--cwd`. Capture excludes it; check reads records from it. |
| `--exclude-output` | Repeat for exact generated evidence/log output files inside the repository. Relative paths resolve from `--repo`. Never use it for source inputs. |
| `--toolchain` | Nonempty JSON object of nonempty observed identity strings, such as executable path and version. |
| `--dependencies` | JSON object with nonempty `installed` and `external` strings. Identify the confirmed installed state and relevant external state, or use `external: "none"` when no external state is relevant. Extra non-secret observation strings are allowed. |
| `--environment` | JSON object of relevant non-secret observed strings. `{}` explicitly declares that no additional environment inputs are relevant; it is not an automatic environment inspection. Empty variable values are allowed. |
| `--build-cache` | Canonical, ignored `<physical-repo>/.cache/<current-branch>/target`; capture and check require exact equality. |
| After `--` | The complete, currently expected command argument vector, supplied explicitly for both operations. |

Main obtains these observations from the established project verification
preflight. They are caller-supplied assertions about observed context. Repeating
the same text cannot prove package installations, ignored inputs, tool binaries
or external services have remained unchanged. A lockfile alone does not confirm
installed dependencies. Account for relevant ignored/local inputs in the
observations; if their state cannot be confirmed, use `unknown` and rerun.
Do not include secrets in arguments or JSON. The tool does not inspect credentials
or dump the process environment, and declarations do not set environment values
for the child process.

Missing required CLI options are usage errors. Empty/unknown request, toolchain
or dependency observations, missing `installed`/`external`, non-string values,
and uncertain environment observations cannot be reused. The case-insensitive
words `unknown`, `unconfirmed`, and `unavailable`, including inside longer
observation strings, and a trimmed value of `?` are reserved uncertainty
sentinels across request, toolchain, dependencies, and environment. They
conservatively cause cache misses even when an environment variable literally
contains such a value. An explicit environment `{}` and genuinely empty string
variable values remain valid; whitespace-only observations are uncertain.
Capture can still run an explicitly supplied baseline when these observations
are uncertain; it emits a nonreusable record even if the child exits zero.
Check returns `rerun` without executing the command. Malformed JSON,
invalid paths, unsafe exclusions or an unsafe/unignored/incompatible build cache
are rejected before command execution.

## Capture and record schema

`capture` runs the supplied argument vector with `shell=False`. No implicit shell
expansion, dependency installation, network request or document command lookup
occurs. Child stdout and stderr remain visible on the CLI's stderr; stdout is
reserved for one JSON record. The child inherits the current process environment.
Authority for the explicit command remains with main and the user task.

Each version 1 record contains:

| Field | Meaning |
| --- | --- |
| `version` | Integer `1`. |
| `record_id` | Unique 32-character lowercase hexadecimal observation identity. |
| `context` | Request identity, exact command argument list, exact exclusion paths, exact build-cache reservation, and declared toolchain/dependencies/environment. |
| `before`, `after` | Workspace observations taken before and after command execution, each with `inputs` and an `uncertainty` list. |
| `exit_code` | Actual child exit status; negative statuses represent signals. `null` means execution could not start. |
| `observed_at` | Timezone-qualified UTC observation time after the attempt; it is not a TTL. |
| `status` | `captured` for successful stable complete evidence, otherwise `rerun`. |
| `reasons` | Empty for a successful capture; otherwise explanations of uncertainty/failure/change. |

Workspace inputs include resolved repository/working-directory paths and their
filesystem identities, Git-directory identity, HEAD, semantic index entries and
flags, tracked files, and nonignored untracked files. File content uses SHA-256;
file modes and symlink identity are included. Manifests, lockfiles and test/build
configuration in that tracked/nonignored set are ordinary content inputs.
The cache path is context; ignored cache contents are not source evidence.
Internal file symlinks include resolved target content/mode. Broken/external
symlinks, nonregular files, submodules (including absent working trees), Git/read
failures or unreadable files produce uncertainty and never a cache hit.

This is a conservative snapshot, not continuous filesystem monitoring or a proof
of external freshness. It cannot detect a change that is fully restored between
snapshots, and it does not recursively inventory ignored dependency trees. Main
must not reuse evidence when it knows of relevant changes or uncertainty, even
if the comparison says `reusable`.

Exclude only the active artifact and explicitly named generated outputs needed
to prevent self-invalidation. Exclusions reject directories, globs, `..`, `.git`
paths and symlinks/symlink parents. Output exclusions cannot hide tracked files.
A tracked Markdown artifact must have an active standalone
`<!-- spec-coder:artifact-v1 spec -->` or
`<!-- spec-coder:artifact-v1 plan -->` marker. Markers in fenced examples or HTML
comments do not qualify. An ordinary tracked `README.md` cannot be excluded as
an artifact. Ignored/untracked active docs may be created during the request;
main remains responsible for their declared role. Index and HEAD changes still
invalidate evidence, even when a changed index entry belongs to the artifact.

A failed command, failure to start, caught interruption or persistent input change
during execution produces nonreusable evidence. Abrupt process termination may
leave no complete record; absence/partial JSON is also never reusable. Existing
old success records must not be substituted for a newer failed attempt.

## Comparison and exit behavior

`check` reads active `spec-coder-verification` fenced JSON blocks from the supplied
artifact and captures the current workspace. It requires exactly one record for
the currently expected command; retain different commands as separate blocks,
and replace a superseded attempt rather than retaining ambiguous duplicates.
Nested fenced examples and HTML-commented blocks do not count. Malformed JSON,
duplicate JSON keys, malformed/unclosed evidence fences, missing/invalid fields,
failed records or uncertainty return `rerun`. The supported syntax is a standalone
labeled fence, not arbitrary Markdown/HTML embeddings.

Comparison requires exact build-cache equality, the same remaining explicit context, and stable matching workspace
observations. Output JSON contains `status: "reusable"` or `status: "rerun"`,
`reasons`, and the matching `record_id` when available. The tool never executes
commands read from a document or the command supplied to `check`. It never edits
the artifact or Git state. A human-edited/forged record is not authenticated by a
hash, record ID, successful comparison or a recorded exit code. Only a record
main actually observed in this request is eligible for planning reuse.

| Exit | Capture | Check |
| --- | --- | --- |
| `0` | Command succeeded and produced stable complete evidence. | Exactly one eligible matching record is reusable. |
| `1` | Command failed, observation was uncertain/unstable, or usable evidence could not be produced. Inspect `exit_code`/`reasons` when a record exists. | Rerun is required; JSON explains why. |
| `2` | CLI syntax/required-option error, before execution. | CLI syntax/required-option error. |

The command's own exit status is recorded, not used as the CLI exit status.
A successful baseline can therefore have CLI exit `1` when its evidence cannot
be reused. This does not authorize an automatic retry of a side-effecting command.

## Worked invocation

For a Python-only repository whose established baseline is unittest discovery,
main first confirms its interpreter, installed dependencies and relevant
environment. Substitute real observations and an identity for this request:

```sh
python3 /absolute/plugin/scripts/verification-evidence.py capture \
  --repo /absolute/project --cwd /absolute/project \
  --request request-2026-10-08-a \
  --artifact docs/spec-coder/specs/active.md \
  --toolchain '{"python":"/usr/bin/python3; observed version 3.11"}' \
  --dependencies '{"installed":"stdlib-only; confirmed by main","external":"none"}' \
  --environment '{"PYTHONDONTWRITEBYTECODE":"1"}' \
  --build-cache /absolute/project/.cache/feat/example/target \
  -- /usr/bin/python3 -B -m unittest discover -s tests
```

The active artifact may be a future path: do not create it before the first
green baseline. Retain stdout JSON in conversation until artifact writing is
permitted; capture does not require the file to exist. Keep the same active
artifact/exclusions during comparison, because moving a record changes context.

Main observes the visible output and CLI/command results, then copies the exact
stdout JSON into the existing active specification or plan:

````markdown
```spec-coder-verification
{ the complete JSON object emitted by capture }
```
````

That placeholder is explanatory, not valid evidence. Do not invent record fields.
If redirecting stdout to an intermediate evidence file, declare that exact file
with `--exclude-output` in both capture and check; keep the authoritative record
in the existing artifact, not a private cache. Preserve stderr visibility.

At planning, invoke the same arguments with `check` instead of `capture`, after
main reaffirms the observations. `reusable` identifies the record and avoids a
duplicate command run. On `rerun`, execute the established verification freshly
and retain the new observed result. The integration and delivery phases always
run their required checks freshly, regardless of this planning result.
