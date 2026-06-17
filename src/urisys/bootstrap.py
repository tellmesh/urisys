"""urisys CLI entry point.

``urisys doctor`` runs without ``uricore`` so broken installs (e.g. Python 3.14
``~/.local`` without dependencies) get actionable diagnostics instead of a traceback.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _missing_uricore_payload(exc: ModuleNotFoundError) -> dict:
    return {
        "ok": False,
        "error": str(exc),
        "type": "module_not_found",
        "missing": exc.name,
        "hint": (
            "uri_control is in tellmesh uricore (GitHub wheel). "
            "PyPI package 'uricore' is a different project — run: urisys init"
        ),
        "commands": {
            "fix": "urisys init",
            "diagnose": "urisys doctor",
            "desktop_slave": "urisys node serve --host 0.0.0.0 --port 8790",
            "dev_server": "urisys serve --port 8789",
        },
    }


def _doctor_main(argv: list[str]) -> int:
    from urisys.doctor import run_doctor

    parser = argparse.ArgumentParser(prog="urisys doctor")
    parser.add_argument(
        "--min-version",
        default=os.environ.get("URISYS_MIN_VERSION", "0.1.25"),
        help="Minimum urisys version (default: 0.1.25).",
    )
    args = parser.parse_args(argv)
    report = run_doctor(min_version=args.min_version or None)
    _print_json(report)
    return 0 if report.get("ok") else 1


def _init_main(argv: list[str]) -> int:
    from urisys.init_setup import DEFAULT_ENV_FILE, run_init

    parser = argparse.ArgumentParser(
        prog="urisys init",
        description="Install uricore/urisysedge/urisys[real], run doctor, write slave env file.",
    )
    parser.add_argument(
        "--profile",
        choices=("slave", "dev"),
        default=os.environ.get("URISYS_INIT_PROFILE", "slave"),
        help="slave: desktop node env (URISYS_ALLOW_REAL, auto-install packs).",
    )
    parser.add_argument(
        "--min-version",
        default=os.environ.get("URISYS_MIN_VERSION", "0.1.25"),
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned steps without pip/write.")
    parser.add_argument("--skip-pip", action="store_true", help="Skip pip install (doctor + env only).")
    parser.add_argument("--no-write-env", action="store_true", help="Do not write ~/.config/urisys/node.env")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Shell env file path.")
    args = parser.parse_args(argv)
    report = run_init(
        profile=args.profile,
        min_version=args.min_version or None,
        install=not args.skip_pip,
        dry_run=args.dry_run,
        write_env=not args.no_write_env,
        env_file=Path(args.env_file),
    )
    _print_json(report)
    if report.get("ok") and report.get("shell_env") and not args.dry_run:
        print(report["shell_env"], file=sys.stderr)
    return 0 if report.get("ok") else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "doctor":
        return _doctor_main(argv[1:])

    if argv and argv[0] == "init":
        return _init_main(argv[1:])

    try:
        from urisys.cli import main as cli_main
    except ModuleNotFoundError as exc:
        if exc.name in ("uri_control", "uricore"):
            _print_json(_missing_uricore_payload(exc))
            return 2
        raise

    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
