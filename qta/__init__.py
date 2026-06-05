"""
Quantum Thermal Architecture (QTA) Simulation Toolkit.

A pre-experimental, mode-separated feasibility framework for same-chamber
NV/He-3 quantum sensing and material processing at millikelvin temperatures.

Modes:
  A - Cryogenic Baseline / Stabilization
  B - Material Processing / LCVD Growth
  C - Isolation / Purge / Thermal Recovery
  D - Sensing / Measurement (NV / He-3)

Status: BLOCKED (no hardware installed or verified).

Usage:
    python run.py                          # full dashboard
    python -c "from qta.sim import main; main()"
"""

__version__ = "3.1.0"
__all__ = ["__version__"]
