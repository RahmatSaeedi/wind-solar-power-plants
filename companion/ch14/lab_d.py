"""Chapter 14, section D - layout comparison lab (the chapter's worked
example): the ridge row W1, the plain W2 and the plain adjusted away
from the herders' camp W2b, compared on energy, collector cable, roads,
earthworks, noise, flicker, ecology, land users and water; fatal flaws
first, then a weighted matrix; every assumption logged.

Run from the project root:   python -m companion.ch14.lab_d
Writes companion/ch14/expected/d_*.txt and diagrams/data/ch14-*.csv.
Synthetic site A-259, teaching screening values A-260, D-015, D-017.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch14 import examples_b as eb, examples_c as ec, sources as src
from companion.ch14.common import csv, emit
from plantp import siting as st

G = src.GRID
PAD_M2 = 45 * 30 + 0.25 * np.pi * 22 ** 2        # crane pad + foundation area
ROAD_W = 8.0                                     # road and shoulders, m (teaching)


def layouts() -> dict[str, np.ndarray]:
    out = dict(src.layouts())
    west = [[3600.0, 1500.0 + 600.0 * k] for k in range(6)]
    east = [[4800.0, 2700.0 + 600.0 * k] for k in range(6)]
    out["W2b plain, adjusted"] = np.array(west + east)
    return out


def footprint(xy) -> dict[str, float]:
    """Hectares of pads and roads on each land use (roads as straight
    tree edges, 8 m wide, sampled every 10 m)."""
    pts = np.vstack([np.array(src.SITE_ENTRANCE), xy])
    edges, _ = st.minimum_spanning_tree(pts)
    xs, ys, ws = [], [], []
    for a, b in edges:
        n = max(int(np.hypot(*(pts[b] - pts[a])) // 10), 2)
        xs += list(np.linspace(pts[a][0], pts[b][0], n))
        ys += list(np.linspace(pts[a][1], pts[b][1], n))
        ws += [ROAD_W * np.hypot(*(pts[b] - pts[a])) / n] * n
    xs, ys, ws = np.array(xs), np.array(ys), np.array(ws)
    out = {}
    for name, poly in src.TENURE.items():
        road = ws[st.in_polygon(xs, ys, poly)].sum()
        pads = PAD_M2 * st.in_polygon(xy[:, 0], xy[:, 1], poly).sum()
        out[name] = (road + pads) / 1e4
    out["total"] = (ws.sum() + PAD_M2 * len(xy)) / 1e4
    return out


@lru_cache(maxsize=None)
def metrics(name: str) -> dict:
    xy = layouts()[name]
    s = eb.speedups(xy)
    free, waked = eb.farm_energy(xy, s)
    pts = np.vstack([np.array(src.SITE_SUB), xy])
    _, mst = st.minimum_spanning_tree(pts)
    _, strings = st.radial_strings(xy, src.SITE_SUB, 4)
    road, extra, _, cross, worst = ec.road_network(xy)
    slope = st.slope_percent(src.terrain(), G.cell) / 100
    earth = float((30 * G.sample(slope, xy[:, 0], xy[:, 1]) * 45 ** 2 / 8).sum())
    noise = ec.noise_levels(xy)[0]
    flick = []
    for hn, (hx, hy) in src.all_dwellings():
        zh = float(ec.z_at([(hx, hy)])[0])
        flick.append((ec.flicker_hours(xy, (hx, hy), zh)[0], hn))
    flick.sort(reverse=True)
    dn = np.hypot(xy[:, 0] - src.NEST[0], xy[:, 1] - src.NEST[1])
    fp = footprint(xy)
    return {"energy": eb.LT * waked, "loss": 1 - waked / free, "mst": mst / 1e3,
            "strings": strings / 1e3, "road": (road + extra) / 1e3, "grade": worst,
            "earth": earth, "noise": noise, "flicker": flick[0], "nest_n": int((dn < 1000).sum()),
            "nest_d": float(dn.min()), "grazing": fp["customary grazing (Apr-Oct)"],
            "private": fp["private farm 1"] + fp["private farm 2"], "fp": fp["total"],
            "cross": cross}


def compare() -> None:
    names = list(layouts())
    m = {n: metrics(n) for n in names}
    short = ["W1", "W2", "W2b"]
    lines = ["three layouts compared (long term, teaching screening values):",
             "  quantity                         " + "".join(f"{s:>10s}" for s in short)]

    def row(label, key, fmt):
        lines.append(f"  {label:32s} " + "".join(f"{fmt(m[n][key]):>10s}" for n in names))

    row("farm energy, GWh a year", "energy", lambda v: f"{v:.1f}")
    row("wake loss", "loss", lambda v: f"{100 * v:.2f} %")
    row("collector tree, km", "mst", lambda v: f"{v:.2f}")
    row("collector strings, km", "strings", lambda v: f"{v:.2f}")
    row("roads incl. zig-zags, km", "road", lambda v: f"{v:.2f}")
    row("steepest road grade", "grade", lambda v: f"{100 * v:.1f} %")
    row("pad earthworks, cut m3", "earth", lambda v: f"{v:,.0f}")
    row("turbines within 1 km of nest", "nest_n", lambda v: f"{v}")
    row("highest noise, dB(A)", "noise", lambda v: f"{v[1]:.1f}")
    row("most flicker, h/yr worst case", "flicker", lambda v: f"{v[0]:.0f}")
    row("footprint, ha", "fp", lambda v: f"{v:.1f}")
    row("  of it customary grazing, ha", "grazing", lambda v: f"{v:.1f}")
    row("  of it private farms, ha", "private", lambda v: f"{v:.1f}")
    row("wadi crossings", "cross", lambda v: f"{v}")
    lines += ["  noise and flicker peaks are all at the herders' seasonal camp",
              "  (the W2b peak is below the 40 dB(A) screening level)"]
    emit("d_compare", lines)
    csv("ch14-turbines.csv", "k,x,y",
        [(k + 1, f"{x / 1e3:.3f}", f"{y / 1e3:.3f}")
         for k, xy in enumerate(layouts().values()) for x, y in xy])
    csv("ch14-compare.csv", "layout,energy,road,cable",
        [(s, f"{m[n]['energy']:.1f}", f"{m[n]['road']:.2f}", f"{m[n]['strings']:.2f}")
         for s, n in zip(short, names)])


def fatal() -> None:
    m = {n: metrics(n) for n in layouts()}
    lines = ["fatal flaws and red flags (screening; each needs its evidence):"]
    for n, v in m.items():
        flags = []
        if v["nest_n"] > 0:
            flags.append(f"FATAL until surveyed: {v['nest_n']} turbines within 1 km of"
                         f" the nest (nearest {v['nest_d']:.0f} m)")
        if v["noise"][1] > ec.NOISE_SCREEN:
            flags.append(f"RED: {v['noise'][0]} at {v['noise'][1]:.1f} dB(A)")
        if v["flicker"][0] > 0:
            flags.append(f"AMBER: {v['flicker'][1]} {v['flicker'][0]:.0f} h/yr"
                         " worst-case flicker")
        if v["grade"] > 0.10:
            flags.append(f"AMBER: road grade {100 * v['grade']:.1f} % on the flank")
        if v["grazing"] > 0:
            flags.append(f"AMBER: {v['grazing']:.1f} ha of customary grazing used:"
                         " consult the users")
        lines.append(f"  {n}")
        lines += [f"    - {f}" for f in flags] or ["    - none found at screening level"]
    lines += ["  flicker flags: check the authority's limit and plan shutdown;",
              "  a fatal flaw is not scored away: the matrix ranks only the",
              "  layouts that survive it"]
    emit("d_fatal", lines)


def matrix() -> None:
    names = [n for n in layouts() if metrics(n)["nest_n"] == 0]
    m = {n: metrics(n) for n in names}
    crit = [("energy", 0.30, True, "energy"), ("strings", 0.10, False, "cable"),
            ("road", 0.10, False, "roads"), ("noise", 0.15, False, "noise"),
            ("flicker", 0.15, False, "flicker"), ("grazing", 0.20, False, "grazing")]

    def val(n, k):
        v = m[n][k]
        return v[1] if k == "noise" else v[0] if k == "flicker" else v

    lines = ["weighted matrix of the layouts that survive the fatal flaws",
             "  (scores 0-10, best = 10, linear between the two; weights",
             "  teaching, A-260):",
             "  criterion   weight   " + "".join(f"{n.split()[0]:>8s}" for n in names)]
    tot = {n: 0.0 for n in names}
    for k, wgt, high, lab in crit:
        vs = [val(n, k) for n in names]
        lo, hi = min(vs), max(vs)
        sc = {}
        for n, v in zip(names, vs):
            s = 10.0 if hi == lo else 10 * ((v - lo) / (hi - lo) if high else (hi - v) / (hi - lo))
            sc[n] = s
            tot[n] += wgt * s
        lines.append(f"  {lab:10s}   {wgt:.2f}   " + "".join(f"{sc[n]:8.1f}" for n in names))
    lines.append("  total               " + "".join(f"{tot[n]:8.1f}" for n in names))
    lines += ["  W2b is better on every criterion but cable; with two options",
              "  the scores are all 0 or 10, so the matrix only records the",
              "  comparison: the reasons are written in the decision (D-018),",
              "  not hidden in the weights"]
    emit("d_matrix", lines)


if __name__ == "__main__":
    compare()
    fatal()
    matrix()
