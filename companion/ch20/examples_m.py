"""Chapter 20, two more lessons: receding-horizon dispatch (plan the
next H hours every hour, execute only the first) for several look-ahead
lengths, and upward reserve sized from the forecast level (dynamic)
against one constant reserve.

Run from the project root:   python -m companion.ch20.examples_m
Writes companion/ch20/expected/m_*.txt.
Teaching values A-299 to A-302.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import examples_b as eb, examples_e as ee, sources as src
from companion.ch20.common import emit
from plantp import control as ct

L = src.LIMITS


# [start: receding]
def receding(h_ahead: int, wear: float = 10.0) -> float:
    """Every hour, plan the next h_ahead hours from the day-ahead
    forecast (ending at e_min) and execute only the first hour."""
    act = np.clip(src.poc_actual(), 0, None)
    fc = np.clip(src.poc_forecast(24), 0, None)
    cap, price = eb.caps(), src.prices()
    c = ct.Controller(e=L["e_min"])
    val = 0.0
    for t in range(8760 - h_ahead):
        g = slice(t, t + h_ahead)
        _, _, plan = ct.dp_schedule(price[g], np.minimum(fc[g], L["bess_mw"]),
                                    np.clip(cap[g] - fc[g], 0, None),
                                    L["bess_mw"], L["e_min"], L["e_max"],
                                    round(c.e), L["eta"], wear=wear,
                                    e_end=L["e_min"])
        r = c.step(t, act[t], plan[0], cap[t], True)
        val += r["export"] * price[t]
    return val
# [end: receding]


def horizons() -> None:
    act = np.clip(src.poc_actual(), 0, None)
    cap, price = eb.caps(), src.prices()
    n = 8760 - 24
    no_bess = float((np.minimum(act, cap) * price)[:n].sum())
    lines = ["receding-horizon dispatch: look-ahead length (8,736 hours):",
             "  look-ahead h   battery adds k u"]
    for h in (2, 4, 8, 12, 24):
        v = receding(h)
        # same hours for every case: stop at 8760 - 24
        lines.append(f"  {h:12d}   {(v - no_bess - extra(h)) / 1000:16.0f}")
    lines += ["  a plan that sees only a few hours sells the battery too",
              "  early (it must end empty); with prices that change between",
              "  morning, midday and evening a look-ahead of about half a day",
              "  captures almost all the value; re-planning every hour lets",
              "  each plan use the latest energy and forecast"]
    emit("m_receding", lines)


def extra(h: int) -> float:
    """Export value of the hours a shorter run covers beyond 8760 - 24."""
    act = np.clip(src.poc_actual(), 0, None)
    cap, price = eb.caps(), src.prices()
    return float((np.minimum(act, cap) * price)[8760 - 24:8760 - h].sum())


def reserve_sizing() -> None:
    act = np.clip(src.poc_actual(), 0, 100)
    idf = np.clip(src.poc_forecast(4), 0, 100)
    short = idf - act
    bins = np.digitize(idf, np.arange(0, 110, 10))
    req = np.zeros(8760)
    for b in np.unique(bins):
        m = bins == b
        tr = m & (np.arange(8760) < ee.TRAIN.stop)
        req[m] = np.quantile(short[tr], 0.95) if tr.sum() > 20 else 0.0
    req = np.clip(req, 0, None)
    const = np.quantile(short[ee.TRAIN], 0.95)
    test = np.arange(8760) >= ee.TEST.start
    lines = ["upward reserve for 95 % cover of the intraday shortfall (test months):",
             "  rule                     mean reserve MW   cover %   MW-h held"]
    for name, r in (("constant", np.full(8760, const)), ("by forecast level", req)):
        cov = (short[test] <= r[test]).mean() * 100
        lines.append(f"  {name:24s} {r[test].mean():15.1f}   {cov:7.1f}   {r[test].sum():9,.0f}")
    lines += ["  a reserve that follows the forecast level holds less on",
              "  average for about the same cover: little at night when the",
              "  forecast is low, more at high output; the rule is fitted on",
              "  January-August and tested on September-December"]
    emit("m_reserve", lines)


if __name__ == "__main__":
    horizons()
    reserve_sizing()
