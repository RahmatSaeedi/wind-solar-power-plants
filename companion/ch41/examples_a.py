"""Chapter 41, lesson A - device principles of the silicon cell at
textbook level: carriers and doping, the junction, lifetime and diffusion
length, surface recombination and the implied open-circuit voltage, the
front-grid trade-off of shading against resistance, the loss budget from
the silicon limit to the cell, process variation and the spread of
efficiency, cell architectures and the temperature coefficient.

Run from the project root:   python -m companion.ch41.examples_a
Writes companion/ch41/expected/a_*.txt and diagrams/data/ch41-*.csv.
Teaching cell of the PVM-550 (A-442): 182 mm wafer, 330 cm2, Voc 0.690 V,
Jsc 41.8 mA/cm2, FF 0.810 - no process settings anywhere.
"""
from __future__ import annotations

import math
import random
from statistics import mean, pstdev

from companion.ch41.common import csv, emit
from plantp import pvfab as fab

Q = 1.602176634e-19
VT300 = 0.025852                 # kT/q at 300 K, V
NI = 9.65e9                      # intrinsic carrier density at 300 K, cm^-3
EPS_SI = 11.7 * 8.854e-14        # F/cm

# [start: cell]
CELL = dict(area_cm2=330.0, voc=0.690, jsc=0.0418, rs=0.64,  # A-442
            rsh=5000.0, w_um=150.0, n_a=1.0e16)
# Jsc in A/cm2; Rs and Rsh in ohm cm2; wafer thickness; base doping
# [end: cell]


# ------------------------------------------------------------- carriers
def carriers() -> dict[str, float]:
    lines = ["carriers in p-type silicon at 300 K (n_i 9.65e9 cm^-3)",
             "  doping N_A cm^-3   holes p     electrons n   resistivity"]
    out = {}
    for na, mu in ((1e15, 460.0), (1e16, 400.0), (1e17, 250.0)):
        n = NI ** 2 / na
        rho = 1 / (Q * na * mu)
        out[na] = rho
        lines.append(f"  {na:12.0e}     {na:9.1e}   {n:11.1e}   "
                     f"{rho:6.2f} ohm cm")
    lines += ["  one boron atom in about five million silicon atoms makes",
              "  the wafer p-type; the electrons (minority carriers) are",
              "  a trillion times fewer, and it is they that the light",
              "  makes and the junction must collect before they recombine",
              "  (hole mobility from textbook tables, teaching values)"]
    emit("a_carriers", lines)
    return out


# ------------------------------------------------------------- junction
def junction() -> dict[float, tuple[float, float]]:
    na = CELL["n_a"]
    lines = ["p-n junction: built-in voltage and depletion width",
             f"  base N_A {na:.0e} cm^-3; emitter N_D varied",
             "  N_D cm^-3   V_bi V   width um   share in the base"]
    out = {}
    for nd in (1e18, 1e19, 1e20):
        vbi = VT300 * math.log(na * nd / NI ** 2)
        w = math.sqrt(2 * EPS_SI * vbi / Q * (1 / na + 1 / nd))
        x_p = w * nd / (na + nd)
        out[nd] = (vbi, w * 1e4)
        lines.append(f"  {nd:8.0e}   {vbi:6.3f}   {w * 1e4:8.3f}   "
                     f"{x_p / w:17.1%}")
    dv = out[1e20][0] - out[1e18][0]
    lines += ["  the field region is a third of a micrometre and lies almost",
              "  wholly in the lightly doped base; an emitter a hundred",
              f"  times heavier adds {dv:.2f} V of built-in voltage but more",
              "  recombination (the trade-off of junction formation, B)"]
    emit("a_junction", lines)
    return out


# --------------------------------------------- lifetime, diffusion length
def diffusion() -> dict[float, float]:
    d_n = VT300 * 1050.0               # cm2/s, electrons, Einstein relation
    w = CELL["w_um"]
    lines = [f"minority electrons: D = kT/q x mu = {d_n:.1f} cm2/s",
             f"  lifetime     diffusion length   against a {w:.0f} um wafer"]
    out = {}
    for tau_us in (1, 10, 100, 1000):
        L = fab.diffusion_length_um(d_n, tau_us * 1e-6)
        out[tau_us] = L
        lines.append(f"  {tau_us:5d} us     {L:9.0f} um          "
                     f"{L / w:5.1f} x thickness")
    lines += ["  an electron made at the back must wander to the junction;",
              "  with 1 us it rarely arrives, with 100 us it crosses the",
              "  wafer several times - a lifetime above about 100 us lets",
              "  the surfaces, not the bulk, decide the losses"]
    emit("a_diffusion", lines)
    return out


