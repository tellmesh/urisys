from __future__ import annotations

import argparse
import json
import os
import sys

from urisysnode.client import call_via_route_map, discover_mdns
from urisysnode.identity import enroll, load_identity, load_pairing
from urisysnode.router import load_route_map, rewrite_uri_for_slave
from urisysnode.runtime import Runtime, load_json
from urisysnode.serve import build_runtime, serve


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="urisys-node", description="urisys slave node — explicit local install")
    p.add_argument("--config", default=os.environ.get("URISYS_NODE_CONFIG", "config/node-profile.json"))
    p.add_argument("--events", default=os.environ.get("URISYS_NODE_EVENTS", "data/events.jsonl"))
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("serve", help="Start HTTP URI server (default :8790)")
    s.add_argument("--host", default=os.environ.get("URISYS_NODE_HOST", "0.0.0.0"))
    s.add_argument("--port", type=int, default=int(os.environ.get("URISYS_NODE_PORT", "8790")))

    e = sub.add_parser("enroll", help="Pair node with controller")
    e.add_argument("--controller", required=True)
    e.add_argument("--code", default=None)
    e.add_argument("--token", default=None)

    sub.add_parser("identity", help="Show node identity")
    sub.add_parser("pairing", help="Show pairing status")

    d = sub.add_parser("discover", help="Discover nodes on LAN (requires zeroconf)")
    d.add_argument("--timeout", type=float, default=2.0)

    nl = sub.add_parser("nodes", help="List known nodes from registry")
    nl.add_argument("--registry", default="config/nodes.registry.json")

    c = sub.add_parser("call", help="Call URI locally or via route map")
    c.add_argument("uri")
    c.add_argument("--payload", default="{}")
    c.add_argument("--approve", action="store_true")
    c.add_argument("--dry-run", action="store_true")
    c.add_argument("--allow-real", action="store_true")
    c.add_argument("--route-map", default=None)
    c.add_argument("--nodes-registry", default="config/nodes.registry.json")

    args = p.parse_args(argv)

    if args.cmd == "serve":
        rt = build_runtime(args.config)
        serve(rt, args.host, args.port)
        return 0

    if args.cmd == "enroll":
        result = enroll(args.controller, code=args.code, token=args.token)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "identity":
        print(json.dumps(load_identity(), indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "pairing":
        print(json.dumps(load_pairing(), indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "discover":
        nodes = discover_mdns(args.timeout)
        print(json.dumps(nodes, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "nodes":
        path = args.registry
        if not os.path.exists(path):
            print(json.dumps({"nodes": {}}, indent=2))
            return 0
        print(open(path, encoding="utf-8").read())
        return 0

    if args.cmd == "call":
        payload = json.loads(args.payload)
        context = {
            "approved": args.approve,
            "dry_run": args.dry_run,
            "allow_real": args.allow_real,
        }
        if args.route_map:
            result = call_via_route_map(
                args.uri,
                route_map_path=args.route_map,
                nodes_registry_path=args.nodes_registry,
                payload=payload,
                context=context,
            )
        else:
            rt = build_runtime(args.config)
            uri = args.uri
            identity = load_identity()
            uri = rewrite_uri_for_slave(uri, node_id=identity["node_id"], target_node="local")
            result = rt.call(uri, payload, context)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
