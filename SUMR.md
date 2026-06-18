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
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_URI_MODEL, LLM_URI_BASE_URL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK, URISYS_URICORE_GITHUB_OWNER, URISYS_URICORE_VERSION, URISYS_URICORE_WHEEL_URL, URISYS_MIN_VERSION, URISYS_INIT_PROFILE, WAYLAND_DISPLAY, URISYS_URIROUTER_GITHUB_OWNER, URISYS_URIROUTER_VERSION, URISYS_URIROUTER_WHEEL_URL, URISYS_NODE_GITHUB_OWNER, URISYS_NODE_VERSION, URISYS_NODE_WHEEL_URL, URISYS_NODE_PIP_SPEC, URISYS_EXAMPLES_ROOT, URISYS_NODE_HOST_PORT, LENOVO, URISYS_LENOVO_ENDPOINT, URISYS_ROUTE_MAP, URISYS_NODE_HOST, URISYS_NODE_PORT, URISYS_NODE_CONFIG, URISYS_RESOLVER_CONFIG, TELLMESH_ROOT;
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

## Call Graph

*379 nodes · 500 edges · 68 modules · CC̄=4.4*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `build_parser` *(in src.urisys.cli.parser)* | 1 | 1 | 108 | **109** |
| `print` *(in scripts.analyze-thin-markpacts)* | 0 | 70 | 0 | **70** |
| `run_cmd` *(in scripts.test_sessions.util)* | 6 | 35 | 12 | **47** |
| `export_platform_artifacts` *(in src.urisys.managers.platform_export)* | 7 | 2 | 35 | **37** |
| `finalize_session` *(in scripts.test_sessions.util)* | 5 | 23 | 13 | **36** |
| `run_flow` *(in src.urisys_lab.lenovo.cli)* | 14 ⚠ | 3 | 33 | **36** |
| `analyze_run` *(in scripts.report.run_analysis)* | 13 ⚠ | 2 | 33 | **35** |
| `generate_pack_markpact` *(in src.urisys.managers.markpact_pack_gen)* | 10 ⚠ | 1 | 33 | **34** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.27s
# nodes: 379 | edges: 500 | modules: 68
# CC̄=4.4

HUBS[20]:
  src.urisys.cli.parser.build_parser
    CC=1  in:1  out:108  total:109
  scripts.analyze-thin-markpacts.print
    CC=0  in:70  out:0  total:70
  scripts.test_sessions.util.run_cmd
    CC=6  in:35  out:12  total:47
  src.urisys.managers.platform_export.export_platform_artifacts
    CC=7  in:2  out:35  total:37
  scripts.test_sessions.util.finalize_session
    CC=5  in:23  out:13  total:36
  src.urisys_lab.lenovo.cli.run_flow
    CC=14  in:3  out:33  total:36
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  src.urisys.managers.markpact_pack_gen.generate_pack_markpact
    CC=10  in:1  out:33  total:34
  src.urisys.markpact.compiler.MarkpactCompiler.compile
    CC=15  in:0  out:33  total:33
  src.urisys.managers.contract_gen._diff_section
    CC=8  in:1  out:32  total:33
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  src.urisys_lab.core.now_iso
    CC=1  in:30  out:2  total:32
  src.urisys_lab.sessions.cli.main
    CC=13  in:0  out:32  total:32
  scripts.generate_pack_markpacts._render
    CC=14  in:1  out:31  total:32
  src.urisys_lab.sessions.runners.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  scripts.report.session.generate_report
    CC=9  in:2  out:27  total:29
  src.urisys.cli.helpers.print_json
    CC=1  in:26  out:2  total:28
  src.urisys.markpact.tests.run_markpact_tests
    CC=12  in:1  out:27  total:28
  src.urisys.managers.markpact_run_flow.run_markpact_flow
    CC=14  in:1  out:26  total:27
  src.urisys.markpact.validate_pack.validate_markpact_file
    CC=12  in:1  out:24  total:25

