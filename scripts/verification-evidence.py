#!/usr/bin/env python3
"""Capture an explicit baseline or compare its Markdown evidence without execution."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
from spec_coder_checks.evidence import compare, parse_json, read_records
from spec_coder_checks.workspace import paths, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["capture", "check"])
    for name in ["repo", "cwd", "request", "artifact", "toolchain", "dependencies", "environment"]:
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--exclude-output", action="append", default=[])
    argv = sys.argv[1:]
    separator = argv.index("--") if "--" in argv else len(argv)
    args = parser.parse_args(argv[:separator])
    try:
        command = argv[separator + 1:]
        if not command:
            raise ValueError("an explicit command argument vector is required after --")
        repo, cwd, exclusions = paths(args.repo, args.cwd, args.artifact, args.exclude_output)
        context = {"request": args.request, "command": command, "exclusions": exclusions}
        for name in ["toolchain", "dependencies", "environment"]:
            value = parse_json(getattr(args, name))
            if not isinstance(value, dict):
                raise ValueError(name + " must be a JSON object")
            context[name] = value
        before = snapshot(repo, cwd, exclusions)
        if args.operation == "capture":
            execution_error = None
            try:
                exit_code = subprocess.run(command, cwd=cwd, stdout=sys.stderr, stderr=sys.stderr, shell=False).returncode
            except KeyboardInterrupt:
                exit_code = -2
                execution_error = "baseline capture interrupted"
            except OSError as error:
                exit_code = None
                execution_error = "baseline could not start: " + str(error)
            record = {"version": 1, "record_id": uuid.uuid4().hex, "context": context, "before": before, "after": snapshot(repo, cwd, exclusions), "exit_code": exit_code, "observed_at": datetime.now(timezone.utc).isoformat(), "status": "captured", "reasons": []}
            record["reasons"] = compare(record, context, record["after"])
            if execution_error:
                record["reasons"].append(execution_error)
            record["status"] = "captured" if not record["reasons"] else "rerun"
            print(json.dumps(record, sort_keys=True))
            return 0 if not record["reasons"] else 1
        records = read_records(Path(exclusions[0]).read_text(encoding="utf-8"))
        matching = [record for record in records if isinstance(record, dict) and isinstance(record.get("context"), dict) and record["context"].get("command") == command]
        if len(matching) != 1:
            reasons = ["missing or ambiguous record for expected command"]
        else:
            reasons = compare(matching[0], context, before)
        print(json.dumps({"status": "rerun" if reasons else "reusable", "reasons": reasons, "record_id": matching[0].get("record_id") if len(matching) == 1 else None}, sort_keys=True))
        return 1 if reasons else 0
    except (OSError, ValueError, RecursionError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "rerun", "reasons": [str(error)]}, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
