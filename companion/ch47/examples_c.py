"""Chapter 47, lesson C: inspection and field integration - the
fabricator's nonconformance register by age, the tower section dossier
against its list, the anchor cage's tilt before and after the pour and
what it means at the hub, a PV post survey split into systematic and
random offsets, and who inspects what in the factory and on site.

Run from the project root:   python -m companion.ch47.examples_c
Writes companion/ch47/expected/c_*.txt and diagrams/data/ch47-*.csv.
Teaching values (A-495 to A-497); no design approval implied.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch47 import sources as src
from companion.ch47.common import csv, emit
from plantp import civilmfg as cv


# ------------------------------------------------ 1. NCR register
def ncrs() -> dict:
    bands = cv.ageing(src.NCRS, src.TODAY)
    old = [n for n in src.NCRS if not n["closed"]
           and (src.TODAY - n["raised"]).days > 90]
    lines = [f"fabricator's NCR register on {src.TODAY}: {len(src.NCRS)} raised, "
             f"{sum(not n['closed'] for n in src.NCRS)} open",
             "  open by age: " + ", ".join(f"{k} days {v}" for k, v in bands.items())]
    for n in old:
        lines.append(f"  {n['id']} open {(src.TODAY - n['raised']).days} days: "
                     f"{n['subject']}")
    lines += ["  an NCR left open for months is a decision nobody took: the",
              "  door-frame MT and the flange flatness block the release of",
              "  sections 1 and 2 - the register is reviewed weekly with an",
              "  owner and a date for each open item (ch 40)"]
    emit("c_ncr", lines)
    return dict(bands=bands, old=[n["id"] for n in old])


# ------------------------------------------------ 2. dossier of section 1
LINKS = {"welder qualifications on the weld dates": "b_welders (3 joints)",
         "NDT reports to the plan": "b_ndt (attachments 4 %)",
         "NCR register with closures": "c_ncr (5 open)",
         "release note signed by the buyer's inspector": "waits for the rest"}


def dossier() -> dict:
    miss = [d for d, ok in src.DOSSIER.items() if not ok]
    lines = [f"tower section 1 dossier: {len(src.DOSSIER) - len(miss)} of "
             f"{len(src.DOSSIER)} documents complete",
             "  missing or incomplete, and why:"]
    lines += [f"    {d}: {LINKS.get(d, '')}" for d in miss]
    lines += ["  the release note is the last line for a reason: it may be",
              "  signed only when every line above it is complete; a section",
              "  shipped on a signed note with open lines carries its holes",
              "  to site, where they cost a crane day each (ch 31)"]
    emit("c_dossier", lines)
    return dict(miss=miss)


# ------------------------------------------------ 3. anchor cage tilt
ANGLES = [k * 45.0 for k in range(8)]
BEFORE = [0.0, 0.5, -0.4, 0.8, 0.2, -0.6, 0.3, -0.1]       # mm, top flange level
AFTER = [0.4, 1.9, 2.8, 3.6, 2.2, 0.5, -0.6, -0.2]


def tilt(levels, radius_m: float = 2.15) -> tuple[float, float]:
    """Best plane through readings on a circle: z = a + b cos + c sin;
    tilt = sqrt(b^2 + c^2) / R in mm per m, and its direction (deg)."""
    th = np.radians(ANGLES)
    a = np.column_stack([np.ones(8), np.cos(th), np.sin(th)])
    coef, *_ = np.linalg.lstsq(a, np.array(levels), rcond=None)
    b, c = coef[1], coef[2]
    return math.hypot(b, c) / radius_m, math.degrees(math.atan2(c, b)) % 360


def anchor(limit: float = 1.0, height_m: float = 100.0) -> dict:
    t0, d0 = tilt(BEFORE)
    t1, d1 = tilt(AFTER)
    csv("ch47-cage.csv", "deg,before,after", list(zip(ANGLES, BEFORE, AFTER)))
    lines = ["anchor-cage top flange levelled at 8 points before and after the pour",
             f"  (teaching limit {limit:.1f} mm/m tilt)",
             f"  before: tilt {t0:.2f} mm/m;  after: tilt {t1:.2f} mm/m toward "
             f"{d1:.0f} deg",
             f"  at the hub ({height_m:.0f} m up) the after-pour tilt is "
             f"{t1 * height_m:.0f} mm of lean",
             f"  inside the teaching limit, but {t1 / t0:.0f} times the tilt before "
             "the pour:",
             "  the cage moved during the pour (concrete pushing one side);",
             "  the level is fixed with the grout's thickness before the",
             "  tower goes up, a decision for the turbine maker and the",
             "  foundation engineer - the before-and-after survey is the",
             "  only proof of when it moved"]
    emit("c_anchor", lines)
    return dict(t0=t0, t1=t1, d1=d1, lean=t1 * height_m)


# ------------------------------------------------ 4. PV posts as built
def posts(seed: int = 4701, rows: int = 10, per_row: int = 12, sd: float = 8.0,
          shift_row: int = 6, shift: float = 30.0, tol: float = 25.0) -> dict:
    rng = np.random.default_rng(seed)
    off = rng.normal(0, sd, (rows, per_row))
    off[shift_row] += shift
    out_n = int((np.abs(off) > tol).sum())
    med = np.median(off, axis=1)
    sys_rows = [r + 1 for r in range(rows) if abs(med[r]) > tol / 2]
    resid = off - med[:, None]
    in_row = int((np.abs(off[shift_row]) > tol).sum())
    lines = [f"PV posts of block PVF1-1 surveyed: {rows} rows x {per_row} posts, "
             f"offset from design (mm)",
             f"  tolerance +/-{tol:.0f} mm; posts outside: {out_n} of {rows * per_row}",
             "  row median offsets: " + ", ".join(f"{m:+.0f}" for m in med),
             f"  rows shifted as a whole: {', '.join(map(str, sys_rows))}; "
             f"spread inside rows sd {resid.std(ddof=1):.1f} mm",
             f"  {in_row} of the {out_n} posts outside sit in row {shift_row + 1}, "
             "shifted as a",
             "  whole - the string line was set from a wrong survey mark, not",
             "  a careless crew; the fix is the mark and the row (the table",
             "  rails can take the shift or the row is re-driven), recorded",
             "  in the as-built survey"]
    emit("c_posts", lines)
    return dict(out=out_n, sys_rows=sys_rows, sd=float(resid.std(ddof=1)))


# ------------------------------------------------ 5. factory and site
ITEMS = [   # item, where made, who checks, independent check
    ("tower sections", "factory", "fabricator QC, buyer's inspector",
     "third-party NDT sample"),
    ("tower erection and bolting", "site", "erector, turbine maker",
     "torque records audit"),
    ("anchor cage", "factory + site", "maker; foundation contractor",
     "survey before and after pour"),
    ("foundation concrete", "site (cast in place)", "contractor, supplier",
     "independent cubes"),
    ("PV tables and posts", "factory + site", "maker; installer",
     "post survey, pull tests"),
    ("tracker rows", "factory + site", "maker; installer", "row survey, drive EOL"),
    ("substation steel", "factory", "fabricator", "zinc and bolt audit"),
]


def factory_site() -> int:
    lines = ["factory or site: where each product is made and who checks it",
             "  item                         where",
             "    checked by; independent check"]
    for it, w, who, ind in ITEMS:
        lines.append(f"  {it:28s} {w}")
        lines.append(f"    {who}; {ind}")
    lines += ["  a prefabricated item is accepted at the factory and checked",
              "  again only for transport damage; a cast-in-place item is",
              "  accepted where it is made - its records start on site, and",
              "  the independent check is the buyer's protection against",
              "  both"]
    emit("c_factory", lines)
    return len(ITEMS)


if __name__ == "__main__":
    ncrs()
    dossier()
    anchor()
    posts()
    factory_site()
