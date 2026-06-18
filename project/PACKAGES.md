# Katalog paczek (sync z map.toon.yaml)

> Odpowiednik human-readable dla sekcji `M[]` w [`map.toon.yaml`](map.toon.yaml).  
> Pełna dokumentacja: [`../docs/PACKAGES.md`](../docs/PACKAGES.md).

## Status konsolidacji (2026-06-18)

| ID | Pakiet | Pliki w mapie | Status |
|----|--------|---------------|--------|
| E1 | `uricore` → `uri_control.edge` | `runtime.py`, `env.py`, `flow_*.py` | ✅ **canonical** |
| E1b | `urirouter` → `uri_router` | resolve, transport, policy | ✅ resolver |
| E2 | `urirdpedge` | `urirdp-docker/.../urirdpedge/` | ✅ shim → E1 |
| E3 | `labedge` | `urisys-automation-lab/.../labedge/` | ✅ shim → E1 |
| E4 | `urikvmedge` | `urikvm-docker/.../urikvmedge/` | ✅ shim → E1 |
| E5 | `uribrowseredge` | `uribrowser-docker/.../` | ✅ shim → E1 |
| E6 | `urisysnode/runtime` | `urisys-node/.../` | 🔶 node variant |
| ~~E0~~ | ~~`urisysedge`~~ | — | 🗄️ **archived** → E1 |

## Handlery — pary fork (urikvm ↔ urirdp)

| Schemat | urikvm | urirdp | map.toon linie |
|---------|--------|--------|----------------|
| kvm | `urikvm/handlers.py` 103 | `urirdp_kvm/handlers.py` 133 | M:125-127, M:163-164 |
| ocr | `uriocr/handlers.py` 115 | `urirdp_ocr/handlers.py` 79 | M:133-134, M:167-168 |
| llm | `urillm/handlers.py` 201 | `urirdp_llm/handlers.py` 196 | M:131-132, M:165-166 |
| him | `urihim/handlers.py` 81 | `urirdp_him/handlers.py` 72 | M:124, M:160-161 |
| browser | `uribrowserdocker/` 87 | `urirdp_browser/` 124 | M:65-66, M:155-156 |

## Core (nie forkować)

| Moduł | Ścieżka | Linie |
|-------|---------|-------|
| CLI | `src/urisys/cli.py` | 176 |
| MarkpactManager | `src/urisys/managers/markpact_manager.py` | 579 |
| PackManager | `src/urisys/managers/pack_manager.py` | 97 |
| FlowController | `src/urisys/controllers/flow_controller.py` | 33 |
| uricore | `../uricore` (tellmesh) lub PyPI | external |
| urirouter | `../urirouter` (tellmesh) lub PyPI | external |

## Lab-only (M:214-220, M:227-229)

| Pakiet | Rola |
|--------|------|
| `uristt` | STT mock MVP |
| `urichat` | NL → URI execute |
| `uriwebrtc` | WebRTC data channel |
| `flow_runner` | Compact flow executor |
| `automation_lab_server` | Gateway :8099 |

## Następne kroki (backlog)

1. Wspólny moduł `urioperators/` dla OCR/LLM/HIM shared logic
2. Regeneracja `map.toon.yaml` po większych zmianach mesh

```bash
code2llm ./ -f all -o ./project
```
