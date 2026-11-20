"""Chapter 42, a sixth round on quality: a process FMEA of blade making
ranked as in ch 40, the turbine's critical characteristics with their
evidence, gear case depth from a hardness traverse, spar-cap thickness
capability by station, and the cost of quality of a blade factory.

Run from the project root:   python -m companion.ch42.examples_w
Writes companion/ch42/expected/w_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-452, A-456).
"""
from __future__ import annotations

import random
from statistics import mean

import numpy as np

from companion.ch42.common import csv, emit
from plantp import quality as qa

# ------------------------------------------------ process FMEA
# [start: fmea]
PFMEA = [  # step, failure mode, effect, S, O, D
    ("lay-up of caps", "ply off its angle", "cap stiffness low", 8, 3, 5),
    ("infusion", "dry spot", "local weakness, NCR", 7, 4, 3),
    ("cure", "under-cured zone", "softens in service", 9, 2, 4),
    ("bonding", "bond-line gap", "web disbond, blade loss", 10, 3, 4),
    ("root inserts", "insert misaligned", "bolt bending, fatigue", 9, 2, 3),
    ("lightning system", "conductor joint loose", "strike damage", 8, 2, 2),
    ("finishing", "thin edge coating", "early erosion", 5, 5, 3),
]
# [end: fmea]


def pfmea() -> list[str]:
    rows = [dict(step=a, mode=b, effect=c, s=s, o=o, d=d)
            for a, b, c, s, o, d in PFMEA]
    ranked = qa.fmea_rank(rows)
    lines = ["process FMEA of blade making, ranked by severity class, then",
             "  S x O, then D (ch 40); RPN shown only for comparison",
             "  step               failure mode            S  O  D  SxO  RPN"]
    for r in ranked:
        lines.append(f"  {r['step']:18s} {r['mode']:22s} {r['s']:2d} {r['o']:2d}"
                     f" {r['d']:2d}  {r['s'] * r['o']:3d}  "
                     f"{qa.rpn(r['s'], r['o'], r['d']):3d}")
    by_rpn = max(rows, key=lambda r: qa.rpn(r["s"], r["o"], r["d"]))
    lines += [f"  first by the ranking: {ranked[0]['mode']}; first by RPN: "
              f"{by_rpn['mode']}",
              "  a bond-line gap that can lose a blade outranks a common but",
              "  milder defect - severity first; the ranking sets where the",
              "  quality plan puts its holds (lab D)"]
    emit("w_pfmea", lines)
    return [r["mode"] for r in ranked]


# ------------------------------------------------ critical characteristics
CRIT = [
    ("blade", "cap fibre fraction", "coupon burn-off per cap"),
    ("blade", "web bond line", "UT scan map, POD on file"),
    ("blade", "root insert pull-out", "characteristic value per batch"),
    ("hub", "flange soundness", "UT by zone, nodularity bar"),
    ("main shaft", "fillet finish and soundness", "roughness, UT"),
    ("gearbox", "tooth case depth", "hardness traverse per heat"),
    ("gearbox", "run-in spectrum and oil", "spectra, iron trend"),
    ("generator", "winding insulation", "PI, sensors tested"),
    ("joints", "bolt preload", "logged torque and angle"),
]


def critical() -> int:
    lines = ["critical characteristics of the turbine and their evidence",
             "  part        characteristic                evidence"]
    for p, c, e in CRIT:
        lines.append(f"  {p:11s} {c:29s} {e}")
    lines += [f"  {len(CRIT)} characteristics where a manufacturing slip reaches",
              "  the load path or safety; each has a control-plan row and",
              "  a record the plant asks for at receipt (ch 40, critical)"]
    emit("w_critical", lines)
    return len(CRIT)


