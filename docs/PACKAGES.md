# Paczki w ekosystemie tellmesh

Ten dokument opisuje **layout paczek** po migracji z vendored `urisys./*/packages/python/*` do sibling repos `tellmesh/{repo}/`.

Indeks modułów (historyczny): [`project/map.toon.yaml`](../project/map.toon.yaml).  
**Mapa mesh:** [`MESH.md`](MESH.md).

## Zasada: jedno źródło prawdy

| Warstwa | Gdzie | Rola |
|---------|-------|------|
| **core** | `urisys/src/urisys/` | CLI, managers, bootstrap |
| **control plane** | `tellmesh/uricontrol/` | `uri_control` — registry, policy, handlers, **edge runtime** |
| **uri router** | `tellmesh/uriresolver/` | `uri_resolver` — resolve, transport delegate |
| **capability packs** | `tellmesh/{urikvm,urihim,…}/` | handlery URI (`handlers.py`, `routes.py`) |
| **LLM shared** | `tellmesh/urioperators/` | chat, plan, decide, JSON parse |
| **docker glue** | `urisys/*-docker/` | Dockerfile, config, flow, testy integracyjne |

> **Legacy ``uri_control.edge`` usunięty.** Edge runtime (`Runtime`, `JsonlEventStore`, `http.serve`, `compose`) żyje w **`uricore`** → `uri_control.edge.*`.

## Workspace tellmesh (dev)

```text
tellmesh/
├── urisys/                 # glue + CLI ★ orchestrator
├── uriresolver/              # resolve + transport
├── uricore/                # uri_control (+ edge runtime)
├── urioperators/           # LLM helpers
├── urisys-node/            # urisysnode (bundled); uriscreen/urishell → pip
├── urichat/ uristt/ uriwebrtc/ urimessage/
└── urisys-automation-lab/  # lab server + voice pack glue
```

```bash
cd tellmesh/urisys
uv sync --extra kvm          # [tool.uv.sources] → ../{pack}
urisys routes --packs all
```

## Legenda ról

| Typ | Opis | Przykład |
|-----|------|----------|
| **core** | Centralny controller | `src/urisys/` |
| **edge-runtime** | `uri_control.edge` w uricore | `Runtime`, `compose`, `http` |
| **edge-compose** | CLI + pack registration | `urirdpedge`, `urikvmedge`, `uristepperedge` |
| **handlers** | Implementacja schematu URI | `tellmesh/urikvm/`, `tellmesh/urirdp/` |

Edge CLIs importują **`uri_control.edge`** (przez zależność `uricore`), nie osobny pakiet.

## Paczki PyPI i dystrybucja

Pełny opis: **[`docs/DISTRIBUTION.md`](DISTRIBUTION.md)**.

| Pakiet | Canonical repo | Rola |
|--------|----------------|------|
| `urisys` | `tellmesh/urisys` | orchestrator |
| `uriresolver` | `tellmesh/uriresolver` | intent router |
| `uricore` | `tellmesh/uricontrol` | control plane + edge |
| `urisys-node` | `tellmesh/urisys-node` | slave node |
| `urioperators` | `tellmesh/urioperators` | LLM helpers |
| `urikvm` … `urivql` | `tellmesh/{pack}/` | capability packs |

## Plan konsolidacji

1. ✅ **`uri_control.edge`** w `uricore` (dawniej ``uri_control.edge``)
2. ✅ **`urioperators` (LLM)** — wired w `urillm`
3. ✅ **`uriresolver`** — wyodrębniony resolver/transport
4. ✅ **PyPI layout** — osobne repo `tellmesh/{pack}/`
5. 🔲 **`urioperators` (OCR/HIM)** — faza 2 dedup

## Instalacja dev

```bash
cd tellmesh/urisys
uv sync
python3 -c "from uri_control.edge.runtime import Runtime; print(Runtime)"
```
