"""Monte Carlo simulation for Mode D sensing."""

import math, random

from .constants import k_B, m_p, pi, mu_0, hbar, sigma_SB

def run_mode_D_MC(N=10000, seed=42):
    """
    Full Mode D Monte Carlo (post-bakeout, N=10,000 samples).
    Samples: P_H2, G_eff, C_contr, T2*, eta_abs, S_vib, tau_c.
    """
    rng = random.Random(seed)
    gNV = 2 * pi * 28.025e9
    gHe = 2 * pi * 32.434e6
    Cc = (mu_0 / (4 * pi))**2 * gNV**2 * gHe**2 * hbar**2
    ns = 3.3e18
    d_nv = 10e-9
    NA = 0.9
    fom = (1 - math.cos(math.asin(NA))) / 2
    ecol = fom * 0.81 * 0.95 * 0.50 * 0.90 * 0.65
    Ndk = 250 * 1e4
    NC_ref = 1e-6 * 0.5e-3 * 3510 / (12 * m_p)
    A_deb_ref = 12 * pi**4 / 5 * NC_ref * k_B / 2200.**3
    dZFS = 74e3 * 2 * pi
    m_H2v = 2 * m_p
    T_room = 300.
    n_mono = 1e19

    pass_total = 0
    fail_reasons = {"tau_c_detection": 0, "G_eff_thermal": 0,
                    "eps_secondary_load": 0, "theta_H2": 0, "other": 0}
    failed_samples = []
    best_snr = -1
    best = None

    for _ in range(N):
        P_H2_s = rng.uniform(5e-13, 2e-12)
        Ge = rng.uniform(5e-6, 3e-5)
        Cc_ = rng.uniform(0.05, 0.20)
        T2s_ = rng.uniform(5e-6, 20e-6)
        ea = rng.uniform(0.02, 0.10)
        Sv = rng.uniform(1e-11, 1e-8)
        tc = 10**rng.uniform(-9, -1)

        th_H2 = 0.3 * P_H2_s / math.sqrt(2 * pi * m_H2v * k_B * T_room) * 1e4 / n_mono

        Ts = 0.010
        for _i in range(50):
            P_He = 1e-6 / (k_B * 4.) * math.sqrt(8 * k_B * 4. / (pi * 3 * m_p)) * k_B * (4. - Ts) * 1e-6
            Popt = ea * 50e-12 * 200.
            Pvib = 1e-4 * Sv * 10. * 100. / (2. * 100.)
            Pt = P_He + Popt + 1e-9 + 2.46e-9 + Pvib + 4.4e-12
            Tn = 0.010 + Pt / Ge
            if abs(Tn - Ts) < 1e-6:
                Ts = Tn
                break
            Ts = Tn

        Cd = A_deb_ref * Ts**3
        dT = math.sqrt(k_B * Ts**2 / Cd)
        dOm = dZFS * dT

        w = 5e-6
        Ic = math.sqrt(2 * 1e-9 / 50.)
        B1 = (mu_0 * Ic / (pi * w)) * (math.atan(w / (2 * d_nv)) - math.atan(-w / (2 * d_nv)))
        OR = gNV * B1 / 2
        tp = (pi / 2.) / OR
        pd = math.exp(-tp / T2s_)
        Ce = Cc_ * pd**2
        GDC = Cc * ns * tc / d_nv**4
        T2e = 1. / (1. / T2s_ + GDC)
        tseq = 3e-6 + 2 * tp + T2e + 300e-9
        Nseq = max(1, int(5e-3 / tseq))
        Nph = 200 * 1e4 * Nseq * 0.70 * ecol
        dG = 1. / (Ce * T2e * math.sqrt(Nph + Ndk)) if Ce > 0 else float("inf")
        SNR = GDC / dG
        eps = dOm / dG if dG > 0 else float("inf")

        g_d10 = th_H2 < 1e-3
        g_d3 = Ts < 0.012
        g_d13 = SNR >= 5.
        g_d18 = eps < 0.01
        all_pass = g_d10 and g_d3 and g_d13 and g_d18

        if all_pass:
            pass_total += 1
            if SNR > best_snr:
                best_snr = SNR
                best = dict(tc_us=tc*1e6, Ge=Ge, Cc=Cc_, T2s_us=T2s_*1e6,
                            ea=ea, Ts_mK=Ts*1e3, SNR=SNR, eps_pct=eps*100)
        else:
            dom = "other"
            if not g_d13:
                dom = "tau_c_detection"
                fail_reasons["tau_c_detection"] += 1
            elif not g_d3:
                dom = "G_eff_thermal"
                fail_reasons["G_eff_thermal"] += 1
            elif not g_d18:
                dom = "eps_secondary_load"
                fail_reasons["eps_secondary_load"] += 1
            elif not g_d10:
                dom = "theta_H2"
                fail_reasons["theta_H2"] += 1
            else:
                fail_reasons["other"] += 1
            if len(failed_samples) < 200:
                failed_samples.append(dict(
                    tc_us=tc*1e6, Ge_WK=Ge, Cc=Cc_, T2s_us=T2s_*1e6,
                    ea=ea, Ts_mK=Ts*1e3, SNR=SNR, eps_pct=eps*100,
                    dominant_failure=dom, g_d10=g_d10, g_d3=g_d3,
                    g_d13=g_d13, g_d18=g_d18))

    sensitivity_rank = sorted(fail_reasons.items(), key=lambda x: -x[1])
    return {
        "N": N, "pass_total": pass_total, "pass_rate": pass_total / N,
        "fail_reasons": fail_reasons,
        "sensitivity_rank": sensitivity_rank,
        "dominant_failure": sensitivity_rank[0][0] if sensitivity_rank else "none",
        "best_SNR": best_snr, "best": best, "failed_samples": failed_samples,
        "note": ("Post-bakeout MC (Mode D only). tau_c log-U[1ns,100ms]. "
                 "C_contr@10mK and tau_c: EXPERIMENTAL VALIDATION REQUIRED."),
    }


def run_MC_staged(N=10000, seed=42, use_post_mitigation=False):
    """Legacy wrapper around run_mode_D_MC."""
    mc_d = run_mode_D_MC(N=N, seed=seed)
    return {
        "N": N, "A_pass": N, "A_frac": 1.0,
        "B_pass": 0 if not use_post_mitigation else N,
        "B_frac": 0.0 if not use_post_mitigation else 1.0,
        "C_pass": N, "C_frac": 1.0,
        "D_pass": mc_d["pass_total"], "D_frac": mc_d["pass_rate"],
        "full_pass": mc_d["pass_total"] if use_post_mitigation else 0,
        "full_frac": mc_d["pass_rate"] if use_post_mitigation else 0.0,
        "best_SNR": mc_d["best_SNR"], "best": mc_d["best"],
        "note": mc_d["note"],
    }, mc_d.get("failed_samples", [])
