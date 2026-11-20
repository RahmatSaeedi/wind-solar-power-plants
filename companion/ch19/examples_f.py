"""Chapter 19, more of sections A and B: the power the cell can give and
take against SOC and temperature (the BMS power map), standby losses,
the auxiliary energy of a year, pre-charge of the DC link, leakage
through a falling insulation resistance, and the cost of storage against
duration for a lithium-ion and a flow battery.

Run from the project root:   python -m companion.ch19.examples_f
Writes companion/ch19/expected/f_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290, A-291 and A-295.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import datapack, storage as st

C, B, T = src.LFP, src.BUILD, src.THERMAL
N_CELLS = B["containers"] * B["r_container"] * B["s_module"] * B["m_rack"]


# [start: power]
LIMITS = {   # cell temperature C: (discharge C-rate, charge C-rate), A-295
    -10.0: (0.3, 0.0), 0.0: (0.5, 0.2), 10.0: (1.0, 0.5),
    25.0: (1.0, 1.0), 45.0: (1.0, 0.5), 55.0: (0.3, 0.0),
}


def r_at(temp_c: float, r25: float, ea_ev: float = 0.3) -> float:
    """Cell resistance at a temperature (Arrhenius, teaching)."""
    kb = 8.617e-5
    return r25 * math.exp(ea_ev / kb * (1 / (temp_c + 273.15) - 1 / 298.15))


def power_limits(soc: float, temp_c: float):
    """Discharge and charge power (W) of one cell: the maker's current
    limit for the temperature, and the voltage limits."""
    r = r_at(temp_c, C.r0 + C.r1)
    v = float(st.ocv(soc))
    c_dis, c_chg = LIMITS[temp_c]
    i_d = min((v - C.v_min) / r, c_dis * C.q_ah)
    i_c = min((C.v_max - v) / r, c_chg * C.q_ah)
    return (v - r * i_d) * i_d, (v + r * i_c) * i_c
# [end: power]


def power_map() -> None:
    lines = ["power the whole battery (39,936 cells) can give and take, MW,",
             "  from the maker's current limits by temperature (A-295):",
             "  cell C   dis C-rate  chg C-rate   discharge MW   charge MW",
             "           (at 50 % SOC; the PCS caps both at 20 MW)"]
    for t, (cd, cc) in LIMITS.items():
        d, c = power_limits(0.5, t)
        lines.append(f"  {t:5.0f}    {cd:9.1f}  {cc:10.1f}   {d * N_CELLS / 1e6:12.1f}"
                     f"   {c * N_CELLS / 1e6:9.1f}")
    rows = []
    for s in np.linspace(0.02, 0.98, 49):
        d0, c0 = power_limits(s, 0.0)
        d25, c25 = power_limits(s, 25.0)
        rows.append((f"{100 * s:.0f}", f"{min(d0 * N_CELLS / 1e6, 20):.2f}",
                     f"{min(c0 * N_CELLS / 1e6, 20):.2f}",
                     f"{min(d25 * N_CELLS / 1e6, 20):.2f}", f"{min(c25 * N_CELLS / 1e6, 20):.2f}"))
    lines += ["  between 10 and 45 C the 20 MW converter is the cap; a cold",
              "  battery (0 C) takes only about 8 MW of charge and none below",
              "  freezing; the BMS sends this limit to the PCS every second",
              "  and the plant controller must plan with it (chapter 20); the",
              "  container is kept warm in winter so that midday charging",
              "  is not lost"]
    emit("f_power", lines)
    csv("ch19-power.csv", "soc,d0,c0,d25,c25", rows)


def standby() -> None:
    leak_ma = 11.0
    sd_day = leak_ma / 1000 * 24 / C.q_ah                        # SOC a day
    e_usable = 40.13 * 0.8
    sd_mwh = sd_day * 40.13
    bms_kw, hvac_idle_kw = 0.5, 6.0                                # per container
    aux_mwh = (bms_kw + hvac_idle_kw) * B["containers"] * 24 / 1000
    lines = ["a week on standby, battery full (teaching, A-291):",
             f"  self-discharge {100 * sd_day:.3f} % a day = {sd_mwh * 1000:.0f} kWh a day",
             f"  BMS and idle HVAC {bms_kw + hvac_idle_kw:.1f} kW x {B['containers']}"
             f" containers = {aux_mwh * 1000:,.0f} kWh a day",
             f"  in a week: {7 * (sd_mwh + aux_mwh):.2f} MWh, {100 * 7 * (sd_mwh + aux_mwh) / e_usable:.1f}"
             " % of the usable energy",
             "  standby costs more in auxiliaries than in chemistry; the",
             "  auxiliaries come from the battery or from the grid, and",
             "  the meter and the contract must say which (chapter 17)"]
    emit("f_standby", lines)


def aux_year() -> None:
    """HVAC electricity for a year of the lab D duty (COP 3, teaching)."""
    h = datapack.load_hourly()
    t_amb = h["t_air_c"].to_numpy(float)
    hour = np.arange(8760) % 24
    run = ((hour >= 10) & (hour < 15)) | ((hour >= 18) & (hour < 22))
    p_cont = B["pcs"] * B["pcs_mw"] / B["containers"] * 1e6
    i = p_cont / B["r_container"] / (B["s_module"] * B["m_rack"] * 3.25)
    n_cont = B["s_module"] * B["m_rack"] * B["r_container"]
    q = n_cont * i ** 2 * (C.r0 + C.r1) / 1000 * 1.3              # mid-life R
    sun = np.clip(np.sin(np.pi * (hour - 6) / 12), 0, None) * T["solar_kw_peak"]
    _, rem = st.container_heat(t_amb, np.where(run, q, 0.0), T["ua_kw_k"], T["c_kwh_k"],
                               120.0, T["setpoint"], sun, T["aux_kw"])
    cop = 3.0
    hvac_mwh = rem.sum() / cop / 1000 * B["containers"]
    bms_mwh = 0.5 * 8760 / 1000 * B["containers"]
    dis = 10817.0
    rt = st.round_trip(C, 0.5) * src.PCS_ETA ** 2 * src.MV_ETA ** 2
    lines = ["auxiliary energy of a year (lab D duty, mid-life resistance):",
             f"  heat removed {rem.sum() / 1000:,.0f} MWh a container; HVAC at COP {cop:.0f}:"
             f" {hvac_mwh:,.0f} MWh for 8",
             f"  BMS and controls: {bms_mwh:,.0f} MWh",
             f"  total {hvac_mwh + bms_mwh:,.0f} MWh = {100 * (hvac_mwh + bms_mwh) / dis:.1f} % of the"
             f" {dis:,.0f} MWh discharged",
             f"  with it the 0.5 C model's {100 * rt:.1f} % round trip (without",
             f"  auxiliaries) falls to {100 * rt * (1 - (hvac_mwh + bms_mwh) / dis):.1f} %:"
             " the data pack's 86 % is this",
             "  winter heating is left out here; the site goes below",
             "  freezing in the data year, so it is one more auxiliary load"]
    emit("f_aux", lines)


def precharge() -> None:
    c_dc, v = 0.020, 1331.0                       # PCS DC-link capacitance (A-295)
    i_lim = 20.0
    r = v / i_lim
    tau = r * c_dc
    e = 0.5 * c_dc * v ** 2
    lines = ["pre-charge of a PCS DC link from one rack (teaching, A-295):",
             f"  capacitance {1000 * c_dc:.0f} mF at {v:,.0f} V; inrush limited to {i_lim:.0f} A",
             f"  resistor {r:.1f} ohm; time constant {tau:.2f} s; 5 tau {5 * tau:.1f} s",
             f"  energy into the resistor {e / 1000:.1f} kJ; peak power {v ** 2 / r / 1000:.1f} kW",
             "  without pre-charge the rack would close onto an empty",
             "  capacitor: the current is set only by milliohms and the",
             "  contactor welds; the resistor is sized for the energy pulse,",
             "  not the steady power"]
    emit("f_precharge", lines)


def insulation() -> None:
    v = 1498.0
    lines = ["leakage to earth of a floating DC system at 1,498 V (teaching):",
             "  insulation resistance   leakage current"]
    for r in (1e6, 1e5, 1e4, 1e3):
        lines.append(f"  {r:>17,.0f} ohm  {1000 * v / r:10.1f} mA")
    lines += ["  a single fault to earth does not trip a floating system, so",
              "  it can go unnoticed until a second fault makes a short;",
              "  the insulation monitor alarms on the first fault; alarm",
              "  levels come from the maker and the applicable standard"]
    emit("f_insulation", lines)


def durations() -> None:
    """Cost per MWh of storage capacity against duration (teaching A-295)."""
    techs = {"lithium-ion": (150.0, 250.0), "flow battery": (600.0, 120.0)}
    lines = ["cost of storage against duration (k u per MWh of capacity, A-295):",
             "  hours   lithium-ion   flow battery"]
    rows = []
    for h in (1, 2, 4, 6, 8, 10, 12):
        v = [(p + e * h) / h for p, e in techs.values()]
        lines.append(f"  {h:5d}   {v[0]:11.0f}   {v[1]:12.0f}")
        rows.append((h, f"{v[0]:.1f}", f"{v[1]:.1f}"))
    cross = (techs["flow battery"][0] - techs["lithium-ion"][0]) / (
        techs["lithium-ion"][1] - techs["flow battery"][1])
    lines += [f"  cross-over at {cross:.1f} hours with these teaching costs: a",
              "  technology whose power and energy are bought apart wins at",
              "  long durations; round trip, life, space and the maturity of",
              "  the supply chain decide the rest"]
    emit("f_durations", lines)
    csv("ch19-duration.csv", "h,li,flow", rows)


if __name__ == "__main__":
    power_map()
    standby()
    aux_year()
    precharge()
    insulation()
    durations()
