"""Chapter 41, lesson B - the route from material to cell at textbook
level: the process map, purity counted for dopants and for metals, dopant
segregation along an ingot, silicon per watt, incoming wafers, the
anti-reflection coating, sheet resistance, the firing window on a
normalised scale, shunts and low light, binning with tester error, cell-lot
genealogy and the reference-cell chain.

Run from the project root:   python -m companion.ch41.examples_b
Writes companion/ch41/expected/b_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-443). Every step is named by its purpose, the variable
it controls and the defect it can cause - never by its settings.
"""
from __future__ import annotations

import cmath
import math
import random
from statistics import mean, pstdev

from companion.ch41 import sources as src
from companion.ch41.common import csv, emit
from companion.ch41.examples_a import CELL, Q, VT300
from plantp import pvfab as fab
from plantp import quality as qa

SI_ATOMS = 5.0e22                 # atoms per cm3


# ------------------------------------------------------------ process map
def process_map() -> None:
    lines = ["cell process map (purpose / controlled variable / defect)"]
    for k, (step, purpose, var, defect) in enumerate(src.CELL_STEPS, 1):
        lines += [f"  {k:2d} {step}: {purpose}",
                  f"       controls: {var}",
                  f"       can cause: {defect}"]
    lines += ["  each step has a measurable output; the cell's Voc, Jsc and",
              "  FF are the sum of all of them, which is why the line keeps",
              "  in-line metrology after the steps that set each one"]
    emit("b_map", lines)


# ------------------------------------------------------------ purity
def purity() -> dict[str, float]:
    sigma, v_th = 4e-14, 1e7               # cm2 (a metal trap), cm/s - A-443
    lines = ["purity: dopants are counted in ppm, metals in ppt",
             "  purity   impurity atoms/cm3   (base doping is 1e16)"]
    for nines in (6, 9, 11):
        n = SI_ATOMS * 10 ** -nines
        lines.append(f"  {nines:2d} N      {n:16.1e}")
    lines += ["  a metal trap with capture cross-section 4e-14 cm2:",
              "  trap density   lifetime from it alone   (1/sigma v N)"]
    out = {}
    for nt in (1e10, 1e11, 1e12):
        tau = 1 / (sigma * v_th * nt)
        out[nt] = tau
        lines.append(f"  {nt:10.0e}     {tau * 1e6:12.1f} us   "
                     f"({nt / SI_ATOMS:.0e} of the atoms)")
    from companion.ch41.examples_a import implied_voc
    v25 = implied_voc(25e-6, 10)[1]
    lines += ["  one metal atom in 5e11 silicon atoms already limits the",
              f"  lifetime to 25 us (implied Voc {v25:.3f} V with good "
              "surfaces);",
              "  a dopant at that level would change nothing - so the",
              "  specification counts metals separately, and gettering and",
              "  clean handling protect the lifetime along the whole line"]
    emit("b_purity", lines)
    return out


# ---------------------------------------------- segregation along an ingot
# [start: scheil]
def scheil(f: float, k: float) -> float:
    """Dopant in the solid at fraction f solidified, relative to the
    melt's starting concentration (normal freezing, Scheil)."""
    return k * (1 - f) ** (k - 1)
# [end: scheil]


def ingot(rho_seed: float = 1.1, lo: float = 0.4) -> dict[str, float]:
    mu = 400.0                         # hole mobility, cm2/Vs (constant)
    rows, usable = [], {}
    for name, k in (("boron", 0.8), ("gallium", 0.008)):
        n_seed = 1 / (Q * mu * rho_seed)
        good = 0.0
        for j in range(0, 991):
            f = j / 1000
            rho = rho_seed * scheil(0.0, k) / scheil(f, k)
            if rho >= lo:
                good = f
        usable[name] = good
        _ = n_seed
    for j in range(0, 96):
        f = j / 100
        rows.append((round(f, 2),
                     round(rho_seed * scheil(0, 0.8) / scheil(f, 0.8), 4),
                     round(rho_seed * scheil(0, 0.008) / scheil(f, 0.008), 4)))
    csv("ch41-ingot.csv", "f,boron,gallium", rows)
    lines = [f"resistivity along a pulled ingot (seed end {rho_seed} ohm cm,"
             f" window {lo}-{rho_seed})",
             "  share solidified   boron (k 0.8)   gallium (k 0.008)"]
    for f in (0.0, 0.25, 0.5, 0.75, 0.9):
        rb = rho_seed * scheil(0, 0.8) / scheil(f, 0.8)
        rg = rho_seed * scheil(0, 0.008) / scheil(f, 0.008)
        lines.append(f"  {f:16.2f}   {rb:13.2f}   {rg:17.2f}")
    lines += [f"  usable length in the window: boron {usable['boron']:.0%}, "
              f"gallium {usable['gallium']:.0%}",
              "  gallium stays in the melt, so the tail gets heavily doped;",
              "  boron is even but pairs with oxygen into a defect that",
              "  costs power in the first hours of sunlight - the choice is",
              "  a trade-off the module buyer sees only through the maker's",
              "  degradation data (light-induced degradation in the dossier)"]
    emit("b_ingot", lines)
    return usable


