"""Chapter 14, sections B4 and E2 - inside the PV block: where the ten
inverter stations go and how long the DC feeders become; and where the
site substation goes: a search over candidate positions that weighs the
wind strings, the PV feeders and the export line (teaching cost weights).

Run from the project root:   python -m companion.ch14.examples_j
Writes companion/ch14/expected/j_*.txt and diagrams/data/ch14-*.csv.
Synthetic site A-259; teaching weights A-266.
"""
from __future__ import annotations

import numpy as np

from companion.ch14 import examples_a as ea, lab_d, sources as src
from companion.ch14.common import csv, emit
from plantp import siting as st

G = src.GRID


def combiners():
    """210 combiner boxes spread evenly over the rows area (88 ha of the
    block's west part: 1,100 m x 800 m, D-013: 10 inverters x 21)."""
    x0, y0 = 6950.0, 2325.0
    xs = x0 + (np.arange(15) + 0.5) * (1100.0 / 15)
    ys = y0 + (np.arange(14) + 0.5) * (800.0 / 14)
    pts = np.array([(a, b) for b in ys for a in xs])[:210]
    return pts


def stations() -> None:
    cb = combiners()
    lines = ["DC feeders from 210 combiner boxes to 10 inverter stations",
             "  (straight-line length, PV block 1,100 x 800 m of rows):",
             "  station placement                 mean m   longest m   total km"]
    cases = {}
    # (a) all ten stations together at the block's east edge, next to the road
    cases["all at the east edge"] = np.array([[8050.0, 2325.0 + 80.0 * k] for k in range(10)])
    # (b) one row of stations through the middle
    cases["one row through the middle"] = np.array([[6950.0 + 110.0 * (k + 0.5), 2725.0]
                                                    for k in range(10)])
    # (c) a 5 x 2 grid, each at the centre of its sub-block
    cases["5 x 2 grid, sub-block centres"] = np.array([[6950.0 + 220.0 * (i + 0.5),
                                                       2325.0 + 400.0 * (j + 0.5)]
                                                      for j in range(2) for i in range(5)])
    best = None
    for name, stn in cases.items():
        # each station takes 21 combiners: assign by nearest, capacity-limited
        d = np.hypot(cb[:, None, 0] - stn[None, :, 0], cb[:, None, 1] - stn[None, :, 1])
        cap = np.zeros(len(stn), int)
        lengths = np.zeros(len(cb))
        for k in np.argsort(d.min(axis=1))[::-1]:
            order = np.argsort(d[k])
            for s_ in order:
                if cap[s_] < 21:
                    cap[s_] += 1
                    lengths[k] = d[k, s_]
                    break
        lines.append(f"  {name:32s}  {lengths.mean():6.0f}    {lengths.max():7.0f}"
                     f"     {lengths.sum() / 1e3:6.1f}")
        if best is None or lengths.mean() < best[1]:
            best = (name, lengths.mean())
    lines += [f"  the grid placement keeps the longest feeder near chapter 6's",
              "  180 m (A-018); stations at the edge save MV cable and road",
              "  but lengthen every DC feeder (losses, voltage drop, copper):",
              "  the block layout is a cable-and-road optimum (chapters 6, 24)"]
    emit("j_stations", lines)


