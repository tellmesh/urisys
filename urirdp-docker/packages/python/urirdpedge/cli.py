from __future__ import annotations

import argparse
import json
import os

from .env import load_urisys_env
from .runtime import Runtime, load_json, run_flow, serve


def build_runtime(args) -> Runtime:
    config = load_json(getattr(args, "config", None))
    rt = Runtime(events_path=getattr(args, "events", "data/events.jsonl"), config=config)
    packs = set(filter(None, (getattr(args, "packs", "rdp,kvm,him,ocr,llm") or "").split(",")))
    if "rdp" in packs:
        import urirdp
        urirdp.register(rt)
    if "him" in packs:
        import urirdp_him
        urirdp_him.register(rt)
    if "ocr" in packs:
        import urirdp_ocr
        urirdp_ocr.register(rt)
    if "llm" in packs:
        import urirdp_llm
        urirdp_llm.register(rt)
    if "kvm" in packs:
        import urirdp_kvm
        urirdp_kvm.register(rt)
    return rt


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="urisys-rdp")
    p.add_argument("--packs", default="rdp,kvm,him,ocr,llm")
    p.add_argument("--config", default=os.environ.get("URISYS_CONFIG", "config/rdp-kvm-profile.json"))
    p.add_argument("--events", default="data/events.jsonl")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("call")
    c.add_argument("uri")
    c.add_argument("--payload", default="{}")
    c.add_argument("--approve", action="store_true")
    c.add_argument("--dry-run", action="store_true")
    c.add_argument("--allow-real", action="store_true")
    c.add_argument("--display", default=None)

    s = sub.add_parser("serve")
    s.add_argument("--host", default="0.0.0.0")
    s.add_argument("--port", type=int, default=8795)

    f = sub.add_parser("flow")
    f.add_argument("path")
    f.add_argument("--approve", action="store_true")
    f.add_argument("--dry-run", action="store_true")
    f.add_argument("--allow-real", action="store_true")
    f.add_argument("--display", default=None)

    args = p.parse_args(argv)
    load_urisys_env()
    rt = build_runtime(args)

    if args.cmd == "serve":
        serve(rt, args.host, args.port)
        return 0

    context = {
        "approved": getattr(args, "approve", False),
        "dry_run": getattr(args, "dry_run", False),
        "allow_real": getattr(args, "allow_real", False),
    }
    if getattr(args, "display", None):
        context["display"] = args.display

    if args.cmd == "call":
        res = rt.call(args.uri, json.loads(args.payload), context)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("ok") else 1

    if args.cmd == "flow":
        res = run_flow(rt, args.path, context)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if all(r.get("ok") for r in res) else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