# ------------------------------------------------------ silicon per watt
def silicon() -> dict[str, float]:
    area, rho_si = CELL["area_cm2"], 2.33
    p_cell = 7.71                                 # W, lesson A budget
    out = {}
    lines = ["silicon in the PVM-550's cells (wafer + kerf, A-443)",
             "  wafer um  kerf um  g a wafer  g with kerf   g/W   t for 60 MWp"]
    for w, kerf in ((180, 120), (150, 55), (130, 45)):
        g = area * w * 1e-4 * rho_si
        gk = area * (w + kerf) * 1e-4 * rho_si
        gpw = gk / p_cell
        out[w] = gpw
        lines.append(f"  {w:8d}  {kerf:7d}  {g:9.1f}  {gk:11.1f}  {gpw:5.2f}"
                     f"   {gpw * 60e6 / 1e6:10.0f}")
    lines += ["  thinner wafers and thinner wire cut the silicon a watt;",
              "  the cost is handling: a thin wafer breaks more easily and",
              "  cracks hide until stringing and lamination (lesson C)"]
    emit("b_silicon", lines)
    return out


# ------------------------------------------------------ incoming wafers
def wafers(seed: int = 4102) -> dict[str, float]:
    rng = random.Random(seed)
    t = [rng.gauss(150.5, 4.0) for _ in range(500)]
    m, s, cp, cpk = qa.cp_cpk(t, 135.0, 165.0)
    crack_rate, find = 0.005, 0.9
    lines = ["incoming wafers: thickness capability and hidden cracks",
             f"  thickness of 500 wafers: mean {m:.1f} um, sd {s:.1f};"
             f" Cp {cp:.2f}, Cpk {cpk:.2f}",
             f"  cracked wafers {crack_rate:.1%}; in-line camera finds "
             f"{find:.0%}",
             f"  cracks passed on to the cell line: "
             f"{crack_rate * (1 - find):.2%} ({crack_rate * (1 - find) * 1e6:,.0f} ppm)",
             "  a crack that passes breaks a wafer in a later step (lost",
             "  work) or, worse, survives into a module (lesson C); the",
             "  camera's find rate is measured with seeded samples, like",
             "  any inspection (ch 40, sampling and detection)"]
    emit("b_wafers", lines)
    return dict(cp=cp, cpk=cpk, escape=crack_rate * (1 - find))


# --------------------------------------------- anti-reflection coating
N_SI = {400: 5.57, 500: 4.29, 600: 3.94, 700: 3.78, 800: 3.69, 900: 3.63,
        1000: 3.57, 1100: 3.54}       # real index of silicon (textbook)


def _n_si(lam: float) -> float:
    ks = sorted(N_SI)
    for a, b in zip(ks, ks[1:]):
        if a <= lam <= b:
            return N_SI[a] + (N_SI[b] - N_SI[a]) * (lam - a) / (b - a)
    return N_SI[ks[-1]]


# [start: arc]
def reflectance(lam_nm: float, n0: float, n1: float, d_nm: float) -> float:
    """Normal-incidence reflectance of one thin layer (index n1, thickness
    d) between a medium n0 and silicon (no absorption)."""
    ns = _n_si(lam_nm)
    r01, r12 = (n0 - n1) / (n0 + n1), (n1 - ns) / (n1 + ns)
    ph = cmath.exp(-2j * 2 * math.pi * n1 * d_nm / lam_nm)
    r = (r01 + r12 * ph) / (1 + r01 * r12 * ph)
    return abs(r) ** 2
# [end: arc]


