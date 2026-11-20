"""Chapter 52 - the three integrated Plant P examples: by hand, the
maintenance system after year one, and the maintenance and RAM basis
(decision D-056).

Run from the project root:   python -m companion.ch52.integrated
Writes companion/ch52/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch52 import sources as src
from companion.ch52.common import emit
from plantp import ram


def by_hand() -> dict:
    n, lam, mttr, delay, *_ = src.CLASSES["PV inverter"]
    mtbf = 8760 / lam
    ai = ram.a_inherent(mtbf, mttr)
    t = src.CLASSES["main transformer"]
    q_t = t[1] * (t[2] + t[3]) / 8760
    pair = 1 - q_t ** 2
    m = n * lam / 8760 * 1440
    p0, p1, p2 = math.exp(-m), math.exp(-m) * (1 + m), math.exp(-m) * (1 + m + m * m / 2)
    lines = ["three numbers by hand",
             f"  PV inverter: MTBF 8,760/{lam} = {mtbf:,.0f} h; A_i = {mtbf:,.0f}/({mtbf:,.0f} + "
             f"{mttr:.0f}) = {ai:.5f}",
             f"  one main transformer unavailable {t[1]} x {t[2] + t[3]:,.0f}/8,760 = {q_t:.4f};",
             f"  both out (independent) {q_t ** 2:.1e}: some export {pair:.6f}",
             f"  inverter spares: demand in 1,440 h = {n} x {lam} x 1,440/8,760 = {m:.2f};",
             f"  P(<=0) {p0:.2f}, P(<=1) {p1:.2f}, P(<=2) {p2:.2f} -> 2 spares for 90 %"]
    emit("int_hand", lines)
    return dict(ai=ai, q_t=q_t, m=m, p2=p2)


REVIEW = [   # item, done
    ("a strategy for each asset class", True),
    ("preventive plan with outage hours", True),
    ("hierarchy complete in the CMMS", False),
    ("a failure code on every corrective order", False),
    ("test record before an order closes", False),
    ("RAM model inside a stated boundary", True),
    ("spares by Poisson and by consequence", False),
    ("export boundary and response times agreed", True),
    ("cleaning method chosen on six criteria", True),
    ("peer-ratio CUSUM watched every day", False),
    ("repeat-failure query run monthly", False),
    ("warranty records complete for claims", False)]


def review() -> dict:
    ok = sum(1 for _, d in REVIEW if d)
    lines = ["the maintenance system after year one: what is in place"]
    lines += [f"  [{'x' if d else ' '}] {k}" for k, d in REVIEW]
    lines += [f"  {ok} of {len(REVIEW)} in place: the plans exist, the records that",
              "  prove and improve them do not yet - the open items are",
              "  data work (lesson I) and one daily habit (lesson D)"]
    emit("int_review", lines)
    return dict(ok=ok, total=len(REVIEW))


def basis() -> None:
    lines = ["D-055 -> D-056 maintenance and RAM basis (teaching, Plant P)",
             "  1. strategy by class from consequence and failure pattern;",
             "     condition-based for turbines' major parts, transformers, line",
             "  2. preventive plan: 4,683 h a year; outage work in low-resource",
             "     months (turbine services in June, not December)",
             "  3. RAM case inside the boundary units -> POC meter: energy",
             "     availability 97.97 %; model 15.1's 98.42 % is optimistic",
             "  4. spares by Poisson and expected loss: two inverters, one",
             "     major turbine kit; transformer spare by loss (shared, ch 18)",
             "  5. daily peer-ratio CUSUM per PV block and per turbine",
             "  6. cleaning: truck + brush with RO water at night, trigger by",
             "     measured soiling (ch 10); no high-pressure lance",
             "  7. export assets: boundary, inspection plan and spares agreed",
             "     with the network owner; insulators held on site",
             "  8. CMMS: hierarchy complete, codes and test records required to",
             "     close, warranty claims from complete orders; monthly",
             "     reconciliation with SCADA events",
             "  open: U-133 (makers' maintenance manuals, failure data and",
             "  service-agreement terms; network owner's boundaries)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    review()
    basis()
