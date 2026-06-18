# urisys

URI control system managers/controllers over separate uri* capability packs.

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `urisys`
- **version**: `0.1.66`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(3), app.doql.less, goal.yaml, .env.example, project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: urisys;
  version: 0.1.66;
}

dependencies {
  runtime: "PyYAML>=6.0, uricore>=0.1.8, urirouter>=0.1.0";
  dev: "pytest>=8.0, uricore, uribrowser, uridocker, goal>=2.1.0, costs>=0.1.20";
  lab: uri2flow>=0.1.2;
  real: "mss>=9.0, Pillow>=10.0, pyautogui>=0.9.54, pytesseract>=0.3.10, litellm>=1.40";
  kvm: "urikvm[real]>=0.1.0, urihim[real]>=0.1.0, uriocr[real]>=0.1.0, urillm[vision]>=0.1.0";
  discovery: zeroconf>=0.131.0;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="urisys"] {
  entry: urisys.bootstrap:main;
}

integration[name="github"] {
  type: scm;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_URI_MODEL, LLM_URI_BASE_URL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK, URISYS_URICORE_GITHUB_OWNER, URISYS_URICORE_VERSION, URISYS_URICORE_WHEEL_URL, URISYS_MIN_VERSION, URISYS_INIT_PROFILE, WAYLAND_DISPLAY, URISYS_URIROUTER_GITHUB_OWNER, URISYS_URIROUTER_VERSION, URISYS_URIROUTER_WHEEL_URL, URISYS_NODE_GITHUB_OWNER, URISYS_NODE_VERSION, URISYS_NODE_WHEEL_URL, URISYS_NODE_PIP_SPEC, URISYS_EXAMPLES_ROOT, URISYS_NODE_HOST_PORT, LENOVO, URISYS_LENOVO_ENDPOINT, URISYS_ROUTE_MAP, URISYS_NODE_HOST, URISYS_NODE_PORT, URISYS_NODE_CONFIG, TELLMESH_ROOT, URISYS_RESOLVER_CONFIG;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, LLM_URI_BASE_URL, LLM_URI_MODEL, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES, PIP_DISABLE_PIP_VERSION_CHECK;
  runtime_llm: OPENROUTER_API_KEY;
  runtime_pfix: PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
}
```

## Interfaces

### CLI Entry Points

- `urisys`

### testql Scenarios

#### `testql-scenarios/generated-api-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-smoke.testql.toon.yaml
# SCENARIO: Auto-generated API Smoke Tests
# TYPE: api
# GENERATED: true
# DETECTORS: ConfigEndpointDetector

CONFIG[5]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 10000
  retry_count, 3
  retry_backoff_ms, 1000
  detected_frameworks, ConfigEndpointDetector

# Wait for service to be ready
WAIT 1000

# Health check
API GET /api/health 200
ASSERT_STATUS 200

# REST API Endpoints (1 unique)
API[1]{method, endpoint, expected_status}:
  GET, /, 200

# Capture useful values from responses for subsequent tests
# CAPTURE request_id FROM 'headers.x-request-id'
# CAPTURE session_token FROM 'body.token'

ASSERT[2]{field, operator, expected}:
  _status, <, 500
  _status, >=, 200

# Conditional flow for error handling
FLOW[2]{condition, action}:
  _status >= 500, LOG 'Server error detected'
  _status == 429, WAIT 2000  # Rate limit - wait and retry


# Summary by Framework:
#   docker: 3 endpoints
```

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m urisys
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m urisys --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m urisys --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m urisys --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 14 assertions from pytest
ASSERT[14]{field, operator, expected}:
  result.operation, ==, "open_page"
  result.operation, ==, "open_page"
  result.result.url, ==, "https://example.com"
  result.error, ==, "Approval required for side-effect operation."
  store.read_all()[-1].event_type, ==, "PolicyDenied"
  result.result.url, ==, "https://example.com"
  store.read_all()[-1].event_type, ==, "browser.v1.PageOpenedEvent"
  result.operation, ==, "open_page"
  result.operation, ==, "open_page"
  result.result.url, ==, "https://example.com"
  result.error, ==, "Approval required for side-effect operation."
  store.read_all()[-1].event_type, ==, "PolicyDenied"
  result.result.url, ==, "https://example.com"
  store.read_all()[-1].event_type, ==, "browser.v1.PageOpenedEvent"
```

## Configuration

```yaml
project:
  name: urisys
  version: 0.1.66
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
PyYAML>=6.0
uricore>=0.1.8
urirouter>=0.1.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0
uricore
uribrowser
uridocker
goal>=2.1.0
costs>=0.1.20
```

## Deployment

```bash markpact:run
pip install urisys

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PIP_DISABLE_PIP_VERSION_CHECK` | `1` | Quiet pip in venv/scripts (suppress "new release of pip" notices) |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`urisys`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/cryptography/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# urisys | 210f 17668L | python:159,shell:49,less:1,javascript:1 | 2026-06-18
# stats: 657 func | 46 cls | 210 mod | CC̄=4.8 | critical:68 | cycles:0
# alerts[5]: CC _render=14; CC check_drift=14; CC _repo_pyproject=14; CC summarize_event_records=14; CC load_event_records=14
# hotspots[5]: main fan=33; analyze_run fan=23; session_lab_10_flows fan=22; session_lab_10_flows fan=22; session_urirdp_real_docker fan=22
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[210]:
  app.doql.less,49
  examples/frontend/app.js,22
  examples/markpact/browser-call.sh,13
  examples/markpact/showcase-run-flow.sh,30
  examples/shell/call-uri.sh,7
  examples/shell/server-curl.sh,9
  local-lab/scripts/01-validate-markpact.sh,25
  local-lab/scripts/02-build-publish.sh,133
  local-lab/scripts/03-resolve-run.sh,17
  local-lab/scripts/04-smoke.sh,36
  local-lab/scripts/05-resolve-from-url.sh,24
  local-lab/scripts/06-register-release.sh,63
  local-lab/scripts/install-urisys.sh,21
  local-lab/scripts/run-all.sh,26
  project.sh,63
  scripts/analyze-legacy-contract-packs.sh,44
  scripts/analyze-process-markpacts.sh,40
  scripts/analyze-thin-markpacts.sh,49
  scripts/bootstrap-lenovo-local.sh,58
  scripts/check_contract_drift.py,106
  scripts/ci-checkout-siblings.sh,57
  scripts/ci-install-siblings.sh,29
  scripts/deploy-lenovo-node.sh,131
  scripts/generate_pack_markpacts.py,372
  scripts/generate_showcase_markpacts.py,7
  scripts/install-kvm-packs-editable.sh,14
  scripts/lenovo-node-session.sh,74
  scripts/lenovo_remote_session.py,8
  scripts/marksync-materialize.sh,32
  scripts/materialize-all-showcases.sh,54
  scripts/office-simulate-loop.py,147
  scripts/pack_registry.py,261
  scripts/pack_sync.py,372
  scripts/paths.sh,70
  scripts/publish-pypi-packs.sh,54
  scripts/publish-tellmesh-wheels.sh,84
  scripts/publish-urisys-node-release.sh,20
  scripts/remote-node-smoke.sh,100
  scripts/report/__init__.py,62
  scripts/report/cli.py,42
  scripts/report/events.py,139
  scripts/report/lab_checks.py,188
  scripts/report/models.py,87
  scripts/report/run_analysis.py,130
  scripts/report/run_markdown.py,43
  scripts/report/session.py,125
  scripts/report/session_io.py,20
  scripts/report/session_markdown.py,121
  scripts/report/util.py,22
  scripts/run-email-mailpit-e2e.sh,135
  scripts/run-full-regression.sh,27
  scripts/run-lab-e2e.sh,15
  scripts/run-lab-nightly.sh,17
  scripts/run-lab-unit-ci.sh,22
  scripts/run-lenovo-office-linkedin.sh,119
  scripts/run-markpact-ci.sh,62
  scripts/run-nl-log-smoke.sh,44
  scripts/run-office-simulate-e2e.sh,131
  scripts/run-office-simulate-lenovo.sh,183
  scripts/run-office-writer-e2e.sh,114
  scripts/run-smoke-all.sh,25
  scripts/run-urisys-node-docker-e2e.sh,164
  scripts/run-urisys-node-docker-session.sh,7
  scripts/run_test_sessions.py,8
  scripts/scan-browser-sessions.py,209
  scripts/session_core.py,5
  scripts/session_report.py,50
  scripts/sync-vendored-pack.sh,39
  scripts/test-goal.sh,12
  scripts/test-python-matrix.sh,59
  scripts/test_sessions/__init__.py,6
  scripts/test_sessions/expectations.py,154
  scripts/test_sessions/lab_flows.py,321
  scripts/test_sessions/lab_rdp.py,181
  scripts/test_sessions/util.py,202
  scripts/update-ecosystem-readmes.py,164
  scripts/validate-all-markpacts.sh,66
  scripts/validate-pypi-metadata.sh,63
  src/urisys/__init__.py,4
  src/urisys/bootstrap.py,117
  src/urisys/cli/__init__.py,11
  src/urisys/cli/__main__.py,5
  src/urisys/cli/commands/__init__.py,21
  src/urisys/cli/commands/markpact.py,208
  src/urisys/cli/commands/node.py,35
  src/urisys/cli/commands/runtime.py,52
  src/urisys/cli/commands/setup.py,32
  src/urisys/cli/errors.py,33
  src/urisys/cli/helpers.py,29
  src/urisys/cli/main.py,18
  src/urisys/cli/parser.py,214
  src/urisys/cli/protocol.py,11
  src/urisys/controllers/__init__.py,1
  src/urisys/controllers/flow_controller.py,34
  src/urisys/controllers/server_controller.py,20
  src/urisys/controllers/uri_controller.py,34
  src/urisys/defaults.py,41
  src/urisys/doctor.py,294
  src/urisys/flow.py,26
  src/urisys/http_server.py,77
  src/urisys/init_setup.py,258
  src/urisys/managers/__init__.py,1
  src/urisys/managers/bridge_manager.py,15
  src/urisys/managers/contract_gen.py,190
  src/urisys/managers/event_manager.py,14
  src/urisys/managers/markpact_flows.py,134
  src/urisys/managers/markpact_manager.py,73
  src/urisys/managers/markpact_materialize.py,70
  src/urisys/managers/markpact_models.py,103
  src/urisys/managers/markpact_pack_deps.py,190
  src/urisys/managers/markpact_pack_gen.py,243
  src/urisys/managers/markpact_profile.py,270
  src/urisys/managers/markpact_run.py,16
  src/urisys/managers/markpact_run_flow.py,161
  src/urisys/managers/markpact_validation.py,157
  src/urisys/managers/pack_manager.py,191
  src/urisys/managers/platform_export.py,14
  src/urisys/managers/policy_manager.py,19
  src/urisys/managers/route_manager.py,24
  src/urisys/managers/runtime_manager.py,31
  src/urisys/managers/source_manager.py,219
  src/urisys/markpact/__init__.py,25
  src/urisys/markpact/analyzer/__init__.py,5
  src/urisys/markpact/analyzer/context.py,16
  src/urisys/markpact/analyzer/lint.py,67
  src/urisys/markpact/analyzer/report.py,53
  src/urisys/markpact/analyzer/rules/__init__.py,28
  src/urisys/markpact/analyzer/rules/base.py,18
  src/urisys/markpact/analyzer/rules/capabilities.py,108
  src/urisys/markpact/analyzer/rules/flows.py,47
  src/urisys/markpact/analyzer/rules/pack.py,46
  src/urisys/markpact/analyzer/rules/schemes.py,20
  src/urisys/markpact/artifacts.py,81
  src/urisys/markpact/blocks.py,64
  src/urisys/markpact/cache.py,119
  src/urisys/markpact/compiler.py,119
  src/urisys/markpact/handlers.py,52
  src/urisys/markpact/manifest.py,128
  src/urisys/markpact/pack.py,55
  src/urisys/markpact/platform_export.py,304
  src/urisys/markpact/run/__init__.py,67
  src/urisys/markpact/run/config.py,26
  src/urisys/markpact/run/context.py,26
  src/urisys/markpact/run/modes/__init__.py,18
  src/urisys/markpact/run/modes/adapter.py,29
  src/urisys/markpact/run/modes/base.py,14
  src/urisys/markpact/run/modes/flow.py,87
  src/urisys/markpact/run/modes/interface.py,29
  src/urisys/markpact/run/modes/pack.py,19
  src/urisys/markpact/run/modes/service.py,25
  src/urisys/markpact/run/runtime_build.py,54
  src/urisys/markpact/tests.py,79
  src/urisys/markpact/validate_pack.py,93
  src/urisys/node_install.py,107
  src/urisys/uricore_install.py,131
  src/urisys/urirouter_install.py,47
  src/urisys_lab/__init__.py,6
  src/urisys_lab/core.py,314
  src/urisys_lab/lenovo/__init__.py,6
  src/urisys_lab/lenovo/cli.py,969
  src/urisys_lab/paths.py,11
  src/urisys_lab/sessions/__init__.py,75
  src/urisys_lab/sessions/cli.py,107
  src/urisys_lab/sessions/expectations.py,154
  src/urisys_lab/sessions/lab_flows.py,321
  src/urisys_lab/sessions/lab_rdp.py,181
  src/urisys_lab/sessions/runners.py,666
  src/urisys_lab/sessions/util.py,198
  tests/conftest.py,54
  tests/pack_import_isolation.py,44
  tests/test_analyze_strict.py,41
  tests/test_bootstrap.py,61
  tests/test_capability_conformance.py,40
  tests/test_contract_gen.py,74
  tests/test_desktop_automation_processes.py,76
  tests/test_doctor.py,29
  tests/test_doctor_uricore.py,27
  tests/test_golden_analyze.py,51
  tests/test_http_server.py,69
  tests/test_init.py,61
  tests/test_kvm_pack_pyprojects.py,71
  tests/test_machine_cycle_process.py,110
  tests/test_markpact.py,105
  tests/test_markpact_analyzer_rules.py,87
  tests/test_markpact_contract_materialize.py,106
  tests/test_markpact_materialize.py,22
  tests/test_markpact_pack_deps.py,33
  tests/test_markpact_profile.py,82
  tests/test_markpact_run.py,98
  tests/test_markpact_run_flow.py,103
  tests/test_markpact_session_isolation.py,63
  tests/test_node_install.py,39
  tests/test_pack_gen.py,83
  tests/test_pack_manager_parse.py,45
  tests/test_pack_manager_sibling.py,39
  tests/test_platform_export.py,64
  tests/test_process_conformance.py,53
  tests/test_pypi_metadata.py,35
  tests/test_python_compat.py,53
  tests/test_run_expectations.py,50
  tests/test_session_core.py,73
  tests/test_session_report_events.py,59
  tests/test_showcase.py,51
  tests/test_source_manager.py,36
  tests/test_uricore_install.py,38
  tests/test_urirouter_install.py,18
  tests/test_urisys.py,65
  tests/test_urisys_flow_handler.py,72
  tests/test_vendored_sync.py,58
  tree.sh,2
