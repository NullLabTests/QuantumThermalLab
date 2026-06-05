#!/usr/bin/env python3
"""
QTA Simulation — Quantum Thermal Architecture Toolkit.

Run:  python run.py          # full simulation
      python run.py --check  # simulation + consistency check
"""

import sys

from qta.sim import run_simulation, main


def run_check():
    """Run simulation then consistency check."""
    main()
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
        print("consistency check: run 'python package_consistency_check.py'")


if __name__ == "__main__":
    if "--check" in sys.argv:
        run_check()
    else:
        main()
