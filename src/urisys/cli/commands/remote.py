from __future__ import annotations

import argparse
import json
import sys
import urllib.error

from ..helpers import print_json


def _parse_remote_host_trust(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="urisys remote host-trust")
    p.add_argument("--endpoint", default=None)
    p.add_argument("--venv", default="~/venv")
    p.add_argument("--node-id", default="lenovo")
    p.add_argument("--port", type=int, default=8790)
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--repo", default="~/github/tellmesh/urisys-node")
    p.add_argument("--pull", dest="pull", action="store_true", default=None, help="git pull urisys-node repo first (default).")
    p.add_argument("--no-pull", dest="pull", action="store_false", help="Skip git pull.")
    args = p.parse_args(argv)
    if args.pull is None:
        args.pull = True
    return args


def cmd_remote_host_trust(argv: list[str]) -> int:
    from ...node_host_trust import remote_host_trust_command

    try:
        from urisysnode.remote import call_uri, default_endpoint
    except ImportError as exc:
        print(f"error: urisys-node required: {exc}", file=sys.stderr)
        return 1

    args = _parse_remote_host_trust(argv)
    pull = bool(args.pull)
    cmd = remote_host_trust_command(
        venv=args.venv,
        node_id=args.node_id,
        port=args.port,
        host=args.host,
        pull=pull,
        repo=args.repo,
    )
    try:
        out = call_uri(
            "shell://bash",
            payload={"args": ["-lc", cmd]},
            endpoint=args.endpoint or default_endpoint(),
        )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            out = json.loads(body)
        except json.JSONDecodeError:
            print_json({"ok": False, "error": str(exc), "body": body})
            return 1
    print_json(out)
    result = out.get("result") or {}
    if result.get("stdout"):
        print(result["stdout"], file=sys.stderr, end="")
    if result.get("stderr"):
        print(result["stderr"], file=sys.stderr, end="")
    return 0 if out.get("ok") and result.get("ok", True) else 1


def cmd_remote(args) -> int:
    remote_argv = list(args.remote_argv or [])
    if remote_argv[:1] == ["--"]:
        remote_argv = remote_argv[1:]
    if remote_argv[:1] == ["host-trust"]:
        return cmd_remote_host_trust(remote_argv[1:])

    try:
        from urisysnode.remote import main as remote_main
    except ImportError as exc:
        print(
            "error: urisys-node is required for `urisys remote`",
            file=sys.stderr,
        )
        print(
            "hint: pip install -U urisys-node  "
            "(or: urisys init --profile dev)",
            file=sys.stderr,
        )
        print(f"detail: {exc}", file=sys.stderr)
        return 1

    if not remote_argv:
        try:
            return remote_main(["--help"])
        except SystemExit as exc:
            return int(exc.code or 0)
    try:
        return remote_main(remote_argv)
    except SystemExit as exc:
        return int(exc.code or 0)
