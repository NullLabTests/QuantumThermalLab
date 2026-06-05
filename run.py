#!/usr/bin/env python3
"""
QTA Simulation — Quantum Thermal Architecture Toolkit.

Usage:
    python run.py                        # full simulation + dashboard
    python run.py bottleneck             # bottleneck analysis
    python run.py report [--output FILE] # HTML report
    python run.py sweep [--out FILE]     # parameter sweep
    python run.py check                  # + consistency check
    python run.py json                   # JSON output to stdout
    python run.py sens                   # sensitivity ranking
    python run.py pc                     # parallel MC
    python run.py --no-viz               # plain output
    python run.py --help                 # this message
"""

import sys
import json
import argparse
from pathlib import Path

from qta.sim import run_simulation, main
from qta.viz import (
    print_dashboard, print_header, print_bottleneck_analysis,
    write_html_report, write_json_output,
)
from qta.sweep import sweep_parameter, sensitivity_ranking
from qta.mc_parallel import run_parallel_MC


def cmd_run(args):
    main(no_viz=args.no_viz)


def cmd_bottleneck(args):
    result = run_simulation()
    verdict, all_gates, mc, info = result
    print_dashboard(all_gates, mc, verdict)
    print_header("Bottleneck Analysis")
    print_bottleneck_analysis(all_gates)


def cmd_report(args):
    result = run_simulation()
    verdict, all_gates, mc, info = result
    path = args.output or "outputs/qta_report.html"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    p = write_html_report(all_gates, mc, info, verdict, path)
    print(f"HTML report written to: {p.resolve()}")


def cmd_json(args):
    result = run_simulation()
    verdict, all_gates, mc, info = result
    p = args.output
    if p:
        write_json_output(all_gates, mc, info, verdict, p)
        print(f"JSON written to: {Path(p).resolve()}")
    else:
        counts = {}
        for g in all_gates:
            counts[g.status] = counts.get(g.status, 0) + 1
        out = {
            "version": "3.1.0",
            "verdict": verdict,
            "total_gates": len(all_gates),
            "gate_counts": counts,
            "mc_pass_rate_pct": info.get("pass_rate", 0) * 100,
            "dominant_failure": info.get("dominant_failure", "unknown"),
            "T_sample_mK": round(info["sv"].T_sample_K * 1e3, 4) if info.get("sv") else None,
            "SNR": round(info["sv"].SNR, 1) if info.get("sv") else None,
        }
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")


def cmd_sweep(args):
    name = args.param or "G_eff"
    vals = [1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4]
    if name == "tau_c":
        vals = [1e-7, 1e-6, 27.7e-6, 292e-6, 1e-3, 4e-3, 10e-3, 0.1]
    elif name == "eta_abs":
        vals = [0.01, 0.03, 0.05, 0.10, 0.20, 0.50]
    elif name == "P_mw":
        vals = [1e-11, 1e-10, 1e-9, 1e-8, 1e-7]
    elif name == "f_rep":
        vals = [10, 50, 100, 200, 500, 1000]
    elif name == "E_pulse":
        vals = [1e-12, 5e-12, 5e-11, 5e-10, 5e-9]
    out = args.out or f"outputs/sweep_{name}.csv"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    res = sweep_parameter(name, vals)
    import csv
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, res[0].keys())
        w.writeheader()
        w.writerows(res)
    print(f"Sweep '{name}' ({len(res)} points) → {out}")
    for r in res:
        print(f"  {r['value']:>10.4e}  →  T={r['T_sample_mK']:.4f} mK  SNR={r['SNR']:.1f}")


def cmd_check(args):
    main(no_viz=args.no_viz)
    print("\n" + "=" * 60)
    print("CONSISTENCY CHECK")
    print("=" * 60)
    try:
        from package_consistency_check import run_checks
        result = run_checks(quiet=True)
        if result:
            print("✓ All consistency checks passed.")
        else:
            print("✗ Some consistency checks failed.")
            sys.exit(1)
    except ImportError:
        print("not found: run 'python package_consistency_check.py'")


def cmd_sens(args):
    ranking = sensitivity_ranking()
    print(f"\n{'Parameter':<12} {'Base':<12} {'dSNR/dP':<10} {'dT/dP(mK)':<12}  T_lo→T_hi")
    print("-" * 70)
    for r in ranking:
        print(f"  {r['parameter']:<12} {r['base_value']:<12.4g} {r['dSNR_dP_norm']:<10.2f} "
              f"{r['dT_dP_norm']:<12.4f} {r['T_lo_mK']}→{r['T_hi_mK']} mK")


def cmd_pc(args):
    N = args.N or 10000
    mc = run_parallel_MC(N=N)
    print(f"\n  Parallel MC ({mc['N']:,} samples): "
          f"{mc['pass_total']:,} pass ({mc['pass_rate']*100:.1f}%)")
    print(f"  Dominant failure: {mc['dominant_failure']}")
    print(f"  Best SNR: {mc['best_SNR']:.1f}")
    if args.out:
        import json
        Path(args.out).write_text(json.dumps(mc, indent=2, default=str))
        print(f"  Results → {args.out}")


def main_cli():
    parser = argparse.ArgumentParser(
        description="QTA Simulation Toolkit v3.1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                 # full simulation
  python run.py bottleneck      # bottleneck analysis
  python run.py report          # HTML report
  python run.py sweep --param tau_c  # tau_c sweep
  python run.py sens            # sensitivity ranking
  python run.py json            # JSON to stdout
""")
    parser.add_argument("--no-viz", action="store_true", help="disable ANSI color")
    parser.add_argument("--out", help="output file path")
    sub = parser.add_subparsers(dest="command", help="sub-command")

    p_run = sub.add_parser("run", help="full simulation (default)")
    p_run.add_argument("--no-viz", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_bn = sub.add_parser("bottleneck", help="bottleneck analysis")
    p_bn.set_defaults(func=cmd_bottleneck)

    p_rp = sub.add_parser("report", help="generate HTML report")
    p_rp.add_argument("--output", "-o", default="outputs/qta_report.html")
    p_rp.set_defaults(func=cmd_report)

    p_js = sub.add_parser("json", help="JSON output")
    p_js.add_argument("--output", "-o")
    p_js.set_defaults(func=cmd_json)

    p_sw = sub.add_parser("sweep", help="parameter sweep")
    p_sw.add_argument("--param", default="G_eff", choices=[
        "G_eff", "eta_abs", "P_mw", "tau_c", "f_rep", "E_pulse"])
    p_sw.add_argument("--out", default="")
    p_sw.set_defaults(func=cmd_sweep)

    p_ch = sub.add_parser("check", help="sim + consistency check")
    p_ch.add_argument("--no-viz", action="store_true")
    p_ch.set_defaults(func=cmd_check)

    p_se = sub.add_parser("sens", help="sensitivity ranking")
    p_se.set_defaults(func=cmd_sens)

    p_pc = sub.add_parser("pc", help="parallel MC")
    p_pc.add_argument("-N", type=int, default=10000)
    p_pc.add_argument("--out")
    p_pc.set_defaults(func=cmd_pc)

    args = parser.parse_args()
    if args.command is None:
        # default: run
        main(no_viz=("--no-viz" in sys.argv or args.no_viz))
    else:
        args.func(args)


if __name__ == "__main__":
    main_cli()
