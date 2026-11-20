"""Chapter 45, lesson B: production and quality - coating weight as a
controlled characteristic, water in the dry room, formation and grading
data of one lot read for outliers, matching cells into modules, laser
welds of the busbars, and the BMS configuration checked against the cell.

Run from the project root:   python -m companion.ch45.examples_b
Writes companion/ch45/expected/b_*.txt and diagrams/data/ch45-*.csv.
Teaching values (A-475 to A-477); purposes and checks, not a recipe.
"""
from __future__ import annotations

import numpy as np

from companion.ch45 import sources as src
from companion.ch45.common import csv, emit
from plantp import cellmfg as cf
from plantp import convmfg as cm
from plantp import pvfab
from plantp import quality as qy

C, B = src.CELL, src.BUILD


# ------------------------------------------------ coating weight
def coating(seed: int = 4503, n: int = 60, tol: float = 0.02) -> dict:
    rng = np.random.default_rng(seed)
    target = src.DESIGN["pos_loading"]
    a = rng.normal(target * 1.002, target * 0.005, n)            # line A
    b = rng.normal(target * 1.010, target * 0.008, n)            # line B
    lsl, usl = target * (1 - tol), target * (1 + tol)
    out = {}
    lines = [f"positive coating weight, target {target} mg/cm2 +-{tol:.0%} "
             "(teaching),",
             "  60 readings a line",
             "  line   mean     sd      Cp     Cpk    worst spot N/P margin"]
    pos0 = cf.areal_capacity(target, src.DESIGN["pos_active"], src.DESIGN["pos_spec"])
    neg = cf.areal_capacity(src.DESIGN["neg_loading"], src.DESIGN["neg_active"],
                            src.DESIGN["neg_spec"])
    for name, x in (("A", a), ("B", b)):
        m, s, cp, cpk = qy.cp_cpk(list(x), lsl, usl)
        worst = cf.np_ratio(neg, pos0 * (m + 3 * s) / target) - 1
        out[name] = (m, s, cp, cpk, worst)
        lines.append(f"  {name:4s}   {m:6.2f}   {s:5.3f}   {cp:5.2f}   {cpk:5.2f}   "
                     f"{worst:+11.1%}")
    lines += ["  line B coats heavy and wide: its Cpk is low and at its",
              "  +3 sigma spot the electrode balance has little margin left;",
              "  the coating weight is measured across and along the web",
              "  and charted - the numbers in the data sheet rest on it"]
    emit("b_coating", lines)
    return out


# ------------------------------------------------ dry room
def dry_room() -> dict:
    rows = [("outside, humid day", 20.0), ("ordinary factory hall", 10.0),
            ("controlled room", -10.0), ("dry room (teaching)", -40.0)]
    base = cf.abs_humidity_g_m3(rows[1][1])
    lines = ["water in the air at a dew point (Magnus, teaching accuracy)",
             "  air                       dew point C   water g/m3   share of hall"]
    out = {}
    for name, dew in rows:
        w = cf.abs_humidity_g_m3(dew)
        out[name] = w
        lines.append(f"  {name:25s} {dew:11.0f}   {w:10.3f}   {w / base:13.2%}")
    share = out["dry room (teaching)"] / base
    lines += ["  water reacts with the electrolyte salt and makes gas and",
              "  acid: electrode and cell assembly are done in air with about",
              f"  {share:.0%} of a hall's water - the dew point is",
              "  logged continuously, and a record above the limit puts the",
              "  hours' cells on hold (the limit is the cell maker's)"]
    emit("b_dryroom", lines)
    return out


# ------------------------------------------------ formation and grading data
def grading(k_limit: float = 3.5) -> dict:
    lot = src.lot()
    k, cap, dcir = lot["k"], lot["cap"], lot["dcir"]
    bad_record = [i for i, x in enumerate(k) if x < 0]
    good = [i for i in range(len(k)) if i not in bad_record]
    zk = pvfab.robust_z([k[i] for i in good])
    zc = pvfab.robust_z(list(cap))
    zr = pvfab.robust_z(list(dcir))
    f_k = [good[j] for j, z in enumerate(zk) if z > k_limit]
    f_c = [i for i, z in enumerate(zc) if z < -k_limit]
    f_r = [i for i, z in enumerate(zr) if z > k_limit]
    hit_k = len(set(f_k) & set(lot["leak"]))
    hit_c = len(set(f_c) & set(lot["low"]))
    hit_r = len(set(f_r) & set(lot["high"]))
    csv("ch45-lot.csv", "cap,k", [(round(float(c), 2), round(float(x), 4))
                                  for c, x in zip(cap, k) if x >= 0])
    lines = [f"formation and grading of lot L4506: {len(k)} cells (synthetic, "
             "A-475)",
             f"  capacity median {np.median(cap):.1f} Ah, pulse resistance "
             f"median {np.median(dcir) * 1000:.0f} uohm,",
             f"  K-value median {np.median(k[good]):.3f} mV/day (14-day rest)",
             f"  records rejected before analysis: {len(bad_record)}",
             "    (a negative voltage drop: a sign or entry error)",
             f"  robust z beyond {k_limit}: K-value high {len(f_k)}, "
             f"capacity low {len(f_c)}, resistance high {len(f_r)}",
             "  flagged K: " + ", ".join(lot["ids"][i] for i in f_k),
             f"  planted leakers found: {hit_k} of {len(lot['leak'])}; "
             f"low-capacity {hit_c} of {len(lot['low'])};",
             f"    high-resistance {hit_r} of {len(lot['high'])}",
             f"  the other {len(f_r) - hit_r} resistance flags are the tail "
             "of a normal spread:",
             "  a flag is a question for the cell's record, not a verdict;",
             "  a slow leaker passes capacity and resistance and shows only",
             "  in its rest voltage - the K-value is the screen for internal",
             "  micro-shorts, and the rest period is part of the process"]
    emit("b_grading", lines)
    return dict(f_k=f_k, f_c=f_c, f_r=f_r, bad_record=bad_record,
                caught=hit_k)


