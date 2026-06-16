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
- **version**: `0.1.15`
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
  version: 0.1.15;
}

dependencies {
  runtime: "uricore>=0.1.0, PyYAML>=6.0";
  dev: "pytest>=8.0, uricore, uribrowser, uridocker, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
  lab: uri2flow>=0.1.2;
  real: "mss>=9.0, Pillow>=10.0, pyautogui>=0.9.54, pytesseract>=0.3.10, litellm>=1.40";
  discovery: zeroconf>=0.131.0;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="urisys"] {
  entry: urisys.cli:main;
}
interface[type="cli"] page[name="urisys-node"] {
  entry: urisysnode.cli:main;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK;
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
uricore>=0.1.0
PyYAML>=6.0
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

*302 nodes · 399 edges · 54 modules · CC̄=4.1*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `analyze_run` *(in scripts.session_report)* | 39 ⚠ | 2 | 69 | **71** |
| `session_urirdp_real_docker` *(in scripts.run_test_sessions)* | 30 ⚠ | 0 | 69 | **69** |
| `session_lab_10_flows` *(in scripts.run_test_sessions)* | 36 ⚠ | 0 | 65 | **65** |
| `print` *(in scripts.run-nl-log-smoke)* | 0 | 60 | 0 | **60** |
| `write_session_report` *(in scripts.session_report)* | 28 ⚠ | 2 | 50 | **52** |
| `main` *(in src.urisys.cli)* | 20 ⚠ | 0 | 49 | **49** |
| `make_handler` *(in uristepper-docker.packages.python.uristepperedge.server)* | 1 | 1 | 43 | **44** |
| `session_automation_lab` *(in scripts.run_test_sessions)* | 16 ⚠ | 1 | 43 | **44** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.15s
# nodes: 302 | edges: 399 | modules: 54
# CC̄=4.1

HUBS[20]:
  scripts.session_report.analyze_run
    CC=39  in:2  out:69  total:71
  scripts.run_test_sessions.session_urirdp_real_docker
    CC=30  in:0  out:69  total:69
  scripts.run_test_sessions.session_lab_10_flows
    CC=36  in:0  out:65  total:65
  scripts.run-nl-log-smoke.print
    CC=0  in:60  out:0  total:60
  scripts.session_report.write_session_report
    CC=28  in:2  out:50  total:52
  src.urisys.cli.main
    CC=20  in:0  out:49  total:49
  uristepper-docker.packages.python.uristepperedge.server.make_handler
    CC=1  in:1  out:43  total:44
  scripts.run_test_sessions.session_automation_lab
    CC=16  in:1  out:43  total:44
  urisys-automation-lab.server.flow_runner.run_flow_file
    CC=13  in:1  out:40  total:41
  urienv-docker.packages.python.urienv.src.urienv.handlers._cfg
    CC=7  in:9  out:29  total:38
  urirdp-docker.packages.python.urirdp_llm.handlers.decide
    CC=23  in:0  out:38  total:38
  src.urisys.cli.build_parser
    CC=1  in:1  out:36  total:37
  scripts.run_test_sessions._run_cmd
    CC=5  in:26  out:11  total:37
  urienv-docker.packages.python.urisysedge.src.urisysedge.server.serve
    CC=1  in:0  out:36  total:36
  scripts.session_report.generate_report
    CC=11  in:2  out:34  total:36
  scripts.run_test_sessions.evaluate_expectations
    CC=29  in:1  out:32  total:33
  urirdp-docker.packages.python.urirdp_browser.handlers.open_page
    CC=15  in:0  out:33  total:33
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  urirdp-docker.packages.python.urirdp_llm.handlers.analyze
    CC=18  in:0  out:31  total:31

MODULES:
  packages.python.urisysedge.env  [7 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    is_secret_env  CC=1  out:1
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  packages.python.urisysedge.runtime  [6 funcs]
    call  CC=10  out:23
    load_json  CC=3  out:5
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  scripts.run-nl-log-smoke  [1 funcs]
    print  CC=0  out:0
  scripts.run_test_sessions  [29 funcs]
    _capture_rdp_screenshot  CC=5  out:6
    _capture_rdp_screenshot_wait  CC=9  out:6
    _compose_cmd  CC=4  out:4
    _copy_container_file  CC=2  out:4
    _docker_logs  CC=4  out:5
    _file_md5  CC=2  out:4
    _finalize_session  CC=5  out:13
    _host_id  CC=1  out:3
    _http_json  CC=9  out:18
    _now_iso  CC=1  out:3
  scripts.session_report  [14 funcs]
    _analyze_lab_flows  CC=5  out:4
    _infer_steps  CC=20  out:25
    _iter_step_results  CC=9  out:7
    _load_flow_outcomes  CC=15  out:22
    _merge_event_summaries  CC=10  out:16
    _read_json  CC=3  out:3
    _resolve_events_paths  CC=5  out:4
    _summarize_events  CC=8  out:28
    _tail  CC=2  out:0
    analyze_run  CC=39  out:69
  src.urisys.cli  [5 funcs]
    _add_runtime_flags  CC=1  out:4
    build_parser  CC=1  out:36
    main  CC=20  out:49
    print_json  CC=1  out:2
    resolve_markpact_source  CC=2  out:3
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [2 funcs]
    __init__  CC=1  out:1
    serve_forever  CC=1  out:3
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
    screenshot  CC=3  out:8
    status  CC=1  out:7
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
  urikvm-docker.packages.python.urillm.handlers  [15 funcs]
    _analyze_litellm  CC=6  out:11
    _analyze_openai  CC=10  out:13
    _box_center  CC=1  out:4
    _driver  CC=1  out:2
    _goal_text  CC=4  out:4
    _heuristic_analyze  CC=16  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=1  out:2
    _normalize_action  CC=4  out:9
    _openai_chat  CC=2  out:9
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
  urirdp-docker.packages.python.urirdp_llm.handlers  [15 funcs]
    _config  CC=2  out:1
    _decide_messages  CC=2  out:2
    _env  CC=3  out:6
    _heuristic  CC=5  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=6  out:7
    _match_transcript  CC=4  out:3
    _openai_compatible_chat  CC=1  out:9
    _parse_json_response  CC=5  out:5
    _screenshot_b64  CC=2  out:7
  urirdp-docker.packages.python.urirdp_ocr.handlers  [5 funcs]
    _mock_ocr  CC=1  out:0
    _parse_tesseract_tsv  CC=7  out:19
    _tesseract_ocr  CC=9  out:23
    image_text  CC=6  out:8
    latest_text  CC=2  out:5
  urirdp-docker.packages.python.urirdp_shell.handlers  [2 funcs]
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
  urisys-node.packages.python.uriscreen.handlers  [8 funcs]
    _backend  CC=2  out:3
    _monitor_index  CC=6  out:9
    _output_dir  CC=2  out:5
    _screen_cfg  CC=1  out:2
    _store_latest  CC=1  out:1
    capture  CC=7  out:25
    capture_loop  CC=4  out:10
    frame  CC=1  out:5
  urisys-node.packages.python.urisysedge.env  [6 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  urisys-node.packages.python.urisysedge.runtime  [5 funcs]
    call  CC=10  out:23
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  urisys-node.packages.python.urisysnode.artifact_resolver  [13 funcs]
    _auth_opener  CC=4  out:11
    docker_pull  CC=4  out:4
    docker_run_worker  CC=3  out:4
    fetch_json  CC=1  out:6
    fetch_release  CC=5  out:11
    is_url  CC=1  out:1
    load_artifact_index  CC=3  out:8
    load_node_profile  CC=3  out:4
    release_api_url  CC=1  out:3
    resolve_and_run  CC=4  out:12
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
  urisys-node.packages.python.urisysnode.serve  [5 funcs]
    _extend_pack_paths  CC=4  out:7
    _register_pack  CC=5  out:6
    build_runtime  CC=6  out:13
    make_handler  CC=1  out:30
    serve  CC=2  out:9

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
  src.urisys.cli.main → src.urisys.cli.print_json
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
# generated in 0.15s
# nodes: 302 | edges: 399 | modules: 54
# CC̄=4.1

HUBS[20]:
  scripts.session_report.analyze_run
    CC=39  in:2  out:69  total:71
  scripts.run_test_sessions.session_urirdp_real_docker
    CC=30  in:0  out:69  total:69
  scripts.run_test_sessions.session_lab_10_flows
    CC=36  in:0  out:65  total:65
  scripts.run-nl-log-smoke.print
    CC=0  in:60  out:0  total:60
  scripts.session_report.write_session_report
    CC=28  in:2  out:50  total:52
  src.urisys.cli.main
    CC=20  in:0  out:49  total:49
  uristepper-docker.packages.python.uristepperedge.server.make_handler
    CC=1  in:1  out:43  total:44
  scripts.run_test_sessions.session_automation_lab
    CC=16  in:1  out:43  total:44
  urisys-automation-lab.server.flow_runner.run_flow_file
    CC=13  in:1  out:40  total:41
  urienv-docker.packages.python.urienv.src.urienv.handlers._cfg
    CC=7  in:9  out:29  total:38
  urirdp-docker.packages.python.urirdp_llm.handlers.decide
    CC=23  in:0  out:38  total:38
  src.urisys.cli.build_parser
    CC=1  in:1  out:36  total:37
  scripts.run_test_sessions._run_cmd
    CC=5  in:26  out:11  total:37
  urienv-docker.packages.python.urisysedge.src.urisysedge.server.serve
    CC=1  in:0  out:36  total:36
  scripts.session_report.generate_report
    CC=11  in:2  out:34  total:36
  scripts.run_test_sessions.evaluate_expectations
    CC=29  in:1  out:32  total:33
  urirdp-docker.packages.python.urirdp_browser.handlers.open_page
    CC=15  in:0  out:33  total:33
  src.urisys.http_server.create_server
    CC=1  in:1  out:31  total:32
  scripts.run_test_sessions.main
    CC=13  in:0  out:32  total:32
  urirdp-docker.packages.python.urirdp_llm.handlers.analyze
    CC=18  in:0  out:31  total:31

MODULES:
  packages.python.urisysedge.env  [7 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    is_secret_env  CC=1  out:1
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  packages.python.urisysedge.runtime  [6 funcs]
    call  CC=10  out:23
    load_json  CC=3  out:5
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  scripts.run-nl-log-smoke  [1 funcs]
    print  CC=0  out:0
  scripts.run_test_sessions  [29 funcs]
    _capture_rdp_screenshot  CC=5  out:6
    _capture_rdp_screenshot_wait  CC=9  out:6
    _compose_cmd  CC=4  out:4
    _copy_container_file  CC=2  out:4
    _docker_logs  CC=4  out:5
    _file_md5  CC=2  out:4
    _finalize_session  CC=5  out:13
    _host_id  CC=1  out:3
    _http_json  CC=9  out:18
    _now_iso  CC=1  out:3
  scripts.session_report  [14 funcs]
    _analyze_lab_flows  CC=5  out:4
    _infer_steps  CC=20  out:25
    _iter_step_results  CC=9  out:7
    _load_flow_outcomes  CC=15  out:22
    _merge_event_summaries  CC=10  out:16
    _read_json  CC=3  out:3
    _resolve_events_paths  CC=5  out:4
    _summarize_events  CC=8  out:28
    _tail  CC=2  out:0
    analyze_run  CC=39  out:69
  src.urisys.cli  [5 funcs]
    _add_runtime_flags  CC=1  out:4
    build_parser  CC=1  out:36
    main  CC=20  out:49
    print_json  CC=1  out:2
    resolve_markpact_source  CC=2  out:3
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [2 funcs]
    __init__  CC=1  out:1
    serve_forever  CC=1  out:3
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
    screenshot  CC=3  out:8
    status  CC=1  out:7
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
  urikvm-docker.packages.python.urillm.handlers  [15 funcs]
    _analyze_litellm  CC=6  out:11
    _analyze_openai  CC=10  out:13
    _box_center  CC=1  out:4
    _driver  CC=1  out:2
    _goal_text  CC=4  out:4
    _heuristic_analyze  CC=16  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=1  out:2
    _normalize_action  CC=4  out:9
    _openai_chat  CC=2  out:9
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
  urirdp-docker.packages.python.urirdp_llm.handlers  [15 funcs]
    _config  CC=2  out:1
    _decide_messages  CC=2  out:2
    _env  CC=3  out:6
    _heuristic  CC=5  out:22
    _litellm_chat  CC=2  out:3
    _llm_cfg  CC=6  out:7
    _match_transcript  CC=4  out:3
    _openai_compatible_chat  CC=1  out:9
    _parse_json_response  CC=5  out:5
    _screenshot_b64  CC=2  out:7
  urirdp-docker.packages.python.urirdp_ocr.handlers  [5 funcs]
    _mock_ocr  CC=1  out:0
    _parse_tesseract_tsv  CC=7  out:19
    _tesseract_ocr  CC=9  out:23
    image_text  CC=6  out:8
    latest_text  CC=2  out:5
  urirdp-docker.packages.python.urirdp_shell.handlers  [2 funcs]
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
  urisys-node.packages.python.uriscreen.handlers  [8 funcs]
    _backend  CC=2  out:3
    _monitor_index  CC=6  out:9
    _output_dir  CC=2  out:5
    _screen_cfg  CC=1  out:2
    _store_latest  CC=1  out:1
    capture  CC=7  out:25
    capture_loop  CC=4  out:10
    frame  CC=1  out:5
  urisys-node.packages.python.urisysedge.env  [6 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  urisys-node.packages.python.urisysedge.runtime  [5 funcs]
    call  CC=10  out:23
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:24
    run_flow  CC=7  out:13
    serve  CC=2  out:6
  urisys-node.packages.python.urisysnode.artifact_resolver  [13 funcs]
    _auth_opener  CC=4  out:11
    docker_pull  CC=4  out:4
    docker_run_worker  CC=3  out:4
    fetch_json  CC=1  out:6
    fetch_release  CC=5  out:11
    is_url  CC=1  out:1
    load_artifact_index  CC=3  out:8
    load_node_profile  CC=3  out:4
    release_api_url  CC=1  out:3
    resolve_and_run  CC=4  out:12
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
  urisys-node.packages.python.urisysnode.serve  [5 funcs]
    _extend_pack_paths  CC=4  out:7
    _register_pack  CC=5  out:6
    build_runtime  CC=6  out:13
    make_handler  CC=1  out:30
    serve  CC=2  out:9

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
  src.urisys.cli.main → src.urisys.cli.print_json
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
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 236f 14783L | python:107,shell:48,yaml:35,json:13,yml:10,toml:8,javascript:2,txt:2,conf:1,gui:1 | 2026-06-16
# generated in 0.04s
# CC̅=4.1 | critical:25/542 | dups:2 | cycles:0

HEALTH[20]:
  🔴 DUP   2 classes duplicated
  🔴 GOD   scripts/session_report.py = 801L, 5 classes, 23m, max CC=39
  🟡 CC    main CC=20 (limit:15)
  🟡 CC    parse_packs CC=15 (limit:15)
  🟡 CC    session_urirdp_real_docker CC=30 (limit:15)
  🟡 CC    session_automation_lab CC=16 (limit:15)
  🟡 CC    evaluate_expectations CC=29 (limit:15)
  🟡 CC    session_lab_10_flows CC=36 (limit:15)
  🟡 CC    _infer_steps CC=20 (limit:15)
  🟡 CC    write_session_report CC=28 (limit:15)
  🟡 CC    _load_flow_outcomes CC=15 (limit:15)
  🟡 CC    analyze_run CC=39 (limit:15)
  🟡 CC    shell_run CC=16 (limit:15)
  🟡 CC    open_page CC=15 (limit:15)
  🟡 CC    analyze CC=18 (limit:15)
  🟡 CC    decide CC=23 (limit:15)
  🟡 CC    uri_execute CC=15 (limit:15)
  🟡 CC    build_lab_runtime CC=17 (limit:15)
  🟡 CC    do_POST CC=23 (limit:15)
  🟡 CC    main CC=16 (limit:15)

REFACTOR[3]:
  1. rm duplicates  (-2 dup classes)
  2. split scripts/session_report.py  (god module)
  3. split 18 high-CC methods  (CC>15)

PIPELINES[273]:
  [1] Src [compile]: compile
      PURITY: 100% pure
  [2] Src [match]: match
      PURITY: 100% pure
  [3] Src [__init__]: __init__
      PURITY: 100% pure
  [4] Src [append]: append
      PURITY: 100% pure
  [5] Src [tail]: tail
      PURITY: 100% pure
  [6] Src [__init__]: __init__
      PURITY: 100% pure
  [7] Src [register]: register
      PURITY: 100% pure
  [8] Src [resolve]: resolve
      PURITY: 100% pure
  [9] Src [_load_handler]: _load_handler
      PURITY: 100% pure
  [10] Src [call]: call → load_env_policy → _env_policy_candidates → _urisys_root
      PURITY: 100% pure
  [11] Src [registry]: registry
      PURITY: 100% pure
  [12] Src [runtime]: runtime
      PURITY: 100% pure
  [13] Src [out]: out
      PURITY: 100% pure
  [14] Src [result]: result
      PURITY: 100% pure
  [15] Src [client]: client
      PURITY: 100% pure
  [16] Src [main]: main → build_parser → _add_runtime_flags
      PURITY: 100% pure
  [17] Src [__init__]: __init__
      PURITY: 100% pure
  [18] Src [run]: run → load_flow
      PURITY: 100% pure
  [19] Src [close]: close
      PURITY: 100% pure
  [20] Src [__init__]: __init__ → create_server → _send
      PURITY: 100% pure
  [21] Src [serve_forever]: serve_forever → print
      PURITY: 100% pure
  [22] Src [__init__]: __init__
      PURITY: 100% pure
  [23] Src [call]: call
      PURITY: 100% pure
  [24] Src [explain]: explain
      PURITY: 100% pure
  [25] Src [routes]: routes
      PURITY: 100% pure
  [26] Src [close]: close
      PURITY: 100% pure
  [27] Src [__init__]: __init__
      PURITY: 100% pure
  [28] Src [list_events]: list_events
      PURITY: 100% pure
  [29] Src [build_context]: build_context
      PURITY: 100% pure
  [30] Src [explain]: explain
      PURITY: 100% pure
  [31] Src [__init__]: __init__
      PURITY: 100% pure
  [32] Src [create_runtime]: create_runtime
      PURITY: 100% pure
  [33] Src [close]: close
      PURITY: 100% pure
  [34] Src [__exit__]: __exit__
      PURITY: 100% pure
  [35] Src [call_http]: call_http
      PURITY: 100% pure
  [36] Src [__init__]: __init__
      PURITY: 100% pure
  [37] Src [_is_all]: _is_all
      PURITY: 100% pure
  [38] Src [parse_packs]: parse_packs
      PURITY: 100% pure
  [39] Src [parse_markpacts]: parse_markpacts
      PURITY: 100% pure
  [40] Src [resolve_package_name]: resolve_package_name
      PURITY: 100% pure
  [41] Src [_is_markpact_path]: _is_markpact_path
      PURITY: 100% pure
  [42] Src [_is_manifest_path]: _is_manifest_path
      PURITY: 100% pure
  [43] Src [create_registry]: create_registry
      PURITY: 100% pure
  [44] Src [capabilities]: capabilities
      PURITY: 100% pure
  [45] Src [close]: close
      PURITY: 100% pure
  [46] Src [__exit__]: __exit__
      PURITY: 100% pure
  [47] Src [__init__]: __init__
      PURITY: 100% pure
  [48] Src [is_remote_source]: is_remote_source
      PURITY: 100% pure
  [49] Src [resolve]: resolve
      PURITY: 100% pure
  [50] Src [fetch]: fetch
      PURITY: 100% pure

LAYERS:
  scripts/                        CC̄=6.8    ←in:49  →out:0
  │ !! run_test_sessions         1218L  0C   38m  CC=36     ←0
  │ !! session_report             801L  5C   23m  CC=39     ←0
  │ run-urisys-node-docker-e2e.sh   136L  0C    4m  CC=0.0    ←0
  │ paths.sh                    54L  0C    6m  CC=0.0    ←0
  │ validate-all-markpacts.sh    53L  0C    0m  CC=0.0    ←0
  │ run-nl-log-smoke.sh         43L  0C    1m  CC=0.0    ←17
  │ run-smoke-all.sh            22L  0C    0m  CC=0.0    ←0
  │ run-lab-unit-ci.sh          19L  0C    0m  CC=0.0    ←0
  │ run-lab-e2e.sh              14L  0C    0m  CC=0.0    ←0
  │ test-goal.sh                11L  0C    0m  CC=0.0    ←0
  │
  src/                            CC̄=4.8    ←in:0  →out:0
  │ !! markpact_manager           385L  1C   18m  CC=28     ←0
  │ source_manager             224L  2C   11m  CC=11     ←0
  │ !! cli                        183L  0C    6m  CC=20     ←0
  │ !! markpact_validation        140L  0C    3m  CC=23     ←1
  │ !! pack_manager               128L  1C   13m  CC=15     ←1
  │ markpact_models             92L  3C    5m  CC=4      ←1
  │ http_server                 78L  0C    3m  CC=3      ←1
  │ flow_controller             33L  1C    3m  CC=6      ←0
  │ uri_controller              33L  1C    5m  CC=3      ←0
  │ runtime_manager             30L  1C    5m  CC=2      ←0
  │ flow                        25L  0C    2m  CC=7      ←1
  │ route_manager               23L  1C    3m  CC=2      ←0
  │ server_controller           18L  1C    2m  CC=1      ←0
  │ policy_manager              18L  1C    1m  CC=2      ←0
  │ defaults                    18L  0C    0m  CC=0.0    ←0
  │ bridge_manager              14L  1C    1m  CC=3      ←0
  │ event_manager               13L  1C    2m  CC=1      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  packages/                       CC̄=4.4    ←in:0  →out:0  ×DUP
  │ runtime                    270L  3C   16m  CC=14     ←10  ×DUP
  │ env                        129L  0C    7m  CC=11     ←7
  │ __init__                    12L  0C    0m  CC=0.0    ←0
  │
  urirdp-docker/                  CC̄=4.2    ←in:0  →out:0
  │ !! handlers                   314L  0C   17m  CC=23     ←0
  │ !! handlers                   171L  0C    7m  CC=15     ←0
  │ handlers                   144L  0C    7m  CC=10     ←1
  │ handlers                   133L  0C    5m  CC=10     ←0
  │ bootstrap-rdp-session.sh   111L  0C    7m  CC=0.0    ←0
  │ cli                         98L  0C    2m  CC=10     ←0
  │ handlers                    79L  0C    5m  CC=9      ←0
  │ handlers                    72L  0C    7m  CC=11     ←0
  │ display                     63L  0C    6m  CC=7      ←6
  │ test-real-docker.sh         63L  0C    1m  CC=0.0    ←0
  │ !! handlers                    57L  0C    2m  CC=16     ←0
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
  urikvm-docker/                  CC̄=3.7    ←in:0  →out:0
  │ !! handlers                   216L  0C   15m  CC=16     ←0
  │ handlers                   115L  0C   10m  CC=8      ←0
  │ handlers                   103L  0C    6m  CC=8      ←0
  │ real_pipeline               95L  0C    4m  CC=14     ←0
  │ handlers                    81L  0C    9m  CC=7      ←0
  │ cli                         56L  0C    2m  CC=7      ←0
  │ pyproject.toml              51L  0C    0m  CC=0.0    ←0
  │ test-real.sh                47L  0C    1m  CC=0.0    ←0
  │ kvm-profile.json            26L  0C    0m  CC=0.0    ←0
  │ kvm-profile.real.json       24L  0C    0m  CC=0.0    ←0
  │ kvm-click-ok.uri.flow.yaml    20L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   8L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ routes                       6L  0C    1m  CC=1      ←0
  │ routes                       5L  0C    1m  CC=1      ←0
  │ call-http.sh                 5L  0C    0m  CC=0.0    ←0
  │ routes                       3L  0C    1m  CC=1      ←0
  │ routes                       2L  0C    1m  CC=1      ←0
  │
  urienv-docker/                  CC̄=3.6    ←in:0  →out:0
  │ handlers                   196L  0C   19m  CC=7      ←2
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
  urisys-node/                    CC̄=3.4    ←in:0  →out:0  ×DUP
  │ runtime                    269L  3C   16m  CC=14     ←0  ×DUP
  │ !! artifact_resolver          225L  1C   15m  CC=15     ←1
  │ !! cli                        170L  0C    1m  CC=16     ←0
  │ env                        129L  0C    7m  CC=11     ←0
  │ serve                      125L  0C    5m  CC=6      ←0
  │ identity                   110L  0C   12m  CC=4      ←3
  │ handlers                   102L  0C    9m  CC=7      ←0
  │ client                      92L  0C    3m  CC=6      ←1
  │ pyproject.toml              87L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               63L  0C    3m  CC=0.0    ←0
  │ Dockerfile.gui              51L  0C    0m  CC=0.0    ←0
  │ router                      47L  0C    5m  CC=6      ←2
  │ handlers                    41L  0C    4m  CC=2      ←0
  │ docker-compose.gui.yml      33L  0C    0m  CC=0.0    ←0
  │ node-profile.json           32L  0C    0m  CC=0.0    ←0
  │ routes                      23L  0C    1m  CC=1      ←0
  │ route-map.host.yaml         23L  0C    0m  CC=0.0    ←0
  │ routes                      19L  0C    1m  CC=1      ←0
  │ route-map.master.yaml       19L  0C    0m  CC=0.0    ←0
  │ node-profile.docker.json    16L  0C    0m  CC=0.0    ←0
  │ install-linux.sh            16L  0C    0m  CC=0.0    ←0
  │ route-map.slave.yaml        14L  0C    0m  CC=0.0    ←0
  │ slave-kvm-demo.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ __init__                    12L  0C    0m  CC=0.0    ←0
  │ screen-capture-mss.uri.flow.yaml    12L  0C    0m  CC=0.0    ←0
  │ nodes.registry.json         10L  0C    0m  CC=0.0    ←0
  │ nodes.registry.host.json     9L  0C    0m  CC=0.0    ←0
  │ runtime                      5L  0C    0m  CC=0.0    ←0
  │ env                          5L  0C    0m  CC=0.0    ←0
  │
  uribrowser-docker/              CC̄=3.1    ←in:0  →out:0
  │ handlers                    87L  0C    6m  CC=11     ←0
  │ pyproject.toml              50L  0C    0m  CC=0.0    ←0
  │ cli                         49L  0C    2m  CC=7      ←0
  │ test-real.sh                28L  0C    0m  CC=0.0    ←0
  │ browser-demo.uri.flow.yaml    14L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ browser-profile.json        10L  0C    0m  CC=0.0    ←0
  │ browser-profile.real.json     9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   8L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ routes                       5L  0C    1m  CC=1      ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  uristepper-docker/              CC̄=2.2    ←in:0  →out:0
  │ runtime                    169L  4C    9m  CC=6      ←5
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
  │
  examples/                       CC̄=1.0    ←in:0  →out:0
  │ app.js                      21L  0C    5m  CC=1      ←0
  │ browser-call.sh             12L  0C    0m  CC=0.0    ←0
  │ server-curl.sh               8L  0C    0m  CC=0.0    ←0
  │ call-uri.sh                  6L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml             1319L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             106L  0C    0m  CC=0.0    ←0
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
  │ device-maintenance.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     src/urisys/controllers/__init__.py        0L

COUPLING:
                                                     scripts               packages.python          urisys-node.packages        urirdp-docker.packages        urienv-docker.packages        urikvm-docker.packages    uristepper-docker.packages  urisys-automation-lab.server    uribrowser-docker.packages                    src.urisys         urikvm-docker.scripts
                       scripts                            ──                            ←3                           ←18                            ←2                            ←5                            ←2                            ←7                            ←5                            ←2                            ←3                            ←2  hub
               packages.python                             3                            ──                            ←5                           ←14                             2                           ←11                            ←1                            ←1                            ←3                                                          ←1  hub
          urisys-node.packages                            18                             5                            ──                                                           2                                                           2                                                                                                                          !! fan-out
        urirdp-docker.packages                             2                            14                                                          ──                                                                                                                                                                                                                    !! fan-out
        urienv-docker.packages                             5                             2                            ←2                                                          ──                                                           2                                                                                         1                                !! fan-out
        urikvm-docker.packages                             2                            11                                                                                                                      ──                                                                                                                                                        !! fan-out
    uristepper-docker.packages                             7                             1                            ←2                                                          ←2                                                          ──                                                                                                                          !! fan-out
  urisys-automation-lab.server                             5                             1                                                                                                                                                                                  ──                                                                                          
    uribrowser-docker.packages                             2                             3                                                                                                                                                                                                                ──                                                            
                    src.urisys                             3                                                                                                                      ←1                                                                                                                                                    ──                              
         urikvm-docker.scripts                             2                             1                                                                                                                                                                                                                                                                            ──
  CYCLES: none
  HUB: scripts/ (fan-in=49)
  HUB: packages.python/ (fan-in=38)
  SMELL: uristepper-docker.packages/ fan-out=8 → split needed
  SMELL: urikvm-docker.packages/ fan-out=13 → split needed
  SMELL: urirdp-docker.packages/ fan-out=16 → split needed
  SMELL: urisys-node.packages/ fan-out=27 → split needed
  SMELL: urienv-docker.packages/ fan-out=10 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 26f 2905L | 2026-06-16

SUMMARY:
  files_scanned: 26
  total_lines:   2905
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       2080
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 459 func | 86f | 2026-06-16
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !  SPLIT-FUNC      MarkpactManager.compile  CC=21  fan=34
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 714

  [2] !  SPLIT-FUNC      main  CC=16  fan=41
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 656

  [3] !  SPLIT-FUNC      main  CC=20  fan=28
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 560

  [4] !! SPLIT-FUNC      MarkpactManager._compile_manifest  CC=28  fan=17
      WHY: CC=28 exceeds 15
      EFFORT: ~1h  IMPACT: 476

  [5] !  SPLIT-FUNC      decide  CC=23  fan=19
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 437

  [6] !  SPLIT-FUNC      MarkpactManager.run_tests  CC=20  fan=21
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 420

  [7] !  SPLIT-FUNC      analyze  CC=18  fan=19
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 342

  [8] !  SPLIT-FUNC      open_page  CC=15  fan=22
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 330

  [9] !  SPLIT-FUNC      build_lab_runtime  CC=17  fan=19
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 323

  [10] !  SPLIT-FUNC      LabHandler.do_POST  CC=23  fan=11
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 253


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.8 → ≤2.7
  max-CC:      28 → ≤14
  god-modules: 2 → 0
  high-CC(≥15): 17 → ≤8
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
  prev CC̄=3.8 → now CC̄=3.8
```

## Intent

URI control system managers/controllers over separate uri* capability packs.
