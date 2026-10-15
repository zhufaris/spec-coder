import unittest
from pathlib import Path

from forward_contracts import (
    BLOCKED,
    READY,
    WARNING,
    aggregate_status,
    apply_approved_setup,
    classify_managed_block,
    choose_isolation_route,
    choose_delivery_review_mode,
    decide_workspace_disposition,
    decide_execution_mode,
    git_worktree_add_args,
    integrate_wave_result,
    apply_mid_run_opt_out,
    route_discovery_document,
    route_new_discovery,
    route_planning_workspace,
    parse_repository_routing_policy,
    parse_user_model_mapping,
    prepare_subagent_spawn,
    prepare_delivery_review_briefs,
    evaluate_delegated_attempt,
    propose_setup,
    route_delegated_work,
    route_configured_subagent,
    render_review_snapshot,
    select_delegated_wave,
    select_execution_wave,
    select_planned_wave_batch,
    validate_planned_waves,
)


START = b"<!-- spec-coder:start -->"
END = b"<!-- spec-coder:end -->"
CANONICAL = START + b"\nmanaged\n" + END + b"\n"
ROUTING_FIXTURES = Path(__file__).parent / "fixtures" / "model-routing"
BUNDLED_ROUTING = Path(__file__).resolve().parents[1] / "config" / "model-routing.toml"


class SetupForwardScenarios(unittest.TestCase):
    def test_first_setup_then_no_op_rerun_preserves_existing_bytes(self) -> None:
        original = b"# Existing\r\n\r\nKeep this.\r\n"
        proposal = propose_setup(original, CANONICAL)
        before, after = proposal

        self.assertEqual(before, original)
        self.assertTrue(after.startswith(original))
        self.assertEqual(classify_managed_block(after, CANONICAL), "current")
        self.assertIsNone(propose_setup(after, CANONICAL))

    def test_first_setup_preserves_existing_final_newline_state(self) -> None:
        original = b"# Existing without final newline"
        _, after = propose_setup(original, CANONICAL)

        self.assertTrue(after.startswith(CANONICAL))
        self.assertTrue(after.endswith(original))
        self.assertFalse(after.endswith(b"\n"))

    def test_stale_replacement_preserves_marker_external_bytes(self) -> None:
        original = b"prefix\n" + START + b"\nold\n" + END + b"\nsuffix\n"
        proposal = propose_setup(original, CANONICAL)

        self.assertEqual(proposal[1], b"prefix\n" + CANONICAL + b"suffix\n")

    def test_malformed_and_duplicate_markers_block_without_a_proposal(self) -> None:
        malformed = b"prefix\n" + START + b"\nmissing end\n"
        nested = START + b"\n" + START + b"\n" + END + b"\n" + END + b"\n"
        later_nested = CANONICAL + nested
        duplicated = CANONICAL + CANONICAL

        self.assertEqual(classify_managed_block(malformed, CANONICAL), "malformed")
        self.assertEqual(classify_managed_block(nested, CANONICAL), "malformed")
        self.assertEqual(classify_managed_block(later_nested, CANONICAL), "malformed")
        self.assertEqual(classify_managed_block(duplicated, CANONICAL), "duplicated")
        with self.assertRaises(ValueError):
            propose_setup(malformed, CANONICAL)
        with self.assertRaises(ValueError):
            propose_setup(duplicated, CANONICAL)

    def test_marker_text_embedded_in_user_lines_is_not_a_managed_boundary(self) -> None:
        original = b"prefix " + START + b" suffix\nquoted " + END + b" text\n"

        self.assertEqual(classify_managed_block(original, CANONICAL), "absent")
        proposal = propose_setup(original, CANONICAL)
        self.assertTrue(proposal[1].startswith(original))
        self.assertTrue(proposal[1].endswith(CANONICAL))

    def test_concurrent_change_invalidates_approved_setup(self) -> None:
        proposal = propose_setup(b"base\n", CANONICAL)

        result = apply_approved_setup(proposal, b"base\nconcurrent\n")

        self.assertEqual(result[0], BLOCKED)
        self.assertIsNone(result[1])

    def test_required_blocker_dominates_safe_local_update(self) -> None:
        content = b"base\n"
        proposal = propose_setup(content, CANONICAL)
        applied = apply_approved_setup(proposal, content)

        self.assertEqual(applied[1], proposal[1])
        self.assertEqual(aggregate_status([READY, BLOCKED]), BLOCKED)
        self.assertEqual(aggregate_status([READY, WARNING]), WARNING)


