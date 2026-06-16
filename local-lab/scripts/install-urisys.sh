#!/usr/bin/env bash
# Install uricore + urisys inside lab containers (uricore is a sibling repo).
set -euo pipefail

URICORE_PATH="${URICORE_PATH:-/workspace/urienv-docker/vendor/uricore}"
WORKSPACE="${WORKSPACE:-/workspace}"

python3 -m pip install --upgrade pip -q

if [ -d "$URICORE_PATH" ]; then
  pip install "$URICORE_PATH" -q
else
  echo "WARN: ${URICORE_PATH} not mounted — trying PyPI uricore" >&2
  pip install "uricore>=0.1.0" -q
fi

pip install -e "$WORKSPACE" -q
