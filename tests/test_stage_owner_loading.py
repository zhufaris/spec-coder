import unittest
from pathlib import Path

from test_stage_loading import required_links


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
EXECUTOR_STAGES = ("spec-coder", "plan-coder", "tdd-coder", "delivery-coder")


def links(stage):
    return required_links(ROOT / "skills" / stage / "SKILL.md")


class StageOwnerLoadingTests(unittest.TestCase):
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

        for stage in ("spec-coder", "plan-coder", "tdd-coder"):
            with self.subTest(stage=stage, owner="execution-waves"):
                self.assertIn(
                    "../../references/subagent-routing-contract.md#execution-waves",
                    links(stage),
                )
        for stage in ("spec-coder", "tdd-coder"):
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

    def test_orchestrator_loads_the_recovery_owner_it_invokes(self):
        self.assertIn(
            "../../references/workflow-contract.md#recovery",
            links("spec-coder"),
        )

    def test_affected_guidance_is_bounded_and_handles_deleted_paths(self):
        for relative in (
            "skills/tdd-coder/SKILL.md",
            "references/ticket-template.md",
        ):
            text = (ROOT / relative).read_text().lower()
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
