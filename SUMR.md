# urisys

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `urisys`
- **version**: `0.1.93`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(3), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: urisys;
  version: 0.1.93;
}

dependencies {
  runtime: "PyYAML>=6.0, uricontrol>=0.1.11, uriresolver>=0.1.0";
  dev: "pytest>=8.0, uricontrol, uribrowser, uridocker, goal>=2.1.0, costs>=0.1.20";
  lab: "urisys-automation-lab[sessions]>=0.1.3, uri2flow>=0.1.2";
  real: "mss>=9.0, Pillow>=10.0, pyautogui>=0.9.54, pytesseract>=0.3.10, litellm>=1.40";
  kvm: "urikvm[real]>=0.1.0, urihim[real]>=0.1.0, uriocr[real]>=0.1.0, urillm[vision]>=0.1.0";
  discovery: zeroconf>=0.131.0;
  node: urisys-node>=0.1.22;
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

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pip install -e .;
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest -q;
}

workflow[name="test-all"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest -v;
}

workflow[name="test-integration"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/integration/ -v;
}

workflow[name="test-coverage"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest --cov=urisysnode --cov-report=term-missing -v;
}

workflow[name="test-watch"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m ptw tests/ --pattern "test_*.py" --ignore "tests/integration/";
}

workflow[name="serve"] {
  trigger: manual;
  step-1: run cmd=URISYS_NODE_SKIP_PAIRING=1 urisys-node serve --host 0.0.0.0 --port $(PORT);
}

workflow[name="health"] {
  trigger: manual;
  step-1: run cmd=curl -fsS "http://127.0.0.1:$(PORT)/health" | $(PYTHON) -m json.tool | head -15;
}

