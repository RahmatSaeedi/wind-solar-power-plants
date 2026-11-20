"""Chapter 42, lesson B - blade, hub and pitch manufacture at textbook
level: fibre fraction against the caps of ch 11, voids from density,
glass or carbon caps, degree of cure and glass transition from DSC
samples (no cure schedule), bond-line inspection by probability of
detection, lightning down-conductor checks, matching blades into sets,
hub casting indications by zone, a bearing shrink fit, and cast against
fabricated hubs.

Run from the project root:   python -m companion.ch42.examples_b
Writes companion/ch42/expected/b_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-451, A-452).
"""
from __future__ import annotations

import math
import random
from statistics import mean

from companion.ch42 import sources as src
from companion.ch42.common import csv, emit
from plantp import materials as mt
from plantp import turbinemfg as tm

GLASS, CARBON = src.FIBRES["E-glass"], src.FIBRES["carbon (standard modulus)"]
RES = src.RESIN


# ------------------------------------------------ fibre fraction
def fibre_fraction() -> dict[str, float]:
    lines = ["spar-cap glass laminate: stiffness against fibre fraction",
             "  (rule of mixtures of ch 4; the ch 11 caps assume 45 GPa)",
             "  fibre mass %   V_f     E along GPa   cap thickness for equal EI"]
    out = {}
    target = 45.0
    for w in (0.65, 0.70, 0.75):
        vf = tm.fibre_volume(w, GLASS["rho"], RES["rho"])
        e, _ = mt.rule_of_mixtures(GLASS["e_gpa"], RES["e_gpa"], vf)
        out[w] = (vf, e)
        lines.append(f"  {w:12.0%}   {vf:5.3f}   {e:11.1f}   {target / e:24.0%}")
    vf_need = (target - RES["e_gpa"]) / (GLASS["e_gpa"] - RES["e_gpa"])
    csv("ch42-fibre.csv", "vf,glass,carbon",
        [(round(v / 100, 2),
          round(mt.rule_of_mixtures(GLASS["e_gpa"], RES["e_gpa"], v / 100)[0], 2),
          round(mt.rule_of_mixtures(CARBON["e_gpa"], RES["e_gpa"], v / 100)[0], 2))
         for v in range(40, 71)])
    lines += [f"  45 GPa needs V_f {vf_need:.3f}: a few points of resin more or",
              "  less move the cap's stiffness by several per cent, and",
              "  stiffness, not strength, keeps the tip off the tower",
              "  (ch 11) - fibre fraction is a controlled characteristic,",
              "  checked by burn-off or density on coupons of every cap"]
    emit("b_fibre", lines)
    return dict(vf_need=vf_need, **{str(k): v for k, v in out.items()})


# ------------------------------------------------ voids from density
def voids(seed: int = 4202, limit: float = 0.02) -> dict[str, float]:
    rng = random.Random(seed)
    w = 0.70
    rho_th = 1 / (w / GLASS["rho"] + (1 - w) / RES["rho"])
    coupons = [rho_th * (1 - abs(rng.gauss(0.008, 0.005))) for _ in range(11)]
    coupons.append(rho_th * (1 - 0.034))                  # one dry zone
    vc = [tm.void_content(r, w, GLASS["rho"], RES["rho"]) for r in coupons]
    bad = [k + 1 for k, v in enumerate(vc) if v > limit]
    lines = [f"void content of 12 cap coupons from density (void-free "
             f"{rho_th:.3f} g/cm3)",
             "  coupon  " + " ".join(f"{k + 1:5d}" for k in range(6)),
             "  voids % " + " ".join(f"{100 * v:5.1f}" for v in vc[:6]),
             "  coupon  " + " ".join(f"{k + 1:5d}" for k in range(6, 12)),
             "  voids % " + " ".join(f"{100 * v:5.1f}" for v in vc[6:]),
             f"  above the teaching limit {limit:.0%}: coupon(s) {bad}",
             "  voids cut the resin-dominated strengths (shear between",
             "  plies) first; a coupon over the limit points at a zone of",
             "  the infusion that did not fill - the cap is scanned there",
             "  (lesson B, POD) before any decision"]
    emit("b_voids", lines)
    return dict(bad=len(bad), worst=max(vc))


