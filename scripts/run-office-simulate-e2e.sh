#!/usr/bin/env bash
# E2E: office simulation (HIM scroll/type/move + optional llm plan) on urisys-node Docker GUI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TELLMESH="$(cd "$ROOT/.." && pwd)"
COMPOSE="${TELLMESH}/urisys-node/docker/docker-compose.gui.yml"
PORT="${URISYS_NODE_HOST_PORT:-8790}"
BASE="http://127.0.0.1:${PORT}"
CONTAINER="${URISYS_NODE_CONTAINER:-urisys-node-gui}"
KEEP="${URISYS_OFFICE_E2E_KEEP:-0}"
SESSION_DIR="${URISYS_OFFICE_SESSION_DIR:-}"

log() { echo "[office-simulate-e2e] $*"; }
fail() { log "FAIL: $*"; exit 1; }

cleanup() {
  if [ "${KEEP}" = "1" ]; then
    log "KEEP=1 — container left running at ${BASE}"
    return 0
  fi
  docker compose -f "${COMPOSE}" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

uri_call() {
  local uri="$1" payload="${2:-\{\}}" ctx="${3:-}"
  URI="$uri" PAYLOAD="$payload" CTX="$ctx" BASE="$BASE" python3 - <<'PY'
import json, os, urllib.request, sys
payload_raw = os.environ.get("PAYLOAD") or "{}"
ctx_raw = os.environ.get("CTX") or ""
if not ctx_raw:
    context = {"approved": True, "dry_run": True, "allow_real": False}
else:
    context = json.loads(ctx_raw)
body = json.dumps({
    "uri": os.environ["URI"],
    "payload": json.loads(payload_raw),
    "context": context,
}).encode("utf-8")
req = urllib.request.Request(
    os.environ["BASE"].rstrip("/") + "/uri/call",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as resp:
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

save_json() {
  local name="$1" content="$2"
  if [ -n "${SESSION_DIR}" ]; then
    mkdir -p "${SESSION_DIR}/responses"
    printf '%s' "${content}" > "${SESSION_DIR}/responses/${name}.json"
  fi
}

log "docker compose build + up"
docker compose -f "${COMPOSE}" build --quiet
docker compose -f "${COMPOSE}" up -d
wait_health

ROUTES="$(curl -fsS "${BASE}/uri/routes")"
save_json "routes" "${ROUTES}"
echo "${ROUTES}" | grep -q 'him://' || fail "him routes missing"
echo "${ROUTES}" | grep -q 'mouse/command/scroll' || fail "him scroll route missing"

log "dry-run HIM move"
MOVE="$(uri_call "him://local/mouse/command/move" '{"x":120,"y":80}')"
save_json "him-move-dry" "${MOVE}"
echo "${MOVE}" | grep -q '"ok": true' || fail "move dry-run: ${MOVE}"
echo "${MOVE}" | grep -q '"dry_run": true' || fail "move not dry_run: ${MOVE}"

log "dry-run HIM type"
TYPE="$(uri_call "him://local/keyboard/command/type" '{"text":"z"}')"
save_json "him-type-dry" "${TYPE}"
echo "${TYPE}" | grep -q '"ok": true' || fail "type dry-run: ${TYPE}"

log "dry-run HIM scroll"
SCROLL="$(uri_call "him://local/mouse/command/scroll" '{"amount":-3}')"
save_json "him-scroll-dry" "${SCROLL}"
echo "${SCROLL}" | grep -q '"ok": true' || fail "scroll dry-run: ${SCROLL}"
echo "${SCROLL}" | grep -q '"amount": -3' || fail "scroll amount: ${SCROLL}"

log "real HIM tick inside Xvfb (allow_real)"
REAL_CTX='{"approved":true,"dry_run":false,"allow_real":true}'
REAL_MOVE="$(uri_call "him://local/mouse/command/move" '{"x":200,"y":150}' "${REAL_CTX}")"
save_json "him-move-real" "${REAL_MOVE}"
echo "${REAL_MOVE}" | grep -q '"ok": true' || fail "move real: ${REAL_MOVE}"

REAL_TYPE="$(uri_call "him://local/keyboard/command/type" '{"text":"x"}' "${REAL_CTX}")"
save_json "him-type-real" "${REAL_TYPE}"
echo "${REAL_TYPE}" | grep -q '"ok": true' || fail "type real: ${REAL_TYPE}"

REAL_SCROLL="$(uri_call "him://local/mouse/command/scroll" '{"amount":-2}' "${REAL_CTX}")"
save_json "him-scroll-real" "${REAL_SCROLL}"
echo "${REAL_SCROLL}" | grep -q '"ok": true' || fail "scroll real: ${REAL_SCROLL}"

log "llm plan (hot-load urillm on first call)"
PLAN="$(uri_call "llm://local/text/query/plan" '{"transcript":"scroll down slightly","allowed_schemes":["him"]}' '{"approved":true,"dry_run":false,"allow_real":true}')"
save_json "llm-plan-scroll" "${PLAN}"
echo "${PLAN}" | grep -q '"ok": true' || fail "llm plan: ${PLAN}"
echo "${PLAN}" | grep -q 'mouse/command/scroll' || fail "plan uri not scroll: ${PLAN}"

log "office-simulate-loop.py --once --dry-run"
export URISYS_URI_BASE="${BASE}"
LOOP_OUT="$(python3 "${ROOT}/scripts/office-simulate-loop.py" --once --dry-run 2>&1)" || fail "loop dry-run failed: ${LOOP_OUT}"
save_json "loop-dry-run-log" "${LOOP_OUT}"
echo "${LOOP_OUT}" | grep -q 'ok=True' || fail "loop missing ok=True: ${LOOP_OUT}"

log "office-simulate-loop.py --once --mode llm --dry-run"
LLM_LOOP="$(python3 "${ROOT}/scripts/office-simulate-loop.py" --once --mode llm --dry-run 2>&1)" || fail "llm loop failed: ${LLM_LOOP}"
save_json "loop-llm-dry-run-log" "${LLM_LOOP}"
echo "${LLM_LOOP}" | grep -q 'ok=True' || fail "llm loop missing ok=True: ${LLM_LOOP}"

log "PASS office-simulate e2e (${BASE})"
exit 0
