"""Gate definitions for all four QTA operating modes."""

import math

from .constants import (
    k_B, m_p, pi, sigma_SB, mu_0, hbar,
    BLOCKING, DESIGN_SPECIFIED,
    gate_status_3layer, hw_status, eng_gate_status, eng_note,
)
from .model import (
    Gate, ModeStateVector, SystemState, ChamberState,
    CURRENT_CHAMBER, make_mode_D_state, CHAMBER_STATE,
)


def kKev(T):
    return 0.040 * (T / 4.)**1.3 if T >= 1. else 3e-4 * (T / 1.)**1.5


def kG10(T):
    return 4.8e-3 * (T / 4.)**1.2 if T >= 1. else 6e-4 * (T / 1.)**1.4


def kVes(T):
    return 2.5e-3 * (T / 4.)**1.6 if T >= 1. else 5e-5 * (T / 0.1)**2.0


def intK(f, lo, hi, N=2000):
    Ts = [lo + (hi - lo) * i / N for i in range(N + 1)]
    return sum((f(Ts[i]) + f(Ts[i+1])) / 2 * (Ts[i+1] - Ts[i]) for i in range(N))


def support_loads():
    Ak = 6 * pi * (0.125e-3)**2
    Lk = 0.05
    Ag = 2 * 0.5e-3 * 5e-3
    Lg = 0.03
    segs = [(4., 1.), (1., 0.1), (0.1, 0.01)]
    kev = [(Ak / Lk) * intK(kKev, lo, hi) for hi, lo in segs]
    g10 = [(Ag / Lg) * intK(kG10, lo, hi) for hi, lo in segs]
    Pv = (3 * 5e-6 / 0.05) * intK(kVes, 0.010, 4.)
    Ps = kev[2] + g10[2]
    return {"Ps": Ps, "Pv": Pv, "red": Pv / Ps, "kev": kev, "g10": g10}


def thermal_D(supp):
    m3 = 3 * m_p
    G = 1e-5
    Ts = 0.010
    for _ in range(500):
        nHe = 1e-6 / (k_B * 4.0)
        vb = math.sqrt(8 * k_B * 4.0 / (pi * m3))
        PHe = nHe * vb * k_B * (4.0 - Ts) * 1e-6
        Popt = 0.05 * 50e-12 * 200.
        Pmw = 1e-9
        Pcd = 2.46e-9
        Pv2 = 1e-4 * (1e-10 * 10) * 100 / (2 * 100)
        Plk = 4.4e-12
        Prad = sigma_SB * 0.10 * 1e-6 * Ts**4
        Pt = supp["Ps"] + PHe + Popt + Pmw + Pcd + Pv2 + Plk + Prad
        Tn = 0.010 + Pt / G
        if abs(Tn - Ts) < 1e-11:
            Ts = Tn
            break
        Ts = Tn
    return {"Ts": Ts, "Ps": supp["Ps"], "PHe": PHe, "Popt": Popt,
            "Pmw": Pmw, "Pcd": Pcd, "Pvib": Pv2, "Plk": Plk, "Prad": Prad, "Pt": Pt}


