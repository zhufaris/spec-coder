"""Validate actual entry-to-owner links, without assuming prior stage context."""
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)]+)\)")
TRIGGERS = {"Human review", "Delegation", "Model examples", "Isolation",
            "Setup audit or mutation", "Reopened gate or mutation",
            "Parallel worker allocation", "Domain behavior", "Persistence",
            "Interactions", "Architecture"}


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
    for line in conditional.splitlines():
        match = re.match(r"- \*\*(.+?):\*\*", line)
        if match and match[1] in triggers:
            reading += "\n" + line
    return LINK.findall(reading)


def instruction_text(path: Path, triggers=TRIGGERS) -> str:
    """Selected stage plus only explicitly required/triggered owner sections."""
    text = path.read_text(encoding="utf-8")
    if path.name != "SKILL.md":
        return text
    for link in dict.fromkeys(required_links(path, triggers)):
        relative, _, anchor = link.partition("#")
        target = (path.parent / relative).resolve()
        content = target.read_text(encoding="utf-8")
        text += "\n" + (section(content, anchor) if anchor else content)
    return text


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
            links = required_links(path)
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
        active = required_links(orchestration, {"Delegation"})
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
            links = required_links(ROOT / "skills" / stage / "SKILL.md", {"Delegation"})
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
