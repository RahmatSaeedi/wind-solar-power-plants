"""Chapter 47, lesson A: design inputs and product families - the
material take-off of one turbine's tower and foundation and of the PV
field's tables, and a simplified load path from the rotor to the soil
(the handoff's first worked example).

Run from the project root:   python -m companion.ch47.examples_a
Writes companion/ch47/expected/a_*.txt.
Teaching values (A-490, A-497); no design is approved here.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as s30
from companion.ch47 import sources as src
from companion.ch47.common import emit
from plantp import structures as st

G = 9.81


# [start: takeoff]
def tower_steel() -> list:
    """Shell mass of each section from its geometry: pi D_mean t L rho."""
    rows = []
    for sec, d0, d1, t_mm, ln in src.TOWER:
        d = (d0 + d1) / 2
        m = math.pi * d * t_mm / 1000 * ln * src.STEEL_RHO / 1000      # t
        rows.append((sec, d, t_mm, ln, m))
    return rows
# [end: takeoff]


def takeoff(flange_share: float = 0.12, rebar_kg_m3: float = 95.0,
            modules: int = 109_200, fatigue_t: float = 32.0) -> dict:
    rows = tower_steel()
    shell = sum(r[4] for r in rows)
    tower = (shell + fatigue_t) * (1 + flange_share)
    rebar = src.BASE_CONCRETE * rebar_kg_m3 / 1000
    tables = modules // (s30.PV_TABLE["rows"] * s30.PV_TABLE["modules_per_row"])
    pv_steel = tables * s30.PV_TABLE["steel_kn"] / G
    lines = ["material take-off (teaching): one turbine and the PV field",
             "  tower section   D mean m   t mm   length m   shell t"]
    for sec, d, t_mm, ln, m in rows:
        lines.append(f"  {sec:13d}   {d:8.2f}   {t_mm:4d}   {ln:8.0f}   {m:7.1f}")
    lines += [f"  shell from the ch 11 wall schedule {shell:.0f} t (ch 11: 340 t);",
              f"  ch 30's fatigue steel low down +{fatigue_t:.0f} t: "
              f"{shell + fatigue_t:.0f} t of shell",
              f"  flanges, door frame and internals +{flange_share:.0%}: "
              f"{tower:.0f} t a tower",
              f"  foundation: {src.BASE_CONCRETE:.0f} m3 concrete, rebar at "
              f"{rebar_kg_m3:.0f} kg/m3: {rebar:.0f} t",
              f"  twelve turbines: {12 * tower:,.0f} t of tower steel, "
              f"{12 * src.BASE_CONCRETE:,.0f} m3 concrete, {12 * rebar:,.0f} t rebar",
              f"  PV: {tables:,} tables of 2 x 26 at {s30.PV_TABLE['steel_kn']:.0f} kN: "
              f"{pv_steel:,.0f} t of galvanized steel",
              "  the take-off from the fabrication drawings must show ch 30's",
              "  32 t: one that matches ch 11's 340 t of shell means the",
              "  drawings still carry the old walls (lesson B checks the plates)"]
    emit("a_takeoff", lines)
    return dict(shell=shell, tower=tower, rebar=rebar, tables=tables, rows=rows,
                pv_steel=pv_steel)


# ------------------------------------------------ load path
def takeoff_quiet(flange_share: float = 0.12, fatigue_t: float = 32.0) -> float:
    return (sum(r[4] for r in tower_steel()) + fatigue_t) * (1 + flange_share)


def load_path(backfill_m3: float = 1100.0, gamma_b: float = 18.0,
              n_bolts: int = 120, d_bolts: float = 4.30,
              preload_kn: float = 1600.0, phi: float = 0.12) -> dict:
    lo = s30.LOADS["extreme (parked, 50-yr gust)"]
    m_base = lo["m_mnm"] * 1e3                                     # kN m at tower base
    h = lo["h_mn"] * 1e3                                            # kN
    w_top = s30.TOP_T * G
    w_tower = takeoff_quiet() * G
    w_conc = src.BASE_CONCRETE * 24.0
    w_back = backfill_m3 * gamma_b
    v = w_top + w_tower + w_conc + w_back
    m_found = m_base + h * s30.FOUNDATION["depth"]
    e, a_eff, q = st.foundation_pressure(v, m_found, src.BASE_D / 2)
    f_bolt = 4 * m_base / (n_bolts * d_bolts) - (w_top + w_tower) / n_bolts
    lines = ["simplified load path, extreme parked case (teaching, ch 30 loads)",
             f"  rotor and nacelle {w_top / 1e3:.2f} MN and tower {w_tower / 1e3:.2f} MN "
             "down the shell",
             f"  base moment {lo['m_mnm']:.1f} MN m, shear {lo['h_mn']:.2f} MN -> "
             f"{n_bolts} bolts on {d_bolts} m:",
             f"    worst flange bolt pulled by {f_bolt:,.0f} kN; the joint stays "
             "closed",
             f"    below {preload_kn / (1 - phi):,.0f} kN (preload {preload_kn:,.0f} kN, "
             "ch 11)",
             f"  at the underside of the base ({s30.FOUNDATION['depth']} m down): M = "
             f"{m_found / 1e3:.1f} MN m",
             f"  vertical load {v / 1e3:.1f} MN (top, tower, {src.BASE_CONCRETE:.0f} m3 "
             f"concrete, {backfill_m3:.0f} m3 fill)",
             f"  eccentricity {e:.2f} m on a {src.BASE_D:.0f} m base; compressed area "
             f"{a_eff:.0f} m2 of {math.pi * (src.BASE_D / 2) ** 2:.0f}",
             f"  soil pressure {q:.0f} kPa against ch 30's dense ground",
             "  each link of the path is a product of this chapter: shell",
             "  plates and welds, flange and bolts, anchor cage and grout,",
             "  concrete and rebar - and each link has its own record"]
    emit("a_loadpath", lines)
    return dict(v=v, m=m_found, e=e, a=a_eff, q=q, f_bolt=f_bolt)


# ------------------------------------------------ product families
FAMILIES = [   # family, governing input, key tolerance, life evidence
    ("tower sections", "fatigue, buckling, frequency", "ovality, flange flatness",
     "coating, weld NDT"),
    ("turbine foundation", "overturning, soil, stiffness", "anchor-cage level",
     "concrete cover, strength"),
    ("PV tables (fixed)", "wind on modules, soil", "post plumb, rail line",
     "zinc thickness"),
    ("single-axis tracker", "wind stow, torque tube", "tube straightness",
     "drive backlash, zinc"),
    ("substation steel", "line pull, seismic", "bolt-hole positions", "zinc"),
    ("container plinths", "battery mass, water", "level and flatness",
     "concrete cover"),
]


def families() -> int:
    lines = ["product families of this chapter and what governs each (teaching)",
             "  family                governing input",
             "    tolerance that matters; evidence of life"]
    for f, g, t, l in FAMILIES:
        lines.append(f"  {f:21s} {g}")
        lines.append(f"    {t}; {l}")
    lines += ["  every family meets the plant through one interface: the",
              "  anchor cage, the post in the ground, the bolt pattern of a",
              "  support, the plinth's level - the fabricator's tolerance",
              "  and the site's tolerance add up there (lesson C)"]
    emit("a_families", lines)
    return len(FAMILIES)


if __name__ == "__main__":
    takeoff()
    load_path()
    families()
