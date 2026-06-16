from __future__ import annotations

from typing import Any

from .common import mock_result, var


def status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    device = var(context, "device", "default")
    return mock_result("printer.status", context, device=device, online=True, ink_level="unknown")


def print_test_page(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("printer.print_test_page", context, device=var(context, "device"), job_id="mock-print-job-1")


def nozzle_check(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("printer.nozzle_check", context, device=var(context, "device"), job_id="mock-nozzle-check")


def clean_head(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("printer.clean_head", context, device=var(context, "device"), started=True)
