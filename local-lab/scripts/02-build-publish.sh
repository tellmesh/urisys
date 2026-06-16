#!/usr/bin/env bash
set -euo pipefail
cd /workspace

CONTRACT_ID="${CONTRACT_ID:-uristepper.contract}"
VERSION="${VERSION:-0.1.0}"
CONTRACT_FILE="${CONTRACT_FILE:-uristepper-docker/markpacts/uristepper.pack.markpact.md}"
IMAGE_NAME="${IMAGE_NAME:-stepper-axis-control}"
IMAGE_TARGET="${IMAGE_TARGET:-linux-amd64-mock}"
OCI_REGISTRY_FOR_DOCKER="${OCI_REGISTRY_FOR_DOCKER:-localhost:5000}"
NEXUS_URL="${NEXUS_URL:-http://nexus:8081}"
NEXUS_RAW_CONTRACTS="${NEXUS_RAW_CONTRACTS:-markpact-contracts-release}"
NEXUS_RAW_ARTIFACTS="${NEXUS_RAW_ARTIFACTS:-markpact-artifacts-release}"
NEXUS_USER="${NEXUS_USER:-admin}"
NEXUS_PASSWORD="${NEXUS_PASSWORD:-admin123}"

mkdir -p local-lab/generated

bash local-lab/scripts/install-urisys.sh

echo "== Markpact validate/compile/test =="
urisys markpact validate "$CONTRACT_FILE"
urisys markpact compile "$CONTRACT_FILE"
urisys markpact test "$CONTRACT_FILE"

CONTRACT_SHA="sha256:$(sha256sum "$CONTRACT_FILE" | awk '{print $1}')"

IMAGE_TAG="${OCI_REGISTRY_FOR_DOCKER}/${IMAGE_NAME}:${VERSION}-${IMAGE_TARGET}"

echo "== Build image =="
docker build \
  -f uristepper-docker/Dockerfile \
  -t "$IMAGE_TAG" \
  uristepper-docker

echo "== Push image to local OCI registry =="
docker push "$IMAGE_TAG"

IMAGE_DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE_TAG" 2>/dev/null || true)"
if [ -z "$IMAGE_DIGEST" ] || [ "$IMAGE_DIGEST" = "<no value>" ]; then
  IMAGE_REF="$IMAGE_TAG"
else
  IMAGE_REF="$IMAGE_DIGEST"
fi

echo "== Generate artifact-index.json =="
python3 - <<PY
import json
from pathlib import Path

payload = {
    "schema": "markpact.artifact-index.v1",
    "contract": {
        "id": "${CONTRACT_ID}",
        "version": "${VERSION}",
        "digest": "${CONTRACT_SHA}",
        "file": "${CONTRACT_FILE}",
    },
    "artifacts": [
        {
            "target": "${IMAGE_TARGET}",
            "kind": "oci-image",
            "platform": "linux/amd64",
            "runtime": "docker",
            "capabilities": ["mock-stepper", "uri-process"],
            "ref": "${IMAGE_REF}",
            "tag": "${IMAGE_TAG}",
        }
    ],
}
Path("local-lab/generated/artifact-index.json").write_text(
    json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, indent=2))
PY

if curl -fsS -u "${NEXUS_USER}:${NEXUS_PASSWORD}" "${NEXUS_URL}/service/rest/v1/status" >/dev/null 2>&1; then
  echo "== Upload contract + artifact-index to Nexus Raw =="
  CONTRACT_PATH="contracts/uristepper/${VERSION}/contract.bundle.markpact.md"
  INDEX_PATH="releases/uristepper/${VERSION}/artifact-index.json"
  curl -fsS -u "${NEXUS_USER}:${NEXUS_PASSWORD}" \
    --upload-file "$CONTRACT_FILE" \
    "${NEXUS_URL}/repository/${NEXUS_RAW_CONTRACTS}/${CONTRACT_PATH}"
  curl -fsS -u "${NEXUS_USER}:${NEXUS_PASSWORD}" \
    --upload-file local-lab/generated/artifact-index.json \
    "${NEXUS_URL}/repository/${NEXUS_RAW_ARTIFACTS}/${INDEX_PATH}"
  echo "nexus_contract=${NEXUS_URL}/repository/${NEXUS_RAW_CONTRACTS}/${CONTRACT_PATH}"
  echo "nexus_index=${NEXUS_URL}/repository/${NEXUS_RAW_ARTIFACTS}/${INDEX_PATH}"
else
  echo "Nexus not reachable — skipped raw upload (OCI push OK)"
fi

echo "PASS build-publish"
