#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if command -v uv >/dev/null 2>&1; then
  uv sync --group dev
  uv run pytest tests/ -q
else
  "$ROOT/../uri-packs/scripts/install-editable.sh"
  python -m pytest tests/ -q
fi
