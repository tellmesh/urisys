#!/usr/bin/env bash
# E2E: host controls urisys-node inside Docker GUI container (:8790).
#
# Flow:
#   1. docker compose up (Xvfb + zenity + urisys-node serve)
#   2. host → GET /health, /uri/routes
#   3. host → urisys-node call via route-map (master → docker-slave)
#   4. host → screen capture + indicator on/off on remote node
#   5. verify urisys --help inside container
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TELLMESH="$(cd "$ROOT/.." && pwd)"
COMPOSE="${TELLMESH}/urisys-node/docker/docker-compose.gui.yml"
CFG="${TELLMESH}/urisys-node/docker/config"
PORT="${URISYS_NODE_HOST_PORT:-8790}"
BASE="http://127.0.0.1:${PORT}"
CONTAINER="${URISYS_NODE_CONTAINER:-urisys-node-gui}"
KEEP="${URISYS_NODE_E2E_KEEP:-0}"
SESSION_DIR="${URISYS_NODE_SESSION_DIR:-}"

save_json() {
  local name="$1" content="$2"
  if [ -n "${SESSION_DIR}" ]; then
    mkdir -p "${SESSION_DIR}/responses"
    printf '%s' "${content}" > "${SESSION_DIR}/responses/${name}.json"
  fi
}

log() { echo "[urisys-node-docker-e2e] $*"; }
fail() { log "FAIL: $*"; exit 1; }

cleanup() {
  if [ "${KEEP}" = "1" ]; then
    log "KEEP=1 — container left running at ${BASE}"
    return 0
  fi
  docker compose -f "${COMPOSE}" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

http_json() {
  local method="$1" url="$2" body="${3:-}"
  if [ -n "${body}" ]; then
    curl -fsS -X "${method}" "${url}" \
      -H 'Content-Type: application/json' \
      -d "${body}"
  else
    curl -fsS -X "${method}" "${url}"
  fi
}

remote_call() {
  local uri="$1" payload="${2:-{}}" ctx="${3:-{\"approved\":true}}"
  python3 - <<PY
import json, urllib.request, sys
body = json.dumps({
    "uri": ${uri@Q},
    "payload": json.loads(${payload@Q}),
    "context": json.loads(${ctx@Q}),
}).encode("utf-8")
req = urllib.request.Request(
    "${BASE}/uri/call",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as resp:
    sys.stdout.write(resp.read().decode("utf-8"))
PY
}

wait_health() {
  log "waiting for ${BASE}/health"
  for _ in $(seq 1 60); do
    if curl -fsS "${BASE}/health" 2>/dev/null | grep -q '"ok"'; then
      return 0
    fi
    sleep 2
  done
  fail "health timeout on ${BASE}"
}

log "docker compose build + up"
docker compose -f "${COMPOSE}" build --quiet
docker compose -f "${COMPOSE}" up -d
wait_health

log "container CLI smoke"
docker exec "${CONTAINER}" urisys --help >/dev/null || fail "urisys --help"
docker exec "${CONTAINER}" bash -lc 'urisys-node serve --help >/dev/null' || fail "urisys-node serve --help"

HEALTH="$(http_json GET "${BASE}/health")"
save_json "health" "${HEALTH}"
echo "${HEALTH}" | grep -q '"service": "urisys-node"' || fail "unexpected health: ${HEALTH}"
NODE_ID="$(python3 -c "import json,sys; print(json.load(sys.stdin)['node_id'])" <<<"${HEALTH}")"
log "remote health ok node_id=${NODE_ID}"

ROUTES="$(http_json GET "${BASE}/uri/routes")"
save_json "routes" "${ROUTES}"
echo "${ROUTES}" | grep -q 'screen://' || fail "screen routes missing"
echo "${ROUTES}" | grep -q 'node://' || fail "node routes missing"

log "host route-map call → node identity"
export PYTHONPATH="${TELLMESH}/urisys-node/packages/python:${ROOT}/src:${PYTHONPATH:-}"
IDENTITY="$(
  python3 -m urisysnode.cli call "node://${NODE_ID}/query/identity" \
    --route-map "${CFG}/route-map.host.yaml" \
    --nodes-registry "${CFG}/nodes.registry.host.json" \
    --approve 2>/dev/null || \
  urisys-node call "node://${NODE_ID}/query/identity" \
    --route-map "${CFG}/route-map.host.yaml" \
    --nodes-registry "${CFG}/nodes.registry.host.json" \
    --approve
)"
save_json "identity" "${IDENTITY}"
echo "${IDENTITY}" | grep -q '"node_id"' || fail "identity call failed: ${IDENTITY}"

log "host remote screen capture (mss on Xvfb)"
CAPTURE="$(
  urisys-node call "screen://${NODE_ID}/monitor/primary/command/capture" \
    --route-map "${CFG}/route-map.host.yaml" \
    --nodes-registry "${CFG}/nodes.registry.host.json" \
    --payload '{"monitor":1}' \
    --approve --allow-real 2>/dev/null || \
  python3 -m urisysnode.cli call "screen://${NODE_ID}/monitor/primary/command/capture" \
    --route-map "${CFG}/route-map.host.yaml" \
    --nodes-registry "${CFG}/nodes.registry.host.json" \
    --payload '{"monitor":1}' \
    --approve --allow-real
)"
save_json "screen-capture" "${CAPTURE}"
echo "${CAPTURE}" | grep -q '"ok": true' || fail "screen capture failed: ${CAPTURE}"
CAP_PATH="$(python3 -c "import json,sys; r=json.load(sys.stdin); print((r.get('result') or {}).get('path',''))" <<<"${CAPTURE}")"
[ -n "${CAP_PATH}" ] || fail "capture path empty"
CAP_SIZE="$(docker exec "${CONTAINER}" stat -c%s "${CAP_PATH}" 2>/dev/null || echo 0)"
[ "${CAP_SIZE}" -gt 500 ] || fail "capture too small (${CAP_SIZE} bytes): ${CAP_PATH}"
log "capture ok path=${CAP_PATH} size=${CAP_SIZE}"

log "host remote indicator on/off"
IND_ON="$(http_json POST "${BASE}/uri/call" '{"uri":"node://local/command/indicator-on","payload":{"message":"host e2e"},"context":{"approved":true}}')"
save_json "indicator-on" "${IND_ON}"
echo "${IND_ON}" | grep -q '"remote_control_active": true' || fail "indicator-on: ${IND_ON}"
IND_OFF="$(http_json POST "${BASE}/uri/call" '{"uri":"node://local/command/indicator-off","payload":{},"context":{"approved":true}}')"
save_json "indicator-off" "${IND_OFF}"
echo "${IND_OFF}" | grep -q '"remote_control_active": false' || fail "indicator-off: ${IND_OFF}"

EVENTS="$(http_json GET "${BASE}/events?limit=5")"
save_json "events" "${EVENTS}"
echo "${EVENTS}" | grep -q '"events"' || fail "events endpoint failed"
if [ -n "${SESSION_DIR}" ]; then
  SESSION_DIR="${SESSION_DIR}" python3 - <<'PY'
import json, os
from pathlib import Path
session = Path(os.environ["SESSION_DIR"])
data = json.loads((session / "responses" / "events.json").read_text(encoding="utf-8"))
lines = [json.dumps(ev, ensure_ascii=False) for ev in data.get("events") or [] if isinstance(ev, dict)]
(session / "events.jsonl").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
PY
fi

log "PASS host→docker urisys-node control (${BASE}, node=${NODE_ID})"
exit 0
