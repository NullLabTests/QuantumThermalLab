```
                         ███████╗ ████████╗ █████╗
                         ██╔════╝ ╚══██╔══╝██╔══██╗
                         █████╗      ██║   ███████║
                         ██╔══╝      ██║   ██╔══██║
                         ███████╗    ██║   ██║  ██║
                         ╚══════╝    ╚═╝   ╚═╝  ╚═╝
   ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗
  ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║
  ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
  ██�▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
  ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
```
# ⚛ Quantum Thermal Architecture (QTA) Simulation Toolkit

> **Pre-experimental feasibility framework** for same-chamber NV⁻/He-₃ quantum sensing
> and diamond material processing at **millikelvin temperatures**.
>
> 🟡 **CONDITIONAL** — Specified ≠ Installed ≠ Verified. No working hardware.

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
# ▶️ Run full simulation with rich terminal dashboard
python run.py

# 🔍 Run with consistency check
python run.py --check

# 🔎 Show bottleneck analysis
python run.py --bottleneck

# 📊 Plain output (no ANSI color)
python run.py --no-viz

# ✅ Run test suite (24 tests, 0 dependencies)
python -m pytest tests/ -v

# 🐍 Use as package
python -c "from qta.sim import main; main()"
```

**📦 Requirements:** Python 3.10+ | **Zero** third-party dependencies

---

## 🔮 THERMAL STATE VECTOR

Forecast for Mode D (post-bakeout, τ_c = 4 ms assumed):

```
  🌡️  T_sample        ─── 10.413 mK        🟢  (+0.413 mK above base)
  📡  P_total         ─── 4.13 nW           🟢  << 200 µW P_cool_MC
  🔦  P_opt           ─── 500.0 pW          🟡  (η_abs = 0.05 ASSUMED)
  📻  P_mw            ─── 1.0 nW            🟡  (ASSUMED)
  🔗  P_cond          ─── 2.5 nW            ⚪  (wiring ASSUMED)
  📳  P_vib           ─── 0.5 pW            ⚪  (ASSUMED)
  ☀️  P_rad           ─── 0.0005 pW         ⚪  (negligible)
  🧊  P_He            ─── 126.0 pW          ⚪  (He-3 film)
  🔧  G_eff           ─── 1.0e-5 W/K        🟡  (ASSUMED — not measured)
  🧲  Ω_R             ─── 139591 rad/s      🟡  (τ_π/2 = 11.25 µs)
  ⏱️  T₂e             ─── 9.36 µs           🟡  (pulse dephasing)
  🎯  SNR             ─── 18.5              🟢  (if τ_c = 4 ms)
  📊  Kn_He           ─── 46                🟢  molecular flow
  🔬  ε_thermo        ─── 0.0001%           🟢  (thermal feedback negligible)
```

---

## 🏛️ ARCHITECTURE: FOUR-MODE OPERATION

```
                          ┌─────────────────────────────────────┐
                          │       HARD INTERLOCK MATRIX         │
                          │    IL-01  through  IL-14  enforce   │
                          │                                     │
                          │    🚫 SENSING + LCVD = IMPOSSIBLE   │
                          │    🚫 He-3 + PRECURSOR = IMPOSSIBLE │
                          │    🚫 LCVD + SWITCH_CLOSED = HEAT   │
                          └─────────────────────────────────────┘
                                    │
                                    ▼
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

## 🔗 DATA FLOW & PACKAGE ARCHITECTURE

```
                         ┌──────────────────────┐
                         │    🧬 PARAM REGISTRY │
                         │    49 parameters     │
                         │    ■ MANUFACTURER_SPEC│
                         │    ■ PHYSICAL_CONSTANT│
                         │    ■ LITERATURE       │
                         │    ■ ASSUMED          │
                         │    ■ UNKNOWN          │
                         │    ■ DESIGN           │
                         └──────────┬───────────┘
                                    │ feeds
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   📐 ModeState    │     │    🚦 SystemState │     │   🏭 ChamberState │
│   Vector.solve() │     │    validate()     │     │   P_H2(), P_CH4() │
│                  │     │                  │     │                  │
│  Self-consistent │     │  Enforces 14     │     │  Hardware state  │
│  thermal balance │     │  hardware        │     │  with bakeout/   │
│  + detection SNR │     │  interlocks      │     │  NEG/cryotrap    │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                       │                         │
         └───────────┬───────────┴───────────┬─────────────┘
                     │                       │
                     ▼                       ▼
          ┌──────────────────┐     ┌──────────────────┐
          │    🚪 GATES      │     │  🎲 MONTE CARLO  │
          │    63 decision   │     │  10,000 samples  │
          │    gates across  │     │  log-U[1ns,100ms]│
          │    4 modes + eng │     │  for τ_c         │
          └────────┬─────────┘     └────────┬─────────┘
                   │                       │
                   └───────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │  📋 OUTPUT FILES     │
                    │  ■ results_gate_table.csv  │
                    │  ■ monte_carlo_summary.csv │
                    │  ■ best_forecast_op.json   │
                    │  ■ tau_c_sweep.csv    │
                    │  ■ interlock_table.csv│
                    │  ■ parameter_registry.csv │
                    │  ■ failed_gate_samples.csv │
                    └──────────────────────┘
```

