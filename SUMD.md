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
- **version**: `0.1.39`
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
  version: 0.1.39;
}

dependencies {
  runtime: "PyYAML>=6.0, urisysedge>=0.1.0";
  dev: "pytest>=8.0, uricore, uribrowser, uridocker, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
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
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK, URISYS_URICORE_GITHUB_OWNER, URISYS_URICORE_VERSION, URISYS_URICORE_WHEEL_URL, URISYS_MIN_VERSION, URISYS_INIT_PROFILE, URISYS_NODE_HOST, URISYS_NODE_PORT, URISYS_NODE_CONFIG, WAYLAND_DISPLAY, URISYS_NODE_GITHUB_OWNER, URISYS_NODE_VERSION, URISYS_NODE_WHEEL_URL;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES, PIP_DISABLE_PIP_VERSION_CHECK;
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
  version: 0.1.39
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
PyYAML>=6.0
urisysedge>=0.1.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0
uricore
uribrowser
uridocker
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
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
# urisys | 169f 12640L | python:100,shell:66,javascript:2,less:1 | 2026-06-17
# stats: 424 func | 28 cls | 169 mod | CC̄=4.5 | critical:38 | cycles:0
# alerts[5]: CC run_init=41; CC main=36; CC session_urirdp_real_docker=30; CC main=28; CC validate_contract=23
# hotspots[5]: main fan=36; session_urirdp_real_docker fan=25; analyze_run fan=23; session_lab_10_flows fan=22; main fan=19
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[169]:
  app.doql.less,49
  examples/frontend/app.js,22
  examples/markpact/browser-call.sh,13
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
  scripts/ci-checkout-siblings.sh,52
  scripts/ci-install-siblings.sh,29
  scripts/deploy-lenovo-node.sh,72
  scripts/install-kvm-packs-editable.sh,14
  scripts/lenovo-node-session.sh,73
  scripts/office-simulate-loop.py,147
  scripts/pack_registry.py,261
  scripts/pack_sync.py,348
  scripts/paths.sh,55
  scripts/publish-pypi-packs.sh,54
  scripts/remote-node-smoke.sh,100
  scripts/report/__init__.py,62
  scripts/report/cli.py,42
  scripts/report/events.py,139
  scripts/report/lab_checks.py,189
  scripts/report/models.py,87
  scripts/report/run_analysis.py,130
  scripts/report/run_markdown.py,43
  scripts/report/session.py,106
  scripts/report/session_io.py,20
  scripts/report/session_markdown.py,121
  scripts/report/util.py,30
  scripts/run-email-mailpit-e2e.sh,134
  scripts/run-lab-e2e.sh,15
  scripts/run-lab-nightly.sh,17
  scripts/run-lab-unit-ci.sh,21
  scripts/run-nl-log-smoke.sh,44
  scripts/run-office-simulate-e2e.sh,130
  scripts/run-office-simulate-lenovo.sh,183
  scripts/run-office-writer-e2e.sh,113
  scripts/run-smoke-all.sh,25
  scripts/run-urisys-node-docker-e2e.sh,163
  scripts/run-urisys-node-docker-session.sh,7
  scripts/run_test_sessions.py,783
  scripts/session_report.py,50
  scripts/sync-vendored-pack.sh,39
  scripts/sync-vendored-urisysedge.sh,17
  scripts/test-goal.sh,12
  scripts/test-python-matrix.sh,59
  scripts/test_sessions/__init__.py,99
  scripts/test_sessions/expectations.py,154
  scripts/test_sessions/lab_flows.py,320
  scripts/test_sessions/lab_rdp.py,181
  scripts/test_sessions/util.py,210
  scripts/validate-all-markpacts.sh,54
  scripts/validate-pypi-metadata.sh,63
  src/urisys/__init__.py,4
  src/urisys/bootstrap.py,112
  src/urisys/cli.py,283
  src/urisys/controllers/__init__.py,1
  src/urisys/controllers/flow_controller.py,34
  src/urisys/controllers/server_controller.py,19
  src/urisys/controllers/uri_controller.py,34
  src/urisys/defaults.py,21
  src/urisys/doctor.py,288
  src/urisys/flow.py,26
  src/urisys/http_server.py,79
  src/urisys/init_setup.py,237
  src/urisys/managers/__init__.py,1
  src/urisys/managers/bridge_manager.py,15
  src/urisys/managers/event_manager.py,14
  src/urisys/managers/markpact_manager.py,402
  src/urisys/managers/markpact_models.py,93
  src/urisys/managers/markpact_validation.py,141
  src/urisys/managers/pack_manager.py,129
  src/urisys/managers/policy_manager.py,19
  src/urisys/managers/route_manager.py,24
  src/urisys/managers/runtime_manager.py,31
  src/urisys/managers/source_manager.py,225
  src/urisys/node_install.py,53
  src/urisys/uricore_install.py,131
  tests/test_bootstrap.py,61
  tests/test_doctor.py,29
  tests/test_doctor_uricore.py,27
  tests/test_init.py,61
  tests/test_kvm_pack_pyprojects.py,69
  tests/test_markpact.py,99
  tests/test_node_install.py,31
  tests/test_pypi_metadata.py,35
  tests/test_python_compat.py,53
  tests/test_run_expectations.py,56
  tests/test_session_report_events.py,59
  tests/test_source_manager.py,36
  tests/test_uricore_install.py,38
  tests/test_urisys.py,46
  tests/test_vendored_sync.py,58
  tree.sh,2
  uribrowser-docker/scripts/test-local.sh,9
  uribrowser-docker/scripts/test-real.sh,29
  uribrowser-docker/tests/test_browser.py,24
  urienv-docker/scripts/local-test.sh,11
  urienv-docker/scripts/test-docker.sh,5
  urienv-docker/tests/e2e_env.py,64
  urienv-docker/tests/test_urienv.py,70
  urikvm-docker/scripts/call-http.sh,6
  urikvm-docker/scripts/real_pipeline.py,96
  urikvm-docker/scripts/test-local.sh,9
  urikvm-docker/scripts/test-real.sh,48
  urikvm-docker/tests/test_him_driver.py,48
  urikvm-docker/tests/test_him_scroll.py,15
  urikvm-docker/tests/test_kvm.py,35
  urikvm-docker/tests/test_llm_plan.py,32
  urikvm-docker/tests/test_ocr_llm.py,87
  urikvm-docker/tests/test_office_mail.py,84
  urikvm-docker/tests/test_vision_dispatch.py,75
  urirdp-docker/docker/bootstrap-rdp-session.sh,112
  urirdp-docker/docker/entrypoint.sh,26
  urirdp-docker/docker/startwm.sh,7
  urirdp-docker/scripts/call-http.sh,11
  urirdp-docker/scripts/test-docker.sh,18
  urirdp-docker/scripts/test-local.sh,9
  urirdp-docker/scripts/test-rdp-real.sh,13
  urirdp-docker/scripts/test-real-docker.sh,64
  urirdp-docker/tests/e2e_rdp_real.sh,101
  urirdp-docker/tests/test_decide_dispatch.py,58
  urirdp-docker/tests/test_env_browser_routes.py,50
  urirdp-docker/tests/test_env_resolve.py,29
  urirdp-docker/tests/test_rdp_kvm.py,76
  uristepper-docker/scripts/call-http.sh,11
  uristepper-docker/scripts/test-docker.sh,8
  uristepper-docker/scripts/test-local.sh,11
  uristepper-docker/tests/e2e.py,71
  uristepper-docker/tests/test_runtime.py,53
  urisys-automation-lab/docker/entrypoint.sh,19
  urisys-automation-lab/scripts/docker-down.sh,7
  urisys-automation-lab/scripts/docker-logs.sh,7
  urisys-automation-lab/scripts/docker-smoke.sh,21
  urisys-automation-lab/scripts/docker-up.sh,22
  urisys-automation-lab/scripts/run-lab.sh,14
  urisys-automation-lab/scripts/validate-flows.sh,29
  urisys-automation-lab/server/automation_lab_server.py,248
  urisys-automation-lab/server/flow_runner.py,170
  urisys-automation-lab/server/lab_uri_adapter.py,130
  urisys-automation-lab/server/static_server.py,7
  urisys-automation-lab/tests/test_flow_08_plan.py,69
  urisys-automation-lab/tests/test_flow_09_plan.py,28
  urisys-automation-lab/tests/test_flow_expectations.py,167
  urisys-automation-lab/tests/test_lab_handlers.py,64
  urisys-automation-lab/tests/test_llm_plan_handlers.py,44
  urisys-automation-lab/web/app.js,132
  urisys-node/docker/entrypoint.sh,64
  urisys-node/scripts/install-linux.sh,17
  urisys-node/tests/test_artifact_resolver.py,96
  urisys-node/tests/test_docker_host_e2e.py,157
  urisys-node/tests/test_forward_config.py,150
  urisys-node/tests/test_forward_pack.py,75
  urisys-node/tests/test_pack_auto_install.py,108
  urisys-node/tests/test_pack_github.py,28
  urisys-node/tests/test_pack_hotload.py,65
  urisys-node/tests/test_pack_office_mail.py,30
  urisys-node/tests/test_release_hotload.py,259
  urisys-node/tests/test_uriscreen_auto.py,37
  urisys-node/tests/test_urishell.py,49
  urisys-node/tests/test_urisys_node.py,65
  urisys-node/tests/test_urisysedge_single_source.py,36
D:
  scripts/office-simulate-loop.py:
    e: call_uri,rules_tick,llm_tick,parse_args,main
    call_uri(base;uri;payload;context)
    rules_tick(base;ctx;letter)
    llm_tick(base;ctx;letter)
    parse_args(argv)
    main(argv)
  scripts/pack_registry.py:
    e: _repo,_vendored_kvm,_vendored_rdp,_vendored_node,sibling_uv_path,sibling_repo,pack_specs,sibling_repo_names,all_promoted_packs,PackSpec
    PackSpec:
    _repo(name)
    _vendored_kvm(name)
    _vendored_rdp(name)
    _vendored_node(name)
    sibling_uv_path(name)
    sibling_repo(name)
    pack_specs()
    sibling_repo_names()
    all_promoted_packs()
  scripts/pack_sync.py:
    e: repo_module_dir,vendored_module_dir,read_version,file_hash,sync_file,sync_to_repo,check_drift,_check_promoted,remove_vendored,_repo_pyproject,init_repo,promote,main
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
    e: iter_step_results,load_flow_outcomes,check_declared_expectations,check_gui_no_effect,check_vision_never_decides,_duplicate_recommendation,check_duplicate_screenshots,check_shell_baseline_duplicate,analyze_lab_flows
    iter_step_results(steps)
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
    e: infer_steps,collect_artifacts,session_status,session_duration,generate_report
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
    e: now_iso,host_id,read_json,tail
    now_iso()
    host_id()
    read_json(path)
    tail(text;limit)
  scripts/run_test_sessions.py:
    e: session_pytest_urirdp,session_pytest_urisys,session_pytest_urisys_node,session_urirdp_mock_docker,session_urirdp_real_docker,session_urirdp_rdp_e2e,session_automation_lab,_monorepo_root,session_urisys_node_docker_gui,session_office_simulate,session_office_simulate_lenovo,session_office_writer,session_email_mailpit,main
    session_pytest_urirdp(session_dir)
    session_pytest_urisys(session_dir)
    session_pytest_urisys_node(session_dir)
    session_urirdp_mock_docker(session_dir)
    session_urirdp_real_docker(session_dir)
    session_urirdp_rdp_e2e(session_dir)
    session_automation_lab(session_dir)
    _monorepo_root()
    session_urisys_node_docker_gui(session_dir)
    session_office_simulate(session_dir)
    session_office_simulate_lenovo(session_dir)
    session_office_writer(session_dir)
    session_email_mailpit(session_dir)
    main()
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
    e: now_iso,run_id,host_id,http_json,wait_health,compose_cmd,save_json,run_cmd,write_meta,read_meta,finalize_session,docker_logs,copy_container_file,copy_host_screenshot,file_md5,sleep_ports,prepare_urirdp_data
    now_iso()
    run_id()
    host_id()
    http_json(method;url;body;timeout)
    wait_health(url;attempts;delay)
    compose_cmd()
    save_json(path;data)
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
  src/urisys/__init__.py:
  src/urisys/bootstrap.py:
    e: _print_json,_missing_uricore_payload,_doctor_main,_init_main,main
    _print_json(data)
    _missing_uricore_payload(exc)
    _doctor_main(argv)
    _init_main(argv)
    main(argv)
  src/urisys/cli.py:
    e: _json_arg,print_json,_add_runtime_flags,resolve_markpact_source,build_parser,main
    _json_arg(value)
    print_json(data)
    _add_runtime_flags(parser)
    resolve_markpact_source(source)
    build_parser()
    main(argv)
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
    e: _read_json,_send,create_server
    _read_json(handler)
    _send(handler;status;data)
    create_server(host;port)
  src/urisys/init_setup.py:
    e: default_pip_specs,default_node_pip_spec,pip_install_specs,verify_uri_control,profile_env,render_env_shell,write_env_file,run_init
    default_pip_specs()
    default_node_pip_spec()
    pip_install_specs(specs)
    verify_uri_control()
    profile_env(profile)
    render_env_shell(env)
    write_env_file(path;env)
    run_init()
  src/urisys/managers/__init__.py:
  src/urisys/managers/bridge_manager.py:
    e: BridgeManager
    BridgeManager: call_http(5)  # Forwards URI envelopes to another URI server.
  src/urisys/managers/event_manager.py:
    e: EventManager
    EventManager: __init__(1),list_events(0)
  src/urisys/managers/markpact_manager.py:
    e: MarkpactManager
    MarkpactManager: __init__(1),read_blocks(1),source_hash(1),load_pack_block(1),validate(1),_validate_pack(3),_yaml_blocks(2),compile(1),manifest_path_for(1),run_tests(1),_build_route(1),_compile_manifest(1),_package_id(2),_capabilities(1),_scheme(2),_handler_blocks(1),_load_yaml_blocks(2),_handler_id_from_ref(1),_ensure_importable(1)  # Parses and compiles one-file UriPack Markpacts.
  src/urisys/managers/markpact_models.py:
    e: safe_identifier,parse_meta,scheme_from_uri,source_hash,MarkpactBlock,CompiledMarkpact,MarkpactError
    MarkpactBlock:
    CompiledMarkpact: to_dict(0)
    MarkpactError:  # Raised when a Markpact cannot be parsed, validated or compil
    safe_identifier(value)
    parse_meta(raw)
    scheme_from_uri(uri)
    source_hash(path)
  src/urisys/managers/markpact_validation.py:
    e: validate_contract,validate_bundle,validate_implementation
    validate_contract(source_path;data;source_hash)
    validate_bundle(source_path;data;source_hash)
    validate_implementation(source_path;data;source_hash)
  src/urisys/managers/pack_manager.py:
    e: PackManager
    PackManager: __init__(1),_is_all(1),parse_packs(1),parse_markpacts(1),resolve_package_name(1),_is_markpact_path(1),_is_manifest_path(1),manifest_paths(0),create_registry(0),capabilities(0),close(0),__enter__(0),__exit__(3)  # Loads separate uri* packages, plain manifest.yaml files and 
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
    SourceManager: __init__(1),is_remote_source(1),resolve(1),fetch(1),_result(2),_cache_dir(1),_fetch_http(1),_fetch_github_uri(1),_fetch_github_raw(4),_fetch_git(1),_fetch_zip(1)  # Resolve Markpact sources from local paths, HTTP(S), GitHub, 
  src/urisys/node_install.py:
    e: github_owner,github_version,wheel_url,pip_spec,is_importable,diagnose_urisys_node
    github_owner()
    github_version()
    wheel_url(version)
    pip_spec()
    is_importable()
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
  tests/test_bootstrap.py:
    e: _load_module,test_bootstrap_import_does_not_require_uri_control,test_cli_import_does_not_require_uri_control,test_missing_uricore_payload,test_doctor_subcommand_via_bootstrap
    _load_module(name;path)
    test_bootstrap_import_does_not_require_uri_control()
    test_cli_import_does_not_require_uri_control()
    test_missing_uricore_payload()
    test_doctor_subcommand_via_bootstrap()
  tests/test_doctor.py:
    e: test_doctor_ok_in_dev_env,test_doctor_fails_high_min_version,test_doctor_hints_include_node_serve
    test_doctor_ok_in_dev_env()
    test_doctor_fails_high_min_version()
    test_doctor_hints_include_node_serve()
  tests/test_doctor_uricore.py:
    e: test_check_uricore_authentic_fails_on_squatter
    test_check_uricore_authentic_fails_on_squatter()
  tests/test_init.py:
    e: test_init_dry_run_via_bootstrap,test_run_init_skip_pip_writes_env,test_pip_install_failure
    test_init_dry_run_via_bootstrap()
    test_run_init_skip_pip_writes_env(tmp_path)
    test_pip_install_failure()
  tests/test_kvm_pack_pyprojects.py:
    e: _name,test_urisysedge_sibling_pyproject,test_each_kvm_pack_has_sibling_pyproject,test_sibling_pack_pyprojects_depend_on_urisysedge,test_urillm_imports_urisysedge_not_urikvmedge,test_urisys_root_uv_sources_point_to_siblings,test_vendored_kvm_pack_dirs_removed,test_urikvmedge_promoted_to_sibling
    _name(path)
    test_urisysedge_sibling_pyproject()
    test_each_kvm_pack_has_sibling_pyproject()
    test_sibling_pack_pyprojects_depend_on_urisysedge()
    test_urillm_imports_urisysedge_not_urikvmedge()
    test_urisys_root_uv_sources_point_to_siblings()
    test_vendored_kvm_pack_dirs_removed()
    test_urikvmedge_promoted_to_sibling()
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
  tests/test_node_install.py:
    e: test_default_pip_specs_no_git_urls,test_urisys_node_uses_release_wheel,test_urisys_node_wheel_url_override
    test_default_pip_specs_no_git_urls()
    test_urisys_node_uses_release_wheel()
    test_urisys_node_wheel_url_override()
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
  tests/test_session_report_events.py:
    e: test_summarize_events_api_json,test_summarize_events_jsonl
    test_summarize_events_api_json(tmp_path)
    test_summarize_events_jsonl(tmp_path)
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
  tests/test_urisys.py:
    e: test_call_browser_open,test_routes_load,test_all_skips_uninstalled_packs,test_explicit_missing_pack_raises_helpful_error
    test_call_browser_open(tmp_path)
    test_routes_load(tmp_path)
    test_all_skips_uninstalled_packs(tmp_path)
    test_explicit_missing_pack_raises_helpful_error()
  tests/test_vendored_sync.py:
    e: _run_check,test_pack_sync_script_exists,test_sibling_repos_exist,test_promoted_packs_not_vendored_in_monorepo,test_sibling_repos_have_pyproject,test_no_drift_promoted_packs
    _run_check(packs)
    test_pack_sync_script_exists()
    test_sibling_repos_exist()
    test_promoted_packs_not_vendored_in_monorepo()
    test_sibling_repos_have_pyproject()
    test_no_drift_promoted_packs()
  uribrowser-docker/tests/test_browser.py:
    e: runtime,test_open_requires_approval,test_open_and_dom
    runtime()
    test_open_requires_approval()
    test_open_and_dom()
  urienv-docker/tests/e2e_env.py:
    e: post,wait_health,main
    post(uri;payload;context;expect_ok)
    wait_health()
    main()
  urienv-docker/tests/test_urienv.py:
    e: runtime,base_context,test_public_var_can_be_read,test_non_allowlisted_var_is_blocked,test_secret_is_masked_but_not_revealed_without_gate,test_secret_can_be_revealed_with_explicit_gate,test_mutable_var_is_process_local
    runtime()
    base_context()
    test_public_var_can_be_read(monkeypatch)
    test_non_allowlisted_var_is_blocked(monkeypatch)
    test_secret_is_masked_but_not_revealed_without_gate(monkeypatch)
    test_secret_can_be_revealed_with_explicit_gate(monkeypatch)
    test_mutable_var_is_process_local(monkeypatch)
  urikvm-docker/scripts/real_pipeline.py:
    e: _png_with_labels,_inject_png,build_runtime,main
    _png_with_labels(labels)
    _inject_png(rt;png_bytes)
    build_runtime(config_path)
    main()
  urikvm-docker/tests/test_him_driver.py:
    e: test_driver_mock_without_allow_real,test_driver_configured,test_driver_env_override,test_driver_wayland_prefers_ydotool,test_driver_x11_defaults_pyautogui,test_driver_x11_prefers_xdotool,test_ydotool_key_sequence_ctrl_enter
    test_driver_mock_without_allow_real()
    test_driver_configured()
    test_driver_env_override()
    test_driver_wayland_prefers_ydotool()
    test_driver_x11_defaults_pyautogui()
    test_driver_x11_prefers_xdotool()
    test_ydotool_key_sequence_ctrl_enter()
  urikvm-docker/tests/test_him_scroll.py:
    e: test_mouse_scroll_dry_run_mock,test_mouse_scroll_dry_run_ydotool
    test_mouse_scroll_dry_run_mock()
    test_mouse_scroll_dry_run_ydotool()
  urikvm-docker/tests/test_kvm.py:
    e: runtime,test_him_requires_approval,test_kvm_click_text_uses_him_ocr_llm,test_type_text
    runtime()
    test_him_requires_approval()
    test_kvm_click_text_uses_him_ocr_llm()
    test_type_text()
  urikvm-docker/tests/test_llm_plan.py:
    e: test_plan_scroll_phrase_map,test_plan_type_letter,test_plan_rejects_disallowed_scheme
    test_plan_scroll_phrase_map()
    test_plan_type_letter()
    test_plan_rejects_disallowed_scheme()
  urikvm-docker/tests/test_ocr_llm.py:
    e: _png_with_labels,_runtime,_inject_png,test_tesseract_finds_ok,test_heuristic_llm_clicks_ok_from_ocr,test_openai_vision_clicks_ok_from_image
    _png_with_labels(labels)
    _runtime(ocr_driver;llm_driver)
    _inject_png(rt;png_bytes)
    test_tesseract_finds_ok()
    test_heuristic_llm_clicks_ok_from_ocr()
    test_openai_vision_clicks_ok_from_image()
  urikvm-docker/tests/test_office_mail.py:
    e: _ctx,test_office_status_and_writer_render,test_office_writer_real_export_pdf,test_mail_unread_compose_send_dry_run,test_vql_detect_compare_mock,test_plan_mail_scheme,test_plan_office_scheme
    _ctx()
    test_office_status_and_writer_render()
    test_office_writer_real_export_pdf(tmp_path)
    test_mail_unread_compose_send_dry_run()
    test_vql_detect_compare_mock()
    test_plan_mail_scheme()
    test_plan_office_scheme()
  urikvm-docker/tests/test_vision_dispatch.py:
    e: _ctx,test_mock_matches_target_box,test_heuristic_goal_substring_match,test_no_target_match_falls_back_to_first_box,test_empty_boxes_yields_no_action,test_unknown_driver_uses_heuristic,test_openai_without_key_falls_back_to_heuristic
    _ctx(driver)
    test_mock_matches_target_box()
    test_heuristic_goal_substring_match()
    test_no_target_match_falls_back_to_first_box()
    test_empty_boxes_yields_no_action()
    test_unknown_driver_uses_heuristic()
    test_openai_without_key_falls_back_to_heuristic(monkeypatch)
  urirdp-docker/tests/test_decide_dispatch.py:
    e: _cfg,test_missing_question_errors,test_mock_retry_on_critical_pattern,test_mock_abort_on_clean_context,test_dry_run_forces_mock,test_real_driver_without_credentials_falls_back,test_unknown_driver_falls_back_to_mock
    _cfg(driver)
    test_missing_question_errors()
    test_mock_retry_on_critical_pattern()
    test_mock_abort_on_clean_context()
    test_dry_run_forces_mock()
    test_real_driver_without_credentials_falls_back(monkeypatch)
    test_unknown_driver_falls_back_to_mock()
  urirdp-docker/tests/test_env_browser_routes.py:
    e: test_env_and_browser_routes_registered,test_env_health_call,test_browser_lab_alias_open_and_dom,_Args
    _Args:
    test_env_and_browser_routes_registered()
    test_env_health_call()
    test_browser_lab_alias_open_and_dom()
  urirdp-docker/tests/test_env_resolve.py:
    e: test_load_env_policy_includes_llm_vars,test_resolve_env_var_falls_back_to_process_env,test_resolve_env_var_secret_via_env_policy
    test_load_env_policy_includes_llm_vars()
    test_resolve_env_var_falls_back_to_process_env()
    test_resolve_env_var_secret_via_env_policy(monkeypatch)
  urirdp-docker/tests/test_rdp_kvm.py:
    e: test_routes_registered,test_rdp_display_status_mock,test_kvm_click_text_dry_run_pipeline,test_rdp_status,test_kvm_click_text_dry_run,test_kvm_click_text_real_without_display,test_him_requires_approval,Args
    Args:
    test_routes_registered()
    test_rdp_display_status_mock()
    test_kvm_click_text_dry_run_pipeline()
    test_rdp_status()
    test_kvm_click_text_dry_run()
    test_kvm_click_text_real_without_display()
    test_him_requires_approval()
  uristepper-docker/tests/e2e.py:
    e: post,get,assert_ok,main
    post(path;data)
    get(path)
    assert_ok(result;label)
    main()
  uristepper-docker/tests/test_runtime.py:
    e: RuntimeTest
    RuntimeTest: setUp(0),test_status(0),test_policy_requires_approval(0),test_move_relative(0),test_safety_limit(0)
  urisys-automation-lab/server/automation_lab_server.py:
    e: build_lab_runtime,forward_uri_call,serve,LabHandler
    LabHandler: log_message(1),_json(2),_read_json(0),do_OPTIONS(0),do_GET(0),do_POST(0)
    build_lab_runtime(config_path)
    forward_uri_call(base_url;uri;payload;context)
    serve(host;port)
  urisys-automation-lab/server/flow_runner.py:
    e: _require_uri_stack,_execution_root,_load_defaults,_lab_adapter_session,plan_flow,_legacy_step,run_flow_file
    _require_uri_stack()
    _execution_root(flow_path;ctx)
    _load_defaults(flow_path)
    _lab_adapter_session()
    plan_flow(flow_path)
    _legacy_step(node;step;payload;step_ctx)
    run_flow_file(flow_path)
  urisys-automation-lab/server/lab_uri_adapter.py:
    e: step_ok,LabCallAdapter
    LabCallAdapter: execute(2),_execute_log(4)
    step_ok(response)
  urisys-automation-lab/server/static_server.py:
  urisys-automation-lab/tests/test_flow_08_plan.py:
    e: _rt,test_message_alert_send,test_llm_plan_from_transcript,test_flow_08_plan_expand
    _rt()
    test_message_alert_send()
    test_llm_plan_from_transcript()
    test_flow_08_plan_expand()
  urisys-automation-lab/tests/test_flow_09_plan.py:
    e: test_flow_09_no_chat_bridge
    test_flow_09_no_chat_bridge()
  urisys-automation-lab/tests/test_flow_expectations.py:
    e: test_flow_files_exist,test_expect_block_is_well_formed,test_flow_still_parses_with_expect,test_evaluate_screen_changed,test_evaluate_screen_changed_since_previous,test_evaluate_ocr_contains,test_evaluate_min_vision_confidence,test_no_expect_is_transport_only,test_evaluate_opened_url_contains,test_analyzer_reports_duplicate_screenshots,test_analyzer_contract_overrides_heuristic
    test_flow_files_exist()
    test_expect_block_is_well_formed(flow_path)
    test_flow_still_parses_with_expect(flow_path)
    test_evaluate_screen_changed()
    test_evaluate_screen_changed_since_previous()
    test_evaluate_ocr_contains()
    test_evaluate_min_vision_confidence()
    test_no_expect_is_transport_only()
    test_evaluate_opened_url_contains()
    test_analyzer_reports_duplicate_screenshots()
    test_analyzer_contract_overrides_heuristic()
  urisys-automation-lab/tests/test_lab_handlers.py:
    e: _rt,test_stt_session_and_transcript,test_chat_uri_execute_dry_run,test_webrtc_data_send
    _rt()
    test_stt_session_and_transcript()
    test_chat_uri_execute_dry_run()
    test_webrtc_data_send()
  urisys-automation-lab/tests/test_llm_plan_handlers.py:
    e: test_plan_phrase_map_default,test_plan_rejects_disallowed_scheme,test_plan_litellm_fallback_on_error
    test_plan_phrase_map_default()
    test_plan_rejects_disallowed_scheme()
    test_plan_litellm_fallback_on_error()
  urisys-node/tests/test_artifact_resolver.py:
    e: test_select_artifact_by_platform,test_load_artifact_index_from_file,test_load_artifact_index_from_url,test_fetch_release,test_release_api_url,test_run_release_honors_artifact_container_port
    test_select_artifact_by_platform(tmp_path)
    test_load_artifact_index_from_file(tmp_path)
    test_load_artifact_index_from_url()
    test_fetch_release()
    test_release_api_url()
    test_run_release_honors_artifact_container_port(monkeypatch;tmp_path)
  urisys-node/tests/test_docker_host_e2e.py:
    e: _http_get,_remote_call,docker_stack,test_container_urisys_cli,test_host_health_and_routes,test_host_remote_identity,test_host_screen_capture,test_host_indicator_control
    _http_get(path)
    _remote_call(uri;payload;context)
    docker_stack()
    test_container_urisys_cli(docker_stack)
    test_host_health_and_routes(docker_stack)
    test_host_remote_identity(docker_stack)
    test_host_screen_capture(docker_stack)
    test_host_indicator_control()
  urisys-node/tests/test_forward_config.py:
    e: _runtime,test_load_forward_entries_from_config,test_load_forward_entries_env_inline,test_wire_forward_packs_registers_routes,test_command_register_forward,test_load_release_forward_entries_from_config,test_load_release_forward_entries_env_inline,test_wire_release_forward_packs_calls_hotload,test_wire_release_forward_packs_is_best_effort,test_build_runtime_wires_config_forwards
    _runtime(tmp_path)
    test_load_forward_entries_from_config()
    test_load_forward_entries_env_inline()
    test_wire_forward_packs_registers_routes(tmp_path)
    test_command_register_forward(tmp_path)
    test_load_release_forward_entries_from_config()
    test_load_release_forward_entries_env_inline()
    test_wire_release_forward_packs_calls_hotload(tmp_path;monkeypatch)
    test_wire_release_forward_packs_is_best_effort(tmp_path;monkeypatch)
    test_build_runtime_wires_config_forwards(tmp_path;monkeypatch)
  urisys-node/tests/test_forward_pack.py:
    e: _runtime,test_register_forward_adds_routes_and_target,test_call_forwards_to_worker,test_forward_without_target_fails_cleanly
    _runtime(tmp_path)
    test_register_forward_adds_routes_and_target(tmp_path)
    test_call_forwards_to_worker(tmp_path;monkeypatch)
    test_forward_without_target_fails_cleanly(tmp_path)
  urisys-node/tests/test_pack_auto_install.py:
    e: _node_only_runtime,test_install_pack_uri,test_install_pack_requires_approval,test_query_packs,test_call_uri_lazy_pack_route_not_found,test_load_pack_with_mock_pip,test_ensure_pack_for_uri_skips_pip_when_importable,test_force_reload_reregister_pack,test_pack_importable_uses_import_pack_module
    _node_only_runtime(tmp_path)
    test_install_pack_uri(tmp_path)
    test_install_pack_requires_approval(tmp_path)
    test_query_packs(tmp_path)
    test_call_uri_lazy_pack_route_not_found(tmp_path)
    test_load_pack_with_mock_pip(tmp_path)
    test_ensure_pack_for_uri_skips_pip_when_importable(tmp_path)
    test_force_reload_reregister_pack(tmp_path)
    test_pack_importable_uses_import_pack_module()
  urisys-node/tests/test_pack_github.py:
    e: test_github_wheel_url_him,test_resolve_pack_spec_auto_prefers_github_for_him,test_resolve_pack_spec_kvm_stays_pypi
    test_github_wheel_url_him()
    test_resolve_pack_spec_auto_prefers_github_for_him()
    test_resolve_pack_spec_kvm_stays_pypi()
  urisys-node/tests/test_pack_hotload.py:
    e: _node_only_runtime,test_hotload_adds_routes,test_hotload_is_idempotent,test_hotload_empty_pack_name_rejected,test_hotload_unknown_pack_reports_failure
    _node_only_runtime(tmp_path)
    test_hotload_adds_routes(tmp_path)
    test_hotload_is_idempotent(tmp_path)
    test_hotload_empty_pack_name_rejected(tmp_path)
    test_hotload_unknown_pack_reports_failure(tmp_path)
  urisys-node/tests/test_pack_office_mail.py:
    e: test_scheme_to_pack_office_mail_vql,test_pack_modules_office_mail_vql
    test_scheme_to_pack_office_mail_vql()
    test_pack_modules_office_mail_vql()
  urisys-node/tests/test_release_hotload.py:
    e: _runtime,_release,test_canonical_digest_ignores_signature_block,test_disabled_policy_passes_through,test_required_but_unsigned_fails,test_required_untrusted_key_fails,test_required_no_crypto_backend_fails_closed,test_required_good_signature_verifies,test_required_mismatched_signature_fails,test_hotload_requires_pairing,test_hotload_happy_path_wires_forward,test_hotload_bad_signature_skips_run,test_hotload_missing_scheme_patterns,test_parse_contract_spec_extracts_scheme_and_patterns,test_parse_contract_spec_rejects_block_without_scheme,test_contract_url_from_release_variants,test_hotload_derives_spec_from_contract
    _runtime(tmp_path)
    _release()
    test_canonical_digest_ignores_signature_block()
    test_disabled_policy_passes_through(monkeypatch)
    test_required_but_unsigned_fails(monkeypatch)
    test_required_untrusted_key_fails(monkeypatch)
    test_required_no_crypto_backend_fails_closed(monkeypatch)
    test_required_good_signature_verifies(monkeypatch)
    test_required_mismatched_signature_fails(monkeypatch)
    test_hotload_requires_pairing(tmp_path;monkeypatch)
    test_hotload_happy_path_wires_forward(tmp_path;monkeypatch)
    test_hotload_bad_signature_skips_run(tmp_path;monkeypatch)
    test_hotload_missing_scheme_patterns(tmp_path;monkeypatch)
    test_parse_contract_spec_extracts_scheme_and_patterns()
    test_parse_contract_spec_rejects_block_without_scheme()
    test_contract_url_from_release_variants()
    test_hotload_derives_spec_from_contract(tmp_path;monkeypatch)
  urisys-node/tests/test_uriscreen_auto.py:
    e: test_resolve_backend_auto_x11,test_resolve_backend_auto_wayland,test_is_black_png
    test_resolve_backend_auto_x11(monkeypatch)
    test_resolve_backend_auto_wayland(monkeypatch)
    test_is_black_png(tmp_path)
  urisys-node/tests/test_urishell.py:
    e: test_shell_route_registered,test_shell_pip_dry_run,test_shell_requires_allow_real
    test_shell_route_registered()
    test_shell_pip_dry_run()
    test_shell_requires_allow_real()
  urisys-node/tests/test_urisys_node.py:
    e: test_identity_and_enroll,test_screen_capture_mock,test_rewrite_uri_for_slave,test_health_payload,test_health_payload_with_runtime
    test_identity_and_enroll()
    test_screen_capture_mock()
    test_rewrite_uri_for_slave()
    test_health_payload()
    test_health_payload_with_runtime()
  urisys-node/tests/test_urisysedge_single_source.py:
    e: test_canonical_urisysedge_present,test_urisysedge_imports_from_canonical,test_no_vendored_duplicate_module
    test_canonical_urisysedge_present()
    test_urisysedge_imports_from_canonical()
    test_no_vendored_duplicate_module(module)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('urisys', '0.1.39', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 49, 'less').
project_file('examples/frontend/app.js', 22, 'javascript').
project_file('examples/markpact/browser-call.sh', 13, 'shell').
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
project_file('scripts/ci-checkout-siblings.sh', 52, 'shell').
project_file('scripts/ci-install-siblings.sh', 29, 'shell').
project_file('scripts/deploy-lenovo-node.sh', 72, 'shell').
project_file('scripts/install-kvm-packs-editable.sh', 14, 'shell').
project_file('scripts/lenovo-node-session.sh', 73, 'shell').
project_file('scripts/office-simulate-loop.py', 147, 'python').
project_file('scripts/pack_registry.py', 261, 'python').
project_file('scripts/pack_sync.py', 348, 'python').
project_file('scripts/paths.sh', 55, 'shell').
project_file('scripts/publish-pypi-packs.sh', 54, 'shell').
project_file('scripts/remote-node-smoke.sh', 100, 'shell').
project_file('scripts/report/__init__.py', 62, 'python').
project_file('scripts/report/cli.py', 42, 'python').
project_file('scripts/report/events.py', 139, 'python').
project_file('scripts/report/lab_checks.py', 189, 'python').
project_file('scripts/report/models.py', 87, 'python').
project_file('scripts/report/run_analysis.py', 130, 'python').
project_file('scripts/report/run_markdown.py', 43, 'python').
project_file('scripts/report/session.py', 106, 'python').
project_file('scripts/report/session_io.py', 20, 'python').
project_file('scripts/report/session_markdown.py', 121, 'python').
project_file('scripts/report/util.py', 30, 'python').
project_file('scripts/run-email-mailpit-e2e.sh', 134, 'shell').
project_file('scripts/run-lab-e2e.sh', 15, 'shell').
project_file('scripts/run-lab-nightly.sh', 17, 'shell').
project_file('scripts/run-lab-unit-ci.sh', 21, 'shell').
project_file('scripts/run-nl-log-smoke.sh', 44, 'shell').
project_file('scripts/run-office-simulate-e2e.sh', 130, 'shell').
project_file('scripts/run-office-simulate-lenovo.sh', 183, 'shell').
project_file('scripts/run-office-writer-e2e.sh', 113, 'shell').
project_file('scripts/run-smoke-all.sh', 25, 'shell').
project_file('scripts/run-urisys-node-docker-e2e.sh', 163, 'shell').
project_file('scripts/run-urisys-node-docker-session.sh', 7, 'shell').
project_file('scripts/run_test_sessions.py', 783, 'python').
project_file('scripts/session_report.py', 50, 'python').
project_file('scripts/sync-vendored-pack.sh', 39, 'shell').
project_file('scripts/sync-vendored-urisysedge.sh', 17, 'shell').
project_file('scripts/test-goal.sh', 12, 'shell').
project_file('scripts/test-python-matrix.sh', 59, 'shell').
project_file('scripts/test_sessions/__init__.py', 99, 'python').
project_file('scripts/test_sessions/expectations.py', 154, 'python').
project_file('scripts/test_sessions/lab_flows.py', 320, 'python').
project_file('scripts/test_sessions/lab_rdp.py', 181, 'python').
project_file('scripts/test_sessions/util.py', 210, 'python').
project_file('scripts/validate-all-markpacts.sh', 54, 'shell').
project_file('scripts/validate-pypi-metadata.sh', 63, 'shell').
project_file('src/urisys/__init__.py', 4, 'python').
project_file('src/urisys/bootstrap.py', 112, 'python').
project_file('src/urisys/cli.py', 283, 'python').
project_file('src/urisys/controllers/__init__.py', 1, 'python').
project_file('src/urisys/controllers/flow_controller.py', 34, 'python').
project_file('src/urisys/controllers/server_controller.py', 19, 'python').
project_file('src/urisys/controllers/uri_controller.py', 34, 'python').
project_file('src/urisys/defaults.py', 21, 'python').
project_file('src/urisys/doctor.py', 288, 'python').
project_file('src/urisys/flow.py', 26, 'python').
project_file('src/urisys/http_server.py', 79, 'python').
project_file('src/urisys/init_setup.py', 237, 'python').
project_file('src/urisys/managers/__init__.py', 1, 'python').
project_file('src/urisys/managers/bridge_manager.py', 15, 'python').
project_file('src/urisys/managers/event_manager.py', 14, 'python').
project_file('src/urisys/managers/markpact_manager.py', 402, 'python').
project_file('src/urisys/managers/markpact_models.py', 93, 'python').
project_file('src/urisys/managers/markpact_validation.py', 141, 'python').
project_file('src/urisys/managers/pack_manager.py', 129, 'python').
project_file('src/urisys/managers/policy_manager.py', 19, 'python').
project_file('src/urisys/managers/route_manager.py', 24, 'python').
project_file('src/urisys/managers/runtime_manager.py', 31, 'python').
project_file('src/urisys/managers/source_manager.py', 225, 'python').
project_file('src/urisys/node_install.py', 53, 'python').
project_file('src/urisys/uricore_install.py', 131, 'python').
project_file('tests/test_bootstrap.py', 61, 'python').
project_file('tests/test_doctor.py', 29, 'python').
project_file('tests/test_doctor_uricore.py', 27, 'python').
project_file('tests/test_init.py', 61, 'python').
project_file('tests/test_kvm_pack_pyprojects.py', 69, 'python').
project_file('tests/test_markpact.py', 99, 'python').
project_file('tests/test_node_install.py', 31, 'python').
project_file('tests/test_pypi_metadata.py', 35, 'python').
project_file('tests/test_python_compat.py', 53, 'python').
project_file('tests/test_run_expectations.py', 56, 'python').
project_file('tests/test_session_report_events.py', 59, 'python').
project_file('tests/test_source_manager.py', 36, 'python').
project_file('tests/test_uricore_install.py', 38, 'python').
project_file('tests/test_urisys.py', 46, 'python').
project_file('tests/test_vendored_sync.py', 58, 'python').
project_file('tree.sh', 2, 'shell').
project_file('uribrowser-docker/scripts/test-local.sh', 9, 'shell').
project_file('uribrowser-docker/scripts/test-real.sh', 29, 'shell').
project_file('uribrowser-docker/tests/test_browser.py', 24, 'python').
project_file('urienv-docker/scripts/local-test.sh', 11, 'shell').
project_file('urienv-docker/scripts/test-docker.sh', 5, 'shell').
project_file('urienv-docker/tests/e2e_env.py', 64, 'python').
project_file('urienv-docker/tests/test_urienv.py', 70, 'python').
project_file('urikvm-docker/scripts/call-http.sh', 6, 'shell').
project_file('urikvm-docker/scripts/real_pipeline.py', 96, 'python').
project_file('urikvm-docker/scripts/test-local.sh', 9, 'shell').
project_file('urikvm-docker/scripts/test-real.sh', 48, 'shell').
project_file('urikvm-docker/tests/test_him_driver.py', 48, 'python').
project_file('urikvm-docker/tests/test_him_scroll.py', 15, 'python').
project_file('urikvm-docker/tests/test_kvm.py', 35, 'python').
project_file('urikvm-docker/tests/test_llm_plan.py', 32, 'python').
project_file('urikvm-docker/tests/test_ocr_llm.py', 87, 'python').
project_file('urikvm-docker/tests/test_office_mail.py', 84, 'python').
project_file('urikvm-docker/tests/test_vision_dispatch.py', 75, 'python').
project_file('urirdp-docker/docker/bootstrap-rdp-session.sh', 112, 'shell').
project_file('urirdp-docker/docker/entrypoint.sh', 26, 'shell').
project_file('urirdp-docker/docker/startwm.sh', 7, 'shell').
project_file('urirdp-docker/scripts/call-http.sh', 11, 'shell').
project_file('urirdp-docker/scripts/test-docker.sh', 18, 'shell').
project_file('urirdp-docker/scripts/test-local.sh', 9, 'shell').
project_file('urirdp-docker/scripts/test-rdp-real.sh', 13, 'shell').
project_file('urirdp-docker/scripts/test-real-docker.sh', 64, 'shell').
project_file('urirdp-docker/tests/e2e_rdp_real.sh', 101, 'shell').
project_file('urirdp-docker/tests/test_decide_dispatch.py', 58, 'python').
project_file('urirdp-docker/tests/test_env_browser_routes.py', 50, 'python').
project_file('urirdp-docker/tests/test_env_resolve.py', 29, 'python').
project_file('urirdp-docker/tests/test_rdp_kvm.py', 76, 'python').
project_file('uristepper-docker/scripts/call-http.sh', 11, 'shell').
project_file('uristepper-docker/scripts/test-docker.sh', 8, 'shell').
project_file('uristepper-docker/scripts/test-local.sh', 11, 'shell').
project_file('uristepper-docker/tests/e2e.py', 71, 'python').
project_file('uristepper-docker/tests/test_runtime.py', 53, 'python').
project_file('urisys-automation-lab/docker/entrypoint.sh', 19, 'shell').
project_file('urisys-automation-lab/scripts/docker-down.sh', 7, 'shell').
project_file('urisys-automation-lab/scripts/docker-logs.sh', 7, 'shell').
project_file('urisys-automation-lab/scripts/docker-smoke.sh', 21, 'shell').
project_file('urisys-automation-lab/scripts/docker-up.sh', 22, 'shell').
project_file('urisys-automation-lab/scripts/run-lab.sh', 14, 'shell').
project_file('urisys-automation-lab/scripts/validate-flows.sh', 29, 'shell').
project_file('urisys-automation-lab/server/automation_lab_server.py', 248, 'python').
project_file('urisys-automation-lab/server/flow_runner.py', 170, 'python').
project_file('urisys-automation-lab/server/lab_uri_adapter.py', 130, 'python').
project_file('urisys-automation-lab/server/static_server.py', 7, 'python').
project_file('urisys-automation-lab/tests/test_flow_08_plan.py', 69, 'python').
project_file('urisys-automation-lab/tests/test_flow_09_plan.py', 28, 'python').
project_file('urisys-automation-lab/tests/test_flow_expectations.py', 167, 'python').
project_file('urisys-automation-lab/tests/test_lab_handlers.py', 64, 'python').
project_file('urisys-automation-lab/tests/test_llm_plan_handlers.py', 44, 'python').
project_file('urisys-automation-lab/web/app.js', 132, 'javascript').
project_file('urisys-node/docker/entrypoint.sh', 64, 'shell').
project_file('urisys-node/scripts/install-linux.sh', 17, 'shell').
project_file('urisys-node/tests/test_artifact_resolver.py', 96, 'python').
project_file('urisys-node/tests/test_docker_host_e2e.py', 157, 'python').
project_file('urisys-node/tests/test_forward_config.py', 150, 'python').
project_file('urisys-node/tests/test_forward_pack.py', 75, 'python').
project_file('urisys-node/tests/test_pack_auto_install.py', 108, 'python').
project_file('urisys-node/tests/test_pack_github.py', 28, 'python').
project_file('urisys-node/tests/test_pack_hotload.py', 65, 'python').
project_file('urisys-node/tests/test_pack_office_mail.py', 30, 'python').
project_file('urisys-node/tests/test_release_hotload.py', 259, 'python').
project_file('urisys-node/tests/test_uriscreen_auto.py', 37, 'python').
project_file('urisys-node/tests/test_urishell.py', 49, 'python').
project_file('urisys-node/tests/test_urisys_node.py', 65, 'python').
project_file('urisys-node/tests/test_urisysedge_single_source.py', 36, 'python').

% ── Python Functions ─────────────────────────────────────
python_function('scripts/office-simulate-loop.py', 'call_uri', 4, 4, 9).
python_function('scripts/office-simulate-loop.py', 'rules_tick', 3, 3, 5).
python_function('scripts/office-simulate-loop.py', 'llm_tick', 3, 7, 6).
python_function('scripts/office-simulate-loop.py', 'parse_args', 1, 1, 4).
python_function('scripts/office-simulate-loop.py', 'main', 1, 10, 9).
python_function('scripts/pack_registry.py', '_repo', 1, 1, 0).
python_function('scripts/pack_registry.py', '_vendored_kvm', 1, 1, 0).
python_function('scripts/pack_registry.py', '_vendored_rdp', 1, 1, 0).
python_function('scripts/pack_registry.py', '_vendored_node', 1, 1, 0).
python_function('scripts/pack_registry.py', 'sibling_uv_path', 1, 1, 0).
python_function('scripts/pack_registry.py', 'sibling_repo', 1, 1, 1).
python_function('scripts/pack_registry.py', 'pack_specs', 0, 17, 7).
python_function('scripts/pack_registry.py', 'sibling_repo_names', 0, 1, 2).
python_function('scripts/pack_registry.py', 'all_promoted_packs', 0, 1, 3).
python_function('scripts/pack_sync.py', 'repo_module_dir', 1, 2, 0).
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
python_function('scripts/pack_sync.py', 'main', 1, 28, 18).
python_function('scripts/report/cli.py', 'main', 0, 4, 13).
python_function('scripts/report/events.py', 'summarize_event_records', 1, 14, 5).
python_function('scripts/report/events.py', 'load_event_records', 1, 14, 7).
python_function('scripts/report/events.py', 'summarize_events', 1, 8, 8).
python_function('scripts/report/events.py', 'resolve_events_paths', 1, 7, 2).
python_function('scripts/report/events.py', 'merge_event_summaries', 1, 10, 9).
python_function('scripts/report/lab_checks.py', 'iter_step_results', 1, 9, 3).
python_function('scripts/report/lab_checks.py', 'load_flow_outcomes', 1, 15, 15).
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
python_function('scripts/report/session.py', 'infer_steps', 2, 20, 13).
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
python_function('scripts/report/util.py', 'now_iso', 0, 1, 3).
python_function('scripts/report/util.py', 'host_id', 0, 1, 3).
python_function('scripts/report/util.py', 'read_json', 1, 3, 3).
python_function('scripts/report/util.py', 'tail', 2, 2, 0).
python_function('scripts/run_test_sessions.py', 'session_pytest_urirdp', 1, 3, 5).
python_function('scripts/run_test_sessions.py', 'session_pytest_urisys', 1, 2, 5).
python_function('scripts/run_test_sessions.py', 'session_pytest_urisys_node', 1, 2, 5).
python_function('scripts/run_test_sessions.py', 'session_urirdp_mock_docker', 1, 5, 17).
python_function('scripts/run_test_sessions.py', 'session_urirdp_real_docker', 1, 30, 25).
python_function('scripts/run_test_sessions.py', 'session_urirdp_rdp_e2e', 1, 5, 11).
python_function('scripts/run_test_sessions.py', 'session_automation_lab', 1, 16, 17).
python_function('scripts/run_test_sessions.py', '_monorepo_root', 0, 4, 1).
python_function('scripts/run_test_sessions.py', 'session_urisys_node_docker_gui', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'session_office_simulate', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'session_office_simulate_lenovo', 1, 6, 10).
python_function('scripts/run_test_sessions.py', 'session_office_writer', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'session_email_mailpit', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'main', 0, 13, 19).
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
python_function('scripts/test_sessions/util.py', 'now_iso', 0, 1, 3).
python_function('scripts/test_sessions/util.py', 'run_id', 0, 1, 2).
python_function('scripts/test_sessions/util.py', 'host_id', 0, 1, 3).
python_function('scripts/test_sessions/util.py', 'http_json', 4, 9, 11).
python_function('scripts/test_sessions/util.py', 'wait_health', 3, 3, 5).
python_function('scripts/test_sessions/util.py', 'compose_cmd', 0, 4, 3).
python_function('scripts/test_sessions/util.py', 'save_json', 2, 1, 3).
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
python_function('src/urisys/bootstrap.py', '_print_json', 1, 1, 2).
python_function('src/urisys/bootstrap.py', '_missing_uricore_payload', 1, 1, 1).
python_function('src/urisys/bootstrap.py', '_doctor_main', 1, 3, 6).
python_function('src/urisys/bootstrap.py', '_init_main', 1, 6, 9).
python_function('src/urisys/bootstrap.py', 'main', 1, 8, 6).
python_function('src/urisys/cli.py', '_json_arg', 1, 3, 4).
python_function('src/urisys/cli.py', 'print_json', 1, 1, 2).
python_function('src/urisys/cli.py', '_add_runtime_flags', 1, 1, 1).
python_function('src/urisys/cli.py', 'resolve_markpact_source', 1, 2, 3).
python_function('src/urisys/cli.py', 'build_parser', 0, 1, 9).
python_function('src/urisys/cli.py', 'main', 1, 36, 36).
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
python_function('src/urisys/http_server.py', '_send', 3, 1, 8).
python_function('src/urisys/http_server.py', 'create_server', 2, 1, 13).
python_function('src/urisys/init_setup.py', 'default_pip_specs', 0, 1, 1).
python_function('src/urisys/init_setup.py', 'default_node_pip_spec', 0, 1, 1).
python_function('src/urisys/init_setup.py', 'pip_install_specs', 1, 4, 2).
python_function('src/urisys/init_setup.py', 'verify_uri_control', 0, 2, 3).
python_function('src/urisys/init_setup.py', 'profile_env', 1, 2, 1).
python_function('src/urisys/init_setup.py', 'render_env_shell', 1, 2, 4).
python_function('src/urisys/init_setup.py', 'write_env_file', 2, 2, 5).
python_function('src/urisys/init_setup.py', 'run_init', 0, 41, 18).
python_function('src/urisys/managers/markpact_models.py', 'safe_identifier', 1, 3, 4).
python_function('src/urisys/managers/markpact_models.py', 'parse_meta', 1, 4, 2).
python_function('src/urisys/managers/markpact_models.py', 'scheme_from_uri', 1, 2, 2).
python_function('src/urisys/managers/markpact_models.py', 'source_hash', 1, 1, 4).
python_function('src/urisys/managers/markpact_validation.py', 'validate_contract', 3, 23, 8).
python_function('src/urisys/managers/markpact_validation.py', 'validate_bundle', 3, 14, 8).
python_function('src/urisys/managers/markpact_validation.py', 'validate_implementation', 3, 18, 7).
python_function('src/urisys/node_install.py', 'github_owner', 0, 1, 2).
python_function('src/urisys/node_install.py', 'github_version', 0, 1, 3).
python_function('src/urisys/node_install.py', 'wheel_url', 1, 3, 5).
python_function('src/urisys/node_install.py', 'pip_spec', 0, 1, 1).
python_function('src/urisys/node_install.py', 'is_importable', 0, 1, 1).
python_function('src/urisys/node_install.py', 'diagnose_urisys_node', 0, 3, 3).
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
python_function('tests/test_bootstrap.py', '_load_module', 2, 2, 3).
python_function('tests/test_bootstrap.py', 'test_bootstrap_import_does_not_require_uri_control', 0, 2, 2).
python_function('tests/test_bootstrap.py', 'test_cli_import_does_not_require_uri_control', 0, 3, 1).
python_function('tests/test_bootstrap.py', 'test_missing_uricore_payload', 0, 4, 2).
python_function('tests/test_bootstrap.py', 'test_doctor_subcommand_via_bootstrap', 0, 6, 4).
python_function('tests/test_doctor.py', 'test_doctor_ok_in_dev_env', 0, 8, 1).
python_function('tests/test_doctor.py', 'test_doctor_fails_high_min_version', 0, 3, 2).
python_function('tests/test_doctor.py', 'test_doctor_hints_include_node_serve', 0, 2, 2).
python_function('tests/test_doctor_uricore.py', 'test_check_uricore_authentic_fails_on_squatter', 0, 7, 4).
python_function('tests/test_init.py', 'test_init_dry_run_via_bootstrap', 0, 8, 4).
python_function('tests/test_init.py', 'test_run_init_skip_pip_writes_env', 1, 5, 4).
python_function('tests/test_init.py', 'test_pip_install_failure', 0, 3, 2).
python_function('tests/test_kvm_pack_pyprojects.py', '_name', 1, 1, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_urisysedge_sibling_pyproject', 0, 3, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_each_kvm_pack_has_sibling_pyproject', 0, 4, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_sibling_pack_pyprojects_depend_on_urisysedge', 0, 3, 4).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_urillm_imports_urisysedge_not_urikvmedge', 0, 4, 2).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_urisys_root_uv_sources_point_to_siblings', 0, 4, 4).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_vendored_kvm_pack_dirs_removed', 0, 3, 1).
python_function('tests/test_kvm_pack_pyprojects.py', 'test_urikvmedge_promoted_to_sibling', 0, 4, 3).
python_function('tests/test_markpact.py', 'test_markpact_validate', 0, 5, 2).
python_function('tests/test_markpact.py', 'test_markpact_validate_contract', 0, 5, 2).
python_function('tests/test_markpact.py', 'test_markpact_validate_implementation', 0, 4, 2).
python_function('tests/test_markpact.py', 'test_markpact_validate_bundle', 0, 3, 2).
python_function('tests/test_markpact.py', 'test_markpact_compile_and_call', 1, 5, 7).
python_function('tests/test_markpact.py', 'test_uri_controller_loads_markpact_directly', 1, 4, 4).
python_function('tests/test_markpact.py', 'test_markpact_embedded_tests', 1, 3, 3).
python_function('tests/test_markpact.py', 'test_build_route_shape', 0, 7, 2).
python_function('tests/test_node_install.py', 'test_default_pip_specs_no_git_urls', 0, 3, 2).
python_function('tests/test_node_install.py', 'test_urisys_node_uses_release_wheel', 0, 5, 3).
python_function('tests/test_node_install.py', 'test_urisys_node_wheel_url_override', 0, 2, 2).
python_function('tests/test_pypi_metadata.py', 'test_validate_pypi_metadata_script_exists', 0, 2, 1).
python_function('tests/test_pypi_metadata.py', 'test_built_wheel_has_no_direct_url_requires_dist', 0, 3, 6).
python_function('tests/test_pypi_metadata.py', 'test_pyproject_runtime_deps_have_no_direct_urls', 0, 4, 2).
python_function('tests/test_python_compat.py', 'test_python_version_gate', 4, 2, 4).
python_function('tests/test_python_compat.py', 'test_current_python_supported', 0, 5, 2).
python_function('tests/test_run_expectations.py', 'test_screen_changed_uses_baseline_not_previous_flow', 0, 2, 1).
python_function('tests/test_run_expectations.py', 'test_screen_changed_fails_when_equal_baseline', 0, 3, 2).
python_function('tests/test_run_expectations.py', 'test_ocr_contains_from_pipeline', 0, 2, 1).
python_function('tests/test_session_report_events.py', 'test_summarize_events_api_json', 1, 4, 3).
python_function('tests/test_session_report_events.py', 'test_summarize_events_jsonl', 1, 4, 5).
python_function('tests/test_source_manager.py', 'test_fetch_local_file', 1, 4, 5).
python_function('tests/test_source_manager.py', 'test_fetch_github_raw', 2, 3, 4).
python_function('tests/test_uricore_install.py', 'test_wheel_url_default', 0, 3, 3).
python_function('tests/test_uricore_install.py', 'test_wrong_uricore_detected_when_squatter_present', 0, 2, 2).
python_function('tests/test_uricore_install.py', 'test_not_wrong_when_uri_control_present', 0, 2, 2).
python_function('tests/test_uricore_install.py', 'test_diagnose_includes_wheel_url', 0, 3, 2).
python_function('tests/test_urisys.py', 'test_call_browser_open', 1, 3, 4).
python_function('tests/test_urisys.py', 'test_routes_load', 1, 3, 5).
python_function('tests/test_urisys.py', 'test_all_skips_uninstalled_packs', 1, 4, 3).
python_function('tests/test_urisys.py', 'test_explicit_missing_pack_raises_helpful_error', 0, 1, 3).
python_function('tests/test_vendored_sync.py', '_run_check', 1, 1, 2).
python_function('tests/test_vendored_sync.py', 'test_pack_sync_script_exists', 0, 4, 1).
python_function('tests/test_vendored_sync.py', 'test_sibling_repos_exist', 0, 4, 1).
python_function('tests/test_vendored_sync.py', 'test_promoted_packs_not_vendored_in_monorepo', 0, 5, 4).
python_function('tests/test_vendored_sync.py', 'test_sibling_repos_have_pyproject', 0, 3, 1).
python_function('tests/test_vendored_sync.py', 'test_no_drift_promoted_packs', 0, 3, 3).
python_function('uribrowser-docker/tests/test_browser.py', 'runtime', 0, 1, 2).
python_function('uribrowser-docker/tests/test_browser.py', 'test_open_requires_approval', 0, 3, 2).
python_function('uribrowser-docker/tests/test_browser.py', 'test_open_and_dom', 0, 4, 2).
python_function('urienv-docker/tests/e2e_env.py', 'post', 4, 6, 9).
python_function('urienv-docker/tests/e2e_env.py', 'wait_health', 0, 4, 8).
python_function('urienv-docker/tests/e2e_env.py', 'main', 0, 9, 4).
python_function('urienv-docker/tests/test_urienv.py', 'runtime', 0, 2, 5).
python_function('urienv-docker/tests/test_urienv.py', 'base_context', 0, 1, 0).
python_function('urienv-docker/tests/test_urienv.py', 'test_public_var_can_be_read', 1, 3, 4).
python_function('urienv-docker/tests/test_urienv.py', 'test_non_allowlisted_var_is_blocked', 1, 3, 4).
python_function('urienv-docker/tests/test_urienv.py', 'test_secret_is_masked_but_not_revealed_without_gate', 1, 5, 4).
python_function('urienv-docker/tests/test_urienv.py', 'test_secret_can_be_revealed_with_explicit_gate', 1, 3, 4).
python_function('urienv-docker/tests/test_urienv.py', 'test_mutable_var_is_process_local', 1, 3, 4).
python_function('urikvm-docker/scripts/real_pipeline.py', '_png_with_labels', 1, 4, 9).
python_function('urikvm-docker/scripts/real_pipeline.py', '_inject_png', 2, 1, 2).
python_function('urikvm-docker/scripts/real_pipeline.py', 'build_runtime', 1, 1, 3).
python_function('urikvm-docker/scripts/real_pipeline.py', 'main', 0, 14, 12).
python_function('urikvm-docker/tests/test_him_driver.py', 'test_driver_mock_without_allow_real', 0, 2, 1).
python_function('urikvm-docker/tests/test_him_driver.py', 'test_driver_configured', 0, 2, 1).
python_function('urikvm-docker/tests/test_him_driver.py', 'test_driver_env_override', 0, 2, 2).
python_function('urikvm-docker/tests/test_him_driver.py', 'test_driver_wayland_prefers_ydotool', 0, 2, 3).
python_function('urikvm-docker/tests/test_him_driver.py', 'test_driver_x11_defaults_pyautogui', 0, 5, 4).
python_function('urikvm-docker/tests/test_him_driver.py', 'test_driver_x11_prefers_xdotool', 0, 2, 3).
python_function('urikvm-docker/tests/test_him_driver.py', 'test_ydotool_key_sequence_ctrl_enter', 0, 2, 1).
python_function('urikvm-docker/tests/test_him_scroll.py', 'test_mouse_scroll_dry_run_mock', 0, 3, 1).
python_function('urikvm-docker/tests/test_him_scroll.py', 'test_mouse_scroll_dry_run_ydotool', 0, 3, 1).
python_function('urikvm-docker/tests/test_kvm.py', 'runtime', 0, 1, 2).
python_function('urikvm-docker/tests/test_kvm.py', 'test_him_requires_approval', 0, 3, 2).
python_function('urikvm-docker/tests/test_kvm.py', 'test_kvm_click_text_uses_him_ocr_llm', 0, 4, 2).
python_function('urikvm-docker/tests/test_kvm.py', 'test_type_text', 0, 3, 2).
python_function('urikvm-docker/tests/test_llm_plan.py', 'test_plan_scroll_phrase_map', 0, 5, 1).
python_function('urikvm-docker/tests/test_llm_plan.py', 'test_plan_type_letter', 0, 4, 1).
python_function('urikvm-docker/tests/test_llm_plan.py', 'test_plan_rejects_disallowed_scheme', 0, 3, 1).
python_function('urikvm-docker/tests/test_ocr_llm.py', '_png_with_labels', 1, 4, 9).
python_function('urikvm-docker/tests/test_ocr_llm.py', '_runtime', 2, 1, 2).
python_function('urikvm-docker/tests/test_ocr_llm.py', '_inject_png', 2, 1, 2).
python_function('urikvm-docker/tests/test_ocr_llm.py', 'test_tesseract_finds_ok', 0, 6, 4).
python_function('urikvm-docker/tests/test_ocr_llm.py', 'test_heuristic_llm_clicks_ok_from_ocr', 0, 6, 4).
python_function('urikvm-docker/tests/test_ocr_llm.py', 'test_openai_vision_clicks_ok_from_image', 0, 4, 7).
python_function('urikvm-docker/tests/test_office_mail.py', '_ctx', 0, 1, 0).
python_function('urikvm-docker/tests/test_office_mail.py', 'test_office_status_and_writer_render', 0, 4, 3).
python_function('urikvm-docker/tests/test_office_mail.py', 'test_office_writer_real_export_pdf', 1, 4, 5).
python_function('urikvm-docker/tests/test_office_mail.py', 'test_mail_unread_compose_send_dry_run', 0, 5, 5).
python_function('urikvm-docker/tests/test_office_mail.py', 'test_vql_detect_compare_mock', 0, 3, 3).
python_function('urikvm-docker/tests/test_office_mail.py', 'test_plan_mail_scheme', 0, 3, 1).
python_function('urikvm-docker/tests/test_office_mail.py', 'test_plan_office_scheme', 0, 3, 1).
python_function('urikvm-docker/tests/test_vision_dispatch.py', '_ctx', 1, 1, 0).
python_function('urikvm-docker/tests/test_vision_dispatch.py', 'test_mock_matches_target_box', 0, 2, 2).
python_function('urikvm-docker/tests/test_vision_dispatch.py', 'test_heuristic_goal_substring_match', 0, 4, 2).
python_function('urikvm-docker/tests/test_vision_dispatch.py', 'test_no_target_match_falls_back_to_first_box', 0, 4, 2).
python_function('urikvm-docker/tests/test_vision_dispatch.py', 'test_empty_boxes_yields_no_action', 0, 2, 2).
python_function('urikvm-docker/tests/test_vision_dispatch.py', 'test_unknown_driver_uses_heuristic', 0, 3, 2).
python_function('urikvm-docker/tests/test_vision_dispatch.py', 'test_openai_without_key_falls_back_to_heuristic', 1, 3, 3).
python_function('urirdp-docker/tests/test_decide_dispatch.py', '_cfg', 1, 1, 0).
python_function('urirdp-docker/tests/test_decide_dispatch.py', 'test_missing_question_errors', 0, 2, 1).
python_function('urirdp-docker/tests/test_decide_dispatch.py', 'test_mock_retry_on_critical_pattern', 0, 3, 2).
python_function('urirdp-docker/tests/test_decide_dispatch.py', 'test_mock_abort_on_clean_context', 0, 2, 2).
python_function('urirdp-docker/tests/test_decide_dispatch.py', 'test_dry_run_forces_mock', 0, 2, 2).
python_function('urirdp-docker/tests/test_decide_dispatch.py', 'test_real_driver_without_credentials_falls_back', 1, 3, 3).
python_function('urirdp-docker/tests/test_decide_dispatch.py', 'test_unknown_driver_falls_back_to_mock', 0, 2, 2).
python_function('urirdp-docker/tests/test_env_browser_routes.py', 'test_env_and_browser_routes_registered', 0, 5, 2).
python_function('urirdp-docker/tests/test_env_browser_routes.py', 'test_env_health_call', 0, 3, 3).
python_function('urirdp-docker/tests/test_env_browser_routes.py', 'test_browser_lab_alias_open_and_dom', 0, 6, 4).
python_function('urirdp-docker/tests/test_env_resolve.py', 'test_load_env_policy_includes_llm_vars', 0, 4, 2).
python_function('urirdp-docker/tests/test_env_resolve.py', 'test_resolve_env_var_falls_back_to_process_env', 0, 3, 2).
python_function('urirdp-docker/tests/test_env_resolve.py', 'test_resolve_env_var_secret_via_env_policy', 1, 4, 3).
python_function('urirdp-docker/tests/test_rdp_kvm.py', 'test_routes_registered', 0, 6, 2).
python_function('urirdp-docker/tests/test_rdp_kvm.py', 'test_rdp_display_status_mock', 0, 5, 3).
python_function('urirdp-docker/tests/test_rdp_kvm.py', 'test_kvm_click_text_dry_run_pipeline', 0, 3, 4).
python_function('urirdp-docker/tests/test_rdp_kvm.py', 'test_rdp_status', 0, 3, 3).
python_function('urirdp-docker/tests/test_rdp_kvm.py', 'test_kvm_click_text_dry_run', 0, 4, 3).
python_function('urirdp-docker/tests/test_rdp_kvm.py', 'test_kvm_click_text_real_without_display', 0, 4, 3).
python_function('urirdp-docker/tests/test_rdp_kvm.py', 'test_him_requires_approval', 0, 3, 3).
python_function('uristepper-docker/tests/e2e.py', 'post', 2, 1, 7).
python_function('uristepper-docker/tests/e2e.py', 'get', 1, 1, 4).
python_function('uristepper-docker/tests/e2e.py', 'assert_ok', 2, 2, 4).
python_function('uristepper-docker/tests/e2e.py', 'main', 0, 3, 7).
python_function('urisys-automation-lab/server/automation_lab_server.py', 'build_lab_runtime', 1, 17, 11).
python_function('urisys-automation-lab/server/automation_lab_server.py', 'forward_uri_call', 4, 4, 9).
python_function('urisys-automation-lab/server/automation_lab_server.py', 'serve', 2, 4, 8).
python_function('urisys-automation-lab/server/flow_runner.py', '_require_uri_stack', 0, 2, 1).
python_function('urisys-automation-lab/server/flow_runner.py', '_execution_root', 2, 4, 4).
python_function('urisys-automation-lab/server/flow_runner.py', '_load_defaults', 1, 5, 6).
python_function('urisys-automation-lab/server/flow_runner.py', '_lab_adapter_session', 0, 1, 3).
python_function('urisys-automation-lab/server/flow_runner.py', 'plan_flow', 1, 2, 7).
python_function('urisys-automation-lab/server/flow_runner.py', '_legacy_step', 4, 7, 3).
python_function('urisys-automation-lab/server/flow_runner.py', 'run_flow_file', 1, 13, 18).
python_function('urisys-automation-lab/server/lab_uri_adapter.py', 'step_ok', 1, 9, 3).
python_function('urisys-automation-lab/tests/test_flow_08_plan.py', '_rt', 0, 1, 2).
python_function('urisys-automation-lab/tests/test_flow_08_plan.py', 'test_message_alert_send', 0, 4, 2).
python_function('urisys-automation-lab/tests/test_flow_08_plan.py', 'test_llm_plan_from_transcript', 0, 4, 2).
python_function('urisys-automation-lab/tests/test_flow_08_plan.py', 'test_flow_08_plan_expand', 0, 5, 2).
python_function('urisys-automation-lab/tests/test_flow_09_plan.py', 'test_flow_09_no_chat_bridge', 0, 5, 3).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_flow_files_exist', 0, 2, 0).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_expect_block_is_well_formed', 1, 15, 6).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_flow_still_parses_with_expect', 1, 4, 5).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_evaluate_screen_changed', 0, 3, 1).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_evaluate_screen_changed_since_previous', 0, 3, 1).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_evaluate_ocr_contains', 0, 3, 1).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_evaluate_min_vision_confidence', 0, 3, 1).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_no_expect_is_transport_only', 0, 2, 1).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_evaluate_opened_url_contains', 0, 3, 1).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_analyzer_reports_duplicate_screenshots', 0, 5, 3).
python_function('urisys-automation-lab/tests/test_flow_expectations.py', 'test_analyzer_contract_overrides_heuristic', 0, 3, 3).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', '_rt', 0, 1, 2).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', 'test_stt_session_and_transcript', 0, 4, 3).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', 'test_chat_uri_execute_dry_run', 0, 4, 2).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', 'test_webrtc_data_send', 0, 4, 3).
python_function('urisys-automation-lab/tests/test_llm_plan_handlers.py', 'test_plan_phrase_map_default', 0, 5, 1).
python_function('urisys-automation-lab/tests/test_llm_plan_handlers.py', 'test_plan_rejects_disallowed_scheme', 0, 3, 1).
python_function('urisys-automation-lab/tests/test_llm_plan_handlers.py', 'test_plan_litellm_fallback_on_error', 0, 4, 3).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_select_artifact_by_platform', 1, 2, 4).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_load_artifact_index_from_file', 1, 2, 3).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_load_artifact_index_from_url', 0, 2, 2).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_fetch_release', 0, 2, 3).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_release_api_url', 0, 2, 1).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_run_release_honors_artifact_container_port', 2, 4, 3).
python_function('urisys-node/tests/test_docker_host_e2e.py', '_http_get', 1, 1, 4).
python_function('urisys-node/tests/test_docker_host_e2e.py', '_remote_call', 3, 3, 7).
python_function('urisys-node/tests/test_docker_host_e2e.py', 'docker_stack', 0, 7, 10).
python_function('urisys-node/tests/test_docker_host_e2e.py', 'test_container_urisys_cli', 1, 3, 1).
python_function('urisys-node/tests/test_docker_host_e2e.py', 'test_host_health_and_routes', 1, 5, 3).
python_function('urisys-node/tests/test_docker_host_e2e.py', 'test_host_remote_identity', 1, 4, 5).
python_function('urisys-node/tests/test_docker_host_e2e.py', 'test_host_screen_capture', 1, 5, 5).
python_function('urisys-node/tests/test_docker_host_e2e.py', 'test_host_indicator_control', 0, 5, 2).
python_function('urisys-node/tests/test_forward_config.py', '_runtime', 1, 1, 3).
python_function('urisys-node/tests/test_forward_config.py', 'test_load_forward_entries_from_config', 0, 3, 2).
python_function('urisys-node/tests/test_forward_config.py', 'test_load_forward_entries_env_inline', 0, 2, 3).
python_function('urisys-node/tests/test_forward_config.py', 'test_wire_forward_packs_registers_routes', 1, 4, 4).
python_function('urisys-node/tests/test_forward_config.py', 'test_command_register_forward', 1, 3, 2).
python_function('urisys-node/tests/test_forward_config.py', 'test_load_release_forward_entries_from_config', 0, 5, 2).
python_function('urisys-node/tests/test_forward_config.py', 'test_load_release_forward_entries_env_inline', 0, 2, 3).
python_function('urisys-node/tests/test_forward_config.py', 'test_wire_release_forward_packs_calls_hotload', 2, 3, 4).
python_function('urisys-node/tests/test_forward_config.py', 'test_wire_release_forward_packs_is_best_effort', 2, 2, 3).
python_function('urisys-node/tests/test_forward_config.py', 'test_build_runtime_wires_config_forwards', 2, 2, 7).
python_function('urisys-node/tests/test_forward_pack.py', '_runtime', 1, 1, 3).
python_function('urisys-node/tests/test_forward_pack.py', 'test_register_forward_adds_routes_and_target', 1, 10, 6).
python_function('urisys-node/tests/test_forward_pack.py', 'test_call_forwards_to_worker', 2, 7, 6).
python_function('urisys-node/tests/test_forward_pack.py', 'test_forward_without_target_fails_cleanly', 1, 3, 4).
python_function('urisys-node/tests/test_pack_auto_install.py', '_node_only_runtime', 1, 1, 3).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_install_pack_uri', 1, 2, 4).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_install_pack_requires_approval', 1, 2, 2).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_query_packs', 1, 4, 2).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_call_uri_lazy_pack_route_not_found', 1, 3, 5).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_load_pack_with_mock_pip', 1, 3, 3).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_ensure_pack_for_uri_skips_pip_when_importable', 1, 2, 4).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_force_reload_reregister_pack', 1, 6, 6).
python_function('urisys-node/tests/test_pack_auto_install.py', 'test_pack_importable_uses_import_pack_module', 0, 3, 2).
python_function('urisys-node/tests/test_pack_github.py', 'test_github_wheel_url_him', 0, 2, 1).
python_function('urisys-node/tests/test_pack_github.py', 'test_resolve_pack_spec_auto_prefers_github_for_him', 0, 2, 2).
python_function('urisys-node/tests/test_pack_github.py', 'test_resolve_pack_spec_kvm_stays_pypi', 0, 2, 1).
python_function('urisys-node/tests/test_pack_hotload.py', '_node_only_runtime', 1, 1, 3).
python_function('urisys-node/tests/test_pack_hotload.py', 'test_hotload_adds_routes', 1, 6, 4).
python_function('urisys-node/tests/test_pack_hotload.py', 'test_hotload_is_idempotent', 1, 4, 3).
python_function('urisys-node/tests/test_pack_hotload.py', 'test_hotload_empty_pack_name_rejected', 1, 2, 2).
python_function('urisys-node/tests/test_pack_hotload.py', 'test_hotload_unknown_pack_reports_failure', 1, 3, 2).
python_function('urisys-node/tests/test_pack_office_mail.py', 'test_scheme_to_pack_office_mail_vql', 0, 5, 1).
python_function('urisys-node/tests/test_pack_office_mail.py', 'test_pack_modules_office_mail_vql', 0, 5, 1).
python_function('urisys-node/tests/test_release_hotload.py', '_runtime', 1, 1, 3).
python_function('urisys-node/tests/test_release_hotload.py', '_release', 0, 1, 1).
python_function('urisys-node/tests/test_release_hotload.py', 'test_canonical_digest_ignores_signature_block', 0, 2, 2).
python_function('urisys-node/tests/test_release_hotload.py', 'test_disabled_policy_passes_through', 1, 4, 3).
python_function('urisys-node/tests/test_release_hotload.py', 'test_required_but_unsigned_fails', 1, 3, 3).
python_function('urisys-node/tests/test_release_hotload.py', 'test_required_untrusted_key_fails', 1, 3, 3).
python_function('urisys-node/tests/test_release_hotload.py', 'test_required_no_crypto_backend_fails_closed', 1, 3, 5).
python_function('urisys-node/tests/test_release_hotload.py', 'test_required_good_signature_verifies', 1, 4, 4).
python_function('urisys-node/tests/test_release_hotload.py', 'test_required_mismatched_signature_fails', 1, 3, 4).
python_function('urisys-node/tests/test_release_hotload.py', 'test_hotload_requires_pairing', 2, 4, 6).
python_function('urisys-node/tests/test_release_hotload.py', 'test_hotload_happy_path_wires_forward', 2, 10, 10).
python_function('urisys-node/tests/test_release_hotload.py', 'test_hotload_bad_signature_skips_run', 2, 3, 7).
python_function('urisys-node/tests/test_release_hotload.py', 'test_hotload_missing_scheme_patterns', 2, 3, 8).
python_function('urisys-node/tests/test_release_hotload.py', 'test_parse_contract_spec_extracts_scheme_and_patterns', 0, 3, 1).
python_function('urisys-node/tests/test_release_hotload.py', 'test_parse_contract_spec_rejects_block_without_scheme', 0, 1, 2).
python_function('urisys-node/tests/test_release_hotload.py', 'test_contract_url_from_release_variants', 0, 4, 1).
python_function('urisys-node/tests/test_release_hotload.py', 'test_hotload_derives_spec_from_contract', 2, 7, 9).
python_function('urisys-node/tests/test_uriscreen_auto.py', 'test_resolve_backend_auto_x11', 1, 2, 2).
python_function('urisys-node/tests/test_uriscreen_auto.py', 'test_resolve_backend_auto_wayland', 1, 2, 2).
python_function('urisys-node/tests/test_uriscreen_auto.py', 'test_is_black_png', 1, 3, 4).
python_function('urisys-node/tests/test_urishell.py', 'test_shell_route_registered', 0, 2, 3).
python_function('urisys-node/tests/test_urishell.py', 'test_shell_pip_dry_run', 0, 4, 3).
python_function('urisys-node/tests/test_urishell.py', 'test_shell_requires_allow_real', 0, 3, 4).
python_function('urisys-node/tests/test_urisys_node.py', 'test_identity_and_enroll', 0, 5, 3).
python_function('urisys-node/tests/test_urisys_node.py', 'test_screen_capture_mock', 0, 4, 4).
python_function('urisys-node/tests/test_urisys_node.py', 'test_rewrite_uri_for_slave', 0, 2, 1).
python_function('urisys-node/tests/test_urisys_node.py', 'test_health_payload', 0, 6, 1).
python_function('urisys-node/tests/test_urisys_node.py', 'test_health_payload_with_runtime', 0, 4, 2).
python_function('urisys-node/tests/test_urisysedge_single_source.py', 'test_canonical_urisysedge_present', 0, 3, 1).
python_function('urisys-node/tests/test_urisysedge_single_source.py', 'test_urisysedge_imports_from_canonical', 0, 4, 0).
python_function('urisys-node/tests/test_urisysedge_single_source.py', 'test_no_vendored_duplicate_module', 1, 2, 4).

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
python_class('src/urisys/managers/bridge_manager.py', 'BridgeManager').
python_method('BridgeManager', 'call_http', 5, 3, 7).
python_class('src/urisys/managers/event_manager.py', 'EventManager').
python_method('EventManager', '__init__', 1, 1, 2).
python_method('EventManager', 'list_events', 0, 1, 2).
python_class('src/urisys/managers/markpact_manager.py', 'MarkpactManager').
python_method('MarkpactManager', '__init__', 1, 1, 1).
python_method('MarkpactManager', 'read_blocks', 1, 3, 8).
python_method('MarkpactManager', 'source_hash', 1, 1, 1).
python_method('MarkpactManager', 'load_pack_block', 1, 4, 6).
python_method('MarkpactManager', 'validate', 1, 12, 12).
python_method('MarkpactManager', '_validate_pack', 3, 11, 16).
python_method('MarkpactManager', '_yaml_blocks', 2, 4, 0).
python_method('MarkpactManager', 'compile', 1, 21, 25).
python_method('MarkpactManager', 'manifest_path_for', 1, 1, 1).
python_method('MarkpactManager', 'run_tests', 1, 20, 15).
python_method('MarkpactManager', '_build_route', 1, 18, 11).
python_method('MarkpactManager', '_compile_manifest', 1, 11, 5).
python_method('MarkpactManager', '_package_id', 2, 5, 5).
python_method('MarkpactManager', '_capabilities', 1, 6, 3).
python_method('MarkpactManager', '_scheme', 2, 8, 5).
python_method('MarkpactManager', '_handler_blocks', 1, 5, 2).
python_method('MarkpactManager', '_load_yaml_blocks', 2, 6, 4).
python_method('MarkpactManager', '_handler_id_from_ref', 1, 2, 2).
python_method('MarkpactManager', '_ensure_importable', 1, 2, 3).
python_class('src/urisys/managers/markpact_models.py', 'MarkpactBlock').
python_class('src/urisys/managers/markpact_models.py', 'CompiledMarkpact').
python_method('CompiledMarkpact', 'to_dict', 0, 4, 1).
python_class('src/urisys/managers/markpact_models.py', 'MarkpactError').
python_class('src/urisys/managers/pack_manager.py', 'PackManager').
python_method('PackManager', '__init__', 1, 1, 6).
python_method('PackManager', '_is_all', 1, 10, 5).
python_method('PackManager', 'parse_packs', 1, 15, 6).
python_method('PackManager', 'parse_markpacts', 1, 8, 4).
python_method('PackManager', 'resolve_package_name', 1, 1, 1).
python_method('PackManager', '_is_markpact_path', 1, 3, 2).
python_method('PackManager', '_is_manifest_path', 1, 4, 1).
python_method('PackManager', 'manifest_paths', 0, 9, 14).
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
python_method('SourceManager', '_fetch_http', 1, 7, 14).
python_method('SourceManager', '_fetch_github_uri', 1, 4, 6).
python_method('SourceManager', '_fetch_github_raw', 4, 6, 13).
python_method('SourceManager', '_fetch_git', 1, 11, 18).
python_method('SourceManager', '_fetch_zip', 1, 10, 17).
python_class('tests/test_python_compat.py', '_FakeVersionInfo').
python_method('_FakeVersionInfo', '__init__', 3, 1, 0).
python_method('_FakeVersionInfo', '__getitem__', 1, 1, 0).
python_method('_FakeVersionInfo', '__ge__', 1, 1, 0).
python_method('_FakeVersionInfo', '__lt__', 1, 1, 0).
python_class('urirdp-docker/tests/test_env_browser_routes.py', '_Args').
python_class('urirdp-docker/tests/test_rdp_kvm.py', 'Args').
python_class('uristepper-docker/tests/test_runtime.py', 'RuntimeTest').
python_method('RuntimeTest', 'setUp', 0, 1, 6).
python_method('RuntimeTest', 'test_status', 0, 1, 3).
python_method('RuntimeTest', 'test_policy_requires_approval', 0, 1, 3).
python_method('RuntimeTest', 'test_move_relative', 0, 1, 3).
python_method('RuntimeTest', 'test_safety_limit', 0, 1, 3).
python_class('urisys-automation-lab/server/automation_lab_server.py', 'LabHandler').
python_method('LabHandler', 'log_message', 1, 1, 2).
python_method('LabHandler', '_json', 2, 1, 8).
python_method('LabHandler', '_read_json', 0, 4, 5).
python_method('LabHandler', 'do_OPTIONS', 0, 1, 3).
python_method('LabHandler', 'do_GET', 0, 9, 12).
python_method('LabHandler', 'do_POST', 0, 23, 9).
python_class('urisys-automation-lab/server/lab_uri_adapter.py', 'LabCallAdapter').
python_method('LabCallAdapter', 'execute', 2, 12, 12).
python_method('LabCallAdapter', '_execute_log', 4, 3, 6).

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

