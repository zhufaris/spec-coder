import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from test_stage_loading import instruction_text, skill_text


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
SUBAGENT_ROUTING_REFERENCE = "../../references/subagent-routing-contract.md"


def read_text(path: Path) -> str:
    return skill_text(path)


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
        return instruction_text(path)

    def test_manifest_is_minimal_and_complete(self) -> None:
        manifest = json.loads(read_text(ROOT / ".codex-plugin" / "plugin.json"))
        self.assertEqual(manifest["name"], "spec-coder")
        self.assertEqual(manifest["version"], "0.9.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["interface"]["displayName"], "Spec Coder")
        self.assertNotIn("TO" + "DO", json.dumps(manifest))

    def test_general_subagent_routing_uses_shared_contract(self) -> None:
        routing = read_text(ROOT / "references" / "subagent-routing-contract.md")
        orchestrator = instruction_text(ROOT / "skills" / "spec-coder" / "SKILL.md")
        for phrase in (
            "economy",
            "standard",
            "strong",
            "inherit-main",
            "main-only",
            "minimum_tier",
            "provider",
            "model",
            "live host",
        ):
            self.assertIn(phrase, routing.lower())
        self.assertIn(SUBAGENT_ROUTING_REFERENCE, orchestrator)
        self.assertIn("main-only", orchestrator.lower())
        self.assertEqual(len(EXPECTED_SKILLS), 9)

    def test_subagent_tree_is_limited_to_two_layers(self) -> None:
        routing = read_text(ROOT / "references" / "subagent-routing-contract.md")
        delegating_stages = {
            stage: instruction_text(ROOT / "skills" / stage / "SKILL.md")
            for stage in ("spec-coder", "tdd-coder", "delivery-coder")
        }
        for phrase in (
            "at most two layers",
            "only the active main agent",
            "delegation_allowed = false",
            "indirect",
            "return",
            "sibling",
        ):
            self.assertIn(phrase, routing.lower())
        for stage, text in delegating_stages.items():
            with self.subTest(stage=stage):
                self.assertIn(SUBAGENT_ROUTING_REFERENCE, text)
                self.assertIn("delegation_allowed = false", text.lower())
                self.assertIn("return", text.lower())

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
            for directory in ("skills", "references", "principles", "playbooks"):
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
                self.assertTrue(any(link.split("#")[0] == APPROVAL_REFERENCE for link in links))
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
        manual_only = set(catalog["manual_only"])
        self.assertEqual(
            declared & manual_only,
            set(),
            "manual-only skill declared as an orchestration dependency",
        )
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
                        self.assertTrue(any(value.split("#")[0] == link for value in links))
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
        design = instruction_text(ROOT / "skills" / "design-coder" / "SKILL.md")
        plan = instruction_text(ROOT / "skills" / "plan-coder" / "SKILL.md")
        orchestrator = instruction_text(ROOT / "skills" / "spec-coder" / "SKILL.md")

        for text in (workflow, design, plan, orchestrator):
            self.assertIn("`show-me`", text)
        for gate in ("Gate 1", "Gate 2", "Gate 3"):
            self.assertIn(gate, workflow)
        normalized_workflow = " ".join((workflow + read_text(ROOT / "references/approval-review-contract.md")).lower().split())
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
        text = instruction_text(path)
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
            "workspace preflight owns dependency preparation and baseline verification",
            "do not create a commit",
            "linked-worktree candidate",
            "mutation-free location",
            "sibling",
            "return the conflict to workspace preflight",
            "disposable small files",
        ):
            self.assertIn(phrase, normalized)
        self.assertNotIn("new sibling location outside the repository", normalized)
        self.assertIn("workspace-policy.py inspect", text)
        self.assertIn("workspace-policy.py validate-allocation", text)
        self.assertIn("do not restate", normalized)
        self.assertIn("every native or Git allocation", text)
        self.assertIn("actual `HEAD`", text)
        ignored = read_text(ROOT / ".gitignore")
        self.assertIn("/.worktrees/", ignored)
        self.assertIn("/.cache/", ignored)
        self.assertLess(normalized.index("enter_worktree"), normalized.index("git worktree add"))
        self.assertIn('$using-git-worktrees', metadata)
        self.assertIn('display_name: "Using Git Worktrees"', metadata)

    def test_runtime_compaction_surface_budgets_and_document_roles(self) -> None:
        worktree_skill = read_text(ROOT / "skills" / "using-git-worktrees" / "SKILL.md")
        ticket_template = read_text(ROOT / "references" / "ticket-template.md")
        readme = read_text(ROOT / "README.md")
        install = read_text(ROOT / "INSTALL.md")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")

        self.assertLessEqual(len(worktree_skill.split()), 1000)
        self.assertLessEqual(len(ticket_template.split()), 1300)
        self.assertIn("## Workflow", readme)
        self.assertIn("## Skills", readme)
        self.assertIn("## 故障排查", install)
        self.assertIn("README.md", install)
        self.assertIn("subagent-routing-contract.md", install)
        self.assertIn(
            "workflow-contract.md#reopened-gate-3-scheduling-barrier",
            install,
        )
        self.assertNotIn("### 默认委派与执行边界", install)
        self.assertNotIn("### Worker Progress Heartbeat", install)

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

    def test_public_docs_describe_the_compacted_owner_map(self) -> None:
        """Keep one public summary and link compatibility readers to it."""
        readme = read_text(ROOT / "README.md")
        compatibility = read_text(ROOT / "references/upstream-compatibility.md")

        normalized = " ".join(readme.split())
        for phrase in (
            "three common owners",
            "conditional trigger",
            "shared Task SOP scaffold",
            "route-specific deltas",
            "workflow contract owns executor entry and handoff",
            "routing contract owns detailed executor and delegation",
            "implementation stage owns one-ticket lifecycle",
        ):
            self.assertIn(phrase, normalized)

        self.assertNotIn("three common owners", compatibility)
        link = "../README.md#context-ownership-and-loading-bounds"
        self.assertIn(f"]({link})", compatibility)
        self.assertTrue((ROOT / "references" / link.split("#", 1)[0]).resolve().is_file())

    def test_readme_assigns_ticket_commit_to_main(self) -> None:
        readme = read_text(ROOT / "README.md")
        row = next(line for line in readme.splitlines() if line.startswith("| `tdd-coder` |"))
        self.assertIn("evidence", row.lower())
        self.assertIn("main", row.lower())
        self.assertNotIn("局部验证和原子提交", row)

    def test_readme_reports_current_router_context_measurements(self) -> None:
        readme = read_text(ROOT / "README.md")
        router = ROOT / "skills" / "spec-coder" / "SKILL.md"
        normal_words = len(instruction_text(router, frozenset()).split())
        all_trigger_words = len(instruction_text(router).split())

        self.assertIn(
            f"| Normal `spec-coder` context | {normal_words} words | 1268 words |",
            readme,
        )
        self.assertIn(
            f"| All-trigger `spec-coder` context | {all_trigger_words} words | 8489 words |",
            readme,
        )

    def test_worktree_adapter_links_canonical_policy_without_copying_outcomes(self) -> None:
        skill = read_text(ROOT / "skills" / "using-git-worktrees" / "SKILL.md").lower()
        workflow = read_text(ROOT / "references" / "workflow-contract.md").lower()

        self.assertIn("workflow-contract.md#workspace-selection", skill)
        self.assertIn("source_worktree", skill)
        self.assertIn("build_cache", skill)
        self.assertIn("git worktree add <source-worktree>", skill)
        self.assertLess(
            skill.index("workspace-policy.py inspect"),
            skill.index("`enter_worktree` is compatible"),
        )
        self.assertNotIn("<repo>/.worktrees/<branch>", skill)
        self.assertNotIn("<repo>/.cache/<branch>/target", skill)
        self.assertNotIn("git worktree add <repo>/.worktrees/<branch>", skill)
        for phrase in (
            "blocked-local-policy-unignored",
            "blocked-ignore-verification",
            "preserve valid slash-separated branch segments",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, workflow)
                self.assertNotIn(phrase, skill)

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
            ".spec-coder/model-routing.toml",
            "read-only",
            "model routing policy",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn(SUBAGENT_ROUTING_REFERENCE, text)
        self.assertIn('display_name: "Setup Coder"', metadata)
        self.assertIn('$setup-coder', metadata)
        self.assertIn(
            "prepend if file lacks final line terminator",
            " ".join(text.lower().split()),
        )

        routing = read_text(ROOT / "assets" / "agents-snippet.md")
        self.assertIn("<!-- spec-coder:start -->", routing)
        self.assertIn("<!-- spec-coder:end -->", routing)
        self.assertFalse((ROOT / "assets" / "global-agents-snippet.md").exists())

        workflow = read_text(ROOT / "references" / "workflow-contract.md")
        self.assertIn("## Repository Setup", workflow)
        self.assertIn("[setup contract](./setup-contract.md)", workflow.lower())
        workflow_normalized = " ".join(workflow.lower().split())
        self.assertIn("onboarding mutation", workflow_normalized)
        self.assertIn("not a coding artifact", workflow_normalized)

    def test_setup_onboards_both_repository_local_isolation_roots(self) -> None:
        setup = read_text(ROOT / "skills" / "setup-coder" / "SKILL.md")
        contract = read_text(ROOT / "references" / "setup-contract.md")
        workflow = read_text(ROOT / "references" / "workflow-contract.md")
        install_guide = read_text(ROOT / "INSTALL.md")
        combined = " ".join((setup + "\n" + contract).lower().split())

        for phrase in (
            ".gitignore",
            "/.worktrees/",
            "/.cache/",
            "all approved targets",
            "partial apply",
            "no final line terminator",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)

        workflow_normalized = " ".join(workflow.lower().split())
        for phrase in (
            "agents.md",
            "managed region",
            "/.worktrees/",
            "/.cache/",
            "does not authorize any other pre-baseline write",
        ):
            with self.subTest(workflow_phrase=phrase):
                self.assertIn(phrase, workflow_normalized)

        for phrase in ("AGENTS.md", "根 `.gitignore`", "`/.worktrees/`", "`/.cache/`", "exact-diff review"):
            with self.subTest(public_setup_phrase=phrase):
                self.assertIn(phrase, install_guide)

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
        text = self.assert_skill_contract(
            "grill-coder", ("grilling", "domain-modeling")
        )
        self.assertIn("dependency-ready frontier", text.lower())
        self.assertIn("up to three", text.lower())
        self.assertIn("stable `qn`", text.lower())
        self.assertIn("qn: default", text.lower())
        self.assertIn("unknown", text.lower())
        self.assertIn("partial", text.lower())
        self.assertIn("recommend", text.lower())
        self.assertIn("original checkout", text.lower())
        for phrase in (
            "confirmed decision",
            "glossary.md",
            "hard to reverse",
            "surprising without context",
            "real trade-off",
            "no document write",
            "ownership",
        ):
            self.assertIn(phrase, text.lower())

        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")
        capability_map = compatibility.split("## Capability Map\n", 1)[1].split(
            "\n## ", 1
        )[0]
        grill_line = next(
            line for line in capability_map.splitlines() if "-> `grill-coder`" in line
        )
        self.assertIn("`grilling`", grill_line)
        self.assertIn("`domain-modeling`", grill_line)
        self.assertNotIn("`grill-with-docs`", grill_line)
        self.assertNotIn("`grill-me-with-doc`", grill_line)

    def test_design_coder_contract(self) -> None:
        text = self.assert_skill_contract(
            "design-coder",
            ("domain-modeling", "codebase-design", "clean-architecture"),
        )
        self.assertIn("2-3", text)
        self.assertIn("adaptive", text.lower())
        self.assertIn("dependency direction", text.lower())
        self.assertIn("testing seams", text.lower())
        self.assertIn("do not write implementation code", text.lower())
        self.assertIn("unknown evidence", text.lower())
        self.assertIn("one gate 1", text.lower())

        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")
        capability_map = compatibility.split("## Capability Map\n", 1)[1].split(
            "\n## ", 1
        )[0]
        design_lines = "\n".join(
            line for line in capability_map.splitlines() if "design-coder" in line
        )
        self.assertNotIn("`brainstorming`", design_lines)

    def test_plan_coder_contract(self) -> None:
        text = self.assert_skill_contract("plan-coder", ("using-git-worktrees",))
        self.assert_planning_templates_resolve(ROOT)
        worktree = text.lower().index("worktree")
        spec = text.lower().index("write the specification")
        reuse = text.lower().index("apply planning reuse interface")
        tickets = text.lower().index("vertical tickets")
        self.assertLess(worktree, spec)
        self.assertLess(spec, reuse)
        self.assertLess(reuse, tickets)
        self.assertLess(spec, tickets)
        self.assertIn("baseline", text.lower())
        self.assertIn("prepared workspace", text.lower())
        self.assertIn("return to workspace preparation", text.lower())
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
        self.assertIn(SUBAGENT_ROUTING_REFERENCE, text)
        for phrase in (
            "bounded",
            "verification seam",
            "main agent",
            "red-green",
            "commit ownership",
        ):
            self.assertIn(phrase, text.lower())

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
        self.assertIn(SUBAGENT_ROUTING_REFERENCE, text)
        for phrase in (
            "bounded evidence",
            "main agent",
            "standards/spec",
            "completion",
        ):
            self.assertIn(phrase, text.lower())

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
            "workspace/mode and branch",
            "plan checkboxes",
            "git log",
            "fresh verification",
            "three consecutive",
        ):
            self.assertIn(phrase, text.lower())
        normalized = " ".join(text.lower().split())
        self.assertIn("prepared workspace", normalized)
        router = read_text(ROOT / "skills" / "spec-coder" / "SKILL.md")
        process = router.split("## Process\n", 1)[1].split("\n## ", 1)[0]
        selected = process.index("**Workspace selection**")
        for decision in ("in-place", "**Isolation**", "**Resume**"):
            self.assertLess(selected, process.index(decision))
        stages = tuple(process.index(f"`{stage}`") for stage in (
            "grill-coder", "design-coder", "plan-coder", "tdd-coder", "delivery-coder"
        ))
        self.assertEqual(stages, tuple(sorted(stages)))
        self.assertIn("start read-only", process)
        self.assertIn("prepare dependencies/baseline before writes", process)
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
            "## Pre-discovery workspace",
            "## Pre-write preparation failure",
            "## Dependency-aware discovery frontier rounds",
            "## Serial discovery coupling and partial answers",
            "## Planning revalidates prepared workspace",
            "## Confirmed discovery term",
            "## Qualifying discovery ADR",
            "## Discovery decision needs no document",
            "## Discovery document ownership conflict",
            "## Manual-only with-doc wrapper",
            "## Required discovery capability unavailable",
            "## Resume with discovery documents",
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
            "## Isolation-root onboarding with exact bytes",
            "## Multi-target setup drift",
            "## Setup partial apply recovery",
            "## Isolation-root idempotent rerun",
            "## Missing required setup capability",
            "## Optional setup warning",
            "## Verification command discovery",
            "## Explicit global setup",
            "## Setup forbidden side effects",
        )
        for heading in setup_headings:
            self.assertIn(heading, scenarios)
        setup_section = scenarios.split("## First repository setup", 1)[1]
        for phrase in (
            "all approved targets",
            "base/proposed digest",
            "partial apply",
            "idempotent rerun",
            "no write",
        ):
            self.assertIn(phrase, setup_section)
        routing_headings = tuple(
            f"## SCN-ROUTE-{number}:" for number in range(1, 10)
        )
        for heading in routing_headings:
            self.assertIn(heading, scenarios)
        depth_headings = tuple(
            f"## SCN-DEPTH-{number}:" for number in range(1, 6)
        )
        for heading in depth_headings:
            self.assertIn(heading, scenarios)
        for field in ("Starting state:", "Expected route:", "Forbidden action:"):
            self.assertEqual(
                scenarios.count(field),
                len(headings)
                + len(approval_headings)
                + len(worktree_headings)
                + len(setup_headings)
                + len(routing_headings)
                + len(depth_headings),
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
            self.assertIn("0.9.0", published_doc)
        for phrase in (
            "selected workspace",
            "read-only discovery",
            "workspace preparation",
            "planning reuse interface",
        ):
            for published_doc in (readme, install_guide):
                self.assertIn(phrase, published_doc.lower())
        for phrase in (
            "reopened gate 3",
            "check-artifacts.py --phase plan",
            "canonical progresssnapshot envelope",
            "tests/forward_contracts.py",
            "tests/fixtures/scenarios.md",
        ):
            self.assertIn(phrase, readme.lower())
        self.assertIn("README.md", install_guide)
        self.assertIn("subagent-routing-contract.md", install_guide)
        for phrase in (
            "progress-snapshot.py",
            "heartbeat-emitter-unavailable",
        ):
            self.assertIn(phrase, readme.lower())
        published_docs = "\n".join((readme, install_guide, compatibility))
        self.assertNotIn("0.5.0", published_docs)
        self.assertNotIn("0.4.1", published_docs)
        self.assertNotIn("0.4.0", published_docs)
        self.assertNotIn("0.3.1", published_docs)
        self.assertNotIn("0.3.0", published_docs)
        self.assertNotIn("0.2.1", published_docs)
        for phrase in (
            "workspace preflight",
            "fresh green baseline",
            "`grilling` + `domain-modeling`",
            "GLOSSARY.md",
            "ADR",
            "fresh Codex session",
        ):
            self.assertIn(phrase, published_docs)
        self.assertIn("九个 skill", readme)
        self.assertIn("九个 skill", install_guide)
        self.assertNotIn(
            "workspace preflight + fresh green baseline\n    -> grill-coder",
            readme.lower(),
        )
        self.assertIn(
            "grill-coder -- qualifying write --> workspace preparation",
            readme.lower(),
        )
        self.assertNotRegex(readme, r"(?i)trax")
        self.assertNotIn("global-agents-snippet.md", readme + install_guide)
        self.assertIn("codex plugin marketplace add", readme)
        self.assertIn("codex plugin add spec-coder@spec-coder", readme)
        self.assertIn('codex plugin marketplace add "$REPO_ROOT"', installer)
        self.assertIn("codex plugin add spec-coder@spec-coder", installer)
        self.assertIn("CODEX_HOME", validator)
        self.assertIn("quick_validate.py", validator)
        self.assertIn("unittest discover", validator)
        self.assertIn("test_*.py", validator)
        published_install_surface = "\n".join(
            (readme, install_guide, installer, validator, compatibility)
        )
        self.assertNotRegex(
            published_install_surface, r"(?i)traecode|traecli|~/\.trae"
        )

    def test_published_default_delegation_contract_is_complete(self) -> None:
        readme = read_text(ROOT / "README.md")
        install_guide = read_text(ROOT / "INSTALL.md")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")
        published = "\n".join((readme, install_guide, compatibility)).lower()

        for phrase in (
            "default delegation",
            "request-wide opt-out",
            "ticket-specific opt-out",
            "review-specific opt-out",
            "real host/task workspace isolation",
            "serialized direct workers",
            "spawn unavailable",
            "delegated review was explicitly required",
            "standards axis",
            "spec axis",
            "main-only",
            "at most two layers",
            "delegation_allowed = false",
            "bundled defaults",
            "no initial configuration",
            "exact diff",
            "two to four",
            "durable planned wave",
            "gate 3",
            "must not pull",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, published)

        # The summary links to the normative wave bound instead of restating it.
        self.assertIn("./subagent-routing-contract.md#execution-waves", compatibility)
        routing = read_text(ROOT / "references/subagent-routing-contract.md")
        self.assertIn("at most four", routing)

    def test_published_model_routing_contract_is_complete_and_optional(self) -> None:
        readme = read_text(ROOT / "README.md")
        install_guide = read_text(ROOT / "INSTALL.md")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")
        published = "\n".join((readme, install_guide, compatibility))

        for phrase in (
            "economy",
            "standard",
            "strong",
            "inherit-main",
            "main-only",
            "minimum_tier",
            "$XDG_CONFIG_HOME/spec-coder/model-routing.toml",
            "~/.config/spec-coder/model-routing.toml",
            ".spec-coder/model-routing.toml",
            "live Host",
        ):
            self.assertIn(phrase, published)

        self.assertIn("provider", readme)
        self.assertIn("model", readme)
        expected_mappings = (
            '[tiers.economy]\nprovider = "trae"\nmodel = "GPT-5.6-Luna"',
            '[tiers.standard]\nprovider = "trae"\nmodel = "GPT-5.6-Terra"',
            '[tiers.strong]\nprovider = "trae"\nmodel = "GPT-5.6-Sol"',
        )
        for document in (readme, install_guide):
            for mapping in expected_mappings:
                self.assertIn(mapping, document)
            self.assertNotIn(
                '[tiers.standard]\nprovider = "trae"\nmodel = "GPT-5.6-Sol"',
                document,
            )
            self.assertNotIn(
                '[tiers.strong]\nprovider = "trae"\nmodel = "GPT-5.6-Terra"',
                document,
            )
        self.assertIn("直接", published)
        self.assertIn("active main model", compatibility)
        self.assertIn("current Agent/session model", published)
        self.assertIn("at most two layers", published)
        self.assertIn("delegation_allowed = false", published)
        self.assertRegex(published, r"only\s+the active main agent")
        self.assertIn("not Host-level sandbox isolation", published)
        self.assertIn("not a required Host model", compatibility)
        self.assertIn("nine bundled skills", compatibility)

    def test_native_implement_spec_delivery_and_published_contract(self) -> None:
        delivery = read_text(ROOT / "skills/delivery-coder/SKILL.md").lower()
        workflow = read_text(ROOT / "references/workflow-contract.md").lower()
        compatibility = read_text(ROOT / "references/upstream-compatibility.md").lower()
        published = "\n".join(
            (read_text(ROOT / "README.md"), read_text(ROOT / "INSTALL.md"))
        ).lower()

        self.assertIn("workflow-contract.md#native-implement-spec-executor", delivery)
        self.assertIn("workflow-contract.md#stage-runtime-envelope", delivery)
        for phrase in (
            "native implement-spec executor",
            "cumulative accepted",
            "authoritative workspace",
        ):
            with self.subTest(surface="delivery", phrase=phrase):
                self.assertIn(phrase, delivery)

        for phrase in (
            "plan-coder",
            "native implement-spec executor",
            "tdd-coder",
            "delivery-coder",
            "every gate 3",
        ):
            with self.subTest(surface="workflow", phrase=phrase):
                self.assertIn(phrase, workflow)

        for phrase in (
            "implement-spec",
            "disable-model-invocation: true",
            "provenance only",
            "not a dependency",
            "to-spec",
            "to-tickets",
        ):
            with self.subTest(surface="compatibility", phrase=phrase):
                self.assertIn(phrase, compatibility)

        for phrase in (
            "plan-coder",
            "native implement-spec executor",
            "delivery-coder",
            "singleton",
            "no implement-spec wrapper agent",
            "no merger subagent",
            "separate authorization",
        ):
            with self.subTest(surface="published", phrase=phrase):
                self.assertIn(phrase, published)
        self.assertNotIn("execution profile", published)

    def test_published_worker_heartbeat_contract_is_complete(self) -> None:
        readme = read_text(ROOT / "README.md").lower()
        install_guide = read_text(ROOT / "INSTALL.md").lower()

        for phrase in (
            "progresssnapshot",
            "45-60 seconds",
            "phase change",
            "long command",
            "heartbeat-capability-unavailable",
            "heartbeat-overdue",
            "awaiting-heartbeat",
            "before or at dispatch",
            "missed interval",
            "wait timeout",
            "main-only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, readme)
        self.assertIn("subagent-routing-contract.md#worker-progress-heartbeat", install_guide)
        self.assertNotIn("### worker progress heartbeat", install_guide)

    def test_published_task_playbooks_are_internal_and_pstack_is_not_a_dependency(self) -> None:
        readme = read_text(ROOT / "README.md")
        install = read_text(ROOT / "INSTALL.md")
        compatibility = read_text(ROOT / "references" / "upstream-compatibility.md")

        for document in (readme, install, compatibility):
            with self.subTest(document=document[:30]):
                self.assertIn("Task Playbook", document)
                self.assertIn("pstack", document)
                self.assertIn("not a dependency", document)
        self.assertIn("nine", compatibility.lower())
        self.assertIn("Gate 1", readme)
        self.assertIn("native implement-spec executor", readme)
        self.assertIn("exactly one Task Playbook", compatibility)
        self.assertIn("two layers", compatibility)
        self.assertIn("no pstack\ninstallation, configuration, model setup", compatibility.lower())
        self.assertIn("task playbook contract", install.lower())


if __name__ == "__main__":
    unittest.main()
