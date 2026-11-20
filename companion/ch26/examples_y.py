"""Chapter 26 - expansion round 10: grading the unit transformer's HV
relay above the turbine's LV breaker and below the feeder relay, and the
station-service protection when the board runs on the standby diesel.

Run from the project root:   python -m companion.ch26.examples_y
Writes companion/ch26/expected/y_*.txt. Teaching values A-331 to A-335.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr


def unit_grading() -> None:
    i_lv_at_hv = 1400.0                   # LV fault seen at 33 kV (lesson C, h_unit)
    pickup_u = 127.0
    t_lv = 0.05                           # turbine LV breaker incl. arcing (teaching)
    f = src.RELAYS["feeder"]
    tms_u = math.ceil(pr.tms_for(t_lv + 0.3, i_lv_at_hv, pickup_u) * 100) / 100
    t_u = pr.trip_time(i_lv_at_hv, pickup_u, tms_u)
    t_f = pr.trip_time(i_lv_at_hv, f["pickup"], f["tms"])
    lines = ["grading at an LV fault in the turbine (seen as 1,400 A at 33 kV):",
             f"  turbine LV breaker clears in {t_lv * 1e3:.0f} ms (teaching)",
             f"  unit HV relay: pickup {pickup_u:.0f} A, TMS for 0.3 s above it: {tms_u:.2f}"
             f" -> {t_u:.2f} s",
             f"  feeder relay at the same current: {t_f:.2f} s",
             f"  margin unit -> feeder: {t_f - t_u:.2f} s "
             f"({'graded' if pr.grading_ok(t_u, t_f) else 'SHORT of 0.3 s'})",
             "  window for the unit stage at this current:"]
    for margin in (0.30, 0.25):
        lo, hi = t_lv + margin, t_f - margin
        lines.append(f"    margins {margin:.2f} s: {lo:.3f} to {hi:.3f} s -> "
                     + ("feasible" if lo < hi else "NO window"))
    lines += ["  with 0.3 s on both sides the unit stage has no room: the",
              "  feeder answers in 0.65 s, and 0.05 + 0.3 + 0.3 needs more;",
              "  a finding of the study - 0.25 s margins justified by",
              "  numerical relays and fast breakers (then a definite-time",
              "  unit stage at 0.35 s fits), or a slower feeder if lesson",
              "  B's grading allows; decided in the coordination report"]
    emit("y_unitgrading", lines)


def diesel_board() -> None:
    u0 = 230.0
    lines = ["the 400 V board on the standby diesel (ch 24 decrement, teaching)",
             "  source           fault A   source ohm   longest 4 mm2 run, 32 A C"]
    for name, i in (("grid via SST", 7900.0), ("diesel, 0.1-1 s", 866.0), ("diesel, steady", 108.0)):
        z = u0 / i
        run = (u0 / 320.0 - z) / 0.0110
        txt = f"{run:6.0f} m" if run > 0 else "   none (never instantaneous)"
        lines.append(f"  {name:16s} {i:7.0f}   {z:10.3f}   {txt}")
    lines += ["  on the diesel the source impedance is far larger: the runs",
              "  that disconnect in time shrink, and with the steady",
              "  current (no field boost) the instantaneous trips never",
              "  operate; so the island board needs residual-current",
              "  devices on long runs, the diesel's own protection set for",
              "  its decrement curve, and a check of every final circuit",
              "  with the diesel as the source (ch 23 island mode)"]
    emit("y_diesel", lines)


if __name__ == "__main__":
    unit_grading()
    diesel_board()
