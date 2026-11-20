"""Chapter 49, lesson D (work-package lab, the chapter's worked example):
sequence the installation of PV block =PVF1-3 with its prerequisites,
crews and hold points; find what drives the finish; list the inspection
records each package leaves; assemble the turnover package.

Run from the project root:   python -m companion.ch49.lab_d
Writes companion/ch49/expected/d_*.txt and diagrams/data/ch49-gantt.csv.
"""
from __future__ import annotations

from companion.ch49 import examples_c as ec
from companion.ch49 import sources as src
from companion.ch49.common import csv, emit
from plantp import appraisal
from plantp import construction as con


def tasks() -> dict:
    return {k: (d, pre, crew, hold) for k, (d, pre, crew, hold, _) in src.PACKAGES.items()}


# [start: drivers]
def drivers(plan: dict) -> list:
    """Walk back from the last package: each step names what held its
    start - a predecessor's release, or its crew being busy."""
    t = max(plan, key=lambda k: plan[k][2])
    chain = []
    while t:
        start = plan[t][0]
        pre = src.PACKAGES[t][1]
        rel = {p: plan[p][2] for p in pre}
        by = max(rel, key=rel.get) if rel else None
        if by is not None and abs(rel[by] - start) < 1e-9:
            chain.append((t, f"waits for {by}"))
            t = by
        else:
            why = "waits for its crew" if start > 0 else "starts the block"
            chain.append((t, why))
            crew = src.PACKAGES[t][2]
            prior = [k for k, v in plan.items()
                     if src.PACKAGES[k][2] == crew
                     and abs(v[1] - start) < 1e-9]
            t = prior[0] if prior and start > 0 else None
    return chain
# [end: drivers]


def schedule() -> dict:
    plan = con.serial_schedule(tasks(), src.CREWS, rule="earliest")
    prio = con.serial_schedule(tasks(), src.CREWS, rule="priority")
    free, crit, _ = appraisal.critical_path({k: (d + h, pre) for k, (d, pre, _, h)
                                             in tasks().items()})
    two = dict(tasks())
    d, pre, crew, h = two["WP10 modules"]
    two["WP10 modules"] = (5, pre, crew, h)            # a second module crew
    end2 = max(v[2] for v in con.serial_schedule(two, src.CREWS).values())
    end = max(v[2] for v in plan.values())
    end_p = max(v[2] for v in prio.values())
    rows = sorted(plan.items(), key=lambda kv: kv[1][0])
    csv("ch49-gantt.csv", "k,label,start,dur,hold",
        [(i + 1, k.split()[0], s, f - s, r - f) for i, (k, (s, f, r)) in enumerate(rows)])
    lines = ["block =PVF1-3: work packages with one crew of each kind (days),",
             "  each step booking the ready package that can start first",
             "  package                 crew        start  finish  hold  released"]
    for k, (s, f, r) in rows:
        lines.append(f"  {k:23s} {src.PACKAGES[k][2]:10s} {s:6.0f}  {f:6.0f}  "
                     f"{r - f:4.0f}  {r:8.0f}")
    idle = prio["WP06 cables in trench"][0] - plan["WP06 cables in trench"][0]
    lines += [f"  walkdown signed on day {end:.0f}; the logic alone allows {free:.0f}",
              f"  booking by longest path instead: day {end_p:.0f} - the trench cables",
              f"  started {idle:.0f} days later, behind the strings, and held the backfill",
              f"  a second module crew (WP10 in 5 days): day {end2:.0f}"]
    emit("d_schedule", lines)
    ch = drivers(plan)
    lines = ["what drives the finish, walking back from the last package"]
    lines += [f"  {t:23s} {why}" for t, why in ch]
    held = sum(src.PACKAGES[t][3] for t, _ in ch)
    lines += ["  the spine is piling, tables, modules, strings and DC",
              "  terminations: the module crew is the first lever; the hold",
              f"  points on the spine hold it {held} of the {end:.0f} days - an",
              "  inspector booked ahead is the second lever"]
    emit("d_drivers", lines)
    return dict(plan=plan, end=end, end_p=end_p, end2=end2, free=free, chain=ch,
                crit=crit)


def holds() -> list:
    rows = [(k, h, rec) for k, (_, _, _, h, rec) in src.PACKAGES.items()]
    lines = ["records each package leaves (hold points stop the next package)",
             "  package                 hold d  record"]
    lines += [f"  {k:23s} {h:6d}  {rec}" for k, h, rec in rows]
    n = sum(1 for _, h, rec in rows if "(hold)" in rec)
    lines += [f"  {n} hold points: each is released by a named inspector on",
              "  the record itself; a witness point is notified and may be",
              "  waived, a hold point may not (ch 40, ch 47)"]
    emit("d_holds", lines)
    return rows


def package() -> dict:
    r = ec.mc_ready()
    contents = [
        ("subsystem boundary drawing (marked-up one-line, layout)", True),
        ("A check sheets for every item", all(c[1] == 1.0 for c in r["comp"].values())),
        ("hold-point releases of WP02-WP14", True),
        ("installation records: posts, torque, as-laid, terminations, earthing", False),
        ("punch list with category, owner and date", True),
        ("asset records at installation stage", False),
        ("as-built red-lines", True),
        ("preservation records of stored items", False),
        ("permits and isolations in force, energisation status", True),
    ]
    ok = sum(v for _, v in contents)
    lines = ["turnover package of block =PVF1-3 (construction to commissioning)"]
    lines += [f"  [{'x' if v else ' '}] {c}" for c, v in contents]
    lines += [f"  {ok} of {len(contents)} parts complete: the missing ones are the",
              "  records of lessons B and K - the package can go subsystem by",
              "  subsystem (MV and inverter now), with what is missing named"]
    emit("d_package", lines)
    return dict(ok=ok, total=len(contents))


if __name__ == "__main__":
    schedule()
    holds()
    package()
