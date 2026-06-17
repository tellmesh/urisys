from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from .defaults import DEFAULT_ENVIRONMENT
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
    parser.add_argument("--events", default="output/urisys-events.jsonl")
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
        default=os.environ.get("URISYS_MIN_VERSION", "0.1.25"),
        help="Minimum urisys version (default: 0.1.25).",
    )

    p = sub.add_parser(
        "init",
        help="Install uricore/urisysedge/urisys[real], doctor, write slave env (~/.config/urisys/node.env).",
    )
    p.add_argument("--profile", choices=("slave", "dev"), default=os.environ.get("URISYS_INIT_PROFILE", "slave"))
    p.add_argument("--min-version", default=os.environ.get("URISYS_MIN_VERSION", "0.1.25"))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-pip", action="store_true")
    p.add_argument("--no-write-env", action="store_true")
    p.add_argument("--env-file", default=str(Path.home() / ".config" / "urisys" / "node.env"))

    p = sub.add_parser("serve", help="Run HTTP URI server (dev packs; for desktop slave use: urisys node serve).")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8789)

    node = sub.add_parser("node", help="urisys-node slave runtime (bundled; lazy pack install via URI).")
    node_sub = node.add_subparsers(dest="node_command", required=True)
    ns = node_sub.add_parser("serve", help="Start node HTTP server (:8790); extra packs install on first URI use.")
    ns.add_argument("--host", default=os.environ.get("URISYS_NODE_HOST", "0.0.0.0"))
    ns.add_argument("--port", type=int, default=int(os.environ.get("URISYS_NODE_PORT", "8790")))
    ns.add_argument("--config", default=os.environ.get("URISYS_NODE_CONFIG", "config/node-profile.json"))
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
    return 1


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
                "hint: desktop slave (lenovo) → urisys node serve --host 0.0.0.0 --port 8790",
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
