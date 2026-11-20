"""Chapter 29, lesson M (more of the civil design basis): earthworks
along the main track as a mass-haul diagram, the road damage done by
construction traffic (fourth-power rule), roadside ditches against
erosion, rock protection at a culvert outlet, the headwater of the wadi
culverts with and without blockage, and a quantity take-off with
teaching rates.

Run from the project root:   python -m companion.ch29.examples_m
Writes companion/ch29/expected/m_*.txt and diagrams/data/ch29-mass.csv.
Teaching values (A-353, A-354).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import sources as s14
from companion.ch18 import sources as s18
from companion.ch29 import sources as src
from companion.ch29.common import csv, emit
from plantp import civil as cv
from plantp import stats as sx

G9 = 9.81


def mass_haul() -> None:
    z = s14.terrain()
    y = np.arange(600.0, 6200.0, 50.0)
    ground = s14.GRID.interp(z, np.full_like(y, 7600.0), y)
    kern = np.ones(9) / 9
    pad = np.r_[np.full(4, ground[0]), ground, np.full(4, ground[-1])]
    smooth = np.convolve(pad, kern, mode="valid")             # first try: smoothed ground
    k_dam = int(np.argmax(smooth - ground))
    crest = 1.5                                               # culvert crest above bed (m_headwater)
    formation = np.minimum(smooth, ground + crest)            # no embankment above the crest
    width, step, shrink = 6.0, 50.0, 0.90
    d = ground - formation                                    # + cut, - fill (m)
    cut = np.clip(d, 0, None) * width * step
    fill = np.clip(-d, 0, None) * width * step
    mass = np.cumsum(cut * shrink - fill)
    grade = 100 * np.abs(np.diff(formation)) / step
    csv("ch29-mass.csv", "s,ground,smooth,formation,mass",
        [(f"{a - 600:.0f}", f"{b:.2f}", f"{s:.2f}", f"{c:.2f}", f"{m:.0f}")
         for a, b, s, c, m in zip(y, ground, smooth, formation, mass)])
    cross = int(np.sum(np.diff(np.sign(mass)) != 0))
    lines = ["earthworks along the main track (x = 7,600 m)",
             "  first try: ground smoothed over 450 m - it crosses the wadi",
             f"  at s = {y[k_dam] - 600:.0f} m on {smooth[k_dam] - ground[k_dam]:.1f} m of fill:"
             " an embankment that dams it",
             f"  corrected: no fill above the culvert crest ({crest:.1f} m over the bed)",
             f"  steepest grade of the corrected line {grade.max():.1f} % (limit 8 %, lesson B)",
             f"  cut {cut.sum():,.0f} m3 (bank), fill {fill.sum():,.0f} m3; cut shrinks to"
             f" {100 * shrink:.0f} % when compacted",
             f"  end of the mass diagram {mass[-1]:+,.0f} m3 (+ surplus, - borrow)",
             f"  largest ordinate {np.abs(mass).max():,.0f} m3",
             f"  the diagram crosses zero {cross} times: between crossings cut",
             "  and fill balance, and the material moves along the road",
             "  instead of to a tip or from a borrow pit",
             "  a grade line is chosen for drainage and the vehicles",
             "  first (lesson B), and for balance second; the mass",
             "  diagram shows the cost of that choice in haul"]
    emit("m_mass", lines)


def traffic() -> None:
    std = 80.0                                                # kN standard axle

    def esal(axles):
        return sum((a / std) ** 4 for a in axles)

    d = src.DEMAND
    concrete = d["construction_concrete_m3"] / 8
    stone = (28_000 * 6 * 0.3 + 12 * 1600 * 0.5) * 2.0 / 25
    water = 75_600 / 20
    classes = [("concrete trucks (8 m3)", concrete, [60, 100, 100], [50, 40, 40]),
               ("aggregate trucks (25 t)", stone, [60, 75, 75, 75], [50, 30, 30, 30]),
               ("water trucks (20 m3)", water, [60, 95, 95], [50, 35, 35]),
               ("tower sections and nacelles", 12 * 6, [100] * 10, [40] * 10),
               ("blades", 12 * 3, [60] * 6, [30] * 6),
               ("crane and ballast", 40, [120] * 6, [60] * 6)]
    total = sum(n * (esal(lo) + esal(un)) for _, n, lo, un in classes)
    lines = ["construction traffic on the site roads (fourth-power rule, 80 kN axle)",
             "  class                          loads   ESAL per round trip   ESAL   share"]
    for name, n, lo, un in classes:
        e = esal(lo) + esal(un)
        lines.append(f"  {name:29s} {n:6,.0f}   {e:19.2f}   {n * e:6,.0f}   {100 * n * e / total:4.0f} %")
    lines += [f"  total {total:,.0f} standard axles",
              "  the turbine parts are the heaviest single loads, but the",
              "  many aggregate and water trucks wear the road most: a",
              "  pavement designed for the abnormal loads alone would",
              "  fail early; the spraying trucks wear the very road they",
              "  keep from dusting - binders on the busiest sections or a",
              "  lower speed (lesson N) cut both the water and the wear"]
    emit("m_traffic", lines)


def ditches() -> None:
    b, zs, y = 0.5, 2.0, 0.4                          # bottom m, side 1:2, depth m
    area = (b + zs * y) * y
    perim = b + 2 * y * math.sqrt(1 + zs * zs)
    lines = ["roadside ditch (0.5 m bottom, 1:2 sides, 0.4 m deep) against erosion",
             "  (allowable velocity, teaching: bare silty sand 0.6 m/s, grassed",
             "   1.2 m/s, stone-lined 2.5 m/s; check dams 0.3 m high)",
             "  slope %   Q earth m3/s   v m/s   lining needed      check dams every m"]
    for s in (0.5, 2.0, 6.0):
        q = cv.manning_q(0.030, area, perim, s / 100)
        v = q / area
        need = "none" if v <= 0.6 else "grass" if v <= 1.2 else "stone"
        lines.append(f"  {s:6.1f}   {q:12.2f}   {v:5.2f}   {need:16s}   {0.3 / (s / 100):10.0f}")
    lines += ["  the same ditch that is safe on the plain scours on a 6 %",
              "  approach: lining or check dams go where the grade is,",
              "  not along the whole road"]
    emit("m_ditches", lines)


def riprap() -> None:
    lines = ["rock at a culvert outlet (Isbash: D = v^2 / (2 g C^2 (s - 1)), s 2.65)",
             "  velocity m/s   D50 exposed (C 0.86) m   D50 embedded (C 1.20) m"]
    for v in (1.5, 3.0, 4.5):
        d1 = v * v / (2 * G9 * 0.86 ** 2 * 1.65)
        d2 = v * v / (2 * G9 * 1.20 ** 2 * 1.65)
        lines.append(f"  {v:12.1f}   {d1:22.2f}   {d2:23.2f}")
    lines += ["  stone size grows with the square of velocity: the outlet",
              "  of the 0.9 m pipes (1.5 m/s full) needs little; the road",
              "  crest overtopped in a big storm (3-4.5 m/s on the",
              "  downstream face) needs rock of 0.4-0.8 m - the overtopping",
              "  path is designed, not left to chance"]
    emit("m_riprap", lines)


def headwater() -> None:
    e = src.extremes()
    mu, beta = sx.gumbel_fit_moments(e["rain_1h"])
    tc = cv.kirpich_tc(2500, 0.01)

    def q_of(years):
        return cv.rational_peak(0.35, cv.gumbel_return(mu, beta, years) * (60 / tc) ** 0.6, 3.2)

    d, cd = 0.9, 0.6
    a = math.pi * d * d / 4
    crest = d + 0.6
    lines = ["headwater at the wadi culverts (inlet as an orifice, Cd 0.6: fair",
             f"  once HW/D > ~1.2, rough below it; road crest {crest:.1f} m above the invert)",
             "  storm                 Q m3/s   pipes open   HW m   overtops?"]
    cases = [("10-year", q_of(10), 10), ("50-year", q_of(50), 10), ("100-year", q_of(100), 10),
             ("50-year, 3 blocked", q_of(50), 7), ("50-year, 5 blocked", q_of(50), 5),
             ("2 x 50-year", 2 * q_of(50), 10)]
    for name, q, n in cases:
        per = q / n
        hw = d / 2 + (per / (cd * a)) ** 2 / (2 * G9)
        lines.append(f"  {name:20s} {q:7.1f}   {n:10d}   {hw:4.2f}   {'yes' if hw > crest else 'no'}")
    lines += ["  the pipes carry the design storm with room to spare, but",
              "  wadi floods carry sediment and brush: with half the pipes",
              "  blocked the 50-year storm overtops the road - inspection",
              "  after every flow and a designed overtopping path matter",
              "  as much as the pipe count"]
    emit("m_headwater", lines)


def takeoff() -> None:
    poly = np.array(list(src.PV_BLOCK) + [src.PV_BLOCK[0]])
    fence = float(np.sum(np.hypot(*np.diff(poly, axis=0).T))) + 4 * 120
    items = [("road aggregate 28 km x 6 m x 0.3 m", 28_000 * 6 * 0.3, "m3", 25.0),
             ("pad stone 12 x 40 x 40 m x 0.5 m", 12 * 1600 * 0.5, "m3", 25.0),
             ("earthworks (roads, pads, platform)", 60_000, "m3", 6.0),
             ("ditches, both sides of the roads", 56_000, "m", 8.0),
             ("culverts (wadi 10 x 12 m + 30 x 10 m)", 10 * 12 + 30 * 10, "m", 300.0),
             ("foundation and plinth concrete", src.DEMAND["construction_concrete_m3"], "m3", 180.0),
             ("reinforcement, 90 kg/m3", src.DEMAND["construction_concrete_m3"] * 90, "kg", 1.2),
             ("fence (PV block and substation)", fence, "m", 40.0),
             ("substation platform fill 120 x 100 x 0.5 m", 6_000, "m3", 12.0)]
    total = sum(q * r for _, q, _, r in items) / 1e3
    wind = 60 * s18.COST["wind_per_mw"]
    pv = 50 * s18.COST["pv_per_mw_ac"]
    lines = ["civil quantity take-off of Plant P (teaching rates, u)",
             "  item                                          quantity   unit     k u"]
    for name, q, unit, r in items:
        lines.append(f"  {name:44s} {q:9,.0f}   {unit:4s} {q * r / 1e3:7,.0f}")
    lines += [f"  total about {total:,.0f} k u = {100 * total / (wind + pv):.1f} % of the wind"
              " and PV installed",
              f"  cost ({wind + pv:,.0f} k u, A-287), which already includes these works",
              "  a take-off this early is a class-4 or class-5 estimate",
              "  (ch 22): its range is wide, and the quantities that",
              "  drive it - concrete and stone - are the ones the ground",
              "  investigation can still change"]
    emit("m_takeoff", lines)


if __name__ == "__main__":
    mass_haul()
    traffic()
    ditches()
    riprap()
    headwater()
    takeoff()