class ApprovalForwardScenarios(unittest.TestCase):
    def test_grounded_unresolved_blocker_is_visible_in_linear_fallback(self) -> None:
        rendered = render_review_snapshot(
            {
                "approval_kind": "Gate 2",
                "artifact": "spec.md",
                "decisions": ["repository-local setup"],
                "blockers": ["Required capability is unresolved"],
                "approval_effect": "authorize ticket planning",
                "next_stage": "Gate 3",
                "review_options": [
                    {
                        "label": "A",
                        "choice": "Approve",
                        "consequence": "Continue to ticket planning",
                    },
                    {
                        "label": "B",
                        "choice": "Request changes",
                        "consequence": "Revise and re-review Gate 2",
                    },
                    {
                        "label": "C",
                        "choice": "Reject and stop",
                        "consequence": "Stop this change",
                    },
                ],
            },
            width=40,
        )

        self.assertIn("Required capability is unresolved", rendered)
        self.assertIn("Gate 2 -> spec.md", rendered)
        self.assertIn("-> Gate 3", rendered)
        self.assertIn("A: Approve", rendered)
        self.assertIn("Continue to ticket planning", rendered)

    def test_missing_or_ungrounded_snapshot_data_stops_rendering(self) -> None:
        with self.assertRaises(ValueError):
            render_review_snapshot({"approval_kind": "Gate 1"}, width=80)


class WorktreeForwardScenarios(unittest.TestCase):
    def test_existing_linked_worktree_precedes_native_and_git_creation(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=False,
            candidate_safe=True,
            native_available=True,
            native_can_pin_recorded_base=True,
            git_fallback_safe=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "reuse-linked")

    def test_unsafe_linked_worktree_returns_conflict_without_nested_creation(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            native_can_pin_recorded_base=True,
            git_fallback_safe=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "linked-conflict")

    def test_submodule_does_not_count_as_linked_worktree(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=True,
            candidate_safe=True,
            native_available=True,
            native_can_pin_recorded_base=True,
            git_fallback_safe=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "native")

    def test_native_precedes_git_fallback(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            native_can_pin_recorded_base=True,
            git_fallback_safe=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "native")

    def test_unignored_local_path_returns_to_preflight_for_mutation_free_path(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=False,
            native_can_pin_recorded_base=False,
            git_fallback_safe=True,
            local_ignore_status=1,
        )
        self.assertEqual(route, "preflight-mutation-free-location")

    def test_incompatible_native_uses_safe_git_fallback(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            native_can_pin_recorded_base=False,
            git_fallback_safe=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "git-local")

    def test_incompatible_native_without_safe_fallback_blocks(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            native_can_pin_recorded_base=False,
            git_fallback_safe=False,
            local_ignore_status=0,
        )
        self.assertEqual(route, "blocked-no-compatible-isolation")

    def test_git_fallback_is_anchored_to_the_recorded_wave_base(self) -> None:
        self.assertEqual(
            git_worktree_add_args(
                absolute_path="/tmp/spec-coder-t1",
                branch_name="spec-coder/t1",
                wave_base="abc1234",
            ),
            (
                "git",
                "worktree",
                "add",
                "/tmp/spec-coder-t1",
                "-b",
                "spec-coder/t1",
                "abc1234",
            ),
        )


class DiscoveryWorkspaceForwardScenarios(unittest.TestCase):
    def test_new_request_reaches_grill_only_after_safe_green_preflight(self) -> None:
        self.assertEqual(
            route_new_discovery(workspace_safe=True, baseline_green=True),
            "start-grill",
        )

    def test_unsafe_workspace_stops_before_discovery(self) -> None:
        self.assertEqual(
            route_new_discovery(workspace_safe=False, baseline_green=True),
            "stop-workspace",
        )

    def test_failing_baseline_stops_before_discovery(self) -> None:
        self.assertEqual(
            route_new_discovery(workspace_safe=True, baseline_green=False),
            "stop-baseline",
        )

    def test_missing_required_capability_stops_before_discovery(self) -> None:
        self.assertEqual(
            route_new_discovery(
                workspace_safe=True,
                baseline_green=True,
                capabilities_ready=False,
            ),
            "stop-capability",
        )

    def test_planning_consumes_only_fresh_valid_prepared_workspace(self) -> None:
        self.assertEqual(
            route_planning_workspace(
                prepared=True, ownership_valid=True, baseline_fresh=True
            ),
            "write-specification",
        )
        self.assertEqual(
            route_planning_workspace(
                prepared=True, ownership_valid=False, baseline_fresh=True
            ),
            "return-preflight",
        )
        self.assertEqual(
            route_planning_workspace(
                prepared=True, ownership_valid=True, baseline_fresh=False
            ),
            "return-preflight",
        )


