"""Resolve Markpact artifact-index to a runnable OCI image on this node."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml


def load_node_profile(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return data.get("node") or data


def load_artifact_index(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def select_artifact(index: dict[str, Any], node_profile: dict[str, Any]) -> dict[str, Any]:
    platform = str(node_profile.get("platform") or "linux/amd64")
    capabilities = set(node_profile.get("capabilities") or [])
    runtimes = set(node_profile.get("runtimes") or [])

    candidates = list(index.get("artifacts") or [])
    if not candidates:
        raise ValueError("artifact-index has no artifacts")

    for art in candidates:
        if art.get("platform") and art["platform"] != platform:
            continue
        if runtimes and art.get("runtime") not in runtimes:
            continue
        art_caps = set(art.get("capabilities") or [])
        if capabilities and art_caps and not capabilities.intersection(art_caps):
            continue
        return art

    # fallback: first artifact
    return candidates[0]


def docker_pull(ref: str) -> None:
    proc = subprocess.run(["docker", "pull", ref], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"docker pull failed: {ref}")


def docker_run_worker(
    ref: str,
    *,
    container: str = "urisys-stepper-worker",
    host_port: int = 8791,
    container_port: int = 8790,
) -> None:
    subprocess.run(["docker", "rm", "-f", container], capture_output=True, text=True)
    proc = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container,
            "-p",
            f"{host_port}:{container_port}",
            ref,
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "docker run failed")


def wait_health(port: int = 8791, attempts: int = 30) -> None:
    url = f"http://127.0.0.1:{port}/health"
    last = ""
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionResetError, OSError) as exc:
            last = str(exc)
        time.sleep(1)
    logs = subprocess.run(["docker", "logs", "--tail", "50", "urisys-stepper-worker"], capture_output=True, text=True)
    raise RuntimeError(f"worker health timeout on {url}: {last}\n{logs.stdout}\n{logs.stderr}")


def resolve_and_run(
    index_path: str | Path,
    profile_path: str | Path,
    *,
    container: str = "urisys-stepper-worker",
    port: int = 8791,
) -> dict[str, Any]:
    index = load_artifact_index(index_path)
    profile = load_node_profile(profile_path)
    art = select_artifact(index, profile)
    ref = str(art.get("ref") or art.get("tag") or "")
    if not ref:
        raise ValueError("selected artifact has no ref or tag")

    docker_pull(ref)
    docker_run_worker(ref, container=container, host_port=port, container_port=8790)
    wait_health(port=port)

    return {
        "ok": True,
        "platform": profile.get("platform"),
        "artifact": art,
        "ref": ref,
        "container": container,
        "port": port,
    }
