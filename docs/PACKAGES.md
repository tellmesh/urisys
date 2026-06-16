# Paczki w monorepo urisys

Ten dokument opisuje **layout paczek**, **duplikaty** i **plan konsolidacji**.  
Indeks modułów z liczbami linii: [`project/map.toon.yaml`](../project/map.toon.yaml) (sekcja `M[]`).

## Legenda ról

| Typ | Opis | Przykład |
|-----|------|----------|
| **core** | Centralny controller | `src/urisys/` |
| **edge-shared** | Wspólny runtime Docker | `packages/python/urisysedge/` |
| **edge-shim** | Alias kompatybilności | `urirdpedge`, `labedge` |
| **edge-fork** | Kopia do konsolidacji | `urikvmedge`, `uribrowseredge` |
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
| urikvmedge | `urikvm-docker/.../urikvmedge/` | ~228 | 🔶 fork — konsolidacja TODO |
| uribrowseredge | `uribrowser-docker/.../` | ~222 | 🔶 fork |
| urisysnode | `urisys-node/.../urisysnode/runtime.py` | ~165 | 🔶 node-specific (tail events) |
| urisysedge (env) | `urienv-docker/.../urisysedge/` | ~21 | 🔶 thin wrapper na uricore |
| uristepper StepperRuntime | `uristepper-docker/.../` | ~193 | 🔶 osobna polityka stepper |

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
| `urikvmedge/env.py` | ~95% identyczny — TODO: shim |

## Paczki zewnętrzne (nie duplikować w urisys)

| Pakiet | Gdzie używany |
|--------|---------------|
| `uri_control` (uricore) | `../uricore` (tellmesh) lub PyPI |
| `uri-packs/*` | `urisys --packs browser,docker,...` |
| `uri2flow`, `uri3` | expand/execute workflow (osobne repo) |

## Plan konsolidacji (kolejność)

1. ✅ **`urisysedge`** — runtime + env; shimy urirdpedge/labedge
2. 🔲 **`urikvmedge` / `uribrowseredge`** — shims do urisysedge + osobne `serve()` w cli
3. 🔲 **Handlery OCR/LLM/HIM** — wspólny `packages/python/urioperators/` z adapterem display
4. 🔲 **`FlowController`** — dodać `after`/`depends_on` (parity z flow_runner)
5. 🔲 **uri3** jako executor w lab zamiast własnego flow_runner (opcjonalnie)

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
