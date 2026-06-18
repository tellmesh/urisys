from __future__ import annotations

import os
import sys


def _prepare_node_serve(*, auto_install: bool) -> int | None:
    """Install urisys-node + uriscreen/urishell before boot. Returns exit code on failure."""
    if not auto_install:
        return None
    from urisys.node_install import CORE_NODE_PACK_SPECS, ensure_core_node_packs, install_urisys_node, is_importable

    if not is_importable():
        result = install_urisys_node()
        if not result.get("ok"):
            print(
                "error: urisys-node is not installed and auto-install failed",
                file=sys.stderr,
            )
            print(f"hint: pip install -U {result.get('spec')}", file=sys.stderr)
            return 1
    core = ensure_core_node_packs()
    if core.get("ok") or core.get("skipped"):
        return None
    print(f"error: node boot packs missing ({core.get('error')})", file=sys.stderr)
    print(
        "hint: pip install --no-deps "
        + " ".join(core.get("specs") or CORE_NODE_PACK_SPECS),
        file=sys.stderr,
    )
    return 1


def cmd_node(args) -> int:
    if args.node_command == "remote":
        from .remote import cmd_remote

        return cmd_remote(args)
    if args.node_command == "serve":
        auto_install = not args.no_auto_install
        if args.no_auto_install:
            os.environ["URISYS_NODE_AUTO_INSTALL"] = "0"
        else:
            os.environ.setdefault("URISYS_NODE_AUTO_INSTALL", "1")
        os.environ.setdefault("URISYS_NODE_ALLOW_PACK_LOAD", "1")
        prep = _prepare_node_serve(auto_install=auto_install)
        if prep is not None:
            return prep
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
