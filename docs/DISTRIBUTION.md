# Dystrybucja capability packów (PyPI · Markpact · GitHub)

Ten dokument opisuje **trzy równoległe ścieżki** dostarczania packów kvm/him/ocr/llm do `urisys-node`, stan publikacji oraz plan domknięcia.

Powiązane: [`PACKAGES.md`](PACKAGES.md) (layout monorepo), [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md) (nowe schematy URI), [`MARKPACT.md`](MARKPACT.md) (format kontraktu), [`../urisys-node/README.md`](../urisys-node/README.md) (instalacja node), [`MIGRATION-STEP3.md`](MIGRATION-STEP3.md) (dedup `urisysedge`).

## Trzy ścieżki (można robić równolegle)

```text
                    ┌─────────────────┐
                    │  UriContract    │  markpact.com — schemat URI, wersja, metadata
                    │  (*.markpact.md)│
                    └────────┬────────┘
                             │
┌──────────────┐    ┌────────▼────────┐    ┌──────────────────┐
│ PyPI wheels  │    │ artifact-index  │    │ OCI / binarki    │
│ pip install  │    │ GitHub releases/│◄───│ ghcr.io / tag v* │
└──────┬───────┘    └────────┬────────┘    └──────────────────┘
       │                     │
       ▼                     ▼
  load_pack_into_runtime   register_forward_pack()
       │                     │
       └──────────┬──────────┘
                  ▼
           urisys-node serve :8790
```

| Ścieżka | Artefakt | Konsument | Wymaga |
|---------|----------|-----------|--------|
| **A — PyPI** | wheel (`urikvm`, `urihim`, …) | `pip install`, hot-load `POST /uri/pack` | `urisysedge` na PyPI |
| **B — Markpact** | kontrakt + wpis w katalogu | walidacja, rejestr release | tylko plik `.markpact.md` |
| **C — GitHub** | obraz OCI + `artifact-index.json` | `ArtifactResolver` | kontrakt (do SHA) + build obrazu |

Ścieżki **B i C** są niezależne od PyPI. Łączą się dopiero przy resolve na node: `artifact-index` wskazuje obraz, kontrakt podaje wzorce URI → `register_forward_pack()`.

## Stan publikacji (2026-06-17)

### Sync vendored ↔ tellmesh repos (Faza 0+1)

```bash
cd urisys
# nowe repo (jednorazowo)
bash scripts/sync-vendored-pack.sh --init urimail urioffice urivql

# monorepo → tellmesh/{pack}
bash scripts/sync-vendored-pack.sh --all

# drift check (CI)
python3 scripts/pack_sync.py check --all
python3 -m pytest tests/test_vendored_sync.py -q
```

Packi office: `tellmesh/urimail`, `urioffice`, `urivql` (GitHub Releases + lazy install na node).

### PyPI

