from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from .defaults import (
    DEFAULT_ENVIRONMENT,
    DEFAULT_EVENTS_PATH,
    DEFAULT_MIN_VERSION,
    MIN_VERSION_ENV,
    NODE_SERVE_CMD,
)
from .doctor import run_doctor

if TYPE_CHECKING:
    from .managers.source_manager import SourceManager


def _json_arg(value: str | None) -> dict:
    if not value:
        return {}
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _add_runtime_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-real", action="store_true")
    parser.add_argument("--environment", default=DEFAULT_ENVIRONMENT)


def resolve_markpact_source(source: str, *, source_manager: SourceManager | None = None) -> str:
    if source_manager is None:
        from .managers.source_manager import SourceManager

        source_manager = SourceManager()
    return str(source_manager.resolve(source))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="urisys", description="URI control system: managers/controllers over uri* packs and UriPack Markpacts.")
    parser.add_argument("--packs", default="all", help="Comma-separated pack aliases/packages, plain manifest paths, Markpact paths or all/none.")
    parser.add_argument("--markpact", action="append", default=[], help="Load one UriPack Markpact. Can be used multiple times.")
    parser.add_argument("--events", default=DEFAULT_EVENTS_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("call", help="Execute a URI through urisys.")
    p.add_argument("uri")
    p.add_argument("--payload", default="{}", help="JSON payload or @file.json")
    _add_runtime_flags(p)

    p = sub.add_parser("explain", help="Explain how a URI routes.")
    p.add_argument("uri")

    sub.add_parser("routes", help="List loaded routes.")
    sub.add_parser("events", help="List event log.")

    p = sub.add_parser("flow", help="Run a compact URI flow YAML.")
    p.add_argument("path")
    _add_runtime_flags(p)

    p = sub.add_parser("doctor", help="Check installation, Python env, and dependencies.")
    p.add_argument(
        "--min-version",
        default=os.environ.get(MIN_VERSION_ENV, DEFAULT_MIN_VERSION),
        help=f"Minimum urisys version (default: {DEFAULT_MIN_VERSION}).",
    )

    p = sub.add_parser(
        "init",
        help="Install uricore/urisysedge/urisys[real], doctor, write slave env (~/.config/urisys/node.env).",
    )
    p.add_argument("--profile", choices=("slave", "dev"), default=os.environ.get("URISYS_INIT_PROFILE", "slave"))
    p.add_argument("--min-version", default=os.environ.get(MIN_VERSION_ENV, DEFAULT_MIN_VERSION))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-pip", action="store_true")
    p.add_argument("--no-write-env", action="store_true")
    p.add_argument("--env-file", default=str(Path.home() / ".config" / "urisys" / "node.env"))

    p = sub.add_parser("serve", help="Run HTTP URI server (dev packs; for desktop slave use: urisys node serve).")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8789)

    node = sub.add_parser("node", help="urisys-node slave runtime (bundled; lazy pack install via URI).")
    node_sub = node.add_subparsers(dest="node_command", required=True)
    ns = node_sub.add_parser(
        "serve",
        help="Start node HTTP server (:8790); kills any prior listener on the port (atomic restart).",
    )
    ns.add_argument("--host", default=os.environ.get("URISYS_NODE_HOST", "0.0.0.0"))
    ns.add_argument("--port", type=int, default=int(os.environ.get("URISYS_NODE_PORT", "8790")))
    ns.add_argument("--config", default=os.environ.get("URISYS_NODE_CONFIG", "config/node-profile.json"))
    ns.add_argument(
        "--no-takeover",
        action="store_true",
        help="Do not kill an existing listener on --port.",
    )
    ns.add_argument(
        "--no-auto-install",
        action="store_true",
        help="Disable URISYS_NODE_AUTO_INSTALL (no pip on first kvm/him/… URI).",
    )

    p = sub.add_parser("markpact", help="Validate, compile, fetch and test one-file UriPack Markpacts.")
    msub = p.add_subparsers(dest="markpact_command", required=True)

    p_fetch = msub.add_parser("fetch", help="Fetch a Markpact from file/HTTP/GitHub/git/ZIP and cache it locally.")
    p_fetch.add_argument("source")
    p_fetch.add_argument("--force", action="store_true")

    p_validate = msub.add_parser("validate", help="Validate a Markpact file or remote source.")
    p_validate.add_argument("path")

    p_compile = msub.add_parser("compile", help="Compile Markpact to cached runtime manifest and handlers.")
    p_compile.add_argument("path")
    p_compile.add_argument("--out", default=None, help="Optional output/cache directory.")
    p_compile.add_argument("--force", action="store_true")

    p_routes = msub.add_parser("routes", help="Compile Markpact and list generated routes.")
    p_routes.add_argument("path")
    p_routes.add_argument("--out", default=None)

    p_test = msub.add_parser("test", help="Run tests embedded in Markpact.")
    p_test.add_argument("path")
    p_test.add_argument("--out", default=None, help="Optional compile/cache directory.")

    p_gen = msub.add_parser("gen-contract", help="Generate a UriContract Markpact from a runtime manifest.yaml.")
    p_gen.add_argument("manifest", help="Path to a pack manifest.yaml.")
    p_gen.add_argument("--out", default=None, help="Write contract to this file (default: print to stdout).")
    p_gen.add_argument("--force", action="store_true", help="Overwrite --out if it already exists.")

    p_drift = msub.add_parser("check-drift", help="Compare a manifest.yaml against an existing UriContract Markpact.")
    p_drift.add_argument("manifest", help="Path to a pack manifest.yaml.")
    p_drift.add_argument("contract", help="Path/source of the UriContract Markpact.")

    p_analyze = msub.add_parser("analyze", help="Summarise a showcase Markpact: definitions, embedded flows (use_case/integration), protos.")
    p_analyze.add_argument("path")

    p_run_flow = msub.add_parser(
        "run-flow",
        help="Compile Markpact, build urisysedge runtime (manifest + uses: packs) and run an embedded flow.",
    )
    p_run_flow.add_argument(
        "path",
        help="Markpact path or markpact://… with optional #flow.id fragment (e.g. showcase.md#open-and-read).",
    )
    p_run_flow.add_argument("--out", default=None, help="Optional compile/cache directory.")
    p_run_flow.add_argument("--force", action="store_true", help="Force recompile before run.")
    p_run_flow.add_argument(
        "--extra-packs",
        default="",
        help="Additional pack aliases to register (comma-separated) beyond flow dependencies.",
    )
    p_run_flow.add_argument(
        "--auto-install",
        action="store_true",
        help="pip install missing flow packs via urisys-node pack_resolver (when available).",
    )
    _add_runtime_flags(p_run_flow)

    p_mat = msub.add_parser(
        "materialize",
        help="Compile Markpact and unpack to .markpact/{package_id}/ (manifest, handlers, flows, proto).",
    )
    p_mat.add_argument("path", help="Markpact path (optional #flow.id ignored).")
    p_mat.add_argument("--root", default=".markpact", help="Output root directory (default: .markpact).")
    p_mat.add_argument("--force", action="store_true")

    p_run = msub.add_parser(
        "run",
        help="Unpack to .markpact/ and run (pack|service|flow|interface|adapter per markpact:run or --as).",
    )
    p_run.add_argument("path", help="Markpact path (optional #flow.id for flow mode).")
    p_run.add_argument("--as", dest="run_mode", default=None, help="Override mode: pack|service|flow|interface|adapter.")
    p_run.add_argument("--out", default=".markpact", help="Unpack root (default: .markpact).")
    p_run.add_argument("--host", default="0.0.0.0")
    p_run.add_argument("--port", type=int, default=None)
    p_run.add_argument("--config", default=None, help="Optional runtime config YAML.")
    p_run.add_argument("--force", action="store_true", help="Force recompile/unpack.")
    p_run.add_argument(
        "--auto-install",
        action="store_true",
        help="pip install missing flow packs via urisys-node pack_resolver (flow mode).",
    )
    _add_runtime_flags(p_run)

    p_pack = msub.add_parser(
        "pack",
        help="Generate a complete self-contained Markpact (definitions + full source + run config) for a uri* package.",
    )
    p_pack.add_argument("package", help="Package name or path (dir holding <pkg>/manifest.yaml).")
    p_pack.add_argument("--out", default=None, help="Write here (default: <pkg>/<pkg>.markpact.md).")
    p_pack.add_argument("--scheme", default=None, help="For multi-scheme packages, which scheme to emit (one pack file per scheme).")
    p_pack.add_argument("--port", type=int, default=8790, help="Default service port written into markpact:run.")
    p_pack.add_argument("--force", action="store_true", help="Overwrite an existing output file.")
    p_pack.add_argument("--stdout", action="store_true", help="Print to stdout instead of writing a file.")

    return parser


