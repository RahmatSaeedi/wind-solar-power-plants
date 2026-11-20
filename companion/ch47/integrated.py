"""Chapter 47 - three integrated Plant P examples: three numbers checked
by hand (a carbon equivalent, a bar's mass, a can's mass), the
acceptance of one turbine's tower and foundation summarised, and the
manufacturing and acceptance basis D-051.

Run from the project root:   python -m companion.ch47.integrated
Writes companion/ch47/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch47 import sources as src
from companion.ch47.common import emit
from plantp import civilmfg as cv


# [start: hand]
def by_hand() -> dict:
    ch = src.CERTS[4]["chem"]                       # plate P105
    e = ch["c"] + ch["mn"] / 6 + ch.get("cr", 0) / 5 + ch.get("cu", 0) / 15
    bar = 32 ** 2 / 162                             # kg/m
    sec, d0, d1, t_mm, ln = src.TOWER[0]
    can = math.pi * (d0 + d1) / 2 * t_mm / 1000 * (ln / 10) * src.STEEL_RHO
    # [end: hand]
    lines = ["three numbers of this chapter checked by hand",
             f"  CEV of P105 = 0.20 + 1.55/6 + 0.10/5 + 0.10/15 = {e:.3f} "
             f"(code {cv.cev(**ch):.3f})",
             f"  32 mm bar: 32^2/162 = {bar:.2f} kg/m (code {cv.bar_mass(32):.2f})",
             f"  one can of section 1: pi x {(d0 + d1) / 2:.2f} m x {t_mm} mm x "
             f"{ln / 10:.1f} m x 7850 = {can / 1000:.1f} t",
             "  ten cans make the 122 t shell of lesson A; a hand check of one",
             "  number per formula protects every table that uses it"]
    emit("int_hand", lines)
    return dict(cev=e, bar=bar, can=can / 1000)


def acceptance() -> dict:
    from companion.ch47 import examples_b as eb
    from companion.ch47 import examples_c as ec
    from companion.ch47 import lab_d
    rel = lab_d.release()
    ce = eb.certs()
    wl = eb.welders()
    nd = eb.ndt()
    tk = eb.tickets()
    stg = eb.strength()
    an = ec.anchor()
    lines = ["acceptance of turbine T05's tower and foundation, summarised",
             f"  plates: {len(ce)} of {len(src.CERTS)} certificates do not match the "
             "order",
             f"  welds: {len(wl)} joints by welders not qualified on the day; NDT "
             f"short: {', '.join(nd['short'])}",
             "  sections releasable: "
             + ", ".join(str(k) for k, v in rel.items() if v == 0)
             + "; held: " + ", ".join(f"{k} ({v})" for k, v in rel.items() if v),
             f"  foundation pour: {len(tk['bad'])} trucks outside the rules; pours "
             f"not conforming: {', '.join(stg)}",
             f"  anchor cage: {an['t1']:.2f} mm/m after the pour, {an['lean']:.0f} mm "
             "at the hub - grout decision",
             "  nothing here shows in the finished tower: the steel looks",
             "  the same, the concrete is grey - only the records carry the",
             "  difference between a proven and an unproven structure"]
    emit("int_accept", lines)
    return dict(rel=rel)


def basis() -> None:
    lines = ["D-051 civil, structural and tracker manufacturing and acceptance basis",
             "  1 every plate's certificate checked against the order (grade,",
             "    thickness, impact temperature and each value, CEV) before",
             "    cutting; plate-to-can marks kept to the section",
             "  2 weld log checked against welder qualifications on the weld",
             "    dates; NDT coverage against the plan by weld category",
             "  3 sections released only with a complete dossier; NCRs owned",
             "    and dated; release note last",
             "  4 tracker tubes surveyed for straightness; drive end-of-line",
             "    records complete; zinc by lot (mean and each reading)",
             "  5 bar bending schedules validated before cutting; delivery",
             "    tickets checked at the gate; strength conformity by pour",
             "  6 anchor cage levelled before and after the pour; post rows",
             "    surveyed and split into systematic and random offsets",
             "  7 every decision on a nonconforming item taken by the named",
             "    responsible person - licensed engineers for structure and",
             "    ground - and filed with the record",
             "  8 later findings: sections weighed and their mass sent to",
             "    logistics (section 1 needs 16 axles) and to the frequency",
             "    check; certificates of the specific kind; one bolt lot a",
             "    flange; embedded items a hold point; 7-day strengths as a",
             "    warning; holds booked ahead; tower lines 63 days ahead",
             "  open: fabricator's qualification records and the geotechnical",
             "    report's final values (U-128)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    acceptance()
    basis()
