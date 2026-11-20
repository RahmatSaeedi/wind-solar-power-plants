"""Chapter 29, lesson I: the connection corridor and the substation site -
the 132 kV route of chapter 14 turned into civil quantities (towers,
angle points, access, crossings, farmland, reinstatement), the
substation platform against the wadi, and the register of surveys and
permits the route still needs.

Run from the project root:   python -m companion.ch29.examples_i
Writes companion/ch29/expected/i_*.txt. Teaching values (A-355).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import examples_e as e14
from companion.ch14 import sources as s14
from companion.ch29 import sources as src
from companion.ch29.common import emit
from plantp import siting as st

G = s14.GRID


def route() -> None:
    c = e14.cost_raster()
    a, b = G.index(*s14.SITE_SUB), G.index(*s14.GRID_SUB)
    path, _ = st.least_cost_path(c, a, b, G.cell)
    stats = e14.route_stats(path)
    p = np.array(path, float)
    xy = np.c_[G.x0 + (p[:, 1] + 0.5) * G.cell, G.y0 + (p[:, 0] + 0.5) * G.cell]
    km = stats["km"]
    span = 300.0
    towers = math.ceil(km * 1000 / span) + 1
    d = np.diff(xy, axis=0)
    ang = np.degrees(np.arctan2(d[:, 1], d[:, 0]))
    turns = np.abs((np.diff(ang) + 180) % 360 - 180)
    angle_points = int(np.sum(turns > 10))
    road_x = int(np.sum(np.diff(np.sign(xy[:, 1] - 600.0)) != 0))
    track_x = int(np.sum(np.diff(np.sign(xy[:, 0] - 7600.0)) != 0))
    access_km = towers * 0.25
    lines = ["the 132 kV route of ch 14 (least cost) in civil quantities",
             f"  length {km:.2f} km; towers at ~{span:.0f} m spans: {towers};"
             f" direction changes over 10 deg: {angle_points}",
             f"  crossings: wadi {stats['wadi']}, public road {road_x}, site track {track_x}",
             f"  farmland crossed {stats['farm_km']:.2f} km; homes within 500 m: {stats['near']}",
             f"  access tracks (~250 m a tower, teaching): {access_km:.1f} km",
             f"  ground disturbed: towers {towers * 100 / 1e4:.1f} ha, tracks {access_km * 4 / 10:.1f} ha"
             " (to reinstate)",
             "  angle points become heavier towers and the 50 m grid's",
             "  zigzag overstates them - the line designer straightens the",
             "  route; each crossing is a separate agreement and permit"]
    emit("i_route", lines)


def platform() -> None:
    z = s14.terrain()
    zs = float(G.interp(z, np.array([s14.SITE_SUB[0]]), np.array([s14.SITE_SUB[1]]))[0])
    xs = np.linspace(0, 13000, 261)
    yw = np.interp(xs, [s14.WADI[0][0], s14.WADI[1][0]], [s14.WADI[0][1], s14.WADI[1][1]])
    k = int(np.argmin(np.hypot(xs - s14.SITE_SUB[0], yw - s14.SITE_SUB[1])))
    t = np.linspace(0, 1, 47)
    px = xs[k] + t * (s14.SITE_SUB[0] - xs[k])
    py = yw[k] + t * (s14.SITE_SUB[1] - yw[k])
    prof = G.interp(z, px, py)
    j = int(np.argmin(prof[:10]))                       # the channel, within ~500 m of the line
    zw = float(prof[j])
    dist = float(np.hypot(px[j] - s14.SITE_SUB[0], py[j] - s14.SITE_SUB[1]))
    ridge = float(prof[j:].max())
    up = [x for x in np.arange(xs[k], 13001, 100.0) if src.channel_invert(x) > zs]
    lines = ["the site substation platform against the wadi",
             f"  ground at the substation {zs:.1f} m",
             f"  channel bed {zw:.1f} m, {dist / 1000:.1f} km away; ridge between {ridge:.1f} m",
             f"  height above the channel bed: {zs - zw:+.1f} m",
             f"  upstream of x = {up[0] / 1000:.1f} km the channel bed itself is higher",
             "  than the substation",
             "  the substation sits less than 2 m above the nearest bed,",
             "  and below the bed upstream: distance alone is no",
             "  protection - the ridge shields it here, but water leaving",
             "  the channel upstream can run down the plain; a flood study",
             "  (with the rain of lesson E) fixes the platform level",
             "  before design, and ponding in a 50-year day of rain",
             "  (80 mm) is checked locally"]
    emit("i_platform", lines)


def register() -> None:
    items = [("topographic survey of the route", "survey contractor", "before line design"),
             ("ground investigation at angle towers", "geotechnical", "before foundation design"),
             ("ecology walkover in the bird season", "ecologist", "before routing is fixed"),
             ("cultural heritage check (ruin buffer)", "heritage authority", "before access tracks"),
             ("drainage paths and flood levels near the route", "hydrologist", "before tower siting"),
             ("site-track crossing; access from the public road", "road authority", "before stringing"),
             ("land access for each parcel", "developer (U-085)", "before entry"),
             ("reinstatement standard and sign-off", "landowners", "after construction")]
    lines = ["what the route still needs before it is built (teaching register)"]
    for it, by, when in items:
        lines.append(f"  {it}")
        lines.append(f"      by {by}, {when}")
    lines += ["  the corridor register keeps each constraint with the",
              "  survey or permit that closes it; ch 33 (environment and",
              "  social) and ch 49 (construction) take it on"]
    emit("i_register", lines)


if __name__ == "__main__":
    route()
    platform()
    register()
