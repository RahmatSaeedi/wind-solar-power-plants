"""Chapter 43 - three integrated Plant P examples: the PV unit transformer
by hand (turns, flux, currents, losses, efficiency), the acceptance of
main transformer T1 summarised, and the design-review and factory
acceptance basis D-047.

Run from the project root:   python -m companion.ch43.integrated
Writes companion/ch43/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch43 import sources as src
from companion.ch43.common import emit


# [start: hand]
def by_hand(load: float = 0.6, pf: float = 1.0) -> dict[str, float]:
    u = src.PVU
    v_lv = u["lv_kv"] * 1e3 / math.sqrt(3)        # star phase
    v_hv = u["hv_kv"] * 1e3                       # delta phase
    n_lv = 16
    e_t = v_lv / n_lv
    n_hv = round(v_hv / e_t)
    phi = e_t / (4.44 * 50)                       # peak flux, Wb
    i_hv = u["s_mva"] * 1e6 / (3 * v_hv)
    i_lv = u["s_mva"] * 1e6 / (3 * v_lv)
    loss = u["p0_kw"] + u["pk_kw"] * load ** 2
    p_out = load * u["s_mva"] * 1000 * pf
    eff = p_out / (p_out + loss)
    # [end: hand]
    lines = [f"PV unit transformer by hand ({u['s_mva']} MVA, {u['hv_kv']:.0f}/"
             f"{u['lv_kv']} kV {u['vector']}):",
             f"  turns ratio {v_hv:,.0f} / {v_lv:.1f} = {v_hv / v_lv:.2f}; with "
             f"{n_lv} LV turns, {n_hv} HV turns",
             f"  volts a turn {e_t:.2f} V; peak flux e_t / (4.44 f) = "
             f"{phi * 1000:.1f} mWb",
             f"  phase currents: HV delta {i_hv:.1f} A, LV star {i_lv:,.0f} A",
             f"  at {load:.0%} load, pf {pf}: losses {u['p0_kw']} + {u['pk_kw']} x "
             f"{load:.1f}^2 = {loss:.2f} kW",
             f"  efficiency {p_out:,.0f} / ({p_out:,.0f} + {loss:.2f}) = {eff:.2%}",
             "  check: same ampere-turns, "
             f"{n_hv * i_hv:,.0f} and {n_lv * i_lv:,.0f} A"]
    emit("int_hand", lines)
    return dict(n_hv=n_hv, e_t=e_t, phi=phi, i_hv=i_hv, i_lv=i_lv, loss=loss,
                eff=eff)


def acceptance() -> dict[str, float]:
    from companion.ch43 import lab_d
    rv = lab_d.review()
    gaps = lab_d.audit(src.TRAVELER)
    lines = ["acceptance of main transformer T1 at the factory, summarised",
             f"  traveler: {len(gaps)} gaps; test report: {rv['fails']} failures, "
             f"deductions {rv['ded']:.1f} k u",
             f"  winding rise {rv['rise']:.1f} K read correctly against 65 K",
             "  decision: not accepted for shipment until the ratio lead,",
             "  the PD source and the acetylene are explained and the",
             "  records completed; the winding-rise exceedance goes to the",
             "  owner with options (cooling repair, a rating limit agreed",
             "  in writing, or rejection) - not a factory floor decision"]
    emit("int_accept", lines)
    return dict(gaps=len(gaps), fails=rv["fails"], ded=rv["ded"])


def basis() -> None:
    lines = ["D-047 transformer design review and factory acceptance basis",
             "  1 design review: flux density with the grid study's V/f;",
             "    turns and tap steps inside the ratio tolerance; impedance",
             "    from the geometry; loss build-up; gap and barrier stress;",
             "    short-circuit stresses with the inner winding supported",
             "  2 losses corrected for waveform and temperature before any",
             "    comparison; deductions with the A and B of the enquiry",
             "  3 heat run read from the cooling curve extrapolated to",
             "    shut-down; winding and top-oil rises both judged",
             "  4 traveler records at every gate, with the core, winding",
             "    heights, drying end point, oil water and preservation",
             "  5 baselines delivered (ratio, R, PI, FRA both windings, DGA,",
             "    impact log) - each site check compares with one",
             "  6 maker data to every discipline before FAT closes",
             "  7 open decisions listed with owners; no 'all pass' summary",
             "  8 energise from the grid on a high tap; the 33 kV winding",
             "    sets the flux in service (TQ-03)",
             "  9 witness points from the FMEA: drying end point, bare core,",
             "    active part; burr, clamping and joint records as holds",
             " 10 readings referred before comparing: tan delta to 20 C,",
             "    delta phases solved, PD with calibration and background",
             " 11 rating plate with measured values; DC-injection limit in",
             "    the PV unit specification; upgraded paper considered",
             " 12 a written rating limit (62 MVA) costs no energy here and",
             "    is an option for the winding-rise finding",
             "  open: maker's design data and short-circuit proof (U-124)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    acceptance()
    basis()
