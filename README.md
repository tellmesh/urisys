# urisys


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.31-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$3.96-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-9.8h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $3.9630 (21 commits)
- 👤 **Human dev:** ~$976 (9.8h @ $100/h, 30min dedup)

Generated on 2026-06-16 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Centralny **URI control plane** dla TellMesh: CLI (`urisys`), managers, Markpact oraz monorepo obrazów Docker z edge runtime.

## Instalacja

```bash
pip install urisys
```

### Dev (checkout tellmesh)

Wymaga checkout **tellmesh** (urisys obok `uricore/`, `uri-packs/`, opcjonalnie `nl2uri/`, `uri2flow/`).

```bash
cd tellmesh/urisys

# wirtualne środowisko (poprawna składnia — NIE komenda `venv`)
python3 -m venv .venv
source .venv/bin/activate

# zalecane: uv (lockfile)
uv sync

# alternatywa bez uv:
pip install -e ".[dev]"
pip install -e ../uricore          # sibling w tellmesh workspace
```

Po instalacji CLI:

```bash
urisys --help
which urisys   # → .venv/bin/urisys
```

Zależności runtime: **`uricore`** (PyPI `uricore>=0.1.2` lub editable `../uricore`), paczki URI z **`uri-packs`** (dev group w `pyproject.toml`).

## Szybki start

```bash
cd urisys && uv sync

# Pojedyncze URI (paczki z uri-packs)
urisys --packs browser call browser://default/page/open \
  --payload '{"url":"https://example.com"}' --approve

# Flow mock
urisys --packs all flow flows/device-maintenance.uri.flow.yaml --approve --dry-run

# HTTP server
urisys --packs all serve --port 8789
```

## Docker lab (10 automatyzacji + RDP)

```bash
cd urisys-automation-lab
bash scripts/docker-up.sh
bash scripts/docker-smoke.sh

# Pełny test E2E
python3 scripts/run_test_sessions.py --sessions lab-10-flows
# lub: bash scripts/run-lab-e2e.sh
```

## Dokumentacja

| Dokument | Temat |
|----------|--------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Jak działa urisys — warstwy, runtime, testy |
| [`docs/PACKAGES.md`](docs/PACKAGES.md) | Layout monorepo, duplikaty, plan konsolidacji |
| [`docs/FLOWS.md`](docs/FLOWS.md) | URI flows, zależności, walidacja |
| [`docs/EXAMPLES.md`](docs/EXAMPLES.md) | Przykłady shell/frontend/Docker |
| [`docs/CLI.md`](docs/CLI.md) | Komendy CLI |
| [`docs/MARKPACT.md`](docs/MARKPACT.md) | Markpact validate/compile/test |
| [`project/MAP.md`](project/MAP.md) | Przewodnik po `map.toon.yaml` (code2llm) |
| [`project/PACKAGES.md`](project/PACKAGES.md) | Indeks paczek sync z mapą |

## Struktura monorepo

```text
src/urisys/              pip package — CLI + managers
packages/python/urisysedge/   wspólny edge runtime (canonical)
urirdp-docker/           RDP + KVM/HIM/OCR/LLM/shell/browser
urisys-automation-lab/   10 flows, lab UI :8099
urisys-node/             slave node + ArtifactResolver
local-lab/               markpact.com release chain
flows/                   przykład flow dla CLI
examples/                shell + frontend
markpacts/packs/         Markpact do walidacji
scripts/                 test sessions, validate-all-markpacts
```

## Managers

- `PackManager` — paczki `uri*`, manifest.yaml, Markpact
- `MarkpactManager` — validate / compile / test `*.markpact.md`
- `RuntimeManager` — `uri_control.UriControlRuntime`
- `UriController` — call, explain, routes
- `FlowController` — sekwencyjne `*.uri.flow.yaml`
- `BridgeManager` — forward do zdalnego `/uri/call`

## Markpact

```bash
urisys markpact validate markpacts/packs/uribrowser.markpact.md
bash scripts/validate-all-markpacts.sh
```

## Analiza projektu (code2llm)

```bash
code2llm ./ -f all -o ./project
# → project/map.toon.yaml, calls.mmd, context.md
```

## License

Licensed under Apache-2.0.
