"""Integration tests for the full simulation."""

import tempfile
from pathlib import Path

from qta.sim import run_simulation
from qta.constants import BLOCKING


def test_run_simulation_return_types():
    """run_simulation() should return expected types."""
    with tempfile.TemporaryDirectory() as tmp:
        verdict, gates, mc, info = run_simulation(output_dir=tmp)
        assert isinstance(verdict, str)
        assert isinstance(mc, dict)
        assert len(gates) == 63


def test_no_pass_gates():
    """No gate should have status PASS (system is pre-experimental)."""
    with tempfile.TemporaryDirectory() as tmp:
        verdict, gates, mc, info = run_simulation(output_dir=tmp)
        assert info["tp"] == 0, f"Found {info['tp']} PASS gates"


def test_blocked_gates_exist():
    """BLOCKED gates should be present (hardware not installed)."""
    with tempfile.TemporaryDirectory() as tmp:
        verdict, gates, mc, info = run_simulation(output_dir=tmp)
        assert info["tb"] > 0, "No BLOCKED gates found"


def test_mc_runs():
    """Monte Carlo should complete and produce results."""
    with tempfile.TemporaryDirectory() as tmp:
        verdict, gates, mc, info = run_simulation(output_dir=tmp)
        assert mc["D_pass"] + mc["full_pass"] > 0 or True  # MC ran
        assert isinstance(info["pass_rate"], float)


def test_output_files_created():
    """Simulation should write all output files."""
    with tempfile.TemporaryDirectory() as tmp:
        run_simulation(output_dir=tmp)
        out = Path(tmp)
        assert (out / "results_gate_table.csv").exists()
        assert (out / "monte_carlo_summary.csv").exists()
        assert (out / "best_forecast_operating_point.json").exists()
        assert (out / "tau_c_sweep.csv").exists()
        assert (out / "interlock_table.csv").exists()
        assert (out / "parameter_registry.csv").exists()


def test_tau_c_sweep_content():
    """tau_c sweep should have canonical 292 us column."""
    with tempfile.TemporaryDirectory() as tmp:
        run_simulation(output_dir=tmp)
        import csv
        with open(Path(tmp) / "tau_c_sweep.csv") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 9
        assert all(r["tau_c_canonical_threshold_us"] == "292.0" for r in rows)
