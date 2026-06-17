# urisys


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.56-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$8.98-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-22.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $8.9766 (73 commits)
- 👤 **Human dev:** ~$2196 (22.0h @ $100/h, 30min dedup)

Generated on 2026-06-17 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Centralny **URI control plane** dla TellMesh: CLI (`urisys`), managers, Markpact oraz monorepo obrazów Docker z edge runtime.

## Instalacja

```bash
pip install urisys
```

### Dev (checkout tellmesh)

Wymaga checkout **tellmesh workspace** — `urisys` obok sibling repos (`urisysedge/`, `urisys-node/`, `urikvm/`, …).

```bash
cd tellmesh/urisys

python3 -m venv .venv
source .venv/bin/activate

uv sync --extra kvm    # [tool.uv.sources] → ../{pack}
```

Po instalacji CLI:

```bash
urisys --help
which urisys   # → .venv/bin/urisys
```

Zależności runtime: **`uricore`** (tellmesh wheel z GitHub — **nie** PyPI `uricore`), paczki URI z **`uri-packs`** (dev group w `pyproject.toml`).

Capability packi **kvm/him/ocr/llm** doinstalowują się **lazy przy pierwszym URI** — [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md).

```bash
# slave / lenovo
pip install -U urisys
urisys init
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

**Indeks:** [`docs/README.md`](docs/README.md) — nawigacja, stan projektu, otwarte zadania.

| Dokument | Temat |
|----------|--------|
| [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md) | **Slave** — `urisys init`, lazy install, hot-load, systemd |
| [`docs/DISTRIBUTION.md`](docs/DISTRIBUTION.md) | **PyPI · Markpact · GitHub OCI** — packi, kvm-release |
| [`docs/PACKAGES.md`](docs/PACKAGES.md) | Layout tellmesh sibling repos, `urioperators` |
| [`docs/REPOS.md`](docs/REPOS.md) | GitHub tellmesh vs semcod, mapowanie paczek |
| [`docs/PACK-EXTENSIBILITY.md`](docs/PACK-EXTENSIBILITY.md) | Nowe schematy URI, forward, `release_forwards` |
| [`docs/OFFICE-AUTOMATION.md`](docs/OFFICE-AUTOMATION.md) | Automatyzacja biurowa — roadmap |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Warstwy, runtime, porty Docker |
| [`docs/FLOWS.md`](docs/FLOWS.md) | URI flows, uri2flow / uri3 |
| [`docs/CLI.md`](docs/CLI.md) | Komendy CLI |
| [`docs/MARKPACT.md`](docs/MARKPACT.md) | Markpact validate/compile/test |
| [`urisys-node/README.md`](urisys-node/README.md) | Slave node, kvm packs, hot-load, forward OCI |
| [`urisys-node/docs/SCREEN_BACKENDS.md`](urisys-node/docs/SCREEN_BACKENDS.md) | Wayland capture — portal, vdisplay, mss |
| [`urisys-node/docs/PAIRING.md`](urisys-node/docs/PAIRING.md) | Parowanie master ↔ slave |
| [`project/MAP.md`](project/MAP.md) | Przewodnik po `map.toon.yaml` (code2llm) |
| [`project/PACKAGES.md`](project/PACKAGES.md) | Indeks paczek sync z mapą |

## Struktura (po migracji packów)

```text
tellmesh/
├── urisys/              pip package — CLI + managers + docker glue
├── urisysedge/          wspólny edge runtime (canonical)
├── urioperators/        wspólne helpery LLM
├── urisys-node/         urisysnode, uriscreen, urishell
├── urikvm/ urihim/ uriocr/ urillm/ …   capability packs
├── urikvmedge/          CLI urisys-kvm
├── urirdp/              RDP desktop bundle
└── urisys-node/  integracja slave (testy, docker config)
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
