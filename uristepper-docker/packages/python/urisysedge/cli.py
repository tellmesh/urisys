from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .runtime import build_runtime
from .server import serve


def _json_arg(value: str | None) -> dict:
    if not value:
        return {}
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def cmd_call(args):
    rt = build_runtime(args.device_config, args.events)
    context = _json_arg(args.context)
    if args.approve:
        context["approved"] = True
    if args.dry_run:
        context["dry_run"] = True
    result = rt.call(args.uri, _json_arg(args.payload), context)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def cmd_explain(args):
    rt = build_runtime(args.device_config, args.events)
    print(json.dumps(rt.explain(args.uri), ensure_ascii=False, indent=2))
    return 0


def cmd_routes(args):
    rt = build_runtime(args.device_config, args.events)
    print(json.dumps({"ok": True, "routes": rt.list_routes()}, ensure_ascii=False, indent=2))
    return 0


def cmd_events(args):
    rt = build_runtime(args.device_config, args.events)
    print(json.dumps({"ok": True, "events": rt.event_store.tail(args.limit)}, ensure_ascii=False, indent=2))
    return 0


def cmd_flow(args):
    rt = build_runtime(args.device_config, args.events)
    flow = json.loads(Path(args.file).read_text(encoding="utf-8"))
    defaults = flow.get("defaults", {})
    results = []
    for item in flow.get("do", []):
        if isinstance(item, str):
            uri, payload = item, {}
        elif isinstance(item, dict) and len(item) == 1:
            uri, payload = next(iter(item.items()))
            payload = payload or {}
        else:
            raise SystemExit(f"Invalid flow item: {item!r}")
        context = dict(defaults)
        if args.approve:
            context["approved"] = True
        if args.dry_run:
            context["dry_run"] = True
        result = rt.call(uri, payload, context)
        results.append(result)
        if not result.get("ok") and not args.continue_on_error:
            break
    out = {"ok": all(r.get("ok") for r in results), "flow": flow.get("flow", {}), "results": results}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 1


def cmd_serve(args):
    serve(args.host, args.port, args.device_config, args.events)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="urisys-edge", description="Minimal urisys edge runtime for stepper://")
    parser.add_argument("--device-config", default=None, help="Path to device profile JSON")
    parser.add_argument("--events", default=None, help="Path to events JSONL")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("call")
    p.add_argument("uri")
    p.add_argument("--payload", default="{}")
    p.add_argument("--context", default="{}")
    p.add_argument("--approve", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_call)

    p = sub.add_parser("explain")
    p.add_argument("uri")
    p.set_defaults(func=cmd_explain)

    p = sub.add_parser("routes")
    p.set_defaults(func=cmd_routes)

    p = sub.add_parser("events")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_events)

    p = sub.add_parser("flow")
    p.add_argument("file")
    p.add_argument("--approve", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--continue-on-error", action="store_true")
    p.set_defaults(func=cmd_flow)

    p = sub.add_parser("serve")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8790)
    p.set_defaults(func=cmd_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
