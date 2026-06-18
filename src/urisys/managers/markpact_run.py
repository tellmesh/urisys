"""Unpack a Markpact into ``.markpact/`` and run it — facade over :mod:`urisys.markpact.run`."""

from __future__ import annotations

from ..markpact.run import DEFAULT_OUT, read_run_config, run_markpact
from ..markpact.run.config import load_run_config as _load_run_config
from ..markpact.run.runtime_build import apply_resolver_config as _apply_resolver_config
from ..markpact.run.runtime_build import build_runtime as _build_runtime

# Backward-compatible private aliases for tests and internal callers.
_apply_resolver_config = _apply_resolver_config
_load_run_config = _load_run_config
_build_runtime = _build_runtime

__all__ = ["DEFAULT_OUT", "read_run_config", "run_markpact"]
