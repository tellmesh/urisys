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
- **version**: `0.1.8`
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
  version: 0.1.8;
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

## Dependencies

### Runtime

```text markpact:deps python
uricore>=0.1.0
PyYAML>=6.0
```

## Call Graph

*303 nodes · 371 edges · 60 modules · CC̄=3.9*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `session_urirdp_real_docker` *(in scripts.run_test_sessions)* | 30 ⚠ | 0 | 69 | **69** |
| `analyze_run` *(in scripts.session_report)* | 34 ⚠ | 2 | 64 | **66** |
| `session_lab_10_flows` *(in scripts.run_test_sessions)* | 26 ⚠ | 0 | 56 | **56** |
| `write_session_report` *(in scripts.session_report)* | 28 ⚠ | 2 | 50 | **52** |
| `compile` *(in src.urisys.managers.markpact_manager.MarkpactManager)* | 21 ⚠ | 0 | 46 | **46** |
| `main` *(in src.urisys.cli)* | 18 ⚠ | 0 | 44 | **44** |
| `make_handler` *(in uristepper-docker.packages.python.urisysedge.server)* | 1 | 1 | 43 | **44** |
| `session_automation_lab` *(in scripts.run_test_sessions)* | 16 ⚠ | 1 | 43 | **44** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.15s
# nodes: 303 | edges: 371 | modules: 60
# CC̄=3.9

HUBS[20]:
  scripts.run_test_sessions.session_urirdp_real_docker
    CC=30  in:0  out:69  total:69
  scripts.session_report.analyze_run
    CC=34  in:2  out:64  total:66
  scripts.run_test_sessions.session_lab_10_flows
    CC=26  in:0  out:56  total:56
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
  scripts.run_test_sessions._run_cmd
    CC=5  in:26  out:11  total:37
  scripts.session_report.generate_report
    CC=13  in:2  out:35  total:37
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
  urienv-docker.vendor.uricore.core.python.uri_control.dispatcher.UriControlRuntime.call
    CC=10  in:0  out:31  total:31
  scripts.run_test_sessions.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  urisys-node.packages.python.urisysnode.serve.make_handler
    CC=1  in:1  out:30  total:31

