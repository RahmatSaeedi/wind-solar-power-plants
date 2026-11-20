"""Chapter 42, a third round on the blade: the stiffness of a ply turned
off its axis (why caps are unidirectional and shells are +-45), wrinkle
knockdown, the full-scale static test, how a fatigue test is
accelerated, characteristic values from insert pull tests, and an SPC
chart of blade weights.

Run from the project root:   python -m companion.ch42.examples_t
Writes companion/ch42/expected/t_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-452); textbook laminate theory.
"""
from __future__ import annotations

import math
import random
from statistics import mean, pstdev

from companion.ch42.common import csv, emit
from plantp import materials as mt

E1, _E2 = mt.rule_of_mixtures(72.0, 3.2, 0.60)
E2 = 1.7 * _E2                    # matrix with fibre support (teaching)
G12, NU12 = 4.0, 0.28


# [start: offaxis]
def e_theta(theta_deg: float) -> float:
    """Modulus of a unidirectional ply loaded at theta to its fibres."""
    c, s = math.cos(math.radians(theta_deg)), math.sin(math.radians(theta_deg))
    inv = c ** 4 / E1 + (1 / G12 - 2 * NU12 / E1) * s * s * c * c + s ** 4 / E2
    return 1 / inv
# [end: offaxis]


def offaxis() -> dict[int, float]:
    out = {t: e_theta(t) for t in (0, 15, 30, 45, 60, 90)}
    csv("ch42-offaxis.csv", "theta,e",
        [(t, round(e_theta(t), 2)) for t in range(0, 91, 3)])
    lines = [f"glass ply (V_f 0.60): E1 {E1:.1f}, E2 {E2:.1f}, G12 {G12} GPa "
             f"(teaching)",
             "  angle deg   modulus along the load GPa"]
    for t, e in out.items():
        lines.append(f"  {t:9d}   {e:26.1f}")
    lines += [f"  turning the ply 15 degrees already loses "
              f"{1 - out[15] / out[0]:.0%} of the stiffness:",
              "  caps carry bending with fibres along the blade; shells use",
              "  +-45 plies for shear and torsion - and a ply laid a few",
              "  degrees off in the cap is a stiffness defect the ply map",
              "  record (lab D) is there to prevent"]
    emit("t_offaxis", lines)
    return out


# ------------------------------------------------ wrinkles
def wrinkles() -> dict[float, float]:
    lines = ["compression strength kept by a cap with a wrinkle of height A",
             "  over length L (teaching curve 1 / (1 + 6 A/L))",
             "  A/L     strength kept   disposition (teaching)"]
    out = {}
    for r in (0.01, 0.03, 0.05, 0.10):
        k = 1 / (1 + 6 * r)
        out[r] = k
        disp = "accept" if r <= 0.02 else ("repair by design" if r <= 0.05
                                           else "reject")
        lines.append(f"  {r:4.2f}   {k:13.0%}   {disp}")
    lines += ["  a wrinkle buckles the fibres and the cap loses compression",
              "  strength where it bends most; the scan finds wrinkles above",
              "  a size, and the design authority, not the shop floor,",
              "  decides whether a wrinkle in a cap may stay (lab D, NCR)"]
    emit("t_wrinkles", lines)
    return out


# ------------------------------------------------ static test
def static_test(predicted: float = 12.1, measured: float = 12.7,
                band: float = 0.10, margin: float = 5.2) -> dict[str, float]:
    dev = measured / predicted - 1
    lines = ["full-scale static test of the first blade (teaching)",
             "  load to the extreme with the test factors of the design",
             f"  tip deflection predicted {predicted} m (ch 11, stiffened caps)",
             f"  measured {measured} m ({dev:+.1%})",
             f"  agreement band +-{band:.0%}: "
             f"{'within' if abs(dev) <= band else 'outside'}",
             f"  the extra {measured - predicted:.1f} m is "
             f"{(measured - predicted) / margin:.0%} of the {margin} m "
             "clearance margin (lesson B, clearance)",
             "  the test checks the model, not only the blade: a deflection",
             "  above the prediction eats into the tip-tower clearance",
             "  of ch 11 and is fed back to the design before series",
             "  production (IEC 61400-5 names the tests)"]
    emit("t_static", lines)
    return dict(dev=dev)


# ------------------------------------------------ fatigue test acceleration
def fatigue_test(f_hz: float = 0.7, n_test: float = 2e6, m: float = 10.0,
                 factor: float = 1.15) -> dict[str, float]:
    days = n_test / f_hz / 86400
    equiv = n_test * factor ** m
    lines = [f"blade fatigue test at resonance, {f_hz} Hz (teaching)",
             f"  {n_test:.0e} cycles take {days:.0f} days of running",
             f"  load raised {factor} x with S-N slope m = {m:.0f} (composite):",
             f"  equivalent to {equiv:.2e} cycles at the design load "
             f"({factor ** m:.1f} x)",
             "  a steep S-N slope lets a little more load stand for many",
             "  more cycles - and the same steepness means a small load",
             "  error makes a large life error; the test load is measured,",
             "  not set"]
    emit("t_fatigue", lines)
    return dict(days=days, equiv=equiv)


# ------------------------------------------------ insert pull tests
def inserts(seed: int = 4210, need: float = 350.0) -> dict[str, float]:
    rng = random.Random(seed)
    tests = [rng.gauss(430.0, 28.0) for _ in range(12)]
    m, s = mean(tests), pstdev(tests)
    k = 2.0                                      # teaching, 12 tests
    char = m - k * s
    lines = [f"root insert pull-out, 12 coupon tests from one mould set (kN)",
             f"  mean {m:.0f}, sd {s:.0f}; characteristic value mean - {k} sd "
             f"= {char:.0f}",
             f"  against the {need:.0f} kN the design asks of one insert "
             "(teaching):",
             f"  {'meets' if char >= need else 'fails'} - the characteristic, "
             "not the mean, is compared",
             "  a lower bound from few tests needs a larger k; a new resin",
             "  or insert batch restarts the series"]
    emit("t_inserts", lines)
    return dict(mean=m, char=char)


# ------------------------------------------------ blade weights SPC
def weights(seed: int = 4211) -> dict[str, int]:
    rng = random.Random(seed)
    w = []
    for k in range(30):
        drift = 0.06 * (k - 17) if k > 17 else 0.0          # t, resin uptake
        w.append(round(22.0 + drift + rng.gauss(0, 0.05), 3))
    base = w[:15]
    mr = mean(abs(a - b) for a, b in zip(base[1:], base))
    cl = mean(base)
    ucl = cl + 2.66 * mr
    first = next((k + 1 for k, x in enumerate(w) if x > ucl), 0)
    csv("ch42-weights.csv", "blade,t", [(k + 1, x) for k, x in enumerate(w)])
    lines = ["weights of 30 blades from one mould (t, individuals chart)",
             f"  centre {cl:.3f} t, upper limit {ucl:.3f} t (from blades 1-15)",
             f"  first blade above the limit: {first}",
             "  heavier blades from blade 19: more resin taken up - a",
             "  bag, an inlet or a fabric batch has changed; the weight is",
             "  the cheapest process signal a blade factory has, and it",
             "  also moves the set matching (lesson B)"]
    emit("t_weights", lines)
    return dict(first=first)


if __name__ == "__main__":
    offaxis()
    wrinkles()
    static_test()
    fatigue_test()
    inserts()
    weights()
