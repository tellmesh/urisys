"""Enable full-trust desktop slave (systemd user unit + node.env + profile)."""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Mirrors urisys-node/config/node-profile.full-trust.json (embedded for pip-only installs).
FULL_TRUST_PROFILE: dict[str, Any] = {
    "profile_id": "urisys-node-full-trust",
    "node_id": "${URISYS_NODE_ID:-host}",
    "screen": {
        "default_backend": "auto",
        "output_dir": "~/.local/share/urisys/screens",
    },
    "kvm": {"driver": "mss"},
    "him": {"driver": "ydotool"},
    "browser": {
        "driver": "system-open",
        "user_data_dir": "~/.config/urisys/chrome-cdp",
        "cdp_endpoint": "http://127.0.0.1:9222",
    },
    "kv": {"driver": "sqlite", "path": "~/.local/share/urisys/store.db"},
    "policy": {
        "require_pairing": False,
        "require_approval_for": [],
        "visible_indicator": True,
    },
    "log": {
        "streams": {
            "events": "~/.local/share/urisys/events.jsonl",
            "node": "/tmp/urisys-node.log",
        }
    },
}

NODE_ENV_TEMPLATE = """\
URISYS_ALLOW_REAL=1
URISYS_NODE_AUTO_INSTALL=1
URISYS_PACK_SOURCE=auto
URISYS_NODE_PACKS=node,screen,shell,browser,kv
URISYS_NODE_ID={node_id}
URISYS_HIM_DRIVER=ydotool
"""

