# urisys


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.79-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$15.70-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-36.3h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $15.6984 (111 commits)
- 👤 **Human dev:** ~$3628 (36.3h @ $100/h, 30min dedup)

Generated on 2026-06-18 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Centralny **URI control plane** dla TellMesh: CLI (`urisys`), managers, Markpact oraz monorepo obrazów Docker z edge runtime.

## Instalacja

```bash
pip install urisys
```

### Dev (checkout tellmesh)

Wymaga checkout **tellmesh workspace** — `urisys` obok sibling repos (`uriresolver/`, `uricore/`, `urisys-node/`, `urikvm/`, …).

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

Zależności runtime: **`uricore`** (tellmesh wheel z GitHub), **`uriresolver`** (resolve + transport delegate), paczki URI z **`uri-packs`** (dev group w `pyproject.toml`).

**Mapa wszystkich paczek (diagramy, linki):** [`docs/MESH.md`](docs/MESH.md).

Capability packi **kvm/him/ocr/llm** doinstalowują się **lazy przy pierwszym URI** — [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md).

```bash
# slave / lenovo
pip install -U urisys
urisys init
urisys node serve --host 0.0.0.0 --port 8790

# dev host → zdalny lenovo
urisys remote health --endpoint http://192.168.188.201:8790
urisys remote restart --endpoint http://192.168.188.201:8790
```

Dev monorepo (wszystkie packi od razu):

```bash
uv sync --extra kvm
```

Każdy capability pack ma własny `pyproject.toml` (samodzielnie publikowalny na PyPI;
zależy od `uricore`). Po publikacji: `pip install urikvm urihim uriocr urillm`.
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
| [`docs/ECOSYSTEM.md`](docs/ECOSYSTEM.md) | Model warstw TellMesh |
| [`docs/MESH.md`](docs/MESH.md) | **Mapa TellMesh** — paczki → urisys, diagramy Mermaid |
| [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md) | **Slave** — `urisys init`, lazy install, hot-load, systemd |
| [`docs/DISTRIBUTION.md`](docs/DISTRIBUTION.md) | **PyPI · Markpact · GitHub OCI** — packi, kvm-release |
| [`docs/PACKAGES.md`](docs/PACKAGES.md) | Layout tellmesh sibling repos, `urioperators` |
| [`docs/REPOS.md`](docs/REPOS.md) | GitHub tellmesh vs semcod, mapowanie paczek |
| [`docs/PACK-EXTENSIBILITY.md`](docs/PACK-EXTENSIBILITY.md) | Nowe schematy URI, forward, `release_forwards` |
| [`docs/OFFICE-AUTOMATION.md`](docs/OFFICE-AUTOMATION.md) | Automatyzacja biurowa — roadmap |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Warstwy, runtime, porty Docker |
| [`docs/PROCESS-ARCHITECTURE.md`](docs/PROCESS-ARCHITECTURE.md) | UriProcess: Markpact → resolver → marksync |
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
├── urisys/              pip package — CLI + managers + docker glue ★
├── uriresolver/           intent router (resolve + transport)
├── uricore/             uri_control + uri_control.edge
├── urioperators/        wspólne helpery LLM
├── urisys-node/         urisysnode (bundled); uriscreen/urishell via pip
├── urikvm/ urihim/ uriocr/ urillm/ urirdp/ urishell/ urienv/ …
├── urikvmedge/          CLI urisys-kvm
├── urirdpedge/          CLI urisys-rdp
├── urirdp-docker/       RDP + URI stack (:8795 / :3389)
└── urisys-automation-lab/  lab UI (:8099)
```

## Managers

- `PackManager` — paczki `uri*`, manifest.yaml, Markpact
- `MarkpactManager` — validate / compile / test `*.markpact.md`
- `RuntimeManager` — `uri_control.UriControlRuntime`
- `UriController` — call, explain, routes
- `FlowController` — sekwencyjne `*.uri.flow.yaml`
- `BridgeManager` — forward do zdalnego `/uri/call`

## Markpact

Thin pack Markpacts live in each capability repo: `{pack}/markpacts/{pack}.markpact.md`.

```bash
cd tellmesh/urisys
python3 scripts/generate_pack_markpacts.py --check   # CI drift guard
bash scripts/run-markpact-ci.sh                      # drift + validate + tests

cd tellmesh/urishell
export TELLMESH_ROOT=~/github/tellmesh
urisys markpact run markpacts/urishell.markpact.md --as flow --approve --dry-run

bash scripts/validate-all-markpacts.sh
bash examples/markpact/showcase-run-flow.sh          # uribrowser integration demo

# UriProcess: materialize + resolver per platform
export TELLMESH_ROOT=~/github/tellmesh
bash scripts/marksync-materialize.sh ../markpact-contracts/packs/desktop-automation-processes.markpact.md
```

Docs: [`docs/MARKPACT.md`](docs/MARKPACT.md) · [`docs/PROCESS-ARCHITECTURE.md`](docs/PROCESS-ARCHITECTURE.md) · layout: [`markpacts/README.md`](markpacts/README.md)

Pełna regresja (tellmesh workspace):

```bash
bash scripts/run-full-regression.sh
```

## Analiza projektu (code2llm)

```bash
code2llm ./ -f all -o ./project
# → project/map.toon.yaml, calls.mmd, context.md
```

## Ekosystem TellMesh

Orchestrator: **[urisys](https://github.com/tellmesh/urisys)** · Mapa: **[MESH.md](https://github.com/tellmesh/urisys/blob/main/docs/MESH.md)** · Model: **[ECOSYSTEM.md](https://github.com/tellmesh/urisys/blob/main/docs/ECOSYSTEM.md)**

| Pole | Wartość |
|------|---------|
| **Warstwa** | Orchestrator (centrum mesh) |
| **Moduł** | `urisys` |
| **Zależności** | `uricontrol`, `uriresolver` |
| **Rola** | CLI, Markpact, flow runner, PackManager, `urisys init` |

Runtime edge: **`uri_control.edge`** w pakiecie **`uricontrol`** (legacy PyPI `uricore` / `urisysedge` usunięty 2026-06).
Resolver intencji: **`uriresolver`** (`uri_resolver`) + transport w **`uritransport`**; policy gate: **`uriguard`** (`uri_guard`).

<!-- end-ecosystem -->

## License

Licensed under Apache-2.0.
