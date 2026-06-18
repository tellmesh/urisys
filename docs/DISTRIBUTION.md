# Dystrybucja capability packów (PyPI · Markpact · GitHub)

Trzy **równoległe ścieżki** dostarczania packów do `urisys-node`.

Powiązane: [`README.md`](README.md) · [`PACKAGES.md`](PACKAGES.md) · [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md) · [`MARKPACT.md`](MARKPACT.md) · [`NODE-SETUP.md`](NODE-SETUP.md).

## Trzy ścieżki

```text
                    ┌─────────────────┐
                    │  UriContract    │  markpact.com
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

| Ścieżka | Artefakt | Konsument |
|---------|----------|-----------|
| **A — PyPI / GitHub wheel** | wheel (`urikvm`, …) | `pip install`, `POST /uri/pack {"pack":"kvm"}` |
| **B — Markpact** | kontrakt + katalog | walidacja, rejestr release |
| **C — GitHub OCI** | obraz + `artifact-index.json` | `ArtifactResolver`, release hot-load |

## Canonical source: tellmesh sibling repos

Po migracji (2026-06-17) kod packów **nie jest vendored** w `urisys/` — każdy pack ma repo:

```text
tellmesh/uricore/     tellmesh/urirouter/   tellmesh/urioperators/
tellmesh/urikvm/      tellmesh/urihim/      tellmesh/uriocr/      tellmesh/urillm/
tellmesh/urimail/     tellmesh/urioffice/   tellmesh/urivql/
tellmesh/urikvmedge/  tellmesh/urirdp/      tellmesh/urisys-node/
tellmesh/uribrowser/  tellmesh/urienv/      tellmesh/uristepper/
tellmesh/urisys-automation-lab/
```

Monorepo `urisys` trzyma: Dockerfile, config, flows, markpacts, testy integracyjne.

### Drift guard

```bash
cd urisys
python3 scripts/pack_sync.py check --all      # 32 packi
python3 -m pytest tests/test_vendored_sync.py tests/test_kvm_pack_pyprojects.py -q
bash scripts/sync-vendored-pack.sh --check --all
```

Promote (sync + usuń vendored — już wykonane):

```bash
python3 scripts/pack_sync.py promote --all
```

### Dev workspace

```bash
# lokalnie: checkout tellmesh z sibling repos
cd tellmesh/urisys && uv sync --extra kvm

# CI / świeży clone bez siblingów:
bash scripts/ci-checkout-siblings.sh
bash scripts/ci-install-siblings.sh
pip install -e .
```

`[tool.uv.sources]` w `pyproject.toml` wskazuje `../{pack}`.

## Stan publikacji

| Pakiet | PyPI | GitHub Releases | Canonical |
|--------|------|-----------------|-----------|
| `urisys` | 🔲 0.1.35 | — | `tellmesh/urisys` |
| `urisys-node` | 🔲 | — | `tellmesh/urisys-node` |
| `uricore` | 🔲 0.1.9 | ✅ v0.1.8+ | `tellmesh/uricore` (`uri_control.edge`) |
| `urirouter` | 🔲 0.1.0 | ✅ v0.1.0 | `tellmesh/urirouter` |
| `urisysedge` | ✅ 0.1.1 (archived) | ✅ | **archived** → `uricore` |
| `urioperators` | 🔲 0.1.0 | 🔲 | `tellmesh/urioperators` |
| `urikvm` | ✅ 0.1.1 | ✅ | `tellmesh/urikvm` |
| `urihim`, `uriocr`, `urillm` | 🔲 | ✅ | `tellmesh/{pack}/` |
| `urimail`, `urioffice`, `urivql` | 🔲 | ✅ | `tellmesh/{pack}/` |
| `urikvmedge`, `urirdp` | 🔲 | 🔲 | bundle CLI repos |

> **Uricore:** PyPI `uricore` to **inny projekt**. Wheel `urisys` nie może mieć `uricore @ https://…` w metadanych (PyPI → HTTP 400). Po `pip install urisys` uruchom **`urisys init`** — instaluje tellmesh **urirouter** + **uricore** + urisys-node z GitHub Releases.

> **Urirouter:** [`tellmesh/urirouter`](https://github.com/tellmesh/urirouter) — wheel `v0.1.0` na GitHub Releases. Override: `URISYS_URIROUTER_WHEEL_URL`. Wymagany przed uricore (zależność resolvera).

**Build + walidacja przed upload:**

```bash
python -m build
bash scripts/validate-pypi-metadata.sh
PYPI_TOKEN=... twine upload dist/urisys-*
```

**Build lokalny (packi kvm):**

```bash
bash scripts/publish-pypi-packs.sh
PYPI_TOKEN=... bash scripts/publish-pypi-packs.sh
```

**GitHub Releases (packi kvm):**

```bash
bash scripts/publish-kvm-packs-github.sh
```

## Markpact (kontrakty kvm)

| Kontrakt | W urisys (glue) | `markpact-contracts/packs/` |
|----------|-----------------|----------------------------|
| `urikvm.contract` | `urikvm-docker/markpacts/` | ✅ |
| `urihim`, `uriocr`, `urillm.vision` | j.w. | ✅ |

Walidacja lokalna:

```bash
urisys markpact validate urikvm-docker/markpacts/urikvm.contract.markpact.md
```

## GitHub OCI (kvm bundle)

Workflow: [`.github/workflows/kvm-release.yml`](../.github/workflows/kvm-release.yml)  
Tag: **`urikvm-v*`** · opublikowany: **`urikvm-v0.1.5`**

**Build context:** root workspace tellmesh (sibling repos wymagane):

```bash
docker build -f urikvm-docker/Dockerfile /path/to/tellmesh
```

CI: `scripts/ci-checkout-siblings.sh` klonuje `tellmesh/{uricore,urirouter,urikvm,…}` obok `urisys/`.

| Deliverable | Wartość |
|-------------|---------|
| OCI | `ghcr.io/tellmesh/urikvm:0.1.5-linux-amd64` |
| Release assets | 4× artifact-index + 4× contract |
| Register markpact.com | best-effort (HTTP 422 bez portal publish) |

Node-side: `hotload_release_pack()`, `release_forwards` — [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md).

## Instalacja na node

```bash
pip install -U "urisys>=0.1.35"
urisys init
urisys node serve --host 0.0.0.0 --port 8790
```

Hot-load:

```bash
curl -X POST http://127.0.0.1:8790/uri/pack \
  -H 'Content-Type: application/json' \
  -d '{"pack":"kvm"}'
```

## Co zostało

| # | Zadanie |
|---|---------|
| 1 | Portal publish kvm kontraktów |
| 2 | PyPI: `urihim`, `uriocr`, `urillm`, `urioperators`, `urisys-node` |
| 3 | Reusable CI: `urirdp`, `uribrowser` bundle release |
| 4 | Tor R faza 2: OCR/HIM → `urioperators` |

## Pliki kluczowe

| Plik | Rola |
|------|------|
| `tellmesh/uricore/` | canonical edge runtime (`uri_control.edge`) |
| `tellmesh/urirouter/` | intent router + resolver policy |
| `tellmesh/urioperators/` | wspólne helpery LLM |
| `tellmesh/urisys-node/urisysnode/` | ArtifactResolver, hot-load, forward |
| `urisys/scripts/pack_sync.py` | drift guard, promote |
| `urisys/scripts/pack_registry.py` | pack → repo mapping |
| `urisys/scripts/ci-checkout-siblings.sh` | CI: clone tellmesh siblings |
| `urisys/.github/workflows/kvm-release.yml` | OCI + release assets |
