
```
   ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗
  ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║
  ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
  ██▄▄▄██║██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
  ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
```
# ⚛ Quantum Thermal Architecture (QTA) Simulation Toolkit

## 🎯 What Is This?

A **pre-experimental feasibility framework** for a proposed quantum sensing platform
that would combine **NV⁻ diamond** and **He-₃ gas** in a single cryogenic chamber
at **millikelvin temperatures**, with **in situ material processing** (LCVD diamond
growth) interleaved between sensing runs.

**The question this toolkit answers:**

> *"Before we spend $500K+ building the hardware — is this design even physically
> feasible? What are the showstoppers? What must we measure first?"*

The answer today: [**🟡 CONDITIONAL**](#-live-status-dashboard) — the physics checks
out on paper, but **zero** hardware components are installed and **zero** parameters
have been measured in the actual system. Two critical unknowns (τ_c and C_contr at
10 mK) require experimental measurement before feasibility can be confirmed.

---

## 👥 Who Is This For?

| Role | What they get |
|------|---------------|
| **Experimental physicists** | A prioritized list of 10 first experiments; tau_c sweep showing SNR vs coherence; thermal budget breakdown |
| **Cryogenic engineers** | 35 ordered engineering fixes; 14 hardware interlocks; 24-component three-layer status; G_eff/sinter analysis |
| **Grant reviewers** | Clear pre-experimental status dashboard; explicit list of ALL assumptions (none hidden); risk register |
| **Lab PIs** | Go/no-go decision framework; bottleneck analysis; Monte Carlo failure mode ranking |

**🔬 Built with zero third-party dependencies** — pure Python 3.10+ stdlib.
Runs on any machine in seconds.

---

## 📊 LIVE STATUS DASHBOARD

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        QTA SIMULATION DASHBOARD                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   GATES:  🟢  0P    🟡 39C    ⬛ 21B    ❓  2U    🔷  1D    🔴  0F         │
│                                                = 63 total                   │
│                                                                              │
│   ────────────────────────────────────────────────────────────────────────   │
│   BLOCKED    ████████████████████████████████████░░░░░░░░░░░  33.3%          │
│   UNKNOWN    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███████   3.2%           │
│   CONDITIONAL███████████████████████████████████████████████  61.9%          │
│   ────────────────────────────────────────────────────────────────────────   │
│                                                                              │
│   MONTE CARLO:  🟡 33.8% pass rate (post-bakeout forecast)                  │
│   Dominant failure: 🔴  tau_c (66.2% of MC samples)                         │
│   🔴 Threshold:  τ_c ≥ 292 µs  for SNR ≥ 5                                  │
│                                                                              │
│   VERDICT:  🟡 CONDITIONAL — EXPERIMENTAL VALIDATION REQUIRED                │
│                                                                              │
│   🌡️  T_sample = 10.413 mK     📡 P_total = 4.13 nW                         │
│                                                                              │
│   ⚠️  0 hardware components installed. 0 parameters measured in this system. │
│   🚫  0 gates reach PASS from assumptions, simulation, or literature.        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ QUICK START

```bash
# ▶️ Full simulation with color dashboard
python run.py

# 🔎 Bottleneck analysis (blocked/unknown gates)
python run.py bottleneck

# 📊 Parameter sweep (tau_c, G_eff, eta_abs...)
python run.py sweep --param tau_c

# 🔬 Sensitivity ranking (dSNR/dP, dT/dP for each parameter)
python run.py sens

# 📄 Standalone HTML report
python run.py report
# → outputs/qta_report.html

# 📋 JSON output (pipe to jq)
python run.py json
python run.py json | jq '.verdict, .gate_counts'

# ⚡ Parallel Monte Carlo (2-4× faster)
python run.py pc -N 10000

# ✅ Run all tests
python -m pytest tests/ -v
```

**📦 Zero dependencies.** Python 3.10+ only.

---

## 🏛️ The Architecture: Four Mutually Exclusive Modes

```
                          ┌─────────────────────────────────────┐
                          │       HARD INTERLOCK MATRIX         │
                          │    IL-01  through  IL-14  enforce   │
                          │                                     │
                          │    🚫 SENSING + LCVD = IMPOSSIBLE   │
                          │    🚫 He-3 + PRECURSOR = IMPOSSIBLE │
                          │    🚫 LCVD + SWITCH_CLOSED = HEAT   │
                          └─────────────────────────────────────┘

  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                                                                       ║
  ║    ❄️ MODE A                     🔥 MODE B                           ║
  ║    ┌─────────────────────┐      ┌─────────────────────┐               ║
  ║    │ Cryogenic Baseline  │      │ Material Processing │               ║
  ║    │ ─────────────────── │      │ ─────────────────── │               ║
  ║    │ ■ Stabilize to 10mK │      │ ■ LCVD precursor    │               ║
  ║    │ ■ Verify vacuum     │ ────▶│ ■ fs-laser diamond  │               ║
  ║    │ ■ NV ODMR baseline  │      │ ■ Molecular beam    │               ║
  ║    │                     │      │ ■ Surface growth    │               ║
  ║    │ 🟡 SENSING = OFF   │      │ 🟡 SENSING = OFF   │               ║
  ║    │ 🔵 HE = ABSENT     │      │ 🔵 HE = ABSENT     │               ║
  ║    └─────────────────────┘      └─────────┬───────────┘               ║
  ║                                           │                           ║
  ║                                           ▼                           ║
  ║                                   ┌─────────────────────┐             ║
  ║                                   │  🌀 MODE C          │             ║
  ║                                   │  ───────────────────│             ║
  ║                                   │  ■ Shut growth      │             ║
  ║                                   │  ■ Cryopump species │             ║
  ║                                   │  ■ RGA + QCM verify │             ║
  ║                                   │  ■ Thermal recovery │             ║
  ║                                   │  ■ Vibration settle │             ║
  ║                                   └─────────┬───────────┘             ║
  ║                                             │                         ║
  ║                                             ▼                         ║
  ║                                   ┌─────────────────────┐             ║
  ║                                   │  🎯 MODE D          │             ║
  ║                                   │  ───────────────────│             ║
  ║  ╔═══════════════════════════════▶│  ■ NV / He-3 Ramsey │             ║
  ║  ║                               │  ■ ODMR at 10 mK    │             ║
  ║  ║   ⚠️  MODE C → D BLOCKED     │  ■ τ_c measurement  │             ║
  ║  ║   until ALL prerequisites     │                     │             ║
  ║  ║   are met (E01–E14)          │  🟡 LCVD = OFF      │             ║
  ║  ║                               │  🔵 HE = PRESENT    │             ║
  ║  ║                               └─────────────────────┘             ║
  ║  ║                                                                   ║
  ╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 🔴 THE PRIMARY BOTTLENECK: τ_c (He-3 Spin Coherence)

The simulation identifies **one dominant unknown** that determines feasibility:

```
  τ_c ≥ 292 µs   →   SNR ≥ 5   →   Mode D feasible
  τ_c < 292 µs   →   SNR < 5   →   Mode D infeasible

  66.2% of Monte Carlo samples fail due to τ_c being too short.
```

### τ_c Sweep Results

```
   τ_c        SNR     Δγ (rad/s)   T₂e (µs)   Gate
   ───────────────────────────────────────────────────────────────────
   1 ns      0.0     6.90e+03     10.0        ❌ FORECAST_THRESHOLD_NOT_MET
   10 ns     0.1     6.90e+04     10.0        ❌ FORECAST_THRESHOLD_NOT_MET
   100 ns    0.3     3.37e+05     9.97        ❌ FORECAST_THRESHOLD_NOT_MET
   1 µs      0.7     6.90e+05     9.69        ❌ FORECAST_THRESHOLD_NOT_MET
   27.7 µs   2.9     1.63e+06     6.14        ⚠️  SUPERSEDED_V30 (old threshold)
   292 µs    5.0     2.41e+06     3.02        ✅ CANONICAL_THRESHOLD
   1 ms      8.7     2.90e+06     1.89        ✅ THRESHOLD_SATISFIED_IF_MEASURED
   4 ms     18.5     3.19e+06     1.03        ✅ THRESHOLD_SATISFIED_IF_MEASURED
   10 ms    29.3     3.24e+06     0.62        ✅ THRESHOLD_SATISFIED_IF_MEASURED
   100 ms   90.5     3.26e+06     0.08        ✅ THRESHOLD_SATISFIED_IF_MEASURED

   Key insight: The v3.0 threshold (27.7 µs) was wrong — it omitted
   pulse dephasing (pd² in C_eff) and the ε_thermo budget.
```

---

## 🧪 Monte Carlo Analysis (N = 10,000)

### Sampling Distributions

```
   τ_c      ████████████████████░░░░░░░░░░░░  log-U[1ns, 100ms]   🔴 66.2%  DOMINANT
   G_eff    ████████████░░░░░░░░░░░░░░░░░░░░  U[5e-6, 3e-5] W/K  🟡 18.3%
   ε_thermo ██████░░░░░░░░░░░░░░░░░░░░░░░░░░  coupled             🟡 11.0%
   C_contr  ████████████████░░░░░░░░░░░░░░░░  U[0.05, 0.20]       secondary
   T₂*      ██████████░░░░░░░░░░░░░░░░░░░░░░  U[5, 20] µs        coupled
   P_H₂     ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  U[5e-13, 2e-12] Pa  0.1%
   η_abs    ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  U[0.02, 0.10]       0.0%
   S_vib    ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  U[1e-11, 1e-8]     coupled
```

---

## 🔧 The 10 Experiments That Determine Feasibility

```
┌─────┬────────────────────────────────────────┬──────────┬────────────────┐
│  #  │  Experiment                            │ Resolves │  Measurement   │
├─────┼────────────────────────────────────────┼──────────┼────────────────┤
│  1  │  ODMR at 10 mK bare diamond            │ C_contr  │  C_contr > 5%  │
│     │  ⚠️  MUST BE FIRST                    │          │                │
│  2  │  Ramsey: He-3 vs He-4 control          │ τ_c      │  τ_c ≥ 292 µs  │
│     │  🔴 CRITICAL — feasibility gate        │          │                │
│  3  │  250 °C/48 h bakeout + NEG + RGA      │ P_H₂     │  < 2e-12 Pa    │
│  4  │  G_eff step-response thermometry       │ G_eff    │  (1.0±0.3) µW/K│
│  5  │  Fabricate 45 cm² Ag sinter            │ A_sinter │  ≥ 1e-5 W/K    │
│  6  │  RGA CH₄ after each purge              │ P_CH₄    │  < 5e-12 Pa    │
│  7  │  Vibration PSD + dB/dz measurement     │ S_vib    │  < 1e-10 m²/Hz │
│  8  │  Rabi oscillation in cryostat          │ Ω_R      │  ±10% of calc  │
│  9  │  s(He)/E_b on F-diamond (TPD/QCM)      │ s_He     │  closes model  │
│ 10  │  η_abs measurement                     │ η_abs    │  closes D6/D7  │
└─────┴────────────────────────────────────────┴──────────┴────────────────┘
```

---

## 🧪 Full CLI Reference

```
  python run.py                              # color dashboard
  python run.py bottleneck                   # bottleneck analysis
  python run.py report                       # → outputs/qta_report.html
  python run.py sweep --param tau_c          # τ_c sweep CSV
  python run.py sweep --param G_eff          # G_eff sweep
  python run.py sweep --param eta_abs        # absorption sweep
  python run.py sens                         # sensitivity ranking
  python run.py json                         # JSON to stdout
  python run.py pc -N 10000                  # parallel Monte Carlo
  python run.py check                        # + consistency check
  python run.py --no-viz                     # plain text output
```

---

## 📦 Package Structure

```
📁 quantum-thermal-architecture/
│
├── 📂 qta/                         # 🧬 Main simulation package
│   ├── __init__.py                 # v3.1.0
│   ├── constants.py                # ⚛️ Physical constants · EngStatus · PARAM_REGISTRY
│   ├── model.py                    # 📐 Gate · ModeStateVector · SystemState · ChamberState
│   ├── gates.py                    # 🚪 All 63 gate definitions (modes A/B/C/D)
│   ├── monte_carlo.py              # 🎲 Sequential MC (N=10k, log-U sampling)
│   ├── mc_parallel.py              # ⚡ Parallel MC (multiprocessing, 2-4× faster)
│   ├── sweep.py                    # 📊 Parameter sweeps · sensitivity ranking
│   ├── engineering.py              # 🔧 35 fixes · 14 interlocks · 10 experiments
│   ├── sim.py                      # 🎯 Orchestrator · CSV/JSON output
│   └── viz.py                      # 🎨 Terminal dashboard · HTML reporter · JSON writer
│
├── 📂 tests/                       # ✅ pytest suite (60 tests)
│   ├── test_constants.py           #   6 tests — constants, status logic
│   ├── test_model.py               #  10 tests — dataclass validation
│   ├── test_model_edge.py          #  13 tests — edge cases, zero limits, interlocks
│   ├── test_sim.py                 #   6 tests — integration, output files
│   ├── test_engineering.py         #   8 tests — gates, interlocks, fixes
│   ├── test_mc_parallel.py         #   4 tests — parallel MC engine
│   ├── test_sweep.py               #   6 tests — sweeps, CSV, sensitivity
│   └── test_viz.py                 #   5 tests — HTML/JSON reports, badges
│
├── run.py                          # ▶️  CLI entry point
├── run_qta_full_sim.py             # 📜 Legacy monolith shim
├── qta_full_sim.py                 # 📜 Legacy (2615 lines, kept for compat)
├── package_consistency_check.py    # 🔍 Independent artifact verifier
│
├── 📂 data/                        # 📊 CSV/JSON data (BOM, risk, validation, source maps)
├── 📂 .github/workflows/           # ⚙️ CI (3 Python versions, lint, test, smoke)
│
├── pyproject.toml                  # 📦 Python project metadata
├── Makefile                        # 🔧 make test / make report / make sweep
├── LICENSE                         # ⚖️ MIT
└── README.md                       # 📖 This file
```

---

## 📐 The Physics Model

The core simulation solves a **self-consistent thermal balance** for Mode D:

```
  T_sample = T_fridge + P_total / G_eff

  P_total = P_He + P_opt + P_mw + P_cond + P_vib + P_lk + P_rad
```

Then computes the **NV/He-3 detection SNR**:

```
  SNR = GDC / δG

  GDC  =  C_c · n_s · τ_c / d⁴        (He-3 dipole coupling)
  δG   =  1 / (C_eff · T₂e · √(N_ph + N_dk))   (detection noise)
  C_eff =  C_contr · exp(-2τ_π/₂ / T₂*)         (pulse dephasing)
```

### Key Parameters

| Parameter | Value | Status | Impact |
|-----------|-------|--------|--------|
| T_fridge | 10 mK | MANUFACTURER_SPEC | Base temperature |
| G_eff | 1e-5 W/K | **ASSUMED** (not measured) | 🔴 D3/D4/D5 thermal budget |
| τ_c | ❓ UNKNOWN | **UNKNOWN** | 🔴 D13 primary bottleneck |
| C_contr@10mK | ❓ UNKNOWN | **UNKNOWN** | 🔴 D12 co-equal bottleneck |
| η_abs | 0.05 | ASSUMED | D6/D7 laser heating |
| T₂* | 10 µs | ASSUMED | D8/D13 pulse dephasing |
| P_H₂ | 1e-10 Pa | ASSUMED | D10a/D10b H₂ coverage |
| τ_c threshold | 292 µs | DERIVED | SNR ≥ 5 + ε_thermo < 1% |

---

## 🏗️ Three-Layer Engineering Status

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    📐  SPECIFIED      →  Design exists (geometry, materials, equations)     │
│    🔧  INSTALLED      →  Hardware physically built & in the cryostat        │
│    ✅  VERIFIED       →  Measurement confirms performance meets spec        │
│                                                                             │
│    ⚠️  SPECIFIED ≠ INSTALLED ≠ VERIFIED                                    │
│         🏆 PASS requires ALL THREE layers.                                  │
│                                                                             │
│    📌  All 24 hardware components at DESIGN_SPECIFIED only:                 │
│                                                                             │
│    Bakeout ▓▓░░░░░░   │  NEG ▓▓░░░░░░░   │  Cryotrap ▓▓░░░░░░░             │
│    RGA     ░░░░░░░░   │  Pump ▓▓░░░░░░░  │  Leak ░░░░░░░░░░░               │
│    Sinter  ▓▓░░░░░░░  │  SC Sw ▓▓░░░░░░░ │  Suspension ▓▓░░░░░░░           │
│    Gas ln  ▓▓░░░░░░░  │  Nozzle ▓▓░░░░░░│  Shutter ▓▓░░░░░░░              │
│    MW att  ▓▓░░░░░░░  │  Helmholtz ▓▓░░░│  Vib iso ▓▓░░░░░░░               │
│    η_col   ░░░░░░░░░  │  η_abs ░░░░░░░░░│  NV chg ░░░░░░░░░                │
│    Rabi    ░░░░░░░░░  │  τ_c ░░░░░░░░░░░│  G_eff ░░░░░░░░░                 │
│    S_vib   ░░░░░░░░░  │  He4 ░░░░░░░░░░░│                                  │
│                                                                             │
│    LEGEND:  ▓▓ = DESIGN_SPECIFIED   ░░ = NOT_SPECIFIED                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Hard Interlock Matrix

14 interlocks prevent physically impossible or damaging mode combinations:

```
┌────────┬──────────────────────────────────────────────┬───────────┬─────────┐
│  ID    │  Condition                                   │  Type     │  Risk   │
├────────┼──────────────────────────────────────────────┼───────────┼─────────┤
│ IL-01  │  LCVD_on AND sensing_on                      │ IMPOSSIBLE│ 250× TL │
│ IL-02  │  precursor_on AND He3_dosing_on              │ IMPOSSIBLE│ chemical│
│ IL-03  │  LCVD_on AND heat_switch_closed              │ IMPOSSIBLE│ heats MC│
│ IL-04  │  sensing_on AND heat_switch_open              │ IMPOSSIBLE│ not 10mK│
│ IL-05  │  sensing_on AND NOT RGA_pass_CH4             │ BLOCKED   │ CH4 cont│
│ IL-06  │  sensing_on AND NOT RGA_pass_H2              │ BLOCKED   │ H₂ cover│
│ IL-07  │  sensing_on AND T_sample > 12 mK             │ BLOCKED   │ too warm│
│ IL-08  │  sensing_on AND NOT vib_settled              │ BLOCKED   │ vib corr│
│ IL-09  │  He3_present AND LCVD_on                     │ IMPOSSIBLE│ thermal │
│ IL-10  │  He3_present AND precursor_on                 │ IMPOSSIBLE│ CH₄ po  │
│ IL-11  │  Mode_D AND NOT Mode_B_complete              │ BLOCKED   │ purge   │
│ IL-12  │  charcoal_regen AND IVC_valve_open            │ BLOCKED   │ burst   │
│ IL-13  │  growth_on AND He3_dosing_on                 │ IMPOSSIBLE│ mutual  │
│ IL-14  │  LCVD_on AND helium_film_present             │ IMPOSSIBLE│ blocks  │
└────────┴──────────────────────────────────────────────┴───────────┴─────────┘
```

---

## 🧪 Test Suite (60 passing)

```bash
python -m pytest tests/ -v

tests/test_constants.py ......                                           [ 10%]
tests/test_engineering.py ........                                       [ 23%]
tests/test_mc_parallel.py ....                                           [ 30%]
tests/test_model.py ............                                         [ 50%]
tests/test_model_edge.py .............                                   [ 71%]
tests/test_sim.py ......                                                 [ 81%]
tests/test_sweep.py ......                                               [ 91%]
tests/test_viz.py .....                                                  [100%]

============================== 60 passed in 0.74s ================================
```

---

## 🛠️ Engineering Fixes (35 Total)

```bash
Fix     Name                                    Priority    Status
─────────────────────────────────────────────────────────────────────
F01     UHV All-Metal Build                     REQUIRED    NOT_INSTALLED
F02     Differentially Pumped Micro-Nozzle      REQUIRED    NOT_INSTALLED
F03     Three-Shutter Stack                     REQUIRED    NOT_INSTALLED
F04     Witness Coupons                         REQUIRED    NOT_INSTALLED
F05     RGA All-Species Thresholds              REQUIRED    NOT_INSTALLED
F06     Pump Train (NEG + Ion + Cryo)           REQUIRED    NOT_INSTALLED
F07     Residual Hydrogen Mitigation            REQUIRED    NOT_INSTALLED
F08     Surface Re-Termination / Recovery       REQUIRED    NOT_INSTALLED
F09     Geometric Baffle / Labyrinth            REQUIRED    NOT_INSTALLED
F10     Cryo-QCM at Sensing Surface             RECOMMENDED NOT_INSTALLED
F11     Thermal Switch Validation               REQUIRED    NOT_INSTALLED
F12     Vibration Metrology                     REQUIRED    NOT_INSTALLED
F13     Optical Scatter Audit                   REQUIRED    NOT_INSTALLED
F14     Microwave Heat Audit                    REQUIRED    NOT_INSTALLED
F15     NV Survival Post-Cycle Pretest          REQUIRED    NOT_INSTALLED
F16     He-4 Control Experiment                 REQUIRED    DESIGN
F17     Multiple NV Depths                      RECOMMENDED DESIGN
F18     SIL / Waveguide Collection Upgrade      RECOMMENDED DESIGN
F19     Magnetic Shielding Package              REQUIRED    DESIGN
F20     Failure Recovery Path                   REQUIRED    DESIGN
FA-FO   15 additional fixes                     varies      varies
```

---

## ⚖️ License

**MIT** — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>⚛ QTA Simulation Toolkit · v3.1.0</sub><br>
  <sub>Pre-experimental conditional validation framework for NV/He-3 quantum sensing at millikelvin temperatures</sub><br>
  <sub>⚠️  No working hardware is claimed. No breakthrough is asserted.</sub>
</p>
