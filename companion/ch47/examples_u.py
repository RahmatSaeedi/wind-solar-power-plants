"""Chapter 47, round u: container plinths levelled, bolt holes of
substation supports, rebar certificates by bundle, the erection schedule
against the sections' release, the grout that corrects a tilted cage,
the fabricator's ovality capability and the NCR backlog by Little's law.

Run from the project root:   python -m companion.ch47.examples_u
Writes companion/ch47/expected/u_*.txt and diagrams/data/ch47-*.csv.
Teaching values (A-490 to A-497); no design approval implied.
"""
from __future__ import annotations

import numpy as np

from companion.ch47 import examples_c as ec
from companion.ch47.common import csv, emit
from plantp import quality as q


# ------------------------------------------------ 1. container plinths
PLINTHS = {   # container: levels at 6 support points, mm from the datum
    "C1": [0, 2, 1, 3, 2, 1], "C2": [1, 0, 2, 1, 3, 2], "C3": [0, 1, 1, 2, 1, 0],
    "C4": [2, 3, 1, 2, 2, 3], "C5": [0, 4, 9, 14, 18, 12], "C6": [1, 1, 2, 0, 1, 2],
    "C7": [2, 0, 1, 1, 2, 1], "C8": [0, 2, 3, 2, 1, 2],
}


def plinths(limit: float = 6.0) -> dict:
    lines = [f"battery container plinths: level at six support points (teaching",
             f"  limit {limit:.0f} mm between the highest and lowest support)",
             "  container   range mm   verdict"]
    bad = []
    for c, z in PLINTHS.items():
        r = max(z) - min(z)
        if r > limit:
            bad.append(c)
        lines.append(f"  {c:9s}   {r:8d}   {'ok' if r <= limit else 'SHIM PLAN'}")
    lines += [f"  out: {', '.join(bad)} - an 18 mm fall along one side twists the",
              "  container frame: doors bind, racks lean and the busbar joints",
              "  of ch 45 see a load they were not built for; the shim plan",
              "  is the container maker's, with the plinth's survey on file"]
    emit("u_plinths", lines)
    return dict(bad=bad)


# ------------------------------------------------ 2. substation support holes
HOLES = {   # support: (dx, dy) of each of 4 holes from the drawing, mm
    "S-CB1": [(0.5, -0.3), (0.2, 0.4), (-0.4, 0.1), (0.3, -0.2)],
    "S-CB2": [(1.1, 0.2), (0.9, 0.5), (1.2, -0.1), (1.0, 0.3)],
    "S-DS1": [(0.3, 0.2), (-0.2, -0.5), (0.1, 0.3), (2.8, 0.4)],
    "S-CT1": [(-0.4, 0.2), (0.3, 0.1), (0.2, -0.3), (-0.1, 0.4)],
}


def holes(tol: float = 2.0) -> dict:
    lines = ["bolt holes of substation supports against the drawing",
             f"  (teaching tolerance {tol} mm)",
             "  support   worst hole mm   pattern shift mm   verdict"]
    out = {}
    for s, hs in HOLES.items():
        d = [np.hypot(x, y) for x, y in hs]
        sx = np.mean([x for x, _ in hs])
        sy = np.mean([y for _, y in hs])
        rel = max(np.hypot(x - sx, y - sy) for x, y in hs)
        v = "ok" if max(d) <= tol else ("one hole off" if rel > tol else "shifted")
        out[s] = (max(d), float(np.hypot(sx, sy)), v)
        lines.append(f"  {s:8s}  {max(d):13.1f}   {np.hypot(sx, sy):16.1f}   {v}")
    lines += ["  S-CB2 is shifted as a whole by about 1 mm - all four holes",
              "  move together and the breaker still fits; S-DS1 has one hole",
              "  2.8 mm out of a pattern that is otherwise right - the",
              "  disconnector's base will not drop on; the hole is re-drilled",
              "  and re-galvanized locally before shipping, by the fabricator"]
    emit("u_holes", lines)
    return out


# ------------------------------------------------ 3. rebar certificates
BUNDLES = [   # tag, yield MPa, tensile MPa, elongation % (teaching rule below)
    ("RB-01", 520, 640, 14.0), ("RB-02", 515, 625, 13.5), ("RB-03", 540, 560, 12.0),
    ("RB-04", 510, 630, 9.5), ("RB-05", 525, 645, 13.0), ("RB-06", 650, 760, 11.0),
]


def rebar(fy_min: float = 500, fy_max: float = 625, ratio_min: float = 1.08,
          elong_min: float = 10.0) -> dict:
    lines = [f"rebar certificates by bundle (teaching rule: yield {fy_min:.0f}-"
             f"{fy_max:.0f} MPa,", f"  tensile/yield >= {ratio_min}, elongation "
             f">= {elong_min:.0f} %)",
             "  bundle   yield   ratio   elong %   finding"]
    bad = {}
    for tag, fy, fu, el in BUNDLES:
        why = []
        if not fy_min <= fy <= fy_max:
            why.append("yield out of range")
        if fu / fy < ratio_min:
            why.append("ratio low")
        if el < elong_min:
            why.append("elongation low")
        if why:
            bad[tag] = why
        lines.append(f"  {tag}    {fy:5d}   {fu / fy:5.2f}   {el:7.1f}   "
                     f"{'; '.join(why) or 'ok'}")
    lines += [f"  {len(bad)} bundles held: a low tensile-to-yield ratio or",
              "  elongation means a bar that cannot stretch before it breaks",
              "  (the foundation relies on it to warn); a yield far above",
              "  the range is not a bonus - it moves where the foundation",
              "  yields first - the designer decides, by bundle tag"]
    emit("u_rebar", lines)
    return bad


