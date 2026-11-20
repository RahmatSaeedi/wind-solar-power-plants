"""Chapter 45, round w: random-input (property) tests of the educational
SOC simulator, boundary tests of a temperature rule for charging, a
process FMEA of module assembly ranked severity first, a p-chart of weld
rejects by shift, and a first-article check of a module.

Run from the project root:   python -m companion.ch45.examples_w
Writes companion/ch45/expected/w_*.txt.
Teaching values (A-476 to A-481); nothing here is a BMS.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch45 import sources as src
from companion.ch45.common import csv, emit
from plantp import cellmfg as cf
from plantp import quality as qy

C = src.CELL


# ------------------------------------------------ 1. property tests
# [start: prop]
def property_test(cls=cf.SocSim, runs: int = 200, steps: int = 50,
                  seed: int = 4511) -> dict:
    """Random currents and time steps; after every step the SOC is in the
    window, and at the end the charge balance holds."""
    rng = np.random.default_rng(seed)
    broken_window = broken_balance = 0
    for _ in range(runs):
        soc0 = float(rng.uniform(0.1, 0.9))
        sim = cls(q_ah=C["q_ah"], soc=soc0)
        for _ in range(steps):
            i = float(rng.normal(0.0, 300.0))
            dt = float(rng.uniform(1.0, 3600.0))
            sim.step(i, dt)
            if not sim.lo - 1e-9 <= sim.soc <= sim.hi + 1e-9:
                broken_window += 1
        if abs(sim.balance_error(soc0)) > 1e-6:
            broken_balance += 1
    return dict(runs=runs, steps=runs * steps, window=broken_window,
                balance=broken_balance)
# [end: prop]


def properties() -> dict:
    from companion.ch45.examples_u import SocSimV11
    a = property_test(cf.SocSim)
    b = property_test(SocSimV11)
    lines = [f"property tests: {a['runs']} runs of 50 random steps each",
             "  (currents and time steps drawn at random)",
             "  version   steps    window broken   balance broken (runs)"]
    for name, r in (("v1.0", a), ("v1.1", b)):
        lines.append(f"  {name:7s} {r['steps']:7d}   {r['window']:13d}   "
                     f"{r['balance']:22d}")
    lines += ["  a hand-written case tests what its author thought of; random",
              "  inputs test what nobody thought of - ten thousand steps in a",
              "  second, and the invariants decide pass or fail without an",
              f"  expected answer for each step; v1.1's bug fails {b['balance']} of",
              f"  {b['runs']} runs"]
    emit("w_prop", lines)
    return dict(v10=a, v11=b)


# ------------------------------------------------ 2. a charging rule and its edges
# [start: rule]
def charge_allowed(t_cell: float, lo: float = 2.0, hi: float = 52.0) -> bool:
    """Educational rule: charging only between lo and hi (inclusive)."""
    return lo <= t_cell <= hi
# [end: rule]


EDGE_CASES = [(1.99, False), (2.00, True), (2.01, True), (25.0, True),
              (51.99, True), (52.00, True), (52.01, False), (-20.0, False),
              (float("nan"), False)]


def edges() -> dict:
    res = [(t, want, charge_allowed(t)) for t, want in EDGE_CASES]
    bad = [(t, w, g) for t, w, g in res if w != g]
    lines = ["boundary tests of the educational charging rule (2 to 52 C, edges "
             "included)",
             "  cell C      expected   got"]
    for t, w, g in res:
        lines.append(f"  {t:9.2f}   {str(w):8s}   {g}")
    lines += [f"  {len(res)} cases, {len(bad)} failing; a missing reading (nan) "
              "is refused because",
              "  every comparison with nan is false - a happy accident here,",
              "  so it gets its own case: a rule that must refuse on a lost",
              "  sensor is tested on a lost sensor, not trusted to"]
    emit("w_edges", lines)
    return dict(n=len(res), bad=len(bad))


# ------------------------------------------------ 3. process FMEA of module assembly
FMEA = [   # step, failure mode, s, o, d
    ("cell placement", "cell reversed", 9, 2, 2),
    ("cell placement", "wrong bin in module", 5, 3, 4),
    ("compression", "force too low", 6, 3, 5),
    ("busbar welding", "cold weld", 8, 4, 4),
    ("busbar welding", "spatter on cell", 7, 2, 6),
    ("sense wiring", "sense lead swapped", 9, 2, 3),
    ("sense wiring", "temperature sensor off its cell", 7, 3, 6),
    ("insulation", "sheet missing at frame", 9, 1, 3),
    ("labelling", "lot not written on module", 4, 3, 7),
]


def fmea() -> dict:
    rows = [dict(step=a, mode=b, s=s, o=o, d=d) for a, b, s, o, d in FMEA]
    ranked = qy.fmea_rank(rows)
    by_rpn = sorted(rows, key=lambda r: -qy.rpn(r["s"], r["o"], r["d"]))
    lines = ["process FMEA of module assembly (teaching ratings),",
             "  ranked severity first (ch 40)",
             "  rank  failure mode                       S  O  D   RPN  "
             "RPN rank"]
    for k, r in enumerate(ranked, 1):
        lines.append(f"  {k:4d}  {r['mode']:33s} {r['s']:2d} {r['o']:2d} "
                     f"{r['d']:2d} {qy.rpn(r['s'], r['o'], r['d']):5d}  "
                     f"{by_rpn.index(r) + 1:8d}")
    top = ranked[0]["mode"]
    lines += [f"  ranked by RPN alone, '{by_rpn[0]['mode']}' would lead;",
              f"  severity first puts '{top}' and the other",
              "  severity-9 modes on top - the controls go to what can hurt",
              "  most, then to what is frequent"]
    emit("w_fmea", lines)
    return dict(top=top, rpn_top=by_rpn[0]["mode"])


# ------------------------------------------------ 4. weld rejects by shift
def weld_chart(seed: int = 4512, shifts: int = 24, n: int = 1224,
               p0: float = 0.004) -> dict:
    """n welds a shift (12 modules); rejects counted; the electrode cap
    wore in shift 17 (planted)."""
    rng = np.random.default_rng(seed)
    p = np.full(shifts, p0)
    p[16:19] = 0.012
    rej = rng.binomial(n, p)
    pbar = rej[:16].sum() / (16 * n)
    ucl = pbar + 3 * math.sqrt(pbar * (1 - pbar) / n)
    sig = [k + 1 for k in range(shifts) if rej[k] / n > ucl]
    csv("ch45-pchart.csv", "shift,p,ucl,pbar",
        [(k + 1, round(1000 * rej[k] / n, 3), round(1000 * ucl, 3),
          round(1000 * pbar, 3)) for k in range(shifts)])
    lines = [f"weld rejects by shift, {n} welds a shift (synthetic); centre from "
             "shifts 1-16",
             f"  p-bar {pbar:.4f}, upper limit {ucl:.4f}",
             "  shift: " + " ".join(f"{k + 1:3d}" for k in range(12)),
             "  rejects " + " ".join(f"{int(x):3d}" for x in rej[:12]),
             "  shift: " + " ".join(f"{k + 1:3d}" for k in range(12, 24)),
             "  rejects " + " ".join(f"{int(x):3d}" for x in rej[12:]),
             f"  shifts above the limit: {', '.join(map(str, sig)) or 'none'}",
             "  the chart sees a worn electrode cap within a shift or two;",
             "  each weld's resistance (lesson B) says which welds, the",
             "  chart says when the process changed (ch 40)"]
    emit("w_chart", lines)
    return dict(ucl=ucl, signals=sig)


# ------------------------------------------------ 5. first article of a module
FAI = [   # characteristic, required, measured, ok
    ("cells, bin and lot recorded", "52 of 52", "52 of 52", True),
    ("cell polarity", "all correct", "all correct", True),
    ("compression force", "within the drawing", "within", True),
    ("weld resistance", "all <= 30 uohm", "102 of 102", True),
    ("sense wiring map", "matches drawing", "2 leads swapped", False),
    ("temperature sensors", "8 at drawing places", "8, one 2 cells off", False),
    ("insulation to frame", "test passed", "passed", True),
    ("label and lot", "present", "present", True),
]


def first_article() -> dict:
    bad = [c for c, _, _, ok in FAI if not ok]
    lines = ["first-article check of the first module off the line",
             "  characteristic               required             measured"]
    for c, req, got, ok in FAI:
        lines.append(f"  {c:28s} {req:20s} {got}{'' if ok else '  <- NO'}")
    lines += [f"  {len(bad)} of {len(FAI)} fail: both in the BMS wiring - the place",
              "  where returns also start (round u); the line does not run",
              "  until the drawing or the jig is corrected and a second",
              "  first article passes (ch 40)"]
    emit("w_fai", lines)
    return dict(bad=bad)


if __name__ == "__main__":
    properties()
    edges()
    fmea()
    weld_chart()
    first_article()
