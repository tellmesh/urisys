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
- **version**: `0.1.66`
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
  version: 0.1.66;
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
# generated in 0.10s
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
  scripts.scan-browser-sessions.main
    CC=23  in:0  out:34  total:34
  scripts.test_sessions.util.finalize_session
    CC=5  in:21  out:13  total:34
  scripts.lenovo_remote_session.run_flow
    CC=14  in:1  out:33  total:34
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  scripts.run_test_sessions.session_automation_lab
    CC=13  in:1  out:31  total:32
  scripts.pack_registry.pack_specs
    CC=17  in:2  out:30  total:32
  src.urisys.init_setup.run_init
    CC=31  in:2  out:30  total:32
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  scripts.session_core.now_iso
    CC=1  in:29  out:2  total:31
  scripts.run_test_sessions.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
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
    verify_uri_control_edge  CC=5  out:8
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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.10s
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
  scripts.scan-browser-sessions.main
    CC=23  in:0  out:34  total:34
  scripts.test_sessions.util.finalize_session
    CC=5  in:21  out:13  total:34
  scripts.lenovo_remote_session.run_flow
    CC=14  in:1  out:33  total:34
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  scripts.run_test_sessions.session_automation_lab
    CC=13  in:1  out:31  total:32
  scripts.pack_registry.pack_specs
    CC=17  in:2  out:30  total:32
  src.urisys.init_setup.run_init
    CC=31  in:2  out:30  total:32
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  scripts.session_core.now_iso
    CC=1  in:29  out:2  total:31
  scripts.run_test_sessions.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
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
    verify_uri_control_edge  CC=5  out:8
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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 102f 11916L | python:49,shell:41,yaml:7,json:1,yml:1,toml:1,javascript:1 | 2026-06-17
# generated in 0.02s
# CC̅=4.7 | critical:13/366 | dups:0 | cycles:0

HEALTH[13]:
  🟡 CC    run_init CC=31 (limit:15)
  🟡 CC    compile CC=17 (limit:15)
  🟡 CC    main CC=23 (limit:15)
  🟡 CC    session_urirdp_real_docker CC=25 (limit:15)
  🟡 CC    _run_host_restart_and_wait_step CC=19 (limit:15)
  🟡 CC    _run_flows CC=22 (limit:15)
  🟡 CC    main CC=37 (limit:15)
  🟡 CC    step_ok CC=16 (limit:15)
  🟡 CC    expand_step_wheels CC=18 (limit:15)
  🟡 CC    main CC=28 (limit:15)
  🟡 CC    pack_specs CC=17 (limit:15)
  🟡 CC    load_flow_outcomes CC=15 (limit:15)
  🟡 CC    infer_steps CC=28 (limit:15)

REFACTOR[1]:
  1. split 13 high-CC methods  (CC>15)

