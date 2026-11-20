"""Chapter 28 - expansion round 7: holding the export limit when a gust
arrives (overshoot and the energy the safety margin costs), negative-
sequence current during an unbalanced fault, and the register of
operating restrictions the studies produce.

Run from the project root:   python -m companion.ch28.examples_r
Writes companion/ch28/expected/r_*.txt and diagrams/data/ch28-limit.csv.
Teaching values (A-348).
"""
from __future__ import annotations

import numpy as np

from companion.ch28.common import csv, emit


# [start: limit]
def limit_sim(setpoint: float, ramp: float = 2.0, delay: float = 1.0,
              tau: float = 0.5, dt: float = 0.05, t_end: float = 30.0):
    """Available power ramps up at `ramp` MW/s from 90 MW (a gust); the
    plant controller caps export at `setpoint`, acting on a measurement
    `delay` s old through units that follow with time constant `tau`."""
    n = int(t_end / dt)
    avail = np.minimum(90 + ramp * np.maximum(np.arange(n) * dt - 5, 0), 115)
    out = np.full(n, avail[0])
    cap = 115.0
    lag = int(delay / dt)
    for k in range(1, n):
        seen = out[max(k - lag, 0)]
        if seen > setpoint:
            cap = max(setpoint, cap - (seen - setpoint))
        else:
            cap = min(115.0, max(cap, setpoint))
        target = min(avail[k], cap)
        out[k] = out[k - 1] + (target - out[k - 1]) * dt / tau
    return np.arange(n) * dt, avail, out
# [end: limit]


def export_limit() -> None:
    from companion.ch15 import sources as s15
    poc = s15.plant_year()["poc"]
    lines = ["holding a 100 MW export limit through a gust (2 MW/s, teaching)",
             "  set-point MW   peak export MW   above 100.05 for s   margin MWh/yr"]
    rows = None
    for sp in (100.0, 99.0, 98.0):
        t, a, o = limit_sim(sp)
        over = float(np.sum(o > 100.05) * (t[1] - t[0]))
        cost = float(np.sum(np.clip(np.minimum(poc, 100.0) - sp, 0, None)))
        lines.append(f"  {sp:12.0f}   {o.max():14.1f}   {over:18.1f}   {cost:13.0f}")
        if sp == 100.0:
            rows = (t, a, o)
        if sp == 98.0:
            rows98 = o
    t, a, o = rows
    csv("ch28-limit.csv", "t,avail,sp100,sp98",
        [(f"{x:.2f}", f"{y:.2f}", f"{z:.2f}", f"{w:.2f}")
         for x, y, z, w in zip(t[::4], a[::4], o[::4], rows98[::4])])
    lines += ["  acting on a measurement one second old, a controller set",
              "  at the limit itself overshoots it by 3.4 MW for about 4 s",
              "  of the gust; one or two MW lower cuts that to one or two",
              "  seconds, at 86-190 MWh a year - the study states the",
              "  overshoot, the margin and its cost, and the operator",
              "  says whether a short overshoot is acceptable (REQ-G16)"]
    emit("r_limit", lines)


def negative_sequence() -> None:
    x = 0.08                                  # grid negative-sequence impedance, pu on plant
    v2_grid = 0.30                            # negative-sequence voltage of the fault, pu
    lines = ["negative-sequence voltage at the POC in an unbalanced fault",
             "  (grid side 0.30 pu; plant injects k2 x V2 of negative-sequence current)",
             "  k2     V2 at POC pu   positive-sequence unaffected"]
    for k2 in (0.0, 1.0, 2.0, 4.0):
        v2 = v2_grid / (1 + k2 * x)
        lines.append(f"  {k2:3.1f}   {v2:13.3f}   yes")
    lines += ["  a converter that also controls the negative sequence (if",
              "  the code asks for it) pulls the unbalance down a little",
              "  on a strong grid - and uses current that the positive",
              "  sequence then cannot; the requirement, the unit's type",
              "  test and the model must all name the same behaviour"]
    emit("r_negseq", lines)


def restrictions() -> None:
    reg = [
        ("one main transformer out", "export <= 62 MW, coupler closed", "G-contingency"),
        ("grid at 1.10 pu, output", "units absorb Q (taps at stop)", "B-stability"),
        ("minimum grid strength", "voltage-loop gain retuned", "C-vcontrol"),
        ("line maintenance", "plan for a calm day", "G-contingency"),
        ("45 C day, full output", "Q > +29 Mvar needs S1 or bank", "F-envelope"),
        ("loss of the grid end", "intertrip within 0.15 s", "C-islanding"),
        ("export near 100 MW", "set-point 98-99 MW", "r_limit"),
    ]
    lines = ["operating restrictions written by the studies (teaching register)",
             "  condition                   restriction                      source"]
    for cond, rest, src_ in reg:
        lines.append(f"  {cond:27s} {rest:32s} {src_}")
    lines += ["  each restriction becomes a line in the operating",
              "  procedures (ch 51) and, where it can, a rule in the plant",
              "  controller (ch 20) - a study result nobody operates by is",
              "  not yet finished"]
    emit("r_restrictions", lines)


if __name__ == "__main__":
    export_limit()
    negative_sequence()
    restrictions()
