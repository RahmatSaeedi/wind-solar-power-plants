"""Chapter 43, an eighth round: a short-circuit test or a design review as
a decision under uncertainty, the forces the transport bracing must hold,
the first month of dissolved gases after energising, and the nameplate
checked against the test report.

Run from the project root:   python -m companion.ch43.examples_y
Writes companion/ch43/expected/y_*.txt.
Teaching values (A-462 to A-464).
"""
from __future__ import annotations

import numpy as np

from companion.ch43 import sources as src
from companion.ch43.common import emit

M = src.MAIN_B


# ------------------------------------------------ short-circuit proof
def sc_decision(p_weak: float = 0.05, test_k: float = 220.0, review_k: float = 30.0,
                p_catch_review: float = 0.7, failure_k: float = 3500.0) -> dict:
    """Expected cost of three routes for the short-circuit proof (teaching)."""
    routes = {
        "no proof": p_weak * failure_k,
        "design review": review_k + p_weak * (1 - p_catch_review) * failure_k,
        "test on this unit": test_k + 0.0,
    }
    lines = [f"short-circuit proof for T1: chance of a weak design {p_weak:.0%},",
             f"  a field failure {failure_k:,.0f} k u (replacement, crane, months out;",
             f"  teaching); a review catches {p_catch_review:.0%} of weak designs",
             "  route                expected cost k u"]
    for k, v in routes.items():
        lines.append(f"  {k:20s} {v:17.0f}")
    best = min(routes, key=routes.get)
    lines += [f"  cheapest in expectation: {best}",
              "  a test proves this unit and risks it (a failed test is a",
              "  damaged transformer); a review of the calculation against",
              "  units the maker has tested costs less - the choice is the",
              "  owner's engineer's, written in the contract (TQ-04)"]
    emit("y_scproof", lines)
    return dict(routes, best=best)


# ------------------------------------------------ transport bracing
def bracing(active_t: float = 44.2, g_long: float = 3.0, g_lat: float = 1.0,
            g_vert: float = 2.0) -> dict[str, float]:
    m = active_t * 1000
    f = {name: m * 9.81 * a / 1e6 for name, a in (("along", g_long),
                                                    ("across", g_lat),
                                                    ("vertical", g_vert))}
    lines = [f"active part of {active_t} t in its tank on the road and the ship",
             "  design accelerations (teaching): along 3 g, across 1 g, vertical 2 g",
             "  direction   force on the bracing MN"]
    for k, v in f.items():
        lines.append(f"  {k:10s}  {v:20.2f}")
    lines += ["  the bracing inside the tank holds the active part against",
              "  these; an impact over the recorder's limit means the",
              "  bracing may have moved - the recorder and the frequency",
              "  response at site are how that is known (lesson E)"]
    emit("y_bracing", lines)
    return f


# ------------------------------------------------ first month of gases
def first_month(seed: int = 4302) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    days = np.array([0, 1, 7, 14, 30])
    h2 = 9.0 + 0.15 * days + rng.normal(0, 0.3, len(days))
    c2h4 = 1.6 + 0.04 * days + rng.normal(0, 0.05, len(days))
    rate_h2 = np.polyfit(days, h2, 1)[0] * 30
    rate_c2h4 = np.polyfit(days, c2h4, 1)[0] * 30
    lines = ["dissolved gases in the first month after energising (synthetic)",
             "  day      " + "  ".join(f"{d:5.0f}" for d in days),
             "  H2 ppm   " + "  ".join(f"{x:5.1f}" for x in h2),
             "  C2H4 ppm " + "  ".join(f"{x:5.1f}" for x in c2h4),
             f"  trend: H2 {rate_h2:+.1f} ppm a month, C2H4 {rate_c2h4:+.1f} ppm a month",
             "  the after-heat-run sample is day 0: a rate, not a level, is",
             "  the early sign - and a rising ethylene fits a hot joint",
             "  (lesson C) better than ageing; the rates are compared with",
             "  the maker's and the guidance (STD-179), then trended (ch 52)"]
    emit("y_month", lines)
    return dict(h2=rate_h2, c2h4=rate_c2h4)


# ------------------------------------------------ nameplate against the report
PLATE = dict(uk_pct=12.0, p0_kw=42.0, pk_kw=290.0, mass_t=95.0, vector="YNd11",
             oil_m3=22.0)
REPORT = dict(uk_pct=12.6, p0_kw=42.2, pk_kw=298.0, mass_t=92.4, vector="YNd11",
              oil_m3=22.0)


def nameplate() -> dict[str, int]:
    lines = ["the rating plate of T1 checked against its test report",
             "  item          plate     report   check"]
    bad = 0
    for k in PLATE:
        a, b = PLATE[k], REPORT[k]
        same = a == b
        bad += 0 if same else 1
        lines.append(f"  {k:12s}  {str(a):8s}  {str(b):8s} {'ok' if same else 'differs'}")
    lines += [f"  {bad} items differ: the plate carries the guaranteed values,",
              "  the measured ones belong on it (impedance, losses, mass) -",
              "  protection settings and fault studies read the plate, and",
              "  a guarantee printed as a measurement misleads them for",
              "  forty years"]
    emit("y_plate", lines)
    return dict(bad=bad)


if __name__ == "__main__":
    sc_decision()
    bracing()
    first_month()
    nameplate()
