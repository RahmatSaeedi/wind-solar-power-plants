"""Chapter 42, an eighth round: where manufacturing tolerances go in the
tip-to-tower clearance, blade frequency as a stiffness check, the gear
contact under the case depth, settling of a flange joint with and without
paint in it, the welds and plates of the tower, and a pressure-decay leak
test corrected for temperature.

Run from the project root:   python -m companion.ch42.examples_y
Writes companion/ch42/expected/y_*.txt and diagrams/data/ch42-contact.csv.
Teaching values (A-453, A-457); relations only, no process recipes.
"""
from __future__ import annotations

import math
import random
from statistics import mean, pstdev

from companion.ch42.common import csv, emit

# ------------------------------------------------ clearance budget
CLEAR0, DEFL = 17.3, 12.1        # m: unloaded clearance, design deflection (ch 11)
TOL = [  # contributor, how it is computed, value used
    ("cap stiffness 3 % low (fibre fraction)", "defl x (1/0.97 - 1)",
     DEFL * (1 / 0.97 - 1)),
    ("prebend 0.15 m short", "as is", 0.15),
    ("blade on the hub 0.15 deg off", "75 m x tan(0.15 deg)",
     75 * math.tan(math.radians(0.15))),
    ("tower top flange 0.10 deg tilted", "75 m x tan(0.10 deg)",
     75 * math.tan(math.radians(0.10))),
]


def clearance() -> dict[str, float]:
    margin = CLEAR0 - DEFL
    worst = sum(v for _, _, v in TOL)
    rss = math.sqrt(sum(v * v for _, _, v in TOL))
    lines = [f"tip-to-tower clearance: {CLEAR0} m unloaded, {DEFL} m design "
             "deflection,",
             f"  margin {margin:.1f} m",
             "  manufacturing contributor               rule                 m"]
    for name, rule, v in TOL:
        lines.append(f"  {name:40s} {rule:20s} {v:4.2f}")
    lines += [f"  all at their limit together {worst:.2f} m "
              f"({worst / margin:.0%} of the margin)",
              f"  root-sum-square {rss:.2f} m ({rss / margin:.0%})",
              "  the 30 % kept in ch 11 is not spare: a part of it is the",
              "  factory's tolerances - which is why the cap's fibre fraction,",
              "  the prebend and the flange angles are measured and recorded"]
    emit("y_clear", lines)
    return dict(margin=margin, worst=worst, rss=rss)


# ------------------------------------------------ frequency as a stiffness check
def frequency(seed: int = 4217, f0: float = 0.75, n: int = 36) -> dict[str, float]:
    rng = random.Random(seed)
    rows, errs, out_band = [], [], 0
    for k in range(n):
        e = rng.gauss(0.0, 0.02)              # stiffness deviation
        m = rng.gauss(0.0, 0.01)              # mass deviation (weighing)
        f = f0 * math.sqrt((1 + e) / (1 + m)) * (1 + rng.gauss(0.0, 0.002))
        e_est = (f / f0) ** 2 * (1 + m) - 1   # frequency + weight -> stiffness
        errs.append(e_est - e)
        out_band += abs(f / f0 - 1) > 0.03
        rows.append((k + 1, round(f, 4), round(100 * e, 2), round(100 * e_est, 2)))
    lines = [f"first flap frequency of {n} blades (nominal {f0} Hz, teaching):",
             "  stiffness sd 2 %, mass sd 1 %, frequency read to 0.2 %",
             f"  frequency spread: sd {pstdev([r[1] for r in rows]) / f0:.2%}; "
             f"outside +-3 %: {out_band}",
             "  stiffness from frequency and weight, E_est = (f/f0)^2 (1+m) - 1:",
             f"  error of the estimate: mean {100 * mean(errs):+.2f} %, "
             f"sd {100 * pstdev(errs):.2f} % (points)",
             "  a frequency test on the stand and the weighing together give",
             "  every blade's stiffness to about half a per cent - a check",
             "  the static test (lesson B) does on one blade only"]
    emit("y_freq", lines)
    return dict(err_sd=100 * pstdev(errs), out=out_band)


# ------------------------------------------------ gear contact under the case
# [start: hertz]
def hertz_line(f_n_mm: float, r_mm: float, e_star: float = 115e3):
    """Line contact of two steel cylinders (Hertz): half width b (mm),
    peak pressure (MPa), depth (mm) and value (MPa) of the largest shear."""
    b = math.sqrt(4 * f_n_mm * r_mm / (math.pi * e_star))
    p = 2 * f_n_mm / (math.pi * b)
    return b, p, 0.786 * b, 0.300 * p


def shear_profile(zeta: float) -> float:
    """Shear under the centre of the contact, as a share of p (z = zeta b)."""
    return zeta - zeta ** 2 / math.sqrt(1 + zeta ** 2)
# [end: hertz]


