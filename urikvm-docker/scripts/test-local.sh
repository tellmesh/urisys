#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -e . >/dev/null
urisys-kvm call kvm://local/monitor/query/list
urisys-kvm call kvm://local/task/command/click-text --payload '{"text":"OK"}' --approve
urisys-kvm flow flows/kvm-click-ok.uri.flow.yaml --approve
python -m pytest tests -q
