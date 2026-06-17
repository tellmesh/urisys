# Dystrybucja capability packów (PyPI · Markpact · GitHub)

Trzy **równoległe ścieżki** dostarczania packów kvm/him/ocr/llm (i rozszerzeń office) do `urisys-node`.

Powiązane: [`README.md`](README.md) · [`PACKAGES.md`](PACKAGES.md) · [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md) · [`MARKPACT.md`](MARKPACT.md) · [`NODE-SETUP.md`](NODE-SETUP.md).

## Trzy ścieżki

```text
                    ┌─────────────────┐
                    │  UriContract    │  markpact.com — schemat URI, wersja, metadata
                    │  (*.markpact.md)│
                    └────────┬────────┘
                             │
┌──────────────┐    ┌────────▼────────┐    ┌──────────────────┐
│ PyPI wheels  │    │ artifact-index  │    │ OCI / binarki    │
│ pip install  │    │ GitHub Release  │◄───│ ghcr.io / tag    │
└──────┬───────┘    └────────┬────────┘    └──────────────────┘
       │                     │
       ▼                     ▼
  load_pack_into_runtime   hotload_release_pack()
       │                     │
       └──────────┬──────────┘
                  ▼
           urisys-node serve :8790
```

| Ścieżka | Artefakt | Konsument | Wymaga |
|---------|----------|-----------|--------|
| **A — PyPI / GitHub wheel** | wheel (`urikvm`, `urihim`, …) | `pip install`, hot-load `POST /uri/pack {"pack":"kvm"}` | `urisysedge` |
| **B — Markpact** | kontrakt + wpis w katalogu | walidacja, rejestr release | plik `.markpact.md` |
| **C — GitHub OCI** | obraz + `artifact-index.json` | `ArtifactResolver`, release hot-load | kontrakt + build obrazu |

Ścieżki **B i C** są niezależne od PyPI. Łączą się na node: `artifact-index` wskazuje obraz, kontrakt podaje wzorce URI → `register_forward_pack()`.

## Stan publikacji (2026-06-17)

### Sync vendored ↔ tellmesh repos

```bash
cd urisys
python3 scripts/pack_sync.py check --all
python3 -m pytest tests/test_vendored_sync.py -q
bash scripts/sync-vendored-pack.sh --all   # monorepo → tellmesh/{pack}
```

Packi office: `tellmesh/urimail`, `urioffice`, `urivql` (GitHub Releases + lazy install na node).

### PyPI / wheels

| Pakiet | PyPI | GitHub Releases | Monorepo |
|--------|------|-----------------|----------|
| `urisys` | 🔲 0.1.33 (init, uricore wheel) | — | root `pyproject.toml` |
| `urisysedge` | ✅ 0.1.1 | ✅ v0.1.1 | `packages/python/urisysedge/` |
| `urikvm` | ✅ 0.1.1 | ✅ v0.1.1 | `urikvm-docker/packages/python/urikvm/` |
| `urihim` | 🔲 | ✅ v0.1.3+ | vendored; wheel `twine check` PASS |
| `uriocr` | 🔲 | ✅ v0.1.0 | vendored; wheel PASS |
| `urillm` | 🔲 | ✅ v0.1.0 | vendored; wheel PASS |
| `urioperators` | 🔲 0.1.0 | 🔲 | `packages/python/urioperators/` (shared LLM helpers) |
| `urimail` / `urioffice` / `urivql` | 🔲 | ✅ | vendored w `urikvm-docker/` |

> **Uricore:** PyPI pakiet `uricore` to **inny projekt** (moduł `uricore/`, nie `uri_control/`).
> `urisys>=0.1.33` instaluje tellmesh uricore z **GitHub wheel** (`v0.1.8`). Zobacz [`NODE-SETUP.md`](NODE-SETUP.md).

**Build lokalny (bez upload):**

```bash
bash scripts/publish-pypi-packs.sh          # dist/ w katalogach packów
PYPI_TOKEN=... bash scripts/publish-pypi-packs.sh
```

**GitHub Releases (działa bez PyPI):**

```bash
bash scripts/publish-kvm-packs-github.sh
# PACKS_OVERRIDE=urihim bash scripts/publish-kvm-packs-github.sh
```

Lazy install na node (`URISYS_PACK_SOURCE=auto`): him/ocr/llm z GitHub, reszta z PyPI.

### Markpact (kontrakty)

| Kontrakt | Lokalizacja | `markpact-contracts/packs/` |
|----------|-------------|----------------------------|
| `urikvm.contract` | `urikvm-docker/markpacts/` | ✅ |
| `urihim.contract` | j.w. | ✅ |
| `uriocr.contract` | j.w. | ✅ |
| `urillm.vision.contract` | j.w. | ✅ |

Walidacja: **11/11 PASS** w `markpact-contracts`. Portal publish (odblokowuje rejestrację release w CI):

