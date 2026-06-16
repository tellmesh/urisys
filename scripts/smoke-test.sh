#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/uricore/core/python:$ROOT/urisys/src:$(find "$ROOT/packages/python" -mindepth 1 -maxdepth 1 -type d -printf '%p/src:')"
cd "$ROOT"

python -m urisys.cli --packs browser call browser://default/page/open --payload '{"url":"https://example.com"}' --approve
python -m urisys.cli --packs docker call docker://container/web/command/restart --approve --dry-run
python -m urisys.cli --packs all flow "$ROOT/urisys/flows/device-maintenance.uri.flow.yaml" --approve --dry-run
python -m urisys.cli markpact validate "$ROOT/urisys/markpacts/packs/uribrowser.markpact.md"
python -m urisys.cli markpact test "$ROOT/urisys/markpacts/packs/uribrowser.markpact.md"
python -m urisys.cli --packs none --markpact "$ROOT/urisys/markpacts/packs/urisystemd.markpact.md" call systemd://unit/docker.service/query/status
