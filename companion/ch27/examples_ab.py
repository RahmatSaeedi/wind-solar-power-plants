"""Chapter 27 - expansion round 12: remedies for the 11th-harmonic
resonance that appears with few units online, each checked over every
unit count, and the alarm threshold of the permanent monitoring.

Run from the project root:   python -m companion.ch27.examples_ab
Writes companion/ch27/expected/ab_*.txt. Teaching values and costs.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import emit

Q_UNIT = 0.15


def z_bus(h: float, n_units: int, filters=(), g_unit: float = 0.0) -> complex:
    """Impedance (ohm) at the 33 kV bus at order h: grid, cables, the
    converters' capacitors, tuned filters (q_mvar, h_tune, quality) and an
    optional damping conductance per converter (MW per unit at h)."""
    n = src.NET
    kv = n["kv_33"]
    x1 = kv ** 2 / n["s_sc_33"] / math.sqrt(1 + 1 / n["xr_33"] ** 2)
    y = 1 / complex(x1 / n["xr_33"], x1 * h)
    y += 1j * h * (n["q_cables"] + n_units * Q_UNIT) / kv ** 2
    y += n_units * g_unit / kv ** 2
    for q_f, h_t, qual in filters:
        xc = kv ** 2 / q_f * h_t ** 2 / (h_t ** 2 - 1)
        xl = xc / h_t ** 2
        y += 1 / complex(xl * h_t / qual, xl * h - xc / h)
    return 1 / y


def worst(filters=(), g_unit=0.0) -> tuple:
    """Largest amplification over the 5th, 7th, 11th and 13th and over
    0-26 units online: (amplification, units, order)."""
    n = src.NET
    x1 = n["kv_33"] ** 2 / n["s_sc_33"] / math.sqrt(1 + 1 / n["xr_33"] ** 2)
    best = (0.0, 0, 0)
    for h in (5, 7, 11, 13):
        zg = abs(complex(x1 / n["xr_33"], x1 * h))
        for k in range(27):
            a = abs(z_bus(float(h), k, filters, g_unit)) / zg
            if a > best[0]:
                best = (a, k, h)
    return best


def remedies() -> None:
    f5 = (src.FILTER["q_mvar"], src.FILTER["h_tune"], src.FILTER["quality"])
    options = [
        ("as built (5th filter out)", (), 0.0, 0, "-"),
        ("5th filter switched in", (f5,), 0.0, 0, "filter already built"),
        ("damped 11th filter 2 Mvar", ((2.0, 10.5, 2.0),), 0.0, 450, "design study, space"),
        ("converter active damping", (), 0.25, 60, "maker's study, test"),
    ]
    lines = ["remedies for the resonance (worst over 0-26 units online and over",
             "  the 5th, 7th, 11th and 13th)",
             "  option                       worst amplification   units   order   cost k u",
             ]
    for name, filt, g, cost, note in options:
        a, k, h = worst(filt, g)
        lines.append(f"  {name:28s} {a:19.1f}   {k:5d}   {h:5d}   {cost:8d}")
    lines += ["  every remedy is judged by its WORST unit count and order,",
              "  not by the all-online case or the order it targets;",
              "  switching the 5th filter in moves the peak but does not",
              "  remove it; the damped 11th filter flattens the 11th but",
              "  leaves a smaller peak at the 7th; active damping grows",
              "  with the units online, so it helps least in the risky",
              "  hours with few units running - cheap only if the maker's",
              "  converters can do it and a test proves it (teaching",
              "  costs; ch 21 weighs them against the energy at risk)"]
    emit("ab_remedy", lines)


def alarms() -> None:
    w = src.week()
    v5 = w["v5_pct"]
    limit = 2.0
    lines = ["alarm threshold for the 5th harmonic voltage (one week, 10-minute values)",
             "  threshold %   values over   alarms (any value)   alarms (3 in a row)",
             ]
    for thr in (1.70, 1.80, 1.90):
        over = v5 > thr
        runs = starts = count = 0
        for o in over:
            count = count + 1 if o else 0
            starts += count == 1
            runs += count == 3
        lines.append(f"  {thr:11.2f}   {int(over.sum()):11d}   {starts:18d}   {runs:19d}")
    lines += [f"  limit {limit:.1f} %: an alarm at 90 % of it rings every",
              "  evening (the network's own evening peak); a higher",
              "  threshold alone gives MORE separate alarms (the runs",
              "  break into pieces), while three values in a row cuts",
              "  the noise without hiding a lasting rise; the threshold",
              "  and the rule are written into the monitoring plan and",
              "  reviewed after the first month"]
    emit("ab_alarms", lines)


if __name__ == "__main__":
    remedies()
    alarms()
