"""Chapter 38, lesson B (requirements and interface control): the flow
from design basis to verification for one component, the interface-
control sheet of the PV inverter skid with its open values computed, and
the design-for-X reviews that close it.

Run from the project root:   python -m companion.ch38.examples_b
Writes companion/ch38/expected/b_*.txt.
Teaching values (A-419); makers' data replace them at the bid.
"""
from __future__ import annotations

import math

from companion.ch38 import sources as src
from companion.ch38.common import emit


def flow() -> None:
    steps = [("design basis", "5.0 MVA at 0.6 kV, 45 C, 1,000 m", "ch 9, D-012"),
             ("functions", "convert, protect, control, communicate", "ch 18"),
             ("preliminary sizing", "LV current 4,811 A; transformer 5.6 MVA", "ch 25"),
             ("detail", "skid drawing, cable schedule, settings", "this chapter"),
             ("materials, tolerances", "busbar Cu, bolt torque, IP54", "maker"),
             ("manufacturing limits", "skid width 2.4 m for road transport", "ch 31"),
             ("inspection access", "front access 1.5 m, IR windows", "ch 51"),
             ("verification", "FAT heat run, SAT power, FRT model", "ch 44, 50")]
    lines = ["requirements-to-design flow for the PV inverter skid (teaching)",
             "  step                    content                                source"]
    for a, b, c in steps:
        lines.append(f"  {a:22s}  {b:38s} {c}")
    lines += ["  every step leaves a record the next one cites; the",
              "  verification step points back to the design basis, so",
              "  a failed test says which assumption was wrong"]
    emit("b_flow", lines)


def icd_values() -> None:
    s_mva, v_kv, eff = 5.0, 0.6, 0.985
    i_lv = s_mva * 1e3 / (math.sqrt(3) * v_kv)
    per_cable = 620.0                                    # A, 630 mm2 Cu in air (teaching)
    n_par = math.ceil(i_lv / per_cable)
    heat_kw = s_mva * 1e3 * (1 - eff)
    s_sc_mva, v_mv = 500.0, 33.0                         # at the 33 kV bus (teaching)
    z_tx = 0.07 * v_mv ** 2 / 5.6                        # ohm, unit transformer 7 %
    z_grid = v_mv ** 2 / s_sc_mva
    i_k_rmu = v_mv / (math.sqrt(3) * (z_grid + 0.12)) # cable 0.12 ohm (teaching)
    open_items = [i for i in src.ICD_INV if i[3] is None]
    lines = ["interface-control sheet of the PV inverter skid: values computed",
             f"  LV current at 5.0 MVA, 0.6 kV: {i_lv:,.0f} A; {n_par} cables of"
             f" {per_cable:.0f} A per phase",
             f"  heat rejected at {eff * 100:.1f} % efficiency: {heat_kw:.0f} kW"
             " (with auxiliaries more)",
             f"  short-circuit current at the skid's RMU: {i_k_rmu:.1f} kA",
             f"    (33 kV bus {s_sc_mva:.0f} MVA and 0.12 ohm of cable, teaching)",
             f"  unit transformer impedance seen from 33 kV: {z_tx:.1f} ohm",
             f"  items still open on the sheet: {len(open_items)} of {len(src.ICD_INV)}"]
    for kind, item, owner, _ in open_items:
        lines.append(f"    {kind:10s} {item:45s} owner {owner}")
    lines += ["  an interface is closed when both owners sign one value;",
              "  until then the item is open, and the drawing that needs",
              "  it carries a hold (ch 18, interface register)"]
    emit("b_icd", lines)


def dfx() -> None:
    rows = [("manufacture", "one busbar size instead of three", "parts 31 -> 22"),
            ("assembly", "cable entry from below, no rear access", "skid 0.6 m narrower"),
            ("test", "test terminals for CT and VT circuits", "FAT 2 days -> 1"),
            ("maintenance", "fans replaceable from the front", "fan 4 h -> 1 h"),
            ("transport", "skid within road width 2.4 m", "no escort (ch 31)")]
    lines = ["design-for-X review of the inverter skid (teaching outcomes)",
             "  for            change                                   result"]
    for a, b, c in rows:
        lines.append(f"  {a:13s}  {b:40s} {c}")
    fan_fail = 24                                        # fan changes a year (teaching)
    lines += [f"  {fan_fail} fan changes a year x 3 h saved = {fan_fail * 3} hours of"
              " inverter downtime",
              "    avoided",
              "  each review is held while the design can still change, with",
              "  the maker, the installer and the operator in the room;",
              "  their findings go into the design basis, not into a",
              "  later deviation"]
    emit("b_dfx", lines)


if __name__ == "__main__":
    flow()
    icd_values()
    dfx()
