"""Data models for the Quantum Thermal Architecture simulation."""

from dataclasses import dataclass, field
import math

from .constants import (
    k_B, hbar, mu_0, sigma_SB, m_p, pi,
    BLOCKING, VALIDATED,
)

@dataclass
class Gate:
    """A single decision gate in the QTA framework."""
    gid: str
    name: str
    mode: str
    eq: str
    computed: object
    thresh: object
    status: str
    reason: str
    fix: str
    unit: str = ""

    def to_dict(self):
        s = self.status
        if s == "BLOCKED":
            src_direct = "BLOCKED_PREREQUISITE"
        elif s == "UNKNOWN":
            src_direct = "UNKNOWN"
        elif s == "DERIVED_CHECK":
            src_direct = "DERIVED_FIRST_PRINCIPLES"
        else:
            src_direct = "ASSUMED_OR_DESIGN_SPECIFIED"
        return {
            "gate_id": self.gid, "mode": self.mode, "name": self.name,
            "equation": self.eq, "computed": self.computed,
            "threshold": self.thresh, "unit": self.unit,
            "status": s, "reason": self.reason, "fix": self.fix,
            "measured_in_this_system": "false",
            "source_directness": src_direct,
            "can_PASS_now": "NO",
            "required_measurement": "see validation_matrix.csv",
            "blocked_by": "see status_reason" if s == "BLOCKED" else "N/A",
            "notes": "FORECAST_ONLY; can_PASS_now=NO"
        }


@dataclass
class ModeBResult:
    """Mode B (Purge/Reset) result. Mode D can only be constructed from this."""
    bakeout_done: bool = False
    cryotrap_installed: bool = False
    NEG_installed: bool = False
    pump_train_installed: bool = False
    leak_check_pass: bool = False
    RGA_done: bool = False
    RGA_CH4_pass: bool = False
    RGA_H2_pass: bool = False
    all_species_pass: bool = False

    @property
    def RGA_verified(self):
        return self.RGA_done

    def overall_pass(self):
        return (self.bakeout_done and self.cryotrap_installed and
                self.NEG_installed and self.pump_train_installed and
                self.leak_check_pass and self.RGA_done and
                self.RGA_CH4_pass and self.RGA_H2_pass and
                self.all_species_pass)

    def blocking_reasons(self):
        reasons = []
        if not self.bakeout_done:
            reasons.append("Bakeout NOT EXECUTED (250°C/48h on real CF chamber required)")
        if not self.cryotrap_installed:
            reasons.append("77K charcoal cryotrap NOT INSTALLED")
        if not self.NEG_installed:
            reasons.append("SAES NEG NOT INSTALLED")
        if not self.pump_train_installed:
            reasons.append("Pump train NOT INSTALLED")
        if not self.leak_check_pass:
            reasons.append("He leak check NOT PERFORMED")
        if not self.RGA_done:
            reasons.append("RGA measurement NOT PERFORMED")
        if not self.RGA_CH4_pass:
            reasons.append("RGA CH4 not below FC-corrected threshold")
        if not self.RGA_H2_pass:
            reasons.append("RGA H2 not below FC-corrected threshold")
        if not self.all_species_pass:
            reasons.append("RGA all-species not verified")
        return reasons

    def hardware_status_table(self):
        rows = [
            ("Bakeout (250°C/48h)", self.bakeout_done),
            ("77K charcoal cryotrap", self.cryotrap_installed),
            ("SAES NEG pump", self.NEG_installed),
            ("Full pump train", self.pump_train_installed),
            ("He leak check", self.leak_check_pass),
            ("RGA measurement", self.RGA_done),
            ("RGA CH4 threshold", self.RGA_CH4_pass),
            ("RGA H2 threshold", self.RGA_H2_pass),
            ("RGA all-species", self.all_species_pass),
        ]
        for name, done in rows:
            status = VALIDATED if done else BLOCKING
            print(f"    {name:<30} {status}")


CURRENT_MODE_B = ModeBResult()


