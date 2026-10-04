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
    route_discovery_document,
    route_new_discovery,
    route_planning_workspace,
    parse_repository_routing_policy,
    parse_user_model_mapping,
    evaluate_delegated_attempt,
    propose_setup,
    route_delegated_work,
    route_configured_subagent,
    render_review_snapshot,
)


START = b"<!-- spec-coder:start -->"
END = b"<!-- spec-coder:end -->"
CANONICAL = START + b"\nmanaged\n" + END + b"\n"
ROUTING_FIXTURES = Path(__file__).parent / "fixtures" / "model-routing"


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
            },
            width=40,
        )

        self.assertIn("Required capability is unresolved", rendered)
        self.assertIn("Gate 2 -> spec.md", rendered)
        self.assertIn("-> Gate 3", rendered)

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
            local_ignore_status=0,
        )
        self.assertEqual(route, "reuse-linked")

    def test_unsafe_linked_worktree_returns_conflict_without_nested_creation(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "linked-conflict")

    def test_submodule_does_not_count_as_linked_worktree(self) -> None:
        route = choose_isolation_route(
            linked_candidate=True,
            superproject=True,
            candidate_safe=True,
            native_available=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "native")

    def test_native_precedes_git_fallback(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=True,
            local_ignore_status=0,
        )
        self.assertEqual(route, "native")

    def test_unignored_local_path_returns_to_preflight_for_mutation_free_path(self) -> None:
        route = choose_isolation_route(
            linked_candidate=False,
            superproject=False,
            candidate_safe=False,
            native_available=False,
            local_ignore_status=1,
        )
        self.assertEqual(route, "preflight-mutation-free-location")


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


if __name__ == "__main__":
    unittest.main()
