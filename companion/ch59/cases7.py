"""Chapter 59: the finance model's stated assumptions, forecast-band coverage
by lead, the CMMS import field count, and the grid study's models and
approvals.

Run from the project root:   python -m companion.ch59.cases7
"""
from __future__ import annotations

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import emit


def h_terms() -> dict:
    from companion.ch21 import sources as s21
    t = s21.TERMS
    lines = ["the stated assumptions of the finance model (ch 21, teaching A-304..310)",
             "  currency: one unit 'u', nominal; costs in year-1 money indexed",
             f"  inflation {t['inflation']:.1%} a year; PPA {t['tariff']:.0f} u/MWh"
             f" +{t['tariff_index']:.0%} a year for {t['ppa_years']} years,",
             f"    then {t['merchant_real']:.0f} u/MWh in year-1 money (merchant)",
             f"  unpaid curtailment {t['curtail_uncomp']:.0%} of energy;"
             f" receivables {t['receivable_days']} days, payables {t['payable_days']}",
             f"  tax {t['tax']:.0%}, straight-line depreciation over {t['dep_years']} years",
             f"  debt {t['rate']:.0%} a year, fee {t['fee']:.1%}, tenor {t['tenor']} years,"
             f" sculpted",
             f"  sizing: DSCR {t['dscr_p50']:.2f} on P50, {t['dscr_p90']:.2f} on P90 one year;"
             f" gearing <= {t['max_gearing']:.0%}",
             f"  DSRA {t['dsra_months']} months; lock-up {t['lockup']:.2f}; default {t['default']:.2f}",
             f"  WACC {t['wacc']:.1%}; cost of equity {t['cost_of_equity']:.0%}",
             f"  energy: P50 year 1 of model 15.1; P90 one year = {s21.P90_1Y:.3f} x P50",
             "  every line is a teaching value; a real model states the same",
             "  list with sources, and the lenders' auditor checks it (ch 21 D)"]
    emit("h_terms", lines)
    return dict(n=len(t))


def f_coverage() -> dict:
    from companion.ch15 import forecast as fc
    w_, pv, *_ = fc.truth()
    act = w_ + pv
    half = 8760 // 2
    lines = ["P10-P90 band learned on Jan-Jun, coverage on Jul-Dec, by lead",
             f"  {'lead h':>6s} {'band MW':>16s} {'coverage':>9s}"]
    out = {}
    for lead in (1, 6, 24, 36):
        wf, pf = fc.nwp(lead)
        e = act - (wf + pf)
        q10, q90 = np.percentile(e[:half], [10, 90])
        cov = float(np.mean((e[half:] >= q10) & (e[half:] <= q90)))
        out[lead] = (q10, q90, cov)
        lines.append(f"  {lead:6d} {q10:7.1f} to {q90:5.1f} {cov:9.0%}")
    lines += ["  a band learned in one season and used in another can be too",
              "  wide or too narrow: coverage is checked by season and by lead,",
              "  and the band is relearned as data arrive (ch 15 E)"]
    emit("f_coverage", lines)
    return out


COUNTS = {"inverter": 10, "transformer": 12, "turbine": 12, "relay": 24}   # teaching


def j_import() -> dict:
    from companion.ch59.cases2 import REQS
    rows = [(k, n, len(REQS[k]), n * len(REQS[k])) for k, n in COUNTS.items()]
    tot = sum(r[3] for r in rows)
    lines = ["field values the CMMS import must carry for four classes (teaching)",
             f"  {'class':12s} {'assets':>6s} {'fields':>6s} {'values':>7s}"]
    lines += [f"  {k:12s} {n:6d} {f:6d} {v:7d}" for k, n, f, v in rows]
    assets = sum(COUNTS.values())
    lines += [f"  total {tot} values on {assets} assets; at the rate of the sample",
              f"  register (3 problems in 10 rows) about {round(0.3 * assets)} rows would",
              "  carry a problem - the validation runs on every row"]
    emit("j_import", lines)
    return dict(tot=tot)


def g_models() -> dict:
    from companion.ch28 import register as r28
    lines = [f"models of the grid study (ch 28): {len(r28.MODELS)}"]
    mism = 0
    for m in r28.MODELS:
        same = m[4].strip() in m[3]          # the site version is the one studied
        mism += not same
        lines += [f"  {m[0]} ({m[1]}, {m[2]})",
                  f"      study: {m[3]}; site: {m[4]}{'' if same else '  <- differs'}"]
    lines.append(f"approvals of the study: {len(r28.APPROVALS)}")
    for a in r28.APPROVALS:
        lines.append(f"  {a[0][:34]:34s} approves: {a[3][:28]}")
    lines += [f"  models whose study version differs from the site: {mism}",
              "  each mismatch reopens the study for that unit (ch 28, ch 50)"]
    emit("g_models", lines)
    return dict(models=len(r28.MODELS), approvals=len(r28.APPROVALS), mism=mism)


def main() -> dict:
    out = {}
    for f in (h_terms, f_coverage, j_import, g_models):
        out[f.__name__] = f()
    return out


if __name__ == "__main__":
    main()
