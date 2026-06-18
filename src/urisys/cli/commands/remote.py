from __future__ import annotations

import sys


def cmd_remote(args) -> int:
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

    remote_argv = list(args.remote_argv or [])
    if remote_argv[:1] == ["--"]:
        remote_argv = remote_argv[1:]
    if not remote_argv:
        try:
            return remote_main(["--help"])
        except SystemExit as exc:
            return int(exc.code or 0)
    return remote_main(remote_argv)
