#!/usr/bin/env bash
set -euo pipefail
cd /workspace

CONTRACT_FILE="${CONTRACT_FILE:-uristepper-docker/markpacts/uristepper.pack.markpact.md}"

python3 -m pip install --upgrade pip -q
bash local-lab/scripts/install-urisys.sh

echo "== validate =="
urisys markpact validate "$CONTRACT_FILE"

echo "== compile =="
urisys markpact compile "$CONTRACT_FILE"

echo "== routes =="
urisys markpact routes "$CONTRACT_FILE"

echo "== tests =="
urisys markpact test "$CONTRACT_FILE"

echo "PASS validate-markpact"