# ------------------------------------- surface recombination and implied Voc
# [start: ivoc]
C_P, C_A = 9.9e-32, 1.66e-30     # Auger coefficients, cm^6/s (textbook)


def implied_voc(tau_b_s: float, s_cm_s: float) -> tuple[float, float]:
    """Effective lifetime of a wafer whose two surfaces recombine at S,
    with the bulk and the intrinsic (Auger) recombination, and the implied
    Voc from the excess density dn at open circuit, where everything the
    light makes recombines: dn W = G tau_eff(dn), solved by bisection."""
    w_cm = CELL["w_um"] * 1e-4
    na = CELL["n_a"]
    g = CELL["jsc"] / Q                       # carriers made per cm2 per s

    def tau_eff(dn):
        auger = C_P * na ** 2 + C_A * dn ** 2
        return 1 / (1 / tau_b_s + 2 * s_cm_s / w_cm + auger)

    lo, hi = 1e8, 1e18
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if mid * w_cm < g * tau_eff(mid):
            lo = mid
        else:
            hi = mid
    dn = math.sqrt(lo * hi)
    return tau_eff(dn), VT300 * math.log(dn * (dn + na) / NI ** 2)
# [end: ivoc]


def passivation() -> dict[tuple[float, float], float]:
    lines = ["effective lifetime and implied Voc against surface",
             "  recombination velocity S (both faces, 150 um wafer)",
             "  bulk tau    S cm/s   tau_eff us   implied Voc V"]
    out, rows = {}, []
    for tau_b in (1e-4, 1e-3):
        for s in (1, 10, 100, 1000):
            tau, v = implied_voc(tau_b, s)
            out[(tau_b, s)] = v
            lines.append(f"  {tau_b * 1e6:6.0f} us   {s:6d}   {tau * 1e6:10.1f}"
                         f"   {v:12.3f}")
    for k in range(0, 41):
        s = 10 ** (k / 10)
        rows.append((round(s, 3), round(implied_voc(1e-4, s)[1], 4),
                     round(implied_voc(1e-3, s)[1], 4),
                     round(implied_voc(1e-2, s)[1], 4)))
    csv("ch41-ivoc.csv", "s,tb100us,tb1ms,tb10ms", rows)
    d = out[(1e-3, 10)] - out[(1e-3, 1000)]
    lines += [f"  passivating the faces (1,000 -> 10 cm/s) adds {d * 1000:.0f} mV;",
              "  with a good bulk the surfaces set the voltage, which is",
              "  why every modern cell architecture is a passivation",
              "  story; the implied Voc is an upper bound - contacts and",
              "  the emitter take more before the finished cell's 0.690 V;",
              f"  with a 10 ms bulk and S = 1 cm/s it reaches "
              f"{implied_voc(1e-2, 1)[1]:.3f} V: Auger",
              "  recombination, which no process removes, sets the ceiling"]
    emit("a_passivation", lines)
    return out


# ------------------------------------------- the front grid: shade vs ohms
# [start: grid]
def grid_loss(s_cm: float, w_f: float = 0.003, rho_sheet: float = 120.0,
              b_cm: float = 0.83, r_line: float = 0.67, j_mp: float = 0.0395,
              v_mp: float = 0.58) -> dict[str, float]:
    """Power share lost by a finger spacing s: shading w_f/s, lateral
    flow in the emitter, and the finger's own resistance (fingers of
    length b between wires, r_line ohm/cm)."""
    shade = w_f / s_cm
    emitter = rho_sheet * j_mp * s_cm ** 2 / (12 * v_mp)
    finger = b_cm ** 2 * r_line * j_mp * s_cm / (3 * v_mp)
    return dict(shade=shade, emitter=emitter, finger=finger,
                total=shade + emitter + finger)
# [end: grid]