@dataclass
class ModeStateVector:
    """Self-consistent thermal/mechanical state vector for a mode."""
    mode_name: str
    G_eff_WK: float;    G_eff_tag: str
    eta_abs: float;     E_pulse_J: float;  f_rep_Hz: float
    P_mw_W: float;      P_cond_W: float;   P_lk_W: float
    T_fridge_K: float;  S_vib_m2Hz: float
    n_s_m2: float;      tau_c_s: float;    tau_c_tag: str
    C_contr: float;     T2s_s: float;      d_NV_m: float; w_CPW_m: float
    P_H2_Pa: float;     P_CH4_Pa: float;   P_He_dose_Pa: float
    theta_H2: float = 0.;       theta_CH4: float = 0.
    lambda_He_m: float = 0.;    Kn_He: float = 0.
    P_He_th_W: float = 0.;     P_opt_W: float = 0.
    P_vib_W: float = 0.;       P_rad_W: float = 0.
    P_total_W: float = 0.;     T_sample_K: float = 0.
    T_peak_K: float = 0.;      tau_ballistic_s: float = 0.
    F_fluence: float = 0.
    dOm_opt_static: float = 0.; dOm_mw_static: float = 0.
    dT_thermo_K: float = 0.;   dOm_thermo: float = 0.
    eps_thermo: float = 0.
    B1_T: float = 0.;          Omega_R_rads: float = 0.
    tau_pi2_s: float = 0.;     pd: float = 0.
    C_eff: float = 0.;         T2e_s: float = 0.
    GDC_rads: float = 0.;      SNR: float = 0.
    delta_G_rads: float = 0.
    P_CH4_valve_leak_Pa: float = 0.

    def solve(self):
        m3 = 3 * m_p
        m_H2 = 2 * m_p
        m_CH4_mass = 16 * m_p
        T_room = 300.
        n_mono = 1e19
        s_H2 = 0.3
        s_CH4 = 1.0
        t_meas = 1e4

        self.theta_H2 = s_H2 * self.P_H2_Pa / math.sqrt(2 * pi * m_H2 * k_B * T_room) * t_meas / n_mono
        self.theta_CH4 = s_CH4 * self.P_CH4_Pa / math.sqrt(2 * pi * m_CH4_mass * k_B * T_room) * t_meas / n_mono

        d_He = 2.6e-10
        self.lambda_He_m = k_B * self.T_fridge_K / (math.sqrt(2) * pi * d_He**2 * max(self.P_He_dose_Pa, 1e-30))
        self.Kn_He = self.lambda_He_m / 0.010

        Ts = self.T_fridge_K
        for _ in range(500):
            nHe = max(self.P_He_dose_Pa, 1e-30) / (k_B * 4.0)
            vHe = math.sqrt(8 * k_B * 4.0 / (pi * m3))
            P_He = nHe * vHe * k_B * (4.0 - Ts) * 1e-6
            Popt = self.eta_abs * self.E_pulse_J * self.f_rep_Hz
            Pvib = 1e-4 * self.S_vib_m2Hz * 10. * 100. / (2. * 100.)
            Prad = sigma_SB * 0.10 * 1e-6 * Ts**4
            Pt = P_He + Popt + self.P_mw_W + self.P_cond_W + Pvib + self.P_lk_W + Prad
            Tn = self.T_fridge_K + Pt / self.G_eff_WK
            if abs(Tn - Ts) < 1e-13:
                Ts = Tn
                break
            Ts = Tn

        self.P_He_th_W = P_He
        self.P_opt_W = Popt
        self.P_vib_W = Pvib
        self.P_rad_W = Prad
        self.P_total_W = Pt
        self.T_sample_K = Ts

        V_d = 1e-6 * 0.5e-3
        NC = V_d * 3510 / (12 * m_p)
        A_deb = 12 * pi**4 / 5 * NC * k_B / 2200.**3
        E_abs = self.eta_abs * self.E_pulse_J
        E_lat = 0.544 * E_abs
        self.T_peak_K = (Ts**4 + 4 * E_lat / A_deb)**0.25
        self.tau_ballistic_s = 0.5e-3 / 1.2e4
        self.F_fluence = E_abs / (pi * (361e-9)**2)

        dZFS = 74e3 * 2 * pi
        self.dOm_opt_static = dZFS * (self.P_opt_W / self.G_eff_WK)
        self.dOm_mw_static = dZFS * (self.P_mw_W / self.G_eff_WK)

        Cd = A_deb * Ts**3
        dT = math.sqrt(k_B * Ts**2 / Cd)
        self.dT_thermo_K = dT
        self.dOm_thermo = dZFS * dT

        gNV = 2 * pi * 28.025e9
        gHe = 2 * pi * 32.434e6
        Cc = (mu_0 / (4 * pi))**2 * gNV**2 * gHe**2 * hbar**2

        Icpw = math.sqrt(2 * self.P_mw_W / 50.)
        w = self.w_CPW_m
        d = self.d_NV_m
        self.B1_T = (mu_0 * Icpw / (pi * w)) * (math.atan(w / (2 * d)) - math.atan(-w / (2 * d)))
        self.Omega_R_rads = gNV * self.B1_T / 2.
        self.tau_pi2_s = (pi / 2.) / self.Omega_R_rads
        self.pd = math.exp(-self.tau_pi2_s / self.T2s_s)
        self.C_eff = self.C_contr * self.pd**2

        GDC = Cc * self.n_s_m2 * self.tau_c_s / d**4
        self.GDC_rads = GDC
        self.T2e_s = 1. / (1. / self.T2s_s + GDC)

        NA = 0.9
        fom = (1 - math.cos(math.asin(NA))) / 2
        ecol = fom * 0.81 * 0.95 * 0.50 * 0.90 * 0.65
        Ndk = 250 * 1e4
        tseq = 3e-6 + 2 * self.tau_pi2_s + self.T2e_s + 300e-9
        Nseq = max(1, int(5e-3 / tseq))
        Nph = 200 * 1e4 * Nseq * 0.70 * ecol
        self.delta_G_rads = 1. / (self.C_eff * self.T2e_s * math.sqrt(Nph + Ndk))
        self.SNR = GDC / self.delta_G_rads
        self.eps_thermo = self.dOm_thermo / self.delta_G_rads if self.delta_G_rads > 0 else float('inf')
        self.P_CH4_valve_leak_Pa = 1e-11 / 0.010
        return self


