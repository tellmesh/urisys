# urisys

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `urisys`
- **version**: `0.1.41`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(3), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: urisys;
  version: 0.1.41;
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
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
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
  src.urisys.init_setup.default_pip_specs → src.urisys.uricore_install.pip_spec
  src.urisys.init_setup.verify_uri_control → src.urisys.uricore_install.diagnose_uricore
  src.urisys.init_setup.verify_uri_control → src.urisys.uricore_install.wheel_url
  src.urisys.init_setup.write_env_file → src.urisys.init_setup.render_env_shell
  src.urisys.init_setup.run_init → src.urisys.init_setup.default_pip_specs
  src.urisys.init_setup.run_init → src.urisys.init_setup.profile_env
  src.urisys.init_setup.run_init → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.init_setup.run_init → src.urisys.uricore_install.repair_uricore
  src.urisys.node_install.wheel_url → src.urisys.node_install.github_owner
  src.urisys.node_install.wheel_url → src.urisys.node_install.github_version
  src.urisys.node_install.pip_spec → src.urisys.node_install.wheel_url
  src.urisys.node_install.diagnose_urisys_node → src.urisys.node_install.is_importable
  src.urisys.node_install.diagnose_urisys_node → src.urisys.node_install.pip_spec
  src.urisys.http_server.create_server → src.urisys.http_server._send
  src.urisys.http_server.create_server → src.urisys.http_server._read_json
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.load_flow
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.iter_steps
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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
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
  src.urisys.init_setup.default_pip_specs → src.urisys.uricore_install.pip_spec
  src.urisys.init_setup.verify_uri_control → src.urisys.uricore_install.diagnose_uricore
  src.urisys.init_setup.verify_uri_control → src.urisys.uricore_install.wheel_url
  src.urisys.init_setup.write_env_file → src.urisys.init_setup.render_env_shell
  src.urisys.init_setup.run_init → src.urisys.init_setup.default_pip_specs
  src.urisys.init_setup.run_init → src.urisys.init_setup.profile_env
  src.urisys.init_setup.run_init → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.init_setup.run_init → src.urisys.uricore_install.repair_uricore
  src.urisys.node_install.wheel_url → src.urisys.node_install.github_owner
  src.urisys.node_install.wheel_url → src.urisys.node_install.github_version
  src.urisys.node_install.pip_spec → src.urisys.node_install.wheel_url
  src.urisys.node_install.diagnose_urisys_node → src.urisys.node_install.is_importable
  src.urisys.node_install.diagnose_urisys_node → src.urisys.node_install.pip_spec
  src.urisys.http_server.create_server → src.urisys.http_server._send
  src.urisys.http_server.create_server → src.urisys.http_server._read_json
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.load_flow
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.iter_steps
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 204f 13691L | shell:65,python:50,yaml:42,json:14,yml:11,toml:7,javascript:2,txt:2,conf:1,gui:1 | 2026-06-17
# generated in 0.03s
# CC̅=4.4 | critical:16/341 | dups:0 | cycles:0

HEALTH[16]:
  🟡 CC    main CC=36 (limit:15)
  🟡 CC    run_init CC=41 (limit:15)
  🟡 CC    validate_contract CC=23 (limit:15)
  🟡 CC    validate_implementation CC=18 (limit:15)
  🟡 CC    compile CC=21 (limit:15)
  🟡 CC    run_tests CC=20 (limit:15)
  🟡 CC    _build_route CC=18 (limit:15)
  🟡 CC    parse_packs CC=15 (limit:15)
  🟡 CC    session_urirdp_real_docker CC=30 (limit:15)
  🟡 CC    session_automation_lab CC=16 (limit:15)
  🟡 CC    main CC=28 (limit:15)
  🟡 CC    pack_specs CC=17 (limit:15)
  🟡 CC    load_flow_outcomes CC=15 (limit:15)
  🟡 CC    infer_steps CC=20 (limit:15)
  🟡 CC    build_lab_runtime CC=17 (limit:15)
  🟡 CC    do_POST CC=23 (limit:15)

