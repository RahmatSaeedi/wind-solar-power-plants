"""Chapter 36 - three integrated Plant P examples: two results by hand,
the security package in numbers, and the basis D-040.

Run from the project root:   python -m companion.ch36.integrated
Writes companion/ch36/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch36.common import emit
from plantp import ot_security as ot


def by_hand() -> None:
    log = 2 * 400_000 * 300 * 365 / 1e9
    lines = ["two security results checked by hand",
             f"  firewall logs: 2 x 400,000 events x 300 B x 365 d = {log:.1f} GB;"
             f" code {ot.log_volume_gb(800_000, 300, 365):.1f}",
             f"  risk of an open vendor path: 4 x 4 = 16 -> {ot.risk_band(16)}",
             "  a hand check catches the commonest slip in sizing logs:",
             "  events a day of one device taken for all devices together"]
    emit("int_hand", lines)


def package() -> None:
    lines = ["the security package of Plant P in numbers (synthetic model)",
             "  8 zones, 8 conduits, each with a purpose; default deny",
             "  rule review: 1 any-any, 3 shadowed, 2 unused, 1 undocumented",
             "  flows outside the conduits: 2; single points of failure: 2",
             "  access: 2 accounts with extra rights, 1 dormant, 1 shared",
             "  inventory: 4 of 10 rows with a gap; 2 baselines drifted",
             "  recovery: 1 of 5 systems over its target; restores quarterly",
             "  vendor access: 48 h a year on request instead of 8,760",
             "  review record: 7 findings, each with an owner and a date"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-040 OT security basis of Plant P (teaching)",
             "  1 governance: asset owner's programme (STD-156), named",
             "    owners, risk register with teaching scales, life cycle",
             "  2 architecture: zones and conduits from the ch 35 logical",
             "    diagram, one rule a conduit with a purpose, default deny,",
             "    DMZ for every outside path, priority to safety and",
             "    availability; no business path into control",
             "  3 access: named accounts by role, quarterly review, vendor",
             "    sessions on request through a recorded jump host",
             "  4 monitoring: logs from every device on the plant clocks,",
             "    the few that matter read daily, alerts tuned",
             "  5 resilience: inventory complete, baselines compared,",
             "    backups before and after each change, three copies one",
             "    offline, quarterly restore tests, recovery objectives",
             "  6 data: classes, custodians, expiring transfers, readable",
             "    archives, media wiped at retirement",
             "  7 supply: security requirements in every purchase,",
             "    scorecards, provenance checks, support dates in the",
             "    inventory; sanitised models for vendor design reviews",
             "  8 people: tabletop each year, a continuity plan without",
             "    SCADA, an interface table with physical security",
             "  open: grid operator's security requirements and the",
             "    site's physical-security assessment (U-117)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
