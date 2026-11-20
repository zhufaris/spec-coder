import unittest
from pathlib import Path

from test_stage_loading import required_links, skill_text


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_STAGES = (
    "spec-coder",
    "grill-coder",
    "design-coder",
    "plan-coder",
    "tdd-coder",
    "delivery-coder",
    "setup-coder",
    "show-me",
)
EXECUTOR_STAGES = ("plan-coder", "tdd-coder", "delivery-coder")


def links(stage):
    return required_links(ROOT / "skills" / stage / "SKILL.md")


class StageOwnerLoadingTests(unittest.TestCase):
    def test_router_normal_reading_is_only_the_common_runtime_envelope(self):
        self.assertEqual(
            set(links("spec-coder")),
            {
                "../../references/workflow-contract.md#stage-runtime-envelope",
                "../../references/upstream-compatibility.md#compatibility-check",
                "../../references/verification-contract.md#authority-and-lifecycle",
            },
        )

    def test_public_stages_load_the_compact_runtime_envelope(self):
        expected = "../../references/workflow-contract.md#stage-runtime-envelope"
        for stage in PUBLIC_STAGES:
            with self.subTest(stage=stage):
                self.assertIn(expected, links(stage))

    def test_executor_stages_link_direct_owners_not_compatibility_contract(self):
        native_executor = (
            "../../references/workflow-contract.md#native-implement-spec-executor"
        )
        for stage in EXECUTOR_STAGES:
            with self.subTest(stage=stage):
                stage_links = links(stage)
                self.assertIn(native_executor, stage_links)
                self.assertFalse(
                    any("implement-spec-execution-contract.md" in link for link in stage_links)
                )

        for stage in ("plan-coder", "tdd-coder"):
            with self.subTest(stage=stage, owner="execution-waves"):
                self.assertIn(
                    "../../references/subagent-routing-contract.md#execution-waves",
                    links(stage),
                )
        for stage in ("tdd-coder",):
            with self.subTest(stage=stage, owner="result-integration"):
                self.assertIn(
                    "../../references/subagent-routing-contract.md#result-integration",
                    links(stage),
                )

    def test_trigger_specific_dispatch_owners_remain_conditional(self):
        for stage in ("grill-coder", "design-coder", "show-me"):
            with self.subTest(stage=stage):
                self.assertFalse(
                    any("subagent-routing-contract.md" in link for link in links(stage))
                )

    def test_router_executor_and_recovery_owners_load_only_for_executor_entry(self):
        normal = links("spec-coder")
        triggered = required_links(
            ROOT / "skills/spec-coder/SKILL.md", {"Executor handoff and recovery"}
        )
        for anchor in ("native-implement-spec-executor", "recovery"):
            link = "../../references/workflow-contract.md#" + anchor
            self.assertNotIn(link, normal)
            self.assertIn(link, triggered)

    def test_router_executor_only_entry_reaches_wave_and_result_owners(self):
        triggered = required_links(
            ROOT / "skills/spec-coder/SKILL.md", {"Executor handoff and recovery"}
        )
        for anchor in ("execution-waves", "result-integration"):
            with self.subTest(anchor=anchor):
                self.assertIn(
                    "../../references/subagent-routing-contract.md#" + anchor,
                    triggered,
                )

    def test_router_dispatch_and_isolation_owners_remain_trigger_specific(self):
        normal = links("spec-coder")
        dispatch = required_links(
            ROOT / "skills/spec-coder/SKILL.md", {"Dispatch assembly"}
        )
        for anchor in ("execution-waves", "result-integration", "worker-progress-heartbeat"):
            link = "../../references/subagent-routing-contract.md#" + anchor
            self.assertNotIn(link, normal)
            self.assertIn(link, dispatch)

        isolation = required_links(
            ROOT / "skills/spec-coder/SKILL.md", {"Isolation"}
        )
        self.assertFalse(any("using-git-worktrees/SKILL.md" in link for link in isolation))
        self.assertIn("invoke bundled `using-git-worktrees`", skill_text(
            ROOT / "skills/spec-coder/SKILL.md"
        ))

    def test_plan_coder_reaches_verification_fallback_owners_conditionally(self):
        normal = links("plan-coder")
        compact = "../../references/verification-contract.md#planning-reuse-interface"
        self.assertIn(compact, normal)
        detailed = (
            "cli-and-explicit-observations",
            "capture-and-record-schema",
            "comparison-and-exit-behavior",
            "worked-invocation",
        )
        for anchor in detailed:
            self.assertNotIn("../../references/verification-contract.md#" + anchor, normal)

        fallback = required_links(
            ROOT / "skills/plan-coder/SKILL.md", {"Verification fallback"}
        )
        for anchor in detailed:
            self.assertIn("../../references/verification-contract.md#" + anchor, fallback)

    def test_spec_coder_reaches_workspace_preparation_owners_conditionally(self):
        normal = links("spec-coder")
        prepared = required_links(
            ROOT / "skills/spec-coder/SKILL.md", {"Workspace preparation"}
        )
        for anchor in (
            "cli-and-explicit-observations",
            "capture-and-record-schema",
            "comparison-and-exit-behavior",
            "worked-invocation",
        ):
            link = "../../references/verification-contract.md#" + anchor
            self.assertNotIn(link, normal)
            self.assertIn(link, prepared)

    def test_router_loads_workspace_selection_before_every_workspace_decision(self):
        path = ROOT / "skills/spec-coder/SKILL.md"
        normal = links("spec-coder")
        selected = required_links(path, {"Workspace selection"})
        owner = "../../references/workflow-contract.md#workspace-selection"
        self.assertNotIn(owner, normal)
        self.assertIn(owner, selected)

        text = skill_text(path)
        process = text.split("## Process\n", 1)[1].split("\n## ", 1)[0]
        selection = process.index("**Workspace selection**")
        for decision in ("in-place", "Isolation", "Resume"):
            with self.subTest(decision=decision):
                self.assertGreater(process.index(decision), selection)

    def test_affected_guidance_is_bounded_and_handles_deleted_paths(self):
        for relative in (
            "skills/tdd-coder/SKILL.md",
            "references/ticket-template.md",
        ):
            text = skill_text(ROOT / relative).lower()
            with self.subTest(path=relative):
                for phrase in (
                    "supported spec-coder",
                    "repository-native",
                    "deleted",
                    "existing post-change owner or test path",
                ):
                    self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
