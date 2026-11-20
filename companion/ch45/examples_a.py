"""Chapter 45, lesson A: cell and pack architecture - electrode balance and
what a local coating error does to it, energy and mass from cell to
system, voltage windows of module, rack and container against the BMS
limits and the PCS, and the interfaces from cell to plant.

Run from the project root:   python -m companion.ch45.examples_a
Writes companion/ch45/expected/a_*.txt.
Teaching values (A-474); a design concept, not a cell-making recipe.
"""
from __future__ import annotations

from companion.ch45 import sources as src
from companion.ch45.common import csv, emit
from plantp import cellmfg as cf

C, B, D = src.CELL, src.BUILD, src.DESIGN


# ------------------------------------------------ electrode balance
def balance() -> dict:
    pos = cf.areal_capacity(D["pos_loading"], D["pos_active"], D["pos_spec"])
    neg = cf.areal_capacity(D["neg_loading"], D["neg_active"], D["neg_spec"])
    npr = cf.np_ratio(neg, pos)
    area = C["q_ah"] * 1000 / (pos * D["first_eff"])
    cases = {"as designed": (1.00, 1.00), "positive +3 %": (1.03, 1.00),
             "negative -3 %": (1.00, 0.97), "both, at one spot": (1.03, 0.97)}
    lines = ["electrode balance of the 314 Ah LFP cell (teaching design values)",
             f"  positive {D['pos_loading']} mg/cm2 x {D['pos_active']} x "
             f"{D['pos_spec']:.0f} mAh/g = {pos:.2f} mAh/cm2",
             f"  negative {D['neg_loading']} mg/cm2 x {D['neg_active']} x "
             f"{D['neg_spec']:.0f} mAh/g = {neg:.2f} mAh/cm2",
             f"  facing area for {C['q_ah']:.0f} Ah after a first-cycle share of "
             f"{D['first_eff']:.0%}: {area / 1e4:.2f} m2",
             "  coating error              N/P     margin"]
    out = {}
    for name, (fp, fn) in cases.items():
        r = cf.np_ratio(neg * fn, pos * fp)
        out[name] = r
        lines.append(f"  {name:26s} {r:5.3f}   {r - 1:+6.1%}")
    lines += ["  the negative must hold more than the positive can give, or",
              "  lithium plates on it while charging; a few per cent of",
              "  coating weight at one spot uses up the margin - which is",
              "  why the coating weight is a controlled characteristic",
              "  (lesson B), not a nominal value"]
    emit("a_balance", lines)
    return dict(pos=pos, neg=neg, np=npr, area=area, worst=out["both, at one spot"])


# ------------------------------------------------ energy and mass by level
def levels(overhead=(1.0, 1.18, 1.30, 1.60)) -> dict:
    e_cell = C["q_ah"] * C["v_nom"] / 1000                  # kWh
    n = [1, B["s_module"], B["s_module"] * B["m_rack"],
         B["s_module"] * B["m_rack"] * B["r_container"]]
    names = ["cell", "module", "rack", "container"]
    lines = ["energy and mass from cell to container (mass overheads teaching)",
             "  level        cells    kWh      mass kg   Wh/kg"]
    out = {}
    for name, k, f in zip(names, n, overhead):
        e = k * e_cell
        m = k * C["mass_kg"] * f
        out[name] = (e, m)
        lines.append(f"  {name:10s} {k:7d}  {e:7.1f}  {m:10.0f}   {e * 1000 / m:5.0f}")
    csv("ch45-levels.csv", "k,whkg",
        [(k + 1, round(e * 1000 / m)) for k, (e, m) in enumerate(out.values())])
    total = n[-1] * B["containers"]
    lines += [f"  system: {B['containers']} containers, {total:,} cells, "
              f"{total * e_cell / 1000:.2f} MWh (ch 19: 40.13)",
              "  each level adds structure, cooling, wiring and protection:",
              "  the cell's energy density is not the system's - a buyer",
              "  compares containers by usable MWh at the PCS, not cells"]
    emit("a_levels", lines)
    return dict(e_cell=e_cell, total=total, mwh=total * e_cell / 1000,
                container=out["container"])


# ------------------------------------------------ voltage windows
def windows(pcs_v=(1150.0, 1500.0)) -> dict:
    bms_lo, bms_hi = src.BMS["v_min"][1], src.BMS["v_max"][1]
    lines = ["voltage windows (cells in series) against the BMS limits and "
             "the PCS",
             "  level      cells   cell limits V       BMS limits V      nominal V"]
    out = {}
    for name, k in (("module", B["s_module"]), ("rack", B["s_module"] * B["m_rack"])):
        lim = cf.pack_limits(k, 1, C["q_ah"], C["v_min"], C["v_nom"], C["v_max"],
                             C["c_max"])
        out[name] = (k * bms_lo, k * bms_hi)
        lines.append(f"  {name:8s} {k:7d}   {lim['v_min']:6.0f} - {lim['v_max']:6.0f}"
                     f"   {k * bms_lo:6.0f} - {k * bms_hi:6.0f}   {lim['v_nom']:9.0f}")
    lo, hi = out["rack"]
    lines += [f"  PCS: full power above {pcs_v[0]:,.0f} V (ch 19, A-296), "
              f"top {pcs_v[1]:,.0f} V (teaching)",
              f"  the rack's BMS window {lo:.0f} - {hi:.0f} V: below "
              f"{pcs_v[0]:.0f} V the PCS derates,",
              f"  above {pcs_v[1]:.0f} V it may not start - the cell count is "
              "chosen against two",
              "  makers' limits at once; changing the BMS limits changes the",
              "  rack window, so the BMS setting is an interface item"]
    emit("a_windows", lines)
    return dict(rack=out["rack"], module=out["module"])


# ------------------------------------------------ interfaces
INTERFACES = [   # interface, what crosses, evidence
    ("cell - module", "current, heat, pressure", "welds, compression"),
    ("module - BMS", "cell voltages, temperatures", "sensor map, calibration"),
    ("module - rack", "DC bus, cooling, frame", "torque, insulation, flow"),
    ("rack - container", "DC, auxiliaries, data", "isolation, HVAC, fire"),
    ("container - PCS", "DC window, limits, commands", "window check, test record"),
    ("container - plant", "SCADA, alarms, isolation", "point list, interlocks"),
    ("container - site", "foundation, earthing, access", "survey, continuity"),
]


def interfaces() -> int:
    lines = ["interfaces from cell to plant and the evidence at each",
             "  interface          crosses                         evidence"]
    for name, what, ev in INTERFACES:
        lines.append(f"  {name:18s} {what:31s} {ev}")
    lines += [f"  {len(INTERFACES)} interfaces; three makers meet at them (cell maker,",
              "  integrator, PCS maker) - each row needs one owner of the",
              "  value and one of the evidence (ch 18, ch 19)"]
    emit("a_interfaces", lines)
    return len(INTERFACES)


if __name__ == "__main__":
    balance()
    levels()
    windows()
    interfaces()
