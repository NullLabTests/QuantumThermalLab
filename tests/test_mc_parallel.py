"""Tests for the parallel MC module."""

from qta.mc_parallel import _sample_one, run_parallel_MC


def test_sample_one_returns_dict():
    """Single MC sample returns well-formed dict."""
    result = _sample_one((42, None))
    assert isinstance(result, dict)
    assert "pass" in result
    assert "snr" in result
    assert "ts_mK" in result
    assert result["snr"] > 0
    assert result["ts_mK"] > 0


def test_parallel_mc_runs():
    """Parallel MC runs and returns results."""
    mc = run_parallel_MC(N=100)
    assert mc["N"] == 100
    assert mc["pass_total"] <= 100
    assert 0 <= mc["pass_rate"] <= 1
    assert isinstance(mc["dominant_failure"], str)


def test_parallel_mc_fail_reasons():
    """Parallel MC identifies dominant failure modes."""
    mc = run_parallel_MC(N=500)
    total_fails = sum(mc["fail_reasons"].values())
    assert total_fails == mc["N"] - mc["pass_total"]


def test_parallel_mc_best():
    """Best sample has highest SNR among passes."""
    mc = run_parallel_MC(N=200)
    if mc["best"]:
        assert mc["best"]["snr"] > 0
        assert mc["best_SNR"] > 0
