# Paczki w ekosystemie tellmesh

Ten dokument opisuje **layout paczek** po migracji z vendored `urisys./*/packages/python/*` do sibling repos `tellmesh/{repo}/`.

Indeks modułów (historyczny, przed migracją): [`project/map.toon.yaml`](../project/map.toon.yaml).

## Zasada: jedno źródło prawdy

| Warstwa | Gdzie | Rola |
|---------|-------|------|
| **core** | `urisys/src/urisys/` | CLI, managers, bootstrap |
| **uri router** | `tellmesh/urirouter/` | resolve, transport delegate, envelope (`uri_router`) |
| **control plane** | `tellmesh/uricore/` | registry, policy, handlers (`uri_control`) |
| **capability packs** | `tellmesh/{urikvm,urihim,…}/` | handlery URI (`handlers.py`, `routes.py`) |
| **edge shared** | `tellmesh/urisysedge/` | `Runtime`, `JsonlEventStore`, env policy |
| **LLM shared** | `tellmesh/urioperators/` | chat, plan, decide, JSON parse |
| **docker glue** | `urisys/*-docker/` | Dockerfile, config, flow, testy integracyjne |

W monorepo **urisys nie ma już** katalogów `packages/python/{pack}/` — tylko glue Docker i testy.

Synchronizacja / drift guard:

```bash
cd urisys
python3 scripts/pack_sync.py check --all
python3 -m pytest tests/test_vendored_sync.py -q
```

## Workspace tellmesh (dev)

```text
tellmesh/
├── urisys/                 # glue + CLI (repo git) ★ orchestrator
├── urirouter/              # ★ URI intent router (resolve + transport)
├── uricore/                # ★ capability dispatch (uri_control)
├── urisysedge/             # ★ edge runtime
├── urioperators/           # ★ LLM helpers
├── urisys-node/            # urisysnode (bundled); uriscreen/urishell → pip
├── uriscreen/ urishell/ urichat/
├── urikvmedge/             # CLI urisys-kvm
├── urirdpedge/             # CLI urisys-rdp
├── uribrowser/ uristepper/ uristepperedge/
└── urisys-automation-lab/  # lab server + voice pack glue
```

```bash
cd tellmesh/urisys
uv sync --extra kvm          # [tool.uv.sources] → ../{pack}
urisys routes --packs all
```

CI bez lokalnego checkout siblingów:

```bash
bash scripts/ci-checkout-siblings.sh   # clone tellmesh/* obok urisys
bash scripts/ci-install-siblings.sh    # pip install -e
```

## Legenda ról

| Typ | Opis | Przykład |
|-----|------|----------|
| **core** | Centralny controller | `src/urisys/` |
| **edge-shared** | Wspólny runtime Docker | `tellmesh/urisysedge/` |
| **edge-shim** | Legacy alias (removed) | — |
| **edge-compose** | CLI + pack registration | `urirdpedge`, `urikvmedge`, `uristepperedge` |
| **handlers** | Implementacja schematu URI | `tellmesh/urikvm/`, `tellmesh/urirdp/` |
| **lab-pack** | MVP w automation-lab | deprecated `urichat/` only |

## Drzewo urisys (glue only)

```text
urisys/
├── src/urisys/                 # pip package urisys
├── scripts/pack_sync.py        # sync / promote / check
├── scripts/pack_registry.py    # mapowanie pack → tellmesh repo
├── urikvm-docker/              # Dockerfile + markpacts (port 8794)
├── urirdp-docker/              # RDP desktop bundle (8795 / 3389)
├── uribrowser-docker/
├── urienv-docker/
├── uristepper-docker/
├── urisys-automation-lab/      # server + web + flows (8099)
└── urisys-node/                # integracja slave (testy, docker config)
```

## Wspólny pakiet: `urioperators`

Wyodrębnione helpery LLM współdzielone przez `urillm`:

| Moduł | Zawartość |
|-------|-----------|
| `llm_json.py` | `parse_json_response` |
| `llm_chat.py` | `openai_compatible_chat`, `litellm_chat` |
| `llm_plan.py` | `plan_from_parsed` |
| `llm_decide.py` | `decision_from_parsed` |

