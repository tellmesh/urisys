from __future__ import annotations

from typing import Any

from .common import run_command, var


def container_status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    name = var(context, "name", payload.get("name", ""))
    return run_command(["docker", "inspect", "--format", "{{json .State}}", name], context)


def container_start(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return run_command(["docker", "start", var(context, "name")], context)


def container_stop(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return run_command(["docker", "stop", var(context, "name")], context)


def container_restart(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return run_command(["docker", "restart", var(context, "name")], context)


def compose_up(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    project = var(context, "project", "default")
    file = str(payload.get("file") or "docker-compose.yml")
    return run_command(["docker", "compose", "-p", project, "-f", file, "up", "-d"], context)


def compose_down(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    project = var(context, "project", "default")
    file = str(payload.get("file") or "docker-compose.yml")
    return run_command(["docker", "compose", "-p", project, "-f", file, "down"], context)
