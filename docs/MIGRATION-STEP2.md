# Migracja krok 2 — uri2flow/uri3, edge shims, releases

## 1. `flow_runner.py` → uri2flow + uri3

| Było | Jest |
|------|------|
| Własny parser YAML + topo-sort | `uri2flow.expand_flow()` |
| Własna pętla kroków | `uri3.graph.run_workflow_node()` + `LabCallAdapter` |
| Brak warunków `if:` | `uri3.graph.conditions.evaluate_condition` (via node runner) |

### Pliki

- `urisys-automation-lab/server/flow_runner.py` — orchestracja uri2flow + uri3
- `urisys-automation-lab/server/lab_uri_adapter.py` — adapter HTTP (`call_uri` z lab gateway)
- `urisys-automation-lab/Dockerfile` — `pip install uri2flow>=0.1.2`

### Weryfikacja lokalna

```bash
# z katalogu tellmesh/urisys (NIE cd urisys gdy już tam jesteś)
bash scripts/run-lab-e2e.sh
# PASS 12/12 (2026-06-16, session 20260616-200505)
```

API `POST /uri/flow` — bez zmian (ten sam kształt odpowiedzi: `ok`, `graph`, `steps[]`).

## 2. Shims `urikvmedge` / `uribrowseredge` → `urisysedge`

| Pakiet | Było | Jest |
|--------|------|------|
| `urikvmedge/runtime.py` | ~228 L fork | re-export z `urisysedge.runtime` |
| `urikvmedge/env.py` | ~116 L fork | re-export z `urisysedge.env` |
| `uribrowseredge/runtime.py` | ~222 L fork | re-export z `urisysedge.runtime` |

Docker build context = katalog `urisys/` (jak `urirdp-docker`):

```bash
docker build -f urikvm-docker/Dockerfile .
docker build -f uribrowser-docker/Dockerfile .
```

## 3. `releases/` poza working tree

| Było | Jest |
|------|------|
| `releases/uristepper-pack/...` w repo | `.gitignore`: `releases/*` (zostaje `.gitkeep`) |
| Lokalny build | `local-lab/generated/releases/<contract>/<ver>/` |
| CI tag `v*` | nadal commituje do `releases/` (`.github/workflows/markpact-release.yml`) |

```bash
source scripts/paths.sh
releases_dir   # → local-lab/generated/releases (lokalnie)
RELEASES_DIR=releases releases_dir   # → releases (CI)
```

## Krok 3 (zrobione)

- `labedge` / `urirdpedge` → shim do `urisysedge` ✅
- `urisys-node/runtime.py` + `env.py` → shim do `urisysedge` ✅
- `uristepper` `JsonlEventStore` → `urisysedge` ✅

Zobacz [`docs/MIGRATION-STEP3.md`](MIGRATION-STEP3.md).

## Krok 4 (planowany)

- `uri2flow`/`uri3` jako optional dependency w `pyproject.toml` (dev/lab group)
- Pełny `uri3 run-workflow` zamiast `run_workflow_node` loop (gdy schema root dostępny w kontenerze)

Zobacz [`docs/FLOWS.md`](FLOWS.md), [`docs/PACKAGES.md`](PACKAGES.md).
