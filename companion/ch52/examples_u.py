"""Chapter 52, round u: reliability-centred task selection, hidden failures
and their test intervals, a spares pool shared by two plants, the
fallback mode as a hidden failure, washing water against the well in a
drought, failures by cost against failures by count, and the value of an
hour of the network owner's response.

Run from the project root:   python -m companion.ch52.examples_u
Writes companion/ch52/expected/u_*.txt. Teaching values (A-530 to A-537).
"""
from __future__ import annotations

from companion.ch15 import sources as s15
from companion.ch52.common import csv, emit
from plantp import ram


# ------------------------------------------------ 1. reliability-centred task selection
MODES = [   # mode, hidden?, detectable before failure (P-F)?, wear-out?, consequence 1-5
    ("gearbox bearing wear", False, True, True, 4),
    ("pitch battery capacity loss", False, True, True, 3),
    ("fire detector failed silent", True, False, False, 5),
    ("protection relay will not trip", True, False, False, 5),
    ("inverter fan failure", False, False, False, 2),
    ("combiner fuse open", False, True, False, 2),
    ("transformer insulation ageing", False, True, True, 5),
    ("diesel will not start", True, False, False, 4)]


def rcm() -> dict:
    out = {}
    for m, hidden, pf, wear, cons in MODES:
        if hidden:
            task = "failure-finding test at an interval"
        elif pf:
            task = "condition monitoring inside the P-F interval"
        elif wear:
            task = "age replacement"
        elif cons <= 2:
            task = "run to failure, spare on the shelf"
        else:
            task = "redesign"
        out[m] = task
    lines = ["task selection, reliability-centred logic (teaching):",
             "  hidden? -> failure-finding; detectable early? -> condition;",
             "  wear-out? -> age replacement; cheap? -> run to failure; else redesign"]
    lines += [f"  {m:30s} {t}" for m, t in out.items()]
    lines += ["  three modes are hidden - nobody sees them fail until the",
              "  moment they are needed: only a test finds them"]
    emit("u_rcm", lines)
    return out


# ------------------------------------------------ 2. hidden failures and test intervals
def hidden(target: float = 0.01) -> dict:
    dev = {"fire detector loop": 0.05, "protection relay trip path": 0.02,
           "diesel start": 0.5}                           # failures a year, hidden
    out = {k: 2 * target / lam * 12 for k, lam in dev.items()}   # months
    csv("ch52-hidden.csv", "months,detector,relay,diesel",
        [(m, round(dev["fire detector loop"] * m / 24, 4),
          round(dev["protection relay trip path"] * m / 24, 4),
          round(dev["diesel start"] * m / 24, 4)) for m in range(1, 25)])
    diesel_wk = out["diesel start"] * 52 / 12
    lines = ["hidden failures: mean unavailability ~ lambda T / 2;",
             f"  test interval for {target:.0%}",
             "  device                       failures/yr   interval (months)"]
    lines += [f"  {k:28s} {dev[k]:8.2f} {v:14.1f}" for k, v in out.items()]
    lines += [f"  the diesel needs a start test every {diesel_wk:.1f} weeks for a 1 %",
              f"  target - the monthly test of ch 51 gives {dev['diesel start'] / 12 / 2:.1%}; the",
              "  relay can wait a year; tests themselves are by qualified",
              "  people and are recorded (the record is the evidence)"]
    emit("u_hidden", lines)
    return out


# ------------------------------------------------ 3. a spares pool for two plants
def pool(target: float = 0.95) -> dict:
    lam = 5.0 / 8760                     # inverter failures an hour, one plant
    lead = 1_440.0
    one = ram.spares_needed(lam, lead, target)
    two = ram.spares_needed(2 * lam, lead, target)
    lines = [f"inverter spares for {target:.0%}: one plant alone needs {one}, two plants",
             f"  sharing one pool need {two} (not {2 * one})",
             f"  the pool saves {2 * one - two} unit(s) - if the plants are close enough",
             "  that the part arrives in hours, and the pool's owner, stock",
             "  record and priority rule are written (ch 25 spare pool)"]
    emit("u_pool", lines)
    return dict(one=one, two=two)


# ------------------------------------------------ 4. the fallback mode as a hidden failure
def fallback(lam_ppc: float = 0.1, p_fb_fail: float = 0.01, test_months: float = 12.0,
             lam_fb: float = 0.05) -> dict:
    q_fb = lam_fb * test_months / 12 / 2                # hidden, tested yearly
    both = lam_ppc * q_fb                               # PPC fails while fallback is dead
    q6 = lam_fb * 6 / 12 / 2
    lines = ["plant controller and its fallback mode (ch 20): the fallback is",
             f"  only used when the controller fails ({lam_ppc} a year)",
             f"  fallback dead and unseen, tested every {test_months:.0f} months: q = {q_fb:.3f}",
             f"  controller failures meeting a dead fallback: {both:.4f} a year",
             f"  tested every 6 months: q = {q6:.3f}, {lam_ppc * q6:.4f} a year",
             "  the fault tree of lesson E used a fixed q for the fallback;",
             "  its real value is set by how often the switch-over is tested"]
    emit("u_fallback", lines)
    return dict(q12=q_fb, q6=q6, both=both)


