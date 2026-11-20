"""Chapter 19 - three integrated Plant P examples: the S1 battery from
cell to POC (introductory), a year of duty and twenty years of health
(intermediate), and the safety-bounded battery design basis (integrated).

Run from the project root:   python -m companion.ch19.integrated
Writes companion/ch19/expected/i_*.txt.
"""
from __future__ import annotations

import math

from companion.ch19 import examples_b as eb, lab_d, sources as src
from companion.ch19.common import emit


def cell_to_poc() -> None:
    b = eb.buildup()
    eta = math.sqrt(src.S1["rt_ac"])
    usable = b["system_mwh"] * (src.S1["soc_hi"] - src.S1["soc_lo"])
    lines = ["S1 from the cell to the POC (data pack S1, A-290):",
             f"  {b['cells']:,} cells, {b['system_mwh']:.2f} MWh nominal;"
             f" usable 10-90 %: {usable:.1f} MWh",
             f"  at the POC in one discharge, new: {usable * eta:.1f} MWh at up to 20 MW",
             f"  rack voltage {b['rack_v_min']:,.0f}-{b['rack_v_max']:,.0f} V inside a teaching"
             " PCS window of",
             "    1,000-1,500 V DC (the PCS maker's data decides)",
             "  0.5 C at full power: two hours from full to empty in theory,",
             "  1.6 hours inside the window"]
    emit("i_cell_poc", lines)


def duty() -> None:
    from plantp import storage as st
    from plantp.wind import rainflow
    y = lab_d.year()
    thr = y["dis"].sum()
    soc = y["soc"] / src.S1["energy_mwh"]
    f = src.FADE
    cyc = st.cycle_fade(rainflow(lab_d.turning(soc)), f["n100"], f["k"], f["loss_at_life"])

    def health(yr):
        cal = float(st.calendar_fade(yr, 25.0, soc.mean(), f["k25"], f["ea_ev"]))
        return 100 * (1 - cal - cyc * yr)
    lines = ["a year of duty and twenty years of health (lab D):",
             f"  {thr:,.0f} MWh discharged at the POC side, 365 full cycles",
             f"  health {health(1):.1f} % after year 1, {health(10):.1f} % after year 10,"
             f" {health(15):.1f} %",
             "    after year 15 (teaching fade model; data pack 2 %/yr)",
             "  warranty limits held, but the cycle allowance is used up:",
             "    any added service (reserve, a second daily cycle) needs a",
             "    warranty with more cycles or a larger battery"]
    emit("i_duty", lines)


def basis() -> None:
    lines = ["battery design basis (D-023; PLP-ELE-REP-0006):",
             "  chemistry LFP prismatic 314 Ah; 1P52S modules; 8-module racks",
             "    up to 1,498 V; 12 racks a container; 8 containers; 4 PCS",
             "  window 10-90 %; 86 % round trip; fade: maker's warranty curve",
             "  HVAC 120 kW a container (end-of-life heat, hottest hour);",
             "    IF-006 closed at 120 kW, not the offered 100 kW",
             "  protection: a fuse and switch per rack for its own fault,",
             "    DC bus rated for all racks; insulation monitoring",
             "  detection: BMS, off-gas, smoke, heat; remote isolation per rack",
             "  separation, ventilation or explosion control, water and runoff:",
             "    from the authority, the hazard mitigation analysis and the",
             "    product's large-scale test report (U-073, U-074)",
             "  dispatch: rule of lab D with its edge-case tests; warranty",
             "    limits as controller settings",
             "  life: augmentation in years 8 and 13 or a larger first stage;",
             "    end-of-life plan with a licensed recycler"]
    emit("i_basis", lines)


if __name__ == "__main__":
    cell_to_poc()
    duty()
    basis()
