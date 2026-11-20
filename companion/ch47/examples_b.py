"""Chapter 47, lesson B: fabrication and production records - mill
certificates against the order, a heat traced to cans and sections,
welder qualifications on the weld dates, NDT coverage against the plan,
a tracker's torque tube and drives, zinc on PV posts, a bar bending
schedule, batching tickets of one pour and strength conformity.

Run from the project root:   python -m companion.ch47.examples_b
Writes companion/ch47/expected/b_*.txt and diagrams/data/ch47-*.csv.
Teaching values (A-490 to A-494); no welding, heat-treatment or cure
values to apply, no concrete mix.
"""
from __future__ import annotations

from companion.ch47 import sources as src
from companion.ch47.common import csv, emit
from plantp import civilmfg as cv


# ------------------------------------------------ 1. mill certificates
def certs() -> dict:
    o = src.ORDER
    lines = [f"mill certificates against the order: {o['grade']}, "
             f"{o['t_range'][0]}-{o['t_range'][1]} mm,",
             f"  impact at {o['impact_c']} C >= {o['impact_j']} J (each of three), "
             f"CEV <= {o['cev_max']}",
             "  plate  heat    t mm   CEV    finding"]
    bad = {}
    for c in src.CERTS:
        p = cv.check_cert(c, o)
        e = cv.cev(**c["chem"])
        if p:
            bad[c["plate"]] = p
        lines.append(f"  {c['plate']}   {c['heat']}  {c['t_mm']:4d}   {e:.2f}   "
                     f"{'; '.join(p) or 'ok'}")
    lines += [f"  {len(bad)} of {len(src.CERTS)} plates do not match the order:",
              "  a certificate tested at 0 C says nothing about -20 C; a mean",
              "  of three impacts can pass while one specimen fails; a high",
              "  CEV needs more preheat than the qualified procedure assumed;",
              "  a lower grade is a different steel - each is a hold, not a",
              "  remark (ch 30 preheat, ch 40 certificates)"]
    emit("b_certs", lines)
    return bad


# ------------------------------------------------ 2. heat to sections
def genealogy(heat: str = "H5523") -> dict:
    plates = [c["plate"] for c in src.CERTS if c["heat"] == heat]
    cans = [k for p in plates for k in src.PLATES[p]]
    sections = sorted({k.split("-")[0] for k in cans})
    lines = [f"heat {heat} (impact tested at the wrong temperature): where did it go?",
             f"  plates: {', '.join(plates)}",
             f"  cans: {', '.join(cans)}",
             f"  tower section(s): {', '.join(sections)}",
             "  four cans of section 1 - the lowest, most loaded one - come",
             "  from a plate whose toughness at -20 C is unknown: the maker",
             "  re-tests specimens from the same heat at -20 C or the cans",
             "  are replaced; without the plate-to-can marks the whole",
             "  section would be in question"]
    emit("b_genealogy", lines)
    return dict(plates=plates, cans=cans, sections=sections)


# ------------------------------------------------ 3. welders on the weld dates
def welders() -> list:
    bad = []
    lines = [f"weld log of section 1 against the welders' qualifications",
             "  joint   welder  process  position  date         finding"]
    for j, w, p, pos, d in src.WELD_LOG:
        r = cv.qualified(src.WELDERS[w], p, pos, d)
        if r != "ok":
            bad.append((j, w, r))
        lines.append(f"  {j:6s}  {w}    {p:5s}    {pos:8s}  {d}   {r}")
    lines += [f"  {len(bad)} joints welded by someone not qualified for them on that",
              "  day: an expired card, a position not covered, a process not",
              "  held - the welds may be good, but they are not proven; the",
              "  fix is the procedure's: extra NDT of those joints and a",
              "  qualification test, decided by the fabricator's welding",
              "  coordinator and accepted by the inspector"]
    emit("b_welders", lines)
    return bad


# ------------------------------------------------ 4. NDT coverage
def ndt() -> dict:
    cov = cv.coverage(src.NDT_PLAN, src.NDT_DONE)
    lines = ["NDT coverage of section 1 against the inspection plan",
             "  weld category     plan    done    status"]
    short = []
    for k, (share, low) in cov.items():
        if low:
            short.append(k)
        lines.append(f"  {k:16s}  {src.NDT_PLAN[k]:5.0%}   {share:5.0%}   "
                     f"{'SHORT' if low else 'ok'}")
    lines += [f"  short: {', '.join(short)} - 1.2 m of 30 m inspected; the plan asks",
              "  for 10 %: 3.0 m; the attachments (ladder brackets, cable",
              "  clamps) are where fatigue cracks start on a tower wall, so",
              "  the 10 % is chosen across all attachment types, not the",
              "  easiest ones (ch 30 fatigue, door frame)"]
    emit("b_ndt", lines)
    return dict(short=short)


