#!/usr/bin/env bash
# Office doc + LinkedIn publish flow on lenovo node (mock or real browser open).
#
#   bash scripts/run-lenovo-office-linkedin.sh
#   LENOVO_PUBLISH_REAL=1 bash scripts/run-lenovo-office-linkedin.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LENOVO="${LENOVO:-http://192.168.188.201:8790}"
DEV_IP="${DEV_IP:-192.168.188.212}"
DEV_PORT="${DEV_PORT:-8765}"
REAL="${LENOVO_PUBLISH_REAL:-0}"
POST_TEXT="${LENOVO_LINKEDIN_TEXT:-Automated office note from urisys — $(date -Iseconds)}"

log() { echo "[lenovo-linkedin] $*"; }
fail() { log "FAIL: $*"; exit 1; }

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

serve_wheels() {
  mkdir -p /tmp/urisys-deploy
  for pkg in uribrowser urioffice urimail; do
    ver="$(python3 - <<PY
import tomllib, pathlib
p = pathlib.Path("${ROOT}/../${pkg}/pyproject.toml")
print(tomllib.loads(p.read_text())["project"]["version"])
PY
)"
    wheel="/tmp/urisys-deploy/${pkg}-${ver}-py3-none-any.whl"
    if [ ! -f "$wheel" ]; then
      log "building ${pkg} ${ver}"
      (cd "${ROOT}/../${pkg}" && python3 -m pip wheel -w /tmp/urisys-deploy . -q)
    fi
  done
  if ! pgrep -f "http.server ${DEV_PORT}.*${DEV_IP}" >/dev/null 2>&1; then
    python3 -m http.server "${DEV_PORT}" --bind "${DEV_IP}" --directory /tmp/urisys-deploy &
    sleep 1
  fi
}

install_pack() {
  local pack="$1" repo="$2"
  local ver wheel url body out
  ver="$(python3 - <<PY
import tomllib, pathlib
p = pathlib.Path("${ROOT}/../${repo}/pyproject.toml")
print(tomllib.loads(p.read_text())["project"]["version"])
PY
)"
  wheel="http://${DEV_IP}:${DEV_PORT}/${repo}-${ver}-py3-none-any.whl"
  log "install-pack ${pack} from ${wheel}"
  body="$(python3 - <<PY
import json
print(json.dumps({
    "uri": "node://local/command/install-pack",
    "payload": {"pack": "${pack}", "install": True, "force": True, "specs": ["uricore>=0.1.0", "${wheel}"]},
    "context": {"approved": True, "allow_real": True},
}))
PY
)"
  out="$(curl -sS -m 180 -X POST "${LENOVO}/uri/call" -H 'Content-Type: application/json' -d "$body")"
  echo "$out" | grep -q '"ok": true' || fail "install-pack ${pack}: $out"
}

curl -fsS -m 5 "${LENOVO}/health" >/dev/null || fail "lenovo node down at ${LENOVO}"

serve_wheels
install_pack browser uribrowser
install_pack office urioffice
install_pack mail urimail

ROUTES="$(curl -fsS "${LENOVO}/uri/routes")"
echo "$ROUTES" | grep -q 'browser://' || fail "browser routes missing"
echo "$ROUTES" | grep -q 'social/command/publish-post' || fail "browser publish-post route missing"

DOC="$(uri_call "urioffice://lenovo/document/command/create" "{\"title\":\"LinkedIn source\",\"body\":\"${POST_TEXT}\"}" '{"approved":true,"dry_run":false,"allow_real":true}')"
echo "$DOC" | grep -q '"ok": true' || fail "office create: $DOC"
log "office doc: $(echo "$DOC" | python3 -c 'import json,sys; r=json.load(sys.stdin).get("result",{}); print(r.get("path") or r)' 2>/dev/null || echo ok)"

if [ "$REAL" = "1" ]; then
  CTX='{"approved":true,"dry_run":false,"allow_real":true}'
else
  CTX='{"approved":true,"dry_run":true,"allow_real":false}'
fi

BROWSER="$(uri_call "browser://linkedin/social/command/publish-post" "{\"platform\":\"linkedin\",\"text\":\"${POST_TEXT}\"}" "$CTX")"
echo "$BROWSER" | grep -q '"ok": true' || fail "browser publish: $BROWSER"
log "browser: $(echo "$BROWSER" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("result"))' 2>/dev/null)"

MAIL="$(uri_call "urimail://lenovo/message/command/publish-post" "{\"platform\":\"linkedin\",\"text\":\"${POST_TEXT}\",\"via\":\"browser\"}" "$CTX")"
echo "$MAIL" | grep -q '"ok": true' || fail "mail publish: $MAIL"
log "mail via browser: $(echo "$MAIL" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("result"))' 2>/dev/null)"

log "PASS lenovo office+linkedin (real=${REAL})"
