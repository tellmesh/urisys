# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/tellmesh/urisys
- **Primary Language**: python
- **Languages**: python: 130, shell: 57, yaml: 40, json: 14, toml: 13
- **Analysis Mode**: static
- **Total Functions**: 639
- **Total Classes**: 34
- **Modules**: 279
- **Entry Points**: 317

## Architecture by Module

### uristepper-docker.packages.python.uristepper.drivers
- **Functions**: 30
- **Classes**: 3
- **File**: `drivers.py`

### urikvm-docker.packages.python.urillm.handlers
- **Functions**: 26
- **File**: `handlers.py`

### urirdp-docker.packages.python.urirdp_llm.handlers
- **Functions**: 22
- **File**: `handlers.py`

### src.urisys.managers.markpact_manager
- **Functions**: 19
- **Classes**: 1
- **File**: `markpact_manager.py`

### urisys-automation-lab.web.app
- **Functions**: 19
- **File**: `app.js`

### urienv-docker.packages.python.urienv.src.urienv.handlers
- **Functions**: 19
- **File**: `handlers.py`

### scripts.test_sessions.util
- **Functions**: 17
- **File**: `util.py`

### packages.python.urisysedge.runtime
- **Functions**: 16
- **Classes**: 3
- **File**: `runtime.py`

### urisys-node.packages.python.urisysnode.pack_resolver
- **Functions**: 16
- **File**: `pack_resolver.py`

### urisys-node.packages.python.urisysnode.artifact_resolver
- **Functions**: 15
- **Classes**: 1
- **File**: `artifact_resolver.py`

### urikvm-docker.packages.python.urihim.handlers
- **Functions**: 14
- **File**: `handlers.py`

### src.urisys.managers.pack_manager
- **Functions**: 13
- **Classes**: 1
- **File**: `pack_manager.py`

### urisys-node.packages.python.uriscreen.backends
- **Functions**: 12
- **File**: `backends.py`

### urisys-node.packages.python.urisysnode.identity
- **Functions**: 12
- **File**: `identity.py`

### src.urisys.managers.source_manager
- **Functions**: 11
- **Classes**: 2
- **File**: `source_manager.py`

### uristepper-docker.packages.python.uristepper.handlers
- **Functions**: 11
- **File**: `handlers.py`

### scripts.run_test_sessions
- **Functions**: 11
- **File**: `run_test_sessions.py`

### urikvm-docker.packages.python.uriocr.handlers
- **Functions**: 10
- **File**: `handlers.py`

### uristepper-docker.packages.python.uristepperedge.runtime
- **Functions**: 9
- **Classes**: 4
- **File**: `runtime.py`

### scripts.report.lab_checks
- **Functions**: 9
- **File**: `lab_checks.py`

## Key Entry Points

Main execution flows into the system:

### urisys-node.packages.python.urisysnode.cli.main
- **Calls**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_subparsers, sub.add_parser, s.add_argument, s.add_argument, sub.add_parser

### scripts.run_test_sessions.session_urirdp_real_docker
- **Calls**: scripts.report.util.now_iso, scripts.test_sessions.util.write_meta, scripts.test_sessions.util.prepare_urirdp_data, scripts.test_sessions.util.sleep_ports, scripts.test_sessions.util.run_cmd, scripts.test_sessions.util.run_cmd, scripts.test_sessions.util.finalize_session, scripts.test_sessions.util.compose_cmd

### urienv-docker.packages.python.urisysedge.src.urisysedge.cli.main
- **Calls**: argparse.ArgumentParser, parser.add_subparsers, sub.add_parser, p_call.add_argument, p_call.add_argument, p_call.add_argument, p_call.add_argument, p_call.add_argument

### src.urisys.cli.main
- **Calls**: None.parse_args, UriController, src.urisys.cli.build_parser, SourceManager, src.urisys.cli.resolve_markpact_source, None.serve_forever, FlowController, src.urisys.cli.print_json

### src.urisys.managers.markpact_manager.MarkpactManager.compile
- **Calls**: Path, self.read_blocks, self.load_pack_block, self.source_hash, self._package_id, _safe_identifier, self.validate, cache_dir.mkdir

