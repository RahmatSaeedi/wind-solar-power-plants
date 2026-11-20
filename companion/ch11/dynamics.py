"""Chapter 11, section A (control dynamics): the rotor as a flywheel driven
by the aerodynamic torque and braked by the generator torque.

Region 2: the k omega^2 law after a wind step and in turbulent wind (how
much energy a heavy rotor loses by tracking the optimum tip-speed ratio
late). Region 3: the sensitivity of rotor torque to pitch at each wind
speed, PI pitch gains by pole placement, gain scheduling, and a gust.

Run from the project root:   python -m companion.ch11.dynamics
Writes companion/ch11/expected/g_*.txt and diagrams/data/ch11-*.csv.
Teaching values A-228 (fictional); quasi-steady aerodynamics (Cp tables
from BEM), no dynamic inflow, no tower or drivetrain flexibility.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from companion.ch11 import rotor
from companion.ch11.common import csv, emit
from plantp import wind as w

J_TOTAL = 36.0e6    # kg m2: rotor 32.0e6 + generator reflected 4.0e6 (A-228)
RHO = rotor.RHO_SITE
LAM = np.arange(2.0, 16.01, 0.25)
PITCH = np.arange(0.0, 36.01, 1.0)


@lru_cache(maxsize=1)
def cp_table() -> RegularGridInterpolator:
    cp = np.array([[w.bem(rotor.blade(), float(lam), float(p)).cp
                    for p in PITCH] for lam in LAM])
    return RegularGridInterpolator((LAM, PITCH), cp, bounds_error=False,
                                   fill_value=None)


# [start: aero]
def aero_torque(v: float, omega: float, pitch_deg: float) -> float:
    """Rotor torque (N m) from the quasi-steady Cp table."""
    lam = min(max(omega * rotor.RADIUS / v, LAM[0]), LAM[-1])
    cp = float(cp_table()((lam, min(max(pitch_deg, 0.0), PITCH[-1]))))
    return 0.5 * RHO * rotor.AREA * v ** 3 * cp / omega
# [end: aero]


def k_law(rho: float = RHO) -> float:
    lam, cp = rotor.tsr_opt(), w.bem(rotor.blade(), rotor.tsr_opt()).cp
    return 0.5 * rho * rotor.AREA * rotor.RADIUS ** 3 * cp / lam ** 3


# [start: region2]
def simulate_region2(wind, dt: float, j: float = J_TOTAL):
    """J d(omega)/dt = T_aero - k omega^2, Euler steps; returns omega and
    electrical power (W) for each time step."""
    t = rotor.turbine()
    k = k_law()
    omega = rotor.tsr_opt() * wind[0] / rotor.RADIUS
    om, pe = np.empty(len(wind)), np.empty(len(wind))
    for n, v in enumerate(wind):
        tg = k * omega ** 2
        omega += dt * (aero_torque(v, omega, 0.0) - tg) / j
        omega = min(max(omega, t.omega_min), t.omega_max)
        om[n], pe[n] = omega, t.eta * tg * omega
    return om, pe
# [end: region2]


def step() -> None:
    dt = 0.05
    tt = np.arange(0.0, 150.0, dt)
    wind = np.where(tt < 20.0, 7.0, 9.0)
    om, pe = simulate_region2(wind, dt)
    w0, w1 = om[int(19.0 / dt)], om[-1]
    t63 = tt[np.argmax(om >= w0 + 0.632 * (w1 - w0))] - 20.0
    # linear time constant: tau = J / (dTg/domega - dTa/domega)
    k, eps = k_law(), 1e-4
    ta = (aero_torque(9.0, w1 + eps, 0)
          - aero_torque(9.0, w1 - eps, 0)) / (2 * eps)
    tau = J_TOTAL / (2 * k * w1 - ta)
    ideal = 0.94 * 0.5 * RHO * rotor.AREA * 9.0 ** 3 * \
        w.bem(rotor.blade(), rotor.tsr_opt()).cp
    rows = [(f"{x:.1f}", f"{y * 30 / math.pi:.3f}", f"{p / 1e6:.4f}")
            for x, y, p in zip(tt[::10], om[::10], pe[::10])]
    csv("ch11-step.csv", "t,rpm,mw", rows)
    lines = [f"region 2 after a wind step 7 -> 9 m/s (J {J_TOTAL / 1e6:.0f}e6"
             f" kg m2, rho {RHO}, A-228):",
             f"  rotor speed {w0 * 30 / math.pi:.2f} ->"
             f" {w1 * 30 / math.pi:.2f}"
             f" rpm; 63 % reached after {t63:.1f} s",
             f"  linear estimate tau = J / (2 k omega - dTa/domega) ="
             f" {tau:.1f} s",
             f"  power just after the step {pe[int(20.5 / dt)] / 1e3:,.0f} kW,"
             f" final {pe[-1] / 1e3:,.0f} kW (ideal {ideal / 1e3:,.0f} kW)",
             "  the generator torque follows the speed, not the wind: the",
             "  rotor first speeds up on the surplus aerodynamic torque and",
             "  the power rises with it (the rotor stores energy meanwhile)"]
    emit("g_step", lines)


def turbulent_wind(mean: float, ti: float, tau_s: float, dt: float,
                   duration: float, seed: int) -> np.ndarray:
    """First-order (AR(1)) wind series with the given mean, intensity and
    time scale: a teaching stand-in for a rotor-averaged turbulent wind."""
    rng = np.random.default_rng(seed)
    n = int(duration / dt)
    phi = math.exp(-dt / tau_s)
    x = np.empty(n)
    x[0] = 0.0
    e = rng.standard_normal(n) * math.sqrt(1 - phi ** 2)
    for k in range(1, n):
        x[k] = phi * x[k - 1] + e[k]
    return mean * (1 + ti * x / x.std())


def tracking() -> None:
    dt = 0.05
    lines = ["region 2 tracking in turbulent wind (1800 s, AR(1) time scale"
             " 10 s, A-228):",
             "  mean m/s  TI    inertia   captured / ideal   tracking loss"]
    cp_max = w.bem(rotor.blade(), rotor.tsr_opt()).cp
    for mean, ti in ((6.0, 0.10), (7.0, 0.10), (7.0, 0.16)):
        wind = turbulent_wind(mean, ti, 10.0, dt, 1800.0, seed=61)
        ideal = (0.94 * 0.5 * RHO * rotor.AREA * wind ** 3 * cp_max).sum()
        for scale, name in ((1.0, "J"), (0.25, "J/4")):
            j = J_TOTAL * scale
            om, pe = simulate_region2(wind, dt, j)
            # energy left in (or taken from) the rotor between the ends
            stored = 0.94 * 0.5 * j * (om[-1] ** 2 - om[0] ** 2) / dt
            r = (pe.sum() + stored) / ideal
            lines.append(f"  {mean:4.1f}      {ti:.2f}  {name:7s}   {r:.4f}"
                         f"             {100 * (1 - r):.2f} %")
    lines += ["  the energy stored in the rotor at the end is counted back;",
              "  a heavier rotor follows the gusts later and loses more, yet",
              "  the loss stays small: the rotor-averaged wind is smooth",
              "  compared with the rotor's time constant of a few seconds"]
    emit("g_tracking", lines)


def operating_point(v: float):
    return w.operate(rotor.turbine(), v, RHO)


def sensitivities(v: float):
    """dT/dpitch (N m per rad) and dT/domega (N m s) at the steady point."""
    op = operating_point(v)
    om, th = op.omega, op.pitch
    h = 0.25
    dth = (aero_torque(v, om, th + h) - aero_torque(v, om, th - h)) / \
        math.radians(2 * h)
    e = 1e-3
    dom = (aero_torque(v, om + e, th) - aero_torque(v, om - e, th)) / (2 * e)
    return op, dth, dom


# [start: gains]
def pi_gains(g: float, d: float, wn: float = 0.6, zeta: float = 0.7):
    """Pole placement for J s^2 + (D + G Kp) s + G Ki = 0 with
    G = -dT/dpitch and D = -dT/domega (both per rad)."""
    kp = (2 * zeta * wn * J_TOTAL - d) / g
    ki = J_TOTAL * wn ** 2 / g
    return kp, ki
# [end: gains]


def schedule() -> tuple[float, float, float]:
    vs = [12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0]
    lines = ["region 3: rotor torque sensitivity to pitch at rated speed"
             f" (rho {RHO}):",
             "  v m/s  pitch deg  dT/dpitch kN m/deg  dT/domega MN m s"
             "   Kp s   Ki"]
    pts = []
    for v in vs:
        op, dth, dom = sensitivities(v)
        kp, ki = pi_gains(-dth, -dom)
        pts.append((op.pitch, -dth))
        per_deg = dth * math.pi / 180 / 1e3
        lines.append(f"  {v:5.1f}  {op.pitch:6.2f}     {per_deg:9.1f}"
                     f"          {dom / 1e6:8.2f}        {kp:.3f}  {ki:.3f}")
    th = np.array([p[0] for p in pts])
    g = np.array([p[1] for p in pts])
    slope, g0 = np.polyfit(th, g, 1)
    deg = math.pi / 180 / 1e3
    lines += [f"  linear fit: G = {g0 * deg:.1f} + {slope * deg:.1f} x pitch"
              " (kN m/deg, pitch in deg),",
              "    almost proportional to pitch on this rotor",
              f"  G at 24 m/s is {g[-1] / g[0]:.1f} times G at 12 m/s:"
              " gains tuned at 12 m/s are",
              "  multiplied by the factor G(pitch_12) / G(pitch)"]
    # fixed gains (tuned at 12 m/s) at 22 m/s, linear model
    _, d12, w12 = sensitivities(12.0)
    kp12, ki12 = pi_gains(-d12, -w12)
    _, d22, w22 = sensitivities(22.0)
    wn22 = math.sqrt(-d22 * ki12 / J_TOTAL)
    z22 = (-w22 - d22 * kp12) / (2 * J_TOTAL * wn22)
    f_tower = 0.215 * 2 * math.pi
    lines += [f"  fixed gains at 22 m/s: natural frequency {wn22:.2f} rad/s,"
              f" damping {z22:.2f}",
              f"    (design 0.60 rad/s and 0.70; tower {f_tower:.2f} rad/s)"]
    emit("g_schedule", lines)
    pitch12 = operating_point(12.0).pitch
    return (g0, slope, pitch12), kp12, ki12


# [start: region3]
def simulate_gust(wind, dt: float, kp: float, ki: float, sched=None):
    """Constant generator torque, PI pitch on rotor speed error; with
    sched = (g0, slope, pitch_ref) the gains are multiplied by
    G(pitch_ref) / G(pitch). Pitch rate limit 8 deg/s, range 0 .. 35 deg.
    The integrator holds pitch in radians; returns omega, pitch (deg)."""
    t = rotor.turbine()
    op = operating_point(float(wind[0]))
    om_r, tg = t.omega_max, t.rated_w / (t.eta * t.omega_max)
    omega, pitch = om_r, op.pitch
    integ = math.radians(pitch)              # integral part of the command
    om, pt = np.empty(len(wind)), np.empty(len(wind))
    for n, v in enumerate(wind):
        e = omega - om_r
        gk = 1.0
        if sched:
            g0, slope, p_ref = sched
            gk = (g0 + slope * p_ref) / (g0 + slope * pitch)
        integ += gk * ki * e * dt
        cmd = math.degrees(gk * kp * e + integ)
        cmd = min(max(cmd, 0.0), 35.0)
        pitch += min(max(cmd - pitch, -8.0 * dt), 8.0 * dt)
        omega += dt * (aero_torque(v, omega, pitch) - tg) / J_TOTAL
        om[n], pt[n] = omega, pitch
    return om, pt
# [end: region3]


def gust(sched, kp12: float, ki12: float) -> None:
    dt = 0.02
    tt = np.arange(0.0, 60.0, dt)
    wind = np.interp(tt, [0, 10, 14, 60], [18.0, 18.0, 23.0, 23.0])
    om_f, pt_f = simulate_gust(wind, dt, kp12, ki12)
    om_s, pt_s = simulate_gust(wind, dt, kp12, ki12, sched)
    _, d12, w12 = sensitivities(12.0)
    kp8, ki8 = pi_gains(-d12, -w12, wn=0.8)
    om_8, pt_8 = simulate_gust(wind, dt, kp8, ki8, sched)
    rpm = 30 / math.pi
    om_r = rotor.turbine().omega_max
    rows = [(f"{a:.2f}", f"{b:.2f}", f"{c * rpm:.3f}", f"{d * rpm:.3f}",
             f"{e:.2f}", f"{f:.2f}")
            for a, b, c, d, e, f in zip(tt[::10], wind[::10], om_f[::10],
                                        om_s[::10], pt_f[::10], pt_s[::10])]
    csv("ch11-gust.csv", "t,v,rpm_fixed,rpm_sched,pitch_fixed,pitch_sched",
        rows)

    def row(name, om, pt):
        rate = np.abs(np.diff(pt)) / dt
        return (f"  {name:15s}  {om.max() * rpm:6.2f}    "
                f"{100 * (om.max() / om_r - 1):5.2f} %    {rate.max():5.2f}"
                f"          {np.abs(np.diff(pt)).sum():5.1f}")

    lines = ["gust 18 -> 23 m/s in 4 s at rated speed (teaching gust, A-228):",
             "  controller       peak rpm  overspeed  max pitch rate  pitch"
             " travel",
             "                                         deg/s           deg",
             row("fixed (12 m/s)", om_f, pt_f),
             row("scheduled 0.6", om_s, pt_s),
             row("scheduled 0.8", om_8, pt_8),
             f"  pitch {pt_s[0]:.1f} -> {pt_s[-1]:.1f} deg in all cases;"
             " limit 8 deg/s",
             "  fixed gains are stiffer at high wind: less overspeed but a",
             "  loop frequency that drifts towards the tower's (not modelled",
             "  here); with the schedule the designer chooses the frequency",
             "  once (0.6 or 0.8 rad/s) and it holds at every wind speed"]
    emit("g_gust", lines)


if __name__ == "__main__":
    step()
    tracking()
    sched, kp12, ki12 = schedule()
    gust(sched, kp12, ki12)
