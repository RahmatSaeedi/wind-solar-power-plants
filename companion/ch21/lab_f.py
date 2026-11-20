"""Chapter 21, lab F - the project-finance model and debt sizing: the
worked period-by-period table (CFADS, interest, principal, service,
DSCR, LLCR, balance), an independent check of the ratios, sculpted
against annuity repayment, debt size against the cover target, tenor
and rate, and the covenant headroom.

DSCR = CFADS / scheduled debt service; LLCR = PV of CFADS over the
remaining loan life at the debt rate / debt outstanding. Transaction
documents define the real ratios; these are the teaching definitions.

Run from the project root:   python -m companion.ch21.lab_f
Writes companion/ch21/expected/f_*.txt and diagrams/data/ch21-*.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit
from plantp import finance as fn

T = src.TERMS


def schedule() -> None:
    r = model.run()
    n = T["tenor"]
    lines = ["base case debt schedule (k u, nominal; A-307..A-309):",
             "  yr   CFADS  interest  principal  service   DSCR   LLCR   balance"]
    rows = []
    for k in range(n):
        lines.append(f"  {k + 1:2d} {r['cfads'][k]:7,.0f} {r['interest'][k]:9,.0f}"
                     f" {r['principal'][k]:10,.0f} {r['ds'][k]:8,.0f}"
                     f" {r['dscr'][k]:6.2f} {r['llcr'][k]:6.2f} {r['balance'][k]:9,.0f}")
        rows.append((k + 1, f"{r['cfads'][k]:.0f}", f"{r['ds'][k]:.0f}", f"{r['dscr'][k]:.3f}"))
    lines += [f"  min DSCR {r['min_dscr']:.2f} (year {int(np.nanargmin(r['dscr'])) + 1}),"
              f" average {r['avg_dscr']:.2f}, min LLCR {r['min_llcr']:.2f}"]
    emit("f_schedule", lines)
    csv("ch21-dscr.csv", "y,cfads,ds,dscr", rows)
    lines = ["independent check of year 1 (by hand from the model lines):",
             f"  revenue {r['revenue'][0]:,.0f} - opex {r['opex'][0]:,.0f}"
             f" - replacements {r['repl'][0]:,.0f}",
             f"  - tax {r['tax'][0]:,.0f} - working capital {r['dwc'][0]:,.0f}"
             f" = CFADS {r['cfads'][0]:,.0f}",
             f"  interest {r['balance'][0]:,.0f} x {T['rate']:.2f} = {r['interest'][0]:,.0f};"
             f" service {r['ds'][0]:,.0f}",
             f"  DSCR = {r['cfads'][0]:,.0f} / {r['ds'][0]:,.0f} = {r['cfads'][0] / r['ds'][0]:.3f}",
             "  model checks:"]
    lines += [f"    {'PASS' if ok else 'FAIL'}  {name}" for name, ok in model.checks(r)]
    lines += ["  year 1 is the lowest: the working capital is built from",
              "  that year's cash (45 days of revenue); the sculpting",
              "  follows the lenders' sizing case, not this one"]
    emit("f_check", lines)


def shapes() -> None:
    r = model.run()
    n = T["tenor"]
    cf = r["cfads"][:n]
    i_a, p_a, b_a = fn.annuity_debt(r["debt"], T["rate"], n)
    ds_a = i_a + p_a
    d_a = fn.dscr(cf, ds_a)
    lines = ["the same debt repaid as an annuity or sculpted to the cash flow:",
             "  shape       min DSCR   year of min   max DSCR   min LLCR"]
    lines.append(f"  sculpted   {np.nanmin(r['dscr']):9.2f}   {int(np.nanargmin(r['dscr'])) + 1:11d}"
                 f"   {np.nanmax(r['dscr']):8.2f}   {r['min_llcr']:8.2f}")
    l_a = fn.llcr(cf, b_a, T["rate"], n)
    lines.append(f"  annuity    {np.nanmin(d_a):9.2f}   {int(np.nanargmin(d_a)) + 1:11d}"
                 f"   {np.nanmax(d_a):8.2f}   {np.nanmin(l_a):8.2f}")
    # largest annuity that keeps min DSCR 1.20 on the P90 sizing case
    o = model.operating_lines(dict(model.DEFAULT, energy_scale=src.P90_1Y))
    p90 = (o["revenue"] - o["opex"] - o["repl"])[:n] * 0.93
    lim = min(p90 / 1.20)
    debt_a = lim * (1 - (1 + T["rate"]) ** -n) / T["rate"]
    lines += [f"  largest annuity debt at DSCR 1.20 on P90: {debt_a:,.0f} k u",
              f"  ({debt_a / r['debt'] * 100:.0f} % of the sculpted debt)",
              "  an annuity is level while the cash flow is not (indexed",
              "  tariff, replacement years): its weakest year sets the debt;",
              "  sculpting matches service to cash flow and carries more debt"]
    emit("f_shapes", lines)
    csv("ch21-shapes.csv", "y,sculpt,annuity",
        [(k + 1, f"{r['dscr'][k]:.3f}", f"{d_a[k]:.3f}") for k in range(n)])


def sizing() -> None:
    lines = ["debt that the cash flows support (sculpted, P90 1-yr case):",
             "  target DSCR   tenor yr   rate %   debt k u   gearing %"]
    cost = model.run()["uses"]
    o = model.operating_lines(dict(model.DEFAULT, energy_scale=src.P90_1Y))
    base = (o["revenue"] - o["opex"] - o["repl"]) * 0.93
    for dscr, tenor, rate in ((1.20, 15, 0.06), (1.30, 15, 0.06), (1.20, 12, 0.06),
                              (1.20, 18, 0.06), (1.20, 15, 0.08)):
        d, *_ = fn.sculpted_debt(base[:tenor], dscr, rate)
        capped = min(d, 0.75 * cost)
        lines.append(f"  {dscr:11.2f}   {tenor:8d}   {rate * 100:6.1f}   {capped:8,.0f}"
                     f"   {capped / cost * 100:9.1f}{'  (cap)' if capped < d else ''}")
    lines += ["  (gearing against the base-case uses; capped at 75 %)",
              "  a higher target, a shorter tenor or a dearer rate each cut",
              "  the debt by 8-15 %: the equity must fill the gap, and the",
              "  equity return falls; none of these numbers is a market",
              "  standard - each comes from the term sheet (A-307)"]
    emit("f_sizing", lines)


def covenants() -> None:
    r = model.run()
    head_l = r["min_dscr"] - T["lockup"]
    head_d = r["min_dscr"] - T["default"]
    e_lock = fn.breakeven(lambda k: model.run(debt=r["debt"], energy_scale=k)["min_dscr"],
                          0.7, 1.0, T["lockup"])
    e_def = fn.breakeven(lambda k: model.run(debt=r["debt"], energy_scale=k)["min_dscr"],
                         0.7, 1.0, T["default"])
    lines = ["covenant headroom of the base case (illustrative levels):",
             f"  min DSCR {r['min_dscr']:.2f}; lock-up below {T['lockup']:.2f},"
             f" default below {T['default']:.2f}",
             f"  headroom to lock-up {head_l:.2f}, to default {head_d:.2f}",
             f"  energy (all years) at which the min DSCR hits lock-up: {e_lock * 100:.1f} % of P50",
             f"  ... and default: {e_def * 100:.1f} % of P50 (P90 1-yr is {src.P90_1Y * 100:.1f} %)",
             "  lock-up stops distributions to the owners until the cover",
             "  recovers; default lets the lenders act; the DSRA pays the",
             "  service for six months while the cause is fixed"]
    emit("f_covenants", lines)


if __name__ == "__main__":
    schedule()
    shapes()
    sizing()
    covenants()
