#!/usr/bin/env bash
# E2E office simulation on lenovo slave (192.168.188.201:8790).
# Run from dev machine (192.168.188.212) on LAN.
#
#   bash scripts/run-office-simulate-lenovo.sh
#   LENOVO=http://192.168.188.201:8790 bash scripts/run-office-simulate-lenovo.sh
#   OFFICE_LENOVO_REAL=1 bash scripts/run-office-simulate-lenovo.sh   # real HIM (careful)
#   OFFICE_LENOVO_WAIT=180 bash scripts/run-office-simulate-lenovo.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LENOVO="${LENOVO:-http://192.168.188.201:8790}"
DEV_IP="${DEV_IP:-192.168.188.212}"
DEV_PORT="${DEV_PORT:-8765}"
WAIT_SEC="${OFFICE_LENOVO_WAIT:-120}"
REAL="${OFFICE_LENOVO_REAL:-0}"
SESSION_DIR="${OFFICE_LENOVO_SESSION_DIR:-}"

log() { echo "[office-lenovo] $*"; }
fail() { log "FAIL: $*"; exit 1; }

save_json() {
  local name="$1" content="$2"
  if [ -n "${SESSION_DIR}" ]; then
    mkdir -p "${SESSION_DIR}/responses"
    printf '%s' "${content}" > "${SESSION_DIR}/responses/${name}.json"
  fi
}

uri_call() {
  local uri="$1" payload="${2:-\{\}}" ctx="${3:-}"
  URI="$uri" PAYLOAD="$payload" CTX="$ctx" BASE="$LENOVO" python3 - <<'PY'
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
with urllib.request.urlopen(req, timeout=180) as resp:
    sys.stdout.write(resp.read().decode("utf-8"))
PY
}

wait_node() {
  log "waiting up to ${WAIT_SEC}s for ${LENOVO}/health"
  local i=0
  while [ "$i" -lt "$WAIT_SEC" ]; do
    if curl -fsS -m 5 "${LENOVO}/health" 2>/dev/null | grep -q '"ok"'; then
      log "node is up"
      return 0
    fi
    sleep 2
    i=$((i + 2))
  done
  fail "node unreachable at ${LENOVO}. On lenovo run: systemctl --user start urisys-node  OR  ~/venv/bin/urisys-node serve --host 0.0.0.0 --port 8790"
}

serve_wheels() {
  mkdir -p /tmp/urisys-deploy
  if [ ! -f /tmp/urisys-deploy/urihim-0.1.5-py3-none-any.whl ]; then
    log "building urihim 0.1.5 wheel"
    (cd "${ROOT}/../urihim" && python3 -m pip wheel -w /tmp/urisys-deploy . -q)
  fi
  if ! pgrep -f "http.server ${DEV_PORT}.*${DEV_IP}" >/dev/null 2>&1; then
    log "HTTP serve wheels on ${DEV_IP}:${DEV_PORT}"
    python3 -m http.server "${DEV_PORT}" --bind "${DEV_IP}" --directory /tmp/urisys-deploy &
    sleep 1
  fi
}

upgrade_him() {
  local wheel="http://${DEV_IP}:${DEV_PORT}/urihim-0.1.5-py3-none-any.whl"
  log "install-pack urihim from ${wheel}"
  local body
  body="$(python3 - <<PY
import json
print(json.dumps({
    "uri": "node://local/command/install-pack",
    "payload": {
        "pack": "him",
        "install": True,
        "force": True,
        "specs": ["uricore>=0.1.0", "${wheel}"],
    },
    "context": {"approved": True, "allow_real": True},
}))
PY
)"
  local out
  out="$(curl -sS -m 180 -X POST "${LENOVO}/uri/call" -H 'Content-Type: application/json' -d "$body")"
  save_json "install-him" "$out"
  echo "$out" | grep -q '"ok": true' || log "WARN install-pack: $(echo "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("error") or d)' 2>/dev/null || echo "$out")"
}

