"""Validate actual entry-to-owner links, without assuming prior stage context."""
import re
import tempfile
import unittest
from pathlib import Path

from task_playbook_contracts import PlaybookKind, select_playbook, validate_selection

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)]+)\)")
TRIGGERS = {"Human review", "Delegation", "Model examples", "Isolation",
            "Setup audit or mutation", "Reopened gate or mutation",
            "Parallel worker allocation", "Domain behavior", "Persistence",
            "Interactions", "Architecture", "Shared mutable state", "Verification fallback",
            "Workspace preparation", "Selected Task Playbook", "Gate transition",
            "Dispatch assembly", "Executor handoff and recovery"}
TRIGGERS |= {"Change sizing", "Domain language", "Behavior preservation",
             "Context pressure", "Completion", "Recurring instruction failure",
             "Repeated repair failure", "Reader load", "Measurement"}
PLAYBOOK_KINDS = ("Feature", "Bug Fix", "Refactor", "Performance",
                  "Skill Change", "Workflow Eval", "Generic")
PLAYBOOK_CASES = {
    PlaybookKind.FEATURE: {"new-user-outcome"},
    PlaybookKind.BUG_FIX: {"reproduced-defect"},
    PlaybookKind.REFACTOR: {"behavior-preserving"},
    PlaybookKind.PERFORMANCE: {"repeatable-performance-baseline"},
    PlaybookKind.SKILL_CHANGE: {"skill-instruction-change"},
    PlaybookKind.WORKFLOW_EVAL: {"standalone-evaluation"},
    PlaybookKind.GENERIC: set(),
}


def section(text: str, anchor: str) -> str:
    headings = list(re.finditer(r"(?m)^(#{1,6}) (.+)$", text))
    for index, heading in enumerate(headings):
        slug = re.sub(r"[^\w -]", "", heading[2].lower()).replace(" ", "-")
        if slug != anchor:
            continue
        end = len(text)
        for following in headings[index + 1:]:
            if len(following[1]) <= len(heading[1]):
                end = following.start()
                break
        return text[heading.start():end]
    raise AssertionError(f"unresolved section #{anchor}")


def required_links(path: Path, triggers=frozenset()) -> list[str]:
    text = path.read_text(encoding="utf-8")
    reading = section(text, "required-reading")
    conditional = section(text, "conditional-reading")
    blocks = re.finditer(
        r"(?ms)^- \*\*(.+?):\*\*.*?(?=^- \*\*|^## |\Z)",
        conditional,
    )
    for block in blocks:
        if block[1] in triggers:
            reading += "\n" + block[0]
    return LINK.findall(reading) + principle_links(skill_text(path), triggers)


def principle_links(text, triggers):
    links = []
    for block in re.finditer(r"(?ms)^- \*\*(.+?):\*\*.*?(?=^- \*\*|^#{1,6} |\Z)", text):
        if block[1] in triggers:
            links.extend(link for link in LINK.findall(block[0]) if "principles/" in link)
    return links


def skill_text(path: Path) -> str:
    """Inspect a compatibility entry together with its one declared SOP owner."""
    text = path.read_text(encoding="utf-8")
    if path.name == "SKILL.md":
        for link in dict.fromkeys(LINK.findall(text)):
            if "playbooks/stages/" not in link:
                continue
            relative, _, anchor = link.partition("#")
            target = (path.parent / relative).resolve()
            text += "\n" + section(target.read_text(encoding="utf-8"), anchor)
    return text


def instruction_text(path: Path, triggers=TRIGGERS) -> str:
    """Selected stage plus only explicitly required/triggered owner sections."""
    text = skill_text(path)
    if path.name != "SKILL.md":
        return text
    for link in dict.fromkeys(required_links(path, triggers)):
        if "playbooks/stages/" in link:
            continue
        relative, _, anchor = link.partition("#")
        target = (path.parent / relative).resolve()
        content = target.read_text(encoding="utf-8")
        text += "\n" + (section(content, anchor) if anchor else content)
    return text


