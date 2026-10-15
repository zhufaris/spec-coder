#!/usr/bin/env python3
"""Emit one canonical ProgressSnapshot line."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


# This script is also executed directly from a relocated bundle.  Disable
# bytecode generation before loading the bundled helper so that invocation
# never mutates that bundle with ``__pycache__`` files.
sys.dont_write_bytecode = True


# The public script must work when invoked by absolute path from any directory.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from spec_coder_checks.progress import (  # noqa: E402
    PROGRESS_PHASES,
    VERIFICATION_STATES,
    build_progress_snapshot,
)


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("--ticket-or-axis", required=True)
    argument_parser.add_argument("--worker-handle", required=True)
    argument_parser.add_argument("--phase", choices=sorted(PROGRESS_PHASES), required=True)
    argument_parser.add_argument("--active-command", required=True)
    argument_parser.add_argument("--progress-evidence", required=True)
    argument_parser.add_argument(
        "--verification-state", choices=sorted(VERIFICATION_STATES), required=True
    )
    argument_parser.add_argument("--blocker", required=True)
    return argument_parser


def main(argv: list[str] | None = None) -> int:
    argument_parser = parser()
    args = argument_parser.parse_args(argv)
    try:
        snapshot = build_progress_snapshot(
            ticket_or_axis=args.ticket_or_axis,
            worker_handle=args.worker_handle,
            phase=args.phase,
            active_command=args.active_command,
            progress_evidence=args.progress_evidence,
            verification_state=args.verification_state,
            blocker=args.blocker,
        )
    except ValueError as exc:
        argument_parser.error(str(exc))
    print(
        "ProgressSnapshot "
        # ASCII-only JSON escapes every Unicode line separator (including
        # U+0085, U+2028, and U+2029), keeping this wire record to one
        # physical line while json.loads preserves the original values.
        + json.dumps(dict(snapshot), ensure_ascii=True, separators=(",", ":"))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
