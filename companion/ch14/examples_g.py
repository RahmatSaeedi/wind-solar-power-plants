"""Chapter 14, deeper sections - GIS in practice (distances and areas on a
flat patch, the cosine of latitude), PV rows on sloping ground and the
grading of the PV block, construction logistics (crane walk, temporary
land), a noise map and noise-reduced modes, collector cables along the
roads, and the herders' routes and construction windows.

Run from the project root:   python -m companion.ch14.examples_g
Writes companion/ch14/expected/g_*.txt and diagrams/data/ch14-*.csv.
Synthetic site A-259; teaching values A-260 and A-264 (logistics, modes,
grazing figures).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

from companion.ch14 import examples_c as ec, lab_d, sources as src
from companion.ch14.common import csv, emit
from plantp import geo, siting as st, wind as w

G = src.GRID
L_TABLE, TILT = 2 * 2.278, 25.0          # D-013 table and tilt
D_FLAT = 11.4                            # pitch at GCR 0.40 (ch 10)


def gis() -> None:
    lat = 34.0
    dlon = 13000.0 / (geo.R_EARTH_M * math.cos(math.radians(lat)) * math.pi / 180)
    true = float(geo.haversine_m(lat, 0.0, lat, dlon))
    e, n = geo.enu_offsets_m(lat, 0.0, lat + 0.06, dlon)
    flat = math.hypot(float(e), float(n))
    true2 = float(geo.haversine_m(lat, 0.0, lat + 0.06, dlon))
    sq_deg = 0.01 * 0.01
    naive = sq_deg * (geo.R_EARTH_M * math.pi / 180) ** 2
    right = naive * math.cos(math.radians(lat))
    lines = ["distances and areas on a flat local patch (latitude 34 N):",
             f"  13 km east-west: great circle {true:,.1f} m (flat patch exact",
             "    along the reference parallel)",
             f"  diagonal to 0.06 deg north: flat {flat:,.1f} m, great circle"
             f" {true2:,.1f} m",
             f"    ({flat - true2:+.1f} m, {100 * (flat / true2 - 1):+.3f} %)",
             f"  a 0.01 x 0.01 deg cell: {right / 1e4:,.1f} ha; computed in degrees as if",
             f"    square: {naive / 1e4:,.1f} ha ({100 * (naive / right - 1):+.0f} %)",
             "  over a 13 km window a flat patch errs by a few metres: fine",
             "  for screening, not for setting out; areas and lengths are never",
             "  computed in degrees; design and survey use a projected grid",
             "  with a stated datum (chapter 29)"]
    emit("g_gis", lines)


def pv_slope() -> None:
    """Pitch that keeps the flat design's limiting sun angle on a slope
    falling to the north (positive) or to the south (negative)."""
    b = math.radians(TILT)
    tan_a = L_TABLE * math.sin(b) / (D_FLAT - L_TABLE * math.cos(b))
    lines = [f"PV row pitch on sloping ground, tables {L_TABLE:.2f} m at {TILT:.0f} deg,"
             " same limiting",
             f"  sun angle as the flat design ({math.degrees(math.atan(tan_a)):.1f} deg at"
             f" {D_FLAT} m pitch):",
             "  ground slope        pitch m   GCR    land against flat"]
    rows = []
    for s in (-0.05, -0.03, 0.0, 0.03, 0.05, 0.08):
        d = L_TABLE * (math.sin(b) + math.cos(b) * tan_a) / (tan_a - s)
        lab = (f"{100 * s:+.0f} % to the north" if s > 0 else
               f"{-100 * s:.0f} % to the south" if s < 0 else "flat")
        lines.append(f"  {lab:18s}  {d:6.2f}    {L_TABLE / d:.3f}   {100 * (d / D_FLAT - 1):+5.1f} %")
        rows.append((f"{100 * s:.0f}", f"{d:.2f}"))
    csv("ch14-pvslope.csv", "slope,pitch", rows)
    lines += ["  a slope falling to the north lowers each row behind the one in",
              "  front: more pitch, more land; a southern slope lets rows close",
              "  up; the block goes on flat or south-facing ground"]
    emit("g_pvslope", lines)


def pv_grading() -> None:
    x, y = G.mesh()
    m = st.in_polygon(x, y, src.PV_BLOCK)
    z = src.terrain()[m]
    xs, ys = x[m], y[m]
    A = np.c_[xs - xs.mean(), ys - ys.mean(), np.ones(len(xs))]
    coef, *_ = np.linalg.lstsq(A, z, rcond=None)
    plane = A @ coef
    dz = z - plane
    a = G.cell ** 2
    slope_plane = 100 * math.hypot(coef[0], coef[1])
    sl = st.slope_percent(src.terrain(), G.cell)[m]
    lines = ["grading the PV block (119 ha) to its best-fit plane:",
             f"  plane slope {slope_plane:.2f} % (east {100 * coef[0]:+.2f}, north"
             f" {100 * coef[1]:+.2f} %)",
             f"  cells steeper than 2 %: {100 * (sl > 2).mean():.0f} %; than 5 %:"
             f" {100 * (sl > 5).mean():.0f} %",
             f"  cut {dz[dz > 0].sum() * a:,.0f} m3, fill {-dz[dz < 0].sum() * a:,.0f} m3;"
             f" mean depth {np.abs(dz).mean():.2f} m",
             "  fixed tables and many trackers follow a gentle plane without",
             "  grading; grading strips the topsoil, raises dust and erosion and",
             "  changes drainage: grade only where the structure demands it"]
    emit("g_pvgrading", lines)


def logistics() -> None:
    xy = lab_d.layouts()["W2b plain, adjusted"]
    _, walk = st.minimum_spanning_tree(xy)
    temp = 12 * 0.30 + 2.0 + 1.0 + 1.5             # pads' laydown, central yard, batch, PV yard
    lines = ["construction logistics of W2b (teaching areas, A-264):",
             f"  crane walk between pads (tree): {walk / 1e3:.2f} km on the plain",
             "  temporary land: laydown 0.30 ha per turbine, central yard 2.0 ha,",
             f"    concrete batch plant 1.0 ha, PV yard 1.5 ha: {temp:.1f} ha",
             "  permanent footprint 10.0 ha (wind) + 119 ha (PV block)",
             "  temporary land is restored and returned to its users: its",
             "  location (not on the herders' route), season and restoration",
             "  are part of the consultation; the crane supplier sets the",
             "  walking path and its grades (chapter 31)"]
    emit("g_logistics", lines)


def levels_at(xy, pts, lw=106.0):
    out = []
    for hx, hy in pts:
        r = np.hypot(np.hypot(xy[:, 0] - hx, xy[:, 1] - hy), src.HUB)
        out.append(w.sum_levels([w.sound_pressure_level(lw, float(d)) for d in r]))
    return np.array(out)


def noise_map() -> None:
    xy = lab_d.layouts()["W2b plain, adjusted"]
    gx = np.arange(1000.0, 7001.0, 100.0)
    gy = np.arange(500.0, 7001.0, 100.0)
    rows = []
    for yy in gy:
        lv = levels_at(xy, [(xx, yy) for xx in gx])
        for xx, v in zip(gx, lv):
            rows.append((f"{xx / 1e3:.1f}", f"{yy / 1e3:.1f}", f"{v:.1f}"))
    csv("ch14-noisemap.csv", "x,y,l", rows)
    camp = src.DWELLINGS["herders' camp B (seasonal)"]
    lines = ["noise map of W2b (106 dB(A) each, 100 m grid, chapter 11 model):",
             f"  grid {len(gx)} x {len(gy)} points; camp B {levels_at(xy, [camp])[0]:.1f} dB(A)",
             "  the 40 dB(A) line lies about 750 to 800 m outside the outer rows",
             "    (more than for one turbine: the others add)",
             "  a map shows where a new house would be affected, not only the",
             "  houses that exist today"]
    emit("g_noisemap", lines)


def modes() -> None:
    """Night mode -2 dB at 1.81 % energy cost per turbine and year when
    used every night (chapter 11, layout A); here only in the camp season
    (Apr-Oct, 7/12) and only on the turbines it needs (A-264)."""
    camp = src.DWELLINGS["herders' camp B (seasonal)"]
    lines = ["noise-reduced mode (-2 dB) to meet a target at the camp:",
             "  layout  target dB(A)  turbines in mode  level   energy cost"]
    for name, target in (("W2 plain (2 rows)", 40.0), ("W2b plain, adjusted", 36.0)):
        xy = lab_d.layouts()[name]
        lw = np.full(len(xy), 106.0)
        d = np.hypot(xy[:, 0] - camp[0], xy[:, 1] - camp[1])
        order = list(np.argsort(d))
        n = 0

        def level():
            r = np.hypot(d, src.HUB)
            return w.sum_levels([w.sound_pressure_level(lw[k], float(r[k])) for k in range(len(xy))])

        while level() > target and n < len(xy):
            lw[order[n]] -= 2.0
            n += 1
        lv = level()
        cost = 1.81 * n / 12 * 7 / 12
        ok = "met" if lv <= target else "NOT met"
        lines.append(f"  {name.split()[0]:6s}   {target:5.1f}           {n:2d}          {lv:5.1f}"
                     f"   {cost:.2f} % ({ok})")
    lines += ["  a mode lowers the level a little at the cost of energy; it",
              "  cannot rescue a turbine 400 m from a dwelling: there the layout",
              "  changes (W2b); targets here are teaching values, not limits"]
    emit("g_modes", lines)


def cables_roads() -> None:
    xy = lab_d.layouts()["W2b plain, adjusted"]
    pts = np.vstack([np.array(src.SITE_ENTRANCE), np.array(src.SITE_SUB), xy])
    edges, _ = st.minimum_spanning_tree(pts)
    n = len(pts)
    wts = [math.hypot(*(pts[a] - pts[b])) for a, b in edges]
    gr = csr_matrix((wts + wts, ([a for a, _ in edges] + [b for _, b in edges],
                                 [b for _, b in edges] + [a for a, _ in edges])), shape=(n, n))
    dist = shortest_path(gr, directed=False)
    strings, straight = st.radial_strings(xy, src.SITE_SUB, 4)
    along = 0.0
    for chain in strings:
        prev = 1                                       # substation node
        for k in chain:
            along += dist[prev, k + 2]
            prev = k + 2
    lines = ["collector strings of W2b: straight against along the roads:",
             f"  straight strings {straight / 1e3:.2f} km; along the road tree"
             f" {along / 1e3:.2f} km ({100 * (along / straight - 1):+.0f} %)",
             "  cables in the road verge share the trench works and stay off",
             "  the fields and grazing; the extra length costs losses and money",
             "  (chapter 24) but saves land, crossings and future digging"]
    emit("g_cablesroads", lines)


def segments_cross(p1, p2, q1, q2) -> bool:
    def orient(a, b, c):
        return np.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
    return (orient(p1, p2, q1) != orient(p1, p2, q2)) and (orient(q1, q2, p1) != orient(q1, q2, p2))


def herders() -> None:
    xy = lab_d.layouts()["W2b plain, adjusted"]
    pts = np.vstack([np.array(src.SITE_ENTRANCE), xy])
    edges, _ = st.minimum_spanning_tree(pts)
    camp = np.array(src.DWELLINGS["herders' camp B (seasonal)"])
    routes = {"camp to spring": [camp, np.array(src.SPRING)],
              "camp to the southern pasture": [camp, np.array([4200.0, 2200.0])]}
    lines = ["herders' routes against the W2b roads (straight routes, A-264):",
             "  route                          road crossings"]
    for name, (a, b) in routes.items():
        k = sum(segments_cross(a, b, pts[i], pts[j]) for i, j in edges)
        lines.append(f"  {name:30s} {k}")
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    camp_on = [m in ("Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct") for m in months]
    lines += ["  camp season Apr-Oct; heavy works near the camp (roads, pads,",
              "  foundations of the west row) planned for "
              + ", ".join(m for m, on in zip(months, camp_on) if not on),
              "  roads cross the routes at grade (open, no fence); crossings and",
              "  the timing are agreed with the families, not assumed"]
    emit("g_herders", lines)


if __name__ == "__main__":
    gis()
    pv_slope()
    pv_grading()
    logistics()
    noise_map()
    modes()
    cables_roads()
    herders()