### src.urisys.managers.markpact_manager.MarkpactManager.run_tests
- **Calls**: self.compile, UriController, yaml.safe_load, isinstance, ctrl.close, all, compiled.to_dict, compiled.tests_path.exists

### urisys-automation-lab.server.automation_lab_server.LabHandler.do_POST
- **Calls**: self._json, self._read_json, req.get, context.setdefault, self.runtime.call, self._json, self._read_json, self.runtime.call

### urirdp-docker.packages.python.urirdpedge.cli.main
- **Calls**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_subparsers, sub.add_parser, c.add_argument, c.add_argument

### urirdp-docker.packages.python.urirdp_kvm.handlers.click_text
- **Calls**: str, None.get, runtime.call, runtime.call, runtime.call, runtime.call, bool, payload.get

### urienv-docker.packages.python.urisysedge.src.urisysedge.server.serve
- **Calls**: uristepper-docker.packages.python.uristepperedge.runtime.build_runtime, urienv-docker.packages.python.urisysedge.src.urisysedge.runtime.load_device_config, urienv-docker.packages.python.urisysedge.src.urisysedge.runtime.load_env_config, ThreadingHTTPServer, scripts.run-nl-log-smoke.print, httpd.serve_forever, None.encode, self.send_response

### urikvm-docker.packages.python.urikvmedge.cli.main
- **Calls**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_subparsers, sub.add_parser, c.add_argument, c.add_argument

### urirdp-docker.packages.python.urirdp_browser.handlers.open_page
- **Calls**: urirdp-docker.packages.python.urirdp_browser.handlers._profile, payload.get, urirdp-docker.packages.python.urirdp_browser.handlers._session_state, urirdp-docker.packages.python.urirdp_browser.handlers._chromium_binary, urirdp-docker.packages.python.urirdp.handlers._dismiss_stale_targets, payload.get, os.environ.copy, context.get

### scripts.test_sessions.lab_flows.session_lab_10_flows
> Run all 10 automation-lab flows; capture one RDP screenshot per flow.
- **Calls**: scripts.report.util.now_iso, scripts.test_sessions.util.write_meta, scripts.test_sessions.util.sleep_ports, scripts.test_sessions.util.run_cmd, scripts.test_sessions.util.run_cmd, scripts.test_sessions.util.finalize_session, steps.append, scripts.test_sessions.util.finalize_session

### urikvm-docker.packages.python.urillm.handlers.text_plan
- **Calls**: None.strip, payload.get, urikvm-docker.packages.python.urillm.handlers._llm_cfg, urikvm-docker.packages.python.urillm.handlers._driver, urikvm-docker.packages.python.urillm.handlers._match_office_transcript, isinstance, urikvm-docker.packages.python.urillm.handlers._real_allowed, urikvm-docker.packages.python.urillm.handlers._env

### uribrowser-docker.packages.python.uribrowseredge.cli.main
- **Calls**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_subparsers, sub.add_parser, c.add_argument, c.add_argument

### scripts.run_test_sessions.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, run_dir.mkdir, scripts.run-urisys-node-docker-e2e.save_json

### uristepper-docker.packages.python.uristepperedge.cli.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_subparsers, sub.add_parser, p.add_argument, p.add_argument, p.add_argument

### urirdp-docker.packages.python.urirdp_llm.handlers.analyze
- **Calls**: urirdp-docker.packages.python.urirdp_llm.handlers._llm_cfg, cfg.get, urirdp-docker.packages.python.urirdp_llm.handlers._target, urirdp-docker.packages.python.urirdp_llm.handlers._env, urirdp-docker.packages.python.urirdp_llm.handlers._env, float, int, urirdp-docker.packages.python.urirdp_llm.handlers._screenshot_b64

### scripts.run_test_sessions.session_urirdp_mock_docker
- **Calls**: scripts.report.util.now_iso, scripts.test_sessions.util.write_meta, scripts.test_sessions.util.prepare_urirdp_data, scripts.test_sessions.util.sleep_ports, scripts.test_sessions.util.run_cmd, scripts.test_sessions.util.run_cmd, scripts.test_sessions.util.finalize_session, scripts.test_sessions.util.compose_cmd

