"""Chapter 14, section A - constraints and spatial evidence: the layer
inventory of the synthetic site, terrain and slope classes, the teaching
setbacks and the buildable area they leave for turbines and for PV,
the effect of the terrain model's resolution, and the water balance of
the spring against the plant's construction and cleaning demand.

Run from the project root:   python -m companion.ch14.examples_a
Writes companion/ch14/expected/a_*.txt and diagrams/data/ch14-*.csv.
Synthetic site A-259; teaching setbacks A-260; water figures A-261.
"""
from __future__ import annotations

import numpy as np

from companion.ch14 import sources as src
from companion.ch14.common import csv, emit
from plantp import siting as st

G = src.GRID
CELL_HA = G.cell ** 2 / 1e4

# teaching setbacks (A-260): NOT any authority's rule; verify (ch 55-57)
WT_SETBACK = {"dwelling": 600.0, "road": 1.1 * src.TIP, "20 kV line": 1.5 * src.TIP,
              "raptor nest": 1000.0, "wetland": 300.0, "cemetery": 150.0,
              "spring": 300.0, "channel": 50.0, "wadi": 100.0}
PV_SETBACK = {"dwelling": 100.0, "road": 30.0, "20 kV line": 30.0, "raptor nest": 300.0,
              "wetland": 300.0, "cemetery": 100.0, "spring": 200.0, "channel": 30.0,
              "wadi": 150.0}
WT_SLOPE, PV_SLOPE = 10.0, 5.0


def distances() -> dict[str, np.ndarray]:
    x, y = G.mesh()
    homes = [p for _, p in src.all_dwellings()]
    return {"dwelling": st.distance_to(x, y, homes),
            "road": np.minimum(st.distance_to_segments(x, y, src.ROAD),
                               st.distance_to_segments(x, y, src.TRACK)),
            "20 kV line": st.distance_to_segments(x, y, src.LINE_20KV),
            "raptor nest": st.distance_to(x, y, [src.NEST]),
            "wetland": st.distance_to(x, y, [src.WETLAND]),
            "cemetery": st.distance_to(x, y, [src.CEMETERY]),
            "spring": st.distance_to(x, y, [src.SPRING]),
            "channel": st.distance_to_segments(x, y, src.CHANNEL),
            "wadi": st.distance_to_segments(x, y, src.WADI)}


def site_mask() -> np.ndarray:
    """Cells of the project land (west of the corridor farmland)."""
    x, _ = G.mesh()
    return x < 9000.0


def buildable(kind: str) -> tuple[np.ndarray, dict]:
    d = distances()
    sb, smax = (WT_SETBACK, WT_SLOPE) if kind == "wt" else (PV_SETBACK, PV_SLOPE)
    x, y = G.mesh()
    ok = site_mask().copy()
    lost = {}
    slope = st.slope_percent(src.terrain(), G.cell)
    for name, r in sb.items():
        m = d[name] < r
        lost[name] = float((m & site_mask()).sum() * CELL_HA)
        ok &= ~m
    m = slope > smax
    lost["slope"] = float((m & site_mask()).sum() * CELL_HA)
    ok &= ~m
    if kind == "pv":
        for nm, poly in src.TENURE.items():
            if nm.startswith("private"):
                m = st.in_polygon(x, y, poly)
                lost[nm] = float((m & site_mask()).sum() * CELL_HA)
                ok &= ~m
    return ok, lost


def layers() -> None:
    x, y = G.mesh()
    site = site_mask()
    total = site.sum() * CELL_HA
    lines = ["layer inventory of the screening window (synthetic, A-259):",
             f"  window 13.0 x 7.0 km, raster {G.cell:.0f} m; project land west of"
             f" x = 9 km: {total:,.0f} ha",
             "  land use and tenure (screening survey, to verify with users):"]
    used = np.zeros(x.shape, bool)
    for name, poly in src.TENURE.items():
        m = st.in_polygon(x, y, poly)
        used |= m
        lines.append(f"    {name:30s} {m.sum() * CELL_HA:7,.0f} ha")
    lines.append(f"    {'state rangeland (rest)':30s} {(site & ~used).sum() * CELL_HA:7,.0f} ha")
    lines += [f"  dwellings: {len(src.DWELLINGS)} isolated (one seasonal) and"
              f" {len(src.village())} in the village",
              "  points: spring, raptor nest, wetland, cemetery, caravanserai ruin",
              "  lines: road, village track, 20 kV line, irrigation channel, wadi",
              "  each layer carries its source, date, accuracy and owner in the",
              "  constraint register; a layer without them is a rumour"]
    emit("a_layers", lines)


def terrain_classes() -> None:
    z = src.terrain()
    slope = st.slope_percent(z, G.cell)
    site = site_mask()
    edges = [0, 2, 5, 10, 15, 100]
    lines = ["terrain of the project land (synthetic, A-259):",
             f"  height {z[site].min():.0f} .. {z[site].max():.0f} m; ridge crest"
             f" about {z[G.index(1800, 4000)]:.0f} m",
             "  slope class      share of land"]
    for a, b in zip(edges[:-1], edges[1:]):
        m = site & (slope >= a) & (slope < b)
        lab = f"{a}-{b} %" if b < 100 else f"> {a} %"
        lines.append(f"  {lab:14s}   {100 * m.mean() / site.mean():5.1f} %")
    sp = st.hill_speedup(z, G.cell, 800.0)
    lines += [f"  teaching speed-up at the crest {100 * sp[G.index(1800, 4000)]:+.1f} %,"
              f" on the plain {100 * sp[G.index(4200, 4000)]:+.1f} %",
              "  slopes steer roads, pads and PV tables; the crest's speed-up",
              "  is energy, its flanks are access and earthworks"]
    emit("a_terrain", lines)
    rows = []
    for j in range(0, G.ny, 4):
        for i in range(0, G.nx, 4):
            xx = G.x0 + (i + 0.5) * G.cell
            yy = G.y0 + (j + 0.5) * G.cell
            rows.append((f"{xx / 1000:.2f}", f"{yy / 1000:.2f}", f"{z[j, i]:.1f}"))
    csv("ch14-terrain.csv", "x,y,z", rows)


