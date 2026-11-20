"""Chapter 8, section A - machine principles and selection: induction law,
magnetic circuit, rotating field, EMF, the synchronous machine, the
induction machine, starting, DFIG slip power, topologies, losses, grid.

Run from the project root:   python -m companion.ch08.examples_a
Writes companion/ch08/expected/a_*.txt and diagrams/data/ch08-*.csv.
Teaching values A-047, A-107, A-111 .. A-114, A-117 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch08.common import csv, emit
from plantp import machines as m
from plantp.phasors import polar, to_polar

MU0 = 4e-7 * math.pi
S3 = math.sqrt(3)
MOTOR = dict(v_ph=230.0, f_hz=50.0, poles=4, r1=0.09, x1=0.33, xm=10.0,
             r2=0.075, x2=0.35, p_mech_loss_w=400.0)               # A-114


def induction_law() -> None:
    b, length, d, n = 0.9, 1.1, 0.8, 1155.0                       # A-111
    v = 2 * math.pi * n / 60 * d / 2
    e = b * length * v
    f = b * 1000.0 * length
    emit("a_motional", [
        "conductor in the air gap of the geared generator (A-111):",
        f"  B {b} T, active length {length} m",
        f"  rotor diameter {d} m at {n:.0f} rpm: surface speed {v:.1f} m/s",
        f"  motional EMF e = B l v = {e:.1f} V per conductor (where B peaks)",
        f"  1000 A in the same conductor: force F = B I l = {f:.0f} N; this",
        "  tangential force on every conductor is the machine's torque",
    ])


def magnetic_circuit() -> None:
    b, l_fe, gap, mu_r = 0.9, 1.2, 2 * 3e-3, 2000.0
    h_air = b / MU0
    ni_air = h_air * gap
    ni_fe = b / (MU0 * mu_r) * l_fe
    lines = [f"flux path: {l_fe} m of iron (mu_r {mu_r:.0f}) and two 3 mm air "
             f"gaps, B {b} T",
             f"  air gap: H = B/mu0 = {h_air:,.0f} A/m x {1000 * gap:.0f} mm = "
             f"{ni_air:,.0f} ampere-turns",
             f"  iron:    H = B/(mu0 mu_r) = {b / (MU0 * mu_r):,.0f} A/m x "
             f"{l_fe} m = {ni_fe:,.0f} ampere-turns",
             f"  the air gap takes {100 * ni_air / (ni_air + ni_fe):.0f} % of "
             "the magnetising effort"]
    for mu in (2000, 500, 100):
        ni = ni_air + b / (MU0 * mu) * l_fe
        lines.append(f"  iron mu_r {mu:5d} (saturating): total "
                     f"{ni:,.0f} ampere-turns")
    lines.append("a large air gap is mechanically safe but costs magnetising "
                 "current;")
    lines.append("  in an induction machine that current is reactive power "
                 "from the grid")
    emit("a_magcircuit", lines)


def rotating_field() -> None:
    lines = ["synchronous speed n_s = 120 f / p:"]
    for p in (2, 4, 6, 8, 48, 120):
        lines.append(f"  {p:3d} poles at 50 Hz: {m.sync_speed_rpm(50, p):7.1f} "
                     "rpm")
    lines += [f"geared generator (A-111): 6 poles at 1155 rpm -> "
              f"{m.electrical_freq_hz(1155, 6):.2f} Hz",
              f"direct drive at 10.5 rpm with 120 poles -> "
              f"{m.electrical_freq_hz(10.5, 120):.2f} Hz",
              "with a full converter the machine frequency need not be 50 Hz"]
    emit("a_field", lines)
    th = np.linspace(0, 2 * math.pi, 73)

    def mmf(wt, x):
        fa = math.cos(wt) * math.cos(x)
        fb = math.cos(wt - 2 * math.pi / 3) * math.cos(x - 2 * math.pi / 3)
        fc = math.cos(wt + 2 * math.pi / 3) * math.cos(x + 2 * math.pi / 3)
        return fa, fa + fb + fc

    rows = []
    for x in th:
        a0, t0 = mmf(0.0, x)
        a1, t1 = mmf(2 * math.pi / 12, x)
        rows.append((f"{math.degrees(x):.0f}", f"{a0:.4f}", f"{t0:.4f}",
                     f"{a1:.4f}", f"{t1:.4f}"))
    csv("ch08-mmf.csv", "deg,fa0,ft0,fa1,ft1", rows)


def emf_turns() -> None:
    d, length, poles, b1 = 0.8, 1.1, 6, 0.9
    f = m.electrical_freq_hz(1155, poles)
    pole_area = math.pi * d * length / poles
    phi = 2 / math.pi * b1 * pole_area
    e_ph = 690 / S3
    nkw = e_ph / (4.44 * f * phi)
    emit("a_emf", [
        f"geared generator (A-111): D {d} m, L {length} m, {poles} poles, "
        f"B1 peak {b1} T, f {f:.2f} Hz",
        f"  pole area pi D L / p = {pole_area:.4f} m2; flux per pole "
        f"(2/pi) B1 A = {phi:.4f} Wb",
        f"  phase EMF 690/sqrt3 = {e_ph:.1f} V -> N k_w = E / (4.44 f Phi) = "
        f"{nkw:.2f} turns",
        "  a few series turns per phase: large low-voltage machines use few",
        "  turns of heavy conductors in several parallel paths",
    ])


def synchronous() -> None:
    s_r, v_ll, xd = 200e3, 400.0, 2.5                             # A-113
    v_ph = v_ll / S3
    z_b = v_ll ** 2 / s_r
    xs = xd * z_b
    i_r = s_r / (S3 * v_ll)
    lines = [f"backup generator 200 kVA, 400 V, x_d {xd} pu (A-113):",
             f"  Z_base {z_b:.3f} ohm, X_s {xs:.2f} ohm, I_r {i_r:.1f} A"]
    for name, pf, sign in (("rated, pf 0.8 lagging", 0.8, -1),
                           ("rated, pf 1", 1.0, 0),
                           ("rated, pf 0.9 leading", 0.9, 1)):
        i = polar(i_r, sign * math.degrees(math.acos(pf)))
        e = m.sm_emf(complex(v_ph, 0), i, xs)
        mag, dl = to_polar(e)
        note = " > 90: impossible" if dl > 90 else ""
        lines.append(f"  {name:22s} E {mag:5.0f} V = {mag / v_ph:.2f} pu, "
                     f"delta {dl:4.1f}{note}")
    e_pu = 2.0
    p_max = 3 * e_pu * v_ph * v_ph / xs
    lines += [f"P = 3 E V sin(delta) / X_s; with E {e_pu} pu the maximum "
              f"(delta 90 deg) is {p_max / 1e3:.0f} kW",
              "more excitation (E) -> more reactive power delivered; less ->"
              " absorbed",
              "  a weakly excited machine near delta 90 deg loses synchronism"]
    emit("a_sync", lines)
    rows = []
    for e_pu in np.linspace(1.27, 4.0, 40):              # above E_min 1.25
        p_ph = 0.5 * s_r / 3
        d = math.asin(min(1.0, p_ph * xs / (e_pu * v_ph * v_ph)))
        e = polar(e_pu * v_ph, math.degrees(d))
        i = (e - v_ph) / complex(0, xs)
        rows.append((f"{e_pu:.2f}", f"{abs(i) / i_r:.4f}"))
    csv("ch08-vcurve.csv", "e,i", rows)
    rows = []
    for dd in range(0, 181, 5):
        rows.append((f"{dd}", f"{3 * 2.0 * v_ph * v_ph / xs * math.sin(math.radians(dd)) / 1e3:.2f}"))
    csv("ch08-pdelta.csv", "delta,p", rows)


def induction() -> None:
    im = m.InductionMachine(**MOTOR)
    s_r = im.slip_for_shaft_power(30e3)
    op = im.operate(s_r)
    st = im.operate(1.0)
    slips = [x / 1000 for x in range(-200, 1001, 2) if x != 0]
    t = [im.operate(s)["torque"] for s in slips]
    k_max = int(np.argmax(t))
    gen = im.operate(-s_r)
    emit("a_induction", [
        "30 kW 4-pole motor at 400 V (A-114), per-phase circuit at 230 V:",
        f"  rated: slip {100 * s_r:.2f} % ({op['n_rpm']:.0f} rpm), current "
        f"{abs(op['i1']):.1f} A, pf {op['pf']:.3f}",
        f"  torque {op['torque']:.0f} N m, efficiency "
        f"{op['p_shaft'] / op['p_in']:.3f}, rotor copper s P_ag "
        f"{op['p_cu2'] / 1e3:.2f} kW",
        f"  starting (s = 1): {abs(st['i1']):.0f} A = "
        f"{abs(st['i1']) / abs(op['i1']):.1f} x rated, pf {st['pf']:.2f}, "
        f"torque {st['torque']:.0f} N m",
        f"  pull-out torque {t[k_max]:.0f} N m = {t[k_max] / op['torque']:.1f}"
        f" x rated at slip {100 * slips[k_max]:.1f} %",
        f"as a generator at slip {-100 * s_r:.2f} %: delivers "
        f"{-gen['p_in'] / 1e3:.1f} kW, absorbs {gen['q_in'] / 1e3:.1f} kvar",
        "  an induction generator always needs reactive power to magnetise",
    ])
    csv("ch08-torque.csv", "s,n,t", [(f"{s:.3f}", f"{1500 * (1 - s):.0f}",
                                      f"{x:.1f}") for s, x in zip(slips, t)])


def starting() -> None:
    im = m.InductionMachine(**MOTOR)
    st = im.operate(1.0)
    z_lr = MOTOR["v_ph"] / st["i1"]
    zb = 400 ** 2 / 250e3
    z_tx = complex(0.012 * zb, math.sqrt(0.06 ** 2 - 0.012 ** 2) * zb)
    z_cab = complex(3.02e-3, 3.20e-3)                         # ch 7, A-110
    z_src = z_tx + z_cab
    v_m = abs(MOTOR["v_ph"] * z_lr / (z_lr + z_src))
    lines = ["direct-on-line start of the 30 kW motor on the auxiliary board:",
             f"  locked-rotor impedance {abs(z_lr):.3f} ohm at "
             f"{math.degrees(math.atan2(z_lr.imag, z_lr.real)):.1f} deg",
             f"  source: transformer 250 kVA 6 % + feeder = {z_src.real * 1e3:.1f}"
             f" + j{z_src.imag * 1e3:.1f} mohm",
             f"  motor terminal voltage during start {v_m:.1f} V = "
             f"{100 * v_m / 230:.1f} % (dip {100 - 100 * v_m / 230:.1f} %)"]
    for name, k in (("star-delta start (1/3 current)", 1 / 3),
                    ("soft starter at 3 x rated", 3 * 53.8 / abs(st["i1"]))):
        v_k = abs(MOTOR["v_ph"] * (z_lr / k) / (z_lr / k + z_src))
        lines.append(f"  {name}: dip {100 - 100 * v_k / 230:.1f} %")
    lines += ["  a frequency converter starts with about rated current and "
              "no dip,",
              "  at the price of harmonics (chapter 7) and cost"]
    emit("a_start", lines)


def dfig() -> None:
    p_mech = 5.32e6                                               # A-047
    lines = ["DFIG, 4 poles (1500 rpm synchronous); shaft power follows speed",
             "  cubed (best tip-speed ratio) up to 5.32 MW at 1800 rpm:"]
    for n in (1050, 1350, 1500, 1800, 1950):
        s = m.slip(1500, n)
        pm = p_mech * min(1.0, (n / 1800) ** 3)
        pr = m.dfig_rotor_power(pm, s) + 0.0          # no "-0.00"
        lines.append(f"  {n} rpm: shaft {pm / 1e6:.2f} MW, slip {100 * s:+5.1f} %, "
                     f"rotor {pr / 1e6:+.2f} MW (+ = to grid)")
    lines += ["  speed range +-30 % needs a converter of about a quarter",
              "  of rating (0.3 / 1.3);",
              "  a full converter carries 100 % but frees the speed and the "
              "machine"]
    emit("a_dfig", lines)


def topologies() -> None:
    p_mech = 5.32e6
    shear = 40e3                                                  # A-112
    rows = [("geared, high speed (1:110)", 1155.0, 6, 1.0, 3),
            ("geared, medium speed (1:40)", 420.0, 24, 1.0, 2),
            ("direct drive", 10.5, 120, 1.0, 0),
            ("DFIG (rated 1800 rpm)", 1800.0, 4, 0.3, 3)]
    lines = [f"5.32 MW shaft power (A-047); air-gap shear stress {shear / 1e3:.0f}"
             " kPa (A-112):"]
    for name, n, poles, conv, stages in rows:
        t = m.torque_nm(p_mech, n)
        vr = m.rotor_volume_m3(t, shear)
        f = m.electrical_freq_hz(n, poles)
        lines.append(f"  {name:28s} {n:6.1f} rpm, T {t / 1e3:8.1f} kN m, "
                     f"V_r {vr:6.2f} m3")
        lines.append(f"    {poles} poles -> {f:5.2f} Hz; converter "
                     f"{100 * conv:.0f} % of rating; gear stages {stages}")
    lines += ["rotor volume grows with torque: the direct-drive machine is "
              "about",
              "  110 times the volume of the geared one; the gearbox moves "
              "the torque",
              "  into steel gears instead of copper and magnets"]
    emit("a_topologies", lines)


def losses() -> None:
    p_r, eta = 5.13e6, 0.970                                      # A-111
    p_loss = p_r * (1 / eta - 1)
    split = {"stator copper": 0.40, "core (hysteresis, eddy)": 0.25,
             "rotor and magnet": 0.05, "friction, windage, fan": 0.10,
             "stray load": 0.20}
    lines = [f"geared generator at rating: {p_r / 1e6:.2f} MW out at "
             f"efficiency {eta}: losses {p_loss / 1e3:.1f} kW"]
    for k, v in split.items():
        lines.append(f"  {k:25s} {100 * v:3.0f} %  {v * p_loss / 1e3:6.1f} kW")
    lines.append("efficiency against load (fixed share of rated losses):")
    for share in (0.20, 0.35, 0.50):
        effs = " ".join(f"{m.efficiency(x, p_r, eta, share):.3f}"
                        for x in (0.1, 0.25, 0.5, 1.0))
        lines.append(f"  fixed {100 * share:.0f} %: at 10/25/50/100 % load "
                     f"{effs}")
    lines.append("  fixed losses (core, friction) dominate at part load")
    emit("a_losses", lines)
    rows = []
    for x in np.linspace(0.02, 1.1, 55):
        rows.append((f"{x:.3f}", f"{m.efficiency(x, p_r, eta, 0.2):.4f}",
                     f"{m.efficiency(x, p_r, eta, 0.5):.4f}"))
    csv("ch08-eff.csv", "load,eff20,eff50", rows)


def grid() -> None:
    i_sg = 1 / 0.12
    emit("a_grid", [
        "fault current at the terminals, in per unit of the unit's rated "
        "current:",
        f"  synchronous machine, x_d'' 0.12 pu (A-113): about {i_sg:.1f} pu "
        "at first",
        "  converter-coupled unit: about 1.1 pu, set by the converter "
        "(A-117)",
        "inertia: the 32.2 MJ in the turbine rotor (chapter 4) reaches the "
        "grid",
        "  only if the converter control is told to release it",
        "reactive power: a synchronous machine by excitation; an induction",
        "  machine only absorbs; converter units within their P-Q chart",
    ])


if __name__ == "__main__":
    induction_law()
    magnetic_circuit()
    rotating_field()
    emf_turns()
    synchronous()
    induction()
    starting()
    dfig()
    topologies()
    losses()
    grid()
