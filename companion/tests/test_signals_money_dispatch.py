"""Tests of plantp.signals, plantp.money, plantp.dispatch and the extreme-value and Markov
helpers of plantp.stats, against hand calculations (chapter 3, third expansion)."""
import math

import numpy as np
import pytest
from scipy.optimize import linprog

from plantp import dispatch, money, signals, stats as st


# ---- signals ----------------------------------------------------------------------
def test_rms_of_sine_is_peak_over_sqrt2():
    t = np.arange(400) / 400
    assert signals.rms(np.sin(2 * np.pi * t)) == pytest.approx(1 / math.sqrt(2), rel=1e-12)


def test_harmonics_recovered_exactly_and_thd():
    t = np.arange(64) / 64
    x = 0.2 + np.sin(2 * np.pi * t) + 0.04 * np.sin(2 * np.pi * 5 * t + 0.3) \
        + 0.03 * np.cos(2 * np.pi * 7 * t)
    a = signals.harmonic_amplitudes(x, 10)
    assert a[0] == pytest.approx(0.2)
    assert a[1] == pytest.approx(1.0)
    assert a[5] == pytest.approx(0.04)
    assert a[7] == pytest.approx(0.03)
    assert a[2] == pytest.approx(0.0, abs=1e-12)
    assert signals.thd(a) == pytest.approx(0.05)


def test_harmonics_refuse_beyond_nyquist():
    with pytest.raises(ValueError):
        signals.harmonic_amplitudes(np.zeros(16), 8)


def test_six_pulse_block_thd_matches_theory():
    n = 3600
    th = (np.arange(n) + 0.5) / n * 2 * np.pi
    x = np.where(np.abs(np.sin(th)) > 0.5, np.sign(np.sin(th)), 0.0)   # 120-degree blocks
    a = signals.harmonic_amplitudes(x, 1000)
    assert a[1] == pytest.approx(2 * math.sqrt(3) / math.pi, rel=1e-4)
    assert a[5] == pytest.approx(a[1] / 5, rel=1e-3)
    assert a[3] == pytest.approx(0.0, abs=1e-6)
    i1 = a[1] / math.sqrt(2)
    theory = math.sqrt(signals.rms(x) ** 2 - i1 ** 2) / i1
    assert theory == pytest.approx(0.3108, abs=2e-4)


def test_alias_and_first_order():
    assert signals.alias_frequency(50, 60) == pytest.approx(10)
    assert signals.alias_frequency(1250, 1000) == pytest.approx(250)
    assert signals.alias_frequency(50, 1000) == pytest.approx(50)
    tau = 2.0
    fc = 1 / (2 * math.pi * tau)
    assert float(signals.first_order_gain(fc, tau)) == pytest.approx(1 / math.sqrt(2))
    assert float(signals.first_order_lag_deg(fc, tau)) == pytest.approx(45.0)


# ---- money ------------------------------------------------------------------------
def test_geometric_sum_and_annuity():
    assert money.geometric_sum(1, 0.5, 4) == pytest.approx(1.875)
    assert money.geometric_sum(3, 1.0, 5) == 15
    af = money.annuity_factor(0.07, 25)
    assert af == pytest.approx(sum(1.07 ** -t for t in range(1, 26)))
    assert money.annuity_factor(0.0, 10) == 10
    assert money.capital_recovery(0.07, 25) * af == pytest.approx(1.0)


def test_present_value_and_discounted_energy():
    assert money.present_value([110.0], 0.10) == pytest.approx(100.0)
    assert money.discounted_energy(100.0, 0.07, 25) == pytest.approx(
        100.0 * money.annuity_factor(0.07, 25))
    e = money.discounted_energy(100.0, 0.0, 3, degradation=0.1)
    assert e == pytest.approx(100 + 90 + 81)


def test_lcoe_hand_case():
    # capex 1000, opex 0, 1 year, 10 % rate, energy 110 -> discounted energy 100
    assert money.lcoe(1000.0, 0.0, money.discounted_energy(110.0, 0.10, 1), 0.10, 1) \
        == pytest.approx(10.0)


