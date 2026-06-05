"""Tests for the data models."""

import math
from qta.model import (
    Gate, ModeBResult, ModeStateVector, SystemState,
    ChamberState, CURRENT_CHAMBER,
    make_A, make_B, make_C, make_D, make_mode_D_state,
)


def test_gate_to_dict():
    """Gate.to_dict() must include required fields."""
    g = Gate("T1", "Test Gate", "MODE_D_SENSE",
             "x > 0", 5.0, 3.0, "PASS", "test", "fix it", "unit")
    d = g.to_dict()
    assert d["gate_id"] == "T1"
    assert d["status"] == "PASS"
    assert d["can_PASS_now"] == "NO"
    assert d["measured_in_this_system"] == "false"


def test_gate_blocked_source_directness():
    """BLOCKED gates get BLOCKED_PREREQUISITE source directness."""
    g = Gate("B", "Blocked", "mode", "eq", 0, 1, "BLOCKED", "blocked", "fix")
    assert g.to_dict()["source_directness"] == "BLOCKED_PREREQUISITE"


def test_mode_b_result_defaults():
    """Mode B result defaults to all False (nothing executed)."""
    mb = ModeBResult()
    assert not mb.overall_pass()
    assert len(mb.blocking_reasons()) == 9


def test_mode_b_result_full_pass():
    """When all tasks complete, overall_pass should be True."""
    mb = ModeBResult(
        bakeout_done=True, cryotrap_installed=True, NEG_installed=True,
        pump_train_installed=True, leak_check_pass=True, RGA_done=True,
        RGA_CH4_pass=True, RGA_H2_pass=True, all_species_pass=True,
    )
    assert mb.overall_pass()
    assert mb.RGA_verified


def test_system_state_validate():
    """System state enforces hard interlocks."""
    bad = SystemState("X", LCVD_on=True, sensing_on=True)
    try:
        bad.validate()
        assert False, "Should have raised AssertionError"
    except AssertionError:
        pass


def test_mode_a_construction():
    """Mode A should construct without error."""
    s = make_A()
    assert s.mode == "MODE_B_PROCESS"
    assert s.LCVD_on


def test_mode_b_construction():
    """Mode B (purge) should construct."""
    s = make_B()
    assert s.mode == "MODE_C_PURGE"


def test_mode_c_construction():
    """Mode C inherits RGA flags from Mode B result."""
    mb = ModeBResult()
    s = make_C(mb)
    assert s.mode == "MODE_C_RECOOL"
    assert not s.RGA_pass_CH4


def test_mode_d_blocked():
    """Mode D should raise ValueError when Mode B not passed."""
    mb = ModeBResult()
    try:
        make_D(mb)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_mode_state_vector_solve():
    """ModeStateVector.solve() should produce reasonable values."""
    sv = make_mode_D_state(tau_c_s=4e-3, tau_c_tag="ASSUMED")
    assert 0.010 < sv.T_sample_K < 0.020
    assert sv.Kn_He > 10  # molecular flow
    assert sv.SNR > 0
    assert sv.tau_pi2_s > 0
    assert sv.Omega_R_rads > 0


def test_chamber_state_pressure():
    """Pre-bakeout chamber should have high H2 pressure."""
    ch = ChamberState()
    assert ch.P_H2_Pa() > 1e-11  # high pre-bakeout pressure

    ch_clean = ChamberState(bakeout_done=True, NEG_installed=True)
    assert ch_clean.P_H2_Pa() < 5e-12  # low post-bakeout pressure


def test_current_chamber_defaults():
    """CURRENT_CHAMBER should be all False."""
    assert not CURRENT_CHAMBER.bakeout_done
    assert not CURRENT_CHAMBER.NEG_installed
