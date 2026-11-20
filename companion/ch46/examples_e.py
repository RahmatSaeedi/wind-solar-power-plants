"""Chapter 46, lesson A (deeper): the field in the insulation and why the
thinnest point matters, insulation thickness read from drum-end slices,
routine test reports checked as records, a compound-lot notice traced to
drums, crimp joints ageing in a qualification report, and contact spots
(Holm) behind a lug's resistance.

Run from the project root:   python -m companion.ch46.examples_e
Writes companion/ch46/expected/e_*.txt and diagrams/data/ch46-field.csv.
Teaching values (A-483, A-484); no test voltages, no process values.
"""
from __future__ import annotations

import math

from companion.ch46.common import csv, emit
from plantp import cablemfg as km

U0 = 33.0 / math.sqrt(3)                 # kV, phase to earth
SCREEN, INS = 0.8, 8.0                   # mm, conductor screen, insulation
COMPACT = 1.054                          # compacted conductor: d / sqrt(4A/pi)


def radii(mm2: int, ins: float = INS) -> tuple[float, float]:
    dc = COMPACT * math.sqrt(4 * mm2 / math.pi)
    rc = dc / 2 + SCREEN
    return rc, rc + ins


# ------------------------------------------------ 1. field in the insulation
def field() -> dict:
    lines = [f"field in the XLPE of the 33 kV cores, U0 = {U0:.2f} kV, insulation "
             f"{INS:.1f} mm",
             "  size mm2   rc mm   ri mm   E at rc kV/mm   E at ri kV/mm   ratio"]
    out = {}
    for a in (240, 400, 630):
        rc, ri = radii(a)
        e1 = km.field_kv_mm(U0, rc, rc, ri)
        e2 = km.field_kv_mm(U0, ri, rc, ri)
        out[a] = (rc, ri, e1, e2)
        lines.append(f"  {a:8d}   {rc:5.1f}   {ri:5.1f}   {e1:13.2f}   {e2:13.2f}   "
                     f"{e1 / e2:5.2f}")
    rows = []
    for k in range(21):
        x = INS * k / 20
        rows.append([round(x, 2)] + [round(km.field_kv_mm(U0, out[a][0] + x,
                                                           out[a][0], out[a][1]), 3)
                                     for a in (240, 400, 630)])
    csv("ch46-field.csv", "x,e240,e400,e630", rows)
    rc, ri = radii(240)
    thin = 7.1
    e_thin = km.field_kv_mm(U0, rc, rc, rc + thin)
    e_opt = math.e * U0 / ri
    lines += [f"  the field is highest at the conductor screen and falls as 1/r;",
              f"  a thin spot of {thin} mm on the 240 mm2 core raises the peak to "
              f"{e_thin:.2f} kV/mm",
              f"  (+{e_thin / out[240][2] - 1:.0%}); with the same outer radius the "
              f"lowest peak, {e_opt:.2f} kV/mm,",
              f"  would need rc = ri / e = {ri / math.e:.1f} mm; the 33 kV cores sit "
              "at ri / rc",
              "  1.5-1.8, not e = 2.72: their conductor is set by the current",
              "  and their insulation by a minimum thickness, so the e-rule",
              "  matters for HV cables, where the insulation is thick"]
    emit("e_field", lines)
    return dict(out=out, e_thin=e_thin)


# ------------------------------------------------ 2. thickness from drum-end slices
SLICES = {   # (drum, end): six readings around the core, mm
    ("D401", "in"): (8.31, 8.22, 8.18, 8.26, 8.35, 8.29),
    ("D401", "out"): (8.28, 8.20, 8.24, 8.30, 8.33, 8.27),
    ("D402", "in"): (8.85, 8.70, 8.10, 6.95, 7.45, 8.40),
    ("D402", "out"): (8.25, 8.19, 8.23, 8.31, 8.28, 8.22),
    ("D403", "in"): (8.20, 8.15, 8.18, 8.24, 8.27, 8.21),
    ("D403", "out"): (8.22, 8.18, 8.16, 8.25, 8.30, 8.24),
    ("D405", "in"): (8.10, 8.05, 8.12, 8.08, 8.15, 8.11),
    ("D405", "out"): (7.95, 7.90, 7.92, 7.96, 7.94, 7.91),
}
NOMINAL = 8.0
MIN_POINT = 0.9 * NOMINAL - 0.1          # teaching rule for the thinnest point


