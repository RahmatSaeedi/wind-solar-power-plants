"""Chapter 29, lesson Q (corridor and the supply of civil materials):
the 132 kV route straightened into angle points and tower types,
concrete supply for a continuous foundation pour, the aggregate source
and its trucks, cover to the reinforcement from a cover meter, the
operating curve of an attribute sampling plan for precast items, and
reinstatement monitoring along the corridor.

Run from the project root:   python -m companion.ch29.examples_q
Writes companion/ch29/expected/q_*.txt and diagrams/data/ch29-route.csv.
Teaching values (A-354, A-355); factory processes are in ch 47.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import examples_e as e14
from companion.ch14 import sources as s14
from companion.ch29.common import csv, emit
from plantp import siting as st

G = s14.GRID


# [start: rdp]
def rdp(pts: np.ndarray, tol: float) -> np.ndarray:
    """Douglas-Peucker simplification of a polyline (returns kept points)."""
    a, b = pts[0], pts[-1]
    ab = b - a
    nrm = np.hypot(*ab) or 1.0
    d = np.abs(ab[0] * (pts[:, 1] - a[1]) - ab[1] * (pts[:, 0] - a[0])) / nrm
    k = int(np.argmax(d))
    if d[k] <= tol:
        return np.array([a, b])
    left = rdp(pts[:k + 1], tol)
    right = rdp(pts[k:], tol)
    return np.vstack([left[:-1], right])
# [end: rdp]


def towers() -> None:
    c = e14.cost_raster()
    path, _ = st.least_cost_path(c, G.index(*s14.SITE_SUB), G.index(*s14.GRID_SUB), G.cell)
    p = np.array(path, float)
    xy = np.c_[G.x0 + (p[:, 1] + 0.5) * G.cell, G.y0 + (p[:, 0] + 0.5) * G.cell]
    lines = ["the least-cost route straightened (Douglas-Peucker) into angle points",
             "  tolerance m   angle points   length km   deviations deg"]
    kept = {}
    for tol in (0.0, 50.0, 150.0):
        q = xy if tol == 0 else rdp(xy, tol)
        seg = np.diff(q, axis=0)
        ang = np.degrees(np.arctan2(seg[:, 1], seg[:, 0]))
        dev = np.abs((np.diff(ang) + 180) % 360 - 180)
        dev = dev[dev > 0.5]
        km = float(np.sum(np.hypot(*seg.T))) / 1000
        kept[tol] = (q, dev, km)
        txt = ", ".join(f"{x:.0f}" for x in dev[:6]) + (" ..." if dev.size > 6 else "")
        lines.append(f"  {tol:11.0f}   {dev.size:12d}   {km:9.2f}   {txt}")
    q, dev, km = kept[150.0]
    csv("ch29-route.csv", "x,y", [(f"{a / 1000:.3f}", f"{b / 1000:.3f}") for a, b in q])
    sites = [q[0]]
    for a, b in zip(q[:-1], q[1:]):                  # equal spans <= 300 m on each straight
        n = math.ceil(np.hypot(*(b - a)) / 300)
        sites += [a + (b - a) * j / n for j in range(1, n + 1)]
    csv("ch29-towers.csv", "x,y", [(f"{a / 1000:.3f}", f"{b / 1000:.3f}") for a, b in sites])
    n_angle = int(np.sum(dev < 30))
    n_heavy = int(np.sum(dev >= 30))
    n_susp = len(sites) - n_angle - n_heavy - 2
    mass = n_susp * 9 + n_angle * 15 + (n_heavy + 2) * 22
    lines += [f"  with 150 m tolerance: {n_susp} suspension, {n_angle} light angle,",
              f"  {n_heavy + 2} heavy angle or terminal towers (an 86 deg turn is nearly a",
              "  dead end: the designer may split it into two angles)",
              f"  steel about {mass} t (teaching 9 / 15 / 22 t a tower)",
              "  the 50 m grid made a zigzag of the route: straightened, a",
              "  few deliberate angle points replace many small ones, and",
              "  each one that remains is a heavier tower and foundation"]
    emit("q_towers", lines)


def concrete_supply() -> None:
    vol, rate = 620.0, 60.0                       # m3, m3/h placed by two pumps (teaching)
    hours = vol / rate
    lines = ["concrete supply for one continuous 620 m3 foundation pour (teaching)",
             f"  placing rate {rate:.0f} m3/h -> {hours:.1f} h of pouring without a cold joint",
             "  source               km   cycle min   trucks of 8 m3   minutes in truck"]
    for name, km in (("site batching plant", 3.0), ("ready-mix in town", 45.0)):
        travel = 2 * km / 40 * 60
        cycle = 10 + travel + 15 + 5
        trucks = math.ceil(rate * cycle / 60 / 8)
        age = 10 + travel / 2 + 15
        lines.append(f"  {name:19s} {km:4.0f}   {cycle:9.0f}   {trucks:14d}   {age:16.0f}")
    lines += ["  (teaching limit 90 min from batching to placing in heat)",
              "  ready-mix from town misses the time limit even before",
              "  summer traffic and needs four times the trucks: a site batching",
              "  plant with a standby mixer and stocked cement is the usual",
              "  answer for twelve such pours - a factory on site (ch 47)"]
    emit("q_concrete", lines)


def aggregate_source() -> None:
    need_m3 = 28_000 * 6 * 0.3 + 12 * 1600 * 0.5
    tonnes = need_m3 * 2.0
    trips = tonnes / 25
    lines = ["aggregate for roads and pads (60,000 m3 = 120,000 t, teaching)",
             "  source                         km   truck trips   truck-km   diesel m3"]
    for name, km, share in (("quarry", 35.0, 1.0), ("on-site crushing of cut rock", 2.0, 0.6),
                            ("  + quarry for the rest", 35.0, 0.4)):
        t = trips * share
        tkm = t * 2 * km
        lines.append(f"  {name:29s} {km:4.0f}   {t:11,.0f}   {tkm:8,.0f}   {tkm * 0.4 / 1000:9.0f}")
    lines += ["  crushing the weathered sandstone met in the cuts would",
              "  save most of the haul, if its grading and strength pass",
              "  the road specification - a test, not an assumption; the",
              "  quarry's own permits and the route's bridges are checked",
              "  before the contract names it"]
    emit("q_aggregate", lines)


def cover() -> None:
    rng = np.random.default_rng(47)
    readings = np.round(57.5 + 5.5 * rng.standard_normal(40), 0)
    nominal, tol = 60.0, 10.0
    low = readings < nominal - tol
    lines = ["cover meter on one foundation cage before the pour (40 readings, mm)",
             f"  mean {readings.mean():.1f}, s {readings.std(ddof=1):.1f}, lowest {readings.min():.0f};"
             f" nominal {nominal:.0f} with {tol:.0f} mm allowed below",
             f"  readings below {nominal - tol:.0f} mm: {low.sum()} of 40"
             f" ({100 * low.mean():.0f} %)",
             f"  5 % fractile (mean - 1.645 s): {readings.mean() - 1.645 * readings.std(ddof=1):.1f} mm",
             "  the low readings are found and fixed (spacers added, bars",
             "  moved) before the hold point is released: cover is the",
             "  foundation's protection against sulphates and chlorides",
             "  (lab D), and it cannot be added after the pour"]
    emit("q_cover", lines)


def oc_curve() -> None:
    n, ac = 13, 1                                # sample size, acceptance number (teaching)
    lines = [f"attribute sampling of precast culvert units: sample {n},",
             f"  accept the lot if at most {ac} is defective",
             "  defective in lot %   probability of acceptance %"]
    for p in (1, 2, 5, 10, 15, 20, 30):
        pa = sum(math.comb(n, k) * (p / 100) ** k * (1 - p / 100) ** (n - k) for k in range(ac + 1))
        lines.append(f"  {p:18d}   {100 * pa:26.1f}")
    pts = []
    for p in range(0, 41):
        pa = sum(math.comb(n, k) * (p / 100) ** k * (1 - p / 100) ** (n - k) for k in range(ac + 1))
        pts.append((p, f"{pa:.4f}"))
    csv("ch29-oc.csv", "p,pa", pts)
    lines += ["  a lot with 10 % defective is still accepted about three",
              "  times in five: a small sample protects only against bad",
              "  lots, not mediocre ones - the plan is chosen from the",
              "  risk it must control (ISO 2859-1 tables, ch 10), and the",
              "  maker's own process control does the rest (ch 47)"]
    emit("q_oc", lines)


def reinstatement() -> None:
    years = [1, 2, 3]
    plots = {"corridor km 1-3": [22, 48, 71], "corridor km 3-5": [15, 31, 52],
             "tower bases": [30, 55, 78]}
    ref, target = 100.0, 70.0
    lines = ["reinstatement monitoring: vegetation cover as % of the undisturbed",
             f"  reference plot (teaching sign-off at {target:.0f} %)",
             "  area                year 1   year 2   year 3   signed off"]
    for name, v in plots.items():
        done = next((y for y, c in zip(years, v) if c >= target), None)
        lines.append(f"  {name:18s}  {v[0]:6.0f}   {v[1]:6.0f}   {v[2]:6.0f}   "
                     f"{('year ' + str(done)) if done else 'not yet'}")
    del ref
    lines += ["  the km 3-5 stretch lags: its topsoil was stockpiled",
              "  longest (lesson N) - reseeding there and one more year",
              "  of monitoring before the landowners sign off"]
    emit("q_reinstate", lines)


if __name__ == "__main__":
    towers()
    concrete_supply()
    aggregate_source()
    cover()
    oc_curve()
    reinstatement()