def contact(f_n_mm: float = 2500.0, r_mm: float = 40.0, k_case: float = 2.5):
    lines = [f"tooth contact as two cylinders: {f_n_mm:.0f} N/mm of face, "
             f"equivalent radius {r_mm:.0f} mm",
             "  load case        b mm   p MPa   shear max at mm   MPa   "
             f"case needed ({k_case} x)"]
    out = {}
    for name, k in (("nominal", 1.0), ("edge load x 1.3", 1.3)):
        b, p, z, tau = hertz_line(k * f_n_mm, r_mm)
        out[name] = k_case * z
        lines.append(f"  {name:15s} {b:5.2f}  {p:6.0f}   {z:15.2f}  {tau:4.0f}"
                     f"   {k_case * z:5.2f} mm")
    b, p, z, _ = hertz_line(f_n_mm, r_mm)
    csv("ch42-contact.csv", "z,tau",
        [(round(zz, 3), round(p * shear_profile(zz / b), 1))
         for zz in [i * 0.05 for i in range(0, 81)]])
    lines += ["  the shear peaks below the surface, not on it: the hard case",
              "  must reach well past that depth or cracks start under it",
              f"  (teaching rule {k_case} x). A misaligned mesh loads one edge -",
              f"  {out['edge load x 1.3']:.2f} mm is needed then, which is "
              "what the 2.4 mm floor of",
              "  lesson C covers; HT-43 at 2.09 mm meets only the nominal case"]
    emit("y_contact", lines)
    return out


# ------------------------------------------------ settling of a flange joint
def settling(d_area_mm2: float = 2676.0, grip_mm: float = 300.0,
             preload_kn: float = 1500.0, kc_ratio: float = 3.0):
    kb = 210e3 * d_area_mm2 / grip_mm / 1e3          # kN/mm
    k = kb * kc_ratio / (1 + kc_ratio)               # preload lost per mm
    out = {}
    lines = [f"tower flange bolt M64 (teaching): grip {grip_mm:.0f} mm, preload "
             f"{preload_kn:.0f} kN",
             f"  bolt stiffness {kb:,.0f} kN/mm; clamped parts {kc_ratio:.0f} x "
             "stiffer",
             f"  preload lost: {k:,.0f} kN per mm of settling",
             "  joint faces                    settling mm   lost kN   share"]
    for name, s in (("bare steel (embedding)", 0.012),
                    ("painted, coating creeps 15 %", 0.012 + 2 * 0.200 * 0.15)):
        lost = k * s
        out[name] = lost / preload_kn
        lines.append(f"  {name:30s} {s:11.3f}   {lost:7.0f}   {lost / preload_kn:5.1%}")
    lines += ["  a few hundredths of a millimetre undo several per cent of the",
              "  preload; paint in the joint multiplies the loss - why the",
              "  faces stay bare (lab D, interface map) and why the bolts are",
              "  re-tensioned after the first months (ch 50)"]
    emit("y_settle", lines)
    return out


# ------------------------------------------------ tower plates and welds
SECTIONS = [(1, 4.50, 4.12, 46, 25.0, 124.0), (2, 4.12, 3.75, 40, 25.0, 96.0),
            (3, 3.75, 3.38, 32, 25.0, 71.0), (4, 3.38, 3.00, 26, 25.0, 50.0)]


def tower_welds(plate_w: float = 3.0, ut_m_h: float = 12.0) -> dict[str, float]:
    lines = [f"tower sections of ch 30 rolled from {plate_w} m plates (teaching)",
             "  sec   cans  shell t  ch 31 t   circ. welds m  long. welds m"]
    tot_c = tot_l = 0.0
    for s, d1, d2, t, length, listed in SECTIONS:
        cans = math.ceil(length / plate_w)
        dm = (d1 + d2) / 2
        shell = math.pi * dm * t / 1000 * length * 7.85
        circ = (cans - 1 + 2) * math.pi * dm      # between cans + two flanges
        tot_c += circ
        tot_l += length
        lines.append(f"  {s:3d}  {cans:5d}  {shell:7.1f}  {listed:7.1f}   "
                     f"{circ:13.0f}  {length:13.0f}")
    total = tot_c + tot_l
    lines += [f"  weld length a tower {total:.0f} m; at {ut_m_h:.0f} m/h of "
              f"ultrasonic scan {total / ut_m_h:.0f} h",
              f"  for 12 towers {12 * total / ut_m_h:,.0f} h",
              "  the shells alone come within 2 t of ch 31's list (which",
              "  rounds and adds the flanges); the",
              "  circumferential welds carry the tower's bending and set its",
              "  fatigue (ch 30, detail category) - their inspection record",
              "  is part of the tower's dossier"]
    emit("y_tower", lines)
    return dict(weld_m=total, ut_h=total / ut_m_h)


# ------------------------------------------------ leak test with temperature
def leak(p0_bar: float = 3.0, t0_c: float = 22.0, t1_c: float = 20.0,
         p1_bar: float = 2.975, limit_mbar: float = 10.0) -> dict[str, float]:
    p_abs0 = p0_bar + 1.013
    p_abs1 = p1_bar + 1.013
    expected = p_abs0 * (t1_c + 273.15) / (t0_c + 273.15)
    raw = 1000 * (p_abs0 - p_abs1)
    corrected = 1000 * (expected - p_abs1)
    lines = ["pressure-decay test of a nacelle cooling circuit (teaching)",
             f"  start {p0_bar} bar gauge at {t0_c} C; after an hour "
             f"{p1_bar} bar at {t1_c} C",
             f"  raw fall {raw:.0f} mbar; the cooling of the gas alone "
             f"explains {1000 * (p_abs0 - expected):.0f} mbar",
             "  (P/T constant; the circuit is tested with gas before filling)",
             f"  corrected fall {corrected:.0f} mbar against a {limit_mbar:.0f} "
             f"mbar limit: {'pass' if corrected <= limit_mbar else 'fail'}",
             "  without the temperature record the circuit would be called",
             "  leaking; with a warming hall a leak could hide - the test",
             "  record carries both readings"]
    emit("y_leak", lines)
    return dict(raw=raw, corrected=corrected)


if __name__ == "__main__":
    clearance()
    frequency()
    contact()
    settling()
    tower_welds()
    leak()