@dataclass
class SystemState:
    """Mode machine state with mutual exclusion enforcement."""
    mode: str
    LCVD_on: bool = False
    precursor_on: bool = False
    He3_dosing_on: bool = False
    He3_present: bool = False
    sensing_on: bool = False
    heat_switch_closed: bool = False
    shutter_closed: bool = False
    cryotrap_active: bool = False
    RGA_pass_CH4: bool = False
    RGA_pass_H2: bool = False
    T_sample_ok: bool = False
    vib_settled: bool = False

    def validate(self):
        assert not (self.LCVD_on and self.sensing_on), "IL-01 LCVD+sensing: 250x thermal overload"
        assert not (self.precursor_on and self.He3_dosing_on), "IL-02 precursor+He3: CH4 destroys He-3 film"
        assert not (self.LCVD_on and self.heat_switch_closed), "IL-03 LCVD+switch_closed: sample heats MC"
        assert not (self.sensing_on and not self.heat_switch_closed), "IL-04 sensing+switch_open: sample not at 10mK"
        assert not (self.sensing_on and not self.RGA_pass_CH4), "IL-05 sensing without RGA_CH4 pass"
        assert not (self.sensing_on and not self.RGA_pass_H2), "IL-06 sensing without RGA_H2 pass"
        assert not (self.sensing_on and not self.T_sample_ok), "IL-07 sensing with T_sample > T_max"
        assert not (self.sensing_on and not self.vib_settled), "IL-08 sensing before vib settled"
        assert not (self.He3_present and self.LCVD_on), "IL-09 He3 present + LCVD on"
        assert not (self.He3_present and self.precursor_on), "IL-10 He3 present + precursor on"


@dataclass
class ChamberState:
    """Hardware installation and contamination state."""
    bakeout_done: bool = False
    cryotrap_installed: bool = False
    NEG_installed: bool = False
    pump_train_installed: bool = False
    leak_check_pass: bool = False
    shutter_stack: bool = False
    labyrinth_installed: bool = False
    nozzle_installed: bool = False
    sinter_fabricated: bool = False
    SC_switch_installed: bool = False
    He4_control_done: bool = False
    RGA_verified: bool = False
    ODMR_10mK_done: bool = False

    @property
    def bakeout_executed(self):
        return self.bakeout_done

    def P_H2_Pa(self):
        if self.bakeout_done and self.NEG_installed:
            return 1e-12
        elif self.bakeout_done:
            return 2e-12
        return 1e-10

    def P_CH4_at_sensing(self, t_purge_s=28800.):
        m_CH4 = 16 * m_p
        T_room = 300.
        P_CH4_work = 1e-4
        S_cryo = 0.795 if self.cryotrap_installed else 0.0
        S_NEG = 0.005 if self.NEG_installed else 0.0
        S_tot = 0.010 + S_cryo + S_NEG + (0.010 if self.pump_train_installed else 0.)
        V_IVC = 1e-3
        tau_p = V_IVC / S_tot
        P_gas = P_CH4_work * math.exp(-t_purge_s / tau_p)
        Q_rate = (1e-11 if self.bakeout_done else 1e-9) * 0.1
        P_outgas = Q_rate / S_tot
        lab_f = 1000. if self.labyrinth_installed else 1.
        shut_f = 100. if self.shutter_stack else 1.
        P_sense = max(P_gas, P_outgas)
        return max(P_sense, P_CH4_work / (lab_f * shut_f) * math.exp(-t_purge_s / tau_p))


