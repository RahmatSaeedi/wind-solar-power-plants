"""Chapter 31, lesson A: logistics engineering - the loads and their
vehicles, axle loads against the road limit, the bridges on the route,
the low points, convoy time and the delivery sequence of one turbine.

Run from the project root:   python -m companion.ch31.examples_a
Writes companion/ch31/expected/a_*.txt. Teaching values (A-363, A-364);
the route permit and the transport company's survey decide.
"""
from __future__ import annotations

import math

from companion.ch31 import sources as src
from companion.ch31.common import emit
from plantp import logistics as lg

AXLE_LIMIT = 120.0          # kN per axle on the district road (teaching permit value)


def loads() -> None:
    lines = ["the abnormal loads of one turbine (A-363, teaching)",
             "  component            mass t   L x W x H m           loads"]
    trips = 0
    for name, (m, l_, w, h, n) in src.COMPONENTS.items():
        if n == 0:
            continue
        trips += n
        lines.append(f"  {name:20s} {m:6.0f}   {l_:5.1f} x {w:4.2f} x {h:4.2f}   {n:5d}")
    lines += [f"  {trips} abnormal loads a turbine, {12 * trips} for the farm (plus cranes,",
              "  containers, foundations' cages and the substation): the",
              "  blade sets the turning radius, the base section the",
              "  height, the nacelle the axle and bridge loads"]
    emit("a_loads", lines)


def axles() -> None:
    cases = [("nacelle", 160.0, 30.0, 40.0, 12), ("nacelle", 160.0, 30.0, 42.0, 16),
             ("tower section 1", 124.0, 30.0, 30.0, 10), ("tower section 1", 124.0, 30.0, 34.0, 14),
             ("main transformer", 72.0, 30.0, 25.0, 8)]
    lines = [f"axle loads on modular trailers (teaching permit limit {AXLE_LIMIT:.0f} kN an axle)",
             "  (modular trailer; 5 % of the payload on a four-axle tractor)",
             "  load                trailer axles   tractor kN/axle   trailer kN/axle"]
    for name, pay, tractor, trailer, n in cases:
        t, r = lg.axle_loads(pay, tractor, trailer, n, tractor_axles=4, tractor_share=0.05)
        flag = "" if max(t, r) <= AXLE_LIMIT else "  over"
        lines.append(f"  {name:18s} {n:15d}   {t:15.0f}   {r:15.0f}{flag}")
    lines += ["  the nacelle needs sixteen trailer axles and the base",
              "  section fourteen to stay under the limit: more axles",
              "  spread the load but lengthen and weigh the vehicle -",
              "  which then needs more room in every turn"]
    emit("a_axles", lines)


def bridges() -> None:
    pay, tractor, trailer, n = 160.0, 30.0, 42.0, 16
    total = (pay + tractor + trailer) * 9.81
    group = n * 1.5
    lines = ["the nacelle convoy on the route's bridges (teaching capacities)",
             f"  gross {total / 1e3:.2f} MN spread over a {group:.0f} m axle group",
             "  bridge                  span m   moment / allowed"]
    for name, span, allow in src.BRIDGES:
        r = lg.bridge_moment_ratio(total, group, span, allow)
        lines.append(f"  {name:22s} {span:7.0f}   {r:16.2f}{'  NO' if r > 1 else ''}")
    lines += ["  the moment grows with the span: the two long bridges are",
              "  over their allowed moment while the short canal bridge",
              "  passes - the bridge owner's engineer decides (assessment",
              "  of the real capacity, strengthening, a temporary bridge",
              "  or a diversion), long before the first convoy"]
    emit("a_bridges", lines)


def clearances() -> None:
    deck = 0.30
    lines = ["height on the route (loaded height = deck + load)",
             "  point                       clearance m   nacelle 4.30   section 1 4.50"]
    for name, c in src.LOW_POINTS:
        n_m = c - (deck + 4.30)
        s_m = c - (deck + 4.50)
        lines.append(f"  {name:27s} {c:11.2f}   {n_m:+12.2f}   {s_m:+14.2f}")
    lines += ["  the power line has margin but is live: its owner sets the",
              "  safe distance and may lift or de-energise it; the overpass",
              "  leaves 5 cm for the base section (ch 30) - measured, not",
              "  read from a map, before the first load leaves the port"]
    emit("a_clearance", lines)


def convoy() -> None:
    h = lg.convoy_time([(km, v) for _, km, v in src.ROUTE], stops_h=3.0)
    lines = ["convoy time port to site (teaching speeds and three stops)"]
    for name, km, v in src.ROUTE:
        lines.append(f"  {name:20s} {km:6.0f} km at {v:4.0f} km/h: {km / v:5.1f} h")
    lines += [f"  total {sum(km for _, km, _ in src.ROUTE):.0f} km in about {h:.1f} h with stops",
              "  permits often allow abnormal loads only at night or off",
              "  peak: a trip longer than the night window needs a planned",
              "  parking place - with security and space for the trailer"]
    emit("a_convoy", lines)


def sequence() -> None:
    days = [("crane pad and hardstand accepted (ch 29)", 0),
            ("tower sections 1-4 delivered and stored", 3),
            ("base section set, anchor bolts (ch 30)", 4),
            ("sections 2-4 erected and bolted", 6),
            ("nacelle delivered just in time, lifted", 7),
            ("hub and three blades delivered", 7),
            ("rotor assembled on the ground, lifted", 8),
            ("mechanical completion checks", 10)]
    lines = ["delivery and erection sequence of one turbine (teaching days)"]
    for what, d in days:
        lines.append(f"  day {d:2d}  {what}")
    lines += ["  the nacelle comes just in time: stored on site it needs",
              "  space, a crane to move it and protection; a late nacelle",
              "  leaves a bare tower overnight (vortex shedding, ch 30)"]
    emit("a_sequence", lines)


if __name__ == "__main__":
    loads()
    axles()
    bridges()
    clearances()
    convoy()
    sequence()