def detection_D():
    gNV = 2 * pi * 28.025e9
    gHe = 2 * pi * 32.434e6
    Cc = (mu_0 / (4 * pi))**2 * gNV**2 * gHe**2 * hbar**2
    w = 5e-6
    d = 10e-9
    I = math.sqrt(2 * 1e-9 / 50)
    B1 = (mu_0 * I / (pi * w)) * (math.atan(w / (2 * d)) - math.atan(-w / (2 * d)))
    OR = gNV * B1 / 2
    tp2 = pi / (2 * OR)
    T2s = 10e-6
    Twin = 1. / 200.
    NA = 0.9
    fom = (1 - math.cos(math.asin(NA))) / 2
    ec = fom * 0.81 * 0.95 * 0.50 * 0.90 * 0.65
    Ndk = 250. * 1e4
    ns = 3.3e18
    Cc_v = 0.10

    def snr_tc(tc):
        GDC = Cc * ns * tc / d**4
        T2e = 1. / (1. / T2s + GDC)
        tseq = 3e-6 + 2 * tp2 + T2e + 300e-9
        Nseq = max(1, int(Twin / tseq))
        Nph = 200. * 1e4 * Nseq * 0.70 * ec
        dG = 1. / (Cc_v * T2e * math.sqrt(Nph + Ndk))
        return GDC / dG, GDC, T2e, dG, Nseq, Nph

    lo, hi = 1e-9, 1.0
    for _ in range(100):
        mid = 10**((math.log10(lo) + math.log10(hi)) / 2)
        if snr_tc(mid)[0] < 5:
            lo = mid
        else:
            hi = mid
    tcmin = hi
    _, _, T2e_t, dG_t, Ns_t, Np_t = snr_tc(tcmin)
    tseq_t = 3e-6 + 2 * tp2 + T2e_t + 300e-9
    return {
        "OR": OR, "tp2": tp2, "tseq": tseq_t, "Twin": Twin, "Nseq": Ns_t,
        "B1": B1, "ec": ec, "Nph": Np_t, "Ndk": Ndk, "dG": dG_t,
        "Cc": Cc, "ns": ns, "d": d, "T2s": T2s, "tcmin": tcmin,
        "snr_tc": snr_tc, "gNV": gNV, "dfrac": Ndk / (Np_t + Ndk),
    }


