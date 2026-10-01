#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v codex >/dev/null 2>&1; then
  echo "error: codex is not available on PATH" >&2
  exit 1
fi

codex plugin marketplace add "$REPO_ROOT"
codex plugin add spec-coder@spec-coder

echo "spec-coder@spec-coder is installed. Start a new Codex session to refresh /skills."
