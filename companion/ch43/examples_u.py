"""Chapter 43, a fourth round: thermally upgraded paper on the data-pack
year, aluminium against copper windings, the thermal side of the
short-circuit withstand, DC injected by inverters into the PV unit
transformer, the PV unit rated for a 45 C ambient, and a core earthed
twice.

Run from the project root:   python -m companion.ch43.examples_u
Writes companion/ch43/expected/u_*.txt.
Teaching values (A-458, A-459, A-465).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch43 import sources as src
from companion.ch43.common import emit
from companion.ch43.examples_a import I_LV, geometry
from plantp import transformer as tr

M, D = src.MAIN_B, src.DESIGN


# ------------------------------------------------ thermally upgraded paper
def paper(load_scale: float = 1.30) -> dict[str, float]:
    from companion.ch25.examples_b import unit_load
    from plantp import datapack
    k = unit_load() * load_scale
    amb = datapack.load_hourly()["t_air_c"].to_numpy()
    hs = np.array([tr.hot_spot(x, a) for x, a in zip(k, amb)])
    out = {}
    lines = [f"paper ageing on the data-pack year at {load_scale:.0%} of today's "
             "load (teaching)",
             "  paper                         reference C   life used days a year"]
    for name, ref in (("kraft (non-upgraded)", 98.0),
                      ("thermally upgraded", 110.0)):
        days = float(sum(tr.ageing_rate(h, ref=ref) for h in hs) / 24)
        out[name] = days
        lines.append(f"  {name:29s} {ref:11.0f}   {days:21.1f}")
    lines += [f"  upgraded paper ages {out['kraft (non-upgraded)'] / out['thermally upgraded']:.0f}"
              " times slower at the same hot spot: a",
              "  material choice that buys margin for a later battery or",
              "  more PV - stated in the specification and shown by the",
              "  paper's certificate (lesson B, materials)"]
    emit("u_paper", lines)
    return out


# ------------------------------------------------ aluminium or copper
def aluminium(cu_price: float = 9.0, al_price: float = 3.0) -> dict[str, float]:
    rho_ratio = 0.0346 / 0.0211          # Al / Cu at 75 C
    cu_kg = 8.4e3
    al_kg = cu_kg * rho_ratio * 2.70 / 8.90
    vol_ratio = rho_ratio
    lines = ["the same windings in aluminium for the same resistance (teaching)",
             f"  resistivity ratio {rho_ratio:.2f}: section x{rho_ratio:.2f}, mass x"
             f"{al_kg / cu_kg:.2f}",
             f"  conductor: copper {cu_kg / 1000:.1f} t = {cu_kg * cu_price / 1000:.0f}"
             f" k u; aluminium {al_kg / 1000:.1f} t = {al_kg * al_price / 1000:.0f} k u",
             f"  but the windings take {vol_ratio:.2f} x the volume: a wider window,",
             "  a larger core and tank and more no-load loss follow -",
             "  aluminium wins on the conductor and gives part of it back",
             "  in steel and A x P0; large power transformers mostly stay",
             "  copper, distribution and unit transformers often go",
             "  aluminium (foil)"]
    emit("u_aluminium", lines)
    return dict(al_kg=al_kg, saving=cu_kg * cu_price / 1000 - al_kg * al_price / 1000)


# ------------------------------------------------ thermal short-circuit withstand
def thermal_sc(t_s: float = 2.0, cv: float = 3.45e6) -> dict[str, float]:
    j_sc = D["j_a_mm2"] / (M["uk_pct"] / 100) * 1e6
    dt = 0.0211e-6 * j_sc ** 2 * t_s / cv
    lines = [f"winding temperature in a {t_s:.0f} s short circuit (adiabatic, teaching)",
             f"  current density {D['j_a_mm2']} / {M['uk_pct'] / 100} = {j_sc / 1e6:.1f}"
             " A/mm2 for the whole fault",
             f"  rise = rho J^2 t / (heat capacity per m3) = {dt:.0f} K",
             "  about ten kelvin: with this impedance the thermal side of the",
             "  short-circuit withstand is easy; the forces of lesson A",
             "  are what the test or the design review must show"]
    emit("u_thermal", lines)
    return dict(dt=dt, j_sc=j_sc / 1e6)


# ------------------------------------------------ DC injection
def dc_injection(dc_share: float = 0.005, h_steel: float = 25.0) -> dict[str, float]:
    u = src.PVU
    v_lv = u["lv_kv"] * 1e3 / math.sqrt(3)
    i_lv = u["s_mva"] * 1e6 / (3 * v_lv)
    n_lv = 16
    path = 3.2
    at_mag = h_steel * path + 2 * 1.7 / 4e-7 / math.pi * 0.03e-3
    at_dc = dc_share * i_lv * n_lv
    lines = [f"DC from the inverters into the PV unit transformer ({dc_share:.1%} of "
             "rated, teaching)",
             f"  LV current {i_lv:,.0f} A: DC {dc_share * i_lv:.0f} A x {n_lv} turns = "
             f"{at_dc:.0f} A-turns",
             f"  the core needs about {at_mag:.0f} A-turns (peak) to magnetise",
             f"  the DC is {at_dc / at_mag:.1f} x that: the flux sits off-centre and",
             "  saturates every half cycle - noise, heating and harmonics;",
             "  why grid codes and inverter makers limit DC injection, and",
             "  why the unit transformer's specification names the limit",
             "  the inverters meet (ch 9, ch 27)"]
    emit("u_dc", lines)
    return dict(at_dc=at_dc, at_mag=at_mag)


# ------------------------------------------------ rated for 45 C
def hot_ambient(rise_std: float = 60.0, x: float = 0.8, extra: float = 5.0):
    u = src.PVU
    ratio = ((rise_std - extra) / rise_std) ** (1 / x)
    k2 = (ratio * (u["p0_kw"] + u["pk_kw"]) - u["p0_kw"]) / u["pk_kw"]
    k = math.sqrt(k2)
    lines = [f"the PV unit rated {u['s_mva']} MVA at a {u['ambient_c']:.0f} C ambient "
             "(ch 39 requirement T01)",
             f"  {extra:.0f} K hotter air than a 40 C reference (teaching) leaves "
             f"{rise_std - extra:.0f} K",
             "  of rise",
             f"  losses must fall to {ratio:.1%}: the same design carries "
             f"{k:.3f} pu",
             f"  so a {u['s_mva']} MVA unit for 45 C is a {u['s_mva'] / k:.1f} MVA unit "
             "at 40 C",
             "  - the specification's ambient changes the size, and two",
             "  offers rated at different ambients are not the same machine"]
    emit("u_ambient", lines)
    return dict(k=k, equiv=u["s_mva"] / k)


# ------------------------------------------------ core earthed twice
def core_earth(emf_v: float = 1.5, r_loop_mohm: float = 2.0) -> dict[str, float]:
    i = emf_v / (r_loop_mohm / 1000)
    p = emf_v * i
    lines = ["a core earthed at two points forms a loop with the frame",
             f"  leakage flux through the loop: about {emf_v} V (teaching);",
             f"  loop resistance {r_loop_mohm:.0f} mOhm: {i:,.0f} A circulating, "
             f"{p / 1000:.1f} kW",
             "  a kilowatt or more in steel and contacts makes gas and local",
             "  heating; the core is earthed at one point, and the core-to-",
             "  frame insulation test of the routine tests shows that no",
             "  second path exists"]
    emit("u_coreearth", lines)
    return dict(i=i, p=p)


if __name__ == "__main__":
    paper()
    aluminium()
    thermal_sc()
    dc_injection()
    hot_ambient()
    core_earth()
    _ = (I_LV, geometry)
