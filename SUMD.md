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
- **version**: `0.1.65`
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
  version: 0.1.65;
}

dependencies {
  runtime: "PyYAML>=6.0, urisysedge>=0.1.0";
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
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_URI_MODEL, LLM_URI_BASE_URL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK, URISYS_URICORE_GITHUB_OWNER, URISYS_URICORE_VERSION, URISYS_URICORE_WHEEL_URL, URISYS_MIN_VERSION, URISYS_INIT_PROFILE, URISYS_NODE_HOST, URISYS_NODE_PORT, URISYS_NODE_CONFIG, WAYLAND_DISPLAY, URISYS_NODE_GITHUB_OWNER, URISYS_NODE_VERSION, URISYS_NODE_WHEEL_URL, URISYS_NODE_PIP_SPEC;
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
  version: 0.1.65
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
# urisys | 111f 10707L | python:68,shell:41,less:1,javascript:1 | 2026-06-17
# stats: 315 func | 23 cls | 111 mod | CC̄=5.4 | critical:43 | cycles:0
# alerts[5]: CC main=37; CC run_init=31; CC main=28; CC infer_steps=28; CC session_urirdp_real_docker=25
# hotspots[5]: main fan=42; session_urirdp_real_docker fan=27; analyze_run fan=23; session_lab_10_flows fan=22; run_flow fan=20
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[111]:
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
  scripts/bootstrap-lenovo-local.sh,58
  scripts/ci-checkout-siblings.sh,52
  scripts/ci-install-siblings.sh,29
  scripts/deploy-lenovo-node.sh,131
  scripts/install-kvm-packs-editable.sh,14
  scripts/lenovo-node-session.sh,74
  scripts/lenovo_remote_session.py,796
  scripts/office-simulate-loop.py,147
  scripts/pack_registry.py,270
  scripts/pack_sync.py,348
  scripts/paths.sh,55
  scripts/publish-pypi-packs.sh,54
  scripts/publish-urisys-node-release.sh,20
  scripts/remote-node-smoke.sh,100
  scripts/report/__init__.py,62
  scripts/report/cli.py,42
  scripts/report/events.py,139
  scripts/report/lab_checks.py,189
  scripts/report/models.py,87
  scripts/report/run_analysis.py,130
  scripts/report/run_markdown.py,43
  scripts/report/session.py,116
  scripts/report/session_io.py,20
  scripts/report/session_markdown.py,121
  scripts/report/util.py,22
  scripts/run-email-mailpit-e2e.sh,135
  scripts/run-lab-e2e.sh,15
  scripts/run-lab-nightly.sh,17
  scripts/run-lab-unit-ci.sh,22
  scripts/run-lenovo-office-linkedin.sh,119
  scripts/run-nl-log-smoke.sh,44
  scripts/run-office-simulate-e2e.sh,131
  scripts/run-office-simulate-lenovo.sh,183
  scripts/run-office-writer-e2e.sh,114
  scripts/run-smoke-all.sh,25
  scripts/run-urisys-node-docker-e2e.sh,164
  scripts/run-urisys-node-docker-session.sh,7
  scripts/run_test_sessions.py,762
  scripts/scan-browser-sessions.py,200
  scripts/session_core.py,277
  scripts/session_report.py,50
  scripts/sync-vendored-pack.sh,39
  scripts/sync-vendored-urisysedge.sh,18
  scripts/test-goal.sh,12
  scripts/test-python-matrix.sh,59
  scripts/test_sessions/__init__.py,101
  scripts/test_sessions/expectations.py,154
  scripts/test_sessions/lab_flows.py,321
  scripts/test_sessions/lab_rdp.py,181
  scripts/test_sessions/util.py,202
  scripts/validate-all-markpacts.sh,54
  scripts/validate-pypi-metadata.sh,63
  src/urisys/__init__.py,4
  src/urisys/bootstrap.py,117
  src/urisys/cli.py,336
  src/urisys/controllers/__init__.py,1
  src/urisys/controllers/flow_controller.py,34
  src/urisys/controllers/server_controller.py,20
  src/urisys/controllers/uri_controller.py,34
  src/urisys/defaults.py,29
  src/urisys/doctor.py,297
  src/urisys/edge_install.py,79
  src/urisys/flow.py,26
  src/urisys/http_server.py,80
  src/urisys/init_setup.py,263
  src/urisys/managers/__init__.py,1
  src/urisys/managers/bridge_manager.py,15
  src/urisys/managers/event_manager.py,14
  src/urisys/managers/markpact_manager.py,413
  src/urisys/managers/markpact_models.py,93
  src/urisys/managers/markpact_validation.py,157
  src/urisys/managers/pack_manager.py,138
  src/urisys/managers/policy_manager.py,19
  src/urisys/managers/route_manager.py,24
  src/urisys/managers/runtime_manager.py,31
  src/urisys/managers/source_manager.py,219
  src/urisys/node_install.py,107
  src/urisys/uricore_install.py,131
  tests/test_bootstrap.py,61
  tests/test_doctor.py,29
  tests/test_doctor_uricore.py,27
  tests/test_edge_install.py,33
  tests/test_init.py,61
  tests/test_kvm_pack_pyprojects.py,69
  tests/test_markpact.py,100
  tests/test_node_install.py,39
  tests/test_pack_manager_parse.py,45
  tests/test_pypi_metadata.py,35
  tests/test_python_compat.py,53
  tests/test_run_expectations.py,56
  tests/test_session_core.py,82
  tests/test_session_report_events.py,59
  tests/test_source_manager.py,36
  tests/test_uricore_install.py,38
  tests/test_urisys.py,46
  tests/test_vendored_sync.py,58
  tree.sh,2
D:
  scripts/lenovo_remote_session.py:
    e: load_yaml,http_get,_run_http_get_step,_run_host_sleep_step,_run_host_restart_and_wait_step,_run_host_schedule_restart_step,_run_host_wait_health_step,_run_uri_call_step,run_step,run_flow,append_log,build_wheels,start_wheel_server,_needs_node_upgrade,_run_upgrade_flow,_md_header,_md_flow_results,_md_step_detail,_md_lessons,write_session_md,resolve_flow_paths,resolve_route_map,load_manifest_session,_run_flows,main
    load_yaml(path)
    http_get(endpoint;path)
    _run_http_get_step(step;out;endpoint)
    _run_host_sleep_step(step;out)
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
    _run_flows(flow_paths)
    main(argv)
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
    e: read_json,tail
    read_json(path)
    tail(text;limit)
  scripts/run_test_sessions.py:
    e: session_pytest_urirdp,session_pytest_urisys,session_pytest_urisys_node,session_urirdp_mock_docker,_record_health,_bootstrap_rdp,_read_display_env,_call_and_record,session_urirdp_real_docker,session_urirdp_rdp_e2e,session_automation_lab,_monorepo_root,session_urisys_node_docker_gui,session_office_simulate,session_office_simulate_lenovo,session_office_writer,session_email_mailpit,main
    session_pytest_urirdp(session_dir)
    session_pytest_urisys(session_dir)
    session_pytest_urisys_node(session_dir)
    session_urirdp_mock_docker(session_dir)
    _record_health(session_dir;steps;seq;name;url;attempts)
    _bootstrap_rdp(container;log;steps;raise_on_fail)
    _read_display_env(container)
    _call_and_record(session_dir;steps;seq;name;uri;payload;ctx;timeout;port;step_name)
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
  scripts/scan-browser-sessions.py:
    e: _copy_query,scan_chrome_cookies,chrome_profiles,firefox_profiles,discover_browsers,main
    _copy_query(db_path;sql_chrome;sql_firefox)
    scan_chrome_cookies(db_path)
    chrome_profiles(base)
    firefox_profiles(base)
    discover_browsers(home)
    main()
  scripts/session_core.py:
    e: default_examples_root,resolve_flow_ref,now_iso,host_id,run_id,save_json,step_ok,image_ext,write_base64_image,extract_images_from_dict,extract_step_screenshots,backfill_session_images,_wheel_version_key,find_wheel_file,wheel_url,expand_step_wheels
    default_examples_root()
    resolve_flow_ref(ref)
    now_iso()
    host_id()
    run_id(prefix)
    save_json(path;data)
    step_ok(result)
    image_ext(mime)
    write_base64_image(b64;dest)
    extract_images_from_dict(obj)
    extract_step_screenshots(step)
    backfill_session_images(session_dir)
    _wheel_version_key(path;prefix)
    find_wheel_file(deploy_dir;prefix)
    wheel_url(wheel_server;wheel_path)
    expand_step_wheels(step)
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
  src/urisys/__init__.py:
  src/urisys/bootstrap.py:
    e: _print_json,_missing_uricore_payload,_doctor_main,_init_main,main
    _print_json(data)
    _missing_uricore_payload(exc)
    _doctor_main(argv)
    _init_main(argv)
    main(argv)
  src/urisys/cli.py:
    e: _json_arg,print_json,_add_runtime_flags,resolve_markpact_source,build_parser,_cmd_markpact,_cmd_init,_cmd_node,_cmd_uri,_handle_cli_error,main
    _json_arg(value)
    print_json(data)
    _add_runtime_flags(parser)
    resolve_markpact_source(source)
    build_parser()
    _cmd_markpact(args)
    _cmd_init(args)
    _cmd_node(args)
    _cmd_uri(args)
    _handle_cli_error(exc)
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
  src/urisys/edge_install.py:
    e: is_importable,_dist_version,is_broken_install,pip_run,repair_urisysedge,ensure_urisysedge
    is_importable()
    _dist_version()
    is_broken_install()
    pip_run(args)
    repair_urisysedge()
    ensure_urisysedge()
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
    e: default_pip_specs,default_node_pip_spec,pip_install_specs,verify_uri_control,profile_env,render_env_shell,write_env_file,_pre_repair_uricore,_build_pip_result,_resolve_error_hint,run_init
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
    MarkpactManager: __init__(1),read_blocks(1),source_hash(1),load_pack_block(1),validate(1),_validate_pack(3),_yaml_blocks(2),compile(1),_write_handler_modules(2),manifest_path_for(1),run_tests(1),_check_expectations(2),_build_route(1),_resolve_handler_ref(4),_compile_manifest(1),_package_id(2),_capabilities(1),_scheme(2),_handler_blocks(1),_load_yaml_blocks(2),_handler_id_from_ref(1),_ensure_importable(1)  # Parses and compiles one-file UriPack Markpacts.
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
    e: _validate_contract_routes,validate_contract,_missing_bundle_imports,validate_bundle,_validate_implementation_capabilities,validate_implementation
    _validate_contract_routes(source_path;data;scheme)
    validate_contract(source_path;data;source_hash)
    _missing_bundle_imports(source_path;imports)
    validate_bundle(source_path;data;source_hash)
    _validate_implementation_capabilities(source_path;capabilities)
    validate_implementation(source_path;data;source_hash)
  src/urisys/managers/pack_manager.py:
    e: PackManager
    PackManager: __init__(1),_split_specs(1),_is_all(1),parse_packs(1),parse_markpacts(1),resolve_package_name(1),_is_markpact_path(1),_is_manifest_path(1),manifest_paths(0),create_registry(0),capabilities(0),close(0),__enter__(0),__exit__(3)  # Loads separate uri* packages, plain manifest.yaml files and 
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
  tests/test_edge_install.py:
    e: test_repair_calls_force_reinstall_when_broken,test_ensure_short_circuits_when_importable
    test_repair_calls_force_reinstall_when_broken()
    test_ensure_short_circuits_when_importable()
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
    e: test_default_pip_specs_no_git_urls,test_urisys_node_uses_release_wheel,test_urisys_node_wheel_filename_pep427,test_urisys_node_wheel_url_override
    test_default_pip_specs_no_git_urls()
    test_urisys_node_uses_release_wheel()
    test_urisys_node_wheel_filename_pep427()
    test_urisys_node_wheel_url_override()
  tests/test_pack_manager_parse.py:
    e: test_parse_packs_default_set,test_parse_packs_explicit_and_none_filter,test_is_all,test_parse_markpacts
    test_parse_packs_default_set()
    test_parse_packs_explicit_and_none_filter()
    test_is_all()
    test_parse_markpacts()
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
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('urisys', '0.1.65', 'python').

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
project_file('scripts/bootstrap-lenovo-local.sh', 58, 'shell').
project_file('scripts/ci-checkout-siblings.sh', 52, 'shell').
project_file('scripts/ci-install-siblings.sh', 29, 'shell').
project_file('scripts/deploy-lenovo-node.sh', 131, 'shell').
project_file('scripts/install-kvm-packs-editable.sh', 14, 'shell').
project_file('scripts/lenovo-node-session.sh', 74, 'shell').
project_file('scripts/lenovo_remote_session.py', 796, 'python').
project_file('scripts/office-simulate-loop.py', 147, 'python').
project_file('scripts/pack_registry.py', 270, 'python').
project_file('scripts/pack_sync.py', 348, 'python').
project_file('scripts/paths.sh', 55, 'shell').
project_file('scripts/publish-pypi-packs.sh', 54, 'shell').
project_file('scripts/publish-urisys-node-release.sh', 20, 'shell').
project_file('scripts/remote-node-smoke.sh', 100, 'shell').
project_file('scripts/report/__init__.py', 62, 'python').
project_file('scripts/report/cli.py', 42, 'python').
project_file('scripts/report/events.py', 139, 'python').
project_file('scripts/report/lab_checks.py', 189, 'python').
project_file('scripts/report/models.py', 87, 'python').
project_file('scripts/report/run_analysis.py', 130, 'python').
project_file('scripts/report/run_markdown.py', 43, 'python').
project_file('scripts/report/session.py', 116, 'python').
project_file('scripts/report/session_io.py', 20, 'python').
project_file('scripts/report/session_markdown.py', 121, 'python').
project_file('scripts/report/util.py', 22, 'python').
project_file('scripts/run-email-mailpit-e2e.sh', 135, 'shell').
project_file('scripts/run-lab-e2e.sh', 15, 'shell').
project_file('scripts/run-lab-nightly.sh', 17, 'shell').
project_file('scripts/run-lab-unit-ci.sh', 22, 'shell').
project_file('scripts/run-lenovo-office-linkedin.sh', 119, 'shell').
project_file('scripts/run-nl-log-smoke.sh', 44, 'shell').
project_file('scripts/run-office-simulate-e2e.sh', 131, 'shell').
project_file('scripts/run-office-simulate-lenovo.sh', 183, 'shell').
project_file('scripts/run-office-writer-e2e.sh', 114, 'shell').
project_file('scripts/run-smoke-all.sh', 25, 'shell').
project_file('scripts/run-urisys-node-docker-e2e.sh', 164, 'shell').
project_file('scripts/run-urisys-node-docker-session.sh', 7, 'shell').
project_file('scripts/run_test_sessions.py', 762, 'python').
project_file('scripts/scan-browser-sessions.py', 200, 'python').
project_file('scripts/session_core.py', 277, 'python').
project_file('scripts/session_report.py', 50, 'python').
project_file('scripts/sync-vendored-pack.sh', 39, 'shell').
project_file('scripts/sync-vendored-urisysedge.sh', 18, 'shell').
project_file('scripts/test-goal.sh', 12, 'shell').
project_file('scripts/test-python-matrix.sh', 59, 'shell').
project_file('scripts/test_sessions/__init__.py', 101, 'python').
project_file('scripts/test_sessions/expectations.py', 154, 'python').
project_file('scripts/test_sessions/lab_flows.py', 321, 'python').
project_file('scripts/test_sessions/lab_rdp.py', 181, 'python').
project_file('scripts/test_sessions/util.py', 202, 'python').
project_file('scripts/validate-all-markpacts.sh', 54, 'shell').
project_file('scripts/validate-pypi-metadata.sh', 63, 'shell').
project_file('src/urisys/__init__.py', 4, 'python').
project_file('src/urisys/bootstrap.py', 117, 'python').
project_file('src/urisys/cli.py', 336, 'python').
project_file('src/urisys/controllers/__init__.py', 1, 'python').
project_file('src/urisys/controllers/flow_controller.py', 34, 'python').
project_file('src/urisys/controllers/server_controller.py', 20, 'python').
project_file('src/urisys/controllers/uri_controller.py', 34, 'python').
project_file('src/urisys/defaults.py', 29, 'python').
project_file('src/urisys/doctor.py', 297, 'python').
project_file('src/urisys/edge_install.py', 79, 'python').
project_file('src/urisys/flow.py', 26, 'python').
project_file('src/urisys/http_server.py', 80, 'python').
project_file('src/urisys/init_setup.py', 263, 'python').
project_file('src/urisys/managers/__init__.py', 1, 'python').
project_file('src/urisys/managers/bridge_manager.py', 15, 'python').
project_file('src/urisys/managers/event_manager.py', 14, 'python').
project_file('src/urisys/managers/markpact_manager.py', 413, 'python').
project_file('src/urisys/managers/markpact_models.py', 93, 'python').
project_file('src/urisys/managers/markpact_validation.py', 157, 'python').
project_file('src/urisys/managers/pack_manager.py', 138, 'python').
project_file('src/urisys/managers/policy_manager.py', 19, 'python').
project_file('src/urisys/managers/route_manager.py', 24, 'python').
project_file('src/urisys/managers/runtime_manager.py', 31, 'python').
project_file('src/urisys/managers/source_manager.py', 219, 'python').
project_file('src/urisys/node_install.py', 107, 'python').
project_file('src/urisys/uricore_install.py', 131, 'python').
project_file('tests/test_bootstrap.py', 61, 'python').
project_file('tests/test_doctor.py', 29, 'python').
project_file('tests/test_doctor_uricore.py', 27, 'python').
project_file('tests/test_edge_install.py', 33, 'python').
project_file('tests/test_init.py', 61, 'python').
project_file('tests/test_kvm_pack_pyprojects.py', 69, 'python').
project_file('tests/test_markpact.py', 100, 'python').
project_file('tests/test_node_install.py', 39, 'python').
project_file('tests/test_pack_manager_parse.py', 45, 'python').
project_file('tests/test_pypi_metadata.py', 35, 'python').
project_file('tests/test_python_compat.py', 53, 'python').
project_file('tests/test_run_expectations.py', 56, 'python').
project_file('tests/test_session_core.py', 82, 'python').
project_file('tests/test_session_report_events.py', 59, 'python').
project_file('tests/test_source_manager.py', 36, 'python').
project_file('tests/test_uricore_install.py', 38, 'python').
project_file('tests/test_urisys.py', 46, 'python').
project_file('tests/test_vendored_sync.py', 58, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('scripts/lenovo_remote_session.py', 'load_yaml', 1, 3, 4).
python_function('scripts/lenovo_remote_session.py', 'http_get', 2, 4, 6).
python_function('scripts/lenovo_remote_session.py', '_run_http_get_step', 3, 2, 3).
python_function('scripts/lenovo_remote_session.py', '_run_host_sleep_step', 2, 3, 3).
python_function('scripts/lenovo_remote_session.py', '_run_host_restart_and_wait_step', 2, 19, 11).
python_function('scripts/lenovo_remote_session.py', '_run_host_schedule_restart_step', 2, 4, 2).
python_function('scripts/lenovo_remote_session.py', '_run_host_wait_health_step', 2, 12, 9).
python_function('scripts/lenovo_remote_session.py', '_run_uri_call_step', 2, 6, 6).
python_function('scripts/lenovo_remote_session.py', 'run_step', 1, 9, 10).
python_function('scripts/lenovo_remote_session.py', 'run_flow', 1, 14, 20).
python_function('scripts/lenovo_remote_session.py', 'append_log', 2, 1, 4).
python_function('scripts/lenovo_remote_session.py', 'build_wheels', 1, 4, 6).
python_function('scripts/lenovo_remote_session.py', 'start_wheel_server', 3, 2, 4).
python_function('scripts/lenovo_remote_session.py', '_needs_node_upgrade', 1, 4, 2).
python_function('scripts/lenovo_remote_session.py', '_run_upgrade_flow', 2, 1, 4).
python_function('scripts/lenovo_remote_session.py', '_md_header', 2, 1, 3).
python_function('scripts/lenovo_remote_session.py', '_md_flow_results', 1, 6, 4).
python_function('scripts/lenovo_remote_session.py', '_md_step_detail', 1, 12, 2).
python_function('scripts/lenovo_remote_session.py', '_md_lessons', 2, 6, 3).
python_function('scripts/lenovo_remote_session.py', 'write_session_md', 3, 1, 9).
python_function('scripts/lenovo_remote_session.py', 'resolve_flow_paths', 2, 5, 4).
python_function('scripts/lenovo_remote_session.py', 'resolve_route_map', 2, 8, 8).
python_function('scripts/lenovo_remote_session.py', 'load_manifest_session', 1, 2, 3).
python_function('scripts/lenovo_remote_session.py', '_run_flows', 1, 22, 14).
python_function('scripts/lenovo_remote_session.py', 'main', 1, 37, 42).
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
python_function('scripts/report/session.py', 'infer_steps', 2, 28, 14).
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
python_function('scripts/run_test_sessions.py', 'session_pytest_urirdp', 1, 3, 5).
python_function('scripts/run_test_sessions.py', 'session_pytest_urisys', 1, 2, 5).
python_function('scripts/run_test_sessions.py', 'session_pytest_urisys_node', 1, 2, 5).
python_function('scripts/run_test_sessions.py', 'session_urirdp_mock_docker', 1, 5, 17).
python_function('scripts/run_test_sessions.py', '_record_health', 6, 1, 3).
python_function('scripts/run_test_sessions.py', '_bootstrap_rdp', 4, 4, 3).
python_function('scripts/run_test_sessions.py', '_read_display_env', 1, 4, 2).
python_function('scripts/run_test_sessions.py', '_call_and_record', 10, 5, 4).
python_function('scripts/run_test_sessions.py', 'session_urirdp_real_docker', 1, 25, 27).
python_function('scripts/run_test_sessions.py', 'session_urirdp_rdp_e2e', 1, 5, 11).
python_function('scripts/run_test_sessions.py', 'session_automation_lab', 1, 13, 18).
python_function('scripts/run_test_sessions.py', '_monorepo_root', 0, 4, 1).
python_function('scripts/run_test_sessions.py', 'session_urisys_node_docker_gui', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'session_office_simulate', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'session_office_simulate_lenovo', 1, 6, 10).
python_function('scripts/run_test_sessions.py', 'session_office_writer', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'session_email_mailpit', 1, 7, 11).
python_function('scripts/run_test_sessions.py', 'main', 0, 13, 19).
python_function('scripts/scan-browser-sessions.py', '_copy_query', 3, 2, 8).
python_function('scripts/scan-browser-sessions.py', 'scan_chrome_cookies', 1, 13, 12).
python_function('scripts/scan-browser-sessions.py', 'chrome_profiles', 1, 11, 9).
python_function('scripts/scan-browser-sessions.py', 'firefox_profiles', 1, 8, 10).
python_function('scripts/scan-browser-sessions.py', 'discover_browsers', 1, 1, 0).
python_function('scripts/scan-browser-sessions.py', 'main', 0, 23, 18).
python_function('scripts/session_core.py', 'default_examples_root', 0, 3, 4).
python_function('scripts/session_core.py', 'resolve_flow_ref', 1, 5, 5).
python_function('scripts/session_core.py', 'now_iso', 0, 1, 2).
python_function('scripts/session_core.py', 'host_id', 0, 1, 3).
python_function('scripts/session_core.py', 'run_id', 1, 2, 2).
python_function('scripts/session_core.py', 'save_json', 2, 1, 3).
python_function('scripts/session_core.py', 'step_ok', 1, 16, 3).
python_function('scripts/session_core.py', 'image_ext', 1, 5, 1).
python_function('scripts/session_core.py', 'write_base64_image', 2, 1, 4).
python_function('scripts/session_core.py', 'extract_images_from_dict', 1, 8, 11).
python_function('scripts/session_core.py', 'extract_step_screenshots', 1, 5, 4).
python_function('scripts/session_core.py', 'backfill_session_images', 1, 8, 11).
python_function('scripts/session_core.py', '_wheel_version_key', 2, 5, 7).
python_function('scripts/session_core.py', 'find_wheel_file', 2, 2, 4).
python_function('scripts/session_core.py', 'wheel_url', 2, 1, 1).
python_function('scripts/session_core.py', 'expand_step_wheels', 1, 18, 11).
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
python_function('src/urisys/cli.py', '_cmd_markpact', 1, 9, 12).
python_function('src/urisys/cli.py', '_cmd_init', 1, 6, 5).
python_function('src/urisys/cli.py', '_cmd_node', 1, 6, 5).
python_function('src/urisys/cli.py', '_cmd_uri', 1, 4, 7).
python_function('src/urisys/cli.py', '_handle_cli_error', 1, 8, 4).
python_function('src/urisys/cli.py', 'main', 1, 11, 18).
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
python_function('src/urisys/doctor.py', 'run_doctor', 0, 12, 14).
python_function('src/urisys/edge_install.py', 'is_importable', 0, 1, 1).
python_function('src/urisys/edge_install.py', '_dist_version', 0, 2, 1).
python_function('src/urisys/edge_install.py', 'is_broken_install', 0, 2, 2).
python_function('src/urisys/edge_install.py', 'pip_run', 1, 4, 2).
python_function('src/urisys/edge_install.py', 'repair_urisysedge', 0, 7, 5).
python_function('src/urisys/edge_install.py', 'ensure_urisysedge', 0, 5, 6).
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
python_function('src/urisys/init_setup.py', '_pre_repair_uricore', 4, 6, 5).
python_function('src/urisys/init_setup.py', '_build_pip_result', 1, 4, 6).
python_function('src/urisys/init_setup.py', '_resolve_error_hint', 3, 5, 2).
python_function('src/urisys/init_setup.py', 'run_init', 0, 31, 17).
python_function('src/urisys/managers/markpact_models.py', 'safe_identifier', 1, 3, 4).
python_function('src/urisys/managers/markpact_models.py', 'parse_meta', 1, 4, 2).
python_function('src/urisys/managers/markpact_models.py', 'scheme_from_uri', 1, 2, 2).
python_function('src/urisys/managers/markpact_models.py', 'source_hash', 1, 1, 4).
python_function('src/urisys/managers/markpact_validation.py', '_validate_contract_routes', 3, 11, 7).
python_function('src/urisys/managers/markpact_validation.py', 'validate_contract', 3, 13, 7).
python_function('src/urisys/managers/markpact_validation.py', '_missing_bundle_imports', 2, 6, 5).
python_function('src/urisys/managers/markpact_validation.py', 'validate_bundle', 3, 9, 8).
python_function('src/urisys/managers/markpact_validation.py', '_validate_implementation_capabilities', 2, 5, 6).
python_function('src/urisys/managers/markpact_validation.py', 'validate_implementation', 3, 14, 7).
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
python_function('tests/test_bootstrap.py', '_load_module', 2, 2, 3).
python_function('tests/test_bootstrap.py', 'test_bootstrap_import_does_not_require_uri_control', 0, 2, 2).
python_function('tests/test_bootstrap.py', 'test_cli_import_does_not_require_uri_control', 0, 3, 1).
python_function('tests/test_bootstrap.py', 'test_missing_uricore_payload', 0, 4, 2).
python_function('tests/test_bootstrap.py', 'test_doctor_subcommand_via_bootstrap', 0, 6, 4).
python_function('tests/test_doctor.py', 'test_doctor_ok_in_dev_env', 0, 8, 1).
python_function('tests/test_doctor.py', 'test_doctor_fails_high_min_version', 0, 3, 2).
python_function('tests/test_doctor.py', 'test_doctor_hints_include_node_serve', 0, 2, 2).
python_function('tests/test_doctor_uricore.py', 'test_check_uricore_authentic_fails_on_squatter', 0, 7, 4).
python_function('tests/test_edge_install.py', 'test_repair_calls_force_reinstall_when_broken', 0, 4, 4).
python_function('tests/test_edge_install.py', 'test_ensure_short_circuits_when_importable', 0, 3, 2).
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
python_function('tests/test_node_install.py', 'test_urisys_node_uses_release_wheel', 0, 6, 3).
python_function('tests/test_node_install.py', 'test_urisys_node_wheel_filename_pep427', 0, 3, 1).
python_function('tests/test_node_install.py', 'test_urisys_node_wheel_url_override', 0, 2, 2).
python_function('tests/test_pack_manager_parse.py', 'test_parse_packs_default_set', 0, 6, 1).
python_function('tests/test_pack_manager_parse.py', 'test_parse_packs_explicit_and_none_filter', 0, 7, 1).
python_function('tests/test_pack_manager_parse.py', 'test_is_all', 0, 5, 1).
python_function('tests/test_pack_manager_parse.py', 'test_parse_markpacts', 0, 6, 1).
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
python_method('MarkpactManager', 'compile', 1, 17, 25).
python_method('MarkpactManager', '_write_handler_modules', 2, 5, 4).
python_method('MarkpactManager', 'manifest_path_for', 1, 1, 1).
python_method('MarkpactManager', 'run_tests', 1, 12, 15).
python_method('MarkpactManager', '_check_expectations', 2, 9, 4).
python_method('MarkpactManager', '_build_route', 1, 14, 8).
python_method('MarkpactManager', '_resolve_handler_ref', 4, 5, 4).
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
python_method('PackManager', '_split_specs', 1, 6, 4).
python_method('PackManager', '_is_all', 1, 4, 1).
python_method('PackManager', 'parse_packs', 1, 8, 2).
python_method('PackManager', 'parse_markpacts', 1, 1, 1).
python_method('PackManager', 'resolve_package_name', 1, 1, 1).
python_method('PackManager', '_is_markpact_path', 1, 3, 2).
python_method('PackManager', '_is_manifest_path', 1, 4, 1).
python_method('PackManager', 'manifest_paths', 0, 11, 15).
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

*206 nodes · 295 edges · 36 modules · CC̄=4.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `build_parser` *(in src.urisys.cli)* | 1 | 1 | 62 | **63** |
| `session_urirdp_real_docker` *(in scripts.run_test_sessions)* | 25 ⚠ | 0 | 59 | **59** |
| `print` *(in scripts.run-nl-log-smoke)* | 0 | 56 | 0 | **56** |
| `run_cmd` *(in scripts.test_sessions.util)* | 6 | 30 | 12 | **42** |
| `main` *(in scripts.pack_sync)* | 28 ⚠ | 0 | 39 | **39** |
| `infer_steps` *(in scripts.report.session)* | 28 ⚠ | 1 | 37 | **38** |
| `_run_flows` *(in scripts.lenovo_remote_session)* | 22 ⚠ | 1 | 34 | **35** |
| `analyze_run` *(in scripts.report.run_analysis)* | 13 ⚠ | 2 | 33 | **35** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.09s
# nodes: 206 | edges: 295 | modules: 36
# CC̄=4.7

HUBS[20]:
  src.urisys.cli.build_parser
    CC=1  in:1  out:62  total:63
  scripts.run_test_sessions.session_urirdp_real_docker
    CC=25  in:0  out:59  total:59
  scripts.run-nl-log-smoke.print
    CC=0  in:56  out:0  total:56
  scripts.test_sessions.util.run_cmd
    CC=6  in:30  out:12  total:42
  scripts.pack_sync.main
    CC=28  in:0  out:39  total:39
  scripts.report.session.infer_steps
    CC=28  in:1  out:37  total:38
  scripts.lenovo_remote_session._run_flows
    CC=22  in:1  out:34  total:35
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  scripts.lenovo_remote_session.run_flow
    CC=14  in:1  out:33  total:34
  scripts.test_sessions.util.finalize_session
    CC=5  in:21  out:13  total:34
  scripts.scan-browser-sessions.main
    CC=23  in:0  out:34  total:34
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  src.urisys.init_setup.run_init
    CC=31  in:2  out:30  total:32
  scripts.run_test_sessions.session_automation_lab
    CC=13  in:1  out:31  total:32
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  scripts.pack_registry.pack_specs
    CC=17  in:2  out:30  total:32
  scripts.run_test_sessions.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  scripts.session_core.now_iso
    CC=1  in:29  out:2  total:31
  scripts.report.session.generate_report
    CC=9  in:2  out:27  total:29

MODULES:
  scripts.lenovo_remote_session  [15 funcs]
    _md_lessons  CC=6  out:8
    _run_flows  CC=22  out:34
    _run_host_sleep_step  CC=3  out:4
    _run_http_get_step  CC=2  out:3
    _run_upgrade_flow  CC=1  out:5
    _run_uri_call_step  CC=6  out:13
    append_log  CC=1  out:4
    http_get  CC=4  out:7
    load_manifest_session  CC=2  out:4
    load_yaml  CC=3  out:4
  scripts.office-simulate-loop  [5 funcs]
    call_uri  CC=4  out:11
    llm_tick  CC=7  out:18
    main  CC=10  out:12
    parse_args  CC=1  out:8
    rules_tick  CC=3  out:8
  scripts.pack_registry  [4 funcs]
    _repo  CC=1  out:0
    all_promoted_packs  CC=1  out:3
    pack_specs  CC=17  out:30
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
    infer_steps  CC=28  out:37
    session_duration  CC=5  out:14
  scripts.report.session_io  [1 funcs]
    write_session_report  CC=2  out:7
  scripts.report.session_markdown  [4 funcs]
    _environment_section  CC=5  out:7
    _screenshots_section  CC=3  out:3
    _steps_section  CC=7  out:4
    render_session_markdown  CC=1  out:16
  scripts.report.util  [2 funcs]
    read_json  CC=3  out:3
    tail  CC=2  out:0
  scripts.run-nl-log-smoke  [1 funcs]
    print  CC=0  out:0
  scripts.run-office-writer-e2e  [2 funcs]
    save_json  CC=0  out:0
    wait_health  CC=0  out:0
  scripts.run-urisys-node-docker-e2e  [1 funcs]
    http_json  CC=0  out:0
  scripts.run_test_sessions  [18 funcs]
    _bootstrap_rdp  CC=4  out:3
    _call_and_record  CC=5  out:4
    _monorepo_root  CC=4  out:3
    _read_display_env  CC=4  out:4
    _record_health  CC=1  out:3
    main  CC=13  out:32
    session_automation_lab  CC=13  out:31
    session_email_mailpit  CC=7  out:13
    session_office_simulate  CC=7  out:13
    session_office_simulate_lenovo  CC=6  out:10
  scripts.scan-browser-sessions  [4 funcs]
    _copy_query  CC=2  out:10
    discover_browsers  CC=1  out:0
    main  CC=23  out:34
    scan_chrome_cookies  CC=13  out:13
  scripts.session_core  [12 funcs]
    _wheel_version_key  CC=5  out:9
    backfill_session_images  CC=8  out:11
    expand_step_wheels  CC=18  out:25
    extract_images_from_dict  CC=8  out:15
    extract_step_screenshots  CC=5  out:7
    find_wheel_file  CC=2  out:4
    host_id  CC=1  out:3
    now_iso  CC=1  out:2
    resolve_flow_ref  CC=5  out:7
    save_json  CC=1  out:3
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
  scripts.test_sessions.util  [12 funcs]
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
  src.urisys.bootstrap  [5 funcs]
    _doctor_main  CC=3  out:7
    _init_main  CC=6  out:18
    _missing_uricore_payload  CC=1  out:1
    _print_json  CC=1  out:2
    main  CC=8  out:6
  src.urisys.cli  [11 funcs]
    _add_runtime_flags  CC=1  out:4
    _cmd_init  CC=6  out:7
    _cmd_markpact  CC=9  out:20
    _cmd_node  CC=6  out:8
    _cmd_uri  CC=4  out:9
    _handle_cli_error  CC=8  out:13
    _json_arg  CC=3  out:5
    build_parser  CC=1  out:62
    main  CC=11  out:20
    print_json  CC=1  out:2
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
  src.urisys.edge_install  [6 funcs]
    _dist_version  CC=2  out:1
    ensure_urisysedge  CC=5  out:8
    is_broken_install  CC=2  out:2
    is_importable  CC=1  out:1
    pip_run  CC=4  out:2
    repair_urisysedge  CC=7  out:10
  src.urisys.flow  [2 funcs]
    iter_steps  CC=7  out:8
    load_flow  CC=3  out:5
  src.urisys.http_server  [3 funcs]
    _read_json  CC=3  out:5
    _send  CC=1  out:12
    create_server  CC=1  out:31
  src.urisys.init_setup  [11 funcs]
    _build_pip_result  CC=4  out:9
    _pre_repair_uricore  CC=6  out:6
    _resolve_error_hint  CC=5  out:4
    default_node_pip_spec  CC=1  out:1
    default_pip_specs  CC=1  out:1
    pip_install_specs  CC=4  out:2
    profile_env  CC=2  out:1
    render_env_shell  CC=2  out:5
    run_init  CC=31  out:30
    verify_uri_control  CC=2  out:3
  src.urisys.managers.markpact_models  [1 funcs]
    scheme_from_uri  CC=2  out:2
  src.urisys.managers.markpact_validation  [6 funcs]
    _missing_bundle_imports  CC=6  out:6
    _validate_contract_routes  CC=11  out:15
    _validate_implementation_capabilities  CC=5  out:6
    validate_bundle  CC=9  out:15
    validate_contract  CC=13  out:21
    validate_implementation  CC=14  out:22
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
  src.urisys.cli._cmd_markpact → src.urisys.cli.resolve_markpact_source
  src.urisys.cli._cmd_markpact → src.urisys.cli.print_json
  src.urisys.cli._cmd_init → src.urisys.init_setup.run_init
  src.urisys.cli._cmd_init → src.urisys.cli.print_json
  src.urisys.cli._cmd_init → scripts.run-nl-log-smoke.print
  src.urisys.cli._cmd_node → scripts.run-nl-log-smoke.print
  src.urisys.cli._cmd_uri → src.urisys.cli.print_json
  src.urisys.cli._cmd_uri → src.urisys.cli._json_arg
  src.urisys.cli._handle_cli_error → src.urisys.cli.print_json
  src.urisys.cli.main → src.urisys.cli._cmd_uri
  src.urisys.cli.main → src.urisys.cli.build_parser
  src.urisys.cli.main → src.urisys.cli._cmd_markpact
  src.urisys.cli.main → src.urisys.doctor.run_doctor
  src.urisys.cli.main → src.urisys.cli.print_json
  src.urisys.cli.main → src.urisys.cli._cmd_init
  src.urisys.cli.main → scripts.run-nl-log-smoke.print
  src.urisys.cli.main → src.urisys.cli._cmd_node
  src.urisys.doctor._version_lt → src.urisys.doctor._parse_version
  src.urisys.doctor._check_import → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._version_lt
  src.urisys.doctor._check_uricore_authentic → src.urisys.uricore_install.diagnose_uricore
  src.urisys.doctor._check_uricore_authentic → src.urisys.uricore_install.is_wrong_uricore_installed
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
