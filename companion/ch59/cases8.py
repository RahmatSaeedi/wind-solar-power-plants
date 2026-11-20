"""Chapter 59: design margins, lock-up years in the downside cases, and one
day of forecast against actual output with its band.

Run from the project root:   python -m companion.ch59.cases8
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import csv, emit


def b_margins() -> dict:
    from companion.ch24 import sources as s24
    from companion.ch25 import sources as s25
    from companion.ch39 import sources as s39
    s_exp = 100.0 / 0.95                                   # MVA at the POC, Q at pf 0.95
    i_line = s_exp * 1e6 / (math.sqrt(3) * 132e3)
    i_inc = s25.MAIN["s_mva"] * 1e6 / (math.sqrt(3) * 33e3)
    pv_inv = 5.5                                           # MVA, PCI-5500 (ch 9, ch 44)
    rows = [("main transformers 2 x 63 MVA / export MVA", 2 * s25.MAIN["s_mva"], s_exp),
            ("132 kV line rating / export current, A", s24.LINE["rating_a"], i_line),
            ("33 kV incomer 1,600 A / one transformer, A", 1600.0, i_inc),
            ("PV unit transformer / inverter MVA", s39.PACKAGE["s_mva"], pv_inv)]
    lines = ["design margins of the main ratings (ch 24, 25, 26, 39)",
             f"  {'item':44s} {'rating':>7s} {'need':>7s} {'margin':>7s}"]
    out = {}
    for name, r, nd in rows:
        m = r / nd - 1
        out[name] = m
        lines.append(f"  {name:44s} {r:7.1f} {nd:7.1f} {m:7.1%}")
    lines += ["  the line's margin shrinks with the weather: at 45 C and still",
              "  air it does not carry 437 A (ch 24); the data year's lowest",
              "  rating was 511 A (ch 51). The incomer's margin is in its",
              "  rating, but 1,600 A has no type test yet (ch 46). The PV unit",
              "  transformer's margin is the one ch 25 found missing at 5.5 MVA"]
    emit("b_margins", lines)
    return out


def h_lockup() -> dict:
    from companion.ch21 import model
    from companion.ch21 import sources as s21
    b = model.run()
    lock = s21.TERMS["lockup"]
    cases = [("base", {}), ("P90 one-year energy", {"energy_scale": 275.9 / 295.14}),
             ("price -10 %", {"price_scale": 0.9}),
             ("P90 + price -10 %", {"energy_scale": 275.9 / 295.14, "price_scale": 0.9})]
    lines = [f"years with the DSCR below the lock-up ({lock:.2f}): dividends stop",
             f"  {'case':22s} {'min':>5s} {'years':>5s}  which"]
    out = {}
    for name, ch in cases:
        r = model.run(debt=b["debt"], **ch)
        d = np.asarray(r["dscr"])
        yrs = [i + 1 for i, v in enumerate(d) if v < lock]
        out[name] = yrs
        lines.append(f"  {name:22s} {d.min():5.2f} {len(yrs):5d}  {', '.join(map(str, yrs)) or '-'}")
    lines += ["  the ch 21 model does not hold dividends in a lock-up year, so",
              "  the equity IRR of these cases is a little high; ch 54 priced",
              "  two held years at 10.22 -> 9.90 %"]
    emit("h_lockup", lines)
    return out


def f_day() -> dict:
    from companion.ch15 import forecast as fc
    w_, pv, *_ = fc.truth()
    act = w_ + pv
    wf, pf = fc.nwp(24)
    fcst = wf + pf
    e = act - fcst
    q10, q90 = np.percentile(e[:4380], [10, 90])
    day = 196                                            # a mid-July day (teaching pick)
    h = slice(day * 24, day * 24 + 24)
    a, f = act[h], fcst[h]
    csv("ch59-day.csv", "h,act,fc,lo,hi",
        [(i, round(float(a[i]), 2), round(float(f[i]), 2),
          round(float(max(f[i] + q10, 0.0)), 2), round(float(f[i] + q90), 2)) for i in range(24)])
    inside = float(np.mean((a >= f + q10) & (a <= f + q90)))
    lines = [f"one day (day {day + 1}) of day-ahead forecast against output, MW",
             f"  energy: forecast {f.sum():.0f}, actual {a.sum():.0f} MWh;"
             f" error {a.sum() - f.sum():+.0f} MWh",
             f"  hours inside the P10-P90 band: {inside:.0%}",
             f"  largest hourly shortfall: {-(a - f).min():.1f} MW at hour {int(np.argmin(a - f))}",
             "  one day says little about skill; it shows what the operator",
             "  sees and why the band, not the line, is the schedule's risk"]
    emit("f_day", lines)
    return dict(inside=inside, f=float(f.sum()), a=float(a.sum()))


def main() -> dict:
    out = {}
    for fn_ in (b_margins, h_lockup, f_day):
        out[fn_.__name__] = fn_()
    return out


if __name__ == "__main__":
    main()
