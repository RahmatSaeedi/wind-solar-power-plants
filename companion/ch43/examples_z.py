"""Chapter 43, a ninth round: the no-load loss at three voltages and the
knee it shows, load loss at two currents, the energy a late T1 costs
with the plant on T2 alone over the data-pack year, and what T1 teaches
the factory before T2.

Run from the project root:   python -m companion.ch43.examples_z
Writes companion/ch43/expected/z_*.txt and diagrams/data/ch43-noload.csv.
Teaching values (A-462, A-464).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch43 import sources as src
from companion.ch43.common import csv, emit

M = src.MAIN_B


# ------------------------------------------------ no-load at three voltages
def noload(u=(0.9, 1.0, 1.1), p0=(33.8, 42.2, 54.1), i0=(0.07, 0.10, 0.31)):
    n_low = math.log(p0[1] / p0[0]) / math.log(u[1] / u[0])
    n_high = math.log(p0[2] / p0[1]) / math.log(u[2] / u[1])
    csv("ch43-noload.csv", "u,p0,i0", list(zip(u, p0, i0)))
    lines = ["no-load test of T1 at 90, 100 and 110 % voltage (report values)",
             "  voltage pu   P0 kW   I0 %",
             *[f"  {a:10.2f}   {b:5.1f}   {c:4.2f}" for a, b, c in zip(u, p0, i0)],
             f"  loss grows as U^{n_low:.1f} below rated and U^{n_high:.1f} above it;",
             f"  the no-load current triples from 100 to 110 %",
             "  a core near its knee: at 110 % (1.87 T, lesson A) the steel",
             "  starts to saturate - the curve confirms what the flux sum",
             "  predicted and is the evidence behind the over-excitation",
             "  limit the protection holds (ch 25)"]
    emit("z_noload", lines)
    return dict(n_low=n_low, n_high=n_high)


# ------------------------------------------------ load loss at two currents
def loadloss(p_half: float = 72.1, p_full: float = 298.0) -> dict[str, float]:
    ratio = p_full / p_half
    lines = ["load loss of T1 at half and full current (at 75 C, report values)",
             f"  half current {p_half} kW; full current {p_full} kW: ratio {ratio:.2f}",
             "  pure I^2 losses would give exactly 4.00; the small excess",
             "  is stray loss in steel parts, which grows faster than I^2",
             "  where the leakage field saturates them locally - a ratio well",
             "  above 4 would point at a tank or clamp hot spot to look for",
             "  in the heat run's thermography"]
    emit("z_loadloss", lines)
    return dict(ratio=ratio)


# ------------------------------------------------ a late T1
def late(weeks: float = 3.0) -> dict[str, float]:
    from companion.ch15 import sources as s15
    mv = s15.plant_year()["mv"]                     # MW at MV, whole plant
    cap = M["s_mva"] * 0.95                         # one unit, pf 0.95
    lost = np.clip(mv - cap, 0, None)
    year_mwh = float(lost.sum())
    frac = weeks * 7 * 24 / len(mv)
    mwh = year_mwh * frac
    price = 70.0
    lines = [f"T1 held {weeks:.0f} weeks: the plant exports through T2 alone "
             f"({M['s_mva']:.0f} MVA, pf 0.95)",
             f"  hours above {cap:.1f} MW in the data-pack year: "
             f"{int((mv > cap).sum())}",
             f"  energy above it {year_mwh:,.0f} MWh",
             f"  {weeks:.0f} weeks of an average year: {mwh:,.0f} MWh = "
             f"{mwh * price / 1000:.0f} k u at {price:.0f} u/MWh",
             "  small against a hold that finds a wrong tap lead or a PD",
             "  source in the factory; the two-transformer split of ch 18",
             "  is what makes a late unit cheap, and lets commissioning",
             "  (ch 50) begin with T2 alone"]
    emit("z_late", lines)
    return dict(year_mwh=year_mwh, mwh=mwh, k_u=mwh * price / 1000)


# ------------------------------------------------ lessons for T2
ACTIONS = [   # finding on T1, action before T2, evidence
    ("tap lead on the wrong tapping", "second check of tap leads against the drawing",
     "ratio at every tap on T2"),
    ("winding rise over guarantee", "cooling margin reviewed; ducts checked",
     "heat run of T2 read by the cooling curve"),
    ("PD over the limit", "drying end point witnessed", "PD of T2, drying record"),
    ("acetylene after the heat run", "joint records reviewed; brazing qualified",
     "DGA before and after T2's heat run"),
    ("records missing", "traveler holds on burr, drying, recorder", "complete traveler"),
]


def actions() -> int:
    lines = ["what T1 changes before T2 is built (corrective actions)",
             "  finding on T1                  action before T2"]
    for f, a, e in ACTIONS:
        lines.append(f"  {f:30s} {a}")
        lines.append(f"    evidence: {e}")
    lines += [f"  {len(ACTIONS)} actions, each with the evidence that shows it worked on",
              "  T2 - the 8D logic of ch 40 applied to a series of two"]
    emit("z_actions", lines)
    return len(ACTIONS)


if __name__ == "__main__":
    noload()
    loadloss()
    late()
    actions()
