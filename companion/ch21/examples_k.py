"""Chapter 21, contracts and model quality: insurance premium against
expected loss and the choice of deductible, the chance that a
performance test triggers damages when the measurement is uncertain,
and three planted errors in the model with the checks that catch them
(and one that no check catches).

Run from the project root:   python -m companion.ch21.examples_k
Writes companion/ch21/expected/k_*.txt.
Teaching values A-308; commercial concepts only.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


def insurance() -> None:
    """Business-interruption cover: events at 0.3 a year, outage days
    lognormal (median 20, wide), loss = days x daily revenue; premium
    1.3 x expected insured loss (teaching)."""
    rng = np.random.default_rng(2108)
    daily = 20_453 / 365
    days = np.exp(np.log(20) + 1.0 * rng.standard_normal(200_000))
    lines = ["business-interruption cover: deductible against premium (k u/yr):",
             "  deductible days   expected loss kept   premium   total expected cost"]
    for ded in (0, 7, 30, 60):
        kept = np.minimum(days, ded).mean() * daily * 0.3
        insured = np.maximum(days - ded, 0).mean() * daily * 0.3
        prem = 1.3 * insured
        lines.append(f"  {ded:15d}   {kept:18,.0f}   {prem:7,.0f}   {kept + prem:19,.0f}")
    worst = np.percentile(days, 99) * daily
    lines += [f"  a 1-in-100 event: {np.percentile(days, 99):.0f} days, {worst:,.0f} k u lost",
              "  a larger deductible lowers the expected cost (the insurer's",
              "  margin is paid on less), but the owner keeps the first days",
              "  of every event; lenders set the minimum cover and the",
              "  largest deductible the cash flow can carry (DSRA, ch 38)"]
    emit("k_insurance", lines)


def test_uncertainty() -> None:
    """True shortfall s; the test measures it with standard uncertainty
    u; damages paid if the measured shortfall exceeds the tolerance."""
    lines = ["a power-curve test with measurement uncertainty (tolerance 1 %):",
             "  true shortfall %   test u 1.5 %: P(pay)   test u 4 %: P(pay)"]
    for s in (0.0, 1.0, 2.0, 4.0):
        p1 = 0.5 * math.erfc((1.0 - s) / (1.5 * math.sqrt(2)))
        p2 = 0.5 * math.erfc((1.0 - s) / (4.0 * math.sqrt(2)))
        lines.append(f"  {s:16.1f}   {p1:20.2f}   {p2:18.2f}")
    lines += ["  with a 4 % test uncertainty a real 2 % shortfall is paid only",
              "  six times in ten, and a perfect machine pays four times in",
              "  ten if the contract counts the measured value; contracts",
              "  therefore subtract the uncertainty before damages - which",
              "  makes the test method (chapter 11) the real value of the LD"]
    emit("k_test", lines)


def audit() -> None:
    base = model.run()
    lines = ["three planted errors and the model checks (teaching):"]
    # 1 tax added instead of subtracted in CFADS
    r = model.run()
    bad = dict(r)
    bad["cfads"] = r["cfads"] + 2 * r["tax"]
    ok = np.allclose(bad["cfads"], bad["ebitda"] - bad["repl"] - bad["tax"]
                     - bad["dwc"] - bad["decom"])
    wrong = np.nanmin(fn.dscr(bad["cfads"][:15], r["ds"][:15]))
    lines += [f"  1 tax added to CFADS: identity check {'PASS' if ok else 'FAIL'}",
              f"    -> caught (the wrong model would show min DSCR {wrong:.2f})"]
    # 2 the wind components reserve entered in year 18, not 15
    rep = dict(src.REPLACE)
    src.REPLACE[18] = src.REPLACE.pop(15)
    r2 = model.run(debt=base["debt"])
    checks = all(ok for _, ok in model.checks(r2))
    src.REPLACE.clear()
    src.REPLACE.update(rep)
    lines += [f"  2 replacement in year 18, not 15: all checks {'PASS' if checks else 'FAIL'}",
              f"    -> NOT caught; DSCR of year 15 {r2['dscr'][14]:.2f} instead of"
              f" {base['dscr'][14]:.2f}"]
    # 3 cost lines left in year-1 money in a nominal model
    keep = T["inflation"]
    T["inflation"] = 0.0
    r3 = model.run(debt=base["debt"])
    T["inflation"] = keep
    lines += ["  3 costs left in year-1 money: checks pass -> NOT caught;",
              f"    equity IRR {r3['equity_irr'] * 100:.2f} % instead of {base['equity_irr'] * 100:.2f} %"]
    lines += ["  checks catch broken identities, not wrong inputs: a",
              "  misplaced year or a mixed convention passes every check;",
              "  only the register (source of each input), a second person",
              "  and a reasonableness review catch those"]
    emit("k_audit", lines)


if __name__ == "__main__":
    insurance()
    test_uncertainty()
    audit()
