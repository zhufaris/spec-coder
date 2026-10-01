# Spec Coder Skill Suite Implementation Plan

> **For agentic workers:** Implement this plan task-by-task in the current session. Steps use checkbox (`- [ ]`) syntax for tracking. Do not use subagents unless the user separately authorizes them.

**Goal:** Build and locally install a six-skill `spec-coder` plugin that becomes the user-level default for code-changing requests and turns them into an approved design, isolated plan, TDD implementation, reviewed verification, and atomic commits.

**Architecture:** A thin `spec-coder` orchestrator delegates to five independently invocable stage skills. Each stage composes installed Matt Pocock, Superpowers, and Clean Architecture skills while shared workflow and compatibility rules live in two plugin-level references. Markdown contract tests protect names, dependencies, gates, safety rules, and artifact paths without copying upstream skill bodies.

**Tech Stack:** TraeCode plugin manifest, Markdown `SKILL.md` files, Python 3 standard-library `unittest`, Git, `traecli`.

**Spec:** `docs/superpowers/specs/2026-10-01-spec-coder-design.md`

## Global Constraints

- Expose exactly `spec-coder`, `grill-coder`, `design-coder`, `plan-coder`, `tdd-coder`, and `delivery-coder`.
- Install and enable the plugin at user scope and route code-changing requests through `spec-coder` by default.
- Exclude read-only explanation, status, investigation, and review requests from automatic routing; honor an explicit user opt-out.
- Keep every wrapper thin; reference upstream skills by name and do not copy their complete instructions.
- Use only locally supported skill frontmatter fields: `name`, `description`, `license`, `allowed-tools`, and `metadata`.
- Require explicit approval for the selected design, written spec, and ticket set before implementation.
- Use adaptive lightweight DDD and Clean Architecture; introduce tactical patterns only when justified.
- Never write target-project artifacts before an isolated worktree exists.
- Never push, create a PR, or publish external tickets without separate explicit authorization.
- Never commit after failed verification, amend pre-existing commits, or stage unrelated files.
- Do not introduce a private workflow state file; recover from Git, the spec, and the plan.
- Do not use subagents by default.

## Review Focus

- Existing dirty checkout: leave it unchanged and create or reuse safe isolation.
- Missing or changed upstream skill: stop with a compatibility error instead of approximating behavior.
- Failing baseline: preserve evidence and stop before generating implementation commits.
- Interrupted ticket: infer the current phase from plan checkboxes and Git, then rerun relevant verification.
- Full-suite failure after ticket commits: return to TDD and withhold the completion claim.

---

### Task 1: Create the plugin manifest and contract-test foundation

**Files:**

- Create: `.codex-plugin/plugin.json`
- Create: `tests/test_contracts.py`
- Generated: `skills/` directory

**Interfaces:**

- Produces: a discoverable plugin named `spec-coder` with `skills: "./skills/"`.
- Produces: reusable test helpers `read_text(path)`, `parse_frontmatter(path)`, and `assert_skill_contract(name, dependencies)`.
- Consumes: the approved plugin metadata and six-skill list from the design spec.

- [x] **Step 1: Write the failing manifest test**

Create `tests/test_contracts.py` with this initial test surface:

```python
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "spec-coder",
    "grill-coder",
    "design-coder",
    "plan-coder",
    "tdd-coder",
    "delivery-coder",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise AssertionError(f"missing frontmatter: {path}")
    fields = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip().strip('"')
    return fields


class PluginContractTests(unittest.TestCase):
    def test_manifest_is_minimal_and_complete(self) -> None:
        manifest = json.loads(read_text(ROOT / ".codex-plugin" / "plugin.json"))
        self.assertEqual(manifest["name"], "spec-coder")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["interface"]["displayName"], "Spec Coder")
        self.assertNotIn("TO" + "DO", json.dumps(manifest))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run the test and verify the missing manifest fails**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `.codex-plugin/plugin.json` does not exist.

- [x] **Step 3: Generate the official plugin skeleton**

Run from `/data00/home/feiyu.zhu/work`:

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/plugin-creator/scripts/create_basic_plugin.py \
  spec-coder \
  --path /data00/home/feiyu.zhu/work \
  --with-skills
```

