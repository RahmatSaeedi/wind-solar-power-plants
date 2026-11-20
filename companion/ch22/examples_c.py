"""Chapter 22, sections C, E, F and G - the development plan as a
critical path, the development budget by stage, a risk register, the
value of a bird survey, stage gates scored against evidence, the
financeability gate (estimate class, contingency, funding, downside,
open conditions), and the social-safeguards screen with a livelihood
restoration budget and labour influx.

Run from the project root:   python -m companion.ch22.examples_c
Writes companion/ch22/expected/c_*.txt, e_*.txt, f_*.txt, g_*.txt.
Teaching values A-311 to A-314; safeguards screened, not judged.
"""
from __future__ import annotations

from companion.ch21 import model
from companion.ch22 import sources as src
from companion.ch22.common import emit
from plantp import appraisal as ap

# [start: plan]
TASKS = {   # months, predecessors (P-Central, the plan drawn at G1)
    "wind campaign (12 mo)": (12, []),
    "grid study and offer": (9, []),
    "ESIA baseline and report": (14, []),
    "land options and access": (4, []),
    "land agreements": (9, ["land options and access"]),
    "geotechnical survey": (4, ["land options and access"]),
    "energy yield report": (2, ["wind campaign (12 mo)"]),
    "permits": (8, ["ESIA baseline and report", "land options and access"]),
    "front-end design": (6, ["energy yield report", "grid study and offer",
                             "geotechnical survey"]),
    "PPA negotiation": (8, ["energy yield report"]),
    "financing and close": (6, ["permits", "front-end design",
                                "PPA negotiation", "land agreements"]),
}
# [end: plan]
TODAY = 14                       # the review month (section D)
LEFT = {"grid study and offer": 2, "land agreements": 3}   # late tasks
DONE = ["wind campaign (12 mo)", "ESIA baseline and report",
        "land options and access", "geotechnical survey", "energy yield report"]


def plan() -> None:
    total, crit, slack = ap.critical_path(TASKS)
    lines = ["development plan of P-Central as a network (months):",
             f"  months to financial close: {total:.0f}",
             "  critical path:"]
    lines += [f"    {t}" for t in crit]
    lines.append("  slack of the others:")
    lines += [f"    {t:28s} {slack[t]:4.0f}" for t in TASKS if t not in crit]
    lines += ["  two chains are critical, 28 months each: wind campaign ->",
              "  yield report -> PPA, and ESIA -> permits; a month lost on",
              "  either moves financial close; the ESIA needs its seasons",
              "  (ch 33), so it starts on day one with the campaign"]
    emit("c_plan", lines)
    ef = {}
    for t, (d, pre) in TASKS.items():          # tasks are listed in order
        ef[t] = d + max((ef[q] for q in pre), default=0.0)
    from companion.ch22.common import csv
    csv("ch22-gantt.csv", "k,start,dcrit,dnon",
        [(i + 1, f"{ef[t] - TASKS[t][0]:.0f}",
          f"{TASKS[t][0] if t in crit else 0:.0f}",
          f"{0 if t in crit else TASKS[t][0]:.0f}") for i, t in enumerate(TASKS)])


def status() -> None:
    """Month 14: five tasks done, two late; recompute from today."""
    now = {t: (0.0 if t in DONE else LEFT.get(t, d), pre)
           for t, (d, pre) in TASKS.items()}
    total, crit, slack = ap.critical_path(now)
    lines = [f"progress review at month {TODAY}:",
             "  done: " + ", ".join(t.split(" (")[0] for t in DONE[:3]) + ",",
             "        " + ", ".join(DONE[3:]),
             f"  late: grid offer due month 9, now forecast {TODAY + LEFT['grid study and offer']};",
             f"        land agreements due month 13, now forecast {TODAY + LEFT['land agreements']}",
             f"  financial close forecast: month {TODAY + total:.0f} (plan 28)",
             "  critical now:"]
    lines += [f"    {t}" for t in crit if now[t][0] > 0]
    lines += [f"  slack left: land agreements {slack['land agreements']:.0f} months",
              "  close holds at 28, but the grid chain has used all its slack",
              "  and is now critical: one more month on the grid offer moves",
              "  financial close; a review re-runs the network from today"]
    emit("c_status", lines)


def budget() -> None:
    stages = [("G1 screening", 300), ("G2 measurement and studies", 1_500),
              ("G3 permits, grid, land", 2_200), ("G4 PPA, design, financing", 2_500)]
    tot = sum(c for _, c in stages)
    lines = ["development budget by stage gate (k u, teaching):",
             "  gate                          spend   cumulative"]
    cum = 0
    for g, c in stages:
        cum += c
        lines.append(f"  {g:28s} {c:6,}   {cum:10,}")
    lines += [f"  total {tot:,} k u = {tot / 156_450 * 100:.1f} % of the capital cost,",
              "  spent at risk before any lender commits: equity of the",
              "  developer, recovered at financial close if the project goes"]
    emit("c_budget", lines)


