"""Chapter 43, lesson C: factory route and test evidence - core joints and
the magnetising current, water in the oil before filling, the ratio test
read against the tap design, losses corrected for waveform and
temperature, the heat run read from the cooling curve, sound power and
the gases before and after the heat run.

Run from the project root:   python -m companion.ch43.examples_c
Writes companion/ch43/expected/c_*.txt and diagrams/data/ch43-*.csv.
Teaching values (A-461 to A-463); no shop or test procedures.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch43 import sources as src
from companion.ch43.common import csv, emit
from companion.ch43.examples_a import I_HV, I_LV, geometry
from plantp import xfmrdesign as xd

M, D, T = src.MAIN_B, src.DESIGN, src.TESTS


# ------------------------------------------------ joints and magnetising current
def joints(h_steel: float = 25.0) -> dict[str, float]:
    g = geometry()
    path = 2 * (D["h"] + D["end_ins"] + g["centres"])
    at_steel = h_steel * path
    lines = [f"magnetising ampere-turns of one phase at {D['b_peak']} T (teaching):",
             f"  steel path {path:.2f} m at {h_steel:.0f} A/m: {at_steel:.0f} "
             "A-turns",
             "  joint form        gap mm   two joints A   total A   no-load "
             "current %"]
    out = {}
    for name, gap_mm in (("step-lap", 0.03), ("mitred, single lap", 0.15)):
        at_j = 2 * D["b_peak"] / xd.MU0 * gap_mm / 1000
        tot = at_steel + at_j
        i0 = 100 * tot / (math.sqrt(2) * D["n_lv"] * I_LV)
        out[name] = i0
        lines.append(f"  {name:18s} {gap_mm:6.2f}   {at_j:12.0f}   {tot:7.0f}   "
                     f"{i0:8.2f}")
    lines += ["  a tenth of a millimetre of air in the joints costs more",
              "  ampere-turns than metres of steel: step-lap joints and",
              "  careful stacking keep the no-load current and the joint",
              f"  losses down (ch 25 listed {0.20:.2f} %); the bare-core check of",
              "  the traveler sees the result before the windings go on"]
    emit("c_joints", lines)
    return out


# ------------------------------------------------ water in oil
def water(ppm: float = 18.0, limit_ppm: float = 10.0) -> dict[float, float]:
    lines = [f"oil sample before filling: {ppm:.0f} ppm water (teaching limit "
             f"{limit_ppm:.0f} ppm)",
             "  temperature C   saturation ppm   relative saturation"]
    out = {}
    rows = []
    for t in (0.0, 20.0, 40.0, 60.0, 80.0):
        s = xd.water_solubility_ppm(t)
        out[t] = ppm / s
        lines.append(f"  {t:13.0f}   {s:14.0f}   {ppm / s:19.0%}")
    for t in range(-10, 91, 5):
        rows.append((t, round(xd.water_solubility_ppm(t), 1)))
    csv("ch43-water.csv", "t,ppm", rows)
    lines += ["  the same ppm is a third of saturation at 20 C and a few",
              "  per cent when hot: cold oil holds little water, and paper",
              "  in contact with wetter oil takes it up - the oil is",
              "  processed again until it meets the limit before filling",
              "  (an NCR on the traveler, lab D); the test methods and",
              "  limits are the oil standard's and the contract's (STD-178)"]
    emit("c_water", lines)
    return out


# ------------------------------------------------ ratio test against the taps
def ratio(tol: float = 0.5) -> dict[str, float]:
    design = {r[0]: r for r in xd.tap_table(D["n_hv"], 1.25, 8, D["tap_turns"])}
    lines = ["ratio test of T1 against the tap design (error %)",
             "  tap %    design   measured   difference   verdict"]
    bad = []
    for tap, meas in T["ratio_err_pct"].items():
        dz = design[tap][2]
        ok = abs(meas) <= tol
        lines.append(f"  {tap:+6.2f}   {dz:+6.2f}   {meas:+8.2f}   {meas - dz:+10.2f}"
                     f"   {'pass' if ok else 'fail'}")
        if not ok:
            bad.append(tap)
    csv("ch43-ratio.csv", "tap,meas",
        [(t, m) for t, m in T["ratio_err_pct"].items()])
    tap = bad[0]
    turns = (T["ratio_err_pct"][tap] - design[tap][2]) / 100 * design[tap][1]
    lines += [f"  tap {tap:+.2f} % is {T['ratio_err_pct'][tap] - design[tap][2]:+.2f}"
              f" % off its design value: about {turns:.1f} turns",
              "  every other tap follows the design's whole-turn steps; one",
              "  tap two turns off points at a lead on the wrong tapping",
              "  point - the maker opens the tap-lead record, the unit is",
              "  held until it is corrected and the ratio test repeated"]
    emit("c_ratio", lines)
    return dict(bad=tap, turns=turns)


# ------------------------------------------------ losses corrected
def corrected() -> dict[str, float]:
    d = (1.0 - T["u_rms_over_mean"]) / 1.0
    p0 = xd.waveform_corrected(T["p0_meas_kw"], T["u_rms_over_mean"], 1.0)
    r_hv75 = xd.r_to_ref(T["r_hv_ohm"], T["r_temp_c"])
    r_lv75 = xd.r_to_ref(T["r_lv_ohm"], T["r_temp_c"])
    i2r75 = 3 * (I_HV ** 2 * r_hv75 + I_LV ** 2 * r_lv75) / 1000
    i2r_t = i2r75 * (235 + T["pk_temp_c"]) / 310
    extra_t = T["pk_meas_kw"] - i2r_t
    pk75 = i2r75 + extra_t * (235 + T["pk_temp_c"]) / 310
    lines = ["losses of T1 from the test report, corrected (teaching forms)",
             f"  no-load: measured {T['p0_meas_kw']} kW with the rms voltage "
             f"{T['u_rms_over_mean'] - 1:+.0%} above",
             f"    the mean-value reading: d = {d:+.2f}, P0 = {p0:.1f} kW",
             f"  resistances at {T['r_temp_c']:.0f} C -> 75 C: HV {r_hv75:.4f}, "
             f"LV {r_lv75:.4f} ohm",
             f"  load: measured {T['pk_meas_kw']} kW at {T['pk_temp_c']:.0f} C; "
             f"I2R there {i2r_t:.0f} kW,",
             f"    the rest {extra_t:.0f} kW; at 75 C: {i2r75:.0f} + "
             f"{extra_t * (235 + T['pk_temp_c']) / 310:.0f} = {pk75:.0f} kW",
             "  I2R rises with temperature, eddy and stray losses fall:",
             "  each part is moved on its own before comparing with the",
             "  guarantee at 75 C"]
    emit("c_losses", lines)
    return dict(p0=p0, pk75=pk75, i2r75=i2r75, d=d)


# ------------------------------------------------ heat run from the cooling curve
def heatrun() -> dict[str, float]:
    fit = xd.cooling_curve(T["cool_t_min"], T["cool_r_hv"])
    r_cold, t_cold = T["r_hv_ohm"], T["r_temp_c"]
    t0 = fit["r0"] / r_cold * (235 + t_cold) - 235
    rise = t0 - T["ambient_c"]
    first = T["cool_r_hv"][0] / r_cold * (235 + t_cold) - 235 - T["ambient_c"]
    grad = rise - T["oil_avg_rise"]
    t = np.linspace(0, 20, 41)
    read = dict(zip(T["cool_t_min"], T["cool_r_hv"]))
    csv("ch43-cooling.csv", "t,r,fit",
        [(float(x), read.get(float(x), "nan"),
          round(float(fit["a"] + fit["b"] * math.exp(-x / fit["tau"])), 5))
         for x in t])
    lines = ["heat run of T1: HV resistance read after shut-down",
             "  minutes: " + ", ".join(f"{x:.0f}" for x in T["cool_t_min"]),
             "  ohm:     " + ", ".join(f"{x:.4f}" for x in T["cool_r_hv"][:5]),
             "           " + ", ".join(f"{x:.4f}" for x in T["cool_r_hv"][5:]),
             f"  fit a + b exp(-t/tau): tau {fit['tau']:.1f} min; at t = 0 "
             f"{fit['r0']:.4f} ohm",
             f"  winding mean {t0:.1f} C, rise {rise:.1f} K (guarantee "
             f"{M['winding_rise']:.0f} K); gradient {grad:.1f} K",
             f"  the report used the 2-minute reading: {first:.1f} K - 'pass'",
             "  the winding cooled for two minutes before the first reading;",
             "  the extrapolation to shut-down is part of the method, and",
             "  read correctly the winding rise exceeds its guarantee"]
    emit("c_heatrun", lines)
    return dict(rise=rise, first=first, tau=fit["tau"], grad=grad)


# ------------------------------------------------ sound power
def sound() -> dict[str, float]:
    s = T["height_m"] * T["contour_m"]
    lw = xd.sound_power_db(T["lpa_db"], s)
    lines = [f"sound of T1: {T['lpa_db']:.0f} dB(A) mean pressure on a contour "
             f"of {T['contour_m']:.0f} m, height {T['height_m']} m",
             f"  radiating area {s:.0f} m2: L_WA = {T['lpa_db']:.0f} + 10 log10("
             f"{s:.0f}) = {lw:.1f} dB(A)",
             f"  guarantee {M['sound_lwa']:.0f} dB(A): margin {M['sound_lwa'] - lw:.1f} dB",
             "  the power, not the pressure at one place, is what the",
             "  village calculation of ch 33 starts from; the measurement",
             "  distance and area follow the sound standard (STD-176)"]
    emit("c_sound", lines)
    return dict(lw=lw)


# ------------------------------------------------ gases before and after the heat run
def gases() -> dict[str, float]:
    b, a = src.DGA["before"], src.DGA["after"]
    lines = [f"dissolved gases before and after the {src.DGA['hours']:.0f} h heat "
             "run (ppm)",
             "  gas     before   after   rise"]
    rise = {}
    for gname in b:
        rise[gname] = a[gname] - b[gname]
        lines.append(f"  {gname:6s} {b[gname]:7.1f}  {a[gname]:6.1f}  "
                     f"{rise[gname]:+6.1f}")
    lines += [f"  acetylene appeared ({b['C2H2']:.1f} -> {a['C2H2']:.1f} ppm): a "
              "heat run",
              "  should not make it; small rises of the others with",
              "  temperature are expected - the interpretation follows the",
              "  guidance (STD-179) and the maker's own limits, and here it",
              "  opens a question before acceptance (lab D)"]
    emit("c_gases", lines)
    return rise


if __name__ == "__main__":
    joints()
    water()
    ratio()
    corrected()
    heatrun()
    sound()
    gases()
