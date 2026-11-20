"""Chapter 11, sections B and C (structure, yaw and availability in
numbers): stresses at the tower base, the bolted base flange and why its
flatness matters, yaw activity from the data-pack directions, and time-
versus energy-based availability from simulated failures.

Run from the project root:   python -m companion.ch11.examples_g
Writes companion/ch11/expected/k_*.txt.
Teaching values A-235 .. A-238 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import lab_d, rotor
from companion.ch11.common import emit

G = 9.81
EXTREME = 2.0           # teaching ratio of extreme to peak operating load


# --------------------------------------------------------------- tower base
def tower_base() -> None:
    """Thin-walled tube at the base: D 4.5 m, t 46 mm (A-218, A-235)."""
    d, t = 4.5, 0.046
    r = d / 2
    area = math.pi * d * t
    w_sec = math.pi * r ** 2 * t                 # elastic section modulus
    thrust = max(o.thrust_n for o in rotor.curve(rotor.RHO0))
    m_op = thrust * rotor.HUB
    weight = (271 + 340) * 1e3 * G
    s_bend = m_op / w_sec
    s_axial = weight / area
    lines = [f"tower base, D {d} m, wall {1e3 * t:.0f} mm (A-235):",
             f"  peak operating thrust {thrust / 1e3:.0f} kN x hub {rotor.HUB:.0f}"
             f" m = {m_op / 1e6:.1f} MN m",
             f"  bending stress M / (pi r^2 t) = {s_bend / 1e6:.0f} MPa;"
             f" weight {weight / 1e6:.2f} MN gives {s_axial / 1e6:.1f} MPa",
             f"  teaching extreme ({EXTREME:.0f} x operating):"
             f" {EXTREME * s_bend / 1e6 + s_axial / 1e6:.0f} MPa, against"
             " 355 MPa yield",
             f"    of S355 steel: utilisation {(EXTREME * s_bend + s_axial) / 355e6:.2f}"
             " before partial factors",
             "  a thin shell this size fails by local buckling before yield;",
             "  the buckling check, the fatigue of welds and flanges and the",
             "  door opening are the real sizing checks (chapter 30)"]
    emit("k_tower", lines)


# --------------------------------------------------------------- base flange
def flange() -> None:
    """Bolted ring flange (A-236, teaching): 120 bolts on a 4.30 m pitch
    circle, preload 1.6 MN each, joint load factor 0.12 while the joint
    stays closed (the bolt takes 12 % of a load change)."""
    n, d_b, preload, phi = 120, 4.30, 1.6e6, 0.12
    thrust = max(o.thrust_n for o in rotor.curve(rotor.RHO0))
    m_op = thrust * rotor.HUB
    weight = (271 + 340) * 1e3 * G
    f_ext = 4 * m_op / (n * d_b) - weight / n     # tension on the worst bolt
    f_ext_x = 4 * EXTREME * m_op / (n * d_b) - weight / n
    closed = preload + phi * f_ext
    lines = ["bolted base flange (A-236, teaching values):",
             f"  {n} bolts on a {d_b} m circle, preload {preload / 1e6:.1f} MN"
             " each",
             f"  external pull on the worst bolt: {f_ext / 1e3:.0f} kN at"
             f" peak thrust,",
             f"    {f_ext_x / 1e3:,.0f} kN at the extreme; the joint stays"
             f" closed below {preload / (1 - phi) / 1e3:,.0f} kN",
             f"  joint closed: bolt force {preload / 1e6:.2f} -> {closed / 1e6:.3f}"
             f" MN; the bolt sees {phi * f_ext / 1e3:.0f} kN of change",
             "  a turn of the rotor or a gust repeats that change: with a",
             f"  closed joint the bolt's fatigue range is {phi * 100:.0f} % of the"
             " load range",
             "  if the flanges are not flat, the joint opens on one side: the",
             "  bolt then takes the whole load change plus bending, and its",
             "  fatigue life drops by orders of magnitude (S-N slope)",
             f"  with m = 3: range x {1 / phi:.1f} -> damage x"
             f" {(1 / phi) ** 3:,.0f}",
             "  flatness tolerances after welding, preload by a controlled",
             "  method and re-checks after the first months are the evidence"]
    emit("k_flange", lines)


# --------------------------------------------------------------- yaw activity
def yaw_activity() -> None:
    """Yaw demand from hourly directions (A-237): a lower bound, since the
    hourly mean hides minute-scale changes."""
    v, wd, _ = lab_d.hourly()
    run = v[1:] > 3.0
    dwd = (np.diff(wd) + 180.0) % 360.0 - 180.0
    moves = run & (np.abs(dwd) > 8.0)            # outside the dead band
    total = np.abs(dwd[moves]).sum()
    rate = 0.5                                   # deg/s
    twist = np.cumsum(np.where(run, dwd, 0.0))
    unwinds, ref = 0, 0.0
    for x in twist:
        if abs(x - ref) > 900.0:                 # 2.5 turns of cable twist
            unwinds += 1
            ref = x
    lines = ["yaw demand from the data-pack hourly directions (A-237):",
             f"  hours with wind above cut-in and a change over 8 deg:"
             f" {moves.sum():,}",
             f"  yaw travel at least {total:,.0f} deg a year"
             f" = {total / 360:.0f} full turns",
             f"  at {rate} deg/s: {total / rate / 3600:.1f} h of yaw motor time"
             " (lower bound)",
             f"  net cable twist reaches 2.5 turns: {unwinds} unwind(s) a"
             " year",
             "  real yaw systems act on ten-minute or shorter averages and",
             "  move many times more often; brakes, motors and the yaw",
             "  bearing's gear are sized for that duty"]
    emit("k_yaw", lines)


# --------------------------------------------------------------- availability
FAILURES = [  # name, failures per turbine-year, downtime h, load driven
    ("pitch system", 0.5, 24, True), ("converter", 0.4, 36, True),
    ("control and sensors", 0.8, 12, False), ("yaw system", 0.2, 24, False),
    ("hydraulics", 0.3, 24, False), ("generator", 0.10, 240, True),
    ("gearbox (major)", 0.05, 1440, True), ("blade repair", 0.05, 480, False),
]


def availability(years: int = 2000, seed: int = 83) -> None:
    """Failures as Poisson events (A-238, fictional rates); a load-driven
    failure is more likely to start in a windy hour (weight = power)."""
    v, _, rho = lab_d.hourly()
    v_eq = np.asarray(v) * (np.asarray(rho) / rotor.RHO0) ** (1 / 3)
    vg, _, sm, _ = rotor.curve_arrays()
    p = np.interp(v_eq, vg, sm)
    n = len(p)
    rng = np.random.default_rng(seed)
    w_load = p / p.sum()
    down_h = lost = 0.0
    for _ in range(years):
        out = np.zeros(n, bool)
        for _, rate, hours, load in FAILURES:
            for _ in range(rng.poisson(rate)):
                k = int(rng.choice(n, p=w_load)) if load else int(rng.integers(n))
                out[k:k + hours] = True
        down_h += out.sum()
        lost += p[out].sum()
    t_av = 1 - down_h / (years * n)
    e_av = 1 - lost / (years * p.sum())
    # scheduled service: 48 h a year in the calmest or a random month
    month = np.repeat(np.arange(12), np.ceil(n / 12))[:n]
    mean_m = np.array([p[month == m].mean() for m in range(12)])
    calm, windy = int(np.argmin(mean_m)), int(np.argmax(mean_m))
    lines = ["availability from simulated failures, one turbine,"
             f" {years} years (A-238):",
             "  rates and downtimes are fictional teaching values",
             f"  time-based availability   {100 * t_av:.2f} %",
             f"  energy-based availability {100 * e_av:.2f} %",
             f"  energy lost a year: {(1 - e_av) * p.sum() / 1e3:,.0f} MWh of"
             f" {p.sum() / 1e3:,.0f} MWh",
             "  load-driven failures start more often in windy hours, so",
             "  energy availability is lower than time availability",
             f"  48 h of service in the calmest month ({calm + 1}):"
             f" {48 * mean_m[calm] / 1e3:.0f} MWh lost;",
             f"    in the windiest month ({windy + 1}):"
             f" {48 * mean_m[windy] / 1e3:.0f} MWh",
             "  the gearbox's few long stops (crane, parts) dominate the",
             "  energy loss: spares and crane access are availability levers"]
    emit("k_availability", lines)
    share = []
    for name, rate, hours, _ in FAILURES:
        share.append((name, rate * hours))
    tot = sum(s for _, s in share)
    lines2 = ["expected downtime by subsystem (rate x hours, A-238):",
              "  subsystem              failures/yr  hours each  h/yr   share"]
    for (name, rate, hours, _), (_, s) in zip(FAILURES, share):
        lines2.append(f"  {name:22s} {rate:6.2f}      {hours:6d}    {s:6.1f}"
                      f"  {100 * s / tot:5.1f} %")
    lines2.append(f"  total {tot:.0f} h a year = {100 * tot / 8760:.2f} % of the"
                  " year (before overlaps)")
    emit("k_downtime", lines2)


if __name__ == "__main__":
    tower_base()
    flange()
    yaw_activity()
    availability()
