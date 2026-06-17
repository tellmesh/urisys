# urisys


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.30-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$8.73-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-15.1h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $8.7298 (40 commits)
- 👤 **Human dev:** ~$1514 (15.1h @ $100/h, 30min dedup)

Generated on 2026-06-17 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

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

Capability packi **kvm/him/ocr/llm** doinstalowują się **lazy przy pierwszym URI** — [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md).

```bash
# slave / lenovo — tylko urisys, potem node
pip install urisys
urisys node serve --host 0.0.0.0 --port 8790
```

Dev monorepo (wszystkie packi od razu):

```bash
uv sync --extra kvm
```

Każdy capability pack ma własny `pyproject.toml` (samodzielnie publikowalny na PyPI;
zależy od `urisysedge`). Po publikacji: `pip install urikvm urihim uriocr urillm`.
Na działającym node dogrywasz po połączeniu: `POST /uri/pack {"pack":"kvm"}` (wymaga
`URISYS_NODE_ALLOW_PACK_LOAD=1`). Szczegóły: [`docs/DISTRIBUTION.md`](docs/DISTRIBUTION.md).

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
| [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md) | **Slave bez `.sh`** — pip, lazy install, hot-load, systemd |
| [`docs/PACK-EXTENSIBILITY.md`](docs/PACK-EXTENSIBILITY.md) | **Nowe schematy URI** — `imgl://`, forward pack, lifecycle |
| [`docs/OFFICE-AUTOMATION.md`](docs/OFFICE-AUTOMATION.md) | **Automatyzacja biurowa** — browser, office, email, roadmap testów Docker |
| [`docs/DISTRIBUTION.md`](docs/DISTRIBUTION.md) | **PyPI · Markpact · GitHub** — packi kvm, publikacja |
| [`docs/PACKAGES.md`](docs/PACKAGES.md) | Layout monorepo, duplikaty, plan konsolidacji |
| [`docs/FLOWS.md`](docs/FLOWS.md) | URI flows, zależności, walidacja |
| [`docs/EXAMPLES.md`](docs/EXAMPLES.md) | Przykłady shell/frontend/Docker |
| [`docs/CLI.md`](docs/CLI.md) | Komendy CLI |
| [`docs/MARKPACT.md`](docs/MARKPACT.md) | Markpact validate/compile/test |
| [`docs/MIGRATION-STEP1.md`](docs/MIGRATION-STEP1.md) | Migracja krok 1 |
| [`docs/MIGRATION-STEP2.md`](docs/MIGRATION-STEP2.md) | Migracja krok 2 |
| [`docs/MIGRATION-STEP3.md`](docs/MIGRATION-STEP3.md) | Migracja krok 3 — dedup urisysedge |
| [`urisys-node/README.md`](urisys-node/README.md) | Slave node, kvm packs, hot-load, forward OCI |
| [`urisys-node/docs/SCREEN_BACKENDS.md`](urisys-node/docs/SCREEN_BACKENDS.md) | Wayland capture — portal, vdisplay, mss |
| [`urisys-node/docs/PAIRING.md`](urisys-node/docs/PAIRING.md) | Parowanie master ↔ slave |
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
