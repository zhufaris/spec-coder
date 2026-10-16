#!/usr/bin/env python3
"""Read-only JSON interface for deterministic workspace policy facts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from spec_coder_checks.workspace_policy import (  # noqa: E402
    PolicyBlocker,
    inspect,
    propose_ignore_for_repository,
    validate_allocation,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subcommands.add_parser("inspect")
    inspect_parser.add_argument("--repo", required=True)
    inspect_parser.add_argument("--branch", required=True)
    allocation = subcommands.add_parser("validate-allocation")
    allocation.add_argument("--repo", required=True)
    allocation.add_argument("--branch", required=True)
    allocation.add_argument("--workspace", "--path", dest="workspace", required=True)
    allocation.add_argument("--recorded-base", required=True)
    proposal = subcommands.add_parser("propose-ignore")
    proposal.add_argument("--repo", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect":
            result = inspect(args.repo, args.branch).as_json()
        elif args.command == "validate-allocation":
            result = validate_allocation(args.repo, args.branch, args.workspace, args.recorded_base)
        else:
            result = propose_ignore_for_repository(args.repo)
    except PolicyBlocker as blocker:
        print(json.dumps(blocker.as_json(), ensure_ascii=False, separators=(",", ":")))
        return 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