---

## 🎯 GATE STATUS BREAKDOWN

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GATE STATUS COLOR CODE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   🟢  PASS         Hardware VERIFIED + physics OK                          │
│                    →  0 gates (⌀: system pre-experimental)                  │
│                                                                             │
│   🟡  CONDITIONAL  Feasible under assumptions — requires validation        │
│                    → 39 gates (61.9%) — dominant category                   │
│                      Includes: A1–A7, B1–B2, C1–C4, D3–D8, shield, E01–E14 │
│                                                                             │
│   ⬛  BLOCKED      Prerequisite absent — cannot proceed                    │
│                    → 21 gates (33.3%)                                       │
│                      Includes: A8–A9, A11, A14, D10a, shield, interlock    │
│                                                                             │
│   ❓  UNKNOWN      Requires experimental measurement                       │
│                    →  2 gates (3.2%)                                        │
│                      D12: C_contr at 10 mK    D13: τ_c (primary bottleneck) │
│                                                                             │
│   🔷 DERIVED_CHECK First-principles check (computational)                  │
│                    →  1 gate (1.6%)                                         │
│                      D9: Knudsen number (molecular flow confirmed ✅)       │
│                                                                             │
│   🔴  FAIL         Physics constraint violated                              │
│                    →  0 gates                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔴 BOTTLENECK ANALYSIS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BOTTLENECK SEVERITY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   BLOCKED     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░  33.3%        │
│              (21 gates blocked by hardware not installed)                   │
│                                                                             │
│   UNKNOWN     ▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   3.2%        │
│              (τ_c and C_contr — require cryogenic experiment)              │
│                                                                             │
│   CONDITIONAL ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░  61.9%       │
│              (39 gates — plausible but unvalidated)                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

 ⛔ Top Blocked Gates:
   A8   — Local surface T during deposition pulse measured    [THERMOMETRY]
   A9   — Deposition yield per pulse measured                 [QCM + AFM]
   A11  — Byproducts pump below RGA threshold before Mode D   [RGA]
   A14  — He-3/He-4 film absent before Mode B Processing     [QCM + RGA]
   D10a — H2 Engineering Readiness (bakeout+NEG+cryotrap+RGA) [4× INFRA]

 ❓ Unknown Gates (require experiment):
   D12_G23 — NV Charge State (UNKNOWN; not derivable)
             → ODMR at 10mK post-cycle (F15)
   D13     — Detection SNR (τ_c UNKNOWN)
             → Ramsey + He-4 control (F16)
```

---

## 🎲 MONTE CARLO ANALYSIS (N = 10,000)

### Sampling Distributions & Failure Impact

```
   τ_c      ████████████████████░░░░░░░░░░░░  log-U[1ns, 100ms]   🔴 66.2%  DOMINANT
   G_eff    ████████████░░░░░░░░░░░░░░░░░░░░  U[5e-6, 3e-5] W/K  🟡 18.3%
   ε_thermo ██████░░░░░░░░░░░░░░░░░░░░░░░░░░  coupled             🟡 11.0%
   C_contr  ████████████████░░░░░░░░░░░░░░░░  U[0.05, 0.20]       🟡 secondary
   T₂*      ██████████░░░░░░░░░░░░░░░░░░░░░░  U[5, 20] µs        ⚪ coupled
   P_H₂     ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  U[5e-13, 2e-12] Pa ⚪  0.1%
   η_abs    ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  U[0.02, 0.10]      ⚪  0.0%
   S_vib    ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  U[1e-11, 1e-8]     ⚪ coupled
