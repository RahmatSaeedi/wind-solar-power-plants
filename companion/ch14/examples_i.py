"""Chapter 14, sections A3 and C3 - flow-model validity and cross-prediction
from the mast to each turbine (ruggedness index, distance, height), the
zone of theoretical visibility of the turbines from the village and the
camp (line of sight over the terrain), and ice-throw risk zones around
the turbines (a published empirical rule of thumb).

Run from the project root:   python -m companion.ch14.examples_i
Writes companion/ch14/expected/i2_*.txt and diagrams/data/ch14-*.csv.
Synthetic site A-259; teaching values A-265 (cross-prediction terms).
"""
from __future__ import annotations

import numpy as np

from companion.ch14 import lab_d, sources as src
from companion.ch14.common import csv, emit
from plantp import siting as st

G = src.GRID
MAST = (4200.0, 3600.0)        # the chapter 13 mast, between the plain rows


def rix(z: np.ndarray, cell: float, radius: float = 3500.0, steep: float = 0.30) -> np.ndarray:
    """Ruggedness index: share of the terrain within `radius` steeper than
    `steep` (rise over run). Linear flow models lose accuracy where it is
    large; the idea is published (Bowen and Mortensen), the numbers here
    are a teaching computation on the synthetic terrain."""
    s = st.slope_percent(z, cell) / 100 > steep
    n = int(radius / cell)
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1]
    disk = (xx ** 2 + yy ** 2) <= n ** 2
    from scipy import ndimage
    num = ndimage.convolve(s.astype(float), disk.astype(float), mode="constant")
    den = ndimage.convolve(np.ones_like(z), disk.astype(float), mode="constant")
    return num / den


def cross() -> None:
    """Teaching cross-prediction uncertainty of the speed from the mast to a
    turbine (A-265): 0.5 % + 0.5 % per km + 1.0 % per 10 m of height
    difference + 2 % per 10 % of ruggedness difference, in quadrature
    with nothing else (a reviewer's model replaces it)."""
    z = src.terrain()
    r = rix(z, G.cell)
    r3 = rix(3 * (z - z.min()) + z.min(), G.cell)
    zm = float(G.sample(z, [MAST[0]], [MAST[1]])[0])
    lines = ["cross-prediction from the mast to the turbines (A-265, teaching):",
             f"  ruggedness index (share steeper than 30 % within 3.5 km): site"
             f" max {100 * r.max():.1f} %",
             f"    the same terrain three times steeper: max {100 * r3.max():.1f} %",
             "  layout              mean km   mean |dz| m   u(speed) mean   max"]
    rows = []
    for name, xy in lab_d.layouts().items():
        if name.startswith("W2 "):
            continue
        d = np.hypot(xy[:, 0] - MAST[0], xy[:, 1] - MAST[1]) / 1e3
        dz = np.abs(G.sample(z, xy[:, 0], xy[:, 1]) - zm)
        drix = np.abs(G.sample(r, xy[:, 0], xy[:, 1]) - float(G.sample(r, [MAST[0]], [MAST[1]])[0]))
        u = 0.5 + 0.5 * d + 1.0 * dz / 10 + 2.0 * drix * 100 / 10
        lines.append(f"  {name:18s}   {d.mean():5.2f}     {dz.mean():6.1f}       {u.mean():5.2f} %"
                     f"      {u.max():.2f} %")
        rows.append((name.split()[0], f"{u.mean():.2f}"))
    lines += ["  the ridge turbines are far from the mast and 60 m higher: the",
              "  speed carried to them is about five times less certain than to",
              "  the plain turbines;",
              "  a second mast or a lidar on the ridge would buy it back",
              "  (U-049); real projects use a validated flow model and its",
              "  documented cross-prediction errors"]
    emit("i2_cross", lines)


