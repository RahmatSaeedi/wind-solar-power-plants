"""Chapter 47, round s: a tracker row's torque at stow and its thermal
movement, can fit-up from the plate cut lengths, zinc on the PV field,
concrete specimens and the laboratory, the fabricator's NCR causes, the
dossiers of all twelve towers, a cracked can traced back and forward,
and the inspector's visits.

Run from the project root:   python -m companion.ch47.examples_s
Writes companion/ch47/expected/s_*.txt and diagrams/data/ch47-*.csv.
Teaching values (A-490 to A-497); no design approval implied.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as s30
from companion.ch47 import sources as src
from companion.ch47.common import csv, emit
from plantp import structures as st


# ------------------------------------------------ 1. tracker torque at stow
def stow(cm: float = 0.10, modules: int = 52, hold_knm: float = 40.0) -> dict:
    chord = s30.PV_TABLE["module_l"]
    area = modules * s30.PV_TABLE["module_w"] * chord
    rho = s30.SITE["rho"]
    lines = [f"single-axis tracker row: {modules} modules in portrait, chord "
             f"{chord} m, area {area:.0f} m2",
             f"  hinge moment T = q Cm A c, Cm {cm} at stow (teaching); drive holds "
             f"{hold_knm:.0f} kN m",
             "  wind m/s   q Pa   torque kN m   share of the drive"]
    out = {}
    for v in (12.0, 18.0, 30.0, s30.SITE["gust50_10m"]):
        q = 0.5 * rho * v * v
        t = q * cm * area * chord / 1000
        out[v] = t
        lines.append(f"  {v:8.1f}   {q:4.0f}   {t:11.1f}   {t / hold_knm:17.0%}")
    lines += ["  the 50-year gust uses most of the drive's holding torque even",
              "  at stow: a drive with large backlash (lesson B) starts to",
              "  rock in gusts and the row can flutter - the static number",
              "  is the easy part; the dynamic check is the tracker maker's",
              "  wind-tunnel and test evidence (ch 39)"]
    emit("s_stow", lines)
    return out


# ------------------------------------------------ 2. thermal movement of a tube
def thermal(length_m: float = 60.0, dt: float = 40.0) -> dict:
    d = st.thermal_expansion(s30.STEEL["alpha"], length_m, dt) * 1000
    lines = [f"a {length_m:.0f} m torque tube between a winter night and a summer "
             f"noon (+/-{dt:.0f} K)",
             f"  movement {d:.1f} mm each way from the reference temperature",
             "  the bearings let the tube slide; a bearing installed with no",
             "  room at one end, or a tube clamped at both ends, turns that",
             "  movement into force on the posts - the installation record",
             "  gives the temperature on the day the bearings were set"]
    emit("s_thermal", lines)
    return dict(mm=d)


# ------------------------------------------------ 3. can fit-up from cut lengths
CUT_DEV = [2, -1, 12, -9, 1, 0, -7, 2, 4, -2]     # mm on the circumference


def fitup(t_mm: float = 46.0) -> dict:
    lim = min(0.1 * t_mm, 3.0)
    dd = [x / math.pi for x in CUT_DEV]
    lines = [f"section 1: plate cut lengths against the drawing, and the step "
             f"between cans",
             f"  (teaching limit for the step: min(0.1 t, 3 mm) = {lim:.1f} mm)",
             "  seam    dev A mm   dev B mm   step mm   verdict"]
    bad = []
    for k in range(len(CUT_DEV) - 1):
        stp = abs(dd[k] - dd[k + 1]) / 2
        ok = stp <= lim
        if not ok:
            bad.append(k + 1)
        lines.append(f"  {k + 1:4d}   {CUT_DEV[k]:8d}   {CUT_DEV[k + 1]:8d}   "
                     f"{stp:7.2f}   {'ok' if ok else 'OVER'}")
    lines += [f"  over: seam {', '.join(map(str, bad))} - a can cut 12 mm long next "
              "to one cut",
              "  9 mm short leaves a step the welder cannot bridge; the cut",
              "  length is checked before rolling, when a re-cut is cheap,",
              "  not at fit-up (ch 30 ovality)"]
    emit("s_fitup", lines)
    return dict(bad=bad, lim=lim)


# ------------------------------------------------ 4. zinc on the PV field
def zinc_mass(steel_t: float = 3211.0, m2_per_t: float = 30.0, um: float = 85.0,
              rho_zn: float = 7.14) -> dict:
    area = steel_t * m2_per_t
    zn = area * um * 1e-6 * rho_zn
    lines = [f"zinc on the PV field's {steel_t:,.0f} t of steel (teaching: "
             f"{m2_per_t:.0f} m2 a tonne)",
             f"  surface {area:,.0f} m2; at {um:.0f} um and {rho_zn} t/m3: "
             f"{zn:,.0f} t of zinc",
             "  the zinc is the PV structure's corrosion life (ch 30) and a",
             "  share of its footprint (ch 33): a lot below the thickness",
             "  rule (lesson B) shortens both"]
    emit("s_zinc", lines)
    return dict(zn=zn, area=area)


# ------------------------------------------------ 5. specimens and laboratory
def specimens(m3_per_set: float = 50.0, per_set: int = 3, per_day: int = 40) -> dict:
    sets = math.ceil(src.BASE_CONCRETE / m3_per_set)
    n = sets * per_set * src.TURBINES
    lines = [f"concrete specimens: one set of {per_set} for each {m3_per_set:.0f} m3 "
             "(teaching)",
             f"  one foundation of {src.BASE_CONCRETE:.0f} m3: {sets} sets, "
             f"{sets * per_set} specimens",
             f"  twelve foundations: {n} specimens; at {per_day} a day the "
             f"laboratory needs {n / per_day:.0f} days",
             "  pours run on a schedule set by the turbine deliveries: the",
             "  laboratory's capacity, curing tanks and the 28-day date of",
             "  each pour belong in the construction plan (ch 49)"]
    emit("s_specimens", lines)
    return dict(sets=sets, n=n)


# ------------------------------------------------ 6. NCR causes
CAUSES = {"dimensions": 14, "coating": 9, "welding": 8, "documents": 5,
          "materials": 3, "other": 1}


def pareto() -> dict:
    tot = sum(CAUSES.values())
    lines = [f"causes of the fabricator's last {tot} NCRs (synthetic)",
             "  cause        count   share   cumulative"]
    cum = 0
    for c, n in sorted(CAUSES.items(), key=lambda x: -x[1]):
        cum += n
        lines.append(f"  {c:11s}  {n:5d}   {n / tot:5.0%}   {cum / tot:10.0%}")
    top2 = sum(sorted(CAUSES.values(), reverse=True)[:2]) / tot
    lines += [f"  two causes make {top2:.0%}: dimensions (ovality, flange",
              "  flatness) and coating - the audit of the fabricator (ch 39)",
              "  goes to the rolling, the flange welding sequence and the",
              "  paint shop first"]
    emit("s_pareto", lines)
    return dict(top2=top2, tot=tot)


# ------------------------------------------------ 7. dossiers of the farm
def farm(seed: int = 4702, p_miss: float = 0.03, per_day: float = 2.0) -> dict:
    rng = np.random.default_rng(seed)
    items = len(src.DOSSIER)
    miss = rng.random((src.TURBINES, 4, items)) < p_miss
    miss[4, 0] = [not ok for ok in src.DOSSIER.values()]   # T05 section 1 as lesson C
    gaps = int(miss.sum())
    complete = int((~miss.any(axis=2)).sum())
    csv("ch47-farm.csv", "tower,s1,s2,s3,s4,held",
        [(t + 1, *[int(miss[t, s].sum()) for s in range(4)],
          int(miss[t].any(axis=1).sum())) for t in range(src.TURBINES)])
    lines = [f"dossiers of {src.TURBINES} towers x 4 sections ({items} documents each)",
             f"  documents missing: {gaps}; sections complete: {complete} of "
             f"{src.TURBINES * 4}",
             f"  at {per_day:.0f} documents closed a day: {gaps / per_day:.0f} working "
             "days of document work",
             f"  {gaps / miss.size:.1%} of the documents missing sounds small; it "
             f"leaves {1 - complete / (src.TURBINES * 4):.0%}",
             "  of the sections unreleasable - tracked per section, not as",
             "  one percentage (ch 46 dossier)"]
    emit("s_farm", lines)
    return dict(gaps=gaps, complete=complete)


# ------------------------------------------------ 8. a cracked can, back and forward
OTHER = {"P203": ("T06", ["1-07", "1-08"]), "P311": ("T09", ["2-02", "2-03", "2-04"])}


def crack(can: str = "1-08") -> dict:
    plate = next(p for p, cans in src.PLATES.items() if can in cans)
    heat = next(c["heat"] for c in src.CERTS if c["plate"] == plate)
    sib = [c for c in src.PLATES[plate] if c != can]
    lines = [f"UT finds a lamination in can {can} of T05:",
             "  back to the plate, forward to its siblings",
             f"  can {can} <- plate {plate} <- heat {heat}",
             f"  same plate, same tower: cans {', '.join(sib)}",
             "  same heat, other towers (the fabricator's heat register):"]
    for p, (t, cans) in OTHER.items():
        lines.append(f"    {p} -> {t}: cans {', '.join(cans)}")
    n = len(sib) + sum(len(v[1]) for v in OTHER.values())
    lines += [f"  {n} other cans get a UT scan for laminations before release;",
              "  the heat register is the fabricator's, so the buyer asks for",
              "  it - one record turns 'check every tower' into a list"]
    emit("s_crack", lines)
    return dict(plate=plate, heat=heat, n=n)


# ------------------------------------------------ 9. inspector visits
def visits(holds_per_section: int = 6, per_day: int = 3,
           full_towers: int = 2) -> dict:
    all_v = holds_per_section * 4 * src.TURBINES
    sample_v = holds_per_section * 4 * full_towers + 2 * 4 * (src.TURBINES -
                                                              full_towers)
    lines = [f"buyer's inspection of the {src.TURBINES} towers (teaching)",
             f"  every hold point of every section: {all_v} visits, "
             f"{all_v / per_day:.0f} inspector-days",
             f"  {full_towers} towers in full, the rest at plate receipt and release: "
             f"{sample_v} visits, {sample_v / per_day:.0f} days",
             "  the saving is real only if the records of the towers not",
             "  witnessed are read line by line (lessons B and C): sampling",
             "  the visits is not sampling the records"]
    emit("s_visits", lines)
    return dict(all=all_v, sample=sample_v)


if __name__ == "__main__":
    stow()
    thermal()
    fitup()
    zinc_mass()
    specimens()
    pareto()
    farm()
    crack()
    visits()
