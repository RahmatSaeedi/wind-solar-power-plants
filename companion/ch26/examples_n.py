"""Chapter 26 - expansion round 2: reading a Wenner soil survey, the
fall-of-potential test of an earth electrode and its 61.8 % point, the
heating of a lightning down conductor, the arc-flash boundary against
the clearing time, and a fast 33 kV bus-blocking scheme.

Run from the project root:   python -m companion.ch26.examples_n
Writes companion/ch26/expected/n_*.txt and diagrams/data/ch26-fop.csv.
Teaching values A-333 to A-335; measurements and assessments are made
by qualified staff with the methods of the applicable standards.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import csv, emit
from plantp import protection as pr


def wenner() -> None:
    survey = [(1.0, 31.8), (2.0, 14.3), (4.0, 5.1), (8.0, 2.4), (16.0, 1.55), (32.0, 0.82)]
    rho = [(a, 2 * math.pi * a * r) for a, r in survey]
    lines = ["Wenner soil survey: four probes a metres apart, rho_a = 2 pi a R",
             "  (teaching readings for the substation plot, U-098)",
             "  spacing a m   reading R ohm   apparent rho ohm m"]
    for (a, r), (_, p) in zip(survey, rho):
        lines.append(f"  {a:11.0f}   {r:13.2f}   {p:18.0f}")
    top, low = rho[0][1], min(p for _, p in rho)
    lines += [f"  near the surface about {top:.0f} ohm m, falling to {low:.0f} at 4-8 m",
              f"  spacing and rising again to {rho[-1][1]:.0f} at 32 m: a dry top layer,",
              "  a wetter middle layer and denser ground below - three",
              "  layers that a fitted soil model describes, not one",
              "  average; the grid design (lesson C) uses the model, and",
              "  the survey is repeated in the dry season"]
    emit("n_wenner", lines)


# [start: fop]
def fop_reading(x: float, d: float, a: float, rho: float) -> float:
    """Apparent resistance of a hemispherical electrode (radius a) read
    with the current probe at d and the potential probe at x (all m):
    (V_electrode - V_probe) / I, the current probe carrying -I."""
    return rho / (2 * math.pi) * (1 / a - 1 / d - 1 / x + 1 / (d - x))
# [end: fop]


def fall_of_potential() -> None:
    rho, a, d = 100.0, 1.0, 100.0
    true_r = rho / (2 * math.pi * a)
    rows = []
    for k in range(5, 96, 5):
        x = d * k / 100
        rows.append((k, f"{fop_reading(x, d, a, rho):.2f}"))
    csv("ch26-fop.csv", "pct,r", rows)
    lo, hi = 0.5, 0.75
    for _ in range(60):
        mid = (lo + hi) / 2
        if fop_reading(mid * d, d, a, rho) < true_r:
            lo = mid
        else:
            hi = mid
    lines = ["fall-of-potential test of an earth electrode (hemisphere model):",
             f"  rho {rho:.0f} ohm m, electrode radius {a:.0f} m, current probe at {d:.0f} m;",
             f"  true resistance rho / 2 pi a = {true_r:.2f} ohm",
             "  potential probe at % of d   reading ohm"]
    for k in (20, 40, 50, 60, 62, 70, 80, 90):
        lines.append(f"  {k:26d}   {fop_reading(d * k / 100, d, a, rho):11.2f}")
    lines += [f"  the reading equals the true value at {lo * 100:.1f} % of the distance:",
              "  the rule of 61.8 %; the readings must also flatten around",
              "  it - a curve without a plateau means the probes are too",
              "  close for the size of the grid; a large substation grid",
              "  needs current leads hundreds of metres long, and the",
              "  test is planned with the transferred-potential hazard",
              "  in mind (qualified staff, the owner's rules)"]
    emit("n_fop", lines)


def down_conductor() -> None:
    w_r, rho, gamma, c = 10e6, 1.75e-8, 8920.0, 385.0
    lines = ["heating of a copper lightning down conductor by one stroke",
             "  (teaching specific energy W/R = 10 MJ per ohm; adiabatic,",
             "  dT ~ (W/R) rho / (S^2 gamma c))",
             "  section mm2   temperature rise K"]
    for s in (16, 25, 35, 50, 70):
        a = s * 1e-6
        dt = w_r * rho / (a * a * gamma * c)
        lines.append(f"  {s:11d}   {dt:17.0f}")
    lines += ["  the rise falls with the square of the section: small",
              "  conductors overheat, 50 mm2 copper stays moderate; the",
              "  turbine's down conductors, receptors and bearing bypasses",
              "  are the maker's design to the turbine lightning standard",
              "  (STD-125), proved by tests on blade samples"]
    emit("n_conductor", lines)


def arc_boundary() -> None:
    e_ref, d_ref, x, threshold = 8.0, 0.455, 2.0, 1.2
    lines = ["arc-flash boundary against clearing time (teaching scaling only)",
             f"  incident energy {e_ref:.0f} cal/cm2 at 455 mm for 1.0 s clearing;",
             "  energy ~ t / d^x with x = 2 (open air); boundary where the",
             "  energy falls to 1.2 cal/cm2 (onset of a second-degree burn)",
             "  clearing s   energy at 455 mm   boundary m"]
    for t in (1.0, 0.5, 0.2, 0.08):
        e = e_ref * t
        b = d_ref * (e / threshold) ** (1 / x)
        lines.append(f"  {t:10.2f}   {e:16.1f}   {b:10.2f}")
    lines += ["  a faster clearing shrinks both the energy and the boundary;",
              "  the real values come from the arc-flash assessment by",
              "  qualified engineers with an accepted method and the",
              "  equipment's data - this table only shows the direction"]
    emit("n_boundary", lines)


def bus_blocking() -> None:
    i = 6.4e3
    inc = src.RELAYS["incomer"]
    t_inc = pr.trip_time(i, inc["pickup"], inc["tms"])
    t_block = 0.10
    lines = ["33 kV bus fault: incomer inverse time against a blocking scheme",
             f"  bus fault {i / 1e3:.1f} kA through the incomer: standard-inverse time {t_inc:.2f} s",
             "  blocking scheme: the incomer's fast stage trips after 100 ms",
             "  unless a feeder relay reports 'I see the fault too' (then",
             "  the fault is on that feeder and the feeder clears it)",
             f"  bus fault cleared in {t_block:.2f} s + breaker 0.06 s = {t_block + 0.06:.2f} s",
             f"  arc energy ratio: {(t_block + 0.06) / (t_inc + 0.06):.2f} of the inverse-time case",
             "  the signal travels over hard wire or IEC 61850 messages; a",
             "  failed signal must not block (the scheme fails safe to the",
             "  inverse time), and the end-to-end test proves both paths"]
    emit("n_blocking", lines)


if __name__ == "__main__":
    wenner()
    fall_of_potential()
    down_conductor()
    arc_boundary()
    bus_blocking()
