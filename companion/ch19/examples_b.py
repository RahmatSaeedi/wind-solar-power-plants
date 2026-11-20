"""Chapter 19, section B - product architecture and design: the build-up
of the S1 battery from cell to system against the 1,500 V DC limit, the
prospective short-circuit current of a rack and of a container DC bus,
heat generation from the beginning to the end of life and the container
heat balance through the hottest week, and the cell count of three cell
formats.

Run from the project root:   python -m companion.ch19.examples_b
Writes companion/ch19/expected/b_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290 and A-291.
"""
from __future__ import annotations

import numpy as np

from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import datapack, storage as st

C, B, T = src.LFP, src.BUILD, src.THERMAL


def buildup() -> dict:
    b = st.build_up(C, src.V_NOM["LFP"], B["s_module"], B["m_rack"],
                    B["r_container"], B["containers"])
    lines = ["S1 battery from cell to system (A-290):",
             f"  cell     LFP {C.q_ah:.0f} Ah, {src.V_NOM['LFP']} V, {C.q_ah * 3.2 / 1000:.3f} kWh",
             f"  module   1P{B['s_module']}S: {b['module_v']:.1f} V, {b['module_kwh']:.1f} kWh",
             f"  rack     {B['m_rack']} modules in series: {b['rack_v_nom']:,.0f} V nominal,"
             f" {b['rack_v_min']:,.0f}-{b['rack_v_max']:,.0f} V,",
             f"           {b['rack_kwh']:.0f} kWh",
             f"  container {B['r_container']} racks in parallel: {b['container_mwh']:.2f} MWh",
             f"  system   {B['containers']} containers: {b['system_mwh']:.2f} MWh, {b['cells']:,} cells",
             f"  power    {B['pcs']} PCS x {B['pcs_mw']:.0f} MW = {B['pcs'] * B['pcs_mw']:.0f} MW:"
             f" {B['pcs'] * B['pcs_mw'] / b['system_mwh']:.2f} C at the cells",
             f"  check: rack maximum {b['rack_v_max']:,.0f} V stays below 1,500 V DC",
             "    (at 3.65 V a cell it would be 1,518 V: the charge limit is a",
             "    design choice tied to the DC voltage class of the PCS)"]
    emit("b_buildup", lines)
    return b


def short_circuit() -> None:
    """Prospective current: rack voltage over rack resistance (teaching)."""
    n = B["s_module"] * B["m_rack"]
    r_rack = n * C.r0 + 0.004                       # cells plus busbars and fuse
    v = n * 3.25                                    # mid-window OCV
    i_rack = v / r_rack / 1000
    i_bus = i_rack * B["r_container"]
    lines = ["prospective short-circuit current (DC, teaching, A-290):",
             f"  rack: {v:,.0f} V over {1000 * r_rack:.0f} mohm = {i_rack:.1f} kA",
             f"  container DC bus fed by {B['r_container']} racks: {i_bus:.0f} kA",
             "  each rack needs its own fuse and switch that can break its",
             "  own fault at up to 1,500 V DC; a fault on the shared DC bus",
             "  sees all racks at once, so the bus, its supports and the",
             "  PCS input are rated for that current; ratings and the",
             "  coordination come from the maker with test evidence"]
    emit("b_short", lines)


def heat() -> None:
    """Heat at 0.5 C from the beginning to the end of life, then the
    container through the hottest week of the data year."""
    n_cont = B["s_module"] * B["m_rack"] * B["r_container"]
    p_cont = B["pcs"] * B["pcs_mw"] / B["containers"] * 1e6           # W
    v_rack = B["s_module"] * B["m_rack"] * 3.25
    i = p_cont / B["r_container"] / v_rack                            # A per rack
    q_bol = n_cont * i ** 2 * (C.r0 + C.r1) / 1000                    # kW
    q_eol = q_bol * T["r_growth_eol"]
    h = datapack.load_hourly()
    t_amb = h["t_air_c"].to_numpy(float)
    hour = np.arange(8760) % 24
    k0 = int(np.argmax(np.convolve(t_amb, np.ones(168), "valid")))
    week = slice(k0, k0 + 168)
    ta = t_amb[week]
    hr = hour[week]
    run = ((hr >= 10) & (hr < 15)) | ((hr >= 18) & (hr < 22))         # S1 duty
    sun = np.clip(np.sin(np.pi * (hr - 6) / 12), 0, None) * T["solar_kw_peak"]
    lines = ["heat of one container at 0.5 C (A-291):",
             f"  rack current {i:.0f} A; heat at beginning of life {q_bol:.0f} kW,"
             f" at end of life {q_eol:.0f} kW",
             f"  hottest week of the data year: {ta.min():.1f}-{ta.max():.1f} C outside",
             "  HVAC kW   resistance   inside max C   hours above 30 C"]
    rows = []
    for hv in (60.0, 100.0, 120.0):
        for name, q in (("BOL", q_bol), ("EOL", q_eol)):
            tin, rem = st.container_heat(ta, np.where(run, q, 0.0), T["ua_kw_k"],
                                         T["c_kwh_k"], hv, T["setpoint"], sun, T["aux_kw"])
            lines.append(f"  {hv:6.0f}     {name:9s}  {tin.max():12.1f}   {int((tin > 30).sum()):10d}")
            if hv == 100.0:
                rows.append((name, tin))
    peak_need = q_eol + T["aux_kw"] + T["solar_kw_peak"] + T["ua_kw_k"] * (ta.max() - T["setpoint"])
    lines += [f"  heat to remove at the worst hour, end of life: {peak_need:.0f} kW",
              "  the HVAC is sized on end-of-life resistance in the hottest",
              "  hour with the sun on the walls, not on the new battery at",
              "  25 C: that is the 120 kW of interface IF-006 (chapter 18)"]
    emit("b_heat", lines)
    csv("ch19-heat.csv", "h,ta,bol,eol",
        [(k, f"{ta[k]:.2f}", f"{rows[0][1][k]:.2f}", f"{rows[1][1][k]:.2f}") for k in range(168)])


def formats() -> None:
    e_sys = 40.0e6                                   # Wh
    rows = (("cylindrical", 5.0, 3.6), ("pouch", 60.0, 3.7), ("prismatic", 314.0, 3.2))
    lines = ["cells needed for 40 MWh by format (teaching sizes):",
             "  format        Ah    V     Wh/cell   cells        joints (2/cell)"]
    for name, ah, v in rows:
        n = e_sys / (ah * v)
        lines.append(f"  {name:12s} {ah:5.0f}  {v:3.1f}  {ah * v:8.0f}  {n:11,.0f}  {2 * n:13,.0f}")
    lines += ["  fewer, larger cells mean fewer welds and sensors, but more",
              "  energy in each cell that fails; the format moves the risk,",
              "  it does not remove it"]
    emit("b_formats", lines)


if __name__ == "__main__":
    buildup()
    short_circuit()
    heat()
    formats()
