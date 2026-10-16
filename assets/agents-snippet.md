<!-- spec-coder:start -->
## Default coding workflow

For requests that create or change code, including features, bug fixes, behavioral changes, and refactors, use the `spec-coder` skill by default. Let it scale artifacts to the task while preserving its approval gates.

Do not automatically invoke `spec-coder` for read-only explanation, status, investigation, or review requests. If the user explicitly says `skip spec-coder` or `directly modify`, bypass this suite and continue under all other applicable instructions and skills.

Repository-local `setup-coder` onboarding may update this managed block and
only the exact root `.gitignore` entries `/.worktrees/` and `/.cache/`, after
one approved multi-target exact-diff review. All other repository instructions
and ignore patterns remain user-owned.
<!-- spec-coder:end -->