def selected_instruction_text(path: Path, selection, *, mode="orchestrated",
                              handoff=None, triggers=frozenset()) -> str:
    """Static scope analysis of router versus stage entry; not a Host executor."""
    if not validate_selection(selection):
        raise ValueError("return to router: invalid selection")
    text = instruction_text(path, triggers | {"Selected Task Playbook"})
    if path.parent.name == "spec-coder":
        relative, _, anchor = selection.conditional_references[0].partition("#")
        target = (path.parent / relative).resolve()
        return text + "\n" + section(target.read_text(encoding="utf-8"), anchor)
    stage_link = next(link for link in required_links(path) if "playbooks/stages/" in link)
    stage = Path(stage_link.split("#")[0]).stem
    if mode not in {"orchestrated", "standalone", "resume"}:
        raise ValueError("unknown entry mode")
    if handoff is None:
        if mode == "orchestrated":
            raise ValueError("return to router: missing current-step handoff")
        relative, _, anchor = selection.conditional_references[0].partition("#")
        target = (path.parent / relative).resolve()
        import runpy
        extractor = runpy.run_path(str(target.parents[2] / "scripts/task-step.py"))["extract_step"]
        packet = extractor(target.read_text(encoding="utf-8"), stage)
        step = packet["step"]
        constraints = "\n".join(packet["constraints"])
        handoff = {"kind": selection.kind, "stage": stage,
                   "step": step, "constraints": constraints}
    if (handoff.get("kind") != selection.kind or handoff.get("stage") != stage
            or not handoff.get("step") or not handoff.get("constraints")):
        raise ValueError("return to router: conflicting current-step handoff")
    return text + "\n" + handoff["step"] + "\n" + handoff["constraints"]


def run_instruction_text(stages, selection, triggers=frozenset()) -> str:
    """Separate reuse metric; never proof of Host runtime deduplication."""
    chunks = []
    seen = set()
    for path in stages:
        chunks.append(path.read_text(encoding="utf-8"))
        for link in dict.fromkeys(required_links(path, triggers | {"Selected Task Playbook"})):
            relative, _, anchor = link.partition("#")
            target = (path.parent / relative).resolve()
            identity = (target, anchor)
            if identity not in seen:
                seen.add(identity)
                content = target.read_text(encoding="utf-8")
                loaded = section(content, anchor) if anchor else content
                chunks.append(loaded)
    relative, _, anchor = selection.conditional_references[0].partition("#")
    target = (stages[0].parent / relative).resolve()
    task = section(target.read_text(encoding="utf-8"), anchor)
    chunks.append(task)
    for link in principle_links(task, triggers):
        relative, _, anchor = link.partition("#")
        target = (stages[0].parent / relative).resolve()
        identity = (target, anchor)
        if identity not in seen:
            seen.add(identity)
            content = target.read_text(encoding="utf-8")
            chunks.append(section(content, anchor) if anchor else content)
    return "\n".join(chunks)


