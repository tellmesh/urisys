"""Lab browser handlers — open a visible window on the RDP display when configured."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from typing import Any

from uribrowserdocker import handlers as browser_handlers

try:
    from urirdp.handlers import _dismiss_stale_targets
except ImportError:  # pragma: no cover
    def _dismiss_stale_targets(context):  # type: ignore[misc]
        return 0


def _profile(context: dict[str, Any]) -> dict[str, Any]:
    return context.get("config", {}).get("browser", {})


def _session_state(context: dict[str, Any]) -> dict[str, Any]:
    session = context.get("params", {}).get("session", "default")
    state = context.setdefault("state", {})
    sessions = state.setdefault("browser_sessions", {})
    return sessions.setdefault(
        session,
        {"url": None, "title": None, "html": "<html><body>empty</body></html>"},
    )


def _chromium_binary(profile: dict[str, Any]) -> str | None:
    for name in (
        profile.get("binary"),
        "chromium",
        "chromium-browser",
        "google-chrome",
    ):
        if not name:
            continue
        path = shutil.which(str(name))
        if path:
            return path
    return None


def open_page(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    profile = _profile(context)
    driver = payload.get("driver") or profile.get("driver", "mock")
    if driver != "display-chromium":
        return browser_handlers.open_page(payload, context)

    url = payload.get("url")
    if not url:
        raise ValueError("payload.url is required")

    sess = _session_state(context)
    if context.get("dry_run") or not context.get("allow_real"):
        return browser_handlers.open_page(payload, context)

    binary = _chromium_binary(profile)
    if not binary:
        raise RuntimeError("display-chromium driver requires chromium in PATH")

    _dismiss_stale_targets(context)
    env = os.environ.copy()
    display = context.get("display") or env.get("DISPLAY")
    if display:
        env["DISPLAY"] = str(display)
    xauth = context.get("xauthority")
    if xauth:
        env["XAUTHORITY"] = str(xauth)

    args = [
        binary,
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        f"--app={url}",
    ]
    if profile.get("headless"):
        args.insert(1, "--headless=new")

    subprocess.Popen(
        args,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    time.sleep(float(profile.get("launch_delay_s") or 2.0))
    try:
        subprocess.run(
            ["xdotool", "search", "--class", "chromium", "windowactivate"],
            env=env,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception:
        pass

    title = payload.get("title") or "Chromium"
    html = f'<html><head><title>{title}</title></head><body><h1>{url}</h1></body></html>'
    sess.update(
        {
            "url": url,
            "title": title,
            "html": html,
            "opened_at": time.time(),
            "driver": driver,
        }
    )
    return {
        "session": context.get("params", {}).get("session"),
        "driver": driver,
        "url": url,
        "title": title,
        "launched": True,
        "binary": binary,
    }


def get_dom(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return browser_handlers.get_dom(payload, context)


def screenshot(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return browser_handlers.screenshot(payload, context)
