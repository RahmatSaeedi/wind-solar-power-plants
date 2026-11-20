"""Chapter 27 - expansion round 3: availability of a contracted service
from a log of outages, the reactive power error made by a transducer's
phase error, a recorder's clock drifting without its satellite time,
and the loss of the filter reactor with harmonic currents.

Run from the project root:   python -m companion.ch27.examples_p
Writes companion/ch27/expected/p_*.txt. Teaching values A-339, A-340.
"""
from __future__ import annotations

import math

from companion.ch27 import sources as src
from companion.ch27.common import emit


def availability() -> None:
    required = 8760.0
    outages = [("controller fault", 6.0), ("comms link down", 14.0), ("planned upgrade", 24.0),
               ("battery HVAC trip", 9.0), ("grid outage (excused)", 30.0)]
    excused = sum(h for n, h in outages if "excused" in n)
    lost = sum(h for n, h in outages if "excused" not in n)
    a = 1 - lost / (required - excused)
    lines = ["availability of the voltage-control service over a year (teaching)",
             "  event                       hours"]
    for n, h in outages:
        lines.append(f"  {n:27s} {h:5.0f}")
    lines += [f"  required {required:.0f} h, excused {excused:.0f} h, lost {lost:.0f} h",
              f"  availability = 1 - lost / (required - excused) = {a:.3%}",
              f"  against a teaching 99.5 % target: {'met' if a >= 0.995 else 'missed'}",
              "  whether a planned upgrade counts as lost, and which grid",
              "  events are excused, are clauses of the service contract",
              "  (ch 21) - the log is the evidence, the clauses the rule"]
    emit("p_availability", lines)


def angle_error() -> None:
    p_mw = 100.0
    lines = ["reactive power error from a transducer phase error (100 MW, pf 1)",
             "  phase error deg   Q error Mvar   share of a 33 Mvar requirement"]
    for d in (0.1, 0.3, 0.5, 1.0):
        dq = p_mw * math.sin(math.radians(d))
        lines.append(f"  {d:15.1f}   {dq:12.2f}   {dq / 32.9:30.1%}")
    lines += ["  at full power and unity power factor a small angle error",
              "  shows up as reactive power that is not there: half a degree",
              "  is nearly a megavar; the reactive measurement for a service",
              "  uses a metering-class chain with its angle stated, and the",
              "  error budget is part of the acceptance (lesson K)"]
    emit("p_angle", lines)


def drift() -> None:
    lines = ["a recorder's clock without its satellite time (teaching drifts)",
             "  drift ppm   after 1 h s   after 1 day s   after 1 week s"]
    for ppm in (1, 5, 20, 50):
        lines.append(f"  {ppm:9d}   {ppm * 3.6e-3:11.3f}   {ppm * 86400e-6:13.2f}   {ppm * 604800e-6:14.1f}")
    lines += ["  a 20 ppm clock is 1.7 s wrong after a day: 10-minute values",
              "  barely notice, an event sequence (ch 26) is ruined; the",
              "  recorder logs when it lost and regained the time source,",
              "  and that log is checked before events are read"]
    emit("p_drift", lines)


def reactor_loss() -> None:
    f = src.FILTER
    i1 = f["q_mvar"] * 1e6 / (math.sqrt(3) * 33e3)
    harm = {5: 0.35 * i1, 7: 0.10 * i1, 11: 0.05 * i1}     # teaching filter currents
    r_dc = 0.08
    lines = ["filter reactor loss with harmonic currents (teaching):",
             f"  fundamental {i1:.0f} A; 5th, 7th, 11th: "
             + ", ".join(f"{v:.0f} A" for v in harm.values()),
             "  order   current A   R factor   loss kW (3 phases)"]
    tot = 3 * i1 ** 2 * r_dc / 1e3
    lines.append(f"  {1:5d}   {i1:9.0f}   {1.0:8.2f}   {tot:18.2f}")
    for h, i in harm.items():
        k = 1 + 0.05 * h * h                                  # teaching eddy/skin growth
        loss = 3 * i * i * r_dc * k / 1e3
        tot += loss
        lines.append(f"  {h:5d}   {i:9.0f}   {k:8.2f}   {loss:18.2f}")
    lines += [f"  total {tot:.2f} kW; the 5th adds {100 * (3 * harm[5] ** 2 * r_dc * 2.25 / 1e3) / (3 * i1 ** 2 * r_dc / 1e3):.0f} % to the 50 Hz loss",
              "  a reactor rated on 50 Hz current alone runs hot: the",
              "  specification gives the harmonic duty and the maker's heat",
              "  run proves it (lesson K)"]
    emit("p_reactor", lines)


if __name__ == "__main__":
    availability()
    angle_error()
    drift()
    reactor_loss()
