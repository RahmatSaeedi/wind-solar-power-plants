"""Chapter 26 - expansion round 9: how a direct strike's current shares
among the services entering a building (the duty of the first SPD
stage), and the protection needed at each energisation stage of
chapter 23 (what is live, what protects it, which setting group).

Run from the project root:   python -m companion.ch26.examples_x
Writes companion/ch26/expected/x_*.txt. Teaching values A-331 to A-335
(sharing assumptions are illustrative; the lightning standard and the
SPD makers give the real method).
"""
from __future__ import annotations

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr


def sharing() -> None:
    i_strike = 100.0                       # kA, a severe teaching stroke
    to_earth = 0.5                         # teaching share into the earth electrode
    lines = ["a direct strike on the control building: where the current goes",
             f"  stroke {i_strike:.0f} kA; teaching assumption: half into the earth",
             "  electrode, half shared equally by the metal services entering",
             "  services   kA per service   per conductor (4-wire LV)"]
    for n in (1, 2, 3, 4):
        per = i_strike * (1 - to_earth) / n
        lines.append(f"  {n:8d}   {per:14.1f}   {per / 4:25.1f}")
    lines += ["  the first SPD stage on each service is rated for its share",
              "  of the lightning impulse current, not for the surges that",
              "  arrive from far away; a fibre data link carries none of it",
              "  (no metal), one reason the plant's networks run on fibre",
              "  (ch 34); the real sharing comes from the lightning",
              "  standard's method and the building's services"]
    emit("x_sharing", lines)


def stages() -> None:
    i_one = src.NETWORK["ik_33_one"]
    feeder = src.RELAYS["feeder"]
    rows = [("S0 utility bay", "operator's relays", "-"),
            ("S1 line to the plant bay", "line diff. + distance", "L1"),
            ("S2 132 kV bus and T1", "T1 diff., gas, HV backup", "T1"),
            ("S3 section A, SST", "incomer, NER standby", "G1"),
            ("S4 first wind string", "feeder and unit relays", "G1")]
    lines = ["protection at each energisation stage of ch 23 (teaching)",
             "  stage                      protects the new part       settings group"]
    for st, prot, grp in rows:
        lines.append(f"  {st:26s} {prot:27s} {grp}")
    i_far = 4.68e3                         # far-end line-to-line, lesson B
    t = pr.trip_time(i_far, feeder["pickup"], feeder["tms"])
    lines += ["  at S4 only one transformer and few units feed a fault: the",
              f"  bus fault level is about {i_one / 1e3:.1f} kA and the far-end feeder fault",
              f"  {i_far / 1e3:.2f} kA, which the feeder relay clears in {t:.2f} s - every",
              "  stage is checked against its own fault levels; nothing is",
              "  energised whose protection has not been tested, and the",
              "  settings group in service is part of the switching",
              "  programme of the operator and the owner (ch 48-50)"]
    emit("x_stages", lines)


if __name__ == "__main__":
    sharing()
    stages()
