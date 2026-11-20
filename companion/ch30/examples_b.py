"""Chapter 30, lesson B: structural response - stresses up the tower,
shell buckling against yield (Rankine), fatigue of the circumferential
welds on a bilinear S-N curve, the wall schedule both checks need, the
door opening, the tower frequency on a flexible foundation (T07), and
the tip deflection.

Run from the project root:   python -m companion.ch30.examples_b
Writes companion/ch30/expected/b_*.txt and diagrams/data/ch30-*.csv.
Teaching values (A-356 .. A-359); never a design.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st

E, FY = src.STEEL["e"], src.STEEL["fy"]
DETAIL = 71.0            # MPa at 2e6 cycles: circumferential butt weld (teaching class)
GAMMA_F = 1.15           # teaching factor on fatigue stress range


def t_needed(check, start_mm: int = 10) -> int:
    """Smallest wall (mm) at which check(t_m) <= 1, searching upwards."""
    t = start_mm
    while check(t / 1000) > 1.0:
        t += 1
    return t


def buckling_use(m: float, d0: float, t: float) -> float:
    s_el = st.shell_buckling(E, t, d0 / 2, 0.4) / 1e6
    return m / src.tube_w(d0, t) / 1e6 / st.rankine(FY / 1e6, s_el)


def fatigue_damage(dm: float, d0: float, t: float) -> float:
    ds = dm / src.tube_w(d0, t) / 1e6 * GAMMA_F
    return 1e7 / st.sn_life(ds, DETAIL)


def stresses() -> None:
    ext = src.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"]
    lines = ["extreme bending up the tower against buckling (teaching, A-356)",
             "  (moment falls with height; knock-down 0.4 on 0.605 E t/r;",
             "   Rankine: 1/s = 1/fy + 1/s_el)",
             "  section  D m   t mm   r/t   stress MPa   strength MPa   use   t for use 1"]
    rows = []
    for sec, d0, d1, t_mm, length in src.TOWER:
        z = (sec - 1) * length
        m = ext * (src.HUB - z) / src.HUB * 1e6
        t = t_mm / 1000
        sig = m / src.tube_w(d0, t) / 1e6
        s_r = st.rankine(FY / 1e6, st.shell_buckling(E, t, d0 / 2, 0.4) / 1e6)
        need = t_needed(lambda tt: buckling_use(m, d0, tt))
        rows.append((sec, f"{sig:.0f}", f"{s_r:.0f}"))
        lines.append(f"  {sec:7d}  {d0:4.2f}  {t_mm:4d}  {d0 / 2 / t:4.0f}   {sig:10.0f}"
                     f"   {s_r:12.0f}   {sig / s_r:4.2f}   {need:8d} mm")
    csv("ch30-buckling.csv", "sec,stress,strength", rows)
    lines += ["  with this teaching knock-down, sections 2 and 3 of the",
              "  ch 11 wall schedule are thin: buckling, not yield, sets",
              "  the wall (strength far below 355 MPa); the real check",
              "  uses the code's reduction for the fabrication quality",
              "  class - which is why ovality and dents are measured"]
    emit("b_buckling", lines)


def fatigue() -> None:
    dm = src.LOADS["fatigue: DEL at 1e7 cycles"]["m_mnm"] * 1e6
    ext = src.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"] * 1e6
    lines = ["fatigue of the circumferential welds (DEL at 1e7 cycles, teaching",
             f"  detail class {DETAIL:.0f} MPa, slopes 3 and 5, stress x {GAMMA_F})",
             "  section  range MPa   damage   t for damage 1   t buckling   t chosen"]
    added = 0.0
    for sec, d0, d1, t_mm, length in src.TOWER:
        z = (sec - 1) * length
        dmz = dm * (src.HUB - z) / src.HUB
        mz = ext * (src.HUB - z) / src.HUB
        ds = dmz / src.tube_w(d0, t_mm / 1000) / 1e6 * GAMMA_F
        t_f = t_needed(lambda tt: fatigue_damage(dmz, d0, tt))
        t_b = t_needed(lambda tt: buckling_use(mz, d0, tt))
        t_c = max(t_mm, t_f, t_b)
        added += math.pi * (d0 + d1) / 2 * length * (t_c - t_mm) / 1000 * src.STEEL["rho"] / 1e3
        lines.append(f"  {sec:7d}   {ds:9.1f}   {fatigue_damage(dmz, d0, t_mm / 1000):6.2f}"
                     f"   {t_f:11d} mm   {t_b:7d} mm   {t_c:5d} mm")
    curve = [(f"{n:.3e}", f"{ds:.2f}") for ds in (150, 120, 100, 80, 71, 60, 52.3, 45, 40, 35,
                                                     30, 25, 20)
             for n in [st.sn_life(ds, DETAIL)]]
    csv("ch30-sn.csv", "n,ds", curve)
    lines += [f"  steel added to the tower: about {added:.0f} t on {src.TOWER_T:.0f} t",
              "  fatigue, not the storm, sizes the lower welds: with the",
              "  ch 11 walls three sections exceed a damage of 1; thicker",
              "  cans, a better weld detail (ground flush) or a lower",
              "  load set fix it - the maker's tower design does this with",
              "  the real load spectrum and the code's detail categories"]
    emit("b_fatigue", lines)


def door() -> None:
    m_op = src.LOADS["production (peak)"]["m_mnm"] * 1e6
    z_door = 2.0
    m = m_op * (src.HUB - z_door) / src.HUB
    sig = m / src.tube_w(4.5, 0.046) / 1e6
    lines = ["the door opening near the base (2.4 x 1.0 m, teaching)",
             f"  nominal bending stress at the door level: {sig:.0f} MPa (production)",
             "  stress at the opening's corner, concentration factor:"]
    for kt, label in ((3.0, "plain cut opening"), (1.6, "with a welded door frame")):
        lines.append(f"    {label:28s} Kt {kt:.1f}: {kt * sig:4.0f} MPa")
    lines += ["  a plain hole triples the stress at its corners, beyond",
              "  yield in a storm and far beyond the fatigue range: the",
              "  door frame (a thick, shaped ring welded in) restores the",
              "  section, and its welds are among the most inspected on",
              "  the tower"]
    emit("b_door", lines)


def foundation_frequency() -> None:
    r = src.FOUNDATION["r"]
    m_top = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3
    f_need = src.ONE_P_MAX * (1 + src.MARGIN_1P)
    f_rot = 1 / math.sqrt(1 / f_need ** 2 - 1 / src.F1_FIXED ** 2)
    k_need = (2 * math.pi * f_rot) ** 2 * m_top * src.HUB ** 2
    lines = ["tower frequency on a flexible foundation (Dunkerley; teaching soils)",
             f"  fixed base f1 = {src.F1_FIXED} Hz; 1P max {src.ONE_P_MAX} Hz;"
             f" required margin {100 * src.MARGIN_1P:.0f} % (A-359)",
             f"  -> f1 at least {f_need:.4f} Hz -> rocking stiffness at least"
             f" {k_need / 1e9:.0f} GN m/rad",
             "  founding soil                            K GN m/rad   f1 Hz   margin"]
    rows = []
    for name, s_ in src.SOILS.items():
        k = st.rotational_stiffness(s_["g_mpa"] * 1e6, r, s_["nu"])
        f = st.frequency_with_foundation(src.F1_FIXED, k, m_top, src.HUB)
        margin = 100 * (f / src.ONE_P_MAX - 1)
        flag = "" if k >= k_need else " short"
        lines.append(f"  {name:40s} {k / 1e9:10.0f}   {f:5.3f}   {margin:4.1f} %{flag}")
        rows.append((name.split()[0], f"{k / 1e9:.0f}", f"{f:.4f}"))
    csv("ch30-stiffness.csv", "soil,k,f", rows)
    csv("ch30-fk.csv", "k,f", [(kk, f"{st.frequency_with_foundation(src.F1_FIXED, kk * 1e9, m_top, src.HUB):.4f}")
                               for kk in range(40, 620, 20)])
    lines += ["  the margin requirement, turned into a stiffness, is met on",
              "  dense ground and missed at T07 (with or without the high",
              "  water): there stiffness, not strength, decides the",
              "  foundation - the schemes of lesson D are compared on it"]
    emit("b_frequency", lines)


def deflection() -> None:
    i_eq = math.pi / 64 * (4.4 ** 4 - (4.4 - 2 * 0.031) ** 4)
    p = src.LOADS["production (peak)"]["m_mnm"] * 1e6 / src.HUB
    tip = p * src.HUB ** 3 / (3 * E * i_eq)
    k = st.rotational_stiffness(25e6, src.FOUNDATION["r"], 0.35)
    tilt = src.LOADS["production (peak)"]["m_mnm"] * 1e6 / k
    lines = ["tower-top deflection at peak thrust (equivalent tube, teaching)",
             f"  bending of the tower: {tip:.2f} m at {src.HUB:.0f} m",
             f"  rocking of the base on T07 soil: tilt {1000 * tilt:.2f} mrad ->"
             f" {tilt * src.HUB:.2f} m at the top",
             "  the top sways more than a metre in normal operation: that",
             "  is design, not damage; what is checked is the permanent",
             "  tilt of the foundation after settlement (verticality",
             "  surveys, lesson C) and the blade-tower clearance (ch 11)"]
    emit("b_deflection", lines)


if __name__ == "__main__":
    stresses()
    fatigue()
    door()
    foundation_frequency()
    deflection()
