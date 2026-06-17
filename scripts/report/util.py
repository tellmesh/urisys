from __future__ import annotations

import json
import platform
import socket
from pathlib import Path
from typing import Any


# Shared timestamp format ('…Z') with the session-runner core (one source).
from session_core import now_iso  # noqa: E402,F401


def host_id() -> str:
    return f"{socket.gethostname()} ({platform.system()} {platform.machine()})"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if text else ""
