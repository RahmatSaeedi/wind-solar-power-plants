"""Chapter 28 - expansion round 6 (S1, when contracted): the battery's
converter shared between a fast-frequency reserve and voltage support,
and what each service gets when a dip and a frequency event come
together under P or Q priority.

Run from the project root:   python -m companion.ch28.examples_q
Writes companion/ch28/expected/q_*.txt. Teaching values (D-023, A-348).
"""
from __future__ import annotations

import math

from companion.ch28.common import emit

S_PCS = 20.0          # MVA of the battery converters (S1)


def sharing() -> None:
    reserve = 5.0
    lines = ["battery converters (20 MVA) shared: dispatch, a 5 MW frequency reserve",
             "  held back, and the reactive power left for voltage support",
             "  dispatch MW   P that must fit MW   Q available Mvar"]
    for p in (0.0, 5.0, 10.0, 15.0):
        p_fit = abs(p) + reserve
        q = math.sqrt(max(S_PCS ** 2 - p_fit ** 2, 0.0))
        lines.append(f"  {p:11.0f}   {p_fit:18.0f}   {q:16.1f}")
    lines += ["  the reserve is power the converter must be able to add at",
              "  any moment, so it is counted against the current limit",
              "  even when unused; the battery's reactive power for the",
              "  POC (lesson F) shrinks as dispatch grows - the controller",
              "  allocates, and the study checks the corners"]
    emit("q_sharing", lines)


def coincident() -> None:
    i_max = 1.1
    iq_need, ip_need = 1.0, 0.5 + 0.25        # dip to 0.5 pu (k 2); export + reserve
    lines = ["a dip (needs reactive current) and a frequency event (needs active",
             "  power) together: 1.1 pu current limit, battery exporting 0.5 pu",
             "  with a 0.25 pu frequency reserve; the dip asks for 1.0 pu reactive",
             "  priority   reactive got/need   active got/need   reserve delivered"]
    for prio in ("Q first", "P first"):
        if prio == "Q first":
            iq = min(iq_need, i_max)
            ip = min(ip_need, math.sqrt(i_max ** 2 - iq ** 2))
        else:
            ip = min(ip_need, i_max)
            iq = min(iq_need, math.sqrt(i_max ** 2 - ip ** 2))
        kept = max(0.0, ip - 0.5) / 0.25
        lines.append(f"  {prio:9s}  {iq:8.2f} / {iq_need:4.2f}   {ip:7.2f} / {ip_need:4.2f}"
                     f"   {100 * kept:17.0f} %")
    lines += ["  the current limit cannot serve both in full: with reactive",
              "  priority (usual for ride-through) the reserve and even part",
              "  of the export vanish during the dip; with active priority",
              "  the voltage gets a fifth less support - the requirement or",
              "  the contract states which wins, and the study shows the cost"]
    emit("q_coincident", lines)


if __name__ == "__main__":
    sharing()
    coincident()