# ------------------------------------------------ glass or carbon caps
def caps(price_glass: float = 1.0, price_carbon: float = 8.0):
    eg, _ = mt.rule_of_mixtures(GLASS["e_gpa"], RES["e_gpa"], 0.60)
    ec, _ = mt.rule_of_mixtures(CARBON["e_gpa"], RES["e_gpa"], 0.60)
    rg = 0.60 * GLASS["rho"] + 0.40 * RES["rho"]
    rc = 0.60 * CARBON["rho"] + 0.40 * RES["rho"]
    m_ratio = (rc / ec) / (rg / eg)
    cap_glass_t = 7.9                                   # ch 11, two caps
    m_carbon = cap_glass_t * m_ratio
    c_ratio = m_ratio * price_carbon / price_glass
    lines = ["spar caps for the same bending stiffness: glass or carbon",
             f"  E along (V_f 0.60): glass {eg:.0f} GPa, carbon {ec:.0f} GPa",
             f"  mass for equal EI: carbon {m_ratio:.2f} x glass -> "
             f"{m_carbon:.1f} t instead of {cap_glass_t} t",
             f"  material cost at {price_carbon:.0f} x the price a kg: "
             f"{c_ratio:.1f} x the glass caps",
             "  lighter caps cut the blade's gravity moment and the whole",
             "  turbine's loads; carbon also conducts, so the caps join",
             "  the lightning system (lesson B, down conductors) - a",
             "  material choice that reaches three other subsystems"]
    emit("b_caps", lines)
    return dict(m_ratio=m_ratio, m_carbon=m_carbon, c_ratio=c_ratio)


# ------------------------------------------------ degree of cure, Tg
def cure(seed: int = 4203, tg0: float = -20.0, tg1: float = 85.0,
         need: float = 0.95, t_service: float = 60.0):
    rng = random.Random(seed)
    h_total = 420.0                                     # J/g, teaching
    samples = {f"S{k + 1}": max(0.0, rng.gauss(10.0, 6.0)) for k in range(8)}
    samples["S9"] = 46.0                                # under-cured zone
    out = {}
    lines = ["degree of cure from DSC residual heat (teaching resin, total "
             f"{h_total:.0f} J/g)",
             "  Tg estimated linearly between uncured and fully cured",
             "  sample  residual J/g   cure    Tg C   margin over 60 C"]
    for name, h in samples.items():
        a = 1 - h / h_total
        tg = tg0 + (tg1 - tg0) * a
        out[name] = (a, tg)
        lines.append(f"  {name:6s}  {h:12.1f}   {a:5.3f}   {tg:5.1f}   "
                     f"{tg - t_service:+16.1f}")
    low = [k for k, (a, _) in out.items() if a < need]
    lines += [f"  below {need:.0%} cure: {low}",
              "  an under-cured laminate softens near its service",
              "  temperature: the sample's place in the mould is found and",
              "  the cure record of that zone reviewed - cure is controlled",
              "  by the maker's qualified cycle; this lesson reads its",
              "  evidence, never its settings"]
    emit("b_cure", lines)
    return dict(low=low, s9=out["S9"])


# ------------------------------------------------ bond-line inspection
def bondline(a50: float = 20.0, beta: float = 0.45):
    sizes = [10, 20, 40, 60, 100]
    p = tm.pod(sizes, a50, beta)
    two = 1 - (1 - p) ** 2
    rows = [(a, round(float(tm.pod(a, a50, beta)[0]), 4))
            for a in range(5, 151, 5)]
    csv("ch42-pod.csv", "a,pod", rows)
    a90 = a50 * math.exp(1.2816 * beta)
    lines = ["ultrasonic scan of the web bond line: probability of detecting",
             f"  a disbond (log-normal POD, a50 {a50:.0f} mm, beta {beta})",
             "  disbond mm   POD one scan   two independent scans"]
    for a, x, y in zip(sizes, p, two):
        lines.append(f"  {a:11d}   {x:12.0%}   {y:21.0%}")
    lines += [f"  a90 = {a90:.0f} mm: the size found nine times in ten",
              "  the design must tolerate a flaw just below the size the",
              "  inspection reliably finds; POD is measured on panels with",
              "  known flaws - a method's claim without it is a hope"]
    emit("b_pod", lines)
    return dict(a90=a90)


# ------------------------------------------------ lightning conductors
def lightning(seed: int = 4204, limit_mohm: float = 50.0):
    rng = random.Random(seed)
    readings = {f"R{k + 1}": abs(rng.gauss(18.0, 4.0)) for k in range(6)}
    readings["R4"] = 420.0                               # a cracked joint
    bad = [k for k, v in readings.items() if v > limit_mohm]
    lines = ["receptor to root resistance of one blade, milliohm (teaching",
             f"  limit {limit_mohm:.0f}): " + ", ".join(
                 f"{k} {v:.0f}" for k, v in readings.items()),
             f"  above the limit: {bad}",
             "  a high reading is a broken or loose conductor joint, not",
             "  a material property: the strike would arc inside the",
             "  shell; the check is a factory release item and is",
             "  repeated after transport and installation (IEC 61400-24)"]
    emit("b_lightning", lines)
    return dict(bad=len(bad))


