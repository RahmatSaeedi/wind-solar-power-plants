"""Chapter 23 - the floating 110 V DC system: pole voltages to earth with
the insulation monitor's balance resistors, what one earth fault does,
and how a second earth fault can energise a trip coil with its contact
open; and the protection zones read back from the one-line model.

Run from the project root:   python -m companion.ch23.examples_u
Writes companion/ch23/expected/u_*.txt. Teaching values (A-318: DC
system; the coil pick-up fraction is the maker's).
"""
from __future__ import annotations

from collections import defaultdict

from companion.ch23 import sources as src
from companion.ch23.common import emit

V = 110.0


def dc_earth() -> None:
    pickup = 0.6 * V
    cases = [("healthy (balance resistors)", +V / 2, -V / 2),
             ("earth fault on the + pole", 0.0, -V),
             ("earth fault on the - pole", +V, 0.0)]
    lines = ["the floating 110 V control battery: pole voltages to earth",
             "  state                          + pole V   - pole V"]
    lines += [f"  {n:30s} {p:8.0f}   {m:8.0f}" for n, p, m in cases]
    coil = 0.0 - (-V)
    lines += ["  second fault: the wire between an OPEN trip contact and the",
              "  trip coil touches earth while the + pole is already earthed:",
              f"    the coil sees {coil:.0f} V, its pick-up is about {pickup:.0f} V -> the breaker",
              "    trips with no protection operating",
              "  one earth fault on a floating system does nothing but an",
              "  alarm; two together can trip or block a breaker - so the",
              "  insulation monitor alarms on the first, and the first is",
              "  found and cleared before a second can join it (ch 26,",
              "  lab E: a standing alarm nobody sees is no alarm)"]
    emit("u_dcearth", lines)


def zones() -> None:
    g = src.plant()
    by_zone = defaultdict(list)
    for b in g.branches:
        by_zone[b.zone].append(b)
    lines = ["protection zones read back from the one-line model:",
             "  zone          branches  breakers  transformers  cables/lines"]
    units = [z for z in by_zone if z.rsplit("-", 1)[-1].isdigit()]
    for z in sorted(set(by_zone) - set(units)):
        bs = by_zone[z]
        cnt = lambda k: sum(b.kind == k for b in bs)
        lines.append(f"  {z:13s} {len(bs):8d}  {cnt('breaker'):8d}  {cnt('transformer'):12d}"
                     f"  {cnt('cable') + cnt('line'):12d}")
    lines.append(f"  + {len(units)} unit-transformer zones, one transformer each")
    edge = [b.tag for b in g.branches if b.kind == "breaker"
            and g.buses[b.a].zone != g.buses[b.b].zone]
    inside = [b.tag for b in g.branches if b.kind == "breaker" and b.tag not in edge]
    lines += [f"  breakers between buses of two zones: {len(edge)} of"
              f" {sum(b.kind == 'breaker' for b in g.branches)}; inside one zone:"
              f" {', '.join(inside)}",
              "  each such breaker is where two zones must overlap: its CTs",
              "  feed the protection on both sides (ch 26); the one inside a",
              "  zone is the utility's breaker between two utility buses -",
              "  its zones are the utility's to draw",
              "  busbar zones (Z-MVA, Z-MVB) are carried by the buses; the",
              "  coupler is listed under Z-MVA",
              "  the table is the first input of the protection one-line"]
    emit("u_zones", lines)


def ner() -> None:
    u_ph, i, t = 33e3 / 3 ** 0.5, 400.0, 10.0
    r = u_ph / i
    energy = i ** 2 * r * t
    c_steel, dt = 500.0, 760.0 - 40.0        # J/(kg K); allowed rise (teaching)
    mass = energy / (c_steel * dt)
    s_short = u_ph * i
    lines = ["sizing the neutral earthing resistor and its transformer (teaching):",
             f"  R = {u_ph:,.0f} / {i:.0f} = {r:.1f} ohm",
             f"  energy in {t:.0f} s: I^2 R t = {energy / 1e6:.0f} MJ",
             f"  stainless-steel grid, c {c_steel:.0f} J/(kg K), allowed rise {dt:.0f} K:",
             f"    at least {mass:.0f} kg of element (adiabatic: all heat stays in it)",
             f"  earthing transformer: {s_short / 1e6:.1f} MVA for {t:.0f} s (short-time),",
             "    a small continuous rating for the neutral's standing current",
             "  the 10 s rating covers the slowest clearing with breaker",
             "  failure (ch 26: 1.75 s) with margin for a repeat fault",
             "  before the element cools; the makers rate both from the",
             "  specification"]
    emit("u_ner", lines)


if __name__ == "__main__":
    dc_earth()
    zones()
    ner()
