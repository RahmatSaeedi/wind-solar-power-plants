"""Chapter 26 - expansion round 13: re-energising a wind feeder with its
four unit transformers - the decaying inrush seen by the feeder relay,
with the inverse-time relay treated as an integrator of 1/t(I).

Run from the project root:   python -m companion.ch26.examples_ac
Writes companion/ch26/expected/ac_*.txt. Teaching values A-331 to A-335
(inrush peak, diversity and decay are illustrative; the makers' data
and an energising study give real values).
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr


# [start: integrate]
def relay_progress(i0: float, tau: float, pickup: float, tms: float,
                   dt: float = 0.001, t_end: float = 5.0) -> tuple:
    """Integrate 1 / t(I(t)) for a current decaying as i0 exp(-t/tau);
    the relay trips when the sum reaches 1. Returns (tripped, time or
    the largest progress reached)."""
    progress, t = 0.0, 0.0
    while t < t_end:
        i = i0 * math.exp(-t / tau)
        op = pr.trip_time(i, pickup, tms)
        if not math.isinf(op):
            progress += dt / op
        if progress >= 1.0:
            return True, t
        t += dt
    return False, progress
# [end: integrate]


def cold_load() -> None:
    f = src.RELAYS["feeder"]
    unit_peak = 1176.0                     # one unit's inrush peak (h_unit)
    lines = ["re-energising feeder =WS1 with four unit transformers (teaching)",
             "  inrush of four units with diversity 0.6, taken as an rms-like",
             "  current decaying with time constant tau; feeder SI 480 A, TMS 0.10",
             "  start A   tau s   feeder relay"]
    for tau in (0.2, 0.5, 1.0):
        i0 = 4 * unit_peak * 0.6 / math.sqrt(2)
        tripped, val = relay_progress(i0, tau, f["pickup"], f["tms"])
        txt = f"TRIPS after {val:.2f} s" if tripped else f"no trip ({val:.0%} of the way)"
        lines.append(f"  {i0:7.0f}   {tau:5.1f}   {txt}")
    lines += ["  an inverse-time relay adds up its progress as the current",
              "  falls: a short inrush passes, a slow one trips the feeder",
              "  it has just closed; the cures are second-harmonic blocking",
              "  on the feeder's overcurrent, a cold-load settings group",
              "  for the first seconds, or energising the units one by one",
              "  (their own breakers) - chosen in the energising study"]
    emit("ac_coldload", lines)


if __name__ == "__main__":
    cold_load()