def setbacks() -> None:
    lines = ["buildable land after the teaching setbacks (A-260, verify with",
             "  the authority; distances in m):"]
    for kind, sb, smax in (("wt", WT_SETBACK, WT_SLOPE), ("pv", PV_SETBACK, PV_SLOPE)):
        ok, lost = buildable(kind)
        name = "turbines" if kind == "wt" else "PV"
        lines.append(f"  {name}: buildable {ok.sum() * CELL_HA:,.0f} ha of"
                     f" {site_mask().sum() * CELL_HA:,.0f} ha")
        biggest = sorted(lost.items(), key=lambda t: -t[1])[:4]
        lines.append("    largest exclusions: " + "; ".join(
            f"{k} {v:,.0f} ha" for k, v in biggest[:2]) + ";")
        lines.append("      " + "; ".join(f"{k} {v:,.0f} ha" for k, v in biggest[2:]))
    lines += [f"  turbine setbacks used: dwelling {WT_SETBACK['dwelling']:.0f},"
              f" road {WT_SETBACK['road']:.0f} (1.1 x tip),",
              f"    20 kV line {WT_SETBACK['20 kV line']:.0f}, nest"
              f" {WT_SETBACK['raptor nest']:.0f}, slope {WT_SLOPE:.0f} %",
              "  exclusions overlap: the shares do not add up; the binding",
              "  constraint differs between the ridge and the plain"]
    emit("a_setbacks", lines)
    ok_wt, _ = buildable("wt")
    ok_pv, _ = buildable("pv")
    rows = []
    for j in range(0, G.ny, 4):
        for i in range(0, 180, 4):
            xx = G.x0 + (i + 0.5) * G.cell
            yy = G.y0 + (j + 0.5) * G.cell
            rows.append((f"{xx / 1000:.2f}", f"{yy / 1000:.2f}",
                         int(ok_wt[j, i]) + 2 * int(ok_pv[j, i])))
    csv("ch14-buildable.csv", "x,y,c", rows)


def resolution() -> None:
    z = src.terrain()
    site = site_mask()
    s50 = st.slope_percent(z, 50.0)
    z200 = z[::4, ::4]
    s200 = st.slope_percent(z200, 200.0)
    site200 = site[::4, ::4]
    lines = ["terrain-model resolution and slope (same terrain):",
             f"  50 m raster:  steepest {s50[site].max():5.1f} %, area above 10 %"
             f" {100 * (s50[site] > 10).mean():4.1f} %",
             f"  200 m raster: steepest {s200[site200].max():5.1f} %, area above 10 %"
             f" {100 * (s200[site200] > 10).mean():4.1f} %",
             "  a coarse model smooths the steep cells away: it overstates the",
             "  buildable land and understates road gradients; screening uses",
             "  what exists, micro-siting needs a survey (chapter 29)"]
    emit("a_resolution", lines)


def water() -> None:
    """Spring flow and demands (A-261, teaching): flow 6.0 L/s in spring,
    2.0 L/s in late summer; village 1.2 L/s and herders 0.3 L/s all year;
    farm irrigation 2.5 L/s May-September. Plant: 12 foundations of 650 m3
    concrete at 0.18 m3 water per m3, road and pad dust suppression 40 m3 a
    day for 9 months, PV module cleaning 0.5 L/m2 six times a year on
    281,000 m2 of modules (chapter 10, D-014)."""
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    flow = np.array([4.0, 4.5, 5.5, 6.0, 5.0, 3.5, 2.5, 2.0, 2.0, 2.5, 3.0, 3.5])
    irr = np.array([0, 0, 0, 0, 2.5, 2.5, 2.5, 2.5, 2.5, 0, 0, 0])
    other = 1.2 + 0.3 + irr
    spare = flow - other
    conc = 12 * 650 * 0.18
    dust = 40 * 30 * 9
    clean = 281_000 * 0.5e-3 * 6
    lines = ["water: the spring against existing uses and the plant (A-261):",
             "  month   flow L/s   existing uses   spare"]
    for m, f, o, s in zip(months, flow, other, spare):
        lines.append(f"  {m}      {f:4.1f}        {o:4.1f}          {s:+4.1f}")
    lines += [f"  construction {conc + dust:,.0f} m3 (concrete {conc:,.0f},"
              f" dust {dust:,.0f}); cleaning {clean:,.0f} m3/yr",
              f"  dust suppression alone needs {40 / 86.4:.2f} L/s on working days",
              "  in Jul-Sep the spring has no spare water: the plant must not",
              "  draw on it;",
              "  options: a licensed well, treated water trucked in, dry or",
              "  robotic cleaning; rights and permits are verified, not assumed"]
    emit("a_water", lines)
    csv("ch14-water.csv", "m,flow,uses", [(k + 1, f, f"{o:.1f}")
                                          for k, (f, o) in enumerate(zip(flow, other))])


if __name__ == "__main__":
    layers()
    terrain_classes()
    setbacks()
    resolution()
    water()
