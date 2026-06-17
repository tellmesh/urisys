# Paczki w ekosystemie tellmesh

Ten dokument opisuje **layout paczek** po migracji z vendored `urisys./*/packages/python/*` do sibling repos `tellmesh/{repo}/`.

Indeks modułów (historyczny, przed migracją): [`project/map.toon.yaml`](../project/map.toon.yaml).

## Zasada: jedno źródło prawdy

| Warstwa | Gdzie | Rola |
|---------|-------|------|
| **core** | `urisys/src/urisys/` | CLI, managers, bootstrap |
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
├── urisys/                 # glue + CLI (repo git)
├── urisysedge/             # ★ edge runtime
├── urioperators/           # ★ LLM helpers
├── urisys-node/            # urisysnode, uriscreen, urishell
├── urikvm/ urihim/ uriocr/ urillm/
├── urimail/ urioffice/ urivql/
├── urikvmedge/             # CLI urisys-kvm
├── urirdp/                 # urirdp*, urirdpedge
├── uribrowser/ urienv/ uristepper/
└── urisys-automation-lab/  # labedge, urichat, uristt, …
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
| **edge-shim** | Alias kompatybilności | `urirdpedge`, `labedge` w bundle repo |
| **handlers** | Implementacja schematu URI | `tellmesh/urikvm/`, `tellmesh/urirdp/` |
| **lab-pack** | MVP w automation-lab | `tellmesh/urisys-automation-lab/` |

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

Wyodrębnione helpery LLM współdzielone przez `urillm` i `urirdp_llm`:

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

Shimy (re-export w bundle repos): `urirdpedge`, `urikvmedge`, `labedge`, `uribrowseredge`, `urisysnode/runtime.py`.

## Fork lineage urikvm ↔ urirdp

| Domena | tellmesh repo | Uwagi |
|--------|---------------|-------|
| KVM | `urikvm` / `urirdp_kvm` | RDP display vs czysty KVM |
| HIM | `urihim` / `urirdp_him` | xdotool |
| OCR | `uriocr` / `urirdp_ocr` | `latest.png` convention |
| LLM | `urillm` / `urirdp_llm` | helpery → `urioperators` |
| Browser | `uribrowser` / `urirdp_browser` | Chromium w RDP |
| Env | `urienv` / `urirdp_env` | alias |

Konwencja danych: `data/screenshots/latest.png`, `runtime.state`.

## Paczki PyPI i dystrybucja

Pełny opis: **[`docs/DISTRIBUTION.md`](DISTRIBUTION.md)**.

| Pakiet | Canonical repo | Monorepo urisys |
|--------|----------------|-----------------|
| `urisys` | `tellmesh/urisys` | root `pyproject.toml` |
| `urisys-node` | `tellmesh/urisys-node` | glue w `urisys/urisys-node/` |
| `urisysedge` | `tellmesh/urisysedge` | brak vendored |
| `urioperators` | `tellmesh/urioperators` | brak vendored |
| `urikvm` … `urivql` | `tellmesh/{pack}/` | brak vendored |
| `urikvmedge` | `tellmesh/urikvmedge` | `urikvm-docker/` = glue only |

### Dev

```bash
cd tellmesh/urisys
uv sync --extra kvm
```

Slave (lenovo): [`docs/NODE-SETUP.md`](NODE-SETUP.md).

### Docker build (kontekst = root tellmesh)

```bash
docker build -f urisys/urikvm-docker/Dockerfile /path/to/tellmesh
docker build -f urisys/urirdp-docker/Dockerfile /path/to/tellmesh
```

## Plan konsolidacji

1. ✅ **`urisysedge`** — runtime + env; shimy edge
2. ✅ **`urioperators` (LLM)** — wired w `urillm` + `urirdp_llm`
3. ✅ **PyPI layout** — osobne repo `tellmesh/{pack}/`
4. ✅ **Migracja vendored → sibling** — `pack_sync promote --all`
5. 🔲 **`urioperators` (OCR/HIM)** — faza 2 dedup
6. 🔲 **`uriimgl` / `urivql`** — forward lub in-process pack

## Instalacja dev

```bash
cd tellmesh/urisys
uv sync
python3 -c "from urisysedge.runtime import Runtime; print(Runtime)"
```
