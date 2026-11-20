"""Chapter 21, overbuild: more PV behind the same 100 MW connection,
priced in the finance model (energy gains from chapter 15's overbuild
lesson, cost from chapter 18's screening cost per MW).

Run from the project root:   python -m companion.ch21.examples_t
Writes companion/ch21/expected/t_*.txt.
Teaching values A-287, A-304 to A-310.
"""
from __future__ import annotations

from companion.ch18 import sources as s18
from companion.ch21 import model, sources as src
from companion.ch21.common import emit

DELIVERED = {50: 295.63, 60: 315.63, 70: 334.74, 80: 352.81, 90: 369.92}   # ch 15


def overbuild() -> None:
    lines = ["more PV behind the same 100 MW connection (S1, debt resized):",
             "  PV MW   extra capex k u   energy x   equity IRR %   NPV k u"]
    for mw, gwh in DELIVERED.items():
        extra = (mw - 50) * s18.COST["pv_per_mw_ac"] * (1 + src.CONTINGENCY)
        r = model.run(capex_scale=1 + extra / src.capex_total(),
                      energy_scale=gwh / DELIVERED[50],
                      opex_scale=1 + (mw - 50) * 10.0 / sum(src.OPEX.values()))
        lines.append(f"  {mw:5d}   {extra:15,.0f}   {gwh / DELIVERED[50]:8.3f}"
                     f"   {r['equity_irr'] * 100:12.2f}   {r['npv']:7,.0f}")
    lines += ["  each added 10 MW block adds less NPV (5.1, 4.6, 3.9, 3.3",
              "  million) because more of its energy is curtailed at the",
              "  limit; the shared connection makes the first blocks cheap",
              "  energy, and the gain stops where the marginal energy no",
              "  longer pays for the block; the PPA must accept the extra",
              "  energy and the grid offer must allow it (ch 17)"]
    emit("t_overbuild", lines)


if __name__ == "__main__":
    overbuild()