Expected: the existing repository gains `.codex-plugin/plugin.json` and `skills/` without changing the committed design document.

- [x] **Step 4: Replace the scaffold placeholders with the minimal manifest**

Set `.codex-plugin/plugin.json` to:

```json
{
  "name": "spec-coder",
  "version": "0.1.0",
  "description": "A gated specification-to-delivery workflow for coding changes.",
  "author": {
    "name": "feiyu.zhu",
    "email": "feiyu.zhu@bytedance.com"
  },
  "keywords": ["specification", "ddd", "clean-architecture", "tdd"],
  "skills": "./skills/",
  "interface": {
    "displayName": "Spec Coder",
    "shortDescription": "Design, plan, implement, and verify coding changes",
    "longDescription": "Turn coding requests into approved specifications, vertical tickets, test-driven implementation, review, and verified commits.",
    "developerName": "feiyu.zhu",
    "category": "Coding",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": [
      "Use spec-coder to take this feature from requirements to verified commits.",
      "Resume the current spec-coder workflow from its durable artifacts."
    ]
  }
}
```

- [x] **Step 5: Run the manifest test and verify it passes**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: PASS, 1 test.

- [x] **Step 6: Commit the plugin foundation**

```bash
git add .codex-plugin/plugin.json tests/test_contracts.py
git commit -m "chore: scaffold spec-coder plugin"
```

### Task 2: Define shared workflow and upstream contracts

**Files:**

- Create: `references/workflow-contract.md`
- Create: `references/upstream-compatibility.md`
- Create: `assets/global-agents-snippet.md`
- Modify: `tests/test_contracts.py`

**Interfaces:**

- Produces: the normative phase order, three gates, failure transitions, artifact paths, task-state rules, and Git safety policy used by every stage.
- Produces: the validated upstream capability map and compatibility failure behavior.
- Produces: the canonical user-level default-routing instruction.
- Consumes: Superpowers `v6.4.1`, the 2026-10-01 Matt Pocock `main` snapshot, and the matching Clean Architecture `main` snapshot.

- [ ] **Step 1: Add failing shared-reference tests**

Add to `PluginContractTests`:

```python
    def test_shared_references_define_required_contracts(self) -> None:
        workflow = read_text(ROOT / "references" / "workflow-contract.md")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")
        routing = read_text(ROOT / "assets" / "global-agents-snippet.md")

        for heading in (
            "## Phase Order",
            "## Approval Gates",
            "## Artifact Contract",
            "## Git Safety",
            "## Failure Transitions",
            "## Recovery",
        ):
            self.assertIn(heading, workflow)

        for dependency in (
            "grilling",
            "brainstorming",
            "domain-modeling",
            "codebase-design",
            "clean-architecture",
            "using-git-worktrees",
            "to-spec",
            "to-tickets",
            "tdd",
            "code-review",
            "verification-before-completion",
        ):
            self.assertIn(f"`{dependency}`", compatibility)

        for phrase in (
            "use the `spec-coder` skill by default",
            "read-only",
            "skip spec-coder",
        ):
            self.assertIn(phrase, routing.lower())

        self.assertNotIn("TO" + "DO", workflow + compatibility + routing)
```

- [ ] **Step 2: Run the new test and observe the missing references**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `references/workflow-contract.md` does not exist.

- [ ] **Step 3: Write `workflow-contract.md`**

Include the following normative sections and decisions:

