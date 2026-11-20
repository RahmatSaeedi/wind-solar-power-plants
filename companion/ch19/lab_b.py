"""Chapter 19, lab B - size a preliminary battery and test its power and
energy limits (the chapter's first worked example).

Requirement (teaching, A-293): deliver 25 MWh at the POC each evening
from 18:00 to 22:00 at up to 20 MW, through year 15, charging only from
the plant (no grid charging, data pack S1).

Run from the project root:   python -m companion.ch19.lab_b
Writes companion/ch19/expected/lb_*.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch19 import sources as src
from companion.ch19.common import emit
from plantp import storage as st
from plantp.yieldrisk import annuity

S1, C = src.S1, src.LFP
E_REQ, P_REQ, YEARS = 25.0, 20.0, 15
ETA_OUT = math.sqrt(S1["rt_ac"])            # one way, data pack
WINDOW = S1["soc_hi"] - S1["soc_lo"]


def soh(y):
    return 1.0 - S1["fade_per_year"] * y     # data pack linear fade


# [start: energy]
def energy_check() -> None:
    bol = S1["energy_mwh"] * WINDOW * ETA_OUT
    need_soh = E_REQ / bol
    y_short = (1 - need_soh) / S1["fade_per_year"]
    e_over = st.size_nominal(E_REQ, WINDOW, ETA_OUT, 0.0, soh(YEARS))
    lines = ["step 1-3, energy (data pack S1: window 10-90 %, RT 86 %):",
             f"  one-way efficiency sqrt(0.86) = {ETA_OUT:.3f}",
             f"  at the POC from 40 MWh, new: 40 x {WINDOW:.1f}"
             f" x {ETA_OUT:.3f} = {bol:.1f} MWh",
             f"  health needed for {E_REQ:.0f} MWh: {need_soh:.3f};"
             f" reached after {y_short:.1f} years at 2 %/yr",
             f"  oversized at the start for year {YEARS}"
             f" (health {soh(YEARS):.2f}): {e_over:.1f} MWh nominal"]
    emit("lb_energy", lines)
# [end: energy]


def augment() -> None:
    def fade(y):
        return S1["fade_per_year"] * max(y, 0)
    need = E_REQ / ETA_OUT                         # MWh usable DC side
    adds, blocks = st.augmentation(S1["energy_mwh"], need, WINDOW, fade, YEARS, 4.0)
    price0, drop, r = 250.0, 0.04, 0.06            # k u per MWh, A-293
    pv_aug = 40 * price0 + sum(4.0 * price0 * (1 - drop) ** y / (1 + r) ** y for y in adds)
    e_over = st.size_nominal(E_REQ, WINDOW, ETA_OUT, 0.0, soh(YEARS))
    pv_over = e_over * price0
    lines = ["step 4, oversize or augment (teaching prices A-293):",
             f"  augmentation: 40 MWh now, 4 MWh blocks in years {', '.join(map(str, adds))}",
             f"  present cost (energy part, 6 %, price -4 %/yr): augment {pv_aug:,.0f} k u,",
             f"    oversize {pv_over:,.0f} k u ({e_over:.1f} MWh at {price0:.0f} k u/MWh)",
             "  augmentation buys later and cheaper, but needs space, bays",
             "  and a battery that accepts mixed ages (chapter 18)"]
    emit("lb_augment", lines)


def power_check() -> None:
    p_dc = P_REQ / ETA_OUT
    rows = []
    for name, cap, rg in (("new", S1["energy_mwh"], 1.0),
                          (f"year {YEARS}", S1["energy_mwh"] * soh(YEARS), src.THERMAL["r_growth_eol"])):
        c_rate = p_dc / cap
        i = c_rate * C.q_ah
        v = float(st.ocv(S1["soc_lo"])) - i * (C.r0 + C.r1) * rg
        rows.append((name, c_rate, i, v, v * 416))
    lines = ["step 5, power at the bottom of the window (10 % SOC):",
             f"  DC power for {P_REQ:.0f} MW at the POC: {p_dc:.1f} MW",
             "  state      C-rate   cell A   cell V   rack V"]
    for name, c_rate, i, v, vr in rows:
        lines.append(f"  {name:9s}  {c_rate:6.2f}  {i:7.0f}  {v:7.3f}  {vr:7,.0f}")
    lines += ["  the cell stays above 2.5 V and the rack above a teaching PCS",
              "  minimum of 1,050 V even at year 15: power is not the limit"]
    emit("lb_power", lines)


def plant_limits() -> None:
    """Can the plant charge it, and can the grid take it, every day?"""
    r = s15.plant_year()
    net = r["net"].reshape(365, 24)
    charge_avail = np.minimum(np.clip(net[:, 10:15], 0, None), P_REQ).sum(axis=1)
    need_charge = E_REQ / S1["rt_ac"]
    head = np.minimum(np.clip(100.0 - net[:, 18:22], 0, None), P_REQ).sum(axis=1)
    short_c = int((charge_avail < need_charge).sum())
    short_d = int((head < E_REQ).sum())
    lines = ["step 6, the plant and the grid (model 15.1, one year):",
             f"  charge needed 25 / 0.86 = {need_charge:.1f} MWh from 10:00 to 15:00",
             f"  days the plant cannot give it: {short_c} of 365"
             f" ({100 * short_c / 365:.0f} %)",
             f"  days the export limit leaves less than {E_REQ:.0f} MWh of room"
             f" from 18:00 to 22:00: {short_d}",
             "  in the data year the plant charges the battery on all but",
             "  one calm, overcast day; a weaker year has more such days, so",
             "  the requirement must say 'when the plant can charge it', or",
             "  allow charging at other hours or from the grid (A-012 forbids",
             "  grid charging today)"]
    emit("lb_limits", lines)


if __name__ == "__main__":
    energy_check()
    augment()
    power_check()
    plant_limits()
