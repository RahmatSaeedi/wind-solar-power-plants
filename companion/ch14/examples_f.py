"""Chapter 14, section F - land and social screening of the adjusted
layout W2b, the PV block, the site substation and the least-cost export
route: who uses the land (formal and customary), how much of each user's
land and access the project touches, the corridor parcels, and the early
consultation steps. All users are fictional; the screening only tells
whom to ask and what, the answers come from the people (chapter 54).

Run from the project root:   python -m companion.ch14.examples_f
Writes companion/ch14/expected/f_*.txt.
Synthetic site A-259; user list A-263 (to be verified in the field).
"""
from __future__ import annotations

import numpy as np

from companion.ch14 import examples_e as ee, lab_d, sources as src
from companion.ch14.common import emit
from plantp import siting as st

G = src.GRID

USERS = [   # (group, land, use, formal or customary, season)
    ("state (rangeland authority)", "state rangeland (rest)", "grazing permits", "formal", "all year"),
    ("owner of farm 1", "private farm 1", "irrigated fields", "formal", "May-Sep water"),
    ("owner of farm 2", "private farm 2", "rain-fed fields", "formal", "Oct-Jun"),
    ("herding families", "customary grazing (Apr-Oct)", "grazing, seasonal camp",
     "customary", "Apr-Oct"),
    ("village", "village lands", "houses, gardens, spring water", "formal and customary",
     "all year"),
    ("corridor farm owners (8 strips)", "corridor farmland", "fields", "formal", "all year"),
]


def exposure() -> None:
    xy = lab_d.layouts()["W2b plain, adjusted"]
    fp = lab_d.footprint(xy)
    x, y = G.mesh()
    pv = st.polygon_area(src.PV_BLOCK) / 1e4
    lines = ["who uses the land and how much the project touches (W2b, PV block,",
             "  site substation; screening survey, to verify, A-263):",
             "  user group                      land ha   project ha   share"]
    for grp, land, use, kind, season in USERS:
        if land.startswith("state"):
            used = np.ones(x.shape, bool)
            for poly in src.TENURE.values():
                used &= ~st.in_polygon(x, y, poly)
            area = (used & (x < 9000)).sum() * G.cell ** 2 / 1e4
            took = fp["total"] - sum(v for k, v in fp.items() if k in src.TENURE) + pv + 1.0
        else:
            area = st.polygon_area(src.TENURE[land]) / 1e4
            took = fp.get(land, 0.0)
        lines.append(f"  {grp:31s} {area:7,.0f}    {took:8.1f}    {100 * took / area:5.2f} %")
    lines += ["  areas are small shares, but shares hide what matters: the",
              "  herders' route to the spring, the camp's season, the farm's",
              "  water and the strips the export line crosses; a footprint",
              "  table starts the conversation, it does not end it"]
    emit("f_exposure", lines)


def corridor_parcels() -> None:
    c = ee.cost_raster()
    a, b = G.index(*src.SITE_SUB), G.index(*src.GRID_SUB)
    p, _ = st.least_cost_path(c, a, b, G.cell)
    p = np.asarray(p)
    xs = G.x0 + (p[:, 1] + 0.5) * G.cell
    ys = G.y0 + (p[:, 0] + 0.5) * G.cell
    edges = np.linspace(9000, 12400, 9)
    lines = ["the least-cost export route and the eight farm strips (x 9.0 to",
             "  12.4 km, each 425 m wide, y 2.3 to 3.9 km):",
             "  strip   route length inside   distance to the strip"]
    for k in range(8):
        poly = [(edges[k], 2300), (edges[k + 1], 2300), (edges[k + 1], 3900), (edges[k], 3900)]
        inside = st.in_polygon(xs, ys, poly)
        cx = 0.5 * (edges[k] + edges[k + 1])
        d = float(np.min(np.hypot(np.clip(xs - cx, -212, 212) - (xs - cx),
                                  np.clip(ys - 3100, -800, 800) - (ys - 3100))))
        lines.append(f"  {k + 1:4d}     {inside.sum() * G.cell:6.0f} m             {d:6.0f} m")
    lines += ["  the route hugs the edge of all eight strips: a least-cost path",
              "  runs along the border of a costly area; no tower stands in a",
              "  field, but the line's easement, access tracks and stringing",
              "  touch them; add a buffer to the cost raster, ask each owner",
              "  (rights of way, crops, damage) and move inside the corridor"]
    emit("f_corridor", lines)


def consultation() -> None:
    lines = ["early consultation plan (screening stage, before any commitment):",
             "  1 map the users with them: walk the land with herders, farmers",
             "    and village elders; mark routes, seasons, water and graves",
             "  2 share the screening maps in plain language and the local",
             "    languages; record concerns in a register with answers",
             "  3 verify tenure: formal records and customary rights; who",
             "    speaks for whom; women's and young people's views separately",
             "  4 screen for vulnerable groups and livelihood dependence; no",
             "    physical or economic displacement assumed acceptable",
             "  5 agree what the layout can still change (W2b moved turbines",
             "    away from the camp before anyone asked: say so, and ask what",
             "    else matters)",
             "  6 set up a grievance mechanism before site work starts",
             "  7 bring in specialists: social, heritage, ecology, water",
             "    (chapters 33, 54); record every step in the dossier"]
    emit("f_consult", lines)


if __name__ == "__main__":
    exposure()
    corridor_parcels()
    consultation()
