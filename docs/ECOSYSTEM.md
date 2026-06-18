# TellMesh URI ecosystem — model warstw (2026-06)

**Centrum orchestracji:** [urisys](https://github.com/tellmesh/urisys)  
**Mapa z diagramami:** [urisys/docs/MESH.md](https://github.com/tellmesh/urisys/blob/main/docs/MESH.md)

## Warstwy

```text
Markpact / kontrakt     → CO (capability, flow, policy)
urisys                  → orchestracja, CLI, flow runner, approval
urirouter (uri_router)  → GDZIE + JAK (resolver, HTTP/MQTT delegate)
uricore (uri_control)   → registry, policy, handlers, event store
uri_control.edge        → edge Runtime, compose, http.serve (w uricore)
*-edge / *-host         → fizyczny runtime (HTTP/MQTT /uri/call)
```

## Pakiety rdzeniowe

| Pakiet | Repo | Moduł | Rola |
|--------|------|-------|------|
| urisys | tellmesh/urisys | `urisys` | Orchestrator — CLI, Markpact, PackManager |
| urirouter | tellmesh/urirouter | `uri_router` | Intent router — targets, transport, envelope |
| uricore | tellmesh/uricore | `uri_control` | Control plane + `uri_control.edge` |
| urisys-node | tellmesh/urisys-node | `urisysnode` | Slave node, lazy pack install |
| urioperators | tellmesh/urioperators | `urioperators` | Wspólne helpery LLM |
| markpact-contracts | tellmesh/markpact-contracts | — | Kontrakty, przykłady resolverów |

## Zmiany 2026-06 (aktualny stan)

| Było | Jest |
|------|------|
| `urisysedge` (osobny PyPI) | **Usunięty** — kod w `uricore` → `uri_control.edge` |
| Resolver w `uri_control.resolver` | **`urirouter`** (`uri_router`) + shimy w uricore |
| `pip install urisysedge` | `pip install urirouter` + `uricore` (wheels z GitHub Releases) |

## Capability packs

Każdy pack: `manifest.yaml` + `handlers.py` + `routes.py` (rejestracja przez `uri_control.edge.manifest`).

Zależność: **`uricore>=0.1.8`**. Rejestrowany przez **urisys** (`urisys routes`, `urisys call`, Docker edge).

| Scheme | Repo | Edge / glue |
|--------|------|-------------|
| `stepper://` | uristepper, markpact-pololu | uristepperedge |
| `screen://` | uriscreen | urisys-node |
| `shell://` | urishell | urisys-node, urirdpedge |
| `kvm://` `him://` `ocr://` `llm://` | urikvm, urihim, uriocr, urillm | urikvmedge, urikvm-docker |
| `rdp://` | urirdp | urirdpedge, urirdp-docker |
| `browser://` | uribrowser | uribrowser-docker |
| `env://` | urienv | urienv-docker |
| `stt://` `webrtc://` `message://` | uristt, uriwebrtc, urimessage | urisys-automation-lab |

## Instalacja dev (workspace)

```bash
export TELLMESH_ROOT=~/github/tellmesh
cd $TELLMESH_ROOT/urisys && uv sync
pip install -e $TELLMESH_ROOT/urirouter -e $TELLMESH_ROOT/uricore
```

## Instalacja slave

```bash
pip install -U urisys
urisys init   # urirouter → uricore → urisys wheels
urisys node serve --host 0.0.0.0 --port 8790
```

Szczegóły: [urisys/docs/DISTRIBUTION.md](https://github.com/tellmesh/urisys/blob/main/docs/DISTRIBUTION.md) · [urisys/docs/NODE-SETUP.md](https://github.com/tellmesh/urisys/blob/main/docs/NODE-SETUP.md)
