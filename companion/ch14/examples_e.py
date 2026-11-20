"""Chapter 14, section E - collector and export corridor screening: a
cost raster (slope, farmland, village, crossings, no-go buffers), the
straight line, the least-cost route and a southern route along the road
from the site substation to the 132 kV grid substation, the corridor of
near-optimal routes, and how the weights move the route.

Run from the project root:   python -m companion.ch14.examples_e
Writes companion/ch14/expected/e_*.txt and diagrams/data/ch14-*.csv.
Synthetic site A-259; teaching weights and buffers A-262.
"""
from __future__ import annotations

import numpy as np

from companion.ch14 import sources as src
from companion.ch14.common import csv, emit
from plantp import siting as st

G = src.GRID


def cost_raster(farm_w: float = 4.0, village_w: float = 6.0) -> np.ndarray:
    """Teaching cost per metre (A-262): 1 on rangeland, x3 on slopes over
    10 %, farmland x farm_w, village lands x village_w, x10 within 100 m of
    the wadi (a crossing), no-go within 300 m of the ruin, 150 m of the
    cemetery, 200 m of a dwelling and 300 m of the wetland."""
    x, y = G.mesh()
    c = np.ones(x.shape)
    c[st.slope_percent(src.terrain(), G.cell) > 10] *= 3
    for name, poly in src.TENURE.items():
        m = st.in_polygon(x, y, poly)
        if "farm" in name:
            c[m] *= farm_w
        if "village" in name:
            c[m] *= village_w
    c[st.distance_to_segments(x, y, src.WADI) < 100] *= 10
    homes = [p for _, p in src.all_dwellings()]
    nogo = ((st.distance_to(x, y, [src.RUIN]) < 300) | (st.distance_to(x, y, [src.CEMETERY]) < 150)
            | (st.distance_to(x, y, homes) < 200) | (st.distance_to(x, y, [src.WETLAND]) < 300))
    c[nogo] = np.inf
    return c


def route_stats(path) -> dict:
    p = np.asarray(path)
    x = G.x0 + (p[:, 1] + 0.5) * G.cell
    y = G.y0 + (p[:, 0] + 0.5) * G.cell
    farm = np.zeros(len(p), bool)
    for name, poly in src.TENURE.items():
        if "farm" in name:
            farm |= st.in_polygon(x, y, poly)
    seg = np.r_[0.0, G.cell * np.hypot(*np.diff(p, axis=0).T)]
    side = np.sign(y - np.interp(x, [src.WADI[0][0], src.WADI[1][0]],
                                 [src.WADI[0][1], src.WADI[1][1]]))
    homes = [q for _, q in src.all_dwellings()]
    near = [n for n, (hx, hy) in src.all_dwellings()
            if np.min(np.hypot(x - hx, y - hy)) < 500]
    del homes
    return {"km": seg.sum() / 1e3, "farm_km": seg[farm].sum() / 1e3,
            "wadi": int(np.sum(side[1:] != side[:-1])),
            "ruin": float(np.min(np.hypot(x - src.RUIN[0], y - src.RUIN[1]))),
            "near": len(near)}


def straight_path():
    a = G.index(*src.SITE_SUB)
    b = G.index(*src.GRID_SUB)
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1])) + 1
    js = np.round(np.linspace(a[0], b[0], n)).astype(int)
    is_ = np.round(np.linspace(a[1], b[1], n)).astype(int)
    return list(zip(js, is_))


