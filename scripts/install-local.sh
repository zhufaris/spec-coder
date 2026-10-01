#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v traecli >/dev/null 2>&1; then
  echo "error: traecli is not available on PATH" >&2
  exit 1
fi

traecli plugin install "$REPO_ROOT" --type local --yes
traecli plugin enable spec-coder@local

echo "spec-coder@local is installed and enabled. Restart TraeCode to refresh /skills."