D:
  scripts/check_contract_drift.py:
    e: manifest_path,contract_paths,check_pair,_check_spec,main
    manifest_path(spec)
    contract_paths(spec)
    check_pair(manifest;contract)
    _check_spec(name;spec)
    main()
  scripts/generate_pack_markpacts.py:
    e: repo_module_dir,_extra_specs,_scheme,_fill_pattern,_capabilities,_tests,_use_case_flow,_run_block,_default_port,_render,_split_by_scheme,manifest_files,_file_stem,generate_for_spec,_process_spec,main
    repo_module_dir(spec)
    _extra_specs()
    _scheme(uri)
    _fill_pattern(pattern)
    _capabilities(manifest;handlers)
    _tests(caps)
    _use_case_flow(manifest;caps)
    _run_block(scheme;flow_id;uses;port)
    _default_port(scheme)
    _render()
    _split_by_scheme(manifest)
    manifest_files(spec)
    _file_stem(spec;manifest;manifest_path)
    generate_for_spec(spec)
    _process_spec(spec)
    main()
  scripts/generate_showcase_markpacts.py:
  scripts/lenovo_remote_session.py:
  scripts/office-simulate-loop.py:
    e: call_uri,rules_tick,llm_tick,parse_args,main
    call_uri(base;uri;payload;context)
    rules_tick(base;ctx;letter)
    llm_tick(base;ctx;letter)
    parse_args(argv)
    main(argv)
  scripts/pack_registry.py:
    e: _repo,sibling_uv_path,sibling_repo,_pack,pack_specs,sibling_repo_names,all_promoted_packs,PackSpec
    PackSpec:
    _repo(name)
    sibling_uv_path(name)
    sibling_repo(name)
    _pack(name)
    pack_specs()
    sibling_repo_names()
    all_promoted_packs()
  scripts/pack_sync.py:
    e: repo_module_dir,vendored_module_dir,read_version,file_hash,sync_file,sync_to_repo,check_drift,_check_promoted,remove_vendored,_repo_pyproject,init_repo,promote,_validate_packs,_cmd_to_repo,_cmd_promote,_cmd_check,_cmd_init_repo,_cmd_print_uv_sources,main
    repo_module_dir(spec)
    vendored_module_dir(spec)
    read_version(path)
    file_hash(path)
    sync_file(src;dst)
    sync_to_repo(spec)
    check_drift(spec)
    _check_promoted(spec)
    remove_vendored(spec)
    _repo_pyproject(spec)
    init_repo(spec)
    promote(spec)
    _validate_packs(names;specs)
    _cmd_to_repo(names;specs;args)
    _cmd_promote(names;specs;args)
    _cmd_check(names;specs;args)
    _cmd_init_repo(names;specs;args)
    _cmd_print_uv_sources(names;specs;args)
    main(argv)
  scripts/report/__init__.py:
  scripts/report/cli.py:
    e: main
    main()
  scripts/report/events.py:
    e: summarize_event_records,load_event_records,summarize_events,resolve_events_paths,merge_event_summaries
    summarize_event_records(records)
    load_event_records(events_path)
    summarize_events(events_path)
    resolve_events_paths(session_dir)
    merge_event_summaries(paths)
  scripts/report/lab_checks.py:
    e: iter_step_results,_response_to_outcome,load_flow_outcomes,check_declared_expectations,check_gui_no_effect,check_vision_never_decides,_duplicate_recommendation,check_duplicate_screenshots,check_shell_baseline_duplicate,analyze_lab_flows
    iter_step_results(steps)
    _response_to_outcome(resp_path)
    load_flow_outcomes(session_dir)
    check_declared_expectations(outcomes)
    check_gui_no_effect(outcomes)
    check_vision_never_decides(outcomes)
    _duplicate_recommendation(outcome)
    check_duplicate_screenshots(outcomes)
    check_shell_baseline_duplicate(outcomes)
    analyze_lab_flows(session_dir)
  scripts/report/models.py:
    e: StepResult,SessionReport,RunAnalysis,Finding,FlowOutcome
    StepResult:
    SessionReport: passed(0),failed(0)
    RunAnalysis: all_passed(0)
    Finding:
    FlowOutcome: no_visible_effect(0),vision_decided(0)
  scripts/report/run_analysis.py:
    e: _session_row,_findings_for_session,_run_recommendations,analyze_run,write_run_analysis
    _session_row(data;report_path;run_dir)
    _findings_for_session(data)
    _run_recommendations(findings;summary)
    analyze_run(run_dir)
    write_run_analysis(run_dir;analysis)
  scripts/report/run_markdown.py:
    e: render_run_analysis_markdown
    render_run_analysis_markdown(analysis)
  scripts/report/session.py:
    e: _extract_metrics,_resolve_screenshot,_response_to_step_result,infer_steps,collect_artifacts,session_status,session_duration,generate_report
    _extract_metrics(result)
    _resolve_screenshot(data;result)
    _response_to_step_result(path;session_dir)
    infer_steps(session_dir;meta)
    collect_artifacts(session_dir)
    session_status(steps;meta)
    session_duration(meta)
    generate_report(session_dir)
  scripts/report/session_io.py:
    e: write_session_report
    write_session_report(session_dir;report)
  scripts/report/session_markdown.py:
    e: render_session_markdown,_environment_section,_steps_section,_screenshots_section,_events_section,_log_errors_section,_duplicate_screenshots_section,_log_tail_section
    render_session_markdown(report)
    _environment_section(report)
    _steps_section(report)
    _screenshots_section(report)
    _events_section(report)
    _log_errors_section(report)
    _duplicate_screenshots_section(report)
    _log_tail_section(report)
  scripts/report/util.py:
    e: read_json,tail
    read_json(path)
    tail(text;limit)
  scripts/run_test_sessions.py:
  scripts/scan-browser-sessions.py:
    e: _copy_query,scan_chrome_cookies,chrome_profiles,firefox_profiles,discover_browsers,_scan_profiles,_output_json,_output_text,main
    _copy_query(db_path;sql_chrome;sql_firefox)
    scan_chrome_cookies(db_path)
    chrome_profiles(base)
    firefox_profiles(base)
    discover_browsers(home)
    _scan_profiles(args)
    _output_json(report)
    _output_text(report;args)
    main()
  scripts/session_core.py:
  scripts/session_report.py:
  scripts/test_sessions/__init__.py:
  scripts/test_sessions/expectations.py:
    e: flow_expectations,ocr_texts,vision_confidences,_screen_changed,_screen_changed_since_previous,_opened_url_contains,_ocr_contains,_min_vision_confidence,evaluate_expectations
    flow_expectations(flow_path)
    ocr_texts(step_results)
    vision_confidences(step_results)
    _screen_changed(expect)
    _screen_changed_since_previous(expect)
    _opened_url_contains(expect;step_results)
    _ocr_contains(expect;step_results)
    _min_vision_confidence(expect;step_results)
    evaluate_expectations(expect)
  scripts/test_sessions/lab_flows.py:
    e: _lab_bootstrap,_capture_flow_screenshot,_flow_step_detail,_run_single_lab_flow,session_lab_10_flows
    _lab_bootstrap(session_dir)
    _capture_flow_screenshot(session_dir)
    _flow_step_detail()
    _run_single_lab_flow(session_dir)
    session_lab_10_flows(session_dir)
  scripts/test_sessions/lab_rdp.py:
    e: parse_lab_flow,flow_step_context,step_pause,summarize_uri_response,parse_docker_log_errors,prepare_ok_target,capture_rdp_screenshot,capture_rdp_screenshot_wait
    parse_lab_flow(path)
    flow_step_context(defaults;uri)
    step_pause(uri)
    summarize_uri_response(res)
    parse_docker_log_errors(session_dir)
    prepare_ok_target(rdp_port;display;xauth)
    capture_rdp_screenshot(session_dir)
    capture_rdp_screenshot_wait(session_dir)
  scripts/test_sessions/util.py:
    e: run_id,http_json,wait_health,compose_cmd,run_cmd,write_meta,read_meta,finalize_session,docker_logs,copy_container_file,copy_host_screenshot,file_md5,sleep_ports,prepare_urirdp_data
    run_id()
    http_json(method;url;body;timeout)
    wait_health(url;attempts;delay)
    compose_cmd()
    run_cmd(cmd)
    write_meta(session_dir)
    read_meta(path)
    finalize_session(session_dir;started_at;exit_code;steps)
    docker_logs(service;compose_file;cwd;out)
    copy_container_file(container;src;dest)
    copy_host_screenshot(src;session_dir;name)
    file_md5(path)
    sleep_ports()
    prepare_urirdp_data(pkg)
  scripts/update-ecosystem-readmes.py:
    e: build_section,strip_old_section,fix_urisysedge_refs,main
    build_section(rows)
    strip_old_section(text)
    fix_urisysedge_refs(text)
    main()
  src/urisys/__init__.py:
  src/urisys/bootstrap.py:
    e: _print_json,_missing_uricore_payload,_doctor_main,_init_main,main
    _print_json(data)
    _missing_uricore_payload(exc)
    _doctor_main(argv)
    _init_main(argv)
    main(argv)
  src/urisys/cli/__init__.py:
  src/urisys/cli/__main__.py:
  src/urisys/cli/commands/__init__.py:
  src/urisys/cli/commands/markpact.py:
    e: cmd_run_flow,cmd_materialize,cmd_export_platform,cmd_run_markpact,cmd_validate,cmd_compile,cmd_routes,cmd_test,_apply_strict_operations,_apply_strict_profile,cmd_analyze,cmd_pack,cmd_contract,_run_path_command,cmd_markpact
    cmd_run_flow(args;manager;source_manager)
    cmd_materialize(args;manager;source_manager)
    cmd_export_platform(args;source_manager)
    cmd_run_markpact(args;source_manager)
    cmd_validate(manager;local_path)
    cmd_compile(manager;local_path;args)
    cmd_routes(manager;local_path;args)
    cmd_test(manager;local_path;args)
    _apply_strict_operations(result;warnings)
    _apply_strict_profile(result;warnings)
    cmd_analyze(manager;local_path;args)
    cmd_pack(args)
    cmd_contract(args;source_manager)
    _run_path_command(cmd;manager;local_path;args)
    cmd_markpact(args)
  src/urisys/cli/commands/node.py:
    e: cmd_node
    cmd_node(args)
  src/urisys/cli/commands/runtime.py:
    e: cmd_uri,cmd_serve,cmd_flow,cmd_events
    cmd_uri(args)
    cmd_serve(args)
    cmd_flow(args)
    cmd_events(args)
  src/urisys/cli/commands/setup.py:
    e: cmd_doctor,cmd_init
    cmd_doctor(args)
    cmd_init(args)
  src/urisys/cli/errors.py:
    e: handle_cli_error
    handle_cli_error(exc)
  src/urisys/cli/helpers.py:
    e: json_arg,print_json,resolve_markpact_source
    json_arg(value)
    print_json(data)
    resolve_markpact_source(source)
  src/urisys/cli/main.py:
    e: main
    main(argv)
  src/urisys/cli/parser.py:
    e: add_runtime_flags,build_parser
    add_runtime_flags(parser)
    build_parser()
  src/urisys/cli/protocol.py:
    e: CliCommand
    CliCommand: __call__(1)  # CLI subcommand handler: ``(args) -> exit code``.
  src/urisys/controllers/__init__.py:
  src/urisys/controllers/flow_controller.py:
    e: FlowController
    FlowController: __init__(1),run(1),close(0)
  src/urisys/controllers/server_controller.py:
    e: ServerController
    ServerController: __init__(0),serve_forever(0)
  src/urisys/controllers/uri_controller.py:
    e: UriController
    UriController: __init__(1),call(2),explain(1),routes(0),close(0)
  src/urisys/defaults.py:
  src/urisys/doctor.py:
    e: _pkg_version,_parse_version,_version_lt,_check_import,_check_python,_check_cli_path,_check_min_version,_check_wayland_him,_check_uricore_authentic,_check_uricore_dist,run_doctor,Check
    Check:
    _pkg_version(dist_name)
    _parse_version(text)
    _version_lt(left;right)
    _check_import(name;module)
    _check_python()
    _check_cli_path()
    _check_min_version(min_version)
    _check_wayland_him()
    _check_uricore_authentic()
    _check_uricore_dist()
    run_doctor()
  src/urisys/flow.py:
    e: load_flow,iter_steps
    load_flow(path)
    iter_steps(flow)
  src/urisys/http_server.py:
    e: _read_json,create_server,_ControllerRuntime
    _ControllerRuntime: __init__(1),call(3)  # Adapt UriController to the duck-typed runtime the shared tra
    _read_json(handler)
    create_server(host;port)
  src/urisys/init_setup.py:
    e: default_pip_specs,default_node_pip_spec,pip_install_specs,verify_uri_control,profile_env,render_env_shell,write_env_file,_pre_repair_uricore,_build_pip_result,_resolve_error_hint,_run_pip_install,_verify_after_install,_run_doctor_check,_write_profile_env,_check_node_after_install,run_init
    default_pip_specs()
    default_node_pip_spec()
    pip_install_specs(specs)
    verify_uri_control()
    profile_env(profile)
    render_env_shell(env)
    write_env_file(path;env)
    _pre_repair_uricore(install;dry_run;steps;profile)
    _build_pip_result(specs)
    _resolve_error_hint(ok;verify;doctor)
    _run_pip_install(specs;dry_run)
    _verify_after_install(dry_run;install;steps)
    _run_doctor_check(min_version;dry_run;steps)
    _write_profile_env(profile;write_env;dry_run;env_file;steps)
    _check_node_after_install(dry_run;install;pip_result;steps)
    run_init()
  src/urisys/managers/__init__.py:
  src/urisys/managers/bridge_manager.py:
    e: BridgeManager
    BridgeManager: call_http(5)  # Forwards URI envelopes to another URI server.
  src/urisys/managers/contract_gen.py:
    e: load_manifest,normalize_version,contract_id,_routes,_entry,manifest_to_contract,render_contract_markpact,load_contract_block,_by_pattern,_diff_scheme_and_metadata,_diff_section,_diff_uses,diff_manifest_contract
    load_manifest(path)
    normalize_version(version)
    contract_id(manifest)
    _routes(manifest)
    _entry(item)
    manifest_to_contract(manifest)
    render_contract_markpact(manifest)
    load_contract_block(path)
    _by_pattern(entries)
    _diff_scheme_and_metadata(expected;contract;issues)
    _diff_section(section;expected;contract;issues)
    _diff_uses(expected;contract;issues)
    diff_manifest_contract(manifest;contract)
  src/urisys/managers/event_manager.py:
    e: EventManager
    EventManager: __init__(1),list_events(0)
  src/urisys/managers/markpact_flows.py:
    e: extract_protos,extract_modules,extract_flows,flow_uris,_scheme,_provider_scheme,classify_flow,declared_uses
    extract_protos(blocks)
    extract_modules(blocks)
    extract_flows(blocks)
    flow_uris(flow_data)
    _scheme(uri)
    _provider_scheme(scheme)
    classify_flow(flow_data)
    declared_uses(pack)
  src/urisys/managers/markpact_manager.py:
    e: MarkpactManager
    MarkpactManager: __init__(1),read_blocks(1),source_hash(1),load_pack_block(1),validate(1),compile(1),analyze(1),manifest_path_for(1),run_tests(1),_build_route(0),_compile_manifest(0)  # Facade over :mod:`urisys.markpact` compile/analyze pipeline.
  src/urisys/managers/markpact_materialize.py:
    e: default_materialize_root,materialize_markpact
    default_materialize_root()
    materialize_markpact(path)
  src/urisys/managers/markpact_models.py:
    e: safe_identifier,parse_meta,scheme_from_uri,source_hash,MarkpactBlock,CompiledMarkpact,MarkpactError
    MarkpactBlock:
    CompiledMarkpact: to_dict(0)
    MarkpactError:  # Raised when a Markpact cannot be parsed, validated or compil
    safe_identifier(value)
    parse_meta(raw)
    scheme_from_uri(uri)
    source_hash(path)
  src/urisys/managers/markpact_pack_deps.py:
    e: tellmesh_root,_is_capability_pack_repo,_register_flat_pack,_is_flat_pack_repo,_discover_pack_modules,_register_existing_pack,_register_sibling_packs,_register_uricore_utils,_register_urioperators,extend_tellmesh_paths,_pack_resolver,ensure_pack_importable,ensure_flow_packs
    tellmesh_root()
    _is_capability_pack_repo(child)
    _register_flat_pack(root;name)
    _is_flat_pack_repo(child)
    _discover_pack_modules(child)
    _register_existing_pack(repo_path;module_name;added;seen_paths)
    _register_sibling_packs(root;added;seen_paths)
    _register_uricore_utils(root;added)
    _register_urioperators(root;added)
    extend_tellmesh_paths()
    _pack_resolver()
    ensure_pack_importable(pack)
    ensure_flow_packs(packs)
  src/urisys/managers/markpact_pack_gen.py:
    e: find_package_dir,_load_manifest,package_schemes,_build_capability,_pack_block,_run_block,_module_blocks,_proto_blocks,_sanitize_docs,_embedded_flows,_resolve_repo_root,generate_pack_markpact
    find_package_dir(target)
    _load_manifest(package_dir)
    package_schemes(manifest)
    _build_capability(item;pkg_name;scheme;handlers)
    _pack_block(manifest;pkg_name;scheme)
    _run_block(scheme;flow_ids;port)
    _module_blocks(package_dir;pkg_name)
    _proto_blocks(repo_root;scheme)
    _sanitize_docs(text)
    _embedded_flows(repo_root;scheme;limit)
    _resolve_repo_root(package_dir;repo_root)
    generate_pack_markpact(target)
  src/urisys/managers/markpact_profile.py:
    e: _issue,_issue_message,declared_schemes,declared_packs,_cap_uri,_step_features,_flow_level_features,_text_pattern_features,_flow_features,_required_features,_validate_scheme_requirements,_validate_undeclared_schemes,_validate_capability_operations,_validate_uri_kind,_validate_command_approval,_validate_process_handler,_validate_capability_uris,_build_flow_profiles,_cross_check_schemes,lint_markpact,LintIssue
    LintIssue:
    _issue(code;severity;message;location)
    _issue_message(issue)
    declared_schemes(pack)
    declared_packs(pack)
    _cap_uri(cap)
    _step_features(steps;features)
    _flow_level_features(flow_data;features)
    _text_pattern_features(text;features)
    _flow_features(flow_data;raw_yaml)
    _required_features(flow_data)
    _validate_scheme_requirements(pack;scheme)
    _validate_undeclared_schemes(errors;undeclared_schemes)
    _validate_capability_operations(capabilities;warnings;issues)
    _validate_uri_kind(uri;kind;op;issues;errors)
    _validate_command_approval(kind;op;uri;cap;issues;errors)
    _validate_process_handler(scheme;op;cap;issues;errors)
    _validate_capability_uris(capabilities;scheme;errors;issues)
    _build_flow_profiles(flows;scheme;warnings;issues)
    _cross_check_schemes(flows;schemes_required;scheme;warnings)
    lint_markpact()
  src/urisys/managers/markpact_run.py:
  src/urisys/managers/markpact_run_flow.py:
    e: split_flow_ref,pick_flow_id,flow_path_for,packs_for_flow,_split_extra,run_markpact_flow
    split_flow_ref(value)
    pick_flow_id(compiled;flow_id)
    flow_path_for(compiled;flow_id)
    packs_for_flow(pack;flow_data)
    _split_extra(value)
    run_markpact_flow(path)
  src/urisys/managers/markpact_validation.py:
    e: _validate_contract_routes,validate_contract,_missing_bundle_imports,validate_bundle,_validate_implementation_capabilities,validate_implementation
    _validate_contract_routes(source_path;data;scheme)
    validate_contract(source_path;data;source_hash)
    _missing_bundle_imports(source_path;imports)
    validate_bundle(source_path;data;source_hash)
    _validate_implementation_capabilities(source_path;capabilities)
    validate_implementation(source_path;data;source_hash)
  src/urisys/managers/pack_manager.py:
    e: _repo_for_package,_sibling_manifest_path,_manifest_is_loadable,PackManager
    PackManager: __init__(1),_split_specs(1),_is_all(1),parse_packs(1),parse_markpacts(1),resolve_package_name(1),_is_markpact_path(1),_is_manifest_path(1),_resolve_importable_manifest(1),_handle_missing_manifest(3),manifest_paths(0),create_registry(0),capabilities(0),close(0),__enter__(0),__exit__(3)  # Loads separate uri* packages, plain manifest.yaml files and 
    _repo_for_package(package_name;root)
    _sibling_manifest_path(package_name)
    _manifest_is_loadable(path)
  src/urisys/managers/platform_export.py:
  src/urisys/managers/policy_manager.py:
    e: PolicyManager
    PolicyManager: build_context(0)  # Placeholder for stronger policies: RBAC, signed approvals, O
  src/urisys/managers/route_manager.py:
    e: RouteManager
    RouteManager: __init__(1),explain(1),list_routes(0)
  src/urisys/managers/runtime_manager.py:
    e: RuntimeManager
    RuntimeManager: __init__(1),create_runtime(0),close(0),__enter__(0),__exit__(3)
  src/urisys/managers/source_manager.py:
    e: SourceError,SourceManager
    SourceError:  # Raised when a Markpact source cannot be resolved.
    SourceManager: __init__(1),is_remote_source(1),resolve(1),fetch(1),_result(2),_cache_dir(1),_http_download(1),_fetch_http(1),_fetch_github_uri(1),_fetch_github_raw(4),_fetch_git(1),_fetch_zip(1)  # Resolve Markpact sources from local paths, HTTP(S), GitHub, 
  src/urisys/markpact/__init__.py:
  src/urisys/markpact/analyzer/__init__.py:
  src/urisys/markpact/analyzer/context.py:
    e: MarkpactLintContext
    MarkpactLintContext:
  src/urisys/markpact/analyzer/lint.py:
    e: _issue_message,run_lint
    _issue_message(issue)
    run_lint()
  src/urisys/markpact/analyzer/report.py:
    e: analyze_markpact
    analyze_markpact(path)
  src/urisys/markpact/analyzer/rules/__init__.py:
  src/urisys/markpact/analyzer/rules/base.py:
    e: cap_uri,MarkpactRule
    MarkpactRule: check(1)
    cap_uri(cap)
  src/urisys/markpact/analyzer/rules/capabilities.py:
    e: MP001NamespacedOperation,MP002QueryKind,MP003CommandKind,MP004CommandApproval,MP005ProcessHandler
    MP001NamespacedOperation: check(1)
    MP002QueryKind: check(1)
    MP003CommandKind: check(1)
    MP004CommandApproval: check(1)
    MP005ProcessHandler: check(1)
  src/urisys/markpact/analyzer/rules/flows.py:
    e: MP007ProcessExpect,MP008ImplicitLatest
    MP007ProcessExpect: check(1)
    MP008ImplicitLatest: check(1)
  src/urisys/markpact/analyzer/rules/pack.py:
    e: MP009ProcessRequiresSchemes,MP010RequiresCapabilitiesNamespaced
    MP009ProcessRequiresSchemes: check(1)
    MP010RequiresCapabilitiesNamespaced: check(1)
  src/urisys/markpact/analyzer/rules/schemes.py:
    e: MP006UndeclaredScheme
    MP006UndeclaredScheme: check(1)
  src/urisys/markpact/artifacts.py:
    e: write_modules,flows_from_cache,protos_from_cache,modules_from_cache,write_flows,write_protos
    write_modules(cache_dir;blocks)
    flows_from_cache(cache_dir;blocks)
    protos_from_cache(cache_dir;blocks)
    modules_from_cache(cache_dir;blocks)
    write_flows(cache_dir;blocks)
    write_protos(cache_dir;blocks)
  src/urisys/markpact/blocks.py:
    e: read_blocks,yaml_blocks,handler_blocks,load_yaml_blocks
    read_blocks(path)
    yaml_blocks(blocks;kind)
    handler_blocks(blocks)
    load_yaml_blocks(blocks;kind)
  src/urisys/markpact/cache.py:
    e: compile_context,compiled_from_cache,write_manifest_flows,write_compile_metadata,ensure_importable
    compile_context(path)
    compiled_from_cache(ctx;blocks)
    write_manifest_flows(manifest_path;flows_dir;flow_ids)
    write_compile_metadata(ctx)
    ensure_importable(cache_dir)
  src/urisys/markpact/compiler.py:
    e: _write_tests_block,_write_docs_block,_existing_path,MarkpactCompiler
    MarkpactCompiler: __init__(1),compile(1)  # Compile one-file Markpacts into cached runtime artifacts.
    _write_tests_block(ctx;blocks)
    _write_docs_block(ctx;blocks)
    _existing_path(p)
  src/urisys/markpact/handlers.py:
    e: handler_id_from_ref,resolve_handler_ref,write_handler_modules
    handler_id_from_ref(ref)
    resolve_handler_ref(handler_ref;operation;module_name;handlers_python;handlers_urisys)
    write_handler_modules(package_dir;blocks)
  src/urisys/markpact/manifest.py:
    e: _resolve_pattern,_validate_scheme,_resolve_operation,_resolve_kind,_build_route_dict,build_route,compile_manifest
    _resolve_pattern(item)
    _validate_scheme(pattern)
    _resolve_operation(item)
    _resolve_kind(item)
    _build_route_dict(pattern;kind;operation;handler_ref;item)
    build_route(item)
    compile_manifest(pack)
  src/urisys/markpact/pack.py:
    e: load_pack_block,package_id,capabilities,scheme_for_pack
    load_pack_block(path)
    package_id(pack;path)
    capabilities(pack)
    scheme_for_pack(pack;caps)
  src/urisys/markpact/platform_export.py:
    e: _resolve_authority,_authorities_from_flow,collect_process_uris,_target_stub,build_resolver_yaml,_esp32_routes_header,_server_compose_snippet,export_platform_artifacts
    _resolve_authority(uri;input_defaults)
    _authorities_from_flow(flow_data)
    collect_process_uris(path)
    _target_stub(authority;platform;schemes)
    build_resolver_yaml()
    _esp32_routes_header(uris;package_id)
    _server_compose_snippet(package_id)
    export_platform_artifacts(path)
  src/urisys/markpact/run/__init__.py:
    e: run_markpact
    run_markpact(path)
  src/urisys/markpact/run/config.py:
    e: read_run_config,load_run_config
    read_run_config(path)
    load_run_config(config_path)
  src/urisys/markpact/run/context.py:
    e: RunContext
    RunContext:
  src/urisys/markpact/run/modes/__init__.py:
  src/urisys/markpact/run/modes/adapter.py:
    e: AdapterMode
    AdapterMode: run(1)
  src/urisys/markpact/run/modes/base.py:
    e: MarkpactRunMode
    MarkpactRunMode: run(1)
  src/urisys/markpact/run/modes/flow.py:
    e: _resolve_flow_ids,_resolve_flow_uses,_build_flow_runtime,FlowMode
    FlowMode: run(1)
    _resolve_flow_ids(compiled;run_cfg)
    _resolve_flow_uses(compiled;ids;path)
    _build_flow_runtime(ctx;flow_uses)
  src/urisys/markpact/run/modes/interface.py:
    e: InterfaceMode
    InterfaceMode: run(1)
  src/urisys/markpact/run/modes/pack.py:
    e: PackMode
    PackMode: run(1)
  src/urisys/markpact/run/modes/service.py:
    e: ServiceMode
    ServiceMode: run(1)
  src/urisys/markpact/run/runtime_build.py:
    e: apply_resolver_config,build_runtime,routes_summary
    apply_resolver_config(rt;config)
    build_runtime(compiled)
    routes_summary(rt)
  src/urisys/markpact/tests.py:
    e: check_expectations,run_markpact_tests,run_tests_for_path
    check_expectations(result;expect)
    run_markpact_tests(compiled)
    run_tests_for_path(path)
  src/urisys/markpact/validate_pack.py:
    e: validate_pack,validate_markpact_file
    validate_pack(source_path;blocks;pack)
    validate_markpact_file(path)
  src/urisys/node_install.py:
    e: github_owner,github_version,wheel_filename,wheel_url,pip_spec,is_importable,pip_run,install_urisys_node,diagnose_urisys_node
    github_owner()
    github_version()
    wheel_filename(version)
    wheel_url(version)
    pip_spec()
    is_importable()
    pip_run(args)
    install_urisys_node()
    diagnose_urisys_node()
  src/urisys/uricore_install.py:
    e: github_owner,github_version,wheel_url,pip_spec,_pkg_version,_module_exists,_dist_top_levels,is_wrong_uricore_installed,diagnose_uricore,pip_run,repair_uricore
    github_owner()
    github_version()
    wheel_url(version)
    pip_spec()
    _pkg_version(dist_name)
    _module_exists(name)
    _dist_top_levels(dist_name)
    is_wrong_uricore_installed()
    diagnose_uricore()
    pip_run(args)
    repair_uricore()
  src/urisys/urirouter_install.py:
    e: github_owner,github_version,wheel_url,pip_spec,_module_exists,diagnose_urirouter
    github_owner()
    github_version()
    wheel_url(version)
    pip_spec()
    _module_exists(name)
    diagnose_urirouter()
  src/urisys_lab/__init__.py:
  src/urisys_lab/core.py:
    e: default_examples_root,resolve_flow_ref,now_iso,host_id,run_id,save_json,_step_ok_http_get,_step_ok_host_restart_and_wait,_step_ok_host_schedule_restart,_step_ok_default,step_ok,image_ext,write_base64_image,extract_images_from_dict,extract_step_screenshots,backfill_session_images,_wheel_version_key,find_wheel_file,wheel_url,_resolve_wheel_name,_apply_wheel_refspec,_resolve_wheel_args,expand_step_wheels
    default_examples_root()
    resolve_flow_ref(ref)
    now_iso()
    host_id()
    run_id(prefix)
    save_json(path;data)
    _step_ok_http_get(result)
    _step_ok_host_restart_and_wait(result)
    _step_ok_host_schedule_restart(result)
    _step_ok_default(result)
    step_ok(result)
    image_ext(mime)
    write_base64_image(b64;dest)
    extract_images_from_dict(obj)
    extract_step_screenshots(step)
    backfill_session_images(session_dir)
    _wheel_version_key(path;prefix)
    find_wheel_file(deploy_dir;prefix)
    wheel_url(wheel_server;wheel_path)
    _resolve_wheel_name(step;payload)
    _apply_wheel_refspec(payload;wheel_name)
    _resolve_wheel_args(payload)
    expand_step_wheels(step)
  src/urisys_lab/lenovo/__init__.py:
  src/urisys_lab/lenovo/cli.py:
    e: load_yaml,http_get,_run_http_get_step,_run_host_sleep_step,_schedule_restart_safely,_poll_health_after_restart,_run_host_restart_and_wait_step,_run_host_schedule_restart_step,_run_host_wait_health_step,_run_uri_call_step,run_step,run_flow,append_log,build_wheels,start_wheel_server,_needs_node_upgrade,_run_upgrade_flow,_md_header,_md_flow_results,_md_step_detail,_md_lessons,write_session_md,resolve_flow_paths,resolve_route_map,load_manifest_session,_check_and_restore_health,_skip_node_down,_maybe_run_node_upgrade,_maybe_run_kvm_upgrade,_maybe_run_playwright_upgrade,_run_flows,_run_extract_images,_ensure_pyyaml,_init_session,_setup_wheels,_check_initial_health,_copy_flow_sources,_build_meta,_collect_step_summaries,_session_result,main
    load_yaml(path)
    http_get(endpoint;path)
    _run_http_get_step(step;out;endpoint)
    _run_host_sleep_step(step;out)
    _schedule_restart_safely(endpoint;route_map)
    _poll_health_after_restart(endpoint)
    _run_host_restart_and_wait_step(step;out)
    _run_host_schedule_restart_step(step;out)
    _run_host_wait_health_step(step;out)
    _run_uri_call_step(step;out)
    run_step(step)
    run_flow(flow_path)
    append_log(path;line)
    build_wheels(deploy_dir)
    start_wheel_server(deploy_dir;host;port)
    _needs_node_upgrade(flow_paths)
    _run_upgrade_flow(upgrade_flow;label)
    _md_header(meta;session_dir)
    _md_flow_results(flow_records)
    _md_step_detail(flow_records)
    _md_lessons(meta;flow_records)
    write_session_md(session_dir;meta;flow_records)
    resolve_flow_paths(manifest_path;explicit)
    resolve_route_map(manifest_path;cli_route_map)
    load_manifest_session(manifest_path)
    _check_and_restore_health(fp)
    _skip_node_down(fp)
    _maybe_run_node_upgrade(fp;flow_paths)
    _maybe_run_kvm_upgrade(fp)
    _maybe_run_playwright_upgrade(fp)
    _run_flows(flow_paths)
    _run_extract_images(extract_images)
    _ensure_pyyaml()
    _init_session(run_id;session_dir_arg)
    _setup_wheels(args;session_cfg)
    _check_initial_health(endpoint)
    _copy_flow_sources(flow_paths;manifest_path;session_dir)
    _build_meta(run_id;session_cfg;node_reachable;args;route_map;examples_root;manifest_path;flow_paths)
    _collect_step_summaries(meta;flow_records)
    _session_result(node_reachable;flow_records;wheel_proc;log_path;session_dir;meta)
    main(argv)
  src/urisys_lab/paths.py:
  src/urisys_lab/sessions/__init__.py:
  src/urisys_lab/sessions/cli.py:
    e: main
    main()
  src/urisys_lab/sessions/expectations.py:
    e: flow_expectations,ocr_texts,vision_confidences,_screen_changed,_screen_changed_since_previous,_opened_url_contains,_ocr_contains,_min_vision_confidence,evaluate_expectations
    flow_expectations(flow_path)
    ocr_texts(step_results)
    vision_confidences(step_results)
    _screen_changed(expect)
    _screen_changed_since_previous(expect)
    _opened_url_contains(expect;step_results)
    _ocr_contains(expect;step_results)
    _min_vision_confidence(expect;step_results)
    evaluate_expectations(expect)
  src/urisys_lab/sessions/lab_flows.py:
    e: _lab_bootstrap,_capture_flow_screenshot,_flow_step_detail,_run_single_lab_flow,session_lab_10_flows
    _lab_bootstrap(session_dir)
    _capture_flow_screenshot(session_dir)
    _flow_step_detail()
    _run_single_lab_flow(session_dir)
    session_lab_10_flows(session_dir)
  src/urisys_lab/sessions/lab_rdp.py:
    e: parse_lab_flow,flow_step_context,step_pause,summarize_uri_response,parse_docker_log_errors,prepare_ok_target,capture_rdp_screenshot,capture_rdp_screenshot_wait
    parse_lab_flow(path)
    flow_step_context(defaults;uri)
    step_pause(uri)
    summarize_uri_response(res)
    parse_docker_log_errors(session_dir)
    prepare_ok_target(rdp_port;display;xauth)
    capture_rdp_screenshot(session_dir)
    capture_rdp_screenshot_wait(session_dir)
  src/urisys_lab/sessions/runners.py:
    e: session_pytest_urirdp,session_pytest_urisys,session_pytest_urisys_node,session_urirdp_mock_docker,_record_health,_bootstrap_rdp,_read_display_env,_call_and_record,_session_compose_up,_record_screenshot_step,_record_ocr_step,_record_click_step,_record_flow_step,session_urirdp_real_docker,session_urirdp_rdp_e2e,session_automation_lab,_monorepo_root,session_urisys_node_docker_gui,session_office_simulate,session_office_simulate_lenovo,session_office_writer,session_email_mailpit
    session_pytest_urirdp(session_dir)
    session_pytest_urisys(session_dir)
    session_pytest_urisys_node(session_dir)
    session_urirdp_mock_docker(session_dir)
    _record_health(session_dir;steps;seq;name;url;attempts)
    _bootstrap_rdp(container;log;steps;raise_on_fail)
    _read_display_env(container)
    _call_and_record(session_dir;steps;seq;name;uri;payload;ctx;timeout;port;step_name)
    _session_compose_up(pkg;log;env;steps)
    _record_screenshot_step(session_dir;steps;seq;port;ctx;container)
    _record_ocr_step(session_dir;steps;seq;port;ctx)
    _record_click_step(session_dir;steps;seq;port;ctx;container)
    _record_flow_step(session_dir;steps;seq;container;display;log)
    session_urirdp_real_docker(session_dir)
    session_urirdp_rdp_e2e(session_dir)
    session_automation_lab(session_dir)
    _monorepo_root()
    session_urisys_node_docker_gui(session_dir)
    session_office_simulate(session_dir)
    session_office_simulate_lenovo(session_dir)
    session_office_writer(session_dir)
    session_email_mailpit(session_dir)
  src/urisys_lab/sessions/util.py:
    e: run_id,http_json,wait_health,compose_cmd,run_cmd,write_meta,read_meta,finalize_session,docker_logs,copy_container_file,copy_host_screenshot,file_md5,sleep_ports,prepare_urirdp_data
    run_id()
    http_json(method;url;body;timeout)
    wait_health(url;attempts;delay)
    compose_cmd()
    run_cmd(cmd)
    write_meta(session_dir)
    read_meta(path)
    finalize_session(session_dir;started_at;exit_code;steps)
    docker_logs(service;compose_file;cwd;out)
    copy_container_file(container;src;dest)
    copy_host_screenshot(src;session_dir;name)
    file_md5(path)
    sleep_ports()
    prepare_urirdp_data(pkg)
  tests/conftest.py:
    e: _tellmesh_root,_ensure_siblings,_cleanup_markpact_embedded_imports
    _tellmesh_root()
    _ensure_siblings()
    _cleanup_markpact_embedded_imports()
  tests/pack_import_isolation.py:
    e: _is_embedded_pack_module,_is_ephemeral_path,reset_embedded_pack_imports
    _is_embedded_pack_module(name)
    _is_ephemeral_path(path)
    reset_embedded_pack_imports()
  tests/test_analyze_strict.py:
    e: _analyze_strict,test_machine_cycle_analyze_strict_passes,test_extend_tellmesh_includes_urioperators
    _analyze_strict(path)
    test_machine_cycle_analyze_strict_passes()
    test_extend_tellmesh_includes_urioperators()
  tests/test_bootstrap.py:
    e: _load_module,test_bootstrap_import_does_not_require_uri_control,test_cli_import_does_not_require_uri_control,test_missing_uricore_payload,test_doctor_subcommand_via_bootstrap
    _load_module(name;path)
    test_bootstrap_import_does_not_require_uri_control()
    test_cli_import_does_not_require_uri_control()
    test_missing_uricore_payload()
    test_doctor_subcommand_via_bootstrap()
  tests/test_capability_conformance.py:
    e: test_capability_pack_analyze_conformance
    test_capability_pack_analyze_conformance(markpact_file;expected_scheme;min_caps)
  tests/test_contract_gen.py:
    e: test_manifest_to_contract_maps_kinds_and_approval,test_generated_contract_validates,test_self_drift_is_clean,test_drift_detected,test_existing_repo_contract_has_no_core_drift
    test_manifest_to_contract_maps_kinds_and_approval()
    test_generated_contract_validates(tmp_path)
    test_self_drift_is_clean()
    test_drift_detected()
    test_existing_repo_contract_has_no_core_drift()
  tests/test_desktop_automation_processes.py:
    e: test_desktop_automation_validates_and_analyzes,test_desktop_automation_embedded_approval_test,test_desktop_gui_flow_dry_run,test_desktop_install_flow_dry_run_with_resolver
    test_desktop_automation_validates_and_analyzes()
    test_desktop_automation_embedded_approval_test(tmp_path)
    test_desktop_gui_flow_dry_run(tmp_path;monkeypatch)
    test_desktop_install_flow_dry_run_with_resolver(tmp_path;monkeypatch)
  tests/test_doctor.py:
    e: test_doctor_ok_in_dev_env,test_doctor_fails_high_min_version,test_doctor_hints_include_node_serve
    test_doctor_ok_in_dev_env()
    test_doctor_fails_high_min_version()
    test_doctor_hints_include_node_serve()
  tests/test_doctor_uricore.py:
    e: test_check_uricore_authentic_fails_on_squatter
    test_check_uricore_authentic_fails_on_squatter()
  tests/test_golden_analyze.py:
    e: _analyze_snapshot,test_analyze_golden_snapshot
    _analyze_snapshot(path)
    test_analyze_golden_snapshot(markpact_name;golden_name)
  tests/test_http_server.py:
    e: _start,_get,test_health_exact_shape_and_cors,test_routes_are_full_dicts_not_flattened,test_options_preflight_204,test_events_endpoint
    _start()
    _get(port;path)
    test_health_exact_shape_and_cors()
    test_routes_are_full_dicts_not_flattened()
    test_options_preflight_204()
    test_events_endpoint()
  tests/test_init.py:
    e: test_init_dry_run_via_bootstrap,test_run_init_skip_pip_writes_env,test_pip_install_failure
    test_init_dry_run_via_bootstrap()
    test_run_init_skip_pip_writes_env(tmp_path)
    test_pip_install_failure()
  tests/test_kvm_pack_pyprojects.py:
    e: _name,_deps,test_uricore_sibling_pyproject,test_each_kvm_pack_has_sibling_pyproject,test_sibling_pack_pyprojects_depend_on_uricore,test_urillm_imports_uri_control_env_not_urikvmedge,test_urisys_root_uv_sources_point_to_siblings,test_vendored_kvm_pack_dirs_removed,test_urikvmedge_promoted_to_sibling
    _name(path)
    _deps(path)
    test_uricore_sibling_pyproject()
    test_each_kvm_pack_has_sibling_pyproject()
    test_sibling_pack_pyprojects_depend_on_uricore()
    test_urillm_imports_uri_control_env_not_urikvmedge()
    test_urisys_root_uv_sources_point_to_siblings()
    test_vendored_kvm_pack_dirs_removed()
    test_urikvmedge_promoted_to_sibling()
  tests/test_machine_cycle_process.py:
    e: test_machine_cycle_process_validates_and_analyzes,test_machine_cycle_compiles_urisys_flow_handler,test_machine_cycle_requires_approval_without_deps,test_machine_cycle_risk_requires_dry_run_and_audit,test_machine_cycle_embedded_markpact_test_policy_only,test_machine_cycle_flow_dry_run_with_tellmesh
    test_machine_cycle_process_validates_and_analyzes()
    test_machine_cycle_compiles_urisys_flow_handler(tmp_path)
    test_machine_cycle_requires_approval_without_deps(tmp_path)
    test_machine_cycle_risk_requires_dry_run_and_audit(tmp_path)
    test_machine_cycle_embedded_markpact_test_policy_only(tmp_path)
    test_machine_cycle_flow_dry_run_with_tellmesh(tmp_path;monkeypatch)
  tests/test_markpact.py:
    e: test_markpact_validate,test_markpact_validate_contract,test_markpact_validate_implementation,test_markpact_validate_bundle,test_markpact_compile_and_call,test_uri_controller_loads_markpact_directly,test_markpact_embedded_tests,test_build_route_shape
    test_markpact_validate()
    test_markpact_validate_contract()
    test_markpact_validate_implementation()
    test_markpact_validate_bundle()
    test_markpact_compile_and_call(tmp_path)
    test_uri_controller_loads_markpact_directly(tmp_path)
    test_markpact_embedded_tests(tmp_path)
    test_build_route_shape()
  tests/test_markpact_analyzer_rules.py:
    e: test_mp001_rule_isolated,test_mp002_rule_isolated,test_mp006_rule_isolated,test_mp009_rule_isolated,test_mp010_rule_isolated
    test_mp001_rule_isolated()
    test_mp002_rule_isolated()
    test_mp006_rule_isolated()
    test_mp009_rule_isolated()
    test_mp010_rule_isolated()
  tests/test_markpact_contract_materialize.py:
    e: test_gen_contract_matches_manifest_no_drift,test_contract_validates_but_does_not_compile,test_thin_pack_materializes_to_markpact_tree,test_thin_pack_routes_via_tellmesh_and_uricore,test_full_pack_embedded_source_runs_without_tellmesh
    test_gen_contract_matches_manifest_no_drift()
    test_contract_validates_but_does_not_compile()
    test_thin_pack_materializes_to_markpact_tree(tmp_path;monkeypatch)
    test_thin_pack_routes_via_tellmesh_and_uricore(tmp_path;monkeypatch)
    test_full_pack_embedded_source_runs_without_tellmesh(tmp_path)
  tests/test_markpact_materialize.py:
    e: test_materialize_unpacks_markpact_tree
    test_materialize_unpacks_markpact_tree(tmp_path)
  tests/test_markpact_pack_deps.py:
    e: test_tellmesh_root_from_env,test_extend_tellmesh_paths_adds_siblings,test_extend_tellmesh_imports_uribrowserdocker
    test_tellmesh_root_from_env(monkeypatch)
    test_extend_tellmesh_paths_adds_siblings(monkeypatch)
    test_extend_tellmesh_imports_uribrowserdocker(monkeypatch)
  tests/test_markpact_profile.py:
    e: test_declared_schemes_from_requires,test_declared_schemes_legacy_flat_uses,test_lint_rejects_query_kind_mismatch,test_lint_emits_mp001_for_flat_operation,test_machine_cycle_analyze_v1alpha_profile,test_desktop_automation_analyze_has_expect_warnings_only
    test_declared_schemes_from_requires()
    test_declared_schemes_legacy_flat_uses()
    test_lint_rejects_query_kind_mismatch()
    test_lint_emits_mp001_for_flat_operation()
    test_machine_cycle_analyze_v1alpha_profile()
    test_desktop_automation_analyze_has_expect_warnings_only()
  tests/test_markpact_run.py:
    e: test_run_pack_mode,test_run_interface_mode,test_run_flow_mode,test_run_flow_fragment,test_run_integration_flow_local_siblings
    test_run_pack_mode(tmp_path;monkeypatch)
    test_run_interface_mode(tmp_path;monkeypatch)
    test_run_flow_mode(tmp_path;monkeypatch)
    test_run_flow_fragment(tmp_path;monkeypatch)
    test_run_integration_flow_local_siblings(tmp_path;monkeypatch)
  tests/test_markpact_run_flow.py:
    e: test_split_flow_ref,test_pick_flow_id_requires_fragment_when_many,test_compile_cache_hit_preserves_flow_ids,test_run_flow_use_case,test_run_flow_via_fragment,test_flow_path_for,test_run_integration_flow_local_siblings
    test_split_flow_ref()
    test_pick_flow_id_requires_fragment_when_many(tmp_path)
    test_compile_cache_hit_preserves_flow_ids(tmp_path)
    test_run_flow_use_case(tmp_path)
    test_run_flow_via_fragment(tmp_path)
    test_flow_path_for(tmp_path)
    test_run_integration_flow_local_siblings(tmp_path;monkeypatch)
  tests/test_markpact_session_isolation.py:
    e: test_embedded_urikvm_does_not_break_integration_flow
    test_embedded_urikvm_does_not_break_integration_flow(tmp_path;monkeypatch)
  tests/test_node_install.py:
    e: test_default_pip_specs_no_git_urls,test_urisys_node_uses_release_wheel,test_urisys_node_wheel_filename_pep427,test_urisys_node_wheel_url_override
    test_default_pip_specs_no_git_urls()
    test_urisys_node_uses_release_wheel()
    test_urisys_node_wheel_filename_pep427()
    test_urisys_node_wheel_url_override()
  tests/test_pack_gen.py:
    e: test_generate_embeds_full_source,test_unpack_and_execute_embedded_handler,test_multi_scheme_requires_scheme_selection,test_run_modes_interface_and_adapter
    test_generate_embeds_full_source(tmp_path)
    test_unpack_and_execute_embedded_handler(tmp_path)
    test_multi_scheme_requires_scheme_selection()
    test_run_modes_interface_and_adapter(tmp_path)
  tests/test_pack_manager_parse.py:
    e: test_parse_packs_default_set,test_parse_packs_explicit_and_none_filter,test_is_all,test_parse_markpacts
    test_parse_packs_default_set()
    test_parse_packs_explicit_and_none_filter()
    test_is_all()
    test_parse_markpacts()
  tests/test_pack_manager_sibling.py:
    e: test_sibling_manifest_path_finds_nested_pack,test_sibling_manifest_path_finds_browser_docker,test_pack_manager_all_loads_sibling_manifests
    test_sibling_manifest_path_finds_nested_pack(monkeypatch)
    test_sibling_manifest_path_finds_browser_docker(monkeypatch)
    test_pack_manager_all_loads_sibling_manifests(monkeypatch)
  tests/test_platform_export.py:
    e: test_collect_process_uris_machine_cycle,test_collect_process_uris_desktop,test_build_resolver_yaml_has_v1_metadata,test_export_platform_artifacts_writes_files
    test_collect_process_uris_machine_cycle()
    test_collect_process_uris_desktop()
    test_build_resolver_yaml_has_v1_metadata()
    test_export_platform_artifacts_writes_files(tmp_path)
  tests/test_process_conformance.py:
    e: test_process_flow_conformance_dry_run
    test_process_flow_conformance_dry_run(markpact_file;flow_id;extra_env;tmp_path;monkeypatch)
  tests/test_pypi_metadata.py:
    e: test_validate_pypi_metadata_script_exists,test_built_wheel_has_no_direct_url_requires_dist,test_pyproject_runtime_deps_have_no_direct_urls
    test_validate_pypi_metadata_script_exists()
    test_built_wheel_has_no_direct_url_requires_dist()
    test_pyproject_runtime_deps_have_no_direct_urls()
  tests/test_python_compat.py:
    e: test_python_version_gate,test_current_python_supported,_FakeVersionInfo
    _FakeVersionInfo: __init__(3),__getitem__(1),__ge__(1),__lt__(1)  # Minimal sys.version_info stand-in for tests.
    test_python_version_gate(monkeypatch;major;minor;expected)
    test_current_python_supported()
  tests/test_run_expectations.py:
    e: test_screen_changed_uses_baseline_not_previous_flow,test_screen_changed_fails_when_equal_baseline,test_ocr_contains_from_pipeline
    test_screen_changed_uses_baseline_not_previous_flow()
    test_screen_changed_fails_when_equal_baseline()
    test_ocr_contains_from_pipeline()
  tests/test_session_core.py:
    e: test_step_ok_variants,test_image_ext,test_write_base64_image_roundtrip,test_extract_step_screenshots_strips_base64,test_extract_handles_nested_shots,test_extract_ignores_non_image_response,test_backfill_session_images
    test_step_ok_variants()
    test_image_ext()
    test_write_base64_image_roundtrip(tmp_path)
    test_extract_step_screenshots_strips_base64(tmp_path)
    test_extract_handles_nested_shots(tmp_path)
    test_extract_ignores_non_image_response(tmp_path)
    test_backfill_session_images(tmp_path)
  tests/test_session_report_events.py:
    e: test_summarize_events_api_json,test_summarize_events_jsonl
    test_summarize_events_api_json(tmp_path)
    test_summarize_events_jsonl(tmp_path)
  tests/test_showcase.py:
    e: test_showcase_validates,test_analyze_classifies_use_case_and_integration,test_compile_extracts_flows_and_protos,test_classify_flow_reports_undeclared_uses,test_declared_uses_strips_scheme_suffix
    test_showcase_validates()
    test_analyze_classifies_use_case_and_integration()
    test_compile_extracts_flows_and_protos(tmp_path)
    test_classify_flow_reports_undeclared_uses()
    test_declared_uses_strips_scheme_suffix()
  tests/test_source_manager.py:
    e: test_fetch_local_file,test_fetch_github_raw
    test_fetch_local_file(tmp_path)
    test_fetch_github_raw(monkeypatch;tmp_path)
  tests/test_uricore_install.py:
    e: test_wheel_url_default,test_wrong_uricore_detected_when_squatter_present,test_not_wrong_when_uri_control_present,test_diagnose_includes_wheel_url
    test_wheel_url_default()
    test_wrong_uricore_detected_when_squatter_present()
    test_not_wrong_when_uri_control_present()
    test_diagnose_includes_wheel_url()
  tests/test_urirouter_install.py:
    e: test_wheel_url_default,test_diagnose_includes_wheel_url
    test_wheel_url_default()
    test_diagnose_includes_wheel_url()
  tests/test_urisys.py:
    e: test_call_browser_open,test_routes_load,test_all_skips_uninstalled_packs,test_explicit_missing_pack_raises_helpful_error
    test_call_browser_open(tmp_path)
    test_routes_load(tmp_path)
    test_all_skips_uninstalled_packs(tmp_path;monkeypatch)
    test_explicit_missing_pack_raises_helpful_error()
  tests/test_urisys_flow_handler.py:
    e: test_process_capability_runs_embedded_flow_via_urisys_handler
    test_process_capability_runs_embedded_flow_via_urisys_handler(tmp_path)
  tests/test_vendored_sync.py:
    e: _run_check,test_pack_sync_script_exists,test_sibling_repos_exist,test_promoted_packs_not_vendored_in_monorepo,test_sibling_repos_have_pyproject,test_no_drift_promoted_packs
    _run_check(packs)
    test_pack_sync_script_exists()
    test_sibling_repos_exist()
    test_promoted_packs_not_vendored_in_monorepo()
    test_sibling_repos_have_pyproject()
    test_no_drift_promoted_packs()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('urisys', '0.1.66', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 49, 'less').
