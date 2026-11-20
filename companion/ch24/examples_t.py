"""Chapter 24 - fourth round: the force between single-core cables in a
fault and the cleats that hold them, how insulation life falls with
temperature, the 600 V link from a PV inverter (parallel cables or a
busduct), the air a switchgear room needs for its losses, cables grouped
on a tray, and the neutral of an LV circuit full of triplen harmonics.

Run from the project root:   python -m companion.ch24.examples_t
Writes companion/ch24/expected/t_*.txt. Teaching values (A-321..A-325
extended): makers' data, the rating method and the room design decide.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as src
from companion.ch24.common import emit


def trefoil() -> None:
    lines = ["force between single-core cables in a fault: F = 0.17 ip^2 / s",
             "  (N/m, ip in kA, s in m; trefoil, teaching constant)",
             "  peak kA   spacing m   force kN/m   cleat every 1.0 m kN   1.5 m kN"]
    for ip, s in ((40.0, 0.14), (80.0, 0.14), (80.0, 0.20)):
        f = 0.17 * ip ** 2 / s / 1e3
        lines.append(f"  {ip:7.0f}   {s:9.2f}   {f:10.1f}   {f * 1.0:20.1f}   {f * 1.5:8.1f}")
    lines += ["  at the switchgear's 80 kA peak the cables push apart with",
              "  nearly 8 kN per metre: cleats sized and spaced for it keep",
              "  them in place - the cleat maker's short-circuit test is the",
              "  evidence, and the spacing goes on the installation drawing"]
    emit("t_trefoil", lines)


def ageing() -> None:
    lines = ["insulation life against conductor temperature (teaching rule:",
             "  life halves for every 8 K above 90 C, 40 years at 90 C):",
             "  conductor C   relative life   years"]
    for t in (70, 80, 90, 98, 106):
        rel = 2 ** ((90 - t) / 8)
        lines.append(f"  {t:11d}   {rel:13.2f}   {40 * rel:6.0f}")
    lines += ["  a cable that runs cooler than its limit most of the time",
              "  lasts longer; one pushed past it ages fast - the cyclic and",
              "  emergency ratings of lesson A spend this life on purpose,",
              "  so they are bounded in hours a year, not left open"]
    emit("t_ageing", lines)


def inverter_link() -> None:
    i = 5.5e6 / (math.sqrt(3) * 600)
    per_cable = src.LV_CABLES[240][1] * 0.70
    n = math.ceil(i / per_cable)
    lines = ["the 600 V link from a 5.5 MVA PV inverter to its transformer:",
             f"  current {i:,.0f} A per phase",
             f"  Cu 240 mm2 in air {src.LV_CABLES[240][1]:.0f} A, grouped x0.70 ="
             f" {per_cable:.0f} A -> {n} cables per phase",
             "  current sharing between parallel cables (teaching): with an",
             "  untransposed flat layout the outer cables carry up to",
             f"  25 % more; to keep the busiest within its rating takes"
             f" {math.ceil(i / (per_cable / 1.25))} cables",
             "  a busduct of the rating, or the transformer bolted to the",
             "  inverter skid, avoids the problem: the skid design (ch 9)",
             "  is chosen partly for this link"]
    emit("t_inverterlink", lines)


def ventilation() -> None:
    losses_kw = 9 * 0.35 + 2.0 + 1.5        # panels, relays and lighting, other
    lines = ["air for the 33 kV switchgear room (section A, teaching):",
             f"  heat: 9 panels x 0.35 kW + relays 2.0 + other 1.5 = {losses_kw:.2f} kW",
             "  rise allowed K   air m3/h"]
    for dt in (5, 10, 15):
        q = losses_kw * 1e3 / (1.2 * 1005 * dt) * 3600
        lines.append(f"  {dt:15d}   {q:9,.0f}")
    lines += ["  the switchgear's losses are small but steady; the room's",
              "  air (or cooling, in a hot climate) is sized for them plus",
              "  the sun on the walls (ch 23 lesson E) - and the internal-",
              "  arc vents must not be blocked by the ducts"]
    emit("t_ventilation", lines)


def tray() -> None:
    lines = ["LV cables grouped on a tray (teaching grouping factors):",
             "  circuits touching   factor   25 mm2 rating A"]
    base = src.LV_CABLES[25][1]
    for n, k in ((1, 1.00), (3, 0.82), (6, 0.73), (9, 0.70), (12, 0.68)):
        lines.append(f"  {n:18d}   {k:6.2f}   {base * k:15.0f}")
    lines += ["  each cable warms its neighbours: twelve circuits side by",
              "  side lose a third of their rating; spacing, a second tray",
              "  or a larger size restores it - the lesson E factor 0.8 was",
              "  a stand-in for this table"]
    emit("t_tray", lines)


def neutral() -> None:
    lines = ["the neutral of a circuit feeding LED drivers and IT loads:",
             "  third harmonic % of phase   neutral / phase current"]
    for h3 in (0, 20, 33, 50):
        i1 = 1.0
        i3 = h3 / 100
        i_ph = math.hypot(i1, i3)
        i_n = 3 * i3
        lines.append(f"  {h3:26d}   {i_n / i_ph:23.2f}")
    lines += ["  the third harmonics of three phases are in phase and add",
              "  in the neutral: above about a third, the neutral carries",
              "  more than a phase - a reduced neutral is wrong for these",
              "  circuits, and a 4-core cable is rated on its neutral"]
    emit("t_neutral", lines)


if __name__ == "__main__":
    trefoil()
    ageing()
    inverter_link()
    ventilation()
    tray()
    neutral()
