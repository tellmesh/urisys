#!/usr/bin/env bash
# E2E: urioffice writer render + export PDF on urisys-node Docker GUI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="${ROOT}/urisys-node/docker/docker-compose.gui.yml"
PORT="${URISYS_NODE_HOST_PORT:-8790}"
BASE="http://127.0.0.1:${PORT}"
KEEP="${URISYS_OFFICE_E2E_KEEP:-0}"
SESSION_DIR="${URISYS_OFFICE_WRITER_SESSION_DIR:-}"

log() { echo "[office-writer-e2e] $*"; }
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

log "hot-load urioffice + urillm"
STATUS="$(uri_call "urioffice://local/query/status" '{}')"
save_json "office-status" "${STATUS}"
echo "${STATUS}" | grep -q '"ok": true' || fail "office status: ${STATUS}"

PLAN="$(uri_call "llm://local/text/query/plan" '{"transcript":"Office writer paragraph about quarterly results","allowed_schemes":["urioffice"]}' '{"approved":true,"dry_run":false,"allow_real":true}')"
save_json "llm-plan-office" "${PLAN}"
echo "${PLAN}" | grep -q 'writer/command/render' || fail "llm office plan: ${PLAN}"

log "dry-run writer render + export-pdf"
RENDER="$(uri_call "urioffice://local/writer/command/render" '{"title":"q-results","text":"Quarterly results.","format":"txt"}')"
save_json "writer-render-dry" "${RENDER}"
echo "${RENDER}" | grep -q '"dry_run": true' || fail "render dry: ${RENDER}"

EXPORT_DRY="$(uri_call "urioffice://local/document/command/export-pdf" '{}')"
save_json "export-pdf-dry" "${EXPORT_DRY}"
echo "${EXPORT_DRY}" | grep -q '"dry_run": true' || fail "export dry: ${EXPORT_DRY}"

REAL_CTX='{"approved":true,"dry_run":false,"allow_real":true}'
log "real writer render + export-pdf"
RENDER_REAL="$(uri_call "urioffice://local/writer/command/render" '{"title":"q-results","text":"Quarterly results.","format":"txt"}' "${REAL_CTX}")"
save_json "writer-render-real" "${RENDER_REAL}"
echo "${RENDER_REAL}" | grep -q '"rendered": true' || fail "render real: ${RENDER_REAL}"

EXPORT_REAL="$(uri_call "urioffice://local/document/command/export-pdf" '{}' "${REAL_CTX}")"
save_json "export-pdf-real" "${EXPORT_REAL}"
echo "${EXPORT_REAL}" | grep -q '"exported": true' || fail "export real: ${EXPORT_REAL}"

log "flow office-writer steps (HTTP, dry-run)"
FLOW_PLAN="$(uri_call "llm://local/text/query/plan" '{"transcript":"Office writer paragraph","allowed_schemes":["urioffice"]}')"
save_json "flow-plan" "${FLOW_PLAN}"
FLOW_RENDER="$(uri_call "urioffice://local/writer/command/render" '{"title":"flow","text":"Flow body","format":"txt"}')"
save_json "flow-render" "${FLOW_RENDER}"
FLOW_EXPORT="$(uri_call "urioffice://local/document/command/export-pdf" '{}')"
save_json "flow-export" "${FLOW_EXPORT}"
echo "${FLOW_EXPORT}" | grep -q '"ok": true' || fail "flow export step: ${FLOW_EXPORT}"

log "PASS office-writer e2e (${BASE})"
exit 0