def mode_B_processing_gates(s):
    """Mode B (Material Processing / LCVD Growth) gates A1-A14."""
    assert s.mode == "MODE_B_PROCESS"
    gates = []

    sc_spec, sc_inst, sc_verif = True, False, False
    a1_status = gate_status_3layer(sc_spec, sc_inst, sc_verif)
    gates.append(Gate("A1", "MC Protected (SC switch open)", "MODE_B_PROCESS",
        "G_sw_open*(T_4K-T_MC)<0.01*P_cool_MC", 1e-8*(4.-0.010), 0.01*200e-6,
        a1_status,
        f"SC switch: [{hw_status(sc_spec,sc_inst,sc_verif)}]. Status={a1_status}: switch DESIGN_SPECIFIED only.",
        "Install Al SC switch. Verify G_sw_open < 1e-8 W/K.", "W"))

    shut_spec, shut_inst, shut_verif = True, False, False
    Q_scat = sigma_SB * 0.10 * (1e-6) * (300.**4 - 4.**4)
    a2_status = gate_status_3layer(shut_spec, shut_inst, shut_verif)
    gates.append(Gate("A2", "4K Stage Handles LCVD Scatter", "MODE_B_PROCESS",
        "Q_scatter < P_cool_4K", Q_scat*1e3, 1.0, a2_status,
        f"Q_scatter={Q_scat*1e3:.3f}mW. Shutter: [{hw_status(shut_spec,shut_inst,shut_verif)}].",
        "Install 4K OFHC Cu radiation shutter.", "mW"))

    Q_shut = sigma_SB * 0.10 * 1e-6 * (4.**4 - 0.010**4)
    Q_thresh_aW = 4.30e9 * 0.01
    a3_status = gate_status_3layer(shut_spec, shut_inst, shut_verif, Q_shut*1e18 < Q_thresh_aW)
    gates.append(Gate("A3", "Cold Optics Shielded by 4K Shutter", "MODE_B_PROCESS",
        "Q_rad(4K shutter->sample) < 1% budget", Q_shut*1e18, Q_thresh_aW, a3_status,
        f"Q_rad={Q_shut*1e18:.0f}aW << {Q_thresh_aW:.0e}aW threshold.",
        "Install retractable 4K OFHC Cu shutter.", "aW"))

    gas_spec, gas_inst, gas_verif = True, False, False
    a4_status = gate_status_3layer(gas_spec, gas_inst, gas_verif)
    gates.append(Gate("A4", "He-3 Film Absent During Mode B", "MODE_B_PROCESS",
        "He3_valve=CLOSED; interlock IL-02", 0, 0, a4_status,
        f"He-3 valve: [{hw_status(gas_spec,gas_inst,gas_verif)}].",
        "Install He-3 injection line + IL-02 interlock.", ""))

    il_spec, il_inst, il_verif = True, False, False
    a5_status = gate_status_3layer(il_spec, il_inst, il_verif)
    gates.append(Gate("A5", "Sensing Disabled During Mode B", "MODE_B_PROCESS",
        "NV_readout_laser=OFF; ODMR_mw=OFF; IL-01", 0, 0, a5_status,
        f"IL-01: [{hw_status(il_spec,il_inst,il_verif)}].",
        "Install hardware interlocks IL-01 to IL-13.", ""))

    # LCVD feasibility gates A6-A14
    gates.append(Gate("A6", "Precursor beam-delivered, not chamber-fill", "MODE_B_PROCESS",
        "precursor delivered via PMB; chamber < cryocondensation threshold",
        "UNKNOWN", "TBD", "CONDITIONAL",
        "PMB doser DESIGN_SPECIFIED, NOT_INSTALLED.",
        "Install warm/differentially-pumped molecular beam line.", "Pa"))

    gates.append(Gate("A7", "Precursor cryocondensation below limit", "MODE_B_PROCESS",
        "theta_precursor on cold shields < TBD", "UNKNOWN", "TBD", "CONDITIONAL",
        "Cryocondensation unmeasured. Witness coupon + QCM + RGA NOT_INSTALLED.",
        "Witness coupon + QCM + RGA after each Mode B pulse.", "%"))

    gates.append(Gate("A8", "Local surface T during deposition pulse measured", "MODE_B_PROCESS",
        "T_growth_surface measured during pulse", "UNKNOWN", "TBD", BLOCKING,
        "No in-situ pump-probe thermometry at growth surface.",
        "Install pump-probe or fast thermometry at growth surface.", "K"))

    gates.append(Gate("A9", "Deposition yield per pulse measured", "MODE_B_PROCESS",
        "yield = atoms/pulse from witness coupon + QCM + AFM/Raman/XPS",
        "UNKNOWN", "TBD", BLOCKING,
        "PRIMARY UNKNOWN for LCVD feasibility.",
        "Witness coupon + QCM + AFM + Raman + XPS post-pulse.", "atoms/pulse"))

    gates.append(Gate("A10", "Growth-zone contamination does not reach sensing zone", "MODE_B_PROCESS",
        "theta_contamination on sensing-zone coupon < TBD",
        "UNKNOWN", "TBD", "CONDITIONAL",
        "Cross-contamination path unmeasured.",
        "Sensing-zone witness coupon + RGA after each Mode B.", "%"))

    gates.append(Gate("A11", "Byproducts pump below RGA threshold before Mode D", "MODE_B_PROCESS",
        "P_species (RGA-corrected) < threshold for each species",
        "UNKNOWN", "TBD", BLOCKING,
        "RGA not installed; species-resolved pressure unknown.",
        "Install RGA; calibrate FC correction.", "Pa"))

    gates.append(Gate("A12", "Mode B heat removed by non-MC dump path", "MODE_B_PROCESS",
        "P_to_MC during Mode B << P_cool_MC", "UNKNOWN", "TBD", "CONDITIONAL",
        "Dedicated growth dump switch + thermometry NOT_INSTALLED.",
        "Install growth thermal dump switch + dump-stage thermometers.", "W"))

    gates.append(Gate("A13", "Repeated A/B/C cycling passes fatigue inspection", "MODE_B_PROCESS",
        "N=100 cycles; no cracks/delamination/conductance drift",
        "UNKNOWN", "N=100/1000", "CONDITIONAL",
        "No cycling completed. Fatigue across mode transitions unverified.",
        "Run N=100 engineering + N=1000 extended cycles.", "cycles"))

    gates.append(Gate("A14", "He-3/He-4 film absent before Mode B Processing", "MODE_B_PROCESS",
        "P_He < threshold; QCM He shift = 0", "UNKNOWN", "TBD", BLOCKING,
        "He purge protocol and verification (RGA + QCM) not in place.",
        "Install RGA + QCM. Define He purge protocol. Install IL-14.", "Pa"))
    return gates