SYSTEMD_UNIT_TEMPLATE = """\
[Unit]
Description=urisys-node URI slave
After=network-online.target graphical-session.target
Wants=network-online.target

[Service]
Type=simple
Environment=URISYS_NODE_PACKS=node
Environment=URISYS_NODE_WORKER_PACKS=screen,shell,kvm,him,ocr,llm,img2nl,browser,office,mail,kv,vql
Environment=URISYS_NODE_AUTO_INSTALL=1
Environment=URISYS_ALLOW_REAL=1
Environment=URISYS_PACK_SOURCE=auto
Environment=URISYS_NODE_DATA=%h/.local/share/urisys
Environment=URISYS_NODE_EVENTS=%h/.local/share/urisys/events.jsonl
Environment=URISYS_NODE_CONFIG=%h/.config/urisys/node-profile.json
Environment=URISYS_BROWSER_USER_DATA_DIR=%h/.config/urisys/chrome-cdp
EnvironmentFile=-%h/.config/urisys/node.env
EnvironmentFile=-%h/.config/urisys/secrets.env
ExecStartPre=/bin/mkdir -p %h/.local/share/urisys/screens %h/.local/share/urisys/office %h/.local/share/urisys/browser
ExecStart={exec_start}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""


def default_node_id() -> str:
    return os.environ.get("URISYS_NODE_ID") or socket.gethostname().split(".")[0]


def resolve_urisys_node_root() -> Path | None:
    env = os.environ.get("URISYS_NODE_ROOT")
    if env:
        root = Path(env).expanduser().resolve()
        if (root / "scripts" / "enable-host-trust.sh").is_file():
            return root
    try:
        import urisysnode  # type: ignore

        pkg = Path(urisysnode.__file__).resolve().parent
        for candidate in (pkg.parent, pkg.parent.parent):
            if (candidate / "scripts" / "enable-host-trust.sh").is_file():
                return candidate
    except ImportError:
        pass
    for candidate in (
        Path.home() / "github" / "tellmesh" / "urisys-node",
        Path(__file__).resolve().parents[3] / "urisys-node",
    ):
        if (candidate / "scripts" / "enable-host-trust.sh").is_file():
            return candidate.resolve()
    return None


def resolve_enable_host_trust_script() -> Path | None:
    root = resolve_urisys_node_root()
    if root is None:
        return None
    script = root / "scripts" / "enable-host-trust.sh"
    return script if script.is_file() else None


def resolve_urisys_node_bin(*, venv: str | Path | None = None) -> Path:
    if venv is not None:
        candidate = Path(venv).expanduser() / "bin" / "urisys-node"
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
        raise FileNotFoundError(f"urisys-node not found in venv: {candidate}")
    found = shutil.which("urisys-node")
    if found:
        return Path(found).resolve()
    for candidate in (
        Path.home() / "venv" / "bin" / "urisys-node",
        Path.home() / ".venv" / "bin" / "urisys-node",
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    raise FileNotFoundError(
        "urisys-node executable not found; pass --venv /path/to/venv (directory containing bin/urisys-node)"
    )


def _git_pull(repo: Path, *, dry_run: bool) -> dict[str, Any]:
    if not (repo / ".git").is_dir():
        return {"ok": True, "skipped": True, "reason": "not a git checkout"}
    cmd = ["git", "-C", str(repo), "pull", "--ff-only"]
    if dry_run:
        return {"ok": True, "dry_run": True, "command": cmd}
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _run_shell_script(
    script: Path,
    *,
    venv: Path,
    node_id: str,
    port: int,
    host: str,
    dry_run: bool,
) -> dict[str, Any]:
    cmd = [
        "bash",
        str(script),
        "--venv",
        str(venv),
        "--node-id",
        node_id,
        "--port",
        str(port),
        "--host",
        host,
    ]
    if dry_run:
        return {"ok": True, "dry_run": True, "mode": "shell_script", "command": cmd}
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "ok": proc.returncode == 0,
        "mode": "shell_script",
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": cmd,
    }


def _write_if_absent(path: Path, content: str, *, dry_run: bool) -> str:
    if path.is_file():
        return "kept"
    if dry_run:
        return "would_write"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "wrote"


def _enable_host_trust_python(
    *,
    node_bin: Path,
    node_id: str,
    port: int,
    host: str,
    dry_run: bool,
) -> dict[str, Any]:
    home = Path.home()
    cfg = home / ".config" / "urisys"
    data = home / ".local" / "share" / "urisys"
    unit_dir = home / ".config" / "systemd" / "user"
    actions: list[dict[str, Any]] = []

    if not dry_run:
        for sub in ("screens", "office", "browser"):
            (data / sub).mkdir(parents=True, exist_ok=True)
        cfg.mkdir(parents=True, exist_ok=True)
        unit_dir.mkdir(parents=True, exist_ok=True)

    node_env = cfg / "node.env"
    actions.append(
        {
            "path": str(node_env),
            "action": _write_if_absent(node_env, NODE_ENV_TEMPLATE.format(node_id=node_id), dry_run=dry_run),
        }
    )

    profile = dict(FULL_TRUST_PROFILE)
    profile["node_id"] = node_id
    profile_path = cfg / "node-profile.json"
    actions.append(
        {
            "path": str(profile_path),
            "action": _write_if_absent(
                profile_path,
                json.dumps(profile, indent=2, ensure_ascii=False) + "\n",
                dry_run=dry_run,
            ),
        }
    )

    exec_start = f"{node_bin} serve --host {host} --port {port}"
    unit_body = SYSTEMD_UNIT_TEMPLATE.format(exec_start=exec_start).replace("%h", str(home))
    unit_path = unit_dir / "urisys-node.service"
    if dry_run:
        actions.append({"path": str(unit_path), "action": "would_write"})
    else:
        unit_path.write_text(unit_body, encoding="utf-8")
        actions.append({"path": str(unit_path), "action": "wrote"})

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "mode": "python",
            "node_bin": str(node_bin),
            "node_id": node_id,
            "bind": f"{host}:{port}",
            "actions": actions,
        }

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "urisys-node.service"], check=False, capture_output=True)
    subprocess.run(["loginctl", "enable-linger", os.environ.get("USER", "")], check=False, capture_output=True)
    restart = subprocess.run(
        ["systemctl", "--user", "restart", "urisys-node.service"],
        capture_output=True,
        text=True,
        check=False,
    )
    time.sleep(2)
    health: dict[str, Any] = {"ok": False}
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            health = {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        health = {"ok": False, "error": str(exc), "url": url}

    ok = restart.returncode == 0 and health.get("ok")
    return {
        "ok": ok,
        "mode": "python",
        "node_bin": str(node_bin),
        "node_id": node_id,
        "bind": f"{host}:{port}",
        "actions": actions,
        "systemd_restart": {
            "exit_code": restart.returncode,
            "stderr": restart.stderr,
        },
        "health": health,
        "hint": None if ok else "check: systemctl --user status urisys-node.service",
    }


def run_host_trust(
    *,
    venv: str | Path | None = None,
    node_id: str | None = None,
    port: int = 8790,
    host: str = "0.0.0.0",
    pull: bool = False,
    dry_run: bool = False,
    prefer_script: bool = True,
) -> dict[str, Any]:
    """Configure full-trust slave (node.env, profile, systemd) and restart the service."""
    nid = node_id or default_node_id()
    venv_path = Path(venv).expanduser() if venv else Path.home() / "venv"
    try:
        node_bin = resolve_urisys_node_bin(venv=venv_path if venv else None)
    except FileNotFoundError as exc:
        return {"ok": False, "error": str(exc)}

    report: dict[str, Any] = {
        "node_id": nid,
        "venv": str(venv_path),
        "node_bin": str(node_bin),
        "bind": f"{host}:{port}",
    }

    root = resolve_urisys_node_root()
    if pull and root is not None:
        pull_result = _git_pull(root, dry_run=dry_run)
        report["git_pull"] = pull_result
        if not pull_result.get("ok"):
            return {**report, "ok": False, "error": "git pull failed"}

    script = resolve_enable_host_trust_script() if prefer_script else None
    if script is not None:
        result = _run_shell_script(
            script,
            venv=venv_path,
            node_id=nid,
            port=port,
            host=host,
            dry_run=dry_run,
        )
        report.update(result)
        return report

    result = _enable_host_trust_python(
        node_bin=node_bin,
        node_id=nid,
        port=port,
        host=host,
        dry_run=dry_run,
    )
    report.update(result)
    return report


def remote_host_trust_command(
    *,
    venv: str = "~/venv",
    node_id: str = "lenovo",
    port: int = 8790,
    host: str = "0.0.0.0",
    pull: bool = True,
    repo: str = "~/github/tellmesh/urisys-node",
    script_url: str | None = None,
) -> str:
    """Shell script to run on the slave (urisys node host-trust, local script, or curl fallback)."""
    venv_exp = str(Path(venv).expanduser())
    repo_exp = str(Path(repo).expanduser())
    url = script_url or os.environ.get(
        "URISYS_HOST_TRUST_SCRIPT_URL",
        "https://raw.githubusercontent.com/tellmesh/urisys-node/main/scripts/enable-host-trust.sh",
    )
    pull_block = ""
    if pull:
        pull_block = f'if [ -d "{repo_exp}/.git" ]; then (cd "{repo_exp}" && git pull --ff-only) || exit 1; fi\n'
    return (
        f'{pull_block}'
        f'if command -v urisys >/dev/null 2>&1 && urisys node host-trust -h >/dev/null 2>&1; then\n'
        f'  source "{venv_exp}/bin/activate" 2>/dev/null || true\n'
        f'  exec urisys node host-trust --venv "{venv_exp}" --node-id {node_id} --port {port} --host {host} --no-pull\n'
        f'fi\n'
        f'if [ -f "{repo_exp}/scripts/enable-host-trust.sh" ]; then\n'
        f'  exec bash "{repo_exp}/scripts/enable-host-trust.sh" --venv "{venv_exp}" --node-id {node_id} --port {port} --host {host}\n'
        f'fi\n'
        f'TMP_SCRIPT="$(mktemp)"\n'
        f'if curl -fsSL "{url}" -o "$TMP_SCRIPT"; then\n'
        f'  chmod +x "$TMP_SCRIPT"\n'
        f'  exec bash "$TMP_SCRIPT" --venv "{venv_exp}" --node-id {node_id} --port {port} --host {host}\n'
        f'fi\n'
        f'echo "ERROR: need urisys with host-trust, urisys-node checkout, or curl access to {url}" >&2\n'
        f"exit 1"
    )
