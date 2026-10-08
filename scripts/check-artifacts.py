#!/usr/bin/env python3
"""Check supported local spec-coder Markdown without modifying or executing it."""
import sys

# A read-only check must also preserve the installed plugin directory.
sys.dont_write_bytecode = True

import argparse
import json

from spec_coder_checks.artifacts import check_artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=("spec", "plan", "delivery"))
    parser.add_argument("--spec", required=True, help="path to supported specification")
    parser.add_argument("--plan", help="path to supported plan; required for plan/delivery")
    parser.add_argument("--repo", default=".", help="local Git repository for delivery commits (default: cwd)")
    parser.add_argument("--json", action="store_true", help="emit status, phase and source-located findings as JSON")
    args = parser.parse_args()
    code, report = check_artifacts(args.spec, args.plan, args.phase, args.repo)
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print(f"{report['phase']}: {report['status']}")
        for finding in report["findings"]:
            print(f"{finding['path']}:{finding['line']}: {finding['rule']}: {finding['message']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
