"""Chapter 24 - switchgear physics for the engineer who specifies it: the
temperature rise of a busbar from its losses and surface, the DC part of
the fault current at contact separation, the energy of an internal arc,
the climate weight of SF6 leaks, and contact wear counted in
interrupted current.

Run from the project root:   python -m companion.ch24.examples_k
Writes companion/ch24/expected/k_*.txt. Teaching values (A-325
extended): ratings, test classes and limits come from the product
standards and the maker's type tests.
"""
from __future__ import annotations

import math

from companion.ch24.common import emit

RHO_CU = 1.72e-8 * (1 + 0.00393 * 70)        # ohm m at 90 C


def busbar() -> None:
    lines = ["temperature rise of a copper busbar in still air (teaching):",
             "  bar mm        current A   loss W/m   surface m2/m   rise K"]
    h = 9.0                                   # W/(m2 K), convection + radiation
    for w, t, i in ((100, 10, 2500), (2 * 100, 10, 2500), (120, 10, 1250), (100, 10, 3150)):
        area = w * t * 1e-6
        loss = i ** 2 * RHO_CU / area * 1.08    # skin and proximity, teaching
        surf = 2 * (w + t) * 1e-3 if w <= 120 else 2 * (100 + t) * 2e-3
        rise = loss / (h * surf)
        name = f"{w}x{t}" if w <= 120 else "2 x 100x10"
        lines.append(f"  {name:12s}  {i:9d}   {loss:8.1f}   {surf:12.3f}   {rise:6.1f}")
    lines += ["  the loss grows with I^2 and the cooling with the surface:",
              "  two thinner bars beat one thick bar; the rise allowed",
              "  at joints and contacts is what the temperature-rise type",
              "  test proves - the panel's rating, not this estimate"]
    emit("k_busbar", lines)


def dc_component() -> None:
    lines = ["DC part of the fault current when the contacts part (teaching):",
             "  X/R   tau ms   10 ms + opening 30 ms   10 ms + opening 50 ms"]
    for xr in (10, 17, 30, 45):
        tau = xr / (2 * math.pi * 50) * 1e3
        dc1 = math.exp(-40 / tau)
        dc2 = math.exp(-60 / tau)
        lines.append(f"  {xr:3d}   {tau:6.1f}   {dc1:21.0%}   {dc2:21.0%}")
    lines += ["  near large transformers X/R is high and the DC part decays",
              "  slowly: a breaker that parts its contacts quickly must",
              "  interrupt a current with a large offset - the DC part at",
              "  separation is a rated value of the breaker, compared with",
              "  the study's X/R in the specification (ch 26)"]
    emit("k_dc", lines)


def internal_arc() -> None:
    lines = ["energy of an internal arc in a 33 kV panel (teaching):",
             "  arc voltage about 500 V per phase; three phases",
             "  current kA   duration s   energy MJ"]
    for ik, t in ((25, 1.0), (25, 0.1), (12.5, 0.5)):
        e = 3 * 500 * ik * 1e3 * t / 1e6
        lines.append(f"  {ik:10.1f}   {t:10.1f}   {e:9.1f}")
    lines += ["  tens of megajoules in a closed box: the pressure must go",
              "  somewhere - flaps and ducts lead it away from people, and",
              "  the internal-arc type test proves the panel does that; an",
              "  arc sensor that trips in 0.1 s cuts the energy ten times",
              "  (ch 26); the room's volume and vents are part of it"]
    emit("k_arc", lines)


def sf6() -> None:
    gwp = 24000.0              # order of magnitude of SF6's 100-year GWP
    lines = ["SF6 in 33 kV gas-insulated switchgear (teaching quantities):",
             "  panels   kg each   leak %/yr   t CO2e per year   over 30 years"]
    for n, kg, leak in ((18, 3.0, 0.1), (18, 3.0, 0.5), (18, 3.0, 1.0)):
        co2 = n * kg * leak / 100 * gwp / 1e3
        lines.append(f"  {n:6d}   {kg:7.1f}   {leak:9.1f}   {co2:15.2f}   {co2 * 30:13.1f}")
    end = 18 * 3.0 * 0.02 * gwp / 1e3
    lines += [f"  losing 2 % of the gas at end of life: {end:.1f} t CO2e more",
              "  (GWP taken as about 24,000; published values differ",
              "  slightly between assessments)",
              "  small leaks matter because the gas is so potent: gas",
              "  handling, recovery at end of life, and the SF6-free",
              "  alternatives (vacuum with dry air, other gas mixtures) are",
              "  choices with a number (ch 31, ch 53)"]
    emit("k_sf6", lines)


def wear() -> None:
    budget = 30 * 25.0 ** 2    # kA^2: 30 interruptions at rated current (teaching)
    rows = [("load switching, 0.4 kA", 0.4, 2000), ("feeder faults, 6 kA", 6.0, 10),
            ("close-in faults, 12 kA", 12.0, 3)]
    used = sum(i * i * n for _, i, n in rows)
    lines = ["contact wear counted as the sum of I^2 interrupted (teaching model):",
             f"  budget: 30 interruptions at 25 kA = {budget:,.0f} kA^2",
             "  duty over 25 years              kA each   count   kA^2 total"]
    lines += [f"  {a:30s} {i:7.1f}   {n:5d}   {i * i * n:10.0f}" for a, i, n in rows]
    lines += [f"  used {used:,.0f} kA^2 = {used / budget:.0%} of the budget",
              "  thirteen faults wear the contacts more than two thousand",
              "  load operations; the exponent (2 here) is the maker's wear",
              "  model; the relay's counter of interrupted current tells",
              "  maintenance when to inspect the interrupter, not the",
              "  calendar alone (ch 52)"]
    emit("k_wear", lines)


if __name__ == "__main__":
    busbar()
    dc_component()
    internal_arc()
    sf6()
    wear()
