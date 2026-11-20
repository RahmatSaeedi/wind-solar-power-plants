"""Chapter 11, section B - turbine architecture and loads: subassembly
masses, drivetrain torque for three architectures, blade-root and tower
loads, rainflow counting and damage-equivalent loads of a synthetic
ten-minute signal, the Campbell diagram with the tower frequency, and a
site-suitability screen.

Run from the project root:   python -m companion.ch11.examples_b
Writes companion/ch11/expected/b_*.txt and diagrams/data/ch11-*.csv.
Teaching values A-214 .. A-216 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import rotor
from companion.ch11.common import csv, emit
from plantp import datapack, wind as w

G = 9.81
MASS = {                                         # A-214, tonnes
    "blades (3 x 22 t)": 66.0, "hub with pitch system": 45.0,
    "nacelle with drivetrain": 160.0, "tower (100 m steel)": 340.0,
    "foundation (concrete and steel)": 1700.0}


def tree_masses() -> None:
    top = MASS["blades (3 x 22 t)"] + MASS["hub with pitch system"] + \
        MASS["nacelle with drivetrain"]
    lines = ["subassembly masses of one WT-5.0-150 (A-214, teaching values):"]
    for k, m in MASS.items():
        lines.append(f"  {k:33s} {m:7.0f} t")
    lines += [f"  tower-top mass (rotor + nacelle) {top:.0f} t; above foundation "
              f"{top + MASS['tower (100 m steel)']:.0f} t",
              "  the foundation weighs more than everything above it: it",
              "  must resist the overturning moment, not only the weight"]
    emit("b_masses", lines)


def drivetrain() -> None:
    op = {o.v: o for o in rotor.curve()}[12.0]
    q = op.torque_nm
    lines = [f"main-shaft torque at rated: {q / 1e6:.2f} MN m at "
             f"{op.omega * 30 / math.pi:.1f} rpm (A-211)",
             "  architecture              generator rpm   ratio   generator"
             " torque"]
    for name, n_gen in (("geared, high speed (D-011)", 1155.0),
                        ("geared, medium speed", 400.0),
                        ("direct drive", op.omega * 30 / math.pi)):
        ratio = n_gen / (op.omega * 30 / math.pi)
        lines.append(f"  {name:26s}  {n_gen:13.1f}   {ratio:5.1f}   "
                     f"{q / ratio / 1e3:9.0f} kN m")
    lines += ["  a machine's active volume grows with its torque (chapter 8):",
              "  the direct-drive generator is about a hundred times larger",
              "  than the high-speed one; the gearbox moves that size into",
              "  gears and bearings that need oil, cooling and maintenance"]
    emit("b_drivetrain", lines)


def loads() -> None:
    ops = rotor.curve()
    peak = max(ops, key=lambda o: o.thrust_n)
    m_b, r_cg = 22e3, 22.0                              # A-214
    om = rotor.turbine().omega_max
    grav = m_b * G * r_cg
    cent = m_b * om ** 2 * r_cg
    flap = peak.thrust_n / 3 * 2 / 3 * rotor.RADIUS
    tower = peak.thrust_n * rotor.HUB
    emit("b_loads", [
        "first-order loads from the operating points (A-214):",
        f"  peak rotor thrust {peak.thrust_n / 1e3:,.0f} kN at {peak.v:.1f} m/s"
        " (just below rated)",
        f"  blade-root flap moment ~ T/3 x 2R/3 = {flap / 1e6:.1f} MN m (mean)",
        f"  blade-root edge moment from gravity +-m g r_cg = "
        f"{grav / 1e6:.2f} MN m, once per turn",
        f"  centrifugal pull at 11.5 rpm m w^2 r_cg = {cent / 1e3:.0f} kN per"
        " blade",
        f"  tower-base moment from thrust T x H = {tower / 1e6:.0f} MN m",
        "  gravity reverses every turn: 20 years at about 10 rpm is of",
        "  the order of 10^8 edgewise cycles; fatigue, not one storm,",
        "  sizes much of a blade"])


def fatigue() -> None:
    rng = np.random.default_rng(53)                     # A-215, 10 Hz, 600 s
    t = np.arange(0, 600, 0.1)
    om = 9.74 * math.pi / 30                            # 9 m/s operating point
    x = np.zeros_like(t)
    for k in range(1, len(t)):                          # AR(1) turbulence
        x[k] = 0.995 * x[k - 1] + rng.normal(0, 0.25)
    m_flap = 12.5 + x + 1.0 * np.sin(om * t)            # MN m
    cyc = w.rainflow(m_flap)
    del10 = w.damage_equivalent_load(cyc, 10.0, 600.0)
    del4 = w.damage_equivalent_load(cyc, 4.0, 600.0)
    n_full = sum(c for _, c in cyc)
    big = max(s for s, _ in cyc)
    emit("b_fatigue", [
        "synthetic 10-min blade-root flap moment at 9 m/s (seed 53, A-215):",
        f"  mean {m_flap.mean():.1f} MN m, std {m_flap.std():.2f}; "
        f"{n_full:.0f} rainflow cycles, largest {big:.1f} MN m",
        f"  damage-equivalent load, 600 cycles: m = 10 (composite) "
        f"{del10:.2f} MN m;",
        f"    m = 4 (welded steel) {del4:.2f} MN m",
        "  the high S-N exponent of composites lets the few large cycles",
        "  dominate; steel details feel the many small cycles too",
        "  a design sums such signals over all wind speeds and the life"])
    edges = np.arange(0, math.ceil(big) + 1, 0.5)
    hist = np.zeros(len(edges) - 1)
    for s, c in cyc:
        k = min(int(s / 0.5), len(hist) - 1)
        hist[k] += c
    csv("ch11-rainflow.csv", "range,count",
        [(f"{e + 0.25:.2f}", f"{h:.1f}") for e, h in zip(edges[:-1], hist)])


def campbell() -> None:
    i_t = w.tube_inertia(4.4, 0.031)                    # A-216 equivalent
    mpm = math.pi * 4.4 * 0.031 * 7850
    top = sum(MASS[k] for k in list(MASS)[:3]) * 1e3
    f_t = w.tower_frequency(210e9, i_t, mpm, rotor.HUB, top)
    lo, hi = 5.0 / 60, 11.5 / 60
    lines = ["tower first bending frequency and rotor excitation (A-216):",
             f"  equivalent tube D 4.4 m, t 31 mm: I {i_t:.3f} m4, {mpm:,.0f}"
             f" kg/m; top {top / 1e3:.0f} t",
             f"  tower f1 = {f_t:.3f} Hz",
             f"  1P band {lo:.3f} .. {hi:.3f} Hz; 3P band {3 * lo:.3f} .. "
             f"{3 * hi:.3f} Hz",
             f"  margins: f1 is {100 * (f_t / hi - 1):.0f} % above 1P max and "
             f"{100 * (1 - f_t / (3 * lo)):.0f} % below 3P min",
             f"  (soft-stiff); 3P would meet f1 at {f_t / 3 * 60:.1f} rpm, just"
             " below",
             "  the 5 rpm minimum: the controller keeps the rotor out of a",
             "  narrow speed band there (an exclusion zone)",
             "  a 4.0 m, 30 mm tube would give "
             f"{w.tower_frequency(210e9, w.tube_inertia(4.0, 0.03), math.pi * 4.0 * 0.03 * 7850, rotor.HUB, top):.3f} Hz: inside the 1P band"]
    emit("b_campbell", lines)
    csv("ch11-campbell.csv", "rpm,p1,p3,ft",
        [(f"{n:.1f}", f"{n / 60:.4f}", f"{3 * n / 60:.4f}", f"{f_t:.4f}")
         for n in np.arange(0, 14.01, 0.5)])


def suitability() -> None:
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    emit("b_suitability", [
        "site suitability screen against the vendor's design values"
        " (A-216):",
        f"  annual mean at hub: site {v.mean():.2f} m/s; design 8.0 m/s ->"
        f" {'ok' if v.mean() <= 8.0 else 'exceeds'}",
        f"  air density: site mean 1.056 kg/m3 (lower density, lower loads)",
        f"  highest hourly mean in the data year {v.max():.1f} m/s; the 50-"
        "year extreme",
        "    needs long-term data and statistics (chapters 3 and 13)",
        "  turbulence intensity needs 10-minute data: the hourly pack",
        "    cannot give it (U-039); wake turbulence adds to it",
        "  the turbine supplier performs the formal site-specific load",
        "  check; the owner supplies measured site data (chapter 13)"])


if __name__ == "__main__":
    tree_masses()
    drivetrain()
    loads()
    fatigue()
    campbell()
    suitability()
