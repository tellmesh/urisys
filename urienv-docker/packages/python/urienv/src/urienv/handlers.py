from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

_NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")


def _split_csv(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(v).strip() for v in value if str(v).strip()}
    if value is None:
        return set()
    return {piece.strip() for piece in str(value).split(",") if piece.strip()}


def _cfg(context: dict[str, Any]) -> dict[str, Any]:
    # Direct env_config wins, otherwise use device_config.env. This lets the same
    # handler work with `--env-config` and with older `--device-config` runtimes.
    data = context.get("env_config") or ((context.get("device_config") or {}).get("env") or {})
    if not isinstance(data, dict):
        data = {}

    public_vars = _split_csv(data.get("public_vars")) | _split_csv(os.environ.get("URISYS_ENV_PUBLIC_VARS"))
    secret_vars = _split_csv(data.get("secret_vars")) | _split_csv(os.environ.get("URISYS_ENV_SECRET_VARS"))
    mutable_vars = _split_csv(data.get("mutable_vars")) | _split_csv(os.environ.get("URISYS_ENV_MUTABLE_VARS"))
    prefixes = _split_csv(data.get("public_prefixes")) | _split_csv(os.environ.get("URISYS_ENV_PUBLIC_PREFIXES"))
    secret_prefixes = _split_csv(data.get("secret_prefixes")) | _split_csv(os.environ.get("URISYS_ENV_SECRET_PREFIXES"))
    secrets_dir = str(data.get("docker_secrets_dir") or os.environ.get("URISYS_DOCKER_SECRETS_DIR") or "/run/secrets")

    return {
        "public_vars": public_vars,
        "secret_vars": secret_vars,
        "mutable_vars": mutable_vars,
        "public_prefixes": prefixes,
        "secret_prefixes": secret_prefixes,
        "docker_secrets_dir": secrets_dir,
        "include_process_metadata": bool(data.get("include_process_metadata", True)),
    }


def _name(context: dict[str, Any]) -> str:
    name = (context.get("variables") or {}).get("name", "")
    name = name.upper()
    if not _NAME_RE.match(name):
        raise ValueError(f"Invalid env var name: {name!r}")
    return name


def _is_public(name: str, cfg: dict[str, Any]) -> bool:
    return name in cfg["public_vars"] or any(name.startswith(prefix) for prefix in cfg["public_prefixes"])


def _is_secret(name: str, cfg: dict[str, Any]) -> bool:
    return name in cfg["secret_vars"] or any(name.startswith(prefix) for prefix in cfg["secret_prefixes"])


def _is_mutable(name: str, cfg: dict[str, Any]) -> bool:
    return name in cfg["mutable_vars"]


def _mask(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) <= 4:
        return "****"
    return value[:2] + "***" + value[-2:]


def _read_docker_secret(name: str, cfg: dict[str, Any]) -> str | None:
    # Docker secret names commonly use lowercase file names. We support exact and lowercase.
    root = Path(cfg["docker_secrets_dir"])
    for candidate in (name, name.lower()):
        path = root / candidate
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8").strip()
    return None


def _get_value(name: str, cfg: dict[str, Any]) -> tuple[str | None, str]:
    if name in os.environ:
        return os.environ.get(name), "process_env"
    secret = _read_docker_secret(name, cfg)
    if secret is not None:
        return secret, "docker_secret"
    return None, "missing"


def _require_visible(name: str, cfg: dict[str, Any]) -> None:
    if not _is_public(name, cfg):
        raise PermissionError(f"{name} is not in public env allowlist")
    if _is_secret(name, cfg):
        raise PermissionError(f"{name} is configured as secret and cannot be read as public var")


def health(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context)
    return {
        "ok": True,
        "scheme": "env",
        "public_vars": sorted(cfg["public_vars"]),
        "secret_vars": sorted(cfg["secret_vars"]),
        "mutable_vars": sorted(cfg["mutable_vars"]),
        "docker_secrets_dir": cfg["docker_secrets_dir"],
    }


def list_vars(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context)
    include_values = bool(payload.get("include_values", False))
    items: list[dict[str, Any]] = []

    for name in sorted(cfg["public_vars"]):
        value, source = _get_value(name, cfg)
        item = {"name": name, "kind": "public", "exists": value is not None, "source": source}
        if include_values:
            item["value"] = value
        items.append(item)

    for name in sorted(cfg["secret_vars"]):
        value, source = _get_value(name, cfg)
        items.append({"name": name, "kind": "secret", "exists": value is not None, "source": source, "masked": _mask(value)})

    return {"items": items}


def startup_config(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context)
    public: dict[str, Any] = {}
    secrets: dict[str, Any] = {}
    for name in sorted(cfg["public_vars"]):
        value, source = _get_value(name, cfg)
        public[name] = {"exists": value is not None, "value": value, "source": source}
    for name in sorted(cfg["secret_vars"]):
        value, source = _get_value(name, cfg)
        secrets[name] = {"exists": value is not None, "masked": _mask(value), "source": source}
    return {"public": public, "secrets": secrets}


def var_exists(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context); name = _name(context)
    value, source = _get_value(name, cfg)
    return {"name": name, "exists": value is not None, "source": source}


def var_value(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context); name = _name(context)
    _require_visible(name, cfg)
    value, source = _get_value(name, cfg)
    return {"name": name, "exists": value is not None, "value": value, "source": source}


def secret_masked(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context); name = _name(context)
    if not _is_secret(name, cfg):
        raise PermissionError(f"{name} is not in secret allowlist")
    value, source = _get_value(name, cfg)
    return {"name": name, "exists": value is not None, "masked": _mask(value), "source": source}


def secret_value(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context); name = _name(context)
    if not _is_secret(name, cfg):
        raise PermissionError(f"{name} is not in secret allowlist")
    # Approval is enforced by uricore because the route is side_effects+approval required.
    # This second gate prevents accidental secret disclosure when a generic caller adds --approve.
    if not (context.get("allow_secret_read") or os.environ.get("URISYS_ALLOW_SECRET_READ") == "1"):
        raise PermissionError("Secret value read requires allow_secret_read=true or URISYS_ALLOW_SECRET_READ=1")
    value, source = _get_value(name, cfg)
    return {"name": name, "exists": value is not None, "value": value, "source": source}


def var_set(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context); name = _name(context)
    if not _is_mutable(name, cfg):
        raise PermissionError(f"{name} is not mutable")
    if "value" not in payload:
        raise ValueError("payload.value is required")
    value = str(payload["value"])
    if context.get("dry_run"):
        return {"name": name, "would_set": value, "dry_run": True}
    os.environ[name] = value
    return {"name": name, "value": value, "set": True, "scope": "current_process"}


def var_unset(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg(context); name = _name(context)
    if not _is_mutable(name, cfg):
        raise PermissionError(f"{name} is not mutable")
    if context.get("dry_run"):
        return {"name": name, "would_unset": True, "dry_run": True}
    existed = name in os.environ
    os.environ.pop(name, None)
    return {"name": name, "unset": True, "existed": existed, "scope": "current_process"}
