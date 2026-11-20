"""Chapter 27 - expansion round 2: the plant's harmonic share estimated by
regression with a bootstrap interval, a unit's harmonic current by power
bin, the P-Q capability test against the claim, the Q(U) slope measured
from records, and the timing of a fast frequency response.

Run from the project root:   python -m companion.ch27.examples_n
Writes companion/ch27/expected/n_*.txt and diagrams/data/ch27-bins.csv.
Synthetic data and teaching criteria (A-336 to A-339).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit


# [start: regress]
def plant_coefficient(p: np.ndarray, v5: np.ndarray) -> tuple:
    """Fit v5^2 = a + (b p)^2 by least squares on p^2 (background plus
    a plant part that grows with output); returns (sqrt a, b)."""
    x = np.column_stack([np.ones_like(p), p ** 2])
    coef, *_ = np.linalg.lstsq(x, v5 ** 2, rcond=None)
    return math.sqrt(max(coef[0], 0.0)), math.sqrt(max(coef[1], 0.0))
# [end: regress]


def regression() -> None:
    w = src.week()
    sel = (w["hour"] >= 10) & (w["hour"] < 14)
    p, v = w["p_mw"][sel], w["v5_pct"][sel]
    bg, b = plant_coefficient(p, v)
    rng = np.random.default_rng(277)
    boot = []
    for _ in range(500):
        k = rng.integers(0, len(p), len(p))
        boot.append(plant_coefficient(p[k], v[k])[1])
    lo, hi = np.percentile(boot, [5, 95])
    lines = ["the plant's share by regression in the midday hours (10-14 h):",
             f"  {len(p)} ten-minute values; fit v5^2 = a + (b p)^2",
             f"  background sqrt(a) = {bg:.2f} %; plant b = {1000 * b:.2f} % per 1,000 MW",
             f"  90 % bootstrap interval of b: {1000 * lo:.2f} to {1000 * hi:.2f}",
             f"  at 100 MW the plant's own part: {100 * b:.2f} % (interval"
             f" {100 * lo:.2f}-{100 * hi:.2f})",
             "  the synthetic truth is 0.80 % at 100 MW: the estimate is",
             "  close, and the interval says how far one week can be",
             "  trusted - a range, not a single number, goes in the report"]
    emit("n_regression", lines)


def bins() -> None:
    rng = np.random.default_rng(278)
    n = 2000
    load = rng.random(n)
    i_rated = 5292.0
    h5 = 0.012 * i_rated * (0.6 + 0.4 * load) * (1 + 0.15 * rng.standard_normal(n))
    edges = np.arange(0, 1.01, 0.1)
    rows, lines = [], ["a PV inverter's 5th-harmonic current by power bin (two weeks,",
                       "  synthetic 10-minute values; 95th percentile per bin):",
                       "  power bin    values   5th A (95 %)   % of rated"]
    for a, b in zip(edges, edges[1:]):
        m = (load >= a) & (load < b)
        q95 = float(np.percentile(h5[m], 95))
        rows.append((f"{100 * (a + b) / 2:.0f}", f"{q95:.1f}"))
        lines.append(f"  {100 * a:3.0f}-{100 * b:3.0f} %   {int(m.sum()):6d}   {q95:12.1f}   {100 * q95 / i_rated:10.2f}")
    csv("ch27-bins.csv", "bin,i5", rows)
    lines += ["  the amperes grow slowly with output - far slower than the",
              "  fundamental (lesson A); the unit's emission is reported",
              "  per power bin, as the turbine measurement standard does",
              "  (STD-053) - not as one number; the binned table feeds the",
              "  plant's summation of lesson B with the right current at",
              "  each output"]
    emit("n_bins", lines)


def pq_test() -> None:
    claim = {(10, "produce"): 115.0, (50, "produce"): 100.0, (100, "produce"): 52.0,
             (10, "absorb"): -110.0, (50, "absorb"): -95.0, (100, "absorb"): -48.0}
    meas = {(10, "produce"): 118.2, (50, "produce"): 98.1, (100, "produce"): 53.9,
            (10, "absorb"): -111.5, (50, "absorb"): -96.2, (100, "absorb"): -44.0}
    tol = 0.05
    lines = ["P-Q capability test at the POC against the claim (teaching; 5 % tolerance)",
             "  P MW   direction   claimed Mvar   measured Mvar   result"]
    for key in claim:
        c, m = claim[key], meas[key]
        ok = abs(m) >= abs(c) * (1 - tol)
        lines.append(f"  {key[0]:4d}   {key[1]:9s}   {c:12.1f}   {m:13.1f}   {'pass' if ok else 'FAIL'}")
    lines += ["  absorbing at full power falls short (44 against 48 Mvar):",
              "  the record of that point - POC voltage, unit terminal",
              "  voltages, temperatures, any unit at its current limit -",
              "  shows whether the units or the network conditions set the",
              "  limit; the finding goes to the operator with the measured",
              "  conditions and a plan (repeat, or a revised capability)"]
    emit("n_pqtest", lines)


def qu_slope() -> None:
    rng = np.random.default_rng(279)
    dv = rng.uniform(-0.04, 0.04, 200)
    q = -100 * np.where(np.abs(dv) > 0.005, dv - np.sign(dv) * 0.005, 0.0) / 0.05 * 0.33
    q += rng.normal(0, 1.0, 200)
    m = np.abs(dv) > 0.005
    eff = dv[m] - np.sign(dv[m]) * 0.005
    slope = float(np.sum(eff * q[m]) / np.sum(eff * eff))
    lines = ["Q(U) characteristic measured from records (teaching set 33 Mvar per",
             "  5 % voltage, deadband 0.5 %):",
             f"  fitted slope {slope / 100:.2f} Mvar per 1 % voltage outside the deadband",
             f"  set value {-33 / 5:.2f} Mvar per 1 %: within {abs(slope / 100 + 6.6) / 6.6:.1%}",
             "  the sign is negative: the plant absorbs when the voltage",
             "  rises and produces when it falls; the fit needs voltage",
             "  changes from the grid, so the test window is chosen with",
             "  the operator (or a set-point step is used instead)"]
    emit("n_qu", lines)


def ffr() -> None:
    t = np.arange(0, 3, 0.01)
    detect, ramp = 0.25, 0.4
    p = np.where(t < detect, 0.0, np.minimum((t - detect) / ramp, 1.0)) * 20.0
    t_full = float(t[np.argmax(p >= 19.99)])
    lines = ["fast frequency response: timing of a 20 MW battery response (teaching)",
             f"  frequency crosses the trigger at 0 s; detection {detect * 1e3:.0f} ms;",
             f"  ramp to full power over {ramp * 1e3:.0f} ms",
             f"  full response at {t_full:.2f} s; a 1 s requirement: "
             f"{'met' if t_full <= 1.0 else 'not met'}",
             "  the measurement must resolve tens of milliseconds: a",
             "  1-second SCADA record cannot prove it - the test uses a",
             "  fast recorder at the POC, time-stamped from one clock"]
    emit("n_ffr", lines)


if __name__ == "__main__":
    regression()
    bins()
    pq_test()
    qu_slope()
    ffr()
