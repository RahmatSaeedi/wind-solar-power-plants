"""Chapter 32, lesson T: a last round - what incidents cost, what a
safety-climate survey says with its uncertainty, how many inspections
find how many defects, whether a fire appliance can turn at a pad, and a
smoke-plume screen toward the village.

Run from the project root:   python -m companion.ch32.examples_t
Writes companion/ch32/expected/t_*.txt and diagrams/data/ch32-returns.csv,
ch32-plume.csv. Teaching values (A-368 to A-375); dispersion and vehicle
data for real decisions come from specialists and the fire service.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit


def incident_cost() -> None:
    items = [("lost-time injury", 3, 25.0, 4.0), ("recordable, no lost time", 8, 3.0, 4.0),
             ("property damage (crane, vehicle)", 6, 40.0, 1.5),
             ("near miss investigated", 30, 0.5, 1.0)]
    lines = ["what a year of incidents costs (teaching, k u)",
             "  kind                              n   direct each   indirect x   total"]
    total = 0.0
    for name, n, direct, mult in items:
        t = n * direct * (1 + mult)
        total += t
        lines.append(f"  {name:32s} {n:3d}   {direct:11.1f}   {mult:10.1f}   {t:6.0f}")
    lines += [f"  total about {total:,.0f} k u a year",
              "  the indirect part - stopped work, investigation, delay,",
              "  replacement crew, reputation - is several times the",
              "  direct cost: prevention pays in money too, but the case",
              "  for it rests on people, not on this table"]
    emit("t_cost", lines)


def climate_survey(seed: int = 32) -> None:
    rng = np.random.default_rng(seed)
    items = [("I can stop work if unsafe", 4.3, 3.6), ("near misses are acted on", 3.9, 3.1),
             ("supervisors put safety first", 4.4, 3.4), ("I have the right tools", 3.8, 3.5)]
    lines = ["safety-climate survey: managers vs workers (scale 1-5, synthetic)",
             "  25 managers, 180 workers; gap with its 95 % margin",
             "  statement                       managers   workers   gap"]
    for name, m_mean, w_mean in items:
        m = np.clip(rng.normal(m_mean, 0.6, 25), 1, 5)
        w = np.clip(rng.normal(w_mean, 0.9, 180), 1, 5)
        se = math.sqrt(m.var(ddof=1) / m.size + w.var(ddof=1) / w.size)
        gap = m.mean() - w.mean()
        lines.append(f"  {name:30s} {m.mean():8.1f}   {w.mean():7.1f}   {gap:3.1f} +/- {1.96 * se:3.1f}")
    lines += ["  managers rate every statement higher; the widest gaps -",
              "  supervisors' priorities and acting on near misses - are",
              "  where workers do not yet trust the system, while the",
              "  tools gap is within its margin: the survey points to",
              "  conversations to have, not to scores to publish"]
    emit("t_climate", lines)


def inspection_returns() -> None:
    defects, k = 40, 0.08
    rows = []
    lines = ["defects found against inspections a month (teaching: 40 present, k 0.08)",
             "  inspections   defects found   found by the last 5"]
    prev = 0.0
    for n in (0, 5, 10, 20, 30, 40, 60):
        found = defects * (1 - math.exp(-k * n))
        rows.append((n, round(found, 1)))
        lines.append(f"  {n:11d}   {found:13.1f}   {found - prev:19.1f}")
        prev = found
    csv("ch32-returns.csv", "n,found", [(n, round(defects * (1 - math.exp(-k * n)), 2))
                                        for n in range(0, 61, 2)])
    lines += ["  the first inspections find most defects; later ones find",
              "  few - which is why inspections rotate areas and change",
              "  focus (the Pareto of lesson R) rather than repeat the",
              "  same walk, and why workers' own reports matter"]
    emit("t_returns", lines)


def appliance_turn() -> None:
    inner, outer = 9.0, 16.0                          # m, teaching fire appliance radii
    lines = ["can a fire appliance turn at the pads and gates? (teaching radii)",
             f"  appliance turning circle: inner {inner} m, outer {outer} m;"
             f" swept width {outer - inner} m",
             "  location               road width m   bend radius m   ok?"]
    for name, w, r in [("site road bend", 6.0, 25.0), ("pad junction", 6.0, 12.0),
                       ("substation gate", 5.0, 10.0), ("BESS yard entry", 8.0, 14.0)]:
        ok = (r - w / 2 <= inner) and (r + w / 2 >= outer) or r >= 25
        lines.append(f"  {name:22s} {w:12.1f}   {r:13.1f}   {'yes' if ok else 'NO'}")
    lines += ["  the roads were sized for cranes and trailers (ch 29), but",
              "  tight gate and junction bends can stop a fire appliance:",
              "  the fire service drives the routes in a familiarisation",
              "  visit (lesson E) and its own vehicle data decide"]
    emit("t_turn", lines)


def plume() -> None:
    q_g_s = 50.0                                      # PLACEHOLDER emission of an irritant gas
    u = 4.0
    h = 20.0
    rows = []
    lines = ["smoke-plume screen toward the village (Gaussian, neutral, teaching)",
             f"  PLACEHOLDER release {q_g_s:.0f} g/s, wind {u:.0f} m/s, effective height"
             f" {h:.0f} m",
             "  distance m   ground concentration mg/m3"]
    for x in (300, 600, 1000, 2000, 3000, 5000):
        sy = 0.08 * x * (1 + 0.0001 * x) ** -0.5
        sz = 0.06 * x * (1 + 0.0015 * x) ** -0.5
        c = q_g_s / (math.pi * u * sy * sz) * math.exp(-h * h / (2 * sz * sz)) * 1000
        rows.append((x, round(c, 3)))
        lines.append(f"  {x:10d}   {c:26.2f}")
    csv("ch32-plume.csv", "x,c", [(x, round(q_g_s / (math.pi * u * (0.08 * x * (1 + 0.0001 * x) ** -0.5)
                                                     * (0.06 * x * (1 + 0.0015 * x) ** -0.5))
                                            * math.exp(-h * h / (2 * (0.06 * x * (1 + 0.0015 * x)
                                                                     ** -0.5) ** 2)) * 1000, 3))
                                  for x in range(100, 5001, 50)])
    lines += ["  the ground concentration peaks within a few hundred metres",
              "  and falls with distance; at the village 3 km away it is",
              "  a small fraction of the peak - but wind direction, night",
              "  inversions and the real release decide, so advice to",
              "  shelter or leave comes from the fire service and the",
              "  authority, with specialists' models (ch 33)"]
    emit("t_plume", lines)


if __name__ == "__main__":
    incident_cost()
    climate_survey()
    inspection_returns()
    appliance_turn()
    plume()
