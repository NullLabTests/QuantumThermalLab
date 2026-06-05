"""Terminal visualization — rich ANSI diagrams and dashboards for QTA."""

import json
import shutil
import textwrap
from pathlib import Path
from .constants import BLOCKING, VALIDATED
from .model import Gate

# ANSI color codes
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"
    BG_MAGENTA = "\033[105m"
    BG_CYAN = "\033[106m"
    BG_GRAY = "\033[100m"


def _term_width():
    return shutil.get_terminal_size((80, 24)).columns


def _bar(label, pct, width=30, color=C.BLUE, char="█"):
    """Draw a horizontal bar chart element."""
    fill = int(pct / 100 * width)
    empty = width - fill
    bar = f"{color}{char * fill}{C.DIM}{char * empty}{C.RESET}"
    return f"  {label:<12} │{bar}│ {pct:>5.1f}%"


def gate_status_badge(status):
    """Return a colored badge string for a gate status."""
    badges = {
        "PASS": f"{C.BG_GREEN}{C.BOLD} PASS {C.RESET}",
        "CONDITIONAL": f"{C.BG_YELLOW}{C.BOLD}COND{C.RESET}",
        "BLOCKED": f"{C.BG_RED}{C.BOLD}BLKD{C.RESET}",
        "UNKNOWN": f"{C.BG_MAGENTA}{C.BOLD} UNK {C.RESET}",
        "DERIVED_CHECK": f"{C.BG_CYAN}{C.BOLD} DER {C.RESET}",
        "FAIL": f"{C.BG_RED}{C.BOLD} FAIL{C.RESET}",
    }
    return badges.get(status, f" {status:<4} ")


def print_dashboard(gates, mc_info, verdict):
    """Print a colorful terminal dashboard of the QTA state."""
    W = min(_term_width(), 80)
    print()
    print(f"{C.BOLD}{C.CYAN}╔{'═' * (W-2)}╗{C.RESET}".format())
    title = " QTA SIMULATION DASHBOARD "
    print(f"{C.BOLD}{C.CYAN}║{C.RESET}{C.WHITE}{C.BOLD}{title:^{W-2}}{C.RESET}{C.BOLD}{C.CYAN}║{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}╠{'═' * (W-2)}╣{C.RESET}")

    # Count by status
    counts = {}
    for g in gates:
        counts[g.status] = counts.get(g.status, 0) + 1
    total = len(gates)

    # Status row
    status_line = (
        f"{C.BOLD}  GATES:  {C.RESET}"
        f"{C.BG_GREEN} {counts.get('PASS', 0)}P {C.RESET} "
        f"{C.BG_YELLOW} {counts.get('CONDITIONAL', 0)}C {C.RESET} "
        f"{C.BG_RED} {counts.get('BLOCKED', 0)}B {C.RESET} "
        f"{C.BG_MAGENTA} {counts.get('UNKNOWN', 0)}U {C.RESET} "
        f"{C.BG_CYAN} {counts.get('DERIVED_CHECK', 0)}D {C.RESET} "
        f"{C.BG_RED} {counts.get('FAIL', 0)}F {C.RESET}"
        f"  = {total} total"
    )
    print(f"  {status_line}")
    print()

    # MC info
    if mc_info:
        pr = mc_info.get("pass_rate", 0) * 100
        df = mc_info.get("dominant_failure", "unknown")
        color = C.GREEN if pr > 50 else C.YELLOW if pr > 10 else C.RED
        print(f"  {C.BOLD}MONTE CARLO:{C.RESET}  {color}{pr:.1f}%{C.RESET} pass rate  |  "
              f"Dominant failure: {C.BOLD}{df}{C.RESET}")

    # Verdict
    v_color = C.GREEN if verdict == "PASS" else C.YELLOW if "CONDITIONAL" in verdict else C.RED
    print(f"\n  {C.BOLD}VERDICT:{C.RESET}  {v_color}{C.BOLD}{verdict}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}╚{'═' * (W-2)}╝{C.RESET}")
    print()


def print_thermal_state(sv):
    """Print the thermal state vector with color coding."""
    W = min(_term_width(), 80)
    print(f"\n{C.BOLD}{C.CYAN}── Thermal State Vector (forecast) ──{C.RESET}")
    items = [
        ("T_sample", f"{sv.T_sample_K*1e3:.4f} mK", C.GREEN if sv.T_sample_K < 0.012 else C.RED),
        ("P_total", f"{sv.P_total_W*1e12:.1f} pW", C.GREEN if sv.P_total_W < 200e-6 else C.RED),
        ("P_opt", f"{sv.P_opt_W*1e12:.1f} pW", C.YELLOW),
        ("P_mw", f"{sv.P_mw_W*1e12:.1f} pW", C.YELLOW),
        ("P_cond", f"{sv.P_cond_W*1e12:.1f} pW", C.DIM),
        ("P_vib", f"{sv.P_vib_W*1e12:.1f} pW", C.DIM),
        ("P_rad", f"{sv.P_rad_W*1e12:.1f} pW", C.DIM),
        ("P_He", f"{sv.P_He_th_W*1e12:.1f} pW", C.DIM),
        ("G_eff", f"{sv.G_eff_WK:.2e} W/K", C.YELLOW),
        ("Omega_R", f"{sv.Omega_R_rads:.0f} rad/s", C.CYAN),
        ("tau_pi2", f"{sv.tau_pi2_s*1e6:.3f} us", C.YELLOW),
        ("T2e", f"{sv.T2e_s*1e6:.3f} us", C.CYAN),
        ("SNR", f"{sv.SNR:.1f}", C.GREEN if sv.SNR >= 5 else C.RED),
        ("Kn_He", f"{sv.Kn_He:.0f}", C.GREEN if sv.Kn_He > 10 else C.RED),
    ]
    for name, val, color in items:
        print(f"  {C.BOLD}{name:<12}{C.RESET} {color}{val}{C.RESET}")


