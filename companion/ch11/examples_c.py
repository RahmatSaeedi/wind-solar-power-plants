"""Chapter 11, section C - product realisation and reliability: rotor mass
and aerodynamic imbalance, tower sections with welding, inspection and
coating quantities, lightning exposure, icing hours and ice throw, and the
traceability records of one turbine.

Run from the project root:   python -m companion.ch11.examples_c
Writes companion/ch11/expected/c_*.txt.
Teaching values A-217 .. A-220 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import rotor
from companion.ch11.common import emit
from plantp import datapack, wind as w


def balance() -> None:
    s = np.array([22.00e3 * 22.0, 22.10e3 * 22.0, 21.95e3 * 22.0])  # kg m
    ang = np.radians([0.0, 120.0, 240.0])
    u = abs(np.sum(s * np.exp(1j * ang)))
    om = rotor.turbine().omega_max
    f_mass = u * om ** 2
    v, lam = 9.0, rotor.tsr_opt()
    q = 0.5 * 1.225 * v ** 2
    ct0 = w.bem(rotor.blade(), lam, 0.0).ct
    ct1 = w.bem(rotor.blade(), lam, 0.5).ct
    d_t = (ct0 - ct1) * q * rotor.AREA / 3
    emit("c_balance", [
        "rotor imbalance from blade mass and pitch errors (A-217):",
        "  blade first mass moments 484.0, 486.2, 482.9 t m (masses 22.00,",
        "    22.10, 21.95 t at 22 m)",
        f"  residual unbalance |sum S e^(j theta)| = {u:,.0f} kg m",
        f"  1P force at 11.5 rpm U w^2 = {f_mass / 1e3:.1f} kN",
        f"  one blade pitched 0.5 deg off at 9 m/s: its thrust changes by "
        f"{d_t / 1e3:.1f} kN,",
        f"    a 1P moment of about {d_t * 2 / 3 * rotor.RADIUS / 1e3:,.0f} kN m"
        " on the hub",
        "  the aerodynamic error can outweigh the mass error: blades are",
        "  weighed and matched in sets in the factory, and pitch angles",
        "  are set and checked on site (photogrammetry, laser tools)"])


def tower_sections() -> None:
    n_sec, length = 4, 25.0                        # A-218
    d_top, d_base = 3.0, 4.5
    t_top, t_base = 0.022, 0.050
    can = 2.5
    lines = ["tower in four 25 m sections, cans 2.5 m (A-218):",
             "  section  D base..top m  t mm  mass t  circ. welds  long."
             " weld m"]
    tot_m, tot_area, tot_circ, tot_long = 0.0, 0.0, 0.0, 0.0
    for k in range(n_sec):
        z0, z1 = k * length, (k + 1) * length
        d0 = d_base + (d_top - d_base) * z0 / 100
        d1 = d_base + (d_top - d_base) * z1 / 100
        t = t_base + (t_top - t_base) * (z0 + z1) / 200
        dm = 0.5 * (d0 + d1)
        mass = math.pi * dm * t * length * 7850 / 1e3
        n_can = int(length / can)
        circ = (n_can - 1 + 2) * math.pi * dm          # + 2 flange welds
        longw = n_can * can
        tot_m += mass
        tot_area += 2 * math.pi * dm * length
        tot_circ += circ
        tot_long += longw
        lines.append(f"  {k + 1:7d}  {d0:5.2f}..{d1:4.2f}     {1e3 * t:4.0f}  "
                     f"{mass:6.0f}  {circ:8.0f} m     {longw:8.0f}")
    paint = tot_area * 320e-6 / 0.70 / 0.60 * 1e3    # litres, 320 um DFT
    lines += [f"  total {tot_m:.0f} t steel; welds {tot_circ:.0f} m circumferential,"
              f" {tot_long:.0f} m longitudinal",
              f"  coated area inside and outside {tot_area:,.0f} m2; paint for "
              f"320 um dry film at",
              f"    70 % solids and 60 % transfer efficiency: {paint:,.0f} L"
              " per tower",
              "  base diameter 4.5 m is near the limit of road transport",
              "  under bridges; larger towers use split or concrete sections"]
    emit("c_tower", lines)


def lightning() -> None:
    ng, h = 2.0, 175.0                               # flashes/km2/yr, tip
    area = 9 * math.pi * h ** 2 / 1e6
    n = ng * area
    emit("c_lightning", [
        "lightning exposure of one turbine (A-219, rough estimate):",
        f"  ground flash density {ng} per km2 a year; tip height {h:.0f} m",
        f"  equivalent collection area 9 pi H^2 = {area:.2f} km2",
        f"  expected flashes {n:.1f} a year per turbine, {12 * n:.0f} for twelve",
        "  tall rotating structures also launch upward flashes that this",
        "  simple estimate omits; the risk method and protection levels",
        "  of the turbine standard (IEC 61400-24:2019) govern the design"])


def icing() -> None:
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy(float)
    v = h["ws_100m_ms"].to_numpy(float)
    cold = (t <= 0.0) & (v >= 3.0)
    d = 1.5 * (2 * rotor.RADIUS + rotor.HUB)
    emit("c_icing", [
        "icing screen from the data pack (A-220):",
        f"  hours at or below 0 C with wind above cut-in: {int(cold.sum())}"
        f" ({100 * cold.mean():.1f} % of the year)",
        "  ice also needs moisture (cloud, fog, freezing rain): the pack",
        "  has no humidity, so this is an upper bound (U-040)",
        f"  rule-of-thumb ice-throw distance 1.5 (D + H) = {d:.0f} m for an",
        "    operating turbine: roads, buildings and the PV field inside it",
        "    need an ice risk assessment and a stop-on-ice control",
        "  iced blades lose lift and gain mass: power drops and the rotor",
        "  becomes unbalanced; ice detection stops or derates the turbine"])


def records() -> None:
    items = {"blades": 3, "hub and pitch bearings": 4, "pitch drives and"
             " batteries": 6, "main bearing and shaft": 2, "gearbox": 1,
             "generator": 1, "converter cabinets": 3, "transformer": 1,
             "yaw bearing and drives": 7, "tower sections": 4,
             "anchor bolt cage": 1, "controller and safety system": 2}
    n = sum(items.values())
    emit("c_records", [
        f"serialised main components of one turbine (A-220): {n}",
        f"  twelve turbines: {12 * n} serial numbers to trace, each with",
        "  material certificates, inspection reports, test records and",
        "  non-conformance history; plus every bolt-tensioning record",
        "  of the tower and blade-root joints",
        "  the records are the turbine's memory: warranty claims, serial",
        "  defect campaigns and life extension all start from them"])


if __name__ == "__main__":
    balance()
    tower_sections()
    lightning()
    icing()
    records()
