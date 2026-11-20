"""Chapter 32, lab J: the integrated readiness exercise - the winter-night
scenario at T07 (lab H) run as a table-top with timed injects. For each
decision: who the plan names as owner, who acted, how fast, and whether
a record was made; then the lessons-learned actions ninety days later,
counted as closed with evidence, closed by claim, open and overdue.

Run from the project root:   python -m companion.ch32.lab_j
Writes companion/ch32/expected/j_*.txt.
Synthetic teaching values (A-375). The exercise tests roles, links and
records; it prescribes no rescue technique and no security tactic.
"""
from __future__ import annotations

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import emit

# [start: injects]
INJECTS = [  # (minute, inject, decision, owners named in the plan,
    #           minutes to act or None, target minutes, record made)
    (0, "alarm from T07: crushed hand", "start rescue, call ambulance",
     ["crew lead"], 2, 5, True),
    (5, "radio repeater fails", "move to the next link",
     ["control room", "crew lead"], 9, 2, False),
    (12, "wadi crossing flooded", "agree a second route",
     ["on-call manager"], 14, 15, True),
    (20, "unknown vehicle at the gate", "report and record, no approach",
     ["control room"], 3, 5, True),
    (25, "ambulance asks for a guide", "meet the ambulance at the gate",
     [], 18, 10, False),
    (35, "village elder calls", "inform and log the call",
     [], 6, 10, False),
    (75, "casualty on the ground", "hand over to the ambulance",
     ["rescue team lead"], 1, 5, True),
    (120, "stand down", "debrief and support the crew",
     ["site manager"], None, 60, False),
    (1440, "next day", "report with actions and owners",
     ["HSE lead"], 300, 480, True),
]
# [end: injects]


def clarity(owners: list[str]) -> str:
    return {0: "none", 1: "one"}.get(len(owners), "two+")


def injects() -> dict:
    lines = ["table-top of the winter night at T07: decisions and roles",
             "   min  decision                        owner  act  target  rec"]
    count = {"one": 0, "none": 0, "two+": 0}
    on_time = recorded = 0
    for m, _, dec, owners, act, target, rec in INJECTS:
        c = clarity(owners)
        count[c] += 1
        ok = act is not None and act <= target
        on_time += ok
        recorded += rec
        a = "-" if act is None else f"{act:d}"
        lines.append(f"  {m:4d}  {dec:31s} {c:5s} {a:>4s}  {target:6d}"
                     f"  {'yes' if rec else 'no'}")
    n = len(INJECTS)
    lines += [f"  decisions {n}: one owner {count['one']}, none "
              f"{count['none']}, two {count['two+']}",
              f"  acted within target: {on_time} of {n}; recorded: "
              f"{recorded} of {n}",
              "  every late or missing action sits where the plan named no",
              "  owner or two: the link (each waited for the other), the",
              "  guide at the gate, the village call - and the debrief the",
              "  plan named but no one held"]
    emit("j_injects", lines)
    return dict(n=n, on_time=on_time, recorded=recorded, **count)


# [start: actions]
ACTIONS = [  # (id, action, owner, due day, status at day 90)
    ("A1", "second trained rescuer on each crew", "HSE lead", 60,
     "evidence"),
    ("A2", "night on-call team within 30 min", "site manager", 90, "open"),
    ("A3", "satellite phone in every duty vehicle", "control room", 30,
     "evidence"),
    ("A4", "second ambulance route agreed", "on-call manager", 45,
     "claimed"),
    ("A5", "visitor log reconciled weekly", "gate process", 30, "evidence"),
    ("A6", "guide for services at the gate", "control room", 30,
     "claimed"),
    ("A7", "village told of night traffic", "liaison officer", 14,
     "evidence"),
    ("A8", "debrief and crew support held", "site manager", 14, "evidence"),
    ("A9", "one owner for the link fallback", "control room", 30,
     "evidence"),
    ("A10", "village-call script in the control room", "liaison officer",
     30, "open"),
    ("A11", "fixes tested in the next table-top", "HSE lead", 120, "open"),
]
# [end: actions]


def tracker(day: int = 90) -> dict:
    out = {"evidence": [], "claimed": [], "open": [], "overdue": []}
    for aid, _, _, due, status in ACTIONS:
        key = "overdue" if status == "open" and due < day else status
        out[key].append(aid)
    return out


def actions() -> None:
    t = tracker()
    n = len(ACTIONS)
    closed = len(t["evidence"]) + len(t["claimed"])
    lines = ["lessons learned: the eleven actions at day 90",
             "  id   action                                    due  status"]
    for aid, act, owner, due, status in ACTIONS:
        st = "overdue" if aid in t["overdue"] else {
            "evidence": "closed, evidence", "claimed": "closed, claimed",
            "open": "open"}[status]
        lines.append(f"  {aid:4s} {act:41s} {due:4d}  {st}")
    lines += [f"  reported closed: {closed} of {n} ({closed / n:.0%}); "
              f"closed with evidence: {len(t['evidence'])} of {n} "
              f"({len(t['evidence']) / n:.0%})",
              f"  claimed only: {', '.join(t['claimed'])}; overdue: "
              f"{', '.join(t['overdue'])}",
              "  the next table-top tests the claimed closures first; a",
              "  fix counts when the exercise shows it working, not when",
              "  the tracker says closed"]
    emit("j_actions", lines)


if __name__ == "__main__":
    injects()
    actions()
