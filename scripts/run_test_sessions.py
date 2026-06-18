#!/usr/bin/env python3
"""Run urisys Docker/RDP test sessions — thin CLI over :mod:`urisys_lab.sessions`."""

from urisys_lab.sessions.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
