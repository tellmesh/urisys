"""Per-rule tests for markpact analyzer MP001–MP010."""

from __future__ import annotations

from urisys.markpact.analyzer.context import MarkpactLintContext
from urisys.markpact.analyzer.rules.capabilities import MP001NamespacedOperation, MP002QueryKind
from urisys.markpact.analyzer.rules.pack import MP009ProcessRequiresSchemes, MP010RequiresCapabilitiesNamespaced
from urisys.markpact.analyzer.rules.schemes import MP006UndeclaredScheme


def test_mp001_rule_isolated():
    rule = MP001NamespacedOperation()
    ctx = MarkpactLintContext(
        pack={},
        scheme="stepper",
        capabilities=[{"uri": "stepper://d/q/status", "kind": "query", "operation": "status"}],
        flows=[],
        undeclared_schemes=[],
    )
    issues = rule.check(ctx)
    assert len(issues) == 1
    assert issues[0].code == "MP001"


def test_mp002_rule_isolated():
    rule = MP002QueryKind()
    ctx = MarkpactLintContext(
        pack={},
        scheme="kvm",
        capabilities=[
            {
                "uri": "kvm://local/monitor/primary/query/screenshot",
                "kind": "command",
                "operation": "kvm.monitor.screenshot",
            }
        ],
        flows=[],
        undeclared_schemes=[],
    )
    issues = rule.check(ctx)
    assert len(issues) == 1
    assert issues[0].code == "MP002"


def test_mp006_rule_isolated():
    rule = MP006UndeclaredScheme()
    ctx = MarkpactLintContext(
        pack={},
        scheme="process",
        capabilities=[],
        flows=[],
        undeclared_schemes=["browser"],
    )
    issues = rule.check(ctx)
    assert len(issues) == 1
    assert issues[0].code == "MP006"


def test_mp009_rule_isolated():
    rule = MP009ProcessRequiresSchemes()
    ctx = MarkpactLintContext(
        pack={"capabilities": []},
        scheme="process",
        capabilities=[],
        flows=[],
        undeclared_schemes=[],
        schemes_required=set(),
    )
    issues = rule.check(ctx)
    assert len(issues) == 1
    assert issues[0].code == "MP009"


def test_mp010_rule_isolated():
    rule = MP010RequiresCapabilitiesNamespaced()
    ctx = MarkpactLintContext(
        pack={"requires": {"capabilities": ["screenshot", "kvm.monitor.screenshot"]}},
        scheme="process",
        capabilities=[],
        flows=[],
        undeclared_schemes=[],
    )
    issues = rule.check(ctx)
    assert len(issues) == 1
    assert issues[0].code == "MP010"
    assert "screenshot" in issues[0].message