MODULES:
  scripts.analyze-thin-markpacts  [1 funcs]
    print  CC=0  out:0
  scripts.check_contract_drift  [2 funcs]
    main  CC=15  out:19
    manifest_path  CC=3  out:1
  scripts.generate_pack_markpacts  [15 funcs]
    _capabilities  CC=7  out:12
    _extra_specs  CC=3  out:2
    _file_stem  CC=4  out:4
    _fill_pattern  CC=1  out:3
    _process_spec  CC=8  out:12
    _render  CC=14  out:31
    _run_block  CC=1  out:0
    _scheme  CC=2  out:1
    _split_by_scheme  CC=13  out:18
    _tests  CC=5  out:4
  scripts.office-simulate-loop  [5 funcs]
    call_uri  CC=4  out:11
    llm_tick  CC=7  out:18
    main  CC=10  out:12
    parse_args  CC=1  out:8
    rules_tick  CC=3  out:8
  scripts.pack_registry  [6 funcs]
    _pack  CC=3  out:2
    _repo  CC=1  out:0
    all_promoted_packs  CC=1  out:3
    pack_specs  CC=7  out:20
    sibling_repo  CC=1  out:1
    sibling_uv_path  CC=1  out:0
  scripts.pack_sync  [19 funcs]
    _check_promoted  CC=5  out:7
    _cmd_check  CC=5  out:7
    _cmd_init_repo  CC=3  out:2
    _cmd_print_uv_sources  CC=4  out:2
    _cmd_promote  CC=3  out:3
    _cmd_to_repo  CC=5  out:6
    _repo_pyproject  CC=14  out:12
    _validate_packs  CC=3  out:1
    check_drift  CC=14  out:19
    file_hash  CC=1  out:3
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
  scripts.report.session  [5 funcs]
    _resolve_screenshot  CC=5  out:6
    _response_to_step_result  CC=12  out:20
    generate_report  CC=9  out:27
    infer_steps  CC=7  out:8
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
  scripts.run-office-writer-e2e  [2 funcs]
    save_json  CC=0  out:0
    wait_health  CC=0  out:0
  scripts.run-urisys-node-docker-e2e  [1 funcs]
    http_json  CC=0  out:0
  scripts.scan-browser-sessions  [9 funcs]
    _copy_query  CC=2  out:10
    _output_json  CC=2  out:4
    _output_text  CC=11  out:16
    _scan_profiles  CC=12  out:11
    chrome_profiles  CC=11  out:14
    discover_browsers  CC=1  out:0
    firefox_profiles  CC=8  out:15
    main  CC=2  out:7
    scan_chrome_cookies  CC=13  out:13
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
  scripts.update-ecosystem-readmes  [4 funcs]
    build_section  CC=1  out:1
    fix_urisysedge_refs  CC=2  out:1
    main  CC=4  out:11
    strip_old_section  CC=2  out:3
  src.urisys.bootstrap  [5 funcs]
    _doctor_main  CC=3  out:7
    _init_main  CC=6  out:18
    _missing_uricore_payload  CC=1  out:1
    _print_json  CC=1  out:2
    main  CC=8  out:6
  src.urisys.cli.commands.markpact  [14 funcs]
    _apply_strict_operations  CC=8  out:2
    _apply_strict_profile  CC=4  out:2
    cmd_analyze  CC=5  out:9
    cmd_compile  CC=1  out:3
    cmd_contract  CC=6  out:14
    cmd_export_platform  CC=3  out:8
    cmd_markpact  CC=15  out:20
    cmd_materialize  CC=3  out:8
    cmd_pack  CC=6  out:10
    cmd_routes  CC=2  out:4
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
    _build_flow_profiles  CC=10  out:21
    _cap_uri  CC=3  out:3
    _cross_check_schemes  CC=9  out:8
    _flow_features  CC=6  out:9
    _flow_level_features  CC=3  out:4
    _issue  CC=1  out:1
    _issue_message  CC=1  out:0
    _required_features  CC=4  out:7
    _step_features  CC=7  out:9
    _text_pattern_features  CC=4  out:3
  src.urisys.managers.markpact_run  [14 funcs]
    _apply_resolver_config  CC=7  out:9
    _build_flow_runtime  CC=2  out:8
    _build_runtime  CC=3  out:5
    _load_run_config  CC=4  out:5
    _resolve_flow_ids  CC=5  out:6
    _resolve_flow_uses  CC=5  out:11
    _routes_summary  CC=2  out:0
    _run_adapter_mode  CC=3  out:5
    _run_flow_mode  CC=8  out:11
    _run_interface_mode  CC=2  out:1
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
  src.urisys.managers.platform_export  [6 funcs]
    _authorities_from_flow  CC=10  out:13
    _resolve_authority  CC=9  out:7
    _target_stub  CC=11  out:1
    build_resolver_yaml  CC=5  out:3
    collect_process_uris  CC=6  out:20
    export_platform_artifacts  CC=7  out:35
  src.urisys.markpact.analyzer  [1 funcs]
    analyze_markpact  CC=8  out:18
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
  src.urisys.markpact.compiler  [1 funcs]
    compile  CC=15  out:33
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
  src.urisys_lab.core  [16 funcs]
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
  src.urisys_lab.lenovo.cli  [1 funcs]
    run_flow  CC=14  out:33
  src.urisys_lab.sessions.cli  [1 funcs]
    main  CC=13  out:32
  src.urisys_lab.sessions.runners  [8 funcs]
    _bootstrap_rdp  CC=4  out:3
    _call_and_record  CC=5  out:4
    _read_display_env  CC=4  out:4
    _record_health  CC=1  out:3
    session_pytest_urirdp  CC=3  out:5
    session_pytest_urisys  CC=2  out:5
    session_pytest_urisys_node  CC=2  out:5
    session_urirdp_mock_docker  CC=5  out:31

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.27s
# nodes: 379 | edges: 500 | modules: 68
# CC̄=4.4

