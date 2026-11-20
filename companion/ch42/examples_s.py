"""Chapter 42, a second round: the blade's mass budget and the cost of
tip mass, infusion fill time by Darcy's law (why long blades need many
inlets), exotherm in thick laminates, the generator's efficiency over the
data-pack year, oil temperature settling in the run-in, an oil iron
trend, a birth-certificate completeness audit, and what the crane
campaigns are worth today.

Run from the project root:   python -m companion.ch42.examples_s
Writes companion/ch42/expected/s_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-452 to A-457); textbook physics, no process settings.
"""
from __future__ import annotations

import math
import random

import numpy as np

from companion.ch42 import sources as src
from companion.ch42.common import csv, emit
from companion.ch42.examples_a import replacements
from plantp import datapack

# ------------------------------------------------ blade mass budget
PARTS = [  # part, mass t, radius of its centre m (teaching)
    ("spar caps (glass)", 7.9, 24.0), ("shells and core", 6.6, 27.0),
    ("shear webs", 2.2, 24.0), ("root laminate and inserts", 3.3, 2.0),
    ("adhesive", 0.9, 26.0), ("coating, LPS, other", 1.1, 31.0)]


def mass_budget() -> dict[str, float]:
    m = sum(p[1] for p in PARTS)
    s = sum(p[1] * p[2] for p in PARTS)
    lines = ["blade mass budget (teaching; ch 11: 22 t, first moment 484 t m)",
             "  part                         mass t   centre m   moment t m"]
    for name, mass, r in PARTS:
        lines.append(f"  {name:28s} {mass:6.1f}   {r:8.1f}   {mass * r:10.1f}")
    tip = 0.1 * 70.0
    lines += [f"  total {m:.1f} t; first moment {s:.0f} t m; centre {s / m:.1f} m",
              f"  100 kg added at 70 m adds {tip:.0f} t m - as much as "
              f"{tip / 2.0 * 1000:,.0f} kg at the root",
              "  mass far out costs most: in gravity moment, in edgewise",
              "  fatigue and in unbalance; coating and repairs near the",
              "  tip are weighed into the blade's record (lesson B)"]
    emit("s_mass", lines)
    return dict(mass=m, moment=s)


# ------------------------------------------------ infusion fill time
# [start: darcy]
def fill_time(length_m: float, k_m2: float = 2e-10, mu: float = 0.25,
              phi: float = 0.45, dp: float = 0.9e5) -> float:
    """Darcy flow from a line inlet: t = mu phi L^2 / (2 K dP), seconds."""
    return mu * phi * length_m ** 2 / (2 * k_m2 * dp)
# [end: darcy]


def infusion(pot_life_min: float = 120.0) -> dict[float, float]:
    out = {}
    lines = ["resin flow distance against fill time (teaching permeability,",
             "  viscosity and pressure; Darcy's law)",
             "  flow length m   fill time min   within the resin's working time?"]
    for l in (0.5, 1.0, 2.0, 4.0):
        t = fill_time(l) / 60
        out[l] = t
        lines.append(f"  {l:13.1f}   {t:13.0f}   "
                     f"{'yes' if t < pot_life_min else 'no'}")
    lines += ["  time grows with the square of the distance: a 75 m blade is",
              "  filled from many inlets a metre or two apart, never from",
              "  one end; the inlet plan is the maker's qualified design, and",
              "  a dry spot (NCR-101) is a flow front that did not meet"]
    emit("s_infusion", lines)
    return out


# ------------------------------------------------ exotherm
def exotherm(h_jg: float = 420.0, resin_mass: float = 0.30,
             cp: float = 1.0) -> dict[str, float]:
    rise = h_jg * resin_mass / cp
    lines = ["heat of cure released in a laminate that cannot lose it",
             f"  resin {resin_mass:.0%} of the mass, {h_jg:.0f} J/g, c_p {cp} "
             "J/g K (teaching)",
             f"  adiabatic rise {rise:.0f} K - the same arithmetic as mass",
             "  concrete (ch 29, adiabatic rise)",
             "  thin shells lose the heat to the mould; a thick root",
             "  laminate does not, and can overheat, crack or burn - why",
             "  thick sections are built and cured in steps the maker",
             "  qualifies; the record of their temperature is the evidence"]
    emit("s_exotherm", lines)
    return dict(rise=rise)


