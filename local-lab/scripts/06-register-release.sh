#!/usr/bin/env bash
# Register a materialized release in markpact.com catalog (GitHub artifact-index URL).
set -euo pipefail
cd /workspace

MARKPACT_URL="${MARKPACT_URL:-http://127.0.0.1:8088}"
MARKPACT_TOKEN="${MARKPACT_TOKEN:-}"
CONTRACT_ID="${CONTRACT_ID:-uristepper-pack}"
VERSION="${VERSION:-0.1.0}"
GITHUB_OWNER="${GITHUB_OWNER:-tellmesh}"
GITHUB_REPO="${GITHUB_REPO:-urisys}"
GIT_REF="${GIT_REF:-main}"
CONTRACT_FILE="${CONTRACT_FILE:-uristepper-docker/markpacts/uristepper.pack.markpact.md}"

if [ -z "$MARKPACT_TOKEN" ]; then
  echo "SKIP register-release — set MARKPACT_TOKEN (API token from markpact.com dashboard)"
  exit 0
fi

if [ -f local-lab/generated/release-manifest.json ]; then
  INDEX_URL="$(python3 -c "import json; print(json.load(open('local-lab/generated/release-manifest.json'))['artifact_index_url'])")"
  CONTRACT_URL="$(python3 -c "import json; print(json.load(open('local-lab/generated/release-manifest.json'))['contract_url'])")"
  CONTRACT_SHA="$(python3 -c "import json; print(json.load(open('local-lab/generated/release-manifest.json'))['contract_digest'])")"
else
  CONTRACT_SHA="sha256:$(sha256sum "$CONTRACT_FILE" | awk '{print $1}')"
  INDEX_URL="https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${GIT_REF}/releases/${CONTRACT_ID}/${VERSION}/artifact-index.json"
  CONTRACT_URL="https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${GIT_REF}/releases/${CONTRACT_ID}/${VERSION}/contract.markpact.md"
fi

export MARKPACT_URL CONTRACT_ID VERSION CONTRACT_SHA INDEX_URL CONTRACT_URL MARKPACT_TOKEN

python3 - <<'PY'
import json
import os
import urllib.request

with open("local-lab/generated/artifact-index.json", encoding="utf-8") as fh:
    artifacts = json.load(fh).get("artifacts") or []

payload = {
    "contract_id": os.environ["CONTRACT_ID"],
    "version": os.environ["VERSION"],
    "contract_digest": os.environ["CONTRACT_SHA"],
    "contract_url": os.environ.get("CONTRACT_URL") or None,
    "artifact_index_url": os.environ["INDEX_URL"],
    "artifacts": artifacts,
}
body = json.dumps({k: v for k, v in payload.items() if v is not None}).encode()
req = urllib.request.Request(
    os.environ["MARKPACT_URL"].rstrip("/") + "/api/releases",
    data=body,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ["MARKPACT_TOKEN"],
    },
    method="POST",
)
with urllib.request.urlopen(req, timeout=30) as resp:
    print(resp.read().decode())
PY

echo "PASS register-release"
