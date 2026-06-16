from __future__ import annotations

import os
from pathlib import Path


def load_urisys_env() -> str | None:
    candidates: list[Path] = []
    if os.environ.get("URISYS_ENV_FILE"):
        candidates.append(Path(os.environ["URISYS_ENV_FILE"]))
    candidates.append(Path(__file__).resolve().parents[4] / ".env")
    for path in candidates:
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return str(path)
    return None