REFACTOR[1]:
  1. split 16 high-CC methods  (CC>15)

PIPELINES[128]:
  [1] Src [registry]: registry
      PURITY: 100% pure
  [2] Src [runtime]: runtime
      PURITY: 100% pure
  [3] Src [out]: out
      PURITY: 100% pure
  [4] Src [result]: result
      PURITY: 100% pure
  [5] Src [client]: client
      PURITY: 100% pure
  [6] Src [main]: main → _doctor_main → run_doctor → _check_uricore_authentic → ...(2 more)
      PURITY: 100% pure
  [7] Src [main]: main → build_parser → _add_runtime_flags
      PURITY: 100% pure
  [8] Src [__init__]: __init__
      PURITY: 100% pure
  [9] Src [run]: run → load_flow
      PURITY: 100% pure
  [10] Src [close]: close
      PURITY: 100% pure
  [11] Src [__init__]: __init__ → create_server → _send
      PURITY: 100% pure
  [12] Src [serve_forever]: serve_forever → print
      PURITY: 100% pure
  [13] Src [__init__]: __init__
      PURITY: 100% pure
  [14] Src [call]: call
      PURITY: 100% pure
  [15] Src [explain]: explain
      PURITY: 100% pure
  [16] Src [routes]: routes
      PURITY: 100% pure
  [17] Src [close]: close
      PURITY: 100% pure
  [18] Src [to_dict]: to_dict
      PURITY: 100% pure
  [19] Src [safe_identifier]: safe_identifier
      PURITY: 100% pure
  [20] Src [parse_meta]: parse_meta
      PURITY: 100% pure
  [21] Src [source_hash]: source_hash
      PURITY: 100% pure
  [22] Src [__init__]: __init__
      PURITY: 100% pure
  [23] Src [list_events]: list_events
      PURITY: 100% pure
  [24] Src [build_context]: build_context
      PURITY: 100% pure
  [25] Src [explain]: explain
      PURITY: 100% pure
  [26] Src [__init__]: __init__
      PURITY: 100% pure
  [27] Src [create_runtime]: create_runtime
      PURITY: 100% pure
  [28] Src [close]: close
      PURITY: 100% pure
  [29] Src [__exit__]: __exit__
      PURITY: 100% pure
  [30] Src [__init__]: __init__
      PURITY: 100% pure
  [31] Src [read_blocks]: read_blocks
      PURITY: 100% pure
  [32] Src [source_hash]: source_hash
      PURITY: 100% pure
  [33] Src [load_pack_block]: load_pack_block
      PURITY: 100% pure
  [34] Src [validate]: validate → validate_contract → scheme_from_uri
      PURITY: 100% pure
  [35] Src [_validate_pack]: _validate_pack
      PURITY: 100% pure
  [36] Src [compile]: compile
      PURITY: 100% pure
  [37] Src [manifest_path_for]: manifest_path_for
      PURITY: 100% pure
  [38] Src [run_tests]: run_tests
      PURITY: 100% pure
  [39] Src [_build_route]: _build_route
      PURITY: 100% pure
  [40] Src [_compile_manifest]: _compile_manifest
      PURITY: 100% pure
  [41] Src [_package_id]: _package_id
      PURITY: 100% pure
  [42] Src [_capabilities]: _capabilities
      PURITY: 100% pure
  [43] Src [_scheme]: _scheme
      PURITY: 100% pure
  [44] Src [_handler_blocks]: _handler_blocks
      PURITY: 100% pure
  [45] Src [_load_yaml_blocks]: _load_yaml_blocks
      PURITY: 100% pure
  [46] Src [_handler_id_from_ref]: _handler_id_from_ref
      PURITY: 100% pure
  [47] Src [_ensure_importable]: _ensure_importable
      PURITY: 100% pure
  [48] Src [call_http]: call_http
      PURITY: 100% pure
  [49] Src [__init__]: __init__
      PURITY: 100% pure
  [50] Src [_is_all]: _is_all
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.7    ←in:0  →out:0
  │ !! markpact_manager           401L  1C   19m  CC=21     ←0
  │ doctor                     288L  1C   11m  CC=11     ←3
  │ !! cli                        282L  0C    6m  CC=36     ←0
  │ !! init_setup                 236L  0C    8m  CC=41     ←2
  │ source_manager             224L  2C   11m  CC=11     ←0
  │ !! markpact_validation        140L  0C    3m  CC=23     ←1
  │ uricore_install            130L  0C   11m  CC=6      ←2
  │ !! pack_manager               128L  1C   13m  CC=15     ←0
  │ bootstrap                  111L  0C    5m  CC=8      ←0
  │ markpact_models             92L  3C    5m  CC=4      ←1
  │ http_server                 78L  0C    3m  CC=3      ←1
  │ node_install                52L  0C    6m  CC=3      ←1
  │ flow_controller             33L  1C    3m  CC=6      ←0
  │ uri_controller              33L  1C    5m  CC=3      ←0
  │ runtime_manager             30L  1C    5m  CC=2      ←0
  │ flow                        25L  0C    2m  CC=7      ←1
  │ route_manager               23L  1C    3m  CC=2      ←0
  │ defaults                    20L  0C    0m  CC=0.0    ←0
  │ server_controller           18L  1C    2m  CC=1      ←0
  │ policy_manager              18L  1C    1m  CC=2      ←0
  │ bridge_manager              14L  1C    1m  CC=3      ←0
  │ event_manager               13L  1C    2m  CC=1      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=4.7    ←in:28  →out:117  !! split
  │ !! run_test_sessions          782L  0C   14m  CC=30     ←0
  │ !! pack_sync                  347L  0C   13m  CC=28     ←0
  │ lab_flows                  319L  0C    5m  CC=13     ←0
  │ !! pack_registry              260L  1C    9m  CC=17     ←1
  │ util                       209L  0C   17m  CC=9      ←3
  │ !! lab_checks                 188L  0C    9m  CC=15     ←1
  │ run-office-simulate-lenovo.sh   182L  0C    6m  CC=0.0    ←0
  │ lab_rdp                    180L  0C    8m  CC=11     ←1
  │ run-urisys-node-docker-e2e.sh   162L  0C    5m  CC=0.0    ←3
  │ expectations               153L  0C    9m  CC=11     ←1
  │ office-simulate-loop       146L  0C    5m  CC=10     ←1
  │ events                     138L  0C    5m  CC=14     ←1
  │ run-email-mailpit-e2e.sh   133L  0C    4m  CC=0.0    ←0
  │ run-office-simulate-e2e.sh   129L  0C    4m  CC=0.0    ←0
  │ run_analysis               129L  0C    5m  CC=13     ←1
  │ session_markdown           120L  0C    8m  CC=7      ←1
  │ run-office-writer-e2e.sh   112L  0C    4m  CC=0.0    ←2
  │ !! session                    105L  0C    5m  CC=20     ←2
  │ remote-node-smoke.sh        99L  0C    2m  CC=0.0    ←0
  │ __init__                    98L  0C    0m  CC=0.0    ←0
  │ models                      86L  5C    0m  CC=0.0    ←0
  │ lenovo-node-session.sh      72L  0C    1m  CC=0.0    ←0
  │ deploy-lenovo-node.sh       71L  0C    2m  CC=0.0    ←0
  │ validate-pypi-metadata.sh    62L  0C    2m  CC=0.0    ←0
  │ __init__                    61L  0C    0m  CC=0.0    ←0
  │ test-python-matrix.sh       58L  0C    1m  CC=0.0    ←0
  │ paths.sh                    54L  0C    6m  CC=0.0    ←0
  │ validate-all-markpacts.sh    53L  0C    0m  CC=0.0    ←0
  │ publish-pypi-packs.sh       53L  0C    0m  CC=0.0    ←0
  │ ci-checkout-siblings.sh     51L  0C    1m  CC=0.0    ←0
  │ session_report              49L  0C    0m  CC=0.0    ←0
  │ run-nl-log-smoke.sh         43L  0C    1m  CC=0.0    ←9
  │ run_markdown                42L  0C    1m  CC=7      ←1
  │ cli                         41L  0C    1m  CC=4      ←0
  │ sync-vendored-pack.sh       38L  0C    0m  CC=0.0    ←0
  │ util                        29L  0C    4m  CC=3      ←5
  │ ci-install-siblings.sh      28L  0C    1m  CC=0.0    ←0
  │ run-smoke-all.sh            24L  0C    0m  CC=0.0    ←0
  │ run-lab-unit-ci.sh          20L  0C    0m  CC=0.0    ←0
  │ session_io                  19L  0C    1m  CC=2      ←2
  │ run-lab-nightly.sh          16L  0C    0m  CC=0.0    ←0
  │ sync-vendored-urisysedge.sh    16L  0C    0m  CC=0.0    ←0
  │ run-lab-e2e.sh              14L  0C    0m  CC=0.0    ←0
  │ install-kvm-packs-editable.sh    13L  0C    0m  CC=0.0    ←0
  │ test-goal.sh                11L  0C    0m  CC=0.0    ←0
  │ run-urisys-node-docker-session.sh     6L  0C    0m  CC=0.0    ←0
  │
  urisys-automation-lab/          CC̄=4.1    ←in:0  →out:0
  │ !! automation_lab_server      247L  1C    9m  CC=23     ←0
  │ flow_runner                169L  0C    7m  CC=13     ←1
  │ app.js                     131L  0C   17m  CC=2      ←0
  │ lab_uri_adapter            129L  1C    3m  CC=12     ←0
  │ docker-compose.lab.yml      66L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  43L  0C    0m  CC=0.0    ←0
  │ 10_full_maintenance_rdp.uri.flow.yaml    42L  0C    0m  CC=0.0    ←0
  │ 08_voice_command_to_kvm.uri.flow.yaml    40L  0C    0m  CC=0.0    ←0
  │ local-rdp.routes.yaml       32L  0C    0m  CC=0.0    ←0
  │ 09_webrtc_video_chat_rdp.uri.flow.yaml    29L  0C    0m  CC=0.0    ←0
  │ validate-flows.sh           28L  0C    0m  CC=0.0    ←0
  │ 05_fill_form_gui.uri.flow.yaml    27L  0C    0m  CC=0.0    ←0
  │ 07_edit_config_nano_tui.uri.flow.yaml    27L  0C    0m  CC=0.0    ←0
  │ 06_terminal_htop_tui.uri.flow.yaml    23L  0C    0m  CC=0.0    ←0
  │ 04_browser_download_file.uri.flow.yaml    22L  0C    0m  CC=0.0    ←0
  │ docker-up.sh                21L  0C    0m  CC=0.0    ←0
  │ docker-smoke.sh             20L  0C    0m  CC=0.0    ←0
  │ 03_open_browser_gui.uri.flow.yaml    19L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               18L  0C    0m  CC=0.0    ←0
  │ 02_update_system_tui.uri.flow.yaml    15L  0C    0m  CC=0.0    ←0
  │ run-lab.sh                  13L  0C    0m  CC=0.0    ←0
  │ 01_install_browser.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ docker-logs.sh               6L  0C    0m  CC=0.0    ←0
  │ docker-down.sh               6L  0C    0m  CC=0.0    ←0
  │ static_server                6L  0C    0m  CC=0.0    ←0
  │
  urikvm-docker/                  CC̄=4.0    ←in:0  →out:0
  │ real_pipeline               95L  0C    4m  CC=14     ←1
  │ pyproject.toml              66L  0C    0m  CC=0.0    ←0
  │ test-real.sh                47L  0C    1m  CC=0.0    ←0
  │ Dockerfile                  27L  0C    0m  CC=0.0    ←0
  │ kvm-profile.json            26L  0C    0m  CC=0.0    ←0
  │ kvm-profile.real.json       24L  0C    0m  CC=0.0    ←0
  │ kvm-click-ok.uri.flow.yaml    20L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ call-http.sh                 5L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.0    ←in:0  →out:0
  │ app.js                      21L  0C    5m  CC=1      ←0
  │ browser-call.sh             12L  0C    0m  CC=0.0    ←0
  │ server-curl.sh               8L  0C    0m  CC=0.0    ←0
  │ call-uri.sh                  6L  0C    0m  CC=0.0    ←0
  │
  urirdp-docker/                  CC̄=0.0    ←in:0  →out:0
  │ bootstrap-rdp-session.sh   111L  0C    7m  CC=0.0    ←0
  │ test-real-docker.sh         63L  0C    1m  CC=0.0    ←0
  │ pyproject.toml              54L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  51L  0C    0m  CC=0.0    ←0
  │ docker-compose.rdp-e2e.yml    41L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-profile.real.json    39L  0C    0m  CC=0.0    ←0
  │ supervisord.conf            35L  0C    0m  CC=0.0    ←0
  │ env-policy.yaml             31L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-profile.json        30L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               25L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          24L  0C    0m  CC=0.0    ←0
  │ Makefile                    20L  0C    0m  CC=0.0    ←0
  │ test-docker.sh              17L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-smoke.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ real-rdp-click-text.uri.flow.yaml    14L  0C    0m  CC=0.0    ←0
  │ test-rdp-real.sh            12L  0C    0m  CC=0.0    ←0
  │ call-http.sh                10L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ startwm.sh                   6L  0C    0m  CC=0.0    ←0
  │
  urisys-node/                    CC̄=0.0    ←in:0  →out:0
  │ pyproject.toml             108L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               63L  0C    3m  CC=0.0    ←0
  │ node-profile.lenovo.json    63L  0C    0m  CC=0.0    ←0
  │ Dockerfile.gui              58L  0C    0m  CC=0.0    ←0
  │ route-map.lenovo.yaml       36L  0C    0m  CC=0.0    ←0
  │ docker-compose.gui.yml      33L  0C    0m  CC=0.0    ←0
  │ node-profile.docker.json    33L  0C    0m  CC=0.0    ←0
  │ node-profile.json           32L  0C    0m  CC=0.0    ←0
  │ bootstrap-kvm-github.uri.flow.yaml    28L  0C    0m  CC=0.0    ←0
  │ route-map.host.yaml         23L  0C    0m  CC=0.0    ←0
  │ route-map.master.yaml       19L  0C    0m  CC=0.0    ←0
  │ nodes.registry.json         18L  0C    0m  CC=0.0    ←0
  │ bootstrap-kvm-pypi.uri.flow.yaml    18L  0C    0m  CC=0.0    ←0
  │ remote-probe.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ install-linux.sh            16L  0C    0m  CC=0.0    ←0
  │ route-map.slave.yaml        14L  0C    0m  CC=0.0    ←0
  │ slave-kvm-demo.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ screen-capture-mss.uri.flow.yaml    12L  0C    0m  CC=0.0    ←0
  │ nodes.registry.host.json     9L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml             1319L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  514L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             126L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                94L  0C    0m  CC=0.0    ←0
  │ project.sh                  63L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  schemas/                        CC̄=0.0    ←in:0  →out:0
  │ uripack-markpact.schema.json    47L  0C    0m  CC=0.0    ←0
  │
  local-lab/                      CC̄=0.0    ←in:0  →out:0
  │ 02-build-publish.sh        132L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          72L  0C    0m  CC=0.0    ←0
  │ 06-register-release.sh      62L  0C    0m  CC=0.0    ←0
  │ 04-smoke.sh                 35L  0C    0m  CC=0.0    ←0
  │ run-all.sh                  25L  0C    0m  CC=0.0    ←0
  │ 01-validate-markpact.sh     24L  0C    0m  CC=0.0    ←0
  │ 05-resolve-from-url.sh      23L  0C    0m  CC=0.0    ←0
  │ install-urisys.sh           20L  0C    0m  CC=0.0    ←0
  │ 03-resolve-run.sh           16L  0C    0m  CC=0.0    ←0
  │ node-profile.local.yaml     11L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  11L  0C    0m  CC=0.0    ←0
  │
  urimail-docker/                 CC̄=0.0    ←in:0  →out:0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │
  uristepper-docker/              CC̄=0.0    ←in:0  →out:0
  │ device-profile.json         61L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              43L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          35L  0C    0m  CC=0.0    ←0
  │ move-test.uri.flow.yaml     35L  0C    0m  CC=0.0    ←0
  │ device-profile.rpi3.example.json    33L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  26L  0C    0m  CC=0.0    ←0
  │ Makefile                    25L  0C    0m  CC=0.0    ←0
  │ docker-compose.rpi3.example.yml    21L  0C    0m  CC=0.0    ←0
  │ safety-denied.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ call-http.sh                10L  0C    0m  CC=0.0    ←0
  │ test-local.sh               10L  0C    0m  CC=0.0    ←0
  │ test-docker.sh               7L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    39L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    24L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  uribrowser-docker/              CC̄=0.0    ←in:0  →out:0
  │ pyproject.toml              46L  0C    0m  CC=0.0    ←0
  │ test-real.sh                28L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  17L  0C    0m  CC=0.0    ←0
  │ browser-demo.uri.flow.yaml    14L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ browser-profile.json        10L  0C    0m  CC=0.0    ←0
  │ browser-profile.real.json     9L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │
  urienv-docker/                  CC̄=0.0    ←in:0  →out:0
  │ docker-compose.yml          52L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  36L  0C    0m  CC=0.0    ←0
  │ env-policy.yaml             36L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              22L  0C    0m  CC=0.0    ←0
  │ mutate-process-env.uri.flow.yaml    16L  0C    0m  CC=0.0    ←0
  │ startup-env-check.uri.flow.yaml    15L  0C    0m  CC=0.0    ←0
  │ local-test.sh               10L  0C    0m  CC=0.0    ←0
  │ test-docker.sh               4L  0C    0m  CC=0.0    ←0
  │ smtp_password.txt            1L  0C    0m  CC=0.0    ←0
  │ markpact_token.txt           1L  0C    0m  CC=0.0    ←0
  │
  flows/                          CC̄=0.0    ←in:0  →out:0
  │ email-mailpit.uri.flow.yaml    36L  0C    0m  CC=0.0    ←0
  │ browser-form-vql.uri.flow.yaml    33L  0C    0m  CC=0.0    ←0
  │ office-writer.uri.flow.yaml    31L  0C    0m  CC=0.0    ←0
  │ office-simulate-tick.uri.flow.yaml    27L  0C    0m  CC=0.0    ←0
  │ device-maintenance.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     src/urisys/controllers/__init__.py        0L