- `Phase Order`: `grill-coder -> design-coder -> plan-coder -> tdd-coder -> delivery-coder`.
- `Approval Gates`: approved design, reviewed written spec, approved tickets plus implementation authorization.
- `Artifact Contract`: `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md`, `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`, optional `GLOSSARY.md`, and qualifying `docs/adr/` entries.
- `Git Safety`: isolated worktree before writes, explicit-path staging, no amend of pre-existing commits, no push/PR/external tickets.
- `Failure Transitions`: TDD retry for behavior failures, design rollback for invalidated assumptions, stop on baseline failure, stop after three identical blockers.
- `Recovery`: infer the earliest incomplete phase from the branch/worktree, spec, plan checkboxes, commits, and fresh verification.
- `Default Routing`: use `spec-coder` for code-changing requests, exclude read-only requests, and honor an explicit opt-out.

- [ ] **Step 4: Write `upstream-compatibility.md`**

Record this exact capability map:

```text
grilling -> grill-coder
brainstorming + domain-modeling + codebase-design + clean-architecture -> design-coder
using-git-worktrees + to-spec + to-tickets -> plan-coder
tdd -> tdd-coder
code-review + verification-before-completion -> delivery-coder
```

Record the validated upstream versions and the rule that a missing or materially incompatible dependency stops the workflow with a compatibility error.

- [ ] **Step 5: Write the canonical global AGENTS snippet**

Create `assets/global-agents-snippet.md` with this managed section:

```markdown
<!-- spec-coder:start -->
## Default coding workflow

For requests that create or change code, including features, bug fixes, behavioral changes, and refactors, use the `spec-coder` skill by default. Let it scale artifacts to the task while preserving its approval gates.

Do not automatically invoke `spec-coder` for read-only explanation, status, investigation, or review requests. If the user explicitly says `skip spec-coder` or `directly modify`, bypass this suite and continue under all other applicable instructions and skills.
<!-- spec-coder:end -->
```

- [ ] **Step 6: Run the reference tests**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: PASS, 2 tests.

- [ ] **Step 7: Commit the shared contracts**

```bash
git add references/workflow-contract.md references/upstream-compatibility.md assets/global-agents-snippet.md tests/test_contracts.py
git commit -m "docs: define spec-coder workflow contracts"
```

### Task 3: Implement `grill-coder`

**Files:**

- Create: `skills/grill-coder/SKILL.md`
- Create: `skills/grill-coder/agents/openai.yaml`
- Modify: `tests/test_contracts.py`

**Interfaces:**

- Consumes: a user request, repository evidence, prior specs, glossary, and ADRs.
- Produces: dependency-ordered confirmed decisions in conversation context, or durable glossary/ADR updates only when already in a safe worktree.
- Upstream dependency: `grilling`.

- [ ] **Step 1: Add a reusable skill assertion and failing `grill-coder` test**

Add this helper and test:

```python
    def assert_skill_contract(self, name: str, dependencies: tuple[str, ...]) -> str:
        path = ROOT / "skills" / name / "SKILL.md"
        fields = parse_frontmatter(path)
        self.assertEqual(fields["name"], name)
        self.assertIn("description", fields)
        self.assertTrue(name.endswith("-coder"))
        text = read_text(path)
        for heading in ("## Input", "## Output", "## Process", "## Stop Conditions"):
            self.assertIn(heading, text)
        for dependency in dependencies:
            self.assertIn(f"`{dependency}`", text)
        self.assertIn("../../references/workflow-contract.md", text)
        return text

    def test_grill_coder_contract(self) -> None:
        text = self.assert_skill_contract("grill-coder", ("grilling",))
        self.assertIn("one question at a time", text.lower())
        self.assertIn("recommend", text.lower())
        self.assertIn("original checkout", text.lower())
```

- [ ] **Step 2: Run the focused test and observe failure**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `skills/grill-coder/SKILL.md` does not exist.

- [ ] **Step 3: Initialize `grill-coder` with the official skill script**

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/init_skill.py \
  grill-coder --path skills \
  --interface 'display_name=Grill Coder' \
  --interface 'short_description=Interrogate requirements with recommended answers' \
  --interface 'default_prompt=Use $grill-coder to stress-test this coding request.'
