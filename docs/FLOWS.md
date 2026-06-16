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
expect:                          # opcjonalny kontrakt efektu (patrz niżej)
  screen_changed: true
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
| `urisys-node/flows/` | 4 | Bootstrap PyPI, remote probe, screen, kvm demo |
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
| lab-10 test (transport) | `flow_ok && steps_ok == steps_total > 0` |
| lab-10 test (**efekt**) | + spełniony kontrakt `expect:` (jeśli zadeklarowany) |

Poziomy 1–4 sprawdzają tylko, że każde URI zwróciło `ok:true` (sukces *transportowy*).
To nie wykrywa flow, które „przeszło", ale nie osiągnęło zamierzonego **efektu**
(np. GUI bez zmiany ekranu, ślepy klik fallback). Od tego jest `expect:`.

## Kontrakt efektu — `expect:`

Opcjonalny blok top-level, w którym flow deklaruje *weryfikowalny* skutek swojego
działania. Asercjonuje go `scripts/run_test_sessions.py` (sesja `lab-10-flows`);
executor flow (`uri2flow`) ten klucz **ignoruje**, więc nie wpływa na wykonanie.

**Opt-in:** flow bez `expect:` zachowuje dotychczasowe zachowanie (tylko transport).
Gdy `expect:` jest obecny, jego złamanie ustawia flow na `fail` z czytelnym `detail`.

| Klucz | Typ | Znaczenie |
|-------|-----|-----------|
| `screen_changed` | bool | Screenshot po flow różni się od baseline (`true`) / pozostaje bez zmian (`false`) |
| `screen_changed_since_previous` | bool | Screenshot różni się od poprzedniego flow (np. nawigacja Chromium) |
| `opened_url_contains` | str | Krok `browser://…/open` musi zwrócić URL zawierający podciąg |
| `ocr_contains` | list[str] | Każdy podciąg musi wystąpić w tekście OCR któregoś kroku |
| `min_vision_confidence` | float | Przynajmniej jedno wywołanie LLM-vision musi osiągnąć ≥ próg (inaczej klik jest „na ślepo") |

```yaml
# flow GUI musi widocznie zmienić pulpit
expect:
  screen_changed: true

# realne wypełnienie formularza — musi trafić w cel, nie kliknąć fallback
expect:
  ocr_contains: ["Name", "TellMesh"]
  min_vision_confidence: 0.3
```

Złamane kontrakty trafiają też do analizy zbiorczej (`analysis.md`) przez
`session_report.py::check_declared_expectations`. Dla flow **bez** `expect:`
analizator stosuje heurystyki fallback (GUI==baseline, martwy vision).

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
