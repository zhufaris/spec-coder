"""Read-only parsing and structural checks for the documented artifact-v1 grammar."""
from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
import subprocess

from .waves import inspect_waves

DECISION = r"(?:SCN|INV|ARCH)-[1-9][0-9]*"
TICKET_ID = r"T[1-9][0-9]*"
SPEC_SECTIONS = (
    "Problem Statement", "Solution", "User Stories", "Implementation Decisions",
    "Testing Decisions", "Out of Scope", "Further Notes",
)


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    line: int
    message: str


@dataclass
class Document:
    path: str
    lines: list
    findings: list = field(default_factory=list)

    def add(self, rule, line, message):
        self.findings.append(Finding(rule, self.path, max(1, line), message))


@dataclass
class Ticket:
    id: str
    line: int
    complete: bool
    fields: dict = field(default_factory=dict)


def active_lines(text):
    """Ignore CommonMark backtick/tilde fences while retaining source lines."""
    result = []
    fence = None
    comment = None
    for number, line in enumerate(text.splitlines(), 1):
        if fence:
            char, length, opening = fence
            if re.fullmatch(r" {0,3}" + re.escape(char) + "{" + str(length) + r",}[ \t]*", line):
                fence = None
            continue
        if comment is not None:
            if "-->" in line:
                comment = None
            continue
        # Marker declarations are preserved for exact validation below. Other
        # HTML comments are inactive, including fence/ticket examples inside.
        marker_candidate = re.match(r"^ {0,3}<!--\s*spec-coder:artifact", line)
        if "<!--" in line and not marker_candidate:
            if "-->" not in line.split("<!--", 1)[1]:
                comment = number
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match and not (match[1][0] == "`" and "`" in match[2]):
            fence = (match[1][0], len(match[1]), number)
            continue
        result.append((number, line))
    issues = []
    if fence:
        issues.append(("format.unclosed-fence", fence[2], "code fence is not closed; following content cannot be checked"))
    if comment:
        issues.append(("format.unclosed-comment", comment, "HTML comment is not closed; following content cannot be checked"))
    return result, issues


def load_document(path, kind):
    name = str(Path(path).absolute())
    try:
        if not Path(path).is_file():
            raise OSError("path is not a readable regular file")
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        return None, "unusable", [Finding("input.unusable", name, 1, f"cannot read {kind}: {exc}")]
    lines, issues = active_lines(text)
    doc = Document(name, lines)
    markers = [(n, s.strip()) for n, s in lines if re.match(r"^ {0,3}<!--\s*spec-coder:artifact", s)]
    expected = f"<!-- spec-coder:artifact-v1 {kind} -->"
    if len(markers) != 1 or markers[0][1] != expected:
        doc.add("format.unsupported", markers[0][0] if markers else 1,
                f"expected exactly one standalone {expected}; normalize manually before checking")
        return doc, "unsupported", doc.findings
    for rule, number, message in issues:
        doc.add(rule, number, message)
    if "\x00" in text:
        doc.add("format.invalid-text", 1, "NUL bytes are not supported Markdown")
    return doc, None, doc.findings


def unquote(value):
    """Allow one balanced inline-code pair; leave malformed quotes invalid."""
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and value.count("`") == 2:
        return value[1:-1]
    return value


def split_ids(doc, value, line, pattern, label, allow_none=True):
    value = value.strip()
    if allow_none and value.lower() == "none":
        return []
    parts = [unquote(p) for p in value.split(",")]
    if not parts or any(not re.fullmatch(pattern, p) for p in parts):
        doc.add("field.invalid-list", line, f"{label} must be comma-separated IDs" + (" or None" if allow_none else ""))
        return []
    if len(parts) != len(set(parts)):
        doc.add("reference.duplicate", line, f"{label} contains duplicate IDs")
    return parts


def table_row(line):
    if not line.startswith("|") or not line.rstrip().endswith("|"):
        return None
    parts = re.split(r"(?<!\\)\|", line.strip())[1:-1]
    if len(parts) != 2:
        return None
    key, value = (p.strip() for p in parts)
    if key.lower() == "field" or re.fullmatch(r":?-+:?", key):
        return None
    return key.lower(), value


