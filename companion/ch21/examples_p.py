"""Chapter 21, operations in the economics: stacking battery uses within
the warranty's cycle budget, a strategic spare transformer against the
expected outage cost, and degradation faster than assumed.

Run from the project root:   python -m companion.ch21.examples_p
Writes companion/ch21/expected/p_*.txt.
Teaching values: cycles from ch 19-20, reliability from ch 18 (A-288).
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch18 import sources as s18
from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


def stacking() -> None:
    uses = {"shifting (ch 20)": (469.0, 336), "absorbing deviations (k_imbalance)": (389.0, 292)}
    budget = 365                                  # warranty cycles a year (ch 19)
    lines = ["two battery uses against the warranty's 365 cycles a year:",
             "  use                                  k u/yr   cycles   k u per cycle"]
    for k, (v, c) in uses.items():
        lines.append(f"  {k:36s} {v:7,.0f}   {c:6d}   {v / c:13.2f}")
    v1, c1 = uses["shifting (ch 20)"]
    v2, c2 = uses["absorbing deviations (k_imbalance)"]
    left = budget - c1
    both = v1 + left * v2 / c2
    lines += [f"  both at full size: {c1 + c2} cycles - outside the warranty",
              f"  shifting first, then absorbing in the {left} cycles left:"
              f" {both:,.0f} k u/yr",
              "  the warranty is a resource like the converter and the SOC",
              "  window: a use is worth its value per cycle, and the cycle",
              "  budget is shared by the contract, not by the controller"]
    emit("p_stacking", lines)


def spare() -> None:
    """Two 63 MVA main transformers; one failing leaves about 60 MW of
    export; a failure is repaired in 4,380 h without a spare and 720 h
    with one (ch 18, A-288); energy above 60 MW in those hours is lost."""
    poc = np.clip(s15.plant_year()["poc"], 0, 100)
    lost_share = np.clip(poc - 60.0, 0, None).sum() / poc.sum()
    e_year = 295.14 * 0.99
    rel = s18.REL
    lam = 2 * rel["trafo_fail"]
    loss_no = lam * e_year * lost_share * rel["trafo_repair_h"] / 8760 * T["tariff"]
    loss_sp = lam * e_year * lost_share * rel["trafo_spare_h"] / 8760 * T["tariff"]
    cost = s18.COST["trafo_63"]
    gain = fn.pv(np.full(25, loss_no - loss_sp) * fn.index(0.02, 25), T["wacc"])
    lines = ["a strategic spare main transformer (k u):",
             f"  share of energy above 60 MW: {lost_share * 100:.1f} %",
             f"  failures a year (two units) {lam:.2f}",
             f"  expected loss a year: no spare {loss_no:,.0f}, with spare {loss_sp:,.0f}",
             f"  PV of the difference over 25 years {gain:,.0f} against a spare at {cost:,.0f}",
             "  on expected value the spare does not pay; it buys protection",
             "  against a six-month half-plant outage (about "
             f"{e_year * lost_share * 0.5 * T['tariff']:,.0f} k u),",
             "  which lenders and insurers may require - or a shared spare",
             "  pool with other plants"]
    emit("p_spare", lines)


def degradation() -> None:
    base = model.run()
    n = T["years"]
    y = np.arange(1, n + 1)
    lines = ["degradation faster than assumed (debt fixed):",
             "  case                                   min DSCR   equity IRR %"]
    cases = {"base (PV 0.5 %/yr)": np.ones(n),
             "PV 0.8 %/yr": 1 - 108.36 / 295.14 * 0.003 * (y - 1),
             "PV 0.8 %/yr and wind -0.3 %/yr": (1 - 108.36 / 295.14 * 0.003 * (y - 1)
                                                - 191.87 / 295.14 * 0.003 * (y - 1))}
    for k, path in cases.items():
        r = model.run(debt=base["debt"], energy_path=path)
        lines.append(f"  {k:38s} {r['min_dscr']:8.2f}   {r['equity_irr'] * 100:12.2f}")
    lines += ["  slow losses grow with time: they hurt the late loan years",
              "  and the merchant tail most; warranties on degradation and",
              "  monitoring (ch 51-53) are worth what they recover"]
    emit("p_degradation", lines)


if __name__ == "__main__":
    stacking()
    spare()
    degradation()
