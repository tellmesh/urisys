# URI flows w urisys

## Format compact (`*.uri.flow.yaml`)

```yaml
flow:
  id: flow-id
  description: Human-readable goal
defaults:
  approved: true
  dry_run: false
do:
  - uri://path                    # krok bez payload
  - uri://path:                   # krok z payload
      key: value
  - id: step_b
    uri: other://path
    after: step_a                # jawna zależność
    if: step_a.ok == false       # warunek (uri3; lab: TODO)
```

## Gdzie są flow w repo

| Katalog | Liczba | Użycie |
|---------|--------|--------|
| `urisys-automation-lab/flows/` | 10 | Lab E2E (`lab-10-flows`) |
| `urirdp-docker/flows/` | 2 | RDP smoke |
| `urikvm-docker/flows/` | 1 | KVM click |
| `uribrowser-docker/flows/` | 1 | Browser demo |
| `urienv-docker/flows/` | 2 | Env checks |
| `uristepper-docker/flows/` | 2 | Stepper safety |
| `urisys-node/flows/` | 2 | Screen capture slave |
| `flows/` | 1 | `device-maintenance` (urisys CLI) |

## Trzy sposoby wykonania

### 1. urisys CLI (sekwencja `do:`)

```bash
urisys --packs docker,systemd flow flows/device-maintenance.uri.flow.yaml --approve --dry-run
```

- `FlowController` — **liniowa** lista `do:`, bez `after`/`id`
- Przerwanie przy pierwszym `ok: false` (chyba że `continue_on_error` w defaults)

### 2. automation-lab `POST /uri/flow`

Implementacja: `urisys-automation-lab/server/flow_runner.py` (uri2flow expand + uri3 graph runner + `LabCallAdapter`).

```bash
curl -X POST http://127.0.0.1:8099/uri/flow \
  -H 'Content-Type: application/json' \
  -d '{"path":"/opt/lab/flows/06_terminal_htop_tui.uri.flow.yaml","context":{"approved":true,"allow_real":true,"dry_run":false,"display":":10","xauthority":"/home/urisys/.Xauthority"}}'
```

- `uri2flow.expand_flow()` — compact YAML → workflow graph
- `uri3.graph.run_workflow_node()` — topo-order, warunki `if:`, zależności
- `LabCallAdapter` — sync HTTP przez lab gateway / forward do urirdp

### 3. uri2flow + uri3 (pełny executor)

```bash
uri2flow expand urisys-automation-lab/flows/10_full_maintenance_rdp.uri.flow.yaml -o /tmp/graph.yaml
uri3 run-workflow /tmp/graph.yaml --approve
```

- Warunki `if: step.ok == false`
- `step_outputs` dla assertion adapterów
- Walidacja cykli w grafie

## Zależności między krokami

| Mechanizm | Warstwa | Opis |
|-----------|---------|------|
| Kolejność w `do:` | Wszystkie | Domyślna sekwencja |
| `after:` / `depends_on` | uri2flow, flow_runner, uri3 | Jawny DAG |
| `if:` | uri3 | Gałąź warunkowa |
| `latest.png`, `runtime.state` | Handlery urirdp | Implicit data coupling |
| `context` HTTP | Lab/urirdp | display, xauthority, approved |

**Brak** automatycznego `${step_id.result}` w compact flow (uri3 ma `resolve_ref` w adapterach).

## Walidacja sukcesu

| Poziom | Kryterium |
|--------|-----------|
| Handler | `result.ok`, `exit_code == 0` |
| Edge `_result_ok` | Propagacja z handler result |
| flow_runner `_step_ok` | + brak dry_run w real mode |
| lab-10 test | `flow_ok && steps_ok == steps_total > 0` |

## Walidacja statyczna

```bash
cd urisys-automation-lab
bash scripts/validate-flows.sh   # YAML; opcjonalnie uri2flow expand
```

## Test E2E (10 flow)

```bash
cd urisys
python3 scripts/run_test_sessions.py --sessions lab-10-flows
# → output/test-sessions/<ts>/lab-10-flows/responses/*.json
```

Opis flow 01–10: [`urisys-automation-lab/docs/10_AUTOMATIONS.md`](../urisys-automation-lab/docs/10_AUTOMATIONS.md).
