"""One-shot environment bootstrap: pip install deps, doctor, slave env hints."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

from .doctor import run_doctor
from .edge_install import ensure_urisysedge
from .node_install import diagnose_urisys_node, install_urisys_node, pip_spec as node_pip_spec
from .uricore_install import diagnose_uricore, is_wrong_uricore_installed, pip_spec, repair_uricore, wheel_url

Profile = Literal["slave", "dev"]

from .defaults import DEFAULT_MIN_VERSION, NODE_SERVE_CMD
DEFAULT_GITHUB_URICORE_VERSION = "0.1.8"

SLAVE_ENV = {
    "URISYS_ALLOW_REAL": "1",
    "URISYS_NODE_AUTO_INSTALL": "1",
}

DEV_ENV: dict[str, str] = {}

DEFAULT_ENV_FILE = Path.home() / ".config" / "urisys" / "node.env"


def default_pip_specs(*, profile: Profile = "slave") -> list[str]:
    del profile
    return [
        "pip",
        pip_spec(),
        "urisysedge>=0.1.0",
        f'urisys[real]>={DEFAULT_MIN_VERSION}',
    ]


def default_node_pip_spec() -> str:
    """Public GitHub Release wheel — never git+https (avoids credential prompts)."""
    return node_pip_spec()


def pip_install_specs(
    specs: list[str],
    *,
    python: str | None = None,
    timeout: float = 600.0,
) -> dict[str, Any]:
    exe = python or sys.executable
    cmd = [exe, "-m", "pip", "install", "-U", *specs]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {
        "ok": proc.returncode == 0,
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "")[-3000:],
        "stderr": (proc.stderr or "")[-3000:],
        "specs": specs,
    }


def verify_uri_control() -> dict[str, Any]:
    try:
        import uri_control  # noqa: F401
    except ModuleNotFoundError as exc:
        detail = diagnose_uricore()
        return {
            "ok": False,
            "error": str(exc),
            "missing": exc.name,
            "diagnosis": detail,
            "pip_hint": f"pip install -U {wheel_url()}",
        }
    return {"ok": True, "module": "uri_control"}


def profile_env(profile: Profile) -> dict[str, str]:
    return dict(SLAVE_ENV if profile == "slave" else DEV_ENV)


def render_env_shell(env: dict[str, str]) -> str:
    lines = [f'export {key}="{value}"' for key, value in sorted(env.items())]
    lines.append("# start desktop slave:")
    lines.append(NODE_SERVE_CMD)
    return "\n".join(lines) + "\n"


def write_env_file(path: Path, env: dict[str, str], *, dry_run: bool = False) -> dict[str, Any]:
    content = render_env_shell(env)
    if dry_run:
        return {"ok": True, "dry_run": True, "path": str(path), "bytes": len(content)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"ok": True, "path": str(path), "bytes": len(content)}


def _pre_repair_uricore(
    install: bool, dry_run: bool, steps: list[dict[str, Any]], profile: str
) -> dict[str, Any] | None:
    """Remove a wrong PyPI uricore before install. Returns an abort-result dict
    if repair failed, else None to continue."""
    if not (install and not dry_run and is_wrong_uricore_installed()):
        return None
    pre_repair = repair_uricore()
    steps.append(
        {
            "name": "pre_repair_uricore",
            "status": "pass" if pre_repair.get("ok") else "fail",
            "detail": pre_repair,
        }
    )
    if pre_repair.get("ok"):
        return None
    return {
        "ok": False,
        "profile": profile,
        "steps": steps,
        "error": "could not remove wrong PyPI uricore before install",
        "hint": f"Run: pip uninstall -y uricore && pip install -U {wheel_url()}",
    }


def _build_pip_result(specs: list[str], *, dry_run: bool) -> dict[str, Any]:
    """Run (or describe, when dry_run) the pip install of core + edge + node."""
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "command": f"{sys.executable} -m pip install -U {' '.join(specs)}",
            "specs": specs,
            "node_spec": default_node_pip_spec(),
        }
    pip_result = pip_install_specs(specs)
    edge_result = ensure_urisysedge()
    node_result = install_urisys_node()
    pip_result = {
        **pip_result,
        "urisysedge_install": edge_result,
        "node_spec": default_node_pip_spec(),
        "node_install": node_result,
    }
    if not edge_result.get("ok"):
        pip_result["edge_warning"] = "urisysedge missing after pip — retry: pip install -U urisysedge"
    if not node_result.get("ok"):
        pip_result["node_warning"] = (
            "urisys-node install failed — publish GitHub Release "
            f"({node_result.get('spec')}) or set URISYS_NODE_WHEEL_URL / URISYS_NODE_PIP_SPEC"
        )
    return pip_result


def _resolve_error_hint(
    ok: bool, verify: dict[str, Any], doctor: dict[str, Any]
) -> tuple[str | None, str | None]:
    """Pick the user-facing error + hint when init did not fully succeed."""
    if ok:
        return None, None
    if not verify.get("ok"):
        return "uri_control not importable after init", verify.get("pip_hint") or f"pip install -U {wheel_url()}"
    if doctor.get("ok") is False:
        return "urisys doctor reported failures", "urisys doctor"
    return None, None


def run_init(
    *,
    profile: Profile = "slave",
    min_version: str | None = DEFAULT_MIN_VERSION,
    install: bool = True,
    dry_run: bool = False,
    write_env: bool = True,
    env_file: Path | None = None,
    extra_specs: list[str] | None = None,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    specs = default_pip_specs(profile=profile)
    if extra_specs:
        specs.extend(extra_specs)

    pip_result: dict[str, Any] | None = None
    abort = _pre_repair_uricore(install, dry_run, steps, profile)
    if abort is not None:
        return abort

    if install:
        pip_result = _build_pip_result(specs, dry_run=dry_run)
        steps.append({"name": "pip_install", "status": "pass" if pip_result.get("ok") else "fail", "detail": pip_result})
        if not pip_result.get("ok"):
            return {
                "ok": False,
                "profile": profile,
                "steps": steps,
                "error": "pip install failed",
                "pip": pip_result,
                "hint": "Fix pip/network, then rerun: urisys init",
            }

    verify = verify_uri_control() if not dry_run else {"ok": True, "dry_run": True}
    if not dry_run and not verify.get("ok") and (is_wrong_uricore_installed() or install):
        repair = repair_uricore()
        steps.append(
            {
                "name": "repair_uricore",
                "status": "pass" if repair.get("ok") else "fail",
                "detail": repair,
            }
        )
        verify = verify_uri_control()
    steps.append({"name": "verify_uri_control", "status": "pass" if verify.get("ok") else "fail", "detail": verify})

    doctor = run_doctor(min_version=min_version) if not dry_run else {"ok": True, "dry_run": True, "checks": []}
    steps.append(
        {
            "name": "doctor",
            "status": "pass" if doctor.get("ok") else "fail",
            "detail": doctor,
        }
    )

    env = profile_env(profile)
    env_path = env_file or DEFAULT_ENV_FILE
    env_written: dict[str, Any] | None = None
    if write_env and env:
        env_written = write_env_file(env_path, env, dry_run=dry_run)
        steps.append({"name": "write_env", "status": "pass", "detail": env_written})

    ok = all(step["status"] == "pass" for step in steps)
    node_diag = diagnose_urisys_node() if not dry_run else {}
    if not dry_run and install and not node_diag.get("urisysnode_importable"):
        node_detail = (pip_result or {}).get("node_install") if pip_result else None
        steps.append(
            {
                "name": "verify_urisysnode",
                "status": "warn",
                "detail": {**node_diag, "pip": node_detail},
            }
        )
    error, hint = _resolve_error_hint(ok, verify, doctor)

    next_steps = [
        f"source {env_path}" if env_written and env else "",
        "urisys doctor",
        NODE_SERVE_CMD,
    ]
    next_steps = [s for s in next_steps if s]

    return {
        "ok": ok,
        "profile": profile,
        "steps": steps,
        "doctor": doctor,
        "pip": pip_result,
        "verify_uri_control": verify,
        "env_file": str(env_path) if env_written else None,
        "shell_env": render_env_shell(env) if env else "",
        "next_steps": next_steps,
        "error": error,
        "hint": hint,
    }