# ------------------------------------------------ generator over a year
def generator_year(p_rated: float = 5000.0, p0: float = 40.0,
                   pk: float = 90.0) -> dict[str, float]:
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy()
    load = np.clip((v - 3.0) / 8.0, 0, 1) ** 3
    load[(v < 3) | (v > 25)] = 0.0
    run = load > 0
    p_out = load * p_rated
    loss = np.where(run, p0 + pk * load ** 2, 0.0)
    e_out = p_out.sum() / 1000
    e_loss = loss.sum() / 1000
    eta_rated = p_rated / (p_rated + p0 + pk)
    eta_year = e_out / (e_out + e_loss)
    lines = ["generator losses over the data-pack year (teaching: no-load",
             f"  {p0:.0f} kW, load losses {pk:.0f} kW at rated, growing with load^2;",
             "  a rough cubic power curve - ch 11 has the turbine's own)",
             f"  efficiency at rated {eta_rated:.2%}; over the year "
             f"{eta_year:.2%}",
             f"  energy out {e_out:,.0f} MWh; losses {e_loss:,.0f} MWh "
             f"({int(run.sum())} running hours)",
             "  part load is where a turbine spends its hours, and there",
             "  the fixed no-load losses weigh more: a generator is judged",
             "  by its loss split from the factory test, not by one",
             "  efficiency at rated"]
    emit("s_generator", lines)
    return dict(eta_rated=eta_rated, eta_year=eta_year)


# ------------------------------------------------ oil temperature settling
def oil_settling(tau_min: float = 40.0, rise: float = 30.0,
                 band: float = 1.0) -> dict[str, float]:
    t_ok = -tau_min * math.log(band / rise)
    lines = [f"gearbox oil temperature after a load step: first order, tau "
             f"{tau_min:.0f} min",
             f"  final rise {rise:.0f} K; 'stable' = within {band} K of the end",
             f"  time to stable {t_ok:.0f} min ({t_ok / 60:.1f} h) at each step",
             "  four load steps take most of a shift before the last",
             "  readings mean anything: vibration and temperature are read",
             "  only once the step has settled - a test plan that records",
             "  earlier compares a warm gearbox with a cold one"]
    emit("s_oil", lines)
    return dict(t_ok=t_ok)


# ------------------------------------------------ oil iron trend
def iron(seed: int = 4208) -> dict[str, list[str]]:
    rng = random.Random(seed)
    hours = [0, 2, 4, 6, 8, 10, 12]
    units = {}
    for u in range(1, 11):
        name = f"G{u:02d}"
        base = [12 * (1 - math.exp(-h / 3)) + rng.gauss(0, 0.6) for h in hours]
        if name == "G04":
            base = [b + 1.5 * h for b, h in zip(base, hours)]
        units[name] = base
    still = [k for k, v in units.items() if v[-1] - v[-3] > 3.0]
    csv("ch42-iron.csv", "h," + ",".join(units),
        [(h, *(round(units[k][i], 2) for k in units)) for i, h in
         enumerate(hours)])
    lines = ["iron in the run-in oil, ppm (synthetic, ten gearboxes)",
             "  running-in wear rises then levels; a unit still climbing",
             f"  after 8 h: {still}",
             "  the same unit whose spectrum showed sidebands (lab D):",
             "  oil and vibration agree, and two kinds of evidence make the",
             "  hold decision firm"]
    emit("s_iron", lines)
    return dict(still=still)


# ------------------------------------------------ birth certificates
FIELDS = ["serial", "heat number", "inspection report", "test report",
          "torque record", "NCR closure", "preservation log"]


def birth(seed: int = 4209, n: int = 40) -> dict[str, int]:
    rng = random.Random(seed)
    missing = {f: 0 for f in FIELDS}
    for _ in range(n):
        for f in FIELDS:
            p = {"preservation log": 0.15, "NCR closure": 0.08,
                 "torque record": 0.05}.get(f, 0.01)
            if rng.random() < p:
                missing[f] += 1
    complete = 1 - sum(missing.values()) / (n * len(FIELDS))
    lines = [f"audit of {n} component birth certificates (7 fields each)",
             "  field                missing"]
    for f, k in missing.items():
        lines.append(f"  {f:20s} {k:7d}")
    lines += [f"  fields complete {complete:.1%}",
              "  the gaps cluster in the records made last - storage and",
              "  NCR closure - where nobody waits for them; a certificate",
              "  is accepted complete or returned, as the dossier of ch 40",
              "  was judged on validity, not on 'pass'"]
    emit("s_birth", lines)
    return dict(complete=complete, **missing)


# ------------------------------------------------ crane campaigns today
def crane_value(cost_k: float = 450.0, rate: float = 0.075, years: int = 25):
    r = replacements()
    per_year = r["total"] / years
    pv = sum(per_year * cost_k / (1 + rate) ** y for y in range(1, years + 1))
    lines = [f"crane campaigns: {r['total']:.0f} expected over {years} years, "
             f"{cost_k:.0f} k u each (teaching)",
             f"  spread evenly: {per_year:.2f} a year; present value at "
             f"{rate:.1%}: {pv:,.0f} k u",
             "  a component quality that halves the major-failure rates is",
             f"  worth about {pv / 2:,.0f} k u today before any lost energy -",
             "  the value of the factory evidence this chapter asks for"]
    emit("s_crane", lines)
    return dict(pv=pv)


if __name__ == "__main__":
    mass_budget()
    infusion()
    exotherm()
    generator_year()
    oil_settling()
    iron()
    birth()
    crane_value()
