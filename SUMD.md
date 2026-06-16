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
- **version**: `0.1.6`
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
  version: 0.1.6;
}

dependencies {
  runtime: "uricore>=0.1.0, PyYAML>=6.0";
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="urisys"] {
  entry: urisys.cli:main;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
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
  version: 0.1.6
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
uricore>=0.1.0
PyYAML>=6.0
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
# urisys | 190f 11165L | python:145,shell:40,javascript:2,less:1,go:1,typescript:1 | 2026-06-16
# stats: 403 func | 64 cls | 190 mod | CC̄=4.1 | critical:35 | cycles:0
# alerts[5]: CC analyze_run=34; CC session_urirdp_real_docker=30; CC session_lab_10_flows=28; CC write_session_report=28; CC _vision_analyze=22
# hotspots[5]: session_lab_10_flows fan=30; main fan=27; main fan=26; session_urirdp_real_docker fan=25; serve fan=24
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[190]:
  app.doql.less,40
  examples/frontend/app.js,22
  examples/markpact/browser-call.sh,9
  examples/shell/call-uri.sh,7
  examples/shell/server-curl.sh,9
  local-lab/scripts/00-init-nexus.sh,90
  local-lab/scripts/01-validate-markpact.sh,23
  local-lab/scripts/02-build-publish.sh,95
  local-lab/scripts/03-resolve-run.sh,17
  local-lab/scripts/04-smoke.sh,36
  local-lab/scripts/install-urisys.sh,18
  local-lab/scripts/run-all.sh,29
  project.sh,59
  scripts/run_test_sessions.py,1003
  scripts/session_report.py,510
  scripts/test-goal.sh,12
  src/urisys/__init__.py,4
  src/urisys/cli.py,177
  src/urisys/controllers/__init__.py,1
  src/urisys/controllers/flow_controller.py,34
  src/urisys/controllers/server_controller.py,19
  src/urisys/controllers/uri_controller.py,34
  src/urisys/defaults.py,19
  src/urisys/flow.py,26
  src/urisys/http_server.py,79
  src/urisys/managers/__init__.py,1
  src/urisys/managers/bridge_manager.py,15
  src/urisys/managers/event_manager.py,14
  src/urisys/managers/markpact_manager.py,409
  src/urisys/managers/pack_manager.py,98
  src/urisys/managers/policy_manager.py,19
  src/urisys/managers/route_manager.py,24
  src/urisys/managers/runtime_manager.py,31
  src/urisys/managers/source_manager.py,225
  tests/test_markpact.py,56
  tests/test_source_manager.py,36
  tests/test_urisys.py,25
  tree.sh,2
  uribrowser-docker/packages/python/uribrowserdocker/__init__.py,2
  uribrowser-docker/packages/python/uribrowserdocker/handlers.py,88
  uribrowser-docker/packages/python/uribrowserdocker/routes.py,6
  uribrowser-docker/packages/python/uribrowseredge/__init__.py,2
  uribrowser-docker/packages/python/uribrowseredge/cli.py,50
  uribrowser-docker/packages/python/uribrowseredge/runtime.py,223
  uribrowser-docker/scripts/test-local.sh,9
  uribrowser-docker/scripts/test-real.sh,29
  uribrowser-docker/tests/test_browser.py,24
  urienv-docker/packages/python/urienv/src/urienv/__init__.py,10
  urienv-docker/packages/python/urienv/src/urienv/handlers.py,197
  urienv-docker/packages/python/urisysedge/src/urisysedge/__init__.py,2
  urienv-docker/packages/python/urisysedge/src/urisysedge/cli.py,27
  urienv-docker/packages/python/urisysedge/src/urisysedge/flow.py,17
  urienv-docker/packages/python/urisysedge/src/urisysedge/pack_loader.py,16
  urienv-docker/packages/python/urisysedge/src/urisysedge/runtime.py,22
  urienv-docker/packages/python/urisysedge/src/urisysedge/server.py,27
  urienv-docker/scripts/local-test.sh,5
  urienv-docker/scripts/test-docker.sh,5
  urienv-docker/tests/e2e_env.py,64
  urienv-docker/tests/test_urienv.py,70
  urienv-docker/vendor/uricore/core/go/uricontrol/uricontrol.go,12
  urienv-docker/vendor/uricore/core/node/uri-control/src/index.ts,10
  urienv-docker/vendor/uricore/core/python/uri_control/__init__.py,38
  urienv-docker/vendor/uricore/core/python/uri_control/cli.py,124
  urienv-docker/vendor/uricore/core/python/uri_control/dispatcher.py,168
  urienv-docker/vendor/uricore/core/python/uri_control/errors.py,23
  urienv-docker/vendor/uricore/core/python/uri_control/event_store.py,66
  urienv-docker/vendor/uricore/core/python/uri_control/models.py,128
  urienv-docker/vendor/uricore/core/python/uri_control/parser.py,46
  urienv-docker/vendor/uricore/core/python/uri_control/policy.py,72
  urienv-docker/vendor/uricore/core/python/uri_control/projection.py,71
  urienv-docker/vendor/uricore/core/python/uri_control/registry.py,203
  urienv-docker/vendor/uricore/examples/__init__.py,1
  urienv-docker/vendor/uricore/examples/call_browser_mock.py,31
  urienv-docker/vendor/uricore/examples/call_systemd_mock.py,23
  urienv-docker/vendor/uricore/examples/packs/__init__.py,1
  urienv-docker/vendor/uricore/examples/packs/browser_mock/__init__.py,1
  urienv-docker/vendor/uricore/examples/packs/browser_mock/handlers.py,46
  urienv-docker/vendor/uricore/examples/packs/systemd_mock/__init__.py,1
  urienv-docker/vendor/uricore/examples/packs/systemd_mock/handlers.py,29
  urienv-docker/vendor/uricore/tests/test_dispatcher.py,50
  urienv-docker/vendor/uricore/tests/test_parser.py,12
  urienv-docker/vendor/uricore/tests/test_registry.py,29
  urikvm-docker/packages/python/urihim/__init__.py,2
  urikvm-docker/packages/python/urihim/handlers.py,82
  urikvm-docker/packages/python/urihim/routes.py,7
  urikvm-docker/packages/python/urikvm/__init__.py,2
  urikvm-docker/packages/python/urikvm/handlers.py,104
  urikvm-docker/packages/python/urikvm/routes.py,6
  urikvm-docker/packages/python/urikvmedge/__init__.py,2
  urikvm-docker/packages/python/urikvmedge/cli.py,57
  urikvm-docker/packages/python/urikvmedge/env.py,116
  urikvm-docker/packages/python/urikvmedge/runtime.py,229
  urikvm-docker/packages/python/urillm/__init__.py,2
  urikvm-docker/packages/python/urillm/handlers.py,202
  urikvm-docker/packages/python/urillm/routes.py,3
  urikvm-docker/packages/python/uriocr/__init__.py,2
  urikvm-docker/packages/python/uriocr/handlers.py,116
  urikvm-docker/packages/python/uriocr/routes.py,4
  urikvm-docker/scripts/call-http.sh,6
  urikvm-docker/scripts/real_pipeline.py,96
  urikvm-docker/scripts/test-local.sh,9
  urikvm-docker/scripts/test-real.sh,48
  urikvm-docker/tests/test_kvm.py,35
  urikvm-docker/tests/test_ocr_llm.py,81
  urirdp-docker/docker/bootstrap-rdp-session.sh,112
  urirdp-docker/docker/entrypoint.sh,24
  urirdp-docker/docker/startwm.sh,7
  urirdp-docker/packages/python/urirdp/__init__.py,4
  urirdp-docker/packages/python/urirdp/handlers.py,90
  urirdp-docker/packages/python/urirdp/routes.py,13
  urirdp-docker/packages/python/urirdp_him/__init__.py,4
  urirdp-docker/packages/python/urirdp_him/handlers.py,73
  urirdp-docker/packages/python/urirdp_him/routes.py,8
  urirdp-docker/packages/python/urirdp_kvm/__init__.py,4
  urirdp-docker/packages/python/urirdp_kvm/display.py,64
  urirdp-docker/packages/python/urirdp_kvm/handlers.py,134
  urirdp-docker/packages/python/urirdp_kvm/routes.py,6
  urirdp-docker/packages/python/urirdp_llm/__init__.py,4
  urirdp-docker/packages/python/urirdp_llm/handlers.py,197
  urirdp-docker/packages/python/urirdp_llm/routes.py,3
  urirdp-docker/packages/python/urirdp_ocr/__init__.py,4
  urirdp-docker/packages/python/urirdp_ocr/handlers.py,80
  urirdp-docker/packages/python/urirdp_ocr/routes.py,4
  urirdp-docker/packages/python/urirdp_shell/__init__.py,5
  urirdp-docker/packages/python/urirdp_shell/handlers.py,54
  urirdp-docker/packages/python/urirdp_shell/routes.py,10
  urirdp-docker/packages/python/urirdpedge/__init__.py,1
  urirdp-docker/packages/python/urirdpedge/cli.py,93
  urirdp-docker/packages/python/urirdpedge/env.py,124
  urirdp-docker/packages/python/urirdpedge/runtime.py,245
  urirdp-docker/scripts/call-http.sh,11
  urirdp-docker/scripts/test-docker.sh,18
  urirdp-docker/scripts/test-local.sh,9
  urirdp-docker/scripts/test-rdp-real.sh,13
  urirdp-docker/scripts/test-real-docker.sh,64
  urirdp-docker/tests/e2e_rdp_real.sh,101
  urirdp-docker/tests/test_env_resolve.py,29
  urirdp-docker/tests/test_rdp_kvm.py,76
  uristepper-docker/packages/python/uristepper/__init__.py,2
  uristepper-docker/packages/python/uristepper/drivers.py,170
  uristepper-docker/packages/python/uristepper/handlers.py,113
  uristepper-docker/packages/python/urisysedge/__init__.py,2
  uristepper-docker/packages/python/urisysedge/__main__.py,3
  uristepper-docker/packages/python/urisysedge/cli.py,125
  uristepper-docker/packages/python/urisysedge/runtime.py,194
  uristepper-docker/packages/python/urisysedge/server.py,72
  uristepper-docker/scripts/call-http.sh,11
  uristepper-docker/scripts/test-docker.sh,8
  uristepper-docker/scripts/test-local.sh,10
  uristepper-docker/tests/e2e.py,71
  uristepper-docker/tests/test_runtime.py,53
  urisys-automation-lab/docker/entrypoint.sh,19
  urisys-automation-lab/packages/python/labedge/__init__.py,1
  urisys-automation-lab/packages/python/labedge/runtime.py,154
  urisys-automation-lab/packages/python/urichat/__init__.py,1
  urisys-automation-lab/packages/python/urichat/handlers.py,82
  urisys-automation-lab/packages/python/urichat/routes.py,18
  urisys-automation-lab/packages/python/uristt/__init__.py,1
  urisys-automation-lab/packages/python/uristt/handlers.py,58
  urisys-automation-lab/packages/python/uristt/routes.py,24
  urisys-automation-lab/packages/python/uriwebrtc/__init__.py,1
  urisys-automation-lab/packages/python/uriwebrtc/handlers.py,36
  urisys-automation-lab/packages/python/uriwebrtc/routes.py,18
  urisys-automation-lab/scripts/docker-down.sh,7
  urisys-automation-lab/scripts/docker-logs.sh,7
  urisys-automation-lab/scripts/docker-smoke.sh,21
  urisys-automation-lab/scripts/docker-up.sh,22
  urisys-automation-lab/scripts/run-lab.sh,14
  urisys-automation-lab/scripts/validate-flows.sh,29
  urisys-automation-lab/server/automation_lab_server.py,214
  urisys-automation-lab/server/static_server.py,7
  urisys-automation-lab/tests/test_lab_handlers.py,62
  urisys-automation-lab/web/app.js,132
  urisys-node/packages/python/uriscreen/__init__.py,1
  urisys-node/packages/python/uriscreen/handlers.py,103
  urisys-node/packages/python/uriscreen/routes.py,24
  urisys-node/packages/python/urisysnode/__init__.py,1
  urisys-node/packages/python/urisysnode/artifact_resolver.py,121
  urisys-node/packages/python/urisysnode/cli.py,137
  urisys-node/packages/python/urisysnode/client.py,93
  urisys-node/packages/python/urisysnode/env.py,23
  urisys-node/packages/python/urisysnode/handlers.py,42
  urisys-node/packages/python/urisysnode/identity.py,111
  urisys-node/packages/python/urisysnode/router.py,48
  urisys-node/packages/python/urisysnode/routes.py,20
  urisys-node/packages/python/urisysnode/runtime.py,166
  urisys-node/packages/python/urisysnode/serve.py,108
  urisys-node/scripts/install-linux.sh,17
  urisys-node/tests/test_artifact_resolver.py,31
  urisys-node/tests/test_urisys_node.py,51
D:
  scripts/run_test_sessions.py:
    e: _now_iso,_run_id,_host_id,_http_json,_wait_health,_compose_cmd,_prepare_urirdp_data,_sleep_ports,_save_json,_run_cmd,_write_meta,_read_meta,_finalize_session,_docker_logs,_copy_container_file,_copy_host_screenshot,session_pytest_urirdp,session_pytest_urisys,session_pytest_urisys_node,session_urirdp_mock_docker,session_urirdp_real_docker,session_urirdp_rdp_e2e,session_automation_lab,_parse_lab_flow,_flow_step_context,_file_md5,_step_pause,_summarize_uri_response,_parse_docker_log_errors,_prepare_ok_target,_capture_rdp_screenshot,session_lab_10_flows,main
    _now_iso()
    _run_id()
    _host_id()
    _http_json(method;url;body;timeout)
    _wait_health(url;attempts;delay)
    _compose_cmd()
    _prepare_urirdp_data(pkg)
    _sleep_ports()
    _save_json(path;data)
    _run_cmd(cmd)
    _write_meta(session_dir)
    _read_meta(path)
    _finalize_session(session_dir;started_at;exit_code;steps)
    _docker_logs(service;compose_file;cwd;out)
    _copy_container_file(container;src;dest)
    _copy_host_screenshot(src;session_dir;name)
    session_pytest_urirdp(session_dir)
    session_pytest_urisys(session_dir)
    session_pytest_urisys_node(session_dir)
    session_urirdp_mock_docker(session_dir)
    session_urirdp_real_docker(session_dir)
    session_urirdp_rdp_e2e(session_dir)
    session_automation_lab(session_dir)
    _parse_lab_flow(path)
    _flow_step_context(defaults;uri)
    _file_md5(path)
    _step_pause(uri)
    _summarize_uri_response(res)
    _parse_docker_log_errors(session_dir)
    _prepare_ok_target(rdp_port;display;xauth)
    _capture_rdp_screenshot(session_dir)
    session_lab_10_flows(session_dir)
    main()
  scripts/session_report.py:
    e: _now_iso,_host_id,_read_json,_tail,_summarize_events,_infer_steps,_collect_artifacts,_session_status,generate_report,write_session_report,analyze_run,write_run_analysis,main,StepResult,SessionReport,RunAnalysis
    StepResult:
    SessionReport: passed(0),failed(0)
    RunAnalysis: all_passed(0)
    _now_iso()
    _host_id()
    _read_json(path)
    _tail(text;limit)
    _summarize_events(events_path)
    _infer_steps(session_dir;meta)
    _collect_artifacts(session_dir)
    _session_status(steps;meta)
    generate_report(session_dir)
    write_session_report(session_dir;report)
    analyze_run(run_dir)
    write_run_analysis(run_dir;analysis)
    main()
  src/urisys/__init__.py:
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
  src/urisys/flow.py:
    e: load_flow,iter_steps
    load_flow(path)
    iter_steps(flow)
  src/urisys/http_server.py:
    e: _read_json,_send,create_server
    _read_json(handler)
    _send(handler;status;data)
    create_server(host;port)
  src/urisys/managers/__init__.py:
  src/urisys/managers/bridge_manager.py:
    e: BridgeManager
    BridgeManager: call_http(5)  # Forwards URI envelopes to another URI server.
  src/urisys/managers/event_manager.py:
    e: EventManager
    EventManager: __init__(1),list_events(0)
  src/urisys/managers/markpact_manager.py:
    e: _safe_identifier,_parse_meta,_scheme_from_uri,MarkpactBlock,CompiledMarkpact,MarkpactError,MarkpactManager
    MarkpactBlock:
    CompiledMarkpact: to_dict(0)
    MarkpactError:  # Raised when a Markpact cannot be parsed, validated or compil
    MarkpactManager: __init__(1),read_blocks(1),source_hash(1),load_pack_block(1),validate(1),compile(1),manifest_path_for(1),run_tests(1),_compile_manifest(1),_package_id(2),_capabilities(1),_scheme(2),_handler_blocks(1),_load_yaml_blocks(2),_handler_id_from_ref(1),_ensure_importable(1)  # Parses and compiles one-file UriPack Markpacts.
    _safe_identifier(value)
    _parse_meta(raw)
    _scheme_from_uri(uri)
  src/urisys/managers/pack_manager.py:
    e: PackManager
    PackManager: __init__(1),parse_packs(1),parse_markpacts(1),resolve_package_name(1),_is_markpact_path(1),_is_manifest_path(1),manifest_paths(0),create_registry(0),capabilities(0),close(0),__enter__(0),__exit__(3)  # Loads separate uri* packages, plain manifest.yaml files and 
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
  tests/test_markpact.py:
    e: test_markpact_validate,test_markpact_compile_and_call,test_uri_controller_loads_markpact_directly,test_markpact_embedded_tests
    test_markpact_validate()
    test_markpact_compile_and_call(tmp_path)
    test_uri_controller_loads_markpact_directly(tmp_path)
    test_markpact_embedded_tests(tmp_path)
  tests/test_source_manager.py:
    e: test_fetch_local_file,test_fetch_github_raw
    test_fetch_local_file(tmp_path)
    test_fetch_github_raw(monkeypatch;tmp_path)
  tests/test_urisys.py:
    e: test_call_browser_open,test_routes_load
    test_call_browser_open(tmp_path)
    test_routes_load(tmp_path)
  uribrowser-docker/packages/python/uribrowserdocker/__init__.py:
  uribrowser-docker/packages/python/uribrowserdocker/handlers.py:
    e: _profile,_session_state,status,open_page,get_dom,screenshot
    _profile(context)
    _session_state(context)
    status(payload;context)
    open_page(payload;context)
    get_dom(payload;context)
    screenshot(payload;context)
  uribrowser-docker/packages/python/uribrowserdocker/routes.py:
    e: register
    register(runtime)
  uribrowser-docker/packages/python/uribrowseredge/__init__.py:
  uribrowser-docker/packages/python/uribrowseredge/cli.py:
    e: build_runtime,main
    build_runtime(args)
    main(argv)
  uribrowser-docker/packages/python/uribrowseredge/runtime.py:
    e: load_json,load_yaml_flow,run_flow,make_handler,serve,Route,JsonlEventStore,Runtime
    Route: compile(0),match(1)
    JsonlEventStore: __init__(1),append(1)
    Runtime: __init__(2),register(2),resolve(1),_load_handler(1),call(3)
    load_json(path)
    load_yaml_flow(path)
    run_flow(runtime;path;context)
    make_handler(runtime)
    serve(runtime;host;port)
  uribrowser-docker/tests/test_browser.py:
    e: runtime,test_open_requires_approval,test_open_and_dom
    runtime()
    test_open_requires_approval()
    test_open_and_dom()
  urienv-docker/packages/python/urienv/src/urienv/__init__.py:
  urienv-docker/packages/python/urienv/src/urienv/handlers.py:
    e: _split_csv,_cfg,_name,_is_public,_is_secret,_is_mutable,_mask,_read_docker_secret,_get_value,_require_visible,health,list_vars,startup_config,var_exists,var_value,secret_masked,secret_value,var_set,var_unset
    _split_csv(value)
    _cfg(context)
    _name(context)
    _is_public(name;cfg)
    _is_secret(name;cfg)
    _is_mutable(name;cfg)
    _mask(value)
    _read_docker_secret(name;cfg)
    _get_value(name;cfg)
    _require_visible(name;cfg)
    health(payload;context)
    list_vars(payload;context)
    startup_config(payload;context)
    var_exists(payload;context)
    var_value(payload;context)
    secret_masked(payload;context)
    secret_value(payload;context)
    var_set(payload;context)
    var_unset(payload;context)
  urienv-docker/packages/python/urisysedge/src/urisysedge/__init__.py:
  urienv-docker/packages/python/urisysedge/src/urisysedge/cli.py:
    e: _packs,main
    _packs(value)
    main(argv)
  urienv-docker/packages/python/urisysedge/src/urisysedge/flow.py:
    e: run_flow
    run_flow(path;runtime)
  urienv-docker/packages/python/urisysedge/src/urisysedge/pack_loader.py:
    e: manifest_path_for_pack,manifest_paths
    manifest_path_for_pack(pack)
    manifest_paths(packs)
  urienv-docker/packages/python/urisysedge/src/urisysedge/runtime.py:
    e: load_device_config,load_env_config,build_runtime,result_to_dict
    load_device_config(path)
    load_env_config(path)
    build_runtime(packs;extra_manifests)
    result_to_dict(result)
  urienv-docker/packages/python/urisysedge/src/urisysedge/server.py:
    e: serve
    serve()
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
  urienv-docker/vendor/uricore/core/python/uri_control/__init__.py:
  urienv-docker/vendor/uricore/core/python/uri_control/cli.py:
    e: _load_payload,_registry_from_args,cmd_explain,cmd_call,cmd_list,cmd_projection_latest,cmd_projection_status,build_parser,main
    _load_payload(value)
    _registry_from_args(args)
    cmd_explain(args)
    cmd_call(args)
    cmd_list(args)
    cmd_projection_latest(args)
    cmd_projection_status(args)
    build_parser()
    main(argv)
  urienv-docker/vendor/uricore/core/python/uri_control/dispatcher.py:
    e: _now_ms,_new_id,UriControlRuntime
    UriControlRuntime: __init__(0),call(3)  # URI → manifest route → policy → handler → event.
    _now_ms()
    _new_id(prefix)
  urienv-docker/vendor/uricore/core/python/uri_control/errors.py:
    e: UriControlError,UriParseError,RegistryError,RouteNotFoundError,HandlerLoadError,PolicyDeniedError
    UriControlError:  # Base exception for uri_control.
    UriParseError:  # Raised when a URI cannot be parsed.
    RegistryError:  # Raised for invalid manifests or registry state.
    RouteNotFoundError:  # Raised when no route matches a URI.
    HandlerLoadError:  # Raised when a handler reference cannot be loaded.
    PolicyDeniedError:  # Raised when policy denies a command or query.
  urienv-docker/vendor/uricore/core/python/uri_control/event_store.py:
    e: dump_events,EventStore,InMemoryEventStore,JsonlEventStore
    EventStore: append(1),read_all(0)
    InMemoryEventStore: __init__(0),append(1),read_all(0)
    JsonlEventStore: __init__(1),append(1),read_all(0)
    dump_events(events)
  urienv-docker/vendor/uricore/core/python/uri_control/models.py:
    e: ParsedUri,Route,MatchedRoute,CapabilityManifest,PolicyDecision,EventEnvelope,DispatchResult
    ParsedUri: body(0)
    Route:
    MatchedRoute:
    CapabilityManifest:
    PolicyDecision:
    EventEnvelope: to_dict(0)
    DispatchResult: to_dict(0)
  urienv-docker/vendor/uricore/core/python/uri_control/parser.py:
    e: parse_uri,canonicalize_uri
    parse_uri(uri)
    canonicalize_uri(uri)
  urienv-docker/vendor/uricore/core/python/uri_control/policy.py:
    e: PolicyEngine
    PolicyEngine: __init__(0),decide(2)  # Small deterministic policy gate.
  urienv-docker/vendor/uricore/core/python/uri_control/projection.py:
    e: ProjectionBuilder
    ProjectionBuilder: __init__(1),latest_by_source_uri(0),status_by_source_uri(0),events_by_type(0),from_events(1)  # Build read models from events.
  urienv-docker/vendor/uricore/core/python/uri_control/registry.py:
    e: _pattern_body,_compile_pattern,_load_python_handler,CapabilityRegistry
    CapabilityRegistry: __init__(0),from_manifest_files(2),manifests(0),routes(0),load_manifest_file(1),load_manifest(1),match(1),explain(1)  # In-memory registry of capability manifests and URI patterns.
    _pattern_body(pattern;scheme)
    _compile_pattern(pattern;scheme)
    _load_python_handler(handler_ref)
  urienv-docker/vendor/uricore/examples/__init__.py:
  urienv-docker/vendor/uricore/examples/call_browser_mock.py:
  urienv-docker/vendor/uricore/examples/call_systemd_mock.py:
  urienv-docker/vendor/uricore/examples/packs/__init__.py:
  urienv-docker/vendor/uricore/examples/packs/browser_mock/__init__.py:
  urienv-docker/vendor/uricore/examples/packs/browser_mock/handlers.py:
    e: open_page,get_dom
    open_page(payload;context)
    get_dom(payload;context)
  urienv-docker/vendor/uricore/examples/packs/systemd_mock/__init__.py:
  urienv-docker/vendor/uricore/examples/packs/systemd_mock/handlers.py:
    e: unit_status,unit_restart
    unit_status(payload;context)
    unit_restart(payload;context)
  urienv-docker/vendor/uricore/tests/test_dispatcher.py:
    e: _runtime,test_command_requires_approval,test_command_executes_when_approved,test_query_does_not_require_approval
    _runtime()
    test_command_requires_approval()
    test_command_executes_when_approved()
    test_query_does_not_require_approval()
  urienv-docker/vendor/uricore/tests/test_parser.py:
    e: test_parse_custom_uri
    test_parse_custom_uri()
  urienv-docker/vendor/uricore/tests/test_registry.py:
    e: test_registry_matches_browser_route,test_registry_explain
    test_registry_matches_browser_route()
    test_registry_explain()
  urikvm-docker/packages/python/urihim/__init__.py:
  urikvm-docker/packages/python/urihim/handlers.py:
    e: _state,_driver,_real_allowed,_pyautogui,mouse_status,mouse_move,mouse_click,keyboard_type,keyboard_hotkey
    _state(context)
    _driver(context)
    _real_allowed(context)
    _pyautogui(context)
    mouse_status(payload;context)
    mouse_move(payload;context)
    mouse_click(payload;context)
    keyboard_type(payload;context)
    keyboard_hotkey(payload;context)
  urikvm-docker/packages/python/urihim/routes.py:
    e: register
    register(runtime)
  urikvm-docker/packages/python/urikvm/__init__.py:
  urikvm-docker/packages/python/urikvm/handlers.py:
    e: _profile,_store_screenshot,monitor_list,screenshot,click_text,type_text
    _profile(context)
    _store_screenshot(context;monitor;driver;mime;raw_bytes;width;height)
    monitor_list(payload;context)
    screenshot(payload;context)
    click_text(payload;context)
    type_text(payload;context)
  urikvm-docker/packages/python/urikvm/routes.py:
    e: register
    register(runtime)
  urikvm-docker/packages/python/urikvmedge/__init__.py:
  urikvm-docker/packages/python/urikvmedge/cli.py:
    e: build_runtime,main
    build_runtime(args)
    main(argv)
  urikvm-docker/packages/python/urikvmedge/env.py:
    e: load_urisys_env,_env_policy_candidates,load_env_policy,_env_config,resolve_env_var,is_secret_env
    load_urisys_env()
    _env_policy_candidates()
    load_env_policy()
    _env_config(context)
    resolve_env_var(name;context)
    is_secret_env(name)
  urikvm-docker/packages/python/urikvmedge/runtime.py:
    e: load_json,load_yaml_flow,run_flow,make_handler,serve,Route,JsonlEventStore,Runtime
    Route: compile(0),match(1)
    JsonlEventStore: __init__(1),append(1)
    Runtime: __init__(2),register(2),resolve(1),_load_handler(1),call(3)
    load_json(path)
    load_yaml_flow(path)
    run_flow(runtime;path;context)
    make_handler(runtime)
    serve(runtime;host;port)
  urikvm-docker/packages/python/urillm/__init__.py:
  urikvm-docker/packages/python/urillm/handlers.py:
    e: _llm_cfg,_driver,_goal_text,_target_from_goal,_box_center,_heuristic_analyze,_parse_json_response,_openai_chat,_litellm_chat,_vision_messages,_normalize_action,_vision_analyze,vision_analyze
    _llm_cfg(context)
    _driver(context)
    _goal_text(payload)
    _target_from_goal(goal)
    _box_center(box)
    _heuristic_analyze(payload;source)
    _parse_json_response(text)
    _openai_chat(messages;model;api_key;base_url)
    _litellm_chat(messages;model)
    _vision_messages(goal;target;shot;ocr)
    _normalize_action(parsed;source)
    _vision_analyze(payload;context)
    vision_analyze(payload;context)
  urikvm-docker/packages/python/urillm/routes.py:
    e: register
    register(runtime)
  urikvm-docker/packages/python/uriocr/__init__.py:
  urikvm-docker/packages/python/uriocr/handlers.py:
    e: _ocr_cfg,_driver,_mock_boxes,_latest_screenshot,_png_bytes,_tesseract_boxes,_merge_word_boxes,_extract_text,latest_text,image_text
    _ocr_cfg(context)
    _driver(context)
    _mock_boxes(context)
    _latest_screenshot(context)
    _png_bytes(context)
    _tesseract_boxes(png_bytes;lang)
    _merge_word_boxes(boxes)
    _extract_text(context)
    latest_text(payload;context)
    image_text(payload;context)
  urikvm-docker/packages/python/uriocr/routes.py:
    e: register
    register(runtime)
  urikvm-docker/scripts/real_pipeline.py:
    e: _png_with_labels,_inject_png,build_runtime,main
    _png_with_labels(labels)
    _inject_png(rt;png_bytes)
    build_runtime(config_path)
    main()
  urikvm-docker/tests/test_kvm.py:
    e: runtime,test_him_requires_approval,test_kvm_click_text_uses_him_ocr_llm,test_type_text
    runtime()
    test_him_requires_approval()
    test_kvm_click_text_uses_him_ocr_llm()
    test_type_text()
  urikvm-docker/tests/test_ocr_llm.py:
    e: _png_with_labels,_runtime,_inject_png,test_tesseract_finds_ok,test_heuristic_llm_clicks_ok_from_ocr,test_openai_vision_clicks_ok_from_image
    _png_with_labels(labels)
    _runtime(ocr_driver;llm_driver)
    _inject_png(rt;png_bytes)
    test_tesseract_finds_ok()
    test_heuristic_llm_clicks_ok_from_ocr()
    test_openai_vision_clicks_ok_from_image()
  urirdp-docker/packages/python/urirdp/__init__.py:
    e: register
    register(runtime)
  urirdp-docker/packages/python/urirdp/handlers.py:
    e: _service_status,status,display,display_status,prepare_target
    _service_status(name)
    status(payload;context)
    display(payload;context)
    display_status(payload;context)
    prepare_target(payload;context)
  urirdp-docker/packages/python/urirdp/routes.py:
    e: register
    register(rt)
  urirdp-docker/packages/python/urirdp_him/__init__.py:
    e: register
    register(runtime)
  urirdp-docker/packages/python/urirdp_him/handlers.py:
    e: _mock,mouse_move,mouse_click,keyboard_type,keyboard_key,keyboard_type_text,keyboard_hotkey
    _mock(action;payload;context)
    mouse_move(payload;context)
    mouse_click(payload;context)
    keyboard_type(payload;context)
    keyboard_key(payload;context)
    keyboard_type_text(payload;context)
    keyboard_hotkey(payload;context)
  urirdp-docker/packages/python/urirdp_him/routes.py:
    e: register
    register(rt)
  urirdp-docker/packages/python/urirdp_kvm/__init__.py:
    e: register
    register(runtime)
  urirdp-docker/packages/python/urirdp_kvm/display.py:
    e: config_value,detect_display,base_env,allow_real,run_cmd,ensure_screenshot_dir
    config_value(context;key;default)
    detect_display(context)
    base_env(context)
    allow_real(context)
    run_cmd(args;context)
    ensure_screenshot_dir(context)
  urirdp-docker/packages/python/urirdp_kvm/handlers.py:
    e: display_info,screenshot,click_text,type_text,_tiny_png
    display_info(payload;context)
    screenshot(payload;context)
    click_text(payload;context)
    type_text(payload;context)
    _tiny_png()
  urirdp-docker/packages/python/urirdp_kvm/routes.py:
    e: register
    register(rt)
  urirdp-docker/packages/python/urirdp_llm/__init__.py:
    e: register
    register(runtime)
  urirdp-docker/packages/python/urirdp_llm/handlers.py:
    e: _config,_llm_cfg,_env,_target,_heuristic,_parse_json_response,_screenshot_b64,_vision_messages,_openai_compatible_chat,_litellm_chat,_normalize,analyze
    _config(context)
    _llm_cfg(context)
    _env(name;cfg;context;default)
    _target(payload)
    _heuristic(tokens;target;source)
    _parse_json_response(text)
    _screenshot_b64(context)
    _vision_messages(target;tokens;png_b64)
    _openai_compatible_chat(messages;model;api_key;base_url;temperature;max_tokens)
    _litellm_chat(messages;model;temperature;max_tokens)
    _normalize(parsed;model)
    analyze(payload;context)
  urirdp-docker/packages/python/urirdp_llm/routes.py:
    e: register
    register(rt)
  urirdp-docker/packages/python/urirdp_ocr/__init__.py:
    e: register
    register(runtime)
  urirdp-docker/packages/python/urirdp_ocr/handlers.py:
    e: _mock_ocr,_parse_tesseract_tsv,_tesseract_ocr,latest_text,image_text
    _mock_ocr()
    _parse_tesseract_tsv(tsv_text)
    _tesseract_ocr(path;context)
    latest_text(payload;context)
    image_text(payload;context)
  urirdp-docker/packages/python/urirdp_ocr/routes.py:
    e: register
    register(rt)
  urirdp-docker/packages/python/urirdp_shell/__init__.py:
    e: register
    register(runtime)
  urirdp-docker/packages/python/urirdp_shell/handlers.py:
    e: _mock,shell_run
    _mock(command;payload;context)
    shell_run(payload;context)
  urirdp-docker/packages/python/urirdp_shell/routes.py:
    e: register
    register(rt)
  urirdp-docker/packages/python/urirdpedge/__init__.py:
  urirdp-docker/packages/python/urirdpedge/cli.py:
    e: build_runtime,main
    build_runtime(args)
    main(argv)
  urirdp-docker/packages/python/urirdpedge/env.py:
    e: load_urisys_env,_env_policy_candidates,load_env_policy,_env_config,resolve_env_var,is_secret_env
    load_urisys_env()
    _env_policy_candidates()
    load_env_policy()
    _env_config(context)
    resolve_env_var(name;context)
    is_secret_env(name)
  urirdp-docker/packages/python/urirdpedge/runtime.py:
    e: load_json,load_yaml_flow,run_flow,make_handler,serve,Route,JsonlEventStore,Runtime
    Route: compile(0),match(1)
    JsonlEventStore: __init__(1),append(1)
    Runtime: __init__(2),register(2),resolve(1),_load_handler(1),call(3)
    load_json(path)
    load_yaml_flow(path)
    run_flow(runtime;path;context)
    make_handler(runtime)
    serve(runtime;host;port)
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
  uristepper-docker/packages/python/uristepper/__init__.py:
  uristepper-docker/packages/python/uristepper/drivers.py:
    e: make_driver,StepperDriver,MockStepperDriver,RpiGpioStepDirDriver
    StepperDriver: status(3),enable(3),disable(3),stop(3),move_relative(6),move_absolute(5),home(5)
    MockStepperDriver: __init__(1),_load(0),_save(1),_key(2),_axis(2),_update(3),status(3),enable(3),disable(3),stop(3),move_relative(6),move_absolute(5),home(5)
    RpiGpioStepDirDriver: __init__(0),_pins(2),_enable_value(2),status(3),enable(3),disable(3),stop(3),move_relative(6),home(5)
    make_driver(driver_name)
  uristepper-docker/packages/python/uristepper/handlers.py:
    e: _device_axis,_driver,_enforce_safety,_dry_or_driver,status,enable,disable,stop,move_relative,move_absolute,home
    _device_axis(context)
    _driver(driver_name;state_path)
    _enforce_safety(payload;safety)
    _dry_or_driver(context;cfg)
    status(payload;context)
    enable(payload;context)
    disable(payload;context)
    stop(payload;context)
    move_relative(payload;context)
    move_absolute(payload;context)
    home(payload;context)
  uristepper-docker/packages/python/urisysedge/__init__.py:
  uristepper-docker/packages/python/urisysedge/__main__.py:
  uristepper-docker/packages/python/urisysedge/cli.py:
    e: _json_arg,cmd_call,cmd_explain,cmd_routes,cmd_events,cmd_flow,cmd_serve,main
    _json_arg(value)
    cmd_call(args)
    cmd_explain(args)
    cmd_routes(args)
    cmd_events(args)
    cmd_flow(args)
    cmd_serve(args)
    main(argv)
  uristepper-docker/packages/python/urisysedge/runtime.py:
    e: load_json,build_runtime,UriError,PolicyDenied,Route,JsonlEventStore,StepperRuntime
    UriError:
    PolicyDenied:
    Route: compile(0),match(1)
    JsonlEventStore: __init__(1),append(1),tail(1)
    StepperRuntime: __init__(3),explain(1),list_routes(0),call(3),_match(1)
    load_json(path)
    build_runtime(device_profile_path;events_path)
  uristepper-docker/packages/python/urisysedge/server.py:
    e: make_handler,serve
    make_handler(runtime)
    serve(host;port;device_profile;events_path)
  uristepper-docker/tests/e2e.py:
    e: post,get,assert_ok,main
    post(path;data)
    get(path)
    assert_ok(result;label)
    main()
  uristepper-docker/tests/test_runtime.py:
    e: RuntimeTest
    RuntimeTest: setUp(0),test_status(0),test_policy_requires_approval(0),test_move_relative(0),test_safety_limit(0)
  urisys-automation-lab/packages/python/labedge/__init__.py:
  urisys-automation-lab/packages/python/labedge/runtime.py:
    e: load_json,Route,JsonlEventStore,Runtime
    Route: compile(0),match(1)
    JsonlEventStore: __init__(1),append(1)
    Runtime: __init__(2),register(2),resolve(1),_load_handler(1),call(3)
    load_json(path)
  urisys-automation-lab/packages/python/urichat/__init__.py:
  urisys-automation-lab/packages/python/urichat/handlers.py:
    e: _match_transcript,_forward_uri,message_send,uri_execute
    _match_transcript(text)
    _forward_uri(uri;payload;context;base_url)
    message_send(payload;context)
    uri_execute(payload;context)
  urisys-automation-lab/packages/python/urichat/routes.py:
    e: register
    register(rt)
  urisys-automation-lab/packages/python/uristt/__init__.py:
  urisys-automation-lab/packages/python/uristt/handlers.py:
    e: _session_id,session_start,session_transcript,audio_transcribe
    _session_id(context)
    session_start(payload;context)
    session_transcript(payload;context)
    audio_transcribe(payload;context)
  urisys-automation-lab/packages/python/uristt/routes.py:
    e: register
    register(rt)
  urisys-automation-lab/packages/python/uriwebrtc/__init__.py:
  urisys-automation-lab/packages/python/uriwebrtc/handlers.py:
    e: _room_id,session_start,data_send
    _room_id(context)
    session_start(payload;context)
    data_send(payload;context)
  urisys-automation-lab/packages/python/uriwebrtc/routes.py:
    e: register
    register(rt)
  urisys-automation-lab/server/automation_lab_server.py:
    e: build_lab_runtime,forward_uri_call,serve,LabHandler
    LabHandler: log_message(1),_json(2),_read_json(0),do_OPTIONS(0),do_GET(0),do_POST(0)
    build_lab_runtime(config_path)
    forward_uri_call(base_url;uri;payload;context)
    serve(host;port)
  urisys-automation-lab/server/static_server.py:
  urisys-automation-lab/tests/test_lab_handlers.py:
    e: _rt,test_stt_session_and_transcript,test_chat_uri_execute_dry_run,test_webrtc_data_send
    _rt()
    test_stt_session_and_transcript()
    test_chat_uri_execute_dry_run()
    test_webrtc_data_send()
  urisys-node/packages/python/uriscreen/__init__.py:
  urisys-node/packages/python/uriscreen/handlers.py:
    e: _screen_cfg,_backend,_output_dir,_monitor_index,_store_latest,_mock_png,capture,frame,capture_loop
    _screen_cfg(context)
    _backend(context;payload)
    _output_dir(payload;context)
    _monitor_index(payload;context;monitor_param)
    _store_latest(context;entry)
    _mock_png(label)
    capture(payload;context)
    frame(payload;context)
    capture_loop(payload;context)
  urisys-node/packages/python/uriscreen/routes.py:
    e: register
    register(rt)
  urisys-node/packages/python/urisysnode/__init__.py:
  urisys-node/packages/python/urisysnode/artifact_resolver.py:
    e: load_node_profile,load_artifact_index,select_artifact,docker_pull,docker_run_worker,wait_health,resolve_and_run
    load_node_profile(path)
    load_artifact_index(path)
    select_artifact(index;node_profile)
    docker_pull(ref)
    docker_run_worker(ref)
    wait_health(port;attempts)
    resolve_and_run(index_path;profile_path)
  urisys-node/packages/python/urisysnode/cli.py:
    e: main
    main(argv)
  urisys-node/packages/python/urisysnode/client.py:
    e: discover_mdns,remote_call,call_via_route_map
    discover_mdns(timeout_s)
    remote_call(endpoint;uri;payload;context)
    call_via_route_map(uri)
  urisys-node/packages/python/urisysnode/env.py:
    e: load_urisys_env
    load_urisys_env()
  urisys-node/packages/python/urisysnode/handlers.py:
    e: query_health,query_identity,command_indicator_on,command_indicator_off
    query_health(payload;context)
    query_identity(payload;context)
    command_indicator_on(payload;context)
    command_indicator_off(payload;context)
  urisys-node/packages/python/urisysnode/identity.py:
    e: _data_dir,_identity_path,_pairing_path,_hostname,load_identity,save_identity,load_pairing,enroll,save_pairing,set_remote_control,require_paired,health_payload
    _data_dir()
    _identity_path()
    _pairing_path()
    _hostname()
    load_identity()
    save_identity(data)
    load_pairing()
    enroll(controller;code;token)
    save_pairing(data)
    set_remote_control(active;message)
    require_paired(context)
    health_payload(version)
  urisys-node/packages/python/urisysnode/router.py:
    e: load_route_map,_match_pattern,resolve_remote_route,rewrite_uri_for_slave,node_endpoint
    load_route_map(path)
    _match_pattern(pattern;uri)
    resolve_remote_route(uri;route_map)
    rewrite_uri_for_slave(uri;node_id;target_node)
    node_endpoint(route;nodes_registry)
  urisys-node/packages/python/urisysnode/routes.py:
    e: register
    register(rt)
  urisys-node/packages/python/urisysnode/runtime.py:
    e: load_json,Route,JsonlEventStore,Runtime
    Route: compile(0),match(1)
    JsonlEventStore: __init__(1),append(1),tail(1)
    Runtime: __init__(2),register(2),resolve(1),_load_handler(1),call(3)
    load_json(path)
  urisys-node/packages/python/urisysnode/serve.py:
    e: _extend_pack_paths,build_runtime,make_handler,serve
    _extend_pack_paths()
    build_runtime(config_path)
    make_handler(runtime)
    serve(runtime;host;port)
  urisys-node/tests/test_artifact_resolver.py:
    e: test_select_artifact_by_platform,test_load_artifact_index
    test_select_artifact_by_platform(tmp_path)
    test_load_artifact_index(tmp_path)
  urisys-node/tests/test_urisys_node.py:
    e: test_identity_and_enroll,test_screen_capture_mock,test_rewrite_uri_for_slave,test_health_payload
    test_identity_and_enroll()
    test_screen_capture_mock()
    test_rewrite_uri_for_slave()
    test_health_payload()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('urisys', '0.1.6', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 40, 'less').
project_file('examples/frontend/app.js', 22, 'javascript').
project_file('examples/markpact/browser-call.sh', 9, 'shell').
project_file('examples/shell/call-uri.sh', 7, 'shell').
project_file('examples/shell/server-curl.sh', 9, 'shell').
project_file('local-lab/scripts/00-init-nexus.sh', 90, 'shell').
project_file('local-lab/scripts/01-validate-markpact.sh', 23, 'shell').
project_file('local-lab/scripts/02-build-publish.sh', 95, 'shell').
project_file('local-lab/scripts/03-resolve-run.sh', 17, 'shell').
project_file('local-lab/scripts/04-smoke.sh', 36, 'shell').
project_file('local-lab/scripts/install-urisys.sh', 18, 'shell').
project_file('local-lab/scripts/run-all.sh', 29, 'shell').
project_file('project.sh', 59, 'shell').
project_file('scripts/run_test_sessions.py', 1003, 'python').
project_file('scripts/session_report.py', 510, 'python').
project_file('scripts/test-goal.sh', 12, 'shell').
project_file('src/urisys/__init__.py', 4, 'python').
project_file('src/urisys/cli.py', 177, 'python').
project_file('src/urisys/controllers/__init__.py', 1, 'python').
project_file('src/urisys/controllers/flow_controller.py', 34, 'python').
project_file('src/urisys/controllers/server_controller.py', 19, 'python').
project_file('src/urisys/controllers/uri_controller.py', 34, 'python').
project_file('src/urisys/defaults.py', 19, 'python').
project_file('src/urisys/flow.py', 26, 'python').
project_file('src/urisys/http_server.py', 79, 'python').
project_file('src/urisys/managers/__init__.py', 1, 'python').
project_file('src/urisys/managers/bridge_manager.py', 15, 'python').
project_file('src/urisys/managers/event_manager.py', 14, 'python').
project_file('src/urisys/managers/markpact_manager.py', 409, 'python').
project_file('src/urisys/managers/pack_manager.py', 98, 'python').
project_file('src/urisys/managers/policy_manager.py', 19, 'python').
project_file('src/urisys/managers/route_manager.py', 24, 'python').
project_file('src/urisys/managers/runtime_manager.py', 31, 'python').
project_file('src/urisys/managers/source_manager.py', 225, 'python').
project_file('tests/test_markpact.py', 56, 'python').
project_file('tests/test_source_manager.py', 36, 'python').
project_file('tests/test_urisys.py', 25, 'python').
project_file('tree.sh', 2, 'shell').
project_file('uribrowser-docker/packages/python/uribrowserdocker/__init__.py', 2, 'python').
project_file('uribrowser-docker/packages/python/uribrowserdocker/handlers.py', 88, 'python').
project_file('uribrowser-docker/packages/python/uribrowserdocker/routes.py', 6, 'python').
project_file('uribrowser-docker/packages/python/uribrowseredge/__init__.py', 2, 'python').
project_file('uribrowser-docker/packages/python/uribrowseredge/cli.py', 50, 'python').
project_file('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 223, 'python').
project_file('uribrowser-docker/scripts/test-local.sh', 9, 'shell').
project_file('uribrowser-docker/scripts/test-real.sh', 29, 'shell').
project_file('uribrowser-docker/tests/test_browser.py', 24, 'python').
project_file('urienv-docker/packages/python/urienv/src/urienv/__init__.py', 10, 'python').
project_file('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 197, 'python').
project_file('urienv-docker/packages/python/urisysedge/src/urisysedge/__init__.py', 2, 'python').
project_file('urienv-docker/packages/python/urisysedge/src/urisysedge/cli.py', 27, 'python').
project_file('urienv-docker/packages/python/urisysedge/src/urisysedge/flow.py', 17, 'python').
project_file('urienv-docker/packages/python/urisysedge/src/urisysedge/pack_loader.py', 16, 'python').
project_file('urienv-docker/packages/python/urisysedge/src/urisysedge/runtime.py', 22, 'python').
project_file('urienv-docker/packages/python/urisysedge/src/urisysedge/server.py', 27, 'python').
project_file('urienv-docker/scripts/local-test.sh', 5, 'shell').
project_file('urienv-docker/scripts/test-docker.sh', 5, 'shell').
project_file('urienv-docker/tests/e2e_env.py', 64, 'python').
project_file('urienv-docker/tests/test_urienv.py', 70, 'python').
project_file('urienv-docker/vendor/uricore/core/go/uricontrol/uricontrol.go', 12, 'go').
project_file('urienv-docker/vendor/uricore/core/node/uri-control/src/index.ts', 10, 'typescript').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/__init__.py', 38, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 124, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/dispatcher.py', 168, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/errors.py', 23, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/event_store.py', 66, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 128, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/parser.py', 46, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/policy.py', 72, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/projection.py', 71, 'python').
project_file('urienv-docker/vendor/uricore/core/python/uri_control/registry.py', 203, 'python').
project_file('urienv-docker/vendor/uricore/examples/__init__.py', 1, 'python').
project_file('urienv-docker/vendor/uricore/examples/call_browser_mock.py', 31, 'python').
project_file('urienv-docker/vendor/uricore/examples/call_systemd_mock.py', 23, 'python').
project_file('urienv-docker/vendor/uricore/examples/packs/__init__.py', 1, 'python').
project_file('urienv-docker/vendor/uricore/examples/packs/browser_mock/__init__.py', 1, 'python').
project_file('urienv-docker/vendor/uricore/examples/packs/browser_mock/handlers.py', 46, 'python').
project_file('urienv-docker/vendor/uricore/examples/packs/systemd_mock/__init__.py', 1, 'python').
project_file('urienv-docker/vendor/uricore/examples/packs/systemd_mock/handlers.py', 29, 'python').
project_file('urienv-docker/vendor/uricore/tests/test_dispatcher.py', 50, 'python').
project_file('urienv-docker/vendor/uricore/tests/test_parser.py', 12, 'python').
project_file('urienv-docker/vendor/uricore/tests/test_registry.py', 29, 'python').
project_file('urikvm-docker/packages/python/urihim/__init__.py', 2, 'python').
project_file('urikvm-docker/packages/python/urihim/handlers.py', 82, 'python').
project_file('urikvm-docker/packages/python/urihim/routes.py', 7, 'python').
project_file('urikvm-docker/packages/python/urikvm/__init__.py', 2, 'python').
project_file('urikvm-docker/packages/python/urikvm/handlers.py', 104, 'python').
project_file('urikvm-docker/packages/python/urikvm/routes.py', 6, 'python').
project_file('urikvm-docker/packages/python/urikvmedge/__init__.py', 2, 'python').
project_file('urikvm-docker/packages/python/urikvmedge/cli.py', 57, 'python').
project_file('urikvm-docker/packages/python/urikvmedge/env.py', 116, 'python').
project_file('urikvm-docker/packages/python/urikvmedge/runtime.py', 229, 'python').
project_file('urikvm-docker/packages/python/urillm/__init__.py', 2, 'python').
project_file('urikvm-docker/packages/python/urillm/handlers.py', 202, 'python').
project_file('urikvm-docker/packages/python/urillm/routes.py', 3, 'python').
project_file('urikvm-docker/packages/python/uriocr/__init__.py', 2, 'python').
project_file('urikvm-docker/packages/python/uriocr/handlers.py', 116, 'python').
project_file('urikvm-docker/packages/python/uriocr/routes.py', 4, 'python').
project_file('urikvm-docker/scripts/call-http.sh', 6, 'shell').
project_file('urikvm-docker/scripts/real_pipeline.py', 96, 'python').
project_file('urikvm-docker/scripts/test-local.sh', 9, 'shell').
project_file('urikvm-docker/scripts/test-real.sh', 48, 'shell').
project_file('urikvm-docker/tests/test_kvm.py', 35, 'python').
project_file('urikvm-docker/tests/test_ocr_llm.py', 81, 'python').
project_file('urirdp-docker/docker/bootstrap-rdp-session.sh', 112, 'shell').
project_file('urirdp-docker/docker/entrypoint.sh', 24, 'shell').
project_file('urirdp-docker/docker/startwm.sh', 7, 'shell').
project_file('urirdp-docker/packages/python/urirdp/__init__.py', 4, 'python').
project_file('urirdp-docker/packages/python/urirdp/handlers.py', 90, 'python').
project_file('urirdp-docker/packages/python/urirdp/routes.py', 13, 'python').
project_file('urirdp-docker/packages/python/urirdp_him/__init__.py', 4, 'python').
project_file('urirdp-docker/packages/python/urirdp_him/handlers.py', 73, 'python').
project_file('urirdp-docker/packages/python/urirdp_him/routes.py', 8, 'python').
project_file('urirdp-docker/packages/python/urirdp_kvm/__init__.py', 4, 'python').
project_file('urirdp-docker/packages/python/urirdp_kvm/display.py', 64, 'python').
project_file('urirdp-docker/packages/python/urirdp_kvm/handlers.py', 134, 'python').
project_file('urirdp-docker/packages/python/urirdp_kvm/routes.py', 6, 'python').
project_file('urirdp-docker/packages/python/urirdp_llm/__init__.py', 4, 'python').
project_file('urirdp-docker/packages/python/urirdp_llm/handlers.py', 197, 'python').
project_file('urirdp-docker/packages/python/urirdp_llm/routes.py', 3, 'python').
project_file('urirdp-docker/packages/python/urirdp_ocr/__init__.py', 4, 'python').
project_file('urirdp-docker/packages/python/urirdp_ocr/handlers.py', 80, 'python').
project_file('urirdp-docker/packages/python/urirdp_ocr/routes.py', 4, 'python').
project_file('urirdp-docker/packages/python/urirdp_shell/__init__.py', 5, 'python').
project_file('urirdp-docker/packages/python/urirdp_shell/handlers.py', 54, 'python').
project_file('urirdp-docker/packages/python/urirdp_shell/routes.py', 10, 'python').
project_file('urirdp-docker/packages/python/urirdpedge/__init__.py', 1, 'python').
project_file('urirdp-docker/packages/python/urirdpedge/cli.py', 93, 'python').
project_file('urirdp-docker/packages/python/urirdpedge/env.py', 124, 'python').
project_file('urirdp-docker/packages/python/urirdpedge/runtime.py', 245, 'python').
project_file('urirdp-docker/scripts/call-http.sh', 11, 'shell').
project_file('urirdp-docker/scripts/test-docker.sh', 18, 'shell').
project_file('urirdp-docker/scripts/test-local.sh', 9, 'shell').
project_file('urirdp-docker/scripts/test-rdp-real.sh', 13, 'shell').
project_file('urirdp-docker/scripts/test-real-docker.sh', 64, 'shell').
project_file('urirdp-docker/tests/e2e_rdp_real.sh', 101, 'shell').
project_file('urirdp-docker/tests/test_env_resolve.py', 29, 'python').
project_file('urirdp-docker/tests/test_rdp_kvm.py', 76, 'python').
project_file('uristepper-docker/packages/python/uristepper/__init__.py', 2, 'python').
project_file('uristepper-docker/packages/python/uristepper/drivers.py', 170, 'python').
project_file('uristepper-docker/packages/python/uristepper/handlers.py', 113, 'python').
project_file('uristepper-docker/packages/python/urisysedge/__init__.py', 2, 'python').
project_file('uristepper-docker/packages/python/urisysedge/__main__.py', 3, 'python').
project_file('uristepper-docker/packages/python/urisysedge/cli.py', 125, 'python').
project_file('uristepper-docker/packages/python/urisysedge/runtime.py', 194, 'python').
project_file('uristepper-docker/packages/python/urisysedge/server.py', 72, 'python').
project_file('uristepper-docker/scripts/call-http.sh', 11, 'shell').
project_file('uristepper-docker/scripts/test-docker.sh', 8, 'shell').
project_file('uristepper-docker/scripts/test-local.sh', 10, 'shell').
project_file('uristepper-docker/tests/e2e.py', 71, 'python').
project_file('uristepper-docker/tests/test_runtime.py', 53, 'python').
project_file('urisys-automation-lab/docker/entrypoint.sh', 19, 'shell').
project_file('urisys-automation-lab/packages/python/labedge/__init__.py', 1, 'python').
project_file('urisys-automation-lab/packages/python/labedge/runtime.py', 154, 'python').
project_file('urisys-automation-lab/packages/python/urichat/__init__.py', 1, 'python').
project_file('urisys-automation-lab/packages/python/urichat/handlers.py', 82, 'python').
project_file('urisys-automation-lab/packages/python/urichat/routes.py', 18, 'python').
project_file('urisys-automation-lab/packages/python/uristt/__init__.py', 1, 'python').
project_file('urisys-automation-lab/packages/python/uristt/handlers.py', 58, 'python').
project_file('urisys-automation-lab/packages/python/uristt/routes.py', 24, 'python').
project_file('urisys-automation-lab/packages/python/uriwebrtc/__init__.py', 1, 'python').
project_file('urisys-automation-lab/packages/python/uriwebrtc/handlers.py', 36, 'python').
project_file('urisys-automation-lab/packages/python/uriwebrtc/routes.py', 18, 'python').
project_file('urisys-automation-lab/scripts/docker-down.sh', 7, 'shell').
project_file('urisys-automation-lab/scripts/docker-logs.sh', 7, 'shell').
project_file('urisys-automation-lab/scripts/docker-smoke.sh', 21, 'shell').
project_file('urisys-automation-lab/scripts/docker-up.sh', 22, 'shell').
project_file('urisys-automation-lab/scripts/run-lab.sh', 14, 'shell').
project_file('urisys-automation-lab/scripts/validate-flows.sh', 29, 'shell').
project_file('urisys-automation-lab/server/automation_lab_server.py', 214, 'python').
project_file('urisys-automation-lab/server/static_server.py', 7, 'python').
project_file('urisys-automation-lab/tests/test_lab_handlers.py', 62, 'python').
project_file('urisys-automation-lab/web/app.js', 132, 'javascript').
project_file('urisys-node/packages/python/uriscreen/__init__.py', 1, 'python').
project_file('urisys-node/packages/python/uriscreen/handlers.py', 103, 'python').
project_file('urisys-node/packages/python/uriscreen/routes.py', 24, 'python').
project_file('urisys-node/packages/python/urisysnode/__init__.py', 1, 'python').
project_file('urisys-node/packages/python/urisysnode/artifact_resolver.py', 121, 'python').
project_file('urisys-node/packages/python/urisysnode/cli.py', 137, 'python').
project_file('urisys-node/packages/python/urisysnode/client.py', 93, 'python').
project_file('urisys-node/packages/python/urisysnode/env.py', 23, 'python').
project_file('urisys-node/packages/python/urisysnode/handlers.py', 42, 'python').
project_file('urisys-node/packages/python/urisysnode/identity.py', 111, 'python').
project_file('urisys-node/packages/python/urisysnode/router.py', 48, 'python').
project_file('urisys-node/packages/python/urisysnode/routes.py', 20, 'python').
project_file('urisys-node/packages/python/urisysnode/runtime.py', 166, 'python').
project_file('urisys-node/packages/python/urisysnode/serve.py', 108, 'python').
project_file('urisys-node/scripts/install-linux.sh', 17, 'shell').
project_file('urisys-node/tests/test_artifact_resolver.py', 31, 'python').
project_file('urisys-node/tests/test_urisys_node.py', 51, 'python').

% ── Python Functions ─────────────────────────────────────
python_function('scripts/run_test_sessions.py', '_now_iso', 0, 1, 3).
python_function('scripts/run_test_sessions.py', '_run_id', 0, 1, 2).
python_function('scripts/run_test_sessions.py', '_host_id', 0, 1, 3).
python_function('scripts/run_test_sessions.py', '_http_json', 4, 5, 11).
python_function('scripts/run_test_sessions.py', '_wait_health', 3, 3, 5).
python_function('scripts/run_test_sessions.py', '_compose_cmd', 0, 4, 3).
python_function('scripts/run_test_sessions.py', '_prepare_urirdp_data', 1, 4, 5).
python_function('scripts/run_test_sessions.py', '_sleep_ports', 0, 1, 1).
python_function('scripts/run_test_sessions.py', '_save_json', 2, 1, 3).
python_function('scripts/run_test_sessions.py', '_run_cmd', 1, 5, 7).
python_function('scripts/run_test_sessions.py', '_write_meta', 1, 1, 3).
python_function('scripts/run_test_sessions.py', '_read_meta', 1, 2, 3).
python_function('scripts/run_test_sessions.py', '_finalize_session', 4, 5, 10).
python_function('scripts/run_test_sessions.py', '_docker_logs', 4, 4, 4).
python_function('scripts/run_test_sessions.py', '_copy_container_file', 3, 2, 4).
python_function('scripts/run_test_sessions.py', '_copy_host_screenshot', 3, 2, 5).
python_function('scripts/run_test_sessions.py', 'session_pytest_urirdp', 1, 3, 5).
python_function('scripts/run_test_sessions.py', 'session_pytest_urisys', 1, 2, 5).
python_function('scripts/run_test_sessions.py', 'session_pytest_urisys_node', 1, 2, 5).
python_function('scripts/run_test_sessions.py', 'session_urirdp_mock_docker', 1, 5, 17).
python_function('scripts/run_test_sessions.py', 'session_urirdp_real_docker', 1, 30, 25).
python_function('scripts/run_test_sessions.py', 'session_urirdp_rdp_e2e', 1, 5, 11).
python_function('scripts/run_test_sessions.py', 'session_automation_lab', 1, 16, 17).
python_function('scripts/run_test_sessions.py', '_parse_lab_flow', 1, 10, 10).
python_function('scripts/run_test_sessions.py', '_flow_step_context', 2, 6, 3).
python_function('scripts/run_test_sessions.py', '_file_md5', 1, 2, 4).
python_function('scripts/run_test_sessions.py', '_step_pause', 1, 5, 2).
python_function('scripts/run_test_sessions.py', '_summarize_uri_response', 1, 11, 3).
python_function('scripts/run_test_sessions.py', '_parse_docker_log_errors', 1, 8, 8).
python_function('scripts/run_test_sessions.py', '_prepare_ok_target', 3, 1, 2).
python_function('scripts/run_test_sessions.py', '_capture_rdp_screenshot', 1, 5, 4).
python_function('scripts/run_test_sessions.py', 'session_lab_10_flows', 1, 28, 30).
python_function('scripts/run_test_sessions.py', 'main', 0, 13, 19).
python_function('scripts/session_report.py', '_now_iso', 0, 1, 3).
python_function('scripts/session_report.py', '_host_id', 0, 1, 3).
python_function('scripts/session_report.py', '_read_json', 1, 3, 3).
python_function('scripts/session_report.py', '_tail', 2, 2, 0).
python_function('scripts/session_report.py', '_summarize_events', 1, 18, 12).
python_function('scripts/session_report.py', '_infer_steps', 2, 20, 13).
python_function('scripts/session_report.py', '_collect_artifacts', 1, 7, 8).
python_function('scripts/session_report.py', '_session_status', 2, 9, 4).
python_function('scripts/session_report.py', 'generate_report', 1, 13, 19).
python_function('scripts/session_report.py', 'write_session_report', 2, 28, 14).
python_function('scripts/session_report.py', 'analyze_run', 1, 34, 22).
python_function('scripts/session_report.py', 'write_run_analysis', 2, 8, 9).
python_function('scripts/session_report.py', 'main', 0, 4, 13).
python_function('src/urisys/cli.py', '_json_arg', 1, 3, 4).
python_function('src/urisys/cli.py', 'print_json', 1, 1, 2).
python_function('src/urisys/cli.py', '_add_runtime_flags', 1, 1, 1).
python_function('src/urisys/cli.py', 'resolve_markpact_source', 1, 2, 3).
python_function('src/urisys/cli.py', 'build_parser', 0, 1, 5).
python_function('src/urisys/cli.py', 'main', 1, 18, 27).
python_function('src/urisys/flow.py', 'load_flow', 1, 3, 5).
python_function('src/urisys/flow.py', 'iter_steps', 1, 7, 7).
python_function('src/urisys/http_server.py', '_read_json', 1, 3, 5).
python_function('src/urisys/http_server.py', '_send', 3, 1, 8).
python_function('src/urisys/http_server.py', 'create_server', 2, 1, 13).
python_function('src/urisys/managers/markpact_manager.py', '_safe_identifier', 1, 3, 4).
python_function('src/urisys/managers/markpact_manager.py', '_parse_meta', 1, 4, 2).
python_function('src/urisys/managers/markpact_manager.py', '_scheme_from_uri', 1, 2, 2).
python_function('tests/test_markpact.py', 'test_markpact_validate', 0, 4, 2).
python_function('tests/test_markpact.py', 'test_markpact_compile_and_call', 1, 5, 7).
python_function('tests/test_markpact.py', 'test_uri_controller_loads_markpact_directly', 1, 4, 4).
python_function('tests/test_markpact.py', 'test_markpact_embedded_tests', 1, 3, 3).
python_function('tests/test_source_manager.py', 'test_fetch_local_file', 1, 4, 5).
python_function('tests/test_source_manager.py', 'test_fetch_github_raw', 2, 3, 4).
python_function('tests/test_urisys.py', 'test_call_browser_open', 1, 3, 4).
python_function('tests/test_urisys.py', 'test_routes_load', 1, 3, 5).
python_function('uribrowser-docker/packages/python/uribrowserdocker/handlers.py', '_profile', 1, 1, 1).
python_function('uribrowser-docker/packages/python/uribrowserdocker/handlers.py', '_session_state', 1, 1, 2).
python_function('uribrowser-docker/packages/python/uribrowserdocker/handlers.py', 'status', 2, 1, 3).
python_function('uribrowser-docker/packages/python/uribrowserdocker/handlers.py', 'open_page', 2, 11, 17).
python_function('uribrowser-docker/packages/python/uribrowserdocker/handlers.py', 'get_dom', 2, 1, 2).
python_function('uribrowser-docker/packages/python/uribrowserdocker/handlers.py', 'screenshot', 2, 3, 5).
python_function('uribrowser-docker/packages/python/uribrowserdocker/routes.py', 'register', 1, 1, 1).
python_function('uribrowser-docker/packages/python/uribrowseredge/cli.py', 'build_runtime', 1, 2, 5).
python_function('uribrowser-docker/packages/python/uribrowseredge/cli.py', 'main', 1, 7, 14).
python_function('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'load_json', 1, 3, 5).
python_function('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'load_yaml_flow', 1, 10, 9).
python_function('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'run_flow', 3, 7, 11).
python_function('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'make_handler', 1, 1, 15).
python_function('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'serve', 3, 2, 4).
python_function('uribrowser-docker/tests/test_browser.py', 'runtime', 0, 1, 2).
python_function('uribrowser-docker/tests/test_browser.py', 'test_open_requires_approval', 0, 3, 2).
python_function('uribrowser-docker/tests/test_browser.py', 'test_open_and_dom', 0, 4, 2).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_split_csv', 1, 7, 5).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_cfg', 1, 7, 5).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_name', 1, 3, 4).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_is_public', 2, 3, 2).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_is_secret', 2, 3, 2).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_is_mutable', 2, 1, 0).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_mask', 1, 3, 1).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_read_docker_secret', 2, 4, 6).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_get_value', 2, 3, 2).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', '_require_visible', 2, 3, 3).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'health', 2, 1, 2).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'list_vars', 2, 4, 7).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'startup_config', 2, 3, 4).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'var_exists', 2, 1, 3).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'var_value', 2, 1, 4).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'secret_masked', 2, 2, 6).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'secret_value', 2, 4, 6).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'var_set', 2, 4, 7).
python_function('urienv-docker/packages/python/urienv/src/urienv/handlers.py', 'var_unset', 2, 3, 6).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/cli.py', '_packs', 1, 3, 2).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/cli.py', 'main', 1, 10, 19).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/flow.py', 'run_flow', 2, 12, 12).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/pack_loader.py', 'manifest_path_for_pack', 1, 4, 5).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/pack_loader.py', 'manifest_paths', 1, 3, 3).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/runtime.py', 'load_device_config', 1, 3, 2).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/runtime.py', 'load_env_config', 1, 3, 2).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/runtime.py', 'build_runtime', 2, 3, 6).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/runtime.py', 'result_to_dict', 1, 2, 0).
python_function('urienv-docker/packages/python/urisysedge/src/urisysedge/server.py', 'serve', 0, 1, 24).
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
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', '_load_payload', 1, 3, 4).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', '_registry_from_args', 1, 2, 2).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 'cmd_explain', 1, 1, 4).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 'cmd_call', 1, 2, 8).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 'cmd_list', 1, 2, 3).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 'cmd_projection_latest', 1, 1, 5).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 'cmd_projection_status', 1, 1, 5).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 'build_parser', 0, 1, 5).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/cli.py', 'main', 1, 1, 4).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/dispatcher.py', '_now_ms', 0, 1, 2).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/dispatcher.py', '_new_id', 1, 1, 1).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/event_store.py', 'dump_events', 1, 2, 1).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/parser.py', 'parse_uri', 1, 7, 9).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/parser.py', 'canonicalize_uri', 1, 1, 1).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/registry.py', '_pattern_body', 2, 2, 4).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/registry.py', '_compile_pattern', 2, 6, 10).
python_function('urienv-docker/vendor/uricore/core/python/uri_control/registry.py', '_load_python_handler', 1, 6, 7).
python_function('urienv-docker/vendor/uricore/examples/packs/browser_mock/handlers.py', 'open_page', 2, 6, 1).
python_function('urienv-docker/vendor/uricore/examples/packs/browser_mock/handlers.py', 'get_dom', 2, 5, 1).
python_function('urienv-docker/vendor/uricore/examples/packs/systemd_mock/handlers.py', 'unit_status', 2, 3, 1).
python_function('urienv-docker/vendor/uricore/examples/packs/systemd_mock/handlers.py', 'unit_restart', 2, 2, 1).
python_function('urienv-docker/vendor/uricore/tests/test_dispatcher.py', '_runtime', 0, 1, 3).
python_function('urienv-docker/vendor/uricore/tests/test_dispatcher.py', 'test_command_requires_approval', 0, 4, 3).
python_function('urienv-docker/vendor/uricore/tests/test_dispatcher.py', 'test_command_executes_when_approved', 0, 4, 3).
python_function('urienv-docker/vendor/uricore/tests/test_dispatcher.py', 'test_query_does_not_require_approval', 0, 3, 2).
python_function('urienv-docker/vendor/uricore/tests/test_parser.py', 'test_parse_custom_uri', 0, 7, 1).
python_function('urienv-docker/vendor/uricore/tests/test_registry.py', 'test_registry_matches_browser_route', 0, 4, 2).
python_function('urienv-docker/vendor/uricore/tests/test_registry.py', 'test_registry_explain', 0, 4, 2).
python_function('urikvm-docker/packages/python/urihim/handlers.py', '_state', 1, 1, 1).
python_function('urikvm-docker/packages/python/urihim/handlers.py', '_driver', 1, 1, 1).
python_function('urikvm-docker/packages/python/urihim/handlers.py', '_real_allowed', 1, 2, 2).
python_function('urikvm-docker/packages/python/urihim/handlers.py', '_pyautogui', 1, 3, 3).
python_function('urikvm-docker/packages/python/urihim/handlers.py', 'mouse_status', 2, 1, 2).
python_function('urikvm-docker/packages/python/urihim/handlers.py', 'mouse_move', 2, 3, 7).
python_function('urikvm-docker/packages/python/urihim/handlers.py', 'mouse_click', 2, 7, 7).
python_function('urikvm-docker/packages/python/urihim/handlers.py', 'keyboard_type', 2, 3, 7).
python_function('urikvm-docker/packages/python/urihim/handlers.py', 'keyboard_hotkey', 2, 6, 9).
python_function('urikvm-docker/packages/python/urihim/routes.py', 'register', 1, 1, 1).
python_function('urikvm-docker/packages/python/urikvm/handlers.py', '_profile', 1, 1, 1).
python_function('urikvm-docker/packages/python/urikvm/handlers.py', '_store_screenshot', 7, 1, 4).
python_function('urikvm-docker/packages/python/urikvm/handlers.py', 'monitor_list', 2, 2, 2).
python_function('urikvm-docker/packages/python/urikvm/handlers.py', 'screenshot', 2, 5, 13).
python_function('urikvm-docker/packages/python/urikvm/handlers.py', 'click_text', 2, 8, 4).
python_function('urikvm-docker/packages/python/urikvm/handlers.py', 'type_text', 2, 1, 2).
python_function('urikvm-docker/packages/python/urikvm/routes.py', 'register', 1, 1, 1).
python_function('urikvm-docker/packages/python/urikvmedge/cli.py', 'build_runtime', 1, 6, 6).
python_function('urikvm-docker/packages/python/urikvmedge/cli.py', 'main', 1, 7, 15).
python_function('urikvm-docker/packages/python/urikvmedge/env.py', 'load_urisys_env', 0, 7, 11).
python_function('urikvm-docker/packages/python/urikvmedge/env.py', '_env_policy_candidates', 0, 2, 5).
python_function('urikvm-docker/packages/python/urikvmedge/env.py', 'load_env_policy', 0, 6, 5).
python_function('urikvm-docker/packages/python/urikvmedge/env.py', '_env_config', 1, 7, 2).
python_function('urikvm-docker/packages/python/urikvmedge/env.py', 'resolve_env_var', 2, 11, 8).
python_function('urikvm-docker/packages/python/urikvmedge/env.py', 'is_secret_env', 1, 1, 1).
python_function('urikvm-docker/packages/python/urikvmedge/runtime.py', 'load_json', 1, 3, 5).
python_function('urikvm-docker/packages/python/urikvmedge/runtime.py', 'load_yaml_flow', 1, 10, 9).
python_function('urikvm-docker/packages/python/urikvmedge/runtime.py', 'run_flow', 3, 7, 11).
python_function('urikvm-docker/packages/python/urikvmedge/runtime.py', 'make_handler', 1, 1, 15).
python_function('urikvm-docker/packages/python/urikvmedge/runtime.py', 'serve', 3, 2, 4).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_llm_cfg', 1, 1, 1).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_driver', 1, 1, 2).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_goal_text', 1, 4, 2).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_target_from_goal', 1, 3, 4).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_box_center', 1, 1, 2).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_heuristic_analyze', 2, 16, 6).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_parse_json_response', 1, 5, 4).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_openai_chat', 4, 2, 9).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_litellm_chat', 2, 2, 3).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_vision_messages', 4, 12, 4).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_normalize_action', 2, 4, 4).
python_function('urikvm-docker/packages/python/urillm/handlers.py', '_vision_analyze', 2, 22, 15).
python_function('urikvm-docker/packages/python/urillm/handlers.py', 'vision_analyze', 2, 1, 1).
python_function('urikvm-docker/packages/python/urillm/routes.py', 'register', 1, 1, 1).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_ocr_cfg', 1, 1, 1).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_driver', 1, 1, 2).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_mock_boxes', 1, 2, 2).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_latest_screenshot', 1, 2, 1).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_png_bytes', 1, 4, 3).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_tesseract_boxes', 2, 8, 11).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_merge_word_boxes', 1, 5, 7).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', '_extract_text', 1, 6, 9).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', 'latest_text', 2, 1, 1).
python_function('urikvm-docker/packages/python/uriocr/handlers.py', 'image_text', 2, 1, 2).
python_function('urikvm-docker/packages/python/uriocr/routes.py', 'register', 1, 1, 1).
python_function('urikvm-docker/scripts/real_pipeline.py', '_png_with_labels', 1, 4, 9).
python_function('urikvm-docker/scripts/real_pipeline.py', '_inject_png', 2, 1, 2).
python_function('urikvm-docker/scripts/real_pipeline.py', 'build_runtime', 1, 1, 3).
python_function('urikvm-docker/scripts/real_pipeline.py', 'main', 0, 14, 12).
python_function('urikvm-docker/tests/test_kvm.py', 'runtime', 0, 1, 2).
python_function('urikvm-docker/tests/test_kvm.py', 'test_him_requires_approval', 0, 3, 2).
python_function('urikvm-docker/tests/test_kvm.py', 'test_kvm_click_text_uses_him_ocr_llm', 0, 4, 2).
python_function('urikvm-docker/tests/test_kvm.py', 'test_type_text', 0, 3, 2).
python_function('urikvm-docker/tests/test_ocr_llm.py', '_png_with_labels', 1, 4, 9).
python_function('urikvm-docker/tests/test_ocr_llm.py', '_runtime', 2, 1, 2).
python_function('urikvm-docker/tests/test_ocr_llm.py', '_inject_png', 2, 1, 2).
python_function('urikvm-docker/tests/test_ocr_llm.py', 'test_tesseract_finds_ok', 0, 6, 4).
python_function('urikvm-docker/tests/test_ocr_llm.py', 'test_heuristic_llm_clicks_ok_from_ocr', 0, 6, 4).
python_function('urikvm-docker/tests/test_ocr_llm.py', 'test_openai_vision_clicks_ok_from_image', 0, 4, 7).
python_function('urirdp-docker/packages/python/urirdp/__init__.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp/handlers.py', '_service_status', 1, 4, 4).
python_function('urirdp-docker/packages/python/urirdp/handlers.py', 'status', 2, 1, 4).
python_function('urirdp-docker/packages/python/urirdp/handlers.py', 'display', 2, 2, 4).
python_function('urirdp-docker/packages/python/urirdp/handlers.py', 'display_status', 2, 7, 9).
python_function('urirdp-docker/packages/python/urirdp/handlers.py', 'prepare_target', 2, 4, 8).
python_function('urirdp-docker/packages/python/urirdp/routes.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_him/__init__.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_him/handlers.py', '_mock', 3, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_him/handlers.py', 'mouse_move', 2, 5, 9).
python_function('urirdp-docker/packages/python/urirdp_him/handlers.py', 'mouse_click', 2, 11, 9).
python_function('urirdp-docker/packages/python/urirdp_him/handlers.py', 'keyboard_type', 2, 5, 10).
python_function('urirdp-docker/packages/python/urirdp_him/handlers.py', 'keyboard_key', 2, 5, 8).
python_function('urirdp-docker/packages/python/urirdp_him/handlers.py', 'keyboard_type_text', 2, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_him/handlers.py', 'keyboard_hotkey', 2, 8, 10).
python_function('urirdp-docker/packages/python/urirdp_him/routes.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_kvm/__init__.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_kvm/display.py', 'config_value', 3, 2, 1).
python_function('urirdp-docker/packages/python/urirdp_kvm/display.py', 'detect_display', 1, 7, 6).
python_function('urirdp-docker/packages/python/urirdp_kvm/display.py', 'base_env', 1, 6, 7).
python_function('urirdp-docker/packages/python/urirdp_kvm/display.py', 'allow_real', 1, 2, 2).
python_function('urirdp-docker/packages/python/urirdp_kvm/display.py', 'run_cmd', 2, 1, 2).
python_function('urirdp-docker/packages/python/urirdp_kvm/display.py', 'ensure_screenshot_dir', 1, 1, 3).
python_function('urirdp-docker/packages/python/urirdp_kvm/handlers.py', 'display_info', 2, 4, 4).
python_function('urirdp-docker/packages/python/urirdp_kvm/handlers.py', 'screenshot', 2, 9, 15).
python_function('urirdp-docker/packages/python/urirdp_kvm/handlers.py', 'click_text', 2, 10, 4).
python_function('urirdp-docker/packages/python/urirdp_kvm/handlers.py', 'type_text', 2, 2, 3).
python_function('urirdp-docker/packages/python/urirdp_kvm/handlers.py', '_tiny_png', 0, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_kvm/routes.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_llm/__init__.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_config', 1, 2, 1).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_llm_cfg', 1, 6, 4).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_env', 4, 3, 5).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_target', 1, 3, 3).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_heuristic', 3, 5, 5).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_parse_json_response', 1, 5, 4).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_screenshot_b64', 1, 2, 7).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_vision_messages', 3, 4, 2).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_openai_compatible_chat', 6, 1, 9).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_litellm_chat', 4, 2, 3).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', '_normalize', 2, 4, 4).
python_function('urirdp-docker/packages/python/urirdp_llm/handlers.py', 'analyze', 2, 18, 17).
python_function('urirdp-docker/packages/python/urirdp_llm/routes.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_ocr/__init__.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_ocr/handlers.py', '_mock_ocr', 0, 1, 0).
python_function('urirdp-docker/packages/python/urirdp_ocr/handlers.py', '_parse_tesseract_tsv', 1, 7, 7).
python_function('urirdp-docker/packages/python/urirdp_ocr/handlers.py', '_tesseract_ocr', 2, 9, 10).
python_function('urirdp-docker/packages/python/urirdp_ocr/handlers.py', 'latest_text', 2, 2, 4).
python_function('urirdp-docker/packages/python/urirdp_ocr/handlers.py', 'image_text', 2, 6, 6).
python_function('urirdp-docker/packages/python/urirdp_ocr/routes.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_shell/__init__.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdp_shell/handlers.py', '_mock', 3, 2, 2).
python_function('urirdp-docker/packages/python/urirdp_shell/handlers.py', 'shell_run', 2, 14, 9).
python_function('urirdp-docker/packages/python/urirdp_shell/routes.py', 'register', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdpedge/cli.py', 'build_runtime', 1, 8, 7).
python_function('urirdp-docker/packages/python/urirdpedge/cli.py', 'main', 1, 8, 16).
python_function('urirdp-docker/packages/python/urirdpedge/env.py', 'load_urisys_env', 0, 8, 12).
python_function('urirdp-docker/packages/python/urirdpedge/env.py', '_env_policy_candidates', 0, 2, 5).
python_function('urirdp-docker/packages/python/urirdpedge/env.py', 'load_env_policy', 0, 6, 5).
python_function('urirdp-docker/packages/python/urirdpedge/env.py', '_env_config', 1, 7, 2).
python_function('urirdp-docker/packages/python/urirdpedge/env.py', 'resolve_env_var', 2, 11, 8).
python_function('urirdp-docker/packages/python/urirdpedge/env.py', 'is_secret_env', 1, 1, 1).
python_function('urirdp-docker/packages/python/urirdpedge/runtime.py', 'load_json', 1, 3, 5).
python_function('urirdp-docker/packages/python/urirdpedge/runtime.py', 'load_yaml_flow', 1, 14, 16).
python_function('urirdp-docker/packages/python/urirdpedge/runtime.py', 'run_flow', 3, 7, 11).
python_function('urirdp-docker/packages/python/urirdpedge/runtime.py', 'make_handler', 1, 1, 15).
python_function('urirdp-docker/packages/python/urirdpedge/runtime.py', 'serve', 3, 2, 4).
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
python_function('uristepper-docker/packages/python/uristepper/drivers.py', 'make_driver', 1, 3, 3).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', '_device_axis', 1, 2, 2).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', '_driver', 2, 1, 2).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', '_enforce_safety', 2, 10, 4).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', '_dry_or_driver', 2, 2, 3).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', 'status', 2, 2, 4).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', 'enable', 2, 2, 3).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', 'disable', 2, 2, 3).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', 'stop', 2, 2, 3).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', 'move_relative', 2, 3, 8).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', 'move_absolute', 2, 2, 7).
python_function('uristepper-docker/packages/python/uristepper/handlers.py', 'home', 2, 2, 5).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', '_json_arg', 1, 3, 4).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', 'cmd_call', 1, 4, 6).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', 'cmd_explain', 1, 1, 4).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', 'cmd_routes', 1, 1, 4).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', 'cmd_events', 1, 1, 4).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', 'cmd_flow', 1, 12, 17).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', 'cmd_serve', 1, 1, 1).
python_function('uristepper-docker/packages/python/urisysedge/cli.py', 'main', 1, 1, 7).
python_function('uristepper-docker/packages/python/urisysedge/runtime.py', 'load_json', 1, 1, 3).
python_function('uristepper-docker/packages/python/urisysedge/runtime.py', 'build_runtime', 2, 6, 7).
python_function('uristepper-docker/packages/python/urisysedge/server.py', 'make_handler', 1, 1, 20).
python_function('uristepper-docker/packages/python/urisysedge/server.py', 'serve', 4, 1, 5).
python_function('uristepper-docker/tests/e2e.py', 'post', 2, 1, 7).
python_function('uristepper-docker/tests/e2e.py', 'get', 1, 1, 4).
python_function('uristepper-docker/tests/e2e.py', 'assert_ok', 2, 2, 4).
python_function('uristepper-docker/tests/e2e.py', 'main', 0, 3, 7).
python_function('urisys-automation-lab/packages/python/labedge/runtime.py', 'load_json', 1, 3, 4).
python_function('urisys-automation-lab/packages/python/urichat/handlers.py', '_match_transcript', 1, 4, 3).
python_function('urisys-automation-lab/packages/python/urichat/handlers.py', '_forward_uri', 4, 2, 9).
python_function('urisys-automation-lab/packages/python/urichat/handlers.py', 'message_send', 2, 2, 2).
python_function('urisys-automation-lab/packages/python/urichat/handlers.py', 'uri_execute', 2, 15, 7).
python_function('urisys-automation-lab/packages/python/urichat/routes.py', 'register', 1, 1, 1).
python_function('urisys-automation-lab/packages/python/uristt/handlers.py', '_session_id', 1, 2, 1).
python_function('urisys-automation-lab/packages/python/uristt/handlers.py', 'session_start', 2, 1, 2).
python_function('urisys-automation-lab/packages/python/uristt/handlers.py', 'session_transcript', 2, 5, 4).
python_function('urisys-automation-lab/packages/python/uristt/handlers.py', 'audio_transcribe', 2, 5, 2).
python_function('urisys-automation-lab/packages/python/uristt/routes.py', 'register', 1, 1, 1).
python_function('urisys-automation-lab/packages/python/uriwebrtc/handlers.py', '_room_id', 1, 4, 1).
python_function('urisys-automation-lab/packages/python/uriwebrtc/handlers.py', 'session_start', 2, 2, 2).
python_function('urisys-automation-lab/packages/python/uriwebrtc/handlers.py', 'data_send', 2, 3, 3).
python_function('urisys-automation-lab/packages/python/uriwebrtc/routes.py', 'register', 1, 1, 1).
python_function('urisys-automation-lab/server/automation_lab_server.py', 'build_lab_runtime', 1, 16, 11).
python_function('urisys-automation-lab/server/automation_lab_server.py', 'forward_uri_call', 4, 1, 8).
python_function('urisys-automation-lab/server/automation_lab_server.py', 'serve', 2, 4, 8).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', '_rt', 0, 1, 2).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', 'test_stt_session_and_transcript', 0, 4, 3).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', 'test_chat_uri_execute_dry_run', 0, 4, 2).
python_function('urisys-automation-lab/tests/test_lab_handlers.py', 'test_webrtc_data_send', 0, 4, 3).
python_function('urisys-node/packages/python/uriscreen/handlers.py', '_screen_cfg', 1, 1, 1).
python_function('urisys-node/packages/python/uriscreen/handlers.py', '_backend', 2, 2, 2).
python_function('urisys-node/packages/python/uriscreen/handlers.py', '_output_dir', 2, 2, 4).
python_function('urisys-node/packages/python/uriscreen/handlers.py', '_monitor_index', 3, 6, 4).
python_function('urisys-node/packages/python/uriscreen/handlers.py', '_store_latest', 2, 1, 1).
python_function('urisys-node/packages/python/uriscreen/handlers.py', '_mock_png', 1, 1, 1).
python_function('urisys-node/packages/python/uriscreen/handlers.py', 'capture', 2, 7, 18).
python_function('urisys-node/packages/python/uriscreen/handlers.py', 'frame', 2, 1, 5).
python_function('urisys-node/packages/python/uriscreen/handlers.py', 'capture_loop', 2, 4, 9).
python_function('urisys-node/packages/python/uriscreen/routes.py', 'register', 1, 1, 1).
python_function('urisys-node/packages/python/urisysnode/artifact_resolver.py', 'load_node_profile', 1, 3, 4).
python_function('urisys-node/packages/python/urisysnode/artifact_resolver.py', 'load_artifact_index', 1, 1, 3).
python_function('urisys-node/packages/python/urisysnode/artifact_resolver.py', 'select_artifact', 2, 15, 6).
python_function('urisys-node/packages/python/urisysnode/artifact_resolver.py', 'docker_pull', 1, 4, 3).
python_function('urisys-node/packages/python/urisysnode/artifact_resolver.py', 'docker_run_worker', 1, 3, 3).
python_function('urisys-node/packages/python/urisysnode/artifact_resolver.py', 'wait_health', 2, 4, 6).
python_function('urisys-node/packages/python/urisysnode/artifact_resolver.py', 'resolve_and_run', 2, 4, 9).
python_function('urisys-node/packages/python/urisysnode/cli.py', 'main', 1, 14, 26).
python_function('urisys-node/packages/python/urisysnode/client.py', 'discover_mdns', 1, 2, 12).
python_function('urisys-node/packages/python/urisysnode/client.py', 'remote_call', 4, 3, 8).
python_function('urisys-node/packages/python/urisysnode/client.py', 'call_via_route_map', 1, 6, 12).
python_function('urisys-node/packages/python/urisysnode/env.py', 'load_urisys_env', 0, 8, 12).
python_function('urisys-node/packages/python/urisysnode/handlers.py', 'query_health', 2, 1, 1).
python_function('urisys-node/packages/python/urisysnode/handlers.py', 'query_identity', 2, 2, 4).
python_function('urisys-node/packages/python/urisysnode/handlers.py', 'command_indicator_on', 2, 1, 3).
python_function('urisys-node/packages/python/urisysnode/handlers.py', 'command_indicator_off', 2, 1, 2).
python_function('urisys-node/packages/python/urisysnode/identity.py', '_data_dir', 0, 1, 3).
python_function('urisys-node/packages/python/urisysnode/identity.py', '_identity_path', 0, 1, 1).
python_function('urisys-node/packages/python/urisysnode/identity.py', '_pairing_path', 0, 1, 1).
python_function('urisys-node/packages/python/urisysnode/identity.py', '_hostname', 0, 1, 1).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'load_identity', 0, 4, 14).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'save_identity', 1, 1, 3).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'load_pairing', 0, 3, 5).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'enroll', 3, 3, 6).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'save_pairing', 1, 1, 3).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'set_remote_control', 2, 2, 2).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'require_paired', 1, 4, 3).
python_function('urisys-node/packages/python/urisysnode/identity.py', 'health_payload', 1, 1, 4).
python_function('urisys-node/packages/python/urisysnode/router.py', 'load_route_map', 1, 3, 4).
python_function('urisys-node/packages/python/urisysnode/router.py', '_match_pattern', 2, 1, 3).
python_function('urisys-node/packages/python/urisysnode/router.py', 'resolve_remote_route', 2, 5, 2).
python_function('urisys-node/packages/python/urisysnode/router.py', 'rewrite_uri_for_slave', 3, 6, 4).
python_function('urisys-node/packages/python/urisysnode/router.py', 'node_endpoint', 2, 5, 1).
python_function('urisys-node/packages/python/urisysnode/routes.py', 'register', 1, 1, 1).
python_function('urisys-node/packages/python/urisysnode/runtime.py', 'load_json', 1, 3, 4).
python_function('urisys-node/packages/python/urisysnode/serve.py', '_extend_pack_paths', 0, 4, 5).
python_function('urisys-node/packages/python/urisysnode/serve.py', 'build_runtime', 1, 11, 10).
python_function('urisys-node/packages/python/urisysnode/serve.py', 'make_handler', 1, 1, 19).
python_function('urisys-node/packages/python/urisysnode/serve.py', 'serve', 3, 2, 6).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_select_artifact_by_platform', 1, 2, 4).
python_function('urisys-node/tests/test_artifact_resolver.py', 'test_load_artifact_index', 1, 2, 3).
python_function('urisys-node/tests/test_urisys_node.py', 'test_identity_and_enroll', 0, 5, 3).
python_function('urisys-node/tests/test_urisys_node.py', 'test_screen_capture_mock', 0, 4, 4).
python_function('urisys-node/tests/test_urisys_node.py', 'test_rewrite_uri_for_slave', 0, 2, 1).
python_function('urisys-node/tests/test_urisys_node.py', 'test_health_payload', 0, 3, 1).

