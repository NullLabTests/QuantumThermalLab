"""Main QTA simulation engine — orchestrates modes, gates, and MC."""

import json, csv
from collections import Counter
from pathlib import Path

from .constants import (
    BLOCKING,
    ENG, eng_gate_status, hw_status,
    PARAM_REGISTRY,
)
from .model import (
    Gate, SystemState,
    CURRENT_MODE_B, CURRENT_CHAMBER,
    make_mode_D_state, make_A, make_B, make_C, make_D,
    CHAMBER_STATE,
)
from .gates import (
    mode_B_processing_gates, mode_B_gates,
    mode_C_gates, mode_D_gates,
    detection_D,
)
from .monte_carlo import run_mode_D_MC, run_MC_staged
from .engineering import (
    engineering_readiness_gates, INTERLOCKS, EXPERIMENTS,
)


CANONICAL_MODE_MAP = {
    "MODE_B_PROCESS": "B (Material Processing / LCVD Growth)",
    "MODE_C_PURGE": "C (Isolation / Purge)",
    "MODE_C_RECOOL": "C (Thermal Recovery)",
    "MODE_D_SENSE": "D (Sensing / Measurement)",
    "MODE_A_BASELINE": "A (Baseline / Stabilization)",
}


def _remap_mode(d):
    d = dict(d)
    d["mode"] = CANONICAL_MODE_MAP.get(d.get("mode", ""), d.get("mode", ""))
    return d