COUPLING:
                                                     scripts         scripts.test_sessions                scripts.report                    src.urisys  urisys-automation-lab.server         urikvm-docker.scripts
                       scripts                            ──                            90                            27                            ←7                            ←6                            ←2  hub
         scripts.test_sessions                             7                            ──                             2                                                                                            hub
                scripts.report                             6                            ←2                            ──                                                                                            hub
                    src.urisys                             7                                                                                        ──                                                           1  !! fan-out
  urisys-automation-lab.server                             6                                                                                                                      ──                              
         urikvm-docker.scripts                             2                                                                                        ←1                                                          ──
  CYCLES: none
  HUB: scripts.test_sessions/ (fan-in=90)
  HUB: scripts/ (fan-in=28)
  HUB: scripts.report/ (fan-in=29)
  SMELL: scripts.test_sessions/ fan-out=9 → split needed
  SMELL: scripts/ fan-out=117 → split needed
  SMELL: src.urisys/ fan-out=8 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 2 groups | 45f 4798L | 2026-06-17

SUMMARY:
  files_scanned: 45
  total_lines:   4798
  dup_groups:    2
  dup_fragments: 4
  saved_lines:   15
  scan_ms:       2645

HOTSPOTS[4] (files with most duplication):
  scripts/report/run_analysis.py  dup=8L  groups=1  frags=1  (0.2%)
  scripts/report/session_io.py  dup=8L  groups=1  frags=1  (0.2%)
  src/urisys/doctor.py  dup=7L  groups=1  frags=1  (0.1%)
  src/urisys/uricore_install.py  dup=7L  groups=1  frags=1  (0.1%)

