from __future__ import annotations

import sys

from ..helpers import json_arg, print_json


def cmd_uri(args) -> int:
    from ...controllers.uri_controller import UriController

    ctrl = UriController(packs=args.packs, markpacts=args.markpact, events_path=args.events)
    try:
        if args.command == "call":
            print_json(ctrl.call(args.uri, json_arg(args.payload), approved=args.approve, dry_run=args.dry_run, allow_real=args.allow_real, environment=args.environment))
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


def cmd_serve(args) -> int:
    from ...controllers.server_controller import ServerController
    from ...defaults import NODE_SERVE_CMD

    print(f"hint: desktop slave (lenovo) → {NODE_SERVE_CMD}", file=sys.stderr)
    ServerController(host=args.host, port=args.port, packs=args.packs, markpacts=args.markpact, events_path=args.events).serve_forever()
    return 0


def cmd_flow(args) -> int:
    from ...controllers.flow_controller import FlowController

    ctrl = FlowController(packs=args.packs, markpacts=args.markpact, events_path=args.events)
    try:
        print_json(ctrl.run(args.path, approved=args.approve, dry_run=args.dry_run, allow_real=args.allow_real, environment=args.environment))
    finally:
        ctrl.close()
    return 0


def cmd_events(args) -> int:
    from ...managers.event_manager import EventManager

    print_json({"ok": True, "events": EventManager(args.events).list_events()})
    return 0
