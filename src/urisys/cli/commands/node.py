from __future__ import annotations

import os
import sys

from ..helpers import print_json


def cmd_node_host_trust(args) -> int:
    from ...node_host_trust import run_host_trust

    pull = bool(args.pull) and not bool(getattr(args, "no_pull", False))
    report = run_host_trust(
        venv=args.venv,
        node_id=args.node_id,
        port=args.port,
        host=args.host,
        pull=pull,
        dry_run=args.dry_run,
        prefer_script=not args.python_only,
    )
    print_json(report)
    if report.get("stdout"):
        print(report["stdout"], file=sys.stderr, end="")
    if report.get("stderr"):
        print(report["stderr"], file=sys.stderr, end="")
    return 0 if report.get("ok") else 1


def _prepare_node_serve(*, auto_install: bool) -> int | None:
    """Install urisys-node + uriscreen/urishell before boot. Returns exit code on failure."""
    if not auto_install:
        return None
    from urisys.node_install import CORE_NODE_PACK_SPECS, _node_version_ok, ensure_core_node_packs, install_urisys_node, is_importable

    if not is_importable() or not _node_version_ok():
        result = install_urisys_node()
        if not result.get("ok"):
            print(
                "error: urisys-node is missing or too old and auto-install failed",
                file=sys.stderr,
            )
            print(f"hint: pip install -U {result.get('pip_hint') or result.get('spec')}", file=sys.stderr)
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
    if args.node_command == "host-trust":
        return cmd_node_host_trust(args)
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
