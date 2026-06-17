#!/usr/bin/env bash
# Upgrade lenovo slave via URI (no .sh on target). Run from dev machine on LAN.
#
#   bash scripts/deploy-lenovo-node.sh
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
if [ ! -f /tmp/urisys-deploy/urisys-0.1.27-py3-none-any.whl ]; then
  (cd "$ROOT" && python3 -m build -o /tmp/urisys-deploy 2>/dev/null || python3 -m pip wheel -w /tmp/urisys-deploy . -q)
fi
if [ ! -f /tmp/urisys-deploy/urihim-0.1.5-py3-none-any.whl ]; then
  (cd "$ROOT/urikvm-docker/packages/python/urihim" && python3 -m pip wheel -w /tmp/urisys-deploy . -q)
fi
if [ ! -f /tmp/urisys-deploy/urillm-0.1.1-py3-none-any.whl ]; then
  (cd "$ROOT/urikvm-docker/packages/python/urillm" && python3 -m pip wheel -w /tmp/urisys-deploy . -q)
fi

echo ""
echo "== HTTP serve wheels on DEV (8765) =="
if ! pgrep -f "http.server 8765.*192.168.188.212" >/dev/null 2>&1; then
  python3 -m http.server 8765 --bind 192.168.188.212 --directory /tmp/urisys-deploy &
  sleep 1
fi

URISYS_WHL="$(ls -1 /tmp/urisys-deploy/urisys-*.whl 2>/dev/null | sort -V | tail -1)"
echo ""
echo "== pip install urisys on lenovo =="
call shell://pip "{\"args\":[\"install\",\"-U\",\"$DEV/$(basename "$URISYS_WHL")\"]}" | python3 -m json.tool

echo ""
echo "== install-pack urihim 0.1.5 =="
call node://local/command/install-pack "{\"pack\":\"him\",\"install\":true,\"force\":true,\"specs\":[\"urisysedge>=0.1.0\",\"$DEV/urihim-0.1.5-py3-none-any.whl\"]}" | python3 -m json.tool

echo ""
echo "== install-pack urillm 0.1.1 =="
call node://local/command/install-pack "{\"pack\":\"llm\",\"install\":true,\"force\":true,\"specs\":[\"urisysedge>=0.1.0\",\"$DEV/urillm-0.1.1-py3-none-any.whl\"]}" | python3 -m json.tool

echo ""
echo "== restart urisys-node =="
call shell://bash '{"args":["-lc","pkill -f \"urisys-node serve\" || true; sleep 2; nohup /home/tom/venv/bin/urisys-node serve --host 0.0.0.0 --port 8790 >> /tmp/urisys-node.log 2>&1 & sleep 2; curl -sS http://127.0.0.1:8790/health"]}' | python3 -m json.tool

echo ""
echo "== probe him driver + scroll route =="
sleep 2
call him://lenovo/mouse/query/status '{}' | python3 -m json.tool
curl -sS "$LENOVO/uri/routes" | grep -E 'scroll|text/query/plan' || true

echo ""
echo "Done. Wayland: sudo apt install ydotool && sudo systemctl enable --now ydotoold"
echo "Test: bash scripts/run-office-simulate-lenovo.sh"
