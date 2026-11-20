"""Chapter 25 - eighth round: the three-winding PV unit transformer
(star equivalent, LV fault, how one LV winding sees a fault on the
other), 30-degree phase shift and the cancellation of locked harmonics,
the off-circuit tap of a PV unit chosen from four operating corners,
furans and the paper's degree of polymerisation, a health index, repair
or replace after a failure, and the carbon of materials against losses.

Run from the project root:   python -m companion.ch25.examples_v
Writes companion/ch25/expected/v_*.txt and diagrams/data/ch25-furan.csv.
Teaching values (A-326..A-330 extended).
"""
from __future__ import annotations

import cmath
import math

from companion.ch25.common import csv, emit


# [start: star]
def star(z12: float, z13: float, z23: float) -> tuple:
    """Star equivalent of a three-winding transformer from the three
    pairwise short-circuit impedances (all on one MVA base)."""
    z1 = (z12 + z13 - z23) / 2
    z2 = (z12 + z23 - z13) / 2
    z3 = (z13 + z23 - z12) / 2
    return z1, z2, z3
# [end: star]


def three_winding() -> None:
    z_h, z_1, z_2 = star(0.060, 0.060, 0.110)
    s_base, v_lv = 5.5e6, 600.0
    i_base = s_base / (math.sqrt(3) * v_lv)
    i_f = 1 / (z_h + z_1)
    v_star = z_1 / (z_h + z_1)
    lines = ["three-winding PV unit transformer: HV 33 kV, LV1 and LV2 0.6 kV,",
             "  2.75 MVA each; tests (on 5.5 MVA): H-L1 6 %, H-L2 6 %, L1-L2 11 %",
             f"  star equivalent: Z_H {z_h:.1%}, Z_L1 {z_1:.1%}, Z_L2 {z_2:.1%}",
             f"  bolted fault on LV1, stiff 33 kV: {i_f:.1f} pu = {i_f * i_base / 1e3:.0f} kA at 0.6 kV",
             f"  voltage left on LV2 during that fault: {v_star:.2f} pu",
             f"  a two-winding 5.5 MVA unit at 6 %: {1 / 0.06:.1f} pu - the same LV fault",
             "  level; but with both inverters on its one LV bus, the bus",
             "  itself is faulted and the second inverter sees 0 pu",
             "  the high L1-L2 impedance keeps one inverter riding through a",
             "  fault on its neighbour's winding and limits what each",
             "  inverter feeds into the other's fault; the price is a",
             "  larger, dearer transformer and two LV boards"]
    emit("v_threewinding", lines)


def cancellation() -> None:
    lines = ["a 30-degree shift between LV1 (star) and LV2 (delta): 5th harmonic",
             "  at HV from two inverters, each 2 % of its own current, locked to it",
             "  case                                   residual % of one group"]
    cases = [("equal load, same harmonic angle", 1.0, 0.0), ("LV2 at half load", 0.5, 0.0),
             ("equal load, 20 deg angle difference", 1.0, 20.0), ("no shift (both star)", 1.0, None)]
    for name, b, delta in cases:
        a = 2.0
        if delta is None:
            res = a + a * b
        else:
            res = abs(a - a * b * cmath.exp(1j * math.radians(delta)))
        lines.append(f"  {name:38s} {res:22.2f}")
    lines += ["  the shift turns the 5th and 7th of one group against the other",
              "  (the 11th and 13th add): only harmonics each inverter makes",
              "  in a fixed relation to its own current cancel; distortion",
              "  driven by the grid's voltage does not - the harmonic study",
              "  (ch 28) uses the makers' measured data, not this ideal"]
    emit("v_cancel", lines)


