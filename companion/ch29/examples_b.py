"""Chapter 29, lesson B: the civil design basis in numbers - road grades
and curve widening for long loads, aggregate thickness over weak
subgrade, the crane pad under an outrigger, drainage of the wadi
crossing (rational method, culverts), erosion of disturbed ground, and
water in a trench.

Run from the project root:   python -m companion.ch29.examples_b
Writes companion/ch29/expected/b_*.txt and diagrams/data/ch29-*.csv.
Teaching values (A-349, A-350, A-353, A-354).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import sources as s14
from companion.ch29 import sources as src
from companion.ch29.common import csv, emit
from plantp import civil as cv
from plantp import stats as sx


def road_grades() -> None:
    z = s14.terrain()
    g = s14.GRID
    y = np.arange(600.0, 6200.0, 50.0)
    x = np.full_like(y, 7600.0)
    zz = g.interp(z, x, y)
    grade = 100 * np.diff(zz) / 50.0
    csv("ch29-track.csv", "s,z,grade", [(f"{a - 600:.0f}", f"{b:.2f}", f"{c:.2f}")
                                        for a, b, c in zip(y[1:], zz[1:], grade)])
    lines = ["the main site track (x = 7,600 m, 5.6 km) from the ch 14 terrain",
             f"  highest grade {np.abs(grade).max():.1f} % over a 50 m step; mean {np.abs(grade).mean():.1f} %",
             "  teaching limits for blade and tower transport (from the",
             "  transport company and OEM, U-106): 8 % loaded, 12 % with",
             "  a tow vehicle; the steepest 50 m step (6.1 %) is below",
             "  the first, but the survey's 1 m resolution, not the 50 m",
             "  grid, decides the short steep pieces (culvert approaches,",
             "  wadi banks)",
             "",
             "widening on a curve for a rigid length L (w = R - sqrt(R^2 - L^2))",
             "  inside radius m   L 20 m (rear-steered)   L 40 m (fixed), teaching"]
    for r in (60, 80, 120, 200):
        w20 = r - math.sqrt(r * r - 20 ** 2)
        w40 = r - math.sqrt(r * r - 40 ** 2)
        lines.append(f"  {r:15d}   {w20:20.1f}   {w40:13.1f}")
    lines += ["  a tight bend needs metres of extra width (and cleared",
              "  overhang for the blade tip) - the swept path of the real",
              "  vehicle is checked on the drawing, junction by junction"]
    emit("b_roads", lines)


def aggregate() -> None:
    wheel = 60.0                              # kN (12 t axle), contact 0.3 x 0.3 m
    lines = ["aggregate thickness so the subgrade is not overloaded (2:1 spread)",
             "  (allowable on subgrade ~ 30 x CBR kPa: a screening rule; teaching)",
             "  CBR %   allowable kPa   thickness needed m"]
    for cbr in (3, 8, 15):
        allow = 30.0 * cbr
        h = next(z / 100 for z in range(0, 300) if cv.spread_pressure(wheel, 0.3, 0.3, z / 100) <= allow)
        lines.append(f"  {cbr:5d}   {allow:13.0f}   {h:18.2f}")
    lines += ["  weak, wet subgrade (CBR 3) needs more than twice the",
              "  stone of a firm one; CBR tests along the route (lesson C)",
              "  set the thickness section by section, and a geotextile",
              "  on soft ground is a design choice, not a habit"]
    emit("b_aggregate", lines)


def crane_pad() -> None:
    load = 2400.0                              # kN on the worst outrigger (teaching)
    mat = (2.5, 6.0)
    lines = ["crane pad under the worst outrigger (2,400 kN on a 2.5 x 6 m mat, teaching)",
             "  depth below mat m   pressure kPa   layer there"]
    for zd, layer in ((0.0, "pad aggregate"), (1.0, "silty sand (top)"),
                      (2.5, "silty clay, soft (T07)")):
        lines.append(f"  {zd:17.1f}   {cv.spread_pressure(load, *mat, zd):12.0f}   {layer}")
    lines += ["  on firm ground the pressure falls quickly with depth; at",
              "  T07 the soft clay 2.5 m down still sees about 60 kPa -",
              "  the crane company's load data and a pad check by the",
              "  civil engineer are needed there before the main lift",
              "  (ch 31 plans the lifts)"]
    emit("b_cranepad", lines)


def drainage() -> None:
    e = src.extremes()
    mu, beta = sx.gumbel_fit_moments(e["rain_1h"])
    area, length, slope = 3.2, 2500.0, 0.01
    tc = cv.kirpich_tc(length, slope)
    lines = ["the site road crossing the wadi: design flow and culverts",
             f"  catchment {area} km2, flow length {length / 1000:.1f} km, slope {100 * slope:.0f} %",
             f"  time of concentration (Kirpich) {tc:.0f} min",
             "  return yrs   1-h rain mm   intensity at tc mm/h   peak Q m3/s   0.9 m pipes"]
    q_pipe = cv.pipe_full_q(0.024, 0.9, 0.01)
    rows = []
    for t in (10, 25, 50):
        r1 = cv.gumbel_return(mu, beta, t)
        i_tc = r1 * (60 / tc) ** 0.6                 # duration scaling (teaching)
        q = cv.rational_peak(0.35, i_tc, area)
        n = math.ceil(q / q_pipe)
        lines.append(f"  {t:9d}   {r1:11.1f}   {i_tc:20.1f}   {q:11.1f}   {n:11d}")
        rows.append((t, f"{q:.2f}"))
    lines += [f"  one 0.9 m corrugated pipe at 1 % carries {q_pipe:.2f} m3/s full",
              "  (C 0.35, intensity scaled from the 1-hour value by",
              "  (60/tc)^0.6 - both teaching); a ford or a box culvert",
              "  may be cheaper than a row of pipes - and the road must",
              "  survive the storm it is not designed for (overtopping",
              "  path, scour protection)"]
    emit("b_drainage", lines)


def erosion() -> None:
    lines = ["soil loss from disturbed ground (USLE, R 300, K 0.30; teaching)",
             "  surface                          slope %   length m   LS     C     t/ha/yr"]
    cases = [("road cut, bare, construction", 15, 20, 1.0), ("pad fill slope, bare", 30, 8, 1.0),
             ("PV block, graded, bare", 1, 100, 1.0), ("PV block, reinstated cover", 1, 100, 0.15),
             ("road cut, reinstated", 15, 20, 0.2)]
    rows = []
    for k, (name, sl, ln, c) in enumerate(cases, 1):
        ls = cv.ls_factor(ln, sl)
        a = cv.usle(src.SOIL["r_factor"], src.SOIL["k_factor"], ls, c, 1.0)
        lines.append(f"  {name:32s} {sl:7d}   {ln:8d}   {ls:4.2f}   {c:4.2f}   {a:7.1f}")
        rows.append((k, f"{a:.1f}"))
    csv("ch29-erosion.csv", "k,a", rows)
    lines += ["  steep, bare cut slopes lose the most; reinstating cover",
              "  cuts the loss by five to seven times - sediment control",
              "  (lesson C) is planned for the bare months, and the PV",
              "  block is graded as little as possible"]
    emit("b_erosion", lines)


def trench_water() -> None:
    lines = ["water in an open cable trench where groundwater is shallow (Dupuit)",
             "  place                 k m/s    water below ground m   inflow per 100 m L/s"]
    for name, k, water in (("wadi crossing", 1e-4, 1.0), ("near T07 (clay)", 1e-6, 3.0)):
        depth = 1.3
        if water >= depth:
            lines.append(f"  {name:20s}  {k:7.0e}   {water:20.1f}   {'dry':>18s}")
            continue
        h, hw = 6.0 - water, 6.0 - depth                     # head above an aquitard at 6 m
        q = 2 * cv.trench_inflow(k, h, hw, 30.0) * 100 * 1000
        lines.append(f"  {name:20s}  {k:7.0e}   {water:20.1f}   {q:18.2f}")
    lines += ["  only the wadi crossing meets water at trench depth: there",
              "  the crossing is timed for the dry season or pumped, and",
              "  the pumped water is settled before release (lesson C)"]
    emit("b_trench", lines)


if __name__ == "__main__":
    road_grades()
    aggregate()
    crane_pad()
    drainage()
    erosion()
    trench_water()
