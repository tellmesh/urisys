# UriRuntime Resolver v1

> Kontrakt resolvera (GDZIE/JAK) — **poza** Markpactem procesu.  
> Przykłady: [`markpact-contracts/packs/examples/`](../../markpact-contracts/packs/examples/)

## Rola

```text
process Markpact     → abstrakcyjne URI (stepper://machine-01/…)
urisys.runtime.yaml  → targets, transport, adapter, policy
export-platform      → generuje stub per linux | server | esp32
```

## Top-level

```yaml
apiVersion: tellmesh.io/v1
kind: UriRuntimeResolver
metadata:
  generated_from: machine-cycle-process
  platform: linux
  profile: uri-resolver/v1

environment: edge-linux

uri_aliases:
  package://chromium/command/install: shell://apt-get

targets:
  machine-01:
    platform: esp32
    transport: mqtt
    endpoint: urisys/machine-01/call
    uri_host: tic-t249          # opcjonalny remap authority
    adapter: external
    options:
      qos: 1
      timeout_ms: 5000

policy:
  operations:
    stepper.move_relative:
      max: { steps: 10000, speed_sps: 1200 }

runtime:
  default_environment: mock
  dry_run: true
  device_profile: { ... }
```

## Pola `targets.*`

| Pole | Opis |
|------|------|
| `platform` | `esp32`, `edge-linux`, `desktop-linux`, `server-linux`, `pc-linux` |
| `transport` | `local`, `http`, `mqtt`, `ssh`, `websocket`, `nats`, `serial`, `usb` |
| `endpoint` | URL lub topic dla delegate |
| `adapter` | moduł packa (`uriscreen`, `uristepper`, `external`) |
| `uri_host` | zamiana hosta w URI przed delegate |
| `options` | timeout, qos, ssh user/host |

## Ładowanie

```bash
export URISYS_RESOLVER_CONFIG=path/to/urisys.runtime.yaml
urisys markpact run process.markpact.md --as flow --approve --dry-run
```

Implementacja: `uri_router.resolver.load_resolver_into_runtime`.  
Walidacja struktury: `uri_router.resolver.validate_resolver` (v1).  
Strukturalne issue codes: `validate_resolver_issues()` → RR001–RR013 (patrz `urirouter/docs/REFACTORING.md`).

## Generowanie

```bash
urisys markpact export-platform markpact-contracts/packs/machine-cycle-process.markpact.md \
  --out .markpact/machine_cycle_process/generated \
  --platforms linux,server,esp32
```

Wygenerowany stub **wymaga review** przed produkcją — `targets` są heurystyką z authorities w flow.

Powiązane: [`URI-TRANSPORT-BINDING`](../../markpact-contracts/packs/examples/uri-transport-binding.stepper.yaml) (transport envelope).