def routes() -> None:
    c = cost_raster()
    a, b = G.index(*src.SITE_SUB), G.index(*src.GRID_SUB)
    lcp, cost = st.least_cost_path(c, a, b, G.cell)
    way = G.index(9000.0, 900.0)
    p1, c1 = st.least_cost_path(c, a, way, G.cell)
    p2, c2 = st.least_cost_path(c, way, b, G.cell)
    south = p1 + p2[1:]
    straight = straight_path()
    sc = sum(c[q] * G.cell for q in straight)
    lines = ["export route options, site substation to the 132 kV substation",
             "  (teaching cost raster A-262; straight-line distance"
             f" {np.hypot(src.GRID_SUB[0] - src.SITE_SUB[0], src.GRID_SUB[1] - src.SITE_SUB[1]) / 1e3:.2f} km):",
             "  route            km    farm km   wadi   ruin m   homes < 500 m   cost"]
    rows = []
    for name, path, cst in (("straight line", straight, sc), ("least cost", lcp, cost),
                            ("south, by road", south, c1 + c2)):
        s = route_stats(path)
        lines.append(f"  {name:15s} {s['km']:5.2f}   {s['farm_km']:5.2f}     {s['wadi']}"
                     f"    {s['ruin']:5,.0f}        {s['near']:2d}        {cst / 1e3:5.1f}")
        rows.append((name, path))
    lines += ["  the straight line is infinite-cost (it crosses the ruin's no-go",
              "  buffer and farmland); the least-cost route bends around them;",
              "  the road route is longer but uses the road for access and",
              "  keeps the line out of the fields; a cost raster is a way to",
              "  argue, not a verdict: its weights are written down"]
    emit("e_routes", lines)
    out = []
    for k, (name, path) in enumerate(rows):
        for j, i in path[::2] + [path[-1]]:
            out.append((k + 1, f"{(G.x0 + (i + 0.5) * G.cell) / 1e3:.3f}",
                        f"{(G.y0 + (j + 0.5) * G.cell) / 1e3:.3f}"))
    csv("ch14-routes.csv", "k,x,y", out)


def corridor() -> None:
    c = cost_raster()
    a, b = G.index(*src.SITE_SUB), G.index(*src.GRID_SUB)
    da = st.cost_distance(c, a, G.cell)
    db = st.cost_distance(c, b, G.cell)
    tot = da + db
    best = np.nanmin(tot[np.isfinite(tot)])
    lines = ["corridor of near-optimal routes (cells whose best route through",
             "  them costs at most the given share more than the best):",
             "  margin    corridor area ha   width at x = 10.5 km"]
    rows = []
    for tol in (0.01, 0.03, 0.05, 0.10):
        band = tot <= best * (1 + tol)
        col = G.index(10500.0, 3000.0)[1]
        width = band[:, col].sum() * G.cell
        lines.append(f"  {100 * tol:4.0f} %       {band.sum() * G.cell ** 2 / 1e4:8.0f}"
                     f"            {width:6.0f} m")
    band = tot <= best * 1.05
    for j in range(0, G.ny, 2):
        for i in range(120, G.nx, 2):
            if band[j, i]:
                rows.append((f"{(G.x0 + (i + 0.5) * G.cell) / 1e3:.3f}",
                             f"{(G.y0 + (j + 0.5) * G.cell) / 1e3:.3f}"))
    csv("ch14-corridor.csv", "x,y", rows)
    lines += ["  a corridor, not a line, goes to the surveys and the land",
              "  talks: the final alignment moves inside it as owners, ground",
              "  and crossings are known (route uncertainty)"]
    emit("e_corridor", lines)


def weights() -> None:
    a, b = G.index(*src.SITE_SUB), G.index(*src.GRID_SUB)
    lines = ["how the farmland weight moves the least-cost route:",
             "  farmland x   km     farmland km"]
    for fw in (1.0, 2.0, 4.0, 8.0):
        p, _ = st.least_cost_path(cost_raster(farm_w=fw), a, b, G.cell)
        s = route_stats(p)
        lines.append(f"  {fw:6.0f}     {s['km']:5.2f}     {s['farm_km']:5.2f}")
    lines += ["  a heavier weight trades length for fields: the weight is a",
              "  value judgement and is agreed with the people it stands for"]
    emit("e_weights", lines)


if __name__ == "__main__":
    routes()
    corridor()
    weights()