*166 nodes · 238 edges · 35 modules · CC̄=4.4*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `session_urirdp_real_docker` *(in scripts.run_test_sessions)* | 30 ⚠ | 0 | 69 | **69** |
| `main` *(in src.urisys.cli)* | 36 ⚠ | 0 | 68 | **68** |
| `build_parser` *(in src.urisys.cli)* | 1 | 1 | 61 | **62** |
| `print` *(in scripts.run-nl-log-smoke)* | 0 | 47 | 0 | **47** |
| `run_init` *(in src.urisys.init_setup)* | 41 ⚠ | 2 | 43 | **45** |
| `session_automation_lab` *(in scripts.run_test_sessions)* | 16 ⚠ | 1 | 43 | **44** |
| `run_cmd` *(in scripts.test_sessions.util)* | 6 | 31 | 12 | **43** |
| `run_flow_file` *(in urisys-automation-lab.server.flow_runner)* | 13 ⚠ | 1 | 40 | **41** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.08s
# nodes: 166 | edges: 238 | modules: 35
# CC̄=4.4

HUBS[20]:
  scripts.run_test_sessions.session_urirdp_real_docker
    CC=30  in:0  out:69  total:69
  src.urisys.cli.main
    CC=36  in:0  out:68  total:68
  src.urisys.cli.build_parser
    CC=1  in:1  out:61  total:62
  scripts.run-nl-log-smoke.print
    CC=0  in:47  out:0  total:47
  src.urisys.init_setup.run_init
    CC=41  in:2  out:43  total:45
  scripts.run_test_sessions.session_automation_lab
    CC=16  in:1  out:43  total:44
  scripts.test_sessions.util.run_cmd
    CC=6  in:31  out:12  total:43
  urisys-automation-lab.server.flow_runner.run_flow_file
    CC=13  in:1  out:40  total:41
  scripts.pack_sync.main
    CC=28  in:0  out:39  total:39
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  scripts.test_sessions.util.finalize_session
    CC=5  in:21  out:13  total:34
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  scripts.run_test_sessions.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  scripts.pack_registry.pack_specs
    CC=17  in:2  out:28  total:30
  scripts.report.session.generate_report
    CC=9  in:2  out:27  total:29
  scripts.report.session.infer_steps
    CC=20  in:1  out:25  total:26
  urikvm-docker.scripts.real_pipeline.main
    CC=14  in:0  out:26  total:26
  urisys-automation-lab.server.automation_lab_server.build_lab_runtime
    CC=17  in:1  out:23  total:24

