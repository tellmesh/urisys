from __future__ import annotations

import json
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
