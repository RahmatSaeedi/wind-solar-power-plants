"""Chapter 38, a further round of lessons on design control in numbers:
the review queue (Little's law), return codes and the cycles they cost,
the cost of a change by stage, a design structure matrix with its
iteration loops, the critical path of the deliverables that feed the
transformer order, estimates at completion and the TCPI, requirements
volatility, data-quality rules on an asset register, and defect
containment by design reviews.

Run from the project root:   python -m companion.ch38.examples_s
Writes companion/ch38/expected/s_*.txt and diagrams/data/ch38-*.csv.
Teaching values (A-424): rules of thumb are labelled as such.
"""
from __future__ import annotations

import re

import numpy as np

from companion.ch38 import sources as src  # noqa: F401  (plantp on path)
from companion.ch38.common import csv, emit


# ------------------------------------------------------ review queue
def backlog(arrivals, capacity: float) -> list[float]:
    """Documents waiting for review at the end of each week."""
    q, out = 0.0, []
    for a in arrivals:
        q = max(0.0, q + a - capacity)
        out.append(q)
    return out


def queue() -> dict[str, float]:
    weeks = list(range(30, 53))
    arrivals = [18 + 14 * np.exp(-((w - 42) / 5.0) ** 2) for w in weeks]
    rows, lines = [], ["review queue of the owner's engineer (documents a week)"]
    peaks = {}
    for cap in (25.0, 30.0):
        b = backlog(arrivals, cap)
        peaks[cap] = max(b)
        k = int(np.argmax(b))
        wait = peaks[cap] / cap                 # Little: L = lambda W
        lines.append(f"  capacity {cap:.0f}/week: peak backlog {peaks[cap]:.0f}"
                     f" in week {weeks[k]}, about {wait:.1f} extra weeks")
    for w, a, b1, b2 in zip(weeks, arrivals, backlog(arrivals, 25.0),
                            backlog(arrivals, 30.0)):
        rows.append((w, round(a, 1), round(b1, 1), round(b2, 1)))
    lines += [f"  arrivals peak at {max(arrivals):.0f} a week (week 42);"
              f" total {sum(arrivals):.0f}",
              "  Little's law: documents waiting = arrival rate x time in",
              "  review; when arrivals beat capacity, the wait grows every",
              "  week until the peak passes - the review slot is planned",
              "  from the deliverable schedule, not from the average"]
    csv("ch38-queue.csv", "week,arrivals,cap25,cap30", rows)
    emit("s_queue", lines)
    return peaks


# ------------------------------------------------------- return codes
RETURN = {  # discipline: (share returned with code C, share code B) (A-424)
    "ELE": (0.25, 0.40), "CIV": (0.15, 0.35), "CTL": (0.30, 0.40),
    "MEC": (0.10, 0.30),
}
CYCLE_WEEKS = 3.0                 # two weeks review + one week to revise


def cycles() -> dict[str, float]:
    lines = ["return codes and the review cycles they cost",
             "  disc  code C  submissions  extra weeks"]
    out = {}
    for d, (pc, _) in RETURN.items():
        subs = 1 / (1 - pc)                     # geometric: until not C
        out[d] = subs
        lines.append(f"  {d}   {pc:5.0%}   {subs:10.2f}   "
                     f"{(subs - 1) * CYCLE_WEEKS:10.1f}")
    lines += ["  (code A approved, B approved with comments, C revise and",
              "  resubmit; a C costs a full cycle)",
              "  a 30 % rejection rate adds about 1.3 weeks to every CTL",
              "  drawing on average - and much more to the unlucky ones;",
              "  first-time-right comes from interface data agreed before",
              "  drawing (lesson B), not from faster reviewers"]
    emit("s_cycles", lines)
    return out


# ----------------------------------------------------- cost of change
STAGES = [("concept", 1), ("basic design", 3), ("detailed design", 10),
          ("construction", 30), ("operation", 100)]   # rule of thumb


