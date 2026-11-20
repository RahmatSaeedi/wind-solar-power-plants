"""Chapter 8 - further lessons: synchronous-machine fault transients, dq
torque and a consistency check, swing equation and inertia, affinity laws
and drives, winding and magnet materials, slot tones, reliability, shaft
stress, the drivetrain loss chain, a backup-generator study, and broken
rotor bars in the motor-current spectrum.

Run from the project root:   python -m companion.ch08.examples_more
Writes companion/ch08/expected/x_*.txt and diagrams/data/ch08-*.csv.
Teaching values A-111, A-113, A-114, A-123 .. A-129 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch08.common import csv, emit
from companion.ch08.examples_a import MOTOR
from plantp import machines as m

S3 = math.sqrt(3)
W = 2 * math.pi * 50


def fault_transient() -> None:
    xd2, xd1, xd = 0.12, 0.20, 2.5                                # A-113
    td2, td1, ta = 0.03, 0.40, 0.04                               # A-123
    i_r = 200e3 / (S3 * 400)
    t = np.linspace(0, 1.0, 2001)
    env = (1 / xd2 - 1 / xd1) * np.exp(-t / td2) \
        + (1 / xd1 - 1 / xd) * np.exp(-t / td1) + 1 / xd
    lines = ["three-phase fault at the terminals of the backup generator "
             "(A-113, A-123):"]
    for tt in (0.0, 0.02, 0.1, 0.5, 1.0):
        k = int(round(tt / 0.0005))
        lines.append(f"  t {1000 * tt:5.0f} ms: symmetrical RMS {env[k]:5.2f} pu "
                     f"= {env[k] * i_r:6.0f} A")
    lines += [f"  steady state 1/x_d = {1 / xd:.2f} pu: below rated current;",
              "  the AVR forces the field up and holds a few pu for a while,",
              "  so protection can see the fault (chapter 26)",
              f"  DC offset decays with T_a = {1000 * ta:.0f} ms (chapter 7)"]
    emit("x_transient", lines)
    csv("ch08-transient.csv", "t,env", [(f"{a:.3f}", f"{b:.3f}")
                                        for a, b in zip(t[::10], env[::10])])


def dq_torque() -> None:
    e_ph, f, poles = 690 / S3, 57.75, 6                           # A-111
    w_e = 2 * math.pi * f
    psi = math.sqrt(2) * e_ph / w_e
    t_rated = m.torque_nm(5.32e6 * 0.97, 1155)        # after the gearbox
    iq_pk = t_rated / (1.5 * (poles / 2) * psi)
    emit("x_dq", [
        f"magnet flux linkage psi = sqrt2 E / omega_e = {psi:.3f} Wb "
        f"(E {e_ph:.1f} V, {f} Hz)",
        f"torque of a surface-magnet machine T = 1.5 (p/2) psi i_q; for "
        f"{t_rated / 1e3:.1f} kN m:",
        f"  i_q = {iq_pk:,.0f} A peak = {iq_pk / math.sqrt(2):,.0f} A RMS",
        "  rated current of A-111 is 4,518 A: the numbers agree within a few",
        "  per cent, a consistency check between torque, EMF and current",
        "  the converter controls i_q for torque and keeps i_d near zero",
        "  (or negative to weaken the field at high speed)",
    ])


def swing() -> None:
    h, s_r, f = 1.0, 200e3, 50.0                                  # A-123
    e_k = h * s_r
    p_max_pu, p0 = 0.8, 0.5
    d0 = math.asin(p0 / p_max_pu)
    k_s = p_max_pu * math.cos(d0)
    w_n = math.sqrt(2 * math.pi * f * k_s / (2 * h))
    lines = [f"backup generator H {h} s (A-123): stored energy {e_k / 1e3:.0f} kJ "
             f"at {s_r / 1e3:.0f} kVA",
             "swing equation 2H/omega_s d2(delta)/dt2 = P_m - P_e (per unit)",
             f"  P_max {p_max_pu} pu, P {p0} pu: delta0 {math.degrees(d0):.1f} deg, "
             f"synchronising power {k_s:.3f} pu/rad",
             f"  natural frequency {w_n / (2 * math.pi):.2f} Hz: the rotor "
             "swings a few times per second",
             "turbine rotor of Plant P: H 5.9 s (chapter 4) behind a "
             "converter;",
             "  a load step of 0.1 pu on a grid of synchronous machines with "
             "H 5 s:",
             f"  initial rate of change of frequency {0.1 / (2 * 5) * 50:.2f} "
             "Hz/s"]
    emit("x_swing", lines)


def affinity() -> None:
    p_r, hours = 15.0, 6000.0                                     # A-124
    lines = [f"fan of {p_r:.0f} kW (A-124): power ~ speed cubed (affinity "
             "laws), flow ~ speed"]
    for k in (1.0, 0.9, 0.8, 0.7, 0.5):
        lines.append(f"  speed {100 * k:3.0f} %: flow {100 * k:3.0f} %, power "
                     f"{p_r * k ** 3:5.2f} kW")
    damper = p_r * 0.85
    vfd = p_r * 0.7 ** 3 / 0.97
    lines += [f"70 % flow for {hours:.0f} h/yr: damper about {damper:.1f} kW, "
              f"drive {vfd:.1f} kW",
              f"  saving {(damper - vfd) * hours / 1e3:.1f} MWh/yr per fan "
              "(drive losses 3 % included)",
              "  the drive adds harmonics (chapter 7) and needs cooling"]
    emit("x_affinity", lines)


def materials() -> None:
    rho_cu, rho_al = 1.72e-8, 2.82e-8
    d_cu, d_al = 8960.0, 2700.0
    area = rho_al / rho_cu
    mass = area * d_al / d_cu
    lines = ["aluminium instead of copper for the same resistance:",
             f"  area x {area:.2f}, mass x {mass:.2f} (lighter, bulkier)",
             "magnet families (indicative, A-118 / A-125 teaching values):"]
    for name, br, alpha, tmax in (("NdFeB", 1.2, -0.12, 150),
                                  ("SmCo", 1.05, -0.035, 300),
                                  ("ferrite", 0.40, -0.20, 250)):
        lines.append(f"  {name:8s} Br {br:4.2f} T, {alpha:6.3f} %/K, use up to "
                     f"about {tmax} C")
    lines.append("  ferrite needs about three times the magnet area for the "
                 "same flux")
    emit("x_materials", lines)


def slot_tone() -> None:
    slots, n = 54, 1155.0                                         # A-125
    f_slot = slots * n / 60
    lines = [f"geared generator with {slots} stator slots (q 3, 6 poles; A-125):",
             f"  slot-passing frequency {slots} x {n / 60:.2f} Hz = "
             f"{f_slot:.1f} Hz"]
    for n2 in (700, 1155):
        lines.append(f"  at {n2} rpm: {slots * n2 / 60:.0f} Hz (moves with speed)")
    lines += ["  a tone in the nacelle can radiate; tonality is judged in the",
              "  noise assessment (chapter 33); skewing and slot design reduce it"]
    emit("x_tone", lines)


def reliability() -> None:
    lam, mttr_d, n_units = 0.05, 20.0, 12                          # A-126
    unavail = lam * mttr_d / 365
    e_lost = lam * mttr_d * 24 * 18.7e3 / 8760 * n_units
    lines = [f"generator failure rate {lam}/yr, repair {mttr_d:.0f} days incl. "
             "logistics (A-126):",
             f"  unavailability per turbine {100 * unavail:.2f} %; expected "
             f"failures in 20 yr x 12: {lam * 20 * n_units:.0f}",
             f"  energy lost per year, 12 turbines: {e_lost:,.0f} MWh "
             "(average output 18.7 GWh/yr)"]
    lines.append(f"  if a crane must come from abroad, MTTR 60 d: "
                 f"{100 * lam * 60 / 365:.2f} % per turbine")
    lines.append("  logistics, not the repair itself, dominates the downtime")
    emit("x_reliability", lines)


def shaft() -> None:
    lines = ["torsional shear stress tau = 16 T / (pi d^3) (A-126):"]
    for name, t, d in (("generator shaft", 44.0e3, 0.18),
                       ("main shaft (rotor side)", 4.84e6, 0.75)):
        tau = 16 * t / (math.pi * d ** 3)
        lines.append(f"  {name:24s} T {t / 1e3:7.1f} kN m, d {d} m: "
                     f"{tau / 1e6:5.1f} MPa")
    tau_sc = 6 * 16 * 44.0e3 / (math.pi * 0.18 ** 3)
    lines += [f"  a short-circuit torque peak of 6 x rated on the generator "
              f"shaft: {tau_sc / 1e6:.0f} MPa",
              "  the coupling's slip clutch limits what reaches the gearbox;",
              "  fatigue under millions of torque cycles decides the size "
              "(chapter 4)"]
    emit("x_shaft", lines)


def loss_chain() -> None:
    stages = [("gearbox", 0.970, 0.30), ("generator", 0.970, 0.35),
              ("converter", 0.975, 0.20), ("turbine transformer", 0.990, 0.50)]
    lines = ["drivetrain chain at rated and at 25 % load (A-047, A-111, A-128);",
             "  gearbox x generator x converter x turbine transformer:"]
    for load in (1.0, 0.25):
        p = load
        parts = []
        for name, eta, share in stages:
            p = p * m.efficiency(load, 1.0, eta, share)
            parts.append(f"{m.efficiency(load, 1.0, eta, share):.3f}")
        lines.append(f"  {100 * load:3.0f} % load: " + " x ".join(parts)
                     + f" = {p / load:.3f}")
    lines.append("  most stages lose more, in per cent, at part load")
    emit("x_chain", lines)


def backup_study() -> None:
    loads = [("UPS and DC chargers", 12.0, 0.9), ("SCADA, telecom", 8.0, 0.95),
             ("battery HVAC (S1)", 60.0, 0.85), ("control HVAC", 25.0, 0.85),
             ("lighting, essential", 3.0, 0.95), ("fire and security", 4.0, 0.9)]
    p = sum(x[1] for x in loads)
    q = sum(x[1] * math.tan(math.acos(x[2])) for x in loads)
    s = math.hypot(p, q)
    lines = ["essential loads on the backup generator (A-129):"]
    for name, kw, pf in loads:
        lines.append(f"  {name:22s} {kw:5.1f} kW, pf {pf}")
    lines += [f"  total {p:.1f} kW, {q:.1f} kvar, {s:.1f} kVA, pf {p / s:.2f}",
              f"  with 25 % margin {1.25 * s:.0f} kVA; the largest motor start "
              "(30 kW DOL) wants",
              "  about 275 kVA for a 15 % dip (problem 55), or a soft start "
              "on 200 kVA",
              "  the rating is set by the motor start and the margin, "
              "whichever is larger"]
    emit("x_backup", lines)


def mcsa() -> None:
    im = m.InductionMachine(**MOTOR)
    s = im.slip_for_shaft_power(30e3)
    f = 50.0
    fs, dur = 2000.0, 20.0
    t = np.arange(0, dur, 1 / fs)
    rng = np.random.default_rng(13)                                # A-127
    i = math.sqrt(2) * 53.8 * np.sin(2 * math.pi * f * t)
    sb = 0.006 * math.sqrt(2) * 53.8                             # -44 dB
    i += sb * np.sin(2 * math.pi * (1 - 2 * s) * f * t)
    i += sb * np.sin(2 * math.pi * (1 + 2 * s) * f * t)
    i += 0.3 * rng.standard_normal(len(t))
    win = np.hanning(len(t))
    spec = np.abs(np.fft.rfft(i * win)) / (win.sum() / 2)
    fr = np.fft.rfftfreq(len(t), 1 / fs)
    db = 20 * np.log10(spec / spec.max())
    sel = (fr > 45) & (fr < 55)
    lo, hi = (1 - 2 * s) * f, (1 + 2 * s) * f
    k_lo = np.argmin(np.abs(fr - lo))
    k_hi = np.argmin(np.abs(fr - hi))
    emit("x_mcsa", [
        f"30 kW motor at rated slip {100 * s:.2f} % (A-114), synthetic current "
        "(A-127):",
        f"  broken-bar sidebands expected at (1 -+ 2s) f = {lo:.2f} and "
        f"{hi:.2f} Hz",
        f"  spectrum (Hanning, 20 s, {1 / dur:.2f} Hz bins): sidebands at "
        f"{db[k_lo]:.1f} and {db[k_hi]:.1f} dB",
        "  relative to the 50 Hz line",
        "  sidebands about 45 dB down are a typical early warning; the",
        "  record must be long and the slip known to place them",
    ])
    csv("ch08-mcsa.csv", "f,db", [(f"{a:.2f}", f"{b:.2f}")
                                  for a, b in zip(fr[sel], db[sel])])


if __name__ == "__main__":
    fault_transient()
    dq_torque()
    swing()
    affinity()
    materials()
    slot_tone()
    reliability()
    shaft()
    loss_chain()
    backup_study()
    mcsa()
