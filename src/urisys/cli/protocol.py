from __future__ import annotations

import argparse
from typing import Protocol


class CliCommand(Protocol):
    """CLI subcommand handler: ``(args) -> exit code``."""

    def __call__(self, args: argparse.Namespace) -> int: ...
