from __future__ import annotations

from .helpers import print_json, resolve_markpact_source
from .main import main
from .parser import build_parser

__all__ = ["main", "build_parser", "print_json", "resolve_markpact_source"]

if __name__ == "__main__":
    raise SystemExit(main())
