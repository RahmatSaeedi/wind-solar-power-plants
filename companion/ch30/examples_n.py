"""Chapter 30, lesson N: more on loads and response - the sun tilting the
tower, a Rayleigh estimate of the stepped tower's frequency (with the
walls before and after the fatigue check), dynamic amplification near
resonance, what a wake does to fatigue, and the tilt budget of a tower.

Run from the project root:   python -m companion.ch30.examples_n
Writes companion/ch30/expected/n_*.txt and diagrams/data/ch30-daf.csv.
Teaching values (A-356, A-359); the maker's model and the type
certificate decide.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st

E = src.STEEL["e"]
RHO = src.STEEL["rho"]


def thermal_tilt() -> None:
    h = 100.0
    lines = ["the sun bends the tower: one side warmer than the other",
             "  top deflection = alpha dT H^2 / (2 D) for a tube of diameter D",
             "  dT K    D m    top deflection mm"]
    d_mean = 3.75
    for dt in (5, 10, 15):
        y = src.STEEL["alpha"] * dt * h * h / (2 * d_mean)
        lines.append(f"  {dt:4d}   {d_mean:4.2f}   {y * 1000:17.0f}")
    lines += ["  a 10 K difference moves the top about 16 cm - more than",
              "  the verticality tolerance; towers are surveyed at dawn",
              "  or in overcast weather, with the turbine yawed and still,",
              "  and the temperature recorded with the reading (lesson C)"]
    emit("n_thermal", lines)


def _tower(walls_mm) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Discretise the tower in 1 m pieces: heights, EI, mass a metre."""
    z, ei, m = [], [], []
    base = 0.0
    for (sec, d0, d1, _t, length), t_mm in zip(src.TOWER, walls_mm):
        t = t_mm / 1000
        for k in range(int(length)):
            frac = (k + 0.5) / length
            d = d0 + (d1 - d0) * frac
            i = math.pi / 64 * (d ** 4 - (d - 2 * t) ** 4)
            a = math.pi / 4 * (d ** 2 - (d - 2 * t) ** 2)
            z.append(base + k + 0.5)
            ei.append(E * i)
            m.append(RHO * a * 1.08)             # +8 % flanges, platforms, cables
        base += length
    return np.array(z), np.array(ei), np.array(m)


def rayleigh_f(walls_mm) -> float:
    z, ei, m = _tower(walls_mm)
    h = z[-1] + 0.5
    top = src.TOP_T * 1000.0
    # deflection shape under a unit top load: curvature = (h - z) / EI
    curv = (h - z) / ei
    slope = np.cumsum(curv)                       # dz = 1 m
    y = np.cumsum(slope)
    y_top = y[-1] + slope[-1] * 0.5
    num = 1.0 * y_top
    den = np.sum(m * y * y) + top * y_top ** 2
    return math.sqrt(num / den) / (2 * math.pi)


def rayleigh() -> None:
    old = [t for (_s, _a, _b, t, _l) in src.TOWER]
    new = [50, 45, 36, 26]
    f_old, f_new = rayleigh_f(old), rayleigh_f(new)
    scaled = src.F1_FIXED * f_new / f_old
    k07 = st.rotational_stiffness(25e6, src.FOUNDATION["r"], 0.35)
    m_eff = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3          # as in lesson B
    f07 = st.frequency_with_foundation(scaled, k07, m_eff, src.HUB)
    lines = ["Rayleigh estimate of the stepped tower's frequency (fixed base)",
             "  1 m pieces, tapered diameters, +8 % mass for internals; top 271 t",
             f"  walls {old} mm (ch 11): f1 = {f_old:.3f} Hz",
             f"  walls {new} mm (fatigue, lesson B): f1 = {f_new:.3f} Hz",
             f"  ch 11's equivalent tube gave {src.F1_FIXED:.3f} Hz",
             f"  Rayleigh is an upper bound ({(f_old / src.F1_FIXED - 1) * 100:.0f} % above"
             " ch 11 here); the ratio",
             f"  is the useful result: the extra steel raises f1 by {(f_new / f_old - 1) * 100:.1f} %",
             f"  scaled to ch 11: fixed {scaled:.4f} Hz; T07 on 20 m base {f07:.3f} Hz"
             f" ({(f07 / src.ONE_P_MAX - 1) * 100:.1f} %)",
             "  the thicker walls would close T07's frequency gap - but",
             "  only the maker's final tower model may be credited, so",
             "  lesson D keeps 0.215 Hz as the conservative basis"]
    emit("n_rayleigh", lines)