project_file('examples/frontend/app.js', 22, 'javascript').
project_file('examples/markpact/browser-call.sh', 13, 'shell').
project_file('examples/markpact/showcase-run-flow.sh', 30, 'shell').
project_file('examples/shell/call-uri.sh', 7, 'shell').
project_file('examples/shell/server-curl.sh', 9, 'shell').
project_file('local-lab/scripts/01-validate-markpact.sh', 25, 'shell').
project_file('local-lab/scripts/02-build-publish.sh', 133, 'shell').
project_file('local-lab/scripts/03-resolve-run.sh', 17, 'shell').
project_file('local-lab/scripts/04-smoke.sh', 36, 'shell').
project_file('local-lab/scripts/05-resolve-from-url.sh', 24, 'shell').
project_file('local-lab/scripts/06-register-release.sh', 63, 'shell').
project_file('local-lab/scripts/install-urisys.sh', 21, 'shell').
project_file('local-lab/scripts/run-all.sh', 26, 'shell').
project_file('project.sh', 63, 'shell').
project_file('scripts/analyze-legacy-contract-packs.sh', 44, 'shell').
project_file('scripts/analyze-process-markpacts.sh', 40, 'shell').
project_file('scripts/analyze-thin-markpacts.sh', 49, 'shell').
project_file('scripts/bootstrap-lenovo-local.sh', 58, 'shell').
project_file('scripts/check_contract_drift.py', 106, 'python').
project_file('scripts/ci-checkout-siblings.sh', 57, 'shell').
project_file('scripts/ci-install-siblings.sh', 29, 'shell').
project_file('scripts/deploy-lenovo-node.sh', 131, 'shell').
project_file('scripts/generate_pack_markpacts.py', 372, 'python').
project_file('scripts/generate_showcase_markpacts.py', 7, 'python').
project_file('scripts/install-kvm-packs-editable.sh', 14, 'shell').
project_file('scripts/lenovo-node-session.sh', 74, 'shell').
project_file('scripts/lenovo_remote_session.py', 8, 'python').
project_file('scripts/marksync-materialize.sh', 32, 'shell').
project_file('scripts/materialize-all-showcases.sh', 54, 'shell').
project_file('scripts/office-simulate-loop.py', 147, 'python').
project_file('scripts/pack_registry.py', 261, 'python').
project_file('scripts/pack_sync.py', 372, 'python').
project_file('scripts/paths.sh', 70, 'shell').
project_file('scripts/publish-pypi-packs.sh', 54, 'shell').
project_file('scripts/publish-tellmesh-wheels.sh', 84, 'shell').
project_file('scripts/publish-urisys-node-release.sh', 20, 'shell').
project_file('scripts/remote-node-smoke.sh', 100, 'shell').
project_file('scripts/report/__init__.py', 62, 'python').
project_file('scripts/report/cli.py', 42, 'python').
project_file('scripts/report/events.py', 139, 'python').
project_file('scripts/report/lab_checks.py', 188, 'python').
project_file('scripts/report/models.py', 87, 'python').
project_file('scripts/report/run_analysis.py', 130, 'python').
project_file('scripts/report/run_markdown.py', 43, 'python').
project_file('scripts/report/session.py', 125, 'python').
project_file('scripts/report/session_io.py', 20, 'python').
project_file('scripts/report/session_markdown.py', 121, 'python').
project_file('scripts/report/util.py', 22, 'python').
project_file('scripts/run-email-mailpit-e2e.sh', 135, 'shell').
project_file('scripts/run-full-regression.sh', 27, 'shell').
project_file('scripts/run-lab-e2e.sh', 15, 'shell').
project_file('scripts/run-lab-nightly.sh', 17, 'shell').
project_file('scripts/run-lab-unit-ci.sh', 22, 'shell').
project_file('scripts/run-lenovo-office-linkedin.sh', 119, 'shell').
project_file('scripts/run-markpact-ci.sh', 62, 'shell').
project_file('scripts/run-nl-log-smoke.sh', 44, 'shell').
project_file('scripts/run-office-simulate-e2e.sh', 131, 'shell').
project_file('scripts/run-office-simulate-lenovo.sh', 183, 'shell').
project_file('scripts/run-office-writer-e2e.sh', 114, 'shell').
project_file('scripts/run-smoke-all.sh', 25, 'shell').
project_file('scripts/run-urisys-node-docker-e2e.sh', 164, 'shell').
project_file('scripts/run-urisys-node-docker-session.sh', 7, 'shell').
project_file('scripts/run_test_sessions.py', 8, 'python').
project_file('scripts/scan-browser-sessions.py', 209, 'python').
project_file('scripts/session_core.py', 5, 'python').
project_file('scripts/session_report.py', 50, 'python').
project_file('scripts/sync-vendored-pack.sh', 39, 'shell').
project_file('scripts/test-goal.sh', 12, 'shell').
project_file('scripts/test-python-matrix.sh', 59, 'shell').
project_file('scripts/test_sessions/__init__.py', 6, 'python').
project_file('scripts/test_sessions/expectations.py', 154, 'python').
project_file('scripts/test_sessions/lab_flows.py', 321, 'python').
project_file('scripts/test_sessions/lab_rdp.py', 181, 'python').
project_file('scripts/test_sessions/util.py', 202, 'python').
project_file('scripts/update-ecosystem-readmes.py', 164, 'python').
project_file('scripts/validate-all-markpacts.sh', 66, 'shell').
project_file('scripts/validate-pypi-metadata.sh', 63, 'shell').
project_file('src/urisys/__init__.py', 4, 'python').
project_file('src/urisys/bootstrap.py', 117, 'python').
project_file('src/urisys/cli/__init__.py', 11, 'python').
project_file('src/urisys/cli/__main__.py', 5, 'python').
project_file('src/urisys/cli/commands/__init__.py', 21, 'python').
project_file('src/urisys/cli/commands/markpact.py', 208, 'python').
project_file('src/urisys/cli/commands/node.py', 35, 'python').
project_file('src/urisys/cli/commands/runtime.py', 52, 'python').
project_file('src/urisys/cli/commands/setup.py', 32, 'python').
project_file('src/urisys/cli/errors.py', 33, 'python').
project_file('src/urisys/cli/helpers.py', 29, 'python').
project_file('src/urisys/cli/main.py', 18, 'python').
project_file('src/urisys/cli/parser.py', 214, 'python').
project_file('src/urisys/cli/protocol.py', 11, 'python').
project_file('src/urisys/controllers/__init__.py', 1, 'python').
project_file('src/urisys/controllers/flow_controller.py', 34, 'python').
project_file('src/urisys/controllers/server_controller.py', 20, 'python').
project_file('src/urisys/controllers/uri_controller.py', 34, 'python').
project_file('src/urisys/defaults.py', 41, 'python').
project_file('src/urisys/doctor.py', 294, 'python').
project_file('src/urisys/flow.py', 26, 'python').
project_file('src/urisys/http_server.py', 77, 'python').
project_file('src/urisys/init_setup.py', 258, 'python').
project_file('src/urisys/managers/__init__.py', 1, 'python').
project_file('src/urisys/managers/bridge_manager.py', 15, 'python').
project_file('src/urisys/managers/contract_gen.py', 190, 'python').
project_file('src/urisys/managers/event_manager.py', 14, 'python').
project_file('src/urisys/managers/markpact_flows.py', 134, 'python').
project_file('src/urisys/managers/markpact_manager.py', 73, 'python').
project_file('src/urisys/managers/markpact_materialize.py', 70, 'python').
project_file('src/urisys/managers/markpact_models.py', 103, 'python').
project_file('src/urisys/managers/markpact_pack_deps.py', 190, 'python').
project_file('src/urisys/managers/markpact_pack_gen.py', 243, 'python').
project_file('src/urisys/managers/markpact_profile.py', 270, 'python').
project_file('src/urisys/managers/markpact_run.py', 16, 'python').
project_file('src/urisys/managers/markpact_run_flow.py', 161, 'python').
project_file('src/urisys/managers/markpact_validation.py', 157, 'python').
project_file('src/urisys/managers/pack_manager.py', 191, 'python').
project_file('src/urisys/managers/platform_export.py', 14, 'python').
project_file('src/urisys/managers/policy_manager.py', 19, 'python').
project_file('src/urisys/managers/route_manager.py', 24, 'python').
project_file('src/urisys/managers/runtime_manager.py', 31, 'python').
project_file('src/urisys/managers/source_manager.py', 219, 'python').
project_file('src/urisys/markpact/__init__.py', 25, 'python').
project_file('src/urisys/markpact/analyzer/__init__.py', 5, 'python').
project_file('src/urisys/markpact/analyzer/context.py', 16, 'python').
project_file('src/urisys/markpact/analyzer/lint.py', 67, 'python').
project_file('src/urisys/markpact/analyzer/report.py', 53, 'python').
project_file('src/urisys/markpact/analyzer/rules/__init__.py', 28, 'python').
project_file('src/urisys/markpact/analyzer/rules/base.py', 18, 'python').
project_file('src/urisys/markpact/analyzer/rules/capabilities.py', 108, 'python').
project_file('src/urisys/markpact/analyzer/rules/flows.py', 47, 'python').
project_file('src/urisys/markpact/analyzer/rules/pack.py', 46, 'python').
project_file('src/urisys/markpact/analyzer/rules/schemes.py', 20, 'python').
project_file('src/urisys/markpact/artifacts.py', 81, 'python').
project_file('src/urisys/markpact/blocks.py', 64, 'python').
project_file('src/urisys/markpact/cache.py', 119, 'python').
project_file('src/urisys/markpact/compiler.py', 119, 'python').
project_file('src/urisys/markpact/handlers.py', 52, 'python').
project_file('src/urisys/markpact/manifest.py', 128, 'python').
project_file('src/urisys/markpact/pack.py', 55, 'python').
project_file('src/urisys/markpact/platform_export.py', 304, 'python').
project_file('src/urisys/markpact/run/__init__.py', 67, 'python').
project_file('src/urisys/markpact/run/config.py', 26, 'python').
project_file('src/urisys/markpact/run/context.py', 26, 'python').
project_file('src/urisys/markpact/run/modes/__init__.py', 18, 'python').
project_file('src/urisys/markpact/run/modes/adapter.py', 29, 'python').
project_file('src/urisys/markpact/run/modes/base.py', 14, 'python').
project_file('src/urisys/markpact/run/modes/flow.py', 87, 'python').
project_file('src/urisys/markpact/run/modes/interface.py', 29, 'python').
project_file('src/urisys/markpact/run/modes/pack.py', 19, 'python').
project_file('src/urisys/markpact/run/modes/service.py', 25, 'python').
project_file('src/urisys/markpact/run/runtime_build.py', 54, 'python').
project_file('src/urisys/markpact/tests.py', 79, 'python').
project_file('src/urisys/markpact/validate_pack.py', 93, 'python').
project_file('src/urisys/node_install.py', 107, 'python').
project_file('src/urisys/uricore_install.py', 131, 'python').
project_file('src/urisys/urirouter_install.py', 47, 'python').
project_file('src/urisys_lab/__init__.py', 6, 'python').
project_file('src/urisys_lab/core.py', 314, 'python').
project_file('src/urisys_lab/lenovo/__init__.py', 6, 'python').
project_file('src/urisys_lab/lenovo/cli.py', 969, 'python').
project_file('src/urisys_lab/paths.py', 11, 'python').
project_file('src/urisys_lab/sessions/__init__.py', 75, 'python').
project_file('src/urisys_lab/sessions/cli.py', 107, 'python').
project_file('src/urisys_lab/sessions/expectations.py', 154, 'python').
project_file('src/urisys_lab/sessions/lab_flows.py', 321, 'python').
project_file('src/urisys_lab/sessions/lab_rdp.py', 181, 'python').
project_file('src/urisys_lab/sessions/runners.py', 666, 'python').
project_file('src/urisys_lab/sessions/util.py', 198, 'python').
project_file('tests/conftest.py', 54, 'python').
project_file('tests/pack_import_isolation.py', 44, 'python').
project_file('tests/test_analyze_strict.py', 41, 'python').
project_file('tests/test_bootstrap.py', 61, 'python').
project_file('tests/test_capability_conformance.py', 40, 'python').
project_file('tests/test_contract_gen.py', 74, 'python').
project_file('tests/test_desktop_automation_processes.py', 76, 'python').
project_file('tests/test_doctor.py', 29, 'python').
project_file('tests/test_doctor_uricore.py', 27, 'python').
project_file('tests/test_golden_analyze.py', 51, 'python').
project_file('tests/test_http_server.py', 69, 'python').
project_file('tests/test_init.py', 61, 'python').
project_file('tests/test_kvm_pack_pyprojects.py', 71, 'python').
project_file('tests/test_machine_cycle_process.py', 110, 'python').
project_file('tests/test_markpact.py', 105, 'python').
project_file('tests/test_markpact_analyzer_rules.py', 87, 'python').
project_file('tests/test_markpact_contract_materialize.py', 106, 'python').
project_file('tests/test_markpact_materialize.py', 22, 'python').
project_file('tests/test_markpact_pack_deps.py', 33, 'python').
project_file('tests/test_markpact_profile.py', 82, 'python').
project_file('tests/test_markpact_run.py', 98, 'python').
project_file('tests/test_markpact_run_flow.py', 103, 'python').
project_file('tests/test_markpact_session_isolation.py', 63, 'python').
project_file('tests/test_node_install.py', 39, 'python').
project_file('tests/test_pack_gen.py', 83, 'python').
project_file('tests/test_pack_manager_parse.py', 45, 'python').
project_file('tests/test_pack_manager_sibling.py', 39, 'python').
project_file('tests/test_platform_export.py', 64, 'python').
project_file('tests/test_process_conformance.py', 53, 'python').
project_file('tests/test_pypi_metadata.py', 35, 'python').
project_file('tests/test_python_compat.py', 53, 'python').
project_file('tests/test_run_expectations.py', 50, 'python').
project_file('tests/test_session_core.py', 73, 'python').
project_file('tests/test_session_report_events.py', 59, 'python').
project_file('tests/test_showcase.py', 51, 'python').
project_file('tests/test_source_manager.py', 36, 'python').
project_file('tests/test_uricore_install.py', 38, 'python').
project_file('tests/test_urirouter_install.py', 18, 'python').
project_file('tests/test_urisys.py', 65, 'python').
project_file('tests/test_urisys_flow_handler.py', 72, 'python').
project_file('tests/test_vendored_sync.py', 58, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('scripts/check_contract_drift.py', 'manifest_path', 1, 3, 1).
python_function('scripts/check_contract_drift.py', 'contract_paths', 1, 2, 3).
python_function('scripts/check_contract_drift.py', 'check_pair', 2, 1, 3).
python_function('scripts/check_contract_drift.py', '_check_spec', 2, 7, 6).
python_function('scripts/check_contract_drift.py', 'main', 0, 9, 12).
python_function('scripts/generate_pack_markpacts.py', 'repo_module_dir', 1, 2, 0).
python_function('scripts/generate_pack_markpacts.py', '_extra_specs', 0, 3, 2).
python_function('scripts/generate_pack_markpacts.py', '_scheme', 1, 2, 1).
python_function('scripts/generate_pack_markpacts.py', '_fill_pattern', 1, 1, 3).
python_function('scripts/generate_pack_markpacts.py', '_capabilities', 2, 7, 5).
python_function('scripts/generate_pack_markpacts.py', '_tests', 1, 5, 4).
python_function('scripts/generate_pack_markpacts.py', '_use_case_flow', 2, 6, 4).
python_function('scripts/generate_pack_markpacts.py', '_run_block', 4, 1, 0).
python_function('scripts/generate_pack_markpacts.py', '_default_port', 1, 1, 1).
python_function('scripts/generate_pack_markpacts.py', '_render', 0, 14, 14).
python_function('scripts/generate_pack_markpacts.py', '_split_by_scheme', 1, 13, 9).
python_function('scripts/generate_pack_markpacts.py', 'manifest_files', 1, 3, 4).
python_function('scripts/generate_pack_markpacts.py', '_file_stem', 3, 4, 3).
python_function('scripts/generate_pack_markpacts.py', 'generate_for_spec', 1, 4, 7).
python_function('scripts/generate_pack_markpacts.py', '_process_spec', 1, 8, 9).
python_function('scripts/generate_pack_markpacts.py', 'main', 0, 9, 12).
python_function('scripts/office-simulate-loop.py', 'call_uri', 4, 4, 9).
python_function('scripts/office-simulate-loop.py', 'rules_tick', 3, 3, 5).
python_function('scripts/office-simulate-loop.py', 'llm_tick', 3, 7, 6).
python_function('scripts/office-simulate-loop.py', 'parse_args', 1, 1, 4).
python_function('scripts/office-simulate-loop.py', 'main', 1, 10, 9).
python_function('scripts/pack_registry.py', '_repo', 1, 1, 0).
python_function('scripts/pack_registry.py', 'sibling_uv_path', 1, 1, 0).
python_function('scripts/pack_registry.py', 'sibling_repo', 1, 1, 1).
python_function('scripts/pack_registry.py', '_pack', 1, 3, 2).
python_function('scripts/pack_registry.py', 'pack_specs', 0, 7, 3).
python_function('scripts/pack_registry.py', 'sibling_repo_names', 0, 1, 2).
python_function('scripts/pack_registry.py', 'all_promoted_packs', 0, 1, 3).
python_function('scripts/pack_sync.py', 'repo_module_dir', 1, 3, 0).
python_function('scripts/pack_sync.py', 'vendored_module_dir', 1, 2, 1).
python_function('scripts/pack_sync.py', 'read_version', 1, 3, 5).
python_function('scripts/pack_sync.py', 'file_hash', 1, 1, 3).
python_function('scripts/pack_sync.py', 'sync_file', 2, 5, 4).
python_function('scripts/pack_sync.py', 'sync_to_repo', 1, 13, 12).
python_function('scripts/pack_sync.py', 'check_drift', 1, 14, 11).
python_function('scripts/pack_sync.py', '_check_promoted', 1, 5, 4).
python_function('scripts/pack_sync.py', 'remove_vendored', 1, 4, 3).
python_function('scripts/pack_sync.py', '_repo_pyproject', 1, 14, 7).
python_function('scripts/pack_sync.py', 'init_repo', 1, 12, 8).
python_function('scripts/pack_sync.py', 'promote', 1, 1, 2).
python_function('scripts/pack_sync.py', '_validate_packs', 2, 3, 1).
python_function('scripts/pack_sync.py', '_cmd_to_repo', 3, 5, 3).
python_function('scripts/pack_sync.py', '_cmd_promote', 3, 3, 2).
python_function('scripts/pack_sync.py', '_cmd_check', 3, 5, 4).
python_function('scripts/pack_sync.py', '_cmd_init_repo', 3, 3, 2).
python_function('scripts/pack_sync.py', '_cmd_print_uv_sources', 3, 4, 2).
python_function('scripts/pack_sync.py', 'main', 1, 9, 12).
python_function('scripts/report/cli.py', 'main', 0, 4, 13).
python_function('scripts/report/events.py', 'summarize_event_records', 1, 14, 5).
python_function('scripts/report/events.py', 'load_event_records', 1, 14, 7).
python_function('scripts/report/events.py', 'summarize_events', 1, 8, 8).
python_function('scripts/report/events.py', 'resolve_events_paths', 1, 7, 2).
python_function('scripts/report/events.py', 'merge_event_summaries', 1, 10, 9).
python_function('scripts/report/lab_checks.py', 'iter_step_results', 1, 9, 3).
python_function('scripts/report/lab_checks.py', '_response_to_outcome', 1, 13, 11).
python_function('scripts/report/lab_checks.py', 'load_flow_outcomes', 1, 3, 4).
python_function('scripts/report/lab_checks.py', 'check_declared_expectations', 1, 3, 2).
python_function('scripts/report/lab_checks.py', 'check_gui_no_effect', 1, 5, 2).
python_function('scripts/report/lab_checks.py', 'check_vision_never_decides', 1, 8, 3).
python_function('scripts/report/lab_checks.py', '_duplicate_recommendation', 1, 6, 1).
python_function('scripts/report/lab_checks.py', 'check_duplicate_screenshots', 1, 5, 3).
python_function('scripts/report/lab_checks.py', 'check_shell_baseline_duplicate', 1, 6, 2).
python_function('scripts/report/lab_checks.py', 'analyze_lab_flows', 1, 5, 3).
python_function('scripts/report/run_analysis.py', '_session_row', 3, 9, 4).
python_function('scripts/report/run_analysis.py', '_findings_for_session', 1, 13, 4).
python_function('scripts/report/run_analysis.py', '_run_recommendations', 2, 10, 3).
python_function('scripts/report/run_analysis.py', 'analyze_run', 1, 13, 23).
python_function('scripts/report/run_analysis.py', 'write_run_analysis', 2, 2, 6).
python_function('scripts/report/run_markdown.py', 'render_run_analysis_markdown', 1, 7, 4).
python_function('scripts/report/session.py', '_extract_metrics', 1, 7, 4).
python_function('scripts/report/session.py', '_resolve_screenshot', 2, 5, 3).
python_function('scripts/report/session.py', '_response_to_step_result', 2, 12, 9).
python_function('scripts/report/session.py', 'infer_steps', 2, 7, 8).
python_function('scripts/report/session.py', 'collect_artifacts', 1, 7, 8).
python_function('scripts/report/session.py', 'session_status', 2, 9, 4).
python_function('scripts/report/session.py', 'session_duration', 1, 5, 8).
python_function('scripts/report/session.py', 'generate_report', 1, 9, 16).
python_function('scripts/report/session_io.py', 'write_session_report', 2, 2, 6).
python_function('scripts/report/session_markdown.py', 'render_session_markdown', 1, 1, 10).
python_function('scripts/report/session_markdown.py', '_environment_section', 1, 5, 2).
python_function('scripts/report/session_markdown.py', '_steps_section', 1, 7, 3).
python_function('scripts/report/session_markdown.py', '_screenshots_section', 1, 3, 2).
python_function('scripts/report/session_markdown.py', '_events_section', 1, 5, 5).
python_function('scripts/report/session_markdown.py', '_log_errors_section', 1, 4, 2).
python_function('scripts/report/session_markdown.py', '_duplicate_screenshots_section', 1, 7, 3).
python_function('scripts/report/session_markdown.py', '_log_tail_section', 1, 2, 1).
python_function('scripts/report/util.py', 'read_json', 1, 3, 3).
python_function('scripts/report/util.py', 'tail', 2, 2, 0).
python_function('scripts/scan-browser-sessions.py', '_copy_query', 3, 2, 8).
python_function('scripts/scan-browser-sessions.py', 'scan_chrome_cookies', 1, 13, 12).
python_function('scripts/scan-browser-sessions.py', 'chrome_profiles', 1, 11, 9).
python_function('scripts/scan-browser-sessions.py', 'firefox_profiles', 1, 8, 10).
python_function('scripts/scan-browser-sessions.py', 'discover_browsers', 1, 1, 0).
python_function('scripts/scan-browser-sessions.py', '_scan_profiles', 1, 12, 10).
python_function('scripts/scan-browser-sessions.py', '_output_json', 1, 2, 4).
python_function('scripts/scan-browser-sessions.py', '_output_text', 2, 11, 6).
python_function('scripts/scan-browser-sessions.py', 'main', 0, 2, 6).
python_function('scripts/test_sessions/expectations.py', 'flow_expectations', 1, 5, 5).
python_function('scripts/test_sessions/expectations.py', 'ocr_texts', 1, 11, 4).
python_function('scripts/test_sessions/expectations.py', 'vision_confidences', 1, 11, 6).
python_function('scripts/test_sessions/expectations.py', '_screen_changed', 1, 5, 1).
python_function('scripts/test_sessions/expectations.py', '_screen_changed_since_previous', 1, 5, 1).
python_function('scripts/test_sessions/expectations.py', '_opened_url_contains', 2, 11, 6).
python_function('scripts/test_sessions/expectations.py', '_ocr_contains', 2, 5, 5).
python_function('scripts/test_sessions/expectations.py', '_min_vision_confidence', 2, 4, 3).
python_function('scripts/test_sessions/expectations.py', 'evaluate_expectations', 1, 3, 6).
python_function('scripts/test_sessions/lab_flows.py', '_lab_bootstrap', 1, 5, 4).
python_function('scripts/test_sessions/lab_flows.py', '_capture_flow_screenshot', 1, 13, 7).
python_function('scripts/test_sessions/lab_flows.py', '_flow_step_detail', 0, 4, 2).
python_function('scripts/test_sessions/lab_flows.py', '_run_single_lab_flow', 1, 10, 11).
python_function('scripts/test_sessions/lab_flows.py', 'session_lab_10_flows', 1, 7, 22).
python_function('scripts/test_sessions/lab_rdp.py', 'parse_lab_flow', 1, 10, 10).
python_function('scripts/test_sessions/lab_rdp.py', 'flow_step_context', 2, 6, 3).
python_function('scripts/test_sessions/lab_rdp.py', 'step_pause', 1, 6, 2).
python_function('scripts/test_sessions/lab_rdp.py', 'summarize_uri_response', 1, 11, 3).
python_function('scripts/test_sessions/lab_rdp.py', 'parse_docker_log_errors', 1, 10, 8).
python_function('scripts/test_sessions/lab_rdp.py', 'prepare_ok_target', 3, 1, 2).
python_function('scripts/test_sessions/lab_rdp.py', 'capture_rdp_screenshot', 1, 5, 4).
python_function('scripts/test_sessions/lab_rdp.py', 'capture_rdp_screenshot_wait', 1, 9, 5).
python_function('scripts/test_sessions/util.py', 'run_id', 0, 1, 2).
python_function('scripts/test_sessions/util.py', 'http_json', 4, 9, 11).
python_function('scripts/test_sessions/util.py', 'wait_health', 3, 3, 5).
python_function('scripts/test_sessions/util.py', 'compose_cmd', 0, 4, 3).
python_function('scripts/test_sessions/util.py', 'run_cmd', 1, 6, 8).
python_function('scripts/test_sessions/util.py', 'write_meta', 1, 1, 3).
python_function('scripts/test_sessions/util.py', 'read_meta', 1, 3, 3).
python_function('scripts/test_sessions/util.py', 'finalize_session', 4, 5, 10).
python_function('scripts/test_sessions/util.py', 'docker_logs', 4, 3, 3).
python_function('scripts/test_sessions/util.py', 'copy_container_file', 3, 2, 4).
python_function('scripts/test_sessions/util.py', 'copy_host_screenshot', 3, 2, 5).
python_function('scripts/test_sessions/util.py', 'file_md5', 1, 2, 4).
python_function('scripts/test_sessions/util.py', 'sleep_ports', 0, 1, 1).
python_function('scripts/test_sessions/util.py', 'prepare_urirdp_data', 1, 4, 5).
python_function('scripts/update-ecosystem-readmes.py', 'build_section', 1, 1, 1).
python_function('scripts/update-ecosystem-readmes.py', 'strip_old_section', 1, 2, 2).
python_function('scripts/update-ecosystem-readmes.py', 'fix_urisysedge_refs', 1, 2, 1).
python_function('scripts/update-ecosystem-readmes.py', 'main', 0, 4, 10).
python_function('src/urisys/bootstrap.py', '_print_json', 1, 1, 2).
python_function('src/urisys/bootstrap.py', '_missing_uricore_payload', 1, 1, 1).
python_function('src/urisys/bootstrap.py', '_doctor_main', 1, 3, 6).
python_function('src/urisys/bootstrap.py', '_init_main', 1, 6, 9).
python_function('src/urisys/bootstrap.py', 'main', 1, 8, 6).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_run_flow', 3, 3, 5).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_materialize', 3, 3, 7).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_export_platform', 2, 3, 7).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_run_markpact', 2, 2, 5).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_validate', 2, 1, 2).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_compile', 3, 1, 3).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_routes', 3, 2, 4).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_test', 3, 1, 2).
python_function('src/urisys/cli/commands/markpact.py', '_apply_strict_operations', 2, 8, 2).
python_function('src/urisys/cli/commands/markpact.py', '_apply_strict_profile', 2, 4, 2).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_analyze', 3, 5, 7).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_pack', 1, 6, 9).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_contract', 2, 6, 12).
python_function('src/urisys/cli/commands/markpact.py', '_run_path_command', 4, 6, 5).
python_function('src/urisys/cli/commands/markpact.py', 'cmd_markpact', 1, 11, 14).
python_function('src/urisys/cli/commands/node.py', 'cmd_node', 1, 6, 5).
python_function('src/urisys/cli/commands/runtime.py', 'cmd_uri', 1, 4, 7).
python_function('src/urisys/cli/commands/runtime.py', 'cmd_serve', 1, 1, 3).
python_function('src/urisys/cli/commands/runtime.py', 'cmd_flow', 1, 1, 4).
python_function('src/urisys/cli/commands/runtime.py', 'cmd_events', 1, 1, 3).
python_function('src/urisys/cli/commands/setup.py', 'cmd_doctor', 1, 3, 3).
python_function('src/urisys/cli/commands/setup.py', 'cmd_init', 1, 6, 5).
python_function('src/urisys/cli/errors.py', 'handle_cli_error', 1, 8, 4).
python_function('src/urisys/cli/helpers.py', 'json_arg', 1, 3, 4).
python_function('src/urisys/cli/helpers.py', 'print_json', 1, 1, 2).
python_function('src/urisys/cli/helpers.py', 'resolve_markpact_source', 1, 2, 3).
python_function('src/urisys/cli/main.py', 'main', 1, 3, 5).
python_function('src/urisys/cli/parser.py', 'add_runtime_flags', 1, 1, 1).
python_function('src/urisys/cli/parser.py', 'build_parser', 0, 1, 9).
python_function('src/urisys/doctor.py', '_pkg_version', 1, 2, 1).
python_function('src/urisys/doctor.py', '_parse_version', 1, 7, 6).
python_function('src/urisys/doctor.py', '_version_lt', 2, 2, 1).
python_function('src/urisys/doctor.py', '_check_import', 2, 5, 7).
python_function('src/urisys/doctor.py', '_check_python', 0, 3, 1).
python_function('src/urisys/doctor.py', '_check_cli_path', 0, 3, 4).
python_function('src/urisys/doctor.py', '_check_min_version', 1, 6, 4).
python_function('src/urisys/doctor.py', '_check_wayland_him', 0, 3, 3).
python_function('src/urisys/doctor.py', '_check_uricore_authentic', 0, 6, 5).
python_function('src/urisys/doctor.py', '_check_uricore_dist', 0, 3, 3).
python_function('src/urisys/doctor.py', 'run_doctor', 0, 11, 13).
python_function('src/urisys/flow.py', 'load_flow', 1, 3, 5).
python_function('src/urisys/flow.py', 'iter_steps', 1, 7, 7).
python_function('src/urisys/http_server.py', '_read_json', 1, 3, 5).
python_function('src/urisys/http_server.py', 'create_server', 2, 1, 10).
python_function('src/urisys/init_setup.py', 'default_pip_specs', 0, 1, 2).
python_function('src/urisys/init_setup.py', 'default_node_pip_spec', 0, 1, 1).
python_function('src/urisys/init_setup.py', 'pip_install_specs', 1, 4, 2).
python_function('src/urisys/init_setup.py', 'verify_uri_control', 0, 2, 3).
python_function('src/urisys/init_setup.py', 'profile_env', 1, 2, 1).
python_function('src/urisys/init_setup.py', 'render_env_shell', 1, 2, 4).
python_function('src/urisys/init_setup.py', 'write_env_file', 2, 2, 5).
python_function('src/urisys/init_setup.py', '_pre_repair_uricore', 4, 6, 5).
python_function('src/urisys/init_setup.py', '_build_pip_result', 1, 5, 7).
python_function('src/urisys/init_setup.py', '_resolve_error_hint', 3, 5, 2).
python_function('src/urisys/init_setup.py', '_run_pip_install', 2, 2, 1).
python_function('src/urisys/init_setup.py', '_verify_after_install', 3, 8, 5).
python_function('src/urisys/init_setup.py', '_run_doctor_check', 3, 3, 3).
python_function('src/urisys/init_setup.py', '_write_profile_env', 5, 4, 3).
python_function('src/urisys/init_setup.py', '_check_node_after_install', 4, 6, 3).
python_function('src/urisys/init_setup.py', 'run_init', 0, 13, 14).
python_function('src/urisys/managers/contract_gen.py', 'load_manifest', 1, 3, 5).
python_function('src/urisys/managers/contract_gen.py', 'normalize_version', 1, 6, 8).
python_function('src/urisys/managers/contract_gen.py', 'contract_id', 1, 4, 5).
python_function('src/urisys/managers/contract_gen.py', '_routes', 1, 5, 3).
python_function('src/urisys/managers/contract_gen.py', '_entry', 1, 8, 5).
python_function('src/urisys/managers/contract_gen.py', 'manifest_to_contract', 1, 11, 11).
python_function('src/urisys/managers/contract_gen.py', 'render_contract_markpact', 1, 2, 4).
python_function('src/urisys/managers/contract_gen.py', 'load_contract_block', 1, 7, 6).
python_function('src/urisys/managers/contract_gen.py', '_by_pattern', 1, 5, 3).
python_function('src/urisys/managers/contract_gen.py', '_diff_scheme_and_metadata', 3, 5, 3).
python_function('src/urisys/managers/contract_gen.py', '_diff_section', 4, 8, 6).
python_function('src/urisys/managers/contract_gen.py', '_diff_uses', 3, 7, 4).
python_function('src/urisys/managers/contract_gen.py', 'diff_manifest_contract', 2, 2, 4).
python_function('src/urisys/managers/markpact_flows.py', 'extract_protos', 1, 7, 5).
python_function('src/urisys/managers/markpact_flows.py', 'extract_modules', 1, 7, 7).
python_function('src/urisys/managers/markpact_flows.py', 'extract_flows', 1, 11, 6).
python_function('src/urisys/managers/markpact_flows.py', 'flow_uris', 1, 8, 6).
python_function('src/urisys/managers/markpact_flows.py', '_scheme', 1, 1, 1).
python_function('src/urisys/managers/markpact_flows.py', '_provider_scheme', 1, 1, 1).
python_function('src/urisys/managers/markpact_flows.py', 'classify_flow', 1, 11, 6).
python_function('src/urisys/managers/markpact_flows.py', 'declared_uses', 1, 1, 1).
python_function('src/urisys/managers/markpact_materialize.py', 'default_materialize_root', 0, 1, 1).
python_function('src/urisys/managers/markpact_materialize.py', 'materialize_markpact', 1, 8, 19).
python_function('src/urisys/managers/markpact_models.py', 'safe_identifier', 1, 3, 4).
python_function('src/urisys/managers/markpact_models.py', 'parse_meta', 1, 4, 2).
python_function('src/urisys/managers/markpact_models.py', 'scheme_from_uri', 1, 2, 2).
python_function('src/urisys/managers/markpact_models.py', 'source_hash', 1, 1, 4).
python_function('src/urisys/managers/markpact_pack_deps.py', 'tellmesh_root', 0, 7, 6).
python_function('src/urisys/managers/markpact_pack_deps.py', '_is_capability_pack_repo', 1, 4, 1).
python_function('src/urisys/managers/markpact_pack_deps.py', '_register_flat_pack', 2, 4, 5).
python_function('src/urisys/managers/markpact_pack_deps.py', '_is_flat_pack_repo', 1, 3, 1).
python_function('src/urisys/managers/markpact_pack_deps.py', '_discover_pack_modules', 1, 12, 6).
python_function('src/urisys/managers/markpact_pack_deps.py', '_register_existing_pack', 4, 6, 7).
python_function('src/urisys/managers/markpact_pack_deps.py', '_register_sibling_packs', 3, 12, 11).
python_function('src/urisys/managers/markpact_pack_deps.py', '_register_uricore_utils', 2, 3, 5).
python_function('src/urisys/managers/markpact_pack_deps.py', '_register_urioperators', 2, 6, 7).
python_function('src/urisys/managers/markpact_pack_deps.py', 'extend_tellmesh_paths', 0, 2, 5).
python_function('src/urisys/managers/markpact_pack_deps.py', '_pack_resolver', 0, 2, 0).
python_function('src/urisys/managers/markpact_pack_deps.py', 'ensure_pack_importable', 1, 5, 6).
python_function('src/urisys/managers/markpact_pack_deps.py', 'ensure_flow_packs', 1, 2, 3).
python_function('src/urisys/managers/markpact_pack_gen.py', 'find_package_dir', 1, 8, 5).
python_function('src/urisys/managers/markpact_pack_gen.py', '_load_manifest', 1, 3, 4).
python_function('src/urisys/managers/markpact_pack_gen.py', 'package_schemes', 1, 11, 5).
python_function('src/urisys/managers/markpact_pack_gen.py', '_build_capability', 4, 11, 4).
python_function('src/urisys/managers/markpact_pack_gen.py', '_pack_block', 3, 9, 7).
python_function('src/urisys/managers/markpact_pack_gen.py', '_run_block', 3, 1, 0).
python_function('src/urisys/managers/markpact_pack_gen.py', '_module_blocks', 2, 3, 7).
python_function('src/urisys/managers/markpact_pack_gen.py', '_proto_blocks', 2, 3, 7).
python_function('src/urisys/managers/markpact_pack_gen.py', '_sanitize_docs', 1, 1, 1).
python_function('src/urisys/managers/markpact_pack_gen.py', '_embedded_flows', 3, 9, 9).
python_function('src/urisys/managers/markpact_pack_gen.py', '_resolve_repo_root', 2, 6, 3).
python_function('src/urisys/managers/markpact_pack_gen.py', 'generate_pack_markpact', 1, 10, 18).
python_function('src/urisys/managers/markpact_profile.py', '_issue', 4, 1, 1).
python_function('src/urisys/managers/markpact_profile.py', '_issue_message', 1, 1, 0).
python_function('src/urisys/managers/markpact_profile.py', 'declared_schemes', 1, 11, 9).
python_function('src/urisys/managers/markpact_profile.py', 'declared_packs', 1, 5, 4).
python_function('src/urisys/managers/markpact_profile.py', '_cap_uri', 1, 3, 2).
python_function('src/urisys/managers/markpact_profile.py', '_step_features', 2, 7, 3).
python_function('src/urisys/managers/markpact_profile.py', '_flow_level_features', 2, 3, 2).
python_function('src/urisys/managers/markpact_profile.py', '_text_pattern_features', 2, 4, 3).
python_function('src/urisys/managers/markpact_profile.py', '_flow_features', 2, 6, 8).
python_function('src/urisys/managers/markpact_profile.py', '_required_features', 1, 4, 5).
python_function('src/urisys/managers/markpact_profile.py', '_validate_scheme_requirements', 2, 1, 2).
python_function('src/urisys/managers/markpact_profile.py', '_validate_undeclared_schemes', 2, 3, 1).
python_function('src/urisys/managers/markpact_profile.py', '_validate_capability_operations', 3, 6, 7).
python_function('src/urisys/managers/markpact_profile.py', '_validate_uri_kind', 5, 5, 2).
python_function('src/urisys/managers/markpact_profile.py', '_validate_command_approval', 6, 7, 4).
python_function('src/urisys/managers/markpact_profile.py', '_validate_process_handler', 5, 5, 5).
python_function('src/urisys/managers/markpact_profile.py', '_validate_capability_uris', 4, 6, 7).
python_function('src/urisys/managers/markpact_profile.py', '_build_flow_profiles', 4, 6, 5).
python_function('src/urisys/managers/markpact_profile.py', '_cross_check_schemes', 4, 9, 6).
python_function('src/urisys/managers/markpact_profile.py', 'lint_markpact', 0, 1, 1).
python_function('src/urisys/managers/markpact_run_flow.py', 'split_flow_ref', 1, 3, 2).
python_function('src/urisys/managers/markpact_run_flow.py', 'pick_flow_id', 2, 5, 4).
python_function('src/urisys/managers/markpact_run_flow.py', 'flow_path_for', 2, 3, 3).
python_function('src/urisys/managers/markpact_run_flow.py', 'packs_for_flow', 2, 4, 7).
python_function('src/urisys/managers/markpact_run_flow.py', '_split_extra', 1, 7, 4).
python_function('src/urisys/managers/markpact_run_flow.py', 'run_markpact_flow', 1, 14, 21).
python_function('src/urisys/managers/markpact_validation.py', '_validate_contract_routes', 3, 11, 7).
python_function('src/urisys/managers/markpact_validation.py', 'validate_contract', 3, 13, 7).
python_function('src/urisys/managers/markpact_validation.py', '_missing_bundle_imports', 2, 6, 5).
python_function('src/urisys/managers/markpact_validation.py', 'validate_bundle', 3, 9, 8).
python_function('src/urisys/managers/markpact_validation.py', '_validate_implementation_capabilities', 2, 5, 6).
python_function('src/urisys/managers/markpact_validation.py', 'validate_implementation', 3, 14, 7).
python_function('src/urisys/managers/pack_manager.py', '_repo_for_package', 2, 2, 0).
python_function('src/urisys/managers/pack_manager.py', '_sibling_manifest_path', 1, 8, 6).
python_function('src/urisys/managers/pack_manager.py', '_manifest_is_loadable', 1, 5, 7).
python_function('src/urisys/markpact/analyzer/lint.py', '_issue_message', 1, 1, 0).
python_function('src/urisys/markpact/analyzer/lint.py', 'run_lint', 0, 8, 11).
python_function('src/urisys/markpact/analyzer/report.py', 'analyze_markpact', 1, 8, 16).
python_function('src/urisys/markpact/analyzer/rules/base.py', 'cap_uri', 1, 3, 2).
python_function('src/urisys/markpact/artifacts.py', 'write_modules', 2, 2, 5).
python_function('src/urisys/markpact/artifacts.py', 'flows_from_cache', 2, 3, 3).
python_function('src/urisys/markpact/artifacts.py', 'protos_from_cache', 2, 3, 3).
python_function('src/urisys/markpact/artifacts.py', 'modules_from_cache', 2, 4, 3).
python_function('src/urisys/markpact/artifacts.py', 'write_flows', 2, 3, 6).
python_function('src/urisys/markpact/artifacts.py', 'write_protos', 2, 3, 5).
python_function('src/urisys/markpact/blocks.py', 'read_blocks', 1, 3, 8).
python_function('src/urisys/markpact/blocks.py', 'yaml_blocks', 2, 4, 0).
python_function('src/urisys/markpact/blocks.py', 'handler_blocks', 1, 5, 2).
python_function('src/urisys/markpact/blocks.py', 'load_yaml_blocks', 2, 6, 4).
python_function('src/urisys/markpact/cache.py', 'compile_context', 1, 2, 6).
python_function('src/urisys/markpact/cache.py', 'compiled_from_cache', 2, 4, 6).
python_function('src/urisys/markpact/cache.py', 'write_manifest_flows', 3, 3, 7).
python_function('src/urisys/markpact/cache.py', 'write_compile_metadata', 1, 1, 4).
python_function('src/urisys/markpact/cache.py', 'ensure_importable', 1, 2, 3).
python_function('src/urisys/markpact/compiler.py', '_write_tests_block', 2, 2, 3).
python_function('src/urisys/markpact/compiler.py', '_write_docs_block', 2, 4, 3).
python_function('src/urisys/markpact/compiler.py', '_existing_path', 1, 3, 2).
python_function('src/urisys/markpact/handlers.py', 'handler_id_from_ref', 1, 2, 2).
python_function('src/urisys/markpact/handlers.py', 'resolve_handler_ref', 5, 7, 4).
python_function('src/urisys/markpact/handlers.py', 'write_handler_modules', 2, 5, 4).
python_function('src/urisys/markpact/manifest.py', '_resolve_pattern', 1, 4, 3).
python_function('src/urisys/markpact/manifest.py', '_validate_scheme', 1, 2, 2).
python_function('src/urisys/markpact/manifest.py', '_resolve_operation', 1, 5, 5).
python_function('src/urisys/markpact/manifest.py', '_resolve_kind', 1, 3, 2).
python_function('src/urisys/markpact/manifest.py', '_build_route_dict', 5, 5, 2).
python_function('src/urisys/markpact/manifest.py', 'build_route', 1, 2, 8).
python_function('src/urisys/markpact/manifest.py', 'compile_manifest', 1, 12, 5).
python_function('src/urisys/markpact/pack.py', 'load_pack_block', 1, 4, 7).
python_function('src/urisys/markpact/pack.py', 'package_id', 2, 5, 5).
python_function('src/urisys/markpact/pack.py', 'capabilities', 1, 6, 3).
python_function('src/urisys/markpact/pack.py', 'scheme_for_pack', 2, 8, 5).
python_function('src/urisys/markpact/platform_export.py', '_resolve_authority', 2, 9, 5).
python_function('src/urisys/markpact/platform_export.py', '_authorities_from_flow', 1, 10, 10).
python_function('src/urisys/markpact/platform_export.py', 'collect_process_uris', 1, 6, 15).
python_function('src/urisys/markpact/platform_export.py', '_target_stub', 3, 11, 1).
python_function('src/urisys/markpact/platform_export.py', 'build_resolver_yaml', 0, 5, 3).
python_function('src/urisys/markpact/platform_export.py', '_esp32_routes_header', 2, 6, 7).
python_function('src/urisys/markpact/platform_export.py', '_server_compose_snippet', 1, 1, 0).
python_function('src/urisys/markpact/platform_export.py', 'export_platform_artifacts', 1, 7, 13).
python_function('src/urisys/markpact/run/__init__.py', 'run_markpact', 1, 6, 10).
python_function('src/urisys/markpact/run/config.py', 'read_run_config', 1, 7, 4).
python_function('src/urisys/markpact/run/config.py', 'load_run_config', 1, 4, 5).
python_function('src/urisys/markpact/run/modes/flow.py', '_resolve_flow_ids', 2, 5, 3).
python_function('src/urisys/markpact/run/modes/flow.py', '_resolve_flow_uses', 3, 5, 11).
python_function('src/urisys/markpact/run/modes/flow.py', '_build_flow_runtime', 2, 2, 7).
python_function('src/urisys/markpact/run/runtime_build.py', 'apply_resolver_config', 2, 7, 6).
python_function('src/urisys/markpact/run/runtime_build.py', 'build_runtime', 1, 3, 5).
python_function('src/urisys/markpact/run/runtime_build.py', 'routes_summary', 1, 2, 0).
python_function('src/urisys/markpact/tests.py', 'check_expectations', 2, 9, 4).
python_function('src/urisys/markpact/tests.py', 'run_markpact_tests', 1, 12, 14).
python_function('src/urisys/markpact/tests.py', 'run_tests_for_path', 1, 1, 3).
python_function('src/urisys/markpact/validate_pack.py', 'validate_pack', 3, 11, 16).
python_function('src/urisys/markpact/validate_pack.py', 'validate_markpact_file', 1, 12, 12).
python_function('src/urisys/node_install.py', 'github_owner', 0, 1, 2).
python_function('src/urisys/node_install.py', 'github_version', 0, 1, 3).
python_function('src/urisys/node_install.py', 'wheel_filename', 1, 2, 2).
python_function('src/urisys/node_install.py', 'wheel_url', 1, 3, 6).
python_function('src/urisys/node_install.py', 'pip_spec', 0, 1, 1).
python_function('src/urisys/node_install.py', 'is_importable', 0, 1, 1).
python_function('src/urisys/node_install.py', 'pip_run', 1, 4, 2).
python_function('src/urisys/node_install.py', 'install_urisys_node', 0, 7, 6).
python_function('src/urisys/node_install.py', 'diagnose_urisys_node', 0, 3, 4).
python_function('src/urisys/uricore_install.py', 'github_owner', 0, 1, 2).
python_function('src/urisys/uricore_install.py', 'github_version', 0, 1, 3).
python_function('src/urisys/uricore_install.py', 'wheel_url', 1, 3, 5).
python_function('src/urisys/uricore_install.py', 'pip_spec', 0, 1, 1).
python_function('src/urisys/uricore_install.py', '_pkg_version', 1, 2, 1).
python_function('src/urisys/uricore_install.py', '_module_exists', 1, 1, 1).
python_function('src/urisys/uricore_install.py', '_dist_top_levels', 1, 6, 5).
python_function('src/urisys/uricore_install.py', 'is_wrong_uricore_installed', 0, 5, 3).
python_function('src/urisys/uricore_install.py', 'diagnose_uricore', 0, 4, 4).
python_function('src/urisys/uricore_install.py', 'pip_run', 1, 4, 2).
python_function('src/urisys/uricore_install.py', 'repair_uricore', 0, 6, 7).
python_function('src/urisys/urirouter_install.py', 'github_owner', 0, 1, 2).
python_function('src/urisys/urirouter_install.py', 'github_version', 0, 1, 3).
python_function('src/urisys/urirouter_install.py', 'wheel_url', 1, 3, 5).
python_function('src/urisys/urirouter_install.py', 'pip_spec', 0, 1, 1).
python_function('src/urisys/urirouter_install.py', '_module_exists', 1, 1, 1).
python_function('src/urisys/urirouter_install.py', 'diagnose_urirouter', 0, 2, 2).
python_function('src/urisys_lab/core.py', 'default_examples_root', 0, 3, 4).
python_function('src/urisys_lab/core.py', 'resolve_flow_ref', 1, 5, 5).
python_function('src/urisys_lab/core.py', 'now_iso', 0, 1, 2).
python_function('src/urisys_lab/core.py', 'host_id', 0, 1, 3).
python_function('src/urisys_lab/core.py', 'run_id', 1, 2, 2).
python_function('src/urisys_lab/core.py', 'save_json', 2, 1, 3).
python_function('src/urisys_lab/core.py', '_step_ok_http_get', 1, 1, 2).
python_function('src/urisys_lab/core.py', '_step_ok_host_restart_and_wait', 1, 2, 2).
python_function('src/urisys_lab/core.py', '_step_ok_host_schedule_restart', 1, 4, 1).
python_function('src/urisys_lab/core.py', '_step_ok_default', 1, 7, 2).
python_function('src/urisys_lab/core.py', 'step_ok', 1, 3, 3).
python_function('src/urisys_lab/core.py', 'image_ext', 1, 5, 1).
python_function('src/urisys_lab/core.py', 'write_base64_image', 2, 1, 4).
python_function('src/urisys_lab/core.py', 'extract_images_from_dict', 1, 8, 11).
python_function('src/urisys_lab/core.py', 'extract_step_screenshots', 1, 5, 4).
python_function('src/urisys_lab/core.py', 'backfill_session_images', 1, 8, 11).
python_function('src/urisys_lab/core.py', '_wheel_version_key', 2, 5, 7).
python_function('src/urisys_lab/core.py', 'find_wheel_file', 2, 2, 4).
python_function('src/urisys_lab/core.py', 'wheel_url', 2, 1, 1).
python_function('src/urisys_lab/core.py', '_resolve_wheel_name', 2, 6, 4).
python_function('src/urisys_lab/core.py', '_apply_wheel_refspec', 2, 4, 4).
python_function('src/urisys_lab/core.py', '_resolve_wheel_args', 1, 7, 8).
python_function('src/urisys_lab/core.py', 'expand_step_wheels', 1, 4, 5).
python_function('src/urisys_lab/lenovo/cli.py', 'load_yaml', 1, 3, 4).
python_function('src/urisys_lab/lenovo/cli.py', 'http_get', 2, 4, 6).
python_function('src/urisys_lab/lenovo/cli.py', '_run_http_get_step', 3, 2, 3).
python_function('src/urisys_lab/lenovo/cli.py', '_run_host_sleep_step', 2, 3, 3).
python_function('src/urisys_lab/lenovo/cli.py', '_schedule_restart_safely', 2, 4, 2).
python_function('src/urisys_lab/lenovo/cli.py', '_poll_health_after_restart', 1, 9, 7).
python_function('src/urisys_lab/lenovo/cli.py', '_run_host_restart_and_wait_step', 2, 11, 8).
python_function('src/urisys_lab/lenovo/cli.py', '_run_host_schedule_restart_step', 2, 4, 2).
python_function('src/urisys_lab/lenovo/cli.py', '_run_host_wait_health_step', 2, 12, 9).
python_function('src/urisys_lab/lenovo/cli.py', '_run_uri_call_step', 2, 6, 6).
python_function('src/urisys_lab/lenovo/cli.py', 'run_step', 1, 9, 10).
python_function('src/urisys_lab/lenovo/cli.py', 'run_flow', 1, 14, 20).
python_function('src/urisys_lab/lenovo/cli.py', 'append_log', 2, 1, 4).
python_function('src/urisys_lab/lenovo/cli.py', 'build_wheels', 1, 4, 6).
python_function('src/urisys_lab/lenovo/cli.py', 'start_wheel_server', 3, 2, 4).
python_function('src/urisys_lab/lenovo/cli.py', '_needs_node_upgrade', 1, 4, 2).
python_function('src/urisys_lab/lenovo/cli.py', '_run_upgrade_flow', 2, 1, 4).
python_function('src/urisys_lab/lenovo/cli.py', '_md_header', 2, 1, 3).
python_function('src/urisys_lab/lenovo/cli.py', '_md_flow_results', 1, 6, 4).
python_function('src/urisys_lab/lenovo/cli.py', '_md_step_detail', 1, 12, 2).
python_function('src/urisys_lab/lenovo/cli.py', '_md_lessons', 2, 6, 3).
python_function('src/urisys_lab/lenovo/cli.py', 'write_session_md', 3, 1, 9).
python_function('src/urisys_lab/lenovo/cli.py', 'resolve_flow_paths', 2, 5, 4).
python_function('src/urisys_lab/lenovo/cli.py', 'resolve_route_map', 2, 8, 8).
python_function('src/urisys_lab/lenovo/cli.py', 'load_manifest_session', 1, 2, 3).
python_function('src/urisys_lab/lenovo/cli.py', '_check_and_restore_health', 1, 4, 5).
python_function('src/urisys_lab/lenovo/cli.py', '_skip_node_down', 1, 4, 8).
python_function('src/urisys_lab/lenovo/cli.py', '_maybe_run_node_upgrade', 2, 6, 5).
python_function('src/urisys_lab/lenovo/cli.py', '_maybe_run_kvm_upgrade', 1, 5, 4).
python_function('src/urisys_lab/lenovo/cli.py', '_maybe_run_playwright_upgrade', 1, 5, 4).
python_function('src/urisys_lab/lenovo/cli.py', '_run_flows', 1, 7, 10).
python_function('src/urisys_lab/lenovo/cli.py', '_run_extract_images', 1, 2, 6).
python_function('src/urisys_lab/lenovo/cli.py', '_ensure_pyyaml', 0, 2, 1).
python_function('src/urisys_lab/lenovo/cli.py', '_init_session', 2, 3, 4).
python_function('src/urisys_lab/lenovo/cli.py', '_setup_wheels', 2, 7, 6).
python_function('src/urisys_lab/lenovo/cli.py', '_check_initial_health', 1, 4, 7).
python_function('src/urisys_lab/lenovo/cli.py', '_copy_flow_sources', 3, 3, 3).
python_function('src/urisys_lab/lenovo/cli.py', '_build_meta', 8, 4, 6).
python_function('src/urisys_lab/lenovo/cli.py', '_collect_step_summaries', 2, 8, 2).
python_function('src/urisys_lab/lenovo/cli.py', '_session_result', 6, 6, 7).
python_function('src/urisys_lab/lenovo/cli.py', 'main', 1, 10, 33).
python_function('src/urisys_lab/sessions/cli.py', 'main', 0, 13, 19).
python_function('src/urisys_lab/sessions/expectations.py', 'flow_expectations', 1, 5, 5).
python_function('src/urisys_lab/sessions/expectations.py', 'ocr_texts', 1, 11, 4).
python_function('src/urisys_lab/sessions/expectations.py', 'vision_confidences', 1, 11, 6).
python_function('src/urisys_lab/sessions/expectations.py', '_screen_changed', 1, 5, 1).
python_function('src/urisys_lab/sessions/expectations.py', '_screen_changed_since_previous', 1, 5, 1).
python_function('src/urisys_lab/sessions/expectations.py', '_opened_url_contains', 2, 11, 6).
python_function('src/urisys_lab/sessions/expectations.py', '_ocr_contains', 2, 5, 5).
python_function('src/urisys_lab/sessions/expectations.py', '_min_vision_confidence', 2, 4, 3).
python_function('src/urisys_lab/sessions/expectations.py', 'evaluate_expectations', 1, 3, 6).
python_function('src/urisys_lab/sessions/lab_flows.py', '_lab_bootstrap', 1, 5, 4).
python_function('src/urisys_lab/sessions/lab_flows.py', '_capture_flow_screenshot', 1, 13, 7).
python_function('src/urisys_lab/sessions/lab_flows.py', '_flow_step_detail', 0, 4, 2).
python_function('src/urisys_lab/sessions/lab_flows.py', '_run_single_lab_flow', 1, 10, 11).
python_function('src/urisys_lab/sessions/lab_flows.py', 'session_lab_10_flows', 1, 7, 22).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'parse_lab_flow', 1, 10, 10).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'flow_step_context', 2, 6, 3).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'step_pause', 1, 6, 2).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'summarize_uri_response', 1, 11, 3).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'parse_docker_log_errors', 1, 10, 8).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'prepare_ok_target', 3, 1, 2).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'capture_rdp_screenshot', 1, 5, 4).
python_function('src/urisys_lab/sessions/lab_rdp.py', 'capture_rdp_screenshot_wait', 1, 9, 5).
python_function('src/urisys_lab/sessions/runners.py', 'session_pytest_urirdp', 1, 3, 5).
python_function('src/urisys_lab/sessions/runners.py', 'session_pytest_urisys', 1, 2, 5).
python_function('src/urisys_lab/sessions/runners.py', 'session_pytest_urisys_node', 1, 2, 5).
python_function('src/urisys_lab/sessions/runners.py', 'session_urirdp_mock_docker', 1, 5, 17).
python_function('src/urisys_lab/sessions/runners.py', '_record_health', 6, 1, 3).
python_function('src/urisys_lab/sessions/runners.py', '_bootstrap_rdp', 4, 4, 3).
python_function('src/urisys_lab/sessions/runners.py', '_read_display_env', 1, 4, 2).
python_function('src/urisys_lab/sessions/runners.py', '_call_and_record', 10, 5, 4).
python_function('src/urisys_lab/sessions/runners.py', '_session_compose_up', 4, 2, 3).
python_function('src/urisys_lab/sessions/runners.py', '_record_screenshot_step', 6, 6, 4).
python_function('src/urisys_lab/sessions/runners.py', '_record_ocr_step', 5, 6, 4).
python_function('src/urisys_lab/sessions/runners.py', '_record_click_step', 6, 7, 4).
python_function('src/urisys_lab/sessions/runners.py', '_record_flow_step', 6, 5, 9).
python_function('src/urisys_lab/sessions/runners.py', 'session_urirdp_real_docker', 1, 5, 22).
python_function('src/urisys_lab/sessions/runners.py', 'session_urirdp_rdp_e2e', 1, 5, 11).
python_function('src/urisys_lab/sessions/runners.py', 'session_automation_lab', 1, 13, 18).
python_function('src/urisys_lab/sessions/runners.py', '_monorepo_root', 0, 4, 1).
python_function('src/urisys_lab/sessions/runners.py', 'session_urisys_node_docker_gui', 1, 7, 11).
python_function('src/urisys_lab/sessions/runners.py', 'session_office_simulate', 1, 7, 11).
python_function('src/urisys_lab/sessions/runners.py', 'session_office_simulate_lenovo', 1, 6, 10).
python_function('src/urisys_lab/sessions/runners.py', 'session_office_writer', 1, 7, 11).
python_function('src/urisys_lab/sessions/runners.py', 'session_email_mailpit', 1, 7, 11).
python_function('src/urisys_lab/sessions/util.py', 'run_id', 0, 1, 2).
python_function('src/urisys_lab/sessions/util.py', 'http_json', 4, 9, 11).
python_function('src/urisys_lab/sessions/util.py', 'wait_health', 3, 3, 5).
python_function('src/urisys_lab/sessions/util.py', 'compose_cmd', 0, 4, 3).
python_function('src/urisys_lab/sessions/util.py', 'run_cmd', 1, 6, 8).
python_function('src/urisys_lab/sessions/util.py', 'write_meta', 1, 1, 3).
python_function('src/urisys_lab/sessions/util.py', 'read_meta', 1, 3, 3).
python_function('src/urisys_lab/sessions/util.py', 'finalize_session', 4, 5, 10).
python_function('src/urisys_lab/sessions/util.py', 'docker_logs', 4, 3, 3).
python_function('src/urisys_lab/sessions/util.py', 'copy_container_file', 3, 2, 4).
python_function('src/urisys_lab/sessions/util.py', 'copy_host_screenshot', 3, 2, 5).
python_function('src/urisys_lab/sessions/util.py', 'file_md5', 1, 2, 4).
python_function('src/urisys_lab/sessions/util.py', 'sleep_ports', 0, 1, 1).
python_function('src/urisys_lab/sessions/util.py', 'prepare_urirdp_data', 1, 4, 5).
python_function('tests/conftest.py', '_tellmesh_root', 0, 6, 5).
python_function('tests/conftest.py', '_ensure_siblings', 0, 6, 5).
python_function('tests/conftest.py', '_cleanup_markpact_embedded_imports', 0, 1, 2).
python_function('tests/pack_import_isolation.py', '_is_embedded_pack_module', 1, 3, 2).
python_function('tests/pack_import_isolation.py', '_is_ephemeral_path', 1, 2, 1).
python_function('tests/pack_import_isolation.py', 'reset_embedded_pack_imports', 0, 8, 5).
python_function('tests/test_analyze_strict.py', '_analyze_strict', 1, 5, 4).
python_function('tests/test_analyze_strict.py', 'test_machine_cycle_analyze_strict_passes', 0, 2, 4).
python_function('tests/test_analyze_strict.py', 'test_extend_tellmesh_includes_urioperators', 0, 1, 3).
python_function('tests/test_bootstrap.py', '_load_module', 2, 2, 3).
python_function('tests/test_bootstrap.py', 'test_bootstrap_import_does_not_require_uri_control', 0, 2, 2).
python_function('tests/test_bootstrap.py', 'test_cli_import_does_not_require_uri_control', 0, 3, 1).
python_function('tests/test_bootstrap.py', 'test_missing_uricore_payload', 0, 4, 2).
python_function('tests/test_bootstrap.py', 'test_doctor_subcommand_via_bootstrap', 0, 6, 4).
python_function('tests/test_capability_conformance.py', 'test_capability_pack_analyze_conformance', 3, 6, 5).
python_function('tests/test_contract_gen.py', 'test_manifest_to_contract_maps_kinds_and_approval', 0, 12, 2).
python_function('tests/test_contract_gen.py', 'test_generated_contract_validates', 1, 4, 5).
python_function('tests/test_contract_gen.py', 'test_self_drift_is_clean', 0, 2, 3).
python_function('tests/test_contract_gen.py', 'test_drift_detected', 0, 5, 5).
python_function('tests/test_contract_gen.py', 'test_existing_repo_contract_has_no_core_drift', 0, 2, 3).
python_function('tests/test_desktop_automation_processes.py', 'test_desktop_automation_validates_and_analyzes', 0, 6, 6).
python_function('tests/test_desktop_automation_processes.py', 'test_desktop_automation_embedded_approval_test', 1, 3, 4).
python_function('tests/test_desktop_automation_processes.py', 'test_desktop_gui_flow_dry_run', 2, 2, 5).
python_function('tests/test_desktop_automation_processes.py', 'test_desktop_install_flow_dry_run_with_resolver', 2, 2, 6).
python_function('tests/test_doctor.py', 'test_doctor_ok_in_dev_env', 0, 8, 1).
python_function('tests/test_doctor.py', 'test_doctor_fails_high_min_version', 0, 3, 2).
python_function('tests/test_doctor.py', 'test_doctor_hints_include_node_serve', 0, 2, 2).
python_function('tests/test_doctor_uricore.py', 'test_check_uricore_authentic_fails_on_squatter', 0, 7, 4).
python_function('tests/test_golden_analyze.py', '_analyze_snapshot', 1, 3, 3).
python_function('tests/test_golden_analyze.py', 'test_analyze_golden_snapshot', 2, 3, 6).
python_function('tests/test_http_server.py', '_start', 0, 1, 5).
python_function('tests/test_http_server.py', '_get', 2, 1, 4).
python_function('tests/test_http_server.py', 'test_health_exact_shape_and_cors', 0, 4, 4).
python_function('tests/test_http_server.py', 'test_routes_are_full_dicts_not_flattened', 0, 5, 4).
python_function('tests/test_http_server.py', 'test_options_preflight_204', 0, 2, 4).
python_function('tests/test_http_server.py', 'test_events_endpoint', 0, 2, 3).
python_function('tests/test_init.py', 'test_init_dry_run_via_bootstrap', 0, 8, 4).
python_function('tests/test_init.py', 'test_run_init_skip_pip_writes_env', 1, 5, 4).
python_function('tests/test_init.py', 'test_pip_install_failure', 0, 3, 2).
python_function('tests/test_kvm_pack_pyprojects.py', '_name', 1, 1, 2).
python_function('tests/test_kvm_pack_pyprojects.py', '_deps', 1, 1, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_uricore_sibling_pyproject', 0, 3, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_each_kvm_pack_has_sibling_pyproject', 0, 4, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_sibling_pack_pyprojects_depend_on_uricore', 0, 3, 3).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_urillm_imports_uri_control_env_not_urikvmedge', 0, 4, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_urisys_root_uv_sources_point_to_siblings', 0, 4, 4).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_vendored_kvm_pack_dirs_removed', 0, 3, 1).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_urikvmedge_promoted_to_sibling', 0, 4, 3).
python_function('tests/test_machine_cycle_process.py', 'test_machine_cycle_process_validates_and_analyzes', 0, 7, 5).
python_function('tests/test_machine_cycle_process.py', 'test_machine_cycle_compiles_urisys_flow_handler', 1, 5, 6).
python_function('tests/test_machine_cycle_process.py', 'test_machine_cycle_requires_approval_without_deps', 1, 3, 8).
python_function('tests/test_machine_cycle_process.py', 'test_machine_cycle_risk_requires_dry_run_and_audit', 1, 5, 8).
python_function('tests/test_machine_cycle_process.py', 'test_machine_cycle_embedded_markpact_test_policy_only', 1, 4, 5).
python_function('tests/test_machine_cycle_process.py', 'test_machine_cycle_flow_dry_run_with_tellmesh', 2, 6, 5).
python_function('tests/test_markpact.py', 'test_markpact_validate', 0, 5, 2).
python_function('tests/test_markpact.py', 'test_markpact_validate_contract', 0, 5, 2).
python_function('tests/test_markpact.py', 'test_markpact_validate_implementation', 0, 4, 2).
python_function('tests/test_markpact.py', 'test_markpact_validate_bundle', 0, 3, 2).
python_function('tests/test_markpact.py', 'test_markpact_compile_and_call', 1, 5, 7).
python_function('tests/test_markpact.py', 'test_uri_controller_loads_markpact_directly', 1, 4, 4).
python_function('tests/test_markpact.py', 'test_markpact_embedded_tests', 1, 3, 3).
python_function('tests/test_markpact.py', 'test_build_route_shape', 0, 7, 2).
python_function('tests/test_markpact_analyzer_rules.py', 'test_mp001_rule_isolated', 0, 3, 4).
python_function('tests/test_markpact_analyzer_rules.py', 'test_mp002_rule_isolated', 0, 3, 4).
python_function('tests/test_markpact_analyzer_rules.py', 'test_mp006_rule_isolated', 0, 3, 4).
python_function('tests/test_markpact_analyzer_rules.py', 'test_mp009_rule_isolated', 0, 3, 5).
python_function('tests/test_markpact_analyzer_rules.py', 'test_mp010_rule_isolated', 0, 4, 4).
python_function('tests/test_markpact_contract_materialize.py', 'test_gen_contract_matches_manifest_no_drift', 0, 4, 6).
python_function('tests/test_markpact_contract_materialize.py', 'test_contract_validates_but_does_not_compile', 0, 3, 6).
python_function('tests/test_markpact_contract_materialize.py', 'test_thin_pack_materializes_to_markpact_tree', 2, 4, 6).
python_function('tests/test_markpact_contract_materialize.py', 'test_thin_pack_routes_via_tellmesh_and_uricore', 2, 4, 11).
python_function('tests/test_markpact_contract_materialize.py', 'test_full_pack_embedded_source_runs_without_tellmesh', 1, 12, 17).
python_function('tests/test_markpact_materialize.py', 'test_materialize_unpacks_markpact_tree', 1, 6, 5).
python_function('tests/test_markpact_pack_deps.py', 'test_tellmesh_root_from_env', 1, 2, 3).
python_function('tests/test_markpact_pack_deps.py', 'test_extend_tellmesh_paths_adds_siblings', 1, 2, 5).
python_function('tests/test_markpact_pack_deps.py', 'test_extend_tellmesh_imports_uribrowserdocker', 1, 1, 5).
python_function('tests/test_markpact_profile.py', 'test_declared_schemes_from_requires', 0, 3, 2).
python_function('tests/test_markpact_profile.py', 'test_declared_schemes_legacy_flat_uses', 0, 2, 1).
python_function('tests/test_markpact_profile.py', 'test_lint_rejects_query_kind_mismatch', 0, 3, 2).
python_function('tests/test_markpact_profile.py', 'test_lint_emits_mp001_for_flat_operation', 0, 4, 2).
python_function('tests/test_markpact_profile.py', 'test_machine_cycle_analyze_v1alpha_profile', 0, 6, 4).
python_function('tests/test_markpact_profile.py', 'test_desktop_automation_analyze_has_expect_warnings_only', 0, 4, 6).
python_function('tests/test_markpact_run.py', 'test_run_pack_mode', 2, 5, 6).
python_function('tests/test_markpact_run.py', 'test_run_interface_mode', 2, 4, 5).
python_function('tests/test_markpact_run.py', 'test_run_flow_mode', 2, 4, 5).
python_function('tests/test_markpact_run.py', 'test_run_flow_fragment', 2, 5, 6).
python_function('tests/test_markpact_run.py', 'test_run_integration_flow_local_siblings', 2, 7, 8).
python_function('tests/test_markpact_run_flow.py', 'test_split_flow_ref', 0, 3, 1).
python_function('tests/test_markpact_run_flow.py', 'test_pick_flow_id_requires_fragment_when_many', 1, 1, 4).
python_function('tests/test_markpact_run_flow.py', 'test_compile_cache_hit_preserves_flow_ids', 1, 4, 2).
python_function('tests/test_markpact_run_flow.py', 'test_run_flow_use_case', 1, 6, 4).
python_function('tests/test_markpact_run_flow.py', 'test_run_flow_via_fragment', 1, 3, 1).
python_function('tests/test_markpact_run_flow.py', 'test_flow_path_for', 1, 3, 4).
python_function('tests/test_markpact_run_flow.py', 'test_run_integration_flow_local_siblings', 2, 5, 9).
python_function('tests/test_markpact_session_isolation.py', 'test_embedded_urikvm_does_not_break_integration_flow', 2, 10, 16).
python_function('tests/test_node_install.py', 'test_default_pip_specs_no_git_urls', 0, 3, 2).
python_function('tests/test_node_install.py', 'test_urisys_node_uses_release_wheel', 0, 6, 3).
python_function('tests/test_node_install.py', 'test_urisys_node_wheel_filename_pep427', 0, 3, 1).
python_function('tests/test_node_install.py', 'test_urisys_node_wheel_url_override', 0, 2, 2).
python_function('tests/test_pack_gen.py', 'test_generate_embeds_full_source', 1, 6, 4).
python_function('tests/test_pack_gen.py', 'test_unpack_and_execute_embedded_handler', 1, 11, 12).
python_function('tests/test_pack_gen.py', 'test_multi_scheme_requires_scheme_selection', 0, 2, 1).
python_function('tests/test_pack_gen.py', 'test_run_modes_interface_and_adapter', 1, 4, 4).
python_function('tests/test_pack_manager_parse.py', 'test_parse_packs_default_set', 0, 6, 1).
python_function('tests/test_pack_manager_parse.py', 'test_parse_packs_explicit_and_none_filter', 0, 7, 1).
python_function('tests/test_pack_manager_parse.py', 'test_is_all', 0, 5, 1).
python_function('tests/test_pack_manager_parse.py', 'test_parse_markpacts', 0, 6, 1).
python_function('tests/test_pack_manager_sibling.py', 'test_sibling_manifest_path_finds_nested_pack', 1, 4, 5).
python_function('tests/test_pack_manager_sibling.py', 'test_sibling_manifest_path_finds_browser_docker', 1, 3, 5).
python_function('tests/test_pack_manager_sibling.py', 'test_pack_manager_all_loads_sibling_manifests', 1, 5, 7).
python_function('tests/test_platform_export.py', 'test_collect_process_uris_machine_cycle', 0, 5, 3).
python_function('tests/test_platform_export.py', 'test_collect_process_uris_desktop', 0, 4, 4).
python_function('tests/test_platform_export.py', 'test_build_resolver_yaml_has_v1_metadata', 0, 4, 1).
python_function('tests/test_platform_export.py', 'test_export_platform_artifacts_writes_files', 1, 6, 5).
python_function('tests/test_process_conformance.py', 'test_process_flow_conformance_dry_run', 5, 4, 8).
python_function('tests/test_pypi_metadata.py', 'test_validate_pypi_metadata_script_exists', 0, 2, 1).
python_function('tests/test_pypi_metadata.py', 'test_built_wheel_has_no_direct_url_requires_dist', 0, 3, 6).
python_function('tests/test_pypi_metadata.py', 'test_pyproject_runtime_deps_have_no_direct_urls', 0, 4, 2).
python_function('tests/test_python_compat.py', 'test_python_version_gate', 4, 2, 4).
python_function('tests/test_python_compat.py', 'test_current_python_supported', 0, 5, 2).
python_function('tests/test_run_expectations.py', 'test_screen_changed_uses_baseline_not_previous_flow', 0, 2, 1).
python_function('tests/test_run_expectations.py', 'test_screen_changed_fails_when_equal_baseline', 0, 3, 2).
python_function('tests/test_run_expectations.py', 'test_ocr_contains_from_pipeline', 0, 2, 1).
python_function('tests/test_session_core.py', 'test_step_ok_variants', 0, 8, 1).
python_function('tests/test_session_core.py', 'test_image_ext', 0, 5, 1).
python_function('tests/test_session_core.py', 'test_write_base64_image_roundtrip', 1, 3, 5).
python_function('tests/test_session_core.py', 'test_extract_step_screenshots_strips_base64', 1, 6, 2).
python_function('tests/test_session_core.py', 'test_extract_handles_nested_shots', 1, 2, 1).
python_function('tests/test_session_core.py', 'test_extract_ignores_non_image_response', 1, 2, 1).
python_function('tests/test_session_core.py', 'test_backfill_session_images', 1, 3, 5).
python_function('tests/test_session_report_events.py', 'test_summarize_events_api_json', 1, 4, 3).
python_function('tests/test_session_report_events.py', 'test_summarize_events_jsonl', 1, 4, 5).
python_function('tests/test_showcase.py', 'test_showcase_validates', 0, 4, 2).
python_function('tests/test_showcase.py', 'test_analyze_classifies_use_case_and_integration', 0, 8, 3).
python_function('tests/test_showcase.py', 'test_compile_extracts_flows_and_protos', 1, 6, 4).
python_function('tests/test_showcase.py', 'test_classify_flow_reports_undeclared_uses', 0, 4, 2).
python_function('tests/test_showcase.py', 'test_declared_uses_strips_scheme_suffix', 0, 2, 1).
python_function('tests/test_source_manager.py', 'test_fetch_local_file', 1, 4, 5).
python_function('tests/test_source_manager.py', 'test_fetch_github_raw', 2, 3, 4).
python_function('tests/test_uricore_install.py', 'test_wheel_url_default', 0, 3, 3).
python_function('tests/test_uricore_install.py', 'test_wrong_uricore_detected_when_squatter_present', 0, 2, 2).
python_function('tests/test_uricore_install.py', 'test_not_wrong_when_uri_control_present', 0, 2, 2).
python_function('tests/test_uricore_install.py', 'test_diagnose_includes_wheel_url', 0, 3, 2).
python_function('tests/test_urirouter_install.py', 'test_wheel_url_default', 0, 3, 3).
python_function('tests/test_urirouter_install.py', 'test_diagnose_includes_wheel_url', 0, 3, 1).
python_function('tests/test_urisys.py', 'test_call_browser_open', 1, 4, 6).
python_function('tests/test_urisys.py', 'test_routes_load', 1, 5, 7).
python_function('tests/test_urisys.py', 'test_all_skips_uninstalled_packs', 2, 3, 6).
python_function('tests/test_urisys.py', 'test_explicit_missing_pack_raises_helpful_error', 0, 1, 3).
python_function('tests/test_urisys_flow_handler.py', 'test_process_capability_runs_embedded_flow_via_urisys_handler', 1, 6, 9).
python_function('tests/test_vendored_sync.py', '_run_check', 1, 1, 2).
python_function('tests/test_vendored_sync.py', 'test_pack_sync_script_exists', 0, 4, 1).
python_function('tests/test_vendored_sync.py', 'test_sibling_repos_exist', 0, 4, 1).
python_function('tests/test_vendored_sync.py', 'test_promoted_packs_not_vendored_in_monorepo', 0, 5, 4).
python_function('tests/test_vendored_sync.py', 'test_sibling_repos_have_pyproject', 0, 3, 1).
python_function('tests/test_vendored_sync.py', 'test_no_drift_promoted_packs', 0, 3, 3).

