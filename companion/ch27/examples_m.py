"""Chapter 27 - expansion round 1: a year of voltage dips at the POC in a
depth-duration table, the transient of energising the filter, the
plant's emission against a teaching allocation, the amplification of
background harmonics by a resonance, and aligning two instruments'
clocks by cross-correlation.

Run from the project root:   python -m companion.ch27.examples_m
Writes companion/ch27/expected/m_*.txt. Teaching values A-336 to A-340.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import emit
from plantp import irradiance as irr
from plantp import pq


def dips() -> None:
    rng = np.random.default_rng(275)
    n = 40
    depth = np.clip(10 + rng.beta(1.5, 4.0, n) * 90, 10, 95)    # % of voltage lost (dip >= 10 %)
    dur = np.exp(rng.normal(math.log(0.12), 0.9, n))              # s
    rows = [(5, 30), (30, 60), (60, 70), (70, 80), (80, 90)]
    cols = [(0.02, 0.2), (0.2, 0.5), (0.5, 1.0), (1.0, 5.0)]
    lines = ["a year of voltage dips at the POC (synthetic, 40 events):",
             "  remaining voltage %   0.02-0.2 s   0.2-0.5 s   0.5-1 s   1-5 s"]
    for lo, hi in rows:
        resid = 100 - depth
        counts = [int(np.sum((resid >= lo) & (resid < hi) & (dur >= a) & (dur < b))) for a, b in cols]
        lines.append(f"  {lo:7d} - {hi:3d} %        " + "   ".join(f"{c:7d}" for c in counts))
    worst = float((100 - depth).min())
    lines += [f"  deepest dip leaves {worst:.0f} % voltage; most dips are shallow and short",
              "  (faults on the network cleared by its protection): each",
              "  cell is compared with the ride-through envelope (ch 26) -",
              "  a plant that trips on dips the envelope covers fails its",
              "  requirement, and the dip table is the evidence of what the",
              "  network delivers"]
    emit("m_dips", lines)


def energising() -> None:
    n = src.NET
    f = src.FILTER
    h_res = math.sqrt(n["s_sc_33"] / (f["q_mvar"] + n["q_cables"]))
    i_rated = f["q_mvar"] * 1e6 / (math.sqrt(3) * 33e3)
    i_peak = math.sqrt(2) * i_rated * h_res
    lines = ["energising the 5 Mvar filter at the 33 kV bus (teaching):",
             f"  ringing frequency ~ 50 x sqrt(S_sc / Q) = {50 * h_res:.0f} Hz",
             f"  rated current {i_rated:.0f} A; inrush peak ~ sqrt2 x I x h = {i_peak:,.0f} A",
             "  bus voltage overshoot up to about 2 pu at the worst instant",
             "  (lightly damped); switching at voltage zero (controlled",
             "  switching) or a pre-insertion resistor keeps it near 1.1 pu",
             "  the transient is a power-quality event too: the operator's",
             "  limit for switching transients applies, and sensitive loads",
             "  nearby may notice it"]
    emit("m_energise", lines)


def allocation() -> None:
    planning, s_i, s_t, alpha = 3.0, 100.0, 600.0, 1.4
    share = planning * (s_i / s_t) ** (1 / alpha)
    z5 = 5 * 132 ** 2 / src.NET["s_sc_poc"]
    i5_33 = 13.0                                     # partly random sum, lesson B
    i5_132 = i5_33 * 33 / 132
    v5 = 100 * i5_132 * z5 / (132e3 / math.sqrt(3))
    lines = ["the plant's 5th-harmonic emission against a teaching allocation",
             f"  teaching planning level {planning} %; plant {s_i:.0f} of {s_t:.0f} MVA of the",
             f"  network's capacity; allocation ~ L x (S_i / S_t)^(1/alpha) = {share:.2f} %",
             f"  plant 5th current {i5_33} A at 33 kV -> {i5_132:.2f} A at 132 kV",
             f"  POC impedance at the 5th: 5 x 132^2 / 1,500 = {z5:.1f} ohm",
             f"  emission voltage {v5:.3f} % - inside the allocation",
             "  the allocation method and its numbers are the operator's",
             "  (STD-130 describes the approach); a resonance near the 5th",
             "  would multiply the impedance and change the answer - so the",
             "  scan of lesson B comes first"]
    emit("m_allocation", lines)


def amplification() -> None:
    n = src.NET
    h = np.array([5.0, 7.0, 11.0, 13.0])
    z_grid = h * n["kv_33"] ** 2 / n["s_sc_33"]
    lines = ["background harmonics amplified at the 33 kV bus (teaching)",
             "  the grid brings a background voltage behind its impedance;",
             "  the bus voltage is that background times Z_bus / (h X)",
             "  order   cables only   with 5 Mvar capacitor   with filter"]
    cases = []
    for q, filt in ((n["q_cables"], None), (n["q_cables"] + 5.0, None),
                    (n["q_cables"], (src.FILTER["q_mvar"], src.FILTER["h_tune"], src.FILTER["quality"]))):
        cases.append(pq.scan(h, n["s_sc_33"], n["xr_33"], q, n["kv_33"], filt) / z_grid)
    for k, hh in enumerate(h):
        lines.append(f"  {hh:5.0f}   {cases[0][k]:11.2f}   {cases[1][k]:21.2f}   {cases[2][k]:11.2f}")
    lines += ["  with the plain capacitor the 7th background is amplified",
              "  about tenfold: 0.6 % upstream becomes some 6 % at the bus,",
              "  without the plant emitting anything - the complaint of",
              "  lab C could come from a capacitor, not from the converters",
              "  the filter attenuates the 5th and 7th below 1"]
    emit("m_amplify", lines)


def clocks() -> None:
    w = src.week()
    p = w["p_mw"]
    shifted = np.roll(p, 3) + np.random.default_rng(276).normal(0, 0.5, len(p))
    lag = irr.best_lag(shifted, p, 12)
    lines = ["aligning a PQ instrument with SCADA by cross-correlation",
             "  the instrument's 10-minute active power against SCADA's,",
             f"  shifted by up to +/- 2 hours: best lag {lag} samples = {10 * lag} minutes",
             "  the instrument's clock was set wrong by half an hour; every",
             "  comparison with plant output (lab D) would be blurred by",
             "  it - align first, then compare; and record the offset and",
             "  how it was found in the investigation file"]
    emit("m_clocks", lines)


if __name__ == "__main__":
    dips()
    energising()
    allocation()
    amplification()
    clocks()
