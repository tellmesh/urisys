# Migracja krok 3 — deduplikacja runtime (JsonlEventStore, Runtime)

## Cel

Usunięcie 2 zduplikowanych klas wskazanych w `project/analysis.toon.yaml`:

- `JsonlEventStore` — fork w `urisys-node` i `uristepper-docker`
- `Runtime` — fork w `urisys-node` (identyczny z `urisysedge`)

## Zmiany

| Było | Jest |
|------|------|
| `urisys-node/.../runtime.py` (~165 L fork) | shim → `uri_control.edge.runtime` |
| `urisys-node/.../env.py` (lokalny loader `.env`) | shim → `uri_control.edge.env` |
| `uristepper-docker/.../JsonlEventStore` | import z `uri_control.edge.runtime` |
| `urisysedge.JsonlEventStore` bez `tail()` | `tail()` + domyślne metadane eventów w `append()` |

### Canonical (`packages/python/urisysedge/runtime.py`)

- `JsonlEventStore.tail(limit)` — używane przez `urisys-node` (`GET /events`) i stepper CLI
- `append()` ustawia `event_id` / `occurred_at_unix_ms` gdy brak (kompatybilność stepper)

### Docker

`uristepper-docker/Dockerfile` — build context = katalog `urisys/`; pakiet `uristepperedge` (nie nadpisuje `urisysedge`):

```dockerfile
COPY packages/python/urisysedge ./packages/python/urisysedge
COPY uristepper-docker/ .
# CMD: python -m uristepperedge serve ...
```

`docker-compose.yml` — `context: ..`, `dockerfile: uristepper-docker/Dockerfile`

## Weryfikacja

```bash
cd urisys

# node
PYTHONPATH=packages/python:urisys-node/packages/python pytest urisys-node/tests -q

# stepper
PYTHONPATH=packages/python:uristepper-docker/packages/python \
  python -m pytest uristepper-docker/tests/test_runtime.py -q

# lab E2E (regresja)
bash scripts/run-lab-e2e.sh
```

Po regeneracji mapy (`code2llm` / `project.sh`):

```bash
grep -E 'DUP|dups' project/analysis.toon.yaml
# oczekiwane: dups:0 lub brak ×DUP na runtime
```

### Monorepo (2026-06)

- **Jedna kopia kodu:** `packages/python/urisysedge/` (root `pyproject.toml` + `PYTHONPATH`)
- **`urisys-node/packages/python/urisysedge/`** — tylko README; przed standalone wheel: `bash scripts/sync-vendored-urisysedge.sh`
- Test: `urisys-node/tests/test_urisysedge_single_source.py`

## Krok 4 (planowany)

- `urioperators/` — wspólne handlery OCR/LLM/HIM (urikvm ↔ urirdp)
- `urienv-docker/.../urisysedge` — osobny runtime na `UriControlRuntime` (uricore); rename/doc
- `FlowController` — `after`/`depends_on` parity z uri2flow

Zobacz [`docs/PACKAGES.md`](PACKAGES.md).
