"""Chapter 47, round x: ch 31's axle and lift checks re-run with the
heavier section 1, coating thickness by section (NCR-203), zinc measured
by weighing and by gauge, the number of records a reviewer must read,
and 7-day strengths as an early warning.

Run from the project root:   python -m companion.ch47.examples_x
Writes companion/ch47/expected/x_*.txt and diagrams/data/ch47-*.csv.
Teaching values (A-490 to A-497); no design approval implied.
"""
from __future__ import annotations

import numpy as np

from companion.ch31 import sources as s31
from companion.ch47 import examples_t as et
from companion.ch47 import sources as src
from companion.ch47.common import csv, emit
from plantp import logistics as lg

AXLE_LIMIT = 120.0          # kN, ch 31's teaching permit value


# ------------------------------------------------ 1. logistics re-run
def logistics(rigging_t: float = 6.0, radius_m: float = 14.0) -> dict:
    now = et.transport()[1][1]
    lines = [f"tower section 1 at {now:.0f} t (was 124 t in ch 31): axles and lift "
             "again",
             "  trailer axles   trailer t   tractor kN/axle   trailer kN/axle"]
    res = {}
    for n, trailer in ((14, 34.0), (16, 38.0), (18, 42.0)):
        t, r = lg.axle_loads(now, 30.0, trailer, n, tractor_axles=4,
                             tractor_share=0.05)
        res[n] = r
        lines.append(f"  {n:13d}   {trailer:9.0f}   {t:15.0f}   {r:15.0f}"
                     f"{'' if max(t, r) <= AXLE_LIMIT else '  over'}")
    u = lg.lift_utilisation(now, rigging_t, radius_m, s31.CRANE_CHART)
    lines += [f"  lift at {radius_m:.0f} m: ({now:.0f} + {rigging_t:.0f}) t against "
              f"{lg.chart_capacity(radius_m, s31.CRANE_CHART):.0f} t: use {u:.2f} "
              "(was 0.57)",
              "  fourteen axles, ch 31's choice, are now over the permit; the",
              "  section needs the nacelle's sixteen-axle trailer and a new",
              "  permit, and the bridge checks are run again - the crane",
              "  still lifts it with margin"]
    emit("x_logistics", lines)
    return dict(now=now, axles=res, use=u)


# ------------------------------------------------ 2. coating by section
def dft(seed: int = 4705, nominal: float = 320.0) -> dict:
    rng = np.random.default_rng(seed)
    means = {1: 345, 2: 338, 3: 302, 4: 350}
    lines = [f"outer coating DFT by section, 30 readings each (teaching rule:",
             f"  mean >= {nominal:.0f} um, none below 80 % = {0.8 * nominal:.0f} um)",
             "  section   mean um   lowest um   verdict"]
    bad = []
    for s, m in means.items():
        r = rng.normal(m, 30, 30)
        ok = r.mean() >= nominal and r.min() >= 0.8 * nominal
        if not ok:
            bad.append(s)
        lines.append(f"  {s:7d}   {r.mean():7.0f}   {r.min():9.0f}   "
                     f"{'ok' if ok else 'REPAIR (NCR-203)'}")
    lines += [f"  section {', '.join(map(str, bad))} fails on its mean and its lowest "
              "reading:",
              "  thin all over - a paint line run thin, not a spot; the whole",
              "  section is re-coated to the coating maker's procedure, then",
              "  measured again; a spot repair would leave the rest thin",
              "  (ch 30)"]
    emit("x_dft", lines)
    return dict(bad=bad)


# ------------------------------------------------ 3. zinc by weighing and gauge
POSTS = [   # post: area m2, mass before kg, after kg, gauge mean um
    ("Z-01/17", 1.20, 38.40, 39.24, 98), ("Z-01/42", 1.20, 38.10, 38.93, 97),
    ("Z-02/08", 1.20, 38.30, 38.92, 73), ("Z-03/11", 1.65, 61.20, 62.49, 107),
]


