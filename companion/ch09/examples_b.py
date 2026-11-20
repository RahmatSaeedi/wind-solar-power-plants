"""Chapter 9, section B - topologies and subsystems: central or string
architecture, MPPT step size, DC link, LCL filter, magnetics, busbar
overshoot, gate drive and dead time, cooling and component ratings.

Run from the project root:   python -m companion.ch09.examples_b
Writes companion/ch09/expected/b_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-145, A-151 .. A-157; PV inverter AC voltage 600 V (D-012).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch09.common import csv, emit
from companion.ch09.examples_a import DEV_NPC
from plantp import mppt as mp, pe

S2, S3 = math.sqrt(2), math.sqrt(3)
# one of the four power stacks of a 5 MW central inverter (A-145, D-012)
STACK = dict(s=1.375e6, v_ll=600.0, v_dc=1000.0, f_sw=3000.0, n=4)


def stack_current() -> tuple[float, float]:
    i_rms = STACK["s"] / (S3 * STACK["v_ll"])
    return i_rms, i_rms * S2


def architecture() -> None:
    e_pv = 101.4e3                                  # MWh/yr AC, lab D model
    p_mean = e_pv / 8760
    rows = [("central, 10 x 5 MW", 10, 0.5, 72.0, 0.006),
            ("string, 167 x 0.3 MW", 167, 0.15, 24.0, 0.003)]    # A-151
    lines = [f"central or string inverters for 60 MWp (A-151); mean PV output"
             f" {p_mean:.2f} MW"]
    for name, n, lam, mttr, mism in rows:
        fails = n * lam
        e_fail = fails * mttr * p_mean / n
        e_mism = mism * e_pv
        lines += [f"  {name}:",
                  f"    failures {fails:4.1f}/yr x {mttr:.0f} h x "
                  f"{p_mean / n:.3f} MW = {e_fail:5.0f} MWh/yr "
                  f"({100 * e_fail / e_pv:.2f} %)",
                  f"    mismatch {100 * mism:.1f} % = {e_mism:5.0f} MWh/yr;"
                  f" one failure removes {100 / n:.1f} % of PV capacity"]
    lines += ["  strings win on energy; the central design has 17 times fewer",
              "  units to buy, connect, monitor and maintain (chapters 18, 51)"]
    emit("b_arch", lines)


def mppt_step() -> None:
    c = mp.PVM_550.at(800, 45, 26)
    v_mpp, p_mpp = c.mpp()
    lines = [f"perturb and observe on one string at 800 W/m2, 45 C: MPP "
             f"{v_mpp:.0f} V, {p_mpp / 1e3:.2f} kW",
             "  start at 0.95 V_oc; one step every 0.1 s (DC link settles,"
             " A-151)",
             "  step V   time to reach 99.5 %   steady loss (mean)"]
    for step in (1.0, 2.0, 5.0, 10.0, 20.0):
        po = mp.PerturbObserve(v_ref=0.95 * c.voc, step=step)
        v = po.v_ref
        reach, p_hist = None, []
        for k in range(600):
            v = po.update(v, float(c.i(v)))
            p = float(c.p(v))
            if reach is None and p >= 0.995 * p_mpp:
                reach = k + 1
            p_hist.append(p)
        loss = 1 - np.mean(p_hist[-200:]) / p_mpp
        lines.append(f"  {step:5.0f}   {0.1 * reach:14.1f} s   "
                     f"{100 * loss:14.3f} %")
    lines += ["  a big step finds the MPP fast but keeps dithering around it;",
              "  a small step wastes little in steady sun but lags a cloud"]
    emit("b_mppt", lines)
    conds = [(1000, 25), (1000, 65), (500, 45), (200, 30)]
    curves = [mp.PVM_550.at(g, t, 26) for g, t in conds]
    v = np.linspace(0, 1300, 261)
    csv("ch09-pv.csv", "v," + ",".join(f"p{k}" for k in range(4)),
        [(f"{vv:.0f}",) + tuple(f"{float(c.p(min(vv, c.voc))) / 1e3:.3f}"
                                for c in curves) for vv in v])


def dclink() -> None:
    i_rms, _ = stack_current()
    m, pf = 0.95, 1.0
    i_c = pe.dclink_ripple_current_rms(i_rms, m, pf)
    cap_i, cap_c, cap_v = 65.0, 1.0e-3, 1300.0              # A-152
    n_cap = math.ceil(i_c / cap_i)
    c_tot = n_cap * cap_c
    e_1500 = pe.capacitor_energy_j(c_tot, 1500)
    r_bl = 50e3
    t_50 = r_bl * c_tot * math.log(1500 / 50)
    lines = [f"DC link of one stack: phase current {i_rms:,.0f} A RMS, m {m}:",
             f"  capacitor ripple current {i_c:,.0f} A RMS (closed form)",
             f"  film capacitors 1 mF / 1300 V / {cap_i:.0f} A each (A-152): "
             f"{n_cap} needed for the ripple",
             f"  bank {c_tot * 1e3:.0f} mF; energy at 1500 V (cold open circuit)"
             f" {e_1500 / 1e3:.1f} kJ",
             f"  holds 1.25 MW for "
             f"{1e3 * c_tot * (1050 ** 2 - 950 ** 2) / 2 / 1.25e6:.1f} ms "
             "from 1050 to 950 V",
             f"  50 kohm bleeder: 1500 -> 50 V in {t_50:,.0f} s "
             f"({t_50 / 60:.0f} min);",
             "    the maker states the real wait time on the label",
             "  the ripple current, not the capacitance, sizes the bank"]
    emit("b_dclink", lines)


def lcl() -> None:
    s, v_ll, v_dc, f_sw = STACK["s"], STACK["v_ll"], STACK["v_dc"], STACK["f_sw"]
    i_rms, i_pk = stack_current()
    z_b = v_ll ** 2 / s
    w1 = 2 * math.pi * 50
    l_b, c_b = z_b / w1, 1 / (w1 * z_b)
    ripple = 0.20 * i_pk                                       # A-154
    l1 = pe.l_for_ripple(v_dc / 2, f_sw, ripple)              # NPC: V_dc/2 steps
    c = 0.05 * c_b
    att = 0.10                                                 # A-154
    w_sw = 2 * math.pi * f_sw
    l2 = (1 + 1 / att) / (w_sw ** 2 * c)
    f_res = pe.lcl_resonance(l1, l2, c)
    r_d = 1 / (3 * 2 * math.pi * f_res * c)
    i_c1 = (v_ll / S3) * w1 * c
    p_d = 3 * r_d * i_c1 ** 2
    l_only = pe.l_for_ripple(v_dc / 2, f_sw, att * ripple)
    drop = w1 * l_only * i_rms / (v_ll / S3)
    lines = [f"LCL filter of one stack, {s / 1e6:.3f} MVA, 600 V, NPC at "
             f"{f_sw / 1e3:.0f} kHz (A-154):",
             f"  bases: Z {z_b * 1e3:.1f} mohm, L {l_b * 1e3:.3f} mH, "
             f"C {c_b * 1e3:.2f} mF",
             f"  L1 for 20 % ripple ({ripple:,.0f} A): {l1 * 1e6:.1f} uH = "
             f"{l1 / l_b:.3f} pu",
             f"  C for 5 % reactive power: {c * 1e6:.0f} uF per phase (star),"
             f" {0.05 * s / 1e3:.0f} kvar",
             f"  L2 for grid ripple 10 % of converter ripple: {l2 * 1e6:.1f} uH"
             f" = {l2 / l_b:.3f} pu",
             f"  resonance {f_res:,.0f} Hz: inside 10 f1 = 500 Hz to f_sw/2 = "
             f"{f_sw / 2:,.0f} Hz",
             f"  damping resistor 1 / (3 w_res C) = {r_d * 1e3:.0f} mohm; "
             f"its fundamental loss {p_d:.0f} W",
             f"  an L-only filter for the same grid ripple: "
             f"{l_only * 1e6:.0f} uH,",
             f"    drop {100 * drop:.0f} % of phase voltage at rated current:"
             " not workable"]
    emit("b_filter", lines)
    f = np.logspace(1, 4, 300)
    g_u = pe.lcl_gain(f, l1, l2, c)
    g_d = pe.lcl_gain(f, l1, l2, c, r_d)
    g_l = 1 / (2 * np.pi * f * (l1 + l2))
    db = lambda g: 20 * np.log10(g / (1 / (w1 * (l1 + l2))))
    csv("ch09-lcl.csv", "f,und,damp,lonly",
        [(f"{a:.1f}", f"{db(b):.2f}", f"{db(cc):.2f}", f"{db(d):.2f}")
         for a, b, cc, d in zip(f, g_u, g_d, g_l)])


def magnetics() -> None:
    _, i_pk = stack_current()
    l1 = pe.l_for_ripple(STACK["v_dc"] / 2, STACK["f_sw"], 0.2 * i_pk)
    i_max = i_pk * 1.1
    e = 0.5 * l1 * i_max ** 2
    b = 1.0
    w = b * b / (2 * 4e-7 * math.pi)
    lines = [f"converter-side inductor L1 = {l1 * 1e6:.1f} uH per phase:",
             f"  stored energy at peak current plus ripple ({i_max:,.0f} A):"
             f" {e:.0f} J",
             f"  energy density in an air gap at {b} T: {w / 1e3:.0f} kJ/m3",
             f"  gap volume about {1e6 * e / w:.0f} cm3 per phase: the gap,"
             " not the iron,",
             "    stores the energy (chapter 8, magnetic circuit)",
             "  the core must not saturate at fault current; inductance that",
             "  collapses lets the current rise fast (protection, section C)"]
    emit("b_magnetics", lines)


def busbar() -> None:
    di_dt = 5e9                                             # A/s (A-155)
    v_op = 1300 / 2
    lines = [f"turn-off overshoot in an NPC commutation loop, di/dt "
             f"{di_dt / 1e9:.0f} kA/us (A-155):"]
    for l_s in (30e-9, 60e-9, 100e-9):
        dv = pe.overshoot_v(l_s, di_dt)
        lines.append(f"  loop {l_s * 1e9:3.0f} nH: overshoot {dv:4.0f} V; device "
                     f"sees {v_op + dv:5.0f} V of 1200 V")
    lines += ["  laminated busbars (plates separated by thin insulation)",
              "  keep the loop small; slower switching cuts overshoot but",
              "  raises switching loss: a design trade-off"]
    emit("b_busbar", lines)


def gate() -> None:
    q_g, dv_g, f = 10e-6, 23.0, STACK["f_sw"]              # A-155
    p_g = pe.gate_drive_power(q_g, dv_g, f)
    v_err = pe.deadtime_error(STACK["v_dc"] / 2, 3e-6, f)
    lines = [f"gate drive of one switch position (Q_g 10 uC, +15/-8 V, "
             f"{f / 1e3:.0f} kHz; A-155):",
             f"  gate power {p_g:.2f} W; twelve positions per stack "
             f"{12 * p_g:.1f} W",
             f"  dead time 3 us: mean voltage error {v_err:.1f} V = "
             f"{100 * v_err / (STACK['v_ll'] / S3):.1f} % of phase voltage",
             "    (compensated in the controller from the current sign)",
             "  desaturation detection turns a shorted switch off within a few",
             "  microseconds, inside the short-circuit time on the data sheet"]
    emit("b_gate", lines)


def cooling() -> None:
    i_rms, i_pk = stack_current()
    leg = pe.npc_leg_losses(i_pk, 0.95, math.degrees(math.acos(0.9)),
                            STACK["v_dc"], STACK["f_sw"], DEV_NPC)
    semi = 3 * sum(leg.values())
    other = {"filter inductors": 0.0035 * STACK["s"],
             "capacitors, busbars, cables": 0.0010 * STACK["s"],
             "control, fans, auxiliaries": 0.0012 * STACK["s"]}    # A-156
    total = semi + sum(other.values())
    cp, dt = 3600.0, 6.0                                     # glycol, A-156
    lines = [f"heat of one stack at full apparent power, pf 0.9 (A-156):",
             f"  semiconductors (NPC model) {semi / 1e3:5.1f} kW"]
    for k, v in other.items():
        lines.append(f"  {k:28s} {v / 1e3:5.1f} kW")
    lines += [f"  total {total / 1e3:.1f} kW per stack, "
              f"{4 * total / 1e3:.0f} kW for the 5 MW inverter",
              f"  liquid loop, cp 3.6 kJ/(kg K), rise {dt:.0f} K: "
              f"{4 * total / (cp * dt):.1f} kg/s"]
    rho0, rho = 1.20, 1.20 * 877.7 / 1013.25
    q_air = 4 * total / (rho * 1005 * 15)
    lines += [f"  if cooled by air (rise 15 K) at 1200 m (air "
              f"{rho:.2f} kg/m3): {q_air:.1f} m3/s,",
              f"    {100 * (rho0 / rho - 1):.0f} % more volume than at sea level:"
              " the reason for altitude derating"]
    emit("b_cooling", lines)


def ratings() -> None:
    i_rms, i_pk = stack_current()
    lines = ["ratings that set the assembly (A-157):"]
    for t_amb, i_mod in ((25, 1400.0), (40, 1150.0), (50, 950.0)):
        n = math.ceil(1.1 * i_pk / i_mod)
        lines.append(f"  module allowed {i_mod:.0f} A peak at {t_amb} C "
                     f"coolant -> {n} in parallel per position")
    lines += [f"  stack peak current with 10 % ripple margin: {1.1 * i_pk:,.0f}"
              " A",
              "  one more parallel module per position adds 12 modules,",
              "  their drivers and busbar space in each of the four stacks",
              "  voltage: 1200 V devices at 650 V working plus overshoot;",
              "  capacitors at 1000 to 1300 V working on 1300 V parts: the",
              "  margin is a reliability choice (cosmic-ray failures of power",
              "  devices grow steeply with DC voltage and altitude)"]
    emit("b_ratings", lines)


if __name__ == "__main__":
    architecture()
    mppt_step()
    dclink()
    lcl()
    magnetics()
    busbar()
    gate()
    cooling()
    ratings()