class WithDocsDiscoveryForwardScenarios(unittest.TestCase):
    def test_confirmed_term_updates_glossary(self) -> None:
        self.assertEqual(
            route_discovery_document(
                prepared=True,
                ownership_safe=True,
                confirmed=True,
                decision_kind="term",
                adr_qualifies=False,
            ),
            "update-glossary",
        )

    def test_qualifying_architecture_decision_updates_adr(self) -> None:
        self.assertEqual(
            route_discovery_document(
                prepared=True,
                ownership_safe=True,
                confirmed=True,
                decision_kind="architecture",
                adr_qualifies=True,
            ),
            "update-adr",
        )

    def test_ephemeral_or_unconfirmed_decision_produces_no_write(self) -> None:
        self.assertEqual(
            route_discovery_document(
                prepared=True,
                ownership_safe=True,
                confirmed=True,
                decision_kind="ephemeral",
                adr_qualifies=False,
            ),
            "no-document-write",
        )
        self.assertEqual(
            route_discovery_document(
                prepared=True,
                ownership_safe=False,
                confirmed=True,
                decision_kind="ephemeral",
                adr_qualifies=False,
            ),
            "no-document-write",
        )
        self.assertEqual(
            route_discovery_document(
                prepared=True,
                ownership_safe=False,
                confirmed=True,
                decision_kind="architecture",
                adr_qualifies=False,
            ),
            "no-document-write",
        )
        self.assertEqual(
            route_discovery_document(
                prepared=True,
                ownership_safe=True,
                confirmed=False,
                decision_kind="term",
                adr_qualifies=False,
            ),
            "no-document-write",
        )

    def test_missing_preflight_or_ownership_conflict_stops_write(self) -> None:
        self.assertEqual(
            route_discovery_document(
                prepared=False,
                ownership_safe=True,
                confirmed=True,
                decision_kind="term",
                adr_qualifies=False,
            ),
            "stop-preflight",
        )
        self.assertEqual(
            route_discovery_document(
                prepared=True,
                ownership_safe=False,
                confirmed=True,
                decision_kind="term",
                adr_qualifies=False,
            ),
            "stop-ownership",
        )