# ------------------------------------------------ gear case depth
def case_depth(seed: int = 4213, limit_hv: float = 550.0,
               spec=(2.4, 3.2)) -> dict[str, float]:
    rng = random.Random(seed)
    depths = np.arange(0.2, 4.01, 0.2)
    out = {}
    lines = [f"carburised gear: depth where hardness falls to {limit_hv:.0f} HV",
             f"  (traverse on a test coupon; teaching spec {spec[0]} - {spec[1]} mm)",
             "  heat    case depth mm   verdict"]
    rows = []
    for heat, cd in (("HT-41", 2.8), ("HT-42", 2.9), ("HT-43", 2.1)):
        hv = [max(300.0, 720 - (720 - 300) * (d / cd) ** 2 * 0.40)
              + rng.gauss(0, 6) for d in depths]
        x = float(np.interp(-limit_hv, [-v for v in hv], depths))
        out[heat] = x
        ok = spec[0] <= x <= spec[1]
        lines.append(f"  {heat:6s}  {x:13.2f}   {'accept' if ok else 'NCR'}")
        if heat == "HT-43":
            rows = [(round(float(d), 2), round(v, 1)) for d, v in zip(depths, hv)]
    csv("ch42-hardness.csv", "d,hv", rows)
    lines += ["  a shallow case wears and pits under contact stress; the",
              "  depth is read off the curve, not off one point, and a",
              "  failed coupon puts every gear of that heat on hold"]
    emit("w_case", lines)
    return out


# ------------------------------------------------ cap thickness by station
def cap_thickness(seed: int = 4214) -> dict[float, float]:
    rng = random.Random(seed)
    stations = {10.0: 65.0, 30.0: 47.0, 50.0: 25.0}     # m: mm (ch 11)
    out = {}
    lines = ["spar-cap thickness by station, 25 blades (UT gauge, +-6 % tol.)",
             "  station m   nominal mm   mean mm   sd    Cpk"]
    for r, nom in stations.items():
        sd = 0.012 * nom if r != 50.0 else 0.025 * nom
        vals = [nom * (1 + rng.gauss(0.0, sd / nom)) for _ in range(25)]
        _, s, _, cpk = qa.cp_cpk(vals, 0.94 * nom, 1.06 * nom)
        out[r] = cpk
        lines.append(f"  {r:9.0f}   {nom:10.0f}   {mean(vals):7.1f}  {s:4.2f}"
                     f"  {cpk:5.2f}")
    worst = min(out, key=out.get)
    lines += [f"  the station at {worst:.0f} m has the lowest capability: thin",
              "  plies near the tip drop off in steps, and a missing step",
              "  is a large share of a thin cap - the ply map's checks",
              "  are densest where the cap is thinnest"]
    emit("w_caps", lines)
    return out


# ------------------------------------------------ cost of quality
COPQ = {"prevention": {"training": 40, "process qualification": 90},
        "appraisal": {"UT scanning": 160, "coupons and DSC": 70, "weighing": 10},
        "internal failure": {"repairs": 210, "scrap (2 blades)": 520},
        "external failure": {"field repair": 380, "blade exchange": 900}}


def copq() -> dict[str, float]:
    tot = {k: sum(v.values()) for k, v in COPQ.items()}
    all_ = sum(tot.values())
    lines = ["cost of quality of one year's blades (36, teaching k u)",
             "  category            k u    share"]
    for k, v in tot.items():
        lines.append(f"  {k:18s} {v:5.0f}   {v / all_:6.0%}")
    lines += [f"  total {all_:,.0f} k u, {all_ / 36:.0f} k u a blade",
              f"  failures cost {(tot['internal failure'] + tot['external failure']) / tot['prevention']:.0f}"
              " times prevention: a blade exchanged in",
              "  the field costs more than all prevention together - the",
              "  same lesson as the skids of ch 40, in a heavier product"]
    emit("w_copq", lines)
    return dict(total=all_, **tot)


if __name__ == "__main__":
    pfmea()
    critical()
    case_depth()
    cap_thickness()
    copq()
