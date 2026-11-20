"""Chapter 15 - three integrated Plant P examples: one windy, sunny day at
the export limit hour by hour (introductory), the energy-yield statement
of the plant with its loss register (intermediate), and the forecast
validation report with the dispatch recommendation (integrated).

Run from the project root:   python -m companion.ch15.integrated
Writes companion/ch15/expected/i_*.txt.
Model 15.1; D-013 .. D-019.
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import forecast as fc, sources as src
from companion.ch15.common import emit
from plantp import yieldmodel as ym


def one_day() -> None:
    r = src.plant_year()
    day = int(np.argmax(r["curtailed"].reshape(365, 24).sum(axis=1)))
    lines = [f"the day with the most curtailment, day {day + 1} (model {src.VERSION}):",
             "  hour   wind MW   PV MW   at MV   losses  at POC  delivered  curtailed"]
    for h in range(6, 20, 2):
        k = day * 24 + h
        lines.append(f"  {h:02d}    {r['w_av'][k]:7.2f}  {r['pv_av'][k]:6.2f}  {r['mv'][k]:6.2f}  "
                     f"{r['el_loss'][k] + r['aux'][k]:6.2f}  {r['poc'][k]:6.2f}   {r['delivered'][k]:6.2f}"
                     f"     {r['curtailed'][k]:5.2f}")
    sl = slice(day * 24, day * 24 + 24)
    lines += [f"  day: delivered {r['delivered'][sl].sum():.0f} MWh, curtailed {r['curtailed'][sl].sum():.1f} MWh",
              "  curtailment needs strong wind and strong sun together: a",
              "  few midday hours of a few days; the year's total is small"]
    emit("i_day", lines)


def statement() -> None:
    r = src.plant_year()
    cfg = src.ModelConfig()
    lines = [f"energy-yield statement of Plant P, model {src.VERSION} (P50, long term, S0):",
             f"  wind at MV {r['w_av'].sum() / 1e3:7.2f} GWh   (gross {r['w_gross'].sum() / 1e3:.2f};"
             " density, terrain,",
             "    wakes, long term, availability)",
             f"  PV at MV   {r['pv_av'].sum() / 1e3:7.2f} GWh   (POA at STC {r['pv_stc'].sum() / 1e3:.2f}; year 1)",
             f"  electrical losses and own use   {(r['el_loss'] + r['aux']).sum() / 1e3:5.2f} GWh",
             f"  curtailment at 100 MW           {r['curtailed'].sum() / 1e3:5.2f} GWh",
             f"  grid outages ({cfg.grid_outage_h} h)            {(r['delivered'] - r['net']).sum() / 1e3:5.2f} GWh",
             f"  net at the point of connection  {r['net'].sum() / 1e3:7.2f} GWh;"
             f" capacity factor {r['net'].sum() / 876e3:.3f}",
             "  not included: uncertainty and P90 (chapter 16), life-mean",
             "  degradation, the S1 battery, price and dispatch effects",
             "  basis: " + src.settings_line(cfg)[:60] + " ..."]
    emit("i_statement", lines)


def validation() -> None:
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    test = np.arange(8760) >= fc.TEST0
    wf, pf = fc.nwp(24)
    f = wf + pf
    s_n = ym.scores(f, h, test)
    s_p = ym.scores(ym.persistence(h, 24), h, test)
    q10, q90 = np.quantile((h - f)[~test], [0.10, 0.90])
    cov = ym.coverage(np.clip(f + q10, 0, 110)[test], np.clip(f + q90, 0, 110)[test], h[test])
    rt = ym.ramp_table(ym.ramps(h, 15.0)[test], ym.ramps(f, 15.0)[test])
    lines = ["forecast validation report, day-ahead hybrid forecast (test Sep-Dec):",
             f"  RMSE {s_n['rmse']:.1f} MW ({100 * s_n['rmse'] / fc.CAP:.1f} % of 110 MW);"
             f" bias {s_n['bias']:+.2f} MW",
             f"  skill against 24 h persistence {ym.skill(s_n['rmse'], s_p['rmse']):+.2f}",
             f"  P10-P90 coverage {100 * cov:.1f} % (target 80 %, quantiles from the past only)",
             f"  ramps above 15 MW/h: POD {rt['pod']:.2f}, FAR {rt['far']:.2f} (timing errors)",
             "  bias by month within about 1.5 MW; retrain on a rolling window",
             "  data: synthetic archive (A-267), train Jan-Aug, test Sep-Dec,",
             "  no feature unknown at the issue time",
             "  recommendation: schedule near P33 with these prices; hold",
             "  about 10 MW of downward reserve (the S1 battery covers it)"]
    emit("i_validation", lines)


if __name__ == "__main__":
    one_day()
    statement()
    validation()
