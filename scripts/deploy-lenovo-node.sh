#!/usr/bin/env bash
# Upgrade lenovo slave via URI (no .sh on target). Run from dev machine on LAN.
#
#   HOST=192.168.188.212 bash scripts/deploy-lenovo-node.sh
#   LENOVO=http://192.168.188.201:8790 DEV=http://192.168.188.212:8765 bash scripts/deploy-lenovo-node.sh
set -euo pipefail

LENOVO="${LENOVO:-http://192.168.188.201:8790}"
DEV="${DEV:-http://192.168.188.212:8765}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

call() {
  local uri="$1" payload="${2:-{}}"
  curl -sS -X POST "$LENOVO/uri/call" \
    -H 'Content-Type: application/json' \
    -d "{\"uri\":\"$uri\",\"payload\":$payload,\"context\":{\"approved\":true,\"allow_real\":true}}"
}

health() {
  curl -sS --connect-timeout 5 "$LENOVO/health"
}

echo "== health =="
health | python3 -m json.tool

echo ""
echo "== build wheels (if missing) =="
mkdir -p /tmp/urisys-deploy
if [ ! -f /tmp/urisys-deploy/urisys-0.1.24-py3-none-any.whl ]; then
  (cd "$ROOT" && python3 -m build -o /tmp/urisys-deploy)
fi

echo ""
echo "== HTTP serve wheels on DEV (8765) =="
if ! pgrep -f "http.server 8765.*192.168.188.212" >/dev/null 2>&1; then
  python3 -m http.server 8765 --bind 192.168.188.212 --directory /tmp/urisys-deploy &
  sleep 1
fi

echo ""
echo "== pip install urisys 0.1.24 on lenovo =="
call shell://pip "{\"args\":[\"install\",\"-U\",\"$DEV/urisys-0.1.24-py3-none-any.whl\"]}" | python3 -m json.tool

echo ""
echo "== pip install urihim from GitHub v0.1.3 =="
call shell://pip "{\"args\":[\"install\",\"-U\",\"https://github.com/tellmesh/urihim/releases/download/v0.1.3/urihim-0.1.3-py3-none-any.whl\"]}" | python3 -m json.tool

echo ""
echo "== restart urisys-node =="
call shell://bash '{"args":["-lc","pkill -f \"urisys-node serve\" || true; sleep 2; nohup /home/tom/venv/bin/urisys-node serve --host 0.0.0.0 --port 8790 >> /tmp/urisys-node.log 2>&1 & sleep 2; curl -sS http://127.0.0.1:8790/health"]}' | python3 -m json.tool

echo ""
echo "== probe him driver =="
sleep 2
call him://lenovo/mouse/query/status '{}' | python3 -m json.tool

echo ""
echo "Done. Install ydotool on lenovo manually: sudo apt install ydotool"