def grid() -> dict[str, float]:
    rows, best = [], (None, 9.0)
    for k in range(5, 41):
        s = k * 0.01
        g = grid_loss(s)
        rows.append((s * 10, round(g["shade"] * 100, 3),
                     round(g["emitter"] * 100, 3), round(g["finger"] * 100, 3),
                     round(g["total"] * 100, 3)))
        if g["total"] < best[1]:
            best = (s, g["total"])
    csv("ch41-grid.csv", "s_mm,shade,emitter,finger,total", rows)
    s_best = best[0]
    g = grid_loss(s_best)
    hi = grid_loss(s_best, rho_sheet=180.0)
    s_hi = min((k * 0.01 for k in range(5, 41)),
               key=lambda x: grid_loss(x, rho_sheet=180.0)["total"])
    lines = ["front grid: finger spacing against three losses",
             "  (30 um fingers, emitter 120 ohm/sq, fingers 8.3 mm long)",
             f"  best spacing {s_best * 10:.1f} mm: shading {g['shade']:.1%}, "
             f"emitter {g['emitter']:.1%},",
             f"  finger {g['finger']:.1%}; total {g['total']:.1%} of the power",
             f"  a lighter emitter (180 ohm/sq, less recombination) wants "
             f"{s_hi * 10:.1f} mm",
             f"  and loses {grid_loss(s_hi, rho_sheet=180.0)['total']:.1%}: "
             "the emitter, the grid and the voltage",
             "  are designed together; a printing defect that widens the",
             "  fingers or breaks one moves the cell off this optimum"]
    emit("a_grid", lines)
    return dict(s_mm=s_best * 10, total=g["total"], hi=hi["total"])


# ----------------------------------------- from the silicon limit to the cell
# [start: budget]
LIMIT = dict(voc=0.7613, jsc=0.04331, ff=0.8926)   # Richter et al. 2013
JSC_LOSS = [("front reflection", 0.0005), ("metal shading", 0.0006),
            ("escape and incomplete collection", 0.0004)]   # A/cm2, A-442
# [end: budget]


def budget() -> list[tuple[str, float, float]]:
    ff = fab.fill_factor(CELL["voc"], CELL["rs"], CELL["jsc"],
                         rsh_ohm_cm2=CELL["rsh"])
    eta_lim = LIMIT["voc"] * LIMIT["jsc"] * LIMIT["ff"] / 0.1   # of 100 mW/cm2
    steps = [("current: optics and collection",
              CELL["jsc"] / LIMIT["jsc"]),
             ("voltage: recombination", CELL["voc"] / LIMIT["voc"]),
             ("fill factor: resistance, shunt", ff / LIMIT["ff"])]
    lines = [f"from the silicon limit ({eta_lim:.2%} - Richter et al. 2013)"
             " to the cell",
             "  step                                    kept    efficiency"]
    eff = eta_lim
    out = []
    for name, keep in steps:
        eff *= keep
        out.append((name, keep, eff))
        lines.append(f"  {name:38s} {keep:6.3f}   {eff:9.2%}")
    lines.append("  the current loss of "
                 f"{(LIMIT['jsc'] - CELL['jsc']) * 1000:.1f} mA/cm2 split:")
    for name, dj in JSC_LOSS:
        lines.append(f"    {name:34s} {dj * 1000:.1f} mA/cm2")
    lines += [f"  cell: {CELL['voc']:.3f} V x {CELL['jsc'] * 1000:.1f} mA/cm2 x "
              f"{ff:.3f} = {eff:.2%}; {eff * CELL['area_cm2'] / 10:.2f} W",
              "  each step is owned by a process: texture and coating the",
              "  current, passivation the voltage, metallisation and firing",
              "  the fill factor (lesson B)"]
    emit("a_budget", lines)
    return out


# ------------------------------------------- process variation -> spread
def cell_eta(jsc, j0, rs, rsh) -> float:
    voc = fab.voc(jsc, j0)
    ff = fab.fill_factor(voc, rs, jsc, rsh_ohm_cm2=rsh)
    return voc * jsc * ff / 0.1              # efficiency at 100 mW/cm2


def sample(rng, vary=("jsc", "j0", "rs", "rsh")):
    jsc = rng.gauss(0.0418, 0.00025) if "jsc" in vary else 0.0418
    j0 = 9.1e-14 * math.exp(rng.gauss(0, 0.25)) if "j0" in vary else 9.1e-14
    rs = max(0.2, rng.gauss(0.64, 0.08)) if "rs" in vary else 0.64
    if "rsh" in vary:
        rsh = 300.0 if rng.random() < 0.02 else 5000.0 * math.exp(
            rng.gauss(0, 0.3))
    else:
        rsh = 5000.0
    return cell_eta(jsc, j0, rs, rsh)