def lv_voltage(v_hv: float, tap: float, p: float, q: float, r: float = 0.0082,
               x: float = 0.060) -> float:
    """LV voltage (pu of 0.6 kV) of a unit exporting p + jq (pu of 5.5 MVA)
    with the HV at v_hv pu; a + tap lowers the LV (HV-tap convention)."""
    v_ratio = v_hv / (1 + tap)
    v = v_ratio
    for _ in range(20):
        i = complex(p, -q) / v
        v = abs(v_ratio + i * complex(r, x))
    return v


def detc() -> None:
    corners = [("full P, producing Q", 0.909, 0.440, 1.006), ("full P, absorbing Q", 0.909, -0.440, 1.006),
               ("night, producing Q", 0.0, 0.440, 1.000), ("night, absorbing Q", 0.0, -0.440, 1.000)]
    lines = ["off-circuit tap of the PV unit at the end of a feeder (teaching):",
             "  33 kV at the unit 1.006 pu at full output (0.6 % feeder rise), 1.000",
             "  at night; inverter full-Q window 0.95-1.05 pu at its terminals",
             "  corner                    tap -2.5 %  tap 0     tap +2.5 % tap +5 %"]
    worst = {}
    taps = [k / 1000 for k in range(-50, 76, 5)]
    csv("ch25-detc.csv", "tap," + ",".join(f"c{i}" for i in range(4)),
        [(f"{t * 100:.1f}",) + tuple(f"{lv_voltage(v, t, p, q):.4f}" for _, p, q, v in corners)
         for t in taps])
    for name, p, q, v_hv in corners:
        row = []
        for tap in (-0.025, 0.0, 0.025, 0.05):
            v = lv_voltage(v_hv, tap, p, q)
            row.append(v)
            worst.setdefault(tap, []).append(v)
        lines.append(f"  {name:25s} " + "  ".join(f"{v:8.3f}" for v in row))
    ok = [t for t, vs in worst.items() if min(vs) >= 0.95 and max(vs) <= 1.05]
    band = []
    for tap in (-0.025, 0.0, 0.025, 0.05):
        vs = [lv_voltage(v_hv * f, tap, p, q) for _, p, q, v_hv in corners for f in (0.9875, 1.0125)]
        if min(vs) >= 0.95 and max(vs) <= 1.05:
            band.append(tap)
    lo = lv_voltage(1.006 * 1.0125, 0.0, 0.909, 0.440)
    lines += ["  taps that keep all four corners inside: "
              + (", ".join(f"{t * 100:+.1f} %" for t in ok) if ok else "none"),
              "  with the 33 kV bus moving +/- 1.25 % (main tap changer band):",
              "  taps that still hold: "
              + (", ".join(f"{t * 100:+.1f} %" for t in band) if band else "none")
              + f" (tap 0 reaches {lo:.3f})",
              "  producing Q at full power raises the terminal voltage most;",
              "  no fixed tap covers every corner with the bus band, so the",
              "  specification states the corner where full Q is limited",
              "  (or a wider inverter window) - checked in the ch 28 load flow"]
    emit("v_detc", lines)


# [start: furan]
def dp_from_furan(fal_mg_kg: float) -> float:
    """Degree of polymerisation from 2-furaldehyde in oil by the
    Chendong correlation (one published relation, teaching use)."""
    return (1.51 - math.log10(fal_mg_kg)) / 0.0035
# [end: furan]


def furan() -> None:
    pts = [10 ** (k / 10) for k in range(-20, 11)]
    csv("ch25-furan.csv", "fal,dp", [(f"{f:.4f}", f"{dp_from_furan(f):.0f}") for f in pts])
    lines = ["paper age from furans in oil (Chendong correlation, teaching):",
             "  2-FAL mg/kg   DP estimate   reading"]
    for f in (0.05, 0.3, 1.0, 3.0, 6.0):
        dp = dp_from_furan(f)
        if dp > 600:
            note = "paper in good condition"
        elif dp > 400:
            note = "ageing, trend it"
        elif dp > 250:
            note = "advanced ageing, plan"
        else:
            note = "near end of life"
        lines.append(f"  {f:11.2f}   {dp:11.0f}   {note}")
    lines += ["  new paper has a DP near 1,000; around 200 it has lost most of",
              "  its strength - but correlations differ by paper type, oil",
              "  and oil changes; one sample means little, a trend and DGA",
              "  (CO and CO2) together tell the story"]
    emit("v_furan", lines)