def print_gate_row(g, verbose=False):
    """Print a single colored gate row."""
    badge = gate_status_badge(g.status)
    name = g.name[:50]
    print(f"  {badge}  {g.gid:<8} {name}")
    if verbose:
        print(f"         {C.DIM}{g.reason[:120]}{C.RESET}")


def print_bottleneck_analysis(all_gates):
    """Print a bottleneck severity chart."""
    W = min(_term_width(), 80)
    print(f"\n{C.BOLD}{C.RED}Bottleneck Analysis{C.RESET}")
    print(f"{C.DIM}{'─' * (W-4)}{C.RESET}")

    blocked = [g for g in all_gates if g.status in ("BLOCKED", BLOCKING)]
    unknown = [g for g in all_gates if g.status == "UNKNOWN"]
    conditional = [g for g in all_gates if g.status == "CONDITIONAL"]

    total = len(all_gates)
    for label, group, color in [
        ("BLOCKED", blocked, C.RED),
        ("UNKNOWN", unknown, C.MAGENTA),
        ("CONDITIONAL", conditional, C.YELLOW),
    ]:
        pct = len(group) / total * 100 if total else 0
        print(_bar(label, pct, width=40, color=color))

    # Top blockages
    if blocked:
        print(f"\n{C.BOLD}{C.RED}Top Blocked Gates:{C.RESET}")
        for g in sorted(blocked, key=lambda x: x.gid)[:5]:
            print(f"  {C.RED}⛔{C.RESET} {g.gid}: {g.name[:60]}")
    if unknown:
        print(f"\n{C.BOLD}{C.MAGENTA}Unknown Gates (require experiment):{C.RESET}")
        for g in unknown:
            print(f"  {C.MAGENTA}❓{C.RESET} {g.gid}: {g.name[:60]}")


def print_header(text):
    """Print a colored section header."""
    W = min(_term_width(), 80)
    print(f"\n{C.BOLD}{C.CYAN}{'═' * (W-4)}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {text}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * (W-4)}{C.RESET}")


def _status_color(status):
    return {"PASS": "#27ae60", "CONDITIONAL": "#f39c12",
            "BLOCKED": "#e74c3c", "UNKNOWN": "#9b59b6",
            "DERIVED_CHECK": "#00bcd4", "FAIL": "#c0392b"}.get(status, "#95a5a6")


def _status_icon(status):
    return {"PASS": "✅", "CONDITIONAL": "🟡", "BLOCKED": "⬛",
            "UNKNOWN": "❓", "DERIVED_CHECK": "🔷", "FAIL": "🔴"}.get(status, "•")


