# Migracja krok 1 — uricore + markpacts

Wykonane w ramach konsolidacji `urisys/` → `tellmesh/*`.

## 1. Usunięcie `urienv-docker/vendor/uricore`

| Było | Jest |
|------|------|
| Kopia ~364 KB w repo | `pip install uricore>=0.1.2` w Docker/CI (lub `../uricore` editable) |
| Lokalny dev | `../uricore` (tellmesh workspace) via `scripts/paths.sh` |
| Fallback | PyPI `uricore` gdy sibling brak |

### Zmienione pliki

- `urienv-docker/Dockerfile` — `pip install uricore`, bez `COPY vendor/`
- `urirdp-docker/Dockerfile` — `pip install uricore`, bez `COPY urienv-docker/vendor/uricore`
- `urienv-docker/pyproject.toml` — pythonpath bez vendor
- `urienv-docker/scripts/local-test.sh`
- `local-lab/scripts/install-urisys.sh`
- `.github/workflows/markpact-release.yml`
- `.gitignore` — `urienv-docker/vendor/uricore/`
- **Usunięty katalog:** `urienv-docker/vendor/uricore/`

### Weryfikacja

```bash
cd urisys
source scripts/paths.sh
uricore_pythonpath   # → ../uricore/core/python w tellmesh workspace

pip install -e ../uricore   # lokalnie
bash urienv-docker/scripts/local-test.sh
```

## 2. Deduplikacja `markpacts/packs`

| Było | Jest |
|------|------|
| 6× identyczne pliki w `urisys/markpacts/packs/` | Canonical: `tellmesh/markpact-contracts/packs/` |
| | `markpacts/packs` → symlink (tellmesh workspace) |

### Zmienione pliki

- **Usunięte:** `markpacts/packs/*.markpact.md` (duplikaty)
- `markpacts/README.md` — dokumentacja źródeł
- `scripts/paths.sh` — `markpact_contracts_packs()`
- `scripts/validate-all-markpacts.sh` — skanuje contracts + markpacts w podprojektach
- `examples/04-markpact-browser-call/run.sh`, `docs/CLI.md`, `docs/MARKPACT.md`, `docs/EXAMPLES.md`

### Weryfikacja

```bash
bash scripts/validate-all-markpacts.sh
# powinno walidować ../markpact-contracts/packs/*.md + *-docker/markpacts/*.md
```

## Krok 2 (następny)

- `flow_runner.py` → zależność `uri2flow` + `uri3`
- `urikvmedge` / `uribrowseredge` → shim do `packages/python/urisysedge`
- `releases/` → poza working tree lub tylko w CI artifact

Zobacz [`docs/PACKAGES.md`](PACKAGES.md).
