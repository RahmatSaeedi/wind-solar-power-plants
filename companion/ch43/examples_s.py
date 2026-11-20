"""Chapter 43, a second round: which winding sets the flux at each tap,
partial discharge in a void, clamping lost when pressboard shrinks, a bad
joint that the resistance test cannot see, what the test bay must supply,
tank shunts against stray loss, and the grading of a condenser bushing.

Run from the project root:   python -m companion.ch43.examples_s
Writes companion/ch43/expected/s_*.txt.
Teaching values (A-458, A-465); no test voltages or procedures.
"""
from __future__ import annotations

import math

from companion.ch43 import sources as src
from companion.ch43.common import emit
from companion.ch43.examples_a import I_HV, I_LV

M, D = src.MAIN_B, src.DESIGN


# ------------------------------------------------ which winding sets the flux
def tap_flux(b_rated: float = 1.70) -> dict[float, float]:
    lines = ["flux at each tap: who sets it (HV taps, LV winding untapped)",
             "  tap %   from the 33 kV side   energised from 132 kV, LV open",
             "           at 1.0 / 1.1 pu        at 1.0 / 1.1 pu"]
    out = {}
    for tap in (-10.0, -5.0, 0.0, 5.0, 10.0):
        n_hv = D["n_hv"] * (1 + tap / 100)
        b_hv = b_rated * D["n_hv"] / n_hv
        out[tap] = b_hv
        lines.append(f"  {tap:+5.0f}   {b_rated:5.2f} / {1.1 * b_rated:4.2f}"
                     f"            {b_hv:5.2f} / {1.1 * b_hv:4.2f} T")
    lines += ["  in service the plant holds the 33 kV bus, and the untapped",
              "  33 kV winding fixes the flux whatever the tap; energised",
              "  from the grid at the -10 % tap, fewer HV turns carry the",
              "  same voltage and the core runs 11 % higher - energise on a",
              "  high tap and keep V/f in view (ch 25, energising)"]
    emit("s_tapflux", lines)
    return out


# ------------------------------------------------ partial discharge in a void
def void(e_solid: float = 4.0, eps_r: float = 4.4, d_mm=(0.05, 0.2, 1.0)):
    e_void = eps_r * e_solid
    lines = ["a flat gas void in impregnated insulation",
             f"  (field {e_solid} kV/mm in the solid, eps {eps_r})",
             f"  the void carries eps x E = {e_void:.1f} kV/mm",
             "  void mm   gas strength kV/mm (teaching)   discharges?"]
    out = {}
    for d in d_mm:
        strength = 3.0 + 1.35 / math.sqrt(d / 10)        # teaching small-gap rise
        pd = e_void > strength
        out[d] = (strength, pd)
        lines.append(f"  {d:7.2f}   {strength:30.1f}   {'yes' if pd else 'no'}")
    lines += ["  a void sees the field multiplied by the permittivity of the",
              "  solid around it, and gas is weaker than oil-filled paper:",
              "  voids left by poor drying or impregnation discharge - the",
              "  PD measurement of the dielectric test is where they show",
              "  (T1's 120 pC, lab D)"]
    emit("s_void", lines)
    return out


# ------------------------------------------------ clamping and shrinkage
def clamping(stack_m: float = 0.30, k_mn_mm: float = 0.25,
             force_mn: float = 2.0) -> dict[float, float]:
    lines = [f"winding clamped with {force_mn} MN; pressboard spacers {stack_m * 1000:.0f}"
             " mm in all (teaching)",
             f"  clamping stiffness {k_mn_mm} MN per mm of stack shortening",
             "  shrink %   stack shortens mm   force left MN   share"]
    out = {}
    for sh in (0.0, 0.5, 1.0, 2.0, 3.0):
        dx = stack_m * 1000 * sh / 100
        left = max(0.0, force_mn - k_mn_mm * dx)
        out[sh] = left / force_mn
        lines.append(f"  {sh:8.1f}   {dx:17.1f}   {left:13.2f}   {left / force_mn:5.0%}")
    lines += ["  pressboard that dries in the tank shrinks, and the clamping",
              "  it carried goes with it; a winding that is not held moves",
              "  in the first short circuit - pre-shrunk board and clamping",
              "  checked after drying are the controls, the clamping record",
              "  is the evidence (traveler, active part)"]
    emit("s_clamp", lines)
    return out