def daf() -> None:
    rows = []
    lines = ["dynamic amplification of a harmonic force near resonance",
             "  r = forcing / natural frequency; zeta = damping ratio",
             "      r   zeta 0.005   zeta 0.02   zeta 0.05"]
    for r in (0.5, 0.7, 0.8, 0.9, 0.95, 1.0, 1.1, 1.3):
        vals = [1 / math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2) for z in (0.005, 0.02, 0.05)]
        rows.append((r, *vals))
        lines.append(f"  {r:5.2f}   {vals[0]:10.1f}   {vals[1]:9.1f}   {vals[2]:9.1f}")
    fine = np.linspace(0.3, 1.6, 131)
    csv("ch30-daf.csv", "r,z005,z02,z05",
        [(round(r, 3), *[round(1 / math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2), 3)
                         for z in (0.005, 0.02, 0.05)]) for r in fine])
    r_t = src.ONE_P_MAX / 0.209
    lines += [f"  T07: 1P max / f1 = {r_t:.2f} -> amplification about"
              f" {1 / math.sqrt((1 - r_t ** 2) ** 2 + (2 * 0.02 * r_t) ** 2):.0f}",
              "  near r = 1 damping alone limits the response: a parked",
              "  rotor (little aerodynamic damping) is the worst case,",
              "  which is why the margin to 1P is a stiffness rule and",
              "  the controller avoids lingering at the critical speed"]
    emit("n_daf", lines)


def wake() -> None:
    lines = ["what a wake does to fatigue (teaching: DEL scales with TI)",
             "  ambient TI 0.10; waked TI from ch 14's spacing",
             "  turbine      TI     DEL ratio   damage ratio m=3   m=5"]
    for name, ti in [("free stream", 0.10), ("one wake", 0.14), ("deep in rows", 0.17)]:
        r = ti / 0.10
        lines.append(f"  {name:12s} {ti:4.2f}   {r:9.2f}   {r ** 3:16.2f}   {r ** 5:5.2f}")
    lines += ["  a 40 % higher turbulence nearly triples the weld damage",
              "  (m = 3): the maker's load set is valid for the layout's",
              "  turbulence only, and a site suitability check confirms",
              "  that every position, waked ones included, stays inside it"]
    emit("n_wake", lines)


def tilt_budget() -> None:
    h = 100.0
    parts = [("foundation tilt limit (teaching 3 mm/m)", 3.0 / 1000 * h),
             ("erection verticality (lesson C)", 0.050),
             ("thermal, 10 K across the tower", src.STEEL["alpha"] * 10 * h * h / (2 * 3.75)),
             ("mean thrust at rated (static)", 0.45)]
    lines = ["tilt budget at the tower top (teaching, metres)"]
    for name, v in parts:
        lines.append(f"  {name:40s} {v:6.3f}")
    worst = sum(v for _, v in parts)
    rss = math.sqrt(sum(v * v for _, v in parts[:3])) + parts[3][1]
    lines += [f"  worst case sum {worst:.2f} m; independent parts RSS + thrust {rss:.2f} m",
              "  the foundation limit dominates the permanent part: a",
              "  settlement survey that shows 1 mm/m after one year is",
              "  a third of the budget gone - the trend matters (lesson C)"]
    emit("n_tilt", lines)


if __name__ == "__main__":
    thermal_tilt()
    rayleigh()
    daf()
    wake()
    tilt_budget()
