"""Chapter 9, section A - conversion fundamentals: why switch, devices,
rectifiers, DC-DC converters, inverter legs and PWM, the DC voltage window,
multilevel legs, conduction and switching losses, junction temperature,
efficiency curves, derating and wide-bandgap devices.

Run from the project root:   python -m companion.ch09.examples_a
Writes companion/ch09/expected/a_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-144 .. A-150 (fictional, not a product).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch09.common import csv, emit
from plantp import pe

S2, S3 = math.sqrt(2), math.sqrt(3)

# one switch position of the turbine grid-side converter, 1700 V class,
# several modules in parallel (A-144)
DEV_WIND = dict(v_t0=0.9, r_t=0.55e-3, v_d0=0.95, r_d=0.45e-3, e_on_off=1.6,
                e_rr=0.35, i_ref=3600, v_ref=900)
# one switch position of a PV inverter stack, 1200 V class, NPC (A-145)
DEV_NPC = dict(v_t0=0.75, r_t=0.35e-3, v_d0=0.8, r_d=0.3e-3, e_on_off=0.9,
               e_rr=0.2, i_ref=2800, v_ref=600)
# PV inverter data-sheet efficiency points (A-147)
EFF_POINTS = [(0.10, 0.970), (0.25, 0.983), (0.50, 0.986), (0.75, 0.985),
              (1.00, 0.983)]


def scale() -> None:
    conv = [("PV inverters", 10, 5.5), ("turbine converters", 12, 5.26),
            ("battery converter (S1)", 1, 22.0)]
    lines = ["power electronics in Plant P (A-101, A-107, BESS 20 MW):"]
    total = 0.0
    for name, n, s in conv:
        total += n * s
        lines.append(f"  {name:24s} {n:3d} x {s:5.2f} MVA = {n * s:6.1f} MVA")
    e = 273.5                                              # GWh/yr, ch 5 S0
    lines += [f"  total {total:.0f} MVA for 110 MW of generation",
              f"  every kWh of the {e} GWh/yr export passes a converter;",
              f"  one per cent of converter efficiency is {e * 0.01:.2f} GWh/yr",
              "  plus auxiliary drives, UPS and DC chargers (chapters 7, 8)"]
    emit("a_scale", lines)


def switch_vs_linear() -> None:
    v_in, v_out, i = 1000.0, 500.0, 100.0
    p_out = v_out * i
    p_lin = (v_in - v_out) * i
    v_on, e_sw, f = 2.0, 0.05, 10e3                       # A-148
    p_cond = v_on * i * v_out / v_in
    p_sw = e_sw * f
    lines = [f"500 V at 100 A from 1000 V ({p_out / 1e3:.0f} kW):",
             "  series resistor or transistor in its linear region:",
             f"    loss {p_lin / 1e3:.0f} kW, efficiency "
             f"{p_out / (p_out + p_lin):.2f}",
             f"  switch with filter, duty 0.5: conduction {p_cond:.0f} W "
             "(2 V drop),",
             f"    switching {p_sw:.0f} W (0.05 J per cycle at 10 kHz); "
             f"efficiency {p_out / (p_out + p_cond + p_sw):.4f}",
             "  a switch is either fully on (small V) or fully off (small I):",
             "  the product V I, the loss, stays small except while switching"]
    emit("a_switch", lines)


def devices() -> None:
    v0, r_igbt, r_mos = 0.8, 0.7e-3, 2.5e-3                  # A-148
    i_x = v0 / (r_mos - r_igbt)
    lines = ["on-state loss: IGBT V0 + r I versus SiC MOSFET R_on I (A-148):",
             f"  IGBT 0.8 V + 0.7 mohm; MOSFET 2.5 mohm; equal at "
             f"{i_x:.0f} A"]
    for i in (100, 300, 444, 800):
        p_i = (v0 + r_igbt * i) * i
        p_m = r_mos * i * i
        lines.append(f"  {i:4d} A: IGBT {p_i:6.0f} W, MOSFET {p_m:6.0f} W")
    lines += ["  below the crossover the MOSFET conducts better; it also",
              "  switches with far smaller energy (section A, wide bandgap)"]
    emit("a_devices", lines)


def rectifier() -> None:
    v_ll = 400.0
    lines = ["six-pulse diode bridge on 400 V, 50 Hz:",
             f"  ideal mean DC voltage 1.35 x 400 = {pe.rectifier_6p_vdc(v_ll):.1f} V",
             f"  with 0.1 mH commutation inductance at 200 A: "
             f"{pe.rectifier_6p_vdc(v_ll, 1e-4, 200):.1f} V"]
    for a in (30, 60, 90):
        lines.append(f"  thyristor bridge, firing angle {a:2d} deg: "
                     f"{pe.rectifier_6p_vdc(v_ll, alpha_deg=a):6.1f} V")
    harm = [5, 7, 11, 13, 17, 19]
    lines += ["  ideal line-current harmonics I_h / I_1 = 1 / h:",
              "    " + ", ".join(f"h {h}: {1 / h:.3f}" for h in harm)]
    thd6 = math.sqrt(sum((1 / h) ** 2 for h in harm))
    thd12 = math.sqrt(sum((1 / h) ** 2 for h in (11, 13)))
    lines += [f"  THD (to 19th) six-pulse {100 * thd6:.1f} %, "
              f"twelve-pulse {100 * thd12:.1f} % (5th, 7th cancel)",
              "  a transformer with two secondaries (star and delta) makes",
              "  the twelve-pulse rectifier (chapter 7, transformer phase shift)"]
    emit("a_rectifier", lines)


def dcdc() -> None:
    lines = []
    d = pe.buck_duty(1000, 400)
    lines += [f"buck 1000 -> 400 V: duty {d:.2f}; L 1 mH at 10 kHz: ripple "
              f"{pe.buck_ripple(1000, d, 1e-3, 10e3):.0f} A peak-to-peak"]
    v_in, v_out, p, f = 600.0, 1000.0, 50e3, 16e3              # A-149
    d = pe.boost_duty(v_in, v_out)
    i_in = p / v_in
    l_h = v_in * d / (0.2 * i_in * f)
    c_f = (p / v_out) * d / (0.01 * v_out * f)
    lines += [f"boost stage of a 50 kW string inverter, 600 -> 1000 V (A-149):",
              f"  duty {d:.2f}, input current {i_in:.1f} A",
              f"  L for 20 % ripple at 16 kHz: {l_h * 1e3:.2f} mH",
              f"  C for 1 % output ripple: {c_f * 1e6:.0f} uF",
              "  volt-second balance: V_in D T = (V_out - V_in)(1 - D) T"]
    emit("a_dcdc", lines)


def inverter_leg() -> None:
    v_dc = 1100.0
    lines = [f"two-level three-phase bridge on {v_dc:.0f} V DC:",
             "  phase fundamental peak m V_dc / 2; line RMS = m V_dc sqrt3 /"
             " (2 sqrt2)"]
    for m in (0.5, 0.8, 1.0):
        lines.append(f"  m {m:.1f}: line voltage {m * v_dc * S3 / (2 * S2):6.1f} V"
                     " RMS")
    lines += [f"  third-harmonic or space-vector PWM: m up to 2/sqrt3 = "
              f"{2 / S3:.3f} -> {v_dc / S2:.1f} V",
              "  above that the leg over-modulates and low-order harmonics"
              " appear"]
    emit("a_inverter", lines)


def pwm_waveform() -> None:
    """Carrier, reference and leg output for a figure (carrier 9 x 50 Hz)."""
    n, f1, mf, m = 3600, 50.0, 9, 0.8
    t, s_leg = pe.spwm_leg(m, f1, mf * f1, n)
    th = 2 * np.pi * f1 * t
    x = (mf * f1 * t) % 1.0
    tri = np.where(x < 0.5, 4 * x - 1, 3 - 4 * x)
    csv("ch09-pwm.csv", "t,ref,tri,out",
        [(f"{a * 1e3:.3f}", f"{m * math.sin(b):.4f}", f"{c:.4f}",
          f"{2 * d - 1:.0f}") for a, b, c, d in
         zip(t[::4], th[::4], tri[::4], s_leg[::4])])


def pwm_spectrum() -> None:
    f1, mf, m, n = 50.0, 51, 0.9, 51000
    rows = {}
    lines = [f"line-to-line PWM voltage, m {m}, carrier {mf} x 50 Hz = "
             f"{mf * 50:.0f} Hz:"]
    for lv in (2, 3):
        _, sa = pe.spwm_leg(m, f1, mf * f1, n, levels=lv)
        _, sb = pe.spwm_leg(m, f1, mf * f1, n, levels=lv, phase_deg=-120)
        scale_v = 1.0 if lv == 2 else 0.5                    # per V_dc
        v_ab = (sa - sb) * scale_v
        h, a = pe.spectrum(v_ab, f1)
        rows[lv] = a
        top = sorted(range(2, 200), key=lambda k: -a[k])[:3]
        lines.append(f"  {lv}-level: fundamental {a[1]:.3f} V_dc, THD to h 200 "
                     f"{100 * pe.thd(a, 200):.1f} %")
        lines.append("    largest: " + ", ".join(f"h {k} ({a[k]:.3f})"
                                                  for k in sorted(top)))
    lines += ["  the carrier itself (h 51) cancels between phases; the",
              "  sidebands near 51 and 2 x 51 dominate; three levels halve",
              "  the voltage steps and cut the distortion by about a quarter",
              "  at the same carrier frequency"]
    emit("a_pwm", lines)
    csv("ch09-spectrum.csv", "h,a2,a3",
        [(k, f"{rows[2][k]:.4f}", f"{rows[3][k]:.4f}") for k in range(1, 161)])


def dc_window() -> None:
    lines = ["smallest DC voltage for an AC line voltage (linear PWM):",
             "  V_LL    sine-triangle   space-vector   s-v + 10 % headroom"]
    for v in (400, 600, 630, 690):
        lines.append(f"  {v:4d} V  {pe.vdc_min(v, 'spwm'):10.0f} V"
                     f"  {pe.vdc_min(v):10.0f} V  {pe.vdc_min(v, headroom=0.1):12.0f} V")
    lines += ["  headroom (A-150): grid +5 %, filter drop 3 %, control 2 %",
              f"  the 850 V lower MPPT bound of chapter 6 (A-020) supports "
              f"at most {pe.vll_max(850):.0f} V",
              f"    AC without headroom, {pe.vll_max(850 / 1.1):.0f} V with it;"
              " a 690 V inverter needs about 1073 V"]
    emit("a_window", lines)


def npc() -> None:
    v_dc_max = 1500.0
    _, s2 = pe.spwm_leg(0.9, 50, 3000, 60000, levels=2)
    lines = ["device voltage in a 1500 V PV inverter (open-circuit, cold):",
             f"  two-level: each switch blocks {v_dc_max:.0f} V -> devices of "
             "2.3 to 3.3 kV class",
             f"  three-level NPC: each switch blocks {v_dc_max / 2:.0f} V -> "
             "1200 V class",
             "  1200 V devices have much lower switching energy, and each",
             "  step of the output voltage is V_dc / 2 (lower dv/dt, ripple)",
             "  price: 12 switches and 6 clamp diodes per three-phase bridge",
             "  and a neutral point whose voltage the control must balance"]
    emit("a_npc", lines)


def losses() -> None:
    s, v_ll, v_dc, pf = 5.26e6, 690.0, 1150.0, 0.95             # A-107
    i_pk = s / (S3 * v_ll) * S2
    m = 2 * S2 * v_ll / S3 / v_dc
    phi = math.acos(pf)
    d = DEV_WIND
    lines = [f"grid-side converter of a turbine, {s / 1e6:.2f} MVA, 690 V,",
             f"  V_dc {v_dc:.0f} V, pf {pf}; one switch position = parallel"
             " modules (A-144):",
             f"  current peak {i_pk:,.0f} A, modulation index {m:.3f}"]
    rows = []
    for f_sw in (1000, 1500, 2000, 2500, 3000, 4000, 5000):
        ct, cd = pe.conduction_losses(i_pk, m, pf, d["v_t0"], d["r_t"],
                                      d["v_d0"], d["r_d"])
        st, sd = pe.switching_losses(i_pk, v_dc, f_sw, d["e_on_off"],
                                     d["e_rr"], d["i_ref"], d["v_ref"])
        cond, sw = 6 * (ct + cd), 6 * (st + sd)
        rows.append((f_sw, f"{cond / 1e3:.2f}", f"{sw / 1e3:.2f}"))
        if f_sw == 2500:
            lines += [f"  per switch position: IGBT {ct:,.0f} W + {st:,.0f} W, "
                      f"diode {cd:,.0f} W + {sd:,.0f} W",
                      f"  six positions at 2.5 kHz: conduction {cond / 1e3:.1f} kW,"
                      f" switching {sw / 1e3:.1f} kW",
                      f"  total {(cond + sw) / 1e3:.1f} kW = "
                      f"{100 * (cond + sw) / (s * pf):.2f} % of the active power"]
    lines.append("  switching loss grows with f_sw; conduction does not")
    emit("a_losses", lines)
    csv("ch09-fsw.csv", "f,cond,sw", rows)


def thermal() -> None:
    r_th = [0.002, 0.004, 0.008, 0.012]                       # K/W, A-148
    tau = [0.002, 0.02, 0.15, 1.2]                            # s
    p_avg = 1500.0                                            # W per IGBT
    lines = ["junction temperature of one IGBT position (Foster network,"
             " A-148):",
             f"  R_th junction-to-coolant {sum(r_th):.3f} K/W; mean loss "
             f"{p_avg:.0f} W -> mean rise {p_avg * sum(r_th):.0f} K"]
    rows = None
    ripple = {}
    for f in (50.0, 10.0, 1.0):
        dt = 1 / (f * 400)
        t = np.arange(int(6 / f * 400 + 8 / dt)) * dt if f < 5 else \
            np.arange(int(4.0 / dt)) * dt
        p = p_avg * 4 * np.maximum(np.sin(2 * np.pi * f * t), 0) ** 2
        rise = pe.foster_sim(p, dt, r_th, tau)
        last = rise[-int(1 / f / dt):]
        ripple[f] = float(np.ptp(last))
        if f == 10.0:
            rows = [(f"{tt:.4f}", f"{40 + r:.2f}")
                    for tt, r in zip(t[-int(0.3 / dt)::4] - t[-int(0.3 / dt)],
                                     rise[-int(0.3 / dt)::4])]
    for f, d in ripple.items():
        lines.append(f"  output {f:4.0f} Hz: junction swing {d:5.1f} K, relative"
                     f" cycle life {pe.relative_cycle_life(d, ripple[50.0]):.3f}")
    lines += ["  slow output (machine side at low speed, or a stalled motor)",
              "  lets each half-wave heat the chip: bigger swings, shorter life"]
    emit("a_thermal", lines)
    csv("ch09-tj.csv", "t,tj", rows)


def efficiency() -> None:
    c = pe.fit_loss_coeffs(EFF_POINTS)
    lines = ["5 MW PV inverter, data-sheet efficiency points (A-147):",
             "  " + ", ".join(f"{int(100 * p)} %: {e}" for p, e in EFF_POINTS),
             f"  fitted loss = {c[0] * 1e3:.2f} + {c[1] * 1e3:.2f} P + "
             f"{c[2] * 1e3:.2f} P^2 (per mille of rating)",
             "    no-load (fixed) + linear (V0 I) + square (R I^2) terms",
             f"  weighted: European {pe.weighted_efficiency(c, pe.EURO_WEIGHTS):.4f},"
             f" CEC {pe.weighted_efficiency(c, pe.CEC_WEIGHTS):.4f}"]
    p = np.linspace(0.02, 1.0, 50)
    e = pe.efficiency_from_coeffs(p, c)
    k = int(np.argmax(e))
    lines.append(f"  peak {e[k]:.4f} at {p[k]:.2f} pu; at 5 % load "
                 f"{float(pe.efficiency_from_coeffs(0.05, c)):.4f}")
    emit("a_eff", lines)
    csv("ch09-eff.csv", "p,eff", [(f"{a:.3f}", f"{b:.5f}") for a, b in zip(p, e)])


def derating() -> None:
    lines = ["teaching derating curve (A-147): full output to 40 C, -2 %/K",
             "  above; -1 % per 100 m above 1000 m altitude:"]
    for t in (35, 40, 45, 50, 55):
        lines.append(f"  {t} C at 1200 m: {float(pe.derating(t, 1200)):.2f} pu"
                     f" = {5.0 * float(pe.derating(t, 1200)):.2f} MW")
    lines += ["  hot hours cost energy only when the plant would otherwise",
              "  run near full output: the data-pack lab counts them (D)"]
    emit("a_derate", lines)


def wbg() -> None:
    p = 100e3
    lines = ["100 kW string-inverter stage, silicon IGBT vs SiC MOSFET (A-148):"]
    for name, e_sw, f in (("Si IGBT", 6e-3, 16e3), ("SiC MOSFET", 1.2e-3, 16e3),
                          ("SiC MOSFET", 1.2e-3, 48e3)):
        p_sw = 6 * e_sw * f / math.pi
        lines.append(f"  {name:10s} at {f / 1e3:2.0f} kHz: switching about "
                     f"{p_sw / 1e3:.2f} kW ({100 * p_sw / p:.2f} %)")
    lines += ["  at three times the frequency SiC still switches with less",
              "  loss, and the filter inductance falls in proportion (L ~ 1/f):",
              "  smaller magnetics, higher price per ampere (chapter 44)"]
    emit("a_wbg", lines)


if __name__ == "__main__":
    scale()
    switch_vs_linear()
    devices()
    rectifier()
    dcdc()
    inverter_leg()
    pwm_waveform()
    pwm_spectrum()
    dc_window()
    npc()
    losses()
    thermal()
    efficiency()
    derating()
    wbg()
