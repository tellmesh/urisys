# Architektura urisys

`urisys` to monorepo **URI control plane**: centralny CLI/controller (`src/urisys/`) plus zestaw **samodzielnych obrazów Docker** (`*-docker/`), które wystawiają ten sam kontrakt HTTP:

```text
POST /uri/call   { "uri": "...", "payload": {...}, "context": {...} }
GET  /health
GET  /uri/routes
```

Mapa modułów: [`project/map.toon.yaml`](../project/map.toon.yaml).  
Indeks dokumentacji: [`docs/README.md`](README.md).  
**Mapa mesh (paczki → urisys):** [`docs/MESH.md`](MESH.md).  
Katalog paczek: [`docs/PACKAGES.md`](PACKAGES.md), [`project/PACKAGES.md`](../project/PACKAGES.md).

## Warstwy

Szczegółowy podział **proces / resolver / marksync**: [`docs/PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md).

```text
┌─────────────────────────────────────────────────────────────┐
│  src/urisys/          CLI, managers, Markpact, FlowController│
│  (PackManager → uri_control.UriControlRuntime z uricore)     │
└───────────────────────────┬─────────────────────────────────┘
                            │ BridgeManager / HTTP
┌───────────────────────────▼─────────────────────────────────┐
│  urirouter (uri_router)   resolve → transport delegate       │
│  uricore (uri_control)    registry, policy, local handlers   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  *-docker/            Edge runtime + handlery per domena     │
│  urirdp / urikvm / uribrowser / urienv / uristepper / lab    │
│  + resolver config (targets) — Etap 3 ✅                      │
│    uri_router + URISYS_RESOLVER_CONFIG                        │
└───────────────────────────┬─────────────────────────────────┘
                            │ *.uri.flow.yaml
┌───────────────────────────▼─────────────────────────────────┐
│  uri2flow → uri3        Graf workflow (depends_on, if:)       │
│  flow_runner (lab)      Uproszczony executor sekwencyjny      │
└─────────────────────────────────────────────────────────────┘

marksync (osobne repo) — sync Markpactów + plugin `urisys` → generated/{platform}/… (Etap 4 ✅)
urisys platform_export — materialize / export-platform → urisys.runtime.yaml, uri_routes.h
```

## Centralny runtime (`src/urisys/`)

| Komponent | Rola |
|-----------|------|
| `PackManager` | Ładuje paczki `uri*` z PyPI/path, `manifest.yaml`, Markpact |
| `MarkpactManager` | Walidacja/kompilacja/test jednoplikowych `*.markpact.md` |
| `platform_export` | `export_platform_artifacts` → `generated/{linux,server,esp32}/` (Etap 4) |
| `RuntimeManager` | Buduje `uri_control.UriControlRuntime` (uricore) |
| `UriController` | `call`, `explain`, `routes` |
| `FlowController` | Sekwencyjne wykonanie `do:` z pliku flow (bez `after`) |
| `ServerController` | HTTP `/uri/call`, `/uri/explain` |
| `BridgeManager` | Forward envelope do zdalnego URI servera |

```bash
urisys --packs browser call browser://default/page/open \
  --payload '{"url":"https://example.com"}' --approve

urisys --packs all flow flows/device-maintenance.uri.flow.yaml --approve --dry-run
urisys --packs all serve --port 8789
```

Szczegóły CLI: [`docs/CLI.md`](CLI.md), Markpact: [`docs/MARKPACT.md`](MARKPACT.md).

## Edge runtime (Docker)

Wspólne biblioteki:

- **`tellmesh/urisysedge/`** — `Runtime`, JSONL events, env policy, `http.serve`
- **`tellmesh/urioperators/`** — helpery LLM dla `urillm`

Edge CLIs (rejestrują standalone packi):

- **`tellmesh/urirdpedge/`** — `urisys-rdp` (:8795)
- **`tellmesh/urikvmedge/`** — `urisys-kvm` (:8794)
- **`tellmesh/uristepperedge/`** — `uristepper` (:8790)

Każdy obraz Docker instaluje sibling packi + edge CLI:

| Obraz | Port | Edge CLI | Schematy |
|-------|------|----------|----------|
| `urirdp-docker` | 8795, 3389 | `urisys-rdp` | rdp, kvm, him, ocr, llm, shell, browser, env |
| `urikvm-docker` | 8794 | `urisys-kvm` | kvm, him, ocr, llm |
| `uribrowser-docker` | 8792 / 8797 | `urisys-browser` | browser |
| `urienv-docker` | 8798 | env pack | env |
| `uristepper-docker` | 8791 | `uristepperedge` | stepper |
| `urisys-automation-lab` | 8099 | lab server | stt, webrtc, message + forward → urirdp |
| `urisys-node` | 8790 | `urisysnode` | screen, node, lazy packs |

Slave (`urisys-node`) ładuje packi **lazy** (PyPI/GitHub), **hot-load** (`POST /uri/pack`) lub **release hot-load** (`{contract,version,catalog}` → OCI worker). Auto-provisioning: `release_forwards` w config. Szczegóły: [`DISTRIBUTION.md`](DISTRIBUTION.md), [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md), [`NODE-SETUP.md`](NODE-SETUP.md).

### Pipeline Wayland (lenovo)

```text
screen://…/query/frame  →  vql://…/compare  →  imgl://…/execute  →  him://…/click
```

- **screen** — portal capture (GNOME Wayland); mss daje czarny ekran
- **vql** — weryfikacja UI ([oqlos/vql](https://github.com/oqlos/vql)); forward worker
- **imgl** — layout + ydotool ([semcod/imgl](https://github.com/semcod/imgl)); forward worker
- **him** — pyautogui na X11; na Wayland wymaga ydotool/imgl lub CDP/Playwright

Backends capture: [`urisys-node/docs/SCREEN_BACKENDS.md`](../urisys-node/docs/SCREEN_BACKENDS.md).

## URI flows

Compact format (`*.uri.flow.yaml`):

```yaml
flow:
  id: my-flow
defaults:
  approved: true
  dry_run: false
do:
  - shell://which:
      args: ["htop"]
  - id: screenshot
    uri: kvm://local/monitor/primary/query/screenshot
    after: which   # jawna zależność (flow 10 w lab)
```

Pipeline:

1. **uri2flow** — expand do `workflow_graph` (repo `tellmesh/uri2flow`)
2. **uri3** — walidacja, topo-sort, warunki `if:`, `step_outputs` (repo `tellmesh/uri3`)
3. **lab `flow_runner.py`** — topo-sort + sync `POST /uri/call`, endpoint `POST /uri/flow`

Szczegóły: [`docs/FLOWS.md`](FLOWS.md).

## Testy i sesje

```bash
python3 scripts/run_test_sessions.py --sessions lab-10-flows
python3 scripts/session_report.py analyze output/test-sessions/<run-id> --write-md
bash scripts/validate-all-markpacts.sh
bash scripts/run-markpact-ci.sh              # drift + validate + markpact tests
```

Artefakty sesji: `responses/*.json`, `screenshots/`, `report.json`, `events-*.jsonl`.

## local-lab (markpact.com chain)

`local-lab/` — Compose: builder → registry → urisys-node z `ArtifactResolver` i release API.

```bash
cd local-lab && bash scripts/run-all.sh
```

## Powiązane repozytoria

| Repo | Rola |
|------|------|
| `uricore` | `UriControlRuntime`, registry, policy, events |
| `uri-packs` | Produkcyjne paczki browser/docker/systemd/… |
| `uri2flow` | Compact flow → workflow_graph |
| `uri3` | Executor grafu |
| `markpact-contracts` | Packs publikowane na markpact.com |
| `markpact/marksync` | Sync Markpactów, pipeline deploy, export K8s/ESP32/… ([PROCESS-ARCHITECTURE.md](PROCESS-ARCHITECTURE.md)) |

## `project/` — analiza code2llm

Katalog generowany przez `code2llm ./ -f all`. Nie edytuj ręcznie `map.toon.yaml` — użyj [`project/MAP.md`](../project/MAP.md) jako przewodnika.

| Plik | Zastosowanie |
|------|--------------|
| `map.toon.yaml` | Mapa modułów M[], eksporty, alerty CC |
| `project/PACKAGES.md` | Duplikaty paczek i plan konsolidacji |
| `context.md` | Narracja dla LLM |
| `analysis.toon.yaml` | Hotspoty refactoringu |