class SubagentRoutingForwardScenarios(unittest.TestCase):
    def test_bundled_mapping_has_the_approved_three_tiers(self) -> None:
        self.assertEqual(
            parse_user_model_mapping(BUNDLED_ROUTING.read_bytes()),
            {
                "economy": ("trae", "GPT-5.6-Luna"),
                "standard": ("trae", "GPT-5.6-Terra"),
                "strong": ("trae", "GPT-5.6-Sol"),
            },
        )

    def test_absent_user_mapping_uses_bundled_defaults(self) -> None:
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=None,
                bundled_config=BUNDLED_ROUTING.read_bytes(),
                repository_policy=None,
                available_models={("trae", "GPT-5.6-Luna")},
                override_supported=True,
            ),
            ("economy", "trae", "GPT-5.6-Luna"),
        )

    def test_valid_user_mapping_replaces_instead_of_merging_bundled_tiers(self) -> None:
        user_config = b"""
version = 1
[tiers.strong]
provider = "trae"
model = "Custom-Sol"
"""

        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=user_config,
                bundled_config=BUNDLED_ROUTING.read_bytes(),
                repository_policy=None,
                available_models={
                    ("trae", "GPT-5.6-Luna"),
                    ("trae", "Custom-Sol"),
                },
                override_supported=True,
            ),
            ("strong", "trae", "Custom-Sol"),
        )

    def test_invalid_user_mapping_does_not_silently_use_bundled_defaults(self) -> None:
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=b"not = [valid",
                bundled_config=BUNDLED_ROUTING.read_bytes(),
                repository_policy=None,
                available_models={("trae", "GPT-5.6-Luna")},
                override_supported=True,
            ),
            ("inherit-main", None, None),
        )

    def test_eligible_work_delegates_by_default_and_opt_out_is_local(self) -> None:
        eligible = dict(
            dependency_ready=True,
            grounded_inputs=True,
            bounded=True,
            reversible=True,
            verification_seam=True,
            main_only=False,
            spawn_available=True,
            available_slots=1,
            delegation_required=False,
        )

        self.assertEqual(decide_execution_mode(opt_out=False, **eligible), "delegate")
        self.assertEqual(decide_execution_mode(opt_out=True, **eligible), "local")

    def test_incomplete_dependency_remains_pending_and_is_not_dispatched(self) -> None:
        self.assertEqual(
            decide_execution_mode(
                dependency_ready=False,
                grounded_inputs=True,
                bounded=True,
                reversible=True,
                verification_seam=True,
                main_only=False,
                opt_out=False,
                spawn_available=True,
                available_slots=1,
                delegation_required=False,
            ),
            "pending",
        )

    def test_ready_but_unsafe_work_stays_local_or_blocks_when_required(self) -> None:
        unsafe = dict(
            dependency_ready=True,
            grounded_inputs=False,
            bounded=True,
            reversible=True,
            verification_seam=True,
            main_only=False,
            opt_out=False,
            spawn_available=True,
            available_slots=1,
        )

        self.assertEqual(
            decide_execution_mode(delegation_required=False, **unsafe), "local"
        )
        self.assertEqual(
            decide_execution_mode(delegation_required=True, **unsafe), "block"
        )

    def test_spawn_absence_falls_back_but_temporary_capacity_waits(self) -> None:
        candidate = dict(
            dependency_ready=True,
            grounded_inputs=True,
            bounded=True,
            reversible=True,
            verification_seam=True,
            main_only=False,
            opt_out=False,
        )

        self.assertEqual(
            decide_execution_mode(
                spawn_available=False,
                available_slots=0,
                delegation_required=False,
                **candidate,
            ),
            "local",
        )
        self.assertEqual(
            decide_execution_mode(
                spawn_available=False,
                available_slots=0,
                delegation_required=True,
                **candidate,
            ),
            "block",
        )
        self.assertEqual(
            decide_execution_mode(
                spawn_available=True,
                available_slots=0,
                delegation_required=False,
                **candidate,
            ),
            "wait",
        )

    def test_wave_filters_dependencies_eligibility_and_conflicts(self) -> None:
        tickets = [
            {"id": "T1", "dependency_ready": True, "delegation_eligible": True, "conflicts": set()},
            {"id": "T2", "dependency_ready": False, "delegation_eligible": True, "conflicts": set()},
            {"id": "T3", "dependency_ready": True, "delegation_eligible": False, "conflicts": set()},
            {"id": "T4", "dependency_ready": True, "delegation_eligible": True, "conflicts": {"T1"}},
            {"id": "T5", "dependency_ready": True, "delegation_eligible": True, "conflicts": set()},
        ]

        self.assertEqual(
            select_delegated_wave(tickets, host_available_slots=4, isolated=True),
            ("T1", "T5"),
        )

    def test_wave_respects_host_capacity_hard_cap_and_isolation(self) -> None:
        tickets = [
            {"id": f"T{index}", "dependency_ready": True, "delegation_eligible": True, "conflicts": set()}
            for index in range(1, 7)
        ]

        self.assertEqual(
            select_delegated_wave(tickets, host_available_slots=6, isolated=True),
            ("T1", "T2", "T3", "T4"),
        )
        self.assertEqual(
            select_delegated_wave(tickets, host_available_slots=2, isolated=True),
            ("T1", "T2"),
        )
        self.assertEqual(
            select_delegated_wave(tickets, host_available_slots=4, isolated=False),
            ("T1",),
        )

    def test_planned_waves_are_a_complete_safe_ordered_partition(self) -> None:
        tickets = [
            {"id": "T1", "dependencies": set(), "conflicts": set(), "mode": "delegate"},
            {"id": "T2", "dependencies": set(), "conflicts": set(), "mode": "delegate"},
            {"id": "T3", "dependencies": {"T1"}, "conflicts": set(), "mode": "delegate"},
            {"id": "T4", "dependencies": set(), "conflicts": {"T2"}, "mode": "delegate"},
            {"id": "T5", "dependencies": {"T3"}, "conflicts": set(), "mode": "local"},
        ]

        self.assertEqual(
            validate_planned_waves(
                tickets,
                (("T1", "T2"), ("T3", "T4"), ("T5",)),
            ),
            (("T1", "T2"), ("T3", "T4"), ("T5",)),
        )

    def test_planned_waves_reject_missing_duplicate_unsafe_or_oversized_members(self) -> None:
        tickets = [
            {"id": "T1", "dependencies": set(), "conflicts": set(), "mode": "delegate"},
            {"id": "T2", "dependencies": {"T1"}, "conflicts": set(), "mode": "delegate"},
            {"id": "T3", "dependencies": set(), "conflicts": {"T1"}, "mode": "delegate"},
            {"id": "T4", "dependencies": set(), "conflicts": set(), "mode": "delegate"},
            {"id": "T5", "dependencies": set(), "conflicts": set(), "mode": "local"},
        ]
        invalid_partitions = (
            (("T1",), ("T2",), ("T3",), ("T4",)),
            (("T1", "T1"), ("T2",), ("T3",), ("T4",), ("T5",)),
            (("T1", "T2"), ("T3",), ("T4",), ("T5",)),
            (("T1", "T3"), ("T2",), ("T4",), ("T5",)),
            (("T2",), ("T1",), ("T3",), ("T4",), ("T5",)),
            (("T1", "T3", "T4", "T5"), ("T2",)),
            (("T1", "T3", "T4", "T2", "T5"),),
        )

        for waves in invalid_partitions:
            with self.subTest(waves=waves):
                with self.assertRaises(ValueError):
                    validate_planned_waves(tickets, waves)

        invalid_mode_tickets = [
            {"id": "T1", "dependencies": set(), "conflicts": set(), "mode": "wait"},
        ]
        with self.assertRaises(ValueError):
            validate_planned_waves(invalid_mode_tickets, (("T1",),))

    def test_runtime_batch_never_pulls_from_a_later_planned_wave(self) -> None:
        tickets = [
            {"id": "T1", "dependencies": set(), "conflicts": set(), "mode": "delegate"},
            {"id": "T2", "dependencies": set(), "conflicts": set(), "mode": "delegate"},
            {"id": "T3", "dependencies": set(), "conflicts": set(), "mode": "delegate"},
        ]
        waves = (("T1", "T2"), ("T3",))

        self.assertEqual(
            select_planned_wave_batch(
                tickets,
                waves,
                completed_ids=set(),
                host_available_slots=1,
                isolated=True,
            ),
            (("T1", "delegate"),),
        )
        self.assertEqual(
            select_planned_wave_batch(
                tickets,
                waves,
                completed_ids={"T1"},
                host_available_slots=4,
                isolated=True,
            ),
            (("T2", "delegate"),),
        )
        self.assertEqual(
            select_planned_wave_batch(
                tickets,
                waves,
                completed_ids={"T1", "T2"},
                host_available_slots=4,
                isolated=True,
            ),
            (("T3", "delegate"),),
        )

    def test_execution_wave_keeps_local_work_serial_and_skips_pending(self) -> None:
        tickets = [
            {"id": "T1", "dependency_ready": False, "mode": "delegate", "conflicts": set()},
            {"id": "T2", "dependency_ready": True, "mode": "local", "conflicts": set()},
            {"id": "T3", "dependency_ready": True, "mode": "delegate", "conflicts": set()},
        ]

        self.assertEqual(
            select_execution_wave(tickets, host_available_slots=4, isolated=True),
            (("T2", "local"),),
        )

    def test_wait_and_block_outcomes_do_not_form_execution_waves(self) -> None:
        for mode in ("wait", "block"):
            with self.subTest(mode=mode):
                self.assertEqual(
                    select_execution_wave(
                        [
                            {
                                "id": "T1",
                                "dependency_ready": True,
                                "mode": mode,
                                "conflicts": set(),
                            }
                        ],
                        host_available_slots=0,
                        isolated=True,
                    ),
                    (),
                )


