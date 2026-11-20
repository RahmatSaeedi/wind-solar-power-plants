"""Chapter 32, lesson P: more on fire - how fast smoke fills a room, how
many portable extinguishers a building needs by travel distance, the
radiant heat between two containers (a screen only), and the flame of a
grass fire and the width of a firebreak.

Run from the project root:   python -m companion.ch32.examples_p
Writes companion/ch32/expected/p_*.txt and diagrams/data/ch32-smoke.csv.
Teaching values (A-369); spacing, detection and protection follow the
fire strategy, the product tests and the authority (U-105, U-110).
"""
from __future__ import annotations

import math

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit
from plantp import safety as sf


def smoke_fill() -> None:
    area, height = 150.0, 4.0                         # control room m2, ceiling m
    rho = 1.1
    rows = []
    lines = ["how fast smoke fills a room (control room 150 m2, 4 m high; teaching)",
             "  plume entrainment m = 0.071 Q^(1/3) z^(5/3) kg/s (Q convective kW)",
             "  fire kW   time for the layer to fall to 2 m"]
    for q in (100, 300, 1000):
        z, t, dt = height, 0.0, 1.0
        while z > 2.0:
            m = 0.071 * (0.7 * q) ** (1 / 3) * z ** (5 / 3)
            z -= m / (rho * area) * dt
            t += dt
            if q == 300:
                rows.append((t, round(z, 3)))
        lines.append(f"  {q:7d}   {t / 60:5.1f} min")
    csv("ch32-smoke.csv", "t,z", rows[::10])
    lines += ["  a 300 kW panel fire brings the smoke to head height in",
              "  a little over two minutes - before most people would",
              "  think of leaving: early detection (lesson C) and two",
              "  short exits are the defence, not a fast walk"]
    emit("p_smoke", lines)


def fire_watch(n: int = 20_000, seed: int = 32) -> None:
    import numpy as np
    rng = np.random.default_rng(seed)
    delay = rng.lognormal(math.log(25), 0.9, n)       # minutes until a smoulder shows (teaching)
    lines = ["how long to watch after hot work (smouldering delay, teaching)",
             "  delay of a smouldering ignition: lognormal, median 25 min",
             "  watch after the work min   share of such fires seen"]
    for w in (30, 60, 120, 240):
        lines.append(f"  {w:24d}   {np.mean(delay <= w) * 100:23.0f} %")
    lines += ["  a short watch misses many slow fires: the hot-work permit",
              "  sets a watch during the work and for a period after it,",
              "  and a final check later - the times come from the",
              "  site's procedure and the insurer, not from this curve"]
    emit("p_watch", lines)


def container_exposure() -> None:
    q = 4000.0                                        # kW, placeholder container fire
    lines = ["radiant heat from one battery container to the next (screen only)",
             f"  PLACEHOLDER heat release {q / 1000:.0f} MW, radiant 0.35 (point source)",
             "  gap m   flux kW/m2"]
    for r in (1.5, 3.0, 6.0, 10.0):
        lines.append(f"  {r:5.1f}   {sf.heat_flux_point(q, 0.35, r + 1.5):10.1f}")
    lines += ["  at a close gap the point source is useless (the flame is",
              "  bigger than the gap): spacing or barriers between",
              "  containers come from the product's large-scale fire test",
              "  and the authority (ch 19, UL 9540A), never from a screen",
              "  like this one, which only shows why the gap matters"]
    emit("p_exposure", lines)


def firebreak() -> None:
    h = 18000.0                                       # kJ/kg, heat of combustion of dry grass
    lines = ["grass fire: Byram's intensity and flame length (teaching)",
             "  I = H w r (kW/m); flame length L = 0.0775 I^0.46 (m)",
             "  fuel kg/m2   spread m/s   intensity kW/m   flame m   break 3 x L m"]
    for w, r in [(0.2, 0.05), (0.3, 0.1), (0.5, 0.3)]:
        i = h * w * r
        length = 0.0775 * i ** 0.46
        lines.append(f"  {w:10.1f}   {r:10.2f}   {i:14.0f}   {length:7.1f}   {3 * length:12.1f}")
    lines += ["  after a wet spring the grass between the PV rows can carry",
              "  a fire with flames of a few metres in wind: firebreaks",
              "  around the array, vegetation control under the tables and",
              "  the perimeter road are the passive defence (lesson C)"]
    emit("p_firebreak", lines)


if __name__ == "__main__":
    smoke_fill()
    fire_watch()
    container_exposure()
    firebreak()
