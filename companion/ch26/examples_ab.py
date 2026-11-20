"""Chapter 26 - expansion round 12: four steps graded together at the
turbine end of a wind feeder - the turbine's LV breaker, the unit
transformer relay (definite time 0.35 s, the 0.25 s margin decision of
lesson C, and its instantaneous stage at 1,820 A), the feeder relay and
the incomer - checked fault case by fault case.

Run from the project root:   python -m companion.ch26.examples_ab
Writes companion/ch26/expected/ab_*.txt and diagrams/data/ch26-fourstep.csv.
Teaching values A-331 to A-335.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import csv, emit
from plantp import protection as pr

T_LV, PICK_U, T_U, I_INST, T_INST = 0.05, 127.0, 0.35, 1820.0, 0.03


def unit_time(i: float) -> float:
    """Unit transformer relay: instantaneous above 1,820 A, definite
    time 0.35 s above twice its pickup, nothing below."""
    if i >= I_INST:
        return T_INST
    return T_U if i >= 2 * PICK_U else math.inf


def fmt(t: float) -> str:
    return "-" if math.isinf(t) else f"{t:.2f}"


def four_steps() -> None:
    f, inc = src.RELAYS["feeder"], src.RELAYS["incomer"]
    # case, current through the feeder relay, through the incomer (lesson B:
    # converters on other feeders feed the feeder relay, not the incomer)
    cases = [("LV fault in the turbine", 1400.0, 1400.0, True, True),
             ("HV fault at the unit transformer", 4680.0, 4680.0, False, True),
             ("feeder cable fault, far end (LL)", 4680.0, 4680.0, False, False),
             ("feeder head fault (coupler open)", 7750.0, 6400.0, False, False)]
    lines = ["four steps at the turbine end of a wind feeder, case by case (33 kV)",
             "  case                               kA    LV    unit  feeder  incomer  margin"]
    for name, i, i_inc, lv, unit in cases:
        t_lv = T_LV if lv else math.inf
        t_u = unit_time(i) if unit else math.inf
        t_f = pr.trip_time(i, f["pickup"], f["tms"])
        t_i = pr.trip_time(i_inc, inc["pickup"], inc["tms"])
        chain = [t for t in (t_lv, t_u, t_f, t_i) if not math.isinf(t)]
        margin = min(b - a for a, b in zip(chain, chain[1:]))
        lines.append(f"  {name:33s} {i / 1e3:4.2f}  {fmt(t_lv):>4s}  {fmt(t_u):>4s}  {t_f:6.2f}"
                     f"  {fmt(t_i):>7s}  {margin:6.2f}")
    rows = []
    for k in range(3, 81):
        i = k * 100.0
        t_u = unit_time(i) if i <= 1400 or i >= I_INST else math.inf
        t_i = pr.trip_time(i, inc["pickup"], inc["tms"])
        rows.append((f"{i / 1e3:.1f}", f"{pr.trip_time(i, f['pickup'], f['tms']):.3f}",
                     "nan" if math.isinf(t_i) else f"{t_i:.3f}",
                     "nan" if math.isinf(t_u) else f"{t_u:.3f}",
                     f"{T_LV:.3f}" if i <= 1400 else "nan"))
    csv("ch26-fourstep.csv", "ka,feeder,incomer,unit,lv", rows)
    lines += ["  no fault drives between 1.4 kA (the largest LV fault seen",
              "  through the unit) and 4.68 kA (the smallest HV fault at the",
              "  turbine) through the unit relay, so its two stages cover",
              "  the two real cases: 0.35 s for LV faults, instantaneous for",
              "  HV faults; every margin in the table is at least 0.27 s,",
              "  and the 0.25 s decision of lesson C is met everywhere;",
              "  below 1.6 kA the incomer does not pick up - its backup",
              "  for those faults is the feeder's breaker-failure stage"]
    emit("ab_fourstep", lines)


if __name__ == "__main__":
    four_steps()
