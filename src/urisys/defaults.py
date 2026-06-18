from __future__ import annotations

DEFAULT_PACKAGES = {
    "browser": "uribrowserdocker",
    "desktop": "uridesktop",
    "android": "uriandroid",
    "docker": "uridocker",
    "systemd": "urisystemd",
    "printer": "uriprinter",
    "camera": "uricamera",
    "display": "uridisplay",
    "mail": "urimail",
    "office": "urioffice",
    "vql": "urivql",
    "llm": "urillm",
    "agent": "uriagent",
    "shell": "urishell",
    "kvm": "urikvm",
    "env": "urienv",
    "rdp": "urirdp",
    "screen": "uriscreen",
    "chat": "urichat",
    "stt": "uristt",
    "message": "urimessage",
    "stepper": "uristepper",
    "him": "urihim",
    "ocr": "uriocr",
    "webrtc": "uriwebrtc",
}

DEFAULT_EVENTS_PATH = "output/urisys-events.jsonl"
DEFAULT_ENVIRONMENT = "real"

# Minimum urisys version asserted by `urisys init` / `doctor`.
# (bootstrap.py mirrors this literal on purpose — it runs standalone, no imports.)
DEFAULT_MIN_VERSION = "0.1.25"
MIN_VERSION_ENV = "URISYS_MIN_VERSION"

# Canonical hint shown to operators for starting a desktop slave node.
NODE_SERVE_CMD = "urisys node serve --host 0.0.0.0 --port 8790"
NODE_REMOTE_HEALTH_CMD = "urisys remote health --endpoint http://192.168.188.201:8790"
NODE_REMOTE_RESTART_CMD = "urisys remote restart --endpoint http://192.168.188.201:8790"

# urisys-node below this lacks port takeover and `urisys remote` delegation targets.
MIN_URISYS_NODE_VERSION = "0.1.10"
