"""Chapter 25 - three integrated Plant P examples: a transformer checked
by hand from its nameplate, the bid evaluation as a decision record, and
the transformer and export-bay basis (D-029).

Run from the project root:   python -m companion.ch25.integrated
Writes companion/ch25/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch25.common import emit
from plantp import transformer as tr


def by_hand() -> None:
    i_hv = 63e6 / (math.sqrt(3) * 132e3)
    i_lv = 63e6 / (math.sqrt(3) * 33e3)
    lines = ["the 63 MVA nameplate by hand:",
             f"  rated currents: HV {i_hv:.0f} A, LV line {i_lv:,.0f} A,"
             f" LV delta winding {i_lv / math.sqrt(3):.0f} A",
             f"  full-load losses 35 + 250 = 285 kW; efficiency at pf 1:"
             f" {63000 / 63285 * 100:.2f} %",
             f"  fault current behind 12 %: {1 / 0.12:.1f} x rated ="
             f" {i_lv / 0.12 / 1e3:.1f} kA on the LV side",
             "  ratio 132/33 = 4.0 at the principal tap"]
    emit("int_hand", lines)


def bid_record() -> None:
    lines = ["decision record: main transformer bids (teaching):",
             "  evaluated at 70 u/MWh, 25 y, 7.5 %, LLF 0.128 from ch 15:",
             "    bid A 2,330 k u, bid B 2,242 k u: bid B preferred",
             "  conditions: impedance 12 % within the band, YNd11, tap",
             "    range after the grid study, ONAF 63 MVA, loss guarantees",
             "    with deductions, type tests or proof of design for the",
             "    short-circuit withstand, transport within 72 t",
             "  sensitivity: bid A wins above about 108 u/MWh",
             "  owner of the decision: the owner's engineer with the",
             "  procurement team (ch 38)"]
    emit("int_bids", lines)


def basis() -> None:
    lines = ["transformer and export-bay basis of Plant P (D-029):",
             "  2 x 63 MVA 132/33 kV YNd11 ONAN/ONAF, z 12 %, OLTC +/-10 %",
             "    in 17 steps (range open to the grid study, U-096)",
             "  losses evaluated with A and B factors stated in the enquiry",
             "  unit transformers: oil-filled 5.5 MVA on the PV and battery",
             "    skids, dry-type 5.6 MVA in the turbine towers",
             "  containment for 110 % of the oil plus rain; separation,",
             "    detection and any suppression from the fire design (ch 31)",
             "  132 kV single bus with a bus disconnector; line bay E1 with",
             "    arresters, CTs and VTs for protection and revenue metering",
             "  dossier review rules: declared values, tolerances and the",
             "    decision for each failure written into the contract"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    bid_record()
    basis()
