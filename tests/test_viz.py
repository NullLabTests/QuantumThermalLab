"""Tests for the viz module."""

import json
import tempfile
from pathlib import Path
from qta.model import Gate, make_mode_D_state, CHAMBER_STATE
from qta.viz import (
    gate_status_badge, write_html_report, write_json_output,
    _status_color, _status_icon,
)


def test_gate_status_badge():
    """Badge returns a string for every status."""
    for s in ("PASS", "CONDITIONAL", "BLOCKED", "UNKNOWN", "DERIVED_CHECK", "FAIL"):
        badge = gate_status_badge(s)
        assert isinstance(badge, str)
        assert len(badge) > 0


def test_status_color():
    """Every status maps to a hex color."""
    for s in ("PASS", "CONDITIONAL", "BLOCKED", "UNKNOWN", "DERIVED_CHECK", "FAIL"):
        c = _status_color(s)
        assert c.startswith("#")
        assert len(c) == 7


def test_status_icon():
    """Every status maps to a non-empty icon."""
    for s in ("PASS", "CONDITIONAL", "BLOCKED", "UNKNOWN", "DERIVED_CHECK", "FAIL"):
        icon = _status_icon(s)
        assert len(icon) > 0


def test_write_html_report_creates_file():
    """HTML report writes a valid HTML file."""
    gates = [
        Gate("T1", "Test", "D", "eq", 5, 3, "PASS", "ok", "fix"),
        Gate("T2", "Test", "D", "eq", 0, 1, "BLOCKED", "no", "fix"),
    ]
    mc = {"pass_rate": 0.5}
    info = {"pass_rate": 0.5, "note": "test", "sv": None}
    with tempfile.TemporaryDirectory() as tmp:
        p = write_html_report(gates, mc, info, "CONDITIONAL", Path(tmp) / "report.html")
        assert p.exists()
        html = p.read_text()
        assert "<!DOCTYPE html>" in html
        assert "CONDITIONAL" in html
        assert "T1" in html
        assert "T2" in html


def test_write_json_output():
    """JSON output writes valid JSON."""
    gates = [Gate("T1", "Test", "D", "eq", 5, 3, "PASS", "ok", "fix")]
    sv = make_mode_D_state(CHAMBER_STATE["post_bakeout"], tau_c_s=4e-3, tau_c_tag="TEST")
    info = {"pass_rate": 0.5, "dominant_failure": "tau_c", "note": "test", "sv": sv}
    with tempfile.TemporaryDirectory() as tmp:
        p = write_json_output(gates, {}, info, "CONDITIONAL", Path(tmp) / "out.json")
        data = json.loads(p.read_text())
        assert data["version"] == "3.1.0"
        assert data["total_gates"] == 1
        assert data["thermal"]["T_sample_mK"] > 0
