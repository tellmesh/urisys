from __future__ import annotations

DEFAULT_PACKAGES = {
    "browser": "uribrowser",
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
}

DEFAULT_EVENTS_PATH = "output/urisys-events.jsonl"
DEFAULT_ENVIRONMENT = "real"

# Minimum urisys version asserted by `urisys init` / `doctor`.
DEFAULT_MIN_VERSION = "0.1.25"
MIN_VERSION_ENV = "URISYS_MIN_VERSION"

# Canonical hint shown to operators for starting a desktop slave node.
NODE_SERVE_CMD = "urisys node serve --host 0.0.0.0 --port 8790"
