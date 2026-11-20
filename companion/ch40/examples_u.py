"""Chapter 40, a third round: a time study that turns observed times into
a standard time, kanban cards for the busbar kits, the economic order
quantity of bought frames, material-flow distance of two factory layouts,
the FMEA rows the control plan covers, the risk of accepting a reading
near its limit, how fast an X-bar chart sees a small shift, a supplier
scorecard with open corrective-action requests, the strength of a
thermal-cycling screen, and the zero-failure test that demonstrates an
MTBF.

Run from the project root:   python -m companion.ch40.examples_u
Writes companion/ch40/expected/u_*.txt and diagrams/data/ch40-*.csv.
Teaching values (A-435 to A-439); a fictional integrator.
"""
from __future__ import annotations

import math
from statistics import mean

from companion.ch40 import sources as src
from companion.ch40.common import csv, emit
from companion.ch40.examples_b import CONTROL
from plantp import quality as qa


# ------------------------------------------------------- time study
# [start: timestudy]
OBSERVED = {  # element: observed minutes in 8 cycles (OP40, one joint)
    "fit bolt, washer, nut": [2.1, 2.3, 1.9, 2.2, 2.0, 2.4, 2.1, 2.2],
    "torque with logged wrench": [1.2, 1.1, 1.3, 1.2, 1.4, 1.2, 1.1, 1.3],
    "paint mark": [0.4, 0.5, 0.4, 0.4, 0.5, 0.4, 0.4, 0.5],
}
RATING = 0.95            # the operator worked a little faster than normal
ALLOWANCE = 0.15         # personal, fatigue and delay allowance
# [end: timestudy]


def time_study() -> dict[str, float]:
    normal = sum(mean(v) for v in OBSERVED.values()) * RATING
    std = normal * (1 + ALLOWANCE)
    per_skid = std * 24 / 60
    lines = ["time study of one LV busbar joint (OP40)"]
    for e, v in OBSERVED.items():
        lines.append(f"  {e:28s} mean {mean(v):4.2f} min")
    lines += [f"  normal time: sum x rating {RATING} = {normal:.2f} min",
              f"  standard time: x (1 + {ALLOWANCE}) = {std:.2f} min",
              f"  24 joints: {per_skid:.2f} h of the 14 h OP40",
              "  the joints are a small part of OP40; most of its hours are",
              "  fitting busbars and landing cables - a time study measures",
              "  work as done, the route's hours were an estimate"]
    emit("u_time", lines)
    return dict(normal=normal, std=std, per_skid=per_skid)


# ------------------------------------------------------------- kanban
def kanban() -> dict[str, float]:
    demand_d, lead_d, safety, per_card = 0.625, 3.0, 0.2, 1   # kits a day
    n = math.ceil(demand_d * lead_d * (1 + safety) / per_card)
    lines = ["kanban cards for LV busbar kits (made in the own shop)",
             f"  use {demand_d} kits a day (one a takt of 16 h at 10 h days);"
             f" refill {lead_d:.0f} days",
             f"  cards = ceil(d x L x (1 + safety) / kits a card) = {n}",
             "  a card returned is the order to make a kit; no card, no",
             "  kit - the shop cannot build ahead of the line, and work in",
             "  progress stays where lesson A wants it"]
    emit("u_kanban", lines)
    return dict(cards=n)


# -------------------------------------------------- economic order size
def eoq() -> dict[str, float]:
    demand_y, order_cost, unit, hold = 40.0, 0.6, 11.0, 0.20  # frames, k u
    q = math.sqrt(2 * demand_y * order_cost / (unit * hold))
    lines = ["economic order quantity of bought frames (teaching)",
             f"  {demand_y:.0f} frames a year (all projects); ordering "
             f"{order_cost} k u an order",
             f"  holding {hold:.0%} a year of {unit} k u",
             f"  EOQ = sqrt(2 D S / H) = {q:.1f} frames",
             "  for Plant P the order is ten frames anyway; EOQ matters to",
             "  the integrator's whole year, and a first-article check",
             "  goes with every new order, whatever its size"]
    emit("u_eoq", lines)
    return dict(q=q)


# ---------------------------------------------- layout and flow distance
FLOW = {  # (from, to): moves a skid (crane lifts or trolley moves)
    ("store", "S1"): 1, ("S1", "S2"): 1, ("store", "S2"): 3,
    ("S2", "S3"): 1, ("store", "S3"): 2, ("S3", "S4"): 1,
    ("S4", "S5"): 1, ("S5", "S6"): 1, ("S6", "yard"): 1}
LAYOUTS = {  # position of each area along the hall, metres
    "as built": {"store": 0, "S1": 60, "S2": 20, "S3": 40, "S4": 80,
                 "S5": 100, "S6": 120, "yard": 140},
    "straight line": {"store": 10, "S1": 0, "S2": 20, "S3": 40, "S4": 60,
                      "S5": 80, "S6": 100, "yard": 120},
}


def layout() -> dict[str, float]:
    lines = ["material-flow distance of a skid in two hall layouts"]
    out, rows = {}, []
    for name, pos in LAYOUTS.items():
        d = sum(n * abs(pos[a] - pos[b]) for (a, b), n in FLOW.items())
        out[name] = d
        lines.append(f"  {name:14s} {d:5.0f} m of moves a skid")
    for k, (a, b) in enumerate(FLOW, 1):
        rows.append((k, abs(LAYOUTS["as built"][a] - LAYOUTS["as built"][b]),
                     abs(LAYOUTS["straight line"][a] -
                         LAYOUTS["straight line"][b])))
    csv("ch40-layout.csv", "k,asbuilt,straight", rows)
    lines += [f"  the straight line saves {out['as built'] - out['straight line']:.0f} m"
              " a skid; every metre is a crane or",
              "  trolley move with a skid of 26 t in the air or on wheels -",
              "  fewer moves are also fewer lifts to plan (lesson on EHS)"]
    emit("u_layout", lines)
    return out


