"""Chapter 26, section C - earthing and lightning: the substation grid's
resistance from soil data, the ground potential rise of a 132 kV earth
fault, why touch voltage is checked against the clearing time, the
number of lightning strikes a year on the turbines and the substation,
and the surge arrester's protective margin.

Run from the project root:   python -m companion.ch26.examples_c
Writes companion/ch26/expected/c_*.txt. Teaching values A-333 to A-335;
tolerable touch and step limits come from the method of the applicable
guide with site data, not from this script.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr

G = src.GRID
L = src.LIGHTNING


def grid() -> None:
    area = G["l_m"] * G["w_m"]
    lines = ["substation earth grid (100 m x 70 m mesh, teaching):",
             "  soil ohm m   conductor m   grid ohm"]
    for rho in (50, 150, 400):
        for length in (1_600, 2_400):
            lines.append(f"  {rho:10d}   {length:11,d}   {pr.grid_resistance(rho, area, length):8.3f}")
    lines += ["  the soil sets the resistance far more than the copper: more",
              "  conductor lowers it little once the mesh covers the area;",
              "  the soil survey (U-098) is the first evidence, layers and",
              "  seasons included"]
    emit("c_grid", lines)


def gpr() -> None:
    r = pr.grid_resistance(G["rho"], G["l_m"] * G["w_m"], G["conductor_m"])
    i_e = src.NETWORK["ik_132"] * G["split"]
    v = pr.gpr(i_e, r)
    lines = ["ground potential rise for a 132 kV earth fault in the substation:",
             f"  grid {r:.3f} ohm; fault {src.NETWORK['ik_132'] / 1e3:.1f} kA, share to earth"
             f" {G['split']:.0%} = {i_e:,.0f} A",
             f"  GPR = {i_e:,.0f} x {r:.3f} = {v:,.0f} V",
             "  the earth wire of the line and the cable screens carry the",
             "  rest of the current back; the split is a study result",
             "  (U-089), not a constant",
             "  touch and step voltages are fractions of the GPR set by the",
             "  mesh geometry; the tolerable limits fall as the clearing",
             "  time grows (roughly with 1/sqrt t): halving the clearing",
             f"  time raises the limit by {math.sqrt(2):.2f} x - fast protection is",
             "  part of the earthing design"]
    emit("c_gpr", lines)


def lightning() -> None:
    tip = L["hub"] + L["rotor_r"]
    a_t = pr.collection_area(tip)
    n_t = pr.strikes_per_year(L["ng"], a_t)
    a_s = pr.collection_area(10, 100, 70)
    lines = ["direct lightning strikes a year (teaching flash density"
             f" {L['ng']} per km2 a year):",
             f"  turbine, tip height {tip:.0f} m: area {a_t / 1e6:.2f} km2 -> {n_t:.2f} a year",
             f"  twelve turbines: {L['turbines'] * n_t:.1f} strikes a year",
             f"  substation 100 x 70 m, 10 m high: {pr.strikes_per_year(L['ng'], a_s):.3f} a year",
             "  each turbine is struck about twice a year - blades, nacelle and",
             "  tower carry a lightning protection system proved by the",
             "  maker; tall structures also launch upward flashes that this",
             "  count does not include; the local flash density (U-099) and",
             "  the risk method of the lightning standard decide the rest"]
    emit("c_lightning", lines)


def arrester() -> None:
    lines = ["surge arrester protective margin (teaching values):",
             "  equipment withstand (lightning impulse) kV   arrester residual kV   margin"]
    for bil, ures in ((650, 330), (650, 400), (550, 400)):
        lines.append(f"  {bil:40d}   {ures:20d}   {bil / ures:6.2f}")
    lines += ["  the margin must also cover the voltage rise along the lead",
              "  and the distance from arrester to equipment - so arresters",
              "  sit at the line entrance and next to each transformer; the",
              "  insulation levels and the arrester come from the insulation",
              "  coordination study, not from this table"]
    emit("c_arrester", lines)


def arc_flash() -> None:
    lines = ["arc-flash: why clearing time matters (concept, no procedure):",
             "  incident energy grows roughly with arcing current x time",
             "  clearing time s    relative energy"]
    for t in (1.0, 0.5, 0.2, 0.08):
        lines.append(f"  {t:15.2f}    {t / 1.0:15.2f}")
    lines += ["  a fast scheme (bus protection, arc sensors) cuts the energy",
              "  in proportion; the arc-flash risk assessment by qualified",
              "  engineers sets boundaries and labels; work on or near live",
              "  equipment follows the owner's safety rules and permits -",
              "  this book does not give live-work procedures"]
    emit("c_arcflash", lines)


if __name__ == "__main__":
    grid()
    gpr()
    lightning()
    arrester()
    arc_flash()
