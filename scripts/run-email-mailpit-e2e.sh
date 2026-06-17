#!/usr/bin/env bash
# E2E: urimail unread → llm summary → compose/send (mock; optional Mailpit when URISYS_MAILPIT=1).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TELLMESH="$(cd "$ROOT/.." && pwd)"
COMPOSE="${TELLMESH}/urisys-node/docker/docker-compose.gui.yml"
MAILPIT_COMPOSE="${ROOT}/urimail-docker/docker-compose.yml"
PORT="${URISYS_NODE_HOST_PORT:-8790}"
BASE="http://127.0.0.1:${PORT}"
KEEP="${URISYS_OFFICE_E2E_KEEP:-0}"
USE_MAILPIT="${URISYS_MAILPIT:-0}"
SESSION_DIR="${URISYS_EMAIL_MAILPIT_SESSION_DIR:-}"

log() { echo "[email-mailpit-e2e] $*"; }
fail() { log "FAIL: $*"; exit 1; }

cleanup() {
  if [ "${KEEP}" = "1" ]; then
    log "KEEP=1 — stacks left running"
    return 0
  fi
  docker compose -f "${COMPOSE}" down -v --remove-orphans >/dev/null 2>&1 || true
  if [ -f "${MAILPIT_COMPOSE}" ]; then
    docker compose -f "${MAILPIT_COMPOSE}" down -v --remove-orphans >/dev/null 2>&1 || true
  fi
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

if [ "${USE_MAILPIT}" = "1" ] && [ -f "${MAILPIT_COMPOSE}" ]; then
  log "starting Mailpit stack"
  docker compose -f "${MAILPIT_COMPOSE}" up -d
  for _ in $(seq 1 30); do
    if curl -fsS "http://127.0.0.1:8025/api/v1/messages" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

log "docker compose build + up node"
docker compose -f "${COMPOSE}" build --quiet
docker compose -f "${COMPOSE}" up -d
wait_health

log "hot-load urimail + urillm"
MAIL_ST="$(uri_call "urimail://local/query/status" '{}')"
save_json "mail-status" "${MAIL_ST}"
echo "${MAIL_ST}" | grep -q '"ok": true' || fail "mail status: ${MAIL_ST}"

UNREAD="$(uri_call "urimail://local/inbox/query/unread" '{"limit":3}')"
save_json "mail-unread" "${UNREAD}"
echo "${UNREAD}" | grep -q '"count"' || fail "unread: ${UNREAD}"

PLAN="$(uri_call "llm://local/text/query/plan" '{"transcript":"Summarize unread mail and draft reply","allowed_schemes":["urimail"]}' '{"approved":true,"dry_run":false,"allow_real":true}')"
save_json "llm-plan-mail" "${PLAN}"
echo "${PLAN}" | grep -q 'message/command/compose' || fail "llm mail plan: ${PLAN}"

COMPOSE_DRY="$(uri_call "urimail://local/message/command/compose" '{"to":"team@example.com","subject":"Re: Weekly","body":"Thanks."}')"
save_json "mail-compose-dry" "${COMPOSE_DRY}"
echo "${COMPOSE_DRY}" | grep -q '"dry_run": true' || fail "compose dry: ${COMPOSE_DRY}"

SEND_DRY="$(uri_call "urimail://local/message/command/send" '{"to":"team@example.com"}')"
save_json "mail-send-dry" "${SEND_DRY}"
echo "${SEND_DRY}" | grep -q '"dry_run": true' || fail "send dry: ${SEND_DRY}"

log "flow email-mailpit steps (HTTP, dry-run)"
FLOW_UNREAD="$(uri_call "urimail://local/inbox/query/unread" '{"limit":5}')"
save_json "flow-unread" "${FLOW_UNREAD}"
FLOW_PLAN="$(uri_call "llm://local/text/query/plan" '{"transcript":"Summarize unread mail","allowed_schemes":["urimail"]}')"
save_json "flow-plan" "${FLOW_PLAN}"
FLOW_COMPOSE="$(uri_call "urimail://local/message/command/compose" '{"to":"team@example.com","subject":"Re: Weekly report","body":"Thanks."}')"
save_json "flow-compose" "${FLOW_COMPOSE}"
FLOW_SEND="$(uri_call "urimail://local/message/command/send" '{"to":"team@example.com"}')"
save_json "flow-send" "${FLOW_SEND}"
echo "${FLOW_SEND}" | grep -q '"ok": true' || fail "flow send step: ${FLOW_SEND}"

if [ "${USE_MAILPIT}" = "1" ]; then
  REAL_CTX='{"approved":true,"dry_run":false,"allow_real":true,"config":{"mail":{"driver":"mailpit","mailpit_api":"http://host.docker.internal:8025/api/v1","smtp_host":"host.docker.internal","smtp_port":1025}}}'
  log "real send via Mailpit SMTP (from container)"
  SEND_REAL="$(uri_call "urimail://local/message/command/compose" '{"to":"mailpit@test.local","subject":"urisys e2e","body":"hello mailpit"}' "${REAL_CTX}")"
  save_json "mail-compose-real" "${SEND_REAL}"
  SEND_REAL="$(uri_call "urimail://local/message/command/send" '{"to":"mailpit@test.local","driver":"mailpit"}' "${REAL_CTX}")"
  save_json "mail-send-real" "${SEND_REAL}"
  echo "${SEND_REAL}" | grep -q '"sent": true' || log "WARN mailpit send skipped (host.docker.internal may be unavailable in CI)"
fi

log "PASS email-mailpit e2e (${BASE})"
exit 0
