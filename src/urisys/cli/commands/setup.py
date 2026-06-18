from __future__ import annotations

import sys
from pathlib import Path

from ..helpers import print_json


def cmd_doctor(args) -> int:
    from ...doctor import run_doctor

    report = run_doctor(min_version=args.min_version or None)
    print_json(report)
    return 0 if report.get("ok") else 1


def cmd_init(args) -> int:
    from ...init_setup import run_init

    report = run_init(
        profile=args.profile,
        min_version=args.min_version or None,
        install=not args.skip_pip,
        dry_run=args.dry_run,
        write_env=not args.no_write_env,
        env_file=Path(args.env_file),
    )
    print_json(report)
    if report.get("ok") and report.get("shell_env") and not args.dry_run:
        print(report["shell_env"], file=sys.stderr)
    return 0 if report.get("ok") else 1
