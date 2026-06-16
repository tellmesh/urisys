#!/usr/bin/env bash
# Probe lenovo and install him/ocr/llm from GitHub Releases — saves session under output/test-sessions/.
#
# Usage:
#   bash scripts/lenovo-node-session.sh
#   LENOVO_BASE=http://192.168.188.201:8790 bash scripts/lenovo-node-session.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="${LENOVO_BASE:-http://192.168.188.201:8790}"
RUN_ID="${LENOVO_RUN_ID:-lenovo-$(date +%Y%m%d-%H%M%S)}"
SESSION_DIR="$ROOT/output/test-sessions/$RUN_ID/lenovo-probe"

mkdir -p "$SESSION_DIR/responses"

log() { echo "[lenovo-session] $*" | tee -a "$SESSION_DIR/session.log"; }
save() { local n="$1"; shift; printf '%s' "$*" > "$SESSION_DIR/responses/${n}.json"; }

log "target=$BASE session=$SESSION_DIR"

save "01-health" "$(curl -fsS -m 10 "$BASE/health")"
save "02-routes" "$(curl -fsS -m 10 "$BASE/uri/routes")"
save "03-packs" "$(curl -fsS -m 10 -X POST "$BASE/uri/call" -H 'Content-Type: application/json' \
  -d '{"uri":"node://local/query/packs","payload":{},"context":{}}')"

install_pack() {
  local pack="$1" repo="$2" ver="$3"
  local wheel="https://github.com/tellmesh/${repo}/releases/download/v${ver}/${repo}-${ver}-py3-none-any.whl"
  local body
  body="$(python3 - <<PY
import json
print(json.dumps({
    "uri": "node://local/command/install-pack",
    "payload": {
        "pack": "${pack}",
        "install": True,
        "specs": ["urisysedge>=0.1.0", "${wheel}"],
    },
    "context": {"approved": True},
}))
PY
)"
  local out
  out="$(curl -sS -m 180 -X POST "$BASE/uri/call" -H 'Content-Type: application/json' -d "$body")"
  save "install-${pack}" "$out"
  echo "$out" | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('result',d); print('${pack}:', 'loaded' if r.get('loaded') else 'FAIL', r.get('pip',{}).get('stderr','')[-120:])"
}

for entry in "him:urihim:0.1.2" "ocr:uriocr:0.1.0" "llm:urillm:0.1.0"; do
  IFS=: read -r pack repo ver <<< "$entry"
  install_pack "$pack" "$repo" "$ver" || true
done

save "04-routes-after" "$(curl -fsS -m 10 "$BASE/uri/routes")"
save "05-screen-capture" "$(curl -sS -m 60 -X POST "$BASE/uri/call" -H 'Content-Type: application/json' \
  -d '{"uri":"screen://local/monitor/primary/command/capture","payload":{"monitor":1},"context":{"approved":true,"allow_real":true}}')"

python3 - <<PY
import json, time
from pathlib import Path
meta = {
    "session_id": "${RUN_ID}",
    "session_name": "lenovo-probe",
    "suite": "remote-node",
    "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "target": "${BASE}",
}
Path("${SESSION_DIR}/meta.json").write_text(json.dumps(meta, indent=2) + "\n")
PY

python3 "$ROOT/scripts/session_report.py" generate "$SESSION_DIR" 2>/dev/null || true
log "done → $SESSION_DIR"