def health_index() -> None:
    weights = {"DGA": 0.30, "oil quality": 0.15, "furans": 0.20, "bushings": 0.15,
               "OLTC": 0.10, "load history": 0.10}
    units = {"T1": {"DGA": 1, "oil quality": 1, "furans": 1, "bushings": 2, "OLTC": 1, "load history": 1},
             "T2": {"DGA": 3, "oil quality": 2, "furans": 2, "bushings": 1, "OLTC": 2, "load history": 2}}
    lines = ["a health index from condition scores (1 good ... 4 poor; teaching weights):",
             "  factor         weight   T1   T2"]
    for k, w in weights.items():
        lines.append(f"  {k:14s} {w:6.2f}   {units['T1'][k]:2d}   {units['T2'][k]:2d}")
    for name, s in units.items():
        hi = 100 * (4 - sum(weights[k] * s[k] for k in weights)) / 3
        band = "good" if hi >= 70 else "fair - watch" if hi >= 40 else "poor - act"
        lines.append(f"  {name}: index {hi:5.1f} / 100  {band}")
    lines += ["  the index ranks attention, it does not diagnose: T2's DGA",
              "  score sends it to the expert first; the weights and scoring",
              "  rules are the owner's maintenance policy (ch 52)"]
    emit("v_health", lines)


def repair_replace() -> None:
    month_cost = 310.0        # energy above one unit's rating, from t_staging
    options = [("repair in a factory", 900.0, 8.0, 0.0),
               ("new transformer", 2_000.0, 14.0, 300.0),
               ("pool spare now, repair later", 1_050.0, 1.5, 0.0)]
    lines = ["one main transformer failed: three ways back (teaching, k u)",
             "  option                         cost   months out   energy lost   total"]
    for name, cost, months, credit in options:
        lost = months * month_cost
        lines.append(f"  {name:30s} {cost:5.0f}   {months:10.1f}   {lost:11.0f}   {cost + lost - credit:5.0f}")
    lines += ["  the new unit's total is after a 300 k u credit for its longer",
              "  life; the months out cost more than the hardware - a share in",
              "  a spare pool (ch 18) is worth its fee if failures like this",
              "  are possible at all; the insurer's terms (ch 39) enter too"]
    emit("v_repair", lines)


def carbon() -> None:
    mats = [("core steel", 38.0, 2.5), ("copper", 9.4, 4.0), ("tank and structure steel", 20.0, 2.0),
            ("oil", 19.4, 1.0), ("paper, pressboard, other", 8.2, 1.5)]
    lines = ["carbon of one main transformer: materials against 25 years of losses",
             "  (teaching factors t CO2e per t; grid 0.5 t CO2e per MWh)",
             "  item                         t      factor   t CO2e"]
    tot = 0.0
    for name, t, f in mats:
        tot += t * f
        lines.append(f"  {name:28s} {t:5.1f}   {f:6.1f}   {t * f:6.0f}")
    loss = 1_174.0 / 2 * 25 * 0.5
    lines += [f"  materials {tot:.0f} t CO2e; losses {loss:,.0f} t CO2e over 25 years",
              f"  the losses weigh {loss / tot:.0f} times the materials: lower losses",
              "  are the transformer's main carbon lever, and the loss",
              "  evaluation of lesson A already prices most of it; real",
              "  factors come from the maker's declaration and the grid's"]
    emit("v_carbon", lines)


if __name__ == "__main__":
    three_winding()
    cancellation()
    detc()
    furan()
    health_index()
    repair_replace()
    carbon()
