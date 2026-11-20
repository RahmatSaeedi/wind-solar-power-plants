"""Tests of plantp.yieldrisk (chapter 16). Hand values in comments."""
import math

import numpy as np
import pytest

from plantp import yieldrisk as un


def test_exceedance_values():
    assert un.z_exceed(0.90) == pytest.approx(1.2816, abs=1e-4)
    assert un.z_exceed(0.99) == pytest.approx(2.3263, abs=1e-4)
    assert un.p_value(300.0, 0.05) == pytest.approx(300 * (1 - 1.2816 * 0.05), abs=0.01)
    assert un.p_value(300.0, 0.05, 0.50) == pytest.approx(300.0)
    # lognormal P90 lies above the normal P90 for the same spread (skew to the right)
    assert un.p_value_lognormal(300.0, 0.10) > un.p_value(300.0, 0.10)


def test_combine_independent_and_correlated():
    assert un.combine([3.0, 4.0]) == pytest.approx(5.0)                  # 3-4-5
    full = [[1, 1], [1, 1]]
    assert un.combine([3.0, 4.0], full) == pytest.approx(7.0)            # adds linearly
    half = [[1, 0.5], [0.5, 1]]
    assert un.combine([3.0, 4.0], half) == pytest.approx(math.sqrt(9 + 16 + 12))
    s = un.shares([3.0, 4.0])
    assert s.sum() == pytest.approx(1.0) and s[1] == pytest.approx(16 / 25)
    assert un.shares([3.0, 4.0], half).sum() == pytest.approx(1.0)


def test_n_year_and_sensitivity():
    assert un.n_year(0.03, 0.04, 1) == pytest.approx(0.05)
    assert un.n_year(0.03, 0.04, 10 ** 6) == pytest.approx(0.03, abs=1e-4)
    v = np.array([5.0, 6.0, 7.0])
    # a cubic curve has a sensitivity close to 3
    cv = np.linspace(0, 20, 2001)
    assert un.sensitivity_ratio(v, cv, cv ** 3) == pytest.approx(3.03, abs=0.02)


@pytest.mark.parametrize("kind", ["normal", "lognormal", "uniform", "triangular"])
def test_sample_mean_and_sd(kind):
    x = un.sample(kind, 0.05, 200_000, np.random.default_rng(1))
    assert x.mean() == pytest.approx(1.0, abs=0.001)
    assert x.std() == pytest.approx(0.05, rel=0.02)


def test_exceedance_and_debt():
    x = np.arange(1, 101, dtype=float)
    assert un.exceedance(x, 0.90) == pytest.approx(10.9)                 # 10th percentile
    assert un.annuity(0.06, 15) == pytest.approx(9.7122, abs=1e-4)
    debt, case = un.debt_size({"P50": 10.0, "P90": 8.0}, {"P50": 1.35, "P90": 1.20}, 0.06, 15)
    assert case == "P90" and debt == pytest.approx(8.0 / 1.20 * 9.7122, abs=1e-3)
