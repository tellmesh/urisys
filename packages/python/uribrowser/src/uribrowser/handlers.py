from __future__ import annotations

from typing import Any

from .common import fake_png_data_url, mock_result, var

_SESSIONS: dict[str, dict[str, Any]] = {}


def _session(context: dict[str, Any]) -> str:
    return var(context, "session", "default")


def open_page(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    session = _session(context)
    url = str(payload.get("url") or "about:blank")
    title = payload.get("title") or ("Example" if "example" in url else "Mock page")
    html = payload.get("html") or f"<html><head><title>{title}</title></head><body data-uri-session='{session}'>{url}</body></html>"
    _SESSIONS[session] = {"session": session, "url": url, "title": title, "html": html}
    return mock_result("browser.open_page", context, session=session, url=url, title=title)


def get_dom(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    session = _session(context)
    data = _SESSIONS.get(session) or {"session": session, "url": "about:blank", "title": "Empty", "html": "<html></html>"}
    return mock_result("browser.get_dom", context, **data)


def screenshot(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    session = _session(context)
    data = _SESSIONS.get(session) or {"url": "about:blank", "title": "Empty"}
    return mock_result(
        "browser.screenshot",
        context,
        session=session,
        url=data.get("url"),
        image_data_url=fake_png_data_url(f"browser:{session}"),
        width=int(payload.get("width") or 1280),
        height=int(payload.get("height") or 720),
    )


def click(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    session = _session(context)
    selector = str(payload.get("selector") or "body")
    return mock_result("browser.click", context, session=session, selector=selector, clicked=True)
