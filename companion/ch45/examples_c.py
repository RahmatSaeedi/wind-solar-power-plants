"""Chapter 45, lesson C: safety and lifecycle engineering - a battery that
cannot be switched off, only divided; energy shipped at a reduced state
of charge; replacing a module in an aged rack; and the materials of a
container at the end of life.

Run from the project root:   python -m companion.ch45.examples_c
Writes companion/ch45/expected/c_*.txt.
Teaching values (A-479, A-480); concepts and interfaces, no work procedure.
"""
from __future__ import annotations

from companion.ch45 import sources as src
from companion.ch45.common import emit
from plantp import cellmfg as cf

C, B = src.CELL, src.BUILD


# ------------------------------------------------ divided, never dead
def divided(threshold_v: float = 60.0) -> dict:
    e_cell = C["q_ah"] * C["v_nom"] / 1000
    parts = [("rack, contactors open", B["s_module"] * B["m_rack"]),
             ("module", B["s_module"]),
             ("half module (service disconnect, teaching)", B["s_module"] // 2),
             ("quarter module (teaching)", B["s_module"] // 4)]
    lines = ["opening a contactor divides a battery; it does not discharge it",
             "  part                                        cells   volts   kWh"]
    out = {}
    for name, n in parts:
        v = n * C["v_nom"]
        out[name] = (v, n * e_cell)
        lines.append(f"  {name:43s} {n:5d}   {v:5.0f}   {n * e_cell:5.1f}")
    below = [n for n, (v, _) in out.items() if v <= threshold_v]
    lines += [f"  parts at or below a {threshold_v:.0f} V teaching threshold: "
              f"{', '.join(below) or 'none'}",
              "  every module stays live at well over a hundred volts with",
              "  tens of kilowatt-hours behind it: the design divides it",
              "  into parts that can be handled, the procedure that uses",
              "  them is the integrator's and is done by qualified people"]
    emit("c_divided", lines)
    return out


# ------------------------------------------------ shipping state of charge
def shipping(socs=(1.0, 0.5, 0.3)) -> dict:
    e_cont = B["s_module"] * B["m_rack"] * B["r_container"] * C["q_ah"] * C["v_nom"] / 1e6
    lines = [f"energy in one container ({e_cont:.2f} MWh at full charge) by state "
             "of charge",
             "  SOC     MWh in the container"]
    out = {}
    for s in socs:
        out[s] = e_cont * s
        lines.append(f"  {s:4.0%}    {e_cont * s:8.2f}")
    lines += ["  cells and modules travel at a reduced state of charge as the",
              "  transport rules and the maker require (to verify for each",
              "  route); the cell type's transport test summary (STD-101) is",
              "  a receiving document, and the record shows the SOC at",
              "  dispatch and on arrival"]
    emit("c_shipping", lines)
    return out


# ------------------------------------------------ replacing a module
def replacement(soh_rack: float = 0.90, soc_rack: float = 0.70,
                soc_new: float = 0.50, i_bal: float = 0.1) -> dict:
    q = C["q_ah"]
    usable_old = soh_rack * q
    new_mod = q
    string = min(usable_old, new_mod)
    d_ah = abs(soc_rack - soc_new) * q
    hours = d_ah / i_bal
    lines = [f"one module of a five-year-old rack replaced (rack health "
             f"{soh_rack:.0%}, teaching)",
             f"  rack modules {usable_old:.0f} Ah, new module {new_mod:.0f} Ah: the "
             f"string gives {string:.0f} Ah",
             "  the new module's extra capacity is not used until the rest",
             "  of the rack is replaced",
             f"  new module at {soc_new:.0%} SOC into a rack at {soc_rack:.0%}: "
             f"{d_ah:.0f} Ah to even out",
             f"  with {i_bal * 1000:.0f} mA passive balancing: {hours:,.0f} h "
             f"({hours / 24:.0f} days)",
             "  a replacement module is brought to the rack's state of",
             "  charge before it goes in, and a spare of similar age, if",
             "  the stock holds one, fits better than a new one (ch 52)"]
    emit("c_replace", lines)
    return dict(string=string, hours=hours)


# ------------------------------------------------ end of life
def end_of_life() -> dict:
    n_cells = B["s_module"] * B["m_rack"] * B["r_container"]
    masses = {k: v * n_cells for k, v in src.MATERIALS.items()}
    rec = cf.recovered(masses, src.RATES)
    tot, got = sum(masses.values()), sum(rec.values())
    lines = [f"materials of one container's {n_cells:,} cells (teaching shares; "
             "A-479)",
             "  material                    in t    recovered t"]
    for k in masses:
        lines.append(f"  {k:26s} {masses[k] / 1000:6.1f}   {rec[k] / 1000:11.1f}")
    lines += [f"  total {tot / 1000:.1f} t of cells, {got / 1000:.1f} t recovered "
              f"({got / tot:.0%} by mass)",
              "  recovery by mass flatters LFP: its cathode holds no costly",
              "  metal, so the value is in aluminium, copper and the lithium",
              "  compound; the take-back route and its record are set in",
              "  the purchase contract, not at the end (ch 39, ch 53)"]
    emit("c_eol", lines)
    return dict(total=tot, recovered=got)


if __name__ == "__main__":
    divided()
    shipping()
    replacement()
    end_of_life()
