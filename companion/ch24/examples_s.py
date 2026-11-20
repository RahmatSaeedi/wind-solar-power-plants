"""Chapter 24 - third round: the sheath losses of three bonding methods,
tower footing resistance and back-flashover, the motor overload class
against the start time, the breaker mechanism's stored energy for an
auto-reclose cycle, terminal counts of the 33 kV panels, joints against
cable in the failure count, and a hold-point log read by program.

Run from the project root:   python -m companion.ch24.examples_s
Writes companion/ch24/expected/s_*.txt. Teaching values (A-321..A-325
extended).
"""
from __future__ import annotations

import math

from companion.ch24.common import emit


def bonding() -> None:
    i, length, s_mm, d_mm = 437.0, 800.0, 140.0, 105.0
    x_m = 2 * math.pi * 50 * 2e-7 * math.log(2 * s_mm / d_mm)       # ohm/m, sheath
    r_s = 0.15e-3                                                    # ohm/m, sheath
    e = x_m * i                                                      # V/m induced
    i_circ = e / math.hypot(r_s, x_m)
    loss_s = 3 * i_circ ** 2 * r_s * length / 1e3
    loss_c = 3 * i ** 2 * 2.6e-5 * length / 1e3
    lines = ["sheath bonding of an 800 m, 132 kV single-core section (teaching):",
             f"  induced sheath voltage {e * 1e3:.0f} mV/m at {i:.0f} A",
             "  method              standing V   circulating A   sheath loss kW",
             f"  both ends bonded    {0:10.0f}   {i_circ:13.0f}   {loss_s:14.1f}",
             f"  single point        {e * length:10.0f}   {0:13.0f}   {0:14.1f}",
             f"  cross-bonded (3)    {e * length / 3:10.0f}   {i_circ * 0.05:13.0f}"
             f"   {loss_s * 0.05 ** 2:14.2f}",
             f"  conductor loss for comparison: {loss_c:.1f} kW",
             "  bonding both ends wastes as much in the sheaths as in the",
             "  conductors; single-point bonding leaves a standing voltage",
             "  that grows with length; cross-bonding in three minor",
             "  sections cancels both (5 % imbalance assumed) - the reason",
             "  long HV routes are cross-bonded, with link boxes to test"]
    emit("s_bonding", lines)


def backflash() -> None:
    i, didt, l_tower, cfo = 30e3, 30e3 / 1e-6, 15e-6, 650e3
    lines = ["back-flashover: lightning on the tower top or earth wire (teaching):",
             f"  30 kA, front 30 kA/us, tower inductance 15 uH, insulation {cfo / 1e3:.0f} kV",
             "  footing ohm   I R kV   L di/dt kV   tower top kV   back-flash"]
    for r in (5, 10, 20, 40):
        v = i * r + l_tower * didt
        lines.append(f"  {r:11d}   {i * r / 1e3:6.0f}   {l_tower * didt / 1e3:10.0f}   {v / 1e3:12.0f}"
                     f"   {'yes' if v > cfo else 'no'}")
    lines += ["  the tower top rises with the current through its footing;",
              "  when the rise beats the insulator, it flashes back to a",
              "  phase and the line trips although the phase was never hit -",
              "  low footing resistance (rods, counterpoise) is the remedy,",
              "  measured at each tower and recorded (ch 26 lightning)"]
    emit("s_backflash", lines)


def overload_class() -> None:
    lines = ["motor overload relay class against the start (teaching curve):",
             "  trip time at 7.2 x set current: class 10 <= 10 s, class 20 <= 20 s",
             "  motor              start current   start time s   class 10   class 20"]
    for name, k, t in (("sump pump", 6.0, 3.0), ("well pump", 6.5, 8.0), ("heavy fan", 6.0, 18.0)):
        t10 = 10.0 * (7.2 / k) ** 2
        t20 = 20.0 * (7.2 / k) ** 2
        lines.append(f"  {name:18s} {k:13.1f} x   {t:12.1f}   {'ok' if t10 > t else 'TRIPS':8s}"
                     f"   {'ok' if t20 > t else 'TRIPS'}")
    lines += ["  a heavy fan takes long to reach speed: a class 10 relay trips",
              "  it during every start; class 20 lets it run up - the class",
              "  is chosen from the motor and load's start time, and the",
              "  motor must survive the class's time (the maker's data)"]
    emit("s_overload", lines)


