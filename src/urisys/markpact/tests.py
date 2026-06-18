"""Embedded Markpact test runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..defaults import DEFAULT_ENVIRONMENT
from ..managers.markpact_models import CompiledMarkpact
from .compiler import MarkpactCompiler


def check_expectations(result: dict[str, Any], expect: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if "ok" in expect and bool(result.get("ok")) != bool(expect["ok"]):
        failures.append(f"expected ok={expect['ok']!r}, got {result.get('ok')!r}")
    if "operation" in expect and result.get("operation") != expect["operation"]:
        failures.append(f"expected operation={expect['operation']!r}, got {result.get('operation')!r}")
    if "result_contains" in expect:
        for key, expected_value in (expect.get("result_contains") or {}).items():
            if result.get("result", {}).get(key) != expected_value:
                failures.append(
                    f"expected result.{key}={expected_value!r}, got {result.get('result', {}).get(key)!r}"
                )
    return not failures, failures


def run_markpact_tests(
    compiled: CompiledMarkpact,
    *,
    events_path: str | Path | None = None,
) -> dict[str, Any]:
    if not compiled.tests_path or not compiled.tests_path.exists():
        return {"ok": True, "compiled": compiled.to_dict(), "tests": [], "message": "No markpact:tests block."}

    from ..controllers.uri_controller import UriController

    test_data = yaml.safe_load(compiled.tests_path.read_text(encoding="utf-8")) or {}
    tests = test_data.get("tests") or [] if isinstance(test_data, dict) else []
    results = []
    ctrl = UriController(
        packs=str(compiled.manifest_path),
        events_path=str(events_path or compiled.cache_dir / "test-events.jsonl"),
    )
    try:
        for item in tests:
            uri = item["uri"]
            context = item.get("context") or {}
            result = ctrl.call(
                uri,
                item.get("payload") or {},
                approved=bool(context.get("approved")),
                dry_run=bool(context.get("dry_run")),
                allow_real=bool(context.get("allow_real")),
                environment=str(context.get("environment", DEFAULT_ENVIRONMENT)),
                context=context,
            )
            ok, failures = check_expectations(result, item.get("expect") or {})
            results.append({"id": item.get("id", uri), "ok": ok, "failures": failures, "result": result})
    finally:
        ctrl.close()
    return {"ok": all(r["ok"] for r in results), "compiled": compiled.to_dict(), "tests": results}


def run_tests_for_path(
    path: str | Path,
    *,
    cache_root: Path,
    events_path: str | Path | None,
    validate,
) -> dict[str, Any]:
    compiled = MarkpactCompiler(cache_root).compile(path, validate=validate)
    return run_markpact_tests(compiled, events_path=events_path)


__all__ = ["check_expectations", "run_markpact_tests", "run_tests_for_path"]