def change_cost() -> None:
    base = 102 * 0.095 / 10         # C-017 rework 102 h at 95 u/h, k u per x
    lines = ["cost of the same change by stage (a common rule of thumb:",
             "about x3 per stage, not a law)",
             "  stage             multiple   cost of C-017, k u"]
    for name, m in STAGES:
        lines.append(f"  {name:16s} {m:8d}   {base * m:10.1f}")
    lines += ["  C-017 (5.5 -> 5.6 MVA) cost 102 h of rework in detailed",
              f"  design ({base * 10:.1f} k u); the same change after the transformers",
              "  were built would mean new units - the multiplier is the",
              "  reason the baseline is frozen before orders are placed"]
    emit("s_change", lines)


# ---------------------------------------- design structure matrix (DSM)
# [start: dsm]
TASKS = ["site layout", "one-line", "load flow", "short circuit",
         "protection", "cable sizing", "earthing", "transformer spec"]
NEEDS = {  # task: tasks whose output it needs (A-424)
    "one-line": ["site layout"], "load flow": ["one-line"],
    "short circuit": ["one-line", "transformer spec"],
    "protection": ["short circuit", "cable sizing"],
    "cable sizing": ["load flow", "short circuit", "protection"],
    "earthing": ["short circuit", "site layout"],
    "transformer spec": ["load flow", "short circuit"],
}
# [end: dsm]


