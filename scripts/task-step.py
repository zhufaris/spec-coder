"""Read one task step without exposing sibling steps or creating workflow state."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TASKS = ("feature", "bug-fix", "refactor", "performance", "skill-change", "workflow-eval", "generic")
STAGES = ("discovery", "design", "planning", "implementation", "delivery")


def extract_step(text, stage):
    if stage not in STAGES:
        raise ValueError("unknown stage")
    procedures = list(re.finditer(r"(?ms)^### Procedure\n(.*?)(?=^#{1,3} |\Z)", text))
    if len(procedures) != 1:
        raise ValueError("task must declare one Procedure section")
    steps = [line for line in procedures[0][1].splitlines()
             if re.match(r"^\d+\. ", line) and f"](../stages/{stage}.md#procedure)" in line]
    all_matches = [line for line in text.splitlines()
                   if re.match(r"^\d+\. ", line) and f"](../stages/{stage}.md#procedure)" in line]
    if len(steps) != 1 or len(all_matches) != 1:
        raise ValueError("task must declare exactly one matching stage step")
    if not re.search(r"\]\(\.\./stages/" + re.escape(stage) + r"\.md#procedure\):\s*\S", steps[0]):
        raise ValueError("stage instruction must be nonempty")
    obligations = []
    for label in ("Entry and design", "Red or pin", "Delivery proof", "Skip reasons"):
        prefix = f"- {label}:"
        matches = [line for line in text.splitlines() if line.startswith(prefix)]
        if len(matches) != 1 or not matches[0][len(prefix):].strip():
            raise ValueError("task must declare each proof obligation once")
        obligations.append(matches[0])
    matches = list(re.finditer(r"(?ms)^### Conditional Principles\n(.*?)(?=^#{1,3} |\Z)", text))
    if len(matches) != 1 or not matches[0][1].strip():
        raise ValueError("task must declare principle triggers")
    triggers = matches[0][1].strip()
    if any(not re.match(r"^- \*\*[^*]+:\*\* .+", line)
           or "../stages/" in line for line in triggers.splitlines() if line.strip()):
        raise ValueError("principle section must contain only trigger bullets")
    return {"stage": stage, "step": steps[0], "constraints": obligations,
            "principle_triggers": triggers}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, choices=TASKS)
    parser.add_argument("--stage", required=True, choices=STAGES)
    args = parser.parse_args()
    try:
        packet = extract_step((ROOT / "playbooks/tasks" / (args.task + ".md")).read_text(encoding="utf-8"), args.stage)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, f"task-step: {exc}\n")
    print(json.dumps({"task": args.task, **packet}, ensure_ascii=False))


if __name__ == "__main__":
    main()