% ── Python Classes ───────────────────────────────────────
python_class('scripts/pack_registry.py', 'PackSpec').
python_class('scripts/report/models.py', 'StepResult').
python_class('scripts/report/models.py', 'SessionReport').
python_method('SessionReport', 'passed', 0, 3, 1).
python_method('SessionReport', 'failed', 0, 3, 1).
python_class('scripts/report/models.py', 'RunAnalysis').
python_method('RunAnalysis', 'all_passed', 0, 2, 1).
python_class('scripts/report/models.py', 'Finding').
python_class('scripts/report/models.py', 'FlowOutcome').
python_method('FlowOutcome', 'no_visible_effect', 0, 2, 0).
python_method('FlowOutcome', 'vision_decided', 0, 2, 1).
python_class('src/urisys/cli/protocol.py', 'CliCommand').
python_method('CliCommand', '__call__', 1, 1, 0).
python_class('src/urisys/controllers/flow_controller.py', 'FlowController').
python_method('FlowController', '__init__', 1, 1, 1).
python_method('FlowController', 'run', 1, 6, 8).
python_method('FlowController', 'close', 0, 1, 1).
python_class('src/urisys/controllers/server_controller.py', 'ServerController').
python_method('ServerController', '__init__', 0, 1, 1).
python_method('ServerController', 'serve_forever', 0, 1, 2).
python_class('src/urisys/controllers/uri_controller.py', 'UriController').
python_method('UriController', '__init__', 1, 1, 4).
python_method('UriController', 'call', 2, 3, 3).
python_method('UriController', 'explain', 1, 1, 1).
python_method('UriController', 'routes', 0, 1, 1).
python_method('UriController', 'close', 0, 1, 1).
python_class('src/urisys/doctor.py', 'Check').
python_class('src/urisys/http_server.py', '_ControllerRuntime').
python_method('_ControllerRuntime', '__init__', 1, 1, 0).
python_method('_ControllerRuntime', 'call', 3, 3, 4).
python_class('src/urisys/managers/bridge_manager.py', 'BridgeManager').
python_method('BridgeManager', 'call_http', 5, 3, 7).
python_class('src/urisys/managers/event_manager.py', 'EventManager').
python_method('EventManager', '__init__', 1, 1, 2).
python_method('EventManager', 'list_events', 0, 1, 2).
python_class('src/urisys/managers/markpact_manager.py', 'MarkpactManager').
python_method('MarkpactManager', '__init__', 1, 1, 2).
python_method('MarkpactManager', 'read_blocks', 1, 1, 1).
python_method('MarkpactManager', 'source_hash', 1, 1, 1).
python_method('MarkpactManager', 'load_pack_block', 1, 1, 1).
python_method('MarkpactManager', 'validate', 1, 1, 1).
python_method('MarkpactManager', 'compile', 1, 1, 1).
python_method('MarkpactManager', 'analyze', 1, 1, 1).
python_method('MarkpactManager', 'manifest_path_for', 1, 1, 1).
python_method('MarkpactManager', 'run_tests', 1, 1, 1).
python_method('MarkpactManager', '_build_route', 0, 1, 1).
python_method('MarkpactManager', '_compile_manifest', 0, 1, 1).
python_class('src/urisys/managers/markpact_models.py', 'MarkpactBlock').
python_class('src/urisys/managers/markpact_models.py', 'CompiledMarkpact').
python_method('CompiledMarkpact', 'to_dict', 0, 6, 2).
python_class('src/urisys/managers/markpact_models.py', 'MarkpactError').
python_class('src/urisys/managers/markpact_profile.py', 'LintIssue').
python_class('src/urisys/managers/pack_manager.py', 'PackManager').
python_method('PackManager', '__init__', 1, 1, 6).
python_method('PackManager', '_split_specs', 1, 6, 4).
python_method('PackManager', '_is_all', 1, 4, 1).
python_method('PackManager', 'parse_packs', 1, 8, 2).
python_method('PackManager', 'parse_markpacts', 1, 1, 1).
python_method('PackManager', 'resolve_package_name', 1, 1, 1).
python_method('PackManager', '_is_markpact_path', 1, 3, 2).
python_method('PackManager', '_is_manifest_path', 1, 4, 1).
python_method('PackManager', '_resolve_importable_manifest', 1, 5, 7).
python_method('PackManager', '_handle_missing_manifest', 3, 6, 3).
python_method('PackManager', 'manifest_paths', 0, 8, 11).
python_method('PackManager', 'create_registry', 0, 1, 2).
python_method('PackManager', 'capabilities', 0, 2, 1).
python_method('PackManager', 'close', 0, 1, 1).
python_method('PackManager', '__enter__', 0, 1, 0).
python_method('PackManager', '__exit__', 3, 1, 1).
python_class('src/urisys/managers/policy_manager.py', 'PolicyManager').
python_method('PolicyManager', 'build_context', 0, 2, 1).
python_class('src/urisys/managers/route_manager.py', 'RouteManager').
python_method('RouteManager', '__init__', 1, 1, 0).
python_method('RouteManager', 'explain', 1, 1, 1).
python_method('RouteManager', 'list_routes', 0, 2, 0).
python_class('src/urisys/managers/runtime_manager.py', 'RuntimeManager').
python_method('RuntimeManager', '__init__', 1, 2, 1).
python_method('RuntimeManager', 'create_runtime', 0, 1, 5).
python_method('RuntimeManager', 'close', 0, 1, 1).
python_method('RuntimeManager', '__enter__', 0, 1, 0).
python_method('RuntimeManager', '__exit__', 3, 1, 1).
python_class('src/urisys/managers/source_manager.py', 'SourceError').
python_class('src/urisys/managers/source_manager.py', 'SourceManager').
python_method('SourceManager', '__init__', 1, 1, 1).
python_method('SourceManager', 'is_remote_source', 1, 3, 4).
python_method('SourceManager', 'resolve', 1, 1, 1).
python_method('SourceManager', 'fetch', 1, 11, 17).
python_method('SourceManager', '_result', 2, 3, 4).
python_method('SourceManager', '_cache_dir', 1, 1, 3).
python_method('SourceManager', '_http_download', 1, 2, 4).
python_method('SourceManager', '_fetch_http', 1, 6, 11).
python_method('SourceManager', '_fetch_github_uri', 1, 4, 6).
python_method('SourceManager', '_fetch_github_raw', 4, 5, 10).
python_method('SourceManager', '_fetch_git', 1, 11, 18).
python_method('SourceManager', '_fetch_zip', 1, 9, 16).
python_class('src/urisys/markpact/analyzer/context.py', 'MarkpactLintContext').
python_class('src/urisys/markpact/analyzer/rules/base.py', 'MarkpactRule').
python_method('MarkpactRule', 'check', 1, 1, 0).
python_class('src/urisys/markpact/analyzer/rules/capabilities.py', 'MP001NamespacedOperation').
python_method('MP001NamespacedOperation', 'check', 1, 7, 6).
python_class('src/urisys/markpact/analyzer/rules/capabilities.py', 'MP002QueryKind').
python_method('MP002QueryKind', 'check', 1, 7, 6).
python_class('src/urisys/markpact/analyzer/rules/capabilities.py', 'MP003CommandKind').
python_method('MP003CommandKind', 'check', 1, 7, 6).
python_class('src/urisys/markpact/analyzer/rules/capabilities.py', 'MP004CommandApproval').
python_method('MP004CommandApproval', 'check', 1, 7, 6).
python_class('src/urisys/markpact/analyzer/rules/capabilities.py', 'MP005ProcessHandler').
python_method('MP005ProcessHandler', 'check', 1, 7, 6).
python_class('src/urisys/markpact/analyzer/rules/flows.py', 'MP007ProcessExpect').
python_method('MP007ProcessExpect', 'check', 1, 4, 3).
python_class('src/urisys/markpact/analyzer/rules/flows.py', 'MP008ImplicitLatest').
python_method('MP008ImplicitLatest', 'check', 1, 4, 3).
python_class('src/urisys/markpact/analyzer/rules/pack.py', 'MP009ProcessRequiresSchemes').
python_method('MP009ProcessRequiresSchemes', 'check', 1, 6, 2).
python_class('src/urisys/markpact/analyzer/rules/pack.py', 'MP010RequiresCapabilitiesNamespaced').
python_method('MP010RequiresCapabilitiesNamespaced', 'check', 1, 6, 5).
python_class('src/urisys/markpact/analyzer/rules/schemes.py', 'MP006UndeclaredScheme').
python_method('MP006UndeclaredScheme', 'check', 1, 2, 1).
python_class('src/urisys/markpact/compiler.py', 'MarkpactCompiler').
python_method('MarkpactCompiler', '__init__', 1, 1, 1).
python_method('MarkpactCompiler', 'compile', 1, 7, 24).
python_class('src/urisys/markpact/run/context.py', 'RunContext').
python_class('src/urisys/markpact/run/modes/adapter.py', 'AdapterMode').
python_method('AdapterMode', 'run', 1, 3, 3).
python_class('src/urisys/markpact/run/modes/base.py', 'MarkpactRunMode').
python_method('MarkpactRunMode', 'run', 1, 1, 0).
python_class('src/urisys/markpact/run/modes/flow.py', 'FlowMode').
python_method('FlowMode', 'run', 1, 9, 11).
python_class('src/urisys/markpact/run/modes/interface.py', 'InterfaceMode').
python_method('InterfaceMode', 'run', 1, 2, 1).
python_class('src/urisys/markpact/run/modes/pack.py', 'PackMode').
python_method('PackMode', 'run', 1, 1, 2).
python_class('src/urisys/markpact/run/modes/service.py', 'ServiceMode').
python_method('ServiceMode', 'run', 1, 6, 5).
python_class('tests/test_python_compat.py', '_FakeVersionInfo').
python_method('_FakeVersionInfo', '__init__', 3, 1, 0).
python_method('_FakeVersionInfo', '__getitem__', 1, 1, 0).
python_method('_FakeVersionInfo', '__ge__', 1, 1, 0).
python_method('_FakeVersionInfo', '__lt__', 1, 1, 0).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PIP_DISABLE_PIP_VERSION_CHECK', '1', 'Quiet pip in venv/scripts (suppress "new release of pip" notices)').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-api-smoke.testql.toon.yaml', 'api').
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-api-smoke.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
```

## Call Graph

*342 nodes · 500 edges · 62 modules · CC̄=4.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `build_parser` *(in src.urisys.cli.parser)* | 1 | 1 | 108 | **109** |
| `print` *(in scripts.analyze-thin-markpacts)* | 0 | 70 | 0 | **70** |
| `run_cmd` *(in src.urisys_lab.sessions.util)* | 6 | 30 | 12 | **42** |
| `export_platform_artifacts` *(in src.urisys.markpact.platform_export)* | 7 | 2 | 35 | **37** |
| `run_flow` *(in src.urisys_lab.lenovo.cli)* | 14 ⚠ | 3 | 33 | **36** |
| `generate_pack_markpact` *(in src.urisys.managers.markpact_pack_gen)* | 10 ⚠ | 1 | 33 | **34** |
| `finalize_session` *(in src.urisys_lab.sessions.util)* | 5 | 21 | 13 | **34** |
| `session_lab_10_flows` *(in scripts.test_sessions.lab_flows)* | 7 | 0 | 33 | **33** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.28s
# nodes: 342 | edges: 500 | modules: 62
# CC̄=4.2

HUBS[20]:
  src.urisys.cli.parser.build_parser
    CC=1  in:1  out:108  total:109
  scripts.analyze-thin-markpacts.print
    CC=0  in:70  out:0  total:70
  src.urisys_lab.sessions.util.run_cmd
    CC=6  in:30  out:12  total:42
  src.urisys.markpact.platform_export.export_platform_artifacts
    CC=7  in:2  out:35  total:37
  src.urisys_lab.lenovo.cli.run_flow
    CC=14  in:3  out:33  total:36
  src.urisys.managers.markpact_pack_gen.generate_pack_markpact
    CC=10  in:1  out:33  total:34
  src.urisys_lab.sessions.util.finalize_session
    CC=5  in:21  out:13  total:34
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  src.urisys.managers.contract_gen._diff_section
    CC=8  in:1  out:32  total:33
  src.urisys_lab.sessions.runners.session_automation_lab
    CC=13  in:1  out:31  total:32
  src.urisys_lab.sessions.cli.main
    CC=13  in:0  out:32  total:32
  src.urisys_lab.core.now_iso
    CC=1  in:29  out:2  total:31
  src.urisys_lab.sessions.runners.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  src.urisys.markpact.tests.run_markpact_tests
    CC=12  in:1  out:27  total:28
  src.urisys.cli.helpers.print_json
    CC=1  in:26  out:2  total:28
  src.urisys.markpact.compiler.MarkpactCompiler.compile
    CC=7  in:0  out:27  total:27
  src.urisys.managers.markpact_run_flow.run_markpact_flow
    CC=14  in:1  out:26  total:27
  src.urisys.doctor.run_doctor
    CC=11  in:3  out:22  total:25
  src.urisys_lab.sessions.util.http_json
    CC=9  in:7  out:18  total:25
  src.urisys.markpact.validate_pack.validate_markpact_file
    CC=12  in:1  out:24  total:25

MODULES:
  scripts.analyze-thin-markpacts  [1 funcs]
    print  CC=0  out:0
  scripts.office-simulate-loop  [1 funcs]
    call_uri  CC=4  out:11
  scripts.test_sessions.expectations  [9 funcs]
    _min_vision_confidence  CC=4  out:3
    _ocr_contains  CC=5  out:6
    _opened_url_contains  CC=11  out:16
    _screen_changed  CC=5  out:1
    _screen_changed_since_previous  CC=5  out:1
    evaluate_expectations  CC=3  out:10
    flow_expectations  CC=5  out:6
    ocr_texts  CC=11  out:10
    vision_confidences  CC=11  out:11
  scripts.test_sessions.lab_flows  [5 funcs]
    _capture_flow_screenshot  CC=13  out:10
    _flow_step_detail  CC=4  out:2
    _lab_bootstrap  CC=5  out:7
    _run_single_lab_flow  CC=10  out:19
    session_lab_10_flows  CC=7  out:33
  scripts.test_sessions.lab_rdp  [3 funcs]
    capture_rdp_screenshot  CC=5  out:6
    capture_rdp_screenshot_wait  CC=9  out:6
    prepare_ok_target  CC=1  out:2
  src.urisys.bootstrap  [5 funcs]
    _doctor_main  CC=3  out:7
    _init_main  CC=6  out:18
    _missing_uricore_payload  CC=1  out:1
    _print_json  CC=1  out:2
    main  CC=8  out:6
  src.urisys.cli.commands.markpact  [15 funcs]
    _apply_strict_operations  CC=8  out:2
    _apply_strict_profile  CC=4  out:2
    _run_path_command  CC=6  out:5
    cmd_analyze  CC=5  out:9
    cmd_compile  CC=1  out:3
    cmd_contract  CC=6  out:14
    cmd_export_platform  CC=3  out:8
    cmd_markpact  CC=11  out:16
    cmd_materialize  CC=3  out:8
    cmd_pack  CC=6  out:10
  src.urisys.cli.commands.node  [1 funcs]
    cmd_node  CC=6  out:8
  src.urisys.cli.commands.runtime  [4 funcs]
    cmd_events  CC=1  out:3
    cmd_flow  CC=1  out:4
    cmd_serve  CC=1  out:3
    cmd_uri  CC=4  out:9
  src.urisys.cli.commands.setup  [2 funcs]
    cmd_doctor  CC=3  out:3
    cmd_init  CC=6  out:7
  src.urisys.cli.errors  [1 funcs]
    handle_cli_error  CC=8  out:13
  src.urisys.cli.helpers  [3 funcs]
    json_arg  CC=3  out:5
    print_json  CC=1  out:2
    resolve_markpact_source  CC=2  out:3
  src.urisys.cli.main  [1 funcs]
    main  CC=3  out:5
  src.urisys.cli.parser  [2 funcs]
    add_runtime_flags  CC=1  out:4
    build_parser  CC=1  out:108
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [2 funcs]
    __init__  CC=1  out:1
    serve_forever  CC=1  out:3
  src.urisys.doctor  [11 funcs]
    _check_cli_path  CC=3  out:6
    _check_import  CC=5  out:12
    _check_min_version  CC=6  out:5
    _check_python  CC=3  out:3
    _check_uricore_authentic  CC=6  out:11
    _check_uricore_dist  CC=3  out:7
    _check_wayland_him  CC=3  out:4
    _parse_version  CC=7  out:6
    _pkg_version  CC=2  out:1
    _version_lt  CC=2  out:2
  src.urisys.flow  [2 funcs]
    iter_steps  CC=7  out:8
    load_flow  CC=3  out:5
  src.urisys.http_server  [2 funcs]
    _read_json  CC=3  out:5
    create_server  CC=1  out:13
  src.urisys.init_setup  [16 funcs]
    _build_pip_result  CC=5  out:11
    _check_node_after_install  CC=6  out:4
    _pre_repair_uricore  CC=6  out:6
    _resolve_error_hint  CC=5  out:4
    _run_doctor_check  CC=3  out:3
    _run_pip_install  CC=2  out:2
    _verify_after_install  CC=8  out:9
    _write_profile_env  CC=4  out:3
    default_node_pip_spec  CC=1  out:1
    default_pip_specs  CC=1  out:2
  src.urisys.managers.contract_gen  [9 funcs]
    _by_pattern  CC=5  out:3
    _diff_scheme_and_metadata  CC=5  out:11
    _diff_section  CC=8  out:32
    _diff_uses  CC=7  out:8
    _routes  CC=5  out:4
    diff_manifest_contract  CC=2  out:4
    manifest_to_contract  CC=11  out:19
    normalize_version  CC=6  out:8
    render_contract_markpact  CC=2  out:4
  src.urisys.managers.markpact_flows  [8 funcs]
    _provider_scheme  CC=1  out:1
    _scheme  CC=1  out:1
    classify_flow  CC=11  out:10
    declared_uses  CC=1  out:1
    extract_flows  CC=11  out:9
    extract_modules  CC=7  out:8
    extract_protos  CC=7  out:6
    flow_uris  CC=8  out:10
  src.urisys.managers.markpact_manager  [5 funcs]
    _build_route  CC=1  out:1
    _compile_manifest  CC=1  out:1
    analyze  CC=1  out:1
    run_tests  CC=1  out:1
    validate  CC=1  out:1
  src.urisys.managers.markpact_materialize  [2 funcs]
    default_materialize_root  CC=1  out:1
    materialize_markpact  CC=8  out:22
  src.urisys.managers.markpact_models  [4 funcs]
    parse_meta  CC=4  out:8
    safe_identifier  CC=3  out:6
    scheme_from_uri  CC=2  out:2
    source_hash  CC=1  out:4
  src.urisys.managers.markpact_pack_deps  [13 funcs]
    _discover_pack_modules  CC=12  out:14
    _is_capability_pack_repo  CC=4  out:3
    _is_flat_pack_repo  CC=3  out:3
    _pack_resolver  CC=2  out:0
    _register_existing_pack  CC=6  out:8
    _register_flat_pack  CC=4  out:5
    _register_sibling_packs  CC=12  out:13
    _register_uricore_utils  CC=3  out:5
    _register_urioperators  CC=6  out:7
    ensure_flow_packs  CC=2  out:3
  src.urisys.managers.markpact_pack_gen  [11 funcs]
    _build_capability  CC=11  out:13
    _embedded_flows  CC=9  out:10
    _load_manifest  CC=3  out:4
    _module_blocks  CC=3  out:7
    _pack_block  CC=9  out:13
    _proto_blocks  CC=3  out:7
    _resolve_repo_root  CC=6  out:4
    _run_block  CC=1  out:0
    find_package_dir  CC=8  out:12
    generate_pack_markpact  CC=10  out:33
  src.urisys.managers.markpact_profile  [19 funcs]
    _build_flow_profiles  CC=6  out:11
    _cap_uri  CC=3  out:3
    _cross_check_schemes  CC=9  out:8
    _flow_features  CC=6  out:9
    _flow_level_features  CC=3  out:4
    _issue  CC=1  out:1
    _issue_message  CC=1  out:0
    _required_features  CC=4  out:7
    _step_features  CC=7  out:9
    _text_pattern_features  CC=4  out:3
  src.urisys.managers.markpact_run_flow  [6 funcs]
    _split_extra  CC=7  out:8
    flow_path_for  CC=3  out:4
    packs_for_flow  CC=4  out:8
    pick_flow_id  CC=5  out:7
    run_markpact_flow  CC=14  out:26
    split_flow_ref  CC=3  out:2
  src.urisys.managers.markpact_validation  [6 funcs]
    _missing_bundle_imports  CC=6  out:6
    _validate_contract_routes  CC=11  out:15
    _validate_implementation_capabilities  CC=5  out:6
    validate_bundle  CC=9  out:15
    validate_contract  CC=13  out:21
    validate_implementation  CC=14  out:22
  src.urisys.managers.pack_manager  [5 funcs]
    _handle_missing_manifest  CC=6  out:5
    manifest_paths  CC=8  out:16
    _manifest_is_loadable  CC=5  out:7
    _repo_for_package  CC=2  out:0
    _sibling_manifest_path  CC=8  out:7
  src.urisys.markpact.analyzer.lint  [2 funcs]
    _issue_message  CC=1  out:0
    run_lint  CC=8  out:14
  src.urisys.markpact.analyzer.report  [1 funcs]
    analyze_markpact  CC=8  out:18
  src.urisys.markpact.analyzer.rules.base  [1 funcs]
    cap_uri  CC=3  out:3
  src.urisys.markpact.analyzer.rules.capabilities  [4 funcs]
    check  CC=6  out:6
    check  CC=7  out:6
    check  CC=7  out:6
    check  CC=10  out:12
  src.urisys.markpact.analyzer.rules.flows  [1 funcs]
    check  CC=4  out:3
  src.urisys.markpact.artifacts  [6 funcs]
    flows_from_cache  CC=3  out:3
    modules_from_cache  CC=4  out:3
    protos_from_cache  CC=3  out:3
    write_flows  CC=3  out:6
    write_modules  CC=2  out:5
    write_protos  CC=3  out:6
  src.urisys.markpact.blocks  [4 funcs]
    handler_blocks  CC=5  out:3
    load_yaml_blocks  CC=6  out:4
    read_blocks  CC=3  out:11
    yaml_blocks  CC=4  out:0
  src.urisys.markpact.cache  [4 funcs]
    compile_context  CC=2  out:7
    compiled_from_cache  CC=4  out:8
    ensure_importable  CC=2  out:3
    write_manifest_flows  CC=3  out:9
  src.urisys.markpact.compiler  [3 funcs]
    compile  CC=7  out:27
    _write_docs_block  CC=4  out:3
    _write_tests_block  CC=2  out:3
  src.urisys.markpact.handlers  [3 funcs]
    handler_id_from_ref  CC=2  out:2
    resolve_handler_ref  CC=7  out:8
    write_handler_modules  CC=5  out:4
  src.urisys.markpact.manifest  [7 funcs]
    _build_route_dict  CC=5  out:3
    _resolve_kind  CC=3  out:2
    _resolve_operation  CC=5  out:10
    _resolve_pattern  CC=4  out:4
    _validate_scheme  CC=2  out:2
    build_route  CC=2  out:8
    compile_manifest  CC=12  out:11
  src.urisys.markpact.pack  [4 funcs]
    capabilities  CC=6  out:5
    load_pack_block  CC=4  out:9
    package_id  CC=5  out:7
    scheme_for_pack  CC=8  out:10
  src.urisys.markpact.platform_export  [6 funcs]
    _authorities_from_flow  CC=10  out:13
    _resolve_authority  CC=9  out:7
    _target_stub  CC=11  out:1
    build_resolver_yaml  CC=5  out:3
    collect_process_uris  CC=6  out:20
    export_platform_artifacts  CC=7  out:35
  src.urisys.markpact.run  [1 funcs]
    run_markpact  CC=6  out:16
  src.urisys.markpact.run.config  [2 funcs]
    load_run_config  CC=4  out:5
    read_run_config  CC=7  out:4
  src.urisys.markpact.run.modes.adapter  [1 funcs]
    run  CC=3  out:5
  src.urisys.markpact.run.modes.flow  [4 funcs]
    run  CC=9  out:12
    _build_flow_runtime  CC=2  out:8
    _resolve_flow_ids  CC=5  out:6
    _resolve_flow_uses  CC=5  out:11
  src.urisys.markpact.run.modes.interface  [1 funcs]
    run  CC=2  out:1
  src.urisys.markpact.run.modes.pack  [1 funcs]
    run  CC=1  out:2
  src.urisys.markpact.run.modes.service  [1 funcs]
    run  CC=6  out:7
  src.urisys.markpact.run.runtime_build  [3 funcs]
    apply_resolver_config  CC=7  out:9
    build_runtime  CC=3  out:5
    routes_summary  CC=2  out:0
  src.urisys.markpact.tests  [2 funcs]
    run_markpact_tests  CC=12  out:27
    run_tests_for_path  CC=1  out:3
  src.urisys.markpact.validate_pack  [2 funcs]
    validate_markpact_file  CC=12  out:24
    validate_pack  CC=11  out:21
  src.urisys.node_install  [9 funcs]
    diagnose_urisys_node  CC=3  out:5
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    install_urisys_node  CC=7  out:12
    is_importable  CC=1  out:1
    pip_run  CC=4  out:2
    pip_spec  CC=1  out:1
    wheel_filename  CC=2  out:2
    wheel_url  CC=3  out:6
  src.urisys.uricore_install  [11 funcs]
    _dist_top_levels  CC=6  out:7
    _module_exists  CC=1  out:1
    _pkg_version  CC=2  out:1
    diagnose_uricore  CC=4  out:4
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    is_wrong_uricore_installed  CC=5  out:3
    pip_run  CC=4  out:2
    pip_spec  CC=1  out:1
    repair_uricore  CC=6  out:10
  src.urisys.urirouter_install  [6 funcs]
    _module_exists  CC=1  out:1
    diagnose_urirouter  CC=2  out:2
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    pip_spec  CC=1  out:1
    wheel_url  CC=3  out:5
  src.urisys_lab.core  [17 funcs]
    _apply_wheel_refspec  CC=4  out:4
    _resolve_wheel_args  CC=7  out:10
    _resolve_wheel_name  CC=6  out:6
    _step_ok_default  CC=7  out:8
    _wheel_version_key  CC=5  out:9
    backfill_session_images  CC=8  out:11
    expand_step_wheels  CC=4  out:7
    extract_images_from_dict  CC=8  out:15
    extract_step_screenshots  CC=5  out:7
    find_wheel_file  CC=2  out:4
  src.urisys_lab.lenovo.cli  [25 funcs]
    _check_and_restore_health  CC=4  out:5
    _maybe_run_kvm_upgrade  CC=5  out:4
    _maybe_run_node_upgrade  CC=6  out:5
    _maybe_run_playwright_upgrade  CC=5  out:4
    _md_lessons  CC=6  out:8
    _needs_node_upgrade  CC=4  out:2
    _poll_health_after_restart  CC=9  out:14
    _run_extract_images  CC=2  out:8
    _run_flows  CC=7  out:12
    _run_host_restart_and_wait_step  CC=11  out:17
  src.urisys_lab.sessions.cli  [1 funcs]
    main  CC=13  out:32
  src.urisys_lab.sessions.runners  [22 funcs]
    _bootstrap_rdp  CC=4  out:3
    _call_and_record  CC=5  out:4
    _monorepo_root  CC=4  out:3
    _read_display_env  CC=4  out:4
    _record_click_step  CC=7  out:10
    _record_flow_step  CC=5  out:9
    _record_health  CC=1  out:3
    _record_ocr_step  CC=6  out:8
    _record_screenshot_step  CC=6  out:8
    _session_compose_up  CC=2  out:5
  src.urisys_lab.sessions.util  [12 funcs]
    compose_cmd  CC=4  out:4
    copy_container_file  CC=2  out:4
    docker_logs  CC=3  out:3
    file_md5  CC=2  out:4
    finalize_session  CC=5  out:13
    http_json  CC=9  out:18
    prepare_urirdp_data  CC=4  out:6
    read_meta  CC=3  out:3
    run_cmd  CC=6  out:12
    sleep_ports  CC=1  out:1

EDGES:
  src.urisys.uricore_install.wheel_url → src.urisys.uricore_install.github_owner
  src.urisys.uricore_install.wheel_url → src.urisys.uricore_install.github_version
  src.urisys.uricore_install.pip_spec → src.urisys.uricore_install.wheel_url
  src.urisys.uricore_install.is_wrong_uricore_installed → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.is_wrong_uricore_installed → src.urisys.uricore_install._dist_top_levels
  src.urisys.uricore_install.is_wrong_uricore_installed → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install.pip_spec
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.pip_run
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.wheel_url
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.diagnose_uricore
  src.urisys.bootstrap._print_json → scripts.analyze-thin-markpacts.print
  src.urisys.bootstrap._doctor_main → src.urisys.doctor.run_doctor
  src.urisys.bootstrap._doctor_main → src.urisys.bootstrap._print_json
  src.urisys.bootstrap._init_main → src.urisys.init_setup.run_init
  src.urisys.bootstrap._init_main → src.urisys.bootstrap._print_json
  src.urisys.bootstrap.main → src.urisys.bootstrap._doctor_main
  src.urisys.bootstrap.main → src.urisys.bootstrap._init_main
  src.urisys.bootstrap.main → src.urisys.bootstrap._print_json
  src.urisys.bootstrap.main → src.urisys.bootstrap._missing_uricore_payload
  src.urisys.doctor._version_lt → src.urisys.doctor._parse_version
  src.urisys.doctor._check_import → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._version_lt
  src.urisys.doctor._check_uricore_authentic → src.urisys.uricore_install.diagnose_uricore
  src.urisys.doctor._check_uricore_authentic → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.doctor._check_uricore_authentic → src.urisys.uricore_install.wheel_url
  src.urisys.doctor._check_uricore_dist → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_uricore_dist → src.urisys.uricore_install.wheel_url
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_uricore_authentic
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_min_version
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_wayland_him
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_python
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_cli_path
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_uricore_dist
  src.urisys.init_setup.default_pip_specs → src.urisys.uricore_install.pip_spec
  src.urisys.init_setup.verify_uri_control → src.urisys.uricore_install.diagnose_uricore
  src.urisys.init_setup.verify_uri_control → src.urisys.uricore_install.wheel_url
  src.urisys.init_setup.write_env_file → src.urisys.init_setup.render_env_shell
  src.urisys.init_setup._pre_repair_uricore → src.urisys.uricore_install.repair_uricore
  src.urisys.init_setup._pre_repair_uricore → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.init_setup._pre_repair_uricore → src.urisys.uricore_install.wheel_url
  src.urisys.init_setup._build_pip_result → src.urisys.init_setup.pip_install_specs
  src.urisys.init_setup._build_pip_result → src.urisys.node_install.install_urisys_node
  src.urisys.init_setup._build_pip_result → src.urisys.init_setup.verify_uri_control
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Api (1)

**`Auto-generated API Smoke Tests`**
- assert `_status < 500`
- assert `_status >= 200`
- detectors: ConfigEndpointDetector

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

URI control system managers/controllers over separate uri* capability packs.
