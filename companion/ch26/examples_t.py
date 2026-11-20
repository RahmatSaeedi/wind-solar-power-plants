"""Chapter 26 - expansion round 6: reading a secondary-injection result
against the relay's and the test set's tolerances, what a reversed CT
looks like in the on-load check of a differential, and how many wiring
errors a panel check should expect to find.

Run from the project root:   python -m companion.ch26.examples_t
Writes companion/ch26/expected/t_*.txt. Teaching values A-331 to A-335
(tolerances from makers' data in a real test plan).
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr


# [start: band]
def acceptance_band(t_set: float, rel_pct: float, abs_s: float,
                    set_pct: float) -> tuple:
    """Accept an operate time within the relay's tolerance (the larger of
    a percentage and a fixed time) widened by the test set's own error."""
    tol = max(t_set * rel_pct / 100, abs_s) + t_set * set_pct / 100
    return t_set - tol, t_set + tol
# [end: band]


def injection() -> None:
    f = src.RELAYS["feeder"]
    lines = ["secondary injection of the feeder relay (SI, TMS 0.10, pickup 0.8 A):",
             "  relay tolerance: 5 % or 30 ms, whichever is larger; test set 1 %",
             "  multiple   expected s   band s            measured s   result"]
    for m, meas in ((2.0, 1.04), (5.0, 0.455), (10.0, 0.335), (20.0, 0.198)):
        t = pr.trip_time(m * f["pickup"], f["pickup"], f["tms"])
        lo, hi = acceptance_band(t, 5.0, 0.030, 1.0)
        ok = lo <= meas <= hi
        lines.append(f"  {m:8.0f}   {t:10.3f}   {lo:6.3f} - {hi:6.3f}   {meas:10.3f}   "
                     f"{'pass' if ok else 'FAIL'}")
    lines += ["  a reading is judged against a band, not the bare number:",
              "  the relay's stated accuracy plus the test set's; one point",
              "  outside the band (here at 10 x) is investigated before",
              "  anyone touches the setting - wrong multiple injected, a",
              "  test lead, or a relay fault; the record keeps all points"]
    emit("t_injection", lines)


def polarity() -> None:
    load_a = 87.0                         # 20 MW at 132 kV on the HV side
    ct = 400.0
    lines = ["on-load check of the transformer differential (teaching):",
             f"  plant exporting 20 MW: HV current {load_a:.0f} A, CT {ct:.0f}/1 ->"
             f" {load_a / ct:.3f} A secondary",
             "  what the relay shows        differential pu   bias pu   trips?"]
    i = load_a / 275.6                    # per unit of the HV rated current
    cases = [("correct polarity", i, -i), ("one CT reversed", i, i)]
    for name, i1, i2 in cases:
        d, b = abs(i1 + i2), (abs(i1) + abs(i2)) / 2
        lines.append(f"  {name:28s} {d:15.2f}   {b:7.2f}   {'YES' if pr.diff_trips(i1, i2) else 'no'}")
    i_trip = 0.2 / (2 - 0.3)
    lines += ["  with correct wiring the differential reads close to zero; a",
              "  reversed CT shows twice the load as 'differential' and, with",
              "  pickup 0.2 and slope 0.3, trips once the load passes",
              f"  {i_trip:.3f} pu ({i_trip * 63:.1f} MVA) - so the first readings are taken at",
              "  low load, and the commissioning programme of qualified",
              "  staff decides how the trip is supervised meanwhile; the",
              "  readings go into the record"]
    emit("t_polarity", lines)


def terminations() -> None:
    n_term = 1800
    lines = ["wiring errors a panel check should expect to find (teaching rates)",
             f"  {n_term:,} terminations in a protection panel",
             "  error rate per 1,000   expected errors   chance of none"]
    for rate in (0.5, 1.0, 2.0):
        mu = n_term * rate / 1000
        lines.append(f"  {rate:21.1f}   {mu:15.1f}   {math.exp(-mu):14.1%}")
    lines += ["  even good wiring leaves one or two errors in a panel of this",
              "  size: a 100 % point-to-point check and the functional FAT",
              "  are expected to find them - a FAT that finds nothing is",
              "  asked how it looked (lesson K's punch list)"]
    emit("t_terminations", lines)


if __name__ == "__main__":
    injection()
    polarity()
    terminations()
