"""Chapter 9, section C - grid behaviour and manufacture: the phase-locked
loop, the current loop, grid-following and grid-forming responses to a
frequency event, weak grids, operating modes, fault ride-through,
negative sequence, common-mode current, configuration control, production
yield and inverter reliability.

Run from the project root:   python -m companion.ch09.examples_c
Writes companion/ch09/expected/c_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-158 .. A-163 (fictional); grid data A-100, A-109.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np

from companion.ch09.common import csv, emit
from companion.ch09.examples_a import EFF_POINTS
from plantp import pe

S3 = math.sqrt(3)


# [start: pll]
def srf_pll(theta_grid, dt: float, f_n: float = 20.0, zeta: float = 0.707,
            f0: float = 50.0):
    """Synchronous-reference-frame PLL on a unit grid voltage: the q-axis
    voltage sin(theta_grid - theta) drives a PI controller whose output is
    the angular frequency. Returns estimated angle and frequency arrays."""
    w_n = 2 * math.pi * f_n
    kp, ki = 2 * zeta * w_n, w_n ** 2
    theta, integ = 0.0, 0.0
    th_out = np.empty(len(theta_grid))
    f_out = np.empty(len(theta_grid))
    for k, tg in enumerate(theta_grid):
        v_q = math.sin(tg - theta)
        integ += ki * v_q * dt
        w = 2 * math.pi * f0 + kp * v_q + integ
        th_out[k], f_out[k] = theta, w / (2 * math.pi)
        theta += w * dt
    return th_out, f_out
# [end: pll]


def pll() -> None:
    dt, t_end = 1e-4, 0.6
    t = np.arange(int(t_end / dt)) * dt
    f_g = np.where(t < 0.3, 50.0, 50.5)                          # step at 0.3 s
    th_g = np.cumsum(2 * np.pi * f_g) * dt
    th_g = th_g + np.where(t >= 0.1, math.radians(30), 0.0)      # jump at 0.1 s
    th, f = srf_pll(th_g, dt)
    err = np.degrees(np.angle(np.exp(1j * (th_g - th))))
    after = t >= 0.1
    k5 = np.flatnonzero(after & (np.abs(err) < 2))
    settle = None
    for k in k5:
        if np.all(np.abs(err[k:int(0.3 / dt)]) < 2):
            settle = t[k] - 0.1
            break
    f_after = f[(t > 0.3)]
    lines = ["synchronous-frame PLL, bandwidth 20 Hz, damping 0.707 (A-158):",
             f"  30 deg phase jump at 0.1 s: error back within 2 deg after "
             f"{1e3 * settle:.0f} ms;",
             f"    meanwhile the frequency estimate jumps to "
             f"{f[(t >= 0.1) & (t < 0.3)].max():.1f} Hz for a few ms",
             f"  frequency step 50 -> 50.5 Hz at 0.3 s: estimate overshoots to "
             f"{f_after.max():.2f} Hz",
             f"    and reads {f[-1]:.3f} Hz at 0.6 s; peak transient error "
             f"{np.abs(err[t > 0.3]).max():.1f} deg",
             "  a faster PLL follows sooner but passes more noise and, in a",
             "  weak grid, can interact with the converter's own current;",
             "  a frequency or RoCoF protection fed from such an estimate",
             "  needs filtering, or a phase jump trips it falsely"]
    emit("c_pll", lines)
    csv("ch09-pll.csv", "t,err,f",
        [(f"{a:.4f}", f"{b:.2f}", f"{c:.3f}") for a, b, c in
         zip(t[::20], err[::20], f[::20])])


def current_loop() -> None:
    l_pu, r_pu, wb = 0.128, 0.005, 2 * math.pi * 50        # A-154 filter
    w_c = 2 * math.pi * 300                                  # bandwidth
    kp, ki = l_pu / wb * w_c, r_pu * w_c
    dt = 1e-6
    t = np.arange(int(0.006 / dt)) * dt
    ts = 1 / 6000                                             # sample, 2 f_sw
    rows = {}
    for name, delay in (("ideal", 0.0), ("delay", 1.5 * ts)):
        n_d = int(round(delay / dt))
        i, integ, buf = 0.0, 0.0, [0.0] * (n_d + 1)
        out = np.empty(len(t))
        v_hold, next_s = 0.0, 0.0
        for k, tk in enumerate(t):
            ref = 1.0 if tk >= 0.001 else 0.0
            if delay == 0.0 or tk >= next_s:
                e = ref - i
                integ += ki * e * (dt if delay == 0.0 else ts)
                v_hold = kp * e + integ
                next_s += ts
            buf.append(v_hold)
            v = buf.pop(0)
            i += (v - r_pu * i) * wb / l_pu * dt
            out[k] = i
        rows[name] = out
    lines = ["current loop of one stack in the dq frame (per unit, A-158):",
             f"  plant L {l_pu} pu, R {r_pu} pu; PI tuned for 300 Hz bandwidth",
             f"  kp {kp:.4f}, ki {ki:.3f} (zero cancels the plant pole)"]
    for name, out in rows.items():
        above = np.flatnonzero(out >= 0.9)
        t90 = (t[above[0]] - 0.001) * 1e3
        lines.append(f"  {name:6s}: 0 -> 90 % in {t90:.2f} ms, overshoot "
                     f"{100 * max(0.0, out.max() - 1):.1f} %")
    lines += ["  the computation and PWM delay (1.5 samples) adds overshoot;",
              "  it limits how fast any converter current loop can be"]
    emit("c_current", lines)
    csv("ch09-icurrent.csv", "t,ideal,delay",
        [(f"{a * 1e3:.3f}", f"{b:.4f}", f"{c:.4f}") for a, b, c in
         zip(t[::20], rows["ideal"][::20], rows["delay"][::20])])


def frequency_event() -> None:
    dt, t_end = 0.005, 20.0
    t = np.arange(int(t_end / dt)) * dt
    share_s, h_s, r_s, tau_g, d_load = 0.6, 4.0, 0.05, 5.0, 1.0   # A-159
    loss = 0.10
    cases = {"GFL, no response": dict(h_v=0.0, droop=0.0, delay=0.0),
             "GFL, fast frequency response": dict(h_v=0.0, droop=0.04,
                                                  delay=0.25),
             "GFM, inertia and droop": dict(h_v=4.0, droop=0.04, delay=0.0)}
    out = {}
    lines = ["frequency after losing 10 % of generation (system base, A-159):",
             "  60 % synchronous (H 4 s, governor droop 5 %, 5 s lag), 40 %",
             "  converters; converter headroom 5 % (curtailed or battery)"]
    for name, c in cases.items():
        h_tot = share_s * h_s + 0.4 * c["h_v"]
        df, p_gov, p_c = 0.0, 0.0, 0.0
        hist = []
        n_del = int(c["delay"] / dt)
        f_trace = np.zeros(len(t))
        for k, tk in enumerate(t):
            dp = -loss if tk >= 1.0 else 0.0
            p_gov += (-share_s * df / r_s - p_gov) * dt / tau_g
            df_seen = hist[-n_del] if n_del and len(hist) >= n_del else df
            if c["droop"]:
                p_c = float(np.clip(-0.4 * df_seen / c["droop"], -0.05, 0.05))
            ddf = (dp + p_gov + p_c - d_load * df) / (2 * h_tot)
            df += ddf * dt
            hist.append(df)
            f_trace[k] = 50 * (1 + df)
        out[name] = f_trace
        k1 = int(1.0 / dt)
        rocof = (f_trace[k1 + int(0.5 / dt)] - f_trace[k1]) / 0.5
        nadir = f_trace.min()
        lines.append(f"  {name:29s} RoCoF {rocof:6.2f} Hz/s, nadir "
                     f"{nadir:6.2f} Hz at {t[int(np.argmin(f_trace))] - 1:4.1f} s")
    lines += ["  grid-forming adds inertia at once (a voltage source behind an",
              "  impedance); grid-following must first measure the frequency",
              "  (PLL, filter), so its help arrives later; both need energy"]
    emit("c_gfm", lines)
    keys = list(out)
    csv("ch09-gfm.csv", "t,a,b,c",
        [(f"{tk:.2f}",) + tuple(f"{out[kk][i]:.4f}" for kk in keys)
         for i, tk in enumerate(t) if i % 10 == 0])


def weak_grid() -> None:
    p = 100.0
    lines = ["voltage change at the point of connection for a 100 MW swing:",
             "  S_sc MVA  SCR   z pu (100 MVA)   dV for dP 1 pu   dV for dQ 0.33 pu"]
    for s_sc in (1000.0, 500.0, 300.0, 200.0):                  # A-109, A-160
        z = p / s_sc
        x = z * 10 / math.sqrt(101)
        r = z / math.sqrt(101)
        lines.append(f"  {s_sc:7.0f}  {s_sc / p:4.1f}   {z:9.3f}        "
                     f"{100 * r:8.2f} %        {100 * x * 0.33:8.2f} %")
    lines += ["  X/R 10 (A-109): active power hardly moves the voltage, reactive",
              "  power does; in a weak grid (SCR below about 3) the same current",
              "  moves the voltage and angle much more, and grid-following",
              "  control can become unstable: check the maker's minimum SCR"]
    emit("c_scr", lines)


def modes() -> None:
    c = pe.fit_loss_coeffs(EFF_POINTS)
    p0 = c[0] * 5e6
    night = 10 * p0 * 12 * 365 / 1e6
    lines = ["operating modes of the PV inverters (teaching settings, A-161):",
             "  P(f): droop 4 %, dead band 0.2 Hz;",
             f"    at 50.5 Hz the plant reduces by "
             f"{100 * (0.3 / 50) / 0.04:.0f} % of rating",
             "  Q(U): no reactive power within +-1 %; full 0.44 pu at 5 % off",
             "    the reference voltage (slope from A-101: Q at 5 MW)"]
    for v in (0.94, 0.97, 0.99, 1.00, 1.03, 1.06):
        dv = v - 1.0
        q = 0.0 if abs(dv) <= 0.01 else -0.44 * (dv - math.copysign(0.01, dv)) / 0.04
        q = max(-0.44, min(0.44, q))
        lines.append(f"    V {v:.2f} pu -> Q {q:+.2f} pu (+ = delivered)")
    lines += [f"  Q at night: each inverter's no-load loss {p0 / 1e3:.1f} kW;",
              f"    ten inverters awake 12 h every night: {night:.0f} MWh/yr",
              "  each mode is a setting the grid code or the plant controller",
              "  asks for (chapters 17, 20, 28); the inverter offers the range"]
    emit("c_modes", lines)


def frt() -> None:
    lines = ["reactive current during a voltage dip, k 2, limit 1.1 pu (A-162):",
             "  V pu   I_q pu   I_p pu   S pu (V x I)"]
    for v in (0.95, 0.85, 0.7, 0.5, 0.2, 0.05):
        iq, ip = pe.frt_currents(v)
        lines.append(f"  {v:4.2f}   {iq:6.2f}   {ip:6.2f}   "
                     f"{v * math.hypot(iq, ip):6.2f}")
    i_inv = 10 * 1.1 * 5.5e6 / (S3 * 33e3)
    i_sm = 10 * 7.0 * 5.5e6 / (S3 * 33e3)
    lines += [f"  fault current of 10 PV inverters at 33 kV: {i_inv:,.0f} A",
              f"  ten synchronous machines of the same rating (~7 pu, chapter"
              f" 8): {i_sm:,.0f} A",
              "  converter plants feed little fault current: protection that",
              "  relies on large currents must be checked (chapter 26)"]
    v_n, c_dc, v_dc, s = 0.3, 12e-3, 1000.0, 1.375e6
    dv = v_n * s / (2 * 2 * math.pi * 50 * c_dc * v_dc)
    lines += [f"  unbalanced dip, negative-sequence voltage {v_n} pu, only",
              f"    positive-sequence current: DC-link power ripple {v_n:.1f} pu"
              f" at 100 Hz,",
              f"    voltage ripple about {dv:.0f} V on 12 mF; controlling the",
              "    negative-sequence current too removes it"]
    emit("c_frt", lines)
    vs = np.linspace(0, 1.0, 101)
    csv("ch09-frt.csv", "v,iq,ip",
        [(f"{v:.2f}",) + tuple(f"{x:.3f}" for x in pe.frt_currents(v))
         for v in vs])


def emc() -> None:
    dvdt = 5e9                                                  # V/s, A-163
    lines = ["common-mode current through stray capacitance, dv/dt 5 kV/us"
             " (A-163):"]
    for name, c in (("cable to ground, 100 m x 0.3 nF/m", 30e-9),
                    ("motor winding to frame", 10e-9)):
        lines.append(f"  {name:35s} {c * 1e9:5.0f} nF -> {c * dvdt:6.0f} A"
                     " pulses")
    lines += ["  pulses last tens of nanoseconds but their high-frequency",
              "  content radiates and couples: shielded cables bonded at both",
              "  ends, common-mode chokes, short return paths and slower",
              "  edges (three levels, gate resistance) keep emissions within",
              "  the limits of the EMC standards"]
    emit("c_emc", lines)


def configuration() -> None:
    base = ("firmware=CI-5000 4.2.1\nP_max_kW=5000\nQ_mode=QU\nQU_slope=0.44\n"
            "QU_deadband=0.01\nPf_droop=0.04\nFRT_k=2.0\nI_max=1.1\n")
    changed = base.replace("FRT_k=2.0", "FRT_k=2.5")
    h1 = hashlib.sha256(base.encode()).hexdigest()
    h2 = hashlib.sha256(changed.encode()).hexdigest()
    lines = ["configuration control of an inverter parameter set:",
             f"  approved set     SHA-256 {h1[:32]}...",
             f"  one value edited SHA-256 {h2[:32]}...",
             "  any change, however small, gives a different fingerprint; the",
             "  record keeps firmware version, parameter-set id and fingerprint",
             "  for every unit, and site readback must match it (chapter 50)"]
    emit("c_config", lines)


def production_yield() -> None:
    stages = [("SMT and reflow, AOI", 0.995), ("in-circuit test", 0.990),
              ("power module and busbar assembly", 0.985),
              ("thermal interface check", 0.995), ("enclosure integration", 0.990),
              ("burn-in", 0.990), ("end-of-line function test", 0.975)]
    fpy = 1.0
    lines = ["first-pass yield of a stack line (A-163, teaching):"]
    for name, y in stages:
        fpy *= y
        lines.append(f"  {name:34s} {y:.3f}  cumulative {fpy:.3f}")
    lines += [f"  {100 * (1 - fpy):.1f} % of stacks need rework somewhere; each",
              "  escape found on site costs about ten times one found in the",
              "  factory (chapter 1, the rule of ten): test where it is cheap"]
    emit("c_yield", lines)


def reliability() -> None:
    fit = {"IGBT modules (24)": 24 * 400, "DC-link film capacitors": 4000,
           "fans and pumps": 15000, "control and gate boards": 12000,
           "auxiliary power supplies": 6000, "contactors and breakers": 5000,
           "sensors and IMD": 4800}                              # A-163
    lam = sum(fit.values()) * 1e-9 * 8760                        # per year
    mttr = 72.0
    lines = ["failure rate of one 5 MW inverter (teaching FIT values, A-163):"]
    for k, v in fit.items():
        lines.append(f"  {k:28s} {v:6d} FIT")
    avail = 1 / (1 + lam * mttr / 8760)
    lines += [f"  total {sum(fit.values())} FIT = {lam:.2f} failures/yr; "
              f"MTBF {1 / lam:.1f} yr",
              f"  with 72 h to restore: availability {avail:.4f}"]
    mu = 10 * fit["fans and pumps"] * 1e-9 * 8760          # fan failures/yr
    p_more = 1 - sum(math.exp(-mu) * mu ** k / math.factorial(k)
                     for k in range(3))
    lines += [f"  10 inverters, fan failures {mu:.2f}/yr: chance of needing more"
              f" than 2 fans {p_more:.3f}",
              "  fans and boards fail most often but are quick to change;",
              "  power modules fail rarely but take longest: stock spares by",
              "  both the rate and the repair time (chapter 52)"]
    emit("c_reliability", lines)


if __name__ == "__main__":
    pll()
    current_loop()
    frequency_event()
    weak_grid()
    modes()
    frt()
    emc()
    configuration()
    production_yield()
    reliability()