HUBS[20]:
  src.urisys.cli.parser.build_parser
    CC=1  in:1  out:108  total:109
  scripts.analyze-thin-markpacts.print
    CC=0  in:70  out:0  total:70
  scripts.test_sessions.util.run_cmd
    CC=6  in:35  out:12  total:47
  src.urisys.managers.platform_export.export_platform_artifacts
    CC=7  in:2  out:35  total:37
  scripts.test_sessions.util.finalize_session
    CC=5  in:23  out:13  total:36
  src.urisys_lab.lenovo.cli.run_flow
    CC=14  in:3  out:33  total:36
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  src.urisys.managers.markpact_pack_gen.generate_pack_markpact
    CC=10  in:1  out:33  total:34
  src.urisys.markpact.compiler.MarkpactCompiler.compile
    CC=15  in:0  out:33  total:33
  src.urisys.managers.contract_gen._diff_section
    CC=8  in:1  out:32  total:33
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  src.urisys_lab.core.now_iso
    CC=1  in:30  out:2  total:32
  src.urisys_lab.sessions.cli.main
    CC=13  in:0  out:32  total:32
  scripts.generate_pack_markpacts._render
    CC=14  in:1  out:31  total:32
  src.urisys_lab.sessions.runners.session_urirdp_mock_docker
    CC=5  in:0  out:31  total:31
  scripts.report.session.generate_report
    CC=9  in:2  out:27  total:29
  src.urisys.cli.helpers.print_json
    CC=1  in:26  out:2  total:28
  src.urisys.markpact.tests.run_markpact_tests
    CC=12  in:1  out:27  total:28
  src.urisys.managers.markpact_run_flow.run_markpact_flow
    CC=14  in:1  out:26  total:27
  src.urisys.markpact.validate_pack.validate_markpact_file
    CC=12  in:1  out:24  total:25

MODULES:
  scripts.analyze-thin-markpacts  [1 funcs]
    print  CC=0  out:0
  scripts.check_contract_drift  [2 funcs]
    main  CC=15  out:19
    manifest_path  CC=3  out:1
  scripts.generate_pack_markpacts  [15 funcs]
    _capabilities  CC=7  out:12
    _extra_specs  CC=3  out:2
    _file_stem  CC=4  out:4
    _fill_pattern  CC=1  out:3
    _process_spec  CC=8  out:12
    _render  CC=14  out:31
    _run_block  CC=1  out:0
    _scheme  CC=2  out:1
    _split_by_scheme  CC=13  out:18
    _tests  CC=5  out:4
  scripts.office-simulate-loop  [5 funcs]
    call_uri  CC=4  out:11
    llm_tick  CC=7  out:18
    main  CC=10  out:12
    parse_args  CC=1  out:8
    rules_tick  CC=3  out:8
  scripts.pack_registry  [6 funcs]
    _pack  CC=3  out:2
    _repo  CC=1  out:0
    all_promoted_packs  CC=1  out:3
    pack_specs  CC=7  out:20
    sibling_repo  CC=1  out:1
    sibling_uv_path  CC=1  out:0
  scripts.pack_sync  [19 funcs]
    _check_promoted  CC=5  out:7
    _cmd_check  CC=5  out:7
    _cmd_init_repo  CC=3  out:2
    _cmd_print_uv_sources  CC=4  out:2
    _cmd_promote  CC=3  out:3
    _cmd_to_repo  CC=5  out:6
    _repo_pyproject  CC=14  out:12
    _validate_packs  CC=3  out:1
    check_drift  CC=14  out:19
    file_hash  CC=1  out:3
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
  scripts.report.session  [5 funcs]
    _resolve_screenshot  CC=5  out:6
    _response_to_step_result  CC=12  out:20
    generate_report  CC=9  out:27
    infer_steps  CC=7  out:8
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
  scripts.run-office-writer-e2e  [2 funcs]
    save_json  CC=0  out:0
    wait_health  CC=0  out:0
  scripts.run-urisys-node-docker-e2e  [1 funcs]
    http_json  CC=0  out:0
  scripts.scan-browser-sessions  [9 funcs]
    _copy_query  CC=2  out:10
    _output_json  CC=2  out:4
    _output_text  CC=11  out:16
    _scan_profiles  CC=12  out:11
    chrome_profiles  CC=11  out:14
    discover_browsers  CC=1  out:0
    firefox_profiles  CC=8  out:15
    main  CC=2  out:7
    scan_chrome_cookies  CC=13  out:13
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
  scripts.update-ecosystem-readmes  [4 funcs]
    build_section  CC=1  out:1
    fix_urisysedge_refs  CC=2  out:1
    main  CC=4  out:11
    strip_old_section  CC=2  out:3
  src.urisys.bootstrap  [5 funcs]
    _doctor_main  CC=3  out:7
    _init_main  CC=6  out:18
    _missing_uricore_payload  CC=1  out:1
    _print_json  CC=1  out:2
    main  CC=8  out:6
  src.urisys.cli.commands.markpact  [14 funcs]
    _apply_strict_operations  CC=8  out:2
    _apply_strict_profile  CC=4  out:2
    cmd_analyze  CC=5  out:9
    cmd_compile  CC=1  out:3
    cmd_contract  CC=6  out:14
    cmd_export_platform  CC=3  out:8
    cmd_markpact  CC=15  out:20
    cmd_materialize  CC=3  out:8
    cmd_pack  CC=6  out:10
    cmd_routes  CC=2  out:4
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
    _build_flow_profiles  CC=10  out:21
    _cap_uri  CC=3  out:3
    _cross_check_schemes  CC=9  out:8
    _flow_features  CC=6  out:9
    _flow_level_features  CC=3  out:4
    _issue  CC=1  out:1
    _issue_message  CC=1  out:0
    _required_features  CC=4  out:7
    _step_features  CC=7  out:9
    _text_pattern_features  CC=4  out:3
  src.urisys.managers.markpact_run  [14 funcs]
    _apply_resolver_config  CC=7  out:9
    _build_flow_runtime  CC=2  out:8
    _build_runtime  CC=3  out:5
    _load_run_config  CC=4  out:5
    _resolve_flow_ids  CC=5  out:6
    _resolve_flow_uses  CC=5  out:11
    _routes_summary  CC=2  out:0
    _run_adapter_mode  CC=3  out:5
    _run_flow_mode  CC=8  out:11
    _run_interface_mode  CC=2  out:1
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
  src.urisys.managers.platform_export  [6 funcs]
    _authorities_from_flow  CC=10  out:13
    _resolve_authority  CC=9  out:7
    _target_stub  CC=11  out:1
    build_resolver_yaml  CC=5  out:3
    collect_process_uris  CC=6  out:20
    export_platform_artifacts  CC=7  out:35
  src.urisys.markpact.analyzer  [1 funcs]
    analyze_markpact  CC=8  out:18
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
  src.urisys.markpact.compiler  [1 funcs]
    compile  CC=15  out:33
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
  src.urisys_lab.core  [16 funcs]
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
  src.urisys_lab.lenovo.cli  [1 funcs]
    run_flow  CC=14  out:33
  src.urisys_lab.sessions.cli  [1 funcs]
    main  CC=13  out:32
  src.urisys_lab.sessions.runners  [8 funcs]
    _bootstrap_rdp  CC=4  out:3
    _call_and_record  CC=5  out:4
    _read_display_env  CC=4  out:4
    _record_health  CC=1  out:3
    session_pytest_urirdp  CC=3  out:5
    session_pytest_urisys  CC=2  out:5
    session_pytest_urisys_node  CC=2  out:5
    session_urirdp_mock_docker  CC=5  out:31

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 156f 16791L | python:95,shell:49,yaml:7,toml:1,json:1,yml:1,javascript:1 | 2026-06-18
# generated in 0.03s
# CC̅=4.4 | critical:5/618 | dups:0 | cycles:0

