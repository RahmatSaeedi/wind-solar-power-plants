"""Chapter 19, further lessons: theoretical capacity from Faraday's law,
uneven ageing from a temperature spread inside a rack, the DC busbar
current, the PCS voltage window against the rack voltage over SOC and
life, estimating capacity from a partial charge, footprint against an
authority's spacing, the site capacity test, and transport mass.

Run from the project root:   python -m companion.ch19.examples_k
Writes companion/ch19/expected/k_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290 to A-296.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import storage as st

C, B = src.LFP, src.BUILD
F_CONST = 96485.0                                    # C/mol
N_RACK = B["s_module"] * B["m_rack"]


# [start: faraday]
def specific_capacity(molar_mass_g: float, electrons: float = 1.0) -> float:
    """Theoretical capacity of an active material, mAh/g: n F / M."""
    return electrons * F_CONST / molar_mass_g / 3.6
# [end: faraday]


def faraday() -> None:
    lfp = specific_capacity(157.76)                  # LiFePO4
    graphite = specific_capacity(6 * 12.011)         # LiC6, per C6
    lines = ["theoretical capacity from Faraday's law (one Li per formula unit):",
             f"  LiFePO4  M = 157.76 g/mol: {lfp:.0f} mAh/g",
             f"  graphite C6 M = 72.07 g/mol: {graphite:.0f} mAh/g",
             f"  active material for one 314 Ah cell at the theoretical value:",
             f"    LFP {314e3 / lfp / 1000:.2f} kg, graphite {314e3 / graphite / 1000:.2f} kg",
             "  real cells use less than the theoretical capacity and carry",
             "  foils, separator, electrolyte and case: the 5.5 kg cell",
             "  holds about a third of its mass as positive active material"]
    emit("k_faraday", lines)


def thermal_spread() -> None:
    """Cells of a rack at different temperatures age differently."""
    f = src.FADE
    lines = ["ten years of calendar fade with a temperature spread in a rack",
             "  (mean 25 C, mean SOC 36 %, A-292, A-296):",
             "  cooling           spread   coolest   hottest   weakest-cell loss"]
    for name, dt in (("liquid", 1.5), ("air, good", 4.0), ("air, poor", 8.0)):
        lo = float(st.calendar_fade(10, 25.0 - dt / 2, 0.36, f["k25"], f["ea_ev"]))
        hi = float(st.calendar_fade(10, 25.0 + dt / 2, 0.36, f["k25"], f["ea_ev"]))
        lines.append(f"  {name:16s}  {dt:4.1f} K   {100 * lo:6.2f} %   {100 * hi:6.2f} %"
                     f"   {100 * (hi - lo):9.2f} pts more")
    lines += ["  the hottest cells age fastest and set the string's capacity",
              "  (section C, grading); a cooling design is judged on spread as",
              "  much as on mean temperature"]
    emit("k_spread", lines)


def busbar() -> None:
    v_rack = N_RACK * 3.25
    lines = ["DC current in a container at full power (A-296):",
             "  C-rate   rack A   container bus A   copper mm2 at 2 A/mm2"]
    for cr in (0.5, 1.0):
        p_cont = cr * 5.02e6
        i_rack = p_cont / B["r_container"] / v_rack
        i_bus = i_rack * B["r_container"]
        lines.append(f"  {cr:6.1f}   {i_rack:6.0f}   {i_bus:15,.0f}   {i_bus / 2:21,.0f}")
    lines += ["  the bus carries the sum of the racks; its section is set by",
              "  heating at the steady current and by the short-circuit force",
              "  (example 19.13), whichever is larger; 2 A/mm2 is a teaching",
              "  density, the maker's thermal test decides"]
    emit("k_busbar", lines)


def pcs_window() -> None:
    """Rack voltage across SOC and life against a teaching PCS window
    (1,000-1,500 V DC, full power only above 1,150 V)."""
    lines = ["rack voltage while discharging at 0.5 C against the PCS window",
             "  (full power above 1,150 V, A-296):",
             "  SOC %   new V    end of life V   PCS power new   end of life"]
    rows = []
    for s in (0.10, 0.20, 0.50, 0.80, 0.90):
        out = []
        for rg in (1.0, src.THERMAL["r_growth_eol"]):
            v = N_RACK * (float(st.ocv(s)) - 0.5 * C.q_ah * (C.r0 + C.r1) * rg)
            share = min(1.0, v / 1150.0)
            out += [v, share]
        lines.append(f"  {100 * s:5.0f}  {out[0]:7,.0f}  {out[2]:13,.0f}   {100 * out[1]:12.0f} %"
                     f"   {100 * out[3]:9.0f} %")
    lines += ["  above 1,150 V the PCS gives full power; the rack stays above",
              "  it across the window even at end of life, so the window is",
              "  not cut by the PCS; with fewer cells in series it would be:",
              "  the DC window is an interface between two makers"]
    emit("k_pcs", lines)


def soh_estimate() -> None:
    """Capacity from a partial charge: Ah counted between two OCV readings
    (2 mV error each), endpoints near the ends or in the middle."""
    q_true = 0.9 * C.q_ah
    lines = ["capacity estimated from a partial charge, OCV error 2 mV each end:",
             "  endpoints     SOC error each   capacity error"]
    for a, b in ((0.10, 0.90), (0.15, 0.85), (0.30, 0.70)):
        ea = 0.002 / float(st.ocv_slope(a))
        eb = 0.002 / float(st.ocv_slope(b))
        err = math.hypot(ea, eb) / (b - a)
        lines.append(f"  {100 * a:3.0f}-{100 * b:3.0f} %     {100 * ea:4.2f} / {100 * eb:4.2f} %"
                     f"      {100 * err:6.2f} %")
    lines += [f"  (true capacity {q_true:.0f} Ah, 90 % health)",
              "  on LFP a capacity estimate needs endpoints on the steep",
              "  ends of the curve; a battery that never leaves the middle",
              "  cannot report its own health well"]
    emit("k_soh", lines)


def footprint() -> None:
    l, w = 12.2, 2.5                                 # container, m (A-296)
    lines = ["footprint of 8 containers in 2 rows of 4 and 4 PCS skids",
             "  against a spacing s set by the authority (not given here):",
             "  s m    battery area m2   with PCS row and 6 m access"]
    for s in (1.5, 3.0, 6.0):
        length = 4 * l + 3 * s
        width = 2 * w + s
        area = length * width
        full = (length + 12) * (width + 3 + 12)
        lines.append(f"  {s:4.1f}   {area:15,.0f}   {full:27,.0f}")
    lines += ["  the spacing the authority sets from the propagation evidence",
              "  can double the battery area; it belongs in the layout before the",
              "  substation and roads are fixed (chapter 14)"]
    emit("k_footprint", lines)


def sat_test() -> None:
    e_poc = 40.13 * 0.8 * math.sqrt(0.86)
    t_dis = e_poc / 20.0
    lines = ["site capacity test of S1 (teaching plan, A-296):",
             "  charge to 90 % from the plant, rest 1 h, discharge at 20 MW",
             f"  to 10 %: about {e_poc:.1f} MWh in {t_dis:.1f} h at the revenue meter,",
             "  rest 1 h, recharge; with the round trip measured on the same",
             "  cycle; needs 20 MW of export room for 1.5 h and a sunny or",
             "  windy morning to charge: a test window agreed with the",
             "  operator and the buyer (chapter 50)"]
    emit("k_sat", lines)


def transport() -> None:
    mass = 38.0                                      # t per container (A-296)
    lines = ["transport and placing (teaching masses, A-296):",
             f"  container about {mass:.0f} t loaded with cells; 8 containers",
             f"  {8 * mass:.0f} t: abnormal loads on some roads (chapter 14 access)",
             "  shipped at a low SOC (transport rules may set it); energy",
             "  stored on the truck at 30 % SOC: "
             f"{5.02 * 0.30:.1f} MWh a container",
             "  crane, lifting points and the foundation level are interfaces",
             "  with the civil contractor; lifting plans are specialists' work"]
    emit("k_transport", lines)


def windows() -> None:
    """The lab D rule with three SOC windows: energy, value, cycles and
    health after ten years (A-292, prices A-273)."""
    from companion.ch15 import sources as s15
    from companion.ch19 import lab_d
    from plantp.wind import rainflow
    r = s15.plant_year()
    pr = src.prices()
    f = src.FADE
    lines = ["the SOC window: energy against life (lab D rule, one year):",
             "  window     discharged MWh   value k u   cycles/yr   health yr 10"]
    rows = []
    keep = (lab_d.LO, lab_d.HI)
    for lo, hi in ((0.20, 0.80), (0.10, 0.90), (0.05, 0.95)):
        lab_d.LO, lab_d.HI = lo * 40.0, hi * 40.0
        soc, ch, dis = lab_d.dispatch(r["net"], r["poc"], r["outage"])
        val = float((pr * (dis - ch)).sum()) / 1000
        cyc = st.cycle_fade(rainflow(lab_d.turning(soc / 40.0)), f["n100"], f["k"],
                            f["loss_at_life"])
        cal = float(st.calendar_fade(10, 25.0, float(soc.mean()) / 40.0, f["k25"], f["ea_ev"]))
        h10 = 100 * (1 - cal - 10 * cyc)
        lines.append(f"  {100 * lo:3.0f}-{100 * hi:3.0f} %   {dis.sum():14,.0f}   {val:9,.0f}"
                     f"   {dis.sum() / lab_d.ETA / (40.0 * (hi - lo)):9.0f}   {h10:11.1f} %")
        rows.append((f"{100 * (hi - lo):.0f}", f"{dis.sum():.0f}", f"{h10:.2f}"))
    lab_d.LO, lab_d.HI = keep
    lines += ["  a wider window sells more energy each day but ages the cells",
              "  faster (deeper cycles, more time near the ends); the choice",
              "  is an economic one (chapter 21) bounded by the warranty"]
    emit("k_windows", lines)
    csv("ch19-windows.csv", "w,mwh,h10", rows)


if __name__ == "__main__":
    windows()
    faraday()
    thermal_spread()
    busbar()
    pcs_window()
    soh_estimate()
    footprint()
    sat_test()
    transport()