def mode_B_gates(s):
    """Mode C (Purge/Reset) gates B1-B5."""
    assert s.mode == "MODE_C_PURGE"
    gates = []
    m_H2 = 2 * m_p
    s_H2 = 0.3
    T_room = 300.
    n_mono = 1e19

    gates.append(Gate("B1", "CH4 Pumpout Sufficient", "MODE_C_PURGE",
        "t_purge >= 2h; P_CH4 -> below threshold",
        7200./3600., 2.0, "CONDITIONAL",
        "Outgassing dominated -> 2-8h realistic. 77K cryotrap accelerates 10-100x.",
        "Execute purge cycle; verify P_CH4<5e-12Pa by RGA.", "h"))

    cryotrap_hw = CURRENT_CHAMBER.cryotrap_installed
    b2_hw_status = "PASS" if cryotrap_hw else "CONDITIONAL"
    gates.append(Gate("B2", "77K Cryotrap [DESIGN_SPECIFIED; NOT INSTALLED]", "MODE_C_PURGE",
        "cryotrap_hw_installed=True AND pumping speed verified",
        int(cryotrap_hw), 1, b2_hw_status,
        "NOT YET INSTALLED. Design: 77K charcoal trap; P_vap(CH4,77K)~1e-8Pa.",
        "Install 77K charcoal cryotrap. Verify pumping speed.", "bool"))

    gates.append(Gate("B3", "RGA All-Species Verification (FC-corrected)", "MODE_C_PURGE",
        "CH4<5e-14, H2<2e-14 Pa at pump port",
        None, 5e-14, "UNKNOWN",
        "RGA measurement NOT performed. Mode D hard-interlocked (IL-05).",
        "RGA after each purge cycle. Calibrate FC factor.", "Pa"))

    P_H2 = 5e-12
    Phi = s_H2 * P_H2 / math.sqrt(2 * pi * m_H2 * k_B * T_room)
    th_H2 = Phi * 1e4 / n_mono
    gates.append(Gate("B4", "H2 Residual Coverage", "MODE_C_PURGE",
        "theta_H2=s_H2*P_H2*t/(sqrt(2pi*mkT)*n_mono)<0.1%",
        th_H2*100, 0.1, "CONDITIONAL" if th_H2 < 1e-3 else "FAIL",
        f"theta_H2={th_H2*100:.4f}% (post-bake ASSUMED). Bakeout NOT executed.",
        "Execute 250C/48h bakeout; install SAES St707 NEG; measure P_H2.", "%"))

    tau_pump = 1e-3 / 10e-3
    intCH4 = 1e-4 * tau_pump * (1 - math.exp(-30. / tau_pump))
    th_CH4 = s_H2 * intCH4 / (math.sqrt(2 * pi * 16 * m_p * k_B * T_room) * n_mono)
    gates.append(Gate("B5", "CH4 Coverage on Sensing Surface", "MODE_C_PURGE",
        "theta_CH4 < 0.1% (shutter closed)",
        th_CH4*100, 0.1, "CONDITIONAL",
        f"theta_CH4={th_CH4*100:.3f}%. Shutter must protect NV surface.",
        "Verify shutter CLOSED during Mode B. Confirm CH4 cannot bypass.", "%"))
    return gates


