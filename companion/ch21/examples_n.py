"""Chapter 21, finance mechanics: cash trapped by the lock-up test,
depreciation profiles and the value of tax timing, working-capital
days, equity-first against pro-rata drawdown, funding a cost overrun
layer by layer, the lenders' case against the sponsor's, and payback.

Run from the project root:   python -m companion.ch21.examples_n
Writes companion/ch21/expected/n_*.txt.
Teaching values A-304 to A-310; no tax law of any country.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


# [start: trap]
def with_lockup(r: dict) -> np.ndarray:
    """Equity cash flow when distributions stop in every loan year with
    DSCR below the lock-up level; trapped cash is paid out in the first
    later year that passes the test (or with the last debt payment)."""
    nd = T["tenor"]
    eq = r["cfads"] - r["ds"]
    out = eq.copy()
    trapped = 0.0
    for t in range(nd):
        if r["dscr"][t] < T["lockup"]:
            trapped += max(out[t], 0.0)
            out[t] = min(out[t], 0.0)
        elif trapped:
            out[t] += trapped
            trapped = 0.0
    out[nd - 1] += trapped + r["dsra"]
    ph = T["construction"]
    return np.concatenate([[-r["equity"] * ph[0], -r["equity"] * ph[1]], out])
# [end: trap]


def lockup() -> None:
    base = model.run()
    r = model.run(debt=base["debt"], energy_scale=src.P90_1Y, price_scale=0.95,
                  opex_scale=1.10, capex_scale=1.05)
    lines = ["cash trapped by the lock-up test (combined downside, no delay):",
             f"  lock-up years {int((r['dscr'] < T['lockup']).sum())} of {T['tenor']}",
             f"  equity IRR, distributions as earned: {r['equity_irr'] * 100:.2f} %",
             f"  equity IRR, cash trapped and released later: {fn.irr(with_lockup(r)) * 100:.2f} %",
             "  the cash is not lost, only late (the owners lose a little",
             "  time value here); the lenders keep it in the project while",
             "  the cover is weak, which is the purpose of the test"]
    emit("n_lockup", lines)


def depreciation() -> None:
    n = T["years"]
    sl = np.zeros(n)
    sl[:20] = 1 / 20
    db = np.zeros(n)                          # declining balance 10 %, then rest
    left = 1.0
    for t in range(n):
        db[t] = left * 0.10 if t < 19 else 0.0
        left -= db[t]
    db[19] += left
    fast = np.zeros(n)
    fast[:5] = 1 / 5
    lines = ["depreciation profile and tax timing (teaching tax rate 25 %):",
             "  profile                       equity IRR %   min DSCR   tax yrs 1-5 k u"]
    for name, sh in (("straight line 20 yr", sl), ("declining balance 10 %", db),
                     ("accelerated 5 yr", fast)):
        r = model.run(dep_shares=sh)
        lines.append(f"  {name:29s} {r['equity_irr'] * 100:12.2f}   {r['min_dscr']:8.2f}"
                     f"   {r['tax'][:5].sum():15,.0f}")
    lines += ["  the same total depreciation, earlier: less tax in the first",
              "  years and more later - the owners gain through time value,",
              "  but the tax returns inside the loan life and the cover falls",
              "  to 1.08: lenders size on the real tax profile; which profile",
              "  is allowed is tax law (U-083), never assumed"]
    emit("n_depreciation", lines)


def working_capital() -> None:
    lines = ["receivable days and the year-1 cover:",
             "  days   WC built yr 1 k u   min DSCR   equity IRR %"]
    keep = T["receivable_days"]
    base = model.run()
    for d in (30, 45, 90):
        T["receivable_days"] = d
        r = model.run(debt=base["debt"])
        lines.append(f"  {d:4d}   {r['dwc'][0]:17,.0f}   {r['min_dscr']:8.2f}   {r['equity_irr'] * 100:12.2f}")
    T["receivable_days"] = keep
    lines += ["  a slow-paying buyer turns revenue into a loan to the buyer:",
              "  the first year carries it; payment terms are a PPA clause"]
    emit("n_wc", lines)


def drawdown() -> None:
    r = model.run()
    capex, debt, eq = r["capex"], r["debt"], r["equity"]
    spend = capex * np.array(T["construction"])
    # pro rata: each year's spend shared in the gearing; equity first:
    # equity pays until used, then debt
    eq1 = min(eq, spend[0])
    debt_y1 = spend[0] - eq1
    idc_first = T["rate"] * (debt_y1 / 2 + debt_y1 + spend[1] / 2)
    lines = ["equity first or pro rata during construction:",
             f"  pro rata: IDC {r['idc']:,.0f} k u; equity paid 40/60 over two years",
             f"  equity first: IDC about {idc_first:,.0f} k u; equity paid in year -1",
             "  equity first saves interest but asks the owners for their",
             "  money earlier (their return falls); lenders like it because",
             "  the owners' money is at risk before theirs"]
    emit("n_drawdown", lines)


def overrun() -> None:
    cap = src.capex_total()
    cont = cap / (1 + src.CONTINGENCY) * src.CONTINGENCY
    standby = 0.10 * model.run()["equity"]
    lines = ["funding a cost overrun layer by layer (k u):",
             f"  contingency inside the budget {cont:,.0f}; standby equity {standby:,.0f}",
             "  overrun %   from contingency   standby equity   left to fund"]
    for o in (0.03, 0.08, 0.15):
        over = o * cap / (1 + src.CONTINGENCY)
        a = min(over, cont)
        b = min(over - a, standby)
        lines.append(f"  {o * 100:9.0f}   {a:16,.0f}   {b:14,.0f}   {over - a - b:12,.0f}")
    lines += ["  beyond both layers the project needs new money before the",
              "  lenders release more: a cost-overrun facility or sponsor",
              "  support - agreed at financial close, not when it happens"]
    emit("n_overrun", lines)


def lenders_case() -> None:
    sponsor = model.run()
    keep = dict(T)
    r = model.run(opex_scale=1.10, curtail_extra=0.01, energy_scale=0.99)
    lenders = model.run(opex_scale=1.10, curtail_extra=0.01, energy_scale=0.99,
                        sizing_price=0.97)
    T.update(keep)
    lines = ["the lenders' case against the sponsor's (teaching haircuts):",
             "  lenders add 10 % to opex, 1 % more curtailment, 1 % less",
             "  energy and size on a price 3 % lower:",
             f"  sponsor case: debt {sponsor['debt']:,.0f}, equity IRR {sponsor['equity_irr'] * 100:.2f} %",
             f"  lenders' case: debt {lenders['debt']:,.0f}, equity IRR"
             f" {lenders['equity_irr'] * 100:.2f} % (if the haircuts come true)",
             "  the debt follows the lenders' case, not the sponsor's: every",
             "  optimistic input the lenders do not accept becomes equity"]
    emit("n_lenders", lines)


def payback() -> None:
    r = model.run()
    proj = np.concatenate([[-0.4 * r["capex"], -0.6 * r["capex"]],
                           r["ebitda"] - r["repl"] - r["dwc"] - r["decom"] - r["tax"]])
    cum = np.cumsum(proj)
    disc = np.cumsum(proj / (1 + T["wacc"]) ** np.arange(-1, proj.size - 1))
    sp = int(np.argmax(cum > 0)) - 1
    dp = int(np.argmax(disc > 0)) - 1
    lines = ["payback of the project cash flow (after the tax paid):",
             f"  simple payback: operating year {sp}",
             f"  discounted at 7.5 %: operating year {dp}",
             "  payback says when the money is back, not how much value is",
             "  made after; it is a liquidity measure, never a substitute",
             "  for NPV"]
    emit("n_payback", lines)


if __name__ == "__main__":
    lockup()
    depreciation()
    working_capital()
    drawdown()
    overrun()
    lenders_case()
    payback()