workflow[name="app-chat-smoke"] {
  trigger: manual;
  step-1: run cmd=curl -fsS -X POST "http://127.0.0.1:$(PORT)/app/chat/messages" \;
  step-2: run cmd=-H 'Content-Type: application/json' \;
  step-3: run cmd=-d '{"channel_id":"smoke","role":"user","text":"ping"}' | $(PYTHON) -m json.tool;
  step-4: run cmd=curl -fsS "http://127.0.0.1:$(PORT)/app/chat/messages?channel_id=smoke" | $(PYTHON) -m json.tool;
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Publishing to PyPI...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine check dist/*;
  step-6: run cmd=echo "🚀 Uploading to PyPI...";
  step-7: run cmd=.venv/bin/twine upload dist/*;
}

workflow[name="publish-test"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Publishing to TestPyPI...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine upload --repository testpypi dist/*;
}

workflow[name="version"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Version information...";
  step-2: run cmd=cat VERSION;
  step-3: run cmd=.venv/bin/python -c "from importlib.metadata import version; print(f'Installed version: {version(\"sumd\")}')";
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_URI_MODEL, LLM_URI_BASE_URL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK, URISYS_GITHUB_OWNER, URISYS_VERSION, URISYS_WHEEL_URL, URISYS_PYPI, URISYS_URICORE_GITHUB_OWNER, URISYS_URICORE_VERSION, URISYS_URICORE_WHEEL_URL, URISYS_URICORE_PYPI, URISYS_URIGUARD_GITHUB_OWNER, URISYS_URIGUARD_VERSION, URISYS_URIGUARD_WHEEL_URL, URISYS_URIGUARD_PYPI, URISYS_OFFLINE, URISYS_GITHUB_TOKEN, GH_TOKEN, GITHUB_TOKEN, URISYS_MIN_VERSION, URISYS_INIT_PROFILE, WAYLAND_DISPLAY, URISYS_URIRESOLVER_GITHUB_OWNER, URISYS_URIRESOLVER_VERSION, URISYS_URIRESOLVER_WHEEL_URL, URISYS_URIRESOLVER_PYPI, URISYS_NODE_ID, URISYS_NODE_ROOT, USER, URISYS_HOST_TRUST_SCRIPT_URL, URISYS_NODE_GITHUB_OWNER, URISYS_NODE_VERSION, URISYS_NODE_WHEEL_URL, URISYS_NODE_PIP_SPEC, URISYS_NODE_HOST, URISYS_NODE_PORT, URISYS_NODE_CONFIG, URISYS_VENV, TELLMESH_ROOT, URISYS_RESOLVER_CONFIG;
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

## Workflows

## Dependencies

### Runtime

```text markpact:deps python
PyYAML>=6.0
uricontrol>=0.1.11
uriresolver>=0.1.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0
uricontrol
uribrowser
uridocker
goal>=2.1.0
costs>=0.1.20
```

## Call Graph

*386 nodes · 500 edges · 84 modules · CC̄=4.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `build_parser` *(in src.urisys.cli.parser)* | 1 | 1 | 131 | **132** |
| `print` *(in scripts.analyze-thin-markpacts)* | 0 | 83 | 0 | **83** |
| `export_platform_artifacts` *(in src.urisys.markpact.platform_export)* | 7 | 2 | 35 | **37** |
| `_enable_host_trust_python` *(in src.urisys.node_host_trust)* | 8 | 1 | 35 | **36** |
| `analyze_run` *(in scripts.report.run_analysis)* | 13 ⚠ | 2 | 33 | **35** |
| `run_doctor` *(in src.urisys.doctor)* | 15 ⚠ | 3 | 30 | **33** |
| `print_json` *(in src.urisys.cli.helpers)* | 1 | 31 | 2 | **33** |
| `session_lab_10_flows` *(in scripts.test_sessions.lab_flows)* | 7 | 0 | 33 | **33** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/urisys
# generated in 0.21s
# nodes: 386 | edges: 500 | modules: 84
# CC̄=4.2

HUBS[20]:
  src.urisys.cli.parser.build_parser
    CC=1  in:1  out:131  total:132
  scripts.analyze-thin-markpacts.print
    CC=0  in:83  out:0  total:83
  src.urisys.markpact.platform_export.export_platform_artifacts
    CC=7  in:2  out:35  total:37
  src.urisys.node_host_trust._enable_host_trust_python
    CC=8  in:1  out:35  total:36
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  src.urisys.doctor.run_doctor
    CC=15  in:3  out:30  total:33
  src.urisys.cli.helpers.print_json
    CC=1  in:31  out:2  total:33
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  scripts.generate_pack_markpacts._render
    CC=14  in:1  out:31  total:32
  scripts.report.session.generate_report
    CC=9  in:2  out:27  total:29
  src.urisys.markpact.tests.run_markpact_tests
    CC=12  in:1  out:27  total:28
  src.urisys.managers.markpact_run_flow.run_markpact_flow
    CC=14  in:1  out:26  total:27
  src.urisys.markpact.compiler.MarkpactCompiler.compile
    CC=7  in:0  out:27  total:27
  src.urisys.markpact.validate_pack.validate_markpact_file
    CC=12  in:1  out:24  total:25
  scripts.pack_registry.pack_specs
    CC=7  in:5  out:20  total:25
  src.urisys.managers.markpact_materialize.materialize_markpact
    CC=8  in:1  out:22  total:23
  src.urisys.managers.markpact_validation.validate_implementation
    CC=14  in:1  out:22  total:23
  src.urisys.markpact.analyzer.report.analyze_markpact
    CC=12  in:1  out:22  total:23
  scripts.report.cli.main
    CC=4  in:0  out:23  total:23
  src.urisys.markpact.platform_export.collect_process_uris
    CC=6  in:2  out:20  total:22

MODULES:
  scripts.analyze-thin-markpacts  [1 funcs]
    print  CC=0  out:0
  scripts.check_contract_drift  [5 funcs]
    _check_spec  CC=7  out:8
    check_pair  CC=3  out:6
    contract_paths  CC=2  out:3
    main  CC=9  out:12
    manifest_path  CC=3  out:1
  scripts.check_flow_uri_patterns  [9 funcs]
    _manifest_schemes  CC=6  out:9
    _patterns_from_manifest_file  CC=6  out:8
    _register_manifest_file  CC=3  out:6
    collect_flow_uris  CC=10  out:13
    load_patterns  CC=8  out:12
    main  CC=7  out:20
    pattern_to_regex  CC=4  out:8
    uri_candidates  CC=4  out:4
    uri_matches  CC=4  out:3
  scripts.check_no_github_only_deps  [3 funcs]
    dep_name  CC=1  out:5
    find_violations  CC=13  out:13
    main  CC=4  out:9
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
  scripts.remove_urirouter_refs  [3 funcs]
    main  CC=10  out:9
    should_skip  CC=7  out:7
    transform  CC=2  out:2
  scripts.rename_uricontrol_docs  [3 funcs]
    apply  CC=2  out:1
    main  CC=6  out:9
    should_process  CC=6  out:3
  scripts.report.cli  [1 funcs]
    main  CC=4  out:23
  scripts.report.events  [4 funcs]
    load_event_records  CC=14  out:14
    merge_event_summaries  CC=10  out:16
    summarize_event_records  CC=14  out:15
    summarize_events  CC=8  out:10
  scripts.report.lab_checks  [6 funcs]
    _duplicate_recommendation  CC=6  out:1
    _response_to_outcome  CC=13  out:18
    analyze_lab_flows  CC=5  out:4
    check_duplicate_screenshots  CC=5  out:3
    iter_step_results  CC=9  out:7
    load_flow_outcomes  CC=3  out:4
  scripts.report.run_analysis  [2 funcs]
    analyze_run  CC=13  out:33
    write_run_analysis  CC=2  out:7
  scripts.report.run_markdown  [1 funcs]
    render_run_analysis_markdown  CC=7  out:16
  scripts.report.session  [4 funcs]
    _resolve_screenshot  CC=5  out:6
    _response_to_step_result  CC=12  out:20
    generate_report  CC=9  out:27
    infer_steps  CC=7  out:8
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
  scripts.test_sessions.lab_rdp  [2 funcs]
    capture_rdp_screenshot  CC=5  out:6
    capture_rdp_screenshot_wait  CC=9  out:6
  scripts.test_sessions.util  [5 funcs]
    file_md5  CC=2  out:4
    finalize_session  CC=5  out:13
    run_cmd  CC=6  out:12
    sleep_ports  CC=1  out:1
    write_meta  CC=1  out:3
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
  src.urisys.cli.commands.markpact  [15 funcs]
    _apply_strict_operations  CC=8  out:2
    _apply_strict_profile  CC=4  out:2
    _run_path_command  CC=6  out:5
    cmd_analyze  CC=6  out:11
    cmd_compile  CC=1  out:3
    cmd_contract  CC=6  out:14
    cmd_export_platform  CC=3  out:8
    cmd_markpact  CC=11  out:16
    cmd_materialize  CC=3  out:8
    cmd_pack  CC=6  out:10
  src.urisys.cli.commands.node  [3 funcs]
    _prepare_node_serve  CC=9  out:16
    cmd_node  CC=9  out:11
    cmd_node_host_trust  CC=5  out:10
  src.urisys.cli.commands.remote  [3 funcs]
    _parse_remote_host_trust  CC=2  out:10
    cmd_remote  CC=10  out:9
    cmd_remote_host_trust  CC=10  out:19
  src.urisys.cli.commands.runtime  [4 funcs]
    cmd_events  CC=1  out:3
    cmd_flow  CC=1  out:4
    cmd_serve  CC=1  out:3
    cmd_uri  CC=4  out:9
  src.urisys.cli.commands.setup  [2 funcs]
    cmd_doctor  CC=3  out:3
    cmd_init  CC=6  out:7
  src.urisys.cli.commands.update  [2 funcs]
    _installed  CC=2  out:1
    cmd_update  CC=17  out:18
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
    build_parser  CC=1  out:131
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [2 funcs]
    __init__  CC=1  out:1
    serve_forever  CC=1  out:3
  src.urisys.doctor  [15 funcs]
    _check_cli_path  CC=3  out:6
    _check_import  CC=5  out:12
    _check_min_version  CC=6  out:5
    _check_node_core_packs  CC=4  out:7
    _check_python  CC=3  out:3
    _check_uricore_authentic  CC=6  out:11
    _check_uricore_dist  CC=3  out:7
    _check_uriresolver_dist  CC=2  out:5
    _check_urirouter_squatter  CC=2  out:3
    _check_urisys_node_version  CC=6  out:9
  src.urisys.flow  [2 funcs]
    iter_steps  CC=7  out:8
    load_flow  CC=3  out:5
  src.urisys.http_server  [2 funcs]
    _read_json  CC=3  out:5
    create_server  CC=1  out:13
  src.urisys.init_setup  [17 funcs]
    _build_pip_result  CC=5  out:11
    _check_node_after_install  CC=7  out:7
    _pre_repair_uricore  CC=6  out:6
    _pre_repair_urirouter  CC=6  out:5
    _resolve_error_hint  CC=5  out:4
    _run_doctor_check  CC=3  out:3
    _run_pip_install  CC=2  out:2
    _verify_after_install  CC=8  out:9
    _write_profile_env  CC=4  out:3
    default_node_pip_spec  CC=1  out:1
  src.urisys.managers.markpact_manager  [5 funcs]
    _build_route  CC=1  out:1
    _compile_manifest  CC=1  out:1
    analyze  CC=1  out:1
    run_tests  CC=1  out:1
    validate  CC=1  out:1
  src.urisys.managers.markpact_materialize  [2 funcs]
    default_materialize_root  CC=1  out:1
    materialize_markpact  CC=8  out:22
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
  src.urisys.markpact.analyzer.format  [3 funcs]
    _normalize_markpact_issue  CC=1  out:2
    analyze_json_report  CC=14  out:20
    collect_analyze_issues  CC=10  out:12
  src.urisys.markpact.analyzer.lint  [2 funcs]
    _issue_message  CC=1  out:0
    run_lint  CC=8  out:14
  src.urisys.markpact.analyzer.report  [1 funcs]
    analyze_markpact  CC=12  out:22
  src.urisys.markpact.analyzer.resolver_lint  [1 funcs]
    lint_process_resolver_stubs  CC=9  out:7
  src.urisys.markpact.analyzer.rules.base  [2 funcs]
    check  CC=1  out:0
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
  src.urisys.markpact.flows  [8 funcs]
    _provider_scheme  CC=1  out:1
    _scheme  CC=1  out:1
    classify_flow  CC=11  out:10
    declared_uses  CC=1  out:1
    extract_flows  CC=11  out:9
    extract_modules  CC=7  out:8
    extract_protos  CC=7  out:6
    flow_uris  CC=8  out:10
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
  src.urisys.markpact.models  [4 funcs]
    parse_meta  CC=4  out:8
    safe_identifier  CC=3  out:6
    scheme_from_uri  CC=2  out:2
    source_hash  CC=1  out:4
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
  src.urisys.markpact.profile  [11 funcs]
    _build_flow_profiles  CC=6  out:11
    _cross_check_schemes  CC=9  out:8
    _flow_features  CC=6  out:9
    _flow_level_features  CC=3  out:4
    _required_features  CC=4  out:7
    _step_features  CC=7  out:9
    _text_pattern_features  CC=4  out:3
    _validate_scheme_requirements  CC=1  out:2
    declared_packs  CC=5  out:8
    declared_schemes  CC=11  out:17
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
  src.urisys.node_host_trust  [8 funcs]
    _enable_host_trust_python  CC=8  out:35
    _git_pull  CC=3  out:3
    default_node_id  CC=2  out:3
    remote_host_trust_command  CC=3  out:7
    resolve_enable_host_trust_script  CC=3  out:2
    resolve_urisys_node_bin  CC=8  out:15
    resolve_urisys_node_root  CC=8  out:13
    run_host_trust  CC=10  out:16
  src.urisys.node_install  [7 funcs]
    _missing_core_node_modules  CC=3  out:3
    _module_for_boot_spec  CC=3  out:2
    _node_version_ok  CC=2  out:3
    diagnose_urisys_node  CC=6  out:14
    ensure_core_node_packs  CC=5  out:7
    install_urisys_node  CC=8  out:19
    is_importable  CC=1  out:1
  src.urisys.uricore_install  [10 funcs]
    _module_exists  CC=1  out:1
    _pkg_version  CC=2  out:1
    diagnose_uricore  CC=3  out:4
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    is_wrong_uricore_installed  CC=2  out:3
    pip_run  CC=4  out:2
    pip_spec  CC=3  out:8
    repair_uricore  CC=6  out:10
    wheel_url  CC=3  out:5
  src.urisys.uriguard_install  [10 funcs]
    _module_exists  CC=1  out:1
    _pkg_version  CC=2  out:1
    diagnose_uriguard  CC=3  out:4
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    is_wrong_urirouter_installed  CC=1  out:2
    pip_run  CC=4  out:2
    pip_spec  CC=3  out:8
    uninstall_squatted_urirouter  CC=4  out:3
    wheel_url  CC=3  out:5
  src.urisys.uriresolver_install  [6 funcs]
    _module_exists  CC=1  out:1
    diagnose_uriresolver  CC=2  out:2
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    pip_spec  CC=3  out:8
    wheel_url  CC=3  out:5
  src.urisys.version_resolve  [5 funcs]
    _get_json  CC=7  out:11
    github_latest  CC=3  out:3
    parse_version  CC=7  out:7
    pypi_latest  CC=3  out:3
    resolve_install_spec  CC=8  out:8

EDGES:
  src.urisys.uricore_install.wheel_url → src.urisys.uricore_install.github_owner
  src.urisys.uricore_install.wheel_url → src.urisys.uricore_install.github_version
  src.urisys.uricore_install.pip_spec → src.urisys.version_resolve.resolve_install_spec
  src.urisys.uricore_install.pip_spec → src.urisys.uricore_install.wheel_url
  src.urisys.uricore_install.pip_spec → src.urisys.uricore_install.github_owner
  src.urisys.uricore_install.pip_spec → src.urisys.uricore_install.github_version
  src.urisys.uricore_install.is_wrong_uricore_installed → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.is_wrong_uricore_installed → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install.pip_spec
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.pip_run
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.wheel_url
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.pip_spec
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.diagnose_uricore
  src.urisys.uriguard_install.wheel_url → src.urisys.uriguard_install.github_owner
  src.urisys.uriguard_install.wheel_url → src.urisys.uriguard_install.github_version
  src.urisys.uriguard_install.pip_spec → src.urisys.version_resolve.resolve_install_spec
  src.urisys.uriguard_install.pip_spec → src.urisys.uriguard_install.wheel_url
  src.urisys.uriguard_install.pip_spec → src.urisys.uriguard_install.github_owner
  src.urisys.uriguard_install.pip_spec → src.urisys.uriguard_install.github_version
  src.urisys.uriguard_install.is_wrong_urirouter_installed → src.urisys.uriguard_install._pkg_version
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install._module_exists
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install.is_wrong_urirouter_installed
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install._pkg_version
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install.pip_spec
  src.urisys.uriguard_install.uninstall_squatted_urirouter → src.urisys.uriguard_install.pip_run
  src.urisys.uriguard_install.uninstall_squatted_urirouter → src.urisys.uriguard_install.is_wrong_urirouter_installed
  src.urisys.version_resolve.github_latest → src.urisys.version_resolve._get_json
  src.urisys.version_resolve.pypi_latest → src.urisys.version_resolve._get_json
  src.urisys.version_resolve.resolve_install_spec → src.urisys.version_resolve.github_latest
  src.urisys.version_resolve.resolve_install_spec → src.urisys.version_resolve.pypi_latest
  src.urisys.version_resolve.resolve_install_spec → src.urisys.version_resolve.parse_version
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
  src.urisys.doctor._check_urisys_node_version → src.urisys.doctor._pkg_version
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
# generated in 0.21s
# nodes: 386 | edges: 500 | modules: 84
# CC̄=4.2

HUBS[20]:
  src.urisys.cli.parser.build_parser
    CC=1  in:1  out:131  total:132
  scripts.analyze-thin-markpacts.print
    CC=0  in:83  out:0  total:83
  src.urisys.markpact.platform_export.export_platform_artifacts
    CC=7  in:2  out:35  total:37
  src.urisys.node_host_trust._enable_host_trust_python
    CC=8  in:1  out:35  total:36
  scripts.report.run_analysis.analyze_run
    CC=13  in:2  out:33  total:35
  src.urisys.doctor.run_doctor
    CC=15  in:3  out:30  total:33
  src.urisys.cli.helpers.print_json
    CC=1  in:31  out:2  total:33
  scripts.test_sessions.lab_flows.session_lab_10_flows
    CC=7  in:0  out:33  total:33
  scripts.generate_pack_markpacts._render
    CC=14  in:1  out:31  total:32
  scripts.report.session.generate_report
    CC=9  in:2  out:27  total:29
  src.urisys.markpact.tests.run_markpact_tests
    CC=12  in:1  out:27  total:28
  src.urisys.managers.markpact_run_flow.run_markpact_flow
    CC=14  in:1  out:26  total:27
  src.urisys.markpact.compiler.MarkpactCompiler.compile
    CC=7  in:0  out:27  total:27
  src.urisys.markpact.validate_pack.validate_markpact_file
    CC=12  in:1  out:24  total:25
  scripts.pack_registry.pack_specs
    CC=7  in:5  out:20  total:25
  src.urisys.managers.markpact_materialize.materialize_markpact
    CC=8  in:1  out:22  total:23
  src.urisys.managers.markpact_validation.validate_implementation
    CC=14  in:1  out:22  total:23
  src.urisys.markpact.analyzer.report.analyze_markpact
    CC=12  in:1  out:22  total:23
  scripts.report.cli.main
    CC=4  in:0  out:23  total:23
  src.urisys.markpact.platform_export.collect_process_uris
    CC=6  in:2  out:20  total:22

MODULES:
  scripts.analyze-thin-markpacts  [1 funcs]
    print  CC=0  out:0
  scripts.check_contract_drift  [5 funcs]
    _check_spec  CC=7  out:8
    check_pair  CC=3  out:6
    contract_paths  CC=2  out:3
    main  CC=9  out:12
    manifest_path  CC=3  out:1
  scripts.check_flow_uri_patterns  [9 funcs]
    _manifest_schemes  CC=6  out:9
    _patterns_from_manifest_file  CC=6  out:8
    _register_manifest_file  CC=3  out:6
    collect_flow_uris  CC=10  out:13
    load_patterns  CC=8  out:12
    main  CC=7  out:20
    pattern_to_regex  CC=4  out:8
    uri_candidates  CC=4  out:4
    uri_matches  CC=4  out:3
  scripts.check_no_github_only_deps  [3 funcs]
    dep_name  CC=1  out:5
    find_violations  CC=13  out:13
    main  CC=4  out:9
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
  scripts.remove_urirouter_refs  [3 funcs]
    main  CC=10  out:9
    should_skip  CC=7  out:7
    transform  CC=2  out:2
  scripts.rename_uricontrol_docs  [3 funcs]
    apply  CC=2  out:1
    main  CC=6  out:9
    should_process  CC=6  out:3
  scripts.report.cli  [1 funcs]
    main  CC=4  out:23
  scripts.report.events  [4 funcs]
    load_event_records  CC=14  out:14
    merge_event_summaries  CC=10  out:16
    summarize_event_records  CC=14  out:15
    summarize_events  CC=8  out:10
  scripts.report.lab_checks  [6 funcs]
    _duplicate_recommendation  CC=6  out:1
    _response_to_outcome  CC=13  out:18
    analyze_lab_flows  CC=5  out:4
    check_duplicate_screenshots  CC=5  out:3
    iter_step_results  CC=9  out:7
    load_flow_outcomes  CC=3  out:4
  scripts.report.run_analysis  [2 funcs]
    analyze_run  CC=13  out:33
    write_run_analysis  CC=2  out:7
  scripts.report.run_markdown  [1 funcs]
    render_run_analysis_markdown  CC=7  out:16
  scripts.report.session  [4 funcs]
    _resolve_screenshot  CC=5  out:6
    _response_to_step_result  CC=12  out:20
    generate_report  CC=9  out:27
    infer_steps  CC=7  out:8
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
  scripts.test_sessions.lab_rdp  [2 funcs]
    capture_rdp_screenshot  CC=5  out:6
    capture_rdp_screenshot_wait  CC=9  out:6
  scripts.test_sessions.util  [5 funcs]
    file_md5  CC=2  out:4
    finalize_session  CC=5  out:13
    run_cmd  CC=6  out:12
    sleep_ports  CC=1  out:1
    write_meta  CC=1  out:3
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
  src.urisys.cli.commands.markpact  [15 funcs]
    _apply_strict_operations  CC=8  out:2
    _apply_strict_profile  CC=4  out:2
    _run_path_command  CC=6  out:5
    cmd_analyze  CC=6  out:11
    cmd_compile  CC=1  out:3
    cmd_contract  CC=6  out:14
    cmd_export_platform  CC=3  out:8
    cmd_markpact  CC=11  out:16
    cmd_materialize  CC=3  out:8
    cmd_pack  CC=6  out:10
  src.urisys.cli.commands.node  [3 funcs]
    _prepare_node_serve  CC=9  out:16
    cmd_node  CC=9  out:11
    cmd_node_host_trust  CC=5  out:10
  src.urisys.cli.commands.remote  [3 funcs]
    _parse_remote_host_trust  CC=2  out:10
    cmd_remote  CC=10  out:9
    cmd_remote_host_trust  CC=10  out:19
  src.urisys.cli.commands.runtime  [4 funcs]
    cmd_events  CC=1  out:3
    cmd_flow  CC=1  out:4
    cmd_serve  CC=1  out:3
    cmd_uri  CC=4  out:9
  src.urisys.cli.commands.setup  [2 funcs]
    cmd_doctor  CC=3  out:3
    cmd_init  CC=6  out:7
  src.urisys.cli.commands.update  [2 funcs]
    _installed  CC=2  out:1
    cmd_update  CC=17  out:18
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
    build_parser  CC=1  out:131
  src.urisys.controllers.flow_controller  [1 funcs]
    run  CC=6  out:19
  src.urisys.controllers.server_controller  [2 funcs]
    __init__  CC=1  out:1
    serve_forever  CC=1  out:3
  src.urisys.doctor  [15 funcs]
    _check_cli_path  CC=3  out:6
    _check_import  CC=5  out:12
    _check_min_version  CC=6  out:5
    _check_node_core_packs  CC=4  out:7
    _check_python  CC=3  out:3
    _check_uricore_authentic  CC=6  out:11
    _check_uricore_dist  CC=3  out:7
    _check_uriresolver_dist  CC=2  out:5
    _check_urirouter_squatter  CC=2  out:3
    _check_urisys_node_version  CC=6  out:9
  src.urisys.flow  [2 funcs]
    iter_steps  CC=7  out:8
    load_flow  CC=3  out:5
  src.urisys.http_server  [2 funcs]
    _read_json  CC=3  out:5
    create_server  CC=1  out:13
  src.urisys.init_setup  [17 funcs]
    _build_pip_result  CC=5  out:11
    _check_node_after_install  CC=7  out:7
    _pre_repair_uricore  CC=6  out:6
    _pre_repair_urirouter  CC=6  out:5
    _resolve_error_hint  CC=5  out:4
    _run_doctor_check  CC=3  out:3
    _run_pip_install  CC=2  out:2
    _verify_after_install  CC=8  out:9
    _write_profile_env  CC=4  out:3
    default_node_pip_spec  CC=1  out:1
  src.urisys.managers.markpact_manager  [5 funcs]
    _build_route  CC=1  out:1
    _compile_manifest  CC=1  out:1
    analyze  CC=1  out:1
    run_tests  CC=1  out:1
    validate  CC=1  out:1
  src.urisys.managers.markpact_materialize  [2 funcs]
    default_materialize_root  CC=1  out:1
    materialize_markpact  CC=8  out:22
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
  src.urisys.markpact.analyzer.format  [3 funcs]
    _normalize_markpact_issue  CC=1  out:2
    analyze_json_report  CC=14  out:20
    collect_analyze_issues  CC=10  out:12
  src.urisys.markpact.analyzer.lint  [2 funcs]
    _issue_message  CC=1  out:0
    run_lint  CC=8  out:14
  src.urisys.markpact.analyzer.report  [1 funcs]
    analyze_markpact  CC=12  out:22
  src.urisys.markpact.analyzer.resolver_lint  [1 funcs]
    lint_process_resolver_stubs  CC=9  out:7
  src.urisys.markpact.analyzer.rules.base  [2 funcs]
    check  CC=1  out:0
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
  src.urisys.markpact.flows  [8 funcs]
    _provider_scheme  CC=1  out:1
    _scheme  CC=1  out:1
    classify_flow  CC=11  out:10
    declared_uses  CC=1  out:1
    extract_flows  CC=11  out:9
    extract_modules  CC=7  out:8
    extract_protos  CC=7  out:6
    flow_uris  CC=8  out:10
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
  src.urisys.markpact.models  [4 funcs]
    parse_meta  CC=4  out:8
    safe_identifier  CC=3  out:6
    scheme_from_uri  CC=2  out:2
    source_hash  CC=1  out:4
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
  src.urisys.markpact.profile  [11 funcs]
    _build_flow_profiles  CC=6  out:11
    _cross_check_schemes  CC=9  out:8
    _flow_features  CC=6  out:9
    _flow_level_features  CC=3  out:4
    _required_features  CC=4  out:7
    _step_features  CC=7  out:9
    _text_pattern_features  CC=4  out:3
    _validate_scheme_requirements  CC=1  out:2
    declared_packs  CC=5  out:8
    declared_schemes  CC=11  out:17
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
  src.urisys.node_host_trust  [8 funcs]
    _enable_host_trust_python  CC=8  out:35
    _git_pull  CC=3  out:3
    default_node_id  CC=2  out:3
    remote_host_trust_command  CC=3  out:7
    resolve_enable_host_trust_script  CC=3  out:2
    resolve_urisys_node_bin  CC=8  out:15
    resolve_urisys_node_root  CC=8  out:13
    run_host_trust  CC=10  out:16
  src.urisys.node_install  [7 funcs]
    _missing_core_node_modules  CC=3  out:3
    _module_for_boot_spec  CC=3  out:2
    _node_version_ok  CC=2  out:3
    diagnose_urisys_node  CC=6  out:14
    ensure_core_node_packs  CC=5  out:7
    install_urisys_node  CC=8  out:19
    is_importable  CC=1  out:1
  src.urisys.uricore_install  [10 funcs]
    _module_exists  CC=1  out:1
    _pkg_version  CC=2  out:1
    diagnose_uricore  CC=3  out:4
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    is_wrong_uricore_installed  CC=2  out:3
    pip_run  CC=4  out:2
    pip_spec  CC=3  out:8
    repair_uricore  CC=6  out:10
    wheel_url  CC=3  out:5
  src.urisys.uriguard_install  [10 funcs]
    _module_exists  CC=1  out:1
    _pkg_version  CC=2  out:1
    diagnose_uriguard  CC=3  out:4
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    is_wrong_urirouter_installed  CC=1  out:2
    pip_run  CC=4  out:2
    pip_spec  CC=3  out:8
    uninstall_squatted_urirouter  CC=4  out:3
    wheel_url  CC=3  out:5
  src.urisys.uriresolver_install  [6 funcs]
    _module_exists  CC=1  out:1
    diagnose_uriresolver  CC=2  out:2
    github_owner  CC=1  out:2
    github_version  CC=1  out:3
    pip_spec  CC=3  out:8
    wheel_url  CC=3  out:5
  src.urisys.version_resolve  [5 funcs]
    _get_json  CC=7  out:11
    github_latest  CC=3  out:3
    parse_version  CC=7  out:7
    pypi_latest  CC=3  out:3
    resolve_install_spec  CC=8  out:8

EDGES:
  src.urisys.uricore_install.wheel_url → src.urisys.uricore_install.github_owner
  src.urisys.uricore_install.wheel_url → src.urisys.uricore_install.github_version
  src.urisys.uricore_install.pip_spec → src.urisys.version_resolve.resolve_install_spec
  src.urisys.uricore_install.pip_spec → src.urisys.uricore_install.wheel_url
  src.urisys.uricore_install.pip_spec → src.urisys.uricore_install.github_owner
  src.urisys.uricore_install.pip_spec → src.urisys.uricore_install.github_version
  src.urisys.uricore_install.is_wrong_uricore_installed → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.is_wrong_uricore_installed → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install.is_wrong_uricore_installed
  src.urisys.uricore_install.diagnose_uricore → src.urisys.uricore_install.pip_spec
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install._pkg_version
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.pip_run
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.wheel_url
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.pip_spec
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install._module_exists
  src.urisys.uricore_install.repair_uricore → src.urisys.uricore_install.diagnose_uricore
  src.urisys.uriguard_install.wheel_url → src.urisys.uriguard_install.github_owner
  src.urisys.uriguard_install.wheel_url → src.urisys.uriguard_install.github_version
  src.urisys.uriguard_install.pip_spec → src.urisys.version_resolve.resolve_install_spec
  src.urisys.uriguard_install.pip_spec → src.urisys.uriguard_install.wheel_url
  src.urisys.uriguard_install.pip_spec → src.urisys.uriguard_install.github_owner
  src.urisys.uriguard_install.pip_spec → src.urisys.uriguard_install.github_version
  src.urisys.uriguard_install.is_wrong_urirouter_installed → src.urisys.uriguard_install._pkg_version
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install._module_exists
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install.is_wrong_urirouter_installed
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install._pkg_version
  src.urisys.uriguard_install.diagnose_uriguard → src.urisys.uriguard_install.pip_spec
  src.urisys.uriguard_install.uninstall_squatted_urirouter → src.urisys.uriguard_install.pip_run
  src.urisys.uriguard_install.uninstall_squatted_urirouter → src.urisys.uriguard_install.is_wrong_urirouter_installed
  src.urisys.version_resolve.github_latest → src.urisys.version_resolve._get_json
  src.urisys.version_resolve.pypi_latest → src.urisys.version_resolve._get_json
  src.urisys.version_resolve.resolve_install_spec → src.urisys.version_resolve.github_latest
  src.urisys.version_resolve.resolve_install_spec → src.urisys.version_resolve.pypi_latest
  src.urisys.version_resolve.resolve_install_spec → src.urisys.version_resolve.parse_version
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
  src.urisys.doctor._check_urisys_node_version → src.urisys.doctor._pkg_version
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 184f 16015L | python:120,shell:51,yaml:7,json:1,yml:1,javascript:1,toml:1 | 2026-06-19
# generated in 0.03s
# CC̅=4.2 | critical:2/563 | dups:0 | cycles:0

HEALTH[2]:
  🟡 CC    run_doctor CC=15 (limit:15)
  🟡 CC    cmd_update CC=17 (limit:15)

REFACTOR[1]:
  1. split 2 high-CC methods  (CC>15)

PIPELINES[130]:
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
  [6] Src [_dist_top_levels]: _dist_top_levels
      PURITY: 100% pure
  [7] Src [main]: main → _doctor_main → run_doctor → _check_uricore_authentic → ...(2 more)
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
  [15] Src [cmd_init]: cmd_init → run_init → default_pip_specs → pip_spec → ...(3 more)
      PURITY: 100% pure
  [16] Src [cmd_node]: cmd_node → cmd_remote → cmd_remote_host_trust → _parse_remote_host_trust
      PURITY: 100% pure
  [17] Src [cmd_update]: cmd_update → print_json → print
      PURITY: 100% pure
  [18] Src [cmd_markpact]: cmd_markpact → resolve_markpact_source
      PURITY: 100% pure
  [19] Src [_issue]: _issue
      PURITY: 100% pure
  [20] Src [to_dict]: to_dict
      PURITY: 100% pure
  [21] Src [__init__]: __init__
      PURITY: 100% pure
  [22] Src [compile]: compile → compile_context → read_blocks → parse_meta
      PURITY: 100% pure
  [23] Src [run]: run → routes_summary
      PURITY: 100% pure
  [24] Src [run]: run → _resolve_flow_ids → pick_flow_id
      PURITY: 100% pure
  [25] Src [run]: run → build_runtime → extend_tellmesh_paths → tellmesh_root
      PURITY: 100% pure
  [26] Src [run]: run → build_runtime → extend_tellmesh_paths → tellmesh_root
      PURITY: 100% pure
  [27] Src [run]: run → build_runtime → extend_tellmesh_paths → tellmesh_root
      PURITY: 100% pure
  [28] Src [check]: check
      PURITY: 100% pure
  [29] Src [check]: check → flow_uris
      PURITY: 100% pure
  [30] Src [check]: check → cap_uri
      PURITY: 100% pure
  [31] Src [check]: check → cap_uri
      PURITY: 100% pure
  [32] Src [check]: check → cap_uri
      PURITY: 100% pure
  [33] Src [check]: check → cap_uri
      PURITY: 100% pure
  [34] Src [check]: check
      PURITY: 100% pure
  [35] Src [check]: check
      PURITY: 100% pure
  [36] Src [check]: check
      PURITY: 100% pure
  [37] Src [check]: check
      PURITY: 100% pure
  [38] Src [__init__]: __init__
      PURITY: 100% pure
  [39] Src [run]: run → load_flow
      PURITY: 100% pure
  [40] Src [close]: close
      PURITY: 100% pure
  [41] Src [__init__]: __init__ → create_server → _read_json
      PURITY: 100% pure
  [42] Src [serve_forever]: serve_forever → print
      PURITY: 100% pure
  [43] Src [__init__]: __init__
      PURITY: 100% pure
  [44] Src [call]: call
      PURITY: 100% pure
  [45] Src [explain]: explain
      PURITY: 100% pure
  [46] Src [routes]: routes
      PURITY: 100% pure
  [47] Src [close]: close
      PURITY: 100% pure
  [48] Src [__init__]: __init__
      PURITY: 100% pure
  [49] Src [list_events]: list_events
      PURITY: 100% pure
  [50] Src [build_context]: build_context
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.2    ←in:0  →out:0
  │ !! doctor                     427L  1C   15m  CC=15     ←3
  │ node_host_trust            387L  0C   10m  CC=10     ←2
  │ platform_export            311L  0C    8m  CC=11     ←3
  │ init_setup                 299L  0C   17m  CC=14     ←2
  │ parser                     263L  0C    2m  CC=1      ←1
  │ source_manager             218L  2C   12m  CC=11     ←0
  │ markpact                   211L  0C   15m  CC=11     ←0
  │ node_install               211L  0C   16m  CC=8      ←3
  │ profile                    194L  1C   13m  CC=11     ←4
  │ pack_manager               190L  1C   19m  CC=8      ←0
  │ markpact_pack_deps         189L  0C   13m  CC=12     ←4
  │ markpact_run_flow          160L  0C    6m  CC=14     ←2
  │ markpact_validation        156L  0C    6m  CC=14     ←1
  │ uricore_install            143L  0C   11m  CC=6      ←2
  │ manifest                   127L  0C    7m  CC=12     ←2
  │ compiler                   118L  1C    5m  CC=7      ←0
  │ cache                      118L  0C    5m  CC=4      ←1
  │ uriguard_install           117L  0C   10m  CC=4      ←2
  │ bootstrap                  116L  0C    5m  CC=8      ←0
  │ flows                      107L  0C    8m  CC=11     ←6
  │ capabilities               107L  5C    5m  CC=10     ←0
  │ version_resolve             99L  0C    5m  CC=8      ←6
  │ remote                      98L  0C    3m  CC=10     ←1
  │ models                      98L  3C    5m  CC=6      ←12
  │ node                        94L  0C    3m  CC=9      ←0
  │ validate_pack               92L  0C    2m  CC=12     ←1
  │ format                      90L  0C    4m  CC=14     ←1
  │ !! update                      88L  0C    3m  CC=17     ←0
  │ flow                        86L  1C    4m  CC=9      ←0
  │ artifacts                   80L  0C    6m  CC=4      ←2
  │ tests                       78L  0C    3m  CC=12     ←1
  │ http_server                 76L  1C    4m  CC=3      ←1
  │ markpact_manager            72L  1C   11m  CC=1      ←1
  │ markpact_materialize        69L  0C    2m  CC=8      ←1
  │ __init__                    66L  0C    1m  CC=6      ←1
  │ lint                        66L  0C    2m  CC=8      ←1
  │ blocks                      63L  0C    4m  CC=6      ←6
  │ urisys_install              63L  0C    5m  CC=7      ←0
  │ uriresolver_install         60L  0C    6m  CC=3      ←1
  │ resolver_lint               60L  0C    1m  CC=9      ←1
  │ report                      57L  0C    1m  CC=12     ←1
  │ pack                        54L  0C    4m  CC=8      ←7
  │ runtime_build               53L  0C    3m  CC=7      ←7
  │ runtime                     51L  0C    4m  CC=4      ←0
  │ handlers                    51L  0C    3m  CC=7      ←3
  │ flows                       46L  2C    2m  CC=4      ←0
  │ defaults                    46L  0C    0m  CC=0.0    ←0
  │ pack                        45L  2C    2m  CC=6      ←0
  │ flow_controller             33L  1C    3m  CC=6      ←0
  │ uri_controller              33L  1C    5m  CC=3      ←0
  │ errors                      32L  0C    1m  CC=8      ←1
  │ setup                       31L  0C    2m  CC=6      ←0
  │ runtime_manager             30L  1C    5m  CC=2      ←0
  │ helpers                     28L  0C    3m  CC=3      ←7
  │ adapter                     28L  1C    1m  CC=3      ←0
  │ interface                   28L  1C    1m  CC=2      ←0
  │ __init__                    27L  0C    0m  CC=0.0    ←0
  │ flow                        25L  0C    2m  CC=7      ←1
  │ config                      25L  0C    2m  CC=7      ←1
  │ context                     25L  1C    0m  CC=0.0    ←0
  │ markpact_profile            25L  0C    0m  CC=0.0    ←0
  │ service                     24L  1C    1m  CC=6      ←0
  │ __init__                    24L  0C    0m  CC=0.0    ←0
  │ __init__                    24L  0C    0m  CC=0.0    ←0
  │ route_manager               23L  1C    3m  CC=2      ←0
  │ markpact_models             23L  0C    0m  CC=0.0    ←0
  │ contract_gen                23L  0C    0m  CC=0.0    ←0
  │ markpact_flows              23L  0C    0m  CC=0.0    ←0
  │ schemes                     19L  1C    1m  CC=2      ←0
  │ server_controller           19L  1C    2m  CC=1      ←0
  │ pack                        18L  1C    1m  CC=1      ←0
  │ policy_manager              18L  1C    1m  CC=2      ←0
  │ main                        17L  0C    1m  CC=3      ←0
  │ base                        17L  1C    2m  CC=3      ←2
  │ __init__                    17L  0C    0m  CC=0.0    ←0
  │ markpact_pack_gen           17L  0C    0m  CC=0.0    ←0
  │ context                     15L  1C    0m  CC=0.0    ←0
  │ markpact_run                15L  0C    0m  CC=0.0    ←0
  │ bridge_manager              14L  1C    1m  CC=3      ←0
  │ base                        13L  1C    1m  CC=1      ←0
  │ event_manager               13L  1C    2m  CC=1      ←0
  │ platform_export             13L  0C    0m  CC=0.0    ←0
  │ protocol                    10L  1C    1m  CC=1      ←0
  │ __init__                    10L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __main__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=4.2    ←in:37  →out:0
  │ pack_sync                  371L  0C   19m  CC=14     ←0
  │ generate_pack_markpacts    370L  0C   16m  CC=14     ←0
  │ lab_flows                  320L  0C    5m  CC=13     ←0
  │ pack_registry              261L  1C    7m  CC=7      ←4
  │ scan-browser-sessions      208L  0C    9m  CC=13     ←0
  │ util                       201L  0C   14m  CC=9      ←2
  │ lab_checks                 187L  0C   10m  CC=13     ←1
  │ run-office-simulate-lenovo.sh   182L  0C    6m  CC=0.0    ←0
  │ lab_rdp                    180L  0C    8m  CC=11     ←1
  │ update-ecosystem-readmes   172L  0C    4m  CC=4      ←0
  │ run-urisys-node-docker-e2e.sh   163L  0C    5m  CC=0.0    ←2
  │ check_flow_uri_patterns    160L  0C   10m  CC=10     ←0
  │ expectations               153L  0C    9m  CC=11     ←1
  │ office-simulate-loop       146L  0C    5m  CC=10     ←1
  │ deploy-lenovo-node.sh      138L  0C    5m  CC=0.0    ←0
  │ events                     138L  0C    5m  CC=14     ←1
  │ run-email-mailpit-e2e.sh   134L  0C    4m  CC=0.0    ←0
  │ run-office-simulate-e2e.sh   130L  0C    4m  CC=0.0    ←0
  │ run_analysis               129L  0C    5m  CC=13     ←1
  │ session                    124L  0C    8m  CC=12     ←2
  │ session_markdown           120L  0C    8m  CC=7      ←1
  │ run-lenovo-office-linkedin.sh   118L  0C    3m  CC=0.0    ←0
  │ remove_urirouter_refs      118L  0C    3m  CC=10     ←0
  │ run-office-writer-e2e.sh   113L  0C    4m  CC=0.0    ←2
  │ check_contract_drift       110L  0C    5m  CC=9      ←0
  │ remote-node-smoke.sh        99L  0C    2m  CC=0.0    ←0
  │ rename_uricontrol_docs      98L  0C    3m  CC=6      ←0
  │ models                      86L  5C    0m  CC=0.0    ←0
  │ publish-tellmesh-wheels.sh    83L  0C    1m  CC=0.0    ←0
  │ publish-uri-releases.sh     82L  0C    3m  CC=0.0    ←0
  │ lenovo-node-session.sh      81L  0C    1m  CC=0.0    ←0
  │ paths.sh                    69L  0C    7m  CC=0.0    ←0
  │ check_no_github_only_deps    68L  0C    3m  CC=13     ←0
  │ run-markpact-ci.sh          66L  0C    0m  CC=0.0    ←0
  │ validate-all-markpacts.sh    65L  0C    1m  CC=0.0    ←0
  │ ci-checkout-siblings.sh     62L  0C    1m  CC=0.0    ←0
  │ validate-pypi-metadata.sh    62L  0C    2m  CC=0.0    ←0
  │ __init__                    61L  0C    0m  CC=0.0    ←0
  │ test-python-matrix.sh       58L  0C    1m  CC=0.0    ←0
  │ bootstrap-lenovo-local.sh    57L  0C    0m  CC=0.0    ←0
  │ materialize-all-showcases.sh    53L  0C    1m  CC=0.0    ←0
  │ publish-pypi-packs.sh       53L  0C    0m  CC=0.0    ←0
  │ session_report              49L  0C    0m  CC=0.0    ←0
  │ analyze-thin-markpacts.sh    48L  0C    1m  CC=0.0    ←19
  │ run-nl-log-smoke.sh         43L  0C    1m  CC=0.0    ←0
  │ analyze-legacy-contract-packs.sh    43L  0C    0m  CC=0.0    ←0
  │ run_markdown                42L  0C    1m  CC=7      ←1
  │ cli                         41L  0C    1m  CC=4      ←0
  │ analyze-process-markpacts.sh    39L  0C    0m  CC=0.0    ←0
  │ sync-vendored-pack.sh       38L  0C    0m  CC=0.0    ←0
  │ marksync-materialize.sh     31L  0C    0m  CC=0.0    ←0
  │ ci-install-siblings.sh      28L  0C    1m  CC=0.0    ←0
  │ publish-github-release.sh    28L  0C    0m  CC=0.0    ←0
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
  │ !! goal.yaml                  527L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             143L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                94L  0C    0m  CC=0.0    ←0
  │ Makefile                    72L  0C    0m  CC=0.0    ←0
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
                                       scripts             src.urisys  scripts.test_sessions         scripts.report
                scripts                     ──                    ←23                     ←8                     ←6  hub
             src.urisys                     23                     ──                                            ←1  !! fan-out
  scripts.test_sessions                      8                                            ──                         !! fan-out
         scripts.report                      6                      1                                            ──
  CYCLES: none
  HUB: scripts/ (fan-in=37)
  SMELL: scripts.test_sessions/ fan-out=8 → split needed
  SMELL: src.urisys/ fan-out=23 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 7 groups | 114f 9899L | 2026-06-19

SUMMARY:
  files_scanned: 114
  total_lines:   9899
  dup_groups:    7
  dup_fragments: 18
  saved_lines:   113
  scan_ms:       2392

HOTSPOTS[7] (files with most duplication):
  src/urisys/uriguard_install.py  dup=41L  groups=4  frags=4  (0.4%)
  src/urisys/uricore_install.py  dup=33L  groups=3  frags=3  (0.3%)
  src/urisys/markpact/analyzer/rules/capabilities.py  dup=30L  groups=1  frags=2  (0.3%)
  src/urisys/uriresolver_install.py  dup=23L  groups=2  frags=2  (0.2%)
  src/urisys/node_install.py  dup=11L  groups=1  frags=1  (0.1%)
  src/urisys/urisys_install.py  dup=9L  groups=1  frags=1  (0.1%)
  scripts/report/run_analysis.py  dup=8L  groups=1  frags=1  (0.1%)

DUPLICATES[7] (ranked by impact):
  [47e13f850f1a5b25]   STRU  pip_spec  L=15 N=3 saved=30 sim=1.00
      src/urisys/uricore_install.py:39-53  (pip_spec)
      src/urisys/uriguard_install.py:40-53  (pip_spec)
      src/urisys/uriresolver_install.py:34-47  (pip_spec)
  [3f18ae8c291ee1c9]   EXAC  pip_run  L=11 N=3 saved=22 sim=1.00
      src/urisys/node_install.py:69-79  (pip_run)
      src/urisys/uricore_install.py:111-121  (pip_run)
      src/urisys/uriguard_install.py:94-104  (pip_run)
  [fb79570911824591]   STRU  wheel_url  L=9 N=3 saved=18 sim=1.00
      src/urisys/uriguard_install.py:29-37  (wheel_url)
      src/urisys/uriresolver_install.py:23-31  (wheel_url)
      src/urisys/urisys_install.py:22-30  (wheel_url)
  [4ebe2e0e30d6012c]   STRU  check  L=15 N=2 saved=15 sim=1.00
      src/urisys/markpact/analyzer/rules/capabilities.py:30-44  (check)
      src/urisys/markpact/analyzer/rules/capabilities.py:50-64  (check)
  [487da026fcebd9df]   EXAC  _pkg_version  L=7 N=3 saved=14 sim=1.00
      src/urisys/doctor.py:29-35  (_pkg_version)
      src/urisys/uricore_install.py:56-62  (_pkg_version)
      src/urisys/uriguard_install.py:56-62  (_pkg_version)
  [bb100fda4da2fc0e]   STRU  write_run_analysis  L=8 N=2 saved=8 sim=1.00
      scripts/report/run_analysis.py:122-129  (write_run_analysis)
      scripts/report/session_io.py:12-19  (write_session_report)
  [609d6158ce918081]   EXAC  manifest_path  L=6 N=2 saved=6 sim=1.00
      scripts/check_contract_drift.py:31-36  (manifest_path)
      scripts/check_flow_uri_patterns.py:36-41  (manifest_path)

REFACTOR[7] (ranked by priority):
  [1] ○ extract_function   → src/urisys/utils/pip_spec.py
      WHY: 3 occurrences of 15-line block across 3 files — saves 30 lines
      FILES: src/urisys/uricore_install.py, src/urisys/uriguard_install.py, src/urisys/uriresolver_install.py
  [2] ○ extract_function   → src/urisys/utils/pip_run.py
      WHY: 3 occurrences of 11-line block across 3 files — saves 22 lines
      FILES: src/urisys/node_install.py, src/urisys/uricore_install.py, src/urisys/uriguard_install.py
  [3] ○ extract_function   → src/urisys/utils/wheel_url.py
      WHY: 3 occurrences of 9-line block across 3 files — saves 18 lines
      FILES: src/urisys/uriguard_install.py, src/urisys/uriresolver_install.py, src/urisys/urisys_install.py
  [4] ○ extract_function   → src/urisys/markpact/analyzer/rules/utils/check.py
      WHY: 2 occurrences of 15-line block across 1 files — saves 15 lines
      FILES: src/urisys/markpact/analyzer/rules/capabilities.py
  [5] ○ extract_function   → src/urisys/utils/_pkg_version.py
      WHY: 3 occurrences of 7-line block across 3 files — saves 14 lines
      FILES: src/urisys/doctor.py, src/urisys/uricore_install.py, src/urisys/uriguard_install.py
  [6] ○ extract_function   → scripts/report/utils/write_run_analysis.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: scripts/report/run_analysis.py, scripts/report/session_io.py
  [7] ○ extract_function   → scripts/utils/manifest_path.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: scripts/check_contract_drift.py, scripts/check_flow_uri_patterns.py

QUICK_WINS[7] (low risk, high savings — do first):
  [1] extract_function   saved=30L  → src/urisys/utils/pip_spec.py
      FILES: uricore_install.py, uriguard_install.py, uriresolver_install.py
  [2] extract_function   saved=22L  → src/urisys/utils/pip_run.py
      FILES: node_install.py, uricore_install.py, uriguard_install.py
  [3] extract_function   saved=18L  → src/urisys/utils/wheel_url.py
      FILES: uriguard_install.py, uriresolver_install.py, urisys_install.py
  [4] extract_function   saved=15L  → src/urisys/markpact/analyzer/rules/utils/check.py
      FILES: capabilities.py
  [5] extract_function   saved=14L  → src/urisys/utils/_pkg_version.py
      FILES: doctor.py, uricore_install.py, uriguard_install.py
  [6] extract_function   saved=8L  → scripts/report/utils/write_run_analysis.py
      FILES: run_analysis.py, session_io.py
  [7] extract_function   saved=6L  → scripts/utils/manifest_path.py
      FILES: check_contract_drift.py, check_flow_uri_patterns.py

EFFORT_ESTIMATE (total ≈ 3.8h):
  medium pip_spec                            saved=30L  ~60min
  medium pip_run                             saved=22L  ~44min
  medium wheel_url                           saved=18L  ~36min
  medium check                               saved=15L  ~30min
  easy   _pkg_version                        saved=14L  ~28min
  easy   write_run_analysis                  saved=8L  ~16min
  easy   manifest_path                       saved=6L  ~12min

METRICS-TARGET:
  dup_groups:  7 → 0
  saved_lines: 113 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 343 func | 69f | 2026-06-19
# generated in 0.00s

NEXT[4] (ranked by impact):
  [1] !  SPLIT-FUNC      run_doctor  CC=15  fan=17
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 255

  [2] !  SPLIT-FUNC      cmd_update  CC=17  fan=11
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 187

  [3] !! SPLIT           planfile.yaml
      WHY: 1319L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0

  [4] !! SPLIT           goal.yaml
      WHY: 527L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.2 → ≤2.9
  max-CC:      17 → ≤8
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