HEALTH[5]:
  🟡 CC    cmd_markpact CC=15 (limit:15)
  🟡 CC    compile CC=15 (limit:15)
  🟡 CC    main CC=15 (limit:15)
  🟡 CC    load_flow_outcomes CC=15 (limit:15)
  🟡 CC    main CC=15 (limit:15)

REFACTOR[1]:
  1. split 5 high-CC methods  (CC>15)

PIPELINES[147]:
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
  [7] Src [diagnose_urirouter]: diagnose_urirouter → _module_exists
      PURITY: 100% pure
  [8] Src [call]: call
      PURITY: 100% pure
  [9] Src [main]: main → build_parser → add_runtime_flags
      PURITY: 100% pure
  [10] Src [cmd_uri]: cmd_uri → print_json → print
      PURITY: 100% pure
  [11] Src [cmd_serve]: cmd_serve → print
      PURITY: 100% pure
  [12] Src [cmd_flow]: cmd_flow → print_json → print
      PURITY: 100% pure
  [13] Src [cmd_events]: cmd_events → print_json → print
      PURITY: 100% pure
  [14] Src [cmd_doctor]: cmd_doctor → run_doctor → _check_uricore_authentic → diagnose_uricore → ...(1 more)
      PURITY: 100% pure
  [15] Src [cmd_init]: cmd_init → run_init → default_pip_specs → pip_spec → ...(2 more)
      PURITY: 100% pure
  [16] Src [cmd_node]: cmd_node → print
      PURITY: 100% pure
  [17] Src [cmd_markpact]: cmd_markpact → resolve_markpact_source
      PURITY: 100% pure
  [18] Src [__init__]: __init__
      PURITY: 100% pure
  [19] Src [compile]: compile → compile_context → read_blocks → parse_meta
      PURITY: 100% pure
  [20] Src [__init__]: __init__
      PURITY: 100% pure
  [21] Src [run]: run → load_flow
      PURITY: 100% pure
  [22] Src [close]: close
      PURITY: 100% pure
  [23] Src [__init__]: __init__ → create_server → _read_json
      PURITY: 100% pure
  [24] Src [serve_forever]: serve_forever → print
      PURITY: 100% pure
  [25] Src [__init__]: __init__
      PURITY: 100% pure
  [26] Src [call]: call
      PURITY: 100% pure
  [27] Src [explain]: explain
      PURITY: 100% pure
  [28] Src [routes]: routes
      PURITY: 100% pure
  [29] Src [close]: close
      PURITY: 100% pure
  [30] Src [to_dict]: to_dict
      PURITY: 100% pure
  [31] Src [__init__]: __init__
      PURITY: 100% pure
  [32] Src [list_events]: list_events
      PURITY: 100% pure
  [33] Src [build_context]: build_context
      PURITY: 100% pure
  [34] Src [explain]: explain
      PURITY: 100% pure
  [35] Src [__init__]: __init__
      PURITY: 100% pure
  [36] Src [create_runtime]: create_runtime
      PURITY: 100% pure
  [37] Src [close]: close
      PURITY: 100% pure
  [38] Src [__exit__]: __exit__
      PURITY: 100% pure
  [39] Src [__init__]: __init__
      PURITY: 100% pure
  [40] Src [read_blocks]: read_blocks
      PURITY: 100% pure
  [41] Src [source_hash]: source_hash
      PURITY: 100% pure
  [42] Src [load_pack_block]: load_pack_block
      PURITY: 100% pure
  [43] Src [compile]: compile
      PURITY: 100% pure
  [44] Src [analyze]: analyze → analyze_markpact → read_blocks → parse_meta
      PURITY: 100% pure
  [45] Src [manifest_path_for]: manifest_path_for
      PURITY: 100% pure
  [46] Src [run_tests]: run_tests → run_tests_for_path → run_markpact_tests → check_expectations
      PURITY: 100% pure
  [47] Src [_build_route]: _build_route → build_route → _resolve_pattern
      PURITY: 100% pure
  [48] Src [_compile_manifest]: _compile_manifest → compile_manifest → capabilities
      PURITY: 100% pure
  [49] Src [call_http]: call_http
      PURITY: 100% pure
  [50] Src [__init__]: __init__
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.5    ←in:0  →out:0
  │ !! cli                        965L  0C   40m  CC=15     ←2
  │ !! runners                    665L  0C   22m  CC=13     ←1
  │ lab_flows                  320L  0C    5m  CC=13     ←0
  │ core                       313L  0C   23m  CC=8      ←9
  │ markpact_profile           307L  1C   20m  CC=11     ←3
  │ platform_export            303L  0C    8m  CC=11     ←2
  │ doctor                     293L  1C   11m  CC=11     ←3
  │ markpact_run               262L  0C   14m  CC=10     ←1
  │ init_setup                 257L  0C   16m  CC=13     ←2
  │ markpact_pack_gen          242L  0C   12m  CC=11     ←1
  │ source_manager             218L  2C   12m  CC=11     ←0
  │ parser                     213L  0C    2m  CC=1      ←1
  │ !! markpact                   198L  0C   14m  CC=15     ←0
  │ util                       197L  0C   14m  CC=9      ←0
  │ pack_manager               190L  1C   19m  CC=8      ←0
  │ markpact_pack_deps         189L  0C   13m  CC=12     ←4
  │ contract_gen               189L  0C   13m  CC=11     ←1
  │ lab_rdp                    180L  0C    8m  CC=11     ←0
  │ markpact_run_flow          160L  0C    6m  CC=14     ←2
  │ markpact_validation        156L  0C    6m  CC=14     ←1
  │ expectations               153L  0C    9m  CC=11     ←0
  │ markpact_flows             133L  0C    8m  CC=11     ←5
  │ uricore_install            130L  0C   11m  CC=6      ←2
  │ manifest                   127L  0C    7m  CC=12     ←2
  │ cache                      118L  0C    5m  CC=4      ←1
  │ bootstrap                  116L  0C    5m  CC=8      ←0
  │ !! compiler                   107L  1C    2m  CC=15     ←0
  │ node_install               106L  0C    9m  CC=7      ←1
  │ cli                        106L  0C    1m  CC=13     ←0
  │ markpact_models            102L  3C    5m  CC=6      ←12
  │ validate_pack               92L  0C    2m  CC=12     ←1
  │ artifacts                   80L  0C    6m  CC=4      ←2
  │ tests                       78L  0C    3m  CC=12     ←1
  │ http_server                 76L  1C    4m  CC=3      ←1
  │ __init__                    74L  0C    0m  CC=0.0    ←0
  │ markpact_manager            72L  1C   11m  CC=1      ←1
  │ markpact_materialize        69L  0C    2m  CC=8      ←1
  │ blocks                      63L  0C    4m  CC=6      ←6
  │ analyzer                    55L  0C    1m  CC=8      ←1
  │ pack                        54L  0C    4m  CC=8      ←7
  │ runtime                     51L  0C    4m  CC=4      ←0
  │ handlers                    51L  0C    3m  CC=7      ←3
  │ urirouter_install           46L  0C    6m  CC=3      ←0
  │ defaults                    40L  0C    0m  CC=0.0    ←0
  │ node                        34L  0C    1m  CC=6      ←0
  │ flow_controller             33L  1C    3m  CC=6      ←0
  │ uri_controller              33L  1C    5m  CC=3      ←0
  │ errors                      32L  0C    1m  CC=8      ←1
  │ setup                       31L  0C    2m  CC=6      ←0
  │ runtime_manager             30L  1C    5m  CC=2      ←0
  │ helpers                     28L  0C    3m  CC=3      ←4
  │ flow                        25L  0C    2m  CC=7      ←1
  │ __init__                    24L  0C    0m  CC=0.0    ←0
  │ route_manager               23L  1C    3m  CC=2      ←0
  │ server_controller           19L  1C    2m  CC=1      ←0
  │ __init__                    19L  0C    0m  CC=0.0    ←0
  │ policy_manager              18L  1C    1m  CC=2      ←0
  │ main                        17L  0C    1m  CC=3      ←0
  │ bridge_manager              14L  1C    1m  CC=3      ←0
  │ event_manager               13L  1C    2m  CC=1      ←0
  │ __init__                    10L  0C    0m  CC=0.0    ←0
  │ paths                       10L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __main__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=4.2    ←in:64  →out:0
  │ generate_pack_markpacts    371L  0C   16m  CC=14     ←0
  │ pack_sync                  371L  0C   19m  CC=14     ←0
  │ lab_flows                  320L  0C    5m  CC=13     ←0
  │ pack_registry              260L  1C    7m  CC=7      ←3
  │ scan-browser-sessions      208L  0C    9m  CC=13     ←0
  │ util                       201L  0C   14m  CC=9      ←6
  │ !! lab_checks                 188L  0C    9m  CC=15     ←1
  │ run-office-simulate-lenovo.sh   182L  0C    6m  CC=0.0    ←0
  │ lab_rdp                    180L  0C    8m  CC=11     ←2
  │ update-ecosystem-readmes   163L  0C    4m  CC=4      ←0
  │ run-urisys-node-docker-e2e.sh   163L  0C    5m  CC=0.0    ←5
  │ expectations               153L  0C    9m  CC=11     ←2
  │ office-simulate-loop       146L  0C    5m  CC=10     ←1
  │ events                     138L  0C    5m  CC=14     ←1
  │ run-email-mailpit-e2e.sh   134L  0C    4m  CC=0.0    ←0
  │ run-office-simulate-e2e.sh   130L  0C    4m  CC=0.0    ←0
  │ deploy-lenovo-node.sh      130L  0C    5m  CC=0.0    ←0
  │ run_analysis               129L  0C    5m  CC=13     ←1
  │ session                    124L  0C    8m  CC=12     ←2
  │ session_markdown           120L  0C    8m  CC=7      ←1
  │ run-lenovo-office-linkedin.sh   118L  0C    3m  CC=0.0    ←0
  │ run-office-writer-e2e.sh   113L  0C    4m  CC=0.0    ←7
  │ remote-node-smoke.sh        99L  0C    2m  CC=0.0    ←0
  │ !! check_contract_drift        95L  0C    4m  CC=15     ←0
  │ models                      86L  5C    0m  CC=0.0    ←0
  │ publish-tellmesh-wheels.sh    83L  0C    1m  CC=0.0    ←0
  │ lenovo-node-session.sh      73L  0C    1m  CC=0.0    ←0
  │ paths.sh                    69L  0C    7m  CC=0.0    ←0
  │ validate-all-markpacts.sh    65L  0C    1m  CC=0.0    ←0
  │ validate-pypi-metadata.sh    62L  0C    2m  CC=0.0    ←0
  │ __init__                    61L  0C    0m  CC=0.0    ←0
  │ test-python-matrix.sh       58L  0C    1m  CC=0.0    ←0
  │ run-markpact-ci.sh          58L  0C    0m  CC=0.0    ←0
  │ bootstrap-lenovo-local.sh    57L  0C    0m  CC=0.0    ←0
  │ ci-checkout-siblings.sh     56L  0C    1m  CC=0.0    ←0
  │ materialize-all-showcases.sh    53L  0C    1m  CC=0.0    ←0
  │ publish-pypi-packs.sh       53L  0C    0m  CC=0.0    ←0
  │ session_report              49L  0C    0m  CC=0.0    ←0
  │ analyze-thin-markpacts.sh    48L  0C    1m  CC=0.0    ←16
  │ run-nl-log-smoke.sh         43L  0C    1m  CC=0.0    ←0
  │ analyze-legacy-contract-packs.sh    43L  0C    0m  CC=0.0    ←0
  │ run_markdown                42L  0C    1m  CC=7      ←1
  │ cli                         41L  0C    1m  CC=4      ←0
  │ analyze-process-markpacts.sh    39L  0C    0m  CC=0.0    ←0
  │ sync-vendored-pack.sh       38L  0C    0m  CC=0.0    ←0
  │ marksync-materialize.sh     31L  0C    0m  CC=0.0    ←0
  │ ci-install-siblings.sh      28L  0C    1m  CC=0.0    ←0
  │ run-full-regression.sh      26L  0C    0m  CC=0.0    ←0
  │ run-smoke-all.sh            24L  0C    0m  CC=0.0    ←0
  │ util                        21L  0C    2m  CC=3      ←3
  │ run-lab-unit-ci.sh          21L  0C    0m  CC=0.0    ←0
  │ session_io                  19L  0C    1m  CC=2      ←2
  │ publish-urisys-node-release.sh    19L  0C    0m  CC=0.0    ←0
  │ run-lab-nightly.sh          16L  0C    0m  CC=0.0    ←0
  │ run-lab-e2e.sh              14L  0C    0m  CC=0.0    ←0
  │ install-kvm-packs-editable.sh    13L  0C    0m  CC=0.0    ←0
  │ test-goal.sh                11L  0C    0m  CC=0.0    ←0
  │ run_test_sessions            7L  0C    0m  CC=0.0    ←0
  │ lenovo_remote_session        7L  0C    0m  CC=0.0    ←0
  │ generate_showcase_markpacts     6L  0C    0m  CC=0.0    ←0
  │ run-urisys-node-docker-session.sh     6L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ session_core                 4L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.0    ←in:0  →out:0
  │ showcase-run-flow.sh        29L  0C    0m  CC=0.0    ←0
  │ app.js                      21L  0C    5m  CC=1      ←0
  │ browser-call.sh             12L  0C    0m  CC=0.0    ←0
  │ server-curl.sh               8L  0C    0m  CC=0.0    ←0
  │ call-uri.sh                  6L  0C    0m  CC=0.0    ←0
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
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    39L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    24L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     src/urisys/controllers/__init__.py        0L

