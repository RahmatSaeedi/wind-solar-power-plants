"""Chapter 10 - three integrated Plant P examples: one module at one hour
of the summer day (introductory), the array design and its annual energy
chain (intermediate), and the inspection and cleaning acceptance basis
(integrated).

Run from the project root:   python -m companion.ch10.integrated
Writes companion/ch10/expected/i_*.txt.
Data pack 1.1.0, S0; teaching values A-183 .. A-199; D-012, D-013.
"""
from __future__ import annotations

import math
import warnings

import numpy as np

from companion.ch10 import pvyear10
from companion.ch10.common import emit
from plantp import datapack, mppt, pe, pvcell as pc

warnings.simplefilter("ignore", RuntimeWarning)
DS = pc.PVM_550_DS
EFF_POINTS = [(0.10, 0.970), (0.25, 0.983), (0.50, 0.986), (0.75, 0.985),
              (1.00, 0.983)]


def one_hour() -> None:
    k = (174 - 1) * 24 + 13                       # 23 June, 13:00
    p = pvyear10.poa()
    s = pvyear10.strings()
    h = datapack.load_hourly()
    ref = pvyear10.ref_sdm()
    g, tc = s["eff"][k], s["t_cell"][k]
    m = pc.at_conditions(ref, g, tc, DS.alpha_isc)
    v, i, pw = m.mpp()
    lin = 550.1 * g / 1000 * (1 - 0.0035 * (tc - 25))
    ex = mppt.PVM_550.at(g, tc).mpp()[1]
    emit("i_hour", [
        "one module at 13:00 on 23 June (data pack 1.1.0, S0):",
        f"  GHI {p['ghi'][k]:.0f} W/m2 -> POA {p['poa'][k]:.0f} (beam "
        f"{p['beam'][k]:.0f}, sky {p['sky'][k]:.0f}, ground {p['ground'][k]:.0f})",
        f"  after incidence losses {g:.0f} W/m2; air {h['t_air_c'].iloc[k]:.1f} C,"
        f" wind at 2 m {pc.wind_at_height(h['ws_100m_ms'].iloc[k], 100, 2):.1f}"
        " m/s",
        f"  Faiman cell temperature {tc:.1f} C",
        f"  single-diode model: {pw:.1f} W at {v:.2f} V (string {26 * v:.0f} V)",
        f"  linear rule P_stc G (1 + gamma dT): {lin:.1f} W; chapter 9 model "
        f"{ex:.1f} W",
        "  the three agree within a few per cent at this hour; the diode",
        "  model also gives the voltage the inverter window needs"])


def array_chain() -> None:
    c = pe.fit_loss_coeffs(EFF_POINTS)
    p = pvyear10.poa()
    s = pvyear10.strings()
    area = 4200 * 26 * 2.58
    h_poa = p["poa"].sum() / 1e3
    e_nominal = 60.06e3 * h_poa / 1000                       # MWh at STC eff.
    dc_gross = (s["p_string"] * 4200).sum() / 1e6
    dc = dc_gross * (1 - pvyear10.DC_LOSS)
    x = pvyear10.dc_power() / 50e6
    c0, c1, c2 = c
    y = np.where(x > c0, (-(1 + c1) + np.sqrt((1 + c1) ** 2 - 4 * c2 * (c0 - x)))
                 / (2 * c2), 0.0)
    ac_u = y * 50e6
    ac = np.minimum(ac_u, 50e6 * 0.98)
    soil, shade = 0.0143, 0.0007                             # d_policies, c_rows
    ac_final = ac.sum() / 1e6 * (1 - soil) * (1 - shade)
    lines = ["array design and energy chain of Plant P (D-012, D-013):",
             "  10 inverters x 21 combiners x 20 strings x 26 modules = "
             f"{4200 * 26:,} modules",
             f"  {60.06:.2f} MWp, DC/AC 1.20, tilt 25 deg, GCR 0.40, pitch 11.4 m",
             f"  POA irradiation {h_poa:,.0f} kWh/m2 on {area / 1e4:.1f} ha of modules",
             f"  energy at STC efficiency              {e_nominal:9,.0f} MWh",
             f"  after IAM, temperature, low light     {dc_gross:9,.0f} MWh "
             f"({100 * (dc_gross / e_nominal - 1):+.1f} %)",
             f"  after DC wiring 2 % and mismatch 1 %  {dc:9,.0f} MWh",
             f"  after inverter and clipping           {ac.sum() / 1e6:9,.0f} MWh",
             f"  after soiling 1.43 % and shading      {ac_final:9,.0f} MWh",
             f"  specific yield {ac_final / 60.06:,.0f} kWh/kWp; performance "
             f"ratio {ac_final / e_nominal:.3f}",
             "  chapter 9's horizontal model gave 101.4 GWh: the tilted plane",
             "  adds about a tenth; chapter 15 adds availability, degradation",
             "  and the uncertainty of each step"]
    emit("i_chain", lines)


def acceptance() -> None:
    n_mod = 4200 * 26
    per_pallet, per_container = 31, 620                         # A-199
    containers = math.ceil(n_mod / per_container)
    lines = ["incoming inspection and cleaning acceptance basis (A-199):",
             f"  {n_mod:,} modules in {math.ceil(n_mod / per_pallet):,} pallets and"
             f" {containers} containers",
             "  every container: seals, shock indicators, pallet damage,",
             "    documents against the packing list (serials, bins)",
             f"  electroluminescence on 1 pallet per container: "
             f"{containers * per_pallet:,} modules ({100 * containers * per_pallet / n_mod:.1f} %)",
             f"  laboratory flash on 12 modules per 10 MWp: {12 * 6} modules,",
             "    judged by the decision rule of the contract",
             "  cleaning robot acceptance: one table row per robot model run",
             "    for a month: removal ratio from paired soiling cells, glass",
             "    coating checked by the module maker's method, no cracks",
             "    under electroluminescence before and after"]
    emit("i_accept", lines)


if __name__ == "__main__":
    one_hour()
    array_chain()
    acceptance()
