#!/usr/bin/env python3
"""Lenovo remote session runner — thin CLI over :mod:`urisys_lab.lenovo`."""

from urisys_lab.lenovo.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