def _cmd_markpact(args) -> int:
    from uri_control import CapabilityRegistry

    from .managers.markpact_manager import MarkpactManager
    from .managers.source_manager import SourceManager

    source_manager = SourceManager(cache_root=(Path(args.out) / "sources") if getattr(args, "out", None) else ".urisys/cache/sources")
    manager = MarkpactManager(cache_root=args.out) if getattr(args, "out", None) else MarkpactManager()
    if args.markpact_command == "fetch":
        print_json(source_manager.fetch(args.source, force=args.force))
        return 0
    if args.markpact_command in ("gen-contract", "check-drift"):
        return _cmd_contract(args, source_manager)
    if args.markpact_command == "run-flow":
        from .managers.markpact_run_flow import run_markpact_flow, split_flow_ref

        base, flow_id = split_flow_ref(args.path)
        local = resolve_markpact_source(base, source_manager=source_manager)
        result = run_markpact_flow(
            local,
            flow_id=flow_id,
            manager=manager,
            out_dir=args.out,
            force=args.force,
            extra_packs=args.extra_packs or None,
            auto_install=args.auto_install,
            events_path=args.events,
            approved=args.approve,
            dry_run=args.dry_run,
            allow_real=args.allow_real,
            environment=args.environment,
        )
        print_json(result)
        return 0 if result.get("ok") else 1
    if args.markpact_command == "materialize":
        from .managers.markpact_materialize import materialize_markpact
        from .managers.markpact_run_flow import split_flow_ref

        base, _ = split_flow_ref(args.path)
        local = resolve_markpact_source(base, source_manager=source_manager)
        print_json(materialize_markpact(local, root=args.root, manager=manager, force=args.force))
        return 0
    if args.markpact_command == "run":
        from .managers.markpact_run import run_markpact
        from .managers.markpact_run_flow import split_flow_ref

        base, flow_id = split_flow_ref(args.path)
        local = resolve_markpact_source(base, source_manager=source_manager)
        result = run_markpact(
            local,
            mode=args.run_mode,
            flow_id=flow_id,
            out=args.out,
            host=args.host,
            port=args.port,
            config_path=args.config,
            approve=args.approve,
            dry_run=args.dry_run,
            auto_install=args.auto_install,
        )
        print_json(result)
        return 0 if result.get("ok", True) else 1
    if args.markpact_command == "pack":
        return _cmd_pack(args)
    local_path = resolve_markpact_source(args.path, source_manager=source_manager)
    if args.markpact_command == "validate":
        print_json(manager.validate(local_path))
        return 0
    if args.markpact_command == "compile":
        compiled = manager.compile(local_path, out_dir=args.out, force=args.force)
        print_json({"ok": True, "compiled": compiled.to_dict()})
        return 0
    if args.markpact_command == "routes":
        compiled = manager.compile(local_path, out_dir=args.out)
        registry = CapabilityRegistry.from_manifest_files([compiled.manifest_path])
        print_json({
            "ok": True,
            "compiled": compiled.to_dict(),
            "routes": [
                {
                    "manifest_id": r.manifest_id,
                    "scheme": r.scheme,
                    "pattern": r.pattern,
                    "kind": r.kind,
                    "operation": r.operation,
                    "approval": r.approval,
                    "side_effects": r.side_effects,
                    "handler_ref": r.handler_ref,
                }
                for r in registry.routes
            ],
        })
        return 0
    if args.markpact_command == "test":
        print_json(manager.run_tests(local_path, events_path=args.events))
        return 0
    if args.markpact_command == "analyze":
        result = manager.analyze(local_path)
        print_json(result)
        return 0 if result.get("ok") else 1
    return 1