MODULES:
  scripts.office-simulate-loop  [5 funcs]
    call_uri  CC=4  out:11
    llm_tick  CC=7  out:18
    main  CC=10  out:12
    parse_args  CC=1  out:8
    rules_tick  CC=3  out:8
  scripts.pack_registry  [4 funcs]
    _repo  CC=1  out:0
    all_promoted_packs  CC=1  out:3
    pack_specs  CC=17  out:28
    sibling_repo  CC=1  out:1
  scripts.pack_sync  [13 funcs]
    _check_promoted  CC=5  out:7
    _repo_pyproject  CC=14  out:12
    check_drift  CC=14  out:19
    file_hash  CC=1  out:3
    init_repo  CC=12  out:21
    main  CC=28  out:39
    promote  CC=1  out:2
    read_version  CC=3  out:8
    remove_vendored  CC=4  out:3
    repo_module_dir  CC=2  out:0
  scripts.report.cli  [1 funcs]
    main  CC=4  out:23
  scripts.report.events  [4 funcs]
    load_event_records  CC=14  out:14
    merge_event_summaries  CC=10  out:16
    summarize_event_records  CC=14  out:15
    summarize_events  CC=8  out:10
  scripts.report.lab_checks  [5 funcs]
    _duplicate_recommendation  CC=6  out:1
    analyze_lab_flows  CC=5  out:4
    check_duplicate_screenshots  CC=5  out:3
    iter_step_results  CC=9  out:7
    load_flow_outcomes  CC=15  out:22
  scripts.report.run_analysis  [2 funcs]
    analyze_run  CC=13  out:33
    write_run_analysis  CC=2  out:7
  scripts.report.run_markdown  [1 funcs]
    render_run_analysis_markdown  CC=7  out:16
  scripts.report.session  [3 funcs]
    generate_report  CC=9  out:27
    infer_steps  CC=20  out:25
    session_duration  CC=5  out:14
  scripts.report.session_io  [1 funcs]
    write_session_report  CC=2  out:7
  scripts.report.session_markdown  [4 funcs]
    _environment_section  CC=5  out:7
    _screenshots_section  CC=3  out:3
    _steps_section  CC=7  out:4
    render_session_markdown  CC=1  out:16
  scripts.report.util  [4 funcs]
    host_id  CC=1  out:3
    now_iso  CC=1  out:3
    read_json  CC=3  out:3
    tail  CC=2  out:0
  scripts.run-nl-log-smoke  [1 funcs]
    print  CC=0  out:0
  scripts.run-office-writer-e2e  [2 funcs]
    save_json  CC=0  out:0
    wait_health  CC=0  out:0
  scripts.run-urisys-node-docker-e2e  [1 funcs]
    http_json  CC=0  out:0
  scripts.run_test_sessions  [14 funcs]
    _monorepo_root  CC=4  out:3
    main  CC=13  out:32
    session_automation_lab  CC=16  out:43
    session_email_mailpit  CC=7  out:13
    session_office_simulate  CC=7  out:13
    session_office_simulate_lenovo  CC=6  out:10
    session_office_writer  CC=7  out:13
    session_pytest_urirdp  CC=3  out:5
    session_pytest_urisys  CC=2  out:5
    session_pytest_urisys_node  CC=2  out:5
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
  scripts.test_sessions.util  [14 funcs]
    compose_cmd  CC=4  out:4
    copy_container_file  CC=2  out:4
    docker_logs  CC=3  out:3
    file_md5  CC=2  out:4
    finalize_session  CC=5  out:13
    http_json  CC=9  out:18
    now_iso  CC=1  out:3
    prepare_urirdp_data  CC=4  out:6
    read_meta  CC=3  out:3
    run_cmd  CC=6  out:12
  src.urisys.bootstrap  [5 funcs]
    _doctor_main  CC=3  out:7
    _init_main  CC=6  out:18
    _missing_uricore_payload  CC=1  out:1
    _print_json  CC=1  out:2
    main  CC=8  out:6
  src.urisys.cli  [5 funcs]
    _add_runtime_flags  CC=1  out:4
    build_parser  CC=1  out:61
    main  CC=36  out:68
    print_json  CC=1  out:2
    resolve_markpact_source  CC=2  out:3
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
  src.urisys.http_server  [3 funcs]
    _read_json  CC=3  out:5
    _send  CC=1  out:12
    create_server  CC=1  out:31
  src.urisys.init_setup  [6 funcs]
    default_pip_specs  CC=1  out:1
    profile_env  CC=2  out:1
    render_env_shell  CC=2  out:5
    run_init  CC=41  out:43
    verify_uri_control  CC=2  out:3
    write_env_file  CC=2  out:7
  src.urisys.node_install  [6 funcs]
    diagnose_urisys_node  CC=3  out:4
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    is_importable  CC=1  out:1
    pip_spec  CC=1  out:1
    wheel_url  CC=3  out:5
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
  urikvm-docker.scripts.real_pipeline  [2 funcs]
    build_runtime  CC=1  out:6
    main  CC=14  out:26
  urisys-automation-lab.server.automation_lab_server  [3 funcs]
    log_message  CC=1  out:2
    build_lab_runtime  CC=17  out:23
    serve  CC=4  out:13
  urisys-automation-lab.server.flow_runner  [5 funcs]
    _lab_adapter_session  CC=1  out:3
    _load_defaults  CC=5  out:7
    _require_uri_stack  CC=2  out:1
    plan_flow  CC=2  out:7
    run_flow_file  CC=13  out:40
  urisys-automation-lab.server.lab_uri_adapter  [2 funcs]
    execute  CC=12  out:20
    step_ok  CC=9  out:9
  urisys-automation-lab.web.app  [6 funcs]
    SR  CC=2  out:1
    data  CC=1  out:1
    log  CC=2  out:2
    rec  CC=1  out:1
    text  CC=1  out:2
    uriCall  CC=1  out:4

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
  src.urisys.bootstrap._print_json → scripts.run-nl-log-smoke.print
  src.urisys.bootstrap._doctor_main → src.urisys.doctor.run_doctor
  src.urisys.bootstrap._doctor_main → src.urisys.bootstrap._print_json
  src.urisys.bootstrap._init_main → src.urisys.init_setup.run_init
  src.urisys.bootstrap._init_main → src.urisys.bootstrap._print_json
  src.urisys.bootstrap.main → src.urisys.bootstrap._doctor_main
  src.urisys.bootstrap.main → src.urisys.bootstrap._init_main
  src.urisys.bootstrap.main → src.urisys.bootstrap._print_json
  src.urisys.bootstrap.main → src.urisys.bootstrap._missing_uricore_payload
  src.urisys.cli.print_json → scripts.run-nl-log-smoke.print
  src.urisys.cli.build_parser → src.urisys.cli._add_runtime_flags
  src.urisys.cli.main → src.urisys.cli.build_parser
  src.urisys.cli.main → src.urisys.cli.resolve_markpact_source
  src.urisys.cli.main → src.urisys.doctor.run_doctor
  src.urisys.cli.main → src.urisys.cli.print_json
  src.urisys.cli.main → src.urisys.init_setup.run_init
  src.urisys.cli.main → scripts.run-nl-log-smoke.print
  src.urisys.http_server.create_server → src.urisys.http_server._send
  src.urisys.http_server.create_server → src.urisys.http_server._read_json
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.load_flow
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.iter_steps
  src.urisys.controllers.server_controller.ServerController.__init__ → src.urisys.http_server.create_server
  src.urisys.controllers.server_controller.ServerController.serve_forever → scripts.run-nl-log-smoke.print
  scripts.office-simulate-loop.rules_tick → scripts.office-simulate-loop.call_uri
  scripts.office-simulate-loop.rules_tick → scripts.run-nl-log-smoke.print
  scripts.office-simulate-loop.llm_tick → scripts.office-simulate-loop.call_uri
  scripts.office-simulate-loop.llm_tick → scripts.run-nl-log-smoke.print
  scripts.office-simulate-loop.main → scripts.office-simulate-loop.parse_args
  scripts.office-simulate-loop.main → scripts.run-nl-log-smoke.print
  scripts.office-simulate-loop.main → scripts.office-simulate-loop.rules_tick
  scripts.office-simulate-loop.main → scripts.office-simulate-loop.llm_tick
  scripts.run_test_sessions.session_pytest_urirdp → scripts.report.util.now_iso
  scripts.run_test_sessions.session_pytest_urirdp → scripts.test_sessions.util.write_meta
  scripts.run_test_sessions.session_pytest_urirdp → scripts.test_sessions.util.run_cmd
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
