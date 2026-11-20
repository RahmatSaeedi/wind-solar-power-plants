"""Chapter 27 - expansion round 9: where the converters' switching
frequencies (supraharmonics) flow, DC current from inverters against the
transformer's magnetising current, unbalance from an untransposed line,
and a ripple-control signal sunk by the plant's filter.

Run from the project root:   python -m companion.ch27.examples_x
Writes companion/ch27/expected/x_*.txt and diagrams/data/ch27-supra.csv.
Teaching values (A-337, A-340 and the main transformer of ch 25).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit

W50 = 2 * math.pi * 50


def grid_share(f_hz: float) -> float:
    """Share of a current injected at the 33 kV bus that flows to the grid
    (the rest flows into the cable capacitance), teaching model."""
    n = src.NET
    x1 = n["kv_33"] ** 2 / n["s_sc_33"]
    zg = complex(x1 / n["xr_33"], x1 * f_hz / 50)
    c = n["q_cables"] * 1e6 / (W50 * (n["kv_33"] * 1e3) ** 2)
    zc = 1 / (1j * 2 * math.pi * f_hz * c)
    return abs(zc / (zc + zg))


def supraharmonics() -> None:
    n = src.NET
    f_r = 50 * math.sqrt(n["s_sc_33"] / n["q_cables"])
    freqs = np.logspace(math.log10(100), math.log10(20000), 160)
    csv("ch27-supra.csv", "f,share", [(f"{f:.0f}", f"{grid_share(f):.4f}") for f in freqs])
    lines = ["where a converter's high-frequency current goes (33 kV bus, teaching)",
             f"  grid path (365 MVA, X/R 10) against the cable capacitance (1.77 Mvar):",
             f"  series resonance near {f_r:.0f} Hz",
             "  frequency Hz   share flowing to the grid"]
    for f in (250, 700, 2500, 5000, 9000):
        lines.append(f"  {f:12d}   {grid_share(f):24.2f}")
    lines += ["  near the resonance the grid share is amplified; above it the",
              "  switching frequencies (2-150 kHz, 'supraharmonics') circulate",
              "  between the converters, their own filter capacitors and the",
              "  cables - they rarely reach the POC but can disturb meters,",
              "  power-line signalling and other converters inside the plant;",
              "  they are measured with a different method and band grouping,",
              "  and only if the operator or the plant's own problems ask"]
    emit("x_supra", lines)


def dc_bias() -> None:
    s, v = 5.6e6, 600.0
    i_rated = s / (math.sqrt(3) * v)
    i0_pct = 0.3
    i0_peak = math.sqrt(2) * i_rated * i0_pct / 100
    lines = ["DC current from an inverter against the unit transformer's magnetising",
             f"  current (5.6 MVA, 600 V side: rated {i_rated:.0f} A; magnetising {i0_pct} %,",
             f"  peak {i0_peak:.0f} A; teaching)",
             "  DC % of rated   DC A   DC / magnetising peak"]
    for pct in (0.1, 0.25, 0.5, 1.0):
        idc = i_rated * pct / 100
        lines.append(f"  {pct:13.2f}   {idc:4.0f}   {idc / i0_peak:21.1f}")
    lines += ["  a DC current that is 'only 0.5 % of rated' is larger than",
              "  the peak magnetising current: the core is biased into",
              "  saturation on one half-cycle - noise, heat and even",
              "  harmonics (2nd, 4th) in the measurement; even orders in",
              "  a spectrum are a clue for this or for a half-wave fault",
              "  (lesson C); the inverter's DC limit comes from its",
              "  type test and the transformer maker's tolerance"]
    emit("x_dc", lines)


def line_unbalance() -> None:
    z_asym = 0.03                      # ohm per km, negative-sequence coupling (teaching)
    v_ph = 132e3 / math.sqrt(3)
    i = 437.0
    lines = ["unbalance caused by an untransposed 132 kV line at full current",
             "  (negative-sequence coupling 0.03 ohm/km, teaching)",
             "  line km   V2 V   unbalance %"]
    for km in (7.06, 30.0, 70.0):
        v2 = z_asym * km * i
        lines.append(f"  {km:7.2f}   {v2:5.0f}   {100 * v2 / v_ph:11.2f}")
    lines += ["  Plant P's short line adds almost nothing; a long untransposed",
              "  line adds unbalance in proportion to its length and current,",
              "  and the plant's own converters (which control positive",
              "  sequence) see it as a background they did not cause"]
    emit("x_lineunb", lines)


def ripple() -> None:
    kv = 33.0
    q_f, h_t, qual = src.FILTER["q_mvar"], src.FILTER["h_tune"], src.FILTER["quality"]
    x_net = kv ** 2 / q_f
    xc = x_net * h_t ** 2 / (h_t ** 2 - 1)
    xl = xc / h_t ** 2
    rf = xl * h_t / qual
    xt = 0.12 * kv ** 2 / 63.0
    h_series = math.sqrt(xc / (xl + xt))
    lines = ["a ripple-control signal against the plant's 5th-harmonic filter",
             f"  filter alone: series resonance at h {h_t:.2f}; seen from the 132 kV side",
             f"  through the main transformer (X {xt:.2f} ohm at 50 Hz): h {h_series:.2f}",
             "  signal Hz   h      impedance from 132 kV side ohm (33 kV base)"]
    for f in (183.3, 216.7, 316.7, 1050.0):
        h = f / 50
        z = complex(rf, (xl + xt) * h - xc / h)
        lines.append(f"  {f:9.1f}   {h:4.2f}   {abs(z):45.1f}")
    lines += ["  a teaching signal at 216.7 Hz meets an impedance of a few",
              "  ohms: the filter sinks the operator's signal and the",
              "  receivers nearby may miss their commands; the signal",
              "  frequencies used in the network belong in the filter's",
              "  design data (a blocking circuit or another tuning), and",
              "  the filter is checked from the side the signal comes from"]
    emit("x_ripple", lines)


if __name__ == "__main__":
    supraharmonics()
    dc_bias()
    line_unbalance()
    ripple()
