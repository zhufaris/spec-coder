import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DefaultSubagentDeliveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.delivery = (
            ROOT / "skills" / "delivery-coder" / "SKILL.md"
        ).read_text(encoding="utf-8").lower()

    def test_delivery_uses_two_direct_reviewers_by_default(self) -> None:
        for phrase in (
            "delegates review by default",
            "standards reviewer",
            "spec reviewer",
            "direct layer-2",
            "delegation_allowed = false",
            "must not spawn",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.delivery)
        self.assertNotIn("route optional delegated work", self.delivery)

    def test_opt_out_and_spawn_fallback_run_both_axes_locally(self) -> None:
        for phrase in (
            "review-specific opt-out",
            "request-wide opt-out",
            "standards axis",
            "spec axis",
            "main-local",
            "spawn unavailable",
            "delegated review was explicitly required",
            "blocker",
            "must not invoke",
            "code-review",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.delivery)

    def test_main_retains_findings_repair_verification_and_completion(self) -> None:
        for phrase in (
            "main authors",
            "final standards/spec conclusions",
            "repair judgment",
            "fresh verification",
            "delivery aggregation",
            "completion claim",
            "verification-before-completion",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.delivery)

    def test_both_review_briefs_require_worker_push_heartbeat(self) -> None:
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
            "completion authority",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.delivery)

        self.assertIn("standards reviewer", self.delivery)
        self.assertIn("spec reviewer", self.delivery)
        self.assertIn("read-only", self.delivery)


if __name__ == "__main__":
    unittest.main()
