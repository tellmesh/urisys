"""Register browser:// routes including shorthand URIs used by automation-lab flows."""

from __future__ import annotations

from typing import Any


def register(runtime: Any) -> None:
    import uribrowserdocker

    uribrowserdocker.register(runtime)

    # Lab flow aliases (see urisys-automation-lab/flows/*.uri.flow.yaml)
    aliases = [
        (
            "browser://{session}/page/open",
            "python://urirdp_browser.handlers:open_page",
            "command",
            "browser.page.open",
            True,
        ),
        (
            "browser://{session}/page/active/dom",
            "python://urirdp_browser.handlers:get_dom",
            "query",
            "browser.page.dom",
            False,
        ),
        (
            "browser://{session}/page/active/screenshot",
            "python://urirdp_browser.handlers:screenshot",
            "command",
            "browser.page.screenshot",
            True,
        ),
    ]
    for pattern, handler, kind, operation, side_effects in aliases:
        runtime.register(
            pattern,
            handler,
            kind=kind,
            operation=operation,
            approval="required" if side_effects else "not_required",
            side_effects=side_effects,
        )
