"""Chapter 26 - expansion round 11: fuse or breaker for the PV unit
transformers (the inrush check), and a completeness check of test
records - what turns a test sheet into evidence.

Run from the project root:   python -m companion.ch26.examples_z
Writes companion/ch26/expected/z_*.txt. Teaching values A-331 to A-335
(fuse data are illustrative; makers' curves decide).
"""
from __future__ import annotations

import math

from companion.ch26.common import emit


def fuse_or_breaker() -> None:
    lines = ["fuse or breaker for a unit transformer at 33 kV (teaching rule:",
             "  a fuse melts in 0.1 s at about 8 x its rating; inrush ~12 x In",
             "  for about 0.1 s must not melt it; teaching top of range 63 A)",
             "  unit MVA   In A   inrush A   smallest fuse A   within the range?"]
    for s in (1.0, 2.5, 5.5):
        i_n = s * 1e6 / (math.sqrt(3) * 33e3)
        inrush = 12 * i_n
        fuse = inrush / 8
        lines.append(f"  {s:8.1f}   {i_n:4.0f}   {inrush:8.0f}   {fuse:15.0f}   "
                     f"{'yes' if fuse <= 63 else 'NO':>17s}")
    lines += ["  for the 5.5 MVA PV units the inrush alone asks for a fuse",
              "  above the teaching range: so they also get a breaker",
              "  with relay (lesson C's window), as the wind units do -",
              "  fuses stay for small transformers such as the station",
              "  service; the maker's time-current curves give the answer"]
    emit("z_fuse", lines)


# [start: record]
REQUIRED = ["relay tag", "setting file and checksum", "firmware version",
            "test set and serial", "calibration date of the test set",
            "results for every point", "acceptance band", "tester", "witness",
            "date", "deviations and their closure"]


def missing(record: dict) -> list:
    """Fields a test record lacks before it can count as evidence."""
    return [f for f in REQUIRED if not record.get(f)]
# [end: record]


def records() -> None:
    rec = {"relay tag": "=WS1-Q1-F1", "setting file and checksum": "rev A d7fc3541542e",
           "firmware version": "", "test set and serial": "TS-200 #4471",
           "calibration date of the test set": "", "results for every point": "4 of 4",
           "acceptance band": "5 % or 30 ms + 1 %", "tester": "commissioning engineer",
           "witness": "", "date": "2026-11-16", "deviations and their closure": "point 10 x: open"}
    gaps = missing(rec)
    lines = ["is this secondary-injection sheet evidence? (fields of a test record)"]
    for f in REQUIRED:
        lines.append(f"  {f:34s} {'present' if rec.get(f) else 'MISSING'}")
    lines += [f"  missing: {len(gaps)} - {', '.join(gaps)}",
              "  without the firmware version the test may be of another",
              "  relay's logic; without the test set's calibration the",
              "  numbers have no anchor; without a witness the operator",
              "  may not accept it - and an open deviation means the record",
              "  is not closed; the record is evidence only when complete"]
    emit("z_record", lines)


if __name__ == "__main__":
    fuse_or_breaker()
    records()
