"""Chapter 49, lesson B (workface execution): installation records read
against their tolerances - post positions and depths, clamp torques and
the tools that made them, as-laid cable lengths, MV termination records,
earthing continuity and the preservation of stored equipment.

Run from the project root:   python -m companion.ch49.examples_b
Writes companion/ch49/expected/b_*.txt.
"""
from __future__ import annotations

import math
from datetime import date

from companion.ch49 import sources as src
from companion.ch49.common import emit
from plantp import construction as con


def piles() -> dict:
    pos = [(p, math.hypot(dx, dy)) for p, (dx, dy, _, _) in src.PILES.items()]
    off = [(p, e) for p, e in pos if e > src.PILE_TOL_MM]
    short = [(p, z, zd) for p, (_, _, z, zd) in src.PILES.items() if z < zd]
    lines = [f"post records of a sample of {len(src.PILES)} in block PVF1-3",
             f"  (tolerance {src.PILE_TOL_MM:.0f} mm radial, teaching)"]
    lines += [f"  {p}: off by {e:.0f} mm" for p, e in off]
    lines += [f"  {p}: embedded {z:.2f} m of {zd:.2f} m - short" for p, z, zd in short]
    lines += ["  an off-position post is checked against the table's slotted",
              "  holes before the table goes on; a short post is the",
              "  designer's decision (a load test or a second post), never",
              "  the crew's - both are non-conformities with a disposition"]
    emit("b_piles", lines)
    return dict(off=off, short=short)


def torque(day: date = date(2027, 8, 25)) -> dict:
    nom, tol = src.TORQUE_SPEC
    missing = [j for j, v, *_ in src.TORQUE if v is None]
    outside = [(j, v) for j, v, *_ in src.TORQUE
               if v is not None and abs(v - nom) > tol * nom]
    stale = sorted({t for _, _, t, due in src.TORQUE if due < day})
    suspect = [j for j, _, t, _ in src.TORQUE if t in stale]
    lines = [f"clamp torque records of {day} against the maker's value",
             f"  (placeholder {nom:.0f} Nm +/- {tol:.0%})"]
    lines += [f"  {j}: no value recorded" for j in missing]
    lines += [f"  {j}: {v:.1f} Nm outside the band" for j, v in outside]
    lines += [f"  tool {t} was past its calibration date; its records are suspect:"
              for t in stale]
    lines += [f"    {', '.join(suspect)}"]
    lines += ["  a missing value is an untightened clamp until shown",
              "  otherwise; a tool past its calibration puts every joint it",
              "  made in doubt - the record names the tool for that reason"]
    emit("b_torque", lines)
    return dict(missing=missing, outside=outside, suspect=suspect)


def as_laid(limit: float = 0.05) -> list:
    rows = [(c, d, a, (a - d) / d) for c, (d, a) in src.AS_LAID.items()]
    bad = [r for r in rows if abs(r[3]) > limit]
    lines = [f"combiner-to-station DC cables: as laid against design (flag over {limit:.0%})",
             "  cable      design m  as laid m  change"]
    lines += [f"  {c:9s}  {d:8d}  {a:9d}  {x:+6.1%}" for c, d, a, x in rows]
    lines += [f"  {', '.join(r[0] for r in bad)} took a detour round the station base:",
              "  its drop and loss are recomputed (ch 24, ch 46 as-laid) and",
              "  the as-built drawing shows the route the cable really took"]
    emit("b_aslaid", lines)
    return bad


def terminations() -> list:
    bad = []
    for end, who, lot, screen, photo in src.TERMS:
        gaps = [k for k, v in (("kit lot", lot), ("screen earth", screen),
                               ("photo", photo)) if not v]
        if gaps:
            bad.append((end, gaps))
    lines = ["MV termination records: each end names the jointer, the kit lot,",
             "  the screen earth and a photo before it is closed"]
    lines += [f"  {e}: missing {', '.join(g)}" for e, g in bad]
    lines += [f"  {len(bad)} of {len(src.TERMS)} ends are not closed: a kit lot links a",
              "  termination to a recall (ch 46), a screen earth not",
              "  recorded is one not checked, and a photo is the only view",
              "  of the inside once the end is sealed"]
    emit("b_terms", lines)
    return bad


def earthing() -> dict:
    high = [(b, r) for b, r in src.EARTH.items() if r is not None and r > src.EARTH_LIMIT]
    none = [b for b, r in src.EARTH.items() if r is None]
    lines = [f"earthing continuity, bond to the earth grid (teaching limit "
             f"{src.EARTH_LIMIT} ohm)"]
    lines += [f"  {b}: {r:.2f} ohm - over the limit" for b, r in high]
    lines += [f"  {b}: not measured" for b in none]
    lines += ["  a high bond is a loose or painted joint; an unmeasured one",
              "  is not a bond yet - both are reworked and measured again",
              "  before the area is handed over (ch 26 earthing)"]
    emit("b_earth", lines)
    return dict(high=high, none=none)


def preservation() -> dict:
    out = {}
    for item, (arr, checks, heater) in src.STORE.items():
        days = [arr] + checks + [src.STORE_DAY]
        gaps = [b - a for a, b in zip(days, days[1:])]
        out[item] = max(gaps)
    late = {k: g for k, g in out.items() if g > src.STORE_EVERY}
    lines = ["stored equipment: longest gap between preservation checks",
             f"  (every {src.STORE_EVERY} days, to day {src.STORE_DAY})"]
    lines += [f"  {k:20s} {g:3d} days" + ("  LATE" if k in late else "")
              for k, g in out.items()]
    lines += ["  a skid stored with its heater on is checked weekly - the",
              "  heater, the desiccant, the covers; one missed fortnight",
              "  is the fortnight a condensation fault starts (ch 31, ch 48",
              "  dew point); the RMU spares had no regular checks at all"]
    emit("b_store", lines)
    return late


def credit() -> dict:
    done = {"received and inspected": 1.0, "mounted": 0.80, "clamps torqued": 0.60,
            "serial captured": 0.55, "inspected": 0.30}
    p = con.rules_of_credit(src.CREDIT, done)
    lines = ["module installation progress of block PVF1-3 by rules of credit",
             "  step                     weight  done"]
    lines += [f"  {s:24s} {w:6.0%}  {done[s]:4.0%}" for s, w in src.CREDIT.items()]
    lines += [f"  earned progress {p:.1%}, against the {done['mounted']:.0%} a "
              "'modules mounted' count reports",
              "  the mounted count looks good on a chart; the steps after it",
              "  (torque, serials, inspection) are where turnover waits"]
    emit("b_credit", lines)
    return dict(progress=p, mounted=done["mounted"])


if __name__ == "__main__":
    piles()
    torque()
    as_laid()
    terminations()
    earthing()
    preservation()
    credit()