```bash
cd ~/github/tellmesh/markpact-contracts
MARKPACT_TOKEN=... bash scripts/publish-all.sh
```

Lokalna walidacja bez portalu:

```bash
urisys markpact validate urikvm-docker/markpacts/urikvm.contract.markpact.md
```

### GitHub OCI + artifact-index (kvm bundle)

Workflow: [`.github/workflows/kvm-release.yml`](../.github/workflows/kvm-release.yml)  
Trigger: tag **`urikvm-v*`** (osobny namespace od `uristepper` `v*`).

**Opublikowany release:** `urikvm-v0.1.5` ✅

| Deliverable | Wartość |
|-------------|---------|
| OCI image | `ghcr.io/tellmesh/urikvm:0.1.5-linux-amd64` |
| Release assets | 4× `artifact-index-*.json` + 4× `contract-*.md` |
| Register markpact.com | best-effort (HTTP 422 dopóki kontrakt nie na portalu) |

Flow:

1. Tag `urikvm-v*` → walidacja 4 kontraktów → build+push obrazu `urikvm-docker` (port **8794**)
2. Upload **GitHub Release assets** (immutable URLs — bez commitów na `main`)
3. Matrix `register`: POST `/api/releases` na markpact.com (wymaga `MARKPACT_API_TOKEN` + kontrakt na portalu)

Node-side (zaimplementowane):

- `run_release()` honoruje `artifact.port` (8794)
- `hotload_release_pack()` wyciąga `{scheme, patterns}` z `contract_url` release'a
- `release_forwards` w config / `URISYS_NODE_RELEASE_FORWARDS` — auto-provisioning przy starcie node

Przykład release hot-load:

```bash
curl -X POST http://127.0.0.1:8790/uri/pack \
  -H 'Content-Type: application/json' \
  -d '{"contract":"urikvm.contract","version":"0.1.5","catalog":"https://markpact.com"}'
```

Wymaga: node sparowany (`require_paired`), opcjonalnie `URISYS_NODE_REQUIRE_SIGNATURE=1` + `URISYS_NODE_TRUSTED_KEYS`.

## Instalacja na node

### Bootstrap lenovo (zalecane)

```bash
python3.12 -m venv ~/venv && source ~/venv/bin/activate
pip install -U "urisys>=0.1.33"
urisys init
source ~/.config/urisys/node.env
urisys node serve --host 0.0.0.0 --port 8790
```

Szczegóły: [`NODE-SETUP.md`](NODE-SETUP.md).

### Hot-load lokalnego packa (PyPI / wheel)

```bash
curl -X POST http://127.0.0.1:8790/uri/pack \
  -H 'Content-Type: application/json' \
  -d '{"pack":"kvm"}'
```

### Worker OCI (forward, bez PyPI)

1. `ArtifactResolver` pobiera `artifact-index.json` z GitHub Release asset URL
2. Start workera (docker) → endpoint HTTP
3. `register_forward_pack(runtime, scheme, endpoint, patterns)`

Forward: `urisysnode/forward.py` → `remote_call()` do workera.

## Co zostało (priorytet)

| # | Zadanie | Blokuje |
|---|---------|---------|
| 1 | Portal publish kvm kontraktów (`MARKPACT_TOKEN`) | catalog register 422 |
| 2 | PyPI upload: `urihim`, `uriocr`, `urillm`, `urioperators` | `pip install` bez GitHub |
| 3 | Publikacja `urisys` 0.1.33 na PyPI | lenovo `pip install -U urisys` z init fix |
| 4 | Reusable CI workflow: `uribrowser`, `urirdp` bundle | — |
| 5 | Tor R faza 2: OCR/HIM → `urioperators` | dedup ~280L |
| 6 | Shared-container hot-load (1 obraz → 4 schematy bez 4× restart) | E2E multi-contract |
| 7 | `uriimgl` / `urivql` packi | Wayland pipeline |

## Pliki kluczowe

| Plik | Rola |
|------|------|
| `packages/python/urisysedge/` | canonical edge runtime |
| `packages/python/urioperators/` | wspólne helpery LLM (chat, plan, decide, JSON parse) |
| `urikvm-docker/packages/python/{urikvm,urihim,uriocr,urillm}/` | handlery + pyproject |
| `urisys-node/.../artifact_resolver.py` | resolve OCI, `run_release`, `contract_spec_from_release` |
| `urisys-node/.../release_verify.py` | gate podpisów release (ed25519) |
| `urisys-node/.../serve.py` | `load_pack_into_runtime`, `hotload_release_pack`, `register_forward_pack` |
| `urisys-node/.../forward_config.py` | `release_forwards` boot wiring |
| `scripts/publish-pypi-packs.sh` | build wheeli |
| `scripts/pack_sync.py` | drift guard vendored ↔ tellmesh repos |
| `.github/workflows/kvm-release.yml` | OCI + release assets + register |