def arc() -> dict[str, float]:
    lams = list(range(400, 1101, 10))
    cases = {"bare, in air": (1.0, 1.0, 0.0),
             "75 nm n 2.0, in air": (1.0, 2.0, 75.0),
             "75 nm n 2.0, under encapsulant": (1.5, 2.0, 75.0),
             "75 nm n 2.2, under encapsulant": (1.5, 2.2, 75.0)}
    avg = {}
    for name, (n0, n1, d) in cases.items():
        avg[name] = mean(reflectance(lam, n0, n1, d) for lam in lams)
    rows = [(lam, round(reflectance(lam, 1, 1, 0) * 100, 2),
             round(reflectance(lam, 1, 2.0, 75) * 100, 2),
             round(reflectance(lam, 1.5, 2.2, 75) * 100, 2)) for lam in lams]
    csv("ch41-arc.csv", "lam,bare,air,encap", rows)
    lines = ["reflectance of polished silicon, 400-1100 nm (flat weighting)",
             "  case                                 mean R   x2 bounces"]
    for name, r in avg.items():
        lines.append(f"  {name:36s} {r:6.1%}   {r * r:8.2%}")
    lines += [f"  the minimum sits at 4 n d = {4 * 2.0 * 75:.0f} nm; 5 nm thicker"
              f" moves it to {4 * 2.0 * 80:.0f} nm,",
              "  which the eye sees as colour - cells are sorted by colour",
              "  so a module looks even; under the encapsulant a higher",
              "  index works better; texture sends the reflected light to a",
              "  second facet (about R squared): optics are designed for the",
              "  module, not for the bare cell"]
    emit("b_arc", lines)
    return avg


# ----------------------------------------------- sheet resistance map
def sheet(seed: int = 4103) -> dict[str, float]:
    rng = random.Random(seed)
    pts = [(x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)]
    vals = []
    lines = ["emitter sheet resistance by four-point probe (9 points)",
             "  R_sheet = (pi / ln 2) V / I = 4.532 V / I"]
    for x, y in pts:
        r = 120 * (1 + 0.04 * (x * x + y * y)) + rng.gauss(0, 1.5)
        v_over_i = r / 4.532
        vals.append(r)
        lines.append(f"  point ({x:+d},{y:+d})  V/I {v_over_i:6.2f} ohm  -> "
                     f"{r:6.1f} ohm/sq")
    u = (max(vals) - min(vals)) / (max(vals) + min(vals))
    lines += [f"  mean {mean(vals):.1f} ohm/sq; non-uniformity "
              f"(max-min)/(max+min) {u:.1%}",
              "  edges higher than the centre: the grid of lesson A was",
              "  designed for 120 ohm/sq, so the edges lose a little more",
              "  to lateral flow; the trend, not one point, is controlled"]
    emit("b_sheet", lines)
    return dict(mean=mean(vals), u=u)


# --------------------------------------------- firing window (normalised)
def firing_ff(x: float) -> float:
    """Teaching model on a normalised firing setting x (0..1, no units):
    contact resistance falls as x rises; past 0.7 the contact starts to
    shunt the junction. Not a recipe: x stands for any thermal input."""
    rc = 0.30 + 3.0 * math.exp(-x / 0.10)
    rsh = 5000.0 if x < 0.7 else 5000.0 * math.exp(-(x - 0.7) / 0.04)
    return fab.fill_factor(CELL["voc"], 0.34 + rc, CELL["jsc"],
                           rsh_ohm_cm2=rsh)


def firing() -> dict[str, float]:
    xs = [k / 200 for k in range(40, 181)]
    ffs = [firing_ff(x) for x in xs]
    best = max(ffs)
    ok = [x for x, f in zip(xs, ffs) if f >= best - 0.005]
    lo, hi = min(ok), max(ok)
    centre, sd = (lo + hi) / 2, 0.03
    cpk = min(centre - lo, hi - centre) / (3 * sd)
    csv("ch41-firing.csv", "x,ff", [(round(x, 3), round(f, 4))
                                     for x, f in zip(xs, ffs)])
    lines = ["firing as a process window (normalised setting 0..1)",
             f"  best fill factor {best:.3f}; window for best - 0.005: "
             f"{lo:.2f} to {hi:.2f}",
             f"  run at the centre {centre:.2f} with a spread of sd {sd}:"
             f" Cpk {cpk:.2f}",
             "  too little: contacts do not form (series resistance);",
             "  too much: the metal reaches the junction (shunts) - the",
             "  window is found by experiment on the line (ch 40, the",
             "  factorial) and guarded by the fill factor of each lot"]
    emit("b_firing", lines)
    return dict(lo=lo, hi=hi, cpk=cpk, best=best)


# --------------------------------------------- shunts and low light
def low_light() -> dict[float, tuple[float, float]]:
    out = {}
    lines = ["edge shunts show at low light (teaching cell)",
             "  shunt ohm cm2   eff at 1000 W/m2   at 200 W/m2   relative"]
    for rsh in (5000.0, 1000.0, 300.0):
        res = []
        for g in (1000.0, 200.0):
            jsc = CELL["jsc"] * g / 1000
            voc = fab.voc(jsc, 9.1e-14)
            ff = fab.fill_factor(voc, CELL["rs"], jsc, rsh_ohm_cm2=rsh)
            res.append(voc * jsc * ff / (g / 1e4))
        out[rsh] = tuple(res)
        lines.append(f"  {rsh:13.0f}   {res[0]:16.2%}   {res[1]:11.2%}   "
                     f"{res[1] / res[0]:8.3f}")
    lines += ["  a shunt that costs a little at full sun costs much more at",
              "  200 W/m2, where the plant spends many hours: cells are",
              "  tested at low light or by dark current before sorting"]
    emit("b_lowlight", lines)
    return out


