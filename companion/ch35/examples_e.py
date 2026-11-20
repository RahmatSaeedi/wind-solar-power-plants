"""Chapter 35, lesson E: the fire-alarm boundary seen from SCADA - which
approved statuses SCADA monitors and which it never commands, how a fire
alarm is routed when the control room is empty, two clocks that disagree
in the event records, behaviour on loss of the link, and who may do
what. The fire panel keeps its authority (ch 32, ch 34 lesson F).

Run from the project root:   python -m companion.ch35.examples_e
Writes companion/ch35/expected/e_*.txt.
Teaching values (A-400); the fire strategy and the authority decide.
"""
from __future__ import annotations

from companion.ch35.common import emit


def statuses() -> None:
    rows = [("zone in alarm (per zone)", "monitored", "hard-wired summary + serial detail"),
            ("fault / supervisory", "monitored", "hard-wired"),
            ("zone disabled or isolated", "monitored", "serial"),
            ("panel on battery", "monitored", "serial"),
            ("silence, reset, disable", "NEVER from SCADA", "fire panel only"),
            ("output test, walk test", "NEVER from SCADA", "fire panel, permit")]
    lines = ["fire-system statuses at the SCADA boundary (teaching, approved list)",
             "  status                         SCADA               path"]
    for a, b, c in rows:
        lines.append(f"  {a:30s} {b:19s} {c}")
    lines += ["  SCADA sees what the fire strategy approves it to see and",
              "  sends nothing back; a disabled zone is shown as loudly as",
              "  an alarm, because a fire there would not be seen"]
    emit("e_statuses", lines)


def routing() -> None:
    manned_h = 8
    rows = [("control room on site (manned 8 h a day)", 1.0),
            ("remote control centre (24 h)", 5.0),
            ("on-call phone call", 60.0),
            ("text message", 30.0)]
    lines = ["routing a fire alarm from an often unmanned site (teaching times)",
             "  path                                       seconds to a person"]
    for name, s in rows:
        lines.append(f"  {name:42s} {s:8.0f}")
    lines += [f"  the site room is manned {manned_h} h a day: for {24 - manned_h} h the alarm",
              "  must reach the remote centre and the on-call person by two",
              "  independent paths; the emergency plan (ch 32) starts from",
              "  that call - SCADA routing tells people, it does not",
              "  replace the fire system's own alarm devices and calls"]
    emit("e_routing", lines)


def clocks() -> None:
    drift_s_month = 30.0
    rows = [(1, drift_s_month), (6, 6 * drift_s_month), (12, 12 * drift_s_month)]
    lines = ["the fire panel's own clock against the synchronised SCADA clock",
             f"  fire panel drift (teaching): {drift_s_month:.0f} s a month, never set",
             "  months   offset s"]
    for m, s in rows:
        lines.append(f"  {m:6d}   {s:8.0f}")
    lines += ["  after a year the panel's log says the detector went off",
              "  six minutes before the SCADA saw the alarm; for the",
              "  investigation both stamps are kept - the panel's own and",
              "  SCADA's on arrival - and the offset is checked at every",
              "  maintenance visit, or the panel synchronised if its maker",
              "  and the fire-system designer allow it"]
    emit("e_clocks", lines)


def loss_of_link() -> None:
    rows = [("serial detail link lost", "alarm 'fire detail lost', priority 1;",
             "hard-wired summary still works"),
            ("hard-wired summary cut", "alarm at once (normally closed);",
             "treated as a possible fire until checked"),
            ("SCADA server down", "fire panel unaffected; local alarms;",
             "the remote centre loses sight - phone path")]
    lines = ["loss of the fire link, seen from SCADA (teaching design intent)"]
    for a, b, c in rows:
        lines += [f"  {a}:", f"    {b}", f"    {c}"]
    lines += ["  every loss is visible and none of them changes what the",
              "  fire system does by itself"]
    emit("e_link", lines)


if __name__ == "__main__":
    statuses()
    routing()
    clocks()
    loss_of_link()