```

- [ ] **Step 4: Replace the generated skill body with the approved contract**

Use only `name` and `description` in frontmatter. Include `Input`, `Output`, `Process`, and `Stop Conditions`. Require repository-first inspection, one question at a time, a recommendation with every question, explicit integration of each answer, and no writes to the original checkout. Link the shared workflow contract and invoke `grilling` rather than copying it.

- [ ] **Step 5: Validate and run the focused contract test**

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-coder
python3 -m unittest -v tests.test_contracts.PluginContractTests.test_grill_coder_contract
```

Expected: both commands pass.

- [ ] **Step 6: Commit `grill-coder`**

```bash
git add skills/grill-coder tests/test_contracts.py
git commit -m "feat: add requirements grilling stage"
```

### Task 4: Implement `design-coder`

**Files:**

- Create: `skills/design-coder/SKILL.md`
- Create: `skills/design-coder/agents/openai.yaml`
- Modify: `tests/test_contracts.py`

**Interfaces:**

- Consumes: decisions confirmed by `grill-coder` and repository architecture evidence.
- Produces: an approved in-conversation design containing alternatives, domain language, boundaries, dependency direction, public seams, and acceptance criteria.
- Upstream dependencies: `brainstorming`, `domain-modeling`, `codebase-design`, and `clean-architecture`.

- [ ] **Step 1: Add the failing `design-coder` contract test**

```python
    def test_design_coder_contract(self) -> None:
        text = self.assert_skill_contract(
            "design-coder",
            ("brainstorming", "domain-modeling", "codebase-design", "clean-architecture"),
        )
        self.assertIn("2-3", text)
        self.assertIn("adaptive", text.lower())
        self.assertIn("dependency direction", text.lower())
        self.assertIn("testing seams", text.lower())
        self.assertIn("do not write implementation code", text.lower())
```

- [ ] **Step 2: Run the focused test and observe failure**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `skills/design-coder/SKILL.md` does not exist.

- [ ] **Step 3: Initialize and implement `design-coder`**

Run:

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/init_skill.py \
  design-coder --path skills \
  --interface 'display_name=Design Coder' \
  --interface 'short_description=Compare designs with lightweight DDD and architecture' \
  --interface 'default_prompt=Use $design-coder to design this approved requirement.'
```

Replace the template with a thin contract that:

- presents two or three approaches with a default recommendation;
- requires Gate 1 approval;
- applies domain modeling and Clean Architecture adaptively;
- defines public seams before TDD;
- avoids tactical DDD patterns without evidence;
- returns design content to `plan-coder` without writing implementation code or pre-isolation artifacts.

- [ ] **Step 4: Validate and run tests**

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py skills/design-coder
python3 -m unittest -v tests/test_contracts.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit `design-coder`**

```bash
git add skills/design-coder tests/test_contracts.py
git commit -m "feat: add adaptive architecture design stage"
```

### Task 5: Implement `plan-coder`

**Files:**

- Create: `skills/plan-coder/SKILL.md`
- Create: `skills/plan-coder/agents/openai.yaml`
- Modify: `tests/test_contracts.py`

**Interfaces:**

- Consumes: the Gate 1-approved design.
- Produces: an isolated worktree, green baseline evidence, reviewed local spec, approved vertical-ticket plan, and implementation authorization.
- Upstream dependencies: `using-git-worktrees`, `to-spec`, and `to-tickets`.

- [ ] **Step 1: Add the failing `plan-coder` contract test**

```python
    def test_plan_coder_contract(self) -> None:
        text = self.assert_skill_contract(
            "plan-coder", ("using-git-worktrees", "to-spec", "to-tickets")
        )
        worktree = text.lower().index("worktree")
        spec = text.lower().index("write the specification")
        tickets = text.lower().index("vertical tickets")
        self.assertLess(worktree, spec)
        self.assertLess(spec, tickets)
        self.assertIn("baseline", text.lower())
        self.assertIn("external issue", text.lower())
