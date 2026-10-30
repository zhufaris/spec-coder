"""Exercise source ownership and actual loading for the three-layer design."""
import re
import unittest
import tempfile
import shutil
from pathlib import Path

from task_playbook_contracts import PlaybookKind, select_playbook
from test_stage_loading import LINK, section, run_instruction_text

ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    "grill-coder": "discovery",
    "design-coder": "design",
    "plan-coder": "planning",
    "tdd-coder": "implementation",
    "delivery-coder": "delivery",
}


class ThreeLayerArchitectureTests(unittest.TestCase):
    def test_stage_sop_has_one_owner_and_skill_is_a_thin_entry(self):
        for skill, stage in STAGES.items():
            with self.subTest(stage=stage):
                entry = (ROOT / f"skills/{skill}/SKILL.md").read_text()
                owner = ROOT / f"playbooks/stages/{stage}.md"
                self.assertTrue(owner.is_file())
                self.assertIn(f"../../playbooks/stages/{stage}.md#procedure", entry)
                process = entry.split("## Process\n", 1)[1].split("\n## ", 1)[0]
                self.assertNotRegex(process, r"(?m)^\d+\. ")
                self.assertRegex(owner.read_text(), r"(?m)^\d+\. ")
                self.assertIn("### Capabilities", owner.read_text())

    def test_selected_task_file_owns_explicit_stage_composition(self):
        for kind in PlaybookKind:
            fact = {
                "Feature": "new-user-outcome", "Bug Fix": "reproduced-defect",
                "Refactor": "behavior-preserving", "Performance": "repeatable-performance-baseline",
                "Skill Change": "skill-instruction-change", "Workflow Eval": "standalone-evaluation",
                "Generic": "none",
            }[kind.value]
            selection = select_playbook(request="change", facts={fact} if kind != PlaybookKind.GENERIC else set())
            relative, anchor = selection.conditional_references[0].split("#")
            with self.subTest(kind=kind):
                self.assertIn("playbooks/tasks/", relative)
                task = (ROOT / "skills/spec-coder" / relative).resolve()
                self.assertTrue(task.is_file())
                content = task.read_text()
                self.assertIn("### Procedure", content)
                self.assertIn("### Completion", content)
                self.assertEqual(len(re.findall(r"\]\(../stages/", content)), 5)
                self.assertIn("principles/", content)

    def test_principles_are_triggered_rules_with_no_execution_authority(self):
        principles = list((ROOT / "principles").glob("*.md"))
        self.assertGreaterEqual(len(principles), 6)
        for path in principles:
            with self.subTest(principle=path.name):
                text = path.read_text()
                for heading in ("## Applies when", "## Rule", "## Limits"):
                    self.assertIn(heading, text)
                self.assertNotIn("SKILL.md", str(path))
                self.assertNotIn("## Process", text)

    def test_all_new_resource_links_resolve_inside_a_relocated_bundle(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary) / "plugin"
            for directory in ("skills", "principles", "playbooks", "references"):
                shutil.copytree(ROOT / directory, bundle / directory)
            for path in (bundle / "playbooks").rglob("*.md"):
                for link in LINK.findall(path.read_text()):
                    if "://" in link:
                        continue
                    relative, _, anchor = link.partition("#")
                    target = (path.parent / relative).resolve()
                    self.assertTrue(target.is_relative_to(bundle))
                    self.assertTrue(target.is_file(), (path, link))
                    if anchor:
                        section(target.read_text(), anchor)

    def test_unique_source_reuse_metric_counts_one_task_and_each_stage_once(self):
        selected = select_playbook(request="repair", facts={"reproduced-defect"})
        paths = [ROOT / f"skills/{name}/SKILL.md" for name in ("spec-coder", *STAGES)]
        text = run_instruction_text(paths, selected)
        self.assertEqual(text.count("## Bug Fix playbook"), 1)
        self.assertNotIn("## Feature playbook", text)
        self.assertEqual(len(re.findall(r"(?m)^## Procedure$", text)), 5)
        self.assertIn("### Scope and authority", text)
        self.assertIn("reproduce the exact reported entry path", text)

    def test_untriggered_human_review_principle_is_not_loaded(self):
        selected = select_playbook(request="repair", facts={"reproduced-defect"})
        paths = [ROOT / f"skills/{name}/SKILL.md" for name in ("spec-coder", *STAGES)]
        text = run_instruction_text(paths, selected)
        self.assertNotRegex(text, r"(?m)^# Protect human authority$")
        sized = run_instruction_text(paths, selected, {"Change sizing"})
        self.assertRegex(sized, r"(?m)^# Subtract before adding$")
        self.assertNotRegex(text, r"(?m)^# Subtract before adding$")

    def test_current_stage_loads_only_observed_principles_and_no_sibling_sop(self):
        from test_stage_loading import instruction_text
        cases = {
            "grill-coder": ("Domain language", "Model the domain"),
            "design-coder": ("Architecture", "Dependency direction"),
            "plan-coder": ("Context pressure", "Guard the context"),
            "tdd-coder": ("Behavior preservation", "Preserve observable behavior"),
            "delivery-coder": ("Completion", "Verify the real outcome"),
        }
        for skill, (trigger, title) in cases.items():
            with self.subTest(skill=skill):
                path = ROOT / f"skills/{skill}/SKILL.md"
                ordinary = instruction_text(path, frozenset())
                active = instruction_text(path, {trigger})
                self.assertNotIn("# " + title + "\n", ordinary)
                self.assertIn("# " + title + "\n", active)
                self.assertNotIn("## Feature playbook", active)
                self.assertEqual(len(re.findall(r"(?m)^## Procedure$", active)), 1)

    def test_task_specific_principles_load_only_for_selected_observed_triggers(self):
        paths = [ROOT / f"skills/{name}/SKILL.md" for name in ("spec-coder", *STAGES)]
        cases = (
            ("reproduced-defect", "Repeated repair failure", "Attack the premise"),
            ("behavior-preserving", "Reader load", "Minimize reader load"),
            ("repeatable-performance-baseline", "Measurement", "Explain the number"),
            ("standalone-evaluation", "Measurement", "Explain the number"),
        )
        titles = {title for _, _, title in cases}
        for fact, trigger, title in cases:
            with self.subTest(fact=fact):
                selection = select_playbook(request="change", facts={fact})
                ordinary = run_instruction_text(paths, selection)
                active = run_instruction_text(paths, selection, {trigger})
                for candidate in titles:
                    pattern = r"(?m)^# " + re.escape(candidate) + r"$"
                    self.assertNotRegex(ordinary, pattern)
                    if candidate == title:
                        self.assertEqual(len(re.findall(pattern, active)), 1)
                    else:
                        self.assertNotRegex(active, pattern)
                task_headings = re.findall(r"(?m)^## (.+ playbook)$", active)
                self.assertEqual(task_headings, [selection.kind.value + " playbook"])
        generic = select_playbook(request="change", facts=set())
        unrelated = run_instruction_text(paths, generic, {trigger for _, trigger, _ in cases})
        for title in titles:
            self.assertNotRegex(unrelated, r"(?m)^# " + re.escape(title) + r"$")

    def test_shared_state_principle_is_conditional_and_design_owned(self):
        from test_stage_loading import instruction_text
        title = "# Separate before serializing shared state\n"
        design = ROOT / "skills/design-coder/SKILL.md"
        for triggers in (frozenset(), {"Architecture"}, {"Interactions"}):
            with self.subTest(triggers=triggers):
                self.assertNotIn(title, instruction_text(design, triggers))
        active = instruction_text(design, {"Shared mutable state"})
        self.assertEqual(active.count(title), 1)
        self.assertNotIn("## Bug Fix playbook", active)
        self.assertEqual(len(re.findall(r"(?m)^## Procedure$", active)), 1)
        for skill in set(STAGES) - {"design-coder"}:
            with self.subTest(skill=skill):
                self.assertNotIn(title, instruction_text(ROOT / f"skills/{skill}/SKILL.md", {"Shared mutable state"}))

    def test_generic_stage_guarantees_survive_task_trigger_replacement(self):
        from test_stage_loading import principle_links
        paths = [ROOT / f"skills/{name}/SKILL.md" for name in ("spec-coder", *STAGES)]
        cases = (
            ("refactor", "behavior-preserving", "Behavior preservation", "Preserve observable behavior"),
            ("performance", "repeatable-performance-baseline", "Completion", "Verify the real outcome"),
            ("workflow-eval", "standalone-evaluation", "Completion", "Verify the real outcome"),
        )
        for task, fact, trigger, title in cases:
            with self.subTest(task=task):
                text = (ROOT / f"playbooks/tasks/{task}.md").read_text()
                self.assertEqual(principle_links(text, {trigger}), [])
                selection = select_playbook(request="change", facts={fact})
                active = run_instruction_text(paths, selection, {trigger})
                self.assertEqual(len(re.findall(r"(?m)^# " + re.escape(title) + r"$", active)), 1)

    def test_stage_handoff_consumption_and_narrow_reconstruction(self):
        from test_stage_loading import selected_instruction_text
        selected = select_playbook(request="repair", facts={"reproduced-defect"})
        for skill, stage in STAGES.items():
            with self.subTest(stage=stage):
                path = ROOT / f"skills/{skill}/SKILL.md"
                with self.assertRaisesRegex(ValueError, "return to router"):
                    selected_instruction_text(path, selected)
                handoff = {"kind": selected.kind, "stage": stage,
                           "step": "Current task instruction supplied by router.",
                           "constraints": "Verify the original entry path."}
                normal = selected_instruction_text(path, selected, handoff=handoff)
                self.assertIn(handoff["step"], normal)
                self.assertNotIn("## Bug Fix playbook", normal)
                for mode in ("standalone", "resume"):
                    restored = selected_instruction_text(path, selected, mode=mode)
                    self.assertIn(f"](../stages/{stage}.md#procedure)", restored)
                    task_steps = re.findall(r"(?m)^\d+\. \[[^\]]+\]\(../stages/", restored)
                    self.assertEqual(len(task_steps), 1)
                    self.assertNotIn("### Completion", restored)
                    self.assertIn("- Delivery proof:", restored)
                with self.assertRaisesRegex(ValueError, "return to router"):
                    selected_instruction_text(path, selected, handoff={**handoff, "kind": PlaybookKind.FEATURE})

    def test_every_entry_has_contracts_and_can_reconstruct_missing_standalone_handoff(self):
        for skill in STAGES:
            with self.subTest(skill=skill):
                entry = (ROOT / f"skills/{skill}/SKILL.md").read_text()
                self.assertIn("Every entry", entry)
                self.assertIn("reconstruct a missing handoff", entry)
                self.assertIn("step only", entry)
                self.assertIn("without rerouting", entry)
                self.assertNotIn("No nested agent.", entry)
                self.assertIn("children must not spawn", entry)


if __name__ == "__main__":
    unittest.main()
