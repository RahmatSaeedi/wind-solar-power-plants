"""Chapter 51, lessons L (community and workforce commitments), M (asset
information and configuration control) and N (emergency and physical-
security operations): the commitments register, local staff in O&M, SCADA
tags against the asset register after changes, work orders without an
asset or a failure code, emergency exercises and the incident trend.

Run from the project root:   python -m companion.ch51.examples_l
Writes companion/ch51/expected/l_*.txt, m_*.txt and n_*.txt.
"""
from __future__ import annotations

from companion.ch51 import sources as src
from companion.ch51.common import emit


def commitments(day: int = 365) -> dict:
    late, open_, done, due_now = [], [], [], []
    for k, (st, due, did) in src.COMMIT.items():
        if st == "ongoing":
            open_.append(k)
        elif did is None and due == day:
            due_now.append(k)
        elif did is None and due < day:
            late.append((k, day - due))
        elif did is not None and did > due:
            late.append((k, did - due))
        elif did is not None:
            done.append(k)
    staff, local = src.OM_STAFF
    lines = [f"commitments register on day {day} of operation"]
    lines += [f"  ongoing: {k}" for k in open_]
    lines += [f"  done on time: {k}" for k in done]
    lines += [f"  late: {k} ({d} days)" for k, d in late]
    lines += [f"  due today: {k}" for k in due_now]
    lines += [f"  O&M staff {staff}, local {local} ({local / staff:.0%} against the 40 % "
              "commitment)",
              f"  the laydown area is still not restored "
              f"{dict(late)['restoration of the laydown area']} days after it was due:",
              "  a construction commitment that passed to operations with",
              "  nobody's name on it; each line has an owner in the",
              "  operator's register, reported to the community (ch 33)"]
    emit("l_commit", lines)
    return dict(late=late, local=local / staff)


def tags() -> list:
    missing = [t for t, ok in src.TAG_CHANGES.items() if not ok]
    lines = ["SCADA tags against the asset register after a year of changes"]
    lines += [f"  {t:18s} {'in the register' if ok else 'NOT in the register'}"
              for t, ok in src.TAG_CHANGES.items()]
    lines += [f"  {len(missing)} tags exist in SCADA and nowhere else: a power stack",
              "  replaced under warranty, a converter swapped on T05, a second",
              "  RTU - each change made the tag; none raised the register",
              "  update: the change procedure lists the register as a step"]
    emit("m_tags", lines)
    return missing


def work_orders() -> dict:
    no_asset = [w for w, a, *_ in src.WORK_ORDERS if not a]
    no_code = [w for w, _, c, _ in src.WORK_ORDERS if not c]
    no_test = [w for w, *_, t in src.WORK_ORDERS if not t]
    n = len(src.WORK_ORDERS)
    lines = [f"{n} corrective work orders closed in a month",
             f"  without an asset ID: {', '.join(no_asset)}",
             f"  without a failure code: {', '.join(no_code)}",
             f"  closed without a test record: {', '.join(no_test)}",
             "  a work order without its asset feeds no reliability",
             "  analysis (ch 37, ch 52); one without a test record is a",
             "  repair nobody proved - the system refuses to close either"]
    emit("m_wo", lines)
    return dict(no_asset=no_asset, no_code=no_code, no_test=no_test)


def exercises() -> dict:
    short = [(k, r - d) for k, (r, d) in src.EXERCISES.items() if d < r]
    inc = sum(a for a, _ in src.INCIDENTS.values())
    nm = sum(b for _, b in src.INCIDENTS.values())
    lines = ["emergency exercises in the first year against the plan"]
    lines += [f"  {k:34s} {d}/{r}" for k, (r, d) in src.EXERCISES.items()]
    lines += [f"  short: {', '.join(f'{k} ({n})' for k, n in short)}",
              f"  incidents {inc}, near misses {nm} in six months; near misses rose",
              f"  from {src.INCIDENTS[1][1]} in the first month to {src.INCIDENTS[6][1]} in the "
              "sixth - a reporting",
              "  culture growing, if each is closed with a lesson; the night",
              "  casualty exercise is the gap carried from ch 50"]
    emit("n_exercises", lines)
    return dict(short=short, inc=inc, nm=nm)


if __name__ == "__main__":
    commitments()
    tags()
    work_orders()
    exercises()