upgrade_llm() {
  # vendored urillm with text/query/plan — install from monorepo wheel if present
  if [ -f /tmp/urisys-deploy/urillm-0.1.1-py3-none-any.whl ]; then
    local wheel="http://${DEV_IP}:${DEV_PORT}/urillm-0.1.1-py3-none-any.whl"
  else
    log "building urillm 0.1.1 wheel"
    (cd "${ROOT}/../urillm" && python3 -m pip wheel -w /tmp/urisys-deploy . -q)
    local wheel="http://${DEV_IP}:${DEV_PORT}/urillm-0.1.1-py3-none-any.whl"
  fi
  log "install-pack llm from ${wheel}"
  local body
  body="$(python3 - <<PY
import json
print(json.dumps({
    "uri": "node://local/command/install-pack",
    "payload": {"pack": "llm", "install": True, "force": True, "specs": ["uricore>=0.1.0", "${wheel}"]},
    "context": {"approved": True},
}))
PY
)"
  local out
  out="$(curl -sS -m 180 -X POST "${LENOVO}/uri/call" -H 'Content-Type: application/json' -d "$body")"
  save_json "install-llm" "$out"
}

wait_node
serve_wheels
upgrade_him
upgrade_llm

HEALTH="$(curl -fsS "${LENOVO}/health")"
save_json "health" "${HEALTH}"
log "health: $(echo "$HEALTH" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("node_id"), d.get("version","?"))' 2>/dev/null || echo ok)"

ROUTES="$(curl -fsS "${LENOVO}/uri/routes")"
save_json "routes" "${ROUTES}"
echo "${ROUTES}" | grep -q 'mouse/command/scroll' || fail "him scroll route missing on lenovo (upgrade urihim 0.1.5)"
echo "${ROUTES}" | grep -q 'text/query/plan' || fail "llm plan route missing (upgrade urillm 0.1.1)"

STATUS="$(uri_call "him://lenovo/mouse/query/status" '{}')"
save_json "him-status" "${STATUS}"
log "him driver: $(echo "$STATUS" | python3 -c 'import json,sys; r=json.load(sys.stdin).get("result",{}); print(r.get("driver","?"))' 2>/dev/null)"

DRY_CTX='{"approved":true,"dry_run":true,"allow_real":false}'
for step in move type scroll; do
  case "$step" in
    move)   out="$(uri_call "him://lenovo/mouse/command/move" '{"x":300,"y":200}' "$DRY_CTX")" ;;
    type)   out="$(uri_call "him://lenovo/keyboard/command/type" '{"text":"a"}' "$DRY_CTX")" ;;
    scroll) out="$(uri_call "him://lenovo/mouse/command/scroll" '{"amount":-2}' "$DRY_CTX")" ;;
  esac
  save_json "him-${step}-dry" "$out"
  echo "$out" | grep -q '"ok": true' || fail "him ${step} dry-run: $out"
  log "PASS dry-run him ${step}"
done

PLAN="$(uri_call "llm://lenovo/text/query/plan" '{"transcript":"scroll down slightly","allowed_schemes":["him"]}' '{"approved":true,"dry_run":false,"allow_real":true}')"
save_json "llm-plan" "$PLAN"
echo "$PLAN" | grep -q '"ok": true' || fail "llm plan: $PLAN"
log "PASS llm plan"

export URISYS_URI_BASE="${LENOVO}"
LOOP="$(python3 "${ROOT}/scripts/office-simulate-loop.py" --once --dry-run 2>&1)" || fail "loop: $LOOP"
save_json "loop-dry" "$LOOP"
echo "$LOOP" | grep -q 'ok=True' || fail "loop dry-run: $LOOP"
log "PASS office-simulate-loop dry-run"

if [ "${REAL}" = "1" ]; then
  log "REAL tick (HIM will move/type/scroll on lenovo desktop)"
  REAL_LOOP="$(URISYS_ALLOW_REAL=1 python3 "${ROOT}/scripts/office-simulate-loop.py" --once --mode rules 2>&1)" || fail "real loop: $REAL_LOOP"
  save_json "loop-real" "$REAL_LOOP"
  echo "$REAL_LOOP" | grep -q 'ok=True' || fail "real loop: $REAL_LOOP"
  log "PASS real office tick on lenovo"
fi

log "PASS office-simulate lenovo (${LENOVO}, real=${REAL})"
exit 0
