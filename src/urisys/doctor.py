from __future__ import annotations

import os
import shutil
import sys
from dataclasses import asdict, dataclass
from typing import Any, Literal

CheckStatus = Literal["ok", "warn", "fail"]


@dataclass
class Check:
    id: str
    status: CheckStatus
    message: str
    detail: dict[str, Any] | None = None


def _pkg_version(dist_name: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(dist_name)
    except Exception:
        return None


def _parse_version(text: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in (text or "").strip().split("."):
        num = ""
        for ch in piece:
            if ch.isdigit():
                num += ch
            else:
                break
        if num:
            parts.append(int(num))
    return tuple(parts) if parts else (0,)


def _version_lt(left: str | None, right: str) -> bool:
    if not left:
        return True
    return _parse_version(left) < _parse_version(right)


def _check_import(name: str, module: str, *, pip_hint: str) -> Check:
    try:
        importlib = __import__("importlib")
        mod = importlib.import_module(module)
        version = getattr(mod, "__version__", None) or _pkg_version(name)
        return Check(
            id=f"import_{module.replace('.', '_')}",
            status="ok",
            message=f"{name} importable",
            detail={"version": version},
        )
    except ModuleNotFoundError as exc:
        missing = exc.name or module
        return Check(
            id=f"import_{module.replace('.', '_')}",
            status="fail",
            message=f"missing {missing}",
            detail={"pip_hint": pip_hint, "error": str(exc)},
        )
    except Exception as exc:
        return Check(
            id=f"import_{module.replace('.', '_')}",
            status="fail",
            message=f"{module} failed to import",
            detail={"error": str(exc), "pip_hint": pip_hint},
        )


def _check_python() -> Check:
    major, minor = sys.version_info[:2]
    executable = sys.executable
    version = f"{major}.{minor}.{sys.version_info.micro}"
    if (major, minor) < (3, 10):
        return Check(
            id="python_version",
            status="fail",
            message=f"Python {version} is below minimum 3.10",
            detail={"executable": executable, "version": version},
        )
    if (major, minor) >= (3, 14):
        return Check(
            id="python_version",
            status="warn",
            message=f"Python {version} is newer than tested range (3.10–3.13); prefer python3.12 venv",
            detail={"executable": executable, "version": version},
        )
    return Check(
        id="python_version",
        status="ok",
        message=f"Python {version}",
        detail={"executable": executable, "version": version},
    )


def _check_cli_path() -> Check:
    urisys_bin = shutil.which("urisys")
    node_bin = shutil.which("urisys-node")
    detail = {
        "urisys": urisys_bin,
        "urisys_node": node_bin,
        "python_executable": sys.executable,
    }
    if urisys_bin and not urisys_bin.startswith(os.path.dirname(sys.executable)):
        return Check(
            id="cli_path",
            status="warn",
            message="urisys on PATH may belong to a different Python than this interpreter",
            detail=detail,
        )
    return Check(
        id="cli_path",
        status="ok",
        message="CLI paths resolved",
        detail=detail,
    )


def _check_min_version(min_version: str | None) -> Check | None:
    if not min_version:
        return None
    current = _pkg_version("urisys")
    try:
        import urisys

        current = getattr(urisys, "__version__", None) or current
    except Exception:
        pass
    if _version_lt(current, min_version):
        return Check(
            id="urisys_min_version",
            status="fail",
            message=f"urisys {current or '?'} is older than required {min_version}",
            detail={"current": current, "required": min_version, "pip_hint": f'pip install -U "urisys[real]>={min_version}"'},
        )
    return Check(
        id="urisys_min_version",
        status="ok",
        message=f"urisys {current} meets minimum {min_version}",
        detail={"current": current, "required": min_version},
    )


def _check_wayland_him() -> Check | None:
    if not os.environ.get("WAYLAND_DISPLAY"):
        return None
    ydotool = shutil.which("ydotool")
    if ydotool:
        return Check(
            id="wayland_ydotool",
            status="ok",
            message="ydotool available for Wayland HIM",
            detail={"path": ydotool},
        )
    return Check(
        id="wayland_ydotool",
        status="warn",
        message="WAYLAND_DISPLAY set but ydotool not found — him:// may fall back to pyautogui (often fails on Wayland)",
        detail={"pip_hint": "sudo apt install ydotool && sudo systemctl enable --now ydotoold"},
    )


def _check_uricore_authentic() -> Check | None:
    from .node_install import pip_spec as node_pip_spec
    from .uricore_install import diagnose_uricore, is_wrong_uricore_installed, wheel_url

    diag = diagnose_uricore()
    if diag.get("uri_control_importable"):
        return Check(
            id="uricore_source",
            status="ok",
            message=f"uri_control from tellmesh uricore {diag.get('uricore_dist') or 'wheel'}",
            detail=diag,
        )
    if is_wrong_uricore_installed():
        return Check(
            id="uricore_source",
            status="fail",
            message="Wrong PyPI package 'uricore' installed (squatter — provides uricore/, not uri_control/)",
            detail={
                **diag,
                "pip_hint": f"pip uninstall -y uricore && pip install -U {wheel_url()}",
                "auto_fix": "urisys init",
            },
        )
    if diag.get("uricore_dist") and not diag.get("uri_control_importable"):
        return Check(
            id="uricore_source",
            status="fail",
            message="uricore metadata present but uri_control missing (broken install)",
            detail={**diag, "pip_hint": f"pip install -U {wheel_url()}", "auto_fix": "urisys init"},
        )
    return None


def _check_uricore_dist() -> Check:
    """urisys declares uricore dependency; a missing dist usually means broken user install."""
    urisys_ver = _pkg_version("urisys")
    uricore_ver = _pkg_version("uricore")
    if uricore_ver:
        return Check(
            id="dist_uricore",
            status="ok",
            message=f"uricore {uricore_ver} installed",
            detail={"urisys": urisys_ver, "uricore": uricore_ver},
        )
    if urisys_ver:
        from .uricore_install import wheel_url

        return Check(
            id="dist_uricore",
            status="fail",
            message="urisys is installed but tellmesh uricore is missing",
            detail={
                "urisys": urisys_ver,
                "pip_hint": f"pip install -U {wheel_url()}",
                "note": "Do not pip install PyPI uricore — wrong package. Use tellmesh GitHub wheel.",
            },
        )
    from .uricore_install import wheel_url

    return Check(
        id="dist_uricore",
        status="warn",
        message="uricore not found in site-packages (editable/dev install?)",
        detail={"pip_hint": f"pip install -U {wheel_url()}"},
    )


def run_doctor(*, min_version: str | None = "0.1.25") -> dict[str, Any]:
    from .node_install import pip_spec as node_pip_spec
    from .uricore_install import wheel_url

    checks: list[Check] = [
        _check_python(),
        _check_cli_path(),
        _check_uricore_dist(),
    ]
    authentic = _check_uricore_authentic()
    if authentic:
        checks.append(authentic)
    checks.extend(
        [
            _check_import("uricore", "uri_control", pip_hint=f"pip install -U {wheel_url()}"),
            _check_import("urisys", "urisys", pip_hint='pip install -U "urisys[real]"'),
            _check_import("urisysedge", "urisysedge", pip_hint="pip install -U urisysedge"),
            _check_import(
                "urisysnode",
                "urisysnode",
                pip_hint=f"pip install -U {node_pip_spec()}",
            ),
        ]
    )
    extra = _check_min_version(min_version)
    if extra:
        checks.append(extra)
    wayland = _check_wayland_him()
    if wayland:
        checks.append(wayland)

    hints = [
        "Desktop slave (lenovo): urisys node serve --host 0.0.0.0 --port 8790",
        "Dev pack server (not slave): urisys serve --port 8789",
        f"Broken uri_control? Run: urisys init  (installs {wheel_url()})",
        "Recommended: python3.12 -m venv ~/venv && source ~/venv/bin/activate && urisys init",
    ]

    failed = [c for c in checks if c.status == "fail"]
    warned = [c for c in checks if c.status == "warn"]
    ok = not failed

    return {
        "ok": ok,
        "checks": [asdict(c) for c in checks],
        "hints": hints,
        "summary": {
            "fail": len(failed),
            "warn": len(warned),
            "pass": len([c for c in checks if c.status == "ok"]),
        },
    }
