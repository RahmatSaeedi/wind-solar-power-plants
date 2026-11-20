"""Chapter 29, lesson A: survey control and its error budget, the terrain
at the turbines and the PV block, the ground model between boreholes,
seismic refraction tied to the boreholes, SPT screening and a first
bearing and settlement estimate - all screening, none a design.

Run from the project root:   python -m companion.ch29.examples_a
Writes companion/ch29/expected/a_*.txt and diagrams/data/ch29-*.csv.
Teaching values (A-349).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import sources as s14
from companion.ch29 import sources as src
from companion.ch29.common import csv, emit
from plantp import civil as cv
from plantp import siting as st


def control() -> None:
    parts = {"base station coordinates (network)": 0.010, "RTK rover, single fix": 0.020,
             "setting out (pole and tripod)": 0.010, "monument stability": 0.005}
    total = math.sqrt(sum(v * v for v in parts.values()))
    lines = ["survey control: horizontal error budget (1 sigma, m, teaching)"]
    for k, v in parts.items():
        lines.append(f"  {k:38s} {v:6.3f}")
    lines.append(f"  combined (root sum of squares)         {total:6.3f}")
    lines += ["  tolerance                              value   ratio to 2 sigma"]
    for name, tol in (("anchor cage centre (teaching)", 0.050), ("PV pile row line", 0.030),
                      ("substation slab corner", 0.020)):
        lines.append(f"  {name:38s} {tol:5.3f}   {tol / (2 * total):16.2f}")
    lines += ["  the budget shows which tolerance the survey can hold with",
              "  margin (ratio above 1) and which needs a better method",
              "  (static GNSS or a total station from local control) -",
              "  chosen before setting out, not after the first misfit"]
    emit("a_control", lines)


def terrain() -> None:
    z = s14.terrain()
    g = s14.GRID
    slope = st.slope_percent(z, g.cell)
    lines = ["terrain at the turbines and the PV block (ch 14 grid, 50 m cells)",
             "  place     ground m   slope %   pad cut m3   pad fill m3 (40 x 40 m pad)"]
    rows = []
    for k, (x, y) in enumerate(src.TURBINES, 1):
        i, j = int(round(y / g.cell)), int(round(x / g.cell))
        xs5, ys5 = np.meshgrid(np.arange(x - 20, x + 20, 5.0) + 2.5, np.arange(y - 20, y + 20, 5.0) + 2.5)
        patch = g.interp(z, xs5, ys5)                  # bilinear, 5 m points on the pad
        cut, fill = st.cut_fill(patch, 5.0)[:2]
        lines.append(f"  T{k:02d}      {z[i, j]:8.1f}   {slope[i, j]:7.1f}   {cut:10.0f}   {fill:11.0f}")
        rows.append((f"T{k:02d}", f"{z[i, j]:.1f}", f"{slope[i, j]:.2f}"))
    xs = [p[0] for p in src.PV_BLOCK]
    ys = [p[1] for p in src.PV_BLOCK]
    sl = slope[int(min(ys) / g.cell):int(max(ys) / g.cell), int(min(xs) / g.cell):int(max(xs) / g.cell)]
    lines += [f"  PV block: mean slope {sl.mean():.1f} %, 95th percentile {np.percentile(sl, 95):.1f} %",
              "  (pad levelled at its mean ground: cut and fill balance)",
              "  the plain is gentle: pads need little earthworks; a 50 m",
              "  grid hides the metre-scale ground a pad or a tracker row",
              "  sits on - the topographic survey (0.5 m contours or a",
              "  drone model) replaces it before design"]
    csv("ch29-terrain.csv", "name,z,slope", rows)
    emit("a_terrain", lines)


# [start: idw]
def idw(xy, points, values, power: float = 2.0) -> float:
    """Inverse-distance-weighted estimate at xy from (points, values)."""
    d = np.array([math.dist(xy, p) for p in points])
    if d.min() < 1e-6:
        return float(values[int(d.argmin())])
    w = 1 / d ** power
    return float(np.sum(w * values) / np.sum(w))
# [end: idw]


def ground_model() -> None:
    bh = [b for b in src.BOREHOLES if b.name.startswith("BH-0") and "T" in b.name]
    pts = [b.xy for b in bh]
    dense = np.array([next(l_.top for l_ in b.layers if "dense" in l_.soil and "medium" not in l_.soil)
                      if any("dense" in l_.soil and "medium" not in l_.soil for l_ in b.layers) else np.nan
                      for b in bh])
    ok = ~np.isnan(dense)
    pts_ok = [p for p, o in zip(pts, ok) if o]
    lines = ["top of the dense layer (m) at turbines without a borehole: IDW estimate",
             "  turbine   estimate m   nearest boreholes range m   nearest borehole km"]
    for k, xy in enumerate(src.TURBINES, 1):
        if any(math.dist(xy, b.xy) < 1 for b in bh):
            continue
        est = idw(xy, pts_ok, dense[ok])
        d = np.array([math.dist(xy, p) for p in pts_ok])
        near = dense[ok][np.argsort(d)[:2]]
        lines.append(f"  T{k:02d}      {est:10.1f}   {near.min():9.1f} to {near.max():4.1f}"
                     f"            {d.min() / 1000:10.2f}")
    lines += ["  BH-04 (T07) has no dense layer at all - soft clay over",
              "  medium sand: an interpolation from its neighbours would",
              "  hide it; every turbine gets its own borehole (or a CPT)",
              "  before its foundation is designed, and the ground model",
              "  states where it is interpolated and where it is measured"]
    emit("a_ground", lines)


def refraction() -> None:
    lines = ["seismic refraction tied to the boreholes",
             "  line                          crossover m   v1 / v2 m/s   depth m"]
    for name, xc, v1, v2 in src.SEISMIC:
        lines.append(f"  {name:29s} {xc:11.0f}   {v1:4.0f} / {v2:4.0f}   {cv.refraction_depth(xc, v1, v2):7.1f}")
    lines += ["  boreholes along SL-1 meet weathered sandstone at 7-8 m; the",
              "  refraction puts its 2,100 m/s layer at about 14 m: the",
              "  methods see different things (the weathered rock is not",
              "  yet fast) - geophysics spans the ground between boreholes,",
              "  and boreholes tell it what its layers are"]
    emit("a_refraction", lines)


def spt_screen() -> None:
    lines = ["SPT N to a screening friction angle and bearing (square 20 m, 3.5 m deep)",
             "  (phi = 27.1 + 0.3 N60 - 0.00054 N60^2, a published screening fit;",
             "   energy ratio unknown: 45 to 80 % -> N60 range)",
             "  layer at 3.5 m            N    N60 range    phi deg   q_ult kPa   FS 3 kPa"]
    for name, n in (("sand and gravel, dense", 33), ("sand, medium dense (T07)", 18)):
        n60_lo, n60_hi = n * 45 / 60, n * 80 / 60
        phi = 27.1 + 0.3 * n60_lo - 0.00054 * n60_lo ** 2
        q = cv.bearing_square(0.0, phi, 19.0, 20.0, 3.5)
        lines.append(f"  {name:25s} {n:3d}   {n60_lo:4.0f} to {n60_hi:3.0f}   {phi:7.1f}   {q:9.0f}"
                     f"   {q / 3:8.0f}")
    s_dense = cv.elastic_settlement(200, 20, 60_000)
    s_med = cv.elastic_settlement(200, 20, 25_000)
    lines += [f"  settlement under 200 kPa: {1000 * s_dense:.0f} mm (E 60 MPa), {1000 * s_med:.0f} mm"
              " (E 25 MPa)",
              "  (lowest energy ratio used: the cautious end)",
              "  bearing is seldom what limits a turbine foundation on such",
              "  ground; settlement, rotational stiffness and the soft",
              "  layer at T07 are - questions for the geotechnical engineer",
              "  and ch 30, not a foundation chosen here"]
    emit("a_spt", lines)


if __name__ == "__main__":
    control()
    terrain()
    ground_model()
    refraction()
    spt_screen()