class ExecutionRecoveryForwardScenarios(unittest.TestCase):
    def test_same_base_and_accepted_sibling_advancement_have_explicit_outcomes(self) -> None:
        common = dict(
            ownership_disjoint=True,
            transfer_clean=True,
            diff_explained=True,
            verification_passes=True,
        )
        self.assertEqual(
            integrate_wave_result(
                base_matches=True,
                accepted_sibling_advancement=False,
                **common,
            ),
            "accept",
        )
        self.assertEqual(
            integrate_wave_result(
                base_matches=False,
                accepted_sibling_advancement=True,
                **common,
            ),
            "accept",
        )
        self.assertEqual(
            integrate_wave_result(
                base_matches=False,
                accepted_sibling_advancement=False,
                **common,
            ),
            "requeue-serialized",
        )
        for unsafe_field in (
            "ownership_disjoint",
            "diff_explained",
            "verification_passes",
        ):
            unsafe = dict(common)
            unsafe[unsafe_field] = False
            with self.subTest(unsafe_field=unsafe_field):
                self.assertEqual(
                    integrate_wave_result(
                        base_matches=True,
                        accepted_sibling_advancement=False,
                        **unsafe,
                    ),
                    "requeue-serialized",
                )
        self.assertEqual(
            integrate_wave_result(
                base_matches=True,
                accepted_sibling_advancement=False,
                ownership_disjoint=True,
                transfer_clean=False,
                diff_explained=True,
                verification_passes=True,
            ),
            "requeue-serialized",
        )

    def test_mid_run_opt_out_stops_new_dispatch_and_preserves_attribution(self) -> None:
        self.assertEqual(
            apply_mid_run_opt_out(
                integrated_commits=("T1",),
                returned_attributable_results=("T2",),
                undispatched_tickets=("T3",),
            ),
            {
                "integrated": ("T1",),
                "inspect_before_disposition": ("T2",),
                "stopped_before_dispatch": ("T3",),
                "promotion": "stopped",
                "cancellation_or_discard": "requires-safe-disposition",
                "remaining_execution": "main-local-after-attribution",
            },
        )

    def test_workspace_cleanup_requires_disposition_and_clean_ownership(self) -> None:
        self.assertEqual(
            decide_workspace_disposition(
                result_disposition="accepted",
                ownership_clean=True,
                user_owned_changes=False,
            ),
            "cleanup-authorized",
        )
        self.assertEqual(
            decide_workspace_disposition(
                result_disposition="pending",
                ownership_clean=True,
                user_owned_changes=False,
            ),
            "retain-recovery-handle",
        )
        self.assertEqual(
            decide_workspace_disposition(
                result_disposition="explicitly-discarded",
                ownership_clean=True,
                user_owned_changes=True,
            ),
            "retain-recovery-handle",
        )

    def test_delivery_mode_covers_delegation_opt_out_and_spawn_fallback(self) -> None:
        self.assertEqual(
            choose_delivery_review_mode(
                opt_out=False,
                spawn_available=True,
                delegation_required=False,
                available_slots=2,
            ),
            "delegate-standards-and-spec",
        )
        self.assertEqual(
            choose_delivery_review_mode(
                opt_out=True,
                spawn_available=True,
                delegation_required=False,
                available_slots=2,
            ),
            "main-local-two-axis",
        )
        self.assertEqual(
            choose_delivery_review_mode(
                opt_out=False,
                spawn_available=False,
                delegation_required=False,
                available_slots=0,
            ),
            "main-local-two-axis",
        )
        self.assertEqual(
            choose_delivery_review_mode(
                opt_out=False,
                spawn_available=False,
                delegation_required=True,
                available_slots=0,
            ),
            "block",
        )
        self.assertEqual(
            choose_delivery_review_mode(
                opt_out=False,
                spawn_available=True,
                delegation_required=False,
                available_slots=0,
            ),
            "wait",
        )

    def test_delegated_delivery_prepares_two_read_only_direct_briefs(self) -> None:
        briefs = prepare_delivery_review_briefs("delegate-standards-and-spec")

        self.assertEqual(tuple(brief["axis"] for brief in briefs), ("standards", "spec"))
        for brief in briefs:
            self.assertEqual(brief["layer"], 2)
            self.assertTrue(brief["read_only"])
            self.assertFalse(brief["delegation_allowed"])
            self.assertTrue(brief["must_not_spawn"])

        self.assertEqual(prepare_delivery_review_briefs("main-local-two-axis"), ())

    def test_complete_mapping_selects_effective_tier(self) -> None:
        user_config = (ROUTING_FIXTURES / "user-complete.toml").read_bytes()
        route = route_configured_subagent(
            classified_tier="economy",
            user_config=user_config,
            repository_policy=(
                ROUTING_FIXTURES / "repository-standard.toml"
            ).read_bytes(),
            available_models={
                ("trae", "Luna"),
                ("trae", "Sol"),
                ("trae", "Terra"),
            },
            override_supported=True,
        )
        self.assertEqual(route, ("standard", "trae", "Sol"))

    def test_missing_mapping_falls_upward_then_inherits_main(self) -> None:
        partial = (ROUTING_FIXTURES / "user-partial.toml").read_bytes()
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=partial,
                repository_policy=None,
                available_models={("trae", "Terra")},
                override_supported=True,
            ),
            ("strong", "trae", "Terra"),
        )
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=partial,
                repository_policy=None,
                available_models=set(),
                override_supported=True,
            ),
            ("inherit-main", None, None),
        )

    def test_invalid_or_model_injecting_config_inherits_main(self) -> None:
        model_injecting_policy = (
            b'version = 1\nminimum_tier = "economy"\nmodel = "Luna"\n'
        )
        self.assertIsNone(parse_user_model_mapping(b"not = [valid"))
        self.assertEqual(
            parse_repository_routing_policy(model_injecting_policy),
            ("inherit-main", False),
        )
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=b"not = [valid",
                repository_policy=None,
                available_models={("trae", "Luna")},
                override_supported=True,
            ),
            ("inherit-main", None, None),
        )
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=(ROUTING_FIXTURES / "user-complete.toml").read_bytes(),
                repository_policy=model_injecting_policy,
                available_models={("trae", "Luna")},
                override_supported=True,
            ),
            ("inherit-main", None, None),
        )

    def test_boolean_schema_versions_are_not_integer_version_one(self) -> None:
        self.assertIsNone(
            parse_user_model_mapping(
                b'version = true\n[tiers.economy]\nprovider = "trae"\nmodel = "Luna"\n'
            )
        )
        self.assertEqual(
            parse_repository_routing_policy(
                b'version = true\nminimum_tier = "economy"\n'
            ),
            ("inherit-main", False),
        )
        self.assertEqual(
            parse_repository_routing_policy(
                b'version = 1\nminimum_tier = []\n'
            ),
            ("inherit-main", False),
        )
    def test_main_only_and_missing_override_never_downgrade(self) -> None:
        config = b"""
version = 1
[tiers.economy]
provider = "trae"
model = "Luna"
"""
        self.assertEqual(
            route_configured_subagent(
                classified_tier="main-only",
                user_config=config,
                repository_policy=None,
                available_models={("trae", "Luna")},
                override_supported=True,
            ),
            ("main-only", None, None),
        )
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=config,
                repository_policy=None,
                available_models={("trae", "Luna")},
                override_supported=False,
            ),
            ("inherit-main", None, None),
        )

    def test_required_model_conflict_is_not_silently_substituted(self) -> None:
        config = b"""
version = 1
[tiers.strong]
provider = "trae"
model = "Terra"
"""
        self.assertEqual(
            route_configured_subagent(
                classified_tier="strong",
                user_config=config,
                repository_policy=None,
                available_models=set(),
                override_supported=True,
                required_model=("trae", "Terra"),
            ),
            ("required-model-conflict", "trae", "Terra"),
        )
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=config,
                repository_policy=b'version = 1\nminimum_tier = "inherit-main"\n',
                available_models=set(),
                override_supported=True,
                required_model=("trae", "Terra"),
            ),
            ("required-model-conflict", "trae", "Terra"),
        )

    def test_explicit_user_constraints_raise_exclude_or_inherit(self) -> None:
        config = (ROUTING_FIXTURES / "user-complete.toml").read_bytes()
        available = {
            ("trae", "Luna"),
            ("trae", "Sol"),
            ("trae", "Terra"),
        }
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=config,
                repository_policy=None,
                available_models=available,
                override_supported=True,
                user_minimum_tier="strong",
            ),
            ("strong", "trae", "Terra"),
        )
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=config,
                repository_policy=None,
                available_models=available,
                override_supported=True,
                excluded_models={("trae", "Luna")},
            ),
            ("standard", "trae", "Sol"),
        )
        self.assertEqual(
            route_configured_subagent(
                classified_tier="economy",
                user_config=config,
                repository_policy=None,
                available_models=available,
                override_supported=True,
                user_minimum_tier="inherit-main",
            ),
            ("inherit-main", None, None),
        )

    def test_bounded_tdd_and_strong_advisory_work_use_configured_tiers(self) -> None:
        config = (ROUTING_FIXTURES / "user-complete.toml").read_bytes()
        available = {
            ("trae", "Luna"),
            ("trae", "Sol"),
            ("trae", "Terra"),
        }
        self.assertEqual(
            route_delegated_work(
                work_kind="ticket-implementation",
                bounded=True,
                reversible=True,
                verification_seam=True,
                user_config=config,
                repository_policy=None,
                available_models=available,
                override_supported=True,
            ),
            ("standard", "trae", "Sol"),
        )
        self.assertEqual(
            route_delegated_work(
                work_kind="complex-advisory-review",
                bounded=True,
                reversible=True,
                verification_seam=True,
                user_config=config,
                repository_policy=None,
                available_models=available,
                override_supported=True,
            ),
            ("strong", "trae", "Terra"),
        )

    def test_ambiguous_or_authoritative_work_remains_main_only(self) -> None:
        config = (ROUTING_FIXTURES / "user-complete.toml").read_bytes()
        common = {
            "user_config": config,
            "repository_policy": None,
            "available_models": {("trae", "Terra")},
            "override_supported": True,
        }
        self.assertEqual(
            route_delegated_work(
                work_kind="ticket-implementation",
                bounded=False,
                reversible=True,
                verification_seam=True,
                **common,
            ),
            ("main-only", None, None),
        )
        self.assertEqual(
            route_delegated_work(
                work_kind="completion-claim",
                bounded=True,
                reversible=True,
                verification_seam=True,
                **common,
            ),
            ("main-only", None, None),
        )

    def test_attempt_requires_main_verification_and_promotes_only_once(self) -> None:
        self.assertEqual(
            evaluate_delegated_attempt(
                outcome="success", main_verified=False, already_promoted=False
            ),
            "await-main-verification",
        )
        self.assertEqual(
            evaluate_delegated_attempt(
                outcome="failed", main_verified=False, already_promoted=False
            ),
            "promote-inherit-main",
        )
        self.assertEqual(
            evaluate_delegated_attempt(
                outcome="failed", main_verified=False, already_promoted=True
            ),
            "stop-after-promotion",
        )

    def test_only_main_prepares_direct_child_with_delegation_disabled(self) -> None:
        self.assertEqual(
            prepare_subagent_spawn(
                caller_layer=1,
                caller_may_delegate=True,
                host_can_deny_child_spawn=False,
            ),
            ("spawn-direct-contract-guarded", 2, False),
        )
        self.assertEqual(
            prepare_subagent_spawn(
                caller_layer=1,
                caller_may_delegate=True,
                host_can_deny_child_spawn=True,
            ),
            ("spawn-direct-host-guarded", 2, False),
        )

    def test_child_direct_or_indirect_delegation_returns_to_main(self) -> None:
        for caller_may_delegate in (False, True):
            with self.subTest(caller_may_delegate=caller_may_delegate):
                self.assertEqual(
                    prepare_subagent_spawn(
                        caller_layer=2,
                        caller_may_delegate=caller_may_delegate,
                        host_can_deny_child_spawn=False,
                    ),
                    ("return-to-main", None, None),
                )

    def test_promotion_is_a_main_owned_layer_two_sibling(self) -> None:
        self.assertEqual(
            evaluate_delegated_attempt(
                outcome="failed", main_verified=False, already_promoted=False
            ),
            "promote-inherit-main",
        )
        self.assertEqual(
            prepare_subagent_spawn(
                caller_layer=1,
                caller_may_delegate=True,
                host_can_deny_child_spawn=False,
            ),
            ("spawn-direct-contract-guarded", 2, False),
        )


if __name__ == "__main__":
    unittest.main()
