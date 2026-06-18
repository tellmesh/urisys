from __future__ import annotations

import os
import sys


def cmd_node(args) -> int:
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