# ------------------------------------------------ matching blade sets
def matching(seed: int = 4205, n: int = 36):
    rng = random.Random(seed)
    moments = [rng.gauss(484.0, 2.5) for _ in range(n)]   # t m (ch 11)
    rnd = list(range(n))
    rng.shuffle(rnd)
    random_sets = [rnd[i:i + 3] for i in range(0, n, 3)]
    sorted_sets = tm.match_sets(moments)
    u_rnd = mean(tm.set_unbalance([moments[k] for k in s]) for s in random_sets)
    u_srt = mean(tm.set_unbalance([moments[k] for k in s]) for s in sorted_sets)
    six = moments[:6]
    best6 = tm.best_sets_bruteforce(six)
    by_sort = sum(tm.set_unbalance([six[k] for k in s])
                  for s in tm.match_sets(six))
    lines = [f"{n} blades weighed: first mass moments {min(moments):.1f} to "
             f"{max(moments):.1f} t m",
             f"  mean residual unbalance, sets taken at random  {u_rnd:.2f} t m",
             f"  sets of neighbours after sorting               {u_srt:.2f} t m",
             f"  check on six blades: sorting {by_sort:.2f}, best of all "
             f"partitions {best6:.2f} t m",
             "  sorting by moment matches the best here and needs no search;",
             "  what is left is removed with balance mass at the root -",
             "  each blade's moment and set number go on its record so a",
             "  replacement blade can be matched later (ch 11, balance)"]
    emit("b_match", lines)
    return dict(random=u_rnd, sorted=u_srt, best6=best6, sort6=by_sort)


# ------------------------------------------------ hub casting indications
ZONES = {"flange (high stress)": 3.0, "body (medium)": 6.0,
         "web (low)": 10.0}                               # mm, teaching


def casting(seed: int = 4206):
    rng = random.Random(seed)
    zones = list(ZONES)
    inds = [(rng.choice(zones), round(abs(rng.gauss(2.5, 1.8)), 1))
            for _ in range(14)]
    inds.append(("flange (high stress)", 4.6))
    rej = [(z, s) for z, s in inds if s > ZONES[z]]
    lines = ["ultrasonic indications in hub casting H-022, equivalent size mm",
             "  zone limits (teaching):",
             *[f"    {z:22s} {v:4.0f} mm" for z, v in ZONES.items()],
             f"  {len(inds)} indications; over the zone limit:",
             *[f"    {s} mm in the {z.split(' (')[0]}" for z, s in rej],
             "  the same flaw is harmless in the web and rejectable in the",
             "  flange: acceptance follows the stress map of the design,",
             "  which the casting drawing carries as zones - a repair by",
             "  welding a ductile-iron flange is normally not allowed, so",
             "  the disposition is the designer's (NCR-103, lab D)"]
    emit("b_casting", lines)
    return dict(n=len(inds), rejected=len(rej))


# ------------------------------------------------ bearing shrink fit
def shrink(d_m: float = 0.90, interference_mm: float = 0.30,
           clearance_mm: float = 0.20, ambient: float = 20.0):
    dt = tm.shrink_delta_t(interference_mm / 1000, d_m, 12e-6,
                           clearance_mm / 1000)
    lines = [f"main-bearing inner ring on a {d_m:.2f} m shaft (teaching fit)",
             f"  interference {interference_mm} mm plus {clearance_mm} mm to "
             "slide it on",
             f"  ring heated by {dt:.0f} K: about {ambient + dt:.0f} C",
             "  the fit holds the ring against creep under load; heating,",
             "  not force, mounts it - the maker of the bearing gives the",
             "  allowed temperature and method, and the fit is checked by",
             "  measuring both diameters at the same temperature first"]
    emit("b_shrink", lines)
    return dict(dt=dt)


# ------------------------------------------------ cast or fabricated hub
def hub_route():
    cast = (18.0, 0.06, 120.0, 900.0)      # k u material, rate, h, tooling
    fab = (24.0, 0.06, 420.0, 60.0)
    be = mt.break_even_volume(cast, fab)
    lines = ["hub: casting against a welded fabrication (teaching k u)",
             "  route        material   hours   tooling   per hub at 12 / 200",
             ]
    for name, r in (("cast", cast), ("fabricated", fab)):
        c12 = float(mt.cost_per_part(12, *r))
        c200 = float(mt.cost_per_part(200, *r))
        lines.append(f"  {name:12s} {r[0]:8.0f}   {r[2]:5.0f}   {r[3]:7.0f}"
                     f"   {c12:6.1f} / {c200:5.1f}")
    lines += [f"  break-even at {be:.0f} hubs: a serial turbine is cast; a",
              "  prototype or a very small series may be fabricated - but a",
              "  fabricated hub has welds in the load path and a fatigue",
              "  design of its own (ch 30, weld details)"]
    emit("b_hub", lines)
    return dict(be=be)


if __name__ == "__main__":
    fibre_fraction()
    voids()
    caps()
    cure()
    bondline()
    lightning()
    matching()
    casting()
    shrink()
    hub_route()
