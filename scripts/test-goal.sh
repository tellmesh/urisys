#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT/../uri-packs/scripts/install-editable.sh"
cd "$ROOT"
python -m pytest tests/ -q