DUPLICATES[2] (ranked by impact):
  [bb100fda4da2fc0e]   STRU  write_run_analysis  L=8 N=2 saved=8 sim=1.00
      scripts/report/run_analysis.py:122-129  (write_run_analysis)
      scripts/report/session_io.py:12-19  (write_session_report)
  [487da026fcebd9df]   EXAC  _pkg_version  L=7 N=2 saved=7 sim=1.00
      src/urisys/doctor.py:22-28  (_pkg_version)
      src/urisys/uricore_install.py:38-44  (_pkg_version)

REFACTOR[2] (ranked by priority):
  [1] ○ extract_function   → scripts/report/utils/write_run_analysis.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: scripts/report/run_analysis.py, scripts/report/session_io.py
  [2] ○ extract_function   → src/urisys/utils/_pkg_version.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: src/urisys/doctor.py, src/urisys/uricore_install.py

QUICK_WINS[2] (low risk, high savings — do first):
  [1] extract_function   saved=8L  → scripts/report/utils/write_run_analysis.py
      FILES: run_analysis.py, session_io.py
  [2] extract_function   saved=7L  → src/urisys/utils/_pkg_version.py
      FILES: doctor.py, uricore_install.py

EFFORT_ESTIMATE (total ≈ 0.5h):
  easy   write_run_analysis                  saved=8L  ~16min
  easy   _pkg_version                        saved=7L  ~14min