# ---- dispatch ---------------------------------------------------------------------
def test_dp_two_hours_by_hand():
    # charge 1 h at price 10, discharge 1 h at price 30; eta = 1, step 1 MWh
    r = dispatch.dp_arbitrage([10, 30], p_max=2, e_min=0, e_max=4, e_start=0, eta=1.0, step=1.0)
    assert r.revenue == pytest.approx(2 * 30 - 2 * 10)
    assert list(r.energy) == [0, 2, 0]


def test_dp_converges_to_lp():
    rng = np.random.default_rng(3)
    price = rng.uniform(20, 80, 12)
    eta, pmax, emin, emax, e0 = 0.9, 5.0, 0.0, 10.0, 5.0
    n = price.size
    tri = np.tril(np.ones((n, n)))
    a_soc = np.hstack([eta * tri, -tri / eta])
    res = linprog(np.concatenate([price, -price]), A_ub=np.vstack([a_soc, -a_soc]),
                  b_ub=np.concatenate([np.full(n, emax - e0), np.full(n, e0 - emin)]),
                  A_eq=np.concatenate([eta * np.ones(n), -np.ones(n) / eta])[None, :],
                  b_eq=[0.0], bounds=[(0, pmax)] * (2 * n), method="highs")
    lp = -res.fun
    coarse = dispatch.dp_arbitrage(price, pmax, emin, emax, e0, eta, 1.0).revenue
    fine = dispatch.dp_arbitrage(price, pmax, emin, emax, e0, eta, 0.125).revenue
    assert coarse <= fine + 1e-9 <= lp + 1e-6
    assert fine == pytest.approx(lp, rel=0.02)


def test_dp_wear_cost_reduces_net_revenue_by_hand():
    # one cycle of 2 MWh at prices 10 then 30, wear 4 per MWh discharged
    r = dispatch.dp_arbitrage([10, 30], 2, 0, 4, 0, 1.0, 1.0, wear=4.0)
    assert r.revenue == pytest.approx(60 - 20 - 8)
    # wear above the spread: doing nothing is best
    r2 = dispatch.dp_arbitrage([10, 30], 2, 0, 4, 0, 1.0, 1.0, wear=25.0)
    assert r2.revenue == pytest.approx(0.0)
    assert list(r2.energy) == [0, 0, 0]


def test_dp_rejects_start_off_grid():
    with pytest.raises(ValueError):
        dispatch.dp_arbitrage([1, 2], 1, 0, 4, 0.3, 1.0, 1.0)


# ---- extremes and Markov ----------------------------------------------------------
def test_gumbel_fit_recovers_parameters():
    rng = np.random.default_rng(7)
    x = rng.gumbel(26.0, 2.5, 20000)
    mu, beta = st.gumbel_fit_moments(x)
    assert mu == pytest.approx(26.0, abs=0.06)
    assert beta == pytest.approx(2.5, abs=0.05)
    mu2, beta2 = st.gumbel_fit_lsq(x)
    assert mu2 == pytest.approx(26.0, abs=0.1)
    assert beta2 == pytest.approx(2.5, abs=0.1)


def test_return_level_and_life_exceedance():
    mu, beta = 26.0, 2.5
    x50 = st.return_level(mu, beta, 50)
    assert float(st.gumbel_cdf(x50, mu, beta)) == pytest.approx(0.98)
    assert st.prob_exceed_in_life(50, 25) == pytest.approx(1 - 0.98 ** 25)
    with pytest.raises(ValueError):
        st.return_level(mu, beta, 1)


def test_markov_two_state_matches_availability():
    lam, mu = 1 / 2000, 1 / 60
    p = np.array([[1 - lam, lam], [mu, 1 - mu]])
    pi = st.markov_stationary(p)
    assert pi[0] == pytest.approx(st.availability(2000, 60))
    assert pi.sum() == pytest.approx(1.0)
    with pytest.raises(ValueError):
        st.markov_stationary([[0.5, 0.4], [0.1, 0.9]])
