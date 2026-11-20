"""Chapter 38 - three integrated Plant P examples: two results by hand,
the design-control package in numbers, and the basis D-042.

Run from the project root:   python -m companion.ch38.integrated
Writes companion/ch38/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch38.common import emit
from plantp import docctl as dc


def by_hand() -> None:
    e = dc.earned_value(4_451, 3_012, 3_553, 7_342)
    p = 1 - math.comb(194, 20) / math.comb(200, 20)
    lines = ["two design-control results checked by hand",
             f"  SPI = 3,012 / 4,451 = {3012 / 4451:.2f}; code {e['spi']:.2f}",
             f"  CPI = 3,012 / 3,553 = {3012 / 3553:.2f}; EAC = 7,342 / CPI ="
             f" {7342 / (3012 / 3553):,.0f} h",
             f"  chance a 20-drawing sample of 200 finds one of 6 errors:"
             f" {p:.3f}; code {dc.detect_chance(200, 6, 20):.3f}",
             "  the hand check of EAC catches the common slip of dividing",
             "  by SPI instead of CPI: hours are a cost, not a date"]
    emit("int_hand", lines)


def package() -> None:
    lines = ["the design-control package of Plant P in numbers (synthetic, week 40)",
             "  register: 120 deliverables; 2 numbers, 3 revisions, 1 checker,",
             "    9 owners to fix; 2 illegal status changes",
             "  linked registers: 5 disagreements; 3 stale or broken references",
             "  requirements: design 83 %, verification method 83 %, evidence",
             "    17 % (rest from FAT, SAT, commissioning)",
             "  inverter skid ICD: 3 of 12 items open; release held",
             "  engineering: SPI 0.68, CPI 0.85, EAC 8,661 h; 18 queries older",
             "    than 14 days",
             "  change C-017: 13 documents, 102 h, about 50 k u, approved",
             "  grid interface: 3 responsibilities without one owner",
             "  handover rule: every critical item at 98 % - 3 short today"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-042 detailed design and information basis of Plant P (teaching)",
             "  1 numbering, revisions and statuses of ch 2, enforced by the",
             "    CDE workflow; register checked every week",
             "  2 one source of truth per value: ratings in the approved",
             "    one-line, CT data from the switchgear data sheets, lengths",
             "    from the route survey; every link carries its revision",
             "  3 requirements traced to design, verification method and",
             "    evidence; none issued for construction without the first",
             "    two",
             "  4 an ICD per major skid; release for manufacture only with",
             "    all items closed and the FAT procedure approved",
             "  5 engineering progress by status credit; queries answered in",
             "    14 days; changes with impact, cost, schedule and approval",
             "  6 independent checks: one by one for protection, lifting and",
             "    foundations, sampled for the rest",
             "  7 grid interface: one accountable party per item; changes on",
             "    either side notified before issue",
             "  8 handover: owner's information requirements as checks;",
             "    critical items at 98 % or better",
             "  open: accountable owners of three interface items; the",
             "    operator's interface schedule (U-115, U-119)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
