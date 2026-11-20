"""Chapter 31, lesson F: the campaign's economics and resources - moving
the main crane between pads (walk or dismantle), one main crane or two,
storage at the port and demurrage, road closures for the convoys, the
cost of moving one turbine, and the fuel a crane campaign burns.

Run from the project root:   python -m companion.ch31.examples_f
Writes companion/ch31/expected/f_*.txt and diagrams/data/ch31-cranes.csv.
Teaching values (A-363 to A-367); the transport and crane contractors'
offers and the port's tariff set the real ones.
"""
from __future__ import annotations

import math

from companion.ch31 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch31.common import csv, emit


def crane_moves() -> None:
    lines = ["moving the main crawler crane to the next pad (teaching)",
             "  distance m   walk h (0.5 km/h + mats)   dismantle-move-rebuild h"]
    for d in (400, 600, 900, 1500):
        walk = d / 500 + d / 100 * 0.25                 # travel + laying mats (0.25 h per 100 m)
        rebuild = 60.0 + d / 1000 * 2
        lines.append(f"  {d:10d}   {walk:24.1f}   {rebuild:24.0f}")
    lines += ["  walking on a prepared track is far quicker up to about a",
              "  kilometre, but it needs the track built for the crane's",
              "  ground pressure, a gentle slope and no overhead line -",
              "  the layout of ch 14 and the roads of ch 29 decide which",
              "  pads are 'walkable'; the others cost two and a half days"]
    emit("f_moves", lines)


def crane_count() -> None:
    per_turbine, move = 10.0, 3.0
    rate_main, rate_assist = 25.0, 4.0                   # k u a day (teaching)
    mob = 180.0                                          # k u per main crane mobilisation
    rows = []
    lines = ["one main crane or two? (12 turbines, teaching day rates)",
             "  cranes   campaign days   crane cost k u   earlier energy k u   net k u"]
    energy_day = 191_870 / 365 * 50 / 1000 / 12          # k u a turbine-day at 50 u/MWh
    for n in (1, 2):
        days = math.ceil(12 / n) * (per_turbine + move)
        cost = n * (mob + days * (rate_main + rate_assist))
        # turbines finish earlier: average completion moves forward
        avg_finish = days / 2
        gain = (12 * 13 / 2 - avg_finish) * 12 * energy_day if n == 2 else 0.0
        rows.append((n, days, round(cost)))
        lines.append(f"  {n:6d}   {days:13.0f}   {cost:14,.0f}   {gain:18,.0f}   {cost - gain:7,.0f}")
    csv("ch31-cranes.csv", "n,days,cost", rows)
    lines += ["  a second crane costs little more - the same crane-days and",
              "  one more mobilisation - and halves the campaign; it pays",
              "  only if the energy brought forward is real: the grid",
              "  connection date (no export before it), a second erection",
              "  crew and the weather decide - the schedule model (ch 22,",
              "  49), not this table alone"]
    emit("f_cranes", lines)


def port() -> None:
    lines = ["storage at the port and demurrage (teaching tariff)",
             "  free storage 21 days, then 0.5 k u a turbine set a day",
             "  sets on the ship   sets leaving a week   last set waits d   storage k u"]
    for sets, per_week in [(6, 3), (12, 2), (12, 1)]:
        last_wait = ((sets - 1) // per_week) * 7
        total_days = sum(max(0, k // per_week * 7 - 21) for k in range(sets))
        lines.append(f"  {sets:15d}   {per_week:19d}   {last_wait:16d}   {total_days * 0.5:11.1f}")
    lines += ["  the port is cheap while the convoys keep pace with the",
              "  ships; a slow permit, a bridge closed for assessment or",
              "  a long wait for a lifting window backs the queue into",
              "  the port, where each set costs money every day - the",
              "  delivery schedule couples the ship, the road and the hook"]
    emit("f_port", lines)


def road_closures() -> None:
    lines = ["road closures for the abnormal convoys (teaching)",
             "  stretch                   closed per convoy min   convoys   total h"]
    convoys = 108
    for name, mins in [("village bypass (rolling block)", 25), ("district road junctions", 15),
                       ("highway on-ramp", 10)]:
        lines.append(f"  {name:28s} {mins:21d}   {convoys:7d}   {mins * convoys / 60:7.0f}")
    lines += ["  45 hours of closure at the village spread over months: the",
              "  community hears the timetable in advance (night moves,",
              "  school runs avoided), the police escort and the road",
              "  authority set the rules (U-106), and complaints reach the",
              "  grievance mechanism of ch 32"]
    emit("f_closures", lines)


def cost_per_turbine() -> None:
    parts = [("sea freight share (blades, nacelle, tower)", 210.0),
             ("port handling and storage", 35.0),
             ("road transport, 9 abnormal loads", 160.0),
             ("escorts, permits, route works", 55.0),
             ("main crane and assist cranes", 345.0),
             ("receiving, preservation, laydown", 25.0)]
    total = sum(v for _, v in parts)
    lines = ["logistics cost of one turbine (teaching, k u)"]
    for name, v in parts:
        lines.append(f"  {name:42s} {v:6.0f}   {v / total * 100:3.0f} %")
    lines += [f"  total {total:,.0f} k u a turbine",
              "  the crane is the biggest single item: the days it waits",
              "  for wind, for a late delivery or for a pad to be accepted",
              "  are where logistics budgets are lost (lab D)"]
    emit("f_cost", lines)


def fuel() -> None:
    l_day_main, l_day_assist, l_day_gen = 900.0, 250.0, 300.0
    days = 156
    total = days * (l_day_main + l_day_assist + l_day_gen)
    lines = ["diesel for the erection campaign (teaching consumptions)",
             f"  main crane {l_day_main:.0f}, assist crane {l_day_assist:.0f}, generators"
             f" {l_day_gen:.0f} L a day; {days} crane days",
             f"  total {total / 1000:,.0f} m3 of diesel; {total / 30_000:.0f} tanker loads of 30 m3",
             f"  CO2 at 2.7 kg/L: about {total * 2.7 / 1000:,.0f} t",
             "  fuel is a logistics stream of its own: a bunded store on",
             "  site, a delivery schedule, spill kits and a refuelling",
             "  procedure - and an environmental permit item (ch 33)"]
    emit("f_fuel", lines)


if __name__ == "__main__":
    crane_moves()
    crane_count()
    port()
    road_closures()
    cost_per_turbine()
    fuel()