COUPLING:
                                src.urisys_lab  scripts.test_sessions                scripts         scripts.report             src.urisys
         src.urisys_lab                     ──                    113                     40                     ←7                     ←2  hub
  scripts.test_sessions                      3                     ──                      8                                                hub
                scripts                    ←40                     ←8                     ──                     ←6                    ←10  hub
         scripts.report                      7                                             6                     ──                         !! fan-out
             src.urisys                      2                                            10                                            ──  !! fan-out
  CYCLES: none
  HUB: src.urisys_lab/ (fan-in=12)
  HUB: scripts/ (fan-in=64)
  HUB: scripts.test_sessions/ (fan-in=113)
  SMELL: src.urisys_lab/ fan-out=153 → split needed
  SMELL: src.urisys/ fan-out=12 → split needed
  SMELL: scripts.test_sessions/ fan-out=11 → split needed
  SMELL: scripts.report/ fan-out=13 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 6 groups | 89f 10917L | 2026-06-18

SUMMARY:
  files_scanned: 89
  total_lines:   10917
  dup_groups:    6
  dup_fragments: 13
  saved_lines:   147
  scan_ms:       2856

HOTSPOTS[7] (files with most duplication):
  src/urisys_lab/sessions/runners.py  dup=138L  groups=1  frags=3  (1.3%)
  src/urisys_lab/sessions/expectations.py  dup=40L  groups=1  frags=2  (0.4%)
  src/urisys/uricore_install.py  dup=27L  groups=3  frags=3  (0.2%)
  src/urisys/node_install.py  dup=11L  groups=1  frags=1  (0.1%)
  src/urisys/urirouter_install.py  dup=9L  groups=1  frags=1  (0.1%)
  scripts/report/run_analysis.py  dup=8L  groups=1  frags=1  (0.1%)
  scripts/report/session_io.py  dup=8L  groups=1  frags=1  (0.1%)