def visible_count(xy, obs, z, h_eye: float = 2.0, target: float = None) -> int:
    """Turbines whose blade tip is in line of sight from an observer."""
    zt = G.interp(z, xy[:, 0], xy[:, 1])
    zo = float(G.interp(z, [obs[0]], [obs[1]])[0]) + h_eye
    target = src.TIP if target is None else target
    n = 0
    for (tx, ty), zb in zip(xy, zt):
        dist = np.hypot(tx - obs[0], ty - obs[1])
        k = max(int(dist // 25), 2)
        xs = np.linspace(obs[0], tx, k)[1:-1]
        ys = np.linspace(obs[1], ty, k)[1:-1]
        zg = G.interp(z, xs, ys)
        frac = np.linspace(0, 1, k)[1:-1]
        line = zo + (zb + target - zo) * frac
        n += int(np.all(zg < line))
    return n


def ztv() -> None:
    z = src.terrain()
    lines = ["zone of theoretical visibility: turbines whose tip is in sight",
             "  (bare terrain, no buildings or trees; eye at 2 m):",
             "  observer                W1 ridge   W2b plain"]
    xy1 = lab_d.layouts()["W1 ridge (1 row)"]
    xy2 = lab_d.layouts()["W2b plain, adjusted"]
    obs = {"village centre": (7600.0, 6250.0), "herders' camp B": (3200.0, 5200.0),
           "farmhouse A": (5600.0, 2200.0), "roadside house D": (2600.0, 750.0),
           "east of the ridge, 3 km": (4800.0, 6600.0), "west of the ridge": (500.0, 4000.0)}
    for name, o in obs.items():
        lines.append(f"  {name:24s}  {visible_count(xy1, o, z):5d}       {visible_count(xy2, o, z):5d}")
    rows = []
    for yy in np.arange(250.0, 7000.0, 250.0):
        for xx in np.arange(250.0, 9000.0, 250.0):
            rows.append((f"{xx / 1e3:.2f}", f"{yy / 1e3:.2f}", visible_count(xy2, (xx, yy), z)))
    csv("ch14-ztv.csv", "x,y,n", rows)
    lines += ["  on flat ground the 175 m tips are seen from everywhere within",
              "  kilometres; the ridge hides the plain turbines from the west",
              "  and puts its own row on the skyline for everyone: landscape",
              "  and visual assessment is a specialist study with photomontages"]
    emit("i2_ztv", lines)


def ice() -> None:
    """Published empirical rule of thumb for ice throw from an operating
    turbine: about 1.5 x (rotor diameter + hub height) (Seifert et al.);
    teaching use only, the site's icing study decides."""
    d_ice = 1.5 * (2 * src.RADIUS + src.HUB)
    xy = lab_d.layouts()["W2b plain, adjusted"]
    pts = np.vstack([np.array(src.SITE_ENTRANCE), xy])
    edges, _ = st.minimum_spanning_tree(pts)
    x, y = G.mesh()
    zone = np.zeros(x.shape, bool)
    for tx, ty in xy:
        zone |= np.hypot(x - tx, y - ty) < d_ice
    road_in = 0.0
    for a, b in edges:
        n = max(int(np.hypot(*(pts[b] - pts[a])) // 10), 2)
        xs = np.linspace(pts[a][0], pts[b][0], n)
        ys = np.linspace(pts[a][1], pts[b][1], n)
        inside = np.array([zone[G.index(p, q)] for p, q in zip(xs, ys)])
        road_in += inside.mean() * np.hypot(*(pts[b] - pts[a]))
    homes = [hn for hn, (hx, hy) in src.all_dwellings()
             if np.min(np.hypot(xy[:, 0] - hx, xy[:, 1] - hy)) < d_ice]
    track = st.distance_to_segments(xy[:, 0], xy[:, 1], src.TRACK).min()
    lines = ["ice-throw screening of W2b (rule of thumb 1.5 x (D + H), teaching):",
             f"  zone radius {d_ice:.0f} m around each turbine; zone area"
             f" {zone.sum() * G.cell ** 2 / 1e4:,.0f} ha",
             f"  site roads inside the zones: {road_in / 1e3:.1f} km (the plant's own access)",
             f"  dwellings inside: {len(homes)}; nearest public track"
             f" {track:,.0f} m from a turbine",
             "  icing hours at the mast (chapter 13) say how often; ice",
             "  detection with automatic stop, signs and staff rules manage",
             "  the plant's own roads; public roads and paths inside a zone",
             "  need the specialist icing assessment"]
    emit("i2_ice", lines)


if __name__ == "__main__":
    cross()
    ztv()
    ice()
