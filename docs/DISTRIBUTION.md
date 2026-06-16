# Dystrybucja capability packów (PyPI · Markpact · GitHub)

Ten dokument opisuje **trzy równoległe ścieżki** dostarczania packów kvm/him/ocr/llm do `urisys-node`, stan publikacji oraz plan domknięcia.

Powiązane: [`PACKAGES.md`](PACKAGES.md) (layout monorepo), [`MARKPACT.md`](MARKPACT.md) (format kontraktu), [`../urisys-node/README.md`](../urisys-node/README.md) (instalacja node), [`MIGRATION-STEP3.md`](MIGRATION-STEP3.md) (dedup `urisysedge`).

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

## Stan publikacji (2026-06-16)

### PyPI

| Pakiet | PyPI | Repo tellmesh | W monorepo urisys |
|--------|------|---------------|-------------------|
| `urisysedge` | ✅ [0.1.1](https://pypi.org/project/urisysedge/) | `tellmesh/urisysedge` | `packages/python/urisysedge/` |
| `urikvm` | ✅ [0.1.1](https://pypi.org/project/urikvm/) | `tellmesh/urikvm` | `urikvm-docker/packages/python/urikvm/` |
| `urihim` | 🔲 | `tellmesh/urihim` | vendored |
| `uriocr` | 🔲 | `tellmesh/uriocr` | vendored |
| `urillm` | 🔲 | `tellmesh/urillm` | vendored |

**Monorepo jako fallback:** dopóki `urihim` / `uriocr` / `urillm` nie są na PyPI, kopię kanoniczną trzymamy w `urisys/` (vendored). `goal -a` w monorepo **nie wymaga** symlinków do sibling repo — symlinki do `../urisysedge` psuły walidację commita (`Is a directory`).

Publikacja brakujących packów PyPI:

```bash
cd ~/github/tellmesh/urihim && goal -a -y
cd ~/github/tellmesh/uriocr && goal -a -y
cd ~/github/tellmesh/urillm && goal -a -y
```

Zbiorczo (z katalogu tellmesh):

```bash
bash scripts/publish-kvm-packs-goal.sh
```

### Markpact (kontrakty)

| Kontrakt | Lokalizacja w urisys | W `markpact-contracts/packs/` |
|----------|----------------------|-------------------------------|
| `urikvm.contract` | `urikvm-docker/markpacts/urikvm.contract.markpact.md` | 🔲 |
| `urihim.contract` | `urikvm-docker/markpacts/urihim.contract.markpact.md` | 🔲 |
| `uriocr.contract` | `urikvm-docker/markpacts/uriocr.contract.markpact.md` | 🔲 |
| `urillm-vision` | `urikvm-docker/markpacts/urillm-vision.contract.markpact.md` | 🔲 |

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

Wzorcowy pipeline: [`.github/workflows/markpact-release.yml`](../.github/workflows/markpact-release.yml) (dziś skonfigurowany dla `uristepper`).

Docelowy flow dla kvm (równoległy do pisania kontraktów):

1. Tag `v*` → build obrazu `urikvm-docker` → push `ghcr.io/...`
2. Generacja `releases/{contract-id}/{version}/artifact-index.json` + `contract.markpact.md`
3. Rejestracja na markpact.com (`local-lab/scripts/06-register-release.sh` lub CI)

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

### Test zdalnego node (np. lenovo `192.168.1.2:8790`)

**URI / flow** (preferowane — bez `.sh` na slave):

```bash
curl -sS http://192.168.1.2:8790/health
urisys-node call "node://lenovo/query/identity" \
  --route-map urisys-node/docker/config/route-map.host.yaml --approve
urisys --packs node,screen flow urisys-node/flows/remote-probe.uri.flow.yaml --approve --allow-real
```

Dev/CI only: `URISYS_NODE_BASE=http://192.168.1.2:8790 bash scripts/remote-node-smoke.sh`

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

1. 🔲 PyPI: `urihim`, `uriocr`, `urillm` (`goal -a` w repo tellmesh)
2. 🔲 Kontrakty kvm w `markpact-contracts/packs/`
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
