"""Chapter 22, lab D - the worked example: three fictional sites ranked
with the scores of lab B and with the finance model of chapter 21, a
challenge to the weighted score, the disqualifiers, and the next
evidence each site needs.

Each site enters the chapter 21 model through its energy, its cost
including grid reinforcement, its later COD (delay against P-Central's
32 months from the review) and its lenders' P90 (wider when the evidence is weaker).

Run from the project root:   python -m companion.ch22.lab_d
Writes companion/ch22/expected/d_*.txt and diagrams/data/ch22-*.csv.
"""
from __future__ import annotations

from companion.ch21 import model, sources as s21
from companion.ch22 import lab_b, sources as src
from companion.ch22.common import csv, emit

U_SITE = {"P-North": 0.09, "P-Central": 0.051, "P-South": 0.065}   # A-313
BUILD = {"P-North": 18, "P-Central": 18, "P-South": 16}   # months
LIFTED = 275.0     # P-South energy without the 70 MW limit (GWh)


# [start: finance]
def site_finance(name: str) -> dict:
    """The chapter 21 model with the site's energy (lenders size the
    debt on it), its cost with grid works and its lenders' P90; the NPV
    at financial close is brought back to the review date."""
    f = src.SITES[name]
    keep = s21.P90_1Y
    s21.P90_1Y = 1 - 1.282 * U_SITE[name]          # lenders' P90, ch 16
    e = f["energy"] / 295.14
    r = model.run(energy_scale=e, sizing_energy=e,
                  capex_scale=(f["capex"] + f["reinforce"])
                  / s21.capex_total())
    s21.P90_1Y = keep
    r["close_months"] = f["schedule"] - BUILD[name]
    wacc = s21.TERMS["wacc"]
    r["npv_today"] = r["npv"] / (1 + wacc) ** (r["close_months"] / 12)
    return r
# [end: finance]


def ranking() -> None:
    s = lab_b.score_matrix()
    dev = lab_b.ap.weighted(s, lab_b.WEIGHTS["developer"])
    lines = ["worked example: three sites, scores and money (teaching):",
             "                              debt    equity      NPV k u",
             "  site       GWh  score    k u       IRR %   at close    today"]
    rows = []
    for i, n in enumerate(lab_b.NAMES):
        r = site_finance(n)
        lines.append(f"  {n:9s} {src.SITES[n]['energy']:4.0f}  {dev[i]:5.2f}  {r['debt']:8,.0f}"
                     f"  {r['equity_irr'] * 100:8.2f}  {r['npv']:9,.0f}  {r['npv_today']:7,.0f}")
        rows.append((i + 1, f"{src.SITES[n]['energy']:.0f}", f"{r['equity_irr'] * 100:.2f}"))
    n_, c_ = site_finance("P-North"), site_finance("P-Central")
    lines += ["  (NPV today: the NPV at financial close discounted at the WACC",
              f"  over the months to close: P-North {n_['close_months']}, P-Central"
              f" {c_['close_months']}, P-South {site_finance('P-South')['close_months']})",
              "  P-North makes 12 % more energy and its NPV at close is the",
              "  highest, but it reaches close 22 months later, so its NPV",
              "  today is below P-Central's; lenders size its debt on a P90",
              "  widened by thin data, so its owners earn less; two flags may",
              "  stop it. P-South's weak grid caps its export: NPV negative.",
              "  P-Central, with 11 % less energy, ranks first on score, on",
              "  equity return and on NPV today - by money alone its lead over",
              "  P-North is thin: the flags, the evidence and the time decide"]
    emit("d_ranking", lines)
    csv("ch22-sites.csv", "k,energy,irr", rows)


def challenge() -> None:
    lines = ["challenging the weighted score:",
             "  1 change the weights: P-North needs an energy weight of"
             f" {lab_b.flip_weight() * 100:.0f} %",
             "    (lab B); its two flags stay whatever the weights",
             "  2 change the set: adding or removing a site moves min-max",
             "    scores; the money results do not move",
             "  3 change the evidence: if a full campaign confirmed P-North's"]
    r = site_finance("P-North")
    U_SITE["P-North"] = 0.051
    r2 = site_finance("P-North")
    U_SITE["P-North"] = 0.09
    c = site_finance("P-Central")
    lines += ["    330 GWh with P-Central's uncertainty, its equity IRR would go",
              f"    from {r['equity_irr'] * 100:.2f} to {r2['equity_irr'] * 100:.2f} %"
              f" (P-Central {c['equity_irr'] * 100:.2f} %): the money gap is",
              "    evidence, not physics - the flags and the 22 months remain"]
    keep = src.SITES["P-South"]["energy"]
    src.SITES["P-South"]["energy"] = LIFTED
    r3 = site_finance("P-South")
    src.SITES["P-South"]["energy"] = keep
    r4 = site_finance("P-South")
    lines += ["  4 change a fact: if P-South's grid study lifted the 70 MW limit",
              f"    ({keep:.0f} -> {LIFTED:.0f} GWh), its NPV at close would go from"
              f" {r4['npv']:,.0f}",
              f"    to {r3['npv']:,.0f} k u and its equity IRR from"
              f" {r4['equity_irr'] * 100:.2f} to {r3['equity_irr'] * 100:.2f} %",
              "  a score is challenged by changing one input at a time and",
              "  recording whether the decision changes"]
    emit("d_challenge", lines)


def next_evidence() -> None:
    need = {
        "P-North": ["bird survey and avoidance layout", "resettlement feasibility",
                    "grid reinforcement offer", "12-month mast campaign"],
        "P-Central": ["grid connection offer (late; U-065, U-068)", "ESIA approval and permits",
                      "land agreements for 2 parcels", "PPA terms and EPC price"],
        "P-South": ["grid strength study (SCR, export limit)", "water supply permit",
                    "heritage survey of 2 sites", "consultation with seasonal herders"],
    }
    lines = ["disqualifiers and next evidence (the decision is conditional):",
             "  P-North: two flags (birds, displacement) - stop spending; if",
             "    it is ever reopened, a cheap bird survey comes first",
             "  P-South: no flag; NPV negative unless the grid limit is lifted"]
    for n, items in need.items():
        lines.append(f"  {n}: next evidence")
        lines += [f"    - {x}" for x in items]
    lines += ["  decision (D-026): continue P-Central to the financeability",
              "  gate; P-South stays on file, unfunded, with one deciding",
              "  question (its grid limit); P-North stops (flags, and its",
              "  development tree in section H is worth nothing)"]
    emit("d_next", lines)


if __name__ == "__main__":
    ranking()
    challenge()
    next_evidence()