# ------------------------------------------------ 5. washing water against the well
def wash_water(washes: int = 13, m3_wash: float = 109.2, well_m3_day: float = 40.0,
               drought_share: float = 0.5) -> dict:
    need = washes * m3_wash
    other = 22.0 * 365                                  # camp, offices, fire top-up (teaching)
    normal = well_m3_day * 365
    drought = normal * drought_share
    lines = [f"water a year: {washes} washes x {m3_wash} m3 = {need:,.0f} m3 + other uses "
             f"{other:,.0f} m3",
             f"  well at {well_m3_day:.0f} m3/day: {normal:,.0f} m3; in a drought year at "
             f"{drought_share:.0%}: {drought:,.0f} m3",
             f"  normal year {'covers' if need + other <= normal else 'does not cover'} "
             f"({normal - need - other:+,.0f} m3); drought year "
             f"{'covers' if need + other <= drought else 'does not cover'} "
             f"({drought - need - other:+,.0f} m3)",
             "  in a drought, washes go by measured benefit only (ch 51) or",
             "  to the dry robot - the method choice of lesson G is also a",
             "  water decision"]
    emit("u_water", lines)
    return dict(need=need, normal=normal - need - other, drought=drought - need - other)


# ------------------------------------------------ 6. failures by cost against by count
def cost_pareto() -> dict:
    data = {"FUSE-OPEN": (14, 0.3), "FAN": (11, 0.6), "CNV-IGBT": (9, 14.0),
            "PIT-BAT": (7, 2.2), "HVAC-FLT": (5, 6.5), "GBX-BRG": (2, 85.0)}   # count, k u each
    by_count = sorted(data, key=lambda k: -data[k][0])
    by_cost = sorted(data, key=lambda k: -data[k][0] * data[k][1])
    tot = sum(n * c for n, c in data.values())
    lines = ["corrective failures of the year: count and cost (k u, labour + parts)",
             "  code        count   each   total"]
    lines += [f"  {k:10s} {n:6d} {c:6.1f} {n * c:7.1f}" for k, (n, c) in data.items()]
    lines += [f"  first by count: {by_count[0]}; first by cost: {by_cost[0]} "
              f"({data[by_cost[0]][0] * data[by_cost[0]][1] / tot:.0%} of {tot:,.0f} k u)",
              "  the two Pareto charts point at different work: count tells",
              "  the crew's load, cost (and energy, lesson F) tells where",
              "  improvement pays - both need labour and parts on each order"]
    emit("u_cost", lines)
    return dict(count=by_count[0], cost=by_cost[0], tot=tot)


# ------------------------------------------------ 7. an hour of the network owner's response
def response_value(price: float = 70.0) -> dict:
    poc = s15.plant_year()["poc"]
    mean = float(poc.mean())
    faults = 2.0
    for_hours = [4, 8, 24]
    rows = [(h, faults * h * mean, faults * h * mean * price) for h in for_hours]
    lines = [f"line faults {faults:.0f} a year; each hour of response costs the mean",
             f"  export of {mean:.1f} MW",
             "  response h   MWh a year   u a year"]
    lines += [f"  {h:10d} {m:12.0f} {u:10,.0f}" for h, m, u in rows]
    lines += ["  the service agreement with the network owner is negotiated",
              f"  with this number: a 24-hour response costs {rows[2][2] / rows[0][2]:.0f} times a",
              "  4-hour one - the boundary of lesson H in money"]
    emit("u_respvalue", lines)
    return dict(mean=mean, rows=rows)


# ------------------------------------------------ 8. key-person risk
SKILLS = {   # task family: technicians qualified (of 10)
    "HV switching (authorised person)": 4, "inverter repair (maker-trained)": 2,
    "BESS module change": 1, "protection relay settings": 1, "drone thermography": 3,
    "tracker controller": 2, "fibre splicing": 0, "crane signalling": 5}


def key_person() -> dict:
    single = [k for k, n in SKILLS.items() if n == 1]
    none = [k for k, n in SKILLS.items() if n == 0]
    lines = ["maintenance skills: technicians qualified for each task family (of 10)"]
    lines += [f"  {k:36s} {n:2d}" for k, n in SKILLS.items()]
    lines += [f"  one person only: {len(single)} ({', '.join(single)})",
              f"  nobody: {', '.join(none)} - bought from a contractor (lesson A)",
              "  a single qualified person is a hidden failure of the crew:",
              "  it shows on the night that person is on leave (ch 51 roster)"]
    emit("u_skills", lines)
    return dict(single=len(single), none=len(none))


# ------------------------------------------------ 9. repair time: median, mean and tail
def repair_spread() -> dict:
    import numpy as np
    down = np.array([46, 18, 70, 9, 4, 26, 31, 22], float)     # ch 51 outages, h
    med, mean, p90 = np.median(down), down.mean(), np.percentile(down, 90)
    lines = ["the eight forced outages of ch 51: hours down",
             "  " + " ".join(f"{x:3.0f}" for x in sorted(down)),
             f"  median {med:.0f} h, mean {mean:.1f} h, 90th percentile {p90:.0f} h",
             "  the mean is pulled up by the long waits; an MTTR quoted as a",
             "  mean hides the outages that set the spares and the contract",
             "  - report the median and a percentile with it (lesson E)"]
    emit("u_spread", lines)
    return dict(med=float(med), mean=float(mean), p90=float(p90))


if __name__ == "__main__":
    rcm()
    hidden()
    pool()
    fallback()
    wash_water()
    cost_pareto()
    response_value()
    key_person()
    repair_spread()
