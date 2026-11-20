"""Chapter 33, lesson M (baseline, more): study areas set by each impact's
reach, a soil baseline that keeps natural metals from looking like
pollution, road-traffic noise past the village, an oil spill outside a
bund, and the register of environmental permits on the critical path.

Run from the project root:   python -m companion.ch33.examples_m
Writes companion/ch33/expected/m_*.txt and diagrams/data/ch33-traffic.csv,
ch33-permits.csv. Teaching values (A-376, A-383); the permits, their lead
times and the soil screening values are PLACEHOLDERS (U-112).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch33 import sources as src  # noqa: F401  (path set-up)
from companion.ch33.common import csv, emit


def study_areas() -> None:
    rows = [("noise", "2 km from any turbine", "below background beyond"),
            ("shadow flicker", "1.5 km (10 rotor diameters)", "too faint beyond"),
            ("raptors", "10 km around the nest", "range of a pair"),
            ("bats", "site + 2 km", "routes, roosts"),
            ("landscape", "20 km (visibility)", "a dot beyond"),
            ("water", "the aquifer (20 km2)", "shared resource"),
            ("traffic", "route from port to site", "where trucks are"),
            ("social", "village, camps, strips", "who is affected")]
    lines = ["study area of each topic: set by the reach of the impact (teaching)",
             "  topic            study area                     reason"]
    for t, a, r in rows:
        lines.append(f"  {t:16s} {a:30s} {r}")
    lines += ["  a single fence-line boundary would miss the aquifer, the",
              "  raptors' range and the haul route; each topic's boundary",
              "  is written down with its reason at scoping, so a reviewer",
              "  can see why a receptor is in or out"]
    emit("m_areas", lines)


def soil_baseline(seed: int = 331) -> None:
    rng = np.random.default_rng(seed)
    ni = rng.lognormal(math.log(55.0), 0.30, 12)          # mg/kg, 12 baseline samples
    mean, sd = ni.mean(), ni.std(ddof=1)
    upper = float(np.exp(np.log(ni).mean() + 1.80 * np.log(ni).std(ddof=1)))
    screen = 60.0                                          # PLACEHOLDER screening value
    after = [41.0, 55.0, 72.0, 118.0]                      # cells after a fire, teaching
    lines = ["soil baseline before construction: nickel in 12 samples (synthetic)",
             f"  mean {mean:.1f} mg/kg, sd {sd:.1f}; upper baseline {upper:.0f}"
             " (mean + 1.8 sd of the logs)",
             f"  screening value of the permit (PLACEHOLDER): {screen:.0f} mg/kg",
             "  cell after a fire   result   above baseline?   above screen?"]
    for k, v in enumerate(after, 1):
        lines.append(f"  {k:17d}   {v:6.0f}   {'yes' if v > upper else 'no':>15s}"
                     f"   {'yes' if v > screen else 'no':>13s}")
    natural = [k for k, v in enumerate(after, 1) if screen < v <= upper]
    real = [k for k, v in enumerate(after, 1) if v > upper and v > screen]
    lines += [f"  the ground is naturally rich in nickel: cell(s) {natural} are",
              "  above the generic screen but inside the baseline - without",
              "  the baseline they would be dug out for nothing; only",
              f"  cell(s) {real} stand out from both, so only they are excavated",
              "  and re-tested (lesson E) - the baseline is sampled before",
              "  the first bulldozer, never after"]
    emit("m_soil", lines)


def traffic_noise() -> None:
    light0, heavy0 = 360, 40            # vehicles a day on the village road (survey, teaching)
    trucks, buses_cars = 116, 60        # project, peak month (ch 32 lesson G)
    w = 10.0                            # one heavy vehicle ~ ten light ones (teaching weighting)
    base = light0 + w * heavy0
    rows = [("baseline", base),
            ("+ buses and cars", base + buses_cars),
            ("+ trucks (peak month)", base + buses_cars + w * trucks),
            ("+ trucks, school hours held", base + buses_cars + w * trucks)]
    lines = ["road traffic noise past the village: change from the baseline",
             f"  baseline {light0} light + {heavy0} heavy a day; one heavy ~"
             f" {w:.0f} light (teaching)",
             "  case                             equivalent flow   change dB"]
    out = []
    for k, (name, q) in enumerate(rows[:3], 1):
        dl = 10 * math.log10(q / base)
        out.append((k, round(dl, 1)))
        lines.append(f"  {name:32s} {q:15,.0f}   {dl:9.1f}")
    csv("ch33-traffic.csv", "case,db", out)
    dl = 10 * math.log10(rows[2][1] / base)
    lines += [f"  the trucks raise the daily road noise by {dl:.1f} dB - more",
              "  than the 3 dB a resident notices as a clear change; the",
              "  cars and buses alone add almost nothing. Holding trucks",
              "  in school hours moves them, it does not remove them: the",
              "  daily level is the same, so the remedy for noise is a",
              "  speed limit, a smooth surface and no night convoys",
              "  through the village except the abnormal loads (ch 31)"]
    emit("m_traffic", lines)


def spill() -> None:
    oil_l = 2_000.0                    # spilt during top-up, outside the bund (teaching)
    retention = 30.0                   # L of oil held per m3 of sandy soil (teaching)
    soil_m3 = oil_l / retention
    density = 1.7                      # t/m3
    bund = 22.0 * 1.10 + 0.10 * 6 * 9  # 110 % of the oil + 100 mm of rain on a 6 x 9 m bund
    lines = ["an oil spill outside a bund and what it costs (teaching)",
             f"  spill: {oil_l:,.0f} L of transformer oil on sandy ground",
             f"  soil holds about {retention:.0f} L/m3: contaminated soil about"
             f" {soil_m3:.0f} m3 = {soil_m3 * density:.0f} t",
             f"  the same spill inside a bund of {bund:.1f} m3 (110 % of 22 m3 +"
             " 100 mm rain): 0 m3",
             "  response, in order: stop the source, contain (pads,",
             "    a sand bund), report, recover free oil, excavate,",
             "    test the walls and floor of the hole, record",
             "  a few hours of top-up outside the bund on a drip tray",
             "  and a hardstand avoid a hundred tonnes of hazardous",
             "  waste: the method statement (ch 49) puts the work where",
             "  a spill cannot reach the ground; the inventory and spill",
             "  kits are in ch 32"]
    emit("m_spill", lines)


def permits() -> None:
    rows = [  # name, lead months, needs before, owner (all PLACEHOLDERS, U-112)
        ("ESIA approval", 14, "any works", "developer"),
        ("vegetation clearing", 3, "earthworks", "contractor"),
        ("heritage survey clearance", 6, "trenching", "developer"),
        ("water abstraction", 8, "well pumping", "developer"),
        ("waste and hazardous storage", 4, "site set-up", "contractor"),
        ("wastewater discharge (camp)", 5, "camp opening", "contractor"),
        ("aviation lighting approval", 6, "tower erection", "developer"),
        ("operating environmental permit", 10, "energisation", "owner")]
    start = {"any works": 0, "earthworks": 0, "trenching": 2, "well pumping": 0,
             "site set-up": 0, "camp opening": 1, "tower erection": 9,
             "energisation": 18}
    lines = ["environmental permits on the critical path (lead times are PLACEHOLDERS)",
             "  permit                          lead mo   needed by month   apply by"]
    out = []
    latest = None
    for k, (name, lead, need, owner) in enumerate(rows, 1):
        apply = start[need] - lead
        out.append((k, apply, start[need]))
        lines.append(f"  {name:32s} {lead:7d}   {start[need]:15d}   {apply:8d}")
        if latest is None or apply < latest[1]:
            latest = (name, apply)
    csv("ch33-permits.csv", "k,apply,need", out)
    lines += ["  month 0 is the start of works; the earliest application:",
              f"  {latest[0]} at month {latest[1]}",
              "  the ESIA sets the pace: every other permit leans on it,",
              "  and the operating permit must be applied for before the",
              "  plant is half built - each row has an owner and a date in",
              "  the project schedule (ch 22, 49)"]
    emit("m_permits", lines)


if __name__ == "__main__":
    study_areas()
    soil_baseline()
    traffic_noise()
    spill()
    permits()