```

### τ_c Sweep (Threshold at 292 µs for SNR ≥ 5)

```
   τ_c        SNR     Δγ (rad/s)   T₂e (µs)   dγ (rad/s)   Gate
   ───────────────────────────────────────────────────────────────────
   1 ns      0.0     6.90e+03     10.0        8.29e+05     ❌ FORECAST_THRESHOLD_NOT_MET
   10 ns     0.1     6.90e+04     10.0        8.29e+05     ❌ FORECAST_THRESHOLD_NOT_MET
   100 ns    0.3     3.37e+05     9.97        8.29e+05     ❌ FORECAST_THRESHOLD_NOT_MET
   1 µs      0.7     6.90e+05     9.69        9.21e+05     ❌ FORECAST_THRESHOLD_NOT_MET
   27.7 µs   2.9     1.63e+06     6.14        5.58e+05     ⚠️  SUPERSEDED_V30
   292 µs    5.0     2.41e+06     3.02        4.83e+05     ✅ CANONICAL_THRESHOLD
   1 ms      8.7     2.90e+06     1.89        3.33e+05     ✅ THRESHOLD_SATISFIED_IF_MEASURED
   4 ms     18.5     3.19e+06     1.03        1.72e+05     ✅ THRESHOLD_SATISFIED_IF_MEASURED
   10 ms    29.3     3.24e+06     0.62        1.11e+05     ✅ THRESHOLD_SATISFIED_IF_MEASURED
   100 ms   90.5     3.26e+06     0.08        3.60e+04     ✅ THRESHOLD_SATISFIED_IF_MEASURED

   Key insight: τ_c ≥ 292 µs is REQUIRED for SNR ≥ 5.
   v3.0 threshold of 27.7 µs is SUPERSEDED — it did not account for
   pulse dephasing (pd² term in C_eff) or ε_thermo budget.
