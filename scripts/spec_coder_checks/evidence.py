"""Versioned observations and pure baseline comparison; no command execution."""
from datetime import datetime
import json
import re


def parse_json(text):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON field: " + key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique_pairs)


def markdown_regions(text):
    """Yield active lines and fenced blocks, ignoring surrounding HTML comments."""
    fence = None
    language = ""
    payload = []
    in_comment = False
    for line in text.splitlines():
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line):
                yield "fence", language, "\n".join(payload)
                fence = None
            else:
                payload.append(line)
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if re.fullmatch(r"<!-- spec-coder:artifact-v1 (spec|plan) -->", line):
            yield "line", "", line
            continue
        if "<!--" in line:
            in_comment = "-->" not in line.split("<!--", 1)[1]
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            fence, language = match[1], match[2].strip()
            if language.startswith("spec-coder-verification") and language != "spec-coder-verification":
                raise ValueError("malformed spec-coder-verification fence label")
            payload = []
        else:
            yield "line", "", line
    if fence is not None and language == "spec-coder-verification":
        raise ValueError("unclosed spec-coder-verification record")


def is_active_artifact(text):
    return any(kind == "line" and re.fullmatch(r"<!-- spec-coder:artifact-v1 (spec|plan) -->", content)
               for kind, _, content in markdown_regions(text))


def read_records(text):
    records = [parse_json(content) for kind, language, content in markdown_regions(text)
               if kind == "fence" and language == "spec-coder-verification"]
    if not records:
        raise ValueError("missing spec-coder-verification record")
    return records


def unknown(value):
    return not isinstance(value, str) or not value.strip() or value.strip() == "?" or bool(re.search(r"\b(unknown|unconfirmed|unavailable)\b", value, re.IGNORECASE))


def context_reasons(context):
    reasons = []
    if unknown(context.get("request")):
        reasons.append("current request identity is unknown")
    for name in ["toolchain", "dependencies", "environment"]:
        value = context.get(name)
        if not isinstance(value, dict):
            reasons.append(name + " observations must be a JSON object")
            continue
        if name != "environment" and not value:
            reasons.append(name + " observations are unknown")
        for key, observation in value.items():
            if not key or (unknown(observation) and not (name == "environment" and observation == "")):
                reasons.append(name + " observation is unknown or invalid: " + key)
        if name == "dependencies" and not {"installed", "external"}.issubset(value):
            reasons.append("dependencies require explicit installed and external observations")
    return reasons


def compare(record, context, current):
    if not isinstance(record, dict) or type(record.get("version")) is not int or record["version"] != 1:
        return ["malformed or unsupported verification record"]
    required = {"context", "before", "after", "exit_code", "observed_at", "status", "reasons", "record_id"}
    if not required.issubset(record):
        return ["incomplete verification record"]
    if not isinstance(record["record_id"], str) or not re.fullmatch(r"[0-9a-f]{32}", record["record_id"]):
        return ["missing or invalid record identity"]
    if not isinstance(record["context"], dict) or (record["exit_code"] is not None and type(record["exit_code"]) is not int) or not isinstance(record["reasons"], list) or not all(isinstance(reason, str) for reason in record["reasons"]):
        return ["malformed verification record"]
    try:
        if not isinstance(record["observed_at"], str) or datetime.fromisoformat(record["observed_at"]).tzinfo is None:
            raise ValueError("missing timezone")
    except ValueError:
        return ["invalid observation time"]
    reasons = context_reasons(context)
    if record["status"] != "captured" or record["reasons"]:
        reasons.append("record does not declare a stable successful capture")
    if record["exit_code"] != 0:
        reasons.append("baseline command did not succeed")
    for key in sorted(set(record["context"]) | set(context)):
        if record["context"].get(key) != context.get(key):
            reasons.append("declared execution context changed: " + key)
    if record["before"] != record["after"]:
        reasons.append("workspace inputs changed during baseline execution")
    for snapshot in [record["before"], record["after"], current]:
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get("inputs"), dict) or not isinstance(snapshot.get("uncertainty"), list) or not all(isinstance(reason, str) for reason in snapshot["uncertainty"]):
            reasons.append("malformed workspace observation")
        elif snapshot["uncertainty"]:
            reasons.extend(snapshot["uncertainty"])
    if record["after"] != current:
        reasons.append("workspace inputs changed since baseline")
    return list(dict.fromkeys(reasons))
