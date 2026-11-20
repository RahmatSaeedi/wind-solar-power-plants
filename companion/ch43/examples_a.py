"""Chapter 43, lesson A: from requirement to the first numbers of a design -
flux density and over-excitation, turns and taps, currents and conductor,
impedance from the geometry, the load-loss build-up and efficiency, the
oil-pressboard gap and the short-circuit stresses of the windings.

Run from the project root:   python -m companion.ch43.examples_a
Writes companion/ch43/expected/a_*.txt and diagrams/data/ch43-*.csv.
Teaching values (A-458); a maker's design uses its own methods.
"""
from __future__ import annotations

import math

from companion.ch43 import sources as src
from companion.ch43.common import csv, emit
from plantp import xfmrdesign as xd

M, D = src.MAIN_B, src.DESIGN
V_HV = M["hv_kv"] * 1e3 / math.sqrt(3)          # phase voltage, star
V_LV = M["lv_kv"] * 1e3                         # phase voltage, delta
I_HV = M["s_mva"] * 1e6 / (3 * V_HV)
I_LV = M["s_mva"] * 1e6 / (3 * V_LV)            # phase current of the delta


def geometry(e_t: float = D["e_t"], b: float = D["b_peak"]) -> dict[str, float]:
    """Diameters, core and winding geometry of the reviewer's design."""
    c = xd.core_section(e_t, b, stacking=D["stacking"], fill=D["fill"])
    d = c["d"]
    d_l = d + 2 * D["gap_core"] + D["a1"]
    d_m = d + 2 * D["gap_core"] + 2 * D["a1"] + D["a12"]
    d_h = d + 2 * D["gap_core"] + 2 * D["a1"] + 2 * D["a12"] + D["a2"]
    centres = d_h + D["a2"] + D["leg_gap"]
    mass = xd.core_mass_kg(c["a_net"], D["h"] + D["end_ins"], centres, d)
    return dict(c, d_l=d_l, d_m=d_m, d_h=d_h, centres=centres, core_kg=mass)


# ------------------------------------------------ flux density
def flux() -> dict[float, dict]:
    st = src.STEELS[D["steel"]]
    lines = [f"flux density at {D['e_t']:.0f} V a turn: core, loss, sound and "
             "over-excitation (teaching)",
             "  loss per kg ~ B^2 from 1.15 W/kg at 1.7 T; sound ~ 40 log B;",
             "  over-excitation 1.10 U at 0.95 f raises B by 16 %",
             "  B T   core dia m   core t   P0 kW   sound dB   B over-excited T"]
    out = {}
    for b in (1.50, 1.60, 1.70, 1.80):
        g = geometry(D["e_t"], b)
        p0 = xd.no_load_loss_kw(g["core_kg"], st["w"] * (b / 1.7) ** 2, st["bf"])
        snd = 40 * math.log10(b / 1.7)
        bo = b * 1.10 / 0.95
        out[b] = dict(p0=p0, mass=g["core_kg"], bo=bo)
        lines.append(f"  {b:4.2f}  {g['d']:10.3f}  {g['core_kg'] / 1000:6.1f}  "
                     f"{p0:6.1f}  {snd:+8.1f}  {bo:16.2f}")
    span = out[1.80]["p0"] - out[1.50]["p0"]
    lines += ["  a lower flux density needs more steel but each kilogram",
              f"  loses less: P0 moves only {span:.1f} kW over the range and the",
              "  sound a few dB; the margin to saturation (about 2.0 T for",
              "  grain-oriented steel) moves most - at 1.8 T the over-excited",
              "  core is past it, so the grid study's highest V/f (ch 28)",
              "  bounds the choice"]
    emit("a_flux", lines)
    return out


# ------------------------------------------------ turns and taps
def turns() -> dict[str, float]:
    n_lv, n_hv = D["n_lv"], D["n_hv"]
    e_t = V_LV / n_lv
    err0 = 100 * (n_hv * e_t / V_HV - 1)
    lines = [f"turns of the reviewer's design: e_t = {e_t:.1f} V",
             f"  LV delta: {V_LV:,.0f} V / {e_t:.1f} = {n_lv} turns",
             f"  HV star: {V_HV:,.0f} V / {e_t:.1f} = {V_HV / e_t:.1f} -> {n_hv} "
             f"turns (ratio error {err0:+.2f} %)",
             f"  tap step 1.25 % = {n_hv * 0.0125:.2f} turns: whole turns only",
             "  turns a step   worst ratio error over the 17 positions"]
    worst = {}
    for k in (8, 9):
        tab = xd.tap_table(n_hv, 1.25, 8, k)
        w = max(tab, key=lambda r: abs(r[2]))
        worst[k] = w[2]
        lines.append(f"  {k:12d}   {w[2]:+.2f} % at tap {w[0]:+.2f} %")
    tab = xd.tap_table(n_hv, 1.25, 8, D["tap_turns"])
    csv("ch43-taps.csv", "tap,err", [(r[0], round(r[2], 3)) for r in tab])
    lines += [f"  {D['tap_turns']} turns a step keeps every tap inside +-0.5 % "
              f"(worst {worst[9]:+.2f} %);",
              f"  8 turns would miss at the end ({worst[8]:+.2f} %) - the ratio",
              "  test at every tap (lesson C) checks the arithmetic in copper"]
    emit("a_turns", lines)
    return dict(e_t=e_t, err0=err0, worst8=worst[8], worst9=worst[9])


