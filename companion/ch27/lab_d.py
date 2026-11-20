"""Chapter 27, lab D - analysis of a synthetic measurement week at the
POC: power factor, the 5th-harmonic voltage against plant output, why a
plain 'plant on / plant off' comparison misleads when the background
has its own daily pattern, a comparison within the same hours, and the
evidence still needed (worked example 2).

Run from the project root:   python -m companion.ch27.lab_d
Writes companion/ch27/expected/d_*.txt and diagrams/data/ch27-week.csv.
Synthetic data (A-338).
"""
from __future__ import annotations

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import pq


def overview() -> None:
    w = src.week()
    pf = w["p_mw"] / np.hypot(w["p_mw"], w["q_mvar"])
    busy = w["p_mw"] > 5
    lo_cut, hi_cut = np.quantile(w["p_mw"], [1 / 3, 2 / 3])
    for name, sel in (("ch27-weekhigh.csv", w["p_mw"] >= hi_cut), ("ch27-weeklow.csv", w["p_mw"] <= lo_cut)):
        csv(name, "hour,v5", [(f"{a:.2f}", f"{b:.3f}") for a, b in zip(w["hour"][sel], w["v5_pct"][sel])])
    lines = ["the measurement week at the POC (1,008 ten-minute values, A-338):",
             f"  plant output: mean {w['p_mw'].mean():.1f} MW, max {w['p_mw'].max():.1f} MW",
             f"  power factor while producing (> 5 MW): mean {pf[busy].mean():.3f}, lowest {pf[busy].min():.3f}",
             f"  5th-harmonic voltage: mean {w['v5_pct'].mean():.2f} %, 95th percentile"
             f" {pq.percentile(w['v5_pct'], 95):.2f} %"]
    emit("d_overview", lines)


# [start: compare]
def compare(w: dict, hours: tuple | None) -> tuple:
    """Mean 5th-harmonic voltage in the top and bottom thirds of plant
    output, using only the given hours of the day (None: all hours)."""
    sel = np.ones(len(w["p_mw"]), bool) if hours is None else \
        (w["hour"] >= hours[0]) & (w["hour"] < hours[1])
    p, v = w["p_mw"][sel], w["v5_pct"][sel]
    lo_cut, hi_cut = np.quantile(p, [1 / 3, 2 / 3])
    high, low = p >= hi_cut, p <= lo_cut
    return v[high].mean(), v[low].mean(), p[high].mean(), p[low].mean()
# [end: compare]


def confounding() -> None:
    w = src.week()
    r_all = float(np.corrcoef(w["p_mw"], w["v5_pct"])[0, 1])
    lines = ["plant high against plant low - first plainly, then within the same hours",
             f"  correlation of V5 with plant output over the week: {r_all:+.2f}",
             "  comparison (top/bottom third)   V5 high %   V5 low %   P high/low MW"]
    for name, hours in (("all hours (plain)", None), ("10-14 h only", (10, 14)), ("0-5 h only", (0, 5))):
        a, b, pa, pb = compare(w, hours)
        lines.append(f"  {name:31s} {a:9.2f}   {b:8.2f}   {pa:6.0f}/{pb:<6.0f}")
    true_share = float(np.mean(w["plant5_pct"][w["p_mw"] > 60]))
    lines += ["  the plain comparison makes the plant look harmless, even",
              "  helpful: the background's evening peak falls in hours of",
              "  low PV output; within the same hours the plant's share",
              f"  shows (the synthetic truth: {true_share:.2f} % of its own when above",
              "  60 MW, adding in power with the background) - time of day",
              "  is a confounder, and the comparison must hold it fixed (or",
              "  switch the plant off at a fixed hour)"]
    emit("d_confounding", lines)


def evidence() -> None:
    items = ["harmonic CURRENTS at the POC and at the units, not only voltages",
             "a planned on/off (or step) test at a fixed hour and a fixed",
             "network state, agreed with the operator",
             "the switching log of the network (capacitor banks, lines)",
             "the neighbour's own load and capacitor status",
             "transducer data at the 5th and 7th (lesson A)",
             "a longer period covering weekdays, weekends and seasons"]
    lines = ["worked example 2: the measurements needed before any conclusion"]
    lines += [f"  - {x}" for x in items]
    lines += ["  the week shows a correlation inside fixed hours, which is",
              "  a lead, not a proof; the report says 'consistent with a",
              "  plant contribution growing with output, to be confirmed',",
              "  and lists these items as its next steps"]
    emit("d_evidence", lines)


if __name__ == "__main__":
    overview()
    confounding()
    evidence()