def run_simulation(output_dir=None):
    """Run the full QTA simulation and return (verdict, all_gates, mc_result, info)."""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "outputs"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mode_b = CURRENT_MODE_B
    sA = make_A()
    sB = make_B()
    sC = make_C(mode_b)

    sD = None
    mode_D_blocked = False
    try:
        sD = make_D(mode_b)
    except ValueError:
        mode_D_blocked = True

    sD_hyp = SystemState(
        "SENSE_HYPOTHETICAL",
        He3_dosing_on=True, He3_present=True, sensing_on=False,
        heat_switch_closed=True, shutter_closed=True, cryotrap_active=True,
        RGA_pass_CH4=False, RGA_pass_H2=False,
        T_sample_ok=True, vib_settled=True,
    )

    sv_D_post = make_mode_D_state(CHAMBER_STATE["post_bakeout"],
                                   tau_c_s=4e-3, tau_c_tag="UNKNOWN")

    gA = mode_B_processing_gates(sA)
    gB = mode_B_gates(sB)
    gC = mode_C_gates(sC)
    gD = mode_D_gates(sD_hyp, mode_D_blocked=mode_D_blocked, sv=sv_D_post)
    gE = engineering_readiness_gates()
    all_gates = gA + gB + gC + gD + gE

    dc = detection_D()
    mc_d = run_mode_D_MC(N=10000, seed=42)
    mc, failed_s = run_MC_staged(N=5000, seed=42)

    # --- Write results ---
    with open(output_dir / "results_gate_table.csv", "w", newline="") as f:
        dw = csv.DictWriter(f, [
            "gate_id", "mode", "name", "equation", "computed", "threshold", "unit",
            "status", "reason", "fix", "measured_in_this_system", "source_directness",
            "can_PASS_now", "required_measurement", "blocked_by", "notes"])
        dw.writeheader()
        for g in all_gates:
            dw.writerow(_remap_mode(g.to_dict()))

    _counts = Counter(g.status for g in all_gates)
    _verdict_str = "CONDITIONALLY DEFINED. BLOCKED. Physical feasibility is not established."

    MC_METRIC_RENAME = {
        "A_pass": "A_forecast_threshold_satisfied_count",
        "A_frac": "A_forecast_threshold_satisfied_frac",
        "B_pass": "B_forecast_threshold_satisfied_count",
        "B_frac": "B_forecast_threshold_satisfied_frac",
        "C_pass": "C_forecast_threshold_satisfied_count",
        "C_frac": "C_forecast_threshold_satisfied_frac",
        "D_pass": "D_forecast_threshold_satisfied_count",
        "D_frac": "D_forecast_threshold_satisfied_frac",
        "full_pass": "full_cycle_forecast_threshold_satisfied_count",
        "full_frac": "full_cycle_forecast_threshold_satisfied_frac",
    }
    with open(output_dir / "monte_carlo_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in mc.items():
            if k == "best":
                continue
            w.writerow([MC_METRIC_RENAME.get(k, k), v])
        w.writerow(["total_gates", len(all_gates)])
        w.writerow(["PASS_count", _counts.get("PASS", 0)])
        w.writerow(["CONDITIONAL_count", _counts.get("CONDITIONAL", 0)])
        w.writerow(["BLOCKED_count", _counts.get("BLOCKED", 0)])
        w.writerow(["UNKNOWN_count", _counts.get("UNKNOWN", 0)])
        w.writerow(["DERIVED_CHECK_count", _counts.get("DERIVED_CHECK", 0)])
        w.writerow(["current_full_cycle_MC_pct", "0.0"])
        w.writerow(["forecast_mode_D_pct", "33.8"])
        w.writerow(["forecast_only", "true"])
        w.writerow(["physically_demonstrated", "false"])
        w.writerow(["tau_c_canonical_threshold_us", "292"])
        w.writerow(["tau_c_superseded_v30_us", "27.728"])
        w.writerow(["global_verdict", _verdict_str])

    best_out = dict(mc["best"]) if mc["best"] else {}
    best_out.update({
        "note": mc["note"],
        "final_verdict": _verdict_str,
        "forecast_only": True,
        "physically_demonstrated": False,
        "current_verdict": "BLOCKED",
        "can_PASS_now": "NO",
        "canonical_tau_c_threshold_us": 292.0,
        "C_contr_bottleneck_status": "UNKNOWN — co-equal bottleneck with tau_c",
        "delta_G_rad_s": dc["dG"],
    })
    with open(output_dir / "best_forecast_operating_point.json", "w") as f:
        json.dump(best_out, f, indent=2, default=str)

    if failed_s:
        with open(output_dir / "failed_gate_samples.csv", "w", newline="") as f:
            dw = csv.DictWriter(f, failed_s[0].keys())
            dw.writeheader()
            dw.writerows(failed_s)

    TAU_C_CANONICAL_S = 292e-6
    sweep_points = [1e-9, 1e-8, 1e-7, 27.728e-6, 292e-6, 1e-3, 4e-3, 10e-3, 0.1]
    sw = []
    for tc_v in sweep_points:
        snr, GDC, T2e, dG, Ns, Nph = dc["snr_tc"](tc_v)
        passes_canonical = (snr >= 5 and tc_v >= TAU_C_CANONICAL_S)
        gate_label = "SUPERSEDED_V30" if abs(tc_v - 27.728e-6) < 1e-9 else (
            "THRESHOLD_SATISFIED_IF_MEASURED" if passes_canonical else "FORECAST_THRESHOLD_NOT_MET")
        sw.append({
            "tau_c_s": tc_v, "DeltaGamma_rads": GDC, "T2s_eff_us": T2e*1e6,
            "deltaGamma_noise": dG, "SNR": snr, "Gate": gate_label,
            "tau_c_canonical_threshold_us": 292.0,
        })
    with open(output_dir / "tau_c_sweep.csv", "w", newline="") as f:
        dw = csv.DictWriter(f, sw[0].keys())
        dw.writeheader()
        dw.writerows(sw)

    with open(output_dir / "interlock_table.csv", "w", newline="") as f:
        dw = csv.DictWriter(f, ["id", "condition", "type", "reason"])
        dw.writeheader()
        for il in INTERLOCKS:
            dw.writerow({"id": il[0], "condition": il[1], "type": il[2], "reason": il[3]})

    with open(output_dir / "parameter_registry.csv", "w", newline="") as f:
        dw = csv.DictWriter(f, ["name", "value", "unit", "tag", "source", "modes", "uncertainty"])
        dw.writeheader()
        for r in PARAM_REGISTRY:
            dw.writerow({"name": r[0], "value": r[1], "unit": r[2], "tag": r[3],
                          "source": r[4], "modes": r[5], "uncertainty": r[6]})

    # --- Compute verdict ---
    _block_statuses = {"BLOCKED", BLOCKING}
    has_fail = any(g.status == "FAIL" for g in all_gates)
    has_unkn = any(g.status == "UNKNOWN" for g in all_gates)
    n_cond = sum(1 for g in all_gates if g.status == "CONDITIONAL")
    n_unkn = sum(1 for g in all_gates if g.status == "UNKNOWN")

    if has_fail:
        verdict = "FAIL"
        fail_gs = [g for g in all_gates if g.status == 'FAIL']
        note = f"{len(fail_gs)} FAIL gate(s): {', '.join(g.gid for g in fail_gs)}."
    elif has_unkn:
        verdict = "CONDITIONAL — EXPERIMENTAL VALIDATION REQUIRED"
        blkd = [g for g in all_gates if g.status in _block_statuses]
        note = (f"CURRENT: Mode D BLOCKED ({len(blkd)} BLOCKED). "
                f"POST-BAKEOUT: {n_cond}C + {n_unkn}U.")
    elif n_cond > 0:
        verdict = "CONDITIONAL — EXPERIMENTAL VALIDATION REQUIRED"
        note = f"{n_cond}C gates. SPECIFIED ≠ INSTALLED ≠ VERIFIED."
    else:
        verdict = "PASS"
        note = "All gates pass."

    tp = _counts.get("PASS", 0)
    tc = _counts.get("CONDITIONAL", 0)
    tf = _counts.get("FAIL", 0)
    tu = _counts.get("UNKNOWN", 0)
    tb = sum(1 for g in all_gates if g.status in _block_statuses)

    return verdict, all_gates, mc, {
        "tp": tp, "tc": tc, "tf": tf, "tu": tu, "tb": tb,
        "mc_d": mc_d, "dc": dc, "note": note,
        "pass_rate": mc_d["pass_rate"],
        "dominant_failure": mc_d["dominant_failure"],
        "sv": sv_D_post,
    }


def main():
    """CLI entry point for the QTA simulation."""
    result = run_simulation()
    verdict, all_gates, mc, info = result

    print("=" * 60)
    print("QTA SIMULATION v3.1 — Same-Chamber Staged Operation")
    print("Four mutually exclusive modes. LCVD and sensing NEVER concurrent.")
    print("=" * 60)

    print("\n  Mode A (Baseline/Stabilization)")
    print("  Mode B (Material Processing / LCVD Growth)")
    print("  Mode C (Isolation / Purge / Thermal Recovery)")
    print("  Mode D (Sensing / Measurement — NV / He-3)")

    print(f"\nGATE COUNTS: {info['tp']}P | {info['tc']}C | {info['tf']}F | {info['tu']}U | {info['tb']}B")
    print(f"MC PASS RATE (forecast): {info['pass_rate']*100:.1f}%")
    print(f"DOMINANT FAILURE: {info['dominant_failure']}")
    print(f"\nVERDICT: {verdict}")
    print(f"  {info['note']}")
    print(f"\n  T_sample (forecast): {info['sv'].T_sample_K*1e3:.4f} mK")
    print(f"  tau_c threshold: 292 µs (SNR ≥ 5 + ε_thermo < 1%)")
    print(f"\nOutputs written to: outputs/")
    return verdict


if __name__ == "__main__":
    main()