### src.urisys.managers.source_manager.SourceManager.fetch
- **Calls**: source.strip, spec.startswith, spec.startswith, spec.startswith, _GITHUB_SHORT.match, spec.startswith, spec.startswith, None.expanduser

### urirdp-docker.packages.python.urirdp_llm.handlers.plan
- **Calls**: None.strip, payload.get, urirdp-docker.packages.python.urirdp_llm.handlers._llm_cfg, cfg.get, urirdp-docker.packages.python.urirdp_llm.handlers._match_transcript, isinstance, urirdp-docker.packages.python.urirdp_kvm.display.allow_real, urirdp-docker.packages.python.urirdp_llm.handlers._env

### src.urisys.managers.source_manager.SourceManager._fetch_git
- **Calls**: body.split, urlsplit, parse_qs, urlunsplit, self._cache_dir, cache_dir.mkdir, checkout_dir.exists, checkout_dir.mkdir

### uribrowser-docker.packages.python.uribrowserdocker.handlers.open_page
- **Calls**: uribrowser-docker.packages.python.uribrowserdocker.handlers._profile, payload.get, uribrowser-docker.packages.python.uribrowserdocker.handlers._session_state, context.get, sess.update, payload.get, profile.get, ValueError

### urisys-automation-lab.packages.python.urichat.handlers.uri_execute
- **Calls**: str, dict, bool, bool, urisys-automation-lab.packages.python.urichat.handlers._forward_uri, None.get, cfg.get, context.get

### urikvm-docker.packages.python.urihim.handlers.mouse_scroll
- **Calls**: int, payload.get, payload.get, urikvm-docker.packages.python.urihim.handlers._driver, urikvm-docker.packages.python.urihim.handlers._state, payload.get, context.get, urikvm-docker.packages.python.urihim.handlers._pyautogui

### urikvm-docker.packages.python.urikvm.handlers.click_text
- **Calls**: None.get, payload.get, runtime.call, runtime.call, runtime.call, payload.get, payload.get, ValueError

### urikvm-docker.scripts.real_pipeline.main
- **Calls**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_argument, p.add_argument, p.parse_args, urikvm-docker.scripts.real_pipeline.build_runtime

### urikvm-docker.packages.python.urihim.handlers.mouse_click
- **Calls**: payload.get, payload.get, payload.get, int, urikvm-docker.packages.python.urihim.handlers._driver, urikvm-docker.packages.python.urihim.handlers._state, payload.get, context.get

### src.urisys.managers.markpact_manager.MarkpactManager.validate
- **Calls**: Path, self.read_blocks, self._yaml_blocks, self._yaml_blocks, self._yaml_blocks, self._yaml_blocks, self.source_hash, MarkpactError

### src.urisys.managers.markpact_manager.MarkpactManager._build_route
> Compile one capability entry into a manifest route, registering its
generated python handler in ``handlers`` when the source is a markpact://
or pytho
- **Calls**: str, _scheme_from_uri, None.replace, str, item.get, MarkpactError, MarkpactError, MarkpactError

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [urisys-node.packages.python.urisysnode.cli]
```

### Flow 2: session_urirdp_real_docker
```
session_urirdp_real_docker [scripts.run_test_sessions]
  └─ →> now_iso
  └─ →> write_meta
      └─> read_meta
      └─> save_json
  └─ →> prepare_urirdp_data
```

### Flow 3: compile
```
compile [src.urisys.managers.markpact_manager.MarkpactManager]
```

### Flow 4: run_tests
```
run_tests [src.urisys.managers.markpact_manager.MarkpactManager]
```

### Flow 5: do_POST
```
do_POST [urisys-automation-lab.server.automation_lab_server.LabHandler]
```

### Flow 6: click_text
```
click_text [urirdp-docker.packages.python.urirdp_kvm.handlers]
```

### Flow 7: serve
```
serve [urienv-docker.packages.python.urisysedge.src.urisysedge.server]
  └─ →> build_runtime
      └─> load_json
  └─ →> load_device_config
  └─ →> load_env_config
```

### Flow 8: open_page
```
open_page [urirdp-docker.packages.python.urirdp_browser.handlers]
  └─> _profile
  └─> _session_state
  └─ →> _dismiss_stale_targets
      └─ →> run_cmd
      └─ →> run_cmd
