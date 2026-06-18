# Proces URI: Markpact → resolver → marksync

Trzy osobne odpowiedzialności. Nie mieszaj ich w jednym pliku procesu.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│  Markpact procesu          CO ma się wydarzyć                           │
│  (machine-cycle-process)     sekwencja URI, policy, approval, uses      │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ compile (urisys)
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Cache runtime             manifest + flows/*.uri.flow.yaml             │
│  (.markpact/ / .urisys/)   urisys://flow/<id> → kroki URI               │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ + resolver config (per środowisko)
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Runtime resolver          GDZIE i JAK wykonać                          │
│  (materializowany YAML)    targets, transport, adapter, endpoint        │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ sync + generate
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  marksync                  synchronizacja + pliki dla środowiska        │
│  github.com/markpact/marksync                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## URI Flow Contract (desktop automation)

Przykład: [`desktop-automation-processes.markpact.md`](../../markpact-contracts/packs/desktop-automation-processes.markpact.md) — procesy z `tellmesh/examples/39_system_automations`.

```text
URI Flow Contract = przenośny opis procesu jako grafu wywołań URI
  do:     sekwencja lub { id, uri, payload, after }
  brak:   handlerów, transportu, języka runtime
analyze: requires.schemes per flow (auto)
```

Źródło flow pozostaje w repo jako `*.uri.flow.yaml`; Markpact to warstwa procesowa + `process://…/command/run` + testy.

## 1. Markpact procesu — **co**

Plik typu [`machine-cycle-process.markpact.md`](../../markpact-contracts/packs/machine-cycle-process.markpact.md).

**Profil v1alpha:** [`MARKPACT-PROFILE.md`](MARKPACT-PROFILE.md) — `requires.schemes` vs `uses.packs`, lint w `urisys markpact analyze`.

Zawiera wyłącznie:

| Blok | Rola |
|------|------|
| `markpact:pack` | scheme `process`, capability `process://…/command/run`, `handler: urisys://flow/<id>` |
| `markpact:flow` | kroki `stepper://…`, `screen://…`, `tts://…` — **abstrakcyjne URI** |
| `markpact:run` | tryby (`flow`, `service`, …), `uses` (zależności od innych packów) |
| `markpact:tests` | kontrakt behawioralny (approval, dry-run) |

**Nie zawiera:** adresów MQTT, SSH, docker-compose, mapy pinów ESP32, kodu handlerów packów.

Paczki URI (`uristepper`, `uriscreen`, `uristt`, `urishell`, …) pozostają niezmienione — proces to klej nad istniejącymi capability.

```yaml
# W procesie — tylko to:
do:
  - stepper://machine-01/axis/x/command/move-relative:
      steps: 100
  - screen://operator/monitor/primary/query/frame
```

Wykonanie: `urisys markpact run … --as flow` albo `POST /uri/call` na `process://machine-cycle/command/run`.

## 2. Runtime resolver — **gdzie i jak**

Warstwa **poza** procesowym Markpactem (lub w materializowanym cache, nie w źródle Git procesu).

Resolver mapuje **logiczne hosty URI** (`machine-01`, `operator`, `build`) na platformę i transport:

```yaml
# generated/edge-linux/urisys.runtime.yaml  — przykład (Etap 3)
environment: edge-linux

targets:
  machine-01:
    platform: esp32
    transport: mqtt
    endpoint: urisys/machine-01/call
  operator:
    platform: desktop-linux
    transport: local
    adapter: uriscreen
  build:
    platform: server-linux
    transport: ssh
    adapter: urishell
```

Ten sam flow procesu na ESP32 vs desktop vs serwer — **te same URI w flow**, inny plik resolvera ładowany do `runtime.config` przed `runtime.call`.

`urisys` wykonuje kroki; resolver decyduje, czy `stepper://machine-01/…` idzie przez MQTT, serial, lokalny Python czy HTTP bridge.

### Wykonanie transportu (Etap 5)

Gdy `targets.<authority>.transport` ≠ `local`, `Runtime.call` deleguje wywołanie **przed** dopasowaniem lokalnej trasy:

| transport | Zachowanie |
|-----------|------------|
| `local` | remap `uri_host` + handler w procesie (domyślnie) |
| `http` | `POST endpoint` z `{uri, payload, context}` (urisys wire ABI) |
| `mqtt` | `POST options.bridge_url` z `{topic, uri, payload, qos}` |
| `ssh` | alias do `http`, gdy `endpoint` to URL zdalnego urisys |
| `unsupported` | błąd (np. ESP32 stub bez adaptera) |

Zmienne środowiskowe: `URISYS_HTTP_BRIDGE`, `URISYS_MQTT_BRIDGE_URL`.  
`dry_run: true` w kontekście — symulacja bez sieci.

Implementacja: `uri_control.transport.delegate_transport_call`.

Pełny przykład: [`markpact-contracts/packs/examples/urisys.runtime.resolver.yaml`](../../markpact-contracts/packs/examples/urisys.runtime.resolver.yaml).

Status w tellmesh: **Etap 3 ✅**

### Implementacja (uricore + urisys)

| Moduł | Rola |
|-------|------|
| `uri_control.resolver` | `load_resolver_file`, `apply_resolver_config`, `resolve_uri` |
| `Runtime.call` | przed `resolve()` — remap authority (`uri_host`), kontekst `source_uri` / `target` / `transport` |
| `markpact_run._build_runtime` | ładuje resolver z `config.resolver_path` lub env **`URISYS_RESOLVER_CONFIG`** |

```python
# resolve_uri — przykład remap
# stepper://machine-01/… + targets.machine-01.uri_host=gateway
# → stepper://gateway/… + context.target="machine-01"
```

### Konwencja YAML resolvera

Pola w `targets.<authority>`:

| Pole | Opis |
|------|------|
| `platform` | Profil środowiska (`edge-linux`, `esp32`, `server-linux`, …) |
| `transport` | `local`, `mqtt`, `ssh`, `http`, … (metadata; wykonanie transportu — przyszły etap) |
| `uri_host` / `host` | Remap netloc URI przed routingiem |
| `adapter` | Pack edge (`uristepper`, `uriscreen`, `uribrowserdocker`, …) |
| `endpoint` | Adres mostu (np. MQTT topic) |
| `options` | Parametry transportu (qos, timeout, …) |

Sekcja opcjonalna `runtime:` — domyślne wartości mergowane do `runtime.config` (np. `device_profile`, `dry_run`).

`uri_aliases` — mapowanie domenowych URI na platformowe (np. `package://chromium/command/install` → `shell://apt-get`). Stosowane w `resolve_uri` przed routingiem.

### Ładowanie resolvera

```bash
export URISYS_RESOLVER_CONFIG=markpact-contracts/packs/examples/urisys.runtime.resolver.yaml

urisys markpact run markpact-contracts/packs/machine-cycle-process.markpact.md \
  --as flow --approve --dry-run

# alternatywa: config YAML z resolver_path (względem katalogu pliku config)
urisys markpact run … --config profiles/edge.config.yaml
```

```yaml
# edge.config.yaml
resolver_path: urisys.runtime.hybrid.yaml   # relative to profiles/
```

Przykład UriRouter + generator resolverów: [tellmesh/markpact-pololu `docs/URI-ROUTER.md`](https://github.com/tellmesh/markpact-pololu/blob/main/docs/URI-ROUTER.md).  
Pakiet Python: [tellmesh/urirouter](https://github.com/tellmesh/urirouter) (`uri_router`).  
Mapa mesh: [`docs/MESH.md`](MESH.md).

## 3. marksync — **synchronizacja i generowanie**

Repozytorium: [markpact/marksync](https://github.com/markpact/marksync) (lokalnie: `~/github/markpact/marksync`).

Rola w łańcuchu URI:

| marksync | urisys |
|----------|--------|
| CRDT sync plików Markpact (współedycja, wersje) | compile → manifest + flows |
| Deployer agent → trigger po zmianie `markpact:run` | `markpact materialize` / `run --as service` |
| Pluginy: K8s, GitHub Actions, Airflow, MQTT, … | artefakty runtime (manifest, routes) |
| `markpact:env` — profile dev/staging/prod | `environment` + resolver per profil |

Typowy przepływ (docelowo):

1. Edycja machine-cycle-process.markpact.md  (marksync server / push)
2. urisys markpact compile + materialize     (manifest + flows)
3. marksync generate per target (plugin `urisys` lub urisys CLI):
     generated/linux/urisys.runtime.yaml
     generated/server/urisys.runtime.yaml + docker-compose.snippet.yml
     generated/esp32/urisys.runtime.yaml + uri_routes.h
     generated/platform-export.json
4. Deploy / sync na urządzenie (resolver: `URISYS_RESOLVER_CONFIG=generated/linux/urisys.runtime.yaml`)

### Layout `generated/` (Etap 4)

```text
.markpact/{package_id}/generated/
  linux/urisys.runtime.yaml
  server/urisys.runtime.yaml
  server/docker-compose.snippet.yml
  esp32/urisys.runtime.yaml
  esp32/uri_routes.h
  platform-export.json
```

Resolver jest **generowany** z authorities i schemes w flow procesu (`platform_export.collect_process_uris`). To stub deploymentu — ops mogą nadpisać `targets` przed produkcją.

### CLI urisys

```bash
export TELLMESH_ROOT=~/github/tellmesh

# pełny pipeline (materialize + platform export)
bash urisys/scripts/marksync-materialize.sh \
  markpact-contracts/packs/desktop-automation-processes.markpact.md

# tylko export resolverów
urisys markpact export-platform \
  markpact-contracts/packs/desktop-automation-processes.markpact.md \
  --out generated

# materialize + generated/ w .markpact/{id}/
urisys markpact materialize \
  markpact-contracts/packs/desktop-automation-processes.markpact.md \
  --platforms linux,server,esp32

# bez exportu platform
urisys markpact materialize … --no-platform-export
```

### Plugin marksync `urisys`

Rejestr: `registry.get("urisys")` → `marksync.plugins.integrations.urisys`.

`PipelineSpec.metadata.urisys`:

```yaml
urisys:
  markpact_path: markpact-contracts/packs/desktop-automation-processes.markpact.md
  materialized_dir: .markpact/desktop_automation_processes   # opcjonalnie
  out_dir: generated                                          # opcjonalnie
  platforms: [linux, server, esp32]
```

Plugin wywołuje `urisys.managers.platform_export.export_platform_artifacts` i zwraca pliki w `ConversionResult.metadata.files`.

Opcjonalnie `MARKSYNC_PUSH=1` w `marksync-materialize.sh` — `marksync push` przed materializacją.

Deploy na edge:

```bash
# shell: materialize → copy → optional script
DEPLOY_DIR=/var/lib/urisys/desktop-automation \
  bash urisys/scripts/marksync-deploy.sh \
  markpact-contracts/packs/desktop-automation-processes.markpact.md

# lub materialize + deploy w jednym kroku
MARKSYNC_DEPLOY=1 bash urisys/scripts/marksync-materialize.sh …
```

marksync plugin `deploy()`:

```python
registry.export("urisys", pipeline)  # tylko export
registry.get("urisys").deploy(pipeline, crdt_doc=crdt)  # materialize + opcjonalnie deploy_dir
```

marksync **nie zastępuje** urisys — synchronizuje kontrakt i **materializuje** to, co resolver i platforma potrzebują lokalnie.

## Podział odpowiedzialności (skrót)

```text
URI packi     = klocki (capability, handlery)
markpact:flow = proces (co, w jakiej kolejności)
resolver      = platforma (gdzie, jak routować hosty URI)
urisys        = wykonanie (call, policy, events, urisys://flow/)
marksync      = sync źródeł + generowanie artefaktów per środowisko
```

## Etapy wdrożenia

| Etap | Co | Status |
|------|-----|--------|
| 1 | `markpact:flow` jako proces produkcyjny (`machine-cycle`, …) | ✅ przykład w repo |
| 2 | `urisys://flow/<id>` — capability `process://…/command/run` | ✅ uricore + urisys |
| 3 | Resolver `targets:` — loader + `resolve_uri` in `Runtime.call` | ✅ |
| 4 | marksync → `generated/{linux,server,esp32}/` | ✅ `export-platform` + marksync plugin `urisys` |

## Kolejne kroki (poza Etap 1–4)

| Temat | Opis |
|-------|------|
| Transport execution | Resolver deleguje `http`/`mqtt` w `Runtime.call` | ✅ podstawowy |
| marksync deploy hook | `plugin.deploy()` + `marksync-deploy.sh` | ✅ |
| `save_as` / `${ref}` w flow | ✅ `run_flow` + `flow_refs.py` |
| Domain URIs | `package://chromium/...` → `uri_aliases` w resolver | ✅ |

## Powiązane

- [`MARKPACT.md`](MARKPACT.md) — bloki, compile, `urisys://flow/`
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — control plane, edge, Docker
- [`FLOWS.md`](FLOWS.md) — format `*.uri.flow.yaml`
