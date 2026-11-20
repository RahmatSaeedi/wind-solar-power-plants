"""Appendix B - conversion factors and constants, each computed with the
book's unit library (plantp.units) and physics module, so the table
prints exactly what the companion code uses.

Run from the project root:   python -m companion.appx.appendix_b
Writes companion/appx/expected/appb_conv.txt and appb_const.txt.
"""
from __future__ import annotations

from companion.appx.common import emit
from plantp import physics, units

CONVERSIONS = [   # (value, from, to, note)
    (1, "kWh", "MJ", "energy"),
    (1, "MWh", "GJ", "energy"),
    (1, "toe", "MWh", "tonne of oil equivalent"),
    (1, "Btu", "kJ", "data sheets"),
    (1, "kcal", "kJ", "thermochemical calorie"),
    (1, "eV", "J", "photon and band-gap energy"),
    (1, "Ah", "C", "cell capacity"),
    (1, "bar", "kPa", "pressure"),
    (1, "psi", "kPa", "data sheets"),
    (1, "mm", "in", "length"),
    (1, "ft", "m", "length"),
    (1, "mi", "km", "length"),
    (1, "nmi", "km", "nautical mile"),
    (1, "km/h", "m/s", "speed"),
    (1, "kn", "m/s", "speed, aviation and sea"),
    (1, "mph", "m/s", "speed"),
    (1, "lb", "kg", "mass"),
    (1, "lbf", "N", "force"),
    (1, "ha", "m^2", "area"),
    (1, "km^2", "ha", "area"),
    (1, "L", "m^3", "volume"),
    (1, "deg", "rad", "plane angle"),
    (1, "rad", "deg", "plane angle"),
    (1, "kW/m^2", "W/m^2", "irradiance"),
    (1, "kWh/m^2", "MJ/m^2", "irradiation"),
    (1, "d", "h", "time"),
]


def conversions() -> list:
    lines = ["conversion factors computed with plantp.units.convert",
             f"  {'from':>10s}  {'to':10s} {'factor':>16s}  note"]
    out = []
    for v, a, b, note in CONVERSIONS:
        f = units.convert(v, a, b)
        out.append((a, b, f))
        lines.append(f"  {('1 ' + a):>10s}  {b:10s} {f:16.8g}  {note}")
    lines += ["  temperature is an offset, not a factor:",
              f"    T(K) = t(C) + 273.15; 25 C = {units.kelvin(25):.2f} K",
              "    a temperature DIFFERENCE of 1 C equals 1 K"]
    emit("appb_conv", lines)
    return out


def constants() -> dict:
    rho0 = 101325.0 / (physics.R_DRY * 288.15)
    p1000 = float(physics.standard_pressure(1000.0))
    rows = [("speed of light in vacuum", "c", physics.C_LIGHT, "m/s", "exact"),
            ("Planck constant", "h", physics.H_PLANCK, "J s", "exact"),
            ("elementary charge", "e", physics.Q_E, "C", "exact"),
            ("Boltzmann constant", "k", physics.K_BOLTZ, "J/K", "exact"),
            ("Stefan-Boltzmann constant", "sigma", physics.SIGMA_SB, "W/(m2 K4)",
             "from exact constants"),
            ("molar gas constant", "R", 8.314462618, "J/(mol K)", "from exact constants"),
            ("magnetic constant (as used)", "mu0", physics.MU0, "H/m", "4 pi 1e-7"),
            ("standard acceleration of gravity", "g_n", physics.G0, "m/s2", "defined"),
            ("specific gas constant, dry air", "R_d", physics.R_DRY, "J/(kg K)",
             "value used in the book"),
            ("air density, 1013.25 hPa and 15 C", "rho_0", rho0, "kg/m3",
             "computed: p/(R_d T)"),
            ("pressure at 1000 m, standard lapse", "p", p1000, "hPa",
             "computed: physics.standard_pressure")]
    lines = ["constants as the companion code holds them"]
    for name, sym, val, unit, note in rows:
        lines.append(f"  {name:36s} {sym:6s} {val:.10g} {unit}")
        lines.append(f"      {note}")
    emit("appb_const", lines)
    return dict(rho0=rho0, p1000=p1000)


if __name__ == "__main__":
    conversions()
    constants()