def risks() -> None:
    reg = [("grid offer later than 12 months", 0.40, 2_500),
           ("ESIA finds a sensitive species", 0.15, 8_000),
           ("land parcel holdout", 0.20, 3_000),
           ("wind lower than modelled by 3 %", 0.30, 4_500),
           ("turbine price +8 %", 0.25, 6_200)]
    lines = ["development risk register (probability, impact k u):",
             "  risk                                 p     impact   expected"]
    for r, p, c in reg:
        lines.append(f"  {r:36s} {p:4.2f}  {c:7,}   {p * c:8,.0f}")
    lines += [f"  expected cost {ap.risk_cost([(p, c) for _, p, c in reg]):,.0f} k u;"
              " the largest impact is the ESIA species",
              "  risk (low chance, large impact): a cheap early survey buys",
              "  most of it down (below); the largest expected cost is the",
              "  turbine price, which only a firm price at G4 removes"]
    emit("c_risks", lines)


def voi() -> None:
    """Spend 120 k u on an early bird survey at P-North: with 35 %
    overlap the chance of a stop is 50 %; without the survey the
    developer would spend 1,500 more before finding out (teaching)."""
    p_stop, spend_more, survey = 0.5, 1_500.0, 120.0
    lines = ["value of an early bird survey at P-North (k u):",
             f"  chance the overlap stops the project {p_stop:.0%}",
             f"  without the survey: {spend_more:,.0f} spent before finding out,"
             f" expected loss {p_stop * spend_more:,.0f}",
             f"  with the survey: {survey:,.0f} spent first; value of the information"
             f" {p_stop * spend_more - survey:,.0f}",
             "  cheap evidence that can stop a project comes first: the",
             "  screening sequence of section A in money"]
    emit("c_voi", lines)


def gates() -> None:
    crit = {"G2 measurement and studies": ["resource 12 months", "grid study started",
                                           "ESIA scoping", "land options signed"],
            "G3 permits, grid, land": ["energy yield report", "grid offer", "ESIA approved",
                                       "land agreements", "geotechnical"],
            "G4 PPA, design, financing": ["PPA signed", "front-end design",
                                          "EPC price", "lender diligence"]}
    have = {"P-Central": {"resource 12 months", "grid study started", "ESIA scoping",
                          "land options signed", "energy yield report", "geotechnical"},
            "P-South": {"grid study started", "ESIA scoping", "land options signed"},
            "P-North": {"ESIA scoping"}}
    lines = ["stage gates against the evidence in hand (teaching):"]
    for site, ev in have.items():
        lines.append(f"  {site}:")
        for g, need in crit.items():
            got = sum(1 for x in need if x in ev)
            status = "pass" if got == len(need) else f"{got}/{len(need)}"
            lines.append(f"    {g:28s} {status}")
    lines += ["  a gate passes only when every listed item is in hand; the",
              "  investment decision (G4) waits for the signed documents,",
              "  not for a score"]
    emit("e_gates", lines)


def financeability() -> None:
    base = model.run()
    classes = [("screening (G1)", -0.30, 0.50), ("feasibility (G2-G3)", -0.20, 0.30),
               ("FEED / bid (G4)", -0.10, 0.15)]
    lines = ["cost estimate maturity (teaching accuracy ranges):",
             "  class                      low k u     high k u   contingency"]
    for name, lo, hi in classes:
        a, b = ap.estimate_range(base["capex"], lo, hi)
        lines.append(f"  {name:24s} {a:10,.0f}   {b:10,.0f}   {hi / 2 * 100:8.0f} %")
    lines += ["  (contingency here: half the upper range, a teaching rule)",
              "  financeability scorecard of P-Central before G4:",
              "    estimate class          feasibility: +30 % still possible",
              "    development funding     6,500 k u by financial close",
              "    yield and revenue       P50/P90 reviewed; PPA not signed",
              "    grid and permits        offer and ESIA approval open",
              "    schedule, supply, O&M   plan exists; no price yet",
              "    downside                break-even energy 85.9 % of P50",
              "    open conditions         9 of 12 (ch 21 CP register)",
              "  verdict: not yet financeable - continue development, not",
              "  the investment decision"]
    emit("f_finance", lines)


def social() -> None:
    lines = ["social-safeguards screen (issues that could change the site):",
             "  issue                        P-North     P-Central   P-South"]
    rows = [("land and livelihood", "high", "low", "medium"),
            ("physical displacement", "6 hh", "none", "none"),
            ("seasonal land users", "-", "-", "40 families"),
            ("labour influx vs local", "high", "low", "medium"),
            ("cultural heritage", "1 site", "none", "2 sites"),
            ("community health, safety", "road", "road", "water"),
            ("consultation started", "no", "yes", "partly")]
    for r in rows:
        lines.append(f"  {r[0]:28s} {r[1]:11s} {r[2]:11s} {r[3]}")
    f = src.SITES
    per_hh, per_ha = 60.0, 1.2      # k u, teaching restoration costs
    lines.append("  livelihood restoration budget (teaching, k u):")
    for n in f:
        cost = (f[n]["households"] * per_hh + f[n]["displaced"] * 400
                + f[n]["grazing_ha"] * per_ha + f[n]["seasonal"] * 20)
        lines.append(f"    {n:10s} {cost:8,.0f}")
    lines += ["  the screen flags, the specialists assess and the affected",
              "  people are consulted; a resettlement or livelihood plan that",
              "  meets the lenders' and the permit's conditions is a cost and",
              "  a schedule item - and can change which site is chosen"]
    emit("g_social", lines)


if __name__ == "__main__":
    plan()
    status()
    budget()
    risks()
    voi()
    gates()
    financeability()
    social()
