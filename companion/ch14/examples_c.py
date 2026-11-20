"""Chapter 14, section C - buildability and impact of the two layouts:
access roads (length, grades, wadi crossings), crane pads (earthworks),
noise at the dwellings, geometric shadow-flicker hours, the raptor nest
and the wetland. Teaching screening levels only (A-260); the authority's
rules decide (chapters 33 and 55-57).

Run from the project root:   python -m companion.ch14.examples_c
Writes companion/ch14/expected/c_*.txt and diagrams/data/ch14-*.csv.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from companion.ch14 import sources as src
from companion.ch14.common import csv, emit
from plantp import siting as st, solar, wind as w

G = src.GRID
LW = 106.0                 # dB(A), declared sound power (A-234)
GRADE = 0.10               # steepest road grade for turbine transport (teaching)
NOISE_SCREEN = 40.0        # dB(A), teaching screening level, not a limit


def z_at(pts) -> np.ndarray:
    p = np.asarray(pts, float)
    return G.sample(src.terrain(), p[:, 0], p[:, 1])


def wadi_y(x):
    (x0, y0), (x1, y1) = src.WADI
    return y0 + (y1 - y0) * (np.asarray(x) - x0) / (x1 - x0)


def road_network(xy):
    """Roads as a minimum spanning tree from the site entrance, with the
    grade of each straight edge from the terrain and the extra length a
    zig-zag needs to keep the grade."""
    pts = np.vstack([np.array(src.SITE_ENTRANCE), xy])
    edges, length = st.minimum_spanning_tree(pts)
    z = src.terrain()
    extra, steep, crossings, worst = 0.0, 0, 0, 0.0
    for a, b in edges:
        pa, pb = pts[a], pts[b]
        n = max(int(math.hypot(*(pb - pa)) // 25), 2)
        xs = np.linspace(pa[0], pb[0], n)
        ys = np.linspace(pa[1], pb[1], n)
        zs = G.interp(z, xs, ys)
        seg = math.hypot(*(pb - pa)) / (n - 1)
        g = np.abs(np.diff(zs)) / seg
        worst = max(worst, float(g.max()))
        over = g > GRADE
        if over.any():
            steep += 1
            extra += float(np.sum(np.abs(np.diff(zs))[over] / GRADE - seg))
        side = np.sign(ys - wadi_y(xs))
        crossings += int(np.sum(side[1:] != side[:-1]))
    return length, extra, steep, crossings, worst


def roads() -> None:
    lines = ["access roads from the site entrance (tree of straight edges, A-259):",
             "  layout              length km   steepest   edges > 10 %   extra km"
             "   wadi"]
    for name, xy in src.layouts().items():
        length, extra, steep, cross, worst = road_network(xy)
        lines.append(f"  {name:18s}   {length / 1e3:6.2f}     {100 * worst:5.1f} %"
                     f"        {steep:2d}         {extra / 1e3:5.2f}     {cross}")
    lines += ["  the ridge road climbs a flank steeper than 10 % (teaching limit",
              "  for blade and tower transport; the transport contractor's route",
              "  survey decides): a short zig-zag or a cut keeps the grade; both",
              "  layouts cross the wadi once, with a culvert or ford sized for",
              "  floods (chapter 29); profiles are sampled bilinearly"]
    emit("c_roads", lines)


def pads() -> None:
    """Crane pad 45 m x 30 m, long side along the steepest slope; planar
    ground levelled at its mean: cut = fill = W s L^2 / 8 (A-260)."""
    slope = st.slope_percent(src.terrain(), G.cell) / 100
    lines = ["crane pads 45 x 30 m on the local slope (planar, balanced):",
             "  layout              mean slope   steepest   cut = fill m3 (total)"]
    for name, xy in src.layouts().items():
        s = G.sample(slope, xy[:, 0], xy[:, 1])
        vol = 30 * s * 45 ** 2 / 8
        lines.append(f"  {name:18s}    {100 * s.mean():4.1f} %      {100 * s.max():4.1f} %"
                     f"      {vol.sum():8,.0f}")
    lines += ["  the crest is flat enough; the flanks are not: a pad on a 7 %",
              "  slope moves about 530 m3 each way, and the crane's ground",
              "  bearing and the pad's level tolerance come from the crane",
              "  supplier and the geotechnical survey (chapters 29 and 45)"]
    emit("c_pads", lines)


def noise_levels(xy):
    out = []
    for name, (hx, hy) in src.all_dwellings():
        r = np.hypot(xy[:, 0] - hx, xy[:, 1] - hy)
        r = np.hypot(r, src.HUB)
        lv = w.sum_levels([w.sound_pressure_level(LW, float(d)) for d in r])
        out.append((name, lv, float(np.min(np.hypot(xy[:, 0] - hx, xy[:, 1] - hy)))))
    return sorted(out, key=lambda t: -t[1])


def noise() -> None:
    lines = [f"noise at the dwellings, all turbines at {LW:.0f} dB(A) (A-234),",
             "  hemispherical spreading and air absorption (chapter 11 model):"]
    for name, xy in src.layouts().items():
        lv = noise_levels(xy)
        over = sum(1 for _, v, _ in lv if v > NOISE_SCREEN)
        lines.append(f"  {name}: highest three")
        for n, v, d in lv[:3]:
            lines.append(f"    {n:28s} {v:5.1f} dB(A) at {d:5,.0f} m")
        lines.append(f"    dwellings above the {NOISE_SCREEN:.0f} dB(A) screening level: {over}")
    lines += ["  the screening level is a teaching value: the applicable limit,",
              "  its time of day, the background noise and the propagation",
              "  method come from the authority and a specialist study"]
    emit("c_noise", lines)


@lru_cache(maxsize=1)
def sun_year(step_min: float = 5.0):
    days = np.repeat(np.arange(1, 366), int(24 * 60 / step_min))
    t = np.tile(np.arange(0, 24, step_min / 60), 365)
    el, az = solar.sun_position(34.0, days, t + step_min / 120)
    keep = el > 0
    return el[keep], az[keep], days[keep], step_min


def flicker_hours(xy, house, z_house):
    el, az, days, step = sun_year()
    m = st.flicker_minutes(house, [tuple(p) for p in xy], src.HUB, src.RADIUS,
                           el, az, step, z_house=z_house, z_turb=z_at(xy),
                           max_dist=10 * 2 * src.RADIUS)
    worst_day = 0.0
    if m.any():
        worst_day = max(float(m[days == d].sum()) for d in np.unique(days[m > 0]))
    return m.sum() / 60, worst_day


def flicker() -> None:
    lines = ["geometric shadow flicker (rotor as a sphere, always turning and",
             "  facing the sun, clear sky; sun above 3 deg; within 10 D):",
             "  layout / dwelling                 worst case h/yr   worst day min"]
    rows = []
    for name, xy in src.layouts().items():
        res = []
        for hn, (hx, hy) in src.all_dwellings():
            zh = float(z_at([(hx, hy)])[0])
            hrs, day = flicker_hours(xy, (hx, hy), zh)
            res.append((hn, hrs, day))
        res.sort(key=lambda t: -t[1])
        lines.append(f"  {name}")
        for hn, hrs, day in res[:3]:
            lines.append(f"    {hn:30s}   {hrs:7.1f}          {day:5.0f}")
        rows.append((name.split()[0], f"{res[0][1]:.1f}"))
    camp = src.DWELLINGS["herders' camp B (seasonal)"]
    zc = float(z_at([camp])[0])
    el, az, days, step = sun_year()
    per_day = {}
    for name, xy in src.layouts().items():
        m = st.flicker_minutes(camp, [tuple(q) for q in xy], src.HUB, src.RADIUS, el, az,
                               step, z_house=zc, z_turb=z_at(xy), max_dist=10 * 2 * src.RADIUS)
        per_day[name] = np.bincount(days, weights=m, minlength=366)[1:]
    names = list(per_day)
    csv("ch14-flicker.csv", "day,w1,w2",
        [(d + 1, f"{per_day[names[0]][d]:.0f}", f"{per_day[names[1]][d]:.0f}")
         for d in range(365)])
    lines += ["  the worst case ignores clouds, calm hours and the rotor's yaw;",
              "  expected hours are a fraction of it; limits (worst case,",
              "  expected, per day) and the remedy (shutdown at those minutes)",
              "  are the authority's and the manufacturer's"]
    emit("c_flicker", lines)


def ecology() -> None:
    lines = ["ecology screening (synthetic layers, specialist surveys needed):",
             "  layout              to the nest   within 1 km   to the wetland"]
    for name, xy in src.layouts().items():
        dn = np.hypot(xy[:, 0] - src.NEST[0], xy[:, 1] - src.NEST[1])
        dw = np.hypot(xy[:, 0] - src.WETLAND[0], xy[:, 1] - src.WETLAND[1])
        lines.append(f"  {name:18s}  {dn.min():7,.0f} m        {int((dn < 1000).sum()):2d}"
                     f"          {dw.min():7,.0f} m")
    lines += ["  the ridge row puts several turbines beside the nesting cliff and",
              "  along the ridge, where soaring birds use the updraft: a likely",
              "  fatal flaw until a year of bird surveys says otherwise",
              "  (chapter 33); the plain layout keeps clear of both"]
    emit("c_ecology", lines)


def aviation() -> None:
    lines = ["aviation screening (tip height 175 m above ground):"]
    for name, xy in src.layouts().items():
        zt = z_at(xy)
        lines.append(f"  {name:18s} highest tip {zt.max() + src.TIP:6.0f} m above sea level")
    lines += ["  the obstacle evaluation, marking and lighting are the aviation",
              "  authority's (chapters 55-57); radar and radio-link checks are",
              "  asked of their operators early, before the layout is frozen"]
    emit("c_aviation", lines)


if __name__ == "__main__":
    roads()
    pads()
    noise()
    flicker()
    ecology()
    aviation()