```

- [ ] **Step 2: Run the focused test and observe failure**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `skills/plan-coder/SKILL.md` does not exist.

- [ ] **Step 3: Initialize and implement `plan-coder`**

Run:

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/init_skill.py \
  plan-coder --path skills \
  --interface 'display_name=Plan Coder' \
  --interface 'short_description=Create isolation, specs, and vertical implementation tickets' \
  --interface 'default_prompt=Use $plan-coder to prepare this approved design for implementation.'
```

Replace the template with an ordered process that:

1. detects existing worktree isolation;
2. creates a native worktree when needed;
3. prepares dependencies and runs baseline tests;
4. stops with evidence on a failing baseline;
5. invokes `to-spec` but writes `docs/spec-coder/specs/YYYY-MM-DD-<slug>.md` locally;
6. pauses for Gate 2 review;
7. invokes `to-tickets` but writes one durable checklist at `docs/spec-coder/plans/YYYY-MM-DD-<slug>.md`;
8. pauses for Gate 3 approval and execution authorization.

State explicitly that external issue publication requires separate authorization.

- [ ] **Step 4: Validate and run tests**

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py skills/plan-coder
python3 -m unittest -v tests/test_contracts.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit `plan-coder`**

```bash
git add skills/plan-coder tests/test_contracts.py
git commit -m "feat: add isolated planning stage"
```

### Task 6: Implement `tdd-coder`

**Files:**

- Create: `skills/tdd-coder/SKILL.md`
- Create: `skills/tdd-coder/agents/openai.yaml`
- Modify: `tests/test_contracts.py`

**Interfaces:**

- Consumes: one approved ticket with all blockers complete and pre-agreed public testing seams.
- Produces: observed Red and Green evidence, passing affected checks, an updated ticket checkbox, and one atomic Conventional Commit.
- Upstream dependency: `tdd`.

- [ ] **Step 1: Add the failing `tdd-coder` contract test**

```python
    def test_tdd_coder_contract(self) -> None:
        text = self.assert_skill_contract("tdd-coder", ("tdd",))
        for phrase in (
            "one unblocked ticket",
            "observe the expected failure",
            "minimum implementation",
            "affected checks",
            "explicit paths",
            "conventional commit",
        ):
            self.assertIn(phrase, text.lower())
        self.assertIn("git add -A", text)
```

- [ ] **Step 2: Run the focused test and observe failure**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `skills/tdd-coder/SKILL.md` does not exist.

- [ ] **Step 3: Initialize and implement `tdd-coder`**

Run:

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/init_skill.py \
  tdd-coder --path skills \
  --interface 'display_name=TDD Coder' \
  --interface 'short_description=Implement one approved ticket through a strict TDD loop' \
  --interface 'default_prompt=Use $tdd-coder to implement the next unblocked ticket.'
```

Replace the template with the fixed cycle from the design spec. Make the prohibition explicit: never run `git add -A`; stage only ticket-owned paths. Require the ticket's affected test, lint, type-check, and build commands before marking it complete and committing.

- [ ] **Step 4: Validate and run tests**

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py skills/tdd-coder
python3 -m unittest -v tests/test_contracts.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit `tdd-coder`**

```bash
git add skills/tdd-coder tests/test_contracts.py
git commit -m "feat: add ticket-level TDD stage"
```

### Task 7: Implement `delivery-coder`

**Files:**

- Create: `skills/delivery-coder/SKILL.md`
- Create: `skills/delivery-coder/agents/openai.yaml`
- Modify: `tests/test_contracts.py`

**Interfaces:**

- Consumes: all completed ticket commits, the approved spec and plan, and current repository verification commands.
- Produces: review findings, TDD-backed repairs when required, fresh full-suite evidence, any final atomic fix commit, and the completion report.
- Upstream dependencies: `code-review` and `verification-before-completion`.

- [ ] **Step 1: Add the failing `delivery-coder` contract test**

```python
    def test_delivery_coder_contract(self) -> None:
        text = self.assert_skill_contract(
            "delivery-coder", ("code-review", "verification-before-completion")
        )
        for phrase in (
            "specification",
            "domain language",
            "dependency direction",
            "full test",
            "fresh evidence",
            "do not push",
        ):
            self.assertIn(phrase, text.lower())
        self.assertIn("tdd-coder", text)
