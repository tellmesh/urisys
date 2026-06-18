# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/tellmesh/urisys
- **Primary Language**: python
- **Languages**: python: 111, shell: 49, md: 30, yaml: 7, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 610
- **Total Classes**: 42
- **Modules**: 202
- **Entry Points**: 0

## Architecture by Module

### src.urisys_lab.lenovo.cli
- **Functions**: 40
- **File**: `cli.py`

### src.urisys_lab.core
- **Functions**: 23
- **File**: `core.py`

### src.urisys_lab.sessions.runners
- **Functions**: 22
- **File**: `runners.py`

### src.urisys.managers.markpact_profile
- **Functions**: 20
- **Classes**: 1
- **File**: `markpact_profile.py`

### src.urisys.managers.pack_manager
- **Functions**: 19
- **Classes**: 1
- **File**: `pack_manager.py`

### scripts.pack_sync
- **Functions**: 19
- **File**: `pack_sync.py`

### src.urisys.init_setup
- **Functions**: 16
- **File**: `init_setup.py`

### scripts.generate_pack_markpacts
- **Functions**: 16
- **File**: `generate_pack_markpacts.py`

### src.urisys.cli.commands.markpact
- **Functions**: 15
- **File**: `markpact.py`

### src.urisys_lab.sessions.util
- **Functions**: 14
- **File**: `util.py`

### scripts.test_sessions.util
- **Functions**: 14
- **File**: `util.py`

### src.urisys.managers.markpact_pack_deps
- **Functions**: 13
- **File**: `markpact_pack_deps.py`

### src.urisys.managers.contract_gen
- **Functions**: 13
- **File**: `contract_gen.py`

### src.urisys.managers.markpact_pack_gen
- **Functions**: 12
- **File**: `markpact_pack_gen.py`

### src.urisys.managers.source_manager
- **Functions**: 12
- **Classes**: 2
- **File**: `source_manager.py`

### src.urisys.uricore_install
- **Functions**: 11
- **File**: `uricore_install.py`

### src.urisys.doctor
- **Functions**: 11
- **Classes**: 1
- **File**: `doctor.py`

### src.urisys.managers.markpact_manager
- **Functions**: 11
- **Classes**: 1
- **File**: `markpact_manager.py`

### scripts.report.lab_checks
- **Functions**: 10
- **File**: `lab_checks.py`

### src.urisys.node_install
- **Functions**: 9
- **File**: `node_install.py`

## Key Entry Points

Main execution flows into the system:

## Process Flows

Key execution flows identified:

## Key Classes

### src.urisys.managers.pack_manager.PackManager
> Loads separate uri* packages, plain manifest.yaml files and UriPack Markpacts.
- **Methods**: 16
- **Key Methods**: src.urisys.managers.pack_manager.PackManager.__init__, src.urisys.managers.pack_manager.PackManager._split_specs, src.urisys.managers.pack_manager.PackManager._is_all, src.urisys.managers.pack_manager.PackManager.parse_packs, src.urisys.managers.pack_manager.PackManager.parse_markpacts, src.urisys.managers.pack_manager.PackManager.resolve_package_name, src.urisys.managers.pack_manager.PackManager._is_markpact_path, src.urisys.managers.pack_manager.PackManager._is_manifest_path, src.urisys.managers.pack_manager.PackManager._resolve_importable_manifest, src.urisys.managers.pack_manager.PackManager._handle_missing_manifest

### src.urisys.managers.source_manager.SourceManager
> Resolve Markpact sources from local paths, HTTP(S), GitHub, git repos and ZIP archives.
- **Methods**: 12
- **Key Methods**: src.urisys.managers.source_manager.SourceManager.__init__, src.urisys.managers.source_manager.SourceManager.is_remote_source, src.urisys.managers.source_manager.SourceManager.resolve, src.urisys.managers.source_manager.SourceManager.fetch, src.urisys.managers.source_manager.SourceManager._result, src.urisys.managers.source_manager.SourceManager._cache_dir, src.urisys.managers.source_manager.SourceManager._http_download, src.urisys.managers.source_manager.SourceManager._fetch_http, src.urisys.managers.source_manager.SourceManager._fetch_github_uri, src.urisys.managers.source_manager.SourceManager._fetch_github_raw

