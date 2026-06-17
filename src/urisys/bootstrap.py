"""urisys CLI entry point.

``urisys doctor`` runs without ``uricore`` so broken installs (e.g. Python 3.14
``~/.local`` without dependencies) get actionable diagnostics instead of a traceback.
"""

from __future__ import annotations

import argparse
import json
import os
import sys


def _print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _missing_uricore_payload(exc: ModuleNotFoundError) -> dict:
    return {
        "ok": False,
        "error": str(exc),
        "type": "module_not_found",
        "missing": exc.name,
        "hint": (
            "uri_control is provided by PyPI package uricore (not a separate pip name). "
            'Install: python3.12 -m venv ~/venv && source ~/venv/bin/activate && '
            'pip install -U uricore urisysedge "urisys[real]" — then run: urisys doctor'
        ),
        "commands": {
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


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "doctor":
        return _doctor_main(argv[1:])

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
