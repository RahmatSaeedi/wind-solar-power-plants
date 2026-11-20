"""Chapter 25 - seventh round: copper mass against load loss (a check on a
bid), the water the factory's drying removes, the tank under full
vacuum, metering accuracy at low output, the spare parts worth holding,
and where the transformers' annual losses really come from.

Run from the project root:   python -m companion.ch25.examples_u
Writes companion/ch25/expected/u_*.txt. Teaching values (A-326..A-330
extended).
"""
from __future__ import annotations

from companion.ch25 import sources as src
from companion.ch25.common import csv, emit

M = src.MAIN


def copper() -> None:
    rho75, dens = 2.1e-8, 8900.0
    lines = ["copper mass against load loss: P = rho J^2 x volume (a review check)",
             "  current density A/mm2   copper t for 200 kW of I2R   kW per tonne"]
    for j in (2.5, 3.0, 3.5):
        per_m3 = rho75 * (j * 1e6) ** 2
        vol = 200e3 / per_m3
        lines.append(f"  {j:21.1f}   {vol * dens / 1e3:26.1f}   {per_m3 / dens:11.1f}")
    lines += ["  the I2R part of the 250 kW load loss (the rest is eddy and",
              "  stray loss) needs about 9 t of copper at 3 A/mm2: a bid",
              "  that promises low load loss with little copper is checked",
              "  against this before it is believed; more copper (lower J)",
              "  buys lower loss - the B factor of lesson A prices it"]
    emit("u_copper", lines)


def drying() -> None:
    paper_t = 8.0
    lines = ["water removed from the insulation in the factory's drying (teaching):",
             f"  {paper_t:.0f} t of paper and pressboard",
             "  from %   to %   water removed kg"]
    for w0, w1 in ((8.0, 0.5), (8.0, 1.0), (5.0, 0.5)):
        lines.append(f"  {w0:6.1f}   {w1:4.1f}   {paper_t * 1e3 * (w0 - w1) / 100:16.0f}")
    lines += ["  hundreds of kilograms of water come out under heat and",
              "  vacuum over days; the end point is proved by the drying",
              "  record (water extracted per hour falling to the maker's",
              "  limit) - the paper stays dry only if the tank is filled",
              "  and sealed without delay (lesson B, quality gates)"]
    emit("u_drying", lines)


def vacuum() -> None:
    lines = ["the tank under full vacuum (atmospheric pressure outside, teaching):",
             "  wall m x m   force MN   per stiffener (6 stiffeners) kN"]
    for w, h in ((3.0, 4.0), (6.0, 4.0), (6.0, 2.5)):
        f = 101.3e3 * w * h
        lines.append(f"  {w:4.1f} x {h:3.1f}   {f / 1e6:8.2f}   {f / 6 / 1e3:31.0f}")
    lines += ["  a 6 m by 4 m wall carries 2.4 MN when the tank is evacuated",
              "  for oil filling: the stiffeners and the wall thickness are",
              "  designed for it, and the vacuum and pressure tests of the",
              "  tank (purpose: no permanent deformation, no leak) are part",
              "  of the factory record - vacuum work belongs to the maker's",
              "  equipment and procedure"]
    emit("u_vacuum", lines)


def metering() -> None:
    ct = 600.0
    bands = [(0.00, 0.01, 0.02), (0.01, 0.05, 0.06), (0.05, 0.20, 0.17), (0.20, 1.20, 0.75)]
    lines = ["revenue metering at low output: share of the year's energy by CT current",
             f"  (CT {ct:.0f}/1 at the line bay, export up to 437 A; teaching shares)",
             "  current band (x rated)   amps         energy share"]
    for lo, hi, share in bands:
        lines.append(f"  {lo:5.2f} - {hi:4.2f}            {lo * ct:4.0f}-{hi * ct:4.0f} A   {share:12.0%}")
    lines += ["  8 % of the energy passes below 5 % of the CT's rating (PV",
              "  mornings, light wind): a CT class accurate down to 1 % of",
              "  rating (the 'S' classes) keeps that energy measured within",
              "  its limits - the class is set by the grid operator's",
              "  metering rules; this table shows why it matters"]
    emit("u_metering", lines)


def spares() -> None:
    items = [("HV bushing (one)", 25, 26, True), ("LV bushing (one)", 8, 16, True),
             ("OLTC diverter insert", 60, 30, True), ("complete tap changer", 250, 40, True),
             ("gasket set, valves", 5, 8, False), ("cooling fans (two)", 4, 6, False),
             ("radiator section", 15, 8, False), ("gas relay, PRD", 6, 10, True),
             ("winding temperature sensors", 3, 8, False)]
    lines = ["spares for the two main transformers (teaching costs k u, lead weeks):",
             "  item                         cost   lead   stops the unit   hold"]
    held = 0
    for name, cost, lead, stops in items:
        if cost <= 6 or (stops and lead >= 12 and cost <= 100):
            hold = "on site"
            held += cost
        elif stops and lead >= 12:
            hold = "pool"
        else:
            hold = "no"
        lines.append(f"  {name:28s} {cost:5d}   {lead:4d}   {'yes' if stops else 'no':>14s}"
                     f"   {hold}")
    lines += [f"  held on site: {held} k u. Rule: cheap parts, and parts that stop",
              "  the unit and take months, are held; a whole tap changer is",
              "  shared with other plants (pool); a radiator is not held - the",
              "  unit runs derated without it. A bushing failure without a",
              "  spare is half a year out (lesson above); with one, weeks",
              "  (the spares list joins ch 18 and ch 52)"]
    emit("u_spares", lines)


def loss_budget() -> None:
    hours = 8760
    rows = [("main transformers (2)", 2, 35.0, 250.0, 0.128),
            ("PV unit (10)", 10, 4.5, 45.0, 0.20), ("wind unit (12)", 12, 7.0, 50.0, 0.30),
            ("BESS unit (4)", 4, 4.5, 45.0, 0.15)]
    lines = ["the transformers' losses over a year (loss load factor per group):",
             "  group                    no-load MWh   load MWh   total MWh"]
    t0 = t1 = 0.0
    data = []
    for k, (name, n, p0, pk, llf) in enumerate(rows):
        e0 = n * p0 * hours / 1e3
        e1 = n * pk * llf * hours / 1e3
        t0 += e0
        t1 += e1
        data.append((k, f"{e0:.0f}", f"{e1:.0f}"))
        lines.append(f"  {name:24s} {e0:11.0f}   {e1:8.0f}   {e0 + e1:9.0f}")
    csv("ch25-lossyear.csv", "k,noload,load", data)
    main = 2 * 35.0 * hours / 1e3 + 2 * 250.0 * 0.128 * hours / 1e3
    lines += [f"  all {t0 + t1:,.0f} MWh: no-load {t0:,.0f} ({t0 / (t0 + t1):.0%}), load {t1:,.0f}",
              "  the main transformers lose about as much in the cores as in",
              "  the windings; the unit transformers, whose load loss is ten",
              "  times their no-load loss, lose most in the windings - so A",
              "  and B are set per group from its own loss load factor, and",
              f"  the 26 unit transformers lose {(t0 + t1 - main) / main:.1f} times as much as the two",
              "  main ones"]
    emit("u_lossbudget", lines)


if __name__ == "__main__":
    copper()
    drying()
    vacuum()
    metering()
    spares()
    loss_budget()
