"""Chapter 37: performance, availability and reliability tools against hand
calculations."""
import math

import numpy as np

from plantp import performance as pf


def test_pr_and_temperature_correction():
    # 60,000 kWp, 150 MWh in a day of 3.0 kWh/m2: PR = 2.5 / 3.0
    assert abs(pf.performance_ratio(150_000, 60_000, 3.0) - 2.5 / 3.0) < 1e-12
    # hotter than 25 C lowers PR; the correction raises it back
    assert pf.pr_temperature(0.80, 45.0) > 0.80
    assert abs(pf.pr_temperature(0.80, 25.0) - 0.80) < 1e-12


def test_availability_definitions():
    assert abs(pf.time_availability(700, 720, 20) - 1.0) < 1e-12
    assert abs(pf.energy_availability(900, 100) - 0.9) < 1e-12
    assert abs(pf.energy_availability(900, 100, 100) - 1.0) < 1e-12


def test_event_cleaning():
    ev = [(0, 2), (0, 2), (1, 3), (5, None), (8, 12), (11, 9)]
    assert pf.merge_events(ev, 0, 10) == [(0, 3), (8, 10)]
    assert pf.event_hours(ev, 0, 10) == 5


def test_cusum_finds_a_drop():
    r = np.r_[np.zeros(20), -np.ones(20)]
    assert pf.cusum(r, k=0.25, h=2.0) == 22


def test_mtbf_and_interval():
    assert pf.mtbf_censored([1000, 3000], [4000, 4000]) == 6000
    lo, hi = pf.rate_interval(2, 12_000, 0.9)
    assert lo < 2 / 12_000 < hi


def test_weibull_recovers_shape():
    rng = np.random.default_rng(1)
    t = 1000 * rng.weibull(2.0, 400)
    k, lam = pf.weibull_mle(t, [])
    assert abs(k - 2.0) < 0.25 and abs(lam - 1000) < 80


def test_crow_amsaa_and_service():
    times = np.array([100.0, 300, 600, 1000])
    beta = pf.crow_amsaa_beta(times, 1000.0)
    assert abs(beta - 4 / np.sum(np.log(1000 / times))) < 1e-12
    t = np.arange(0, 10.0, 0.1)
    r = 1 - np.exp(-t / 1.0)
    t90, ts = pf.response_times(t, r, 0.0, 1.0, 0.02)
    assert abs(t90 - 2.4) < 0.11 and abs(ts - 4.0) < 0.11
    rms, mx = pf.tracking_error([1, 1, 1], [1, 2, 1])
    assert abs(rms - math.sqrt(1 / 3)) < 1e-12 and mx == 1
