"""Chapter 26, section C (continued) - earthing and surge physics: the
potential around a single electrode, the body current with and without
a surface layer, the earth-grid conductor, rods and the plant-wide
earthing system, transferred potentials, rolling-sphere cover of the
substation, voltages induced in PV string loops, arrester distance,
arrester voltage against the earthing method, and lightning over the
plant's life.

Run from the project root:   python -m companion.ch26.examples_g
Writes companion/ch26/expected/g_*.txt. Teaching values A-333 to A-335;
tolerable touch and step voltages come from the applicable guide's
method with site data and clearing times - none is set here.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr
from plantp.cables import adiabatic_mm2

G = src.GRID


def electrode() -> None:
    rho, i, a = G["rho"], 2_080.0, 0.5
    r0 = rho / (2 * math.pi * a)
    lines = ["potential around a single hemispherical electrode (a = 0.5 m):",
             f"  soil {rho:.0f} ohm m, current {i:,.0f} A: R = rho/(2 pi a) = {r0:.1f} ohm,"
             f" GPR {i * r0 / 1e3:.0f} kV",
             "  distance m   potential kV   share of GPR"]
    for r in (0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 50.0):
        v = pr.hemisphere_v(rho, i, r)
        lines.append(f"  {r:10.1f}   {v / 1e3:12.1f}   {v / (i * r0):12.0%}")
    lines += [f"  step from 0.5 to 1.5 m: {(pr.hemisphere_v(rho, i, 0.5) - pr.hemisphere_v(rho, i, 1.5)) / 1e3:.0f} kV"
              " - two-thirds of the GPR within a pace",
              "  one rod cannot carry a substation's fault current: the mesh",
              f"  of lesson C spreads it (0.86 ohm, GPR {i * 0.857:,.0f} V) and keeps",
              "  the surface inside it nearly at one potential; a real mesh",
              "  is not a hemisphere - current leaves mostly at its edges",
              "  and corners, which the guide's method takes into account"]
    emit("g_electrode", lines)


def body() -> None:
    v = 500.0
    lines = ["body current for a 500 V touch voltage (teaching resistances):",
             "  body 1,000 ohm; each foot a disc of 0.08 m: R = rho_s/(4 b)",
             "  surface              rho_s ohm m   foot ohm   touch A   step A"]
    for name, rho_s in (("natural soil", 150.0), ("wet gravel layer", 1_000.0),
                        ("crushed rock layer", 3_000.0)):
        rf = pr.foot_resistance(rho_s)
        lines.append(f"  {name:20s} {rho_s:11,.0f}   {rf:8,.0f}"
                     f"   {pr.body_current(v, 1000, rf):7.3f}"
                     f"   {pr.body_current(v, 1000, rf, 'step'):6.3f}")
    lines += ["  a high-resistivity surface layer puts resistance in series",
              "  with the body: the same voltage drives several times less",
              "  current; the tolerable current itself falls as the clearing",
              "  time grows - the guide's method combines the two, and fast",
              "  protection and the surface layer are earthing measures"]
    emit("g_body", lines)


def conductor() -> None:
    lines = ["earth-grid conductor by the adiabatic rule S = I sqrt(t) / k",
             "  (copper, teaching k = 143 as in ch 24 - bare conductors may",
             "  use a higher final temperature and k)",
             "  fault kA   time s   S mm2"]
    for ik, t in ((5.2, 0.5), (5.2, 1.0), (31.5, 1.0), (31.5, 3.0)):
        lines.append(f"  {ik:8.1f}   {t:6.1f}   {adiabatic_mm2(ik, t, 143):5.0f}")
    lines += ["  the 132 kV earth fault sets the size (the 33 kV earth faults",
              "  are held to 400 A by the resistor); many owners size the",
              "  grid for the switchgear rating (31.5 kA) and its time, so",
              "  the grid outlives fault-level growth; corrosion allowance",
              "  and mechanical strength add to the electrical minimum"]
    emit("g_conductor", lines)


def rods() -> None:
    rho, length, d = G["rho"], 3.0, 0.016
    r1 = rho / (2 * math.pi * length) * (math.log(4 * length / d) - 1)
    lines = ["rods and the plant-wide earthing system:",
             f"  one rod 3 m x 16 mm in {rho:.0f} ohm m: R = rho/(2 pi L)(ln(4L/d) - 1)"
             f" = {r1:.1f} ohm",
             f"  ten rods far apart: {r1 / 10:.1f} ohm; close together they share"
             " soil and give more",
             "  turbine foundation earth (teaching 5 ohm each), 12 turbines,",
             "  bonded through the cable screens to the substation grid:"]
    par = 1 / (1 / 0.857 + 12 / 5.0)
    lines += [f"    substation alone 0.857 ohm; all together about {par:.2f} ohm",
              "  the screens join the earths into one system: lower resistance",
              "  and shared fault current, but a substation fault also raises",
              "  the turbines' earths a little - the study models it"]
    emit("g_rods", lines)


def transferred() -> None:
    gpr = 1_783
    lines = ["transferred potential: a metal path leaving the earth grid",
             f"  during a 132 kV earth fault the grid rises to about {gpr:,} V",
             "  a copper telecom pair or an LV supply bonded to the grid",
             f"  carries those {gpr:,} V to remote earth (a house, an office)",
             "  - and remote earth back into the substation the other way",
             "  remedies: optical fibre (no metal) for telecom, isolation",
             "  transformers, no shared LV earth with neighbours, and a",
             "  fence either bonded to the grid with the grid extended past",
             "  it, or kept separate - each decided in the earthing study"]
    emit("g_transferred", lines)


def sphere() -> None:
    h, hx = 20.0, 8.0
    lines = ["rolling-sphere cover of the substation by masts (h = 20 m):",
             "  sphere radius m   radius at ground m   radius at 8 m height m"]
    for r in (20.0, 30.0, 45.0, 60.0):
        r0 = pr.rolling_sphere_r(h, r)
        rx = r0 - math.sqrt(hx * (2 * r - hx))
        lines.append(f"  {r:15.0f}   {r0:18.1f}   {rx:22.1f}")
    rx45 = pr.rolling_sphere_r(h, 45) - math.sqrt(hx * (2 * 45 - hx))
    lines += ["  the sphere radius falls with the protection level the risk",
              "  study chooses (teaching radii here); a smaller sphere gives",
              "  less cover per mast",
              f"  with 45 m: one mast covers {math.pi * rx45 ** 2:,.0f} m2 at 8 m; the"
              f" 7,000 m2 yard needs about {7000 / (math.pi * rx45 ** 2):.0f}",
              "  masts if each stood alone - shield wires between masts, or",
              "  the cover between two masts, need far fewer"]
    emit("g_sphere", lines)


def induced() -> None:
    lines = ["voltage induced in a PV string loop by a strike 50 m away",
             "  (di/dt 10 kA per microsecond, teaching):",
             "  routing of + and -                    loop m2   induced V"]
    for name, area in (("returned 2 m apart along 28.6 m", 57.2),
                       ("returned 0.3 m apart", 8.6),
                       ("bundled together", 1.4)):
        lines.append(f"  {name:37s} {area:7.1f}   {pr.loop_voltage(area, 50, 1e10):9,.0f}")
    lines += ["  the loop area sets the voltage: running the plus and minus",
              "  cables together is the cheapest surge measure; DC surge",
              "  protective devices at the inverter (and combiner) take the",
              "  rest; the cable layout of ch 24 and the SPDs of the PV",
              "  design are checked together"]
    emit("g_induced", lines)


def distance() -> None:
    bil, ures, du = 650.0, 330.0, 1_000.0
    lines = ["arrester to equipment distance (travelling wave, teaching):",
             f"  residual {ures:.0f} kV, front {du:.0f} kV/us, wave speed 300 m/us,"
             f" withstand {bil:.0f} kV",
             "  distance m   voltage at equipment kV   margin"]
    for s in (5, 15, 30, 40):
        v = pr.at_equipment(ures, s, du)
        lines.append(f"  {s:10d}   {v:23.0f}   {bil / v:6.2f}")
    smax = (bil / 1.2 - ures) * 300 / (2 * du)
    lines += [f"  for a margin of 1.2 the arrester must be within {smax:.0f} m of the",
              "  transformer bushing (lead lengths count as distance): one",
              "  reason arresters are mounted on or beside the transformer"]
    emit("g_distance", lines)


def tov() -> None:
    um = 36.0
    lines = ["arrester voltage against the earthing method (33 kV system):",
             f"  normal phase-to-earth voltage {um / math.sqrt(3):.1f} kV (Um 36 kV)",
             f"  during an earth fault the healthy phases rise towards {um:.0f} kV",
             "  earthing                  overvoltage lasts    continuous"
             " rating   residual",
             ]
    for name, last, mcov in (("resistance, cleared", "about 2 s", um / math.sqrt(3)),
                             ("unearthed, not cleared", "hours", um)):
        lines.append(f"  {name:25s} {last:18s} {mcov:9.1f} kV   {2.8 * mcov:6.0f} kV")
    lines += ["  (residual taken as 2.8 x the continuous rating, teaching)",
              "  a short overvoltage is met by the arrester's temporary",
              "  rating; one lasting hours needs a continuous rating at line",
              "  voltage - a larger arrester with a higher residual and less",
              f"  margin to a 170 kV impulse level ({170 / (2.8 * um / math.sqrt(3)):.1f}"
              f" against {170 / (2.8 * um):.1f})",
              "  the earthing decision of lesson B fixes the arresters too"]
    emit("g_tov", lines)


def life() -> None:
    n_year = 20.8
    lines = ["lightning over the plant's life (teaching):",
             f"  {n_year:.1f} strikes a year on the twelve turbines -> {n_year * 25:,.0f} in 25 years"]
    for p in (0.01, 0.02, 0.05):
        lines.append(f"  if {p:.0%} of strikes need a blade repair: {n_year * 25 * p:5.1f}"
                     " repairs over the life")
    lines += ["  the lightning protection of the blades is a design and a",
              "  maintenance subject: receptor and down-conductor checks",
              "  after storms and at inspections, records of strikes (some",
              "  turbines log them), and spares (ch 18, ch 52)"]
    emit("g_life", lines)


def zones() -> None:
    z = [("LPZ 0A", "exposed to direct strikes and the full field",
          "air terminals, down conductors"),
         ("LPZ 0B", "shielded from direct strikes, full field", "masts, shield wires cover it"),
         ("LPZ 1", "inside a building or nacelle: surges limited", "SPD at every line entering"),
         ("LPZ 2", "inside a cabinet: further reduced", "second SPD stage, shielding")]
    lines = ["lightning protection zones (concept):"]
    for a, b, c in z:
        lines += [f"  {a}: {b}", f"    measure: {c}"]
    lines += ["  every conductor that crosses a zone boundary - power, signal,",
              "  data, pipes - is bonded or protected at the boundary"]
    emit("g_zones", lines)


if __name__ == "__main__":
    electrode()
    body()
    conductor()
    rods()
    transferred()
    sphere()
    induced()
    distance()
    tov()
    life()
    zones()
