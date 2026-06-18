# Refaktoryzacja TellMesh URI (2026-06)

Dokument opisuje **docelowy podział warstw** po refaktoryzacji urirouter / uricore / urisys oraz **stan lokalny** implementacji (bez wymogu push na GitHub).

## Model warstw

```text
uricore      = mały kernel wykonawczy URI (registry, policy, local handlers, edge Runtime)
uri_router   = resolver + transport + placement (HTTP/MQTT/SSH delegate)
urisys       = CLI, Markpact, materializacja, dev/lab/CI
uri* packi   = capability + handlery + manifesty — bez routingu
```

Szerszy kontekst: [`ECOSYSTEM.md`](ECOSYSTEM.md), [`PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md).

## Sprinty i stan

| Sprint | Zakres | Status |
|--------|--------|--------|
| 0 | Golden snapshots `tests/golden/` | ✅ 3 kontrakty referencyjne |
| 1 | `urirouter`: models, transports/, policy/, resolver/ | ✅ 24 testy |
| 2 | `uricore`: `edge/call/` (pipeline, resolver_hook), `edge/flow/` | ✅ 52 testy |
| 3 | `urisys/markpact/`: compile, analyze, materialize | ✅ |
| 3b | Analyzer rule engine MP001–MP010, run modes (strategy) | ✅ |
| 4 | `urisys/cli/` — rejestr komend | ✅ |
| 5 | `urisys_lab/` — sesje lab, lenovo | ✅ |
| 6 | Pack conformance matrix | ✅ analyze (10 packs) + process dry-run |
| 7 | `markpact/models`, `flows`, `profile` — wyniesienie z `managers/` | ✅ shims w `managers/` |
| 8 | `urisys_lab/` → `urisys-automation-lab` | ✅ pakiet `urisys_lab` w `src/` |
| 8b | `contract_gen`, `pack_gen` → `urisys-dev` | ✅ shims w `managers/` |
| 9 | `urirouter` Sprint 0–5: schema rules, target selector, MQTT split, shell rules | ✅ patrz `urirouter/docs/REFACTORING.md` |
| 10 | `urirouter` Sprint 10: http_endpoint, loader validate, SH007, contract matrix | ✅ |
| 11 | `urirouter` SH004–SH006/SH008/SH010 + RR lint w `analyze_markpact` | ✅ |
| 12 | `urisys markpact analyze --json` — stabilny kontrakt MP + RR | ✅ |
| 13 | Capability dry-run conformance matrix (10 packs) | ✅ |

## urirouter (`tellmesh/urirouter`)

```
src/uri_router/
├── models.py              # ResolvedTarget, TransportRequest/Response
├── router.py              # UriRouter facade
├── envelope.py
├── transport.py           # shim → transports/
├── transports/
│   ├── registry.py, base.py
│   ├── http.py, ssh.py, unsupported.py, planned.py
│   ├── http_endpoint.py     # normalize_base_url, join_uri_call_path
│   ├── mqtt.py            # MqttAdapter facade
│   ├── mqtt_client.py, mqtt_request_reply.py, mqtt_topics.py
├── policy/
│   ├── limits.py          # operation payload limits
│   ├── shell.py           # facade
│   ├── shell_rules.py     # SH002/SH003
│   ├── allowlist.py, violations.py
└── resolver/
    ├── loader.py, aliases.py, engine.py
    ├── schema.py          # validate_resolver facade
    ├── schema_rules.py    # RR001–RR013 rule engine
    ├── issues.py          # ResolverIssue
    ├── targets.py, target_selector.py
```

**Testy:** `cd urirouter && python -m pytest tests/ -q` → **64 passed** (1 skipped)

Szczegóły issue codes RR/SH: [`urirouter/docs/REFACTORING.md`](../../urirouter/docs/REFACTORING.md)

## uricontrol (`tellmesh/uricontrol`)

```
uri_control/edge/
├── runtime.py             # Runtime.call() → RuntimeCallPipeline
├── call/
│   ├── pipeline.py
│   └── resolver_hook.py
├── flow/
│   ├── loader.py
│   ├── steps.py
│   └── runner.py          # FlowRunner + run_flow()
├── flow_refs.py, flow_expect.py, flow_artifacts.py  # sibling modules (plan: merge)
└── http.py, compose.py, manifest.py, …
```

**Uwaga:** `runtime.py` nadal importuje `uri_router.policy` (limity operacji, shell) — to zamierzone do czasu pełnego odcięcia policy od edge.

**Testy:** `cd uricore && python -m pytest tests/ -q` → **52 passed**

## urisys — pakiet `markpact/`

```
src/urisys/markpact/
├── blocks.py, pack.py, compiler.py, manifest.py, cache.py
├── models.py              # MarkpactBlock, CompiledMarkpact, MarkpactError
├── flows.py               # extract_flows, classify_flow, flow_uris
├── profile.py             # LintIssue, declared_schemes, lint_markpact
├── analyzer/
│   ├── report.py          # analyze_markpact()
│   ├── lint.py            # run_lint() orchestrator
│   ├── context.py
│   └── rules/
│       ├── capabilities.py   # MP001–MP005
│       ├── schemes.py        # MP006
│       ├── flows.py          # MP007–MP008
│       └── pack.py           # MP009–MP010
├── run/
│   ├── config.py, context.py, runtime_build.py
│   └── modes/               # adapter, pack, interface, service, flow
├── platform_export.py       # generated/{linux,server,esp32}/
└── …
```

**Fasady w `managers/`** (cienkie, kompatybilność):

| Plik | Rola |
|------|------|
| `markpact_manager.py` | deleguje do `markpact.*` |
| `markpact_run.py` | re-export `markpact.run` |
| `platform_export.py` | re-export `markpact.platform_export` |
| `markpact_profile.py` | re-export `markpact.profile` |
| `markpact_models.py` | re-export `markpact.models` |
| `markpact_flows.py` | re-export `markpact.flows` |

## urisys — CLI

```
src/urisys/cli/
├── main.py, parser.py, helpers.py, errors.py, protocol.py  # CliCommand Protocol
└── commands/   # markpact, runtime, node, setup
```

Skrypty w `scripts/` są shimami do `urisys_lab` (pakiet w `urisys-automation-lab`).

## urisys-automation-lab — `urisys_lab`

```
urisys-automation-lab/src/urisys_lab/
├── core.py, paths.py
├── lenovo/          # remote session runner
└── sessions/        # Docker/RDP test sessions, expectations
```

Instalacja dev (tellmesh workspace):

```bash
pip install -e ../urisys-automation-lab --no-deps   # lub urisys[lab]
export PYTHONPATH=../urisys-automation-lab/src:$PYTHONPATH
```

Entry points: `urisys-test-sessions`, `urisys-lenovo-session`

## urisys-dev — generatory Markpact

```
urisys-dev/src/urisys_dev/
├── contract_gen.py    # manifest → UriContract, drift check
├── pack_gen.py        # manifest → self-contained UriPack Markpact
└── paths.py           # tellmesh_root()
```

Shims w `urisys/managers/contract_gen.py` i `markpact_pack_gen.py` re-eksportują z `urisys_dev`.

`paths.py` zakotwicza:
- `LAB_ROOT` → `urisys-automation-lab/`
- `URISYS_ROOT` → `tellmesh/urisys/`
- `TELLMESH_ROOT` → `tellmesh/`

## Reguły analyze (v1alpha)

Szczegóły semantyczne: [`MARKPACT-PROFILE.md`](MARKPACT-PROFILE.md).

| Kod | Severity | Moduł | Opis |
|-----|----------|-------|------|
| MP001 | warning | `rules/capabilities.py` | `operation` bez namespace |
| MP002 | error | `rules/capabilities.py` | URI `/query/` vs `kind` |
| MP003 | error | `rules/capabilities.py` | URI `/command/` vs `kind` |
| MP004 | error | `rules/capabilities.py` | command + side_effects + approval:not_required |
| MP005 | error | `rules/capabilities.py` | process handler ≠ `urisys://flow/<id>` |
| MP006 | error | `rules/schemes.py` | undeclared scheme w flow |
| MP007 | warning | `rules/flows.py` | process flow bez `expect:` |
| MP008 | warning | `rules/flows.py` | implicit `image/latest` |
| MP009 | warning | `rules/pack.py` | process bez `requires.schemes` |
| MP010 | warning | `rules/pack.py` | `requires.capabilities` bez kropki |

## Testy (dev workspace)

```bash
export TELLMESH_ROOT=~/github/tellmesh
export PYTHONPATH=$TELLMESH_ROOT/uricore/core/python:$TELLMESH_ROOT/urirouter/src:$TELLMESH_ROOT/urisys/src

cd $TELLMESH_ROOT/urirouter  && python -m pytest tests/ -q
cd $TELLMESH_ROOT/uricore     && python -m pytest tests/ -q
cd $TELLMESH_ROOT/urisys      && bash scripts/run-markpact-ci.sh
cd $TELLMESH_ROOT/urisys      && python -m pytest tests/test_golden_analyze.py tests/test_markpact_analyzer_rules.py -q
```

| Suite | Oczekiwany wynik |
|-------|------------------|
| urirouter | 64 passed (1 skipped) |
| uricore | 53 passed |
| markpact-ci | 109 passed |
| golden analyze | 3 passed |
| capability conformance | 10 passed |
| urisys pełny | 147+ passed (1 znany flaky: `test_all_skips_uninstalled_packs` — PyPI wheel) |

## Pozostałe (backlog)

### uri_router (Sprint 13+)

- Pełna implementacja websocket, nats, serial, usb (dziś: `transport_planned` stub)

### urisys / uricore

- Pełna implementacja websocket, nats, serial, usb w urirouter
- `scripts/generate_pack_markpacts.py` — opcjonalnie przenieść do `urisys-dev`
- `urisys markpact analyze --json` — użyj w CI zamiast pełnego raportu (format `urisys.markpact.analyze-v1`)
