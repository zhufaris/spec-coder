"""Public CLI checks using real Markdown and temporary local repositories."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/check-artifacts.py"
FIXTURES = Path(__file__).parent / "fixtures/artifacts"


class ArtifactCheckerCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = Path(self.tmp.name)
        subprocess.run(["git", "-C", str(self.cwd), "init", "-q", "-b", "feat/cache-tests"], check=True)
        (self.cwd / ".gitignore").write_text("/.cache/\n")
        self.spec = self.cwd / "spec.md"
        self.plan = self.cwd / "plan.md"
        self.spec.write_text((FIXTURES / "spec.md").read_text())
        plan = (FIXTURES / "plan.md").read_text()
        cache = self.cwd / ".cache" / "feat" / "cache-tests" / "target"
        self.plan.write_text(plan.replace(
            "| Mutation ownership | scripts/check.py |",
            "| Mutation ownership | scripts/check.py |\n| Build cache | %s |" % cache,
        ))

    def run_cli(self, phase="plan", *extra):
        args = [sys.executable, str(CLI), "--phase", phase,
                "--spec", str(self.spec), "--json"]
        if phase != "spec":
            args += ["--plan", str(self.plan)]
        result = subprocess.run(args + list(extra), cwd=self.cwd,
                                capture_output=True, text=True)
        self.assertNotIn("Traceback", result.stderr)
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_supported_artifacts_and_invalid_wave_partition_and_legacy_format(self):
        for phase in ("spec", "plan"):
            with self.subTest(phase=phase):
                code, report = self.run_cli(phase)
                self.assertEqual(code, 0, report)
                self.assertEqual(report["status"], "passed")
                self.assertEqual(report["findings"], [])
        original = self.plan.read_text()
        for heading, rule in (("## Wave W1: `T1`, `T1`", "wave.duplicate-member"),
                              ("## Wave W1: None", "wave.missing-member")):
            with self.subTest(rule=rule):
                self.plan.write_text(original.replace("## Wave W1: `T1`", heading))
                code, report = self.run_cli()
                self.assertEqual(code, 1, report)
                finding = next(f for f in report["findings"] if f["rule"] == rule)
                self.assertEqual(finding["path"], str(self.plan))
                self.assertGreater(finding["line"], 0)
                self.assertTrue(finding["message"])
        self.spec.write_text(self.spec.read_text().replace("artifact-v1", "artifact-v99"))
        code, report = self.run_cli("spec")
        self.assertEqual(code, 2, report)
        self.assertEqual(report["status"], "unsupported")
        self.assertEqual(report["findings"][0]["rule"], "format.unsupported")

    def assert_rule(self, rule, phase="plan", code=1):
        actual, report = self.run_cli(phase)
        self.assertEqual(actual, code, report)
        matches = [f for f in report["findings"] if f["rule"] == rule]
        self.assertTrue(matches, report)
        for finding in matches:
            self.assertIn(finding["path"], {str(self.plan), str(self.spec)})
            self.assertGreater(finding["line"], 0)
            self.assertTrue(finding["message"])
        return matches

    def edit_field(self, name, value):
        lines = self.plan.read_text().splitlines()
        prefix = "| " + name + " |"
        lines = [(prefix + " " + value + " |") if line.startswith(prefix) else line
                 for line in lines]
        self.plan.write_text("\n".join(lines) + "\n")

    def add_ticket(self, number=2, same_wave=True):
        source = (FIXTURES / "plan.md").read_text().split("### - [ ] T1:", 1)[1]
        source = source.replace(
            "| Mutation ownership | scripts/check.py |",
            "| Mutation ownership | scripts/check.py |\n| Build cache | %s |" % (
                self.cwd / ".cache" / "feat" / "cache-tests" / "target"
            ),
        )
        ticket = "### - [ ] T%d:" % number + source.replace("scripts/check.py", "scripts/other%d.py" % number)
        content = self.plan.read_text()
        if same_wave:
            content = content.replace("## Wave W1: `T1`", "## Wave W1: `T1`, `T%d`" % number)
        else:
            content += "\n## Wave W%d: `T%d`\n" % (number, number)
        self.plan.write_text(content + "\n" + ticket)

    def test_marker_examples_in_prose_are_not_declarations(self):
        self.spec.write_text(self.spec.read_text() + "\nUse `<!-- spec-coder:artifact-v1 spec -->` in specs.\n")
        code, report = self.run_cli("spec")
        self.assertEqual(code, 0, report)

    def test_duplicate_malformed_and_missing_markers_are_unsupported(self):
        original = self.spec.read_text()
        for marker in ("", "<!-- spec-coder:artifact-v1 plan -->", "<!-- spec-coder:artifact-v1 spec --!>",
                       "<!-- spec-coder:artifact-v1 spec -->\n<!-- spec-coder:artifact-v1 spec -->"):
            with self.subTest(marker=marker):
                self.spec.write_text(original.replace("<!-- spec-coder:artifact-v1 spec -->", marker))
                self.assert_rule("format.unsupported", "spec", 2)

    def test_required_sections_and_definition_locations(self):
        original = self.spec.read_text()
        for section in ("Problem Statement", "Solution", "User Stories", "Implementation Decisions", "Testing Decisions", "Out of Scope", "Further Notes"):
            self.spec.write_text(original.replace("## " + section, "## Other"))
            self.assert_rule("spec.required-section", "spec")
        self.spec.write_text(original + "\n### INV-1: Duplicate\n")
        self.assert_rule("decision.duplicate-id", "spec")
        self.spec.write_text(original.replace("### INV-1: Read only", "### INV-0: "))
        self.assert_rule("decision.invalid-definition", "spec")

    def test_explicit_internal_references_and_coverage(self):
        self.spec.write_text(self.spec.read_text() + "\nReferences: SCN-999\n")
        self.assert_rule("reference.unknown", "spec")
        self.spec.write_text((FIXTURES / "spec.md").read_text())
        self.edit_field("Spec references", "SCN-1, SCN-99")
        self.assert_rule("reference.unknown")
        self.assert_rule("coverage.uncovered")
        self.edit_field("Spec references", "SCN-1, SCN-1, INV-1, ARCH-1")
        self.assert_rule("reference.duplicate")
        self.edit_field("Spec references", "SCN-1 extra")
        self.assert_rule("field.invalid-list")

    def test_malformed_declared_spec_reference_is_a_finding(self):
        self.spec.write_text(self.spec.read_text() + "\n| References | SCN-99 | trailing junk\n")
        self.assert_rule("field.malformed", "spec")

    def test_no_invented_decisions_required_for_small_spec(self):
        self.spec.write_text(self.spec.read_text().replace("### INV-1: Read only\n", "").replace("### ARCH-1: CLI\n", ""))
        self.edit_field("Spec references", "SCN-1")
        self.assertEqual(self.run_cli()[0], 0)

    def test_ticket_fields_are_required_nonempty_and_unique(self):
        original = self.plan.read_text()
        for name in ("Spec references", "Dependencies", "Delegation mode", "Mutation ownership", "Concurrency conflicts", "Acceptance criteria and verification"):
            with self.subTest(name=name):
                self.plan.write_text(original)
                self.edit_field(name, "")
                self.assert_rule("field.required")
        self.plan.write_text(original + "| Dependencies | None |\n")
        self.assert_rule("field.duplicate")
        self.plan.write_text(original.replace("[ ] T1:", "[?] T1:"))
        self.assert_rule("ticket.invalid-definition")
        self.plan.write_text(original + original.split("## Wave W1: `T1`", 1)[1])
        self.assert_rule("ticket.duplicate-id")

    def test_mutating_ticket_requires_a_build_cache_field(self):
        lines = [
            line
            for line in self.plan.read_text().splitlines()
            if not line.startswith("| Build cache |")
        ]
        self.plan.write_text("\n".join(lines) + "\n")

        self.assert_rule("field.required")

    def test_build_cache_matches_mutation_ownership_and_repository_policy(self):
        original = self.plan.read_text()
        self.edit_field("Build cache", "None")
        self.assert_rule("field.invalid-build-cache")

        self.plan.write_text(original)
        self.edit_field("Mutation ownership", "None")
        self.edit_field("Build cache", "None")
        self.assertEqual(self.run_cli()[0], 0)

        self.plan.write_text(original)
        self.edit_field("Mutation ownership", "None")
        self.assert_rule("field.invalid-build-cache")

        self.plan.write_text(original)
        self.edit_field(
            "Build cache", str(self.cwd / ".cache" / "worker" / "other-branch" / "target")
        )
        self.assertEqual(self.run_cli()[0], 0)

        for value in (
            "relative/.cache/target",
            "/tmp/escaped/target",
            str(self.cwd / ".cache" / "invalid..branch" / "target"),
            str(self.cwd / ".cache" / "feat" / ".." / "escaped" / "target"),
        ):
            with self.subTest(value=value):
                self.plan.write_text(original)
                self.edit_field("Build cache", value)
                self.assert_rule("field.invalid-build-cache")

    def test_build_cache_rejects_symlinked_or_unignored_reservations(self):
        original = self.plan.read_text()
        outside = self.cwd / "outside"
        outside.mkdir()
        cache_root = self.cwd / ".cache"
        cache_root.symlink_to(outside, target_is_directory=True)
        self.assert_rule("field.invalid-build-cache")
        cache_root.unlink()

        self.plan.write_text(original)
        (self.cwd / ".gitignore").write_text("")
        self.assert_rule("field.invalid-build-cache")

    def test_malformed_table_rows_and_unbalanced_id_quotes_are_not_silently_skipped(self):
        original = self.plan.read_text()
        self.plan.write_text(original + "| Dependencies | T99 | trailing junk\n")
        self.assert_rule("field.malformed")
        self.plan.write_text(original)
        self.edit_field("Dependencies", "`T1")
        self.assert_rule("field.invalid-list")
        self.plan.write_text(original)
        self.edit_field("Mutation ownership", "`src/file.py")
        self.assert_rule("ownership.ambiguous")

    def test_ticket_id_checkboxes_outside_canonical_heading_are_rejected(self):
        original = self.plan.read_text()
        # Ordinary checklist prose and fenced examples are not ticket declarations.
        self.plan.write_text(original + "\n- [ ] Record verification evidence\n```markdown\n- [ ] T99: Fenced example\n```\n")
        code, report = self.run_cli()
        self.assertEqual(code, 0, report)
        for declaration in (
                "- [ ] T99: An additional ticket",
                "- [x] T1: A hidden duplicate ticket",
                "* [ ] T99: An additional ticket",
                "+ [ ] T1: A hidden duplicate ticket",
                "1. [ ] T99: An additional ticket",
                "  - [ ] T1: A hidden duplicate ticket"):
            with self.subTest(declaration=declaration):
                self.plan.write_text(original + "\n" + declaration + "\n")
                findings = self.assert_rule("ticket.invalid-definition")
                self.assertEqual(findings[0]["path"], str(self.plan))
                self.assertEqual(findings[0]["line"], len(original.splitlines()) + 2)

    def test_separate_acceptance_and_verification_fields(self):
        self.plan.write_text(self.plan.read_text().replace("| Acceptance criteria and verification | Invoke CLI on valid and invalid documents and assert exit codes. |", "| Acceptance criteria | Valid documents pass. |\n| Verification | Run the CLI fixture checks. |"))
        self.assertEqual(self.run_cli()[0], 0)
        self.edit_field("Verification", "None")
        self.assert_rule("field.required")

    def test_dependencies_unknown_cycle_later_wave_and_blocked_by(self):
        original = self.plan.read_text()
        self.edit_field("Dependencies", "T9")
        self.assert_rule("dependency.unknown")
        self.plan.write_text(original)
        self.add_ticket(same_wave=False)
        content = self.plan.read_text().replace("| Dependencies | None |", "| Dependencies | T2 |", 1)
        self.plan.write_text(content)
        self.assert_rule("dependency.earlier-wave")
        # Add a back edge while retaining an unknown edge: both must be reported.
        index = content.rfind("| Dependencies | None |")
        self.plan.write_text(content[:index] + content[index:].replace("| Dependencies | None |", "| Dependencies | T1, T99 |", 1))
        self.assert_rule("dependency.cycle")
        self.assert_rule("dependency.unknown")
        self.plan.write_text(original + "| Blocked by | T9 |\n")
        self.assert_rule("dependency.blocked-by-mismatch")

    def test_wave_unknown_duplicate_id_empty_and_capacity(self):
        original = self.plan.read_text()
        self.plan.write_text(original.replace("`T1`", "`T9`", 1))
        self.assert_rule("wave.unknown-member")
        self.plan.write_text(original + "\n## Wave W1: None\n")
        self.assert_rule("wave.duplicate-id")
        self.assert_rule("wave.empty")
        self.plan.write_text(original.replace("`T1`", "`T1`, `T2`, `T3`, `T4`, `T5`", 1))
        self.assert_rule("wave.capacity")

    def test_local_singleton_declared_conflicts_and_exact_ownership(self):
        self.add_ticket()
        original = self.plan.read_text()
        self.edit_field("Delegation mode", "main-local; credentials require main")
        self.assert_rule("wave.local-singleton")
        self.plan.write_text(original.replace("| Concurrency conflicts | None |", "| Concurrency conflicts | T2 |", 1))
        self.assert_rule("wave.declared-conflict")
        self.plan.write_text(original.replace("scripts/other2.py", "scripts/check.py"))
        self.assert_rule("wave.ownership-overlap")
        self.plan.write_text(original.replace("scripts/check.py", "scripts/"))
        self.assert_rule("wave.ownership-overlap")
        self.plan.write_text(original.replace("scripts/other2.py", "scripts/check.py.extra"))
        self.assertEqual(self.run_cli()[0], 0)

    def test_ambiguous_paths_are_findings_even_in_singleton_wave(self):
        for value in ("../src/a.py", "/tmp/a.py", "src/*.py", "src/[ab].py", "src/{a,b}.py", "src//a.py", "./src/a.py", "all source files", "module", "C:\\src"):
            with self.subTest(value=value):
                self.edit_field("Mutation ownership", value)
                self.assert_rule("ownership.ambiguous")

    def test_fenced_examples_commands_and_mismatched_closers_are_ignored(self):
        original = self.plan.read_text()
        fake = "\n### - [ ] T99: Fake\n## Wave W9: `T99`\n<!-- spec-coder:artifact-v99 plan -->\n"
        for opening, inner, closing in (("````markdown", "```", "`````"), ("~~~markdown", "```", "~~~~"), ("   ```markdown", "~~~", "   ```")):
            with self.subTest(opening=opening):
                self.plan.write_text(original + "\n" + opening + fake + inner + fake + closing + "\n")
                self.assertEqual(self.run_cli()[0], 0)
        self.plan.write_text(original + "\n```markdown" + fake)
        self.assert_rule("format.unclosed-fence")

    def test_html_comments_do_not_define_tickets_waves_or_markers(self):
        self.plan.write_text(self.plan.read_text() + "\n<!--\n### - [ ] T99: Comment\n## Wave W9: `T99`\n-->\n<!-- spec-coder:artifact-v99 plan --> example in prose\n")
        # A malformed standalone marker remains an error even with trailing prose.
        self.assert_rule("format.unsupported", code=2)
        self.plan.write_text(self.plan.read_text().rsplit("<!-- spec-coder:artifact-v99", 1)[0])
        self.assertEqual(self.run_cli()[0], 0)
        self.plan.write_text(self.plan.read_text() + "\n<!-- unclosed\n")
        self.assert_rule("format.unclosed-comment")

    def test_cli_does_not_create_bytecode_in_installed_package(self):
        plugin = self.cwd / "plugin"
        package = plugin / "spec_coder_checks"
        package.mkdir(parents=True)
        (plugin / "check-artifacts.py").write_bytes(CLI.read_bytes())
        for name in ("artifacts.py", "evidence.py", "waves.py"):
            (package / name).write_bytes((ROOT / "scripts/spec_coder_checks" / name).read_bytes())
        before = {str(p.relative_to(plugin)): p.read_bytes() for p in plugin.rglob("*") if p.is_file()}
        env = dict(os.environ)
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        result = subprocess.run([sys.executable, str(plugin / "check-artifacts.py"), "--phase", "plan", "--spec", str(self.spec), "--plan", str(self.plan)], cwd=self.cwd, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {str(p.relative_to(plugin)): p.read_bytes() for p in plugin.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_unusable_inputs_never_pass_and_plain_output_has_locations(self):
        self.spec.unlink()
        self.assert_rule("input.unusable", "spec", 2)
        self.spec.write_bytes(b"\xff")
        self.assert_rule("input.unusable", "spec", 2)
        self.spec.unlink()
        self.spec.mkdir()
        self.assert_rule("input.unusable", "spec", 2)
        result = subprocess.run([sys.executable, str(CLI), "--phase", "spec", "--spec", str(self.spec)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(str(self.spec) + ":1: input.unusable:", result.stdout)

    def test_delivery_requires_completion_and_recorded_evidence(self):
        self.assert_rule("delivery.incomplete", "delivery")
        self.assert_rule("field.required", "delivery")
        self.plan.write_text(self.plan.read_text().replace("[ ] T1", "[x] T1") + "| Verification commands | None |\n| Verification results | None |\n| Commits | None |\n")
        self.assert_rule("delivery.missing-evidence", "delivery")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.cwd), *args], check=True, capture_output=True, text=True).stdout.strip()

    def test_delivery_resolves_only_local_commit_ids_and_never_executes_commands(self):
        self.git("init", "-q")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-qm", "fixture")
        commit = self.git("rev-parse", "HEAD")
        sentinel = self.cwd / "COMMAND_MUST_NOT_RUN"
        self.plan.write_text(self.plan.read_text().replace("[ ] T1", "[x] T1") +
                             "| Verification commands | touch " + str(sentinel) + " |\n| Verification results | exit 0, one test passed |\n| Commits | " + commit + " |\n")
        before = {p: p.read_bytes() for p in (self.spec, self.plan)}
        status = self.git("status", "--porcelain=v1")
        index = (self.cwd / ".git/index").read_bytes() if (self.cwd / ".git/index").exists() else None
        code, report = self.run_cli("delivery")
        self.assertEqual(code, 0, report)
        self.assertFalse(sentinel.exists())
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertEqual(status, self.git("status", "--porcelain=v1"))
        self.assertEqual(index, (self.cwd / ".git/index").read_bytes() if (self.cwd / ".git/index").exists() else None)
        for value, rule in (("HEAD", "delivery.invalid-commit"), ("--help", "delivery.invalid-commit"), ("$(touch BAD)", "delivery.invalid-commit"), ("f" * 40, "delivery.unknown-commit")):
            self.edit_field("Commits", value)
            self.assert_rule(rule, "delivery")
        self.assertFalse((self.cwd / "BAD").exists())
        blob = self.git("hash-object", "-w", str(self.spec))
        self.edit_field("Commits", blob)
        self.assert_rule("delivery.unknown-commit", "delivery")


if __name__ == "__main__":
    unittest.main()
