"""Chapter 41, a third round: light trapping and wafer thickness, silver
per watt, agreement of two EL graders, water through the backsheet, the
strain a joint sees each cycle, glass-glass stiffness and the
encapsulant's grip, check digits on serial numbers, where to put the EL
inspection, and the capability of ribbon peel strength.

Run from the project root:   python -m companion.ch41.examples_t
Writes companion/ch41/expected/t_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-443 to A-445); absorption coefficients are rounded
textbook values for silicon at 300 K.
"""
from __future__ import annotations

import math
import random

import numpy as np

from companion.ch41.common import csv, emit
from plantp import quality as qa

H, C_L, Q, K_B = 6.62607015e-34, 2.99792458e8, 1.602176634e-19, 1.380649e-23

# [start: alpha]
ALPHA = {400: 9.5e4, 500: 1.1e4, 600: 4.1e3, 700: 1.9e3, 800: 850.0,
         900: 306.0, 1000: 64.0, 1050: 16.3, 1100: 3.5}   # 1/cm, textbook
# [end: alpha]


def _alpha(lam: float) -> float:
    ks = sorted(ALPHA)
    for a, b in zip(ks, ks[1:]):
        if a <= lam <= b:
            la, lb = math.log(ALPHA[a]), math.log(ALPHA[b])
            return math.exp(la + (lb - la) * (lam - a) / (b - a))
    return 0.0


def _flux(lam_nm: float, t: float = 5778.0) -> float:
    """Blackbody photon flux shape (as ch 10, A-184), per nm, unscaled."""
    lam = lam_nm * 1e-9
    return 2 * C_L / lam ** 4 / math.expm1(H * C_L / (lam * K_B * t))


# ------------------------------------------------ light trapping
def trapping(n_si: float = 3.6) -> dict[str, dict[int, float]]:
    lams = np.arange(400, 1101, 5)
    phi = np.array([_flux(x) for x in lams])
    scale = 39.6 / (phi.sum())            # ch 10: J max 39.6 mA/cm2
    out = {}
    cases = {"one pass": lambda a, w: 1 - math.exp(-a * w),
             "two passes (mirror)": lambda a, w: 1 - math.exp(-2 * a * w),
             "light trapping (4n2)": lambda a, w: 1 - 1 / (1 + 4 * n_si ** 2
                                                            * a * w)}
    rows = []
    for name, f in cases.items():
        out[name] = {}
        for w_um in (50, 100, 150, 180):
            w = w_um * 1e-4
            j = sum(p * f(_alpha(x), w) for x, p in zip(lams, phi)) * scale
            out[name][w_um] = j
    for w_um in range(20, 301, 10):
        w = w_um * 1e-4
        row = [w_um]
        for f in cases.values():
            row.append(round(sum(p * f(_alpha(x), w) for x, p in
                                 zip(lams, phi)) * scale, 3))
        rows.append(tuple(row))
    csv("ch41-trap.csv", "w,one,two,trap", rows)
    lines = ["current a wafer can absorb (blackbody sun as ch 10, 39.6 max)",
             "  optics                      50 um   100 um   150 um   180 um"]
    for name, d in out.items():
        lines.append(f"  {name:26s} " + "  ".join(f"{d[w]:6.1f}" for w in
                                                    (50, 100, 150, 180)))
    lines += ["  mA/cm2; light trapping (texture plus a reflecting rear)",
              "  lets a 100 um wafer absorb more than a 180 um wafer in one",
              "  pass - why texture and the rear mirror allowed thinner",
              "  wafers (lesson B, silicon per watt)"]
    emit("t_trapping", lines)
    return out


# ------------------------------------------------ silver per watt
def silver(mg_cell=(100.0, 70.0, 40.0), p_cell: float = 7.71,
           mwp: float = 60.06) -> dict[float, float]:
    out = {}
    lines = ["silver in the front and rear contacts (teaching amounts)",
             "  mg a cell   mg/W   kg for Plant P (60 MWp)"]
    for mg in mg_cell:
        mgw = mg / p_cell
        kg = mgw * mwp * 1e6 / 1e6
        out[mg] = kg
        lines.append(f"  {mg:9.0f}   {mgw:4.1f}   {kg:10.0f}")
    lines += ["  silver is the costliest material per gram in the cell;",
              "  thinner fingers, more wires and partial copper cut it, and",
              "  each change moves the grid optimum of lesson A and the",
              "  firing window of lesson B - a BOM change that needs",
              "  re-qualification (lesson C)"]
    emit("t_silver", lines)
    return out


