"""Chapter 21 - three integrated Plant P examples: a simple payback and
LCOE by hand, the bankability verdict on the alternatives, and the
finance basis of the plant (D-025).

Run from the project root:   python -m companion.ch21.integrated
Writes companion/ch21/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


def by_hand() -> None:
    cap = src.capex_total()
    rev = 295.14 * 0.99 * T["tariff"]
    opx = sum(src.OPEX.values())
    crf = 0.05 / (1 - 1.05 ** -25)
    lines = ["Plant P on the back of an envelope (year-1 money):",
             f"  revenue 295.14 GWh x 0.99 x 70 u = {rev:,.0f} k u",
             f"  operating cost {opx:,.0f}; margin {rev - opx:,.0f} k u a year",
             f"  simple payback {cap:,.0f} / {rev - opx:,.0f} = {cap / (rev - opx):.1f} years",
             f"  capital recovery factor 5 %, 25 yr = {crf:.4f}",
             f"  LCOE ~ ({cap:,.0f} x {crf:.4f} + {opx:,.0f}) / 288,854 MWh"
             f" = {(cap * crf + opx) / 288.854:.1f} u/MWh",
             "  (288,854 MWh = mean of the 25-year energy series; the model's",
             "  LCOE adds replacements and decommissioning: 54.3)"]
    emit("int_hand", lines)


def basis() -> None:
    r = model.run()
    lines = ["finance basis of Plant P (D-025), from this chapter:",
             f"  uses {r['uses']:,.0f} k u: capex {r['capex']:,.0f}, IDC {r['idc']:,.0f},"
             f" fee {r['fee']:,.0f}, DSRA {r['dsra']:,.0f}",
             f"  debt {r['debt']:,.0f} ({r['gearing'] * 100:.0f} %), 15 yr sculpted,"
             f" sized by {r['binding']}",
             f"  equity {r['equity']:,.0f}; equity IRR {r['equity_irr'] * 100:.1f} %,"
             f" project IRR {r['project_irr'] * 100:.1f} %",
             f"  min DSCR {r['min_dscr']:.2f}, average {r['avg_dscr']:.2f}, min LLCR {r['min_llcr']:.2f}",
             "  stresses: P99 every year, tariff -10 %, unhedged rate +2 points",
             "  reach lock-up; buyer 6 months late needs the DSRA",
             "  revenue: flat PPA in the base; time-of-day, services and",
             "  carbon only as labelled sensitivities until verified",
             "  conditions precedent: 9 of 12 open (not yet bankable)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    basis()
