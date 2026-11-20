"""Chapter 51, lessons A (operating organisation) and C (operational
assurance): roles covered on every shift, the handover checklist, a week
of logs, the day-ahead deadline against the forecast's arrival, permits in
operation, event reporting, procedure reviews.

Run from the project root:   python -m companion.ch51.examples_a
Writes companion/ch51/expected/a_*.txt and c_*.txt.
"""
from __future__ import annotations

import numpy as np

from companion.ch51 import sources as src
from companion.ch51.common import emit
from plantp import operations


def roster() -> list:
    gaps = [(r, s, n, src.NEED[r]) for r, shifts in src.ROSTER.items()
            for s, n in shifts.items() if n < src.NEED[r]]
    lines = ["people qualified for each role, by shift (need in brackets)",
             "  role                        A   B   C   D"]
    for r, shifts in src.ROSTER.items():
        lines.append(f"  {r:26s} " + "  ".join(f"{shifts[s]:2d}" for s in "ABCD")
                     + f"   ({src.NEED[r]})")
    lines += ["  gaps:"] + [f"    {r} on shift {s}" for r, s, *_ in gaps]
    lines += [
              "  shift C has one operator and no authorised person; shift D",
              "  no first aider: a roster is checked role by role, not by",
              "  head count (ch 50 authorised persons)"]
    emit("a_roster", lines)
    return gaps


def handover() -> list:
    miss = [k for k, v in src.HANDOVER.items() if not v]
    lines = ["shift handover checklist (one handover, 18:00)"]
    lines += [f"  [{'x' if v else ' '}] {k}" for k, v in src.HANDOVER.items()]
    lines += [f"  {len(miss)} items not passed on: the alarms nobody owns and the",
              "  forecast version in use - the next shift re-reads the old",
              "  forecast and inherits alarms it believes are being handled"]
    emit("a_handover", lines)
    return miss


def log_week() -> dict:
    a = np.array(src.LOG_WEEK).reshape(7, 24)
    silent = int((a == 0).sum())
    night = int((a[:, 0:6] == 0).sum())
    lines = [f"a week of operating log entries per hour: {a.sum()} entries, "
             f"{silent} silent hours",
             f"  silent hours between 00:00 and 06:00: {night} of {silent}",
             "  a silent hour is not proof that nothing happened: the log",
             "  records at least the hourly round (plant state, alarms,",
             "  limits) so that 'nothing' is written, not assumed"]
    emit("a_log", lines)
    return dict(silent=silent, night=night)


def deadline() -> dict:
    t = np.array(src.FORECAST_READY_H)
    late = [(k + 1, x) for k, x in enumerate(t) if x > src.DA_DEADLINE_H - 1.0]
    lines = [f"day-ahead schedule due {src.DA_DEADLINE_H}:00; forecast arrival over a week"]
    lines += [f"  day {k + 1}: {int(x)}:{int(round((x % 1) * 60)):02d}"
              + ("  less than an hour to work with" if x > src.DA_DEADLINE_H - 1.0 else "")
              for k, x in enumerate(t)]
    lines += [f"  {len(late)} days left under an hour (one arrived after the deadline):",
              "  the procedure names a fallback - yesterday's forecast with",
              "  today's weather update - and the record says it was used"]
    emit("a_deadline", lines)
    return dict(late=late)


# ------------------------------------------------ C. assurance
def permits() -> dict:
    rows = [(m, i, o, c) for m, (i, o, c) in src.PERMITS_OP.items()]
    tot = sum(i for _, i, _, _ in rows)
    over = sum(o for _, _, o, _ in rows)
    conf = sum(c for *_, c in rows)
    lines = ["permits to work in operation, first half-year",
             "  month  issued  overran  isolation conflicts"]
    lines += [f"  {m:5d}  {i:6d}  {o:7d}  {c:19d}" for m, i, o, c in rows]
    busiest = max(rows, key=lambda r: r[1])
    cm = [str(m) for m, *_, c in rows if c]
    lines += [f"  {tot} permits, {over} overran ({over / tot:.1%}), {conf} isolation conflicts",
              f"  conflicts in months {', '.join(cm)}; the busiest month ({busiest[0]}, "
              f"{busiest[1]} permits) had",
              f"  {busiest[3]}: conflicts follow two jobs on one isolation point, not",
              "  volume - the permit office checks isolation points, not only",
              "  areas (ch 32, ch 50)"]
    emit("c_permits", lines)
    return dict(tot=tot, over=over, conf=conf)


def reporting() -> list:
    late = [(e, r - o, c) for e, o, r, c in src.EVENTS if r - o > src.REPORT_DAYS]
    lines = [f"reportable events: reported within {src.REPORT_DAYS} day?"]
    lines += [f"  {e:42s} {r - o} d" + ("  LATE" if r - o > src.REPORT_DAYS else "")
              for e, o, r, c in src.EVENTS]
    lines += [f"  {len(late)} late; two are safety events - the slip and the crane",
              "  near miss, whose lessons expire fastest; the SCADA loss is an",
              "  OT event with its own notice rule (ch 36) - a near miss",
              "  reported after five days is a memory, not a record"]
    emit("c_reporting", lines)
    return late


def procedures() -> list:
    due = operations.stale(src.PROCEDURES, src.TODAY, src.REVIEW_DAYS)
    lines = [f"operating procedures past their yearly review on {src.TODAY}"]
    lines += [f"  {k:38s} reviewed {d}" for k, d in src.PROCEDURES.items() if k in due]
    lines += ["  the two oldest are the ones used least and needed most:",
              "  loss of SCADA and restoration after a blackout - reviewed",
              "  against the plant as built and the ch 50 restart test"]
    emit("c_procedures", lines)
    return due


if __name__ == "__main__":
    roster()
    handover()
    log_week()
    deadline()
    permits()
    reporting()
    procedures()
