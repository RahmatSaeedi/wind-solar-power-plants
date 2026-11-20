"""Chapter 39 - three integrated Plant P examples: two results by hand,
the procurement package in numbers, and the basis D-043.

Run from the project root:   python -m companion.ch39.integrated
Writes companion/ch39/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch39.common import emit
from plantp import procure as pr
from plantp import transformer as tr


def by_hand() -> None:
    a, b = tr.ab_factors(70, 25, 0.075, 0.20)
    unit = tr.loss_cost(4.1, 41.0, a, b)
    lines = ["two procurement results checked by hand",
             f"  A = 70 u/MWh x 8,760 h x annuity(7.5 %, 25 y) = {a:.2f} k u/kW",
             f"  B = 0.20 A = {b:.2f} k u/kW",
             f"  U-A losses per unit: {a:.2f} x 4.1 + {b:.2f} x 41 = {unit:.1f} k u;"
             f" x 10 = {10 * unit:.0f}",
             f"  delay damages, 8 weeks at 0.5 % of 1,160 k u:"
             f" {pr.ld_amount(8, 0.005, 1160, 0.10)[0]:.1f} k u",
             "  a hand check of A catches the slip of annuity years vs",
             "  months, or of MWh vs kWh in the energy price"]
    emit("int_hand", lines)


def package() -> None:
    lines = ["the procurement package of the PV unit transformers in numbers",
             "  offers: U-A 2,072, U-C 2,093, U-B 2,141 k u evaluated;",
             "    lowest price U-B, lowest evaluated U-A",
             "  U-B not acceptable: no heat-run witness, no data schedule,",
             "    process control below its floor",
             "  data schedule: U-A 93 %, U-C 86 %, U-B 57 % of 14 items",
             "  sub-tier on-time chance 86 %; core steel gets a buffer",
             "  labour screen: 1 high-risk sub-supplier without evidence",
             "  contracts: 7 gaps to close before financial close",
             "  prequalification: U-D not invited; U-B passed by a hair",
             "  ranking holds above 52 u/MWh (U-C would undercut below)",
             "  exposure peak 290 k u at week 8; 174 k u uncovered",
             "  a strategic spare unit pays (expected loss 973 k u)",
             "  warranty security ends 4 weeks short even without delay"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-043 procurement basis of Plant P (teaching)",
             "  1 packages: EPC with a separate turbine OEM contract; the",
             "    owner's engineer keeps SCADA integration",
             "  2 evaluation: compliance matrix first (critical items are",
             "    cleared, not priced), then evaluated price with losses,",
             "    delivery and currency, then the capability audit floors",
             "  3 PV unit transformers: recommend U-A subject to closing",
             "    two deviations and the data update duty",
             "  4 supplier data: 14 items with schema, update duty and",
             "    rights; delivery is accepted on the data, not a count",
             "  5 RAM: plant targets split into supplier shares with",
             "    response and repair times and on-site spares",
             "  6 labour: proportionate screen to tier 2; claims kept apart",
             "    from verified findings; remedy and escalation in contract",
             "  7 contracts: interface matrix with an owner for every gap;",
             "    wording for the lawyers",
             "  8 commercial: milestones near value; securities tied to",
             "    events, not dates; one strategic spare transformer",
             "  9 factory: 18 hold/witness points; lots held on sample",
             "    evidence (module power), source inspection funded",
             "  open: grid operator's interface schedule (U-115, U-119);",
             "    tier-2 source of U-B's winding wire if U-B returns (U-120)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