```

---

## 🏗️ THREE-LAYER ENGINEERING STATUS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    📐  SPECIFIED      →  Design exists (geometry, materials, equations,    │
│                           expected performance)                             │
│                                                                             │
│    🔧  INSTALLED      →  Hardware physically built & present               │
│                           in the cryostat                                   │
│                                                                             │
│    ✅  VERIFIED       →  Measurement confirms performance                  │
│                           meets specification                                │
│                                                                             │
│    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                             │
│    ⚠️  SPECIFIED ≠ INSTALLED ≠ VERIFIED                                   │
│         🏆 PASS requires ALL THREE layers.                                  │
│                                                                             │
│    📌  All 24 hardware components at DESIGN_SPECIFIED only:                │
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

## 🔧 ENGINEERING FIXES (35 TOTAL)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ID    Name                                     Priority    Status           │
├─────────────────────────────────────────────────────────────────────────────┤
│  F01   UHV All-Metal Build                     ⬛ REQUIRED  NOT_INSTALLED     │
│  F02   Differentially Pumped Micro-Nozzle      ⬛ REQUIRED  NOT_INSTALLED     │
│  F03   Three-Shutter Stack                     ⬛ REQUIRED  NOT_INSTALLED     │
│  F04   Witness Coupons                         ⬛ REQUIRED  NOT_INSTALLED     │
│  F05   RGA All-Species Thresholds              ⬛ REQUIRED  NOT_INSTALLED     │
│  F06   Pump Train (NEG + Ion + Cryo)           ⬛ REQUIRED  NOT_INSTALLED     │
│  F07   Residual Hydrogen Mitigation            ⬛ REQUIRED  NOT_INSTALLED     │
│  F08   Surface Re-Termination / Recovery       ⬛ REQUIRED  NOT_INSTALLED     │
│  F09   Geometric Baffle / Labyrinth            ⬛ REQUIRED  NOT_INSTALLED     │
│  F10   Cryo-QCM at Sensing Surface             🟡 RECOMMEND NOT_INSTALLED    │
│  F11   Thermal Switch Validation               ⬛ REQUIRED  NOT_INSTALLED     │
│  F12   Vibration Metrology                     ⬛ REQUIRED  NOT_INSTALLED     │
│  F13   Optical Scatter Audit                   ⬛ REQUIRED  NOT_INSTALLED     │
│  F14   Microwave Heat Audit                    ⬛ REQUIRED  NOT_INSTALLED     │
│  F15   NV Survival Post-Cycle Pretest          ⬛ REQUIRED  NOT_INSTALLED     │
│  F16   He-4 Control Experiment                 ⬛ REQUIRED  DESIGN            │
│  F17   Multiple NV Depths                      🟡 RECOMMEND DESIGN            │
│  F18   SIL / Waveguide Collection Upgrade      🟡 RECOMMEND DESIGN            │
│  F19   Magnetic Shielding Package              ⬛ REQUIRED  DESIGN            │
│  F20   Failure Recovery Path                   ⬛ REQUIRED  DESIGN            │
│  FA    Protected NV Cartridge / Load-Lock      🟡 RECOMMEND NOT_INSTALLED    │
│  FB    All-Metal Bake-Compatible Valve Tree    ⬛ REQUIRED  NOT_INSTALLED     │
│  FC    RGA Line-of-Sight Correction            ⬛ REQUIRED  NOT_INSTALLED     │
│  FD    Cold-Surface Memory / Desorption        ⬛ REQUIRED  NOT_INSTALLED     │
│  FE    Shutter Contamination Replacement       ⬛ REQUIRED  NOT_INSTALLED     │
│  FF    Optical Window Contamination            ⬛ REQUIRED  NOT_INSTALLED     │
│  FG    Gas Purity Chain                        ⬛ REQUIRED  DESIGN            │
│  FH    Helium Leak Check Requirement           ⬛ REQUIRED  NOT_INSTALLED     │
│  FI    Electrical Filtering Heat Budget        ⬛ REQUIRED  NOT_INSTALLED     │
│  FJ    Thermometer Self-Heating Audit          ⬛ REQUIRED  NOT_INSTALLED     │
│  FK    Magnetic Field Compatibility Map        ⬛ REQUIRED  DESIGN            │
│  FL    Eddy-Current Heating                    ⬛ REQUIRED  DESIGN            │
│  FM    Acoustic Isolation for Pumps            ⬛ REQUIRED  DESIGN            │
│  FN    Emergency Fail-Safe State               ⬛ REQUIRED  DESIGN            │
│  FO    Acceptance Test Matrix                  ⬛ REQUIRED  DESIGN            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 HARD INTERLOCK MATRIX

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

## 🧪 KEY PHYSICS PARAMETERS

```
┌────────────────┬──────────────────┬────────────────┬────────────────────────┐
│ Parameter      │ Value            │ Status         │ Impact                 │
├────────────────┼──────────────────┼────────────────┼────────────────────────┤
│ T_fridge       │ 10 mK            │ 📄 MANUF_SPEC  │ Base temperature       │
│ P_cool_MC      │ 200 µW           │ 📄 MANUF_SPEC  │ D3 cooling capacity    │
│ G_eff          │ 1e-5 W/K         │ 📝 ASSUMED     │ 🔴 D3/D4/D5 thermal    │
│ τ_c            │ ❓ UNKNOWN        │ ❓ UNKNOWN     │ 🔴 D13 primary bottleneck│
│ C_contr@10mK   │ ❓ UNKNOWN        │ ❓ UNKNOWN     │ 🔴 D12 co-bottleneck   │
│ η_abs          │ 0.05             │ 📝 ASSUMED     │ 🟡 D6/D7 laser heat    │
│ T₂*            │ 10 µs            │ 📝 ASSUMED     │ 🟡 D8/D13 dephasing    │
│ P_H₂           │ 1e-10 Pa         │ 📝 ASSUMED     │ 🟡 D10a/D10b coverage  │
│ γ_NV           │ 28.025 GHz/T     │ ⚛️ CODATA       │ D13 gyromagnetic ratio │
│ γ_He₃          │ 32.434 MHz/T     │ ⚛️ CODATA       │ D13 gyromagnetic ratio │
│ E_pulse        │ 50 pJ            │ 📝 ASSUMED     │ D6 laser energy        │
│ f_rep          │ 200 Hz           │ 📝 ASSUMED     │ D6 rep rate            │
│ S_vib          │ 1e-10 m²/Hz      │ 📝 ASSUMED     │ D17 vibration          │
│ n_s            │ 3.3e18 m⁻²       │ 📝 ASSUMED     │ D11 He-3 coverage      │
│ η_col          │ 6.35%            │ 📝 ASSUMED     │ D14 collection eff     │
└────────────────┴──────────────────┴────────────────┴────────────────────────┘
```

---

## 🛠️ FIRST EXPERIMENTS (PRIORITY ORDERED)

```
┌─────┬────────────────────────────────────────────┬──────────┬────────────────┐
│  #  │  Experiment                                │ Resolves │  Measurement   │
├─────┼────────────────────────────────────────────┼──────────┼────────────────┤
│  1  │  ODMR at 10 mK bare diamond                │ C_contr  │  C_contr > 5%  │
│     │  ⚠️  MUST BE FIRST — establishes NV signal │          │                │
│  2  │  Ramsey: He-3 vs He-4 control              │ τ_c      │  τ_c ≥ 292 µs  │
│     │  🔴 CRITICAL — determines whole feasibility│          │                │
│  3  │  250 °C/48 h bakeout + SAES NEG + RGA     │ P_H₂     │  < 2e-12 Pa    │
│  4  │  G_eff step-response thermometry           │ G_eff    │  (1.0±0.3) µW/K│
│  5  │  Fabricate 45 cm² Ag sinter                │ A_sinter │  ≥ 1e-5 W/K    │
│  6  │  RGA CH₄ after each purge                  │ P_CH₄    │  < 5e-12 Pa    │
│  7  │  Vibration PSD + dB/dz measurement         │ S_vib    │  < 1e-10 m²/Hz │
│  8  │  Rabi oscillation in cryostat              │ Ω_R      │  ±10% of calc  │
│  9  │  s(He)/E_b on F-diamond (TPD/QCM)          │ s_He     │  closes model  │
│ 10  │  η_abs measurement                         │ η_abs    │  closes D6/D7  │
└─────┴────────────────────────────────────────────┴──────────┴────────────────┘
```

---

## 📦 PACKAGE STRUCTURE

```
📁 quantum-thermal-architecture/
│
├── 📂 qta/                         # 🧬 Main simulation package
│   ├── 📄 __init__.py              # Package info · v3.1.0
│   ├── 📄 constants.py             # ⚛️ Physical constants · EngStatus · PARAM_REGISTRY
│   ├── 📄 model.py                 # 📐 Gate · ModeStateVector · SystemState · ChamberState
│   ├── 📄 gates.py                 # 🚪 All 63 gate definitions (modes A/B/C/D)
│   ├── 📄 monte_carlo.py           # 🎲 MC engine (N=10,000, log-U sampling)
│   ├── 📄 engineering.py           # 🔧 35 fixes · 14 interlocks · 10 experiments
│   ├── 📄 sim.py                   # 🎯 Orchestrator · CLI · CSV/JSON output
│   └── 📄 viz.py                   # 🎨 Terminal visualization · ANSI dashboard
│
├── 📂 tests/                       # ✅ pytest suite (24 tests)
│   ├── 📄 __init__.py
│   ├── 📄 test_constants.py        # Constants & status logic (6 tests)
│   ├── 📄 test_model.py            # Dataclass validation (10 tests)
│   └── 📄 test_sim.py              # Integration (7 tests)
│
├── 📄 run.py                       # ▶️  CLI entry point
├── 📄 run_qta_full_sim.py          # 📜 Legacy monolith shim
├── 📄 qta_full_sim.py              # 📜 Legacy monolith (2615 lines, kept for compat)
├── 📄 package_consistency_check.py # 🔍 Independent artifact verifier
│
├── 📂 data/                        # 📊 CSV/JSON data files
│   ├── 📄 BOM.csv                  #   121-item bill of materials
│   ├── 📄 risk_register.csv        #   107 identified risks
│   ├── 📄 validation_matrix.csv    #   157 validation requirements
│   ├── 📄 source_map.csv           #   60 parameter-to-source mappings
│   └── 📄 ... (25+ data files)
│
├── 📄 pyproject.toml               # 📦 Python project metadata
├── 📄 LICENSE                      # ⚖️ MIT License
└── 📄 README.md                    # 📖 This file
```

---

## 🧪 RUNNING TESTS

```bash
# Full test suite
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=qta

