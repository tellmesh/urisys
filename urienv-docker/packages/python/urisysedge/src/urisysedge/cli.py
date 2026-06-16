from __future__ import annotations
import argparse, json
from .flow import run_flow
from .runtime import build_runtime, load_device_config, load_env_config, result_to_dict
from .server import serve

def _packs(value: str) -> list[str]: return [p.strip() for p in value.split(",") if p.strip()]

def main(argv=None):
    parser = argparse.ArgumentParser(prog="urisys-edge"); sub = parser.add_subparsers(dest="cmd", required=True)
    p_call = sub.add_parser("call"); p_call.add_argument("uri"); p_call.add_argument("--packs", default="all"); p_call.add_argument("--payload", default="{}"); p_call.add_argument("--context", default="{}"); p_call.add_argument("--approve", action="store_true"); p_call.add_argument("--dry-run", action="store_true"); p_call.add_argument("--allow-real", action="store_true"); p_call.add_argument("--device-config"); p_call.add_argument("--env-config")
    p_serve = sub.add_parser("serve"); p_serve.add_argument("--packs", default="all"); p_serve.add_argument("--host", default="0.0.0.0"); p_serve.add_argument("--port", type=int, default=8790); p_serve.add_argument("--allow-real", action="store_true"); p_serve.add_argument("--device-config"); p_serve.add_argument("--env-config")
    p_routes = sub.add_parser("routes"); p_routes.add_argument("--packs", default="all")
    p_flow = sub.add_parser("flow"); p_flow.add_argument("path"); p_flow.add_argument("--packs", default="all"); p_flow.add_argument("--approve", action="store_true"); p_flow.add_argument("--dry-run", action="store_true"); p_flow.add_argument("--allow-real", action="store_true"); p_flow.add_argument("--device-config"); p_flow.add_argument("--env-config")
    args = parser.parse_args(argv)
    if args.cmd == "serve": serve(host=args.host, port=args.port, packs=_packs(args.packs), device_config_path=args.device_config, env_config_path=args.env_config, allow_real=args.allow_real); return 0
    runtime = build_runtime(_packs(getattr(args, "packs", "all")))
    if args.cmd == "routes": print(json.dumps([r.__dict__ for r in runtime.registry.routes], indent=2, ensure_ascii=False)); return 0
    if args.cmd == "call":
        context = json.loads(args.context); context.update({"approved": args.approve or context.get("approved", False), "dry_run": args.dry_run or context.get("dry_run", False), "allow_real": args.allow_real or context.get("allow_real", False), "device_config": load_device_config(args.device_config), "env_config": load_env_config(args.env_config)})
        result = runtime.call(args.uri, json.loads(args.payload), context); print(json.dumps(result_to_dict(result), indent=2, ensure_ascii=False)); return 0 if result.ok else 2
    if args.cmd == "flow":
        context = {"approved": args.approve, "dry_run": args.dry_run, "allow_real": args.allow_real, "device_config": load_device_config(args.device_config), "env_config": load_env_config(args.env_config)}
        print(json.dumps(run_flow(args.path, runtime, context=context), indent=2, ensure_ascii=False)); return 0
    return 1
if __name__ == "__main__": raise SystemExit(main())