### src.urisys.managers.markpact_manager.MarkpactManager
> Facade over :mod:`urisys.markpact` compile/analyze pipeline.

Markpact is an authoring/distribution 
- **Methods**: 11
- **Key Methods**: src.urisys.managers.markpact_manager.MarkpactManager.__init__, src.urisys.managers.markpact_manager.MarkpactManager.read_blocks, src.urisys.managers.markpact_manager.MarkpactManager.source_hash, src.urisys.managers.markpact_manager.MarkpactManager.load_pack_block, src.urisys.managers.markpact_manager.MarkpactManager.validate, src.urisys.managers.markpact_manager.MarkpactManager.compile, src.urisys.managers.markpact_manager.MarkpactManager.analyze, src.urisys.managers.markpact_manager.MarkpactManager.manifest_path_for, src.urisys.managers.markpact_manager.MarkpactManager.run_tests, src.urisys.managers.markpact_manager.MarkpactManager._build_route

### src.urisys.controllers.uri_controller.UriController
- **Methods**: 5
- **Key Methods**: src.urisys.controllers.uri_controller.UriController.__init__, src.urisys.controllers.uri_controller.UriController.call, src.urisys.controllers.uri_controller.UriController.explain, src.urisys.controllers.uri_controller.UriController.routes, src.urisys.controllers.uri_controller.UriController.close

### src.urisys.managers.runtime_manager.RuntimeManager
- **Methods**: 5
- **Key Methods**: src.urisys.managers.runtime_manager.RuntimeManager.__init__, src.urisys.managers.runtime_manager.RuntimeManager.create_runtime, src.urisys.managers.runtime_manager.RuntimeManager.close, src.urisys.managers.runtime_manager.RuntimeManager.__enter__, src.urisys.managers.runtime_manager.RuntimeManager.__exit__

### src.urisys.controllers.flow_controller.FlowController
- **Methods**: 3
- **Key Methods**: src.urisys.controllers.flow_controller.FlowController.__init__, src.urisys.controllers.flow_controller.FlowController.run, src.urisys.controllers.flow_controller.FlowController.close

### src.urisys.managers.route_manager.RouteManager
- **Methods**: 3
- **Key Methods**: src.urisys.managers.route_manager.RouteManager.__init__, src.urisys.managers.route_manager.RouteManager.explain, src.urisys.managers.route_manager.RouteManager.list_routes

### src.urisys.http_server._ControllerRuntime
> Adapt UriController to the duck-typed runtime the shared transport calls.

The transport invokes ``c
- **Methods**: 2
- **Key Methods**: src.urisys.http_server._ControllerRuntime.__init__, src.urisys.http_server._ControllerRuntime.call

### src.urisys.markpact.compiler.MarkpactCompiler
> Compile one-file Markpacts into cached runtime artifacts.
- **Methods**: 2
- **Key Methods**: src.urisys.markpact.compiler.MarkpactCompiler.__init__, src.urisys.markpact.compiler.MarkpactCompiler.compile

### src.urisys.controllers.server_controller.ServerController
- **Methods**: 2
- **Key Methods**: src.urisys.controllers.server_controller.ServerController.__init__, src.urisys.controllers.server_controller.ServerController.serve_forever

### src.urisys.managers.event_manager.EventManager
- **Methods**: 2
- **Key Methods**: src.urisys.managers.event_manager.EventManager.__init__, src.urisys.managers.event_manager.EventManager.list_events

### scripts.report.models.SessionReport
- **Methods**: 2
- **Key Methods**: scripts.report.models.SessionReport.passed, scripts.report.models.SessionReport.failed

### scripts.report.models.FlowOutcome
- **Methods**: 2
- **Key Methods**: scripts.report.models.FlowOutcome.no_visible_effect, scripts.report.models.FlowOutcome.vision_decided

### src.urisys.markpact.run.modes.base.MarkpactRunMode
- **Methods**: 1
- **Key Methods**: src.urisys.markpact.run.modes.base.MarkpactRunMode.run
- **Inherits**: Protocol

### src.urisys.markpact.run.modes.adapter.AdapterMode
- **Methods**: 1
- **Key Methods**: src.urisys.markpact.run.modes.adapter.AdapterMode.run