CURRENT_CHAMBER = ChamberState()
POST_MITIGATION_CHAMBER = ChamberState(
    bakeout_done=True, cryotrap_installed=True, NEG_installed=True,
    pump_train_installed=True, leak_check_pass=True,
    shutter_stack=True, labyrinth_installed=True, nozzle_installed=True,
    sinter_fabricated=True, SC_switch_installed=True,
    He4_control_done=False, ODMR_10mK_done=False,
)

CHAMBER_STATE = {
    "pre_bakeout": {"P_H2_Pa": 1e-10, "P_CH4_Pa": 1.2e-9,
                    "label": "pre-bakeout (current physical state)"},
    "post_bakeout": {"P_H2_Pa": 1e-12, "P_CH4_Pa": 1.2e-13,
                     "label": "post-bakeout+NEG+cryotrap (required for Mode D)"},
}


def make_A():
    """Mode A: Baseline. LCVD ON, sensing OFF."""
    s = SystemState("MODE_B_PROCESS", LCVD_on=True, precursor_on=True, cryotrap_active=True)
    s.validate()
    return s


def make_B():
    """Mode B -> C transition: Purge/Reset."""
    s = SystemState("MODE_C_PURGE", shutter_closed=True, cryotrap_active=True)
    s.validate()
    return s


def make_C(mode_b_result):
    """Mode C: Recooling. Inherits RGA flags from Mode B."""
    s = SystemState(
        "MODE_C_RECOOL",
        heat_switch_closed=True, shutter_closed=True, cryotrap_active=True,
        RGA_pass_CH4=mode_b_result.RGA_CH4_pass,
        RGA_pass_H2=mode_b_result.RGA_H2_pass,
    )
    s.validate()
    return s


def make_D(mode_b_result):
    """Mode D: Sensing. Raises ValueError if Mode B not passed."""
    if not mode_b_result.overall_pass():
        reasons = mode_b_result.blocking_reasons()
        raise ValueError(
            "Mode D BLOCKED: Mode B has not passed.\n" +
            "\n".join(f"  [BLOCKED] {r}" for r in reasons))
    s = SystemState(
        "MODE_D_SENSE",
        He3_dosing_on=True, He3_present=True, sensing_on=True,
        heat_switch_closed=True, shutter_closed=True, cryotrap_active=True,
        RGA_pass_CH4=mode_b_result.RGA_CH4_pass,
        RGA_pass_H2=mode_b_result.RGA_H2_pass,
        T_sample_ok=True, vib_settled=True,
    )
    s.validate()
    return s


def make_mode_D_state(chamber_cfg=None, tau_c_s=4e-3, tau_c_tag="UNKNOWN"):
    if chamber_cfg is None:
        chamber_cfg = CHAMBER_STATE["post_bakeout"]
    sv = ModeStateVector(
        mode_name="MODE_D_SENSE",
        G_eff_WK=1e-5, G_eff_tag="ASSUMED",
        eta_abs=0.05, E_pulse_J=50e-12, f_rep_Hz=200.,
        P_mw_W=1e-9, P_cond_W=2.46e-9, P_lk_W=4.4e-12,
        T_fridge_K=0.010, S_vib_m2Hz=1e-10,
        n_s_m2=3.3e18, tau_c_s=tau_c_s, tau_c_tag=tau_c_tag,
        C_contr=0.10, T2s_s=10e-6, d_NV_m=10e-9, w_CPW_m=5e-6,
        P_H2_Pa=chamber_cfg["P_H2_Pa"],
        P_CH4_Pa=chamber_cfg["P_CH4_Pa"],
        P_He_dose_Pa=1e-6,
    )
    sv.solve()
    return sv
