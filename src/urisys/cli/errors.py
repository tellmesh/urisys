from __future__ import annotations

from .helpers import print_json


def handle_cli_error(exc: Exception) -> int:
    """Map a known CLI exception to a JSON error + exit code; re-raise the rest."""
    from ..managers.markpact_manager import MarkpactError
    from ..managers.source_manager import SourceError

    if isinstance(exc, MarkpactError):
        print_json({"ok": False, "error": str(exc), "type": "markpact_error"})
        return 2
    if isinstance(exc, SourceError):
        print_json({"ok": False, "error": str(exc), "type": "source_error"})
        return 2
    try:
        from uri_control.errors import UriControlError
    except ModuleNotFoundError:
        UriControlError = ()  # type: ignore[misc, assignment]
    if UriControlError and isinstance(exc, UriControlError):
        print_json({"ok": False, "error": str(exc), "type": type(exc).__name__})
        return 2
    if isinstance(exc, ModuleNotFoundError) and exc.name in ("uri_control", "uricore"):
        print_json({
            "ok": False,
            "error": str(exc),
            "type": "module_not_found",
            "hint": 'pip install -U urirouter uricore "urisys[real]" — then run: urisys doctor',
        })
        return 2
    raise exc