### src.urisys.markpact.run.modes.flow.FlowMode
- **Methods**: 1
- **Key Methods**: src.urisys.markpact.run.modes.flow.FlowMode.run

### src.urisys.markpact.run.modes.pack.PackMode
- **Methods**: 1
- **Key Methods**: src.urisys.markpact.run.modes.pack.PackMode.run

### src.urisys.markpact.run.modes.interface.InterfaceMode
- **Methods**: 1
- **Key Methods**: src.urisys.markpact.run.modes.interface.InterfaceMode.run

### src.urisys.markpact.run.modes.service.ServiceMode
- **Methods**: 1
- **Key Methods**: src.urisys.markpact.run.modes.service.ServiceMode.run

### src.urisys.markpact.analyzer.rules.base.MarkpactRule
- **Methods**: 1
- **Key Methods**: src.urisys.markpact.analyzer.rules.base.MarkpactRule.check
- **Inherits**: Protocol

## Data Transformation Functions

Key functions that process and transform data:

### src.urisys.doctor._parse_version
- **Output to**: None.split, tuple, None.strip, ch.isdigit, parts.append

### src.urisys.cli.parser.build_parser
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_subparsers

### src.urisys.cli.commands.markpact.cmd_validate
- **Output to**: src.urisys.cli.helpers.print_json, manager.validate

### src.urisys.markpact.validate_pack.validate_pack
- **Output to**: src.urisys.markpact.pack.package_id, src.urisys.markpact.pack.capabilities, src.urisys.markpact.blocks.handler_blocks, set, sorted

### src.urisys.markpact.validate_pack.validate_markpact_file
- **Output to**: Path, src.urisys.markpact.blocks.read_blocks, src.urisys.markpact.blocks.yaml_blocks, src.urisys.markpact.blocks.yaml_blocks, src.urisys.markpact.blocks.yaml_blocks

### src.urisys.markpact.manifest._validate_scheme
- **Output to**: src.urisys.managers.markpact_models.scheme_from_uri, MarkpactError

### src.urisys.managers.markpact_validation._validate_contract_routes
> Validate every query/command entry and return them; scheme must match.
- **Output to**: data.get, isinstance, MarkpactError, None.strip, None.strip

### src.urisys.managers.markpact_validation.validate_contract
- **Output to**: None.strip, str, None.strip, src.urisys.managers.markpact_validation._validate_contract_routes, isinstance

### src.urisys.managers.markpact_validation.validate_bundle
- **Output to**: None.strip, str, src.urisys.managers.markpact_validation._missing_bundle_imports, isinstance, MarkpactError

### src.urisys.managers.markpact_validation._validate_implementation_capabilities
> Validate each capability entry; warn on ones missing a handler reference.
- **Output to**: isinstance, MarkpactError, None.strip, warnings.append, str

### src.urisys.managers.markpact_validation.validate_implementation
- **Output to**: None.strip, str, isinstance, src.urisys.managers.markpact_validation._validate_implementation_capabilities, isinstance

### src.urisys.managers.markpact_models.parse_meta
- **Output to**: shlex.split, raw.strip, raw.strip, token.split, None.strip

### src.urisys.managers.markpact_manager.MarkpactManager.validate
- **Output to**: src.urisys.markpact.validate_pack.validate_markpact_file

### src.urisys.managers.pack_manager.PackManager.parse_packs
- **Output to**: PackManager._split_specs, list, list

### src.urisys.managers.pack_manager.PackManager.parse_markpacts
- **Output to**: PackManager._split_specs

### src.urisys.managers.markpact_profile._validate_scheme_requirements
- **Output to**: src.urisys.managers.markpact_profile.declared_schemes, src.urisys.managers.markpact_profile.declared_packs, warnings.append, isinstance, None.get

### src.urisys.managers.markpact_profile._validate_undeclared_schemes
- **Output to**: errors.append

### src.urisys.managers.markpact_profile._validate_capability_operations
- **Output to**: None.strip, src.urisys.managers.markpact_profile._issue, issues.append, warnings.append, str

### src.urisys.managers.markpact_profile._validate_uri_kind
- **Output to**: issues.append, errors.append, issues.append, errors.append, src.urisys.managers.markpact_profile._issue

### src.urisys.managers.markpact_profile._validate_command_approval
- **Output to**: cap.get, issues.append, errors.append, str, src.urisys.managers.markpact_profile._issue