| Pakiet | PyPI | Repo tellmesh | W monorepo urisys |
|--------|------|---------------|-------------------|
| `urisys` | 🔲 0.1.25 (fix hot-load, forward) | `tellmesh/urisys` | root `pyproject.toml` |
| `urisysedge` | ✅ [0.1.1 PyPI](https://pypi.org/project/urisysedge/) / ✅ [GitHub v0.1.1](https://github.com/tellmesh/urisysedge/releases/tag/v0.1.1) | `tellmesh/urisysedge` | `packages/python/urisysedge/` |
| `urikvm` | ✅ [0.1.1 PyPI](https://pypi.org/project/urikvm/) / ✅ [GitHub v0.1.1](https://github.com/tellmesh/urikvm/releases/tag/v0.1.1) | `tellmesh/urikvm` | `urikvm-docker/packages/python/urikvm/` |
| `urihim` | 🔲 PyPI / ✅ [GitHub v0.1.3](https://github.com/tellmesh/urihim/releases/tag/v0.1.3) | `tellmesh/urihim` | vendored |
| `uriocr` | 🔲 PyPI / ✅ [GitHub v0.1.0](https://github.com/tellmesh/uriocr/releases/tag/v0.1.0) | `tellmesh/uriocr` | vendored |
| `urillm` | 🔲 PyPI / ✅ [GitHub v0.1.0](https://github.com/tellmesh/urillm/releases/tag/v0.1.0) | `tellmesh/urillm` | vendored |
| `urimail` | 🔲 PyPI / 🔲 GitHub | `tellmesh/urimail` | vendored |
| `urioffice` | 🔲 PyPI / 🔲 GitHub | `tellmesh/urioffice` | vendored |
| `urivql` | 🔲 PyPI / 🔲 GitHub | `tellmesh/urivql` | vendored |

**Monorepo jako fallback:** dopóki `urihim` / `uriocr` / `urillm` nie są na PyPI, kopię kanoniczną trzymamy w `urisys/` (vendored). Lazy install na node domyślnie pobiera wheel z **GitHub Releases** (`URISYS_PACK_SOURCE=auto`).

Publikacja PyPI (gdy rate limit minie):

```bash
cd ~/github/tellmesh/urihim && goal -a -y
cd ~/github/tellmesh/uriocr && goal -a -y
cd ~/github/tellmesh/urillm && goal -a -y
```

**GitHub Releases (alternatywa PyPI — działa teraz):**

```bash
bash scripts/publish-kvm-packs-github.sh
# pojedynczy pack: PACKS_OVERRIDE=urihim bash scripts/publish-kvm-packs-github.sh
```

Ręczna instalacja z release:

```bash
pip install https://github.com/tellmesh/urihim/releases/download/v0.1.3/urihim-0.1.3-py3-none-any.whl
```

Na node z lazy install — domyślnie `auto` (him/ocr/llm z GitHub, reszta z PyPI). Wymuszenie:

```text
URISYS_PACK_SOURCE=github   # wszystkie packi z GitHub Releases
URISYS_PACK_SOURCE=pypi     # tylko PyPI
```

Zbiorczo (z katalogu tellmesh):

```bash
bash scripts/publish-kvm-packs-goal.sh
```

### Markpact (kontrakty)

| Kontrakt | Lokalizacja w urisys | W `markpact-contracts/packs/` |
|----------|----------------------|-------------------------------|
| `urikvm.contract` | `urikvm-docker/markpacts/urikvm.contract.markpact.md` | ✅ skopiowany + w `manifest.json` |
| `urihim.contract` | `urikvm-docker/markpacts/urihim.contract.markpact.md` | ✅ skopiowany + w `manifest.json` |
| `uriocr.contract` | `urikvm-docker/markpacts/uriocr.contract.markpact.md` | ✅ skopiowany + w `manifest.json` |
| `urillm-vision` (`urillm.vision.contract`) | `urikvm-docker/markpacts/urillm-vision.contract.markpact.md` | ✅ skopiowany + w `manifest.json` |

Kontrakty skopiowane do `markpact-contracts/packs/` (delivery `oci-forward`); `scripts/validate-all.sh` → **11/11 PASS**. Portal publish (`publish-all.sh`) wymaga `MARKPACT_TOKEN` (poniżej).

Walidacja lokalna (bez publikacji portalu):

```bash
urisys markpact validate urikvm-docker/markpacts/urikvm.contract.markpact.md
urisys markpact test urikvm-docker/markpacts/urikvm.contract.markpact.md
```

Publikacja kontraktów do markpact.com (repo `markpact-contracts`):

```bash
cd ~/github/tellmesh/markpact-contracts
MARKPACT_TOKEN=... bash scripts/publish-all.sh
```

### GitHub (OCI + artifact-index)

Pipeline'y:
- [`.github/workflows/markpact-release.yml`](../.github/workflows/markpact-release.yml) — `uristepper` (tag `v*`).
- [`.github/workflows/kvm-release.yml`](../.github/workflows/kvm-release.yml) — **kvm bundle** (tag `urikvm-v*`): **build-once + matrix-register**. Jeden obraz `urikvm-docker` (port 8794) serwuje 4 schematy; job `build` buduje/pushuje obraz raz, generuje 4× `artifact-index.json` (+ `contract.markpact.md`) i commituje raz; job `register` (matrix po 4 kontraktach, bez git) POST-uje każdy release na markpact.com.

Flow kvm:

1. Tag `urikvm-v*` → walidacja 4 kontraktów → build obrazu `urikvm-docker` → push `ghcr.io/{owner}/urikvm:{ver}-linux-amd64`
2. Generacja `releases/{contract-id}/{version}/artifact-index.json` (`port: 8794`, `capabilities` per scheme) + `contract.markpact.md`
3. Rejestracja na markpact.com (job `register`, wymaga `MARKPACT_API_TOKEN`)

> Node-side: `artifact_resolver.run_release` honoruje `artifact.port` (kvm = 8794), a `hotload_release_pack` wyciąga scheme+patterns z `contract_url` release'a — więc payload rejestracji wystarcza do poprawnego wpięcia route'ów. Walidacja workflow wymaga **otagowania** (`git tag urikvm-v0.1.0 && git push --tags`) i sekretów (`MARKPACT_API_TOKEN`).

Chain local-lab (pełny E2E):

```bash
cd local-lab
bash scripts/01-validate-markpact.sh
bash scripts/02-build-publish.sh
# … → 06-register-release.sh
```

## Instalacja na node (dev / lenovo)

### Tylko screen (PyPI)

```bash
pip install "urisys-node[real]"
URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen urisys-node serve --port 8790
```

### Pełny kvm — slave bez skryptów `.sh`

Na lenovo **nie** używaj `bash scripts/*.sh`. Zobacz **[`NODE-SETUP.md`](NODE-SETUP.md)**.

**PyPI (copy-paste, bez monorepo):**

```text
pip install -U urisysedge urikvm "urisys-node[real]"
URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen,kvm,him urisys-node serve --host 0.0.0.0 --port 8790
```

**`shell://` flow (RDP / urirdp stack):**

```bash
urisys --packs shell flow urisys-node/flows/bootstrap-kvm-pypi.uri.flow.yaml --approve --allow-real
```

**Probe z mastera (URI):**

```bash
urisys --packs node,screen flow urisys-node/flows/remote-probe.uri.flow.yaml --approve --allow-real
# lub pojedynczo: urisys-node call "node://lenovo/query/health" --route-map ... --approve
```

### Dev monorepo (checkout tellmesh)

```bash
cd urisys
uv sync --extra kvm
```

Skrypt `scripts/install-kvm-packs-editable.sh` — **tylko dev/CI**, nie na slave.

### Po publikacji wszystkich packów PyPI

```bash
pip install "urisys-node[real,kvm]"
URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen,kvm,him urisys-node serve --port 8790
```

Hot-load po starcie:

```bash
curl -X POST http://127.0.0.1:8790/uri/pack \
  -H 'Content-Type: application/json' -d '{"pack":"kvm"}'
```

### Test zdalnego node (np. lenovo `192.168.188.201:8790`)

**URI / flow** (preferowane — bez `.sh` na slave):

```bash
curl -sS http://192.168.188.201:8790/health
urisys-node call "node://lenovo/query/identity" \
  --route-map urisys-node/docker/config/route-map.host.yaml --approve
urisys --packs node,screen flow urisys-node/flows/remote-probe.uri.flow.yaml --approve --allow-real
```

Dev/CI only: `URISYS_NODE_BASE=http://192.168.188.201:8790 bash scripts/remote-node-smoke.sh`

Szczegóły: [`NODE-SETUP.md`](NODE-SETUP.md).

### Worker OCI (bez PyPI)

Gdy capability działa w osobnym kontenerze:

1. `ArtifactResolver` pobiera `artifact-index.json` z GitHub (raw) lub lokalnie
2. Start workera (docker) → endpoint HTTP
3. `register_forward_pack(runtime, scheme, endpoint, patterns)` w `urisysnode/serve.py`

Forward handler: `urisysnode/forward.py` → `remote_call()` do workera.

## Równoległy podział pracy

| Track | Kto / co | Blokuje |
|-------|----------|---------|
| **1 — Kontrakty** | skopiować `urikvm-docker/markpacts/*` → `markpact-contracts/packs/`, validate, publish portal | nic |
| **2 — GitHub OCI** | rozszerzyć `markpact-release.yml` o matrix kvm | walidacja kontraktu (soft) |
| **3 — PyPI** | `goal -a` dla urihim/uriocr/urillm | tylko kolejność: po `urisysedge` |
| **4 — Node wiring** | auto `ArtifactResolver` → `register_forward_pack` przy starcie | track 2+3 do E2E |

## Co zostało (priorytet)

1. 🔲 PyPI: `urisys` 0.1.24 (fix `import_pack_module`), potem `urihim`, `uriocr`, `urillm` (`goal -a`)
2. 🔲 Packi rozszerzone: `uriimgl`, `urivql` — [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md)
3. 🔲 Kontrakty kvm w `markpact-contracts/packs/`
3. 🔲 CI: `markpact-release.yml` dla `urikvm-docker` (matrix lub osobne tagi)
4. 🔲 Spięcie `ArtifactResolver` + auto-forward przy starcie node
5. 🔲 Refactor CC>15 (REFACTOR[1] w `project/analysis.toon.yaml`)
6. 🔲 `urioperators/` — wspólne handlery OCR/LLM/HIM
7. 🔲 Deprecacja `chat://` → `llm://` (lab shim)

## Pliki kluczowe

| Plik | Rola |
|------|------|
| `packages/python/urisysedge/` | canonical edge runtime (bundled w wheel `urisys`) |
| `urikvm-docker/packages/python/{urikvm,urihim,uriocr,urillm}/` | handlery + pyproject (vendored) |
| `scripts/install-kvm-packs-editable.sh` | dev/CI editable — **slave: [`NODE-SETUP.md`](NODE-SETUP.md)** |
| `scripts/publish-pypi-packs.sh` | build wheeli w monorepo |
| `../scripts/publish-kvm-packs-goal.sh` | publish z repo tellmesh/* |
| `urisys-node/.../artifact_resolver.py` | resolve OCI z artifact-index |
| `urisys-node/.../serve.py` | `load_pack_into_runtime`, `register_forward_pack` |
| `tests/test_kvm_pack_pyprojects.py` | layout + uv.sources |
