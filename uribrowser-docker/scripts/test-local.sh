#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -e . >/dev/null
urisys-browser call browser://default/query/status
urisys-browser call browser://default/page/command/open --payload '{"url":"https://example.com"}' --approve
urisys-browser flow flows/browser-demo.uri.flow.yaml --approve
python -m pytest tests -q
