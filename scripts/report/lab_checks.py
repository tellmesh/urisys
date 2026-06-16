from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .models import (
    BASELINE_LABEL,
    MIN_VISION_CONFIDENCE,
    Finding,
    FlowOutcome,
    GUI_SCHEMES,
)
from .util import read_json


def iter_step_results(steps: list[dict[str, Any]]):
    for step in steps or []:
        result = ((step.get("response") or {}).get("result")) or {}
        yield result
        for stage in (result.get("pipeline") or {}).values():
            if isinstance(stage, dict) and isinstance(stage.get("result"), dict):
                yield stage["result"]


def load_flow_outcomes(session_dir: Path) -> list[FlowOutcome]:
    responses_dir = session_dir / "responses"
    if not responses_dir.is_dir():
        return []
    outcomes: list[FlowOutcome] = []
    for resp_path in sorted(responses_dir.glob("*.json")):
        data = read_json(resp_path) or {}
        steps = data.get("steps") or []
        confidences = [
            float(r.get("confidence") or 0.0)
            for r in iter_step_results(steps)
            if "action" in r and "confidence" in r and "model" in r
        ]
        expect_data = dict(data.get("expect") or {})
        outcomes.append(
            FlowOutcome(
                flow=str(data.get("flow") or resp_path.stem),
                is_gui=any(str(s.get("uri") or "").startswith(GUI_SCHEMES) for s in steps),
                duplicate_of=data.get("duplicate_of"),
                vision_confidences=confidences,
                has_contract=bool(expect_data),
                expect=expect_data,
                expect_failures=list(data.get("expect_failures") or []),
            )
        )
    return outcomes


def check_declared_expectations(outcomes: list[FlowOutcome]) -> list[Finding]:
    findings: list[Finding] = []
    for o in outcomes:
        for failure in o.expect_failures:
            findings.append(
                Finding(
                    code="expectation-failed",
                    message=f"Flow `{o.flow}` złamał zadeklarowany kontrakt `expect:` — {failure}.",
                )
            )
    return findings


def check_gui_no_effect(outcomes: list[FlowOutcome]) -> list[Finding]:
    flows = [o.flow for o in outcomes if o.no_visible_effect and not o.has_contract]
    if not flows:
        return []
    return [
        Finding(
            code="gui-no-visible-effect",
            message=f"GUI flows produced no visible change (screenshot == baseline): {', '.join(flows)}.",
            recommendation=(
                "Wzbogać kryterium pass o weryfikację efektu: dla flow GUI traktuj "
                "screenshot identyczny z baseline jako ostrzeżenie/fail, albo asercję "
                "na zmianę OCR/diff pikseli."
            ),
        )
    ]


def check_vision_never_decides(outcomes: list[FlowOutcome]) -> list[Finding]:
    relevant = [o for o in outcomes if not o.has_contract]
    calls = [c for o in relevant for c in o.vision_confidences]
    if not calls or any(o.vision_decided for o in relevant):
        return []
    return [
        Finding(
            code="vision-never-decides",
            message=(
                f"Pipeline LLM-vision nie podjął żadnej decyzji ({len(calls)} wywołań, "
                f"confidence < {MIN_VISION_CONFIDENCE}) — klik spada na współrzędne fallback."
            ),
            recommendation=(
                "Zweryfikuj klucz/modele LLM (np. OPENROUTER_API_KEY i model vision) — "
                "obecnie kvm.click_text klika 'na ślepo' mimo ok:true; rozważ fail gdy "
                "target_text nie został znaleziony w OCR i LLM nie wskazał celu."
            ),
        )
    ]


def _duplicate_recommendation(outcome: FlowOutcome) -> str:
    if outcome.duplicate_of == BASELINE_LABEL and outcome.is_gui:
        return (
            "Flow GUI nie zmienił pulpitu względem baseline — rozważ dismiss-target "
            "przed akcją lub dodaj `expect: screen_changed: true`."
        )
    if outcome.expect.get("opened_url_contains"):
        return (
            "Duplikat pikseli jest akceptowalny — flow weryfikuje nawigację przez "
            "`opened_url_contains`, nie diff screenshotu."
        )
    if outcome.has_contract:
        return (
            "Dodaj `screen_changed_since_previous: true` lub `opened_url_contains` "
            "gdy flow musi udowodnić efekt poza samym screenshotem."
        )
    if outcome.duplicate_of != BASELINE_LABEL:
        return (
            "Flow protokołowy (np. WebRTC) może nie zmieniać pulpitu — "
            "to informacja, nie fail, jeśli brak `expect: screen_changed`."
        )
    return ""


def check_duplicate_screenshots(outcomes: list[FlowOutcome]) -> list[Finding]:
    findings: list[Finding] = []
    for o in outcomes:
        if not o.duplicate_of:
            continue
        if not o.is_gui and o.duplicate_of == BASELINE_LABEL:
            continue
        findings.append(
            Finding(
                code="duplicate-screenshot",
                message=f"Flow `{o.flow}` — screenshot identyczny z `{o.duplicate_of}` (md5 duplicate).",
                recommendation=_duplicate_recommendation(o),
            )
        )
    return findings


def check_shell_baseline_duplicate(outcomes: list[FlowOutcome]) -> list[Finding]:
    flows = [
        o.flow
        for o in outcomes
        if not o.is_gui and o.duplicate_of == BASELINE_LABEL and not o.has_contract
    ]
    if not flows:
        return []
    return [
        Finding(
            code="shell-baseline-duplicate",
            message=(
                f"Flow shell/TUI bez efektu na pulpicie RDP (screenshot == baseline): "
                f"{', '.join(flows)}."
            ),
            recommendation=(
                "To oczekiwane dla kroków apt/shell w kontenerze — transport ok. "
                "Dla obserwowalności rozważ osobny krok kvm:// screenshot lub `expect:`."
            ),
        )
    ]


LAB_FLOW_CHECKS: list[Callable[[list[FlowOutcome]], list[Finding]]] = [
    check_declared_expectations,
    check_duplicate_screenshots,
    check_shell_baseline_duplicate,
    check_gui_no_effect,
    check_vision_never_decides,
]


def analyze_lab_flows(session_dir: Path) -> tuple[list[str], list[str]]:
    outcomes = load_flow_outcomes(session_dir)
    if not outcomes:
        return [], []
    findings: list[str] = []
    recommendations: list[str] = []
    for check in LAB_FLOW_CHECKS:
        for finding in check(outcomes):
            findings.append(finding.message)
            if finding.recommendation:
                recommendations.append(finding.recommendation)
    return findings, recommendations
