from __future__ import annotations

from .commands import COMMAND_HANDLERS
from .errors import handle_cli_error
from .parser import build_parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        handler = COMMAND_HANDLERS.get(args.command)
        if handler is None:
            return 1
        return handler(args)
    except Exception as exc:
        return handle_cli_error(exc)
