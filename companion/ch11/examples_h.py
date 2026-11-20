"""Chapter 11, section D (selection): the rotor-size trade study. Three
rotors on the same 5 MW drivetrain, each blade designed with the same
method, the same tip-speed limit and the same ground clearance; energy at
the site from the data-pack year with hourly density.

Run from the project root:   python -m companion.ch11.examples_h
Writes companion/ch11/expected/m_rotorsize.txt and
diagrams/data/ch11-rotorsize.csv. Teaching values A-239 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import lab_d, rotor
from companion.ch11.common import csv, emit
from plantp import wind as w

TIP = 90.3              # m/s, tip-speed limit of the 150 m rotor kept for all
CLEAR = 25.0            # m, lowest tip above ground
MASS_EXP = 2.5          # blade mass ~ R^2.5 (teaching scaling, A-239)


def study() -> None:
    v, _, rho = lab_d.hourly()
    lines = ["rotor-size trade study, 5 MW drivetrain, site year (A-239):",
             "  rotor m  W/m2  hub m  rated v  energy MWh  CF     peak"
             " thrust  blade t"]
    rows, base = [], None
    vg = np.arange(0.0, 30.01, 0.5)
    for radius in (68.0, 75.0, 81.0):
        blade = w.design_blade(radius=radius)
        t = w.Turbine(blade, tsr_opt=rotor.tsr_opt(), omega_max=TIP / radius)
        hub = radius + CLEAR
        shear = (hub / rotor.HUB) ** 0.2           # data pack is at 100 m
        ops = [w.operate(t, float(x), rotor.RHO0)
               for x in np.arange(3.0, 25.01, 0.5)]
        p = np.zeros_like(vg)
        for o in ops:
            p[int(round(o.v / 0.5))] = o.power_w / 1e3
        sm = w.smooth_power_curve(vg, p)
        sm[(vg > 25.0) | (vg < 2.5)] = 0.0
        v_eq = v * shear * (np.asarray(rho) / rotor.RHO0) ** (1 / 3)
        e = float(np.interp(v_eq, vg, sm).sum() / 1e3)
        rated = next(o.v for o in ops if o.power_w >= 0.999 * t.rated_w)
        thrust = max(o.thrust_n for o in ops)
        mass = 22.0 * (radius / 75.0) ** MASS_EXP
        spec = t.rated_w / (math.pi * radius ** 2)
        if radius == 75.0:
            base = (e, thrust, mass)
        rows.append((radius, spec, hub, rated, e, thrust, mass))
    for radius, spec, hub, rated, e, thrust, mass in rows:
        lines.append(f"  {2 * radius:5.0f}   {spec:4.0f}  {hub:5.0f}  {rated:6.1f}"
                     f"   {e:9,.0f}  {e / (5 * 8760):.3f}  {thrust / 1e3:7.0f} kN"
                     f"  {mass:5.1f}")
    e0, t0, m0 = base
    lines.append("  relative to the 150 m rotor:")
    for radius, _, _, _, e, thrust, mass in rows:
        lines.append(f"    {2 * radius:3.0f} m: energy {100 * (e / e0 - 1):+5.1f} %,"
                     f" thrust {100 * (thrust / t0 - 1):+5.1f} %, blade mass"
                     f" {100 * (mass / m0 - 1):+5.1f} %")
    lines += ["  a bigger rotor buys energy below rated wind; blade mass",
              "  (and cost) grows faster than the energy, while peak thrust",
              "  grows slowly because rated wind falls; fatigue loads and",
              "  tip height also grow. The choice is made on cost of energy",
              "  with the vendor's prices and loads, and on site limits",
              "  (transport, tip height, noise, export cap)"]
    emit("m_rotorsize", lines)
    csv("ch11-rotorsize.csv", "d,energy,thrust,mass",
        [(f"{2 * r:.0f}", f"{100 * (e / e0 - 1):.2f}",
          f"{100 * (t / t0 - 1):.2f}", f"{100 * (m / m0 - 1):.2f}")
         for r, _, _, _, e, t, m in rows])


if __name__ == "__main__":
    study()
