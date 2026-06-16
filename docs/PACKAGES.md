# Paczki w monorepo urisys

Ten dokument opisuje **layout paczek**, **duplikaty** i **plan konsolidacji**.  
Indeks modułów z liczbami linii: [`project/map.toon.yaml`](../project/map.toon.yaml) (sekcja `M[]`).

## Legenda ról

| Typ | Opis | Przykład |
|-----|------|----------|
| **core** | Centralny controller | `src/urisys/` |
| **edge-shared** | Wspólny runtime Docker | `packages/python/urisysedge/` |
| **edge-shim** | Alias kompatybilności | `urirdpedge`, `labedge` |
| **edge-fork** | Kopia do konsolidacji | _(wszystkie edge → urisysedge)_ |
| **handlers** | Implementacja schematu URI | `urirdp_kvm`, `uriocr` |
| **lab-pack** | MVP mock/real w automation-lab | `uristt`, `urichat`, `uriwebrtc` |

## Drzewo katalogów (skrót)

```text
urisys/
├── src/urisys/                 # pip package urisys (CLI + managers)
├── packages/python/urisysedge/ # ★ wspólny edge runtime (NOWY)
├── flows/                      # przykładowy flow CLI
├── examples/                   # shell + frontend
├── markpacts/                  # → ../markpact-contracts/packs (symlink w tellmesh)
├── scripts/                    # test sessions, validate
├── local-lab/                  # chain markpact.com
├── urirdp-docker/              # RDP + pełny desktop automation
├── urikvm-docker/              # KVM bez RDP
├── uribrowser-docker/          # tylko browser://
├── urienv-docker/              # env:// (uricore z PyPI / ../uricore)
├── uristepper-docker/          # stepper://
├── urisys-automation-lab/      # 10 flows + lab UI
└── urisys-node/                # slave/master node + ArtifactResolver
```

## Wspólny pakiet: `urisysedge`

**Wyodrębniony** (2026-06-16) z `urirdpedge`:

| Moduł | Zawartość |
|-------|-----------|
| `runtime.py` | `Route`, `Runtime`, `JsonlEventStore`, `run_flow`, HTTP handler |
| `env.py` | `load_env_policy`, `resolve_env_var`, `load_urisys_env` |

Shimy (tylko re-export):

- `urirdp-docker/packages/python/urirdpedge/{runtime,env}.py`
- `urisys-automation-lab/packages/python/labedge/runtime.py`
- `urikvm-docker/packages/python/urikvmedge/{runtime,env}.py`
- `uribrowser-docker/packages/python/uribrowseredge/runtime.py`
- `urisys-node/packages/python/urisysnode/{runtime,env}.py`

Stepper (osobny pakiet, współdzieli tylko `JsonlEventStore`):

- `uristepper-docker/packages/python/uristepperedge/` — `StepperRuntime`, nie duplikuje `Runtime`

Docker COPY (build context = katalog `urisys/`):

```dockerfile
COPY packages/python/urisysedge ./packages/python/urisysedge
```

## Duplikaty — runtime / edge

| Pakiet | Lokalizacja | Linie | Status |
|--------|-------------|-------|--------|
| **urisysedge** | `packages/python/urisysedge/` | ~255 | ★ canonical |
| urirdpedge | `urirdp-docker/.../urirdpedge/` | shim | ✅ migrowany |
| labedge | `urisys-automation-lab/.../labedge/` | shim | ✅ migrowany |
| urikvmedge | `urikvm-docker/.../urikvmedge/` | shim | ✅ migrowany |
| uribrowseredge | `uribrowser-docker/.../` | shim | ✅ migrowany |
| urisysnode | `urisys-node/.../urisysnode/runtime.py` | shim | ✅ migrowany |
| uristepperedge | `uristepper-docker/.../uristepperedge/` | ~170 | ✅ StepperRuntime; `JsonlEventStore` → urisysedge |

## Duplikaty — handlery (fork lineage urikvm → urirdp)

| Domena | urikvm-docker | urirdp-docker | Uwagi |
|--------|---------------|---------------|-------|
| KVM | `urikvm` | `urirdp_kvm` | RDP display vs czysty KVM |
| HIM | `urihim` | `urirdp_him` | xdotool |
| OCR | `uriocr` | `urirdp_ocr` | `latest.png` convention |
| LLM | `urillm` | `urirdp_llm` | vision analyze |
| Browser | `uribrowserdocker` | `urirdp_browser` | Chromium w RDP |
| Env | — | `urirdp_env` | alias do urienv |