def _cmd_pack(args) -> int:
    from .managers.markpact_pack_gen import find_package_dir, generate_pack_markpact

    rendered = generate_pack_markpact(args.package, port=args.port, scheme=args.scheme)
    if args.stdout:
        print(rendered)
        return 0
    if args.out:
        out = Path(args.out)
    else:
        pkg_dir = find_package_dir(args.package)
        suffix = f".{args.scheme}" if args.scheme else ""
        out = pkg_dir.parent / f"{pkg_dir.name}{suffix}.markpact.md"
    if out.exists() and not args.force:
        print_json({"ok": False, "error": f"{out} exists; use --force to overwrite."})
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print_json({"ok": True, "package": args.package, "markpact": str(out)})
    return 0


def _cmd_contract(args, source_manager: SourceManager) -> int:
    from .managers import contract_gen

    manifest = contract_gen.load_manifest(args.manifest)
    if args.markpact_command == "gen-contract":
        rendered = contract_gen.render_contract_markpact(manifest)
        if args.out:
            out = Path(args.out)
            if out.exists() and not args.force:
                print_json({"ok": False, "error": f"{out} exists; use --force to overwrite."})
                return 2
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(rendered, encoding="utf-8")
            print_json({"ok": True, "manifest": args.manifest, "contract": str(out)})
            return 0
        print(rendered)
        return 0
    # check-drift
    contract_path = resolve_markpact_source(args.contract, source_manager=source_manager)
    contract = contract_gen.load_contract_block(contract_path)
    issues = contract_gen.diff_manifest_contract(manifest, contract)
    print_json({
        "ok": not issues,
        "manifest": args.manifest,
        "contract": contract_path,
        "drift": issues,
    })
    return 0 if not issues else 1


