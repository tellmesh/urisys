#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -e . >/dev/null
python3 -m pytest tests
urisys-rdp --config config/rdp-kvm-profile.json --events data/events.jsonl flow flows/rdp-kvm-smoke.uri.flow.yaml --approve --dry-run >/tmp/urirdp-flow.json
python3 -m json.tool /tmp/urirdp-flow.json >/dev/null
echo "local tests passed"