**Konwencja danych między krokami** (bez explicit edge w YAML): `data/screenshots/latest.png`, `runtime.state`.

## Duplikaty — env policy

| Plik | Pakiet |
|------|--------|
| `packages/python/urisysedge/env.py` | ★ canonical |
| `urirdpedge/env.py` | shim |
| `urikvmedge/env.py` | shim |

## Paczki PyPI i dystrybucja (stan 2026-06-16)

Pełny opis trzech ścieżek (PyPI · Markpact · GitHub): **[`docs/DISTRIBUTION.md`](DISTRIBUTION.md)**.

| Pakiet | PyPI | Monorepo (vendored) |
|--------|------|---------------------|
| `urisys`, `urisys-node` | ✅ | ✅ |
| `uriscreen` | bundled w node | ✅ |
| `urisysedge` | ✅ 0.1.1 | `packages/python/urisysedge/` |
| `urikvm` | ✅ 0.1.1 | `urikvm-docker/packages/python/urikvm/` |
| `urihim`, `uriocr`, `urillm` | 🔲 brak | vendored w monorepo |
| `urikvm-docker-example` | ❌ nie publikować | dev bundle only |

### Dev — monorepo (gdy PyPI nie ma packa)

```bash
cd urisys
uv sync --extra kvm
```

Slave (lenovo): **pip one-liners** lub **`shell://` flow** — [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md).  
Nie używaj `bash scripts/install-kvm-packs-editable.sh` na maszynie slave.

### PyPI — publikacja z repo tellmesh

```bash
# pojedynczo
cd ~/github/tellmesh/urihim && goal -a -y

# wszystkie packi (kolejność: urisysedge → urikvm → …)
bash ~/github/tellmesh/scripts/publish-kvm-packs-goal.sh
```

Build tylko lokalnie (monorepo):

```bash
bash scripts/publish-pypi-packs.sh   # bez PYPI_TOKEN = tylko dist/
```

### Po pełnej publikacji PyPI

```bash
pip install "urisys-node[real,kvm]"
URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen,kvm,him urisys-node serve --port 8790
```

### Bez PyPI — Markpact + GitHub OCI

Kontrakty: `urikvm-docker/markpacts/*.markpact.md` → docelowo `markpact-contracts/packs/`.  
Runtime: `ArtifactResolver` + `register_forward_pack()` — szczegóły w [`DISTRIBUTION.md`](DISTRIBUTION.md).


| Pakiet | Gdzie używany |
|--------|---------------|
| `uri_control` (uricore) | `../uricore` (tellmesh) lub PyPI |
| `uri-packs/*` | `urisys --packs browser,docker,...` |
| `uri2flow`, `uri3` | expand/execute workflow (osobne repo) |

## Plan konsolidacji (kolejność)

1. ✅ **`urisysedge`** — runtime + env; shimy urirdpedge/labedge/urikvmedge/uribrowseredge/**urisysnode**
2. ✅ **`flow_runner`** — uri2flow + uri3 (`LabCallAdapter`)
3. ✅ **`JsonlEventStore`/`Runtime` dedup** — urisys-node + uristepper → urisysedge ([`MIGRATION-STEP3.md`](MIGRATION-STEP3.md))
4. ✅ **PyPI layout packów** — vendored w monorepo + osobne repo `tellmesh/{urisysedge,urikvm,urihim,uriocr,urillm}`; [`DISTRIBUTION.md`](DISTRIBUTION.md)
5. 🔲 **Handlery OCR/LLM/HIM** — wspólny `packages/python/urioperators/` z adapterem display
6. 🔲 **`FlowController`** — dodać `after`/`depends_on` (parity z uri2flow)
7. 🔲 **Pełny `uri3 run-workflow`** w lab (schema root w kontenerze)

## Zależności importów (z map.toon.yaml)

Hotspoty fan-out (refactor candidates):

- `scripts/run_test_sessions.session_lab_10_flows` — 31
- `src/urisys/cli.main` — 41
- `MarkpactManager.compile` — 34

Pełny call graph: `project/calls.mmd`, `project/calls.yaml`.

## Instalacja dev

```bash
cd urisys
uv sync
urisys routes --packs all

# edge lokalnie (PYTHONPATH)
export PYTHONPATH="packages/python:urirdp-docker/packages/python"
python3 -c "from urisysedge.runtime import Runtime; print(Runtime)"
```
