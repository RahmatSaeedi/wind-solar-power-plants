"""Chapter 52, lesson A: maintenance strategy - workload against the crew,
a strategy for each asset class from consequence and failure pattern,
inherent / achieved / operational availability per class, prioritising
work requests, in-house or contractor, and spares by Poisson.

Run from the project root:   python -m companion.ch52.examples_a
Writes companion/ch52/expected/a_*.txt. Teaching values (A-530).
"""
from __future__ import annotations

from companion.ch52 import sources as src
from companion.ch52.common import emit
from plantp import ram


# ------------------------------------------------ 1. workload against the crew
def workload() -> dict:
    pm = sum(units * hours * 12 / months for _, _, months, hours, units, _ in src.PM_TASKS)
    cm = sum(n * lam * mttr for n, lam, mttr, *_ in src.CLASSES.values())
    w = src.WORK_HOURS
    cap = w["technicians"] * w["hours_each"] * (1 - w["overhead"])
    lines = ["maintenance work of a year against the crew (hands-on hours)",
             f"  preventive (task list): {pm:,.0f} h; corrective (rate x MTTR): {cm:,.0f} h",
             f"  crew: {w['technicians']} x {w['hours_each']:,} h x (1 - {w['overhead']:.2f} "
             f"travel, permits, records) = {cap:,.0f} h",
             f"  load {(pm + cm) / cap:.0%} of the crew: "
             + ("it fits, with the rest for improvement work" if pm + cm <= cap else
                "it does not fit - contract out or cut tasks by value"),
             "  the turbine services are bought from the maker (ch 39 service",
             "  agreement) and are not in the crew's hours"]
    emit("a_workload", lines)
    return dict(pm=pm, cm=cm, cap=cap, load=(pm + cm) / cap)


# ------------------------------------------------ 2. strategy by class
def strategy() -> dict:
    out = {}
    for k, (n, lam, mttr, delay, pmh, cons, mw) in src.CLASSES.items():
        if lam == 0:
            continue
        if cons >= 4:
            s = "condition-based + planned overhaul"
        elif lam * n >= 5 and cons <= 2:
            s = "run to failure, spares on the shelf"
        elif delay > 5 * mttr:
            s = "preventive + critical spare"
        else:
            s = "preventive (time-based)"
        out[k] = s
    lines = ["a strategy for each class from consequence and failures a year (teaching rule)"]
    lines += [f"  {k:30s} {v}" for k, v in out.items()]
    lines += ["  consequence 4-5: watch the condition and plan the overhaul;",
              "  frequent, cheap failures: let them fail, keep the part; long",
              "  waits for parts: buy the spare - the rule is a start, each",
              "  line is then checked against the class's failure pattern"]
    emit("a_strategy", lines)
    return out


# ------------------------------------------------ 3. three availabilities
def availabilities() -> dict:
    out = {}
    for k, (n, lam, mttr, delay, pmh, cons, mw) in src.CLASSES.items():
        if lam == 0:
            continue
        mtbf = src.YEAR_H / lam
        ai = ram.a_inherent(mtbf, mttr)
        aa = 1 - (lam * mttr + pmh) / src.YEAR_H
        ao = 1 - (lam * (mttr + delay) + pmh) / src.YEAR_H
        out[k] = (ai, aa, ao)
    lines = ["availability of one unit of each class: inherent (repair only), achieved",
             "  (+ preventive work), operational (+ waiting for parts and people)",
             "  class                           inherent  achieved  operational"]
    lines += [f"  {k:30s} {a:9.4f} {b:9.4f} {c:12.4f}" for k, (a, b, c) in out.items()]
    worst = min(out, key=lambda k: out[k][2])
    lines += [f"  lowest operational: {worst}; the gap between achieved and",
              "  operational is waiting - the part of availability that",
              "  spares, access and permits decide (ch 51 round s: 61 %)"]
    emit("a_avail", lines)
    return out


# ------------------------------------------------ 4. prioritising requests
REQUESTS = [   # request, consequence 1-5, urgency 1-5 (how fast it gets worse)
    ("T03 converter trips on dips", 4, 4), ("PV fence gap near the road", 3, 3),
    ("SST fan alarm (inhibited 76 days)", 3, 4), ("road grading after rain", 2, 2),
    ("inverter fan noisy PVF2-3", 2, 3), ("BESS-A container 2 HVAC fault", 4, 5),
    ("string fuses open PVF2-3 CB14", 2, 1), ("office air-conditioning", 1, 2)]


def priorities() -> list:
    rank = sorted(REQUESTS, key=lambda r: (-r[1] * r[2], -r[1]))
    lines = ["work requests ranked by consequence x urgency (ties by consequence)"]
    lines += [f"  {k + 1}. {r:36s} {c} x {u} = {c * u:2d}" for k, (r, c, u) in enumerate(rank)]
    lines += ["  the battery HVAC fault and the converter come first; the",
              "  open string fuse ranks low on consequence - but lesson D",
              "  shows what one open fuse can hide, so 'low' still gets a",
              "  date, not a place at the end of the queue"]
    emit("a_priority", lines)
    return [r for r, *_ in rank]


# ------------------------------------------------ 5. in-house or contractor
def make_or_buy(hours: float = 1_200.0) -> dict:
    inhouse = dict(rate=45.0, fixed=38_000.0, response_h=2.0)     # u/h, u/yr tools+training
    contract = dict(rate=85.0, fixed=0.0, response_h=24.0)
    c_in = inhouse["fixed"] + inhouse["rate"] * hours
    c_co = contract["fixed"] + contract["rate"] * hours
    breakeven = inhouse["fixed"] / (contract["rate"] - inhouse["rate"])
    lines = [f"HV switching and testing work: {hours:,.0f} h a year (teaching rates)",
             f"  in-house {c_in:,.0f} u (response {inhouse['response_h']:.0f} h); contractor "
             f"{c_co:,.0f} u (response {contract['response_h']:.0f} h)",
             f"  break-even at {breakeven:,.0f} h a year: in-house is cheaper above it",
             "  money is half the question: a 24-hour response on a trip of",
             "  a feeder costs energy every time - the price of that energy",
             "  goes into the comparison too (lesson F)"]
    emit("a_makebuy", lines)
    return dict(c_in=c_in, c_co=c_co, be=breakeven)


# ------------------------------------------------ 6. spares by Poisson
def spares(target: float = 0.90) -> dict:
    lead = {"PV inverter": 1_440.0, "BESS PCS": 2_160.0, "PV unit transformer": 4_380.0,
            "main transformer": 8_760.0}
    out = {}
    for k, lt in lead.items():
        n, lam, *_ = src.CLASSES[k]
        rate = n * lam / src.YEAR_H
        out[k] = (rate * lt, ram.spares_needed(rate, lt, target))
    lines = [f"spares to cover the lead time with {target:.0%} confidence (Poisson demand)",
             "  class                 demand in lead time   spares"]
    lines += [f"  {k:22s} {m:17.2f} {s:10d}" for k, (m, s) in out.items()]
    lines += ["  the unit and main transformers need none at 90 %, while the",
              "  strategy rule above asks for a critical unit-transformer",
              "  spare: one failure without a spare costs months of a block",
              "  (or of half the export, lesson F) - a rule on confidence alone",
              "  misses the consequence, so the big spares are decided on",
              "  expected loss, not on Poisson"]
    emit("a_spares", lines)
    return out


if __name__ == "__main__":
    workload()
    strategy()
    availabilities()
    priorities()
    make_or_buy()
    spares()
