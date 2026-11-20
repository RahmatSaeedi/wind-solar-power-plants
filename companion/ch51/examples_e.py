"""Chapter 51, lessons E (commercial operations), I (forecast-informed
operations) and J (grid-service operations): settlement inputs validated
month by month, a forecast's drifting bias, reserve sized from forecast
error, a P90 schedule against a P50 one, and the service's availability
and suspensions.

Run from the project root:   python -m companion.ch51.examples_e
Writes companion/ch51/expected/e_*.txt, i_*.txt, j_*.txt and
diagrams/data/ch51-bias.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import sources as s20
from companion.ch51 import sources as src
from companion.ch51.common import csv, emit
from plantp import control, operations


# ------------------------------------------------ E. commercial
def settlement() -> dict:
    rows = []
    for m, (sch, met, miss) in src.SETTLE.items():
        dev = met - sch
        rows.append((m, sch, met, dev, miss))
    lines = ["settlement inputs by month: scheduled, metered, missing meter intervals",
             "  month  scheduled MWh  metered MWh  deviation  missing intervals"]
    lines += [f"  {m:5d}  {s:13,d}  {t:11,d}  {d:+9,d}  {x:17d}" for m, s, t, d, x in rows]
    bad = [m for m, *_, x in rows if x > 0]
    lines += [f"  months with missing intervals: {', '.join(map(str, bad))} - each is filled",
              "  from the check meter (ch 48) with a flag before the file goes",
              "  to settlement; June's 30 intervals are a day's work to",
              "  validate, not a figure to estimate"]
    emit("e_settle", lines)
    return dict(bad=bad, rows=rows)


def imbalance_month() -> dict:
    rows = [(m, s, t) for m, (s, t, _) in src.SETTLE.items()]
    sh, lo = s20.IMBALANCE["short"], s20.IMBALANCE["long"]
    cost = {m: control.imbalance([s], [t], sh, lo) for m, s, t in rows}
    lines = [f"imbalance cost by month (short {sh:.0f}, long {lo:.0f} u/MWh, teaching)",
             "  month  deviation MWh  cost u"]
    lines += [f"  {m:5d}  {t - s:+13,d}  {cost[m]:9,.0f}" for m, s, t in rows]
    lines += [f"  half-year {sum(cost.values()):,.0f} u; the short months cost three times",
              "  the long ones per MWh - a schedule that leans low (lesson I)",
              "  trades short penalties for long ones; whether that is",
              "  allowed is the market's or the contract's rule, verified",
              "  locally (ch 55-57)"]
    emit("e_imbalance", lines)
    return cost


# ------------------------------------------------ I. forecast-informed
def bias(window: int = 24 * 7) -> dict:
    act = s20.poc_actual()
    fc = s20.poc_forecast(24).copy()
    fc[24 * 200:] *= 1.12                       # a model update on day 200 (teaching)
    b = operations.rolling_bias(fc, act, window)
    days = np.arange(b.size) / 24
    csv("ch51-bias.csv", "day,bias", [(round(d, 1), round(x, 2))
                                     for d, x in zip(days[::24], b[::24])])
    before = float(b[24 * 150:24 * 190].mean())
    after = float(b[24 * 215:24 * 255].mean())
    lines = [f"rolling one-week bias of the day-ahead forecast (forecast - actual, MW)",
             f"  days 150-190: {before:+.1f} MW; days 215-255: {after:+.1f} MW",
             "  the provider's model update on day 200 moved the forecast up;",
             "  the bias chart shows it within a week, and the shift lead's",
             "  schedule correction is recorded with the forecast version -",
             "  a forecast is an input with a history, not a guarantee"]
    emit("i_bias", lines)
    return dict(before=before, after=after)


def reserve(q: float = 0.95) -> dict:
    act = s20.poc_actual()
    fc = s20.poc_forecast(3)
    err = fc - act
    day = (np.arange(8760) % 24 >= 7) & (np.arange(8760) % 24 < 19)
    up = float(np.quantile(err[day], q))
    lines = [f"intraday (3 h) forecast error, daytime hours of the year",
             f"  {q:.0%} of hours the plant delivers no less than the forecast minus "
             f"{up:.1f} MW",
             f"  a schedule backed to that level needs {up:.1f} MW of reserve from the",
             "  battery or a margin in the declaration; the battery's 20 MW",
             "  covers it, but not together with the 5 MW service and a",
             "  full charge plan - the three compete for one battery"]
    emit("i_reserve", lines)
    return dict(up=up)


def p90_schedule() -> dict:
    act = s20.poc_actual()
    fc = s20.poc_forecast(24)
    err = act - fc
    q10 = float(np.quantile(err, 0.10))
    sh, lo = s20.IMBALANCE["short"], s20.IMBALANCE["long"]
    p50 = control.imbalance(np.minimum(fc, 100), np.minimum(act, 100), sh, lo)
    p90 = control.imbalance(np.minimum(np.clip(fc + q10, 0, None), 100),
                            np.minimum(act, 100), sh, lo)
    lines = ["day-ahead schedule at the forecast (P50) or lowered to its P90",
             f"  P90 offset {q10:.1f} MW (10 % of hours fall below it)",
             f"  imbalance over the year: P50 {p50:,.0f} u, P90 {p90:,.0f} u",
             "  lowering the schedule trades short penalties for long ones",
             f"  ({'cheaper' if p90 < p50 else 'dearer'} here); it also sells less energy ahead -",
             "  the choice is a commercial one, written in the operating",
             "  procedure with its rule, not made hour by hour"]
    emit("i_p90", lines)
    return dict(p50=p50, p90=p90)


# ------------------------------------------------ J. grid services
def service(seed: int = 53) -> dict:
    rng = np.random.default_rng(seed)
    window = np.zeros(24 * 30, bool)
    for d in range(30):
        window[d * 24 + 18: d * 24 + 22] = True
    held = window.copy()
    held[rng.choice(np.where(window)[0], 4, replace=False)] = False     # SOC below floor
    comms = np.zeros_like(held)
    comms[5 * 24 + 18: 5 * 24 + 21] = True                              # link lost day 6
    held &= ~comms
    a = operations.service_availability(held, window)
    lines = [f"upward reserve REQ-S01 over a month: {window.sum()} window hours",
             f"  held {held[window].sum()}, not held {(~held[window]).sum()} "
             f"(SOC below the floor 4, link lost 3)",
             f"  availability {a:.1%} against the {s20.SERVICE['availability']:.0%} "
             f"teaching target - {'met' if a >= s20.SERVICE['availability'] else 'below it'}",
             "  the three hours with the link lost were declared unavailable",
             "  at once, as the service rules ask: a service not deliverable",
             "  is suspended and reported, never left to look available"]
    emit("j_service", lines)
    return dict(a=a)


if __name__ == "__main__":
    settlement()
    imbalance_month()
    bias()
    reserve()
    p90_schedule()
    service()