# ------------------------------------------------ matching
def matching(seed: int = 4504) -> dict:
    lot = src.lot()
    flagged = set(lot["leak"]) | set(lot["low"]) | set(lot["high"]) | {lot["bad_record"]}
    caps = [float(c) for i, c in enumerate(lot["cap"]) if i not in flagged]
    rng = np.random.default_rng(seed)
    order = list(rng.permutation(len(caps)))
    arrival = [caps[i] for i in order]
    n = B["s_module"]
    out = {}
    lines = [f"{len(caps)} graded cells into modules of {n} in series;",
             "  a string delivers its weakest cell",
             "  method          modules   mean of string min Ah   spread lost Ah"]
    for name, cells in (("arrival order", arrival), ("sorted", caps)):
        mods = cf.match(cells, n, "random" if name == "arrival order" else "sorted")
        mins = [cf.string_capacity(m) for m in mods]
        lost = np.mean([np.mean(m) - min(m) for m in mods])
        out[name] = (len(mods), float(np.mean(mins)), float(lost))
        lines.append(f"  {name:14s} {len(mods):8d}   {np.mean(mins):21.2f}   "
                     f"{lost:14.2f}")
    gain = out["sorted"][1] - out["arrival order"][1]
    lines += [f"  sorting gains {gain:.2f} Ah a module ({gain / C['q_ah']:.2%}); "
              "the BMS balances",
              "  charge, not capacity - a matched string uses more of its",
              "  cells; the bin of each cell goes into the module record"]
    emit("b_matching", lines)
    return out


# ------------------------------------------------ busbar welds
def welds(i_a: float = 157.0, limit_uohm: float = 30.0) -> dict:
    r = src.welds()
    bad = [k for k, x in enumerate(r) if x > limit_uohm]
    heat = i_a ** 2 * r * 1e-6
    lines = [f"laser welds of one module's busbars: {len(r)} welds, current "
             f"{i_a:.0f} A (0.5 C)",
             f"  resistance median {np.median(r):.1f} uohm, limit {limit_uohm:.0f} "
             "uohm (teaching)",
             f"  welds over the limit: {len(bad)} (positions {', '.join(str(k + 1) for k in bad)})",
             f"  heat: good weld {np.median(heat):.2f} W, worst "
             f"{heat.max():.2f} W ({heat.max() / np.median(heat):.1f} x)",
             f"  module drop over all welds: {r.sum() * i_a * 1e-6 * 1000:.0f} mV",
             "  a cold weld conducts on day one and heats in service: the",
             "  resistance of every weld is measured and kept - a visual",
             "  check sees the bead, not the bond"]
    emit("b_welds", lines)
    return dict(bad=bad, worst_w=float(heat.max()), median_w=float(np.median(heat)))


# ------------------------------------------------ BMS configuration
def bms() -> dict:
    res = cf.bms_check(src.BMS, src.CELL_LIMITS, src.MARGINS)
    fp = cm.fingerprint({k: v[1] for k, v in src.BMS.items()})
    lines = ["BMS limits as configured against the cell data and the required "
             "margins",
             "  limit             setting   cell   margin   ok"]
    for name, val, lim, ok in res:
        lines.append(f"  {name:16s} {val:8.2f} {lim:6.2f}   "
                     f"{src.MARGINS[name]:6.2f}   {'yes' if ok else 'NO'}")
    bad = [r[0] for r in res if not r[3]]
    lines += [f"  configuration fingerprint {fp}",
              f"  {len(bad)} limit wrong: {', '.join(bad)} - set above the cell's own",
              "  charging limit; the cell data sheet, the BMS settings and the",
              "  integrator's test record must name the same values, and the",
              "  fingerprint ties the delivered configuration to the record"]
    emit("b_bms", lines)
    return dict(bad=bad, fp=fp)


if __name__ == "__main__":
    coating()
    dry_room()
    grading()
    matching()
    welds()
    bms()