def loops(nodes, needs) -> list[list[str]]:
    """Strongly connected groups (Tarjan): tasks that need each other."""
    index, low, stack, on, out = {}, {}, [], set(), []
    counter = [0]

    def visit(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in needs.get(v, []):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            out.append(comp)
    for v in nodes:
        if v not in index:
            visit(v)
    return out                       # in dependency order (needs first)


def dsm() -> list[list[str]]:
    groups = loops(TASKS, NEEDS)
    order = [t for g in groups for t in sorted(g, key=TASKS.index)]
    lines = ["design structure matrix: who needs whose output",
             "  order of work (a group in [ ] must iterate):"]
    for g in groups:
        g = sorted(g, key=TASKS.index)
        lines.append("    " + (f"[{', '.join(g)}]" if len(g) > 1 else g[0]))
    big = [g for g in groups if len(g) > 1]
    lines += [f"  iteration groups: {len(big)}; largest has {max(map(len, big))}"
              " tasks",
              "  both loops are physics: the transformer impedance sets the",
              "  fault current, and the fault current sets what the",
              "  transformer must withstand; cable size depends on fault",
              "  current and clearing time, clearing time on the settings,",
              "  settings on the cable. The plan budgets two passes and",
              "  freezes the impedance first to break the first loop"]
    rows = []
    for i, a in enumerate(order, 1):
        for j, b in enumerate(order, 1):
            if b in NEEDS.get(a, []):
                rows.append((i, j))
    csv("ch38-dsm.csv", "row,col", rows)
    emit("s_dsm", lines)
    return groups


# -------------------------------------------- critical path to the order
# [start: cpm]
WORK = {  # deliverable: (weeks, predecessors) (A-424)
    "load flow": (3, []), "short circuit": (2, ["load flow"]),
    "transformer spec": (2, ["load flow", "short circuit"]),
    "earthing study": (4, ["short circuit"]),
    "RFQ issued": (1, ["transformer spec"]),
    "bids evaluated": (6, ["RFQ issued"]),
    "order placed": (2, ["bids evaluated", "earthing study"]),
}
# [end: cpm]


def cpm(work, start: int = 10) -> dict[str, tuple[int, int, int]]:
    """Earliest start, latest start and float of each task (weeks)."""
    es, ef = {}, {}
    for t in work:                                   # listed in order
        d, pre = work[t]
        es[t] = max([ef[p] for p in pre], default=start)
        ef[t] = es[t] + d
    end = max(ef.values())
    ls, lf = {}, {}
    for t in reversed(list(work)):
        succ = [s for s, (_, pre) in work.items() if t in pre]
        lf[t] = min([ls[s] for s in succ], default=end)
        ls[t] = lf[t] - work[t][0]
    return {t: (es[t], ls[t], ls[t] - es[t]) for t in work}


def critical_path() -> dict:
    res = cpm(WORK)
    end = max(es + WORK[t][0] for t, (es, _, _) in res.items())
    lines = ["critical path from load flow to the transformer order",
             "  deliverable        weeks  start  latest  float"]
    rows = []
    for k, (t, (es, ls, fl)) in enumerate(res.items(), 1):
        lines.append(f"  {t:18s} {WORK[t][0]:5d}  {es:5d}  {ls:6d}  {fl:5d}")
        rows.append((k, es, WORK[t][0], fl))
    crit = [t for t, (_, _, fl) in res.items() if fl == 0]
    fl_e = res["earthing study"][2]
    lines += [f"  order placed by week {end}; critical: {len(crit)} of "
              f"{len(res)} tasks",
              f"  the earthing study has float: it can slip {fl_e} weeks",
              "  without moving the order; a week lost on the short-",
              "  circuit study moves the order and the transformers by",
              "  a week (ch 39: delivery 30 weeks after the order)"]
    csv("ch38-cpm.csv", "k,start,weeks,float", rows)
    emit("s_cpm", lines)
    return dict(res=res, end=end)


# ----------------------------------------------- estimate at completion
def eac() -> dict[str, float]:
    bac, pv, ev, ac = 7342.0, 4451.0, 3012.0, 3553.0
    cpi, spi = ev / ac, ev / pv
    out = {"BAC / CPI": bac / cpi,
           "AC + (BAC - EV)": ac + (bac - ev),
           "AC + (BAC - EV) / (CPI x SPI)": ac + (bac - ev) / (cpi * spi)}
    tcpi = (bac - ev) / (bac - ac)
    lines = ["estimates at completion of the engineering (hours)",
             f"  BAC {bac:,.0f}; CPI {cpi:.2f}; SPI {spi:.2f}"]
    for name, v in out.items():
        lines.append(f"  {name:31s} {v:8,.0f}")
    lines += [f"  TCPI to finish on budget: {tcpi:.2f} - every remaining",
              f"  hour would have to earn {tcpi:.2f} hours of work",
              "  the three formulas say: problems are over (AC + rest),",
              "  they continue (BAC/CPI), or late work costs more as it",
              "  is rushed (CPI x SPI); the forecast states its assumption"]
    out["TCPI"] = tcpi
    emit("s_eac", lines)
    return out


# ----------------------------------------------- requirements volatility
CHANGES = [9, 7, 6, 8, 5, 4, 6, 3, 2, 4, 1, 2]   # changes a month (A-424)
N_REQ = 180
FREEZE = 8                                         # month of the freeze


def volatility() -> dict[str, float]:
    rate = [100 * c / N_REQ for c in CHANGES]
    after = sum(CHANGES[FREEZE:])
    lines = ["requirements volatility (180 requirements, 12 months)",
             "  month: " + " ".join(f"{c:2d}" for c in CHANGES),
             f"  first-quarter rate {sum(rate[:3]) / 3:.1f} % a month; "
             f"last quarter {sum(rate[-3:]) / 3:.1f} %",
             f"  changes after the freeze (month {FREEZE}): {after}, each by",
             "  the change procedure with its impact list (lesson D)",
             f"  at the average C-017 rework of 102 h for 13 documents, "
             f"{after} late",
             f"  changes would cost about {after * 102:,} h if each were as"
             " wide",
             "  volatility falling to near zero is the evidence that the",
             "  basis is stable enough to buy against"]
    emit("s_volatility", lines)
    return dict(after=after, first=sum(rate[:3]) / 3, last=sum(rate[-3:]) / 3)


# --------------------------------------------- asset data quality rules
TAG = re.compile(r"^=[A-Z]+[0-9]-[0-9]+(-[A-Z][0-9]+)?$")


def register(n: int = 400, seed: int = 383) -> list[dict]:
    rng = np.random.default_rng(seed)
    rows = []
    for k in range(n):
        blk = f"PVF{1 + k % 3}-{1 + k % 4}"
        rows.append(dict(tag=f"={blk}-Q{k + 1}", parent=f"={blk}",
                         maker="M" + str(k % 5), serial=f"SN{10000 + k}",
                         rating=float(rng.choice([630, 1250, 1600])),
                         unit="A", installed=2028))
    for k in rng.choice(n, 12, replace=False):
        rows[k]["serial"] = None                     # missing attribute
    for k in rng.choice(n, 6, replace=False):
        rows[k]["unit"] = "kA"                       # wrong unit
    for k in rng.choice(n, 5, replace=False):
        rows[k]["tag"] = rows[k]["tag"].replace("=", "")   # bad format
    for k in rng.choice(n, 4, replace=False):
        rows[k]["parent"] = "=PVF9-9"                # parent not in plant
    for a, b in ((10, 11), (200, 201), (300, 301)):  # duplicated tags
        rows[b]["tag"] = rows[a]["tag"]
    return rows


RULES = {
    "tag format": lambda r, ctx: bool(TAG.match(r["tag"])),
    "tag unique": lambda r, ctx: ctx["count"][r["tag"]] == 1,
    "parent exists": lambda r, ctx: r["parent"] in ctx["parents"],
    "serial present": lambda r, ctx: bool(r["serial"]),
    "unit valid": lambda r, ctx: r["unit"] == "A",
}


def data_quality() -> dict[str, float]:
    rows = register()
    count: dict[str, int] = {}
    for r in rows:
        count[r["tag"]] = count.get(r["tag"], 0) + 1
    parents = {f"=PVF{a}-{b}" for a in (1, 2, 3) for b in (1, 2, 3, 4)}
    ctx = dict(count=count, parents=parents)
    lines = [f"data-quality rules on an asset register of {len(rows)} rows"]
    out = {}
    clean = [all(f(r, ctx) for f in RULES.values()) for r in rows]
    for name, f in RULES.items():
        ok = sum(f(r, ctx) for r in rows)
        out[name] = ok / len(rows)
        lines.append(f"  {name:15s} {ok:4d} pass  ({ok / len(rows):6.1%})")
    out["all rules"] = sum(clean) / len(rows)
    lines += [f"  rows passing every rule: {sum(clean)} ({out['all rules']:.1%})",
              "  each rule is simple; together they reject one row in",
              "  twelve. A duplicated tag is the worst: two functions",
              "  answer to one name (ch 23). The register exposes it before",
              "  handover, not an operator during a fault"]
    emit("s_dataq", lines)
    return out


# ----------------------------------------- defect containment in reviews
INJECTED = {"30 %": 40, "60 %": 50, "90 %": 30}   # defects made in each
FIND = {"30 %": 0.5, "60 %": 0.6, "90 %": 0.6, "IFC check": 0.5}


def containment() -> dict[str, float]:
    open_d, found = 0.0, {}
    lines = ["defect containment by design reviews (teaching rates)",
             "  stage       made  found  passed on"]
    for stage in ["30 %", "60 %", "90 %", "IFC check"]:
        open_d += INJECTED.get(stage, 0)
        f = open_d * FIND[stage]
        found[stage] = f
        open_d -= f
        lines.append(f"  {stage:10s} {INJECTED.get(stage, 0):5d}  {f:5.1f}"
                     f"  {open_d:9.1f}")
    total = sum(INJECTED.values())
    lines += [f"  made {total}; reach construction {open_d:.1f} "
              f"({open_d / total:.0%})",
              "  each review finds a share of what is there, never all:",
              "  the escapes are found on site at ten times the cost",
              "  (rule of thumb above); a better checklist at 60 % pays",
              "  more than a longer IFC check"]
    emit("s_contain", lines)
    return dict(escaped=open_d, total=total)


if __name__ == "__main__":
    queue()
    cycles()
    change_cost()
    dsm()
    critical_path()
    eac()
    volatility()
    data_quality()
    containment()