# ------------------------------------------------ two EL graders
def grading(n: int = 300, seed: int = 4115) -> dict[str, float]:
    rng = random.Random(seed)
    true = [rng.choice("A" * 85 + "B" * 12 + "C" * 3) for _ in range(n)]

    def grade(t, p_ok):
        if rng.random() < p_ok:
            return t
        return {"A": "B", "B": rng.choice("AC"), "C": "B"}[t]
    g1 = [grade(t, 0.95) for t in true]
    g2 = [grade(t, 0.85) for t in true]
    cats = "ABC"
    po = sum(a == b for a, b in zip(g1, g2)) / n
    pe = sum((g1.count(c) / n) * (g2.count(c) / n) for c in cats)
    kappa = (po - pe) / (1 - pe)
    per = {}
    for c in cats:
        either = sum(1 for a, b in zip(g1, g2) if c in (a, b))
        both = sum(1 for a, b in zip(g1, g2) if a == b == c)
        per[c] = both / either if either else 1.0
    lines = [f"{n} EL images graded A/B/C by two inspectors (teaching)",
             f"  observed agreement {po:.1%}; by chance {pe:.1%}; kappa "
             f"{kappa:.2f}",
             "  agreement within each grade (both / either called it): " +
             ", ".join(f"{c} {v:.0%}" for c, v in per.items()),
             "  most images are A, so chance agreement is high and a raw",
             f"  agreement of {po:.0%} hides a kappa of only {kappa:.2f}; the "
             "graders",
             f"  agree least on B ({per['B']:.0%}) and C ({per['C']:.0%}), "
             "the grades that sort",
             "  and reject - reference images for each grade and a",
             "  periodic attribute study (ch 40, kappa) keep the graders",
             "  together"]
    emit("t_grading", lines)
    return dict(po=po, kappa=kappa)


# ------------------------------------------------ water through the back
def moisture(wvtr_38: float = 1.5, area: float = 2.58) -> dict[str, float]:
    temps = [12, 15, 20, 26, 31, 35, 37, 36, 32, 25, 18, 13]  # module, C
    out = {}
    lines = ["water vapour through a backsheet over a year (teaching:",
             "  1.5 g/m2/day at 38 C, doubling every 10 K; monthly mean",
             "  module temperature of a hot dry site)",
             "  build                       g a year   in 25 years"]
    g = sum(wvtr_38 * 2 ** ((t - 38) / 10) * area * 30.4 for t in temps)
    out["glass-backsheet"] = g
    out["glass-glass, edge seal"] = g * 0.02
    for name, v in out.items():
        lines.append(f"  {name:26s} {v:9.0f}   {v * 25:9,.0f} g")
    lines += ["  a breathable backsheet lets water in and acetic acid from",
              "  the encapsulant out; glass-glass keeps water out but traps",
              "  what gets in through the edge - which build is safer",
              "  depends on the encapsulant, so the BOM, not one material,",
              "  is qualified (damp heat, lesson C)"]
    emit("t_moisture", lines)
    return out


# ------------------------------------------------ strain each cycle
def strain(length_mm: float = 1.0) -> dict[str, float]:
    a_cu, a_si, a_glass = 17e-6, 2.6e-6, 9e-6
    out = {}
    lines = ["mismatch strain at a ribbon joint (copper on silicon)",
             "  cycle                     dT K   strain %   relative life"]
    base = None
    for name, dt in (("test -40 to 85 C", 125.0), ("hot summer day", 45.0),
                     ("mild day", 25.0)):
        e = (a_cu - a_si) * dt
        base = base or e
        out[name] = e
        lines.append(f"  {name:24s} {dt:5.0f}   {e * 100:8.3f}   "
                     f"{(base / e) ** 2:12.1f}")
    lines += ["  glass (9e-6/K) sits between copper and silicon: the",
              "  laminate bends as well as shears; with a Coffin-Manson",
              "  exponent of 2 a test cycle wears a joint like 8 hot days",
              "  or 25 mild ones - the basis of equation 41.17, and why",
              "  joint shape and solder, not only ribbon size, matter"]
    emit("t_strain", lines)
    return out


# ------------------------------------------------ glass-glass stiffness
def stiffness() -> dict[str, float]:
    t_mono = 3.2
    cases = {"3.2 mm glass + backsheet": t_mono ** 3,
             "2 + 2 mm glass, slipping": 2 * 2.0 ** 3,
             "2 + 2 mm glass, fully bonded": (4.0 + 0.5) ** 3 - 0.5 ** 3}
    mass = {"3.2 mm glass + backsheet": 3.2, "2 + 2 mm glass, slipping": 4.0,
            "2 + 2 mm glass, fully bonded": 4.0}
    lines = ["bending stiffness per width (relative to t^3 of 3.2 mm glass)",
             "  build                          stiffness   glass mm"]
    out = {}
    for name, s in cases.items():
        out[name] = s / cases["3.2 mm glass + backsheet"]
        lines.append(f"  {name:30s} {out[name]:9.2f}   {mass[name]:8.1f}")
    lines += ["  two thin sheets act as one only if the encapsulant grips",
              "  them in shear; it softens when hot, so a glass-glass",
              "  module is stiff on a cold morning and much less so at",
              "  70 C - the mechanical load test is run on the BOM as",
              "  built, and the clamping zones (lesson C) follow it"]
    emit("t_stiffness", lines)
    return out