PIPELINES[111]:
  [1] Src [main]: main → _doctor_main → run_doctor → _check_uricore_authentic → ...(2 more)
      PURITY: 100% pure
  [2] Src [main]: main → _cmd_uri → print_json → print
      PURITY: 100% pure
  [3] Src [__init__]: __init__
      PURITY: 100% pure
  [4] Src [run]: run → load_flow
      PURITY: 100% pure
  [5] Src [close]: close
      PURITY: 100% pure
  [6] Src [__init__]: __init__ → create_server → _send
      PURITY: 100% pure
  [7] Src [serve_forever]: serve_forever → print
      PURITY: 100% pure
  [8] Src [__init__]: __init__
      PURITY: 100% pure
  [9] Src [call]: call
      PURITY: 100% pure
  [10] Src [explain]: explain
      PURITY: 100% pure
  [11] Src [routes]: routes
      PURITY: 100% pure
  [12] Src [close]: close
      PURITY: 100% pure
  [13] Src [to_dict]: to_dict
      PURITY: 100% pure
  [14] Src [safe_identifier]: safe_identifier
      PURITY: 100% pure
  [15] Src [parse_meta]: parse_meta
      PURITY: 100% pure
  [16] Src [source_hash]: source_hash
      PURITY: 100% pure
  [17] Src [__init__]: __init__
      PURITY: 100% pure
  [18] Src [list_events]: list_events
      PURITY: 100% pure
  [19] Src [build_context]: build_context
      PURITY: 100% pure
  [20] Src [explain]: explain
      PURITY: 100% pure
  [21] Src [__init__]: __init__
      PURITY: 100% pure
  [22] Src [create_runtime]: create_runtime
      PURITY: 100% pure
  [23] Src [close]: close
      PURITY: 100% pure
  [24] Src [__exit__]: __exit__
      PURITY: 100% pure
  [25] Src [__init__]: __init__
      PURITY: 100% pure
  [26] Src [read_blocks]: read_blocks
      PURITY: 100% pure
  [27] Src [source_hash]: source_hash
      PURITY: 100% pure
  [28] Src [load_pack_block]: load_pack_block
      PURITY: 100% pure
  [29] Src [validate]: validate → validate_contract → _validate_contract_routes → scheme_from_uri
      PURITY: 100% pure
  [30] Src [_validate_pack]: _validate_pack
      PURITY: 100% pure
  [31] Src [compile]: compile
      PURITY: 100% pure
  [32] Src [_write_handler_modules]: _write_handler_modules
      PURITY: 100% pure
  [33] Src [manifest_path_for]: manifest_path_for
      PURITY: 100% pure
  [34] Src [run_tests]: run_tests
      PURITY: 100% pure
  [35] Src [_check_expectations]: _check_expectations
      PURITY: 100% pure
  [36] Src [_build_route]: _build_route
      PURITY: 100% pure
  [37] Src [_resolve_handler_ref]: _resolve_handler_ref
      PURITY: 100% pure
  [38] Src [_compile_manifest]: _compile_manifest
      PURITY: 100% pure
  [39] Src [_package_id]: _package_id
      PURITY: 100% pure
  [40] Src [_capabilities]: _capabilities
      PURITY: 100% pure
  [41] Src [_scheme]: _scheme
      PURITY: 100% pure
  [42] Src [_handler_blocks]: _handler_blocks
      PURITY: 100% pure
  [43] Src [_load_yaml_blocks]: _load_yaml_blocks
      PURITY: 100% pure
  [44] Src [_handler_id_from_ref]: _handler_id_from_ref
      PURITY: 100% pure
  [45] Src [_ensure_importable]: _ensure_importable
      PURITY: 100% pure
  [46] Src [call_http]: call_http
      PURITY: 100% pure
  [47] Src [__init__]: __init__
      PURITY: 100% pure
  [48] Src [_split_specs]: _split_specs
      PURITY: 100% pure
  [49] Src [_is_all]: _is_all
      PURITY: 100% pure
  [50] Src [parse_packs]: parse_packs
      PURITY: 100% pure

