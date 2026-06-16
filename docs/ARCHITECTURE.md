# Architektura urisys

`urisys` to monorepo **URI control plane**: centralny CLI/controller (`src/urisys/`) plus zestaw **samodzielnych obrazów Docker** (`*-docker/`), które wystawiają ten sam kontrakt HTTP:

```text
POST /uri/call   { "uri": "...", "payload": {...}, "context": {...} }
GET  /health
GET  /uri/routes
```

Mapa modułów (243 pliki, 581 funkcji): [`project/map.toon.yaml`](../project/map.toon.yaml).  
Katalog paczek i duplikatów: [`docs/PACKAGES.md`](PACKAGES.md), [`project/PACKAGES.md`](../project/PACKAGES.md).

## Warstwy

```text
┌─────────────────────────────────────────────────────────────┐
│  src/urisys/          CLI, managers, Markpact, FlowController│
│  (PackManager → uri_control.UriControlRuntime z uricore)     │
└───────────────────────────┬─────────────────────────────────┘
                            │ BridgeManager / HTTP
┌───────────────────────────▼─────────────────────────────────┐
│  *-docker/            Edge runtime + handlery per domena     │
│  urirdp / urikvm / uribrowser / urienv / uristepper / lab    │
└───────────────────────────┬─────────────────────────────────┘
                            │ *.uri.flow.yaml
┌───────────────────────────▼─────────────────────────────────┐
│  uri2flow → uri3        Graf workflow (depends_on, if:)       │
│  flow_runner (lab)      Uproszczony executor sekwencyjny      │
└─────────────────────────────────────────────────────────────┘
```

## Centralny runtime (`src/urisys/`)

| Komponent | Rola |
|-----------|------|
| `PackManager` | Ładuje paczki `uri*` z PyPI/path, `manifest.yaml`, Markpact |
| `MarkpactManager` | Walidacja/kompilacja/test jednoplikowych `*.markpact.md` |
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

Wspólna biblioteka: **`packages/python/urisysedge/`** (Route, Runtime, JSONL events, env policy).

Shimy kompatybilności:

- `urirdp-docker/packages/python/urirdpedge/` → import z `urisysedge`
- `urisys-automation-lab/packages/python/labedge/` → import z `urisysedge`

Każdy obraz Docker rejestruje własne schematy URI (`routes.py` + `handlers.py`):

| Obraz | Port | Schematy |
|-------|------|----------|
| `urirdp-docker` | 8795, 3389 | rdp, kvm, him, ocr, llm, shell, browser, env |
| `urikvm-docker` | 8796 | kvm, him, ocr, llm |
| `uribrowser-docker` | 8797 | browser |
| `urienv-docker` | 8798 | env |
| `uristepper-docker` | 8799 | stepper |
| `urisys-automation-lab` | 8099 | stt, chat, webrtc + forward do urirdp |
| `urisys-node` | 8790 | screen, node identity, routing slave |

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

## `project/` — analiza code2llm

Katalog generowany przez `code2llm ./ -f all`. Nie edytuj ręcznie `map.toon.yaml` — użyj [`project/MAP.md`](../project/MAP.md) jako przewodnika.

| Plik | Zastosowanie |
|------|--------------|
| `map.toon.yaml` | Mapa modułów M[], eksporty, alerty CC |
| `project/PACKAGES.md` | Duplikaty paczek i plan konsolidacji |
| `context.md` | Narracja dla LLM |
| `analysis.toon.yaml` | Hotspoty refactoringu |
