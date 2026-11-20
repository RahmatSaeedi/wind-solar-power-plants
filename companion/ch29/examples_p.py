"""Chapter 29, lesson P (more on climate and water): heat hours of the
data-pack year now and with the warming of lesson E, evaporation from
an open reservoir and the brine pond, RO recovery against brine
strength, the wadi in flood beside the substation, the chance of a
design event within the plant's life, and an adaptation register.

Run from the project root:   python -m companion.ch29.examples_p
Writes companion/ch29/expected/p_*.txt and diagrams/data/ch29-flood.csv.
Teaching values (A-350, A-351, A-355); a flood study replaces lesson
P's flows.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import sources as s14
from companion.ch29 import examples_g as g
from companion.ch29.common import csv, emit
from plantp import datapack
from plantp import pe
from plantp import stats as sx


def heat() -> None:
    d = datapack.load_hourly()
    t = d["t_air_c"].to_numpy()
    ghi = d["ghi_wm2"].to_numpy()
    lines = ["heat hours of the data-pack year, shifted by the warming of lesson E",
             "  (inverter derating from 40 C at 2 %/K, ch 9; cooling degree-hours",
             "   above 25 C as a measure of battery and building HVAC energy)",
             "  case               h > 35 C   h > 40 C   PV energy derated %   CDH k"]
    base_cdh = None
    for name, dt in (("today", 0.0), ("end of life +1.35 K", 1.35), ("pessimistic +2.7 K", 2.7)):
        tt = t + dt
        k = pe.derating(tt)
        lost = float(np.sum(ghi * (1 - k)) / np.sum(ghi))
        cdh = float(np.sum(np.clip(tt - 25, 0, None))) / 1000
        base_cdh = base_cdh or cdh
        lines.append(f"  {name:19s} {np.sum(tt > 35):8d}   {np.sum(tt > 40):8d}   {100 * lost:19.3f}"
                     f"   {cdh:5.1f}")
    lines += ["  the PV energy lost to derating stays tiny (the hottest",
              "  hours are few and the knee is high), but the cooling",
              "  load grows by about 30 % (+1.35 K) to 60 % (+2.7 K):",
              "  HVAC for the battery and the buildings, not the",
              "  inverters, is where warming costs",
              "  - sized with margin now or planned as a later addition"]
    emit("p_heat", lines)


def evaporation() -> None:
    pan, coef, rain = 2.8, 0.7, 0.11                  # m/yr pan, pan coefficient, rain (teaching)
    e_open = pan * coef
    tank_area = 2500 / 1.5
    demand = sum(v.sum() for v in g.demand().values())
    brine = 1019.0
    lines = ["evaporation (teaching: pan 2.8 m a year, pan coefficient 0.7, rain 0.11 m)",
             f"  open reservoir of 2,500 m3, 1.5 m deep ({tank_area:,.0f} m2): loses"
             f" {e_open * tank_area:,.0f} m3 a year",
             f"  - more than the plant's whole operating demand ({demand:,.0f} m3, lesson G);",
             "  a closed steel or concrete tank loses almost nothing",
             f"  brine pond for {brine:,.0f} m3 a year: net evaporation {e_open - rain:.2f} m a year",
             f"  area needed {brine / (e_open - rain):,.0f} m2, plus freeboard and a second cell"
             " for maintenance",
             f"  rain on 1,000 m2 of roofs: {1000 * rain * 0.85:.0f} m3 a year - worth"
             " collecting, never a supply",
             "  in a desert the sun is the largest water user on site"]
    emit("p_evaporation", lines)


def brine() -> None:
    feed = 2500.0                                     # mg/L, well water (teaching)
    treated = 1529.0
    lines = ["RO recovery against brine strength (feed 2,500 mg/L, permeate taken as pure)",
             "  recovery %   raw m3   brine m3   brine mg/L   pond m2"]
    for r in (0.50, 0.60, 0.75, 0.85):
        raw = treated / r
        b = raw - treated
        lines.append(f"  {100 * r:10.0f}   {raw:6,.0f}   {b:8,.0f}   {feed / (1 - r):10,.0f}"
                     f"   {b / (2.8 * 0.7 - 0.11):7,.0f}")
    lines += ["  higher recovery saves raw water and pond area but makes",
              "  the brine stronger, until salts scale the membranes: the",
              "  supplier's analysis of the actual well water sets the",
              "  limit, not this table"]
    emit("p_brine", lines)


def flood() -> None:
    z = s14.terrain()
    g = s14.GRID
    xs = np.linspace(0, 13000, 261)
    yw = np.interp(xs, [s14.WADI[0][0], s14.WADI[1][0]], [s14.WADI[0][1], s14.WADI[1][1]])
    k = int(np.argmin(np.hypot(xs - s14.SITE_SUB[0], yw - s14.SITE_SUB[1])))
    t = np.linspace(0, 1, 47)
    px = xs[k] + t * (s14.SITE_SUB[0] - xs[k])
    py = yw[k] + t * (s14.SITE_SUB[1] - yw[k])
    prof = g.interp(z, px, py)
    zs = float(prof[-1])
    ridge = float(prof.max())
    csv("ch29-flood.csv", "d,z", [(f"{a:.0f}", f"{b:.2f}") for a, b in
                                  zip(t * np.hypot(s14.SITE_SUB[0] - xs[k], s14.SITE_SUB[1] - yw[k]),
                                      prof)])
    width, n, slope, bank = 40.0, 0.035, 0.006, 1.5

    def depth(q):
        lo, hi = 0.01, 10.0
        for _ in range(60):
            y = (lo + hi) / 2
            a = width * y
            qq = a * (a / (width + 2 * y)) ** (2 / 3) * math.sqrt(slope) / n
            lo, hi = (y, hi) if qq < q else (lo, y)
        return y

    j = int(np.argmin(prof[:10]))                      # channel bed beside the line
    inv = float(prof[j])
    lines = ["the wadi in flood beside the substation (channel 40 m wide, banks",
             "  1.5 m, n 0.035, bed slope 0.6 %; flows are placeholders until a",
             "  flood study gives them)",
             "  flow m3/s   depth in channel m   water level m   out of banks?"]
    for q in (50, 150, 300):
        y = depth(q)
        lines.append(f"  {q:9d}   {y:18.2f}   {inv + y:13.2f}   {'yes' if y > bank else 'no'}")
    lines += [f"  ground: channel bed {inv:.1f} m, ridge {ridge:.1f} m, substation {zs:.1f} m",
              "  at 300 m3/s the water stands above the substation's ground",
              f"  level, but the ridge is {ridge - inv - depth(300):.1f} m higher still: here the flood",
              "  does not reach it; upstream the bed itself is higher than",
              "  the substation, and water leaving the channel there can",
              "  run down the plain towards it - the flood study follows",
              "  that path, and the platform level and any diversion bund",
              "  come from it"]
    emit("p_flood", lines)


def lifetime() -> None:
    life = 25
    lines = [f"the chance of at least one T-year event in a {life}-year life",
             "  T years   chance %"]
    for t in (10, 25, 50, 100, 500, 1000):
        lines.append(f"  {t:7d}   {100 * sx.prob_exceed_in_life(t, life):8.1f}")
    lines += ["  a 50-year design storm has two chances in five of coming",
              "  within the plant's life; the culverts' overtopping path",
              "  and the substation level are chosen with that in mind -",
              "  and with a changing climate the 'T' itself drifts"]
    emit("p_lifetime", lines)


def adaptation() -> None:
    rows = [("heat", "hours > 40 C a year", "> 30", "add HVAC (space kept)"),
            ("rain", "culvert blocked after a flow", "any", "clear; review pipe count"),
            ("flood", "water within 50 m of platform", "any", "raise bund (study)"),
            ("dust", "soiling loss a month", "> 4 %", "extra wash or robot pass"),
            ("drought", "tank below 40 % in June", "yes", "cut washes, truck water"),
            ("wind", "gust > 50-year value", "any", "inspect structures (ch 30)")]
    lines = ["adaptation register: what is watched, the trigger, and the planned action",
             "  hazard   indicator                      trigger  action"]
    for h, ind, trig, act in rows:
        lines.append(f"  {h:8s} {ind:30s} {trig:7s}  {act}")
    lines += ["  each trigger is measured by the plant's own records (ch",
              "  51-53) and reviewed each year; the design kept the space",
              "  and the margins that make each action possible"]
    emit("p_adapt", lines)


if __name__ == "__main__":
    heat()
    evaporation()
    brine()
    flood()
    lifetime()
    adaptation()