% ── Python Classes ───────────────────────────────────────
python_class('scripts/session_report.py', 'StepResult').
python_class('scripts/session_report.py', 'SessionReport').
python_method('SessionReport', 'passed', 0, 3, 1).
python_method('SessionReport', 'failed', 0, 3, 1).
python_class('scripts/session_report.py', 'RunAnalysis').
python_method('RunAnalysis', 'all_passed', 0, 2, 1).
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
python_class('src/urisys/managers/bridge_manager.py', 'BridgeManager').
python_method('BridgeManager', 'call_http', 5, 3, 7).
python_class('src/urisys/managers/event_manager.py', 'EventManager').
python_method('EventManager', '__init__', 1, 1, 2).
python_method('EventManager', 'list_events', 0, 1, 2).
python_class('src/urisys/managers/markpact_manager.py', 'MarkpactBlock').
python_class('src/urisys/managers/markpact_manager.py', 'CompiledMarkpact').
python_method('CompiledMarkpact', 'to_dict', 0, 4, 1).
python_class('src/urisys/managers/markpact_manager.py', 'MarkpactError').
python_class('src/urisys/managers/markpact_manager.py', 'MarkpactManager').
python_method('MarkpactManager', '__init__', 1, 1, 1).
python_method('MarkpactManager', 'read_blocks', 1, 3, 8).
python_method('MarkpactManager', 'source_hash', 1, 1, 4).
python_method('MarkpactManager', 'load_pack_block', 1, 7, 5).
python_method('MarkpactManager', 'validate', 1, 10, 18).
python_method('MarkpactManager', 'compile', 1, 21, 25).
python_method('MarkpactManager', 'manifest_path_for', 1, 1, 1).
python_method('MarkpactManager', 'run_tests', 1, 20, 15).
python_method('MarkpactManager', '_compile_manifest', 1, 28, 14).
python_method('MarkpactManager', '_package_id', 2, 5, 5).
python_method('MarkpactManager', '_capabilities', 1, 6, 3).
python_method('MarkpactManager', '_scheme', 2, 8, 5).
python_method('MarkpactManager', '_handler_blocks', 1, 5, 2).
python_method('MarkpactManager', '_load_yaml_blocks', 2, 6, 4).
python_method('MarkpactManager', '_handler_id_from_ref', 1, 2, 2).
python_method('MarkpactManager', '_ensure_importable', 1, 2, 3).
python_class('src/urisys/managers/pack_manager.py', 'PackManager').
python_method('PackManager', '__init__', 1, 1, 5).
python_method('PackManager', 'parse_packs', 1, 15, 6).
python_method('PackManager', 'parse_markpacts', 1, 8, 4).
python_method('PackManager', 'resolve_package_name', 1, 1, 1).
python_method('PackManager', '_is_markpact_path', 1, 3, 2).
python_method('PackManager', '_is_manifest_path', 1, 4, 1).
python_method('PackManager', 'manifest_paths', 0, 6, 12).
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
python_class('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'Route').
python_method('Route', 'compile', 0, 3, 6).
python_method('Route', 'match', 1, 4, 5).
python_class('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'JsonlEventStore').
python_method('JsonlEventStore', '__init__', 1, 2, 2).
python_method('JsonlEventStore', 'append', 1, 1, 3).
python_class('uribrowser-docker/packages/python/uribrowseredge/runtime.py', 'Runtime').
python_method('Runtime', '__init__', 2, 2, 1).
python_method('Runtime', 'register', 2, 2, 4).
python_method('Runtime', 'resolve', 1, 3, 2).
python_method('Runtime', '_load_handler', 1, 2, 5).
python_method('Runtime', 'call', 3, 8, 12).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/dispatcher.py', 'UriControlRuntime').
python_method('UriControlRuntime', '__init__', 0, 3, 2).
python_method('UriControlRuntime', 'call', 3, 10, 10).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/errors.py', 'UriControlError').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/errors.py', 'UriParseError').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/errors.py', 'RegistryError').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/errors.py', 'RouteNotFoundError').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/errors.py', 'HandlerLoadError').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/errors.py', 'PolicyDeniedError').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/event_store.py', 'EventStore').
python_method('EventStore', 'append', 1, 1, 0).
python_method('EventStore', 'read_all', 0, 6, 0).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/event_store.py', 'InMemoryEventStore').
python_method('InMemoryEventStore', '__init__', 0, 1, 0).
python_method('InMemoryEventStore', 'append', 1, 1, 1).
python_method('InMemoryEventStore', 'read_all', 0, 6, 1).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/event_store.py', 'JsonlEventStore').
python_method('JsonlEventStore', '__init__', 1, 1, 2).
python_method('JsonlEventStore', 'append', 1, 1, 4).
python_method('JsonlEventStore', 'read_all', 0, 6, 8).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 'ParsedUri').
python_method('ParsedUri', 'body', 0, 4, 1).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 'Route').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 'MatchedRoute').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 'CapabilityManifest').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 'PolicyDecision').
python_class('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 'EventEnvelope').
python_method('EventEnvelope', 'to_dict', 0, 3, 0).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/models.py', 'DispatchResult').
python_method('DispatchResult', 'to_dict', 0, 3, 1).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/policy.py', 'PolicyEngine').
python_method('PolicyEngine', '__init__', 0, 2, 1).
python_method('PolicyEngine', 'decide', 2, 9, 3).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/projection.py', 'ProjectionBuilder').
python_method('ProjectionBuilder', '__init__', 1, 1, 0).
python_method('ProjectionBuilder', 'latest_by_source_uri', 0, 2, 2).
python_method('ProjectionBuilder', 'status_by_source_uri', 0, 6, 4).
python_method('ProjectionBuilder', 'events_by_type', 0, 2, 5).
python_method('ProjectionBuilder', 'from_events', 1, 2, 3).
python_class('urienv-docker/vendor/uricore/core/python/uri_control/registry.py', 'CapabilityRegistry').
python_method('CapabilityRegistry', '__init__', 0, 1, 0).
python_method('CapabilityRegistry', 'from_manifest_files', 2, 2, 2).
python_method('CapabilityRegistry', 'manifests', 0, 1, 1).
python_method('CapabilityRegistry', 'routes', 0, 2, 1).
python_method('CapabilityRegistry', 'load_manifest_file', 1, 3, 6).
python_method('CapabilityRegistry', 'load_manifest', 1, 21, 11).
python_method('CapabilityRegistry', 'match', 1, 6, 8).
python_method('CapabilityRegistry', 'explain', 1, 1, 1).
python_class('urikvm-docker/packages/python/urikvmedge/runtime.py', 'Route').
python_method('Route', 'compile', 0, 3, 6).
python_method('Route', 'match', 1, 4, 5).
python_class('urikvm-docker/packages/python/urikvmedge/runtime.py', 'JsonlEventStore').
python_method('JsonlEventStore', '__init__', 1, 2, 2).
python_method('JsonlEventStore', 'append', 1, 1, 3).
python_class('urikvm-docker/packages/python/urikvmedge/runtime.py', 'Runtime').
python_method('Runtime', '__init__', 2, 2, 1).
python_method('Runtime', 'register', 2, 2, 4).
python_method('Runtime', 'resolve', 1, 3, 2).
python_method('Runtime', '_load_handler', 1, 2, 5).
python_method('Runtime', 'call', 3, 10, 13).
python_class('urirdp-docker/packages/python/urirdpedge/runtime.py', 'Route').
python_method('Route', 'compile', 0, 3, 6).
python_method('Route', 'match', 1, 5, 5).
python_class('urirdp-docker/packages/python/urirdpedge/runtime.py', 'JsonlEventStore').
python_method('JsonlEventStore', '__init__', 1, 2, 2).
python_method('JsonlEventStore', 'append', 1, 1, 3).
python_class('urirdp-docker/packages/python/urirdpedge/runtime.py', 'Runtime').
python_method('Runtime', '__init__', 2, 2, 1).
python_method('Runtime', 'register', 2, 2, 4).
python_method('Runtime', 'resolve', 1, 3, 2).
python_method('Runtime', '_load_handler', 1, 2, 5).
python_method('Runtime', 'call', 3, 10, 13).
python_class('urirdp-docker/tests/test_rdp_kvm.py', 'Args').
python_class('uristepper-docker/packages/python/uristepper/drivers.py', 'StepperDriver').
python_method('StepperDriver', 'status', 3, 1, 0).
python_method('StepperDriver', 'enable', 3, 2, 0).
python_method('StepperDriver', 'disable', 3, 2, 0).
python_method('StepperDriver', 'stop', 3, 1, 0).
python_method('StepperDriver', 'move_relative', 6, 4, 0).
python_method('StepperDriver', 'move_absolute', 5, 2, 5).
python_method('StepperDriver', 'home', 5, 1, 0).
python_class('uristepper-docker/packages/python/uristepper/drivers.py', 'MockStepperDriver').
python_method('MockStepperDriver', '__init__', 1, 2, 3).
python_method('MockStepperDriver', '_load', 0, 3, 3).
python_method('MockStepperDriver', '_save', 1, 1, 2).
python_method('MockStepperDriver', '_key', 2, 1, 0).
python_method('MockStepperDriver', '_axis', 2, 1, 4).
python_method('MockStepperDriver', '_update', 3, 1, 5).
python_method('MockStepperDriver', 'status', 3, 1, 2).
python_method('MockStepperDriver', 'enable', 3, 2, 2).
python_method('MockStepperDriver', 'disable', 3, 2, 1).
python_method('MockStepperDriver', 'stop', 3, 1, 1).
python_method('MockStepperDriver', 'move_relative', 6, 4, 7).
python_method('MockStepperDriver', 'move_absolute', 5, 2, 5).
python_method('MockStepperDriver', 'home', 5, 1, 1).
python_class('uristepper-docker/packages/python/uristepper/drivers.py', 'RpiGpioStepDirDriver').
python_method('RpiGpioStepDirDriver', '__init__', 0, 2, 1).
python_method('RpiGpioStepDirDriver', '_pins', 2, 3, 3).
python_method('RpiGpioStepDirDriver', '_enable_value', 2, 2, 2).
python_method('RpiGpioStepDirDriver', 'status', 3, 1, 0).
python_method('RpiGpioStepDirDriver', 'enable', 3, 2, 2).
python_method('RpiGpioStepDirDriver', 'disable', 3, 2, 2).
python_method('RpiGpioStepDirDriver', 'stop', 3, 1, 0).
python_method('RpiGpioStepDirDriver', 'move_relative', 6, 4, 9).
python_method('RpiGpioStepDirDriver', 'home', 5, 1, 1).
python_class('uristepper-docker/packages/python/urisysedge/runtime.py', 'UriError').
python_class('uristepper-docker/packages/python/urisysedge/runtime.py', 'PolicyDenied').
python_class('uristepper-docker/packages/python/urisysedge/runtime.py', 'Route').
python_method('Route', 'compile', 0, 1, 3).
python_method('Route', 'match', 1, 3, 3).
python_class('uristepper-docker/packages/python/urisysedge/runtime.py', 'JsonlEventStore').
python_method('JsonlEventStore', '__init__', 1, 4, 2).
python_method('JsonlEventStore', 'append', 1, 1, 9).
python_method('JsonlEventStore', 'tail', 1, 4, 5).
python_class('uristepper-docker/packages/python/urisysedge/runtime.py', 'StepperRuntime').
python_method('StepperRuntime', '__init__', 3, 4, 3).
python_method('StepperRuntime', 'explain', 1, 1, 2).
python_method('StepperRuntime', 'list_routes', 0, 2, 0).
python_method('StepperRuntime', 'call', 3, 6, 7).
python_method('StepperRuntime', '_match', 1, 4, 3).
python_class('uristepper-docker/tests/test_runtime.py', 'RuntimeTest').
python_method('RuntimeTest', 'setUp', 0, 1, 6).
python_method('RuntimeTest', 'test_status', 0, 1, 3).
python_method('RuntimeTest', 'test_policy_requires_approval', 0, 1, 3).
python_method('RuntimeTest', 'test_move_relative', 0, 1, 3).
python_method('RuntimeTest', 'test_safety_limit', 0, 1, 3).
python_class('urisys-automation-lab/packages/python/labedge/runtime.py', 'Route').
python_method('Route', 'compile', 0, 3, 6).
python_method('Route', 'match', 1, 5, 5).
python_class('urisys-automation-lab/packages/python/labedge/runtime.py', 'JsonlEventStore').
python_method('JsonlEventStore', '__init__', 1, 2, 2).
python_method('JsonlEventStore', 'append', 1, 1, 3).
python_class('urisys-automation-lab/packages/python/labedge/runtime.py', 'Runtime').
python_method('Runtime', '__init__', 2, 2, 1).
python_method('Runtime', 'register', 2, 2, 4).
python_method('Runtime', 'resolve', 1, 3, 2).
python_method('Runtime', '_load_handler', 1, 2, 5).
python_method('Runtime', 'call', 3, 8, 12).
python_class('urisys-automation-lab/server/automation_lab_server.py', 'LabHandler').
python_method('LabHandler', 'log_message', 1, 1, 2).
python_method('LabHandler', '_json', 2, 1, 8).
python_method('LabHandler', '_read_json', 0, 4, 5).
python_method('LabHandler', 'do_OPTIONS', 0, 1, 3).
python_method('LabHandler', 'do_GET', 0, 9, 12).
python_method('LabHandler', 'do_POST', 0, 18, 8).
python_class('urisys-node/packages/python/urisysnode/runtime.py', 'Route').
python_method('Route', 'compile', 0, 3, 6).
python_method('Route', 'match', 1, 5, 5).
python_class('urisys-node/packages/python/urisysnode/runtime.py', 'JsonlEventStore').
python_method('JsonlEventStore', '__init__', 1, 2, 2).
python_method('JsonlEventStore', 'append', 1, 1, 3).
python_method('JsonlEventStore', 'tail', 1, 4, 5).
python_class('urisys-node/packages/python/urisysnode/runtime.py', 'Runtime').
python_method('Runtime', '__init__', 2, 2, 1).
python_method('Runtime', 'register', 2, 2, 4).
python_method('Runtime', 'resolve', 1, 3, 2).
python_method('Runtime', '_load_handler', 1, 2, 5).
python_method('Runtime', 'call', 3, 8, 12).

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

*286 nodes · 350 edges · 58 modules · CC̄=3.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `session_urirdp_real_docker` *(in scripts.run_test_sessions)* | 30 ⚠ | 0 | 69 | **69** |
| `analyze_run` *(in scripts.session_report)* | 34 ⚠ | 2 | 64 | **66** |
| `session_lab_10_flows` *(in scripts.run_test_sessions)* | 28 ⚠ | 0 | 55 | **55** |
| `write_session_report` *(in scripts.session_report)* | 28 ⚠ | 2 | 50 | **52** |
| `compile` *(in src.urisys.managers.markpact_manager.MarkpactManager)* | 21 ⚠ | 0 | 46 | **46** |
| `main` *(in src.urisys.cli)* | 18 ⚠ | 0 | 44 | **44** |
| `make_handler` *(in uristepper-docker.packages.python.urisysedge.server)* | 1 | 1 | 43 | **44** |
| `session_automation_lab` *(in scripts.run_test_sessions)* | 16 ⚠ | 1 | 43 | **44** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.15s
# nodes: 286 | edges: 350 | modules: 58
# CC̄=3.7

HUBS[20]:
  scripts.run_test_sessions.session_urirdp_real_docker
    CC=30  in:0  out:69  total:69
  scripts.session_report.analyze_run
    CC=34  in:2  out:64  total:66
  scripts.run_test_sessions.session_lab_10_flows
    CC=28  in:0  out:55  total:55
  scripts.session_report.write_session_report
    CC=28  in:2  out:50  total:52
  src.urisys.managers.markpact_manager.MarkpactManager.compile
    CC=21  in:0  out:46  total:46
  src.urisys.cli.main
    CC=18  in:0  out:44  total:44
  uristepper-docker.packages.python.urisysedge.server.make_handler
    CC=1  in:1  out:43  total:44
  scripts.run_test_sessions.session_automation_lab
    CC=16  in:1  out:43  total:44
  urienv-docker.packages.python.urienv.src.urienv.handlers._cfg
    CC=7  in:9  out:29  total:38
  src.urisys.cli.build_parser
    CC=1  in:1  out:36  total:37
  scripts.session_report.generate_report
    CC=13  in:2  out:35  total:37
  scripts.run_test_sessions._run_cmd
    CC=5  in:26  out:11  total:37
  urienv-docker.packages.python.urisysedge.src.urisysedge.server.serve
    CC=1  in:0  out:36  total:36
  urikvm-docker.packages.python.urillm.handlers._vision_analyze
    CC=22  in:1  out:34  total:35
  src.urisys.managers.markpact_manager.MarkpactManager._compile_manifest
    CC=28  in:0  out:35  total:35
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  scripts.run_test_sessions.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  urisys-node.packages.python.urisysnode.serve.make_handler
    CC=1  in:1  out:30  total:31
  urienv-docker.vendor.uricore.core.python.uri_control.dispatcher.UriControlRuntime.call
    CC=10  in:0  out:31  total:31

MODULES:
  scripts.run_test_sessions  [25 funcs]
    _capture_rdp_screenshot  CC=5  out:6
    _compose_cmd  CC=4  out:4
    _copy_container_file  CC=2  out:4
    _docker_logs  CC=4  out:5
    _finalize_session  CC=5  out:13
    _host_id  CC=1  out:3
    _http_json  CC=5  out:12
    _now_iso  CC=1  out:3
    _prepare_ok_target  CC=1  out:2
    _prepare_urirdp_data  CC=4  out:6
  scripts.session_report  [8 funcs]
    _infer_steps  CC=20  out:25
    _read_json  CC=3  out:3
    _tail  CC=2  out:0
    analyze_run  CC=34  out:64
    generate_report  CC=13  out:35
    main  CC=4  out:23
    write_run_analysis  CC=8  out:23
    write_session_report  CC=28  out:50
  src.urisys.cli  [5 funcs]
    _add_runtime_flags  CC=1  out:4
    build_parser  CC=1  out:36
    main  CC=18  out:44
    print_json  CC=1  out:2
    resolve_markpact_source  CC=2  out:3
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [1 funcs]
    __init__  CC=1  out:1
  src.urisys.flow  [2 funcs]
    iter_steps  CC=7  out:8
    load_flow  CC=3  out:5
  src.urisys.http_server  [3 funcs]
    _read_json  CC=3  out:5
    _send  CC=1  out:12
    create_server  CC=1  out:31
  src.urisys.managers.event_manager  [1 funcs]
    list_events  CC=1  out:2
  src.urisys.managers.markpact_manager  [7 funcs]
    _compile_manifest  CC=28  out:35
    _scheme  CC=8  out:10
    compile  CC=21  out:46
    read_blocks  CC=3  out:11
    _parse_meta  CC=4  out:8
    _safe_identifier  CC=3  out:6
    _scheme_from_uri  CC=2  out:2
  src.urisys.managers.pack_manager  [1 funcs]
    manifest_paths  CC=6  out:18
  uribrowser-docker.packages.python.uribrowserdocker.handlers  [6 funcs]
    _profile  CC=1  out:2
    _session_state  CC=1  out:5
    get_dom  CC=1  out:4
    open_page  CC=11  out:27
    screenshot  CC=3  out:8
    status  CC=1  out:7
  uribrowser-docker.packages.python.uribrowseredge.cli  [1 funcs]
    build_runtime  CC=2  out:7
  uribrowser-docker.packages.python.uribrowseredge.runtime  [4 funcs]
    load_yaml_flow  CC=10  out:15
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  urienv-docker.packages.python.urienv.src.urienv.handlers  [19 funcs]
    _cfg  CC=7  out:29
    _get_value  CC=3  out:2
    _is_mutable  CC=1  out:0
    _is_public  CC=3  out:2
    _is_secret  CC=3  out:2
    _mask  CC=3  out:1
    _name  CC=3  out:5
    _read_docker_secret  CC=4  out:6
    _require_visible  CC=3  out:4
    _split_csv  CC=7  out:10
  urienv-docker.packages.python.urisysedge.src.urisysedge.flow  [1 funcs]
    run_flow  CC=12  out:15
  urienv-docker.packages.python.urisysedge.src.urisysedge.pack_loader  [2 funcs]
    manifest_path_for_pack  CC=4  out:6
    manifest_paths  CC=3  out:3
  urienv-docker.packages.python.urisysedge.src.urisysedge.runtime  [4 funcs]
    build_runtime  CC=3  out:6
    load_device_config  CC=3  out:2
    load_env_config  CC=3  out:2
    result_to_dict  CC=2  out:0
  urienv-docker.packages.python.urisysedge.src.urisysedge.server  [1 funcs]
    serve  CC=1  out:36
  urienv-docker.vendor.uricore.core.python.uri_control.cli  [7 funcs]
    _load_payload  CC=3  out:5
    _registry_from_args  CC=2  out:2
    build_parser  CC=1  out:25
    cmd_call  CC=2  out:8
    cmd_explain  CC=1  out:4
    cmd_list  CC=2  out:3
    main  CC=1  out:4
  urienv-docker.vendor.uricore.core.python.uri_control.dispatcher  [2 funcs]
    call  CC=10  out:31
    _new_id  CC=1  out:1
  urienv-docker.vendor.uricore.core.python.uri_control.event_store  [1 funcs]
    dump_events  CC=2  out:1
  urienv-docker.vendor.uricore.core.python.uri_control.parser  [2 funcs]
    canonicalize_uri  CC=1  out:1
    parse_uri  CC=7  out:11
  urienv-docker.vendor.uricore.core.python.uri_control.registry  [4 funcs]
    match  CC=6  out:8
    _compile_pattern  CC=6  out:12
    _load_python_handler  CC=6  out:11
    _pattern_body  CC=2  out:4
  urikvm-docker.packages.python.urihim.handlers  [9 funcs]
    _driver  CC=1  out:3
    _pyautogui  CC=3  out:3
    _real_allowed  CC=2  out:3
    _state  CC=1  out:2
    keyboard_hotkey  CC=6  out:11
    keyboard_type  CC=3  out:8
    mouse_click  CC=7  out:16
    mouse_move  CC=3  out:11
    mouse_status  CC=1  out:2
  urikvm-docker.packages.python.urikvm.handlers  [4 funcs]
    _profile  CC=1  out:2
    _store_screenshot  CC=1  out:4
    monitor_list  CC=2  out:4
    screenshot  CC=5  out:18
  urikvm-docker.packages.python.urikvmedge.cli  [1 funcs]
    build_runtime  CC=6  out:11
  urikvm-docker.packages.python.urikvmedge.env  [4 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    load_env_policy  CC=6  out:5
    resolve_env_var  CC=11  out:9
  urikvm-docker.packages.python.urikvmedge.runtime  [5 funcs]
    call  CC=10  out:22
    load_yaml_flow  CC=10  out:15
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  urikvm-docker.packages.python.urillm.handlers  [12 funcs]
    _box_center  CC=1  out:4
    _driver  CC=1  out:2
    _goal_text  CC=4  out:4
    _heuristic_analyze  CC=16  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=1  out:2
    _openai_chat  CC=2  out:9
    _parse_json_response  CC=5  out:5
    _target_from_goal  CC=3  out:6
    _vision_analyze  CC=22  out:34
  urikvm-docker.packages.python.uriocr.handlers  [10 funcs]
    _driver  CC=1  out:2
    _extract_text  CC=6  out:10
    _latest_screenshot  CC=2  out:2
    _merge_word_boxes  CC=5  out:17
    _mock_boxes  CC=2  out:2
    _ocr_cfg  CC=1  out:2
    _png_bytes  CC=4  out:4
    _tesseract_boxes  CC=8  out:14
    image_text  CC=1  out:3
    latest_text  CC=1  out:1
  urikvm-docker.scripts.real_pipeline  [2 funcs]
    build_runtime  CC=1  out:6
    main  CC=14  out:26
  urirdp-docker.packages.python.urirdp.handlers  [5 funcs]
    _service_status  CC=4  out:4
    display  CC=2  out:4
    display_status  CC=7  out:12
    prepare_target  CC=4  out:9
    status  CC=1  out:9
  urirdp-docker.packages.python.urirdp_him.handlers  [7 funcs]
    _mock  CC=1  out:1
    keyboard_hotkey  CC=8  out:11
    keyboard_key  CC=5  out:9
    keyboard_type  CC=5  out:13
    keyboard_type_text  CC=1  out:1
    mouse_click  CC=11  out:18
    mouse_move  CC=5  out:13
  urirdp-docker.packages.python.urirdp_kvm.display  [6 funcs]
    allow_real  CC=2  out:3
    base_env  CC=6  out:10
    config_value  CC=2  out:2
    detect_display  CC=7  out:10
    ensure_screenshot_dir  CC=1  out:3
    run_cmd  CC=1  out:2
  urirdp-docker.packages.python.urirdp_kvm.handlers  [2 funcs]
    display_info  CC=4  out:5
    screenshot  CC=9  out:23
  urirdp-docker.packages.python.urirdp_llm.handlers  [11 funcs]
    _config  CC=2  out:1
    _env  CC=3  out:6
    _heuristic  CC=5  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=6  out:7
    _openai_compatible_chat  CC=1  out:9
    _parse_json_response  CC=5  out:5
    _screenshot_b64  CC=2  out:7
    _target  CC=3  out:4
    _vision_messages  CC=4  out:2
  urirdp-docker.packages.python.urirdp_ocr.handlers  [5 funcs]
    _mock_ocr  CC=1  out:0
    _parse_tesseract_tsv  CC=7  out:19
    _tesseract_ocr  CC=9  out:23
    image_text  CC=6  out:8
    latest_text  CC=2  out:5
  urirdp-docker.packages.python.urirdp_shell.handlers  [2 funcs]
    _mock  CC=2  out:2
    shell_run  CC=14  out:17
  urirdp-docker.packages.python.urirdpedge.cli  [1 funcs]
    build_runtime  CC=8  out:14
  urirdp-docker.packages.python.urirdpedge.env  [6 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    is_secret_env  CC=1  out:1
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:18
    resolve_env_var  CC=11  out:9
  urirdp-docker.packages.python.urirdpedge.runtime  [5 funcs]
    call  CC=10  out:22
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  uristepper-docker.packages.python.uristepper.drivers  [1 funcs]
    make_driver  CC=3  out:3
  uristepper-docker.packages.python.uristepper.handlers  [11 funcs]
    _device_axis  CC=2  out:9
    _driver  CC=1  out:2
    _dry_or_driver  CC=2  out:5
    _enforce_safety  CC=10  out:15
    disable  CC=2  out:3
    enable  CC=2  out:3
    home  CC=2  out:8
    move_absolute  CC=2  out:8
    move_relative  CC=3  out:10
    status  CC=2  out:4
  uristepper-docker.packages.python.urisysedge.cli  [7 funcs]
    _json_arg  CC=3  out:5
    cmd_call  CC=4  out:7
    cmd_events  CC=1  out:4
    cmd_explain  CC=1  out:4
    cmd_flow  CC=12  out:22
    cmd_routes  CC=1  out:4
    cmd_serve  CC=1  out:1
  uristepper-docker.packages.python.urisysedge.runtime  [2 funcs]
    build_runtime  CC=6  out:14
    load_json  CC=1  out:3
  uristepper-docker.packages.python.urisysedge.server  [2 funcs]
    make_handler  CC=1  out:43
    serve  CC=1  out:5
  urisys-automation-lab.packages.python.urichat.handlers  [2 funcs]
    _forward_uri  CC=2  out:9
    uri_execute  CC=15  out:27
  urisys-automation-lab.packages.python.uristt.handlers  [3 funcs]
    _session_id  CC=2  out:2
    session_start  CC=1  out:3
    session_transcript  CC=5  out:7
  urisys-automation-lab.packages.python.uriwebrtc.handlers  [3 funcs]
    _room_id  CC=4  out:3
    data_send  CC=3  out:4
    session_start  CC=2  out:2
  urisys-automation-lab.server.automation_lab_server  [2 funcs]
    build_lab_runtime  CC=16  out:22
    serve  CC=4  out:13
  urisys-automation-lab.web.app  [6 funcs]
    SR  CC=2  out:1
    data  CC=1  out:1
    log  CC=2  out:2
    rec  CC=1  out:1
    text  CC=1  out:2
    uriCall  CC=1  out:4
  urisys-node.packages.python.uriscreen.handlers  [8 funcs]
    _backend  CC=2  out:3
    _monitor_index  CC=6  out:9
    _output_dir  CC=2  out:5
    _screen_cfg  CC=1  out:2
    _store_latest  CC=1  out:1
    capture  CC=7  out:25
    capture_loop  CC=4  out:10
    frame  CC=1  out:5
  urisys-node.packages.python.urisysnode.artifact_resolver  [7 funcs]
    docker_pull  CC=4  out:4
    docker_run_worker  CC=3  out:4
    load_artifact_index  CC=1  out:3
    load_node_profile  CC=3  out:4
    resolve_and_run  CC=4  out:11
    select_artifact  CC=15  out:14
    wait_health  CC=4  out:6
  urisys-node.packages.python.urisysnode.client  [2 funcs]
    call_via_route_map  CC=6  out:14
    remote_call  CC=3  out:8
  urisys-node.packages.python.urisysnode.handlers  [4 funcs]
    command_indicator_off  CC=1  out:2
    command_indicator_on  CC=1  out:4
    query_health  CC=1  out:1
    query_identity  CC=2  out:8
  urisys-node.packages.python.urisysnode.identity  [12 funcs]
    _data_dir  CC=1  out:3
    _hostname  CC=1  out:1
    _identity_path  CC=1  out:1
    _pairing_path  CC=1  out:1
    enroll  CC=3  out:6
    health_payload  CC=1  out:8
    load_identity  CC=4  out:15
    load_pairing  CC=3  out:5
    require_paired  CC=4  out:5
    save_identity  CC=1  out:3
  urisys-node.packages.python.urisysnode.router  [5 funcs]
    _match_pattern  CC=1  out:4
    load_route_map  CC=3  out:4
    node_endpoint  CC=5  out:6
    resolve_remote_route  CC=5  out:3
    rewrite_uri_for_slave  CC=6  out:5
  urisys-node.packages.python.urisysnode.serve  [4 funcs]
    _extend_pack_paths  CC=4  out:7
    build_runtime  CC=11  out:18
    make_handler  CC=1  out:30
    serve  CC=2  out:9

EDGES:
  src.urisys.cli.build_parser → src.urisys.cli._add_runtime_flags
  src.urisys.cli.main → src.urisys.cli.build_parser
  src.urisys.cli.main → src.urisys.cli.resolve_markpact_source
  src.urisys.cli.main → src.urisys.cli.print_json
  src.urisys.http_server.create_server → src.urisys.http_server._send
  src.urisys.http_server.create_server → src.urisys.http_server._read_json
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.load_flow
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.iter_steps
  src.urisys.controllers.server_controller.ServerController.__init__ → src.urisys.http_server.create_server
  src.urisys.managers.event_manager.EventManager.list_events → urienv-docker.vendor.uricore.core.python.uri_control.event_store.dump_events
  src.urisys.managers.markpact_manager.MarkpactManager.read_blocks → src.urisys.managers.markpact_manager._parse_meta
  src.urisys.managers.markpact_manager.MarkpactManager.compile → src.urisys.managers.markpact_manager._safe_identifier
  src.urisys.managers.markpact_manager.MarkpactManager._compile_manifest → src.urisys.managers.markpact_manager._scheme_from_uri
  src.urisys.managers.markpact_manager.MarkpactManager._scheme → src.urisys.managers.markpact_manager._scheme_from_uri
  uristepper-docker.packages.python.uristepper.handlers._driver → uristepper-docker.packages.python.uristepper.drivers.make_driver
  uristepper-docker.packages.python.uristepper.handlers._dry_or_driver → uristepper-docker.packages.python.uristepper.handlers._driver
  uristepper-docker.packages.python.uristepper.handlers.status → uristepper-docker.packages.python.uristepper.handlers._device_axis
  uristepper-docker.packages.python.uristepper.handlers.status → uristepper-docker.packages.python.uristepper.handlers._dry_or_driver
  uristepper-docker.packages.python.uristepper.handlers.enable → uristepper-docker.packages.python.uristepper.handlers._device_axis
  uristepper-docker.packages.python.uristepper.handlers.enable → uristepper-docker.packages.python.uristepper.handlers._dry_or_driver
  uristepper-docker.packages.python.uristepper.handlers.disable → uristepper-docker.packages.python.uristepper.handlers._device_axis
  uristepper-docker.packages.python.uristepper.handlers.disable → uristepper-docker.packages.python.uristepper.handlers._dry_or_driver
  uristepper-docker.packages.python.uristepper.handlers.stop → uristepper-docker.packages.python.uristepper.handlers._device_axis
  uristepper-docker.packages.python.uristepper.handlers.stop → uristepper-docker.packages.python.uristepper.handlers._dry_or_driver
  uristepper-docker.packages.python.uristepper.handlers.move_relative → uristepper-docker.packages.python.uristepper.handlers._device_axis
  uristepper-docker.packages.python.uristepper.handlers.move_relative → uristepper-docker.packages.python.uristepper.handlers._enforce_safety
  uristepper-docker.packages.python.uristepper.handlers.move_relative → uristepper-docker.packages.python.uristepper.handlers._dry_or_driver
  uristepper-docker.packages.python.uristepper.handlers.move_absolute → uristepper-docker.packages.python.uristepper.handlers._device_axis
  uristepper-docker.packages.python.uristepper.handlers.move_absolute → uristepper-docker.packages.python.uristepper.handlers._enforce_safety
  uristepper-docker.packages.python.uristepper.handlers.move_absolute → uristepper-docker.packages.python.uristepper.handlers._dry_or_driver
  uristepper-docker.packages.python.uristepper.handlers.home → uristepper-docker.packages.python.uristepper.handlers._device_axis
  uristepper-docker.packages.python.uristepper.handlers.home → uristepper-docker.packages.python.uristepper.handlers._dry_or_driver
  uristepper-docker.packages.python.urisysedge.runtime.build_runtime → uristepper-docker.packages.python.urisysedge.runtime.load_json
  uristepper-docker.packages.python.urisysedge.cli.cmd_call → uristepper-docker.packages.python.urisysedge.runtime.build_runtime
  uristepper-docker.packages.python.urisysedge.cli.cmd_call → uristepper-docker.packages.python.urisysedge.cli._json_arg
  uristepper-docker.packages.python.urisysedge.cli.cmd_explain → uristepper-docker.packages.python.urisysedge.runtime.build_runtime
  uristepper-docker.packages.python.urisysedge.cli.cmd_routes → uristepper-docker.packages.python.urisysedge.runtime.build_runtime
  uristepper-docker.packages.python.urisysedge.cli.cmd_events → uristepper-docker.packages.python.urisysedge.runtime.build_runtime
  uristepper-docker.packages.python.urisysedge.cli.cmd_flow → uristepper-docker.packages.python.urisysedge.runtime.build_runtime
  uristepper-docker.packages.python.urisysedge.cli.cmd_serve → uristepper-docker.packages.python.urisysedge.server.serve
  uristepper-docker.packages.python.urisysedge.server.serve → uristepper-docker.packages.python.urisysedge.runtime.build_runtime
  uristepper-docker.packages.python.urisysedge.server.serve → uristepper-docker.packages.python.urisysedge.server.make_handler
  scripts.run_test_sessions._wait_health → scripts.run_test_sessions._http_json
  scripts.run_test_sessions._write_meta → scripts.run_test_sessions._read_meta
  scripts.run_test_sessions._write_meta → scripts.run_test_sessions._save_json
  scripts.run_test_sessions._finalize_session → scripts.run_test_sessions._now_iso
  scripts.run_test_sessions._finalize_session → scripts.run_test_sessions._write_meta
  scripts.run_test_sessions._docker_logs → scripts.run_test_sessions._run_cmd
  scripts.run_test_sessions.session_pytest_urirdp → scripts.run_test_sessions._now_iso
  scripts.run_test_sessions.session_pytest_urirdp → scripts.run_test_sessions._write_meta
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
