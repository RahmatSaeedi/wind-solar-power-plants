"""Chapter 22 - three integrated Plant P examples: the fatal-flaw screen
by hand, the site decision as a traceable record, and the feasibility
basis (D-026).

Run from the project root:   python -m companion.ch22.integrated
Writes companion/ch22/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch22 import lab_d, sources as src
from companion.ch22.common import emit


def by_hand() -> None:
    f = src.SITES["P-North"]
    lines = ["P-North's flags by hand:",
             f"  bird overlap {f['bird_overlap']:.0%} > 25 % -> flag",
             f"  displaced households {f['displaced']} > 0 without a plan -> flag",
             f"  grid: {f['grid_free_mw']:.0f} MW free, reinforcement {f['reinforce']:,.0f} k u offered",
             "    -> no flag (but its cost and a 30-month wait)",
             f"  permits {f['permit_months']} months <= 36 -> no flag"]
    emit("int_hand", lines)


def record() -> None:
    r = {n: lab_d.site_finance(n) for n in src.SITES}
    lines = ["decision record D-026 (site and next stage):",
             "  decision: develop P-Central to G4; P-South kept on file,",
             "            unfunded; P-North stopped (two flags)",
             "  evidence: flags (A), scores and stability (B), plan and",
             "            review (C), money and challenge (D), gates (E),",
             "            financeability (F), social screen (G), tree (H)",
             "  equity IRR %: " + ", ".join(
                 f"{n} {r[n]['equity_irr'] * 100:.2f}" for n in src.SITES),
             "  NPV today k u: " + ", ".join(
                 f"{n} {r[n]['npv_today']:,.0f}" for n in src.SITES),
             "  conditions: grid offer, ESIA approval, land agreements,",
             "              PPA, EPC price before the investment decision",
             "  owner of the decision: the developer's board; advisers:",
             "  yield, grid, ESIA, social, legal (local counsel)"]
    emit("int_record", lines)


def basis() -> None:
    lines = ["feasibility basis of Plant P at month 14 (one page):",
             "  site          P-Central (ch 13-21); alternatives screened",
             "  energy        295.1 GWh P50 (D-019), sigma 5.1 % (D-020)",
             "  cost          156,450 k u with 5 % allowance; Monte Carlo",
             "                P80 158,443 before allowance (6.3 %)",
             "  schedule      close month 28 (plan); P80 33.6 months;",
             "                grid chain now critical",
             "  money         equity IRR 10.2 %, DSCR 1.20 on P90 (D-025)",
             "  development   6,500 k u to close: 1,800 spent, 4,700 to go;",
             "                EV of going on 569 k u (own money)",
             "  social        9 households, no displacement; consultation",
             "                and grievance channel open",
             "  open          grid offer, ESIA approval, 2 land parcels,",
             "                PPA, EPC price, 9 of 12 CPs",
             "  verdict       continue development; not yet an investment"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    record()
    basis()
