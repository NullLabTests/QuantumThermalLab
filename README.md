# Quantum Thermal Architecture (QTA) Simulation Toolkit

**Pre-experimental feasibility framework for same-chamber NV/He-3 quantum sensing
and material processing at millikelvin temperatures.**

```
        MODE A                  MODE B                  MODE C                  MODE D
   Cryogenic Baseline      Material Processing     Isolation / Purge       Sensing / Measurement
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  Stabilize to   │    │  LCVD precursor │    │  Shut off       │    │  NV / He-3      │
   │  10 mK baseline │───▶│  exposure +     │───▶│  inputs, purge  │───▶│  Ramsey / ODMR  │
   │  Verify vacuum  │    │  fs-laser       │    │  cryopump,      │    │  measurement    │
   │  NV baseline    │    │  processing     │    │  thermal recov. │    │  at 10 mK       │
   └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                                                                    │
         │                         Hard interlocks prevent concurrent         │
         │                         LCVD + sensing (IL-01 through IL-14)       │
         └─────────────────────────────────────────────────────────────────────┘
                              Mode C-to-D transition is BLOCKED
                              until all prerequisites are measured.
```

## Current Status

| Metric | Value |
|--------|-------|
| **Gates** | 63 total — 0 PASS, 39 CONDITIONAL, 21 BLOCKED, 2 UNKNOWN, 1 DERIVED_CHECK |
| **Full-cycle MC pass rate** | 0.0% (current), 33.8% (forecast, post-installation) |
| **Hardware** | All components DESIGN_SPECIFIED only. None installed or verified. |
| **Dominant failure mode** | `tau_c` (66% of MC failures) — UNKNOWN on F-diamond at 10 mK |
| **Canonical tau_c threshold** | 292 µs (combined SNR ≥ 5 + ε_thermo < 1%) |
| **Package status** | COMPLETE_DRAFT — ready for technical review |

> **No hardware is installed. No parameter is measured in this system.**
> **No gate reaches PASS from assumptions, simulation, or literature.**

## Quick Start

```bash
# Run the full simulation
python run.py

# Run with consistency check
python run.py --check

# Or using the package directly
python -c "from qta.sim import main; main()"

# Run tests
python -m pytest tests/ -v
```

**Requires:** Python 3.10+ (stdlib only — no third-party packages needed).

## The Four Operating Modes

QTA defines four **mutually exclusive, hardware-interlocked** operating modes
within a single cryogenic chamber:

### Mode A — Cryogenic Baseline / Stabilization
Bring chamber and sample to 10 mK operating state. Verify thermal stability,
vacuum integrity, and NV baseline. **Sensing OFF. LCVD OFF.**

### Mode B — Material Processing / LCVD Growth
Precursor exposure, femtosecond laser processing, pulsed molecular-beam
delivery. **Sensing OFF. Helium ABSENT.** Gates A1-A14 (legacy "A" prefix)
evaluate LCVD feasibility at 10 mK.

### Mode C — Isolation / Purge / Thermal Recovery
Shut off growth inputs, isolate gas lines, cryopump residual species, let
sample thermally relax. Verify contamination limits and vibration settling.

### Mode D — Sensing / Measurement
NV / He-3 isotope measurement at millikelvin condition. **LCVD OFF.**
Precursor below threshold. Gates D1-D18 evaluate sensing feasibility
including thermal, detection, and noise budgets.

## Architecture

```
                   ┌──────────────┐
                   │  Hard       │
                   │  Interlocks │
                   │  IL-01–14   │
                   └──────┬───────┘
                          │ enforces
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
    ▼                     ▼                     ▼
┌──────────┐      ┌──────────────┐      ┌──────────┐
│ Mode B   │      │ Mode C       │      │ Mode D   │
│ Process  │─────▶│ Purge/Recov │─────▶│ Sense    │
│ LCVD ON  │      │ LCVD OFF    │      │ LCVD OFF │
│ He ABSENT│      │ He ABSENT   │      │ He PRESENT│
└──────────┘      └──────────────┘      └──────────┘
```

### Key Physics

- **Thermal:** G_eff (Kapitza conductance via Ag sinter) is ASSUMED = 1e-5 W/K.
  Step-response measurement required. D3/D4/D5 evaluate thermal budget.
- **Vacuum:** Bakeout (250°C/48h) + NEG + cryotrap required for
  P_H2 < 1e-12 Pa and P_CH4 < 5e-14 Pa. D10a/D10b evaluate readiness.
- **Detection:** tau_c (He-3 spin diffusion) is the PRIMARY UNKNOWN.
  D13 evaluates combined SNR threshold at 292 µs.
- **Noise:** Mode-local secondary thermal feedback (D18) bounds thermal,
  vibrational, and charge-state noise contributions.

## Package Structure

