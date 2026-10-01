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

    def test_manifest_is_minimal_and_complete(self) -> None:
        manifest = json.loads(read_text(ROOT / ".codex-plugin" / "plugin.json"))
        self.assertEqual(manifest["name"], "spec-coder")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["interface"]["displayName"], "Spec Coder")
        self.assertNotIn("TO" + "DO", json.dumps(manifest))

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

    def test_grill_coder_contract(self) -> None:
        text = self.assert_skill_contract("grill-coder", ("grilling",))
        self.assertIn("one question at a time", text.lower())
        self.assertIn("recommend", text.lower())
        self.assertIn("original checkout", text.lower())

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


if __name__ == "__main__":
    unittest.main()