```

- [ ] **Step 2: Run the focused test and observe failure**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `skills/delivery-coder/SKILL.md` does not exist.

- [ ] **Step 3: Initialize and implement `delivery-coder`**

Run:

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/init_skill.py \
  delivery-coder --path skills \
  --interface 'display_name=Delivery Coder' \
  --interface 'short_description=Review changes and require fresh full-suite evidence' \
  --interface 'default_prompt=Use $delivery-coder to review and verify this completed plan.'
```

Replace the template with an ordered review-before-verification process. Require findings-first review against the spec, plan, domain language, architecture boundaries, and diff. Route behavior defects through `tdd-coder`; permit structural refactoring only under passing behavior tests. Run all applicable full test, lint, type-check, and build commands freshly before completion. Prohibit push, PR creation, and external publication.

- [ ] **Step 4: Validate and run tests**

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py skills/delivery-coder
python3 -m unittest -v tests/test_contracts.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit `delivery-coder`**

```bash
git add skills/delivery-coder tests/test_contracts.py
git commit -m "feat: add reviewed delivery stage"
```

### Task 8: Implement the `spec-coder` orchestrator

**Files:**

- Create: `skills/spec-coder/SKILL.md`
- Create: `skills/spec-coder/agents/openai.yaml`
- Modify: `tests/test_contracts.py`

**Interfaces:**

- Consumes: a new coding request or an existing repository with partial `spec-coder` artifacts.
- Produces: routing to the earliest incomplete phase and a terminal result from `delivery-coder`.
- Depends on: all five local stage skills and the shared workflow contract.

- [ ] **Step 1: Add failing suite and recovery tests**

```python
    def test_exact_skill_set_exists(self) -> None:
        actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
        self.assertEqual(actual, EXPECTED_SKILLS)

    def test_spec_coder_orchestration_contract(self) -> None:
        text = self.assert_skill_contract(
            "spec-coder",
            (
                "grill-coder",
                "design-coder",
                "plan-coder",
                "tdd-coder",
                "delivery-coder",
            ),
        )
        for phrase in (
            "earliest incomplete phase",
            "current branch",
            "plan checkboxes",
            "git log",
            "fresh verification",
            "three consecutive",
        ):
            self.assertIn(phrase, text.lower())
        self.assertNotIn("state.yaml", text.lower())
```

- [ ] **Step 2: Run both focused tests and observe failure**

```bash
python3 -m unittest -v tests/test_contracts.py
```

Expected: FAIL because `skills/spec-coder/SKILL.md` does not exist and the skill set is incomplete.

- [ ] **Step 3: Initialize and implement `spec-coder`**

Run:

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/init_skill.py \
  spec-coder --path skills \
  --interface 'display_name=Spec Coder' \
  --interface 'short_description=Run a gated workflow from requirements to verified commits' \
  --interface 'default_prompt=Use $spec-coder to take this coding request through verified commits.'
