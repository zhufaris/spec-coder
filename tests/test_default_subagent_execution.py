import unittest
from pathlib import Path
from test_stage_loading import instruction_text


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return instruction_text(ROOT / relative).lower()


class DefaultSubagentExecutionContractTests(unittest.TestCase):
    def test_explicit_parallel_request_prepares_isolation_before_fallback(self) -> None:
        routing = " ".join(read("references/subagent-routing-contract.md").split())
        self.assertIn("## explicit parallel requests", routing)
        section = routing.split("## explicit parallel requests", 1)[1].split("## ", 1)[0]
        for phrase in (
            "attempt to prepare",
            "using-git-worktrees",
            "before selecting serial fallback",
            "concrete blocker",
            "parallel-only",
            "must not silently serialize",
            "read-only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)

        for path in (
            "skills/spec-coder/SKILL.md",
            "skills/plan-coder/SKILL.md",
            "references/workflow-contract.md",
            "references/ticket-template.md",
            "references/upstream-compatibility.md",
            "skills/using-git-worktrees/SKILL.md",
            "README.md",
            "INSTALL.md",
        ):
            with self.subTest(path=path):
                self.assertIn("subagent-routing-contract.md#explicit-parallel-requests", read(path))

    def test_single_ticket_scope_does_not_serialize_sibling_workers(self) -> None:
        tdd = " ".join(read("skills/tdd-coder/SKILL.md").split())
        self.assertIn("per ticket, not per wave", tdd)
        self.assertIn("sibling workers", tdd)
        self.assertIn("parallel", tdd)
        self.assertIn("integration and commits remain serial", tdd)

    def test_parallel_capacity_wait_can_recheck_before_dispatch(self) -> None:
        routing = " ".join(read("references/subagent-routing-contract.md").split())
        self.assertNotIn(
            "recompute isolation and capacity only after the main agent has accounted",
            routing,
        )
        self.assertIn("before dispatch", routing)
        self.assertIn("no batch in flight", routing)

    def test_orchestrator_forms_default_dependency_aware_waves(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")

        for phrase in (
            "dependency-aware execution wave",
            "delegates to one direct child by default",
            "host capacity",
            "at most four",
            "real isolation",
            "serial fallback through one direct worker at a time",
            "one active execution wave",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, orchestrator)

        tdd = read("skills/tdd-coder/SKILL.md")
        self.assertIn("current planned wave", tdd)
        self.assertIn("gate-3-approved", tdd)

        for phrase in (
            "approved or autonomously selected durable planned wave order",
            "current planned wave",
            "live dispatch batch",
            "must not pull",
        ):
            with self.subTest(durable_wave_phrase=phrase):
                self.assertIn(phrase, orchestrator)
        self.assertNotIn("executes exactly one unblocked ticket at a time", orchestrator)
        self.assertNotIn("at most one active ticket", orchestrator)

    def test_tdd_handoff_keeps_red_or_structural_evidence_with_main(self) -> None:
        tdd = read("skills/tdd-coder/SKILL.md")

        for phrase in (
            "delegates eligible implementation work by default",
            "behavior red",
            "structural preservation",
            "delegation_allowed = false",
            "must not stage or commit",
            "freshly verifies",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, tdd)
        self.assertNotIn("route optional delegated work", tdd)

    def test_main_integrates_same_base_results_sequentially(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")

        for phrase in (
            "recorded wave base",
            "complete task-owned diff",
            "one result at a time",
            "accepted sibling",
            "ownership overlap",
            "later serialized",
            "fresh verification",
            "atomic commit",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, orchestrator)

    def test_opt_out_capacity_and_spawn_failures_have_distinct_outcomes(self) -> None:
        orchestrator = read("skills/spec-coder/SKILL.md")

        for phrase in (
            "opt-out",
            "stop new dispatch",
            "zero currently available direct-child slots",
            "wait",
            "absent host spawn capability",
            "local fallback",
            "explicitly required",
            "blocker",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, orchestrator)

    def test_orchestrator_and_tdd_briefs_require_worker_push_heartbeat(self) -> None:
        orchestrator = " ".join(read("skills/spec-coder/SKILL.md").split())
        tdd = " ".join(read("skills/tdd-coder/SKILL.md").split())
        workflow = " ".join(read("references/workflow-contract.md").split())
        ticket_template = " ".join(
            read("references/ticket-template.md").split()
        )

        for document in (orchestrator, tdd):
            for phrase in (
                "worker progress heartbeat",
                "progresssnapshot",
                "45-60 seconds",
            ):
                with self.subTest(document=document[:30], phrase=phrase):
                    self.assertIn(phrase, document)

        for document in (orchestrator, tdd):
            self.assertIn("promotion sibling", document)
            self.assertIn("delegation_allowed = false", document)
            self.assertIn("must not stage or commit", document)
            self.assertIn("before or at dispatch", document)

        for document in (workflow, ticket_template):
            for phrase in (
                "worker progress heartbeat",
                "progresssnapshot",
                "heartbeat-overdue",
                "completion authority",
            ):
                with self.subTest(document=document[:30], phrase=phrase):
                    self.assertIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