# ------------------------------------------------ currents and conductor
def currents() -> dict[str, float]:
    g = geometry()
    j = D["j_a_mm2"]
    a_hv, a_lv = I_HV / j, I_LV / j
    cu = 8900 * 3 * (D["n_hv"] * math.pi * g["d_h"] * a_hv
                     + D["n_lv"] * math.pi * g["d_l"] * a_lv) * 1e-6
    lines = [f"currents of {M['s_mva']:.0f} MVA at rated:",
             f"  HV line = phase (star): {I_HV:.1f} A",
             f"  LV line {I_LV * math.sqrt(3):,.0f} A; phase of the delta "
             f"{I_LV:.1f} A",
             f"  at {j} A/mm2: HV conductor {a_hv:.1f} mm2, LV {a_lv:.1f} mm2",
             f"  copper in the two windings: {cu / 1000:.1f} t (mean turns "
             f"{math.pi * g['d_l']:.2f} and {math.pi * g['d_h']:.2f} m)",
             f"  same ampere-turns both sides: {D['n_lv'] * I_LV:,.0f} and "
             f"{D['n_hv'] * I_HV:,.0f} A",
             "  the delta carries 1/sqrt3 of the line current, so its",
             "  conductor is sized on the phase current, not the line"]
    emit("a_currents", lines)
    return dict(i_hv=I_HV, i_lv=I_LV, a_hv=a_hv, a_lv=a_lv, cu_t=cu / 1000)


# ------------------------------------------------ impedance from geometry
def impedance() -> dict[str, float]:
    g = geometry()
    ni = D["n_lv"] * I_LV

    def ux(a12=D["a12"], h=D["h"]):
        return xd.ux_pct(50.0, ni, D["e_t"], g["d_m"] + a12 - D["a12"], a12,
                         D["a1"], D["a2"], h)
    base = ux()
    lines = [f"impedance of the design from its geometry: {base:.2f} % "
             f"(guarantee {M['uk_pct']} %, +-7.5 %)",
             f"  Dm {g['d_m']:.3f} m, h {D['h']} m, a12 {D['a12'] * 1000:.0f} mm,"
             f" a1 {D['a1'] * 1000:.0f}, a2 {D['a2'] * 1000:.0f} mm; Rogowski "
             f"factor {1 - (D['a1'] + D['a2'] + D['a12']) / (math.pi * D['h']):.3f}",
             "  change               ux %"]
    rows = []
    for name, kw in (("gap +10 mm", dict(a12=D["a12"] + 0.01)),
                     ("gap -10 mm", dict(a12=D["a12"] - 0.01)),
                     ("height +50 mm", dict(h=D["h"] + 0.05)),
                     ("height -50 mm", dict(h=D["h"] - 0.05))):
        v = ux(**kw)
        rows.append((name, v))
        lines.append(f"  {name:18s} {v:6.2f}")
    lo, hi = M["uk_pct"] * (1 - 0.075), M["uk_pct"] * (1 + 0.075)
    per_mm = (ux(a12=D["a12"] + 0.001) - base)
    lines += [f"  band {lo:.2f} - {hi:.2f} %: the gap may move about "
              f"{(hi - base) / per_mm:.0f} mm up or {(base - lo) / per_mm:.0f} mm down",
              "  the main gap is set by the insulation (lesson A, gap), so",
              "  the impedance is tuned with the height and the diameters -",
              "  and the test (lesson C) is where the copper meets the sum"]
    emit("a_impedance", lines)
    return dict(ux=base, per_mm=per_mm, rows=rows)


