"""Chapter 42, a fifth round on the nacelle and its integration: cable
twist counted from a data-pack year of yaw, sun on the nacelle cover,
what the service crane can lift, where the converter and transformer
sit (cable losses down the tower), and bolt re-tension sampling.

Run from the project root:   python -m companion.ch42.examples_v
Writes companion/ch42/expected/v_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-454, A-457).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch42 import sources as src
from companion.ch42.common import csv, emit
from plantp import datapack


# ------------------------------------------------ cable twist
def twist(deadband: float = 8.0, limit_turns: float = 3.0):
    h = datapack.load_hourly()
    wd = h["wd_100m_deg"].to_numpy()
    yaw, total, untwists, trace = float(wd[0]), 0.0, 0, []
    for d in wd[1:]:
        err = (d - yaw + 540) % 360 - 180
        if abs(err) > deadband:
            yaw = (yaw + err) % 360
            total += err
            if abs(total) > limit_turns * 360:
                untwists += 1
                total = 0.0
        trace.append(total / 360)
    csv("ch42-twist.csv", "day,turns",
        [(round(k / 24, 2), round(t, 3)) for k, t in enumerate(trace) if k % 24 == 0])
    lines = [f"cable twist from the data-pack year of wind direction "
             f"(yaw deadband {deadband:.0f} deg)",
             f"  untwist at +-{limit_turns:.0f} turns: {untwists} untwist(s) a year",
             f"  largest twist in the year {max(abs(t) for t in trace):.1f} turns; "
             f"at the year's end {total / 360:+.1f}",
             "  this site's winds turn back and forth more than round: the",
             "  limit is approached, not passed, in a typical year",
             "  the cable loop in the tower takes a few turns; the",
             "  controller unwinds when the count reaches the limit -",
             "  the loop's length, clamps and drip loop are installation",
             "  hold points, and the twist count is a monitored signal"]
    emit("v_twist", lines)
    return dict(untwists=untwists)


# ------------------------------------------------ sun on the cover
def cover(area_m2: float = 120.0, g: float = 900.0,
          flow_kg_s: float = 6.0) -> dict[str, float]:
    out = {}
    lines = [f"sun on the nacelle cover ({area_m2:.0f} m2 facing the sky, "
             f"{g:.0f} W/m2, teaching)",
             f"  ventilation {flow_kg_s:.0f} kg/s of air through the nacelle",
             "  cover colour   absorbed   heat into nacelle kW   air rise K"]
    for name, a, into in (("white", 0.25, 0.25), ("grey", 0.60, 0.25)):
        q = area_m2 * g * a * into / 1000
        rise = q * 1000 / (flow_kg_s * 1005)
        out[name] = rise
        lines.append(f"  {name:12s}   {a:8.0%}   {q:20.1f}   {rise:10.1f}")
    lines += ["  a few kelvin more nacelle air come straight off the",
              "  cooling margin on the hottest hours (lesson C): the",
              "  cover's colour is a thermal choice as much as a look"]
    emit("v_cover", lines)
    return out


# ------------------------------------------------ service crane
def crane(capacity_t: float = 10.0) -> dict[str, list[str]]:
    parts = [(r[2], r[3]) for r in src.TREE if r[1] == "NAC"]
    parts += [("pitch drive", 0.8), ("yaw drive", 0.6), ("cooling pump", 0.3)]
    inside = [p for p, m in parts if m <= capacity_t]
    outside = [p for p, m in parts if m > capacity_t]
    lines = [f"nacelle service crane of {capacity_t:.0f} t (teaching)",
             "  liftable inside: " + ", ".join(inside),
             "  need an external crane:"]
    lines += [f"    {p} ({m:.0f} t)" for p, m in parts if m > capacity_t]
    lines += [
             "  a part that the service crane can lift is a day's job; one",
             "  that needs a main crane is a campaign (lesson A): splitting",
             "  a generator into modules or a gearbox into stages is",
             "  design for maintainability, decided at the drawing board"]
    emit("v_crane", lines)
    return dict(inside=inside, outside=outside)


# ------------------------------------------------ converter placement
def placement(p_kw: float = 5000.0, length_m: float = 110.0, pf: float = 0.95):
    out = {}
    lines = [f"cable from nacelle to tower base, {length_m:.0f} m, at rated "
             "(teaching cables)",
             "  what runs down                  voltage V   current A   copper mm2"
             "   loss kW"]
    for name, v, area in (("690 V from the converter", 690.0, 9 * 240.0),
                          ("33 kV from a nacelle transformer", 33000.0, 95.0)):
        i = p_kw * 1e3 / (math.sqrt(3) * v * pf)
        r = 0.0225e-6 * length_m / (area * 1e-6)
        loss = 3 * i * i * r / 1e3
        out[name] = loss
        lines.append(f"  {name:32s} {v:6.0f}   {i:9.0f}   {area:10.0f}   "
                     f"{loss:7.1f}")
    trf = next(r[3] for r in src.TREE if r[0] == "TRF")
    lines += ["  low voltage needs nine parallel cables and still loses more;",
              f"  a nacelle transformer saves copper and loss but lifts {trf:.0f} t",
              "  to the top and adds a medium-voltage fire and access question",
              "  - Plant P's turbines keep it at the tower base (D-029, dry",
              "  type, ch 25); the split is a design choice the plant inherits"]
    emit("v_place", lines)
    return out


# ------------------------------------------------ bolt re-tension sampling
def retension(n_bolts: int = 450, loose: int = 9, share: float = 0.10):
    n = int(n_bolts * share)
    p_miss = math.comb(n_bolts - loose, n) / math.comb(n_bolts, n)
    lines = [f"tower flange bolts: {n_bolts} a turbine, {loose} loose "
             "(teaching)",
             f"  a yearly check of {share:.0%} ({n} bolts) finds at least one: "
             f"{1 - p_miss:.0%}",
             "  a sample tells whether looseness exists, not which bolts:",
             "  one loose bolt found opens a full check of that flange;",
             "  bolts are marked so a turned nut shows at a glance - a",
             "  cheap aid that makes every visit a 100 % visual check"]
    emit("v_retension", lines)
    return dict(found=1 - p_miss)


if __name__ == "__main__":
    twist()
    cover()
    crane()
    placement()
    retension()