# ------------------------------------------------ a bad joint
def joint(r_good_uohm: float = 2.0, r_bad_uohm: float = 50.0) -> dict[str, float]:
    r_phase = 0.0836                                   # LV phase at 75 C, ohm
    p_good = I_LV ** 2 * r_good_uohm * 1e-6
    p_bad = I_LV ** 2 * r_bad_uohm * 1e-6
    share = (r_bad_uohm - r_good_uohm) * 1e-6 / r_phase
    lines = [f"brazed lead joint in the LV delta at {I_LV:.0f} A (teaching):",
             f"  good joint {r_good_uohm:.0f} uOhm: {p_good:.1f} W; poor joint "
             f"{r_bad_uohm:.0f} uOhm: {p_bad:.0f} W in a few cm3",
             f"  the poor joint raises the phase resistance by {share:.3%}",
             "  - inside the scatter of the resistance test between phases",
             "  twenty watts in one spot heats the oil and the paper there:",
             "  gases (ethylene, then more) and thermography find what the",
             "  resistance test cannot; the joint record (brazing, crimp,",
             "  bolt torque) is the control that prevents it"]
    emit("s_joint", lines)
    return dict(p_bad=p_bad, share=share)


# ------------------------------------------------ test bay capability
def testbay() -> dict[str, float]:
    uk = M["uk_pct"] / 100
    s_test = uk * M["s_mva"]
    pk = 298.0
    pf = pk / (s_test * 1000)
    total = 42.2 + pk
    i_ratio = math.sqrt(total / pk)
    lines = ["what the test bay must supply for T1 (from the design values)",
             f"  load-loss test at rated current: {s_test:.2f} MVA at a power "
             f"factor of {pf:.3f}",
             "  almost all reactive: the bay compensates it with capacitor",
             "  banks and its generator supplies the losses",
             f"  heat run by the short-circuit method: total losses {total:.0f} kW,",
             f"  current {i_ratio:.3f} x rated",
             "  a bay smaller than this cannot test the unit at rated",
             "  current; its capability is checked at the factory audit",
             "  (ch 39, type-test applicability), before the order"]
    emit("s_testbay", lines)
    return dict(s_test=s_test, pf=pf, i_ratio=i_ratio)


# ------------------------------------------------ shunts and stray loss
def shunts(stray_share: float = 0.12, with_shunts: float = 0.06) -> dict[str, float]:
    i2r = 247.0
    saved = i2r * (stray_share - with_shunts)
    value = saved * src.COSTS["b_kw"]
    lines = ["leakage flux into the tank wall: stray loss with and without",
             "  magnetic shunts on the tank (teaching shares of I2R)",
             f"  without: {i2r * stray_share:.0f} kW; with shunts: "
             f"{i2r * with_shunts:.0f} kW; saved {saved:.0f} kW",
             f"  evaluated with B = {src.COSTS['b_kw']}: {value:.0f} k u, against "
             "the shunts' steel and work",
             "  the higher the impedance, the more leakage flux and the more",
             "  the tank heats where it is struck - shunts also keep the",
             "  tank's local hot spots down, which the heat run's",
             "  thermography sees"]
    emit("s_shunts", lines)
    return dict(saved=saved, value=value)


# ------------------------------------------------ condenser bushing grading
def bushing(u_kv: float = 76.2, r0_mm: float = 20.0, r1_mm: float = 80.0,
            layers: int = 10) -> dict[str, float]:
    e_plain = u_kv / (r0_mm * math.log(r1_mm / r0_mm))
    e_mean = u_kv / (r1_mm - r0_mm)
    # graded: equal radial thickness layers with equal voltage share each
    t = (r1_mm - r0_mm) / layers
    e_graded = (u_kv / layers) / t
    lines = [f"bushing insulation between a {r0_mm:.0f} mm conductor and an "
             f"{r1_mm:.0f} mm flange,",
             f"  {u_kv} kV phase (teaching)",
             f"  ungraded (one cylinder): field at the conductor {e_plain:.2f} kV/mm",
             f"  mean field {e_mean:.2f} kV/mm; {layers} condenser layers sharing the "
             f"voltage: {e_graded:.2f}",
             "  the bare cylinder crowds the field at the conductor; foil",
             "  layers of chosen lengths divide the voltage evenly - the",
             "  capacitance and dissipation factor the factory records",
             "  (ch 25, bushings) are the fingerprint of those layers"]
    emit("s_bushing", lines)
    return dict(e_plain=e_plain, e_graded=e_graded)


if __name__ == "__main__":
    tap_flux()
    void()
    clamping()
    joint()
    testbay()
    shunts()
    bushing()
    _ = I_HV