MODULES:
  scripts.run_test_sessions  [25 funcs]
    _capture_rdp_screenshot  CC=5  out:6
    _compose_cmd  CC=4  out:4
    _copy_container_file  CC=2  out:4
    _docker_logs  CC=4  out:5
    _finalize_session  CC=5  out:13
    _host_id  CC=1  out:3
    _http_json  CC=9  out:18
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
  urikvm-docker.packages.python.urikvmedge.env  [6 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    is_secret_env  CC=1  out:1
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=7  out:16
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
  urirdp-docker.packages.python.urirdp_browser.handlers  [4 funcs]
    _chromium_binary  CC=4  out:3
    _profile  CC=1  out:2
    _session_state  CC=1  out:5
    open_page  CC=14  out:30
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
    shell_run  CC=16  out:18
  urirdp-docker.packages.python.urirdpedge.cli  [1 funcs]
    build_runtime  CC=10  out:16
  urirdp-docker.packages.python.urirdpedge.env  [4 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:8
    load_env_policy  CC=6  out:5
    resolve_env_var  CC=11  out:9
  urirdp-docker.packages.python.urirdpedge.runtime  [5 funcs]
    call  CC=10  out:23
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
  urisys-automation-lab.server.flow_runner  [7 funcs]
    _expand_graph  CC=8  out:8
    _load_flow_document  CC=11  out:19
    _node_id  CC=4  out:8
    _parse_step  CC=9  out:23
    _topo_sort  CC=15  out:8
    plan_flow  CC=2  out:6
    run_flow_file  CC=17  out:29
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
  scripts.session_report.generate_report → scripts.session_report._infer_steps
  scripts.session_report.generate_report → scripts.session_report._read_json
  scripts.session_report.generate_report → scripts.session_report._tail
  scripts.session_report.write_session_report → scripts.session_report.generate_report
  scripts.session_report.analyze_run → scripts.session_report._read_json
  scripts.session_report.write_run_analysis → scripts.session_report.analyze_run
  scripts.session_report.main → scripts.session_report.analyze_run
  scripts.session_report.main → scripts.session_report.write_run_analysis
  urirdp-docker.packages.python.urirdp_ocr.handlers._tesseract_ocr → urirdp-docker.packages.python.urirdp_kvm.display.run_cmd
  urirdp-docker.packages.python.urirdp_ocr.handlers._tesseract_ocr → urirdp-docker.packages.python.urirdp_ocr.handlers._parse_tesseract_tsv
  urirdp-docker.packages.python.urirdp_ocr.handlers.latest_text → urirdp-docker.packages.python.urirdp_ocr.handlers.image_text
  urirdp-docker.packages.python.urirdp_ocr.handlers.image_text → urirdp-docker.packages.python.urirdp_ocr.handlers._tesseract_ocr
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
# nodes: 303 | edges: 371 | modules: 60
# CC̄=3.9

HUBS[20]:
  scripts.run_test_sessions.session_urirdp_real_docker
    CC=30  in:0  out:69  total:69
  scripts.session_report.analyze_run
    CC=34  in:2  out:64  total:66
  scripts.run_test_sessions.session_lab_10_flows
    CC=26  in:0  out:56  total:56
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
  scripts.run_test_sessions._run_cmd
    CC=5  in:26  out:11  total:37
  scripts.session_report.generate_report
    CC=13  in:2  out:35  total:37
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
  urienv-docker.vendor.uricore.core.python.uri_control.dispatcher.UriControlRuntime.call
    CC=10  in:0  out:31  total:31
  scripts.run_test_sessions.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  urisys-node.packages.python.urisysnode.serve.make_handler
    CC=1  in:1  out:30  total:31

MODULES:
  scripts.run_test_sessions  [25 funcs]
    _capture_rdp_screenshot  CC=5  out:6
    _compose_cmd  CC=4  out:4
    _copy_container_file  CC=2  out:4
    _docker_logs  CC=4  out:5
    _finalize_session  CC=5  out:13
    _host_id  CC=1  out:3
    _http_json  CC=9  out:18
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
  urikvm-docker.packages.python.urikvmedge.env  [6 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    is_secret_env  CC=1  out:1
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=7  out:16
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
  urirdp-docker.packages.python.urirdp_browser.handlers  [4 funcs]
    _chromium_binary  CC=4  out:3
    _profile  CC=1  out:2
    _session_state  CC=1  out:5
    open_page  CC=14  out:30
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
    shell_run  CC=16  out:18
  urirdp-docker.packages.python.urirdpedge.cli  [1 funcs]
    build_runtime  CC=10  out:16
  urirdp-docker.packages.python.urirdpedge.env  [4 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:8
    load_env_policy  CC=6  out:5
    resolve_env_var  CC=11  out:9
  urirdp-docker.packages.python.urirdpedge.runtime  [5 funcs]
    call  CC=10  out:23
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
  urisys-automation-lab.server.flow_runner  [7 funcs]
    _expand_graph  CC=8  out:8
    _load_flow_document  CC=11  out:19
    _node_id  CC=4  out:8
    _parse_step  CC=9  out:23
    _topo_sort  CC=15  out:8
    plan_flow  CC=2  out:6
    run_flow_file  CC=17  out:29
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
  scripts.session_report.generate_report → scripts.session_report._infer_steps
  scripts.session_report.generate_report → scripts.session_report._read_json
  scripts.session_report.generate_report → scripts.session_report._tail
  scripts.session_report.write_session_report → scripts.session_report.generate_report
  scripts.session_report.analyze_run → scripts.session_report._read_json
  scripts.session_report.write_run_analysis → scripts.session_report.analyze_run
  scripts.session_report.main → scripts.session_report.analyze_run
  scripts.session_report.main → scripts.session_report.write_run_analysis
  urirdp-docker.packages.python.urirdp_ocr.handlers._tesseract_ocr → urirdp-docker.packages.python.urirdp_kvm.display.run_cmd
  urirdp-docker.packages.python.urirdp_ocr.handlers._tesseract_ocr → urirdp-docker.packages.python.urirdp_ocr.handlers._parse_tesseract_tsv
  urirdp-docker.packages.python.urirdp_ocr.handlers.latest_text → urirdp-docker.packages.python.urirdp_ocr.handlers.image_text
  urirdp-docker.packages.python.urirdp_ocr.handlers.image_text → urirdp-docker.packages.python.urirdp_ocr.handlers._tesseract_ocr
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 243f 14958L | python:112,shell:41,yaml:36,json:16,yml:9,toml:9,javascript:2,txt:2,proto:2,go:1,php:1,typescript:1,conf:1 | 2026-06-16
# generated in 0.04s
# CC̅=3.9 | critical:26/581 | dups:11 | cycles:0

HEALTH[20]:
  🔴 DUP   11 classes duplicated
  🔴 GOD   src/urisys/managers/markpact_manager.py = 579L, 4 classes, 25m, max CC=28
  🟡 CC    main CC=18 (limit:15)
  🟡 CC    parse_packs CC=15 (limit:15)
  🟡 CC    _summarize_events CC=18 (limit:15)
  🟡 CC    _infer_steps CC=20 (limit:15)
  🟡 CC    write_session_report CC=28 (limit:15)
  🟡 CC    analyze_run CC=34 (limit:15)
  🟡 CC    analyze CC=18 (limit:15)
  🟡 CC    _heuristic_analyze CC=16 (limit:15)
  🟡 CC    _vision_analyze CC=22 (limit:15)
  🟡 CC    uri_execute CC=15 (limit:15)
  🟡 CC    load_manifest CC=21 (limit:15)
  🟡 CC    main CC=16 (limit:15)
  🟡 CC    _topo_sort CC=15 (limit:15)
  🟡 CC    run_flow_file CC=17 (limit:15)
  🟡 CC    shell_run CC=16 (limit:15)
  🟡 CC    session_urirdp_real_docker CC=30 (limit:15)
  🟡 CC    session_automation_lab CC=16 (limit:15)
  🟡 CC    session_lab_10_flows CC=26 (limit:15)

REFACTOR[3]:
  1. rm duplicates  (-11 dup classes)
  2. split src/urisys/managers/markpact_manager.py  (god module)
  3. split 18 high-CC methods  (CC>15)

PIPELINES[324]:
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
  [6] Src [main]: main → build_parser → _add_runtime_flags
      PURITY: 100% pure
  [7] Src [__init__]: __init__
      PURITY: 100% pure
  [8] Src [run]: run → load_flow
      PURITY: 100% pure
  [9] Src [close]: close
      PURITY: 100% pure
  [10] Src [__init__]: __init__ → create_server → _send
      PURITY: 100% pure
  [11] Src [serve_forever]: serve_forever
      PURITY: 100% pure
  [12] Src [__init__]: __init__
      PURITY: 100% pure
  [13] Src [call]: call
      PURITY: 100% pure
  [14] Src [explain]: explain
      PURITY: 100% pure
  [15] Src [routes]: routes
      PURITY: 100% pure
  [16] Src [close]: close
      PURITY: 100% pure
  [17] Src [__init__]: __init__
      PURITY: 100% pure
  [18] Src [list_events]: list_events → dump_events
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
  [25] Src [call_http]: call_http
      PURITY: 100% pure
  [26] Src [__init__]: __init__
      PURITY: 100% pure
  [27] Src [parse_packs]: parse_packs
      PURITY: 100% pure
  [28] Src [parse_markpacts]: parse_markpacts
      PURITY: 100% pure
  [29] Src [resolve_package_name]: resolve_package_name
      PURITY: 100% pure
  [30] Src [_is_markpact_path]: _is_markpact_path
      PURITY: 100% pure
  [31] Src [_is_manifest_path]: _is_manifest_path
      PURITY: 100% pure
  [32] Src [create_registry]: create_registry
      PURITY: 100% pure
  [33] Src [capabilities]: capabilities
      PURITY: 100% pure
  [34] Src [close]: close
      PURITY: 100% pure
  [35] Src [__exit__]: __exit__
      PURITY: 100% pure
  [36] Src [__init__]: __init__
      PURITY: 100% pure
  [37] Src [is_remote_source]: is_remote_source
      PURITY: 100% pure
  [38] Src [resolve]: resolve
      PURITY: 100% pure
  [39] Src [fetch]: fetch
      PURITY: 100% pure
  [40] Src [_result]: _result
      PURITY: 100% pure
  [41] Src [_cache_dir]: _cache_dir
      PURITY: 100% pure
  [42] Src [_fetch_http]: _fetch_http
      PURITY: 100% pure
  [43] Src [_fetch_github_uri]: _fetch_github_uri
      PURITY: 100% pure
  [44] Src [_fetch_github_raw]: _fetch_github_raw
      PURITY: 100% pure
  [45] Src [_fetch_git]: _fetch_git
      PURITY: 100% pure
  [46] Src [_fetch_zip]: _fetch_zip
      PURITY: 100% pure
  [47] Src [move_absolute]: move_absolute
      PURITY: 100% pure
  [48] Src [__init__]: __init__
      PURITY: 100% pure
  [49] Src [_load]: _load
      PURITY: 100% pure
  [50] Src [_save]: _save
      PURITY: 100% pure

LAYERS:
  scripts/                        CC̄=7.5    ←in:0  →out:0
  │ !! run_test_sessions         1031L  0C   33m  CC=30     ←0
  │ !! session_report             509L  3C   13m  CC=34     ←0
  │ validate-all-markpacts.sh    40L  0C    0m  CC=0.0    ←0
  │ test-goal.sh                11L  0C    0m  CC=0.0    ←0
  │
  src/                            CC̄=4.8    ←in:0  →out:0
  │ !! markpact_manager           579L  4C   25m  CC=28     ←0
  │ source_manager             224L  2C   11m  CC=11     ←0
  │ !! cli                        176L  0C    6m  CC=18     ←0
  │ !! pack_manager                97L  1C   12m  CC=15     ←1
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
  urisys-automation-lab/          CC̄=4.2    ←in:0  →out:0  ×DUP
  │ !! automation_lab_server      243L  1C    9m  CC=23     ←0
  │ !! flow_runner                221L  0C    9m  CC=17     ←1
  │ runtime                    164L  3C   11m  CC=8      ←1  ×DUP
  │ app.js                     131L  0C   17m  CC=2      ←0
  │ !! handlers                    81L  0C    4m  CC=15     ←0
  │ docker-compose.lab.yml      66L  0C    0m  CC=0.0    ←0
  │ handlers                    57L  0C    4m  CC=5      ←0
  │ 10_full_maintenance_rdp.uri.flow.yaml    37L  0C    0m  CC=0.0    ←0
  │ handlers                    35L  0C    3m  CC=4      ←0
  │ Dockerfile                  34L  0C    0m  CC=0.0    ←0
  │ local-rdp.routes.yaml       29L  0C    0m  CC=0.0    ←0
  │ validate-flows.sh           28L  0C    0m  CC=0.0    ←0
  │ routes                      23L  0C    1m  CC=1      ←0
  │ 07_edit_config_nano_tui.uri.flow.yaml    22L  0C    0m  CC=0.0    ←0
  │ docker-up.sh                21L  0C    0m  CC=0.0    ←0
  │ docker-smoke.sh             20L  0C    0m  CC=0.0    ←0
  │ 09_webrtc_video_chat_rdp.uri.flow.yaml    19L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               18L  0C    0m  CC=0.0    ←0
  │ 05_fill_form_gui.uri.flow.yaml    18L  0C    0m  CC=0.0    ←0
  │ 08_voice_command_to_kvm.uri.flow.yaml    18L  0C    0m  CC=0.0    ←0
  │ 06_terminal_htop_tui.uri.flow.yaml    18L  0C    0m  CC=0.0    ←0
  │ routes                      17L  0C    1m  CC=1      ←0
  │ routes                      17L  0C    1m  CC=1      ←0
  │ 02_update_system_tui.uri.flow.yaml    15L  0C    0m  CC=0.0    ←0
  │ run-lab.sh                  13L  0C    0m  CC=0.0    ←0
  │ 04_browser_download_file.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ 01_install_browser.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ 03_open_browser_gui.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ docker-logs.sh               6L  0C    0m  CC=0.0    ←0
  │ docker-down.sh               6L  0C    0m  CC=0.0    ←0
  │ static_server                6L  0C    0m  CC=0.0    ←0
  │
  urirdp-docker/                  CC̄=3.9    ←in:0  →out:0  ×DUP
  │ runtime                    255L  3C   15m  CC=14     ←0  ×DUP
  │ !! handlers                   196L  0C   12m  CC=18     ←0
  │ handlers                   133L  0C    5m  CC=10     ←0
  │ env                        125L  0C    6m  CC=11     ←0
  │ handlers                   124L  0C    6m  CC=14     ←0
  │ bootstrap-rdp-session.sh   111L  0C    7m  CC=0.0    ←0
  │ cli                         98L  0C    2m  CC=10     ←0
  │ handlers                    89L  0C    5m  CC=7      ←0
  │ handlers                    79L  0C    5m  CC=9      ←0
  │ handlers                    72L  0C    7m  CC=11     ←0
  │ display                     63L  0C    6m  CC=7      ←6
  │ test-real-docker.sh         63L  0C    1m  CC=0.0    ←0
  │ !! handlers                    57L  0C    2m  CC=16     ←0
  │ pyproject.toml              50L  0C    0m  CC=0.0    ←0
  │ routes                      45L  0C    1m  CC=3      ←0
  │ docker-compose.rdp-e2e.yml    41L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  40L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-profile.real.json    39L  0C    0m  CC=0.0    ←0
  │ routes                      35L  0C    1m  CC=3      ←0
  │ supervisord.conf            35L  0C    0m  CC=0.0    ←0
  │ env-policy.yaml             31L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-profile.json        30L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh               25L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          24L  0C    0m  CC=0.0    ←0
  │ Makefile                    20L  0C    0m  CC=0.0    ←0
  │ test-docker.sh              17L  0C    0m  CC=0.0    ←0
  │ rdp-kvm-smoke.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ real-rdp-click-text.uri.flow.yaml    14L  0C    0m  CC=0.0    ←0
  │ routes                      12L  0C    1m  CC=1      ←0
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
  │ routes                       3L  0C    1m  CC=1      ←0
  │ __init__                     3L  0C    1m  CC=1      ←0
  │ routes                       2L  0C    1m  CC=1      ←0
  │
  urikvm-docker/                  CC̄=3.9    ←in:0  →out:0  ×DUP
  │ runtime                    228L  3C   14m  CC=10     ←0  ×DUP
  │ !! handlers                   201L  0C   13m  CC=22     ←0
  │ env                        115L  0C    6m  CC=11     ←7
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
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ routes                       6L  0C    1m  CC=1      ←0
  │ Dockerfile                   6L  0C    0m  CC=0.0    ←0
  │ routes                       5L  0C    1m  CC=1      ←0
  │ call-http.sh                 5L  0C    0m  CC=0.0    ←0
  │ routes                       3L  0C    1m  CC=1      ←0
  │ routes                       2L  0C    1m  CC=1      ←0
  │
  uribrowser-docker/              CC̄=3.3    ←in:0  →out:0  ×DUP
  │ runtime                    222L  3C   14m  CC=10     ←4  ×DUP
  │ handlers                    87L  0C    6m  CC=11     ←0
  │ pyproject.toml              50L  0C    0m  CC=0.0    ←0
  │ cli                         49L  0C    2m  CC=7      ←0
  │ test-real.sh                28L  0C    0m  CC=0.0    ←0
  │ browser-demo.uri.flow.yaml    14L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ browser-profile.json        10L  0C    0m  CC=0.0    ←0
  │ browser-profile.real.json     9L  0C    0m  CC=0.0    ←0
  │ test-local.sh                8L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   6L  0C    0m  CC=0.0    ←0
  │ routes                       5L  0C    1m  CC=1      ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  urisys-node/                    CC̄=3.3    ←in:0  →out:0  ×DUP
  │ !! artifact_resolver          225L  1C   15m  CC=15     ←1
  │ !! cli                        170L  0C    1m  CC=16     ←0
  │ runtime                    165L  3C   11m  CC=8      ←0  ×DUP
  │ identity                   110L  0C   12m  CC=4      ←3
  │ serve                      107L  0C    4m  CC=11     ←0
  │ handlers                   102L  0C    9m  CC=7      ←0
  │ client                      92L  0C    3m  CC=6      ←1
  │ pyproject.toml              57L  0C    0m  CC=0.0    ←0
  │ router                      47L  0C    5m  CC=6      ←2
  │ handlers                    41L  0C    4m  CC=2      ←0
  │ node-profile.json           32L  0C    0m  CC=0.0    ←0
  │ routes                      23L  0C    1m  CC=1      ←0
  │ env                         22L  0C    1m  CC=8      ←0
  │ routes                      19L  0C    1m  CC=1      ←0
  │ route-map.master.yaml       19L  0C    0m  CC=0.0    ←0
  │ install-linux.sh            16L  0C    0m  CC=0.0    ←0
  │ route-map.slave.yaml        14L  0C    0m  CC=0.0    ←0
  │ slave-kvm-demo.uri.flow.yaml    13L  0C    0m  CC=0.0    ←0
  │ screen-capture-mss.uri.flow.yaml    12L  0C    0m  CC=0.0    ←0
  │ nodes.registry.json         10L  0C    0m  CC=0.0    ←0
  │
  urienv-docker/                  CC̄=3.2    ←in:0  →out:0
  │ !! registry                   202L  1C    9m  CC=21     ←0
  │ handlers                   196L  0C   19m  CC=7      ←2
  │ dispatcher                 167L  1C    4m  CC=10     ←0
  │ models                     127L  7C    2m  CC=3      ←0
  │ cli                        123L  0C    9m  CC=3      ←0
  │ policy                      71L  1C    2m  CC=9      ←0
  │ projection                  70L  1C    5m  CC=6      ←0
  │ manifest.yaml               67L  0C    0m  CC=0.0    ←0
  │ event_store                 65L  3C    9m  CC=6      ←1
  │ docker-compose.yml          52L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              50L  0C    0m  CC=0.0    ←0
  │ handlers                    45L  0C    2m  CC=6      ←0
  │ parser                      45L  0C    2m  CC=7      ←1
  │ __init__                    37L  0C    0m  CC=0.0    ←0
  │ env-policy.yaml             36L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  33L  0C    0m  CC=0.0    ←0
  │ envelope.proto              31L  0C    0m  CC=0.0    ←0
  │ call_browser_mock           30L  0C    0m  CC=0.0    ←0
  │ handlers                    28L  0C    2m  CC=3      ←0
  │ cli                         26L  0C    2m  CC=10     ←0
  │ server                      26L  0C    1m  CC=1      ←0
  │ manifest.yaml               25L  0C    0m  CC=0.0    ←0
  │ manifest.yaml               25L  0C    0m  CC=0.0    ←0
  │ browser.proto               24L  0C    0m  CC=0.0    ←0
  │ errors                      22L  6C    0m  CC=0.0    ←0
  │ call_systemd_mock           22L  0C    0m  CC=0.0    ←0
  │ runtime                     21L  0C    4m  CC=3      ←3
  │ pyproject.toml              20L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              19L  0C    0m  CC=0.0    ←0
  │ flow                        16L  0C    1m  CC=12     ←0
  │ mutate-process-env.uri.flow.yaml    16L  0C    0m  CC=0.0    ←0
  │ Makefile                    16L  0C    0m  CC=0.0    ←0
  │ pack_loader                 15L  0C    2m  CC=4      ←0
  │ startup-env-check.uri.flow.yaml    15L  0C    0m  CC=0.0    ←0
  │ composer.json               13L  0C    0m  CC=0.0    ←0
  │ uricontrol.go               11L  1C    1m  CC=1      ←0
  │ UriControl.php              11L  1C    1m  CC=1      ←0
  │ pyproject.toml              11L  0C    0m  CC=0.0    ←0
  │ package.json                11L  0C    0m  CC=0.0    ←0
  │ index.ts                     9L  0C    1m  CC=1      ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │ test-docker.sh               4L  0C    0m  CC=0.0    ←0
  │ local-test.sh                4L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ smtp_password.txt            1L  0C    0m  CC=0.0    ←0
  │ markpact_token.txt           1L  0C    0m  CC=0.0    ←0
  │
  uristepper-docker/              CC̄=2.2    ←in:0  →out:0  ×DUP
  │ runtime                    193L  5C   12m  CC=6      ←11  ×DUP
  │ drivers                    169L  3C   30m  CC=4      ←1
  │ cli                        124L  0C    8m  CC=12     ←0
  │ handlers                   112L  0C   11m  CC=10     ←0
  │ server                      71L  0C    2m  CC=1      ←6
  │ device-profile.json         61L  0C    0m  CC=0.0    ←0
  │ move-test.uri.flow.yaml     35L  0C    0m  CC=0.0    ←0
  │ device-profile.rpi3.example.json    33L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          31L  0C    0m  CC=0.0    ←0
  │ Makefile                    25L  0C    0m  CC=0.0    ←0
  │ docker-compose.rpi3.example.yml    21L  0C    0m  CC=0.0    ←0
  │ safety-denied.uri.flow.yaml    17L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  15L  0C    0m  CC=0.0    ←0
  │ call-http.sh                10L  0C    0m  CC=0.0    ←0
  │ test-local.sh                9L  0C    0m  CC=0.0    ←0
  │ test-docker.sh               7L  0C    0m  CC=0.0    ←0
  │ __main__                     2L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.0    ←in:0  →out:0
  │ app.js                      21L  0C    5m  CC=1      ←0
  │ browser-call.sh              8L  0C    0m  CC=0.0    ←0
  │ server-curl.sh               8L  0C    0m  CC=0.0    ←0
  │ call-uri.sh                  6L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml             1319L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                94L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              72L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  schemas/                        CC̄=0.0    ←in:0  →out:0
  │ uripack-markpact.schema.json    47L  0C    0m  CC=0.0    ←0
  │
  local-lab/                      CC̄=0.0    ←in:0  →out:0
  │ 02-build-publish.sh        129L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          72L  0C    0m  CC=0.0    ←0
  │ 06-register-release.sh      62L  0C    0m  CC=0.0    ←0
  │ 04-smoke.sh                 35L  0C    0m  CC=0.0    ←0
  │ run-all.sh                  25L  0C    0m  CC=0.0    ←0
  │ artifact-index.json         23L  0C    0m  CC=0.0    ←0
  │ 05-resolve-from-url.sh      23L  0C    0m  CC=0.0    ←0
  │ 01-validate-markpact.sh     22L  0C    0m  CC=0.0    ←0
  │ install-urisys.sh           17L  0C    0m  CC=0.0    ←0
  │ 03-resolve-run.sh           16L  0C    0m  CC=0.0    ←0
  │ release-manifest.json       15L  0C    0m  CC=0.0    ←0
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
  releases/                       CC̄=0.0    ←in:0  →out:0
  │ artifact-index.json         23L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     src/urisys/controllers/__init__.py        0L

COUPLING:
                                      uristepper-docker.packages          urikvm-docker.packages          urirdp-docker.packages          urienv-docker.packages      uribrowser-docker.packages            urisys-node.packages                      src.urisys            urienv-docker.vendor           urikvm-docker.scripts  urisys-automation-lab.packages    urisys-automation-lab.server
      uristepper-docker.packages                              ──                              ←2                              ←2                              ←3                              ←2                              ←4                                                                                              ←1                                                              ←1  hub
          urikvm-docker.packages                               2                              ──                              ←8                               2                               1                              ←1                                                                                                                                                                  hub
          urirdp-docker.packages                               2                               8                              ──                               2                               1                                                                                                                                                               1                                  !! fan-out
          urienv-docker.packages                               3                              ←2                              ←2                              ──                               1                                                               1                                                                                                                                
      uribrowser-docker.packages                               2                              ←1                              ←1                              ←1                              ──                                                                                                                                                                                                
            urisys-node.packages                               4                               1                                                                                                                              ──                                                                                                                                                                
                      src.urisys                                                                                                                              ←1                                                                                              ──                               1                                                                                                
            urienv-docker.vendor                                                                                                                                                                                                                              ←1                              ──                                                                                                
           urikvm-docker.scripts                               1                                                                                                                                                                                                                                                              ──                                                                
  urisys-automation-lab.packages                                                                                              ←1                                                                                                                                                                                                                              ──                                
    urisys-automation-lab.server                               1                                                                                                                                                                                                                                                                                                                              ──
  CYCLES: none
  HUB: urikvm-docker.packages/ (fan-in=9)
  HUB: uristepper-docker.packages/ (fan-in=15)
  SMELL: urirdp-docker.packages/ fan-out=14 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 23f 2456L | 2026-06-16

SUMMARY:
  files_scanned: 23
  total_lines:   2456
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       2110
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 520 func | 95f | 2026-06-16
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT           src/urisys/managers/markpact_manager.py
      WHY: 579L, 4 classes, max CC=28
      EFFORT: ~4h  IMPACT: 16212

  [2] !  SPLIT-FUNC      MarkpactManager.compile  CC=21  fan=34
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 714

  [3] !  SPLIT-FUNC      main  CC=16  fan=41
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 656

  [4] !  SPLIT-FUNC      main  CC=18  fan=27
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 486

  [5] !! SPLIT-FUNC      MarkpactManager._compile_manifest  CC=28  fan=17
      WHY: CC=28 exceeds 15
      EFFORT: ~1h  IMPACT: 476

  [6] !  SPLIT-FUNC      MarkpactManager.run_tests  CC=20  fan=21
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 420

  [7] !  SPLIT-FUNC      _vision_analyze  CC=22  fan=18
      WHY: CC=22 exceeds 15
      EFFORT: ~1h  IMPACT: 396

  [8] !  SPLIT-FUNC      analyze  CC=18  fan=19
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 342

  [9] !  SPLIT-FUNC      CapabilityRegistry.load_manifest  CC=21  fan=16
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 336

  [10] !  SPLIT-FUNC      build_lab_runtime  CC=16  fan=18
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 288


RISKS[3]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting src/urisys/managers/markpact_manager.py may break 25 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.7 → ≤2.6
  max-CC:      28 → ≤14
  god-modules: 3 → 0
  high-CC(≥15): 19 → ≤9
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
  prev CC̄=3.4 → now CC̄=3.7
```

## Intent

URI control system managers/controllers over separate uri* capability packs.
