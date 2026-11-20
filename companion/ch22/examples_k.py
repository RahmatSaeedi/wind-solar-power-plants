"""Chapter 22 - four more lessons: weights elicited by swing weighting
(and why they depend on the ranges), a stakeholder map by interest and
influence, the downside of each site as break-even energies, and the
construction water balance of the water-scarce site.

Run from the project root:   python -m companion.ch22.examples_k
Writes companion/ch22/expected/k_*.txt. Teaching values (A-312, A-314,
A-315); the stakeholders are fictional types, not real people.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as s21
from companion.ch22 import lab_b, lab_d, sources as src
from companion.ch22.common import emit
from plantp import appraisal as ap
from plantp import finance as fn

# [start: swing]
SWING = {   # points for moving each criterion from worst to best site
    "energy": 100, "cost incl. grid": 80, "time to COD": 50,
    "grid readiness": 35, "environment": 20, "social": 20,
    "constructability": 30,
}


def swing_weights(points: dict) -> np.ndarray:
    """Weights proportional to the points given to each swing."""
    v = np.array([points[c[0]] for c in lab_b.CRITERIA], float)
    return v / v.sum()
# [end: swing]


def swing() -> None:
    w = swing_weights(SWING)
    s = lab_b.score_matrix()
    tot = ap.weighted(s, w)
    lines = ["weights from a swing-weighting interview (developer, teaching):",
             "  criterion          points  weight   developer set"]
    for k, (lab, *_r) in enumerate(lab_b.CRITERIA):
        lines.append(f"  {lab:18s} {SWING[lab]:6d}  {w[k]:6.2f}   {lab_b.WEIGHTS['developer'][k]:12.2f}")
    lines.append("  totals: " + ", ".join(f"{n} {t:.2f}" for n, t in zip(lab_b.NAMES, tot)))
    # range effect: P-North's energy lead was a guess; if the energy swing
    # were only 295 -> 330 instead of 262 -> 330, its points should fall
    narrow = dict(SWING, energy=round(100 * (330 - 295.14) / (330 - 262)))
    w2 = swing_weights(narrow)
    lines += [f"  if the energy range shrank to 295-330 GWh the swing is"
              f" {(330 - 295.14) / (330 - 262):.0%} as large:",
              f"  energy points {narrow['energy']}, weight {w[0]:.2f} -> {w2[0]:.2f}",
              "  a weight answers 'how much does moving from the worst to the",
              "  best option on this criterion matter?' - it depends on the",
              "  range of the options, so weights are re-asked when the set",
              "  of options changes"]
    emit("k_swing", lines)


def stakeholders() -> None:
    reg = [  # fictional types: (name, interest 1-5, influence 1-5)
        ("landholders of two parcels", 5, 4), ("village council", 5, 3),
        ("seasonal herders (P-South)", 5, 2), ("grid operator", 3, 5),
        ("permitting authority", 3, 5), ("lenders", 4, 5),
        ("local businesses", 3, 2), ("environmental group", 4, 3),
        ("nearby town residents", 2, 2), ("turbine maker", 3, 3),
    ]
    lines = ["stakeholder map by interest and influence (fictional types):",
             "  stakeholder                    interest  influence  approach"]
    for name, i, f in reg:
        hi_i, hi_f = i >= 4, f >= 4
        how = ("manage closely" if hi_i and hi_f else "keep satisfied" if hi_f
               else "involve and consult" if hi_i else "keep informed")
        lines.append(f"  {name:30s} {i:8d} {f:10d}  {how}")
    lines += ["  the map sets how often and how deeply each group is engaged;",
              "  it does not rank whose rights count - people with high",
              "  interest and little influence (herders, the village) need",
              "  the most deliberate consultation, not the least"]
    emit("k_stakeholders", lines)


# [start: downside]
def breakevens(name: str) -> tuple[float, float]:
    """Energy (share of the site's P50) at which the minimum DSCR falls
    to 1.00 with the debt fixed at close, and at which the NPV is 0."""
    f = src.SITES[name]
    e = f["energy"] / 295.14
    k = (f["capex"] + f["reinforce"]) / s21.capex_total()
    keep = s21.P90_1Y
    s21.P90_1Y = 1 - 1.282 * lab_d.U_SITE[name]
    d = model.run(energy_scale=e, sizing_energy=e, capex_scale=k)["debt"]
    s21.P90_1Y = keep
    run = lambda x: model.run(energy_scale=e * x, sizing_energy=e,  # noqa
                              capex_scale=k, debt=d)
    x_dscr = fn.breakeven(lambda x: run(x)["min_dscr"], 0.5, 1.2, 1.0)
    x_npv = fn.breakeven(lambda x: run(x)["npv"], 0.5, 1.5, 0.0)
    return x_dscr, x_npv
# [end: downside]


def downside() -> None:
    lines = ["downside of each site: energy at which the plant breaks even",
             "(share of its own P50; debt fixed at close; teaching):",
             "  site       DSCR 1.00 at   NPV 0 at   lenders' P90 1-yr   P99 1-yr"]
    for n in src.SITES:
        x_d, x_n = breakevens(n)
        u = lab_d.U_SITE[n]
        lines.append(f"  {n:9s} {x_d * 100:11.1f} %  {x_n * 100:8.1f} %   {(1 - 1.282 * u) * 100:14.1f} %"
                     f"   {(1 - 2.326 * u) * 100:7.1f} %")
    lines += ["  P-Central keeps paying its lenders in a P99 year; P-North's",
              "  wider uncertainty puts its P99 year below its DSCR",
              "  break-even; P-South's NPV is negative even at P50 (break-even",
              "  above 100 %): resource downside is read against each",
              "  site's own uncertainty, not against one common percentage"]
    emit("k_downside", lines)


def water() -> None:
    days = 540                            # 18 months of building
    demand = {   # m3 over the build (teaching, A-315)
        "turbine foundations (12 x 650 m3 concrete x 0.2)": 12 * 650 * 0.2,
        "other concrete and grout": 900.0,
        "dust on 25 km of tracks (2 m3/km a day, 300 days)": 25 * 2 * 300,
        "worker camp (270 people x 0.1 m3 a day)": 270 * 0.1 * days,
        "PV module first cleaning": 600.0,
    }
    tot = sum(demand.values())
    well = 40.0 * days                    # m3: a teaching well yield
    lines = ["construction water at P-South (water scarce, teaching):"]
    lines += [f"  {k:50s} {v:8,.0f}" for k, v in demand.items()]
    lines += [f"  total demand {tot:,.0f} m3; well at 40 m3 a day {well:,.0f} m3",
              f"  shortfall {tot - well:,.0f} m3 = {(tot - well) / 25:,.0f} truck loads of 25 m3",
              "  water is a buildability item (trucks, storage, cost) and a",
              "  social one: the herders' wells serve the same aquifer; the",
              "  supply permit and a water plan agreed with the users come",
              "  before the site can be chosen (sections A and G, ch 18)"]
    emit("k_water", lines)


# [start: permits]
PERMITS = {  # generic categories; months from the month-14 review (A-314)
    "grid offer (late)": (2, []),
    "ESIA approval": (5, []),
    "land-use consent": (5, []),
    "aviation clearance": (4, []),
    "water abstraction": (4, []),
    "transport permit": (2, []),
    "grid connection agreement": (2, ["grid offer (late)"]),
    "construction permit": (3, ["ESIA approval", "land-use consent"]),
    "generation licence": (3, ["ESIA approval",
                               "grid connection agreement"]),
}
VALID = {"ESIA approval": 36, "construction permit": 24}   # months
# [end: permits]


def permits() -> None:
    total, crit, slack = ap.critical_path(PERMITS)
    ef = {}
    for t, (d, pre) in PERMITS.items():        # listed in order
        ef[t] = d + max((ef[q] for q in pre), default=0.0)
    lines = ["permit register as a network (generic categories, months from",
             "the month-14 review; teaching durations):",
             "  permit                       ends at month   slack"]
    for t in PERMITS:
        lines.append(f"  {t:28s} {14 + ef[t]:13.0f}   {slack[t]:5.0f}")
    lines += [f"  all permits in hand at month {14 + total:.0f}; critical:",
              "    " + ", ".join(t for t in crit if t != "grid offer (late)")]
    start = 28                                 # construction after close
    lines.append(f"  validity against the start of building (month {start}):")
    for t, v in VALID.items():
        lines.append(f"    {t}: valid {v} months, expires at month"
                     f" {14 + ef[t] + v:.0f}, margin {14 + ef[t] + v - start:.0f}")
    lines += ["  the permits sit inside the plan's 8 months, with the licence",
              "  as critical as the construction permit; each permit with a",
              "  validity is checked against the start of building, and the",
              "  real list, durations and validity come from the country's",
              "  rules (ch 55-57)"]
    emit("k_permits", lines)


if __name__ == "__main__":
    swing()
    stakeholders()
    downside()
    water()
    permits()
