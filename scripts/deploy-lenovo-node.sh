#!/usr/bin/env bash
# Upgrade lenovo slave via URI (no .sh on target). Run from dev machine on LAN.
#
#   bash scripts/deploy-lenovo-node.sh
#   LENOVO=http://192.168.188.201:8790 DEV=http://192.168.188.212:8765 bash scripts/deploy-lenovo-node.sh
set -euo pipefail

LENOVO="${LENOVO:-http://192.168.188.201:8790}"
DEV="${DEV:-http://192.168.188.212:8765}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TELLMESH="$(dirname "$ROOT")"
DEPLOY_DIR="${DEPLOY_DIR:-/tmp/urisys-deploy}"

pkg_version() {
  python3 -c "import tomllib; print(tomllib.load(open('$1/pyproject.toml','rb'))['project']['version'])"
}

wheel_name() {
  # PEP 427: hyphens in PyPI name → underscores in wheel filename
  local name="$1" ver="$2"
  local file="${name//-/_}-${ver}-py3-none-any.whl"
  echo "$file"
}

build_wheel() {
  local dir="$1"
  local name ver whl
  name="$(python3 -c "import tomllib; print(tomllib.load(open('$dir/pyproject.toml','rb'))['project']['name'])")"
  ver="$(pkg_version "$dir")"
  whl="$(wheel_name "$name" "$ver")"
  if [ -f "${DEPLOY_DIR}/${whl}" ]; then
    echo "skip build ${whl} (exists)"
    return 0
  fi
  echo "build ${name} ${ver} → ${whl}"
  rm -rf "${dir}/build" "${dir}/dist" "${dir}"/*.egg-info 2>/dev/null || true
  (cd "$dir" && python3 -m pip install -q build && python3 -m build -w -o "$DEPLOY_DIR")
}

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
if ! health | python3 -m json.tool; then
  echo "FAIL: lenovo node not reachable at $LENOVO" >&2
  echo "Start on lenovo: urisys node serve --host 0.0.0.0 --port 8790" >&2
  exit 1
fi

URISYS_VER="$(pkg_version "$ROOT")"
URIHIM_VER="$(pkg_version "$TELLMESH/urihim")"
URILLM_VER="$(pkg_version "$TELLMESH/urillm")"
URIBROWSER_VER="$(pkg_version "$TELLMESH/uribrowser")"
URISHELL_VER="$(pkg_version "$TELLMESH/urishell")"
URISCREEN_VER="$(pkg_version "$TELLMESH/uriscreen")"
NODE_VER="$(pkg_version "$TELLMESH/urisys-node")"

echo ""
echo "== build wheels (urisys ${URISYS_VER}, urisys-node ${NODE_VER}, urishell, uriscreen, urihim, urillm, uribrowser) =="
mkdir -p "$DEPLOY_DIR"
build_wheel "$ROOT"
build_wheel "$TELLMESH/urisys-node"
build_wheel "$TELLMESH/urishell"
build_wheel "$TELLMESH/uriscreen"
build_wheel "$TELLMESH/urihim"
build_wheel "$TELLMESH/urillm"
build_wheel "$TELLMESH/uribrowser"

URISYS_WHL="$(wheel_name urisys "$URISYS_VER")"
NODE_WHL="$(wheel_name urisys-node "$NODE_VER")"
URISHELL_WHL="$(wheel_name urishell "$URISHELL_VER")"
URISCREEN_WHL="$(wheel_name uriscreen "$URISCREEN_VER")"
URIHIM_WHL="$(wheel_name urihim "$URIHIM_VER")"
URILLM_WHL="$(wheel_name urillm "$URILLM_VER")"
URIBROWSER_WHL="$(wheel_name uribrowser "$URIBROWSER_VER")"

for whl in "$URISYS_WHL" "$NODE_WHL" "$URISHELL_WHL" "$URISCREEN_WHL" "$URIHIM_WHL" "$URILLM_WHL" "$URIBROWSER_WHL"; do
  test -f "${DEPLOY_DIR}/${whl}" || { echo "missing ${DEPLOY_DIR}/${whl}" >&2; exit 1; }
done

echo ""
echo "== HTTP serve wheels on DEV (${DEV#http://}) =="
DEV_HOST="${DEV#http://}"
DEV_HOST="${DEV_HOST%%:*}"
DEV_PORT="${DEV##*:}"
if ! pgrep -f "http.server ${DEV_PORT}.*${DEV_HOST}" >/dev/null 2>&1; then
  python3 -m http.server "$DEV_PORT" --bind "$DEV_HOST" --directory "$DEPLOY_DIR" &
  sleep 1
fi

echo ""
echo "== pip install urisys-node deps + wheels on lenovo =="
call shell://pip "{\"args\":[\"install\",\"-U\",\"--no-deps\",\"$DEV/$URISHELL_WHL\",\"$DEV/$URISCREEN_WHL\"]}" | python3 -m json.tool
call shell://pip "{\"args\":[\"install\",\"-U\",\"--no-deps\",\"$DEV/$NODE_WHL\"]}" | python3 -m json.tool
call shell://pip "{\"args\":[\"install\",\"-U\",\"uricontrol>=0.1.8\",\"$DEV/$URISYS_WHL\"]}" | python3 -m json.tool

echo ""
echo "== schedule urisys node restart (venv; delayed so this URI returns first) =="
call shell://bash '{"args":["-lc","( sleep 1; pkill -f \"urisys node serve\" || pkill -f \"urisys-node serve\" || true; sleep 2; source ~/venv/bin/activate && nohup urisys node serve --host 0.0.0.0 --port 8790 >> /tmp/urisys-node.log 2>&1 & ) & echo scheduled"]}' | python3 -m json.tool

echo ""
echo "== wait for node health =="
for i in $(seq 1 30); do
  if health | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("ok") else 1)' 2>/dev/null; then
    break
  fi
  sleep 2
done
health | python3 -m json.tool

echo ""
echo "== install-pack urihim ${URIHIM_VER} =="
call node://local/command/install-pack "{\"pack\":\"him\",\"install\":true,\"force\":true,\"specs\":[\"uricontrol>=0.1.8\",\"$DEV/$URIHIM_WHL\"]}" | python3 -m json.tool

echo ""
echo "== install-pack urillm ${URILLM_VER} =="
call node://local/command/install-pack "{\"pack\":\"llm\",\"install\":true,\"force\":true,\"specs\":[\"uricontrol>=0.1.8\",\"$DEV/$URILLM_WHL\"]}" | python3 -m json.tool

echo ""
echo "== install-pack uribrowser ${URIBROWSER_VER} =="
call node://local/command/install-pack "{\"pack\":\"browser\",\"install\":true,\"force\":true,\"specs\":[\"uricontrol>=0.1.8\",\"$DEV/$URIBROWSER_WHL\"]}" | python3 -m json.tool

echo ""
echo "== probe him driver + routes =="
sleep 2
call him://lenovo/mouse/query/status '{}' | python3 -m json.tool || true
curl -sS "$LENOVO/uri/routes" | grep -E 'scroll|text/query/plan|browser://|him://' || true

echo ""
echo "Done. Test: bash scripts/run-lenovo-office-linkedin.sh"