class StageLoadingTests(unittest.TestCase):
    def test_every_stage_has_standalone_required_sections(self):
        for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(stage=path.parent.name):
                text = path.read_text()
                for heading in ("Input", "Output", "Process", "Stop Conditions",
                                "Required Reading", "Conditional Reading"):
                    self.assertIn("## " + heading, text)
                self.assertIn("standalone invocation and resume", text)
                links = required_links(path)
                self.assertTrue(links)
                for link in links:
                    self.assertIn("#", link, "mandatory reading must name a section")
                for link in required_links(path, TRIGGERS):
                    relative, _, anchor = link.partition("#")
                    target = (path.parent / relative).resolve()
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.is_file(), link)
                    if anchor:
                        section(target.read_text(), anchor)

    def test_authority_and_domain_owners_are_reachable_on_direct_entry(self):
        for stage in ("spec-coder", "grill-coder", "design-coder", "plan-coder",
                      "tdd-coder", "delivery-coder"):
            path = ROOT / "skills" / stage / "SKILL.md"
            links = (
                required_links(path, {"Gate transition"})
                if stage == "spec-coder"
                else required_links(path)
            )
            self.assertIn("../../references/workflow-contract.md#approval-gates", links)
            self.assertIn("../../references/workflow-contract.md#failure-transitions", links)
            if stage != "spec-coder":
                self.assertIn("../../references/domain-design-contract.md#discover-and-evolve-domain-language", links)
        for stage in ("design-coder", "plan-coder", "tdd-coder", "delivery-coder"):
            links = required_links(ROOT / "skills" / stage / "SKILL.md",
                                   {"Domain behavior", "Persistence", "Interactions", "Architecture"})
            for anchor in ("protect-behavior-and-valid-values", "aggregate-persistence-semantics",
                           "consistency-and-interaction-contracts", "architecture-that-can-be-verified"):
                self.assertIn("../../references/domain-design-contract.md#" + anchor, links)

    def test_conditional_loading_does_not_load_dispatch_during_discovery(self):
        discovery = ROOT / "skills/grill-coder/SKILL.md"
        self.assertFalse(any("subagent-routing" in p for p in required_links(discovery)))
        orchestration = ROOT / "skills/spec-coder/SKILL.md"
        self.assertFalse(any("#worker-progress-heartbeat" in p for p in required_links(orchestration)))
        active = required_links(orchestration, {"Dispatch assembly"})
        self.assertIn("../../references/subagent-routing-contract.md#worker-progress-heartbeat", active)
        self.assertFalse(any("approval-review" in p for p in active))
        design = ROOT / "skills/design-coder/SKILL.md"
        self.assertFalse(any("#aggregate-persistence-semantics" in p for p in required_links(design)))
        self.assertIn("../../references/domain-design-contract.md#aggregate-persistence-semantics",
                      required_links(design, {"Persistence"}))
        human = required_links(orchestration, {"Human review"})
        self.assertIn("../../references/approval-review-contract.md#review-snapshot", human)

    def test_every_dispatch_loads_owners_and_complete_brief(self):
        for stage in ("spec-coder", "tdd-coder", "delivery-coder"):
            triggers = (
                {"Delegation", "Dispatch assembly"}
                if stage == "spec-coder"
                else {"Delegation"}
            )
            links = required_links(ROOT / "skills" / stage / "SKILL.md", triggers)
            for anchor in ("authority", "delegation-eligibility-and-execution-mode",
                           "explicit-parallel-requests", "worker-progress-heartbeat",
                           "attempt-evidence-and-promotion", "result-integration"):
                self.assertIn("../../references/subagent-routing-contract.md#" + anchor, links)
            for anchor in ("assembly", "common-brief", "role-additions"):
                self.assertIn("../../references/worker-brief-template.md#" + anchor, links)

    def test_missing_owner_anchor_is_a_failure_not_a_silent_full_file_load(self):
        with self.assertRaisesRegex(AssertionError, "unresolved section"):
            section("## Authority\nOnly main may approve.\n", "missing-owner")

    def test_unlinked_rules_cannot_satisfy_reachability(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "owner.md").write_text("## Loaded\nOne rule.\n## Hidden\nNo spawning.\n")
            stage = root / "SKILL.md"
            stage.write_text("## Required Reading\n[x](owner.md#loaded)\n## Conditional Reading\n")
            resolved = instruction_text(stage)
            self.assertIn("One rule.", resolved)
            self.assertNotIn("No spawning.", resolved)

    def test_multiline_conditional_links_are_loaded_as_one_trigger_block(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "owner.md").write_text("## Loaded\nPreparation rules.\n")
            stage = root / "SKILL.md"
            stage.write_text(
                "## Required Reading\n\n"
                "## Conditional Reading\n\n"
                "- **Workspace preparation:** before a write, load\n"
                "  [Preparation rules](owner.md#loaded).\n"
            )
            self.assertIn(
                "owner.md#loaded",
                required_links(stage, {"Workspace preparation"}),
            )

    def test_fresh_context_common_brief_and_role_constraints(self):
        template = (ROOT / "references/worker-brief-template.md").read_text()
        common = section(template, "common-brief")
        roles = section(template, "role-additions")
        for role in ("Implementation", "Reviewer", "Promotion"):
            match = re.search(r"(?ms)^- \*\*" + role + r":\*\*.*?(?=^- \*\*|\Z)", roles)
            self.assertIsNotNone(match)
            # No prior conversation or external reference is used to inspect this brief.
            brief = common + match[0]
            for constraint in ("delegation_allowed = false", "must_not_spawn = true",
                               "directly or indirectly", "must not stage or commit",
                               "Mutation ownership:", "Exclusions:", "Verification seam:",
                               "ProgressSnapshot", "45-60 seconds", "observed_at",
                               "before or at dispatch", "complete task-owned diff",
                               "provisional evidence", "completion authority"):
                self.assertIn(constraint, brief)
            if role == "Reviewer":
                self.assertIn("read-only; no edits", brief)
                self.assertIn("axis = {standards |", brief)
            if role == "Promotion":
                self.assertIn("exactly", brief)
                self.assertIn("promoted reviewer is read-only", brief)
                self.assertIn("Heartbeat delay alone never authorizes promotion", brief)

    def test_resolved_required_owner_budgets(self):
        budgets = {
            "spec-coder": 6500,
            "grill-coder": 4000,
            "design-coder": 5000,
            "plan-coder": 5800,
            "tdd-coder": 7000,
            "delivery-coder": 8000,
        }
        counts = {}
        for stage, budget in budgets.items():
            path = ROOT / "skills" / stage / "SKILL.md"
            counts[stage] = len(instruction_text(path, frozenset()).split())
            with self.subTest(stage=stage):
                self.assertLessEqual(counts[stage], budget)
        self.assertLess(sum(counts.values()), 22500)

    def test_runtime_compaction_targets_and_conditional_non_growth(self):
        stages = (
            "spec-coder",
            "grill-coder",
            "design-coder",
            "plan-coder",
            "tdd-coder",
            "delivery-coder",
        )
        normal = {
            stage: len(
                instruction_text(
                    ROOT / "skills" / stage / "SKILL.md", frozenset()
                ).split()
            )
            for stage in stages
        }
        all_trigger_limits = {
            "spec-coder": 8489,
            "grill-coder": 5419,
            "design-coder": 6969,
            "plan-coder": 11105,
            "tdd-coder": 11091,
            "delivery-coder": 11606,
        }

        self.assertLessEqual(sum(normal.values()), 19000)
        self.assertLessEqual(normal["plan-coder"], 5200)
        for stage, limit in all_trigger_limits.items():
            with self.subTest(stage=stage):
                triggered = len(
                    instruction_text(ROOT / "skills" / stage / "SKILL.md").split()
                )
                self.assertLessEqual(triggered, limit)

    def test_selected_playbook_loading_is_direct_and_excludes_other_anchors(self):
        expected = {
            "spec-coder": {"route-precedence-and-one-selection-rule", "conversational-todo-boundary"},
            "grill-coder": {"taskplaybookselection", "empirical-facts-and-human-decisions"},
            "design-coder": {"taskplaybookselection", "empirical-facts-and-human-decisions"},
            "plan-coder": {"taskplaybookselection"},
            "tdd-coder": {"taskplaybookselection"},
            "delivery-coder": {"taskplaybookselection"},
        }
        forbidden = {"conditional-loading-intent", "blinded-evaluation-constraints", "pstack-provenance-and-nondependency"}
        for stage, anchors in expected.items():
            path = ROOT / "skills" / stage / "SKILL.md"
            normal = required_links(path)
            selected = required_links(path, {"Selected Task Playbook"})
            normal_playbook = {link for link in normal if "task-playbook-contract" in link}
            selected_playbook = {link for link in selected if "task-playbook-contract" in link}
            with self.subTest(stage=stage):
                self.assertFalse(normal_playbook)
                self.assertEqual({link.rsplit("#", 1)[1] for link in selected_playbook}, anchors)
                self.assertTrue(forbidden.isdisjoint({link.rsplit("#", 1)[1] for link in selected_playbook}))

        stage_paths = [ROOT / "skills" / stage / "SKILL.md" for stage in expected]
        all_anchors = {kind.value.lower().replace(" ", "-") + "-playbook" for kind in PLAYBOOK_CASES}
        for kind, facts in PLAYBOOK_CASES.items():
            selection = select_playbook(request="change", facts=facts)
            selected_anchor = selection.conditional_references[0].rsplit("#", 1)[1]
            for path in stage_paths:
                resolved = selected_instruction_text(path, selection, mode="standalone").lower()
                with self.subTest(stage=path.parent.name, kind=kind):
                    if path.parent.name == "spec-coder":
                        self.assertIn("## " + selected_anchor.replace("-", " "), resolved)
                    else:
                        self.assertNotIn("### Completion", resolved)
                        self.assertIn("- delivery proof:", resolved)
                    for absent in all_anchors - {selected_anchor}:
                        self.assertNotIn("## " + absent.replace("-", " "), resolved)

    def test_normal_and_each_selected_route_have_measured_context(self):
        stages = ("spec-coder", "grill-coder", "design-coder", "plan-coder", "tdd-coder", "delivery-coder")
        normal = sum(len(instruction_text(ROOT / "skills" / stage / "SKILL.md", frozenset()).split()) for stage in stages)
        self.assertLessEqual(normal, 19000)
        route_counts = {}
        observed = {
            PlaybookKind.FEATURE: {"Domain behavior"},
            PlaybookKind.BUG_FIX: {"Change sizing", "Repeated repair failure"},
            PlaybookKind.REFACTOR: {"Reader load"},
            PlaybookKind.PERFORMANCE: {"Measurement"},
            PlaybookKind.SKILL_CHANGE: {"Recurring instruction failure"},
            PlaybookKind.WORKFLOW_EVAL: {"Measurement"},
            PlaybookKind.GENERIC: set(),
        }
        for kind, facts in PLAYBOOK_CASES.items():
            selection = select_playbook(request="change", facts=facts)
            route_counts[kind.value] = len(run_instruction_text(
                [ROOT / "skills" / stage / "SKILL.md" for stage in stages], selection, observed[kind]
            ).split())
        self.assertEqual(set(route_counts), set(PLAYBOOK_KINDS))
        self.assertTrue(all(count > 0 for count in route_counts.values()))
        self.assertTrue(all(count <= 20000 for count in route_counts.values()))
        self.assertGreater(len(set(route_counts.values())), 1)

    def test_plan_coder_verification_fallback_owns_detailed_contract(self):
        path = ROOT / "skills/plan-coder/SKILL.md"
        normal = required_links(path)
        compact = "../../references/verification-contract.md#planning-reuse-interface"
        detailed = (
            "cli-and-explicit-observations",
            "capture-and-record-schema",
            "comparison-and-exit-behavior",
            "worked-invocation",
        )
        self.assertIn(compact, normal)
        for anchor in detailed:
            self.assertNotIn("../../references/verification-contract.md#" + anchor, normal)

        fallback = required_links(path, {"Verification fallback"})
        for anchor in detailed:
            self.assertIn("../../references/verification-contract.md#" + anchor, fallback)

    def test_spec_coder_loads_detailed_verification_only_for_preparation(self):
        path = ROOT / "skills/spec-coder/SKILL.md"
        detailed = (
            "cli-and-explicit-observations",
            "capture-and-record-schema",
            "comparison-and-exit-behavior",
            "worked-invocation",
        )
        normal = required_links(path)
        prepared = required_links(path, {"Workspace preparation"})
        for anchor in detailed:
            link = "../../references/verification-contract.md#" + anchor
            self.assertNotIn(link, normal)
            self.assertIn(link, prepared)

    def test_redundant_executor_owner_is_absent_from_distribution(self):
        old_owner = ROOT / "references/implement-spec-execution-contract.md"
        self.assertFalse(old_owner.exists())
        distributed = [ROOT / "README.md", ROOT / "INSTALL.md"]
        distributed.extend((ROOT / "skills").glob("*/SKILL.md"))
        distributed.extend((ROOT / "references").glob("*.md"))
        for path in distributed:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotIn(
                    "implement-spec-execution-contract.md",
                    path.read_text(),
                )

    def test_ticket_tdd_names_the_affected_validation_interface(self):
        for relative in (
            "skills/tdd-coder/SKILL.md",
            "references/ticket-template.md",
        ):
            text = skill_text(ROOT / relative)
            with self.subTest(path=relative):
                for token in ("scripts/validate-affected.py", "--repo", "--path"):
                    self.assertIn(token, text)

    def test_exact_plan_checker_commands_name_repository_context(self):
        required = {
            ROOT / "references/ticket-template.md",
            ROOT / "references/workflow-contract.md",
            ROOT / "playbooks/stages/planning.md",
        }
        observed = set()
        sources = list((ROOT / "references").glob("*.md"))
        sources.extend((ROOT / "skills").glob("*/SKILL.md"))
        sources.extend((ROOT / "playbooks/stages").glob("*.md"))
        for path in sources:
            for paragraph in re.split(r"\n\s*\n", path.read_text()):
                command = re.sub(r"\s+", " ", paragraph.replace("\\\n", " "))
                if not all(
                    token in command
                    for token in (
                        "check-artifacts.py",
                        "--phase plan",
                        "--spec",
                        "--plan",
                    )
                ):
                    continue
                observed.add(path)
                self.assertIn("--repo", command, path.relative_to(ROOT))
        self.assertTrue(required.issubset(observed), required - observed)

    def test_readme_artifact_summary_names_explicit_target_repository(self):
        summary = section(
            (ROOT / "README.md").read_text(),
            "baseline-evidence-and-artifact-checks",
        )
        for token in ("--phase plan", "--phase delivery", "--repo", "explicit target"):
            self.assertIn(token, summary)

    def test_legacy_execution_wave_oracle_is_removed(self):
        oracle = (ROOT / "tests/forward_contracts.py").read_text()
        self.assertNotIn("def select_execution_wave(", oracle)

    def test_prompt_reduction_is_material(self):
        # Approved 502fa87 baseline: 9781 words across the nine stage entrypoints.
        words = sum(len(path.read_text().split()) for path in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertLess(words, 9781)
        for stage in ("spec-coder", "tdd-coder", "delivery-coder"):
            raw = (ROOT / "skills" / stage / "SKILL.md").read_text()
            self.assertNotIn("every 45-60 seconds", raw)
            self.assertNotIn("timezone-aware ISO", raw)


if __name__ == "__main__":
    unittest.main()
