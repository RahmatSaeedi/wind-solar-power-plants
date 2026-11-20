"""Chapter 37 labs: the planted problems are found and the event-log
reconciliation behaves as the chapter says."""
import numpy as np

from companion.ch37 import lab_c, lab_e, sources as src
from companion.ch37.examples_c import curve


def test_operating_year_planted_problems():
    y = src.operating_year()
    apr = y["month"] == 3
    jun_out = (y["day"] >= 160) & (y["day"] < 169)
    assert y["soil"][apr].max() > 0.059
    assert np.all(y["outage"] == jun_out)
    oct_bad = (y["day"] >= 285) & (y["day"] < 305)
    ratio = y["poa_sensor"][oct_bad].sum() / y["poa_true"][oct_bad].sum()
    assert abs(ratio - 0.92) < 1e-9


def test_daily_ratio_sees_june_outage():
    y = src.operating_year()
    rows = lab_c.daily_ratio(y, 5)                    # June: (day, ratio, PRs)
    out = (rows[:, 0] >= 160) & (rows[:, 0] < 169)
    assert np.nanmax(rows[out, 1]) < 0.92
    assert np.nanmin(rows[~out, 1]) > 0.95


def test_october_sensor_fault_raises_pr_only():
    y = src.operating_year()
    rows = lab_c.daily_ratio(y, 9)
    bad = (rows[:, 0] >= 285) & (rows[:, 0] < 305)
    assert np.nanmean(rows[bad, 2]) > np.nanmean(rows[bad, 3]) * 1.05
    assert abs(np.nanmean(rows[bad, 1]) - 1.0) < 0.02


def test_cleaning_removes_duplicates_but_not_missing_ends():
    truth, log = lab_e.event_log()
    a_t, n_t, _ = lab_e.metrics(truth, 3)
    a_c, n_c, _ = lab_e.metrics(log, 3)
    assert n_c < n_t            # three outages lost with their end times
    assert a_c > a_t            # so the cleaned log is optimistic


def test_shared_outage_counts_once_per_turbine():
    truth, _ = lab_e.event_log()
    _, n0, _ = lab_e.metrics(truth, 3)
    sub = [[t, 4000.0, 4010.0, 4010.0] for t in range(12)]
    _, n1, _ = lab_e.metrics(truth + sub, 3)
    assert n1 - n0 <= 12


def test_power_curve_shape():
    assert curve(2.0) == 0.0
    assert curve(12.0) == 5.0
    assert 0 < curve(8.0) < 5.0
    assert curve(26.0) == 0.0