# ------------------------------------------------ 5. tracker
def tracker(limit_mm: float = 12.0, backlash_max: float = 0.15) -> dict:
    off, x = cv.straightness(src.TUBE["x"], src.TUBE["y"])
    csv("ch47-tube.csv", "x,y", list(zip(src.TUBE["x"], src.TUBE["y"])))
    lines = [f"tracker row R-17: torque tube surveyed every 6 m over 60 m",
             f"  largest offset from the chord {off:.1f} mm at {x:.0f} m "
             f"(teaching limit {limit_mm:.0f} mm)",
             f"  slew drives at end of line (backlash limit {backlash_max} deg):"]
    odd = []
    for s, b, hold, lub in src.DRIVES:
        why = []
        if b > backlash_max:
            why.append(f"backlash {b} deg")
        if not hold:
            why.append("holding test missing")
        if why:
            odd.append((s, why))
        lines.append(f"    {s}  {b:.2f} deg  {hold or '-':4s}  lubricant {lub}  "
                     f"{'; '.join(why) or 'ok'}")
    lines += ["  a bent tube puts the modules of one row at several angles and",
              "  loads the bearings sideways; a drive with large backlash lets",
              "  the row flutter in wind instead of holding its stow angle;",
              "  the drive with the large backlash and the one with no holding",
              "  record both used lubricant lot L-8 (so did SD-306, which",
              "  passed) - a question to the maker, not yet a verdict on the lot"]
    emit("b_tracker", lines)
    return dict(off=off, x=x, odd=odd)


# ------------------------------------------------ 6. zinc on PV posts
def zinc() -> dict:
    lines = ["hot-dip zinc on PV posts by lot (teaching rule: mean >= 85 um,",
             "  each reading >= 70 um)",
             "  lot    steel mm   mean um   lowest um   verdict"]
    bad = []
    for lot, (t, r) in src.ZINC.items():
        m, lo = sum(r) / len(r), min(r)
        mn, each = src.ZINC_MIN[t]
        ok = m >= mn and lo >= each
        if not ok:
            bad.append(lot)
        lines.append(f"  {lot}   {t:8.1f}   {m:7.1f}   {lo:9d}   "
                     f"{'ok' if ok else 'REJECT'}")
    lines += [f"  rejected: {', '.join(bad)} - posts from it would lose their zinc",
              "  years early in the site's aggressive soil (ch 30 zinc life);",
              "  the lot is re-galvanized or used where the soil is mild,",
              "  decided by the designer, with the post numbers recorded"]
    emit("b_zinc", lines)
    return dict(bad=bad)


# ------------------------------------------------ 7. bar bending schedule
def bbs() -> dict:
    probs = cv.check_bbs(src.BBS, src.DIAS, src.SHAPES)
    mass = cv.bbs_mass([r for r in src.BBS
                        if r["mark"] not in {m for m, _ in probs}])
    lines = [f"bar bending schedule of one foundation (excerpt, {len(src.BBS)} rows)",
             "  mark   problem"]
    lines += [f"  {m:5s}  {p}" for m, p in probs]
    lines += [f"  {len(probs)} problems; mass of the clean rows {mass / 1000:.1f} t "
              f"(d^2/162 kg/m)",
              "  a length of 3.6 'mm' would cut 240 stubs; a duplicate mark",
              "  makes two bundles answer to one label on site; a 22 mm bar",
              "  is not stocked and would be swapped without a record - the",
              "  schedule is checked before the bars are cut, like the cable",
              "  schedule of ch 46"]
    emit("b_bbs", lines)
    return dict(probs=probs, mass=mass)


# ------------------------------------------------ 8. batching tickets
def tickets(max_min: float = 90.0, max_temp: float = 32.0) -> dict:
    bad = []
    csv("ch47-tickets.csv", "truck,minutes,temp",
        [(t["truck"], t["discharged_min"], t["temp_c"]) for t in src.TICKETS])
    for t in src.TICKETS:
        p = cv.check_ticket(t, max_min, max_temp, 0.0)
        if p:
            bad.append((t["truck"], p))
    lines = [f"delivery tickets of the T05 foundation pour, {len(src.TICKETS)} trucks "
             f"(teaching rules:", f"  discharged within {max_min:.0f} min, concrete "
             f"<= {max_temp:.0f} C, no water added on site)"]
    lines += [f"  truck {k}: {'; '.join(p)}" for k, p in bad]
    lines += [f"  {len(bad)} trucks outside the rules; the concrete of each is either",
              "  refused at the gate or its place in the pour is recorded, so",
              "  the strength results and any core later can be tied to it;",
              "  water added on site raises the water-cement ratio the mix was",
              "  designed for - the supplier's mix design, not the driver,",
              "  decides what may be added"]
    emit("b_tickets", lines)
    return dict(bad=bad)


# ------------------------------------------------ 9. strength conformity
def strength(fck: float = 35.0) -> dict:
    lines = [f"28-day strength by pour against a teaching conformity rule, class {fck:.0f}:",
             f"  mean of three >= {fck + 4:.0f} MPa and each >= {fck - 4:.0f} MPa",
             "  pour   results MPa          mean   verdict"]
    bad = {}
    for p, r in src.CUBES.items():
        c = cv.conformity(r, fck)
        why = []
        if not c["ok_mean"]:
            why.append("mean")
        if not c["ok_each"]:
            why.append(f"one result {c['lowest']}")
        if why:
            bad[p] = why
        lines.append(f"  {p}    {', '.join(f'{x:.1f}' for x in r):19s}  {c['mean']:5.1f}   "
                     f"{'ok' if not why else 'FAIL ' + ', '.join(why)}")
    lines += [f"  not conforming: {', '.join(bad)}",
              "  F03 is low all round (a weak delivery); F04 has one low",
              "  specimen among two good ones (a bad specimen or a bad truck) -",
              "  the tickets of that pour and the specimen records decide",
              "  which; the structural engineer decides on cores and on what",
              "  the foundation needs (ch 29 characteristic strength)"]
    emit("b_strength", lines)
    return bad


if __name__ == "__main__":
    certs()
    genealogy()
    welders()
    ndt()
    tracker()
    zinc()
    bbs()
    tickets()
    strength()
