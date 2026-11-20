"""Chapter 11, section B (subsystems in numbers): a three-stage gearbox
(tooth counts, ratios, mesh and planet-pass frequencies), the main bearing
life from the year's thrust, the turbine's own consumption, and the blade
as a beam (flap moments from BEM, spar caps sized for strain, tip
deflection and tower clearance).

Run from the project root:   python -m companion.ch11.examples_f
Writes companion/ch11/expected/f_*.txt and diagrams/data/ch11-*.csv.
Teaching values A-229 .. A-232 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import lab_d, rotor
from companion.ch11.common import csv, emit
from plantp import wind as w

G = 9.81
RPM_RATED = 11.5


# --------------------------------------------------------------- gearbox
STAGES = [("planetary 1", 21, 99, 3), ("planetary 2", 23, 97, 3),
          ("parallel", 101, 30, 0)]       # sun, ring, planets / wheel, pinion


def gearbox() -> None:
    f_in = RPM_RATED / 60
    total = 1.0
    lines = [f"three-stage gearbox at rated speed {RPM_RATED} rpm (A-229):",
             "  stage         teeth                 ratio  input Hz   mesh Hz"]
    for name, z1, z2, n_pl in STAGES:
        if n_pl:
            ratio = w.planetary_ratio(z1, z2)
            mesh = z2 * f_in                        # ring fixed, carrier in
            z_pl = (z2 - z1) // 2
            ok = (z1 + z2) % n_pl == 0
            other = (f"{n_pl} planets x {z_pl} teeth, planet pass"
                     f" {n_pl * f_in:.3f} Hz, spacing {'ok' if ok else 'no'}")
            teeth = f"sun {z1}, ring {z2}"
        else:
            ratio = z1 / z2
            mesh = z1 * f_in
            other = f"pinion {z2} teeth"
            teeth = f"wheel {z1}, pinion {z2}"
        lines.append(f"  {name:12s}  {teeth:20s}  {ratio:6.3f}  {f_in:8.3f}"
                     f"  {mesh:8.2f}")
        lines.append(f"      {other}")
        f_in *= ratio
        total *= ratio
    lines += [f"  total ratio {total:.2f}: generator {RPM_RATED * total:.0f}"
              f" rpm ({f_in:.2f} Hz)",
              "  equal planet spacing needs (sun + ring) / planets to be a",
              "  whole number; the first planet-pass frequency equals 3P",
              f"  ({3 * RPM_RATED / 60:.3f} Hz): condition monitoring must"
              " tell them apart",
              "  by order analysis (frequencies divided by shaft speed)"]
    emit("f_gearbox", lines)


# --------------------------------------------------------------- main bearing
def main_bearing() -> None:
    """Spherical roller main bearing carrying rotor weight (radial) and
    thrust (axial). Factors X 1.0, Y 2.0 and the rating C are fictional
    catalogue values (A-230); a real check uses the maker's data, the
    shaft moments and the lubrication conditions."""
    v, _, _ = lab_d.hourly()
    ops = rotor.curve(rotor.RHO_SITE)
    vg = np.array([o.v for o in ops])
    thrust = np.interp(v, vg, [o.thrust_n for o in ops], left=0, right=0)
    rpm = np.interp(v, vg, [o.omega * 30 / math.pi for o in ops],
                    left=0, right=0)
    fr = (66 + 45) * 1e3 * G
    p = 1.0 * fr + 2.0 * thrust
    rev = rpm * 60.0
    run = rev > 0
    p_eq = (np.sum(p[run] ** (10 / 3) * rev[run]) / rev[run].sum()) ** 0.3
    rev_year = rev.sum()
    need = rev_year * 20 / 1e6
    c_req = p_eq * need ** 0.3
    c_given = 11.0e6
    life = w.bearing_life_mrev(c_given, p_eq)
    lines = ["main bearing: life-weighted load over the data-pack year (A-230):",
             f"  radial: rotor weight {fr / 1e3:,.0f} kN; axial: thrust,"
             f" up to {thrust.max() / 1e3:,.0f} kN",
             f"  equivalent load P = Fr + 2 Fa, weighted by revolutions:"
             f" {p_eq / 1e3:,.0f} kN",
             f"  revolutions: {rev_year / 1e6:.2f} million a year,"
             f" {need:.0f} million in 20 years",
             f"  rating needed for L10 = 20 years: C = P x L^0.3 ="
             f" {c_req / 1e6:.2f} MN",
             f"  with a bearing of C = {c_given / 1e6:.1f} MN:"
             f" L10 = {life:,.0f} million rev = {life / (rev_year / 1e6):.0f}"
             " years",
             "  L10 is a statistical life (90 % survive) for clean, well",
             "  lubricated bearings; main-bearing failures in service often",
             "  start from lubrication, sealing or misalignment instead"]
    emit("f_bearing", lines)


# --------------------------------------------------------------- own use
def auxiliary() -> None:
    """Own consumption of one turbine (A-231, teaching values): controller,
    lights and UPS 3 kW always; heating 25 kW in cold standby hours;
    cooling, pumps and hydraulics 0.8 % of the output while producing;
    yaw 15 kW for 2 % of the hours."""
    v, _, _ = lab_d.hourly()
    t_air = lab_d.datapack.load_hourly()["t_air_c"].to_numpy(float)
    ops = rotor.curve(rotor.RHO_SITE)
    vg = np.array([o.v for o in ops])
    p_kw = np.interp(v, vg, [o.power_w / 1e3 for o in ops], left=0, right=0)
    prod = p_kw > 0
    base = 3.0 * len(v)
    heat = 25.0 * np.sum(~prod & (t_air < 0.0))
    cool = 0.008 * p_kw[prod].sum()
    yaw = 15.0 * 0.02 * len(v)
    total = base + heat + cool + yaw
    standby = 3.0 * np.sum(~prod) + heat + 15.0 * 0.02 * np.sum(~prod)
    gross = p_kw.sum()
    lines = ["own consumption of one turbine over the data-pack year (A-231):",
             f"  hours producing {prod.sum():,}, standing {(~prod).sum():,}"
             f" (cold standby {np.sum(~prod & (t_air < 0.0))})",
             f"  controller, lights, UPS   {base / 1e3:7.1f} MWh",
             f"  heating in cold standby   {heat / 1e3:7.1f} MWh",
             f"  cooling and hydraulics    {cool / 1e3:7.1f} MWh",
             f"  yaw drives                {yaw / 1e3:7.1f} MWh",
             f"  total                     {total / 1e3:7.1f} MWh"
             f" = {100 * total / gross:.2f} % of {gross / 1e3:,.0f} MWh",
             f"  drawn while standing (imported): {standby / 1e3:.1f} MWh;"
             " the rest is netted",
             "  inside the turbine while it produces. Metering decides how",
             "  each part is counted between gross and delivered energy",
             "  (chapters 21 and 23)"]
    emit("f_aux", lines)


# --------------------------------------------------------------- blade beam
E_CAP = 45e9            # Pa, glass/epoxy unidirectional (A-232)
STRAIN = 0.005          # allowable strain at the extreme load (teaching)
WIDTH = 0.9             # m, spar cap width
RHO_CAP = 1950.0        # kg/m3
R_ROOT = 10.0           # m, inboard of this the round root carries the load


def thickness_ratio(r):
    """Relative thickness t/c along the blade (teaching): 0.40 at the end
    of the root, 0.24 at 40 m, 0.18 at the tip."""
    return np.interp(r, [R_ROOT, 40.0, rotor.RADIUS], [0.40, 0.24, 0.18])


def blade_structure() -> None:
    b = rotor.blade()
    op = w.operate(rotor.turbine(), 10.0, rotor.RHO0)     # peak thrust
    res = w.bem(b, op.tsr, op.pitch)
    force = res.dt / b.n_blades * rotor.RHO0 * op.v ** 2   # N per annulus
    m_op = w.flap_moments(b.r, force)
    root = float(w.flap_moments(np.concatenate(([b.hub], b.r)),
                                np.concatenate(([0.0], force)))[0])
    m_ext = 2.0 * m_op                                    # teaching ratio
    h = thickness_ratio(b.r) * b.chord
    sigma = E_CAP * STRAIN
    t_cap = np.maximum(m_ext / (sigma * WIDTH * h), 0.005)
    out = b.r >= R_ROOT
    cap_mass = 2 * WIDTH * RHO_CAP * np.sum(t_cap[out] * b.dr[out])
    ei = E_CAP * WIDTH * t_cap * h ** 2 / 2
    kappa = np.where(out, m_op / ei, 0.0)
    slope = np.cumsum(kappa * b.dr)
    defl = np.cumsum(slope * b.dr)
    tip_op = float(defl[-1])
    tip_ext = 2.0 * tip_op
    clear0 = 6.0 + rotor.RADIUS * (math.sin(math.radians(5.0)) +
                                   math.sin(math.radians(3.0))) + 3.0 - 2.2
    rows = [(f"{r:.2f}", f"{m / 1e6:.3f}", f"{t * 1e3:.1f}", f"{d:.3f}")
            for r, m, t, d in zip(b.r, m_op, t_cap, defl)]
    csv("ch11-bladebeam.csv", "r,moment,tcap,defl", rows)
    k30 = int(np.argmin(np.abs(b.r - 30.0)))
    lines = [f"blade as a beam at the peak-thrust point (10 m/s, 1.225 kg/m3,"
             " A-232):",
             f"  thrust {op.thrust_n / 1e3:.0f} kN, one blade"
             f" {force.sum() / 1e3:.0f} kN; flap moment at the root"
             f" {root / 1e6:.1f} MN m",
             f"    (first-order estimate T/3 x 2R/3 = {op.thrust_n / 3 * 50 / 1e6:.1f}"
             " MN m)",
             f"  extreme = 2 x operating (teaching); caps E {E_CAP / 1e9:.0f} GPa,"
             f" strain {100 * STRAIN:.1f} %, width {WIDTH} m",
             f"  at r = {b.r[k30]:.1f} m: chord {b.chord[k30]:.2f} m,"
             f" height {h[k30]:.2f} m, moment {m_ext[k30] / 1e6:.1f} MN m"
             f" -> cap {1e3 * t_cap[k30]:.0f} mm",
             f"  cap thickness {1e3 * t_cap[out][0]:.0f} mm at {R_ROOT:.0f} m"
             f" falling to {1e3 * t_cap[-1]:.0f} mm at the tip;"
             f" two caps {cap_mass / 1e3:.1f} t",
             f"    ({100 * cap_mass / 22e3:.0f} % of the 22 t blade)",
             f"  tip deflection: {tip_op:.1f} m at peak thrust, {tip_ext:.1f} m"
             " at the extreme load",
             f"  unloaded tip-tower clearance {clear0:.1f} m (overhang 6 m, tilt"
             " 5 deg, cone 3 deg,",
             f"    prebend 3 m, tower radius 2.2 m); left at the extreme"
             f" {clear0 - tip_ext:.1f} m",
             "  sized for strength, the blade would touch the tower:",
             "  stiffness, not stress, decides the caps of a long blade"]
    allowed = 0.7 * clear0                       # keep 30 % (teaching)
    factor = tip_ext / allowed
    glass = cap_mass * factor
    carbon = cap_mass * factor * (E_CAP / 135e9) * (1600.0 / RHO_CAP)
    lines += [f"  keep 30 % of the clearance (teaching): deflection at most"
              f" {allowed:.1f} m,",
              f"    so the caps need {factor:.2f} times the bending stiffness",
              f"  glass caps (45 GPa, 1950 kg/m3):  {glass / 1e3:4.1f} t",
              f"  carbon caps (135 GPa, 1600 kg/m3): {carbon / 1e3:4.1f} t",
              "  a cap sized for strain has EI = M h / (2 strain) whatever",
              "  its fibre: only a stiffness-driven design gains from carbon"]
    emit("f_bladebeam", lines)


if __name__ == "__main__":
    gearbox()
    main_bearing()
    auxiliary()
    blade_structure()
