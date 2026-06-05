"""Tests for the sweep module."""

import tempfile
from qta.sweep import (
    sweep_tau_c, sweep_parameter, sensitivity_ranking,
)


def test_sweep_tau_c_returns_points():
    """tau_c sweep returns 9 points with SNR data."""
    results = sweep_tau_c()
    assert len(results) == 9
    for r in results:
        assert "tau_c_s" in r
        assert "SNR" in r
        assert r["SNR"] >= 0


def test_sweep_tau_c_threshold():
    """At 292 us, SNR should be >= 5 (threshold)."""
    results = sweep_tau_c()
    threshold = [r for r in results if abs(r["tau_c_s"] - 292e-6) < 1e-9]
    assert len(threshold) == 1
    assert threshold[0]["pass"]


def test_sweep_G_eff():
    """G_eff sweep produces expected parameter."""
    vals = [1e-6, 1e-5, 1e-4]
    results = sweep_parameter("G_eff", vals)
    assert len(results) == 3
    assert results[0]["param"] == "G_eff"
    assert results[0]["T_sample_mK"] > 0


def test_sweep_eta_abs():
    """eta_abs sweep: higher eta_abs -> higher T_sample."""
    vals = [0.01, 0.10]
    results = sweep_parameter("eta_abs", vals)
    assert results[1]["T_sample_mK"] > results[0]["T_sample_mK"]


def test_sweep_with_output():
    """Sweep writes CSV when output path given."""
    with tempfile.TemporaryDirectory() as tmp:
        out = tmp + "/sweep.csv"
        p = sweep_parameter("G_eff", [1e-5, 2e-5], output=out)
        assert p.exists()
        lines = p.read_text().strip().split("\n")
        assert len(lines) == 3  # header + 2 data


def test_sensitivity_ranking_returns_list():
    """Sensitivity ranking returns sorted list of parameters."""
    ranking = sensitivity_ranking()
    assert len(ranking) >= 4
    params = {r["parameter"] for r in ranking}
    assert "tau_c" in params  # tau_c is always ranked
    assert "G_eff" in params
    for r in ranking:
        assert r["dSNR_dP_norm"] >= 0
        assert r["dT_dP_norm"] >= 0
