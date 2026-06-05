#!/usr/bin/env python3
"""Compatibility shim — loads the legacy qta_full_sim.py monolith.

Usage:
    python run_qta_full_sim.py          # one-shot simulation
    python run_qta_full_sim.py --serve  # interactive mode
"""

import sys

if __name__ == "__main__":
    from qta_full_sim import main
    sys.exit(main())
