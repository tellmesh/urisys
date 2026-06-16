from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any

from urirdp_kvm.display import allow_real, base_env, detect_display, run_cmd


def _service_status(name: str) -> dict[str, Any]:
    try:
        res = subprocess.run(['pgrep', '-a', name], text=True, capture_output=True, check=False)
        return {'running': res.returncode == 0, 'processes': [x for x in res.stdout.splitlines() if x.strip()]}
    except Exception as exc:
        return {'running': False, 'error': str(exc)}


def status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {
        'target': context.get('params', {}).get('target'),
        'xrdp': _service_status('xrdp'),
        'xrdp_sesman': _service_status('xrdp-sesman'),
        'display': detect_display(context),
        'rdp_port': int(os.environ.get('RDP_PORT', '3389')),
        'uri_port': int(os.environ.get('URISYS_RDP_PORT', '8795')),
        'hint': 'Connect with an RDP client, then run kvm://... calls against the active X session.',
    }


def display(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    display_name = detect_display(context)
    res = run_cmd(['xdpyinfo'], {**context, 'display': display_name}, timeout=5)
    return {
        'display': display_name,
        'available': res.returncode == 0,
        'xdpyinfo_first_lines': res.stdout.splitlines()[:8],
        'error': res.stderr.strip() if res.returncode != 0 else None,
    }


def display_status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    display_name = detect_display(context)
    socket_path = Path('/tmp/.X11-unix') / f"X{display_name.lstrip(':')}"
    display_exists = socket_path.exists()
    xdpyinfo_ok = False
    if display_exists:
        xdpyinfo_ok = run_cmd(['xdpyinfo'], context, timeout=5).returncode == 0

    screenshot_ok = False
    if allow_real(context) and xdpyinfo_ok:
        probe = Path('/tmp/urirdp-probe.png')
        shot = run_cmd(['scrot', str(probe)], context, timeout=10)
        screenshot_ok = shot.returncode == 0 and probe.exists() and probe.stat().st_size >= 128
        probe.unlink(missing_ok=True)

    return {
        'display': display_name,
        'display_exists': display_exists,
        'xdpyinfo_ok': xdpyinfo_ok,
        'screenshot_ok': screenshot_ok,
        'ready': display_exists and xdpyinfo_ok,
    }


def prepare_target(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    display_name = detect_display(context)
    kind = str(payload.get('kind') or 'info')
    text = str(payload.get('text') or 'OK')
    if context.get('dry_run') or not allow_real(context):
        return {'prepared': True, 'driver': 'mock', 'display': display_name, 'text': text, 'kind': kind}

    env = base_env(context)
    if kind == 'form':
        subprocess.Popen(
            [
                'zenity', '--forms',
                '--title=TellMesh Demo',
                '--text=Fill the form',
                '--add-entry=Name',
                '--ok-label=Submit',
                '--width=420',
                '--height=220',
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2.0)
        run_cmd(['xdotool', 'search', '--name', 'TellMesh Demo', 'windowactivate'], context, timeout=5)
        return {'prepared': True, 'display': display_name, 'kind': 'form', 'driver': 'zenity-forms'}

    subprocess.Popen(
        [
            'zenity', '--info',
            '--title=Automation Target',
            f'--text={text}',
            '--no-wrap',
            '--width=320',
            '--height=120',
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    run_cmd(['xdotool', 'search', '--name', 'Automation Target', 'windowactivate'], context, timeout=5)
    return {'prepared': True, 'display': display_name, 'text': text, 'driver': 'zenity', 'kind': kind}