```

### Flow 9: session_lab_10_flows
```
session_lab_10_flows [scripts.test_sessions.lab_flows]
  └─ →> now_iso
  └─ →> write_meta
      └─> read_meta
      └─> save_json
  └─ →> sleep_ports
```

### Flow 10: text_plan
```
text_plan [urikvm-docker.packages.python.urillm.handlers]
  └─> _llm_cfg
  └─> _driver
      └─> _llm_cfg
```

## Key Classes

### src.urisys.managers.markpact_manager.MarkpactManager
> Parses and compiles one-file UriPack Markpacts.

Markpact is an authoring/distribution format. Runti
- **Methods**: 19
- **Key Methods**: src.urisys.managers.markpact_manager.MarkpactManager.__init__, src.urisys.managers.markpact_manager.MarkpactManager.read_blocks, src.urisys.managers.markpact_manager.MarkpactManager.source_hash, src.urisys.managers.markpact_manager.MarkpactManager.load_pack_block, src.urisys.managers.markpact_manager.MarkpactManager.validate, src.urisys.managers.markpact_manager.MarkpactManager._validate_pack, src.urisys.managers.markpact_manager.MarkpactManager._yaml_blocks, src.urisys.managers.markpact_manager.MarkpactManager.compile, src.urisys.managers.markpact_manager.MarkpactManager.manifest_path_for, src.urisys.managers.markpact_manager.MarkpactManager.run_tests

### src.urisys.managers.pack_manager.PackManager
> Loads separate uri* packages, plain manifest.yaml files and UriPack Markpacts.
- **Methods**: 13
- **Key Methods**: src.urisys.managers.pack_manager.PackManager.__init__, src.urisys.managers.pack_manager.PackManager._is_all, src.urisys.managers.pack_manager.PackManager.parse_packs, src.urisys.managers.pack_manager.PackManager.parse_markpacts, src.urisys.managers.pack_manager.PackManager.resolve_package_name, src.urisys.managers.pack_manager.PackManager._is_markpact_path, src.urisys.managers.pack_manager.PackManager._is_manifest_path, src.urisys.managers.pack_manager.PackManager.manifest_paths, src.urisys.managers.pack_manager.PackManager.create_registry, src.urisys.managers.pack_manager.PackManager.capabilities

### uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver
- **Methods**: 13
- **Key Methods**: uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver.__init__, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver._load, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver._save, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver._key, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver._axis, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver._update, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver.status, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver.enable, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver.disable, uristepper-docker.packages.python.uristepper.drivers.MockStepperDriver.stop
- **Inherits**: StepperDriver

### src.urisys.managers.source_manager.SourceManager
> Resolve Markpact sources from local paths, HTTP(S), GitHub, git repos and ZIP archives.
- **Methods**: 11
- **Key Methods**: src.urisys.managers.source_manager.SourceManager.__init__, src.urisys.managers.source_manager.SourceManager.is_remote_source, src.urisys.managers.source_manager.SourceManager.resolve, src.urisys.managers.source_manager.SourceManager.fetch, src.urisys.managers.source_manager.SourceManager._result, src.urisys.managers.source_manager.SourceManager._cache_dir, src.urisys.managers.source_manager.SourceManager._fetch_http, src.urisys.managers.source_manager.SourceManager._fetch_github_uri, src.urisys.managers.source_manager.SourceManager._fetch_github_raw, src.urisys.managers.source_manager.SourceManager._fetch_git

### uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver
- **Methods**: 9
- **Key Methods**: uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver.__init__, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver._pins, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver._enable_value, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver.status, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver.enable, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver.disable, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver.stop, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver.move_relative, uristepper-docker.packages.python.uristepper.drivers.RpiGpioStepDirDriver.home
- **Inherits**: StepperDriver

### uristepper-docker.packages.python.uristepper.drivers.StepperDriver
- **Methods**: 7
- **Key Methods**: uristepper-docker.packages.python.uristepper.drivers.StepperDriver.status, uristepper-docker.packages.python.uristepper.drivers.StepperDriver.enable, uristepper-docker.packages.python.uristepper.drivers.StepperDriver.disable, uristepper-docker.packages.python.uristepper.drivers.StepperDriver.stop, uristepper-docker.packages.python.uristepper.drivers.StepperDriver.move_relative, uristepper-docker.packages.python.uristepper.drivers.StepperDriver.move_absolute, uristepper-docker.packages.python.uristepper.drivers.StepperDriver.home

### urisys-automation-lab.server.automation_lab_server.LabHandler
- **Methods**: 6
- **Key Methods**: urisys-automation-lab.server.automation_lab_server.LabHandler.log_message, urisys-automation-lab.server.automation_lab_server.LabHandler._json, urisys-automation-lab.server.automation_lab_server.LabHandler._read_json, urisys-automation-lab.server.automation_lab_server.LabHandler.do_OPTIONS, urisys-automation-lab.server.automation_lab_server.LabHandler.do_GET, urisys-automation-lab.server.automation_lab_server.LabHandler.do_POST
- **Inherits**: BaseHTTPRequestHandler

### packages.python.urisysedge.runtime.Runtime
- **Methods**: 5
- **Key Methods**: packages.python.urisysedge.runtime.Runtime.__init__, packages.python.urisysedge.runtime.Runtime.register, packages.python.urisysedge.runtime.Runtime.resolve, packages.python.urisysedge.runtime.Runtime._load_handler, packages.python.urisysedge.runtime.Runtime.call

### src.urisys.controllers.uri_controller.UriController
- **Methods**: 5
- **Key Methods**: src.urisys.controllers.uri_controller.UriController.__init__, src.urisys.controllers.uri_controller.UriController.call, src.urisys.controllers.uri_controller.UriController.explain, src.urisys.controllers.uri_controller.UriController.routes, src.urisys.controllers.uri_controller.UriController.close

### src.urisys.managers.runtime_manager.RuntimeManager
- **Methods**: 5
- **Key Methods**: src.urisys.managers.runtime_manager.RuntimeManager.__init__, src.urisys.managers.runtime_manager.RuntimeManager.create_runtime, src.urisys.managers.runtime_manager.RuntimeManager.close, src.urisys.managers.runtime_manager.RuntimeManager.__enter__, src.urisys.managers.runtime_manager.RuntimeManager.__exit__

### uristepper-docker.packages.python.uristepperedge.runtime.StepperRuntime
- **Methods**: 5
- **Key Methods**: uristepper-docker.packages.python.uristepperedge.runtime.StepperRuntime.__init__, uristepper-docker.packages.python.uristepperedge.runtime.StepperRuntime.explain, uristepper-docker.packages.python.uristepperedge.runtime.StepperRuntime.list_routes, uristepper-docker.packages.python.uristepperedge.runtime.StepperRuntime.call, uristepper-docker.packages.python.uristepperedge.runtime.StepperRuntime._match

### packages.python.urisysedge.runtime.JsonlEventStore
- **Methods**: 3
- **Key Methods**: packages.python.urisysedge.runtime.JsonlEventStore.__init__, packages.python.urisysedge.runtime.JsonlEventStore.append, packages.python.urisysedge.runtime.JsonlEventStore.tail

### src.urisys.controllers.flow_controller.FlowController
- **Methods**: 3
- **Key Methods**: src.urisys.controllers.flow_controller.FlowController.__init__, src.urisys.controllers.flow_controller.FlowController.run, src.urisys.controllers.flow_controller.FlowController.close

### src.urisys.managers.route_manager.RouteManager
- **Methods**: 3
- **Key Methods**: src.urisys.managers.route_manager.RouteManager.__init__, src.urisys.managers.route_manager.RouteManager.explain, src.urisys.managers.route_manager.RouteManager.list_routes

### packages.python.urisysedge.runtime.Route
- **Methods**: 2
- **Key Methods**: packages.python.urisysedge.runtime.Route.compile, packages.python.urisysedge.runtime.Route.match

### src.urisys.controllers.server_controller.ServerController
- **Methods**: 2
- **Key Methods**: src.urisys.controllers.server_controller.ServerController.__init__, src.urisys.controllers.server_controller.ServerController.serve_forever

### src.urisys.managers.event_manager.EventManager
- **Methods**: 2
- **Key Methods**: src.urisys.managers.event_manager.EventManager.__init__, src.urisys.managers.event_manager.EventManager.list_events

### uristepper-docker.packages.python.uristepperedge.runtime.Route
- **Methods**: 2
- **Key Methods**: uristepper-docker.packages.python.uristepperedge.runtime.Route.compile, uristepper-docker.packages.python.uristepperedge.runtime.Route.match

### scripts.report.models.SessionReport
- **Methods**: 2
- **Key Methods**: scripts.report.models.SessionReport.passed, scripts.report.models.SessionReport.failed

### scripts.report.models.FlowOutcome
- **Methods**: 2
- **Key Methods**: scripts.report.models.FlowOutcome.no_visible_effect, scripts.report.models.FlowOutcome.vision_decided

## Data Transformation Functions

Key functions that process and transform data:

### src.urisys.cli.build_parser
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_subparsers

### src.urisys.managers.markpact_validation.validate_contract
- **Output to**: None.strip, str, None.strip, isinstance, MarkpactError

### src.urisys.managers.markpact_validation.validate_bundle
- **Output to**: None.strip, str, isinstance, isinstance, MarkpactError

### src.urisys.managers.markpact_validation.validate_implementation
- **Output to**: None.strip, str, isinstance, isinstance, MarkpactError

### src.urisys.managers.markpact_models.parse_meta
- **Output to**: shlex.split, raw.strip, raw.strip, token.split, None.strip

### src.urisys.managers.markpact_manager.MarkpactManager.validate
- **Output to**: Path, self.read_blocks, self._yaml_blocks, self._yaml_blocks, self._yaml_blocks

### src.urisys.managers.markpact_manager.MarkpactManager._validate_pack
- **Output to**: self._package_id, self._capabilities, self._handler_blocks, set, sorted

### src.urisys.managers.pack_manager.PackManager.parse_packs
- **Output to**: isinstance, any, any, list, list

### src.urisys.managers.pack_manager.PackManager.parse_markpacts
- **Output to**: isinstance, None.strip, p.strip, None.strip, markpacts.split

### scripts.test_sessions.lab_rdp.parse_lab_flow
- **Output to**: dict, yaml.safe_load, data.get, isinstance, path.read_text

### scripts.test_sessions.lab_rdp.parse_docker_log_errors
- **Output to**: path.read_text, text.count, text.count, text.splitlines, path.is_file

### urirdp-docker.packages.python.urirdp_ocr.handlers._parse_tesseract_tsv
- **Output to**: csv.DictReader, io.StringIO, None.strip, tokens.append, float

### urirdp-docker.packages.python.urirdp_llm.handlers._parse_json_response
- **Output to**: None.strip, json.loads, re.search, json.loads, match.group

### urirdp-docker.packages.python.urirdp_llm.handlers._decision_from_parsed
- **Output to**: None.lower, bool, str, float, str

### urirdp-docker.packages.python.urirdp_llm.handlers._plan_from_parsed
- **Output to**: None.strip, isinstance, parsed.get, ValueError, str

### scripts.office-simulate-loop.parse_args
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### urikvm-docker.packages.python.urillm.handlers._parse_json_response
- **Output to**: None.strip, json.loads, re.search, json.loads, match.group

### urikvm-docker.packages.python.urillm.handlers._plan_from_parsed
- **Output to**: None.strip, isinstance, parsed.get, ValueError, str

## Behavioral Patterns

### recursion_register
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: urirdp-docker.packages.python.urirdp_ocr.register

### recursion_register
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: urirdp-docker.packages.python.urirdp_shell.register

### state_machine_RuntimeManager
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.urisys.managers.runtime_manager.RuntimeManager.__init__, src.urisys.managers.runtime_manager.RuntimeManager.create_runtime, src.urisys.managers.runtime_manager.RuntimeManager.close, src.urisys.managers.runtime_manager.RuntimeManager.__enter__, src.urisys.managers.runtime_manager.RuntimeManager.__exit__

### state_machine_PackManager
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.urisys.managers.pack_manager.PackManager.__init__, src.urisys.managers.pack_manager.PackManager._is_all, src.urisys.managers.pack_manager.PackManager.parse_packs, src.urisys.managers.pack_manager.PackManager.parse_markpacts, src.urisys.managers.pack_manager.PackManager.resolve_package_name

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `urisys-node.packages.python.urisysnode.cli.main` - 104 calls
- `scripts.run_test_sessions.session_urirdp_real_docker` - 69 calls
- `urienv-docker.packages.python.urisysedge.src.urisysedge.cli.main` - 54 calls
- `src.urisys.cli.main` - 53 calls
- `urisys-node.packages.python.urisysnode.serve.make_handler` - 50 calls
- `src.urisys.cli.build_parser` - 47 calls
- `src.urisys.managers.markpact_manager.MarkpactManager.compile` - 46 calls
- `uristepper-docker.packages.python.uristepperedge.server.make_handler` - 43 calls
- `scripts.run_test_sessions.session_automation_lab` - 43 calls
- `src.urisys.managers.markpact_manager.MarkpactManager.run_tests` - 42 calls
- `urisys-automation-lab.server.automation_lab_server.LabHandler.do_POST` - 41 calls
- `urirdp-docker.packages.python.urirdpedge.cli.main` - 40 calls
- `urirdp-docker.packages.python.urirdp_kvm.handlers.click_text` - 40 calls
- `urisys-automation-lab.server.flow_runner.run_flow_file` - 40 calls
- `urienv-docker.packages.python.urisysedge.src.urisysedge.server.serve` - 36 calls
- `src.urisys.managers.markpact_validation.validate_contract` - 35 calls
- `urikvm-docker.packages.python.urikvmedge.cli.main` - 34 calls
- `scripts.report.run_analysis.analyze_run` - 33 calls
- `urirdp-docker.packages.python.urirdp_browser.handlers.open_page` - 33 calls
- `scripts.test_sessions.lab_flows.session_lab_10_flows` - 33 calls
- `urikvm-docker.packages.python.urillm.handlers.text_plan` - 33 calls
- `uribrowser-docker.packages.python.uribrowseredge.cli.main` - 32 calls
- `scripts.run_test_sessions.main` - 32 calls
- `src.urisys.http_server.create_server` - 31 calls
- `uristepper-docker.packages.python.uristepperedge.cli.main` - 31 calls
- `urirdp-docker.packages.python.urirdp_llm.handlers.analyze` - 31 calls
- `scripts.run_test_sessions.session_urirdp_mock_docker` - 31 calls
- `src.urisys.managers.source_manager.SourceManager.fetch` - 29 calls
- `urisys-node.packages.python.urisysnode.serve.call_uri` - 29 calls
- `urirdp-docker.packages.python.urirdp_llm.handlers.plan` - 28 calls
- `src.urisys.managers.markpact_validation.validate_implementation` - 27 calls
- `scripts.report.session.generate_report` - 27 calls
- `uribrowser-docker.packages.python.uribrowserdocker.handlers.open_page` - 27 calls
- `urisys-automation-lab.packages.python.urichat.handlers.uri_execute` - 27 calls
- `urikvm-docker.packages.python.urihim.handlers.mouse_scroll` - 27 calls
- `urikvm-docker.packages.python.urikvm.handlers.click_text` - 26 calls
- `urikvm-docker.scripts.real_pipeline.main` - 26 calls
- `scripts.report.session.infer_steps` - 25 calls
- `urikvm-docker.packages.python.urihim.handlers.mouse_click` - 25 calls
- `packages.python.urisysedge.runtime.make_handler` - 24 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> ArgumentParser
    main --> add_argument
    main --> add_subparsers
    main --> add_parser
    session_urirdp_real_ --> now_iso
    session_urirdp_real_ --> write_meta
    session_urirdp_real_ --> prepare_urirdp_data
    session_urirdp_real_ --> sleep_ports
    session_urirdp_real_ --> run_cmd
    main --> parse_args
    main --> UriController
    main --> build_parser
    main --> SourceManager
    main --> resolve_markpact_sou
    compile --> Path
    compile --> read_blocks
    compile --> load_pack_block
    compile --> source_hash
    compile --> _package_id
    run_tests --> compile
    run_tests --> UriController
    run_tests --> safe_load
    run_tests --> isinstance
    run_tests --> close
    do_POST --> _json
    do_POST --> _read_json
    do_POST --> get
    do_POST --> setdefault
    do_POST --> call
    click_text --> str
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.