# ------------------------------------------------ load loss and efficiency
def losses() -> dict[str, float]:
    g = geometry()
    j = D["j_a_mm2"]
    r_lv = xd.resistance_ohm(D["n_lv"], g["d_l"], I_LV / j)
    r_hv = xd.resistance_ohm(D["n_hv"], g["d_h"], I_HV / j)
    i2r = 3 * (I_LV ** 2 * r_lv + I_HV ** 2 * r_hv) / 1000
    eddy = i2r * D["eddy_share"]
    stray = i2r * D["stray_share"]
    pk = i2r + eddy + stray
    st = src.STEELS[D["steel"]]
    p0 = xd.no_load_loss_kw(g["core_kg"], st["w"], st["bf"])
    lines = ["load loss of the design at 75 C, built up (teaching shares):",
             f"  R per phase: LV {r_lv * 1000:.1f} mOhm, HV {r_hv * 1000:.0f} mOhm",
             f"  I2R {i2r:.0f} kW + eddy {eddy:.0f} + stray (tank, clamps, leads) "
             f"{stray:.0f} = {pk:.0f} kW",
             f"  no-load loss {p0:.1f} kW ({D['steel']}, {g['core_kg'] / 1000:.1f} t "
             f"core); bid B {M['p0_kw']:.0f} / {M['pk_kw']:.0f} kW",
             "  load pu   efficiency at pf 0.95"]
    eff = {}
    for k in (0.25, 0.38, 0.5, 0.75, 1.0):
        out = k * M["s_mva"] * 1000 * 0.95
        e = out / (out + p0 + pk * k * k)
        eff[k] = e
        lines.append(f"  {k:7.2f}   {e:.3%}")
    lines += [f"  highest efficiency where P0 = Pk k^2: k = "
              f"{math.sqrt(p0 / pk):.2f}, close to",
              "  Plant P's mean load of 0.29 pu (ch 25) - a design for this",
              "  plant, not for full load"]
    emit("a_losses", lines)
    return dict(i2r=i2r, pk=pk, p0=p0, r_lv=r_lv, r_hv=r_hv, eff=eff)


# ------------------------------------------------ oil and pressboard
def gap(u_kv: float = 100.0, gap_mm: float = 75.0, barriers: int = 3,
        t_pb: float = 3.0) -> dict[str, float]:
    oil = gap_mm - barriers * t_pb
    duct = oil / (barriers + 1)
    e_all, _ = xd.field_in_gap(u_kv, gap_mm, 0.0)
    e_oil, e_pb = xd.field_in_gap(u_kv, oil, barriers * t_pb)

    def strength(d_mm):                       # teaching size effect
        return 12.0 * d_mm ** -0.37

    m_all = strength(gap_mm) / e_all
    m_bar = strength(duct) / e_oil
    lines = [f"HV-LV gap of {gap_mm:.0f} mm at a teaching {u_kv:.0f} kV across it",
             f"  all oil: {e_all:.2f} kV/mm; strength of a {gap_mm:.0f} mm duct "
             f"{strength(gap_mm):.2f} -> margin {m_all:.2f}",
             f"  {barriers} pressboard barriers of {t_pb:.0f} mm: oil {e_oil:.2f}, "
             f"board {e_pb:.2f} kV/mm",
             f"  ducts of {duct:.1f} mm hold {strength(duct):.2f} kV/mm -> "
             f"margin {m_bar:.2f}",
             "  the board (permittivity 4.4) pushes more stress into the oil",
             "  (2.2), yet thin oil ducts hold much more than one wide one:",
             "  barriers divide the gap - the stress curve is teaching; the",
             "  insulation levels and tests are the standard's and maker's"]
    emit("a_gap", lines)
    return dict(m_all=m_all, m_bar=m_bar, e_oil=e_oil)


# ------------------------------------------------ short-circuit stresses
def forces(kappa: float = 1.8, e_cu: float = 110e9, t_cond: float = 0.010,
           sticks: int = 24) -> dict[str, float]:
    g = geometry()
    i_sc = I_HV / (M["uk_pct"] / 100)
    ni = D["n_hv"] * i_sc * kappa * math.sqrt(2)
    s_hv = xd.hoop_stress_mpa(ni, D["h"], g["d_h"], D["n_hv"], I_HV / D["j_a_mm2"])
    s_lv = xd.hoop_stress_mpa(ni, D["h"], g["d_l"], D["n_lv"], I_LV / D["j_a_mm2"])
    free = xd.buckling_free_mpa(e_cu, t_cond, g["d_l"])
    span = math.pi * g["d_l"] / sticks
    held = xd.buckling_supported_mpa(e_cu, t_cond, span)
    lines = [f"windings at the peak short-circuit current (uk {M['uk_pct']} %,",
             f"  peak factor {kappa} x sqrt2)",
             f"  HV {i_sc:,.0f} A rms, {ni / 1e6:.2f} MA-turns at the peak",
             f"  HV hoop tension {s_hv:.0f} MPa; LV hoop compression "
             f"{s_lv:.0f} MPa",
             f"  LV conductor {t_cond * 1000:.0f} mm thick on a {g['d_l']:.2f} m "
             f"winding: free buckling at {free:.0f} MPa",
             f"  held by {sticks} sticks ({span * 1000:.0f} mm apart): buckling "
             f"at {held:,.0f} MPa",
             "  free, the inner winding would buckle below the fault stress;",
             "  sticks on a strong cylinder hold it, and the copper's proof",
             "  strength becomes the limit - a design review asks for the",
             "  calculation or the test that shows it (STD-175)"]
    emit("a_forces", lines)
    return dict(s_hv=s_hv, s_lv=s_lv, free=free, held=held)


if __name__ == "__main__":
    flux()
    turns()
    currents()
    impedance()
    losses()
    gap()
    forces()
