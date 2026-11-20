"""Chapter 18, section A - operating concepts and coupling: the
conversion chains of an AC- and a DC-coupled battery, and a year of the
S1 battery (20 MW, 40 MWh) in both couplings with model 15.1: what each
can store (DC clipping only reaches a DC-coupled battery; wind and the
export limit only an AC-coupled one), what returns to the grid, and
where the DC coupling's shared inverter limits it.

Run from the project root:   python -m companion.ch18.examples_a
Writes companion/ch18/expected/a_*.txt.
Teaching efficiencies A-286; model 15.1.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch18 import sources as src
from companion.ch18.common import emit
from plantp import architecture as ar

E = src.EFF


def chains() -> None:
    ac = ar.ac_coupled(E["pv_inverter"], E["bess_inverter"], E["cell_round_trip"])
    dc = ar.dc_coupled(E["pv_inverter"], E["dcdc"], E["cell_round_trip"])
    lines = ["conversion chains of a battery storing PV energy (A-286):",
             f"  AC-coupled: PV inverter {E['pv_inverter']}, battery inverter"
             f" {E['bess_inverter']} twice, cells {E['cell_round_trip']}",
             f"    PV energy back to the grid via the battery: {100 * ac['pv_to_grid_via_battery']:.1f} %",
             f"  DC-coupled: DC/DC {E['dcdc']} twice, cells, PV inverter once",
             f"    PV energy back to the grid via the battery: {100 * dc['pv_to_grid_via_battery']:.1f} %",
             f"  the DC route saves one AC conversion: +{100 * (dc['pv_to_grid_via_battery'] - ac['pv_to_grid_via_battery']):.1f}"
             " points on every MWh shifted"]
    emit("a_chains", lines)


def year(kind: str) -> dict:
    """One year of the S1 battery: store what is lost (DC clipping for DC
    coupling; export-limit curtailment for both; wind only for AC), send
    back from 18:00 to 22:00 within the limits."""
    r = s15.plant_year()
    hour = np.arange(8760) % 24
    clip_dc = (r["pv_inv"] - r["pv_clip"]) / E["pv_inverter"]   # DC that the inverter dropped
    curt = r["curtailed"]
    one = math.sqrt(E["cell_round_trip"])
    soc, lo, hi = 4.0, 4.0, 36.0
    stored = back = 0.0
    for k in range(8760):
        if kind == "DC":
            # clipped DC, and the PV share of any export-limit curtailment
            avail = clip_dc[k] + min(curt[k], r["pv_clip"][k]) / E["pv_inverter"]
            conv_in, conv_out = E["dcdc"], E["dcdc"] * E["pv_inverter"]
            room_out = max(49.0 - r["pv_clip"][k], 0.0)          # shared PV inverter
        else:
            avail = curt[k]
            conv_in, conv_out = E["bess_inverter"], E["bess_inverter"]
            room_out = 20.0
        ch = min(avail, 20.0, (hi - soc) / (conv_in * one))
        soc += ch * conv_in * one
        stored += ch
        if 18 <= hour[k] < 22 and soc > lo:
            head = max(100.0 - r["delivered"][k], 0.0)
            d = min(20.0, room_out, head, (soc - lo) * one * conv_out)
            soc -= d / (one * conv_out)
            back += d
    return {"stored": stored, "back": back}


def couplings() -> None:
    r = s15.plant_year()
    clip_ac = float((r["pv_inv"] - r["pv_clip"]).sum())
    curt = float(r["curtailed"].sum())
    ac, dc = year("AC"), year("DC")
    lines = ["S1 battery used only for energy that would be lost (one year):",
             f"  lost today: PV clipping {clip_ac:,.0f} MWh (AC equivalent), export limit"
             f" {curt:,.0f} MWh",
             f"  AC-coupled: stores {ac['stored']:,.0f} MWh, returns {ac['back']:,.0f} MWh",
             f"  DC-coupled: stores {dc['stored']:,.0f} MWh, returns {dc['back']:,.0f} MWh",
             "  only the DC coupling reaches the clipped DC energy; the AC",
             "  coupling can also charge from wind and the grid and discharge",
             "  at any hour without sharing the PV inverter; the market uses",
             "  of chapter 19, not clipping, decide the coupling here"]
    emit("a_couplings", lines)


def modes() -> None:
    lines = ["operating modes and what each needs (summary, teaching):",
             "  grid-connected (Plant P's mode): grid sets voltage and",
             "    frequency; units follow it (grid-following inverters)",
             "  islanded: a grid-forming source sets voltage and frequency;",
             "    storage or a generator balances every second; protection",
             "    must work with small fault currents",
             "  hybrid (grid-connected with a planned island for critical",
             "    loads): a transfer switch, a grid-forming battery inverter",
             "    and the operator's permission (chapters 19, 25, 28)"]
    emit("a_modes", lines)


if __name__ == "__main__":
    chains()
    couplings()
    modes()