def mechanism() -> None:
    e_op = {"O": 120.0, "C": 300.0}                  # J per operation (teaching)
    store = 900.0
    seq = ["O", "C", "O"]
    need = sum(e_op[x] for x in seq)
    lines = ["breaker mechanism energy for an auto-reclose cycle (teaching):",
             f"  spring stores {store:.0f} J; open {e_op['O']:.0f} J, close {e_op['C']:.0f} J",
             f"  cycle O - 0.3 s - CO needs {need:.0f} J: {'enough' if store >= need else 'NOT enough'}",
             f"  a second CO right after: {need + e_op['C'] + e_op['O']:.0f} J - needs the motor",
             "  to recharge (about 10-15 s) - the rated operating sequence",
             "  on the nameplate says what the mechanism can do; line",
             "  reclosing (utility's choice) must fit inside it; cable",
             "  feeders of Plant P do not reclose (cable faults are",
             "  permanent)"]
    emit("s_mechanism", lines)


def terminals() -> None:
    panels = [("+H01 incomer", 2, 3, 40), ("+H02..H05 feeders", 1, 2, 30),
              ("+H06 station service", 1, 2, 28), ("+H07 earthing transformer", 1, 2, 24),
              ("+H08 coupler", 1, 2, 30), ("+H09 metering and VT", 0, 1, 36)]
    lines = ["terminal count of the 33 kV section A panels (teaching):",
             "  panel                         CT cores  V-circ  other   terminals"]
    total = 0
    for name, cts, vts, other in panels:
        n = (4 if "H02" in name else 1)
        t = (cts * 3 * 4 + vts * 4 + other) * n
        total += t
        lines.append(f"  {name:28s}  {cts:8d}  {vts:6d}  {other:5d}   {t:9d}")
    spare = math.ceil(total * 0.2)
    lines += [f"  total {total} terminals, plus 20 % spare: {total + spare}",
              "  every terminal has a number on the wiring diagram, a label",
              "  in the panel and a line in the cable core list; the spare",
              "  terminals are the room for the changes that always come"]
    emit("s_terminals", lines)


def joints() -> None:
    lam_km, lam_joint, years = 0.002, 0.002, 25
    lines = ["faults over 25 years in a 4.4 km string: cable against joints",
             f"  (teaching rates: {lam_km} per km a year, {lam_joint} per joint a year)",
             "  drum m   joints   cable faults   joint faults   total"]
    for m, j in ((500, 8), (750, 4), (1100, 0)):
        c = 4.4 * lam_km * years
        jf = j * lam_joint * years
        lines.append(f"  {m:6d}   {j:6d}   {c:12.2f}   {jf:12.2f}   {c + jf:5.2f}")
    lines += ["  with short drums the joints fail more often than the cable",
              "  itself: fewer joints, and joints made by qualified jointers",
              "  with records, are the cheapest reliability (lesson B)"]
    emit("s_joints", lines)


LOG = [("H1 trench before laying", "released", "inspector"),
       ("H2 backfill before closing", "released", "foreman"),
       ("W1 drum receiving", "notified", ""),
       ("H3 joint 4 before backfill", "released", "inspector"),
       ("H4 test after laying", "open", ""),
       ("H5 backfill section 3", "released", "")]


def holdlog() -> None:
    bad = [(a, s, w) for a, s, w in LOG if a.startswith("H") and s == "released"
           and w != "inspector"]
    lines = ["hold-point log of one feeder (teaching):"]
    lines += [f"  {a:28s} {s:9s} {w or '-'}" for a, s, w in LOG]
    lines += [f"  hold points released by someone other than the inspector: {len(bad)}"]
    lines += [f"    {a} ({w or 'nobody named'})" for a, s, w in bad]
    lines += ["  a hold point released by the crew is not released: the work",
              "  after it is at risk and the record is a nonconformity; the",
              "  open H4 keeps the feeder from energisation (ch 48)"]
    emit("s_holdlog", lines)


if __name__ == "__main__":
    bonding()
    backflash()
    overload_class()
    mechanism()
    terminals()
    joints()
    holdlog()