# ------------------------------------------------ binning with tester error
def binning(n: int = 20000, seed: int = 4104, rep: float = 0.02,
            drift: float = 0.0) -> dict[str, float]:
    rng = random.Random(seed)
    edges = src.CELL_BINS
    wrong = 0
    out_true, out_meas = [0] * 4, [0] * 4
    for _ in range(n):
        true = rng.gauss(14.00, 0.08)
        meas = true * (1 + drift) + rng.gauss(0, rep)
        try:
            bt = fab.bin_of(true, edges)
            bm = fab.bin_of(meas, edges)
        except ValueError:
            continue
        out_true[bt] += 1
        out_meas[bm] += 1
        wrong += bt != bm
    return dict(wrong=wrong / n, true=out_true, meas=out_meas)


def binning_lesson() -> dict[str, float]:
    a = binning()
    b = binning(drift=0.005)
    lines = ["cell current bins 13.8-14.2 A by 0.1 A (cells: mean 14.00, sd 0.08)",
             f"  tester repeatability sd 0.02 A: {a['wrong']:.1%} of cells "
             "land in a neighbour bin",
             f"  with a +0.5 % reference drift as well: {b['wrong']:.1%}",
             "  cells per bin, true / measured with the drift:",
             "    " + ", ".join(f"{t}/{m}" for t, m in zip(b["true"],
                                                      b["meas"])),
             "  a cell one bin off costs little (its string runs at the",
             "  weakest current, lesson D); a drift shifts every bin and",
             "  every module's label - the tester's reference is checked",
             "  each shift against a golden cell (lesson D, the flasher)"]
    emit("b_binning", lines)
    return dict(rep=a["wrong"], drift=b["wrong"])


# ------------------------------------------------ cell-lot genealogy
def genealogy(seed: int = 4105) -> dict[str, int]:
    rng = random.Random(seed)
    lot_size, cells_module, per_day = 24000, 72, 2400
    lots, cursor, lot_id = {}, 0, 100
    for m in range(per_day):
        need = cells_module
        mods_lots = set()
        while need:
            take = min(need, lot_size - cursor)
            mods_lots.add(lot_id)
            need -= take
            cursor += take
            if cursor == lot_size:
                cursor, lot_id = 0, lot_id + 1
        for lt in mods_lots:
            lots.setdefault(lt, set()).add(m)
    target = 101
    _ = rng
    lines = ["a cell lot found contaminated: which modules hold its cells?",
             f"  lot of {lot_size:,} cells; {cells_module} full cells a module;"
             f" {per_day:,} modules a day",
             f"  traced to the lot: {len(lots[target]):,} modules",
             f"  traced only to the day: {per_day:,} modules",
             "  lot-level genealogy (cell box scanned at the stringer) cuts",
             f"  the suspect set {per_day / len(lots[target]):.1f} times; the "
             "modules at a lot change",
             "  hold cells of two lots and belong to both suspect sets"]
    emit("b_genealogy", lines)
    return dict(lot=len(lots[target]), day=per_day)


# ------------------------------------------------ the reference-cell chain
def chain() -> dict[str, float]:
    steps = [("primary reference (world scale)", 0.4),
             ("secondary reference cell", 0.6),
             ("working reference module", 0.8),
             ("flash tester repeatability and spectrum", 0.9)]
    u = math.sqrt(sum(x * x for _, x in steps))
    lines = ["standard uncertainty of a module power reading (teaching %)"]
    for name, x in steps:
        lines.append(f"  {name:42s} {x:4.1f} %")
    lines += [f"  combined {u:.2f} %; expanded (k = 2) {2 * u:.2f} % = "
              f"{2 * u / 100 * 550:.1f} W at 550 W",
              f"  the label tolerance 0/+5 W is {5 / 550:.1%}: smaller than "
              "the",
              "  uncertainty of the reading - a tolerance is the maker's",
              "  sorting rule on its own tester, and the buyer's check needs",
              "  a decision rule (ch 10, flash; ch 40, conformity)"]
    emit("b_chain", lines)
    return dict(u=u, U=2 * u)


if __name__ == "__main__":
    process_map()
    purity()
    ingot()
    silicon()
    wafers()
    arc()
    sheet()
    firing()
    low_light()
    binning_lesson()
    genealogy()
    chain()
