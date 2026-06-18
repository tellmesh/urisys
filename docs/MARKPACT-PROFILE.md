# Markpact profiles v1alpha (frozen)

> Status: **v1alpha** — egzekwowany przez `urisys markpact analyze` (errors/warnings).  
> Mapa ról: [`PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md) · format bloków: [`MARKPACT.md`](MARKPACT.md) · flow: [`FLOWS.md`](FLOWS.md)

## Profile stack

```text
UriPack Markpact v1        cienki kontrakt capability (manifest → markpact)
UriProcess Profile v1      process:// + urisys://flow + markpact:flow
UriFlow Profile v1         do / id / after / save_as / ${ref} / expect
UriRuntime Resolver v1     targets + transport + adapter (poza procesem)
UriTransport Binding v1    HTTP/MQTT/… dla tej samej koperty /uri/call
```

## Rozdzielenie `requires` vs `uses`

W `markpact:pack` **nie mieszaj** schematów z nazwami paczek:

```yaml
requires:
  schemes:          # CO jest potrzebne semantycznie (analyze, resolver)
    - stepper
    - screen
  capabilities:     # opcjonalnie: stabilne operation names
    - stepper.status
    - screen.frame

uses:
  packs:            # DOMYŚLNE paczki Python w dev (TELLMESH_ROOT)
    - uristepper
    - uriscreen
```

| Pole | Poziom | Znaczenie |
|------|--------|-----------|
| `requires.schemes` | semantyczny | Jakie scheme muszą być dostępne w runtime |
| `requires.capabilities` | semantyczny | Dokumentacja / conformance (operation names) |
| `uses.packs` | implementacja | Domyślne paczki do `markpact run --as flow` |
| `markpact:run uses` | runtime | Lista packów ładowanych przy service/flow (jak dotąd) |

Resolver może podmienić implementację (`uristepper` → ESP32 firmware, `uribrowserdocker` → Chrome CDP).

**Legacy:** płaska lista `uses: [stepper, screen]` w packu = `requires.schemes` (backward compatible).

## `operation` — globalna nazwa

```text
operation = stabilna nazwa semantyczna między mock / Python / Docker / ESP32
```

```yaml
operation: stepper.move_relative    # ✅
operation: move_relative            # ⚠️ warning (brak namespace)
operation: machine_cycle.run        # ✅ proces
```

Handler może mieć inną ścieżkę; `operation` jest kluczem policy i eventów.

## URI path ↔ `kind`

| Reguła | Severity |
|--------|----------|
| URI zawiera `/query/` → `kind: query` | ERROR |
| URI zawiera `/command/` → `kind: command` | ERROR |
| `kind: command` + `side_effects: true` → `approval` ≠ `not_required` | ERROR |

## Risk (obok `approval`)

```yaml
risk:
  class: physical_process | host_shell | remote_session | capture_sensitive | user_visible_output
  level: low | medium | high | critical
  requires:
    - approval
    - dry_run_supported
    - audit
```

Klasy efektów (dokumentacyjnie): `read_observation`, `physical_motion`, `host_mutation`, `remote_session_mutation`, …

## Context envelope (minimum)

```yaml
context:
  approved: true
  dry_run: true
  environment: mock
  trace_id: "..."
  request_id: "..."
  deadline_ms: 5000
  policy_profile: lab | production | ci | maintenance
  resolver_profile: mock | docker-pc-usb | esp32-mqtt | …
```

Ta sama koperta przez HTTP, MQTT, lokalny runtime.

## UriFlow levels

| Level | Features | Executor |
|-------|----------|----------|
| 0 | linear `do:` | `FlowController` (urisys CLI) |
| 1 | `id`, `after` | `run_flow`, uri2flow |
| 2 | `save_as`, `${ref}`, `payload_from`, `if:` | `run_flow`, uri3 |
| 3 | `expect`, compensation (plan) | lab sessions, analyze |

W flow deklaruj:

```yaml
flow:
  id: machine-cycle
  profile: uri-flow/v1          # poziom docelowy (informacyjnie)
requires_features:              # jawna lista — tylko to analyze egzekwuje
  - linear
  - step_id
  - save_as
  - ref
  - expect
```

`analyze` ostrzega, gdy **`requires_features`** jest ustawione i brakuje wymaganego feature w flow.

## Proces UriProcess

- **Brak** `targets:` w `markpact:flow` / packu procesu
- Capability wejścia: `process://<authority>/command/run`
- Handler: `urisys://flow/<flow-id>`
- Resolver: `URISYS_RESOLVER_CONFIG` lub materialized `generated/*/urisys.runtime.yaml`

## Analyze / CI rules (v1alpha)

**ERROR**

- command + side_effects + approval:not_required
- URI `/query/` z kind:command lub odwrotnie
- process capability bez `urisys://flow/<id>`
- flow używa scheme spoza `requires.schemes` (undeclared)
- handler `markpact://self` bez sandbox policy (plan)

**WARNING**

- `operation` bez kropki (nie namespaced)
- flow bez `expect:`
- `ocr://…/image/latest/…` (implicit state)
- test mutacji bez `dry_run: true` w context
- command bez testu approval / dry_run
- `requires.schemes` vs faktyczne scheme w flow — rozjazd
- brak `requires` przy `scheme: process` (użyj jawnego profilu)

## Service ports

```yaml
service:
  port_hint: 8799      # dokumentacja / dev default
  path: /uri/call
  port_policy: default_only   # plan: allocator + URISYS_PORT
```

## Dokumentacja — podział ról

| Plik | Zawartość |
|------|-----------|
| README paczki | szybki start, link do MESH |
| `MARKPACT.md` | składnia bloków |
| `MARKPACT-PROFILE.md` | ten dokument — profile v1alpha |
| `PROCESS-ARCHITECTURE.md` | proces / resolver / marksync |
| `FLOWS.md` | UriFlow levels, save_as, expect |
| `SECURITY.md` | sandbox, allowlist shell (plan) |

## Priorytety implementacji

1. ✅ `requires.schemes` / `uses.packs` + analyze lint  
2. 🔄 risk + context envelope w kontraktach referencyjnych  
3. 🔄 expect w CI sesji (lab-10)  
4. 📋 resolver schema jako osobny kontrakt (`uri-transport-binding`)  
5. 📋 conformance tests per capability
