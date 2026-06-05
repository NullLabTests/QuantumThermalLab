"""Edge-case tests for models."""

import math
import pytest
from qta.model import (
    Gate, ModeStateVector, SystemState, ChamberState,
    ModeBResult, make_mode_D_state, make_D, CHAMBER_STATE,
)


def test_gate_with_none_values():
    """Gate handles None computed/thresh values."""
    g = Gate("N1", "None Test", "D", "x > y", None, None, "UNKNOWN", "no data", "measure")
    assert g.computed is None
    assert g.thresh is None
    d = g.to_dict()
    assert d["source_directness"] == "UNKNOWN"


def test_gate_numeric_threshold():
    """Gate with numeric threshold works."""
    g = Gate("N2", "Num", "D", "x", 5.0, 3.0, "PASS", "ok", "")
    assert g.computed > g.thresh


def test_mode_state_vector_zero_limits():
    """ModeStateVector handles extreme inputs without crashing."""
    sv = ModeStateVector(
        mode_name="TEST",
        G_eff_WK=1e-5, G_eff_tag="ASSUMED",
        eta_abs=0.0, E_pulse_J=0, f_rep_Hz=0,
        P_mw_W=0, P_cond_W=0, P_lk_W=0,
        T_fridge_K=0.010, S_vib_m2Hz=0,
        n_s_m2=0, tau_c_s=0, tau_c_tag="ASSUMED",
        C_contr=0, T2s_s=1e-6, d_NV_m=10e-9, w_CPW_m=5e-6,
        P_H2_Pa=0, P_CH4_Pa=1e-12, P_He_dose_Pa=0,
    )
    sv.solve()
    assert sv.T_sample_K > 0
    assert sv.SNR == 0  # ns=0, tau_c=0 -> GDC=0


def test_mode_state_vector_high_power():
    """High power leads to higher T_sample."""
    sv_low = make_mode_D_state(CHAMBER_STATE["post_bakeout"], tau_c_s=4e-3, tau_c_tag="TEST")
    sv_high = ModeStateVector(
        mode_name="TEST",
        G_eff_WK=1e-5, G_eff_tag="ASSUMED",
        eta_abs=0.5, E_pulse_J=500e-12, f_rep_Hz=2000,
        P_mw_W=1e-6, P_cond_W=2.46e-7, P_lk_W=4.4e-10,
        T_fridge_K=0.010, S_vib_m2Hz=1e-8,
        n_s_m2=3.3e18, tau_c_s=4e-3, tau_c_tag="TEST",
        C_contr=0.10, T2s_s=10e-6, d_NV_m=10e-9, w_CPW_m=5e-6,
        P_H2_Pa=1e-10, P_CH4_Pa=1.2e-9, P_He_dose_Pa=1e-6,
    )
    sv_high.solve()
    assert sv_high.T_sample_K > sv_low.T_sample_K
    assert sv_high.P_total_W > sv_low.P_total_W


def test_system_state_validate_all_ok():
    """Valid state passes all interlocks."""
    s = SystemState(
        "TEST", LCVD_on=False, sensing_on=False,
        heat_switch_closed=True, shutter_closed=True,
        cryotrap_active=True, RGA_pass_CH4=True, RGA_pass_H2=True,
        T_sample_ok=True, vib_settled=True,
    )
    s.validate()  # should not raise


@pytest.mark.parametrize("bad_kwargs,expected_msg", [
    ({"LCVD_on": True, "sensing_on": True}, "IL-01"),
    ({"precursor_on": True, "He3_dosing_on": True}, "IL-02"),
    ({"LCVD_on": True, "heat_switch_closed": True}, "IL-03"),
    ({"sensing_on": True, "heat_switch_closed": False}, "IL-04"),
    ({"sensing_on": True, "RGA_pass_CH4": False}, "IL-05"),
])
def test_system_state_validate_interlocks(bad_kwargs, expected_msg):
    """Each specific interlock violation raises the right error."""
    kwargs = dict(LCVD_on=False, sensing_on=False, heat_switch_closed=True,
                  shutter_closed=True, cryotrap_active=True,
                  RGA_pass_CH4=True, RGA_pass_H2=True,
                  T_sample_ok=True, vib_settled=True)
    kwargs.update(bad_kwargs)
    s = SystemState("TEST", **kwargs)
    with pytest.raises(AssertionError) as exc:
        s.validate()
    assert expected_msg in str(exc.value)


def test_chamber_state_extremes():
    """Chamber state handles extreme conditions."""
    ch = ChamberState()
    assert ch.P_H2_Pa() > 0
    
    ch_all_ok = ChamberState(
        bakeout_done=True, cryotrap_installed=True, NEG_installed=True,
        pump_train_installed=True, leak_check_pass=True,
        shutter_stack=True, labyrinth_installed=True,
    )
    assert ch_all_ok.P_H2_Pa() < 5e-12
    assert ch_all_ok.P_CH4_at_sensing() > 0


def test_mode_b_result_partial():
    """Partial Mode B result reports proper blocking reasons."""
    mb = ModeBResult(bakeout_done=True, cryotrap_installed=True)
    assert not mb.overall_pass()
    reasons = mb.blocking_reasons()
    assert len(reasons) == 7  # 9 total - 2 done


def test_make_mode_D_state_uses_chamber():
    """make_mode_D_state accepts custom chamber config."""
    sv = make_mode_D_state(tau_c_s=4e-3, tau_c_tag="TEST")
    assert sv.P_H2_Pa == 1e-12
    # pre-bakeout has higher pressure
    sv2 = make_mode_D_state(CHAMBER_STATE["pre_bakeout"], tau_c_s=4e-3, tau_c_tag="TEST")
    assert sv2.P_H2_Pa > sv.P_H2_Pa