### src.urisys.managers.markpact_profile._validate_process_handler
- **Output to**: str, issues.append, errors.append, cap.get, handler.startswith

### src.urisys.managers.markpact_profile._validate_capability_uris
- **Output to**: src.urisys.managers.markpact_profile._cap_uri, None.strip, None.strip, src.urisys.managers.markpact_profile._validate_command_approval, src.urisys.managers.markpact_profile._validate_process_handler

### src.urisys.managers.platform_export.collect_process_uris
> Extract URIs, authorities and schemes from embedded process flows.
- **Output to**: Path, src.urisys.markpact.blocks.read_blocks, src.urisys.markpact.pack.load_pack_block, src.urisys.managers.markpact_flows.extract_flows, set

### scripts.test_sessions.lab_rdp.parse_lab_flow
- **Output to**: dict, yaml.safe_load, data.get, isinstance, path.read_text

### scripts.test_sessions.lab_rdp.parse_docker_log_errors
- **Output to**: path.read_text, text.count, text.count, text.splitlines, path.is_file

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `src.urisys.cli.parser.build_parser` - 108 calls
- `src.urisys_lab.lenovo.cli.main` - 64 calls
- `src.urisys.managers.platform_export.export_platform_artifacts` - 35 calls
- `src.urisys.managers.markpact_pack_gen.generate_pack_markpact` - 33 calls
- `scripts.test_sessions.lab_flows.session_lab_10_flows` - 33 calls
- `src.urisys_lab.lenovo.cli.run_flow` - 33 calls
- `scripts.report.run_analysis.analyze_run` - 33 calls
- `src.urisys_lab.sessions.cli.main` - 32 calls
- `src.urisys_lab.sessions.runners.session_urirdp_mock_docker` - 31 calls
- `src.urisys_lab.sessions.runners.session_automation_lab` - 31 calls
- `src.urisys.managers.source_manager.SourceManager.fetch` - 29 calls
- `src.urisys.markpact.tests.run_markpact_tests` - 27 calls
- `src.urisys.markpact.compiler.MarkpactCompiler.compile` - 27 calls
- `scripts.report.session.generate_report` - 27 calls
- `src.urisys.managers.markpact_run_flow.run_markpact_flow` - 26 calls
- `src.urisys.markpact.validate_pack.validate_markpact_file` - 24 calls
- `src.urisys_lab.sessions.runners.session_urirdp_real_docker` - 24 calls
- `scripts.report.cli.main` - 23 calls
- `src.urisys.doctor.run_doctor` - 22 calls
- `src.urisys.managers.markpact_validation.validate_implementation` - 22 calls
- `src.urisys.managers.markpact_materialize.materialize_markpact` - 22 calls
- `src.urisys.markpact.validate_pack.validate_pack` - 21 calls
- `src.urisys.managers.markpact_validation.validate_contract` - 21 calls
- `scripts.pack_sync.init_repo` - 21 calls
- `scripts.pack_sync.main` - 21 calls
- `src.urisys.managers.platform_export.collect_process_uris` - 20 calls
- `scripts.pack_registry.pack_specs` - 20 calls
- `src.urisys.controllers.flow_controller.FlowController.run` - 19 calls
- `src.urisys.managers.contract_gen.manifest_to_contract` - 19 calls
- `src.urisys_lab.sessions.runners.session_urirdp_rdp_e2e` - 19 calls
- `src.urisys_lab.lenovo.cli.write_session_md` - 19 calls
- `scripts.pack_sync.check_drift` - 19 calls
- `src.urisys.markpact.analyzer.report.analyze_markpact` - 18 calls
- `scripts.test_sessions.lab_rdp.parse_lab_flow` - 18 calls
- `src.urisys_lab.sessions.util.http_json` - 18 calls
- `scripts.office-simulate-loop.llm_tick` - 18 calls
- `scripts.test_sessions.util.http_json` - 18 calls
- `src.urisys.managers.markpact_profile.declared_schemes` - 17 calls
- `src.urisys.cli.commands.markpact.cmd_markpact` - 16 calls
- `src.urisys.markpact.run.run_markpact` - 16 calls

## System Interactions

How components interact:

```mermaid
graph TD
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.