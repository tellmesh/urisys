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

## Paczki zewnętrzne (nie duplikować w urisys)

| Pakiet | Gdzie używany |
|--------|---------------|
| `uri_control` (uricore) | `../uricore` (tellmesh) lub PyPI |
| `uri-packs/*` | `urisys --packs browser,docker,...` |
| `uri2flow`, `uri3` | expand/execute workflow (osobne repo) |

## Plan konsolidacji (kolejność)

1. ✅ **`urisysedge`** — runtime + env; shimy urirdpedge/labedge/urikvmedge/uribrowseredge/**urisysnode**
2. ✅ **`flow_runner`** — uri2flow + uri3 (`LabCallAdapter`)
3. ✅ **`JsonlEventStore`/`Runtime` dedup** — urisys-node + uristepper → urisysedge ([`MIGRATION-STEP3.md`](MIGRATION-STEP3.md))
4. 🔲 **Handlery OCR/LLM/HIM** — wspólny `packages/python/urioperators/` z adapterem display
5. 🔲 **`FlowController`** — dodać `after`/`depends_on` (parity z uri2flow)
6. 🔲 **Pełny `uri3 run-workflow`** w lab (schema root w kontenerze)

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
