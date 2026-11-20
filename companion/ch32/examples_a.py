"""Chapter 32, lesson A: the safety management system in numbers - the
teaching risk matrix, controls up the hierarchy and the risk left over,
incident rates with their uncertainty, near misses as a learning source,
and the competency matrix of a crew.

Run from the project root:   python -m companion.ch32.examples_a
Writes companion/ch32/expected/a_*.txt and diagrams/data/ch32-matrix.csv.
Teaching values (A-368); the project's safety management system sets
the real matrix, bands and records.
"""
from __future__ import annotations

from companion.ch32 import sources as src
from companion.ch32.common import csv, emit
from plantp import safety as sf


def matrix() -> None:
    rows = []
    lines = ["the teaching 5 x 5 risk matrix (score = likelihood x severity)",
             "  likelihood \\ severity    1    2    3    4    5"]
    for lk in range(5, 0, -1):
        cells = [sf.risk_score(lk, sv) for sv in range(1, 6)]
        rows += [(lk, sv, sf.risk_score(lk, sv)) for sv in range(1, 6)]
        lines.append(f"  {lk:22d}  " + "  ".join(f"{c:3d}" for c in cells))
    csv("ch32-matrix.csv", "l,s,score", rows)
    lines += ["  bands: up to 4 low, 5-9 medium, 10-16 high, above 16 very",
              "  high (teaching); a matrix ranks risks for attention - it",
              "  does not prove a risk acceptable, and its numbers are",
              "  judgements to be written down with their reasons"]
    emit("a_matrix", lines)


def hierarchy() -> None:
    steps = [("hazard: tool dropped from the nacelle", 3, 5),
             ("reduce: tools tethered, carried in closed bags", 2, 5),
             ("engineer: exclusion zone under the turbine", 1, 5),
             ("administrate: permit names the zone, door watch", 1, 5),
             ("protect: helmets for anyone who must enter", 1, 4)]
    lines = ["controls up the hierarchy for one hazard (teaching scores)",
             "  step                                              L  S  score  band"]
    for name, lk, sv in steps:
        s = sf.risk_score(lk, sv)
        lines.append(f"  {name:49s} {lk}  {sv}  {s:5d}  {sf.risk_band(s)}")
    only_ppe = sf.risk_score(3, 4)
    lines += ["  controls are chosen from the top of the hierarchy down; the",
              "  residual 4 (low) holds only while the tethers, the zone and",
              "  the permit hold every day - helmets alone would have left",
              f"  {only_ppe} ({sf.risk_band(only_ppe)}), with the likelihood untouched"]
    emit("a_hierarchy", lines)


def rates() -> None:
    lines = ["incident rates per 200,000 h with 90 % Poisson intervals (synthetic)",
             "  period          hours      kind          n    rate   interval"]
    his = {}
    for period, d in src.HOURS.items():
        for kind in ("lost_time", "recordable"):
            r, lo, hi = sf.incident_rate(d[kind], d["hours"])
            his[(period.split()[0], kind)] = (r, hi)
            lines.append(f"  {period.split()[0]:13s} {d['hours']:9,.0f}  {kind:12s} {d[kind]:3d}"
                         f"  {r:6.2f}   {lo:5.2f}-{hi:5.2f}")
    hi_op = his[("operation", "lost_time")][1]
    r_con = his[("construction", "lost_time")][0]
    lines += ["  operation's zero lost-time injuries in 52,000 h says little:",
              f"  its interval reaches {hi_op:.1f} per 200,000 h, {hi_op / r_con:.0f} times",
              "  the construction rate - a small workforce needs many years,",
              "  or leading indicators, before its rate means anything"]
    emit("a_rates", lines)


def near_miss() -> None:
    c = src.HOURS["construction (18 months)"]
    ratio = c["near_miss"] / max(c["recordable"], 1)
    cats = [("dropped objects", 38), ("vehicle and plant movements", 41),
            ("electrical isolation found incomplete", 9), ("work at height", 22),
            ("housekeeping, slips and trips", 33), ("heat stress symptoms", 21)]
    lines = ["near misses as a learning source (construction, synthetic)",
             f"  {c['near_miss']} near misses against {c['recordable']} recordable injuries"
             f" ({ratio:.0f} to 1)"]
    for name, n in cats:
        lines.append(f"  {name:40s} {n:4d}")
    lines += ["  the nine incomplete isolations caused no injury, but each",
              "  could have been fatal: a near miss is ranked by what it",
              "  could have done, not by what it did - those nine get a",
              "  full investigation and a fix to the permit system"]
    emit("a_nearmiss", lines)


