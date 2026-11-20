"""Chapter 24 - fifth round: SF6 pressure against temperature at constant
density, current chopping when a vacuum breaker switches an unloaded
unit transformer, the capacitive current a feeder breaker must switch,
allocating cut lengths to drums with the least waste, and the earth bar
of the switchboard.

Run from the project root:   python -m companion.ch24.examples_u
Writes companion/ch24/expected/u_*.txt. Teaching values (A-321..A-325
extended): ratings and limits come from the makers and the standards.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as src
from companion.ch24.common import emit
from plantp import cables as cb


def sf6_density() -> None:
    p20 = 1.40                     # bar abs at 20 C (filling, teaching)
    lines = ["SF6 in a sealed panel: same gas, different pressure (ideal gas):",
             "  ambient C   pressure bar abs   density relative"]
    for t in (-25, 0, 20, 40, 55):
        p = p20 * (t + 273.15) / 293.15
        lines.append(f"  {t:9d}   {p:16.2f}   {1.00:16.2f}")
    lines += ["  the insulation depends on the density, not the pressure: a",
              "  cold morning lowers the pressure without any leak; a density",
              "  monitor (temperature-compensated) alarms only when gas has",
              "  really gone - a plain pressure gauge would cry wolf in",
              "  winter and miss a leak in summer"]
    emit("u_sf6density", lines)


def chopping() -> None:
    lines = ["current chopping: a vacuum breaker opens an unloaded transformer",
             "  U = I_ch x sqrt(L/C) (teaching surge impedances)",
             "  chopped A   surge impedance ohm   overvoltage kV peak   vs 33 kV peak"]
    u_peak = 33 * math.sqrt(2) / math.sqrt(3)
    for ich, z in ((1.0, 5000), (3.0, 10000), (3.0, 20000), (5.0, 20000)):
        u = ich * z / 1e3
        lines.append(f"  {ich:9.1f}   {z:19d}   {u:19.1f}   {u / u_peak:13.1f} x")
    lines += ["  the magnetising current is cut before its zero and the",
              "  transformer's magnetic energy rings into its capacitance:",
              "  several times the normal peak on a dry-type or cable-fed",
              "  transformer - wind farms switch many such transformers, so",
              "  surge arresters or RC snubbers at the unit transformers are",
              "  a common answer, decided with the makers' studies"]
    emit("u_chopping", lines)


def capacitive() -> None:
    lines = ["capacitive current the feeder breakers must switch (33 kV, teaching):",
             "  circuit                    uF per phase   charging A"]
    for name, c_uf in (("feeder =WS1 (4.4 km)", 1.02), ("feeder =PVF1 (2.4 km)", 0.50),
                       ("whole section A", 2.68), ("section A + B (coupler)", 5.36)):
        i = cb.charging_a(33.0, c_uf, 1.0)
        lines.append(f"  {name:26s} {c_uf:12.2f}   {i:10.1f}")
    lines += ["  small next to the load current, but switching it off is a",
              "  special duty: the capacitor keeps its charge and the voltage",
              "  across the opening contacts doubles - a breaker that",
              "  restrikes makes overvoltages; the cable-charging switching",
              "  rating (and its low-restrike class) belongs in the",
              "  specification next to the fault rating"]
    emit("u_capacitive", lines)


# [start: drums]
def allocate(cuts: list, drum: float) -> list:
    """First-fit decreasing: put each cut length (largest first) on the
    first drum with room; return the list of drums (lists of cuts)."""
    drums: list = []
    for c in sorted(cuts, reverse=True):
        for d in drums:
            if sum(d) + c <= drum:
                d.append(c)
                break
        else:
            drums.append([c])
    return drums
# [end: drums]


def drum_plan() -> None:
    cuts = [1.18, 1.05, 1.12, 1.09, 0.64, 0.58, 0.61, 0.66, 0.59, 0.62, 0.55, 0.63, 0.60]
    lines = ["allocating surveyed cut lengths (km, with 2 % for terminations) to drums:"]
    for drum in (1.2, 2.4, 3.6):
        plan = allocate([c * 1.02 for c in cuts], drum)
        used = sum(sum(d) for d in plan)
        waste = len(plan) * drum - used
        lines.append(f"  drums of {drum:.1f} km: {len(plan):2d} drums, off-cut {waste:.2f} km"
                     f" ({waste / (len(plan) * drum):.0%})")
    lines += ["  short drums leave an off-cut on every cut; very long drums",
              "  leave large remainders; the middle size wastes least here -",
              "  and longer drums weigh more (lesson B) and are cut on site",
              "  with the off-cuts stored; the allocation is made from the",
              "  route survey, not from the design lengths, and repeated",
              "  when the survey changes"]
    emit("u_drums", lines)


def earth_bar() -> None:
    ik, t = 25.0, 1.0
    need = cb.adiabatic_mm2(ik, t, src.K_CU)
    lines = ["earth bar of the 33 kV switchboard (copper, k 143 as in lesson A):",
             f"  rated short-time current {ik:.0f} kA for {t:.0f} s: S = {need:.0f} mm2",
             "  chosen: copper bar 40 x 5 mm = 200 mm2 (above the minimum)",
             "  every panel's frame, earthing switch and cable screen ends",
             "  on it, and it is bonded to the station earth grid at two",
             "  points at least (ch 26) - its rating is the switchgear's",
             "  rating, because an earth switch closed onto a live circuit",
             "  sends the full fault current through it"]
    emit("u_earthbar", lines)


if __name__ == "__main__":
    sf6_density()
    chopping()
    capacitive()
    drum_plan()
    earth_bar()