Lokalizacja: **`tellmesh/urioperators/`**.

**Faza 2 (plan):** OCR/HIM helpers — ten sam wzorzec.

## Wspólny pakiet: `urisysedge`

| Moduł | Zawartość |
|-------|-----------|
| `runtime.py` | `Route`, `Runtime`, `JsonlEventStore`, `run_flow` |
| `env.py` | `load_env_policy`, `resolve_env_var` |

Lokalizacja: **`tellmesh/urisysedge/`**.

Shimy usunięte — edge CLIs importują `urisysedge` bezpośrednio: `urirdpedge`, `urikvmedge`, `uristepperedge`.

## Standalone packs (by domain)

| Schemes | Canonical repo | Edge CLI |
|---------|----------------|----------|
| `rdp://` | `urirdp` | `urirdpedge` (`urisys-rdp`) |
| `kvm/him/ocr/llm` | `urikvm`, `urihim`, `uriocr`, `urillm` | `urikvmedge` / `urirdpedge` |
| `screen://` | `uriscreen` | bundled in `urisys-node` via pip |
| `shell://` | `urishell` | `urirdpedge` / `urisys-node` pip dep |
| `stt/webrtc/message/chat` | `uristt`, `uriwebrtc`, `urimessage`, `urichat` | lazy-install on `urisys-node`; ifURI duplex: [if-uri/docs/WEBRTC.md](https://github.com/if-uri/app/blob/main/docs/WEBRTC.md) |
| `env://` | `urienv` | `urirdpedge` |
| `browser://` | `uribrowser` | `urirdpedge` (+ lab aliases) |
| `stepper://` | `uristepper` | `uristepperedge` |

Wspólne X11 helpers: `urirdp/urirdp/display.py`, `urikvm/urikvm/display.py`.

Konwencja danych: `data/screenshots/latest.png`, `runtime.state`.

## Paczki PyPI i dystrybucja

Pełny opis: **[`docs/DISTRIBUTION.md`](DISTRIBUTION.md)**.

| Pakiet | Canonical repo | Monorepo urisys |
|--------|----------------|-----------------|
| `urisys` | `tellmesh/urisys` | root `pyproject.toml` |
| `urirouter` | `tellmesh/urirouter` | resolve + transport (zależność urisys) |
| `uricore` | `tellmesh/uricore` | GitHub Releases wheel |
| `urisys-node` | `tellmesh/urisys-node` | config/docker w `tellmesh/urisys-node/` |
| `urisysedge` | `tellmesh/urisysedge` | brak vendored |
| `urioperators` | `tellmesh/urioperators` | brak vendored |
| `urikvm` … `urivql` | `tellmesh/{pack}/` | brak vendored |
| `urikvmedge` | `tellmesh/urikvmedge` | `tellmesh/urikvm-docker/` glue |
| `urirdpedge` | `tellmesh/urirdpedge` | `tellmesh/urirdp-docker/` glue |

### Dev

```bash
cd tellmesh/urisys
uv sync --extra kvm
```

Slave (lenovo): [`docs/NODE-SETUP.md`](NODE-SETUP.md).

### Docker build (kontekst = root tellmesh)

```bash
docker build -f urikvm-docker/Dockerfile /path/to/tellmesh
docker build -f urirdp-docker/Dockerfile /path/to/tellmesh
```

## Plan konsolidacji

1. ✅ **`urisysedge`** — runtime + env + HTTP
2. ✅ **`urioperators` (LLM)** — wired w `urillm`
3. ✅ **PyPI layout** — osobne repo `tellmesh/{pack}/`
4. ✅ **Migracja monolitu `urirdp`** → `urirdp` + `urirdpedge` + standalone packi
5. ✅ **Voice packs** — `uristt`, `uriwebrtc`, `urimessage` poza automation-lab
6. ✅ **`urirouter`** — wyodrębniony z `uricore` (resolver + transport + envelope)
7. 🔲 **`urioperators` (OCR/HIM)** — faza 2 dedup
8. 🔲 **`uriimgl` / `urivql`** — forward lub in-process pack

## Instalacja dev

```bash
cd tellmesh/urisys
uv sync
python3 -c "from urisysedge.runtime import Runtime; print(Runtime)"
```