# ------------------------------------------------ check digits
# [start: luhn]
def luhn_ok(digits: str) -> bool:
    """Luhn check: double every second digit from the right."""
    total = 0
    for k, ch in enumerate(reversed(digits)):
        d = int(ch)
        if k % 2:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0
# [end: luhn]


def check_digit(body: str) -> str:
    for c in "0123456789":
        if luhn_ok(body + c):
            return body + c
    raise ValueError


def serials(seed: int = 4116) -> dict[str, float]:
    rng = random.Random(seed)
    good = [check_digit(f"{rng.randrange(10 ** 8):08d}") for _ in range(2000)]
    single = trans = s_caught = t_caught = 0
    for s in good:
        k = rng.randrange(len(s))
        d = str((int(s[k]) + rng.randrange(1, 10)) % 10)
        single += 1
        s_caught += not luhn_ok(s[:k] + d + s[k + 1:])
        k = rng.randrange(len(s) - 1)
        if s[k] != s[k + 1]:
            trans += 1
            t_caught += not luhn_ok(s[:k] + s[k + 1] + s[k] + s[k + 2:])
    out = dict(single=s_caught / single, trans=t_caught / trans)
    lines = ["serial numbers with a check digit (Luhn), 2,000 keyed at receipt",
             f"  one wrong digit caught: {out['single']:.0%}",
             f"  two neighbours swapped caught: {out['trans']:.0%}",
             "  a scanner rarely errs, a person typing does: the check",
             "  digit stops a mistyped serial from linking a module to",
             "  another module's flash record (lab D), which would make",
             "  a warranty claim argue about the wrong module"]
    emit("t_serials", lines)
    return out


# ------------------------------------------------ where to put the EL
def el_placement(crack: float = 0.006, find: float = 0.95,
                 repair: float = 2.0, scrap: float = 95.0,
                 modules: int = 109200) -> dict[str, float]:
    made = crack * modules
    pre = made * find * repair + made * (1 - find) * find * scrap
    post = made * find * scrap
    lines = [f"cracked strings in {modules:,} modules: {made:,.0f} (teaching "
             f"{crack:.1%})",
             "  EL placed                       cost k u   escapes",
             f"  before lamination, and after     {pre / 1000:7.1f}   "
             f"{made * (1 - find) ** 2:7.1f}",
             f"  after lamination only            {post / 1000:7.1f}   "
             f"{made * (1 - find):7.1f}",
             "  a crack found before lamination costs a string repair; one",
             "  found after costs a scrapped module - the pre-lamination",
             "  image pays for itself many times over, and the final image",
             "  still catches what lamination itself cracks"]
    emit("t_placement", lines)
    return dict(pre=pre, post=post)


# ------------------------------------------------ ribbon peel capability
def peel(seed: int = 4117, lsl: float = 1.0) -> dict[str, float]:
    rng = random.Random(seed)
    shifts = {"stringer 1": [rng.gauss(2.1, 0.30) for _ in range(40)],
              "stringer 2": [rng.gauss(1.6, 0.25) for _ in range(40)]}
    lines = [f"ribbon peel force, N/mm (lower limit {lsl}, teaching)",
             "  machine       mean    sd    Cpk    ppm under"]
    out = {}
    for name, v in shifts.items():
        m, s, _, cpk = qa.cp_cpk(v, lsl, None)
        ppm = qa.ppm_out(m, s, lsl, None)
        out[name] = cpk
        lines.append(f"  {name:12s} {m:5.2f}  {s:5.2f}  {cpk:5.2f}  "
                     f"{ppm:10,.0f}")
    lines += ["  the destructive peel test runs on sample strings each shift;",
              f"  stringer 1 is just capable (Cpk {out['stringer 1']:.2f}); "
              f"stringer 2 (Cpk {out['stringer 2']:.2f})",
              "  makes weak joints in thousands per million because its mean",
              "  is low - the fix is the joint, not more testing, the same",
              "  lesson as the crimp of ch 40"]
    emit("t_peel", lines)
    return out


if __name__ == "__main__":
    trapping()
    silver()
    grading()
    moisture()
    strain()
    stiffness()
    serials()
    el_placement()
    peel()