# ------------------------------------------------ 4. erection against release
def erection(days_per_turbine: float = 3.0, standby_ku: float = 18.0) -> dict:
    """Release days of each tower's last section (synthetic, from the
    dossier lesson) against a crane that erects one turbine every 3 days."""
    ready = [0, 0, 2, 4, 19, 6, 8, 12, 14, 31, 18, 20]      # day the tower may ship
    t, idle, rows = 0.0, 0.0, []
    for k, r in enumerate(ready):
        start = max(t, r)
        idle += start - t
        rows.append((k + 1, r, start, start + days_per_turbine))
        t = start + days_per_turbine
    csv("ch47-erection.csv", "turbine,ready,start,end", rows)
    waits = [(k, r, st) for k, r, st, _ in rows if st == r and r > 0 and
             (k == 1 or rows[k - 2][3] < r)]
    lines = ["crane erection of 12 turbines against the release of their towers",
             f"  (one turbine every {days_per_turbine:.0f} days, crane standby "
             f"{standby_ku:.0f} k u a day; teaching)",
             f"  finished on day {t:.0f}; crane idle {idle:.0f} days "
             f"({idle * standby_ku:.0f} k u)",
             f"  with every tower released on time: day "
             f"{len(ready) * days_per_turbine:.0f}, idle 0",
             "  the crane waited for: " + ", ".join(
                 f"T{k:02d} (ready day {r}, crane free day {rows[k - 2][3]:.0f})"
                 for k, r, _ in waits),
             "  T05's section 1 carried the eight holds of lab D; each",
             "  dossier gap of lesson C becomes crane days here (ch 31)"]
    emit("u_erection", lines)
    return dict(end=t, idle=idle, rows=rows)


# ------------------------------------------------ 5. grout under a tilted cage
def grout(ring_d: float = 4.30, nominal: float = 60.0, lo: float = 50.0,
          hi: float = 80.0) -> dict:
    an = ec.anchor()
    dz = an["t1"] * ring_d                      # mm across the ring
    thin, thick = nominal - dz / 2, nominal + dz / 2
    lines = [f"grout that levels the tower on the T05 cage (tilt {an['t1']:.2f} mm/m)",
             f"  across the {ring_d} m ring the cage falls {dz:.1f} mm",
             f"  grout of nominal {nominal:.0f} mm becomes {thin:.1f} to {thick:.1f} mm "
             f"(teaching range {lo:.0f}-{hi:.0f})",
             "  inside the range: the grout can take the tilt, and the tower",
             "  stands plumb - provided the grout's own records (cubes, cure,",
             "  thickness at 8 points) are kept; the decision is the turbine",
             "  maker's, as lesson C said (ch 30 grout)"]
    emit("u_grout", lines)
    return dict(dz=dz, thin=thin, thick=thick)


# ------------------------------------------------ 6. ovality capability
def ovality(seed: int = 4703, n: int = 40, limit: float = 0.7) -> dict:
    rng = np.random.default_rng(seed)
    ov = list(np.round(np.abs(rng.normal(0.45, 0.10, n)), 3))
    m, s, _, cpk = q.cp_cpk(ov, None, limit)
    ppm = q.ppm_out(m, s, None, limit)
    over = sum(1 for x in ov if x > limit)
    edges = [0.20 + 0.05 * k for k in range(12)]
    counts = np.histogram(ov, bins=edges)[0]
    csv("ch47-ovality.csv", "x,n", [(round((a + b) / 2, 3), int(c))
                                    for a, b, c in zip(edges, edges[1:], counts)])
    lines = [f"ovality of the fabricator's last {n} cans, % of D (limit {limit} %)",
             f"  mean {m:.3f}, sd {s:.3f}; Cpk {cpk:.2f}; expected over the limit "
             f"{ppm / 1e4:.1f} %; found {over}",
             f"  a Cpk of {cpk:.2f} means about one can in {1e6 / ppm:.0f} needs "
             "re-rolling;",
             "  a small share - but a Cpk under 1.33 leaves no room for a",
             "  drift in the rolls, and dimensions are the fabricator's first",
             "  NCR cause (round s): the audit asks for the capability, and",
             "  the buyer's plan keeps ovality on every can, not on a sample"]
    emit("u_ovality", lines)
    return dict(cpk=cpk, ppm=ppm, over=over)


# ------------------------------------------------ 7. NCR backlog
def backlog(target_days: float = 21.0) -> dict:
    from companion.ch47 import sources as src
    first = min(n["raised"] for n in src.NCRS)
    span = (src.TODAY - first).days
    lam = len(src.NCRS) / span                       # NCRs a day
    open_now = sum(not n["closed"] for n in src.NCRS)
    w = open_now / lam
    open_target = lam * target_days
    lines = ["NCR backlog by Little's law: open = rate x time to decide",
             f"  the register: {len(src.NCRS)} NCRs in {span} days "
             f"({lam * 7:.2f} a week), {open_now} open",
             f"  so an NCR waits about {w:.0f} days for its decision on average",
             f"  deciding in {target_days:.0f} days instead would leave about "
             f"{open_target:.1f} open",
             "  the open list is not shortened by working harder on the old",
             "  NCRs once; only a shorter time to decide keeps it short - an",
             "  owner and a date on each (lesson C)"]
    emit("u_backlog", lines)
    return dict(now=open_now, target=open_target, w=w)


if __name__ == "__main__":
    plinths()
    holes()
    rebar()
    erection()
    grout()
    ovality()
    backlog()