LAYERS:
  scripts/                        CC̄=5.1    ←in:32  →out:88  !! split
  │ !! lenovo_remote_session      795L  0C   25m  CC=37     ←0
  │ !! run_test_sessions          761L  0C   18m  CC=25     ←0
  │ !! pack_sync                  347L  0C   13m  CC=28     ←0
  │ lab_flows                  320L  0C    5m  CC=13     ←0
  │ !! session_core               276L  0C   16m  CC=18     ←6
  │ !! pack_registry              269L  1C    9m  CC=17     ←1
  │ util                       201L  0C   14m  CC=9      ←3
  │ !! scan-browser-sessions      199L  0C    6m  CC=23     ←0
  │ !! lab_checks                 188L  0C    9m  CC=15     ←1
  │ run-office-simulate-lenovo.sh   182L  0C    6m  CC=0.0    ←0
  │ lab_rdp                    180L  0C    8m  CC=11     ←1
  │ run-urisys-node-docker-e2e.sh   163L  0C    5m  CC=0.0    ←3
  │ expectations               153L  0C    9m  CC=11     ←1
  │ office-simulate-loop       146L  0C    5m  CC=10     ←1
  │ events                     138L  0C    5m  CC=14     ←1
  │ run-email-mailpit-e2e.sh   134L  0C    4m  CC=0.0    ←0
  │ run-office-simulate-e2e.sh   130L  0C    4m  CC=0.0    ←0
  │ deploy-lenovo-node.sh      130L  0C    5m  CC=0.0    ←0
  │ run_analysis               129L  0C    5m  CC=13     ←1
  │ session_markdown           120L  0C    8m  CC=7      ←1
  │ run-lenovo-office-linkedin.sh   118L  0C    3m  CC=0.0    ←0
  │ !! session                    115L  0C    5m  CC=28     ←2
  │ run-office-writer-e2e.sh   113L  0C    4m  CC=0.0    ←4
  │ __init__                   100L  0C    0m  CC=0.0    ←0
  │ remote-node-smoke.sh        99L  0C    2m  CC=0.0    ←0
  │ models                      86L  5C    0m  CC=0.0    ←0
  │ lenovo-node-session.sh      73L  0C    1m  CC=0.0    ←0
  │ validate-pypi-metadata.sh    62L  0C    2m  CC=0.0    ←0
  │ __init__                    61L  0C    0m  CC=0.0    ←0
  │ test-python-matrix.sh       58L  0C    1m  CC=0.0    ←0
  │ bootstrap-lenovo-local.sh    57L  0C    0m  CC=0.0    ←0
  │ paths.sh                    54L  0C    6m  CC=0.0    ←0
  │ validate-all-markpacts.sh    53L  0C    0m  CC=0.0    ←0
  │ publish-pypi-packs.sh       53L  0C    0m  CC=0.0    ←0
  │ ci-checkout-siblings.sh     51L  0C    1m  CC=0.0    ←0
  │ session_report              49L  0C    0m  CC=0.0    ←0
  │ run-nl-log-smoke.sh         43L  0C    1m  CC=0.0    ←9
  │ run_markdown                42L  0C    1m  CC=7      ←1
  │ cli                         41L  0C    1m  CC=4      ←0
  │ sync-vendored-pack.sh       38L  0C    0m  CC=0.0    ←0
  │ ci-install-siblings.sh      28L  0C    1m  CC=0.0    ←0
  │ run-smoke-all.sh            24L  0C    0m  CC=0.0    ←0
  │ util                        21L  0C    2m  CC=3      ←3
  │ run-lab-unit-ci.sh          21L  0C    0m  CC=0.0    ←0
  │ session_io                  19L  0C    1m  CC=2      ←2
  │ publish-urisys-node-release.sh    19L  0C    0m  CC=0.0    ←0
  │ sync-vendored-urisysedge.sh    17L  0C    0m  CC=0.0    ←0
  │ run-lab-nightly.sh          16L  0C    0m  CC=0.0    ←0
  │ run-lab-e2e.sh              14L  0C    0m  CC=0.0    ←0
  │ install-kvm-packs-editable.sh    13L  0C    0m  CC=0.0    ←0
  │ test-goal.sh                11L  0C    0m  CC=0.0    ←0
  │ run-urisys-node-docker-session.sh     6L  0C    0m  CC=0.0    ←0
  │
  src/                            CC̄=4.2    ←in:0  →out:0
  │ !! markpact_manager           412L  1C   22m  CC=17     ←0
  │ cli                        335L  0C   11m  CC=11     ←0
  │ doctor                     296L  1C   11m  CC=12     ←3
  │ !! init_setup                 262L  0C   11m  CC=31     ←2
  │ source_manager             218L  2C   12m  CC=11     ←0
  │ markpact_validation        156L  0C    6m  CC=14     ←1
  │ pack_manager               137L  1C   14m  CC=11     ←0
  │ uricore_install            130L  0C   11m  CC=6      ←2
  │ bootstrap                  116L  0C    5m  CC=8      ←0
  │ node_install               106L  0C    9m  CC=7      ←1
  │ markpact_models             92L  3C    5m  CC=4      ←1
  │ http_server                 79L  0C    3m  CC=3      ←1
  │ edge_install                78L  0C    6m  CC=7      ←2
  │ flow_controller             33L  1C    3m  CC=6      ←0
  │ uri_controller              33L  1C    5m  CC=3      ←0
  │ runtime_manager             30L  1C    5m  CC=2      ←0
  │ defaults                    28L  0C    0m  CC=0.0    ←0
  │ flow                        25L  0C    2m  CC=7      ←1
  │ route_manager               23L  1C    3m  CC=2      ←0
  │ server_controller           19L  1C    2m  CC=1      ←0
  │ policy_manager              18L  1C    1m  CC=2      ←0
  │ bridge_manager              14L  1C    1m  CC=3      ←0
  │ event_manager               13L  1C    2m  CC=1      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.0    ←in:0  →out:0
  │ app.js                      21L  0C    5m  CC=1      ←0
  │ browser-call.sh             12L  0C    0m  CC=0.0    ←0
  │ server-curl.sh               8L  0C    0m  CC=0.0    ←0
  │ call-uri.sh                  6L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml             1319L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  514L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             125L  0C    0m  CC=0.0    ←0
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
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    39L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    24L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     src/urisys/controllers/__init__.py        0L

