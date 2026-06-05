"""Parameter sweeps and sensitivity analysis for QTA."""

import csv, math, json
from pathlib import Path
from .constants import k_B, m_p, pi, mu_0, hbar, sigma_SB
from .model import make_mode_D_state, CHAMBER_STATE
from .monte_carlo import run_mode_D_MC


def sweep_tau_c(output_dir=None):
    """Sweep tau_c and return SNR at each point."""
    from .gates import detection_D
    dc = detection_D()
    points = [1e-9, 1e-8, 1e-7, 27.728e-6, 292e-6, 1e-3, 4e-3, 10e-3, 0.1]
    results = []
    for tc_v in points:
        snr, GDC, T2e, dG, Ns, Nph = dc["snr_tc"](tc_v)
        results.append({
            "tau_c_s": tc_v,
            "tau_c_label": f"{tc_v*1e6:.3f} us" if tc_v < 1 else f"{tc_v:.3f} s",
            "SNR": round(snr, 1),
            "GDC_rads": round(GDC, 1),
            "T2e_us": round(T2e * 1e6, 2),
            "dG_rads": round(dG, 1),
            "pass": snr >= 5,
            "Nseq": Ns,
            "Nph": Nph,
        })
    return results


def sweep_parameter(param_name, values, output=None):
    """Sweep a single parameter and compute resulting T_sample and SNR."""
    results = []
    for v in values:
        kwargs = {"tau_c_s": 4e-3, "tau_c_tag": "SWEEP"}
        if param_name == "G_eff":
            kwargs["G_eff_WK"] = v
        elif param_name == "eta_abs":
            kwargs["eta_abs"] = v
        elif param_name == "P_mw":
            kwargs["P_mw_W"] = v
        elif param_name == "tau_c":
            kwargs["tau_c_s"] = v
        elif param_name == "E_pulse":
            kwargs["E_pulse_J"] = v
        elif param_name == "f_rep":
            kwargs["f_rep_Hz"] = v

        sv = make_mode_D_state(CHAMBER_STATE["post_bakeout"], **kwargs)
        results.append({
            "param": param_name,
            "value": v,
            "T_sample_mK": round(sv.T_sample_K * 1e3, 4),
            "SNR": round(sv.SNR, 1),
            "P_total_pW": round(sv.P_total_W * 1e12, 1),
            "tau_pi2_us": round(sv.tau_pi2_s * 1e6, 3),
            "T2e_us": round(sv.T2e_s * 1e6, 3),
            "Kn_He": round(sv.Kn_He),
        })

    if output:
        path = Path(output)
        with open(path, "w", newline="") as f:
            if results:
                w = csv.DictWriter(f, results[0].keys())
                w.writeheader()
                w.writerows(results)
        return path
    return results


def sensitivity_ranking():
    """Rank parameters by impact on SNR and T_sample using local sensitivity."""
    base = make_mode_D_state(CHAMBER_STATE["post_bakeout"],
                              tau_c_s=4e-3, tau_c_tag="SWEEP")
    base_T = base.T_sample_K
    base_SNR = base.SNR

    perturbations = {
        "G_eff": ("G_eff_WK", 1e-5, 0.5),
        "eta_abs": ("eta_abs", 0.05, 0.5),
        "P_mw": ("P_mw_W", 1e-9, 0.5),
        "tau_c": ("tau_c_s", 4e-3, 0.5),
        "f_rep": ("f_rep_Hz", 200, 0.3),
    }

    ranking = []
    for name, (attr, base_val, frac) in sorted(perturbations.items()):
        delta = base_val * frac
        kwargs_lo = {"tau_c_s": 4e-3, "tau_c_tag": "SWEEP", attr: base_val - delta}
        kwargs_hi = {"tau_c_s": 4e-3, "tau_c_tag": "SWEEP", attr: base_val + delta}
        sv_lo = make_mode_D_state(CHAMBER_STATE["post_bakeout"], **kwargs_lo)
        sv_hi = make_mode_D_state(CHAMBER_STATE["post_bakeout"], **kwargs_hi)
        dT = abs(sv_hi.T_sample_K - sv_lo.T_sample_K) / (2 * delta / base_val) if base_val else 0
        dSNR = abs(sv_hi.SNR - sv_lo.SNR) / (2 * delta / base_val) if base_val else 0
        ranking.append({
            "parameter": name,
            "base_value": base_val,
            "frac_perturbation": frac,
            "dT_dP_norm": round(dT * 1e3, 4),
            "dSNR_dP_norm": round(dSNR, 2),
            "T_lo_mK": round(sv_lo.T_sample_K * 1e3, 4),
            "T_hi_mK": round(sv_hi.T_sample_K * 1e3, 4),
            "SNR_lo": round(sv_lo.SNR, 1),
            "SNR_hi": round(sv_hi.SNR, 1),
        })

    ranking.sort(key=lambda r: -r["dSNR_dP_norm"])
    return ranking