def check_spec(doc):
    sections = {}
    decisions = {}
    references = []
    for number, line in doc.lines:
        match = re.fullmatch(r"## (.+?)\s*", line)
        if match:
            sections.setdefault(match[1], []).append(number)
        definition = re.fullmatch(r"#{3,6} (" + DECISION + r"): (\S.*)", line)
        if definition:
            decision_id = definition[1]
            if decision_id in decisions:
                doc.add("decision.duplicate-id", number, f"{decision_id} already defined at line {decisions[decision_id]}")
            else:
                decisions[decision_id] = number
        elif re.match(r"#{1,6}\s+(SCN|INV|ARCH)-", line):
            doc.add("decision.invalid-definition", number, "use ### SCN-1: Nonempty title (or INV-/ARCH-)")
        row = table_row(line)
        if row is None and re.match(r"\|\s*(?:Spec references|References)\s*\|", line, re.IGNORECASE):
            doc.add("field.malformed", number, "reference fields require a two-column Markdown table")
        inline = re.fullmatch(r"(?:Spec references|References):\s*(.*)", line)
        if (row and row[0] in {"spec references", "references"}) or inline:
            value = row[1] if row else inline[1]
            references.extend((ref, number) for ref in split_ids(doc, value, number, DECISION, "References"))
    for section in SPEC_SECTIONS:
        locations = sections.get(section, [])
        if not locations:
            doc.add("spec.required-section", 1, f"missing ## {section}")
        elif len(locations) > 1:
            doc.add("spec.duplicate-section", locations[1], f"duplicate ## {section}")
    for ref, number in references:
        if ref not in decisions:
            doc.add("reference.unknown", number, f"undefined specification decision {ref}")
    return decisions


def parse_plan(doc):
    tickets, waves = [], []
    current = None
    seen = set()
    wave_ids = set()
    for number, line in doc.lines:
        heading = re.fullmatch(r"### - \[([ xX])\] (" + TICKET_ID + r"): (\S.*)", line)
        wave = re.fullmatch(r"## Wave (W[1-9][0-9]*):\s*(.*)", line)
        if heading:
            current = Ticket(heading[2], number, heading[1].lower() == "x")
            if current.id in seen:
                doc.add("ticket.duplicate-id", number, f"duplicate ticket {current.id}")
            seen.add(current.id)
            tickets.append(current)
        elif wave:
            current = None
            if wave[1] in wave_ids:
                doc.add("wave.duplicate-id", number, f"duplicate wave {wave[1]}")
            wave_ids.add(wave[1])
            waves.append((number, split_ids(doc, wave[2], number, TICKET_ID, "Wave members")))
        elif (re.match(r"#{1,6}\s+(?:- \[|T[0-9])", line) or
              re.match(r" {0,3}(?:[-+*]|[0-9]+[.)])\s+\[[ xX]\]\s+T[0-9]+\s*:", line)):
            current = None
            doc.add("ticket.invalid-definition", number, "use ### - [ ] T1: Nonempty title")
        elif re.match(r"## Wave\b", line):
            current = None
            doc.add("wave.invalid-definition", number, "use ## Wave W1: `T1`, `T2`")
        elif re.match(r"#{1,3} ", line):
            current = None
        elif current:
            row = table_row(line)
            if row:
                key, value = row
                if key in current.fields:
                    doc.add("field.duplicate", number, f"{current.id} repeats field {key}")
                else:
                    current.fields[key] = (value, number)
            elif line.startswith("|") and not re.fullmatch(
                    r"\|\s*(?:Field\s*\|\s*Content|:?-+:?\s*\|\s*:?-+:?)\s*\|\s*", line, re.IGNORECASE):
                doc.add("field.malformed", number, "ticket fields require a two-column Markdown table; escape literal pipes")
    if not tickets:
        doc.add("plan.missing-tickets", 1, "plan must declare at least one checkbox ticket")
    if not waves:
        doc.add("plan.missing-waves", 1, "plan must declare ordered wave sections")
    return tickets, waves


def required_field(doc, ticket, name):
    value, line = ticket.fields.get(name, ("", ticket.line))
    if not value.strip() or value.strip().lower() in {"tbd", "todo", "n/a"}:
        doc.add("field.required", line, f"{ticket.id} requires nonempty {name}")
    return value, line


def ownership_paths(doc, value, line):
    if value.lower() == "none":
        return []
    paths = []
    for raw in value.split(","):
        path = unquote(raw)
        components = path.rstrip("/").split("/")
        if (not path or path.startswith(("/", "~", "-")) or
                re.search(r"[\s*?\[\]{}\\:`]", path) or
                any(part in {"", ".", ".."} for part in components) or
                ("/" not in path and "." not in path)):
            doc.add("ownership.ambiguous", line,
                    f"{raw!r} is not an exact repository-relative file/module path; resolve manually (no globs, traversal or absolute paths)")
        else:
            paths.append(path.rstrip("/"))
    if len(paths) != len(set(paths)):
        doc.add("ownership.duplicate", line, "mutation ownership repeats a path")
    return paths