DUPLICATES[6] (ranked by impact):
  [68032876d180e62e] ! STRU  session_urisys_node_docker_gui  L=46 N=3 saved=92 sim=1.00
      src/urisys_lab/sessions/runners.py:440-485  (session_urisys_node_docker_gui)
      src/urisys_lab/sessions/runners.py:488-533  (session_office_simulate)
      src/urisys_lab/sessions/runners.py:571-616  (session_office_writer)
  [5053c450ed7255b6]   STRU  _screen_changed  L=20 N=2 saved=20 sim=1.00
      src/urisys_lab/sessions/expectations.py:41-60  (_screen_changed)
      src/urisys_lab/sessions/expectations.py:63-82  (_screen_changed_since_previous)
  [3f18ae8c291ee1c9]   EXAC  pip_run  L=11 N=2 saved=11 sim=1.00
      src/urisys/node_install.py:48-58  (pip_run)
      src/urisys/uricore_install.py:99-109  (pip_run)
  [fd0f5f10244e4f23]   STRU  wheel_url  L=9 N=2 saved=9 sim=1.00
      src/urisys/uricore_install.py:23-31  (wheel_url)
      src/urisys/urirouter_install.py:21-29  (wheel_url)
  [bb100fda4da2fc0e]   STRU  write_run_analysis  L=8 N=2 saved=8 sim=1.00
      scripts/report/run_analysis.py:122-129  (write_run_analysis)
      scripts/report/session_io.py:12-19  (write_session_report)
  [487da026fcebd9df]   EXAC  _pkg_version  L=7 N=2 saved=7 sim=1.00
      src/urisys/doctor.py:23-29  (_pkg_version)
      src/urisys/uricore_install.py:38-44  (_pkg_version)

