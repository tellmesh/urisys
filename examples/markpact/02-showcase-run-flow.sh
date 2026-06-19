#!/usr/bin/env bash
# Smoke: compile + run embedded flows from uribrowser.showcase.markpact.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=../scripts/paths.sh
source "$ROOT/scripts/paths.sh"

export TELLMESH_ROOT="${TELLMESH_ROOT:-$(cd "$ROOT/.." && pwd)}"
SHOWCASE="$(markpact_contracts_packs)/uribrowser.showcase.markpact.md"
EVENTS="${TMPDIR:-/tmp}/urisys-showcase-flow.jsonl"

echo "== analyze =="
urisys markpact analyze "$SHOWCASE"

echo "== run-flow use case =="
urisys --events "$EVENTS" markpact run-flow "${SHOWCASE}#open-and-read" --approve --dry-run

echo "== run-flow integration (needs sibling packs or --auto-install) =="
urisys --events "$EVENTS" markpact run-flow "${SHOWCASE}#install-and-verify" --approve --dry-run || {
  echo "hint: export TELLMESH_ROOT=$TELLMESH_ROOT or add --auto-install" >&2
  exit 1
}

echo "== markpact run (thin CLI, same flows) =="
urisys --events "$EVENTS" markpact run "${SHOWCASE}#open-and-read" --as flow --approve --dry-run
urisys --events "$EVENTS" markpact run "${SHOWCASE}#install-and-verify" --as flow --approve --dry-run

echo "PASS showcase run-flow"