# -------------------------------------- FMEA rows covered by the control plan
def coverage() -> dict[str, float]:
    covered_modes = {"LV joint under-torqued", "MV stress cone misplaced",
                     "earth bond missing"}
    needs = [r for r in src.FMEA if r["s"] >= 7]
    gaps = [r["mode"] for r in needs if r["mode"] not in covered_modes]
    lines = [f"control plan against the FMEA: {len(needs)} modes with "
             f"severity 7 or more",
             f"  covered by a control-plan row ({len(CONTROL)} rows): "
             f"{len(needs) - len(gaps)}",
             "  not covered: " + "; ".join(gaps),
             "  the wrong-die crimp needs a die check at the press; the",
             "  handling damage needs the lift plan as a control - each",
             "  gap becomes a row with a method and a reaction"]
    emit("u_coverage", lines)
    return dict(needs=len(needs), gaps=len(gaps))


# ------------------------------------- risk of accepting near the limit
def false_accept() -> dict[float, float]:
    usl, u_std = 20.0, 0.235                    # micro-ohm; from the budget
    lines = ["a reading near the limit: chance the true value is over it",
             f"  limit {usl:.0f} micro-ohm; standard uncertainty {u_std}",
             "  reading   chance the joint is really over 20"]
    out = {}
    for r in (19.2, 19.5, 19.7, 19.9):
        p = 1 - qa.phi((usl - r) / u_std)
        out[r] = p
        lines.append(f"  {r:7.1f}   {p:8.1%}")
    lines += ["  a reading of 19.9 passes the limit but is a coin toss;",
              "  the guard band (accept below 20 - U = 19.5) keeps the",
              "  risk near 2 % - the decision rule is written in the ITP"]
    emit("u_accept", lines)
    return out


# ------------------------------------ how fast the chart sees a shift
def arl() -> dict[float, float]:
    n = 5
    lines = ["average run length of the X-bar chart (subgroups of 5)",
             "  shift in sigma   chance a subgroup signals   ARL"]
    out = {}
    for d in (0.0, 0.5, 1.0, 1.5, 2.0):
        z = d * math.sqrt(n)
        p = (1 - qa.phi(3 - z)) + qa.phi(-3 - z)
        out[d] = 1 / p
        lines.append(f"  {d:14.1f}   {p:25.4f}   {1 / p:5.0f}")
    lines += ["  a 2.6-sigma shift (the drifted wrench) is caught at once;",
              "  a half-sigma drift takes about 33 subgroups - the CUSUM",
              "  of ch 37 sees small drifts sooner"]
    emit("u_arl", lines)
    return out


# ------------------------------------------------ supplier scorecard
SUPPLIERS = {  # supplier: (parts received, rejected, on time share,
    #                      open SCARs, oldest SCAR days)  (A-438)
    "lug maker": (12000, 54, 0.92, 1, 40),
    "panel builder": (40, 3, 0.80, 2, 75),
    "fastener stockist": (30000, 12, 0.98, 0, 0),
    "paint supplier": (900, 2, 0.95, 0, 0),
}


def scorecard() -> dict[str, float]:
    lines = ["supplier scorecard of the integrator (one year)",
             "  supplier            ppm rejected  on time  open SCAR (oldest)"]
    out = {}
    for s, (n, rej, ot, op, age) in SUPPLIERS.items():
        ppm = 1e6 * rej / n
        out[s] = ppm
        lines.append(f"  {s:18s} {ppm:12,.0f}  {ot:7.0%}  {op} ({age} d)")
    lines += ["  the panel builder: 75,000 ppm and a SCAR open 75 days -",
              "  it is also the week-9 signal of the p-chart; ppm compares",
              "  a 40-panel supplier with a 30,000-fastener one only when",
              "  the consequence of a reject is read beside it"]
    emit("u_scorecard", lines)
    return out


# ------------------------------------------- thermal-cycling screen
def screen() -> dict[int, float]:
    k = 0.12                      # share of latent defects found a cycle
    lines = ["strength of a thermal-cycling screen (teaching rate 0.12)",
             "  cycles   share of latent defects found"]
    out = {}
    for n in (2, 5, 10, 20):
        s = 1 - math.exp(-k * n)
        out[n] = s
        lines.append(f"  {n:6d}   {s:8.0%}")
    lines += ["  each cycle finds a share of what is left, so the screen",
              "  flattens; ten cycles find 70 % - the rest is the job of",
              "  the supplier's corrective action, not of more cycles"]
    emit("u_screen", lines)
    return out


# --------------------------------------- zero-failure demonstration test
def demo_test() -> dict[float, float]:
    target = 1000.0
    lines = [f"zero-failure test to demonstrate MTBF {target:,.0f} h",
             "  confidence   test hours without a failure"]
    out = {}
    for c in (0.6, 0.8, 0.9):
        t = -target * math.log(1 - c)
        out[c] = t
        lines.append(f"  {c:10.0%}   {t:14,.0f}")
    lines += ["  90 % needs 2,303 h with no failure at all; one failure",
              "  stretches the test - which is why growth testing (lesson",
              "  E) comes first, and the demonstration only at the end"]
    emit("u_demo", lines)
    return out


if __name__ == "__main__":
    time_study()
    kanban()
    eoq()
    layout()
    coverage()
    false_accept()
    arl()
    scorecard()
    screen()
    demo_test()
