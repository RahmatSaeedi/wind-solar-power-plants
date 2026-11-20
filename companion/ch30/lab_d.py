"""Chapter 30, lab D (worked example): compare conceptual foundation
schemes for one turbine under alternative soil assumptions - a 20 m
gravity base, a 24 m gravity base, a 20 m base on improved ground, and a
piled base - against lift-off in production, the effective area and
pressure in the extreme case, rocking stiffness for the 1P margin,
settlement, and concrete and cost. Conceptual only: the geotechnical
and structural engineers choose and design (ch 29, Q1-Q10).

Run from the project root:   python -m companion.ch30.lab_d
Writes companion/ch30/expected/d_*.txt. Teaching values (A-357, A-358, A-362).
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import emit
from plantp import civil as cv
from plantp import structures as st

G = 9.81
M_TOP = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3


def k_needed() -> float:
    f_need = src.ONE_P_MAX * (1 + src.MARGIN_1P)
    f_rot = 1 / math.sqrt(1 / f_need ** 2 - 1 / src.F1_FIXED ** 2)
    return (2 * math.pi * f_rot) ** 2 * M_TOP * src.HUB ** 2


# [start: schemes]
SCHEMES = {   # radius m, concrete and backfill m3; g_mult None = new gravel
    "S1 gravity 20 m": dict(r=10.0, conc=620.0, back=800.0,
                            g_mult=1.0, piles=0),
    "S2 gravity 24 m": dict(r=12.0, conc=893.0, back=1152.0,
                            g_mult=1.0, piles=0),
    "S3 24 m + gravel": dict(r=12.0, conc=893.0, back=1152.0,
                             g_mult=None, piles=0),
    "S4 piled 18 m": dict(r=9.0, conc=560.0, back=650.0,
                          g_mult=None, piles=24),
}
# [end: schemes]
COST = dict(concrete=288.0, gravel_m3=45.0, pile=6_000.0)    # u, teaching (A-362)


def check(name: str, sc: dict, soil: dict, water_high: bool) -> dict:
    """The five conceptual checks of one scheme on one soil assumption."""
    r = sc["r"]
    area = math.pi * r * r
    above = (src.TOP_T + src.TOWER_T) * G / 1e3                 # MN
    sub = 9.81 * area * (src.FOUNDATION["depth"] - 0.5) / 1e3 if water_high else 0.0
    v = above + sc["conc"] * 24 / 1e3 + sc["back"] * 18 / 1e3 - sub
    prod = src.LOADS["production (peak)"]
    ext = src.LOADS["extreme (parked, 50-yr gust)"]
    m_p = prod["m_mnm"] + prod["h_mn"] * src.FOUNDATION["depth"]
    m_e = ext["m_mnm"] + ext["h_mn"] * src.FOUNDATION["depth"]
    e_p = m_p / v
    e_e, a_eff, q_e = st.foundation_pressure(v * 1e3, m_e * 1e3, r)
    if sc["piles"]:
        k = 400e9                                                # teaching piled stiffness
        q_ok, lift_ok = True, True
    else:
        g = soil["g_mpa"] if sc["g_mult"] else 60.0              # S3: improved layer
        k = st.rotational_stiffness(g * 1e6, r, soil["nu"])
        q_lim = soil["q_ult"] if sc["g_mult"] else max(soil["q_ult"], 6000.0)
        q_ok = q_e <= q_lim / 2.0
        lift_ok = e_p <= r / 4
    e_mod = 2 * (soil["g_mpa"] if sc["g_mult"] else 60.0) * 1e3 * (1 + soil["nu"])  # kPa
    settle = 0.0 if sc["piles"] else 1000 * cv.elastic_settlement(v * 1e3 / area, 2 * r, e_mod)
    cost = sc["conc"] * COST["concrete"] + sc["piles"] * COST["pile"]
    if sc["g_mult"] is None and not sc["piles"]:
        cost += math.pi * (r + 2) ** 2 * 2.0 * COST["gravel_m3"]
    return dict(e_p=e_p, lift_ok=lift_ok, a_frac=a_eff / area, q_e=q_e, q_ok=q_ok,
                k=k, k_ok=k >= k_needed(), settle=settle, cost=cost / 1e3)


def compare() -> None:
    cases = [("dense", src.SOILS["dense sand and gravel (T01-T06, T08-T12)"], False),
             ("T07", src.SOILS["medium sand at founding level (T07)"], False),
             ("T07 wet", src.SOILS["T07 with water at 0.5 m"], True)]
    lines = ["conceptual foundation schemes under three soil assumptions (teaching)",
             f"  checks: no lift-off in production (e <= r/4); extreme pressure on the",
             f"  effective area <= q_ult / 2; rocking stiffness >= {k_needed() / 1e9:.0f} GN m/rad",
             "  (wet: water at 0.5 m; S3 sits on 2 m of new compacted gravel; S4 on piles)",
             "  scheme            soil      e/r  A'/A  q' kPa  K GNm  s mm   k u  result"]
    for sname, sc in SCHEMES.items():
        for cname, soil, wet in cases:
            c = check(sname, sc, soil, wet)
            ok = "ok" if (c["lift_ok"] and c["q_ok"] and c["k_ok"]) else "NO"
            why = [] if ok == "ok" else [x for x, good in (("lift", c["lift_ok"]),
                                                             ("q", c["q_ok"]), ("K", c["k_ok"]))
                                         if not good]
            q_txt = " piles" if sc["piles"] else f"{c['q_e']:6.0f}"
            er = "   -" if sc["piles"] else f"{c['e_p'] / sc['r']:4.2f}"
            af = "   -" if sc["piles"] else f"{c['a_frac']:4.2f}"
            res = ok if ok == "ok" else "NO " + ",".join(why)
            lines.append(f"  {sname:16s}  {cname:7s}  {er}  {af}  {q_txt}  {c['k'] / 1e9:5.0f}"
                         f"  {c['settle']:4.0f}  {c['cost']:4.0f}  {res}")
    lines += ["  the 20 m base lifts off in production even on dense",
              "  ground (e > r/4): this turbine needs a wider base; 24 m",
              "  passes on dense ground and at T07, but not with the high",
              "  water (the softer wet soil lowers the stiffness);",
              "  new gravel under the 24 m base or piles pass in every",
              "  case - at T07 the water range (ch 29, Q6) decides between",
              "  them; a comparison of concepts, not a choice"]
    emit("d_schemes", lines)


def questions() -> None:
    qs = ["What operating-strain shear modulus does the engineer adopt at T07, and from"
          " which test (seismic CPT, cross-hole, laboratory)?",
          "Does the turbine maker accept the stiffness rule of A-359, and what dynamic"
          " stiffness does its load document state?",
          "Is the 2 m gravel replacement (S3) stable under the water range of Q6, and how"
          " is its compaction proven?",
          "For S4, what pile capacities in tension and compression, and how many pile"
          " tests?",
          "How is the settlement of the T12 gypsum layer handled (collapse, ch 29)?",
          "Which scheme does the independent design verifier and the certification body"
          " review, and with which load set?"]
    lines = ["questions the comparison raises (for the qualified engineers)"]
    for k, q in enumerate(qs, 1):
        lines.append(f"  F{k} {q}")
    lines += ["  each answer comes back with its source; the scheme is",
              "  chosen by the foundation designer, checked by the",
              "  independent verifier and accepted under the type",
              "  certificate's site-specific assessment"]
    emit("d_questions", lines)


if __name__ == "__main__":
    compare()
    questions()