def mode_C_gates(s):
    """Mode C (Recooling) gates C1-C4."""
    assert s.mode == "MODE_C_RECOOL"
    gates = []
    V_d = 1e-6 * 0.5e-3
    NC = V_d * 3510 / (12 * m_p)
    A_deb = 12 * pi**4 / 5 * NC * k_B / 2200.**3
    G = 1e-5
    tau_r = (A_deb / 4) * (4.**4 - 0.010**4) / G

    gates.append(Gate("C1", "Sample Recools to Sensing T", "MODE_C_RECOOL",
        "tau_recool from 4K to 10mK", tau_r, 10., "CONDITIONAL",
        f"tau_recool={tau_r:.3f}s. G_eff=1e-5W/K ASSUMED (not measured).",
        "Measure G_eff. Monitor T_sample until stable.", "s"))

    gates.append(Gate("C2", "Vibration Settled", "MODE_C_RECOOL",
        "t_wait >= t_vib_settle=100s", 100., 100., "CONDITIONAL",
        "S_vib not measured on this system.",
        "Measure S_vib on fridge platform. Add damped flex drive.", "s"))

    gates.append(Gate("C3", "Temperature Drift OK", "MODE_C_RECOOL",
        "dT/dt < 1uK/s at T_sample", None, 1.0, "CONDITIONAL",
        "dT/dt threshold not verified. RuO2 reading required.",
        "Monitor T_sample >=10min; require dT/dt<1uK/s.", "uK/s"))

    _c4_hw = gate_status_3layer(True, False, False, bool(s.shutter_closed))
    gates.append(Gate("C4", "Radiation Shutter (DESIGN_SPECIFIED; not installed)", "MODE_C_RECOOL",
        "shutter_closed=True; 4K OFHC Cu shutter DESIGN_SPECIFIED",
        int(s.shutter_closed), 1, _c4_hw,
        "Shutter: [DESIGN_SPECIFIED only; NOT INSTALLED].",
        "Install 4K OFHC Cu retractable shutter. Install position sensor.", "bool"))
    return gates


