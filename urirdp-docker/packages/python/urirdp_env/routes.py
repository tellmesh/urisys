"""Register env:// capability routes from urienv manifest."""

from __future__ import annotations

from typing import Any


def register(runtime: Any) -> None:
    routes = [
        ("env://runtime/query/health", "python://urienv.handlers:health", "query", "health", False),
        ("env://runtime/query/list", "python://urienv.handlers:list_vars", "query", "list_vars", False),
        ("env://runtime/config/query/startup", "python://urienv.handlers:startup_config", "query", "startup_config", False),
        ("env://runtime/var/{name}/query/exists", "python://urienv.handlers:var_exists", "query", "var_exists", False),
        ("env://runtime/var/{name}/query/value", "python://urienv.handlers:var_value", "query", "var_value", False),
        ("env://runtime/secret/{name}/query/masked", "python://urienv.handlers:secret_masked", "query", "secret_masked", False),
        (
            "env://runtime/secret/{name}/query/value",
            "python://urienv.handlers:secret_value",
            "query",
            "secret_value",
            True,
        ),
        ("env://runtime/var/{name}/command/set", "python://urienv.handlers:var_set", "command", "var_set", True),
        ("env://runtime/var/{name}/command/unset", "python://urienv.handlers:var_unset", "command", "var_unset", True),
    ]
    for pattern, handler, kind, operation, side_effects in routes:
        approval = "required" if side_effects else "not_required"
        runtime.register(
            pattern,
            handler,
            kind=kind,
            operation=operation,
            approval=approval,
            side_effects=side_effects,
        )