REFACTOR[6] (ranked by priority):
  [1] ○ extract_function   → src/urisys_lab/sessions/utils/session_urisys_node_docker_gui.py
      WHY: 3 occurrences of 46-line block across 1 files — saves 92 lines
      FILES: src/urisys_lab/sessions/runners.py
  [2] ○ extract_function   → src/urisys_lab/sessions/utils/_screen_changed.py
      WHY: 2 occurrences of 20-line block across 1 files — saves 20 lines
      FILES: src/urisys_lab/sessions/expectations.py
  [3] ○ extract_function   → src/urisys/utils/pip_run.py
      WHY: 2 occurrences of 11-line block across 2 files — saves 11 lines
      FILES: src/urisys/node_install.py, src/urisys/uricore_install.py
  [4] ○ extract_function   → src/urisys/utils/wheel_url.py
      WHY: 2 occurrences of 9-line block across 2 files — saves 9 lines
      FILES: src/urisys/uricore_install.py, src/urisys/urirouter_install.py
  [5] ○ extract_function   → scripts/report/utils/write_run_analysis.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: scripts/report/run_analysis.py, scripts/report/session_io.py
  [6] ○ extract_function   → src/urisys/utils/_pkg_version.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: src/urisys/doctor.py, src/urisys/uricore_install.py