```

Replace the template with:

- new-request detection that starts at `grill-coder`;
- recovery inspection using Git, spec, plan checkboxes, commits, and fresh verification;
- the fixed five-stage order;
- all three human gates;
- one-active-ticket execution;
- failure routing and the three-identical-blocker stop condition;
- a rule to stop on missing or incompatible upstream skills;
- a terminal completion condition reachable only through `delivery-coder`.

- [ ] **Step 4: Validate and run the complete contract suite**

```bash
python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py skills/spec-coder
python3 -m unittest -v tests/test_contracts.py
```

Expected: all contract tests pass and exactly six skill directories exist.

- [ ] **Step 5: Commit the orchestrator**

```bash
git add skills/spec-coder tests/test_contracts.py
git commit -m "feat: orchestrate the spec-coder workflow"
```

### Task 9: Validate scenarios and install the local plugin

**Files:**

- Create: `tests/fixtures/scenarios.md`
- Modify: `tests/test_contracts.py`
- Modify: `references/upstream-compatibility.md` only if observed installed paths differ from the recorded snapshot.
- Create or update outside the repository: `~/.trae/AGENTS.md`

**Interfaces:**

- Consumes: the complete six-skill plugin and installed upstream skills.
- Produces: structural validation, scenario coverage evidence, an installed and enabled local plugin, an idempotent global default-routing rule, and a clean repository.

- [ ] **Step 1: Add a failing scenario-matrix test**

```python
    def test_required_scenarios_are_documented(self) -> None:
        scenarios = read_text(ROOT / "tests" / "fixtures" / "scenarios.md")
        for heading in (
            "## New feature",
            "## Resume from approved spec",
            "## Resume partial tickets",
            "## Failing baseline",
            "## Dirty original checkout",
            "## Failing ticket test",
            "## Failing final suite",
        ):
            self.assertIn(heading, scenarios)
        for field in ("Starting state:", "Expected route:", "Forbidden action:"):
            self.assertEqual(scenarios.count(field), 7)
```

- [ ] **Step 2: Run the focused test and observe failure**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: FAIL because `tests/fixtures/scenarios.md` does not exist.

- [ ] **Step 3: Write the seven-scenario fixture matrix**

For each required heading, specify one starting repository state, the expected stage route, and one forbidden action. The cases must prove the design's recovery and safety decisions rather than restate generic happy paths.

- [ ] **Step 4: Run all local contract tests**

Run: `python3 -m unittest -v tests/test_contracts.py`

Expected: all tests pass with zero failures and zero errors.

- [ ] **Step 5: Run the official validator for every skill**

```bash
for skill in skills/*; do
  python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```

Expected: six `Skill is valid!` results.

- [ ] **Step 6: Check formatting, placeholders, and repository scope**

```bash
git diff --check
rg -n 'TO''DO|TB''D|\[TO''DO:' .codex-plugin skills references tests
git status --short
```

Expected: `git diff --check` succeeds; the placeholder search returns no matches; status contains only Task 9 files.

- [ ] **Step 7: Commit scenario validation**

```bash
git add tests/fixtures/scenarios.md tests/test_contracts.py references/upstream-compatibility.md
git commit -m "test: cover spec-coder workflow scenarios"
```

If `references/upstream-compatibility.md` did not change, omit it from `git add`.

- [ ] **Step 8: Install and verify the local plugin**

```bash
traecli plugin install /data00/home/feiyu.zhu/work/spec-coder --type local --yes
traecli plugin enable spec-coder@local
traecli plugin list
```

Expected: `spec-coder` appears enabled as a local plugin. Restart TraeCode after installation so the six new skills enter the host catalog.

- [ ] **Step 9: Install the managed global default-routing section**

Read `~/.trae/AGENTS.md` if it exists. Replace only the content from `<!-- spec-coder:start -->` through `<!-- spec-coder:end -->`; otherwise append `assets/global-agents-snippet.md`, preserving every unrelated instruction. Apply the same operation a second time and verify the file is unchanged and contains exactly one start marker and one end marker.

- [ ] **Step 10: Run final repository and installation verification**

```bash
python3 -m unittest -v tests/test_contracts.py
for skill in skills/*; do
  python3 /data00/home/feiyu.zhu/.trae/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
git status --short --branch
git log --oneline --decorate -10
traecli plugin list
rg -n '<!-- spec-coder:(start|end) -->' ~/.trae/AGENTS.md
```

Expected: all tests and validators pass, `spec-coder@local` is enabled, the global AGENTS file contains exactly one managed section, the worktree is clean, and the commit sequence contains one independently reviewable commit per task. After restarting TraeCode, use `/skills` and `/status` to verify that the six skills and global AGENTS instructions are visible.