def _cmd_init(args) -> int:
    from .init_setup import run_init

    report = run_init(
        profile=args.profile,
        min_version=args.min_version or None,
        install=not args.skip_pip,
        dry_run=args.dry_run,
        write_env=not args.no_write_env,
        env_file=Path(args.env_file),
    )
    print_json(report)
    if report.get("ok") and report.get("shell_env") and not args.dry_run:
        import sys

        print(report["shell_env"], file=sys.stderr)
    return 0 if report.get("ok") else 1


def _cmd_node(args) -> int:
    if args.node_command == "serve":
        if args.no_auto_install:
            os.environ["URISYS_NODE_AUTO_INSTALL"] = "0"
        else:
            os.environ.setdefault("URISYS_NODE_AUTO_INSTALL", "1")
        os.environ.setdefault("URISYS_NODE_ALLOW_PACK_LOAD", "1")
        from urisysnode.serve import build_runtime, serve as node_serve

        rt = build_runtime(args.config)
        takeover = not args.no_takeover
        try:
            import inspect

            params = inspect.signature(node_serve).parameters
            if "takeover" in params:
                node_serve(rt, args.host, args.port, takeover=takeover)
            else:
                if takeover:
                    print(
                        "warning: urisys-node is too old for port takeover; "
                        "upgrade urisys-node (pip install -U urisys-node) or use --no-takeover",
                        file=sys.stderr,
                    )
                node_serve(rt, args.host, args.port)
        except TypeError:
            node_serve(rt, args.host, args.port)
    return 0


def _cmd_uri(args) -> int:
    from .controllers.uri_controller import UriController

    ctrl = UriController(packs=args.packs, markpacts=args.markpact, events_path=args.events)
    try:
        if args.command == "call":
            print_json(ctrl.call(args.uri, _json_arg(args.payload), approved=args.approve, dry_run=args.dry_run, allow_real=args.allow_real, environment=args.environment))
            return 0
        if args.command == "explain":
            print_json({"ok": True, "explain": ctrl.explain(args.uri)})
            return 0
        if args.command == "routes":
            print_json({"ok": True, "routes": ctrl.routes()})
            return 0
    finally:
        ctrl.close()
    return 1


def _handle_cli_error(exc: Exception) -> int:
    """Map a known CLI exception to a JSON error + exit code; re-raise the rest."""
    from .managers.markpact_manager import MarkpactError
    from .managers.source_manager import SourceError

    if isinstance(exc, MarkpactError):
        print_json({"ok": False, "error": str(exc), "type": "markpact_error"})
        return 2
    if isinstance(exc, SourceError):
        print_json({"ok": False, "error": str(exc), "type": "source_error"})
        return 2
    try:
        from uri_control.errors import UriControlError
    except ModuleNotFoundError:
        UriControlError = ()  # type: ignore[misc, assignment]
    if UriControlError and isinstance(exc, UriControlError):
        print_json({"ok": False, "error": str(exc), "type": type(exc).__name__})
        return 2
    if isinstance(exc, ModuleNotFoundError) and exc.name in ("uri_control", "uricore"):
        print_json({
            "ok": False,
            "error": str(exc),
            "type": "module_not_found",
            "hint": 'pip install -U uricore urisysedge "urisys[real]" — then run: urisys doctor',
        })
        return 2
    raise exc


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "markpact":
            return _cmd_markpact(args)

        if args.command == "doctor":
            report = run_doctor(min_version=args.min_version or None)
            print_json(report)
            return 0 if report.get("ok") else 1

        if args.command == "init":
            return _cmd_init(args)

        if args.command == "serve":
            import sys

            from .controllers.server_controller import ServerController

            print(
                f"hint: desktop slave (lenovo) → {NODE_SERVE_CMD}",
                file=sys.stderr,
            )
            ServerController(host=args.host, port=args.port, packs=args.packs, markpacts=args.markpact, events_path=args.events).serve_forever()
            return 0

        if args.command == "node":
            return _cmd_node(args)

        if args.command == "flow":
            from .controllers.flow_controller import FlowController

            ctrl = FlowController(packs=args.packs, markpacts=args.markpact, events_path=args.events)
            try:
                print_json(ctrl.run(args.path, approved=args.approve, dry_run=args.dry_run, allow_real=args.allow_real, environment=args.environment))
            finally:
                ctrl.close()
            return 0

        if args.command == "events":
            from .managers.event_manager import EventManager

            print_json({"ok": True, "events": EventManager(args.events).list_events()})
            return 0

        return _cmd_uri(args)
    except Exception as exc:
        return _handle_cli_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())