def write_html_report(gates, mc, info, verdict, output_path):
    """Generate a standalone HTML report with all QTA results."""
    counts = {}
    for g in gates:
        counts[g.status] = counts.get(g.status, 0) + 1
    total = len(gates)

    sv = info.get("sv")
    thermal_rows = ""
    if sv:
        thermal_items = [
            ("T_sample", f"{sv.T_sample_K*1e3:.4f} mK", "green" if sv.T_sample_K < 0.012 else "red"),
            ("P_total", f"{sv.P_total_W*1e12:.1f} pW", "green" if sv.P_total_W < 200e-6 else "red"),
            ("P_opt", f"{sv.P_opt_W*1e12:.1f} pW", "amber"),
            ("P_mw", f"{sv.P_mw_W*1e12:.1f} pW", "amber"),
            ("P_cond", f"{sv.P_cond_W*1e12:.1f} pW", "gray"),
            ("G_eff", f"{sv.G_eff_WK:.2e} W/K", "amber"),
            ("Omega_R", f"{sv.Omega_R_rads:.0f} rad/s", "blue"),
            ("tau_pi2", f"{sv.tau_pi2_s*1e6:.3f} us", "amber"),
            ("T2e", f"{sv.T2e_s*1e6:.3f} us", "blue"),
            ("SNR", f"{sv.SNR:.1f}", "green" if sv.SNR >= 5 else "red"),
            ("Kn_He", f"{sv.Kn_He:.0f}", "green" if sv.Kn_He > 10 else "red"),
        ]
        for name, val, color in thermal_items:
            thermal_rows += f"<tr><td>{name}</td><td style='color:{color};font-weight:bold'>{val}</td></tr>\n"

    gate_rows = ""
    for g in gates:
        sc = _status_color(g.status)
        si = _status_icon(g.status)
        gate_rows += (
            f"<tr><td>{g.gid}</td><td>{g.mode}</td><td>{g.name}</td>"
            f"<td style='background:{sc};color:white;text-align:center'>{si} {g.status}</td>"
            f"<td>{g.reason[:100]}</td></tr>\n"
        )

    mc_rows = ""
    if mc:
        for k, v in sorted(mc.items()):
            if k in ("best", "failed_samples"):
                continue
            mc_rows += f"<tr><td>{k}</td><td>{v}</td></tr>\n"

    bottleneck_rows = ""
    for label in ["BLOCKED", "UNKNOWN", "CONDITIONAL"]:
        cnt = counts.get(label, 0)
        pct = cnt / total * 100 if total else 0
        sc = _status_color(label)
        bottleneck_rows += (
            f"<tr><td>{label}</td>"
            f"<td style='color:{sc};font-weight:bold'>{cnt}</td>"
            f"<td>{pct:.1f}%</td>"
            f"<td><div style='background:#ecf0f1;border-radius:4px;overflow:hidden'>"
            f"<div style='width:{pct}%;height:20px;background:{sc}'></div></div></td></tr>\n"
        )

    html = textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html><head><meta charset="utf-8">
    <title>QTA Simulation Report</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              max-width: 1100px; margin: 2em auto; padding: 0 20px; background: #f8f9fa; color: #333; }}
      h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 8px; }}
      h2 {{ color: #34495e; margin-top: 2em; }}
      table {{ width: 100%; border-collapse: collapse; margin: 1em 0; background: white;
               box-shadow: 0 1px 3px rgba(0,0,0,.1); border-radius: 6px; overflow: hidden; }}
      th {{ background: #34495e; color: white; padding: 10px 12px; text-align: left; }}
      td {{ padding: 8px 12px; border-bottom: 1px solid #ecf0f1; }}
      tr:hover td {{ background: #f5f6fa; }}
      .verdict {{ font-size: 1.3em; padding: 12px 20px; border-radius: 6px; margin: 1em 0; }}
      .footer {{ margin-top: 3em; padding-top: 1em; border-top: 1px solid #ddd; font-size: .85em; color: #7f8c8d; text-align: center; }}
    </style></head><body>
    <h1>⚛ QTA Simulation Report</h1>
    <div class="verdict" style='background:#{"fef9e7" if "CONDITIONAL" in verdict else "eafaf1"};border-left:5px solid {"#f39c12" if "CONDITIONAL" in verdict else "#27ae60"}'>
      <strong>Verdict:</strong> {verdict}
    </div>
    <h2>📊 Gate Status</h2>
    <table><tr><th>Status</th><th>Count</th><th>%</th><th>Bar</th></tr>
    {bottleneck_rows}
    <tr style='font-weight:bold'><td>TOTAL</td><td>{total}</td><td>100%</td><td></td></tr>
    </table>
    <h2>🌡️ Thermal State Vector</h2>
    <table><tr><th>Parameter</th><th>Value</th></tr>{thermal_rows}</table>
    <h2>🚪 All Gates ({total})</h2>
    <table><tr><th>ID</th><th>Mode</th><th>Name</th><th>Status</th><th>Reason</th></tr>
    {gate_rows}</table>
    <h2>🎲 Monte Carlo</h2>
    <table><tr><th>Metric</th><th>Value</th></tr>{mc_rows}</table>
    <div class="footer">
      QTA Simulation Toolkit v3.1.0 &mdash; Pre-experimental conditional validation framework<br>
      Generated: <span id="ts"></span>
    </div>
    <script>document.getElementById('ts').textContent = new Date().toISOString();</script>
    </body></html>
    """)

    path = Path(output_path)
    path.write_text(html)
    return path


def write_json_output(gates, mc, info, verdict, output_path):
    """Write a JSON summary of the simulation."""
    counts = {}
    for g in gates:
        counts[g.status] = counts.get(g.status, 0) + 1

    sv = info.get("sv")
    out = {
        "version": "3.1.0",
        "verdict": verdict,
        "total_gates": len(gates),
        "gate_counts": counts,
        "mc_pass_rate_pct": info.get("pass_rate", 0) * 100,
        "dominant_failure": info.get("dominant_failure", "unknown"),
        "thermal": {
            "T_sample_mK": round(sv.T_sample_K * 1e3, 4) if sv else None,
            "P_total_pW": round(sv.P_total_W * 1e12, 1) if sv else None,
            "SNR": round(sv.SNR, 1) if sv else None,
            "Kn_He": round(sv.Kn_He) if sv else None,
        } if sv else None,
        "note": info.get("note", ""),
    }
    path = Path(output_path)
    path.write_text(json.dumps(out, indent=2))
    return path
