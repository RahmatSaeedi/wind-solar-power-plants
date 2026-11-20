"""Chapter 30, lesson T: a last round on structures over their life - the
chance of meeting the design storm, damping against vortex shedding,
why preload protects the anchor bolts from fatigue, steel loss on PV
posts once the zinc is gone, a lifting lug, weld preheat from the carbon
equivalent, what decommissioning removes, and the embodied carbon of a
foundation and tower.

Run from the project root:   python -m companion.ch30.examples_t
Writes companion/ch30/expected/t_*.txt and diagrams/data/ch30-joint.csv.
Teaching values (A-356 to A-362); the codes, the maker and the
certifier set the real values.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st


def exceedance() -> None:
    lines = ["chance of meeting a return-period event within the design life",
             "  return period yr   in 25 years   in 30 years"]
    for t in (10, 50, 100, 475, 2475):
        p25 = 1 - (1 - 1 / t) ** 25
        p30 = 1 - (1 - 1 / t) ** 30
        lines.append(f"  {t:16d}   {p25 * 100:9.0f} %   {p30 * 100:9.0f} %")
    lines += ["  the '50-year' gust has a 40 % chance of arriving during a",
              "  25-year life: it is a likely event, not a remote one,",
              "  which is why it is a characteristic load with partial",
              "  factors on top, and the 475-year earthquake about 5 %"]
    emit("t_exceedance", lines)


def scruton() -> None:
    d, m_line = 3.0, 3364.0                       # top diameter, mass a metre (ch 11 tube)
    lines = ["damping against vortex shedding: the Scruton number (bare tower)",
             "  Sc = 2 m delta / (rho D^2), delta = 2 pi zeta (log decrement)",
             "  case                           zeta     Sc     relative amplitude"]
    base = None
    for name, z in [("bare steel tower", 0.002), ("with temporary damper", 0.010),
                    ("tuned mass damper", 0.040)]:
        sc = 2 * m_line * 2 * math.pi * z / (src.SITE["rho"] * d * d)
        base = base or sc
        lines.append(f"  {name:30s} {z:6.3f}   {sc:5.1f}   {base / sc:18.2f}")
    lines += ["  the vortex amplitude falls roughly as 1/Sc: a damper that",
              "  raises damping fivefold cuts the swing to a fifth - which",
              "  is how the maker's procedure may allow a bare tower to",
              "  stand overnight (lesson A); without it, a wind limit applies"]
    emit("t_scruton", lines)


def joint() -> None:
    kb, kc = 1.0, 6.0                             # bolt and clamped-part stiffness ratio
    phi = kb / (kb + kc)
    preload = 1250.0
    rows = []
    lines = ["why preload protects an anchor bolt from fatigue (joint diagram)",
             f"  load factor phi = kb/(kb+kc) = {phi:.2f}; preload {preload:,.0f} kN",
             "  external pull kN   bolt force (preloaded)   bolt force (lost preload)"]
    for f_ext in (0, 200, 400, 600, 800, 1036):
        tight = preload + phi * f_ext
        loose = f_ext
        rows.append((f_ext, round(tight, 1), loose))
        lines.append(f"  {f_ext:16.0f}   {tight:22.0f}   {loose:25.0f}")
    csv("ch30-joint.csv", "fext,tight,loose", rows)
    rng_tight = phi * 400
    lines += [f"  a fatigue cycle of 400 kN gives the tight bolt {rng_tight:.0f} kN of range,",
              "  the slack bolt the full 400 kN - seven times more, and",
              f"  with slope 3 about {7 ** 3:.0f} times the damage: the re-tensioning",
              "  of lesson C is a fatigue measure as much as a strength one"]
    emit("t_joint", lines)


def steel_loss() -> None:
    lines = ["PV post steel after the zinc is gone (C-post, 3 mm walls; teaching)",
             "  soil                       zinc life   steel loss um/yr   wall at 30 yr"]
    for name, zinc_life, rate in [("dense sand, dry", 85, 6.0), ("silty sand, moist", 28, 15.0),
                                  ("gypsum, saline", 11, 40.0)]:
        years = max(0, 30 - zinc_life)
        wall = 3.0 - 2 * rate * years / 1000           # both faces
        lines.append(f"  {name:25s} {zinc_life:9d}   {rate:16.0f}   {wall:10.2f} mm")
    lines += ["  in the saline zone the wall loses about half its thickness",
              "  by year 30, at the ground line where the bending is",
              "  greatest; a thicker section, a duplex coating or a",
              "  concrete footing there - sized from the ch 29 tests"]
    emit("t_steelloss", lines)


def lug() -> None:
    mass = 124.0e3                                 # base section, kg (ch 31)
    daf = 1.3
    per_lug = mass * 9.81 * daf / 2 / 1e3
    fy = 355.0
    lines = ["a lifting lug on the base section (teaching check)",
             f"  124 t, two lugs, dynamic factor {daf}: {per_lug:,.0f} kN a lug",
             "  thickness mm   tear-out area mm2   shear stress MPa   use (0.58 fy)"]
    for t in (40, 50, 60):
        a = 2 * t * 50.0                           # two shear planes, 50 mm edge (teaching)
        tau = per_lug * 1e3 / a
        lines.append(f"  {t:12d}   {a:17,.0f}   {tau:16.0f}   {tau / (0.58 * fy):13.2f}")
    lines += ["  a 40 mm lug is at the limit; 50 or 60 mm leaves a margin.",
              "  A real lug design checks bearing, tear-out, the weld and",
              "  the shell behind it, and each lug is tested and recorded",
              "  - lifting points are the maker's design, never improvised"]
    emit("t_lug", lines)


def preheat() -> None:
    def ce(c, mn, cr=0.0, mo=0.0, v=0.0, ni=0.0, cu=0.0):
        return c + mn / 6 + (cr + mo + v) / 5 + (ni + cu) / 15

    lines = ["carbon equivalent and preheat (IIW formula; teaching thresholds)",
             "  heat (mill certificate)          CE     t mm   preheat (teaching)"]
    for name, chem, t in [("S355 heat A", (0.16, 1.45, 0.05, 0.02, 0.0, 0.05, 0.10), 30),
                          ("S355 heat A", (0.16, 1.45, 0.05, 0.02, 0.0, 0.05, 0.10), 50),
                          ("S355 heat B", (0.20, 1.55, 0.15, 0.05, 0.05, 0.10, 0.20), 50)]:
        e = ce(*chem)
        if e < 0.40:
            need = "none" if t <= 40 else "50 C"
        elif e < 0.45:
            need = "50 C" if t <= 40 else "100 C"
        else:
            need = "125 C"
        lines.append(f"  {name:30s} {e:5.2f}   {t:5d}   {need}")
    lines += ["  the same grade can need different preheat by heat and",
              "  thickness: the welding procedure (lesson C) takes CE",
              "  from the mill certificate of the plate in the jig, not",
              "  from the grade's maximum"]
    emit("t_preheat", lines)


def decommission() -> None:
    f = src.FOUNDATION
    area = math.pi * f["r"] ** 2
    top = area * 1.0
    lines = ["what decommissioning removes from one turbine base (teaching)",
             f"  concrete {f['concrete_m3']:.0f} m3; base area {area:.0f} m2",
             f"  removing the top 1 m: about {top:.0f} m3 of concrete (incl. pedestal)",
             f"  full removal: {f['concrete_m3']:.0f} m3 and {f['concrete_m3'] * 0.10:.0f} t of rebar"
             " (about 100 kg/m3)",
             "  tower 340 t and most of the 271 t on top: steel, recycled",
             "  which depth applies is a permit and land-agreement",
             "  condition (ch 53): the volume, the crushing and the",
             "  haul are priced in the decommissioning reserve from day 1"]
    emit("t_decom", lines)


def carbon() -> None:
    f = src.FOUNDATION
    conc = f["concrete_m3"] * 0.30                 # t CO2e per m3 (teaching)
    rebar = f["concrete_m3"] * 0.10 * 1.9          # t steel x t CO2e/t
    tower = (src.TOWER_T + 32) * 2.0               # t steel x t CO2e/t (plates)
    total = conc + rebar + tower
    energy_mwh = 191_870 / 12 * 1000 / 1000        # MWh a turbine a year (ch 13 P50)
    lines = ["embodied carbon of one foundation and tower (teaching factors)",
             f"  concrete 620 m3 x 0.30 t/m3        {conc:7.0f} t CO2e",
             f"  rebar 62 t x 1.9 t/t              {rebar:7.0f} t CO2e",
             f"  tower 372 t x 2.0 t/t             {tower:7.0f} t CO2e",
             f"  total                             {total:7.0f} t CO2e",
             f"  a turbine's energy: about {energy_mwh:,.0f} MWh a year",
             "  at 0.5 t CO2 per MWh displaced (teaching), the structure's",
             f"  carbon is repaid in about {total / (energy_mwh * 0.5) * 12:.1f} months of operation;",
             "  lower-cement concrete and recycled steel cut it further,",
             "  and the real factors come from the suppliers' declarations"]
    emit("t_carbon", lines)


if __name__ == "__main__":
    exceedance()
    scruton()
    joint()
    steel_loss()
    lug()
    preheat()
    decommission()
    carbon()
