"""Chapter 4, sections C and D — material and process selection, and from design intent to
an inspected product: indices, conductors, a selection matrix, welding, curing, process
cost, fits, surface roughness, process capability, control charts and detection.

Run from the project root:   python -m companion.ch04.examples_cd
Writes companion/ch04/expected/c_*.txt, d_*.txt and diagrams/data/ch04-*.csv.
Property values are INDICATIVE (A-059): real selection uses certified supplier data.
Money is in fictional units (A-060).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch04.common import csv, emit
from plantp import materials as mt

# name: (E GPa, density kg/m3, strength MPa) -- indicative teaching values (A-059)
MATERIALS = {
    "structural steel": (210, 7850, 355),
    "aluminium alloy": (70, 2700, 260),
    "GFRP (along fibres)": (42, 1950, 900),
    "CFRP (along fibres)": (135, 1550, 1500),
    "spruce (along grain)": (11, 450, 60),
    "concrete (tension)": (32, 2400, 3),
}


def indices() -> None:
    lines = ["material indices in SI units (bigger is better; indicative data, A-059):",
             "  material               E/rho (x 1e6)  E^0.5/rho  sigma^(2/3)/rho"]
    for name, (e, rho, s) in MATERIALS.items():
        lines.append(f"  {name:22s} {e * 1e9 / rho / 1e6:11.1f}  {math.sqrt(e * 1e9) / rho:9.1f}"
                     f"  {(s * 1e6) ** (2 / 3) / rho:13.1f}")
    lines += ["  tie of given stiffness: E/rho; beam of given stiffness: E^0.5/rho;",
              "  beam of given strength: sigma^(2/3)/rho (minimum mass in each case)",
              "  steel and aluminium tie on E/rho; for bending, lighter and fatter wins"]
    emit("c_index", lines)
    csv("ch04-ashby.csv", "rho,e,label", [(rho, e, i) for i, (e, rho, _) in enumerate(MATERIALS.values())])


def conductors() -> None:
    rho_cu, rho_al = 1.72e-8, 2.82e-8
    d_cu, d_al = 8960, 2700
    ratio = rho_al / rho_cu
    price_cu, price_al = 9.0, 2.6                    # per kg, fictional (A-060)
    mass_ratio = ratio * d_al / d_cu
    emit("c_conductor", [
        "aluminium instead of copper for the same resistance per metre:",
        f"  area x {ratio:.2f}, diameter x {math.sqrt(ratio):.2f}, mass x {mass_ratio:.3f}",
        f"  metal cost x {mass_ratio * price_al / price_cu:.2f} (prices 9.0 and 2.6 units/kg, A-060)",
        "  but: a fatter conductor needs more insulation, screen and sheath; aluminium",
        "    creeps under bolts and grows an oxide skin, so terminations need care",
        f"  a 240 mm2 Al conductor matches about {240 / ratio:.0f} mm2 of copper",
    ])
    roles = {
        "MV cable conductor": (["Al", "Cu"], ["cost", "mass", "jointing", "size"],
                               [0.4, 0.2, 0.25, 0.15], [[5, 5, 3, 3], [2, 2, 5, 5]]),
        "cable insulation": (["XLPE", "EPR", "PVC"], ["dielectric loss", "max temp",
                                                     "cost", "flexibility"],
                             [0.35, 0.3, 0.2, 0.15], [[5, 4, 4, 3], [3, 4, 3, 5], [1, 2, 5, 4]]),
        "PV pile in corrosive soil": (["HDG steel", "thicker HDG", "stainless"],
                                      ["strength", "corrosion life", "cost", "supply"],
                                      [0.3, 0.35, 0.25, 0.1], [[4, 2, 5, 5], [4, 4, 4, 4], [4, 5, 1, 2]]),
        "fasteners near the coast": (["HDG", "stainless A4", "zinc-flake"],
                                     ["corrosion", "galling risk", "cost", "preload control"],
                                     [0.4, 0.2, 0.2, 0.2], [[3, 5, 4, 3], [5, 2, 2, 3], [4, 4, 3, 4]]),
    }
    lines = ["weighted selection, scores 1 (poor) .. 5 (good), weights sum to 1 (A-059):"]
    for role, (opts, crit, w, mat) in roles.items():
        sc_ = mt.weighted_scores(mat, w)
        best = opts[int(np.argmax(sc_))]
        lines.append(f"  {role}: " + ", ".join(f"{o} {s:.2f}" for o, s in zip(opts, sc_))
                     + f" -> {best}")
        lines.append(f"    criteria {', '.join(crit)}; weights {', '.join(f'{x:.2f}' for x in w)}")
    lines.append("  scores are judgements: record who scored, on what evidence, and test")
    lines.append("    whether the winner changes when a weight moves by 0.1")
    emit("c_select", lines)


def processes() -> None:
    saw = mt.weld_heat_input(32, 650, 8.0, 1.0)
    mag = mt.weld_heat_input(25, 220, 4.0, 0.8)
    emit("c_weld", [
        "heat input Q = eta V I / v (assumed parameters):",
        f"  submerged arc, tower plate seam: 32 V, 650 A, 8 mm/s, eta 1.0 -> {saw:.2f} kJ/mm",
        f"  gas-shielded wire, bracket fillet: 25 V, 220 A, 4 mm/s, eta 0.8 -> {mag:.2f} kJ/mm",
        "  more heat input: slower cooling, larger heat-affected zone, possible loss of",
        "    toughness; qualified procedures fix the window (chapters 42 and 47)",
    ])
    ea = 60e3                                         # assumed resin activation energy
    lines = ["resin cure, time to the same degree of cure (Arrhenius, Ea 60 kJ/mol assumed):"]
    for t_c in (50, 60, 70, 80, 90):
        lines.append(f"  {t_c:3d} C: {8.0 / mt.arrhenius_factor(ea, 70, t_c):5.1f} h "
                     "(8 h at 70 C as reference)")
    lines.append("  thick laminates heat themselves while curing (exotherm): the core can")
    lines.append("    run far hotter than the mould, so curing is controlled, not just timed")
    emit("c_cure", lines)
    mach = (4.0, 60.0, 0.25, 0.0)                     # material, rate/h, hours, tooling
    mold = (0.8, 80.0, 0.01, 25_000.0)
    n_be = mt.break_even_volume(mach, mold)
    lines = ["connector housing: machining vs injection moulding (fictional costs, A-060)",
             f"  machining:  {mach[0]} + {mach[1]} x {mach[2]} h = "
             f"{mach[0] + mach[1] * mach[2]:.2f} per part, no tooling",
             f"  moulding:   {mold[0]} + {mold[1]} x {mold[2]} h = "
             f"{mold[0] + mold[1] * mold[2]:.2f} per part + tool {mold[3]:,.0f}",
             f"  break-even volume {n_be:,.0f} parts"]
    for n_ in (100, 1000, 10_000):
        lines.append(f"  {n_:6,d} parts: machining {float(mt.cost_per_part(n_, *mach)):6.2f}, "
                     f"moulding {float(mt.cost_per_part(n_, *mold)):6.2f} per part")
    emit("c_cost", lines)
    vols = np.logspace(1, 5, 41)
    csv("ch04-cost.csv", "n,mach,mold",
        [(f"{v:.1f}", f"{float(mt.cost_per_part(v, *mach)):.3f}",
          (f"{float(mt.cost_per_part(v, *mold)):.3f}"
           if float(mt.cost_per_part(v, *mold)) < 200 else "nan")) for v in vols])


def fits_and_surfaces() -> None:
    cases = [("M36 bolt in a 39 mm flange hole", (39.000, 39.620), (35.380, 36.000)),
             ("bearing seat (shaft pressed in)", (600.000, 600.070), (600.080, 600.124)),
             ("locating pin", (20.000, 20.021), (20.002, 20.015))]
    lines = ["hole and shaft limits (mm, assumed) and the resulting fit:"]
    for name, hole, shaft in cases:
        cmin, cmax, kind = mt.fit_limits(hole, shaft)
        lines.append(f"  {name}: clearance {cmin:+.3f} .. {cmax:+.3f} mm -> {kind}")
    lines += ["  two flanges, each hole position within 0.5 mm of nominal: the holes may",
              "    disagree by up to 1.0 mm; the 3.0 mm minimum clearance still passes",
              "    the bolt (a worst-case stack, chapter 2)"]
    emit("d_fit", lines)
    x = np.arange(0, 4.0, 0.001)                     # mm
    rng = np.random.default_rng(20260301)
    z = 2.0 * np.sin(2 * math.pi * x / 0.25) + rng.normal(0, 0.5, x.size)
    ra, rq = mt.roughness(z)
    ra_sine = 2 * 2.0 / math.pi
    emit("d_rough", [
        "synthetic profile: 2 micrometre sine of 0.25 mm wavelength plus 0.5 micrometre noise",
        f"  Ra = mean |z| = {ra:.2f} micrometre; Rq = rms = {rq:.2f} micrometre",
        f"  pure sine: Ra = 2A/pi = {ra_sine:.2f}, Rq = A/sqrt(2) = {2 / math.sqrt(2):.2f}",
        "  very different surfaces can share one Ra value: a drawing states the",
        "    parameter, the filter and the evaluation length together",
    ])
    csv("ch04-profile.csv", "x,z", [(f"{a:.3f}", f"{b:.3f}") for a, b in zip(x[:1000:4], z[:1000:4])])


def capability_and_detection() -> None:
    rng = np.random.default_rng(20260302)
    target, tol = 475.0, 47.5                        # bolt preload kN, +-10 % (A-060)
    data = rng.normal(480.0, 13.0, (25, 5))
    data[18:] += 15.0                                 # a shift after subgroup 18
    cp, cpk, ppm = mt.capability(data[:18].ravel(), target - tol, target + tol)
    cp2, cpk2, ppm2 = mt.capability(data[18:].ravel(), target - tol, target + tol)
    xbar, r = data.mean(axis=1), np.ptp(data, axis=1)
    xbb, rbar = xbar[:18].mean(), r[:18].mean()
    ucl, lcl = xbb + 0.577 * rbar, xbb - 0.577 * rbar
    out = [i + 1 for i, v in enumerate(xbar) if v > ucl or v < lcl]
    emit("d_capability", [
        "bolt preload measured on 25 subgroups of 5 bolts (kN; synthetic, A-060)",
        f"  specification 475 +- 47.5 kN; first 18 subgroups: Cp {cp:.2f}, Cpk {cpk:.2f}, "
        f"expected {ppm:.0f} ppm outside",
        f"  last 7 subgroups (mean moved +15 kN): Cp {cp2:.2f}, Cpk {cpk2:.2f}, {ppm2:,.0f} ppm",
        f"  X-bar chart from the first 18: centre {xbb:.1f}, limits {lcl:.1f} .. {ucl:.1f} "
        "(A2 = 0.577 for n = 5)",
        f"  subgroups outside the limits: {', '.join(map(str, out)) if out else 'none'}",
        "  Cp ignores where the mean is; Cpk punishes an off-centre process",
    ])
    csv("ch04-xbar.csv", "k,xbar", [(i + 1, f"{v:.2f}") for i, v in enumerate(xbar)])
    csv("ch04-xbar-lim.csv", "k,ucl,cl,lcl", [(k, f"{ucl:.2f}", f"{xbb:.2f}", f"{lcl:.2f}") for k in (0.5, 25.5)])
    a50, s_ln = 1.5, 0.4                              # probability of detection, assumed
    a90 = a50 * math.exp(s_ln * math.log(9))
    emit("d_pod", [
        "probability of detection POD(a) = 1 / (1 + exp(-(ln a - ln a50) / s)) (assumed)",
        f"  a50 = {a50} mm, s = {s_ln}: a90 = a50 exp(s ln 9) = {a90:.2f} mm",
        f"  a crack of 1 mm is found with probability {1 / (1 + math.exp(-(math.log(1) - math.log(a50)) / s_ln)):.2f}",
        "  compared with the critical cracks of b_fracture (5.7 .. 63 mm), a90 leaves a",
        "    margin for growth between inspections; for the 5.7 mm case the margin is thin",
    ])
    aa = np.linspace(0.2, 6, 59)
    csv("ch04-pod.csv", "a,pod", [(f"{a:.2f}", f"{1 / (1 + math.exp(-(math.log(a) - math.log(a50)) / s_ln)):.4f}")
                                  for a in aa])


def main() -> None:
    indices()
    conductors()
    processes()
    fits_and_surfaces()
    capability_and_detection()


if __name__ == "__main__":
    main()
