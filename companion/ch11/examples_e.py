"""Chapter 11, section A (deeper aerodynamics): the ideal rotor with wake
rotation (Glauert), the high-thrust state (Buhl), wind shear and tower
shadow seen by the rotating blades (1P and 3P), the rotor-equivalent wind
speed, and the energy cost of leading-edge erosion.

Run from the project root:   python -m companion.ch11.examples_e
Writes companion/ch11/expected/e_*.txt and diagrams/data/ch11-*.csv.
Teaching values A-226 .. A-228 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import lab_d, rotor
from companion.ch11.common import csv, emit
from plantp import wind as w


def glauert() -> None:
    lams = [0.5, 1.0, 2.0, 4.0, 6.0, 8.5, 10.0]
    lines = ["ideal rotor with wake rotation (Glauert) against the rotor of",
             "Plant P (BEM with drag and tip losses):",
             "  TSR   Glauert Cp_max   rotor Cp   rotor / Glauert"]
    rows = []
    for lam in np.arange(0.5, 12.01, 0.5):
        g = w.glauert_cp_max(float(lam))
        cp = w.bem(rotor.blade(), float(lam)).cp if lam >= 3.0 else float("nan")
        rows.append((f"{lam:.1f}", f"{g:.4f}", f"{16 / 27:.4f}",
                     "nan" if math.isnan(cp) else f"{max(cp, 0.0):.4f}"))
    for lam in lams:
        g = w.glauert_cp_max(lam)
        if lam >= 3.0:
            cp = w.bem(rotor.blade(), lam).cp
            lines.append(f"  {lam:4.1f}   {g:.4f}           {cp:.4f}     "
                         f"{cp / g:.3f}")
        else:
            lines.append(f"  {lam:4.1f}   {g:.4f}           -")
    g85 = w.glauert_cp_max(8.5)
    cp85 = w.bem(rotor.blade(), 8.5).cp
    lines += [f"  Betz 16/27 = {16 / 27:.4f}; at TSR 8.5 wake rotation costs"
              f" {100 * (16 / 27 - g85) / (16 / 27):.1f} % of Betz,",
              f"  drag, tip loss and the finite blade cost another"
              f" {100 * (g85 - cp85) / g85:.1f} %",
              "  slow rotors (water pumps, old mills) give much of the power",
              "  away as wake swirl; fast rotors need little torque for the",
              "  same power and so leave little swirl behind"]
    emit("e_glauert", lines)
    csv("ch11-glauert.csv", "tsr,glauert,betz,rotor", rows)


def high_thrust() -> None:
    a = np.round(np.arange(0.0, 1.0001, 0.02), 4)
    mom = 4 * a * (1 - a)
    buhl = w.thrust_coefficient(a)
    csv("ch11-ctbuhl.csv", "a,momentum,buhl",
        [(f"{x:.2f}", f"{m:.4f}", f"{b:.4f}") for x, m, b in zip(a, mom, buhl)])
    lines = ["thrust coefficient against axial induction (F = 1):",
             "  a      momentum 4a(1-a)   Buhl (used by the BEM code)"]
    for x in (0.2, 1 / 3, 0.4, 0.5, 0.6, 0.8, 1.0):
        lines.append(f"  {x:.3f}  {4 * x * (1 - x):.3f}              "
                     f"{float(w.thrust_coefficient(x)):.3f}")
    res = w.bem(rotor.blade(), 12.0)
    hi = res.a[res.a > 0.4]
    lines += ["  momentum theory says thrust falls after a = 0.5; measured",
              "  rotors show it keeps rising (turbulent wake state)",
              f"  rotor at TSR 12 (low wind, high speed): {len(hi)} of"
              f" {len(res.a)} annuli above a = 0.4",
              "  the correction keeps the iteration from a false solution"]
    emit("e_highthrust", lines)


def shear_and_shadow() -> None:
    """Azimuth-resolved inflow of each blade with shear and tower shadow:
    quasi-steady weight of each annulus from the BEM torque distribution,
    local torque scaled with the square of the local wind (teaching model,
    A-226)."""
    b = rotor.blade()
    res = w.bem(b, rotor.tsr_opt())
    weight = res.dq / res.dq.sum()
    shear, hub, v_hub = 0.20, rotor.HUB, 8.0
    a_tower, x_tower = 2.2, 6.0          # tower radius, overhang at the root
    x_r = x_tower + b.r * (math.sin(math.radians(5.0)) +   # tilt 5 deg
                           math.sin(math.radians(3.0)))    # cone 3 deg
    psi = np.radians(np.arange(0, 360, 2))  # azimuth 0 = blade up
    rows, per_blade = [], []
    for k in range(3):
        ang = psi + 2 * math.pi * k / 3
        z = hub + np.outer(np.cos(ang), b.r)            # height of each element
        y = np.outer(np.sin(ang), b.r)                  # sideways offset
        v = v_hub * (z / hub) ** shear
        below = np.cos(ang)[:, None] < 0                # only the lower half
        x = x_r[None, :]
        shadow = 1 - a_tower ** 2 * (x ** 2 - y ** 2) / (x ** 2 + y ** 2) ** 2
        v = np.where(below, v * shadow, v)
        per_blade.append((weight[None, :] * (v / v_hub) ** 2).sum(axis=1) / 3)
    per_blade = np.array(per_blade)
    total = per_blade.sum(axis=0)
    deg = np.degrees(psi)
    for j in range(len(deg)):
        rows.append((f"{deg[j]:.0f}", *(f"{100 * per_blade[k, j] * 3:.2f}"
                                        for k in range(3)),
                     f"{100 * total[j]:.2f}"))
    csv("ch11-shear3p.csv", "psi,b1,b2,b3,total", rows)
    one = per_blade[0] * 3
    reqs = [w.rotor_equivalent_speed(10.0, hub, rotor.RADIUS, s)
            for s in (0.0, 0.1, 0.2, 0.3, 0.4)]
    lines = [f"wind shear {shear} and tower shadow at {v_hub:.0f} m/s (A-226):",
             f"  wind at the lowest tip ({hub - rotor.RADIUS:.0f} m)"
             f" {v_hub * ((hub - rotor.RADIUS) / hub) ** shear:.2f} m/s,"
             f" at the top tip {v_hub * ((hub + rotor.RADIUS) / hub) ** shear:.2f}"
             " m/s",
             f"  torque of one blade over a turn (100 = uniform wind):"
             f" {100 * one.min():.1f} .. {100 * one.max():.1f}",
             f"  rotor torque: {100 * total.min():.1f} .. {100 * total.max():.1f}"
             f" (ripple {100 * (total.max() - total.min()):.1f} points, 3P)",
             f"  tower radius {a_tower} m; rotor plane {x_tower:.0f} m"
             f" upwind at the root, {x_r[-1]:.1f} m at the tip",
             f"  deficit in front of the tower:"
             f" {100 * deficit0(a_tower, x_r[0]):.0f} % at the root,"
             f" {100 * deficit0(a_tower, x_r[-1]):.1f} % at the tip;",
             f"    the dip is {shadow_width(a_tower, x_r):.0f} deg wide"
             " at 0.7 R",
             "  rotor-equivalent speed for 10 m/s at hub height:",
             "    shear  0.0    0.1    0.2    0.3    0.4",
             "    REWS   " + "  ".join(f"{x:.2f}" for x in reqs),
             "  a power-law profile changes the rotor energy by under 1 %;",
             "  the 1P load on each blade is the real cost of shear"]
    emit("e_shear", lines)


def deficit0(a_tower: float, x: float) -> float:
    """Potential-flow speed deficit straight in front of the tower axis."""
    return a_tower ** 2 / x ** 2


def shadow_width(a_tower: float, x_r: np.ndarray) -> float:
    """Azimuth band (deg) at 0.7 R where the potential-flow deficit exceeds
    1 % of the free wind."""
    r07 = 0.7 * rotor.RADIUS
    x = float(np.interp(r07, rotor.blade().r, x_r))
    ys = np.linspace(-20, 20, 4001)
    d = a_tower ** 2 * (x ** 2 - ys ** 2) / (x ** 2 + ys ** 2) ** 2
    span = ys[d > 0.01]
    return float(np.degrees((span.max() - span.min()) / r07))


def eroded_polar_factory(r: np.ndarray, r_start: float):
    """Leading-edge erosion on the outer blade (A-227, teaching): drag
    up by 0.006 and lift slope down 6 % before stall, stall 2 deg earlier."""
    mask = r >= r_start

    def eroded(alpha):
        alpha = np.asarray(alpha, float)
        cl, cd = w.polar(alpha)
        a_att = np.minimum(alpha, w.ALPHA_STALL - 2.0)
        cl_e = np.where(alpha <= w.ALPHA_STALL - 2.0, 0.94 * 0.11 * (alpha + 2),
                        0.94 * 0.11 * (a_att + 2) - 0.03 * (alpha - a_att))
        cl_e = np.where(np.abs(alpha) > w.ALPHA_STALL + 4, cl, cl_e)
        cd_e = cd + 0.006
        return np.where(mask, cl_e, cl), np.where(mask, cd_e, cd)
    return eroded


def erosion() -> None:
    b = rotor.blade()
    eroded = eroded_polar_factory(b.r, 0.67 * rotor.RADIUS)
    rows = []
    for lam in np.arange(4.0, 12.01, 0.25):
        c0 = w.bem(b, float(lam)).cp
        c1 = w.bem(b, float(lam), polar_fn=eroded).cp
        rows.append((f"{lam:.2f}", f"{c0:.4f}", f"{c1:.4f}"))
    csv("ch11-erosion.csv", "tsr,clean,eroded", rows)
    lam0 = rotor.tsr_opt()
    cp0 = w.bem(b, lam0).cp
    cp1 = w.bem(b, lam0, polar_fn=eroded).cp
    # annual energy: below rated the power scales with Cp at the operating
    # TSR; at rated pitch makes up the loss (enough margin assumed)
    ops = rotor.curve(rotor.RHO_SITE)
    v = np.arange(0.0, 30.01, 0.5)
    p_c, p_e = np.zeros_like(v), np.zeros_like(v)
    for o in ops:
        k = int(round(o.v / 0.5))
        p_c[k] = o.power_w / 1e3
        if o.pitch == 0.0 and o.power_w > 0:
            ratio = w.bem(b, o.tsr, polar_fn=eroded).cp / o.cp
            p_e[k] = min(o.power_w * ratio, rotor.turbine().rated_w) / 1e3
        else:
            p_e[k] = o.power_w / 1e3
    sm_c, sm_e = w.smooth_power_curve(v, p_c), w.smooth_power_curve(v, p_e)
    for s in (sm_c, sm_e):
        s[(v > 25.0) | (v < 2.5)] = 0.0
    vh = lab_d.hourly()[0]
    e_c = np.interp(vh, v, sm_c).sum() / 1e3
    e_e = np.interp(vh, v, sm_e).sum() / 1e3
    loss = 100 * (1 - e_e / e_c)
    lines = ["leading-edge erosion on the outer third of the blade (A-227):",
             f"  peak Cp at TSR {lam0:.2f}: clean {cp0:.4f}, eroded {cp1:.4f}"
             f" ({100 * (cp1 / cp0 - 1):+.1f} %)",
             f"  one turbine at site density: {e_c:,.0f} MWh clean,"
             f" {e_e:,.0f} MWh eroded ({-loss:+.1f} %)",
             f"  twelve turbines: {12 * (e_c - e_e) / 1e3:.2f} GWh a year,"
             f" {12 * (e_c - e_e) * 50 / 1e3:,.0f} k u at 50 u/MWh",
             "  the outer third makes most of the torque and sees the highest",
             "  speed (rain and dust hit it hardest): leading-edge protection",
             "  and repair are planned maintenance, not cosmetics"]
    emit("e_erosion", lines)


if __name__ == "__main__":
    glauert()
    high_thrust()
    shear_and_shadow()
    erosion()