COUPLING:
                                       scripts  scripts.test_sessions         scripts.report             src.urisys
                scripts                     ──                     88                    ←13                     ←8  hub
  scripts.test_sessions                     11                     ──                                                hub
         scripts.report                     13                                            ──                         !! fan-out
             src.urisys                      8                                                                   ──  !! fan-out
  CYCLES: none
  HUB: scripts/ (fan-in=32)
  HUB: scripts.test_sessions/ (fan-in=88)
  SMELL: scripts/ fan-out=88 → split needed
  SMELL: src.urisys/ fan-out=8 → split needed
  SMELL: scripts.test_sessions/ fan-out=11 → split needed
  SMELL: scripts.report/ fan-out=13 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 3 groups | 44f 5697L | 2026-06-17

SUMMARY:
  files_scanned: 44
  total_lines:   5697
  dup_groups:    3
  dup_fragments: 7
  saved_lines:   37
  scan_ms:       2451

HOTSPOTS[6] (files with most duplication):
  src/urisys/uricore_install.py  dup=18L  groups=2  frags=2  (0.3%)
  src/urisys/edge_install.py  dup=11L  groups=1  frags=1  (0.2%)
  src/urisys/node_install.py  dup=11L  groups=1  frags=1  (0.2%)
  scripts/report/run_analysis.py  dup=8L  groups=1  frags=1  (0.1%)
  scripts/report/session_io.py  dup=8L  groups=1  frags=1  (0.1%)
  src/urisys/doctor.py  dup=7L  groups=1  frags=1  (0.1%)

DUPLICATES[3] (ranked by impact):
  [3f18ae8c291ee1c9]   EXAC  pip_run  L=11 N=3 saved=22 sim=1.00
      src/urisys/edge_install.py:29-39  (pip_run)
      src/urisys/node_install.py:48-58  (pip_run)
      src/urisys/uricore_install.py:99-109  (pip_run)
  [bb100fda4da2fc0e]   STRU  write_run_analysis  L=8 N=2 saved=8 sim=1.00
      scripts/report/run_analysis.py:122-129  (write_run_analysis)
      scripts/report/session_io.py:12-19  (write_session_report)
  [487da026fcebd9df]   EXAC  _pkg_version  L=7 N=2 saved=7 sim=1.00
      src/urisys/doctor.py:23-29  (_pkg_version)
      src/urisys/uricore_install.py:38-44  (_pkg_version)

REFACTOR[3] (ranked by priority):
  [1] ○ extract_function   → src/urisys/utils/pip_run.py
      WHY: 3 occurrences of 11-line block across 3 files — saves 22 lines
      FILES: src/urisys/edge_install.py, src/urisys/node_install.py, src/urisys/uricore_install.py
  [2] ○ extract_function   → scripts/report/utils/write_run_analysis.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: scripts/report/run_analysis.py, scripts/report/session_io.py
  [3] ○ extract_function   → src/urisys/utils/_pkg_version.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: src/urisys/doctor.py, src/urisys/uricore_install.py

QUICK_WINS[3] (low risk, high savings — do first):
  [1] extract_function   saved=22L  → src/urisys/utils/pip_run.py
      FILES: edge_install.py, node_install.py, uricore_install.py
  [2] extract_function   saved=8L  → scripts/report/utils/write_run_analysis.py
      FILES: run_analysis.py, session_io.py
  [3] extract_function   saved=7L  → src/urisys/utils/_pkg_version.py
      FILES: doctor.py, uricore_install.py

EFFORT_ESTIMATE (total ≈ 1.2h):
  medium pip_run                             saved=22L  ~44min
  easy   write_run_analysis                  saved=8L  ~16min
  easy   _pkg_version                        saved=7L  ~14min

METRICS-TARGET:
  dup_groups:  3 → 0
  saved_lines: 37 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 150 func | 22f | 2026-06-17
# generated in 0.00s

NEXT[4] (ranked by impact):
  [1] !! SPLIT-FUNC      run_init  CC=31  fan=22
      WHY: CC=31 exceeds 15
      EFFORT: ~1h  IMPACT: 682

  [2] !  SPLIT-FUNC      MarkpactManager.compile  CC=17  fan=33
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 561

  [3] !! SPLIT           planfile.yaml
      WHY: 1319L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0

  [4] !! SPLIT           goal.yaml
      WHY: 514L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.2 → ≤2.9
  max-CC:      31 → ≤15
  god-modules: 2 → 0
  high-CC(≥15): 2 → ≤1
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
  prev CC̄=4.2 → now CC̄=4.2
```

## Intent

URI control system managers/controllers over separate uri* capability packs.