def variation(n: int = 20000, seed: int = 4101) -> dict[str, float]:
    rng = random.Random(seed)
    eta = [sample(rng) for _ in range(n)]
    m, sd = mean(eta), pstdev(eta)
    shares = {}
    for p in ("jsc", "j0", "rs", "rsh"):
        r = random.Random(seed + 1)
        shares[p] = pstdev([sample(r, (p,)) for _ in range(n)]) ** 2
    tot = sum(shares.values())
    lo = sorted(eta)[int(0.01 * n)]
    edges = [0.220 + 0.0005 * k for k in range(0, 61)]
    counts = [sum(edges[k] <= x < edges[k + 1] for x in eta)
              for k in range(len(edges) - 1)]
    csv("ch41-spread.csv", "lo,count",
        [(round(e * 100, 3), c) for e, c in zip(edges[:-1], counts)])
    lines = [f"process variation of {n:,} teaching cells (A-442)",
             "  Jsc sd 0.6 %, J0 lognormal sd 25 %, Rs sd 0.08 ohm cm2,",
             "  shunt lognormal, 2 % of cells shunted (300 ohm cm2)",
             f"  efficiency mean {m:.2%}, sd {sd:.2%}; 1st percentile {lo:.2%}",
             "  share of the variance from each parameter alone:"]
    names = {"jsc": "current (optics)", "j0": "recombination (J0)",
             "rs": "series resistance", "rsh": "shunts"}
    for p, v in sorted(shares.items(), key=lambda t: -t[1]):
        lines.append(f"    {names[p]:22s} {v / tot:6.0%}")
    lines += ["  the shunted 2 % form a separate tail: they are found by",
              "  sorting (low-light test, EL) and must not be mixed into",
              "  strings - the rest of the spread is binned by current"]
    emit("a_variation", lines)
    return dict(mean=m, sd=sd, p1=lo, **{k: v / tot for k, v in
                                          shares.items()})


# ------------------------------------------------ cell architectures
ARCH = [  # name, what it adds, rough production efficiency %, bifaciality
    ("Al-BSF", "aluminium rear: simple, high recombination",
     "~20", "none"),
    ("PERC", "passivated rear with local contacts", "~22-23", "~0.70"),
    ("TOPCon", "tunnel oxide + doped poly-Si contact",
     "~24-25", "~0.80"),
    ("HJT", "thin amorphous-Si layers on both faces", "~24-25", "~0.85+"),
    ("IBC", "all contacts at the back, no front shading", "~24-26", "low"),
]


def architectures() -> None:
    lines = ["cell architectures as passivation steps (rough teaching ranges,",
             "  A-442; makers' data sheets decide)",
             "  type    what it adds                                 eta %"
             "   bifacial"]
    for name, adds, eta, bif in ARCH:
        lines.append(f"  {name:6s}  {adds:44s} {eta:7s} {bif}")
    lines += ["  each step cuts recombination at one more surface or",
              "  contact (lesson A, passivation): the voltage rises, and",
              "  with it the temperature coefficient improves"]
    emit("a_arch", lines)


# ------------------------------------------------ temperature coefficient
def tempco() -> dict[float, float]:
    eg0, gamma, t = 1.206, 3.0, 298.15
    lines = ["Voc temperature coefficient from the diode law:",
             "  dVoc/dT = -(Eg0/q - Voc + gamma kT/q) / T, Eg0 1.206 V, gamma 3",
             "  cell Voc V   dVoc/dT mV/K   per cent per K"]
    out = {}
    for v in (0.62, 0.69, 0.74):
        d = (eg0 - v + gamma * VT300 * t / 300) / t
        out[v] = -d / v * 100
        lines.append(f"  {v:9.3f}   {-d * 1000:12.2f}   {out[v]:12.3f}")
    lines += ["  the PVM-550 data sheet gives -0.27 %/K for the module's",
              f"  Voc; the 0.690 V cell gives {out[0.69]:.3f} %/K: the same",
              "  physics - a higher Voc loses less per kelvin, worth about",
              f"  {abs(out[0.74] - out[0.62]) * 40:.1f} % of Voc at a 65 C cell "
              "between the 0.62 and 0.74 V cells"]
    emit("a_tempco", lines)
    return out


if __name__ == "__main__":
    carriers()
    junction()
    diffusion()
    passivation()
    grid()
    budget()
    variation()
    architectures()
    tempco()