def substation() -> None:
    """Weighted length (km-equivalent): wind strings x 1.0, two PV feeders
    from the block's centre x 1.0, export line to the 132 kV substation x
    1.6 with a 1.13 detour factor (A-266, teaching)."""
    xy = lab_d.layouts()["W2b plain, adjusted"]
    pv_c = np.array([7600.0, 2725.0])
    ok, _ = ea.buildable("pv")
    best, rows = None, []
    for yy in np.arange(1500.0, 6001.0, 250.0):
        for xx in np.arange(4000.0, 9001.0, 250.0):
            if not ok[G.index(xx, yy)]:
                continue
            _, strings = st.radial_strings(xy, (xx, yy), 4)
            pv = 2 * np.hypot(*(pv_c - (xx, yy)))
            exp = 1.13 * np.hypot(src.GRID_SUB[0] - xx, src.GRID_SUB[1] - yy)
            cost = (strings + pv + 1.6 * exp) / 1e3
            rows.append((f"{xx / 1e3:.2f}", f"{yy / 1e3:.2f}", f"{cost:.2f}"))
            if best is None or cost < best[0]:
                best = (cost, xx, yy, strings, pv, exp)
    x0, y0 = src.SITE_SUB
    _, s0 = st.radial_strings(xy, (x0, y0), 4)
    pv0 = 2 * np.hypot(*(pv_c - (x0, y0)))
    e0 = 1.13 * np.hypot(src.GRID_SUB[0] - x0, src.GRID_SUB[1] - y0)
    c0 = (s0 + pv0 + 1.6 * e0) / 1e3
    csv("ch14-subsearch.csv", "x,y,c", rows)
    lines = ["site substation position: weighted cable and line length (A-266):",
             "  position           strings km  PV feeders km  export km  weighted",
             f"  chosen (6.5, 3.5)    {s0 / 1e3:6.2f}       {pv0 / 1e3:5.2f}        {e0 / 1e3:5.2f}"
             f"     {c0:6.2f}",
             f"  best ({best[1] / 1e3:.2f}, {best[2] / 1e3:.2f})   {best[3] / 1e3:6.2f}       {best[4] / 1e3:5.2f}"
             f"        {best[5] / 1e3:5.2f}     {best[0]:6.2f}",
             f"  the search saves {100 * (1 - best[0] / c0):.1f} % of the weighted length by moving",
             "  the substation to the west edge of the PV block, nearer the",
             "  PV and the grid; the weights decide where the",
             "  optimum lies, and the export corridor, ground, access and land",
             "  users decide whether it can go there"]
    emit("j_substation", lines)


def colocation() -> None:
    """PV between the W2b rows: the land between x 3.6 and 4.8 km, y 1.5 to
    5.7 km, outside the ice zones (375 m) and outside the long winter
    shadow north of each turbine (a 150 m wide strip 500 m long, teaching)."""
    xy = lab_d.layouts()["W2b plain, adjusted"]
    x, y = G.mesh()
    box = (x > 3600) & (x < 4800) & (y > 1500) & (y < 5700)
    ice = np.zeros(x.shape, bool)
    shade = np.zeros(x.shape, bool)
    for tx, ty in xy:
        ice |= np.hypot(x - tx, y - ty) < 1.5 * (2 * src.RADIUS + src.HUB)
        shade |= (np.abs(x - tx) < 75) & (y > ty) & (y < ty + 500)
    ok_pv, _ = ea.buildable("pv")
    free = box & ~ice & ~shade & ok_pv
    graze = st.in_polygon(x, y, src.TENURE["customary grazing (Apr-Oct)"])
    a = G.cell ** 2 / 1e4
    lines = ["PV between the turbine rows of W2b (co-location screening):",
             f"  land between the rows {box.sum() * a:,.0f} ha; outside the ice zones"
             f" {(box & ~ice).sum() * a:,.0f} ha",
             f"  also outside the winter shadow strips and PV exclusions:"
             f" {free.sum() * a:,.0f} ha",
             f"    of it outside the customary grazing area: {(free & ~graze).sum() * a:,.0f} ha"
             " (88 ha needed)",
             "  co-location is possible here: the ice zones take less than half",
             "  the space; it would shorten the PV cables to the strings, but",
             "  the block would fence land near the herders' area, PV crews",
             "  would work beside the ice zones, and the east block keeps the",
             "  wind and PV apart for maintenance: a trade for the consultation"]
    emit("j_colocation", lines)


if __name__ == "__main__":
    stations()
    substation()
    colocation()