def competency() -> None:
    tasks = ["work at height and rescue", "electrical isolation (authorised)",
             "lifting supervision", "confined space entry", "first aid"]
    crew = {"technician A": [1, 1, 0, 1, 1], "technician B": [1, 0, 0, 0, 1],
            "technician C": [1, 1, 1, 0, 0], "supervisor": [1, 1, 1, 1, 1]}
    lines = ["competency matrix of a turbine maintenance crew (1 = current)",
             "  task                                 " + "  ".join(n.split()[-1] for n in crew)]
    for k, t in enumerate(tasks):
        lines.append(f"  {t:36s} " + "  ".join(f"{crew[n][k]:1d}" for n in crew))
    lines += ["  every pair is current in height and rescue; an isolation",
              "  needs A, C or the supervisor; a hub entry (confined space)",
              "  needs two current people and only A and the supervisor are;",
              "  a lift needs C or the supervisor - the planner checks the",
              "  matrix, not names, and the gaps go into the training plan"]
    emit("a_competency", lines)


# [start: permits]
PERMITS = [  # (id, kind, area, isolation points)
    ("P-101", "electrical isolation", "WS2 feeder", {"Q-WS2", "T03-Q1"}),
    ("P-102", "work at height", "T03 nacelle", {"T03-Q1"}),
    ("P-103", "lifting", "T03 pad", set()),
    ("P-104", "hot work", "T03 tower base", set()),
    ("P-105", "confined space", "T03 hub", {"T03-Q1"}),
]
# [end: permits]


def permits() -> None:
    lines = ["permits open on one day at T03 and the checks between them",
             "  id     kind                   area              isolation points"]
    for pid, kind, area, iso in PERMITS:
        lines.append(f"  {pid}  {kind:21s}  {area:16s}  {', '.join(sorted(iso)) or '-'}")
    shared = {}
    for pid, _, _, iso in PERMITS:
        for q in iso:
            shared.setdefault(q, []).append(pid)
    lines.append("  isolation points shared by several permits:")
    for q, ps in sorted(shared.items()):
        if len(ps) > 1:
            lines.append(f"    {q}: {', '.join(ps)} - de-isolate only after all close")
    lines += ["  simultaneous operations: the lift (P-103) over the tower",
              "  base puts the hot work (P-104) and anyone at the door under",
              "  a suspended load - the permit office sees both, sequences",
              "  them, and names who coordinates; a permit is a",
              "  conversation about one job among others, not a form"]
    emit("a_permits", lines)


def contractors() -> None:
    crit = [("safety record (rates, fatalities)", 0.25),
            ("safety management system", 0.20),
            ("competence and training records", 0.20),
            ("plant and equipment inspection", 0.15),
            ("subcontractor control", 0.10),
            ("welfare and labour practices", 0.10)]
    bidders = {"C1": [4, 4, 3, 4, 3, 4], "C2": [5, 5, 2, 5, 2, 4],
               "C3": [3, 4, 4, 4, 4, 3]}
    lines = ["contractor prequalification (scores 1-5, teaching weights)",
             "  criterion                            weight   C1  C2  C3"]
    for k, (c, w) in enumerate(crit):
        lines.append(f"  {c:36s} {w:6.2f}   " +
                     "  ".join(f"{bidders[b][k]:2d}" for b in bidders))
    tot = {b: sum(w * s for (_, w), s in zip(crit, sc)) for b, sc in bidders.items()}
    low = {b: min(sc) for b, sc in bidders.items()}
    lines.append("  weighted " + "   ".join(f"{b} {t:.2f}" for b, t in tot.items()))
    lines += ["  C2 has the best weighted score but 2 on competence and on",
              "  subcontractor control: a minimum of 3 on every line",
              f"  (lowest scores {', '.join(f'{b} {v}' for b, v in low.items())}) qualifies",
              "  C1 and C3 only - a weighted sum alone would hide the gap"]
    emit("a_contractors", lines)


if __name__ == "__main__":
    matrix()
    hierarchy()
    rates()
    near_miss()
    competency()
    permits()
    contractors()