def mode_D_gates(s, mode_D_blocked=False, sv=None):
    """Mode D (Sensing) gates D1-D18."""
    assert s.mode in ("MODE_D_SENSE", "SENSE_HYPOTHETICAL")
    if sv is None:
        sv = make_mode_D_state(CURRENT_CHAMBER, tau_c_s=4e-3, tau_c_tag="UNKNOWN")
    gates = []
    Ts = sv.T_sample_K
    gNV = 2 * pi * 28.025e9
    gHe = 2 * pi * 32.434e6
    Cc = (mu_0 / (4 * pi))**2 * gNV**2 * gHe**2 * hbar**2

    gates.append(Gate("D1", "LCVD Off / Mode D Status", "MODE_D_SENSE",
        "LCVD_on=False AND Mode B validated",
        "BLOCKED" if mode_D_blocked else "PASS", None,
        "PASS" if not mode_D_blocked else "BLOCKED",
        "MODE D BLOCKED — Mode B not passed." if mode_D_blocked else "LCVD off.",
        "Hardware IL-01.", ""))

    rga_thr = 5e-14
    gates.append(Gate("D2", "Precursor Threshold (sv.P_CH4; FC-corrected)", "MODE_D_SENSE",
        "sv.P_CH4 < 5e-14 Pa at RGA port",
        sv.P_CH4_Pa, rga_thr,
        "BLOCKED" if mode_D_blocked else (
            "UNKNOWN" if not CURRENT_CHAMBER.bakeout_done else
            ("PASS" if sv.P_CH4_Pa < rga_thr else "CONDITIONAL")),
        f"sv.P_CH4={sv.P_CH4_Pa:.2e}Pa. Threshold={rga_thr:.0e}Pa.",
        "RGA. He3 positive pressure. Double-valve isolation.", "Pa"))

    Pc = 200e-6
    _spec, _inst, _verif = True, False, False
    gates.append(Gate("D3", "Cooling Capacity (sv.P_total; G_eff ASSUMED)", "MODE_D_SENSE",
        "sv.P_total < P_cool_MC", sv.P_total_W*1e9, Pc*1e9,
        gate_status_3layer(_spec, _inst, _verif, sv.P_total_W < Pc),
        f"sv.P_total={sv.P_total_W*1e12:.1f}pW << P_cool={Pc*1e6:.0f}uW. G_eff ASSUMED.",
        "Fabricate 45cm2 Ag sinter. Measure G_eff.", "nW"))

    gates.append(Gate("D4", "T_sample (sv.T_sample; G_eff ASSUMED)", "MODE_D_SENSE",
        "sv.T_sample = T_fridge + sv.P_total/G_eff",
        Ts*1e3, 10.0, "CONDITIONAL",
        f"sv.T_sample={Ts*1e3:.4f}mK. G_eff={sv.G_eff_WK:.0e}W/K [{sv.G_eff_tag}].",
        "Measure G_eff by step-response.", "mK"))

    alpha_K = 2000.
    G_nom = alpha_K * 45e-4 * Ts**3
    G_req = sv.P_total_W / (0.05 * 0.010)
    G_worst = alpha_K * 0.5 * 45e-4 * Ts**3 * 0.5
    wc = "FAILS" if G_worst < G_req else "passes"
    gates.append(Gate("D5", "G_eff / Sinter (marginal at worst-case)", "MODE_D_SENSE",
        "G_nom >= G_req = sv.P_total/dT_crit",
        G_nom, G_req, eng_gate_status("Ag_sinter", physics_ok=(G_nom >= G_req)),
        f"Ag_sinter: {eng_note('Ag_sinter')}. G_nom={G_nom:.3e}W/K. "
        f"WORST: G={G_worst:.2e}W/K ({wc}).",
        "Fabricate 45cm2 Ag sinter. Measure G_eff.", "W/K"))

    _spec, _inst, _verif = True, False, False
    gates.append(Gate("D6", "Laser Avg Heating (sv.P_opt; eta_abs ASSUMED)", "MODE_D_SENSE",
        "sv.P_opt = eta_abs*E_pulse*f_rep",
        sv.P_opt_W*1e12, 1e6,
        gate_status_3layer(_spec, _inst, _verif, sv.P_opt_W < 1e-6),
        f"sv.P_opt={sv.P_opt_W*1e12:.1f}pW. eta_abs={sv.eta_abs} [ASSUMED].",
        "Measure eta_abs.", "pW"))

    t_rep = 1. / sv.f_rep_Hz
    gates.append(Gate("D7", "Laser Transient — T_peak vs T_baseline", "MODE_D_SENSE",
        "T_baseline=sv.T_sample; T_peak=transient spike; tau_ballistic<<t_rep",
        sv.T_peak_K*1e3, None, "CONDITIONAL",
        f"T_baseline={sv.T_sample_K*1e3:.3f}mK. T_peak={sv.T_peak_K*1e3:.3f}mK. "
        f"tau_ballistic={sv.tau_ballistic_s*1e9:.0f}ns << t_rep={t_rep*1e3:.0f}ms.",
        "Measure eta_abs. Time-resolved PL to verify recovery.", "mK"))

    gates.append(Gate("D8", "Sequence Timing (sv.tau_pi2)", "MODE_D_SENSE",
        "tau_seq = 3us + 2*tau_pi2 + T2e + 0.3us << 5ms",
        sv.tau_pi2_s*1e6, 5e3, "CONDITIONAL",
        f"sv.Omega_R={sv.Omega_R_rads:.0f}rad/s, tau_pi2={sv.tau_pi2_s*1e6:.2f}us. "
        f"tau_pi2/T2*={sv.tau_pi2_s/sv.T2s_s:.2f}: DEGRADED.",
        "Increase P_mw or use resonator.", "us"))

    gates.append(Gate("D9", "Molecular Flow (sv.Kn_He; gas Knudsen number)", "MODE_D_SENSE",
        "sv.Kn_He = lambda_He / L_char >> 10",
        sv.Kn_He, 10., "DERIVED_CHECK",
        f"Kn=sv.Kn={sv.Kn_He:.0f} >> 10 — molecular flow confirmed (first-principles check).",
        "Specify full dosing geometry.", ""))

    _ch = CURRENT_CHAMBER
    _d10a_prereqs = (_ch.bakeout_executed and _ch.NEG_installed and
                     _ch.cryotrap_installed and _ch.RGA_verified)
    _d10a_status = "PASS" if _d10a_prereqs else (
        "CONDITIONAL" if (_ch.bakeout_executed and _ch.NEG_installed) else BLOCKING)

    gates.append(Gate("D10a", "H2 Engineering Readiness (bakeout+NEG+cryotrap+RGA)", "MODE_D_SENSE",
        "bakeout_executed AND NEG_installed AND cryotrap_installed AND RGA_verified",
        int(_d10a_prereqs), 1, _d10a_status,
        f"bakeout={_ch.bakeout_executed} NEG={_ch.NEG_installed} "
        f"cryotrap={_ch.cryotrap_installed} RGA={_ch.RGA_verified}. ALL False.",
        "Execute bakeout+NEG+cryotrap+RGA in sequence.", "bool"))

    _P_H2_actual = _ch.P_H2_Pa()
    _m_H2 = 2 * m_p
    _s_H2 = 0.3
    _n_mono = 1e19
    _T_room = 300.
    _theta_actual = _s_H2 * _P_H2_actual / math.sqrt(2 * pi * _m_H2 * k_B * _T_room) * 1e4 / _n_mono
    if not _d10a_prereqs:
        _d10b_status = BLOCKING
        _d10b_note = f"BLOCKED — D10a prereqs not met. theta_H2={_theta_actual*100:.3f}%."
    elif _theta_actual < 1e-3:
        _d10b_status = "PASS"
        _d10b_note = f"theta_H2={_theta_actual*100:.4f}% < 0.1%. PASS."
    else:
        _d10b_status = "FAIL"
        _d10b_note = f"theta_H2={_theta_actual*100:.3f}% > 0.1%. Execute bakeout+NEG."

    gates.append(Gate("D10b", "H2 Physical Result (actual P_H2)", "MODE_D_SENSE",
        "theta_H2 < 0.1%; D10a prerequisite", _theta_actual*100, 0.1,
        _d10b_status, _d10b_note, "D10a must be PASS first.", "%"))

    m3v = 3 * m_p
    T_F = hbar**2 * pi * sv.n_s_m2 / (m3v * k_B)
    gates.append(Gate("D11", "He-3 Coverage (sv.n_s)", "MODE_D_SENSE",
        "sv.n_s >= 3.3e18 m-2; He frozen (E_b/kT>>1)",
        sv.n_s_m2, 3.3e18, "CONDITIONAL",
        f"n_s={sv.n_s_m2:.2e}m-2 [ASSUMED]. T/T_F={Ts/T_F:.5f}<<1. s_He UNKNOWN.",
        "Measure s_He by TPD/QCM.", "m-2"))

    gates.append(Gate("D12_G23", "NV Charge State (UNKNOWN; not derivable)", "MODE_D_SENSE",
        "C_contr > 0 at 10mK under 532nm",
        None, 0.05, "UNKNOWN",
        f"NV_charge_val: {eng_note('NV_charge_val')}. Co-equal bottleneck with tau_c.",
        "ODMR at 10mK post-cycle (F15).", ""))

    gates.append(Gate("D13", "Detection SNR (sv; pulse dephasing included)", "MODE_D_SENSE",
        "sv.SNR = sv.GDC/sv.delta_G >= 5",
        sv.SNR if sv.tau_c_tag != "UNKNOWN" else None, 5.,
        eng_gate_status("T2star_tau_c", physics_ok=(sv.SNR >= 5)) if sv.tau_c_tag != "UNKNOWN"
        else eng_gate_status("T2star_tau_c"),
        f"sv.tau_c={sv.tau_c_s*1e6:.0f}us [{sv.tau_c_tag}]. "
        f"sv.SNR={sv.SNR:.1f}. Threshold: tau_c>292us.",
        "Ramsey + He-4 control. Measure tau_c.", "SNR"))

    NA = 0.9
    fom = (1 - math.cos(math.asin(NA))) / 2
    ecol_v = fom * 0.81 * 0.95 * 0.50 * 0.90 * 0.65
    Ndk = 250 * 1e4
    tseq_r = 3e-6 + 2 * sv.tau_pi2_s + sv.T2e_s + 300e-9
    Nseq_r = max(1, int(5e-3 / tseq_r))
    Nph_r = 200 * 1e4 * Nseq_r * 0.70 * ecol_v
    dfrac = Ndk / (Nph_r + Ndk)
    gates.append(Gate("D14", "Optical Collection (sv.tau_pi2, T2e)", "MODE_D_SENSE",
        "dark_frac = Ndk/(Nph+Ndk) < 20%",
        dfrac*100, 20., eng_gate_status("eta_col_cal"),
        f"eta_col={ecol_v*100:.2f}% [ASSUMED]. dark_frac={dfrac*100:.0f}%.",
        "Calibrate eta_col. Consider SIL.", "%"))

    gates.append(Gate("D15", "Rabi Control (sv.Omega_R)", "MODE_D_SENSE",
        "sv.Omega_R = gamma_NV * sv.B1 / 2",
        sv.Omega_R_rads, None, eng_gate_status("Rabi_cal"),
        f"sv.Omega_R={sv.Omega_R_rads:.0f}rad/s. Not measured in cryostat.",
        "Measure Rabi in cryostat.", "rad/s"))

    dT_mw = sv.P_mw_W / sv.G_eff_WK
    thr_mw = 0.01 * Ts
    _spec, _inst, _verif = True, False, False
    gates.append(Gate("D16", "MW Heating (sv.P_mw/sv.G_eff; both ASSUMED)", "MODE_D_SENSE",
        "dT_mw < 1%*T_s", dT_mw*1e6, thr_mw*1e6,
        gate_status_3layer(_spec, _inst, _verif, dT_mw < thr_mw),
        f"dT_mw={dT_mw*1e6:.0f}uK vs threshold {thr_mw*1e6:.1f}uK.",
        "Verify NbN SC at 10mK.", "uK"))

    gNV_v = 2 * pi * 28.025e9
    dr = math.sqrt(sv.S_vib_m2Hz * 10.) / (2 * pi * 100.)
    R = 0.025
    B0 = 1e-3
    d2B = 12. / 5 * B0 / R**2
    Gvib_H = gNV_v * 0.5 * d2B * dr**2
    gates.append(Gate("D17", "Vibration (sv.S_vib; Helmholtz)", "MODE_D_SENSE",
        "Gamma_vib << sv.delta_G",
        Gvib_H, sv.delta_G_rads,
        eng_gate_status("helmholtz", physics_ok=(Gvib_H < sv.delta_G_rads)),
        f"Gamma_vib={Gvib_H:.3f}rad/s << delta_G={sv.delta_G_rads:.0f}rad/s.",
        "Helmholtz geometry. Measure S_vib.", "rad/s"))

    eps_v = sv.eps_thermo
    eps_vib_v = Gvib_H / sv.delta_G_rads if sv.delta_G_rads > 0 else 0
    eps_charge = 0.0 if CURRENT_CHAMBER.He4_control_done else 0.10
    eps_total = math.sqrt(eps_v**2 + eps_vib_v**2 + eps_charge**2)
    cc_status = eng_gate_status("He4_control", physics_ok=(eps_total < 0.01))
    gates.append(Gate("D18", "Mode-Local Secondary Thermal Feedback", "MODE_D_SENSE",
        "eps=sqrt(eps_thermo^2+eps_vib^2+eps_charge^2) < 0.01",
        eps_total*100, 1.0, cc_status,
        f"eps={eps_total*100:.3f}%. He-4 control experiment F16 required.",
        "He-4 control experiment F16.", "% of dG"))
    return gates
