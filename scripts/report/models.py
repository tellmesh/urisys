from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

GUI_SCHEMES = ("kvm://", "him://", "browser://", "ocr://", "display://")
BASELINE_LABEL = "00-baseline"
MIN_VISION_CONFIDENCE = 0.1


@dataclass
class StepResult:
    name: str
    status: str  # pass | fail | skip
    uri: str | None = None
    duration_s: float | None = None
    response_file: str | None = None
    screenshot: str | None = None
    detail: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionReport:
    session_id: str
    session_name: str
    suite: str
    started_at: str
    finished_at: str
    duration_s: float
    status: str  # pass | fail | error
    host: str
    steps: list[StepResult] = field(default_factory=list)
    artifacts: dict[str, list[str]] = field(default_factory=dict)
    events_summary: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    log_tail: str = ""

    @property
    def passed(self) -> int:
        return sum(1 for s in self.steps if s.status == "pass")

    @property
    def failed(self) -> int:
        return sum(1 for s in self.steps if s.status == "fail")


@dataclass
class RunAnalysis:
    run_id: str
    generated_at: str
    host: str
    sessions: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return self.summary.get("fail", 0) == 0 and self.summary.get("error", 0) == 0


@dataclass
class Finding:
    code: str
    message: str
    recommendation: str = ""


@dataclass
class FlowOutcome:
    flow: str
    is_gui: bool
    duplicate_of: str | None
    vision_confidences: list[float] = field(default_factory=list)
    has_contract: bool = False
    expect: dict[str, Any] = field(default_factory=dict)
    expect_failures: list[str] = field(default_factory=list)

    @property
    def no_visible_effect(self) -> bool:
        return self.is_gui and self.duplicate_of == BASELINE_LABEL

    @property
    def vision_decided(self) -> bool:
        return any(c >= MIN_VISION_CONFIDENCE for c in self.vision_confidences)
