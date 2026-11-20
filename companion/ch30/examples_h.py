"""Chapter 30, lesson H: from plate to erected tower - cans cut from
plate and the steel ordered, the section against a bridge on the route,
bolt tightening during erection, the rebar bending schedule of the
foundation, and the verticality of the finished tower.

Run from the project root:   python -m companion.ch30.examples_h
Writes companion/ch30/expected/h_*.txt. Teaching values (A-362).
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import emit


def plates() -> None:
    can_h, plate_w = 2.5, 2.5
    lines = ["cans cut from plate for the four sections (teaching; ch 11 geometry)",
             "  section  cans   plate length m   steel t   ordered t (8 % scrap)"]
    total = 0.0
    for sec, d0, d1, t_mm, length in src.TOWER:
        n = round(length / can_h)
        d_mean = (d0 + d1) / 2
        plate_l = math.pi * d_mean
        mass = n * plate_l * plate_w * t_mm / 1000 * src.STEEL["rho"] / 1000
        total += mass
        lines.append(f"  {sec:7d}  {n:4d}   {plate_l:14.2f}   {mass:7.0f}   {1.08 * mass:21.0f}")
    lines += [f"  shell steel {total:.0f} t (flanges, door frame and internals extra);",
              "  each can is one plate rolled into a ring: the plate's heat",
              "  number goes onto the can and into the data book, so a",
              "  later finding traces to the mill (lab E)"]
    emit("h_plates", lines)


def bridge() -> None:
    clearance, deck = 4.85, 0.30
    lines = ["the base section against a bridge on the delivery route (teaching)",
             f"  bridge clearance {clearance} m; low-loader deck {deck} m above the road",
             "  section  D m   height loaded m   margin m"]
    for sec, d0, d1, t_mm, length in src.TOWER:
        h = d0 + deck
        lines.append(f"  {sec:7d}  {d0:4.2f}   {h:15.2f}   {clearance - h:8.2f}")
    lines += ["  the base section clears by 5 cm: a route survey measures",
              "  every bridge and wire, and a section a few centimetres",
              "  larger takes another road or a split design (ch 31) - the",
              "  tower's base diameter is a logistics decision as well"]
    emit("h_bridge", lines)


def bolting() -> None:
    flanges = [("base (anchor cage)", 160), ("flange 1-2", 120), ("flange 2-3", 108),
               ("flange 3-4", 96), ("tower-top / yaw", 90)]
    minutes, tools = 2.5, 2
    lines = ["bolt tightening during erection (two passes, 2.5 min a bolt a pass,",
             "  two tools working; teaching)",
             "  joint                 bolts   hours"]
    total = 0.0
    for name, n in flanges:
        h = n * 2 * minutes / 60 / tools
        total += h
        lines.append(f"  {name:20s} {n:6d}   {h:5.1f}")
    lines += [f"  total about {total:.0f} hours of tightening for one turbine",
              "  the next section is lifted only after the joint below has",
              "  its first pass at the maker's value: bolting, not the",
              "  crane, often sets the pace of erection (ch 31), and every",
              "  bolt's final value is recorded for the data book"]
    emit("h_bolting", lines)


def rebar() -> None:
    marks = [("B1 bottom radial", 32, 11.0, 320), ("B2 bottom ring", 32, 70.0, 26),
             ("T1 top radial", 25, 10.0, 300), ("P1 pedestal vertical", 32, 4.5, 180),
             ("L1 shear links", 16, 3.0, 1400)]
    lines = ["bending schedule of one 24 m foundation (teaching bar marks)",
             "  mark                    dia mm   length m   number   mass t"]
    total = 0.0
    for mark, d, length, n in marks:
        mass = n * length * math.pi * (d / 1000) ** 2 / 4 * 7850 / 1000
        total += mass
        lines.append(f"  {mark:22s} {d:6d}   {length:8.1f}   {n:6d}   {mass:6.1f}")
    lines += [f"  total {total:.0f} t, about {1000 * total / 893:.0f} kg per m3 of concrete",
              "  the schedule is the cutting and bending factory's order;",
              "  cages are tied to it, checked bar by bar against it (cover",
              "  and spacing, ch 29) and released at a hold point"]
    emit("h_rebar", lines)


def verticality() -> None:
    settle_mm = (12.0, 27.0)            # opposite edges of the base after one year (teaching)
    base = 24.0
    tilt_found = (settle_mm[1] - settle_mm[0]) / base           # mm/m
    flange = 0.6                                                # mm/m from flange flatness
    total = tilt_found + flange
    limit = 3.0                                                 # mm/m (teaching OEM value)
    lines = ["verticality of the erected tower (teaching tolerance 3 mm per m)",
             f"  differential settlement across the 24 m base: {settle_mm[1] - settle_mm[0]:.0f} mm"
             f" -> {tilt_found:.2f} mm/m",
             f"  from flange tolerances: {flange:.2f} mm/m",
             f"  total {total:.2f} mm/m -> {total * src.HUB:.0f} mm at the hub; limit"
             f" {limit * src.HUB:.0f} mm",
             "  within the limit, and the settlement survey continues:",
             "  a foundation that keeps tilting is a finding long before",
             "  it is a failure (lesson K)"]
    emit("h_vertical", lines)


if __name__ == "__main__":
    plates()
    bridge()
    bolting()
    rebar()
    verticality()
