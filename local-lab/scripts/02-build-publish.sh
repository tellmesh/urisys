#!/usr/bin/env bash
set -euo pipefail
cd /workspace

# shellcheck source=../scripts/paths.sh
source "$(dirname "$0")/../../scripts/paths.sh"

CONTRACT_ID="${CONTRACT_ID:-uristepper-pack}"
VERSION="${VERSION:-0.1.0}"
CONTRACT_FILE="${CONTRACT_FILE:-uristepper-docker/markpacts/uristepper.pack.markpact.md}"
IMAGE_NAME="${IMAGE_NAME:-stepper-axis-control}"
IMAGE_TARGET="${IMAGE_TARGET:-linux-amd64-mock}"
OCI_REGISTRY_FOR_DOCKER="${OCI_REGISTRY_FOR_DOCKER:-localhost:5000}"
GHCR_REGISTRY="${GHCR_REGISTRY:-}"
GITHUB_OWNER="${GITHUB_OWNER:-tellmesh}"
GITHUB_REPO="${GITHUB_REPO:-urisys}"
GIT_REF="${GIT_REF:-main}"

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

echo "== Push image to OCI registry =="
docker push "$IMAGE_TAG"

IMAGE_DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE_TAG" 2>/dev/null || true)"
if [ -z "$IMAGE_DIGEST" ] || [ "$IMAGE_DIGEST" = "<no value>" ]; then
  IMAGE_REF="$IMAGE_TAG"
else
  IMAGE_REF="$IMAGE_DIGEST"
fi

if [ -n "$GHCR_REGISTRY" ]; then
  echo "== Push image to GHCR =="
  GHCR_TAG="${GHCR_REGISTRY}/${IMAGE_NAME}:${VERSION}-${IMAGE_TARGET}"
  docker tag "$IMAGE_TAG" "$GHCR_TAG"
  docker push "$GHCR_TAG"
  GHCR_DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "$GHCR_TAG" 2>/dev/null || true)"
  if [ -n "$GHCR_DIGEST" ] && [ "$GHCR_DIGEST" != "<no value>" ]; then
    IMAGE_REF="$GHCR_DIGEST"
    IMAGE_TAG="$GHCR_TAG"
  else
    IMAGE_REF="$GHCR_TAG"
    IMAGE_TAG="$GHCR_TAG"
  fi
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

RELEASE_DIR="$(releases_dir)/${CONTRACT_ID}/${VERSION}"
mkdir -p "$RELEASE_DIR"
cp local-lab/generated/artifact-index.json "${RELEASE_DIR}/artifact-index.json"
cp "$CONTRACT_FILE" "${RELEASE_DIR}/contract.markpact.md"

GITHUB_RAW_BASE="https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${GIT_REF}"
ARTIFACT_INDEX_GITHUB_URL="${GITHUB_RAW_BASE}/releases/${CONTRACT_ID}/${VERSION}/artifact-index.json"
CONTRACT_GITHUB_URL="${GITHUB_RAW_BASE}/releases/${CONTRACT_ID}/${VERSION}/contract.markpact.md"

python3 - <<PY
import json
from pathlib import Path

manifest = {
    "schema": "markpact.release-manifest.v1",
    "contract_id": "${CONTRACT_ID}",
    "version": "${VERSION}",
    "contract_digest": "${CONTRACT_SHA}",
    "contract_url": "${CONTRACT_GITHUB_URL}",
    "artifact_index_url": "${ARTIFACT_INDEX_GITHUB_URL}",
    "artifact_index_local_url": "http://127.0.0.1:8190/artifact-index.json",
    "oci_ref": "${IMAGE_REF}",
    "github": {
        "owner": "${GITHUB_OWNER}",
        "repo": "${GITHUB_REPO}",
        "ref": "${GIT_REF}",
    },
}
Path("local-lab/generated/release-manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(json.dumps(manifest, indent=2))
PY

echo "github_artifact_index=${ARTIFACT_INDEX_GITHUB_URL}"
echo "local_artifact_index=http://127.0.0.1:8190/artifact-index.json"
echo "PASS build-publish"