def zinc_methods(rho_zn: float = 7.14) -> dict:
    lines = ["zinc on four posts by two methods: weighing before and after",
             "  galvanizing, and the magnetic gauge",
             "  post      gain kg   by mass um   by gauge um   difference"]
    out = {}
    for p, a, m0, m1, g in POSTS:
        um = (m1 - m0) / (a * rho_zn) * 1000
        out[p] = (um, g)
        lines.append(f"  {p:8s}  {m1 - m0:7.2f}   {um:10.0f}   {g:11d}   "
                     f"{int(round(g - um)):+10d}")
    lines += ["  the two methods agree within a few micrometres on the good",
              "  lots and both put Z-02 below the rule: the weighing is the",
              "  referee when a gauge reading is disputed, because it does",
              "  not depend on the gauge's calibration or the spot chosen"]
    emit("x_zinc", lines)
    return out


# ------------------------------------------------ 4. records to read
def records(min_per_record: float = 1.5, day_h: float = 7.0) -> dict:
    per_section = {"plate certificates": 3, "plate-to-can marks": 10,
                   "weld map lines": 22, "welder checks": 22, "NDT reports": 8,
                   "repairs": 2, "dimensional records": 12, "DFT records": 4,
                   "NCRs": 2, "release": 1}
    n_sec = sum(per_section.values())
    n_all = n_sec * 4 * src.TURBINES
    days = n_all * min_per_record / 60 / day_h
    lines = ["records a buyer's reviewer reads for the towers (teaching counts)",
             "  per section: " + ", ".join(f"{k} {v}" for k, v in
                                          list(per_section.items())[:3]),
             "    " + ", ".join(f"{k} {v}" for k, v in list(per_section.items())[3:6]),
             "    " + ", ".join(f"{k} {v}" for k, v in list(per_section.items())[6:]),
             f"  {n_sec} a section, {n_all:,} for 48 sections; at "
             f"{min_per_record} minutes a record:",
             f"  {days:.0f} reviewer-days - which is why the checks of this chapter",
             "  are programs: a program reads every line in minutes and the",
             "  reviewer reads the findings, not the thousands of lines"]
    emit("x_records", lines)
    return dict(n=n_all, days=days)


# ------------------------------------------------ 5. 7-day strength as a warning
SEVEN = {"F01": [28.6, 28.1, 29.4], "F02": [30.3, 29.4, 30.8], "F03": [26.1, 25.4, 26.3],
         "F04": [28.5, 21.0, 29.0], "F05": [29.7, 30.1, 28.6], "F06": [27.9, 28.3, 28.8]}


def early(ratio: float = 0.70, fck: float = 35.0) -> dict:
    lines = [f"7-day results as an early warning (teaching ratio 7/28 day = "
             f"{ratio})",
             f"  predicted 28-day mean against the {fck + 4:.0f} MPa of the "
             "conformity rule",
             "  pour   7-day mean   predicted 28-day   warning"]
    warn = []
    rows = []
    for p, r in SEVEN.items():
        m7 = sum(r) / len(r)
        pred = m7 / ratio
        w = pred < fck + 4 or min(r) / ratio < fck - 4
        if w:
            warn.append(p)
        rows.append((p, round(pred, 1), round(sum(src.CUBES[p]) / 3, 1)))
        lines.append(f"  {p}    {m7:10.1f}   {pred:16.1f}   {'YES' if w else '-'}")
    csv("ch47-early.csv", "pour,predicted,actual",
        [(k + 1, a, b) for k, (_, a, b) in enumerate(rows)])
    lines += [f"  warned at day 7: {', '.join(warn)} - the same two pours that",
              "  failed at 28 days (lesson B); 21 days earlier the engineer can",
              "  plan cores, and the next pours can be held to a closer watch",
              "  - the 28-day result still decides"]
    emit("x_early", lines)
    return dict(warn=warn)


if __name__ == "__main__":
    logistics()
    dft()
    zinc_methods()
    records()
    early()
