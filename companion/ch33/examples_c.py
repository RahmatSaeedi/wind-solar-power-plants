"""Chapter 33, lesson C: mitigation and monitoring - impact pathways from
source to receptor, the step of the mitigation hierarchy chosen for each,
indicators with a red/amber/green status, the age of corrective actions,
how many survey days a monitoring programme needs to see a change, and
closure criteria with their evidence.

Run from the project root:   python -m companion.ch33.examples_c
Writes companion/ch33/expected/c_*.txt and diagrams/data/ch33-power.csv.
Teaching values (A-382); indicators and targets come from the impact
assessment, the permits and the lenders' plan.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch33 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch33.common import csv, emit
from plantp import envsocial as es


def pathways() -> None:
    rows = [("turbine rotors", "air (sound)", "camp, farmhouse A", "minimise: reduced mode"),
            ("grading, haul", "air (dust)", "village, farms", "minimise: water, speed"),
            ("well pumping", "aquifer", "village wells", "avoid: limit, monitor"),
            ("rotors in flight path", "collision", "raptors near nest", "avoid: siting; minimise"),
            ("trucks", "village road", "children, elders", "minimise: hours, marshal"),
            ("PV fence", "lost access", "herders' families", "avoid: gap and crossing"),
            ("trenches", "ground", "buried heritage", "avoid: buffer; chance finds"),
            ("fire water", "drains, soil", "wadi, groundwater", "minimise: closed pond")]
    lines = ["impact pathways: source -> pathway -> receptor -> chosen step",
             "  source                  pathway       receptor"]
    for s, pw, r, st in rows:
        lines += [f"  {s:23s} {pw:13s} {r}", f"      step: {st}"]
    lines += ["  a pathway with no receptor is no impact; breaking the",
              "  pathway (a gap in the fence, a closed pond) often beats",
              "  treating the receptor - and avoidance comes first"]
    emit("c_pathways", lines)


def indicators() -> None:
    items = [("night noise at camp B, dB(A)", 38.5, 40.0, 2.0, False),
             ("dust days over trigger a month", 3, 2, 2, False),
             ("village well level change, m", 0.6, 0.5, 0.3, False),
             ("raptor collisions found a year", 1, 0, 1, False),
             ("grievances closed in 30 days, %", 88, 90, 5, True),
             ("local hires, % of workforce", 36, 40, 5, True),
             ("restored area with cover >= 70 %, %", 55, 80, 10, True)]
    lines = ["indicators with targets and a red/amber/green status (synthetic)",
             "  indicator                               value   target   status"]
    for name, v, t, tol, hib in items:
        lines.append(f"  {name:39s} {v:5.1f}   {t:6.1f}   {es.kpi_rag(v, t, tol, hib)}")
    lines += ["  amber asks for a look, red for a corrective action with",
              "  an owner and a date; an indicator without a target, a",
              "  frequency and an owner is a statistic, not monitoring"]
    emit("c_indicators", lines)


def corrective(seed: int = 33) -> None:
    rng = np.random.default_rng(seed)
    days = rng.gamma(2.0, 20.0, 46)
    lines = ["corrective actions of the construction year (synthetic)",
             f"  actions raised: {days.size}; median days to close {np.median(days):.0f}",
             f"  closed within 30 days: {np.mean(days <= 30) * 100:.0f} %; longest {days.max():.0f} days",
             "  closure means the cause is fixed and checked on site -",
             "  an action closed by a new procedure nobody follows is",
             "  reopened at the next audit (ch 32, lesson A)"]
    emit("c_corrective", lines)


def survey_power() -> None:
    rate = 3.0                                     # raptor passages a survey day (teaching)
    rows = []
    lines = ["survey days needed to see a 30 % fall in raptor passages (Poisson)",
             f"  before: {rate} passages a day; after: {rate * 0.7:.1f}; one-sided test 5 %",
             "  days before and after   power to detect"]
    for days in (10, 20, 40, 80):
        n0 = rate * days
        crit = stats.poisson.ppf(0.05, n0)
        power = stats.poisson.cdf(crit, rate * 0.7 * days)
        rows.append((days, round(power, 3)))
        lines.append(f"  {days:21d}   {power * 100:14.0f} %")
    csv("ch33-power.csv", "days,power", rows)
    lines += ["  a short survey cannot tell a real change from chance: the",
              "  monitoring plan fixes the effort from the change it must",
              "  see - before the turbines turn, so there is a baseline"]
    emit("c_power", lines)


def closure() -> None:
    items = [("laydown restored, cover >= 70 % of reference", "photo plots, year 3", False),
             ("temporary roads ripped and seeded", "survey", True),
             ("borrow pits shaped and drained", "survey, photos", True),
             ("all grievances closed or escalated", "log", True),
             ("water point handed to herders, working", "joint visit", True),
             ("contaminated soil removed, tested", "lab results", False)]
    lines = ["closure of construction: criteria and evidence (teaching)",
             "  criterion                                      evidence            met"]
    met = 0
    for c, ev, ok in items:
        met += ok
        lines.append(f"  {c:46s} {ev:19s} {'yes' if ok else 'no'}")
    lines += [f"  {met} of {len(items)} met: closure waits for the vegetation and",
              "  the soil tests - criteria fixed in advance, evidence on",
              "  file, and the people affected see the result before the",
              "  file is closed"]
    emit("c_closure", lines)


if __name__ == "__main__":
    pathways()
    indicators()
    corrective()
    survey_power()
    closure()
