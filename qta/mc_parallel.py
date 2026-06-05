"""Parallel Monte Carlo simulation using multiprocessing."""

import math
import random
from multiprocessing import Pool, cpu_count
from .constants import k_B, m_p, pi, mu_0, hbar


def _sample_one(args):
    """Run a single MC sample (for parallel map)."""
    seed, params = args
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

    return {
        "pass": all([th_H2 < 1e-3, Ts < 0.012, SNR >= 5., eps < 0.01]),
        "ts_mK": Ts * 1e3,
        "snr": SNR,
        "eps_pct": eps * 100,
        "tc_us": tc * 1e6,
        "ge_wk": Ge,
        "t2s_us": T2s_ * 1e6,
        "ce": Cc_,
        "ea": ea,
    }


def run_parallel_MC(N=10000, processes=None):
    """Run Mode D MC in parallel using multiprocessing."""
    if processes is None:
        processes = max(1, cpu_count() - 1)
    chunk = max(1, N // processes)
    args = [(i, None) for i in range(N)]
    with Pool(processes) as pool:
        results = pool.map(_sample_one, args, chunksize=chunk)

    passed = [r for r in results if r["pass"]]
    failed = [r for r in results if not r["pass"]]

    fail_reasons = {"tau_c_detection": 0, "G_eff_thermal": 0,
                    "eps_secondary_load": 0, "theta_H2": 0, "other": 0}
    for r in failed:
        if r["snr"] < 5:
            fail_reasons["tau_c_detection"] += 1
        elif r["ts_mK"] > 12:
            fail_reasons["G_eff_thermal"] += 1
        elif r["eps_pct"] >= 1:
            fail_reasons["eps_secondary_load"] += 1
        else:
            fail_reasons["other"] += 1

    sensitivity = sorted(fail_reasons.items(), key=lambda x: -x[1])
    best = max(passed, key=lambda r: r["snr"]) if passed else None

    return {
        "N": N,
        "pass_total": len(passed),
        "pass_rate": len(passed) / N,
        "fail_reasons": fail_reasons,
        "sensitivity_rank": sensitivity,
        "dominant_failure": sensitivity[0][0] if sensitivity else "none",
        "best_SNR": best["snr"] if best else 0,
        "best": best,
        "note": "Parallel MC (multiprocessing). Same physics as run_mode_D_MC.",
    }