```
quantum-thermal-architecture/
├── qta/                        # Main package
│   ├── __init__.py             # Version and docstring
│   ├── constants.py            # Physical constants, param registry, EngStatus
│   ├── model.py                # Dataclasses: Gate, ModeStateVector, SystemState
│   ├── gates.py                # Gate definitions for all four modes
│   ├── monte_carlo.py          # Mode D Monte Carlo simulation
│   ├── engineering.py          # Engineering readiness gates and fixes
│   └── sim.py                  # Orchestrator: run_simulation() and main()
├── tests/                      # Test suite (pytest)
│   ├── test_constants.py       # Constants, EngStatus, gate_status_3layer
│   ├── test_model.py           # Dataclass construction and validation
│   └── test_sim.py             # Integration tests (full simulation run)
├── run.py                      # CLI entry point
├── run_qta_full_sim.py         # Legacy entry point (compatibility shim)
├── package_consistency_check.py# Independent artifact verifier
├── data/                       # CSV/JSON data files (BOM, risk register, etc.)
│   ├── BOM.csv
│   ├── parameter_registry.csv
│   ├── risk_register.csv
│   ├── validation_matrix.csv
│   ├── source_map.csv
│   ├── ... and more
├── outputs/                    # Generated by simulation (gitignored)
├── pyproject.toml
└── README.md
```

## Gate Status Categories

| Status | Meaning |
|--------|---------|
| **PASS** | Hardware VERIFIED and physics condition satisfied. **None in this system.** |
| **CONDITIONAL** | Feasible under assumptions. Needs measurement or installation to advance. |
| **BLOCKED** | Prerequisite hardware or measurement absent. Cannot evaluate. |
| **UNKNOWN** | Cannot be derived; requires experiment. tau_c and C_contr at 10 mK. |
| **DERIVED_CHECK** | First-principles physics check (e.g., Knudsen number). Not a PASS. |
| **FAIL** | Physics condition violated with verified hardware. |

## Three-Layer Engineering Status

```
SPECIFIED  →  Design exists (geometry, materials, equations)
INSTALLED  →  Hardware physically built and present
VERIFIED   →  Measurement confirms performance to spec

          SPECIFIED ≠ INSTALLED ≠ VERIFIED
          PASS requires all three layers.
```

All 24 hardware components in the ENG registry are currently at
**DESIGN_SPECIFIED** only. None are installed or verified.

## The tau_c Bottleneck

tau_c (He-3 spin coherence time on F-terminated diamond at 10 mK) is the
dominant unknown:

- **Canonical threshold:** τ_c ≥ 292 µs (SNR ≥ 5 with pulse dephasing)
- **MC sensitivity rank:** #1 (66.2% of failed samples)
- **He-4 control experiment** (F16) is required before He-3 to establish
  isotope specificity
- **Branch options:** SIL collection (F18) or shallower NV (F17) if τ_c
  is marginal (10-28 µs range)

## Sample Output

```
$ python run.py
============================================================
QTA SIMULATION v3.1 — Same-Chamber Staged Operation
============================================================
GATE COUNTS: 0P | 39C | 0F | 2U | 21B
MC PASS RATE (forecast): 33.3%
DOMINANT FAILURE: tau_c_detection

VERDICT: CONDITIONAL — EXPERIMENTAL VALIDATION REQUIRED
  T_sample (forecast): 10.4131 mK
  tau_c threshold: 292 µs (SNR ≥ 5 + ε_thermo < 1%)
```

## Monte Carlo Summary

| Parameter | Distribution | Dominant Failure |
|-----------|-------------|------------------|
| tau_c | log-U[1 ns, 100 ms] | 66.2% |
| C_contr | U[0.05, 0.20] | secondary |
| G_eff | U[5e-6, 3e-5] W/K | 18.3% |
| T2* | U[5, 20] µs | coupled with tau_c |
| P_H2 | U[5e-13, 2e-12] Pa | 0.1% |
| eta_abs | U[0.02, 0.10] | 0.0% |
| S_vib | U[1e-11, 1e-8] m²/Hz | coupled with eps |

## Related Documents

| Document | Description |
|----------|-------------|
| CLAIMS_BOUNDARY.md | Explicit list of claimed and not-claimed items |
| REVIEWER_COVER_NOTE.md | One-page summary for technical review |
| REVIEWER_QUESTIONS.md | Eight specific technical questions for reviewers |
| FIRST_VALIDATION_EXPERIMENTS.md | Priority-ordered first experiments |
| mode_transition_acceptance_tests.csv | Mode transition test criteria |
| shielding_stack_register.csv | Shielding and isolation stack details |
| risk_register.csv | 107 identified risks |
| BOM.csv | 121-item bill of materials |
| validation_matrix.csv | 157-row validation requirements |
| qta_manuscript_v4.pdf | Full manuscript (LaTeX, ~40 KB source) |

## License

MIT — see [LICENSE](LICENSE) for details.
