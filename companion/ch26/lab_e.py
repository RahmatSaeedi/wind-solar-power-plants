"""Chapter 26, lab E - reading a sequence-of-events record after a trip:
which relay operated, whether it operated as set, what failed, and what
the clock offset of one relay would have made us believe.

Run from the project root:   python -m companion.ch26.lab_e
Writes companion/ch26/expected/e2_*.txt. The record is synthetic
(A-335), built to teach the reading, not taken from a real plant.
"""
from __future__ import annotations

from companion.ch26.common import emit

# [start: soe]
SOE = [   # time s, device, event (negative time: standing before)
    (-1.0, "=WS2-Q1", "TCS coil 2 alarm standing, shelved in SCADA"),
    (0.000, "=WS2-Q1-F1", "51N start (earth fault on =WS2)"),
    (0.001, "=MV-A-F59N", "59N start (bus neutral voltage)"),
    (0.002, "=NER-A-F51N", "standby earth fault start"),
    (0.503, "=WS2-Q1-F1", "51N trip"),
    (0.504, "=WS2-Q1-F1", "50BF start"),
    (0.505, "=WS2-Q1", "trip coil 1 energised"),
    (0.655, "=WS2-Q1-F1", "50BF trip to section A"),
    (0.660, "=MV-Q0", "open (already open)"),
    (0.716, "=T1-Q2", "open"),
    (0.718, "=WS2-Q1-F1", "51N reset"),
    (0.720, "=NER-A-F51N", "standby earth fault reset"),
    (0.722, "=MV-A-F59N", "59N reset"),
]
SET = {"51N delay": 0.50, "BF timer": 0.15}
# [end: soe]


def first(event: str) -> float:
    return next(t for t, _, e in SOE if event in e)


def reading() -> None:
    t_start, t_trip = first("51N start"), first("51N trip")
    t_bf = first("50BF trip")
    t_inc = next(t for t, d, e in SOE if d == "=T1-Q2")
    breaker_open = any(d == "=WS2-Q1" and e == "open" for _, d, e in SOE)
    lines = ["reading the sequence of events (worked):",
             f"  51N operated after {t_trip - t_start:.3f} s (set {SET['51N delay']} s):"
             " as set",
             f"  =WS2-Q1 got its trip at {first('trip coil 1'):.3f} s but no 'open' follows:"
             f" {'opened' if breaker_open else 'FAILED to open'}",
             f"  breaker failure tripped at {t_bf:.3f} s, {t_bf - first('50BF start'):.3f} s"
             f" after start (set {SET['BF timer']} s)",
             f"  =T1-Q2 opened at {t_inc:.3f} s: the fault was cleared by the",
             "  incomer, and all of section A was lost (two wind feeders,",
             "  PV feeder 3, battery A) instead of one feeder",
             f"  earth-fault duration {t_inc:.2f} s - inside the resistor's 10 s",
             "  the first line points to the cause: coil 2's supervision",
             "  alarm had stood since energising and was shelved - its",
             "  circuit was open all along (lesson K's punch item, wrongly",
             "  classed B), and coil 1's circuit or the mechanism did not",
             "  open the breaker: the backup trip path did not exist",
             "  actions: test both coils and the mechanism of =WS2-Q1;",
             "  close the punch item; review shelved alarms (ch 20); record",
             "  the event and its analysis"]
    emit("e2_reading", lines)


def clocks() -> None:
    offset = 0.040
    t_inc_wrong = next(t for t, d, e in SOE if d == "=T1-Q2") - offset
    lines = ["what a clock error does to the reading:",
             f"  if the incomer's recorder ran {offset * 1e3:.0f} ms slow, its"
             f" open would read {t_inc_wrong:.3f} s",
             f"  breaker failure at {first('50BF trip'):.3f} s and the incomer open"
             f" {t_inc_wrong - first('50BF trip'):.3f} s later:",
             "  an opening time shorter than any breaker's - the reader",
             "  would suspect the breaker-failure logic, not the clocks",
             "  so every recorder takes its time from one source (a",
             "  satellite clock with a network time protocol); the record",
             "  of time quality is part of the evidence",
             "  a check: an event every recorder sees (the fault's start)",
             "  must carry the same time in all of them"]
    emit("e2_clocks", lines)


if __name__ == "__main__":
    reading()
    clocks()