METRICS-TARGET:
  dup_groups:  2 → 0
  saved_lines: 15 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 171 func | 27f | 2026-06-17
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT-FUNC      main  CC=36  fan=36
      WHY: CC=36 exceeds 15
      EFFORT: ~1h  IMPACT: 1296

  [2] !! SPLIT-FUNC      run_init  CC=41  fan=25
      WHY: CC=41 exceeds 15
      EFFORT: ~1h  IMPACT: 1025

  [3] !  SPLIT-FUNC      MarkpactManager.compile  CC=21  fan=34
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 714

  [4] !  SPLIT-FUNC      MarkpactManager.run_tests  CC=20  fan=21
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 420

  [5] !  SPLIT-FUNC      build_lab_runtime  CC=17  fan=19
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 323

  [6] !  SPLIT-FUNC      LabHandler.do_POST  CC=23  fan=11
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 253

  [7] !  SPLIT-FUNC      validate_contract  CC=23  fan=10
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 230

  [8] !  SPLIT-FUNC      MarkpactManager._build_route  CC=18  fan=11
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 198

  [9] !  SPLIT-FUNC      validate_implementation  CC=18  fan=10
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 180

  [10] !! SPLIT           planfile.yaml
      WHY: 1319L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.3 → ≤3.0
  max-CC:      41 → ≤20
  god-modules: 2 → 0
  high-CC(≥15): 10 → ≤5
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=4.3 → now CC̄=4.3
```

## Intent

URI control system managers/controllers over separate uri* capability packs.
