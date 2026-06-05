"""Tests for the constants module."""

import math
from qta.constants import (
    k_B, hbar, mu_0, sigma_SB, m_p, pi,
    EngStatus, gate_status_3layer, hw_status,
    PARAM_REGISTRY, BLOCKING, VALIDATED,
)


def test_physical_constants():
    """Verify physical constants have expected values."""
    assert abs(k_B - 1.380649e-23) < 1e-30
    assert abs(sigma_SB - 5.670374419e-8) < 1e-15
    assert abs(m_p - 1.67262192369e-27) < 1e-36


def test_eng_status_layers():
    """Test EngStatus three-layer status codes."""
    e = EngStatus("test")
    assert e.layer_status() == "NOT_SPECIFIED"

    e.specified = True
    assert e.layer_status() == "DESIGN_SPECIFIED"

    e.installed = True
    assert e.layer_status() == "INSTALLED_UNVERIFIED"

    e.verified = True
    assert e.layer_status() == "VERIFIED"


def test_gate_status_3layer():
    """Test SPECIFIED ≠ INSTALLED ≠ VERIFIED rule."""
    assert gate_status_3layer(False, False, False) == "CONDITIONAL"
    assert gate_status_3layer(False, False, False, blocking_if_not_specified=True) == BLOCKING
    assert gate_status_3layer(True, False, False) == "CONDITIONAL"
    assert gate_status_3layer(True, True, False) == "CONDITIONAL"
    assert gate_status_3layer(True, True, True, physics_ok=True) == "PASS"
    assert gate_status_3layer(True, True, True, physics_ok=False) == "FAIL"


def test_hw_status():
    """Test hardware status strings."""
    assert hw_status(False, False, False) == "NOT_INSTALLED"
    assert hw_status(True, False, False) == "DESIGN_SPECIFIED"
    assert hw_status(True, True, False) == "INSTALLED_UNTESTED"
    assert hw_status(True, True, True) == VALIDATED


def test_param_registry():
    """All parameters have valid source tags."""
    valid_tags = {
        "MEASURED", "LITERATURE", "ASSUMED", "UNKNOWN", "DESIGN",
        "MANUFACTURER_SPEC", "PHYSICAL_CONSTANT",
        "LITERATURE_CONSTANT", "DESIGN_ASSUMPTION",
    }
    for p in PARAM_REGISTRY:
        name, value, unit, tag, source, modes, uncertainty = p
        assert len(name) > 0
        assert tag in valid_tags, f"{name} has invalid tag: {tag}"
        assert len(modes) > 0


def test_missing_measured():
    """No parameter should be tagged MEASURED (system not built)."""
    measured = [p[0] for p in PARAM_REGISTRY if p[3] == "MEASURED"]
    assert len(measured) == 0, f"Found MEASURED params: {measured}"
