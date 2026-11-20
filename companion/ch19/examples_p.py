"""Chapter 19, final lessons: how racks in parallel share current and
what flows when racks at different SOC are closed together, winter
heating of a container, two battery offers compared on levelised cost
of storage (LCOS) over 15 years, and the battery's own availability.

Run from the project root:   python -m companion.ch19.examples_p
Writes companion/ch19/expected/p_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290 to A-298.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import datapack, storage as st
from plantp.yieldrisk import annuity

C, B, T = src.LFP, src.BUILD, src.THERMAL
N_RACK = B["s_module"] * B["m_rack"]
R_RACK = N_RACK * (C.r0 + C.r1) + 0.004             # ohm, with busbars


def parallel() -> None:
    rng = np.random.default_rng(1991)
    r = R_RACK * rng.normal(1.0, 0.05, B["r_container"])
    i_tot = 0.5 * 5.02e6 / 1352
    share = (1 / r) / (1 / r).sum() * i_tot
    lines = ["12 racks in parallel at 0.5 C, rack resistance spread 5 % (A-298):",
             f"  mean rack current {i_tot / 12:.0f} A; highest {share.max():.0f} A,"
             f" lowest {share.min():.0f} A ({100 * (share.max() / share.min() - 1):.0f} % apart)",
             "  closing a rack onto the others at a different SOC (OCV gap):",
             "  SOC of the rack vs the bus   gap V   current at closing A"]
    for s_rack, s_bus in ((0.50, 0.52), (0.85, 0.90), (0.10, 0.15)):
        dv = N_RACK * float(st.ocv(s_bus) - st.ocv(s_rack))
        lines.append(f"  {100 * s_rack:5.0f} % vs {100 * s_bus:3.0f} %             "
                     f"{dv:6.1f}   {dv / (2 * R_RACK):18.0f}")
    lines += ["  the lowest-resistance rack works hardest and ages fastest;",
              "  racks are closed onto the bus only when their voltages",
              "  match within a limit, or through the pre-charge path"]
    emit("p_parallel", lines)


def heating() -> None:
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy(float)
    keep = 10.0                                          # minimum inside, C
    need_kw = np.clip(T["ua_kw_k"] * (keep - t), 0, None)
    e_kwh = need_kw.sum()                               # resistive heating, COP 1
    lines = ["keeping a container at 10 C or more in winter (data-year air):",
             f"  hours below 10 C outside: {int((t < keep).sum()):,}",
             f"  heat needed {e_kwh / 1000:.1f} MWh a container a year; for 8:"
             f" {8 * e_kwh / 1000:.0f} MWh",
             "  (resistive heating; the cells' own heat helps on working",
             "  days and is left out here, so this is an upper bound)",
             "  about a third of the cooling electricity, and it decides whether midday",
             "  charging works in January (@exm-ch19-power)"]
    lines = [ln.replace(" (@exm-ch19-power)", " (the power map)") for ln in lines]
    emit("p_heating", lines)


# [start: lcos]
def lcos(capex: float, opex_share: float, rt: float, fade: float,
         years: int = 15, rate: float = 0.06, e_nom: float = 40.13,
         window: float = 0.8, cycles: int = 365) -> tuple[float, float]:
    """Levelised cost of storage (u per MWh discharged at the POC) and
    the discounted energy: cost / energy, both discounted."""
    eta = math.sqrt(rt)
    pv_cost = capex + sum(opex_share * capex / (1 + rate) ** y
                          for y in range(1, years + 1))
    pv_e = sum(e_nom * window * eta * (1 - fade * y) * cycles / (1 + rate) ** y
               for y in range(1, years + 1))
    return 1000.0 * pv_cost / pv_e, pv_e
# [end: lcos]


def offers() -> None:
    offers_ = {"offer X": (12500.0, 0.025, 0.85, 0.025),
               "offer Y": (14000.0, 0.020, 0.88, 0.018)}
    lines = ["two battery offers over 15 years (teaching, A-298):",
             "  offer    capex k u  opex  round trip  fade/yr   LCOS u/MWh"]
    rows = []
    for k, (capex, ox, rt, fd) in offers_.items():
        c, e = lcos(capex, ox, rt, fd)
        lines.append(f"  {k:8s} {capex:9,.0f}  {100 * ox:3.1f} %  {100 * rt:8.0f} %"
                     f"  {100 * fd:5.1f} %   {c:10.1f}")
        pv_capex = 1000.0 * capex / e
        rows.append((1 if k == "offer X" else 2, f"{pv_capex:.2f}", f"{c - pv_capex:.2f}"))
    lines += ["  almost the same cost per MWh: the dearer offer's better",
              "  round trip and slower fade just pay its price; the cost of",
              "  the charging energy, left out here, tips it towards Y; the",
              "  warranty terms and the evidence behind the fade (chapter 39)",
              "  decide whether either number holds"]
    emit("p_offers", lines)
    csv("ch19-lcos.csv", "o,capex,opex", rows)


def availability() -> None:
    pcs = 4 * 0.5 * 48 / 8760 / 4                    # mean share of power lost
    racks = 96 * 2.0 * 8 / 8760 / 96
    hvac = 8 * 0.3 * 24 / 8760 / 8
    lines = ["availability of the battery itself (teaching rates, A-298):",
             "  item                 failures/yr   hours each   power lost while out",
             "  PCS (4 x 5 MW)              2.0          48      a quarter",
             "  rack trips (96)           192.0           8      a 96th",
             "  HVAC unit (8)               2.4          24      one container",
             f"  energy-based availability about {100 * (1 - pcs - racks - hvac):.2f} %",
             "  frequent rack trips cost little energy but much attention;",
             "  the PCS dominates the lost energy; spares and response times",
             "  are what the service contract buys (chapter 51)"]
    emit("p_availability", lines)


if __name__ == "__main__":
    parallel()
    heating()
    offers()
    availability()
