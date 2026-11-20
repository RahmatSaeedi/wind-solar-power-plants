"""Chapter 37, lab E (reliability lab): availability and failure-duration
metrics of the 12 turbines from a synthetic event log, computed raw and
after cleaning - missing end times, duplicate events, overlapping
records and two definitions of an outage.

Run from the project root:   python -m companion.ch37.lab_e
Writes companion/ch37/expected/e_*.txt.
Synthetic event log (A-412).
"""
from __future__ import annotations

import numpy as np

from companion.ch37.common import emit
from plantp import performance as pf

YEAR = 8760.0


def event_log(seed: int = 374, parts=None):
    """(turbine, start h, repaired h, restarted h) with planted defects;
    if a list is given as parts, (wait, repair) of each outage go in it."""
    rng = np.random.default_rng(seed)
    ev = []
    for t in range(12):
        s = rng.exponential(1500)
        while s < YEAR - 200:                        # outages one after another
            wait = rng.uniform(2, 30)
            repair = rng.exponential(6)
            check = 0.5
            ev.append([t, s, s + wait + repair, s + wait + repair + check])
            if parts is not None:
                parts.append((wait, repair))
            s = s + wait + repair + check + rng.exponential(1500)
    ev = [[t, round(a, 2), round(b, 2), round(c, 2)] for t, a, b, c in ev]
    log = [list(e) for e in ev]
    log += [list(log[3]), list(log[10]), list(log[17]), list(log[25])]   # duplicates
    for k in (5, 14, 30):
        log[k][3] = None                                                 # no restart time
        log[k][2] = None
    t8, s8, _, e8 = log[8]
    log.append([t8, s8 + 1, e8 + 4, e8 + 4.5])          # same outage logged twice, longer
    return ev, log


# [start: metrics]
def metrics(log, end_col: int):
    by_t = {t: [] for t in range(12)}
    for row in log:
        by_t[row[0]].append((row[1], row[end_col]))
    down = {t: pf.event_hours(v, 0, YEAR) for t, v in by_t.items()}
    n = sum(len(pf.merge_events(v, 0, YEAR)) for v in by_t.values())
    a = 1 - sum(down.values()) / (12 * YEAR)
    return a, n, sum(down.values()) / max(n, 1)
# [end: metrics]


def lab() -> None:
    truth, log = event_log()
    a_t, n_t, mttr_t = metrics(truth, 3)
    raw_n = len(log)
    raw_down = sum((r[3] - r[1]) for r in log if r[3] is not None)
    a_raw = 1 - raw_down / (12 * YEAR)
    a_c, n_c, mttr_c = metrics(log, 3)
    a_rep, _, mttr_rep = metrics(truth, 2)
    lines = ["12 turbines, one year of outage records (synthetic, planted defects)",
             f"  records: {raw_n} ({raw_n - n_t} more than the true {n_t} outages)",
             "  defects planted: 4 duplicates, 1 outage logged twice with",
             "    different times, 3 records without an end time",
             "  metric                              raw sum   cleaned   true",
             f"  fleet time availability            {a_raw * 100:7.2f}   {a_c * 100:7.2f}   {a_t * 100:5.2f}",
             f"  outages counted                    {raw_n:7d}   {n_c:7d}   {n_t:5d}",
             f"  mean downtime per outage, h        {raw_down / raw_n:7.1f}   {mttr_c:7.1f}   {mttr_t:5.1f}",
             "  duplicates add downtime that never happened; records",
             "  without an end vanish from a plain sum and hide their",
             "  downtime; cleaning (sort, drop duplicates, merge, clip)",
             "  removes the first error, but only the maintenance record",
             "  can give back the missing end times - the cleaned result",
             "  is still optimistic by those three outages",
             "  if 'outage' ends at repair instead of restart:",
             f"    availability {a_rep * 100:.2f} %, mean {mttr_rep:.1f} h",
             "  - the definition alone moves the result as much as the",
             "  defects do"]
    emit("e_lab", lines)


def shared_outage() -> None:
    truth, _ = event_log()
    a0, n0, _ = metrics(truth, 3)
    sub = [[t, 4000.0, 4010.0, 4010.0] for t in range(12)]     # 10 h substation outage
    a1, n1, _ = metrics(truth + sub, 3)
    lines = ["a 10 h substation outage stops all 12 turbines at once",
             f"  turbine availability without it {a0 * 100:.2f} %, with it {a1 * 100:.2f} %",
             f"  outages counted: {n0} -> {n1}; one event in the substation",
             "    becomes 12 turbine events",
             "  is it a turbine outage at all? At turbine level it is",
             "  'external' (the turbines were ready); at plant level it",
             "  is one forced outage of the substation. The hierarchy",
             "  records it once, on the substation, and the turbine",
             "  hours point to it - or the turbines' failure rate rises",
             "  by an event none of them had"]
    emit("e_shared", lines)


def repair_sensitivity() -> None:
    parts = []
    truth, _ = event_log(parts=parts)
    w_all = sum(w for w, _ in parts)
    r_all = sum(r for _, r in parts)
    lines = ["what drives the downtime: waiting or repairing (12 turbines)",
             f"  of all outage hours: waiting {w_all:,.0f} h, repair {r_all:,.0f} h,"
             f" checks {0.5 * len(parts):.0f} h",
             "  case                                  availability   mean h"]
    for name, fw, fr in (("as logged", 1.0, 1.0), ("waiting halved", 0.5, 1.0),
                         ("repair halved", 1.0, 0.5), ("both halved", 0.5, 0.5)):
        ev = []
        for (t, s, _, _), (wait, repair) in zip(truth, parts):
            ev.append([t, s, None, s + wait * fw + repair * fr + 0.5])
        a, n, m = metrics(ev, 3)
        lines.append(f"  {name:37s} {a * 100:12.2f}   {m:6.1f}")
    lines += ["  waiting (travel, spares, access) is most of each outage,",
              "  so halving it gains more than halving the repair: the",
              "  record must keep the two apart to show where the cure is",
              "  (lesson D, boundaries)"]
    emit("e_repair", lines)


if __name__ == "__main__":
    lab()
    shared_outage()
    repair_sensitivity()
