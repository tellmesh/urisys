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
- **version**: `0.1.31`
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
  version: 0.1.31;
}

dependencies {
  runtime: "uricore>=0.1.2, PyYAML>=6.0, urisysedge>=0.1.0";
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
interface[type="cli"] page[name="urisys-node"] {
  entry: urisysnode.cli:main;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK, URISYS_MIN_VERSION, URISYS_NODE_HOST, URISYS_NODE_PORT, URISYS_NODE_CONFIG, WAYLAND_DISPLAY;
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
uricore>=0.1.2
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

*405 nodes · 500 edges · 77 modules · CC̄=4.3*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `make_handler` *(in urisys-node.packages.python.urisysnode.serve)* | 2 | 1 | 77 | **78** |
| `print` *(in scripts.run-nl-log-smoke)* | 0 | 68 | 0 | **68** |
| `run_cmd` *(in scripts.test_sessions.util)* | 6 | 51 | 12 | **63** |
| `main` *(in src.urisys.cli)* | 28 ⚠ | 0 | 57 | **57** |
| `build_parser` *(in src.urisys.cli)* | 1 | 1 | 50 | **51** |
| `make_handler` *(in uristepper-docker.packages.python.uristepperedge.server)* | 1 | 1 | 43 | **44** |
| `run_flow_file` *(in urisys-automation-lab.server.flow_runner)* | 13 ⚠ | 1 | 40 | **41** |
| `_cfg` *(in urienv-docker.packages.python.urienv.src.urienv.handlers)* | 7 | 9 | 29 | **38** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.20s
# nodes: 405 | edges: 500 | modules: 77
# CC̄=4.3

HUBS[20]:
  urisys-node.packages.python.urisysnode.serve.make_handler
    CC=2  in:1  out:77  total:78
  scripts.run-nl-log-smoke.print
    CC=0  in:68  out:0  total:68
  scripts.test_sessions.util.run_cmd
    CC=6  in:51  out:12  total:63
  src.urisys.cli.main
    CC=28  in:0  out:57  total:57
  src.urisys.cli.build_parser
    CC=1  in:1  out:50  total:51
  uristepper-docker.packages.python.uristepperedge.server.make_handler
    CC=1  in:1  out:43  total:44
  urisys-automation-lab.server.flow_runner.run_flow_file
    CC=13  in:1  out:40  total:41
  urienv-docker.packages.python.urienv.src.urienv.handlers._cfg
    CC=7  in:9  out:29  total:38
  urikvm-docker.packages.python.urihim.handlers.mouse_scroll
    CC=18  in:0  out:37  total:37
  urienv-docker.packages.python.urisysedge.src.urisysedge.server.serve
    CC=1  in:0  out:36  total:36
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  urikvm-docker.packages.python.urihim.handlers.mouse_click
    CC=17  in:0  out:34  total:34
  scripts.test_sessions.util.finalize_session
    CC=5  in:21  out:13  total:34
  urikvm-docker.packages.python.urillm.handlers.text_plan
    CC=24  in:0  out:33  total:33
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  urirdp-docker.packages.python.urirdp_browser.handlers.open_page
    CC=15  in:0  out:33  total:33
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  packages.python.urisysedge.env.resolve_env_var
    CC=11  in:23  out:9  total:32
  urirdp-docker.packages.python.urirdp_llm.handlers.analyze
    CC=18  in:0  out:31  total:31
  urisys-node.packages.python.urisysnode.serve.call_uri
    CC=20  in:1  out:29  total:30

MODULES:
  packages.python.urisysedge.env  [7 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    is_secret_env  CC=1  out:1
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  packages.python.urisysedge.runtime  [7 funcs]
    tail  CC=4  out:5
    call  CC=10  out:23
    load_json  CC=3  out:5
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  scripts.office-simulate-loop  [5 funcs]
    call_uri  CC=4  out:11
    llm_tick  CC=7  out:18
    main  CC=10  out:12
    parse_args  CC=1  out:8
    rules_tick  CC=3  out:8
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
  scripts.report.util  [2 funcs]
    now_iso  CC=1  out:3
    read_json  CC=3  out:3
  scripts.run-nl-log-smoke  [1 funcs]
    print  CC=0  out:0
  scripts.run-office-simulate-e2e  [1 funcs]
    wait_health  CC=0  out:0
  scripts.run-office-simulate-lenovo  [1 funcs]
    save_json  CC=0  out:0
  scripts.run-urisys-node-docker-e2e  [2 funcs]
    http_json  CC=0  out:0
    remote_call  CC=0  out:0
  scripts.run_test_sessions  [1 funcs]
    session_pytest_urirdp  CC=3  out:5
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
  scripts.test_sessions.util  [13 funcs]
    compose_cmd  CC=4  out:4
    copy_container_file  CC=2  out:4
    docker_logs  CC=3  out:3
    file_md5  CC=2  out:4
    finalize_session  CC=5  out:13
    http_json  CC=9  out:18
    now_iso  CC=1  out:3
    read_meta  CC=3  out:3
    run_cmd  CC=6  out:12
    save_json  CC=1  out:3
  src.urisys.cli  [5 funcs]
    _add_runtime_flags  CC=1  out:4
    build_parser  CC=1  out:50
    main  CC=28  out:57
    print_json  CC=1  out:2
    resolve_markpact_source  CC=2  out:3
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [2 funcs]
    __init__  CC=1  out:1
    serve_forever  CC=1  out:3
  src.urisys.doctor  [9 funcs]
    _check_cli_path  CC=3  out:6
    _check_import  CC=5  out:12
    _check_min_version  CC=6  out:5
    _check_python  CC=3  out:3
    _check_wayland_him  CC=3  out:4
    _parse_version  CC=7  out:6
    _pkg_version  CC=2  out:1
    _version_lt  CC=2  out:2
    run_doctor  CC=10  out:14
  src.urisys.flow  [2 funcs]
    iter_steps  CC=7  out:8
    load_flow  CC=3  out:5
  src.urisys.http_server  [3 funcs]
    _read_json  CC=3  out:5
    _send  CC=1  out:12
    create_server  CC=1  out:31
  src.urisys.managers.pack_manager  [1 funcs]
    manifest_paths  CC=9  out:20
  uribrowser-docker.packages.python.uribrowserdocker.handlers  [6 funcs]
    _profile  CC=1  out:2
    _session_state  CC=1  out:5
    get_dom  CC=1  out:4
    open_page  CC=11  out:27
    status  CC=1  out:7
    submit_form  CC=8  out:19
  uribrowser-docker.packages.python.uribrowseredge.cli  [1 funcs]
    build_runtime  CC=2  out:7
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
  urikvm-docker.packages.python.urihim.handlers  [16 funcs]
    _driver  CC=7  out:9
    _pyautogui  CC=3  out:3
    _real_allowed  CC=2  out:3
    _run_xdotool  CC=5  out:9
    _run_ydotool  CC=3  out:5
    _state  CC=1  out:2
    _wayland_session  CC=1  out:2
    _xdotool_available  CC=2  out:3
    _ydotool_available  CC=1  out:1
    _ydotool_key_sequence  CC=9  out:13
  urikvm-docker.packages.python.urikvm.handlers  [4 funcs]
    _profile  CC=1  out:2
    _store_screenshot  CC=1  out:4
    monitor_list  CC=2  out:4
    screenshot  CC=5  out:18
  urikvm-docker.packages.python.urikvmedge.cli  [1 funcs]
    build_runtime  CC=6  out:11
  urikvm-docker.packages.python.urillm.handlers  [24 funcs]
    _analyze_litellm  CC=6  out:11
    _analyze_openai  CC=10  out:13
    _box_center  CC=1  out:4
    _click_box  CC=1  out:2
    _driver  CC=1  out:2
    _env  CC=3  out:6
    _find_goal_box  CC=6  out:2
    _find_target_box  CC=6  out:2
    _goal_text  CC=4  out:4
    _heuristic_analyze  CC=8  out:17
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
  urirdp-docker.packages.python.urirdp.handlers  [7 funcs]
    _dismiss_stale_targets  CC=10  out:11
    _service_status  CC=4  out:4
    dismiss_target  CC=3  out:4
    display  CC=2  out:4
    display_status  CC=7  out:12
    prepare_target  CC=6  out:15
    status  CC=1  out:9
  urirdp-docker.packages.python.urirdp_browser.handlers  [4 funcs]
    _chromium_binary  CC=4  out:3
    _profile  CC=1  out:2
    _session_state  CC=1  out:5
    open_page  CC=15  out:33
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
  urirdp-docker.packages.python.urirdp_llm.handlers  [17 funcs]
    _config  CC=2  out:1
    _decide_litellm  CC=3  out:5
    _decide_messages  CC=2  out:2
    _decide_openai  CC=3  out:2
    _env  CC=3  out:6
    _heuristic  CC=5  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=6  out:7
    _match_transcript  CC=4  out:3
    _openai_compatible_chat  CC=1  out:9
  urirdp-docker.packages.python.urirdp_ocr.handlers  [5 funcs]
    _mock_ocr  CC=1  out:0
    _parse_tesseract_tsv  CC=7  out:19
    _tesseract_ocr  CC=9  out:23
    image_text  CC=6  out:8
    latest_text  CC=2  out:5
  urirdp-docker.packages.python.urirdp_shell.handlers  [3 funcs]
    _detect_display  CC=5  out:6
    _mock  CC=2  out:2
    shell_run  CC=16  out:18
  urirdp-docker.packages.python.urirdpedge.cli  [1 funcs]
    build_runtime  CC=10  out:16
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
  uristepper-docker.packages.python.uristepperedge.cli  [7 funcs]
    _json_arg  CC=3  out:5
    cmd_call  CC=4  out:7
    cmd_events  CC=1  out:4
    cmd_explain  CC=1  out:4
    cmd_flow  CC=12  out:22
    cmd_routes  CC=1  out:4
    cmd_serve  CC=1  out:1
  uristepper-docker.packages.python.uristepperedge.runtime  [2 funcs]
    build_runtime  CC=6  out:14
    load_json  CC=1  out:3
  uristepper-docker.packages.python.uristepperedge.server  [2 funcs]
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
  urisys-node.packages.python.uriscreen.backends  [11 funcs]
    _http_json  CC=3  out:7
    capture_portal  CC=2  out:4
    capture_vdisplay  CC=8  out:15
    capture_with_fallback  CC=13  out:12
    is_black_png  CC=5  out:6
    is_wayland  CC=1  out:1
    resolve_backend  CC=7  out:9
    session_type  CC=2  out:3
    vdisplay_agent_up  CC=2  out:4
    vdisplay_agent_url  CC=1  out:2
  urisys-node.packages.python.uriscreen.handlers  [8 funcs]
    _backend  CC=2  out:3
    _monitor_index  CC=6  out:9
    _output_dir  CC=2  out:5
    _screen_cfg  CC=1  out:2
    _store_latest  CC=1  out:1
    capture  CC=5  out:21
    capture_loop  CC=4  out:10
    frame  CC=1  out:5
  urisys-node.packages.python.uriscreen.portal_capture  [2 funcs]
    _portal_python  CC=6  out:5
    capture_portal_png  CC=8  out:14
  urisys-node.packages.python.urishell.handlers  [3 funcs]
    _detect_display  CC=5  out:6
    _mock  CC=2  out:2
    shell_run  CC=16  out:18
  urisys-node.packages.python.urisysnode.artifact_resolver  [19 funcs]
    _auth_opener  CC=4  out:11
    _contract_yaml_block  CC=6  out:6
    contract_spec_from_release  CC=2  out:4
    contract_url_from_release  CC=6  out:8
    docker_pull  CC=4  out:4
    docker_run_worker  CC=3  out:4
    fetch_json  CC=1  out:6
    fetch_release  CC=5  out:11
    fetch_text  CC=1  out:5
    is_url  CC=1  out:1
  urisys-node.packages.python.urisysnode.client  [2 funcs]
    call_via_route_map  CC=6  out:14
    remote_call  CC=3  out:8
  urisys-node.packages.python.urisysnode.display_bootstrap  [7 funcs]
    _agent_up  CC=2  out:2
    _agent_url  CC=1  out:2
    _ensure_session_env  CC=5  out:7
    _screencast_ready  CC=4  out:9
    _start_agent  CC=4  out:9
    _start_screencast  CC=5  out:7
    bootstrap_wayland_capture  CC=7  out:17
  urisys-node.packages.python.urisysnode.forward  [1 funcs]
    forward_call  CC=9  out:8
  urisys-node.packages.python.urisysnode.forward_config  [6 funcs]
    _normalize_entry  CC=11  out:13
    _normalize_release_entry  CC=11  out:15
    load_forward_entries  CC=15  out:20
    load_release_forward_entries  CC=11  out:12
    wire_forward_packs  CC=2  out:2
    wire_release_forward_packs  CC=3  out:4
  urisys-node.packages.python.urisysnode.handlers  [7 funcs]
    command_indicator_off  CC=1  out:2
    command_indicator_on  CC=1  out:4
    command_install_pack  CC=6  out:13
    command_register_forward  CC=7  out:12
    query_health  CC=1  out:2
    query_identity  CC=2  out:8
    query_packs  CC=2  out:7
  urisys-node.packages.python.urisysnode.identity  [12 funcs]
    _data_dir  CC=1  out:3
    _hostname  CC=1  out:1
    _identity_path  CC=1  out:1
    _pairing_path  CC=1  out:1
    enroll  CC=3  out:6
    health_payload  CC=15  out:22
    load_identity  CC=4  out:15
    load_pairing  CC=3  out:5
    require_paired  CC=4  out:5
    save_identity  CC=1  out:3
  urisys-node.packages.python.urisysnode.pack_resolver  [16 funcs]
    _pip_install  CC=3  out:2
    auto_install_enabled  CC=1  out:1
    ensure_pack_pypi  CC=3  out:3
    ensure_pip_specs  CC=4  out:2
    ensure_real_deps  CC=1  out:2
    github_owner  CC=1  out:2
    github_wheel_url  CC=4  out:6
    github_wheel_urls  CC=5  out:4
    import_pack_module  CC=1  out:2
    pack_for_scheme  CC=1  out:1
  urisys-node.packages.python.urisysnode.release_verify  [4 funcs]
    _ed25519_verify  CC=3  out:5
    canonical_digest  CC=3  out:5
    signature_required  CC=3  out:2
    verify_release  CC=14  out:15
  urisys-node.packages.python.urisysnode.router  [5 funcs]
    _match_pattern  CC=1  out:4
    load_route_map  CC=3  out:4
    node_endpoint  CC=5  out:6
    resolve_remote_route  CC=5  out:3
    rewrite_uri_for_slave  CC=6  out:5
  urisys-node.packages.python.urisysnode.serve  [11 funcs]
    _extend_pack_paths  CC=4  out:7
    _register_pack  CC=8  out:13
    _release_forward_spec  CC=11  out:8
    build_runtime  CC=13  out:28
    call_uri  CC=20  out:29
    ensure_pack_for_uri  CC=3  out:6
    hotload_release_pack  CC=14  out:17
    load_pack_into_runtime  CC=23  out:23
    make_handler  CC=2  out:77
    register_forward_pack  CC=13  out:8

EDGES:
  packages.python.urisysedge.runtime.Runtime.call → packages.python.urisysedge.env.load_env_policy
  packages.python.urisysedge.runtime.run_flow → packages.python.urisysedge.runtime.load_yaml_flow
  packages.python.urisysedge.runtime.serve → scripts.run-nl-log-smoke.print
  packages.python.urisysedge.runtime.serve → packages.python.urisysedge.runtime.make_handler
  packages.python.urisysedge.env.load_urisys_env → packages.python.urisysedge.env._urisys_root
  packages.python.urisysedge.env._env_policy_candidates → packages.python.urisysedge.env._urisys_root
  packages.python.urisysedge.env.load_env_policy → packages.python.urisysedge.env._env_policy_candidates
  packages.python.urisysedge.env.resolve_env_var → packages.python.urisysedge.env._env_config
  packages.python.urisysedge.env.resolve_env_var → packages.python.urisysedge.env.load_env_policy
  packages.python.urisysedge.env.resolve_env_var → urienv-docker.packages.python.urienv.src.urienv.handlers.secret_value
  packages.python.urisysedge.env.resolve_env_var → urienv-docker.packages.python.urienv.src.urienv.handlers.var_value
  src.urisys.cli.print_json → scripts.run-nl-log-smoke.print
  src.urisys.cli.build_parser → src.urisys.cli._add_runtime_flags
  src.urisys.cli.main → src.urisys.cli.build_parser
  src.urisys.cli.main → src.urisys.cli.resolve_markpact_source
  src.urisys.cli.main → src.urisys.doctor.run_doctor
  src.urisys.cli.main → src.urisys.cli.print_json
  src.urisys.cli.main → scripts.run-nl-log-smoke.print
  src.urisys.doctor._version_lt → src.urisys.doctor._parse_version
  src.urisys.doctor._check_import → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._version_lt
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_min_version
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_wayland_him
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_python
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_cli_path
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_import
  src.urisys.http_server.create_server → src.urisys.http_server._send
  src.urisys.http_server.create_server → src.urisys.http_server._read_json
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.load_flow
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.iter_steps
  src.urisys.controllers.server_controller.ServerController.__init__ → src.urisys.http_server.create_server
  src.urisys.controllers.server_controller.ServerController.serve_forever → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.runtime.build_runtime → uristepper-docker.packages.python.uristepperedge.runtime.load_json
  uristepper-docker.packages.python.uristepperedge.cli.cmd_call → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_call → uristepper-docker.packages.python.uristepperedge.cli._json_arg
  uristepper-docker.packages.python.uristepperedge.cli.cmd_call → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_explain → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_explain → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_routes → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_routes → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_events → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_events → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_flow → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_flow → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_serve → packages.python.urisysedge.runtime.serve
  uristepper-docker.packages.python.uristepperedge.server.serve → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.server.serve → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.server.serve → uristepper-docker.packages.python.uristepperedge.server.make_handler
  uristepper-docker.packages.python.uristepper.handlers._driver → uristepper-docker.packages.python.uristepper.drivers.make_driver
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
# generated in 0.20s
# nodes: 405 | edges: 500 | modules: 77
# CC̄=4.3

HUBS[20]:
  urisys-node.packages.python.urisysnode.serve.make_handler
    CC=2  in:1  out:77  total:78
  scripts.run-nl-log-smoke.print
    CC=0  in:68  out:0  total:68
  scripts.test_sessions.util.run_cmd
    CC=6  in:51  out:12  total:63
  src.urisys.cli.main
    CC=28  in:0  out:57  total:57
  src.urisys.cli.build_parser
    CC=1  in:1  out:50  total:51
  uristepper-docker.packages.python.uristepperedge.server.make_handler
    CC=1  in:1  out:43  total:44
  urisys-automation-lab.server.flow_runner.run_flow_file
    CC=13  in:1  out:40  total:41
  urienv-docker.packages.python.urienv.src.urienv.handlers._cfg
    CC=7  in:9  out:29  total:38
  urikvm-docker.packages.python.urihim.handlers.mouse_scroll
    CC=18  in:0  out:37  total:37
  urienv-docker.packages.python.urisysedge.src.urisysedge.server.serve
    CC=1  in:0  out:36  total:36
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  urikvm-docker.packages.python.urihim.handlers.mouse_click
    CC=17  in:0  out:34  total:34
  scripts.test_sessions.util.finalize_session
    CC=5  in:21  out:13  total:34
  urikvm-docker.packages.python.urillm.handlers.text_plan
    CC=24  in:0  out:33  total:33
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  urirdp-docker.packages.python.urirdp_browser.handlers.open_page
    CC=15  in:0  out:33  total:33
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  packages.python.urisysedge.env.resolve_env_var
    CC=11  in:23  out:9  total:32
  urirdp-docker.packages.python.urirdp_llm.handlers.analyze
    CC=18  in:0  out:31  total:31
  urisys-node.packages.python.urisysnode.serve.call_uri
    CC=20  in:1  out:29  total:30

MODULES:
  packages.python.urisysedge.env  [7 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    is_secret_env  CC=1  out:1
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  packages.python.urisysedge.runtime  [7 funcs]
    tail  CC=4  out:5
    call  CC=10  out:23
    load_json  CC=3  out:5
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  scripts.office-simulate-loop  [5 funcs]
    call_uri  CC=4  out:11
    llm_tick  CC=7  out:18
    main  CC=10  out:12
    parse_args  CC=1  out:8
    rules_tick  CC=3  out:8
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
  scripts.report.util  [2 funcs]
    now_iso  CC=1  out:3
    read_json  CC=3  out:3
  scripts.run-nl-log-smoke  [1 funcs]
    print  CC=0  out:0
  scripts.run-office-simulate-e2e  [1 funcs]
    wait_health  CC=0  out:0
  scripts.run-office-simulate-lenovo  [1 funcs]
    save_json  CC=0  out:0
  scripts.run-urisys-node-docker-e2e  [2 funcs]
    http_json  CC=0  out:0
    remote_call  CC=0  out:0
  scripts.run_test_sessions  [1 funcs]
    session_pytest_urirdp  CC=3  out:5
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
  scripts.test_sessions.util  [13 funcs]
    compose_cmd  CC=4  out:4
    copy_container_file  CC=2  out:4
    docker_logs  CC=3  out:3
    file_md5  CC=2  out:4
    finalize_session  CC=5  out:13
    http_json  CC=9  out:18
    now_iso  CC=1  out:3
    read_meta  CC=3  out:3
    run_cmd  CC=6  out:12
    save_json  CC=1  out:3
  src.urisys.cli  [5 funcs]
    _add_runtime_flags  CC=1  out:4
    build_parser  CC=1  out:50
    main  CC=28  out:57
    print_json  CC=1  out:2
    resolve_markpact_source  CC=2  out:3
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [2 funcs]
    __init__  CC=1  out:1
    serve_forever  CC=1  out:3
  src.urisys.doctor  [9 funcs]
    _check_cli_path  CC=3  out:6
    _check_import  CC=5  out:12
    _check_min_version  CC=6  out:5
    _check_python  CC=3  out:3
    _check_wayland_him  CC=3  out:4
    _parse_version  CC=7  out:6
    _pkg_version  CC=2  out:1
    _version_lt  CC=2  out:2
    run_doctor  CC=10  out:14
  src.urisys.flow  [2 funcs]
    iter_steps  CC=7  out:8
    load_flow  CC=3  out:5
  src.urisys.http_server  [3 funcs]
    _read_json  CC=3  out:5
    _send  CC=1  out:12
    create_server  CC=1  out:31
  src.urisys.managers.pack_manager  [1 funcs]
    manifest_paths  CC=9  out:20
  uribrowser-docker.packages.python.uribrowserdocker.handlers  [6 funcs]
    _profile  CC=1  out:2
    _session_state  CC=1  out:5
    get_dom  CC=1  out:4
    open_page  CC=11  out:27
    status  CC=1  out:7
    submit_form  CC=8  out:19
  uribrowser-docker.packages.python.uribrowseredge.cli  [1 funcs]
    build_runtime  CC=2  out:7
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
  urikvm-docker.packages.python.urihim.handlers  [16 funcs]
    _driver  CC=7  out:9
    _pyautogui  CC=3  out:3
    _real_allowed  CC=2  out:3
    _run_xdotool  CC=5  out:9
    _run_ydotool  CC=3  out:5
    _state  CC=1  out:2
    _wayland_session  CC=1  out:2
    _xdotool_available  CC=2  out:3
    _ydotool_available  CC=1  out:1
    _ydotool_key_sequence  CC=9  out:13
  urikvm-docker.packages.python.urikvm.handlers  [4 funcs]
    _profile  CC=1  out:2
    _store_screenshot  CC=1  out:4
    monitor_list  CC=2  out:4
    screenshot  CC=5  out:18
  urikvm-docker.packages.python.urikvmedge.cli  [1 funcs]
    build_runtime  CC=6  out:11
  urikvm-docker.packages.python.urillm.handlers  [24 funcs]
    _analyze_litellm  CC=6  out:11
    _analyze_openai  CC=10  out:13
    _box_center  CC=1  out:4
    _click_box  CC=1  out:2
    _driver  CC=1  out:2
    _env  CC=3  out:6
    _find_goal_box  CC=6  out:2
    _find_target_box  CC=6  out:2
    _goal_text  CC=4  out:4
    _heuristic_analyze  CC=8  out:17
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
  urirdp-docker.packages.python.urirdp.handlers  [7 funcs]
    _dismiss_stale_targets  CC=10  out:11
    _service_status  CC=4  out:4
    dismiss_target  CC=3  out:4
    display  CC=2  out:4
    display_status  CC=7  out:12
    prepare_target  CC=6  out:15
    status  CC=1  out:9
  urirdp-docker.packages.python.urirdp_browser.handlers  [4 funcs]
    _chromium_binary  CC=4  out:3
    _profile  CC=1  out:2
    _session_state  CC=1  out:5
    open_page  CC=15  out:33
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
  urirdp-docker.packages.python.urirdp_llm.handlers  [17 funcs]
    _config  CC=2  out:1
    _decide_litellm  CC=3  out:5
    _decide_messages  CC=2  out:2
    _decide_openai  CC=3  out:2
    _env  CC=3  out:6
    _heuristic  CC=5  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=6  out:7
    _match_transcript  CC=4  out:3
    _openai_compatible_chat  CC=1  out:9
  urirdp-docker.packages.python.urirdp_ocr.handlers  [5 funcs]
    _mock_ocr  CC=1  out:0
    _parse_tesseract_tsv  CC=7  out:19
    _tesseract_ocr  CC=9  out:23
    image_text  CC=6  out:8
    latest_text  CC=2  out:5
  urirdp-docker.packages.python.urirdp_shell.handlers  [3 funcs]
    _detect_display  CC=5  out:6
    _mock  CC=2  out:2
    shell_run  CC=16  out:18
  urirdp-docker.packages.python.urirdpedge.cli  [1 funcs]
    build_runtime  CC=10  out:16
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
  uristepper-docker.packages.python.uristepperedge.cli  [7 funcs]
    _json_arg  CC=3  out:5
    cmd_call  CC=4  out:7
    cmd_events  CC=1  out:4
    cmd_explain  CC=1  out:4
    cmd_flow  CC=12  out:22
    cmd_routes  CC=1  out:4
    cmd_serve  CC=1  out:1
  uristepper-docker.packages.python.uristepperedge.runtime  [2 funcs]
    build_runtime  CC=6  out:14
    load_json  CC=1  out:3
  uristepper-docker.packages.python.uristepperedge.server  [2 funcs]
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
  urisys-node.packages.python.uriscreen.backends  [11 funcs]
    _http_json  CC=3  out:7
    capture_portal  CC=2  out:4
    capture_vdisplay  CC=8  out:15
    capture_with_fallback  CC=13  out:12
    is_black_png  CC=5  out:6
    is_wayland  CC=1  out:1
    resolve_backend  CC=7  out:9
    session_type  CC=2  out:3
    vdisplay_agent_up  CC=2  out:4
    vdisplay_agent_url  CC=1  out:2
  urisys-node.packages.python.uriscreen.handlers  [8 funcs]
    _backend  CC=2  out:3
    _monitor_index  CC=6  out:9
    _output_dir  CC=2  out:5
    _screen_cfg  CC=1  out:2
    _store_latest  CC=1  out:1
    capture  CC=5  out:21
    capture_loop  CC=4  out:10
    frame  CC=1  out:5
  urisys-node.packages.python.uriscreen.portal_capture  [2 funcs]
    _portal_python  CC=6  out:5
    capture_portal_png  CC=8  out:14
  urisys-node.packages.python.urishell.handlers  [3 funcs]
    _detect_display  CC=5  out:6
    _mock  CC=2  out:2
    shell_run  CC=16  out:18
  urisys-node.packages.python.urisysnode.artifact_resolver  [19 funcs]
    _auth_opener  CC=4  out:11
    _contract_yaml_block  CC=6  out:6
    contract_spec_from_release  CC=2  out:4
    contract_url_from_release  CC=6  out:8
    docker_pull  CC=4  out:4
    docker_run_worker  CC=3  out:4
    fetch_json  CC=1  out:6
    fetch_release  CC=5  out:11
    fetch_text  CC=1  out:5
    is_url  CC=1  out:1
  urisys-node.packages.python.urisysnode.client  [2 funcs]
    call_via_route_map  CC=6  out:14
    remote_call  CC=3  out:8
  urisys-node.packages.python.urisysnode.display_bootstrap  [7 funcs]
    _agent_up  CC=2  out:2
    _agent_url  CC=1  out:2
    _ensure_session_env  CC=5  out:7
    _screencast_ready  CC=4  out:9
    _start_agent  CC=4  out:9
    _start_screencast  CC=5  out:7
    bootstrap_wayland_capture  CC=7  out:17
  urisys-node.packages.python.urisysnode.forward  [1 funcs]
    forward_call  CC=9  out:8
  urisys-node.packages.python.urisysnode.forward_config  [6 funcs]
    _normalize_entry  CC=11  out:13
    _normalize_release_entry  CC=11  out:15
    load_forward_entries  CC=15  out:20
    load_release_forward_entries  CC=11  out:12
    wire_forward_packs  CC=2  out:2
    wire_release_forward_packs  CC=3  out:4
  urisys-node.packages.python.urisysnode.handlers  [7 funcs]
    command_indicator_off  CC=1  out:2
    command_indicator_on  CC=1  out:4
    command_install_pack  CC=6  out:13
    command_register_forward  CC=7  out:12
    query_health  CC=1  out:2
    query_identity  CC=2  out:8
    query_packs  CC=2  out:7
  urisys-node.packages.python.urisysnode.identity  [12 funcs]
    _data_dir  CC=1  out:3
    _hostname  CC=1  out:1
    _identity_path  CC=1  out:1
    _pairing_path  CC=1  out:1
    enroll  CC=3  out:6
    health_payload  CC=15  out:22
    load_identity  CC=4  out:15
    load_pairing  CC=3  out:5
    require_paired  CC=4  out:5
    save_identity  CC=1  out:3
  urisys-node.packages.python.urisysnode.pack_resolver  [16 funcs]
    _pip_install  CC=3  out:2
    auto_install_enabled  CC=1  out:1
    ensure_pack_pypi  CC=3  out:3
    ensure_pip_specs  CC=4  out:2
    ensure_real_deps  CC=1  out:2
    github_owner  CC=1  out:2
    github_wheel_url  CC=4  out:6
    github_wheel_urls  CC=5  out:4
    import_pack_module  CC=1  out:2
    pack_for_scheme  CC=1  out:1
  urisys-node.packages.python.urisysnode.release_verify  [4 funcs]
    _ed25519_verify  CC=3  out:5
    canonical_digest  CC=3  out:5
    signature_required  CC=3  out:2
    verify_release  CC=14  out:15
  urisys-node.packages.python.urisysnode.router  [5 funcs]
    _match_pattern  CC=1  out:4
    load_route_map  CC=3  out:4
    node_endpoint  CC=5  out:6
    resolve_remote_route  CC=5  out:3
    rewrite_uri_for_slave  CC=6  out:5
  urisys-node.packages.python.urisysnode.serve  [11 funcs]
    _extend_pack_paths  CC=4  out:7
    _register_pack  CC=8  out:13
    _release_forward_spec  CC=11  out:8
    build_runtime  CC=13  out:28
    call_uri  CC=20  out:29
    ensure_pack_for_uri  CC=3  out:6
    hotload_release_pack  CC=14  out:17
    load_pack_into_runtime  CC=23  out:23
    make_handler  CC=2  out:77
    register_forward_pack  CC=13  out:8

EDGES:
  packages.python.urisysedge.runtime.Runtime.call → packages.python.urisysedge.env.load_env_policy
  packages.python.urisysedge.runtime.run_flow → packages.python.urisysedge.runtime.load_yaml_flow
  packages.python.urisysedge.runtime.serve → scripts.run-nl-log-smoke.print
  packages.python.urisysedge.runtime.serve → packages.python.urisysedge.runtime.make_handler
  packages.python.urisysedge.env.load_urisys_env → packages.python.urisysedge.env._urisys_root
  packages.python.urisysedge.env._env_policy_candidates → packages.python.urisysedge.env._urisys_root
  packages.python.urisysedge.env.load_env_policy → packages.python.urisysedge.env._env_policy_candidates
  packages.python.urisysedge.env.resolve_env_var → packages.python.urisysedge.env._env_config
  packages.python.urisysedge.env.resolve_env_var → packages.python.urisysedge.env.load_env_policy
  packages.python.urisysedge.env.resolve_env_var → urienv-docker.packages.python.urienv.src.urienv.handlers.secret_value
  packages.python.urisysedge.env.resolve_env_var → urienv-docker.packages.python.urienv.src.urienv.handlers.var_value
  src.urisys.cli.print_json → scripts.run-nl-log-smoke.print
  src.urisys.cli.build_parser → src.urisys.cli._add_runtime_flags
  src.urisys.cli.main → src.urisys.cli.build_parser
  src.urisys.cli.main → src.urisys.cli.resolve_markpact_source
  src.urisys.cli.main → src.urisys.doctor.run_doctor
  src.urisys.cli.main → src.urisys.cli.print_json
  src.urisys.cli.main → scripts.run-nl-log-smoke.print
  src.urisys.doctor._version_lt → src.urisys.doctor._parse_version
  src.urisys.doctor._check_import → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._pkg_version
  src.urisys.doctor._check_min_version → src.urisys.doctor._version_lt
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_min_version
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_wayland_him
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_python
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_cli_path
  src.urisys.doctor.run_doctor → src.urisys.doctor._check_import
  src.urisys.http_server.create_server → src.urisys.http_server._send
  src.urisys.http_server.create_server → src.urisys.http_server._read_json
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.load_flow
  src.urisys.controllers.flow_controller.FlowController.run → src.urisys.flow.iter_steps
  src.urisys.controllers.server_controller.ServerController.__init__ → src.urisys.http_server.create_server
  src.urisys.controllers.server_controller.ServerController.serve_forever → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.runtime.build_runtime → uristepper-docker.packages.python.uristepperedge.runtime.load_json
  uristepper-docker.packages.python.uristepperedge.cli.cmd_call → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_call → uristepper-docker.packages.python.uristepperedge.cli._json_arg
  uristepper-docker.packages.python.uristepperedge.cli.cmd_call → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_explain → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_explain → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_routes → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_routes → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_events → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_events → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_flow → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.cli.cmd_flow → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.cli.cmd_serve → packages.python.urisysedge.runtime.serve
  uristepper-docker.packages.python.uristepperedge.server.serve → uristepper-docker.packages.python.uristepperedge.runtime.build_runtime
  uristepper-docker.packages.python.uristepperedge.server.serve → scripts.run-nl-log-smoke.print
  uristepper-docker.packages.python.uristepperedge.server.serve → uristepper-docker.packages.python.uristepperedge.server.make_handler
  uristepper-docker.packages.python.uristepper.handlers._driver → uristepper-docker.packages.python.uristepper.drivers.make_driver
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 303f 19509L | python:141,shell:60,yaml:46,toml:16,json:14,yml:11,javascript:2,txt:2,conf:1,gui:1 | 2026-06-17
# generated in 0.06s
# CC̅=4.3 | critical:31/711 | dups:0 | cycles:0

HEALTH[20]:
  🟡 CC    main CC=28 (limit:15)
  🟡 CC    validate_contract CC=23 (limit:15)
  🟡 CC    validate_implementation CC=18 (limit:15)
  🟡 CC    compile CC=21 (limit:15)
  🟡 CC    run_tests CC=20 (limit:15)
  🟡 CC    _build_route CC=18 (limit:15)
  🟡 CC    parse_packs CC=15 (limit:15)
  🟡 CC    load_flow_outcomes CC=15 (limit:15)
  🟡 CC    infer_steps CC=20 (limit:15)
  🟡 CC    shell_run CC=16 (limit:15)
  🟡 CC    open_page CC=15 (limit:15)
  🟡 CC    analyze CC=18 (limit:15)
  🟡 CC    decide CC=15 (limit:15)
  🟡 CC    plan CC=20 (limit:15)
  🟡 CC    mouse_click CC=17 (limit:15)
  🟡 CC    mouse_scroll CC=18 (limit:15)
  🟡 CC    uri_execute CC=15 (limit:15)
  🟡 CC    build_lab_runtime CC=17 (limit:15)
  🟡 CC    do_POST CC=23 (limit:15)
  🟡 CC    main CC=19 (limit:15)

REFACTOR[1]:
  1. split 20 high-CC methods  (CC>15)

PIPELINES[290]:
  [1] Src [compile]: compile
      PURITY: 100% pure
  [2] Src [match]: match
      PURITY: 100% pure
  [3] Src [__init__]: __init__
      PURITY: 100% pure
  [4] Src [append]: append
      PURITY: 100% pure
  [5] Src [__init__]: __init__
      PURITY: 100% pure
  [6] Src [register]: register
      PURITY: 100% pure
  [7] Src [resolve]: resolve
      PURITY: 100% pure
  [8] Src [_load_handler]: _load_handler
      PURITY: 100% pure
  [9] Src [call]: call → load_env_policy → _env_policy_candidates → _urisys_root
      PURITY: 100% pure
  [10] Src [registry]: registry
      PURITY: 100% pure
  [11] Src [runtime]: runtime
      PURITY: 100% pure
  [12] Src [out]: out
      PURITY: 100% pure
  [13] Src [result]: result
      PURITY: 100% pure
  [14] Src [client]: client
      PURITY: 100% pure
  [15] Src [main]: main → build_parser → _add_runtime_flags
      PURITY: 100% pure
  [16] Src [__init__]: __init__
      PURITY: 100% pure
  [17] Src [run]: run → load_flow
      PURITY: 100% pure
  [18] Src [close]: close
      PURITY: 100% pure
  [19] Src [__init__]: __init__ → create_server → _send
      PURITY: 100% pure
  [20] Src [serve_forever]: serve_forever → print
      PURITY: 100% pure
  [21] Src [__init__]: __init__
      PURITY: 100% pure
  [22] Src [call]: call
      PURITY: 100% pure
  [23] Src [explain]: explain
      PURITY: 100% pure
  [24] Src [routes]: routes
      PURITY: 100% pure
  [25] Src [close]: close
      PURITY: 100% pure
  [26] Src [to_dict]: to_dict
      PURITY: 100% pure
  [27] Src [safe_identifier]: safe_identifier
      PURITY: 100% pure
  [28] Src [parse_meta]: parse_meta
      PURITY: 100% pure
  [29] Src [source_hash]: source_hash
      PURITY: 100% pure
  [30] Src [__init__]: __init__
      PURITY: 100% pure
  [31] Src [list_events]: list_events
      PURITY: 100% pure
  [32] Src [build_context]: build_context
      PURITY: 100% pure
  [33] Src [explain]: explain
      PURITY: 100% pure
  [34] Src [__init__]: __init__
      PURITY: 100% pure
  [35] Src [create_runtime]: create_runtime
      PURITY: 100% pure
  [36] Src [close]: close
      PURITY: 100% pure
  [37] Src [__exit__]: __exit__
      PURITY: 100% pure
  [38] Src [__init__]: __init__
      PURITY: 100% pure
  [39] Src [read_blocks]: read_blocks
      PURITY: 100% pure
  [40] Src [source_hash]: source_hash
      PURITY: 100% pure
  [41] Src [load_pack_block]: load_pack_block
      PURITY: 100% pure
  [42] Src [validate]: validate → validate_contract → scheme_from_uri
      PURITY: 100% pure
  [43] Src [_validate_pack]: _validate_pack
      PURITY: 100% pure
  [44] Src [compile]: compile
      PURITY: 100% pure
  [45] Src [manifest_path_for]: manifest_path_for
      PURITY: 100% pure
  [46] Src [run_tests]: run_tests
      PURITY: 100% pure
  [47] Src [_build_route]: _build_route
      PURITY: 100% pure
  [48] Src [_compile_manifest]: _compile_manifest
      PURITY: 100% pure
  [49] Src [_package_id]: _package_id
      PURITY: 100% pure
  [50] Src [_capabilities]: _capabilities
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.8    ←in:0  →out:0
  │ !! markpact_manager           401L  1C   19m  CC=21     ←0
  │ !! cli                        234L  0C    6m  CC=28     ←0
  │ source_manager             224L  2C   11m  CC=11     ←0
  │ doctor                     205L  1C    9m  CC=10     ←2
  │ !! markpact_validation        140L  0C    3m  CC=23     ←1
  │ !! pack_manager               128L  1C   13m  CC=15     ←1
  │ markpact_models             92L  3C    5m  CC=4      ←1
  │ http_server                 78L  0C    3m  CC=3      ←1
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
  urikvm-docker/                  CC̄=4.8    ←in:0  →out:0
  │ !! handlers                   414L  0C   26m  CC=31     ←0
  │ !! handlers                   263L  0C   16m  CC=18     ←0
  │ handlers                   138L  0C   11m  CC=9      ←0
  │ !! handlers                   127L  0C   11m  CC=18     ←0
  │ handlers                   115L  0C   10m  CC=8      ←0
  │ handlers                   103L  0C    6m  CC=8      ←0
  │ real_pipeline               95L  0C    4m  CC=14     ←0
  │ cli                         56L  0C    2m  CC=7      ←0
  │ pyproject.toml              51L  0C    0m  CC=0.0    ←0
  │ test-real.sh                47L  0C    1m  CC=0.0    ←0
  │ routes                      39L  0C    1m  CC=1      ←0
  │ manifest.yaml               39L  0C    0m  CC=0.0    ←0
  │ manifest.yaml               39L  0C    0m  CC=0.0    ←0
  │ routes                      37L  0C    1m  CC=1      ←0
  │ handlers                    33L  0C    2m  CC=11     ←0
  │ kvm-profile.json            26L  0C    0m  CC=0.0    ←0
  │ kvm-profile.real.json       24L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              23L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              23L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              23L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              22L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              21L  0C    0m  CC=0.0    ←0
  │ kvm-click-ok.uri.flow.yaml    20L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              18L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              18L  0C    0m  CC=0.0    ←0
  │ manifest.yaml               18L  0C    0m  CC=0.0    ←0
  │ routes                      13L  0C    1m  CC=1      ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   8L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ routes                       7L  0C    1m  CC=1      ←0
  │ routes                       5L  0C    1m  CC=1      ←0
  │ call-http.sh                 5L  0C    0m  CC=0.0    ←0
  │ routes                       3L  0C    1m  CC=1      ←0
  │ routes                       3L  0C    1m  CC=1      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=4.6    ←in:65  →out:117  !! split
  │ !! run_test_sessions          782L  0C   14m  CC=30     ←0
  │ lab_flows                  319L  0C    5m  CC=13     ←0
  │ util                       209L  0C   17m  CC=9      ←7
  │ !! lab_checks                 188L  0C    9m  CC=15     ←1
  │ run-office-simulate-lenovo.sh   182L  0C    6m  CC=0.0    ←2
  │ lab_rdp                    180L  0C    8m  CC=11     ←1
  │ run-urisys-node-docker-e2e.sh   162L  0C    5m  CC=0.0    ←4
  │ expectations               153L  0C    9m  CC=11     ←1
  │ office-simulate-loop       146L  0C    5m  CC=10     ←1
  │ events                     138L  0C    5m  CC=14     ←1
  │ run-email-mailpit-e2e.sh   133L  0C    4m  CC=0.0    ←0
  │ run-office-simulate-e2e.sh   129L  0C    4m  CC=0.0    ←2
  │ run_analysis               129L  0C    5m  CC=13     ←1
  │ session_markdown           120L  0C    8m  CC=7      ←1
  │ run-office-writer-e2e.sh   112L  0C    4m  CC=0.0    ←0
  │ !! session                    105L  0C    5m  CC=20     ←2
  │ remote-node-smoke.sh        99L  0C    2m  CC=0.0    ←0
  │ __init__                    98L  0C    0m  CC=0.0    ←0
  │ models                      86L  5C    0m  CC=0.0    ←0
  │ lenovo-node-session.sh      72L  0C    1m  CC=0.0    ←0
  │ deploy-lenovo-node.sh       71L  0C    2m  CC=0.0    ←0
  │ publish-pypi-packs.sh       64L  0C    0m  CC=0.0    ←0
  │ __init__                    61L  0C    0m  CC=0.0    ←0
  │ paths.sh                    54L  0C    6m  CC=0.0    ←0
  │ validate-all-markpacts.sh    53L  0C    0m  CC=0.0    ←0
  │ session_report              49L  0C    0m  CC=0.0    ←0
  │ run-nl-log-smoke.sh         43L  0C    1m  CC=0.0    ←17
  │ run_markdown                42L  0C    1m  CC=7      ←1
  │ cli                         41L  0C    1m  CC=4      ←0
  │ util                        29L  0C    4m  CC=3      ←5
  │ run-smoke-all.sh            24L  0C    0m  CC=0.0    ←0
  │ run-lab-unit-ci.sh          20L  0C    0m  CC=0.0    ←0
  │ session_io                  19L  0C    1m  CC=2      ←2
  │ run-lab-nightly.sh          16L  0C    0m  CC=0.0    ←0
  │ install-kvm-packs-editable.sh    15L  0C    0m  CC=0.0    ←0
  │ sync-vendored-urisysedge.sh    15L  0C    0m  CC=0.0    ←0
  │ run-lab-e2e.sh              14L  0C    0m  CC=0.0    ←0
  │ test-goal.sh                11L  0C    0m  CC=0.0    ←0
  │ run-urisys-node-docker-session.sh     6L  0C    0m  CC=0.0    ←0
  │
  urisys-node/                    CC̄=4.6    ←in:0  →out:0
  │ !! serve                      462L  0C   11m  CC=23     ←2
  │ !! artifact_resolver          302L  1C   21m  CC=15     ←2
  │ pack_resolver              217L  0C   16m  CC=7      ←2
  │ !! cli                        180L  0C    1m  CC=19     ←0
  │ backends                   170L  0C   12m  CC=13     ←1
  │ !! identity                   162L  0C   13m  CC=15     ←3
  │ !! forward_config             144L  0C    6m  CC=15     ←1
  │ release_verify             138L  0C    5m  CC=14     ←1
  │ display_bootstrap          114L  0C    7m  CC=7      ←1
  │ portal_capture             110L  1C    2m  CC=8      ←1
  │ pyproject.toml             100L  0C    0m  CC=0.0    ←0
  │ handlers                    94L  0C    9m  CC=6      ←0
  │ client                      92L  0C    3m  CC=6      ←1
  │ handlers                    89L  0C    7m  CC=7      ←0
  │ !! handlers                    70L  0C    4m  CC=16     ←0
  │ entrypoint.sh               63L  0C    3m  CC=0.0    ←0
  │ node-profile.lenovo.json    63L  0C    0m  CC=0.0    ←0
  │ Dockerfile.gui              51L  0C    0m  CC=0.0    ←0
  │ router                      47L  0C    5m  CC=6      ←2
  │ routes                      41L  0C    1m  CC=1      ←0
  │ route-map.lenovo.yaml       36L  0C    0m  CC=0.0    ←0
  │ forward                     33L  0C    1m  CC=9      ←0
  │ docker-compose.gui.yml      33L  0C    0m  CC=0.0    ←0
  │ node-profile.docker.json    33L  0C    0m  CC=0.0    ←0
  │ node-profile.json           32L  0C    0m  CC=0.0    ←0
  │ bootstrap-kvm-github.uri.flow.yaml    28L  0C    0m  CC=0.0    ←0
  │ routes                      23L  0C    1m  CC=1      ←0
  │ route-map.host.yaml         23L  0C    0m  CC=0.0    ←0
  │ route-map.master.yaml       19L  0C    0m  CC=0.0    ←0
  │ nodes.registry.json         18L  0C    0m  CC=0.0    ←0
  │ bootstrap-kvm-pypi.uri.flow.yaml    18L  0C    0m  CC=0.0    ←0
  │ remote-probe.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ install-linux.sh            16L  0C    0m  CC=0.0    ←0
  │ route-map.slave.yaml        14L  0C    0m  CC=0.0    ←0
  │ slave-kvm-demo.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ screen-capture-mss.uri.flow.yaml    12L  0C    0m  CC=0.0    ←0
  │ routes                       9L  0C    1m  CC=1      ←0
  │ nodes.registry.host.json     9L  0C    0m  CC=0.0    ←0
  │ runtime                      5L  0C    0m  CC=0.0    ←0
  │ env                          5L  0C    0m  CC=0.0    ←0
  │
  packages/                       CC̄=4.4    ←in:0  →out:0
  │ runtime                    270L  3C   16m  CC=14     ←10
  │ env                        129L  0C    7m  CC=11     ←6
  │ pyproject.toml              21L  0C    0m  CC=0.0    ←0
  │ __init__                    12L  0C    0m  CC=0.0    ←0
  │
  urirdp-docker/                  CC̄=4.2    ←in:0  →out:0
  │ !! handlers                   387L  0C   22m  CC=20     ←0
  │ !! handlers                   171L  0C    7m  CC=15     ←0
  │ handlers                   144L  0C    7m  CC=10     ←1
  │ handlers                   133L  0C    5m  CC=10     ←0
  │ bootstrap-rdp-session.sh   111L  0C    7m  CC=0.0    ←0
  │ cli                         98L  0C    2m  CC=10     ←0
  │ handlers                    79L  0C    5m  CC=9      ←0
  │ handlers                    72L  0C    7m  CC=11     ←0
  │ !! handlers                    68L  0C    4m  CC=16     ←0
  │ display                     63L  0C    6m  CC=7      ←5
  │ test-real-docker.sh         63L  0C    1m  CC=0.0    ←0
  │ pyproject.toml              50L  0C    0m  CC=0.0    ←0
  │ routes                      45L  0C    1m  CC=3      ←0
  │ Dockerfile                  43L  0C    0m  CC=0.0    ←0
  │ docker-compose.rdp-e2e.yml    41L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-profile.real.json    39L  0C    0m  CC=0.0    ←0
  │ routes                      35L  0C    1m  CC=3      ←0
  │ supervisord.conf            35L  0C    0m  CC=0.0    ←0
  │ env-policy.yaml             31L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-profile.json        30L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               25L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          24L  0C    0m  CC=0.0    ←0
  │ runtime                     23L  0C    0m  CC=0.0    ←0
  │ routes                      20L  0C    1m  CC=1      ←0
  │ Makefile                    20L  0C    0m  CC=0.0    ←0
  │ env                         19L  0C    0m  CC=0.0    ←0
  │ test-docker.sh              17L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-smoke.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ real-rdp-click-text.uri.flow.yaml    14L  0C    0m  CC=0.0    ←0
  │ test-rdp-real.sh            12L  0C    0m  CC=0.0    ←0
  │ call-http.sh                10L  0C    0m  CC=0.0    ←0
  │ routes                       9L  0C    1m  CC=1      ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ routes                       7L  0C    1m  CC=1      ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ startwm.sh                   6L  0C    0m  CC=0.0    ←0
  │ routes                       5L  0C    1m  CC=1      ←0
  │ __init__                     4L  0C    1m  CC=1      ←0
  │ routes                       4L  0C    1m  CC=1      ←0
  │ routes                       3L  0C    1m  CC=1      ←0
  │ __init__                     3L  0C    1m  CC=1      ←0
  │
  urisys-automation-lab/          CC̄=3.9    ←in:0  →out:0
  │ !! automation_lab_server      247L  1C    9m  CC=23     ←0
  │ flow_runner                169L  0C    7m  CC=13     ←1
  │ app.js                     131L  0C   17m  CC=2      ←0
  │ lab_uri_adapter            129L  1C    3m  CC=12     ←0
  │ !! handlers                    81L  0C    4m  CC=15     ←0
  │ docker-compose.lab.yml      66L  0C    0m  CC=0.0    ←0
  │ handlers                    57L  0C    4m  CC=5      ←0
  │ 10_full_maintenance_rdp.uri.flow.yaml    42L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  41L  0C    0m  CC=0.0    ←0
  │ 08_voice_command_to_kvm.uri.flow.yaml    40L  0C    0m  CC=0.0    ←0
  │ handlers                    35L  0C    3m  CC=4      ←0
  │ local-rdp.routes.yaml       32L  0C    0m  CC=0.0    ←0
  │ 09_webrtc_video_chat_rdp.uri.flow.yaml    29L  0C    0m  CC=0.0    ←0
  │ validate-flows.sh           28L  0C    0m  CC=0.0    ←0
  │ 05_fill_form_gui.uri.flow.yaml    27L  0C    0m  CC=0.0    ←0
  │ 07_edit_config_nano_tui.uri.flow.yaml    27L  0C    0m  CC=0.0    ←0
  │ routes                      23L  0C    1m  CC=1      ←0
  │ 06_terminal_htop_tui.uri.flow.yaml    23L  0C    0m  CC=0.0    ←0
  │ 04_browser_download_file.uri.flow.yaml    22L  0C    0m  CC=0.0    ←0
  │ docker-up.sh                21L  0C    0m  CC=0.0    ←0
  │ docker-smoke.sh             20L  0C    0m  CC=0.0    ←0
  │ 03_open_browser_gui.uri.flow.yaml    19L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               18L  0C    0m  CC=0.0    ←0
  │ routes                      17L  0C    1m  CC=1      ←0
  │ handlers                    17L  0C    1m  CC=4      ←0
  │ routes                      17L  0C    1m  CC=1      ←0
  │ 02_update_system_tui.uri.flow.yaml    15L  0C    0m  CC=0.0    ←0
  │ run-lab.sh                  13L  0C    0m  CC=0.0    ←0
  │ 01_install_browser.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ routes                       9L  0C    1m  CC=1      ←0
  │ docker-logs.sh               6L  0C    0m  CC=0.0    ←0
  │ docker-down.sh               6L  0C    0m  CC=0.0    ←0
  │ static_server                6L  0C    0m  CC=0.0    ←0
  │ runtime                      5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  uribrowser-docker/              CC̄=3.7    ←in:0  →out:0
  │ handlers                   109L  0C    6m  CC=11     ←0
  │ pyproject.toml              50L  0C    0m  CC=0.0    ←0
  │ cli                         49L  0C    2m  CC=7      ←0
  │ test-real.sh                28L  0C    0m  CC=0.0    ←0
  │ browser-demo.uri.flow.yaml    14L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ browser-profile.json        10L  0C    0m  CC=0.0    ←0
  │ browser-profile.real.json     9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   8L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ routes                       6L  0C    1m  CC=1      ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  urienv-docker/                  CC̄=3.6    ←in:0  →out:0
  │ handlers                   196L  0C   19m  CC=7      ←1
  │ manifest.yaml               67L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          52L  0C    0m  CC=0.0    ←0
  │ env-policy.yaml             36L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  32L  0C    0m  CC=0.0    ←0
  │ cli                         26L  0C    2m  CC=10     ←0
  │ server                      26L  0C    1m  CC=1      ←0
  │ runtime                     21L  0C    4m  CC=3      ←3
  │ pyproject.toml              20L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              19L  0C    0m  CC=0.0    ←0
  │ flow                        16L  0C    1m  CC=12     ←0
  │ mutate-process-env.uri.flow.yaml    16L  0C    0m  CC=0.0    ←0
  │ pack_loader                 15L  0C    2m  CC=4      ←0
  │ startup-env-check.uri.flow.yaml    15L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              10L  0C    0m  CC=0.0    ←0
  │ local-test.sh               10L  0C    0m  CC=0.0    ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │ test-docker.sh               4L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ smtp_password.txt            1L  0C    0m  CC=0.0    ←0
  │ markpact_token.txt           1L  0C    0m  CC=0.0    ←0
  │
  uristepper-docker/              CC̄=2.2    ←in:0  →out:0
  │ runtime                    169L  4C    9m  CC=6      ←6
  │ drivers                    169L  3C   30m  CC=4      ←1
  │ cli                        124L  0C    8m  CC=12     ←0
  │ handlers                   112L  0C   11m  CC=10     ←0
  │ server                      74L  0C    2m  CC=1      ←0
  │ device-profile.json         61L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          35L  0C    0m  CC=0.0    ←0
  │ move-test.uri.flow.yaml     35L  0C    0m  CC=0.0    ←0
  │ device-profile.rpi3.example.json    33L  0C    0m  CC=0.0    ←0
  │ Makefile                    25L  0C    0m  CC=0.0    ←0
  │ docker-compose.rpi3.example.yml    21L  0C    0m  CC=0.0    ←0
  │ safety-denied.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  16L  0C    0m  CC=0.0    ←0
  │ call-http.sh                10L  0C    0m  CC=0.0    ←0
  │ test-local.sh               10L  0C    0m  CC=0.0    ←0
  │ test-docker.sh               7L  0C    0m  CC=0.0    ←0
  │ __main__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
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
  │ pyproject.toml             117L  0C    0m  CC=0.0    ←0
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
  flows/                          CC̄=0.0    ←in:0  →out:0
  │ email-mailpit.uri.flow.yaml    36L  0C    0m  CC=0.0    ←0
  │ browser-form-vql.uri.flow.yaml    33L  0C    0m  CC=0.0    ←0
  │ office-writer.uri.flow.yaml    31L  0C    0m  CC=0.0    ←0
  │ office-simulate-tick.uri.flow.yaml    27L  0C    0m  CC=0.0    ←0
  │ device-maintenance.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │
  urimail-docker/                 CC̄=0.0    ←in:0  →out:0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     src/urisys/controllers/__init__.py        0L

COUPLING:
                                                     scripts         scripts.test_sessions               packages.python        urirdp-docker.packages                scripts.report          urisys-node.packages        urikvm-docker.packages    uristepper-docker.packages        urienv-docker.packages                    src.urisys  urisys-automation-lab.server    uribrowser-docker.packages         urikvm-docker.scripts
                       scripts                            ──                            90                            ←3                            ←2                            27                           ←19                            ←2                            ←7                            ←5                            ←4                            ←6                            ←2                            ←2  hub
         scripts.test_sessions                             7                            ──                                                         ←20                             2                                                                                                                                                                                                                                                  hub
               packages.python                             3                                                          ──                           ←16                            ←1                            ←3                           ←17                            ←1                             2                                                          ←1                            ←3                            ←1  hub
        urirdp-docker.packages                             2                            20                            16                            ──                                                                                                                                                                                                                                                                                !! fan-out
                scripts.report                             6                            ←2                             1                                                          ──                                                                                                                                                                                                                                                  hub
          urisys-node.packages                            19                                                           3                                                                                        ──                                                           2                                                           1                                                                                            !! fan-out
        urikvm-docker.packages                             2                                                          17                                                                                                                      ──                                                                                                                                                                                      !! fan-out
    uristepper-docker.packages                             7                                                           1                                                                                        ←2                                                          ──                            ←2                            ←1                                                                                            hub
        urienv-docker.packages                             5                                                           2                                                                                                                                                     2                            ──                             1                                                                                            !! fan-out
                    src.urisys                             4                                                                                                                                                    ←1                                                           1                            ←1                            ──                                                                                          
  urisys-automation-lab.server                             6                                                           1                                                                                                                                                                                                                                              ──                                                            
    uribrowser-docker.packages                             2                                                           3                                                                                                                                                                                                                                                                            ──                              
         urikvm-docker.scripts                             2                                                           1                                                                                                                                                                                                                                                                                                          ──
  CYCLES: none
  HUB: scripts/ (fan-in=65)
  HUB: scripts.test_sessions/ (fan-in=110)
  HUB: scripts.report/ (fan-in=29)
  HUB: uristepper-docker.packages/ (fan-in=5)
  HUB: packages.python/ (fan-in=45)
  SMELL: urisys-node.packages/ fan-out=25 → split needed
  SMELL: scripts/ fan-out=117 → split needed
  SMELL: urikvm-docker.packages/ fan-out=19 → split needed
  SMELL: urienv-docker.packages/ fan-out=10 → split needed
  SMELL: scripts.test_sessions/ fan-out=9 → split needed
  SMELL: urirdp-docker.packages/ fan-out=38 → split needed
  SMELL: uristepper-docker.packages/ fan-out=8 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 1 groups | 39f 3531L | 2026-06-17

SUMMARY:
  files_scanned: 39
  total_lines:   3531
  dup_groups:    1
  dup_fragments: 2
  saved_lines:   8
  scan_ms:       2346

HOTSPOTS[2] (files with most duplication):
  scripts/report/run_analysis.py  dup=8L  groups=1  frags=1  (0.2%)
  scripts/report/session_io.py  dup=8L  groups=1  frags=1  (0.2%)

DUPLICATES[1] (ranked by impact):
  [bb100fda4da2fc0e]   STRU  write_run_analysis  L=8 N=2 saved=8 sim=1.00
      scripts/report/run_analysis.py:122-129  (write_run_analysis)
      scripts/report/session_io.py:12-19  (write_session_report)

REFACTOR[1] (ranked by priority):
  [1] ○ extract_function   → scripts/report/utils/write_run_analysis.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: scripts/report/run_analysis.py, scripts/report/session_io.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=8L  → scripts/report/utils/write_run_analysis.py
      FILES: run_analysis.py, session_io.py

EFFORT_ESTIMATE (total ≈ 0.3h):
  easy   write_run_analysis                  saved=8L  ~16min

METRICS-TARGET:
  dup_groups:  1 → 0
  saved_lines: 8 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 568 func | 100f | 2026-06-17
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT-FUNC      main  CC=28  fan=34
      WHY: CC=28 exceeds 15
      EFFORT: ~1h  IMPACT: 952

  [2] !  SPLIT-FUNC      main  CC=19  fan=44
      WHY: CC=19 exceeds 15
      EFFORT: ~1h  IMPACT: 836

  [3] !  SPLIT-FUNC      MarkpactManager.compile  CC=21  fan=34
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 714

  [4] !  SPLIT-FUNC      text_plan  CC=24  fan=20
      WHY: CC=24 exceeds 15
      EFFORT: ~1h  IMPACT: 480

  [5] !  SPLIT-FUNC      load_pack_into_runtime  CC=23  fan=20
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 460

  [6] !  SPLIT-FUNC      MarkpactManager.run_tests  CC=20  fan=21
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 420

  [7] !  SPLIT-FUNC      plan  CC=20  fan=18
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 360

  [8] !  SPLIT-FUNC      analyze  CC=18  fan=19
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 342

  [9] !! SPLIT-FUNC      _match_office_transcript  CC=31  fan=11
      WHY: CC=31 exceeds 15
      EFFORT: ~1h  IMPACT: 341

  [10] !  SPLIT-FUNC      open_page  CC=15  fan=22
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 330


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.2 → ≤2.9
  max-CC:      31 → ≤15
  god-modules: 2 → 0
  high-CC(≥15): 27 → ≤13
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