# Individual test files
python -m pytest tests/test_constants.py -v
python -m pytest tests/test_model.py -v
python -m pytest tests/test_sim.py -v
```

### Current Test Results

```
tests/test_constants.py ......                                          [ 25%]
tests/test_model.py ..........                                         [ 66%]
tests/test_sim.py .......                                              [100%]

======================= 24 passed in 8.32s ========================
```

---

## 📚 RELATED DOCUMENTS

| File | Description |
|------|-------------|
| 📄 `CLAIMS_BOUNDARY.md` | Explicit list of claimed / not-claimed items |
| 📄 `REVIEWER_COVER_NOTE.md` | One-page summary for technical review |
| 📄 `REVIEWER_QUESTIONS.md` | ❓ Eight specific technical questions |
| 📄 `FIRST_VALIDATION_EXPERIMENTS.md` | Priority-ordered first experiments |
| 📄 `mode_transition_acceptance_tests.csv` | Mode transition criteria |
| 📄 `shielding_stack_register.csv` | Isolation stack details |
| 📄 `qta_manuscript_v4.pdf` | Full manuscript (LaTeX, ~40 KB) |
| 📄 `package_consistency_check.py` | Standalone consistency check |

---

## ⚖️ LICENSE

**MIT** — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>⚛ QTA Simulation Toolkit · v3.1.0 · Pre-experimental conditional validation framework</sub><br>
  <sub>⚠️  No working hardware is claimed. No breakthrough is asserted.</sub>
</p>
```

---

## 🚀 NOW RUN IT

```bash
python run.py          # Full simulation + rich dashboard
python run.py --bottleneck  # Focus on bottleneck analysis
```
