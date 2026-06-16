from __future__ import annotations

import argparse
import json
from pathlib import Path

from uri_control import CapabilityRegistry

from .controllers.flow_controller import FlowController
from .controllers.server_controller import ServerController
from .controllers.uri_controller import UriController
from .managers.event_manager import EventManager
from .managers.markpact_manager import MarkpactManager, MarkpactError


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
    parser.add_argument("--environment", default="mock")


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

    p = sub.add_parser("serve", help="Run HTTP URI server.")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8789)

    p = sub.add_parser("markpact", help="Validate, compile and test one-file UriPack Markpacts.")
    msub = p.add_subparsers(dest="markpact_command", required=True)

    p_validate = msub.add_parser("validate", help="Validate a Markpact file.")
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


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "markpact":
            manager = MarkpactManager(cache_root=args.out) if getattr(args, "out", None) else MarkpactManager()
            if args.markpact_command == "validate":
                print_json(manager.validate(args.path))
                return 0
            if args.markpact_command == "compile":
                compiled = manager.compile(args.path, out_dir=args.out, force=args.force)
                print_json({"ok": True, "compiled": compiled.to_dict()})
                return 0
            if args.markpact_command == "routes":
                compiled = manager.compile(args.path, out_dir=args.out)
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
                print_json(manager.run_tests(args.path, events_path=args.events))
                return 0

        if args.command == "serve":
            ServerController(host=args.host, port=args.port, packs=args.packs, markpacts=args.markpact, events_path=args.events).serve_forever()
            return 0

        if args.command == "flow":
            ctrl = FlowController(packs=args.packs, markpacts=args.markpact, events_path=args.events)
            try:
                print_json(ctrl.run(args.path, approved=args.approve, dry_run=args.dry_run, allow_real=args.allow_real, environment=args.environment))
            finally:
                ctrl.close()
            return 0

        if args.command == "events":
            print_json({"ok": True, "events": EventManager(args.events).list_events()})
            return 0

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
    except MarkpactError as exc:
        print_json({"ok": False, "error": str(exc), "type": "markpact_error"})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
