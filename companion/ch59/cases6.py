"""Chapter 59: schedule risk to COD, the LCOE broken into its parts, the
operating water balance, and the Monte Carlo of the plant's availability.

Run from the project root:   python -m companion.ch59.cases6
"""
from __future__ import annotations

import contextlib
import io

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import csv, emit


def c_schedrisk(n: int = 10_000) -> dict:
    """The 63-month plan with triangular durations (0.8 d, d, 1.6 d)."""
    from companion.ch59 import dossier
    from plantp import appraisal
    rng = np.random.default_rng(59)
    tasks0 = {k: (float(d), pre) for k, (d, pre) in dossier.TASKS.items()}
    tot = np.empty(n)
    crit = {k: 0 for k in tasks0}
    for i in range(n):
        tasks = {k: (rng.triangular(0.8 * d, d, 1.6 * d), pre) for k, (d, pre) in tasks0.items()}
        t, c, _ = appraisal.critical_path(tasks)
        tot[i] = t
        for k in c:
            crit[k] += 1
    p50, p80, p90 = (float(np.percentile(tot, q)) for q in (50, 80, 90))
    lines = ["the plan to COD with uncertain durations (triangular 0.8 d - d - 1.6 d,",
             f"teaching, {n:,} runs)",
             f"  deterministic 63 months; P50 {p50:.1f}, P80 {p80:.1f}, P90 {p90:.1f}",
             "  on the critical path in:"]
    for k in sorted(crit, key=lambda k: -crit[k]):
        if crit[k]:
            lines.append(f"    {crit[k] / n:5.0%}  {k}")
    lines += [f"  a COD promised at 63 months is met in {float(np.mean(tot <= 63.0)):.0%} of runs;",
              "  the PPA and the debt plan carry the P80, not the deterministic plan"]
    emit("c_schedrisk", lines)
    return dict(p50=p50, p80=p80, p90=p90, met=float(np.mean(tot <= 63.0)),
                crit={k: v / n for k, v in crit.items()})


def a_lcoe() -> dict:
    from companion.ch21 import model
    from companion.ch21 import sources as s21
    from plantp import finance as fn
    r = model.run()
    w = s21.TERMS["wacc"]
    e = fn.pv(np.asarray(r["energy"]), w)
    parts = [("capital", r["capex"]), ("operation", fn.pv(np.asarray(r["opex"]), w)),
             ("replacements", fn.pv(np.asarray(r["repl"]), w)),
             ("decommissioning", fn.pv(np.asarray(r["decom"]), w))]
    tot = sum(v for _, v in parts) / e
    lines = [f"LCOE of Plant P by part (ch 21 model, WACC {w:.1%}, k u / GWh = u/MWh)"]
    rows = []
    for name, v in parts:
        rows.append((name, v / e))
        lines.append(f"  {name:16s} {v / e:6.1f} u/MWh  {v / e / tot:5.0%}")
    cap = rows[0][1] / tot
    no_dec = tot - rows[3][1]
    lines += [f"  total            {tot:6.1f} u/MWh ({no_dec:.1f} without decommissioning,",
              "                   the LCOE of section A)",
              f"  capital is {cap:.0%} of the cost of a kWh: the capex range of the",
              "  tornado and the EPC price are the levers; operation is most",
              "  of the rest; decommissioning, 25 years away, weighs little"]
    csv("ch59-lcoe.csv", "k,v", [(i + 1, round(v, 2)) for i, (_, v) in enumerate(rows)])
    emit("a_lcoe", lines)
    return dict(rows=rows, tot=tot)


def a_water() -> dict:
    from companion.ch29 import sources as s29
    d = s29.DEMAND
    wash = d["modules"] * d["wash_l_module"] / 1000
    month = [n * wash + d["staff"] * d["staff_l_day"] * 30.4 / 1000 for n in d["washes"]]
    year = sum(month)
    lines = ["operating water of Plant P (ch 29 demand, treated water, A-352)",
             f"  one wash {wash:.1f} m3; {sum(d['washes'])} washes a year; staff"
             f" {d['staff']} x {d['staff_l_day']:.0f} l/day",
             "  month: " + " ".join(f"{m:5.0f}" for m in month[:6]),
             "         " + " ".join(f"{m:5.0f}" for m in month[6:]),
             f"  year {year:,.0f} m3; peak month {max(month):.0f} m3",
             "  the construction water (ch 29: about 87,000 m3) is thirty times",
             "  a year of operation: the stewardship plan is mostly a",
             "  construction plan, then a drought rule for washing (ch 51)"]
    emit("a_water", lines)
    return dict(year=year, peak=max(month), wash=wash)


def e_montecarlo() -> dict:
    from companion.ch52 import lab_f
    with contextlib.redirect_stdout(io.StringIO()):
        mc = lab_f.monte_carlo()
    keys = ["mean", "p50", "p90"]
    lines = ["energy lost to unplanned failures, MWh a year (ch 52 Monte Carlo of",
             "the failure classes, 400 simulated years; planned services apart)"]
    lines += [f"  {k:5s} {mc[k]:7,.0f}" for k in keys]
    lines += [f"  the P90 year loses {mc['p90'] / mc['p50']:.1f} times the median year: the",
              "  yearly spread, not only the mean, enters the uncertainty",
              "  budget (ch 16) and the debt case (ch 21)"]
    emit("e_montecarlo", lines)
    return {k: mc[k] for k in keys}


def main() -> dict:
    out = {}
    for f in (c_schedrisk, a_lcoe, a_water, e_montecarlo):
        out[f.__name__] = f()
    return out


if __name__ == "__main__":
    main()