QUICK_WINS[6] (low risk, high savings — do first):
  [1] extract_function   saved=92L  → src/urisys_lab/sessions/utils/session_urisys_node_docker_gui.py
      FILES: runners.py
  [2] extract_function   saved=20L  → src/urisys_lab/sessions/utils/_screen_changed.py
      FILES: expectations.py
  [3] extract_function   saved=11L  → src/urisys/utils/pip_run.py
      FILES: node_install.py, uricore_install.py
  [4] extract_function   saved=9L  → src/urisys/utils/wheel_url.py
      FILES: uricore_install.py, urirouter_install.py
  [5] extract_function   saved=8L  → scripts/report/utils/write_run_analysis.py
      FILES: run_analysis.py, session_io.py
  [6] extract_function   saved=7L  → src/urisys/utils/_pkg_version.py
      FILES: doctor.py, uricore_install.py

EFFORT_ESTIMATE (total ≈ 6.4h):
  hard   session_urisys_node_docker_gui      saved=92L  ~276min
  medium _screen_changed                     saved=20L  ~40min
  easy   pip_run                             saved=11L  ~22min
  easy   wheel_url                           saved=9L  ~18min
  easy   write_run_analysis                  saved=8L  ~16min
  easy   _pkg_version                        saved=7L  ~14min

METRICS-TARGET:
  dup_groups:  6 → 0
  saved_lines: 147 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 422 func | 56f | 2026-06-18
# generated in 0.00s

NEXT[6] (ranked by impact):
  [1] !! SPLIT           src/urisys_lab/lenovo/cli.py
      WHY: 965L, 0 classes, max CC=15
      EFFORT: ~4h  IMPACT: 14475

  [2] !! SPLIT           src/urisys_lab/sessions/runners.py
      WHY: 665L, 0 classes, max CC=13
      EFFORT: ~4h  IMPACT: 8645

  [3] !  SPLIT-FUNC      main  CC=15  fan=37
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 555

  [4] !  SPLIT-FUNC      MarkpactCompiler.compile  CC=15  fan=24
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 360

  [5] !  SPLIT-FUNC      cmd_markpact  CC=15  fan=18
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 270

  [6] !! SPLIT           planfile.yaml
      WHY: 1319L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[3]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting src/urisys_lab/lenovo/cli.py may break 40 import paths
  ⚠ Splitting src/urisys_lab/sessions/runners.py may break 22 import paths

METRICS-TARGET:
  CC̄:          4.5 → ≤3.1
  max-CC:      15 → ≤7
  god-modules: 4 → 0
  high-CC(≥15): 3 → ≤1
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
  prev CC̄=4.3 → now CC̄=4.5
```

## Intent

URI control system managers/controllers over separate uri* capability packs.