def check_plan(doc, decisions):
    tickets, waves = parse_plan(doc)
    normalized = []
    covered = set()
    for ticket in tickets:
        refs, refs_line = required_field(doc, ticket, "spec references")
        ids = split_ids(doc, refs, refs_line, DECISION, "Spec references")
        for ref in ids:
            if ref not in decisions:
                doc.add("reference.unknown", refs_line, f"{ticket.id} references undefined specification decision {ref}")
            covered.add(ref)
        deps, deps_line = required_field(doc, ticket, "dependencies")
        dependencies = split_ids(doc, deps, deps_line, TICKET_ID, "Dependencies")
        if "blocked by" in ticket.fields:
            value, line = ticket.fields["blocked by"]
            blocked = split_ids(doc, value, line, TICKET_ID, "Blocked by")
            if set(blocked) != set(dependencies):
                doc.add("dependency.blocked-by-mismatch", line, "Blocked by must agree with Dependencies")
        mode, mode_line = required_field(doc, ticket, "delegation mode")
        # A semicolon permits an explicit reason without guessing arbitrary prose.
        mode = mode.split(";", 1)[0].strip().lower()
        aliases = {"default direct worker": "delegate", "required delegation": "delegate",
                   "delegate": "delegate", "main-local": "main-local", "local": "local",
                   "opt-out": "local"}
        if mode not in aliases:
            doc.add("ticket.invalid-mode", mode_line, "unknown delegation mode; use Default direct worker, required delegation, main-local, local, delegate or opt-out")
        paths, paths_line = required_field(doc, ticket, "mutation ownership")
        conflicts, conflicts_line = required_field(doc, ticket, "concurrency conflicts")
        conflict_ids = split_ids(doc, conflicts, conflicts_line, TICKET_ID, "Concurrency conflicts")
        if "acceptance criteria and verification" in ticket.fields:
            value, line = required_field(doc, ticket, "acceptance criteria and verification")
            if value.lower() == "none":
                doc.add("field.required", line, f"{ticket.id} requires acceptance and verification content")
        else:
            for name in ("acceptance criteria", "verification"):
                value, line = required_field(doc, ticket, name)
                if value.lower() == "none":
                    doc.add("field.required", line, f"{ticket.id} requires {name} content")
        normalized.append(dict(id=ticket.id, mode=aliases.get(mode), dependencies=dependencies,
                               conflicts=conflict_ids, ownership=ownership_paths(doc, paths, paths_line)))
    by_id = {ticket.id: ticket for ticket in tickets}
    for finding in inspect_waves(normalized, [members for _, members in waves]):
        if finding.wave_index is not None:
            line = waves[finding.wave_index][0]
        elif finding.ticket_id in by_id:
            ticket = by_id[finding.ticket_id]
            field_name = "dependencies" if finding.rule.startswith("dependency.") else "concurrency conflicts"
            line = ticket.fields.get(field_name, ("", ticket.line))[1] if finding.rule.startswith(("dependency.", "conflict.", "wave.declared")) else ticket.line
        else:
            line = 1
        doc.add(finding.rule, line, finding.message)
    return tickets, covered


def check_delivery(doc, tickets, repo):
    for ticket in tickets:
        if not ticket.complete:
            doc.add("delivery.incomplete", ticket.line, f"{ticket.id} is not complete")
        for name in ("verification commands", "verification results", "commits"):
            value, line = required_field(doc, ticket, name)
            if value.lower() == "none":
                doc.add("delivery.missing-evidence", line, f"{ticket.id} needs recorded {name}")
            if name != "commits" or not value or value.lower() == "none":
                continue
            for raw in value.split(","):
                commit = unquote(raw)
                if not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit):
                    doc.add("delivery.invalid-commit", line, f"{commit!r} must be a local hexadecimal commit ID (7-64 characters)")
                    continue
                try:
                    result = subprocess.run(
                        ["git", "--no-optional-locks", "-C", str(repo), "rev-parse", "--verify", "--end-of-options", commit + "^{commit}"],
                        capture_output=True, text=True, timeout=10,
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    doc.add("delivery.commit-unavailable", line, f"cannot inspect local Git commits: {exc}")
                    continue
                if result.returncode:
                    doc.add("delivery.unknown-commit", line, f"{commit} does not resolve to a local commit in {repo}")


def check_artifacts(spec_path, plan_path=None, phase="spec", repo="."):
    """Return (exit status, JSON-ready report); do not execute artifact commands."""
    findings = []
    documents = []
    failures = []
    for path, kind in [(spec_path, "spec")] + ([(plan_path, "plan")] if phase != "spec" else []):
        if path is None:
            failures.append("unusable")
            findings.append(Finding("input.required", "", 1, f"{kind} path is required"))
            continue
        doc, failure, load_findings = load_document(path, kind)
        if failure:
            failures.append(failure)
            findings.extend(load_findings)
        elif doc:
            documents.append(doc)
    if failures:
        status = "unusable" if "unusable" in failures else "unsupported"
        return 2, dict(status=status, phase=phase, findings=[asdict(f) for f in findings])
    spec = documents[0]
    decisions = check_spec(spec)
    if phase != "spec":
        plan = documents[1]
        tickets, covered = check_plan(plan, decisions)
        for decision in decisions.keys() - covered:
            spec.add("coverage.uncovered", decisions[decision], f"{decision} has no implementing ticket")
        if phase == "delivery":
            check_delivery(plan, tickets, repo)
    findings = [asdict(f) for doc in documents for f in doc.findings]
    return (1 if findings else 0), dict(status="findings" if findings else "passed", phase=phase, findings=findings)
