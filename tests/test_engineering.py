"""Tests for the engineering module."""

from qta.engineering import (
    engineering_readiness_gates, INTERLOCKS, EXPERIMENTS, ALL_FIXES,
    print_fixes,
)


def test_engineering_readiness_count():
    """Engineering readiness returns expected number of gates."""
    gates = engineering_readiness_gates()
    assert len(gates) >= 19  # E01-E14 + 5 shield + RTB + C_to_D


def test_engineering_gate_fields():
    """Every engineering gate has required fields."""
    for g in engineering_readiness_gates():
        assert g.gid
        assert g.name
        assert g.mode
        assert g.status in ("PASS", "CONDITIONAL", "BLOCKED", "UNKNOWN",
                            "DERIVED_CHECK", "FAIL")
        assert g.reason
        assert g.fix


def test_engineering_gate_status():
    """All engineering gates should be BLOCKED or CONDITIONAL."""
    for g in engineering_readiness_gates():
        assert g.status in ("BLOCKED", "CONDITIONAL"), f"{g.gid} is {g.status}"


def test_interlock_count():
    """There should be 14 interlocks."""
    assert len(INTERLOCKS) == 14


def test_interlock_types():
    """Interlocks are either IMPOSSIBLE or BLOCKED."""
    for il in INTERLOCKS:
        assert il[2] in ("IMPOSSIBLE", "BLOCKED")


def test_experiment_count():
    """There should be 10 priority experiments."""
    assert len(EXPERIMENTS) == 10


def test_all_fixes():
    """All fixes have required fields."""
    for fix in ALL_FIXES:
        fid, name, priority, status, gates, desc, impl, risks = fix
        assert fid
        assert priority in ("REQUIRED", "RECOMMENDED")
        assert status in ("NOT_INSTALLED", "DESIGN", "INSTALLED")
        assert len(gates) > 0


def test_print_fixes_runs():
    """print_fixes runs without error."""
    import io, sys
    captured = io.StringIO()
    sys.stdout = captured
    try:
        print_fixes()
    finally:
        sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert "ENGINEERING FIXES" in output
    assert "F01" in output
