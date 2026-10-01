#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"
VALIDATOR="${SKILL_VALIDATOR:-$CODEX_HOME_DIR/skills/.system/skill-creator/scripts/quick_validate.py}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -f "$VALIDATOR" ]; then
  echo "error: skill validator not found: $VALIDATOR" >&2
  echo "set SKILL_VALIDATOR to the quick_validate.py path" >&2
  exit 1
fi

cd "$REPO_ROOT"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON_BIN" -m unittest -v tests/test_contracts.py

for skill in skills/*; do
  /usr/bin/python3 "$VALIDATOR" "$skill"
done

git diff --check
