"""Chapter 27 - expansion round 5: harmonic current a converter draws
because of the grid's background voltage (response, not emission),
reactive capability at the edges of the voltage band, flagged intervals
in the weekly statistics, and verifying a corrective action with
before/after data.

Run from the project root:   python -m companion.ch27.examples_s
Writes companion/ch27/expected/s_*.txt and diagrams/data/ch27-beforeafter.csv.
Synthetic data and teaching values (A-336 to A-340).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import pq


def response() -> None:
    emission = 1.2                              # % of rated, the unit's own 5th
    lines = ["a converter's measured 5th current: its own emission plus the current",
             "  the grid's background 5th voltage drives into its filter (teaching)",
             "  background V5 %   converter Z5 pu   driven %   measured % (random sum)"]
    for v5 in (0.5, 1.0, 2.0):
        for z5 in (0.15, 0.40):
            driven = v5 / z5
            meas = math.hypot(emission, driven)
            lines.append(f"  {v5:15.1f}   {z5:15.2f}   {driven:8.1f}   {meas:22.1f}")
    lines += ["  with a low-impedance output filter most of the 'emission'",
              "  measured at the terminals is the grid's background flowing",
              "  in: the converter acts as a sink, not a source; an emission",
              "  test is done with the background known (or measured before",
              "  and after), and the maker's harmonic impedance is part of",
              "  the evidence"]
    emit("s_response", lines)


def band_capability() -> None:
    s_units, p = 121.0, 100.0
    lines = ["reactive capability at full power across the voltage band",
             "  (units current-limited: apparent power scales with voltage)",
             "  voltage pu   units S MVA   units Q at 100 MW Mvar"]
    for v in (0.90, 0.95, 1.00, 1.05, 1.10):
        s = s_units * v
        q = math.sqrt(max(s * s - p * p, 0.0))
        lines.append(f"  {v:10.2f}   {s:11.1f}   {q:22.1f}")
    lines += ["  at 0.9 pu the units give 43 Mvar instead of 68 - just when",
              "  a low voltage asks for more; the requirement is checked at",
              "  the band's edges; a capability chart drawn at 1.0 pu",
              "  promises too much at low voltage (ch 28 tests the corners)"]
    emit("s_band", lines)


def flagging() -> None:
    w = src.week()
    v5 = w["v5_pct"].copy()
    rng = np.random.default_rng(280)
    flagged = np.zeros(len(v5), bool)
    for k in rng.choice(len(v5), 40, replace=False):           # a stormy week
        flagged[k] = True
        v5[k] = 4.5 + rng.random()                 # distorted by a dip in that interval
    lines = ["flagged intervals in the weekly statistics (synthetic)",
             f"  {int(flagged.sum())} ten-minute intervals contain a dip; their harmonic",
             "  values are distorted by the event itself",
             f"  95th percentile with them: {pq.percentile(v5, 95):.2f} %",
             f"  95th percentile without them (flagged out): {pq.percentile(v5[~flagged], 95):.2f} %",
             "  the measurement method flags intervals with dips, swells",
             "  or interruptions so that one event does not appear as",
             "  harmonic distortion (STD-034); the report states how many",
             "  were flagged"]
    emit("s_flagging", lines)


def before_after() -> None:
    rng = np.random.default_rng(281)
    before = 1.9 + 0.25 * rng.standard_normal(1008)
    after = 1.5 + 0.25 * rng.standard_normal(1008)
    b95, a95 = pq.percentile(before, 95), pq.percentile(after, 95)
    diffs = []
    for _ in range(400):
        diffs.append(pq.percentile(rng.choice(before, 1008), 95) - pq.percentile(rng.choice(after, 1008), 95))
    lo, hi = np.percentile(diffs, [5, 95])
    csv("ch27-beforeafter.csv", "v,before,after",
        [(f"{x:.2f}",) + tuple(f"{np.mean(arr <= x):.3f}" for arr in (before, after))
         for x in np.arange(0.8, 2.8, 0.05)])
    lines = ["verifying a corrective action (filter retuned): one week before and after",
             f"  95th percentile of V5: before {b95:.2f} %, after {a95:.2f} %",
             f"  reduction {b95 - a95:.2f} % (90 % bootstrap interval {lo:.2f} to {hi:.2f})",
             "  teaching acceptance: after-week 95th percentile below 2.0 %",
             f"  and a reduction whose interval excludes zero: {'accepted' if a95 < 2.0 and lo > 0 else 'not yet'}",
             "  the same network state and season are needed for the",
             "  comparison to mean anything; the acceptance rule is set",
             "  before the 'after' week, not fitted to its result"]
    emit("s_beforeafter", lines)


if __name__ == "__main__":
    response()
    band_capability()
    flagging()
    before_after()
