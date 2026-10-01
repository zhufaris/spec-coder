import json
import os
import re
import shutil
import subprocess
import tempfile
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
    "show-me",
    "using-git-worktrees",
    "setup-coder",
}
DESIGN_STAGES = ("grill-coder", "design-coder", "plan-coder", "tdd-coder", "delivery-coder")
DESIGN_REFERENCE = "../../references/domain-design-contract.md"
EXAMPLE_REFERENCE = "../../references/domain-design-examples.md"
PLANNING_REFERENCES = (
    "../../references/specification-template.md",
    "../../references/ticket-template.md",
)
APPROVAL_REFERENCE = "../../references/approval-review-contract.md"
SETUP_REFERENCE = "../../references/setup-contract.md"
SETUP_ASSET = "../../assets/agents-snippet.md"


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
        self.assertEqual(manifest["version"], "0.3.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["interface"]["displayName"], "Spec Coder")
        self.assertNotIn("TO" + "DO", json.dumps(manifest))

    def test_codex_marketplace_exposes_root_plugin(self) -> None:
        marketplace = json.loads(
            read_text(ROOT / ".agents" / "plugins" / "marketplace.json")
        )
        self.assertEqual(marketplace["name"], "spec-coder")
        self.assertEqual(len(marketplace["plugins"]), 1)
        plugin = marketplace["plugins"][0]
        self.assertEqual(plugin["name"], "spec-coder")
        self.assertEqual(plugin["source"], {"source": "local", "path": "."})
        self.assertEqual(plugin["policy"]["installation"], "AVAILABLE")
        self.assertEqual(plugin["policy"]["products"], ["CODEX"])

    def test_codex_cli_installs_plugin_in_isolated_home(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex, "codex must be available on PATH")

        with tempfile.TemporaryDirectory(prefix="spec-coder-codex-") as codex_home:
            env = os.environ | {"CODEX_HOME": codex_home}
            subprocess.run(
                [codex, "plugin", "marketplace", "add", str(ROOT)],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            installation = json.loads(
                subprocess.run(
                    [
                        codex,
                        "plugin",
                        "add",
                        "spec-coder@spec-coder",
                        "--json",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env,
                ).stdout
            )
            marketplaces = json.loads(
                subprocess.run(
                    [codex, "plugin", "marketplace", "list", "--json"],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env,
                ).stdout
            )
            plugins = json.loads(
                subprocess.run(
                    [codex, "plugin", "list", "--json"],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env,
                ).stdout
            )

            self.assertEqual(
                [marketplace["name"] for marketplace in marketplaces["marketplaces"]],
                ["spec-coder"],
            )
            installed = plugins["installed"]
            self.assertEqual(len(installed), 1)
            self.assertEqual(installed[0]["pluginId"], "spec-coder@spec-coder")
            self.assertTrue(installed[0]["installed"])
            self.assertTrue(installed[0]["enabled"])
            self.assertEqual(installation["pluginId"], "spec-coder@spec-coder")
            manifest = json.loads(read_text(ROOT / ".codex-plugin" / "plugin.json"))
            self.assertEqual(installed[0]["version"], manifest["version"])
            installed_root = Path(installation["installedPath"])
            self.assertEqual(
                json.loads(read_text(installed_root / ".codex-plugin" / "plugin.json")),
                manifest,
            )

            installed_skills = {
                path.parent.name
                for path in (Path(installation["installedPath"]) / "skills").glob(
                    "*/SKILL.md"
                )
            }
            self.assertEqual(installed_skills, EXPECTED_SKILLS)
            for directory in ("skills", "references"):
                for source in (ROOT / directory).rglob("*"):
                    if not source.is_file():
                        continue
                    relative = source.relative_to(ROOT)
                    with self.subTest(installed_file=str(relative)):
                        target = installed_root / relative
                        self.assertTrue(
                            target.resolve().is_relative_to(installed_root.resolve())
                        )
                        self.assertTrue(target.is_file())
                        self.assertEqual(target.read_bytes(), source.read_bytes())
            self.assert_domain_reference_resolves(installed_root)
            self.assert_planning_templates_resolve(installed_root)
            self.assert_approval_reference_resolves(installed_root)
            self.assert_setup_reference_resolves(installed_root)
            notice = installed_root / "THIRD_PARTY_NOTICES.md"
            self.assertTrue(notice.is_file())
            self.assertEqual(
                notice.read_bytes(), (ROOT / "THIRD_PARTY_NOTICES.md").read_bytes()
            )

    def assert_planning_templates_resolve(self, root: Path) -> None:
        skill = root / "skills" / "plan-coder" / "SKILL.md"
        links = re.findall(r"\]\(([^)]+)\)", read_text(skill))
        for link in PLANNING_REFERENCES:
            with self.subTest(template=link):
                self.assertIn(link, links)
                target = (skill.parent / link).resolve()
                self.assertTrue(target.is_relative_to(root.resolve()))
                self.assertTrue(target.is_file())

    def assert_approval_reference_resolves(self, root: Path) -> None:
        for skill_name in (
            "show-me",
            "using-git-worktrees",
            "design-coder",
            "plan-coder",
        ):
            with self.subTest(skill=skill_name):
                skill = root / "skills" / skill_name / "SKILL.md"
                links = re.findall(r"\]\(([^)]+)\)", read_text(skill))
                self.assertIn(APPROVAL_REFERENCE, links)
                target = (skill.parent / APPROVAL_REFERENCE).resolve()
                self.assertTrue(target.is_relative_to(root.resolve()))
                self.assertTrue(target.is_file())

    def assert_setup_reference_resolves(self, root: Path) -> None:
        skill = root / "skills" / "setup-coder" / "SKILL.md"
        links = re.findall(r"\]\(([^)]+)\)", read_text(skill))
        self.assertIn(SETUP_REFERENCE, links)
        self.assertIn(SETUP_ASSET, links)
        for link in (SETUP_REFERENCE, SETUP_ASSET):
            target = (skill.parent / link).resolve()
            self.assertTrue(target.is_relative_to(root.resolve()))
            self.assertTrue(target.is_file())

    def test_declared_dependencies_match_model_visible_host_fixture(self) -> None:
        catalog = json.loads(read_text(ROOT / "tests/fixtures/host-skill-catalog.json"))
        compatibility = read_text(ROOT / "references/upstream-compatibility.md")
        capability_map = compatibility.split("## Capability Map\n", 1)[1].split(
            "\n## ", 1
        )[0]
        declared = {
            name
            for line in capability_map.splitlines()
            if line.startswith("- ") and " -> " in line
            for name in re.findall(r"`([^`]+)`", line.split(" -> ", 1)[0])
        }
        self.assertTrue(declared, "no declared upstream capabilities found")
        visible = set(catalog["model_visible"])
        self.assertEqual(declared - visible, set(), "upstream absent from Host catalog")
        self.assertFalse(declared & set(catalog["manual_only"]))
        for skill in (ROOT / "skills").glob("*/SKILL.md"):
            self.assertNotEqual(
                parse_frontmatter(skill).get("disable-model-invocation", "false").lower(),
                "true",
                f"suite stage is manual-only: {skill}",
            )

    def assert_domain_reference_resolves(self, root: Path) -> None:
        for stage in DESIGN_STAGES:
            with self.subTest(stage=stage):
                skill = root / "skills" / stage / "SKILL.md"
                links = re.findall(r"\]\(([^)]+)\)", read_text(skill))
                for link in (DESIGN_REFERENCE, EXAMPLE_REFERENCE):
                    with self.subTest(reference=link):
                        self.assertIn(link, links)
                        reference = (skill.parent / link).resolve()
                        self.assertTrue(reference.is_relative_to(root.resolve()))
                        self.assertTrue(reference.is_file())
                        self.assertEqual(
                            read_text(reference),
                            read_text(ROOT / "references" / reference.name),
                        )

    def test_domain_reference_is_available_to_every_design_stage(self) -> None:
        self.assert_domain_reference_resolves(ROOT)

    def test_approval_review_is_available_at_every_gate(self) -> None:
        self.assert_approval_reference_resolves(ROOT)
        workflow = read_text(ROOT / "references" / "workflow-contract.md")
        design = read_text(ROOT / "skills" / "design-coder" / "SKILL.md")
        plan = read_text(ROOT / "skills" / "plan-coder" / "SKILL.md")
        orchestrator = read_text(ROOT / "skills" / "spec-coder" / "SKILL.md")

        for text in (workflow, design, plan, orchestrator):
            self.assertIn("`show-me`", text)
        for gate in ("Gate 1", "Gate 2", "Gate 3"):
            self.assertIn(gate, workflow)
        normalized_workflow = " ".join(workflow.lower().split())
        for phrase in (
            "reopened gate",
            "artifact or exact proposed mutation",
            "explicit approval question",
        ):
            self.assertIn(phrase, normalized_workflow)

    def test_show_me_contract_is_ascii_only_and_non_authorizing(self) -> None:
        path = ROOT / "skills" / "show-me" / "SKILL.md"
        fields = parse_frontmatter(path)
        self.assertEqual(fields["name"], "show-me")
        self.assertIn("approval", fields["description"].lower())
        self.assertNotEqual(
            fields.get("disable-model-invocation", "false").lower(), "true"
        )
        text = read_text(path)
        contract = read_text(ROOT / "references" / "approval-review-contract.md")
        metadata = read_text(path.parent / "agents" / "openai.yaml")

        for heading in ("## Input", "## Output", "## Process", "## Stop Conditions"):
            self.assertIn(heading, text)
        for field in (
            "approval kind",
            "artifact or exact proposed mutation",
            "key decisions",
            "risks or blockers",
            "approval effect",
            "next stage",
        ):
            self.assertIn(field, contract.lower())
        for phrase in (
            "3-7",
            "80 columns",
            "linear fallback",
            "does not grant approval",
            "authoritative artifact or diff",
            "returned gate",
            "exact diff or replacement bytes",
        ):
            self.assertIn(phrase, contract.lower())
        for dependency in ("tmux", "neovim", "browser", "external executable"):
            self.assertIn(f"must not require {dependency}", contract.lower())
        self.assertIn('$show-me', metadata)
        self.assertIn('display_name: "Show Me"', metadata)

        notice = read_text(ROOT / "THIRD_PARTY_NOTICES.md")
        for phrase in (
            "mbailey/show-me",
            "Copyright (c) 2024 Mike Bailey",
            "MIT License",
        ):
            self.assertIn(phrase, notice)

    def test_bundled_worktree_contract_is_safe_and_optional(self) -> None:
        path = ROOT / "skills" / "using-git-worktrees" / "SKILL.md"
        fields = parse_frontmatter(path)
        self.assertEqual(fields["name"], "using-git-worktrees")
        self.assertIn("isolation", fields["description"].lower())
        self.assertNotEqual(
            fields.get("disable-model-invocation", "false").lower(), "true"
        )
        text = read_text(path)
        metadata = read_text(path.parent / "agents" / "openai.yaml")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")
        normalized = " ".join(text.lower().split())

        for heading in ("## Input", "## Output", "## Process", "## Stop Conditions"):
            self.assertIn(heading, text)
        for phrase in (
            "git rev-parse --git-dir",
            "git rev-parse --git-common-dir",
            "git rev-parse --show-superproject-working-tree",
            "enter_worktree",
            "exit_worktree",
            "git worktree add",
            "detached head",
            "permission",
            "optional",
            "in-place",
            "`.gitignore`",
            "`show-me`",
            "plan-coder owns dependency preparation and baseline verification",
            "do not create a commit",
            "linked-worktree candidate",
            "`0` means ignored",
            "`1` means definitively not ignored",
            "approved mutation pending",
            "committed `.gitignore` base",
        ):
            self.assertIn(phrase, normalized)
        self.assertLess(normalized.index("enter_worktree"), normalized.index("git worktree add"))
        self.assertIn('$using-git-worktrees', metadata)
        self.assertIn('display_name: "Using Git Worktrees"', metadata)

        capability_map = compatibility.split("## Capability Map\n", 1)[1].split(
            "\n## ", 1
        )[0]
        bundled = compatibility.split("## Bundled Capabilities\n", 1)[1].split(
            "\n## ", 1
        )[0]
        self.assertNotIn("`using-git-worktrees`", capability_map)
        self.assertIn("`using-git-worktrees`", bundled)

        notice = read_text(ROOT / "THIRD_PARTY_NOTICES.md")
        for phrase in (
            "obra/superpowers",
            "Copyright (c) 2025 Jesse Vincent",
            "MIT License",
        ):
            self.assertIn(phrase, notice)

    def test_setup_coder_contract_is_local_idempotent_and_guarded(self) -> None:
        text = self.assert_skill_contract("setup-coder", ("show-me",))
        self.assert_setup_reference_resolves(ROOT)
        contract = read_text(ROOT / "references" / "setup-contract.md")
        metadata = read_text(ROOT / "skills" / "setup-coder" / "agents" / "openai.yaml")
        normalized = " ".join((text + "\n" + contract).lower().split())

        for phrase in (
            "repository-local",
            "explicit global",
            "ready",
            "warning",
            "blocked",
            "absent",
            "current",
            "stale",
            "malformed",
            "duplicated",
            "byte-for-byte",
            "exact diff",
            "re-read",
            "unchanged base",
            "zero diff",
            "disable-model-invocation",
            "executed",
            "discovered",
            "agents.md",
            "readme",
            "contributing",
            "makefile",
            "ci workflow",
            "do not install dependencies",
            "do not create a worktree",
            "do not create a specification",
            "do not stage",
            "do not commit",
            "do not persist the setup report",
            "pending approval",
            "## repository verification",
            "unbalanced",
            "two or more complete, ordered, disjoint pairs",
            "stale compatible global",
            "not assessable from supplied evidence",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn('display_name: "Setup Coder"', metadata)
        self.assertIn('$setup-coder', metadata)

        routing = read_text(ROOT / "assets" / "agents-snippet.md")
        self.assertIn("<!-- spec-coder:start -->", routing)
        self.assertIn("<!-- spec-coder:end -->", routing)
        self.assertFalse((ROOT / "assets" / "global-agents-snippet.md").exists())

        workflow = read_text(ROOT / "references" / "workflow-contract.md")
        self.assertIn("## Repository Setup", workflow)
        self.assertIn("[setup contract](./setup-contract.md)", workflow.lower())

    def test_maintainer_docs_are_repository_ignored(self) -> None:
        ignore_rules = read_text(ROOT / ".gitignore").splitlines()
        self.assertIn("/docs/", ignore_rules)

    def test_shared_references_define_required_contracts(self) -> None:
        workflow = read_text(ROOT / "references" / "workflow-contract.md")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")
        routing = read_text(ROOT / "assets" / "agents-snippet.md")

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
        text = self.assert_skill_contract("plan-coder", ("using-git-worktrees",))
        self.assert_planning_templates_resolve(ROOT)
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

    def test_required_scenarios_are_documented(self) -> None:
        scenarios = read_text(ROOT / "tests" / "fixtures" / "scenarios.md")
        headings = (
            "## New feature",
            "## Resume from approved spec",
            "## Resume partial tickets",
            "## Failing baseline",
            "## Dirty original checkout",
            "## Failing ticket test",
            "## Failing final suite",
            "## Focused in-place change",
            "## Reuse existing worktree",
            "## Optional isolation capability missing",
            "## Required isolation unavailable",
            "## Failing in-place baseline",
            "## Overlapping user changes",
        )
        for heading in headings:
            self.assertIn(heading, scenarios)
        approval_headings = (
            "## Approval review at a main gate",
            "## Reopened gate review",
            "## Approval review fallback",
        )
        for heading in approval_headings:
            self.assertIn(heading, scenarios)
        approval_section = scenarios.split(approval_headings[0], 1)[1]
        for phrase in (
            "ReviewSnapshot",
            "authoritative artifact",
            "does not grant approval",
            "linear ASCII",
        ):
            self.assertIn(phrase, approval_section)

        worktree_headings = (
            "## Linked worktree detection",
            "## Submodule is not a linked worktree",
            "## Native worktree tool precedence",
            "## Git worktree fallback safety",
        )
        for heading in worktree_headings:
            self.assertIn(heading, scenarios)

        setup_headings = (
            "## First repository setup",
            "## Idempotent setup rerun",
            "## Stale managed block",
            "## Malformed managed markers",
            "## Concurrent AGENTS change",
            "## Missing required setup capability",
            "## Optional setup warning",
            "## Verification command discovery",
            "## Explicit global setup",
            "## Setup forbidden side effects",
        )
        for heading in setup_headings:
            self.assertIn(heading, scenarios)
        for field in ("Starting state:", "Expected route:", "Forbidden action:"):
            self.assertEqual(
                scenarios.count(field),
                len(headings)
                + len(approval_headings)
                + len(worktree_headings)
                + len(setup_headings),
            )

    def test_repository_is_self_describing_and_installable(self) -> None:
        readme = read_text(ROOT / "README.md")
        install_guide = read_text(ROOT / "INSTALL.md")
        installer = read_text(ROOT / "scripts" / "install-local.sh")
        validator = read_text(ROOT / "scripts" / "validate.sh")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")

        for skill in EXPECTED_SKILLS:
            self.assertIn(f"`{skill}`", readme)
        self.assertEqual(len(EXPECTED_SKILLS), 9)
        for published_doc in (readme, install_guide, compatibility):
            self.assertIn("0.3.0", published_doc)
        self.assertNotIn("0.2.1", "\n".join((install_guide, compatibility)))
        self.assertIn("九个 skill", readme)
        self.assertIn("九个 skill", install_guide)
        self.assertNotRegex(readme, r"(?i)trax")
        self.assertNotIn("global-agents-snippet.md", readme + install_guide)
        self.assertIn("codex plugin marketplace add", readme)
        self.assertIn("codex plugin add spec-coder@spec-coder", readme)
        self.assertIn('codex plugin marketplace add "$REPO_ROOT"', installer)
        self.assertIn("codex plugin add spec-coder@spec-coder", installer)
        self.assertIn("CODEX_HOME", validator)
        self.assertIn("quick_validate.py", validator)
        self.assertIn("tests/test_contracts.py", validator)
        published_install_surface = "\n".join(
            (readme, install_guide, installer, validator, compatibility)
        )
        self.assertNotRegex(
            published_install_surface, r"(?i)traecode|traecli|~/\.trae"
        )


if __name__ == "__main__":
    unittest.main()