def thickness() -> dict:
    lines = [f"insulation thickness from drum-end slices, nominal {NOMINAL} mm",
             f"  (teaching rules: mean >= nominal; thinnest point >= {MIN_POINT:.1f} mm)",
             "  drum  end   mean   min    eccentricity   verdict"]
    bad = {}
    for (d, end), v in SLICES.items():
        m, lo, hi = sum(v) / len(v), min(v), max(v)
        ecc = (hi - lo) / hi
        why = []
        if m < NOMINAL:
            why.append("mean")
        if lo < MIN_POINT:
            why.append("thin point")
        if why:
            bad[(d, end)] = why
        lines.append(f"  {d}  {end:3s}  {m:5.2f}  {lo:5.2f}   {ecc:11.1%}   "
                     f"{'ok' if not why else 'FAIL ' + ', '.join(why)}")
    lines += ["  D402's inner end passes on its mean but has a thin point: the",
              "  core was off centre there, and the field peaks at the thin",
              "  side (e_field); D405's outer end is concentric but thin all",
              "  round - two different faults, both found only because each",
              "  drum's two ends are measured and kept in its record"]
    emit("e_thickness", lines)
    return dict(bad=bad)


# ------------------------------------------------ 3. routine test reports
REPORTS = [   # drum, made, tested, length on the label, length in the report,
              # conductor result, PD result, voltage test, calibration due
    ("D401", "2026-03-02", "2026-03-04", 1000, 1000, "pass", "pass", "pass", "2026-09-30"),
    ("D402", "2026-03-02", "2026-03-04", 1000, 1000, "pass", "pass", "pass", "2026-09-30"),
    ("D403", "2026-03-03", "2026-03-05", 1000, 1000, "fail", "pass", "pass", "2026-09-30"),
    ("D404", "2026-03-05", "2026-03-04", 1000, 1000, "fail", "pass", "pass", "2026-09-30"),
    ("D405", "2026-03-05", "2026-03-07", 1000, 985, "pass", "pass", "pass", "2026-09-30"),
    ("D406", "2026-03-06", "2026-03-09", 1000, 1000, "fail", "", "pass", "2026-09-30"),
    ("D407", "2026-03-09", "2026-03-11", 1000, 1000, "pass", "pass", "pass", "2026-03-10"),
]


def reports() -> list:
    probs = []
    for d, made, tested, lab, rep, rc, pd, vt, cal in REPORTS:
        if tested < made:
            probs.append((d, "tested before it was made (date slip or wrong drum)"))
        if cal < tested:
            probs.append((d, "instrument calibration expired on the test date"))
        if lab != rep:
            probs.append((d, f"report length {rep} m, label {lab} m"))
        for name, v in (("conductor", rc), ("PD", pd), ("voltage", vt)):
            if v == "":
                probs.append((d, f"{name} result missing"))
            elif v == "fail":
                probs.append((d, f"{name} result FAIL - the drum may not ship"))
    lines = [f"routine test reports of {len(REPORTS)} drums read as records (results "
             "only)", "  drum   finding"]
    lines += [f"  {d}   {p}" for d, p in probs]
    lines += [f"  {len(probs)} findings on {len({d for d, _ in probs})} drums: three "
              "drums were shipped",
              "  although the maker's own report failed them on conductor",
              "  resistance (the buyer's corrected check of lesson A found the",
              "  same three), a test dated before the drum was",
              "  made, a short length the report admits but the label hides,",
              "  a missing PD result and a test on an expired instrument -",
              "  a report is accepted line by line, not by its front page"]
    emit("e_reports", lines)
    return probs


# ------------------------------------------------ 4. compound lot notice
RUNS = {   # extrusion run: (insulation compound lots used, drums made)
    "R3": (["C-16"], ["D401", "D402", "D403"]),
    "R4": (["C-16", "C-17"], ["D404", "D405"]),
    "R5": (["C-17"], ["D406", "D407"]),
    "R6": (["C-18"], ["D408", "D409"]),
}
ALLOCATED = {"D401": "W002", "D402": "W006", "D403": "W010", "D404": "W013",
             "D405": "W017", "D406": "W020"}


