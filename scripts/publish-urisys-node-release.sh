#!/usr/bin/env bash
# Build urisys-node wheel and create GitHub Release asset (PEP 427: urisys_node-*.whl).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NODE_ROOT="${TELLMESH_NODE_ROOT:-${ROOT}/urisys-node}"
VERSION="${1:-$(python3 -c "import tomllib; print(tomllib.load(open('${NODE_ROOT}/pyproject.toml','rb'))['project']['version'])")}"

cd "${NODE_ROOT}"
python3 -m pip install -q build
python3 -m build -w
WHEEL="dist/urisys_node-${VERSION}-py3-none-any.whl"
test -f "${WHEEL}" || { echo "missing ${WHEEL}" >&2; exit 1; }

echo "Built ${WHEEL}"
echo "Publish:"
echo "  gh release create v${VERSION} ${WHEEL} --repo tellmesh/urisys-node --title v${VERSION} --notes 'urisys-node ${VERSION}'"
echo "  # or upload to existing release:"
echo "  gh release upload v${VERSION} ${WHEEL} --repo tellmesh/urisys-node --clobber"
