#!/usr/bin/env python3
"""Run deterministic affected checks for explicitly supplied repository paths."""
import argparse
import json
from pathlib import Path
import sys

from spec_coder_checks.affected import (
    build_affected_commands,
    execute_affected_commands,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="physical repository root")
    parser.add_argument(
        "--path",
        action="append",
        required=True,
        help="owned repository-relative path; repeat as needed",
    )
    parser.add_argument(
        "--python-bin", default=sys.executable, help="Python executable for unittest"
    )
    parser.add_argument(
        "--validator",
        default=str(
            Path.home()
            / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"
        ),
        help="quick_validate.py executable",
    )
    args = parser.parse_args(argv)
    try:
        commands = build_affected_commands(
            Path(args.repo), args.path, args.python_bin, args.validator
        )
        result = execute_affected_commands(commands)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