def compound(lot: str = "C-17") -> dict:
    drums = [d for r, (lots, ds) in RUNS.items() if lot in lots for d in ds]
    mixed = [r for r, (lots, _) in RUNS.items() if lot in lots and len(lots) > 1]
    cables = [ALLOCATED[d] for d in drums if d in ALLOCATED]
    stock = [d for d in drums if d not in ALLOCATED]
    lines = [f"compound maker's notice on insulation lot {lot}: which drums, which "
             "cables?",
             f"  runs that used it: {', '.join(r for r in RUNS if lot in RUNS[r][0])}"
             f" (mixed lots in {', '.join(mixed)})",
             f"  drums: {', '.join(drums)}",
             f"  cables cut from them: {', '.join(cables)}; in stock: "
             f"{', '.join(stock)}",
             "  run R4 changed lots part-way and the change point was not",
             "  recorded, so both of its drums count - one written changeover",
             "  position could have taken a drum off the list; D404 and D406",
             "  were already rejected on resistance, so the notice adds W017",
             "  and the stock drum: their PD reports are re-read and the",
             "  maker's lot analysis decides; the drum stays on hold until then"]
    emit("e_compound", lines)
    return dict(drums=drums, cables=cables, stock=stock)


# ------------------------------------------------ 5. crimp joints ageing
AGEING = {   # lug design: resistance ratio (joint / equal conductor) after cycles
    "L-A": [(0, 0.62), (250, 0.63), (500, 0.63), (1000, 0.64)],
    "L-B": [(0, 0.65), (250, 0.71), (500, 0.80), (1000, 0.95)],
}


def ageing(limit: float = 1.0) -> dict:
    lines = ["crimp joints in a heat-cycling qualification report (teaching):",
             "  resistance of the joint / resistance of an equal conductor",
             "  lug    0 cycles   1000 cycles   rise per 1000   reaches 1.0 at"]
    out = {}
    for lug, pts in AGEING.items():
        x = [a for a, _ in pts]
        y = [b for _, b in pts]
        b, se = km.trend(x, y)
        at = (limit - y[0]) / b if b > 0 else float("inf")
        out[lug] = (b * 1000, at)
        lines.append(f"  {lug}   {y[0]:8.2f}   {y[-1]:11.2f}   {b * 1000:13.2f}   "
                     f"{at:10.0f} cycles")
    lines += ["  both joints start below the conductor, so both pass a test on",
              "  day one; L-B's joint loosens with each cycle - the stability",
              "  of the ratio is the evidence, and only a cycling test shows it",
              "  (the qualification report is asked for by lug and tool, ch 39)"]
    emit("e_ageing", lines)
    return out


# ------------------------------------------------ 6. contact spots (Holm)
def holm() -> dict:
    al, cu = (2.8e-8, 0.4e9), (1.72e-8, 0.8e9)       # rho ohm m, hardness Pa
    lines = ["constriction resistance of a bolted joint (Holm), micro-ohm",
             "  force kN   Al 1 spot   Al 10 spots   Cu 1 spot   Cu 10 spots"]
    out = {}
    for f in (5, 10, 20, 40):
        r = [km.holm_r(f * 1e3, rho, h, n) * 1e6 for rho, h in (al, cu)
             for n in (1, 10)]
        out[f] = r
        lines.append(f"  {f:8d}   {r[0]:9.2f}   {r[1]:11.2f}   {r[2]:9.2f}   "
                     f"{r[3]:11.2f}")
    lines += ["  resistance falls as 1 / sqrt(force) and with the number of",
              "  spots: a clean, flat, well-tightened face makes many spots;",
              "  an oxide film on aluminium adds far more than the table and",
              "  is broken by the contact preparation the maker specifies",
              "  heat in one phase of a lug at 368 A (string WS1, W001):"]
    for r_u in (10, 30, 100):
        lines.append(f"    {r_u:3d} micro-ohm: {368 ** 2 * r_u * 1e-6:5.1f} W")
    lines += ["  the bad joint heats ten times more - and its heat oxidises the",
              "  faces, which raises the resistance further: a joint drifts",
              "  one way, so a torque mark and a thermal image are kept (ch 24)"]
    emit("e_holm", lines)
    return out


if __name__ == "__main__":
    field()
    thickness()
    reports()
    compound()
    ageing()
    holm()
