"""Chapter 34, lesson A: the measurement chain in numbers - range and
scaling of a 4-20 mA signal, the longest loop a transmitter tolerates,
converter resolution, the uncertainty of the POC voltage from the VT to
the controller, a Pt100 and its leads, a thermocouple's cold junction,
RMS over whole cycles and aliasing, clock drift and the order of events,
calibration intervals, and what a filter costs in delay.

Run from the project root:   python -m companion.ch34.examples_a
Writes companion/ch34/expected/a_*.txt and diagrams/data/ch34-uncert.csv,
ch34-filter.csv. Teaching values (A-385, A-386).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch34 import sources as src
from companion.ch34.common import csv, emit
from plantp import instrumentation as ic
from plantp import signals as sg


def scaling() -> None:
    lo, hi = src.CHAIN["tx_range_kv"]
    rows = [(0.90, "low limit"), (1.00, "nominal"), (1.10, "high limit"),
            (1.13, "range end"), (1.20, "fault swell")]
    lines = ["POC voltage on a 0-150 kV transducer (4-20 mA, live zero)",
             "  per unit   kV       mA      reading kV"]
    for pu, note in rows:
        kv = pu * src.CHAIN["u_nom_kv"]
        ma = ic.eng_to_ma(kv, lo, hi)
        shown = ic.ma_to_eng(min(ma, 20.5), lo, hi)       # module saturates
        lines.append(f"  {pu:8.2f}   {kv:6.1f}   {ma:6.2f}   {shown:9.1f}   {note}")
    clip = ic.ma_to_eng(20.5, lo, hi) / src.CHAIN["u_nom_kv"]
    lines += ["  the range leaves 13 % above nominal: every normal and",
              f"  emergency voltage is read, but a swell above {clip:.2f} pu is",
              "  clipped by the module - a recorder for disturbances uses",
              "  its own wider channel (ch 27); 0 kV reads 4 mA, so a",
              "  dead loop (0 mA) is told apart from a dead line"]
    emit("a_scaling", lines)


def loop_length() -> None:
    lines = ["longest two-wire 4-20 mA loop: 24 V supply, transmitter >= 12 V,",
             "  250 ohm receiver, 22 mA (top of the fault-signalling range)",
             "  cable mm2   cable ohm allowed   longest loop m (one way)"]
    for a in (0.5, 0.75, 1.5):
        length = ic.loop_max_length(src.LOOP["v_supply"], src.LOOP["v_min_tx"],
                                    src.LOOP["r_receiver"], a)
        r = 12.0 / 0.022 - 250.0
        lines.append(f"  {a:9.2f}   {r:17.0f}   {length:24,.0f}")
    lines += ["  the 250 ohm receiver takes most of the voltage, not the",
              "  cable: even 0.5 mm2 reaches several kilometres - the",
              "  limit that bites first is noise pick-up and earthing,",
              "  not resistance"]
    emit("a_loop", lines)


def resolution() -> None:
    c = src.CHAIN
    step_ma = ic.adc_step(c["ai_full_ma"], c["ai_bits"])
    lo, hi = c["tx_range_kv"]
    step_kv = step_ma * (hi - lo) / 16.0
    rel = step_kv / c["u_nom_kv"] * 100
    ratio = 0.66 / rel                       # expanded uncertainty of the next lesson, %
    lines = ["what one converter count is worth (16 bits over 0-21 mA)",
             f"  one count: {step_ma * 1000:.2f} uA = {step_kv * 1000:.1f} V on the"
             f" 132 kV system ({rel:.4f} %)",
             "  the counts are fine-grained; the chain's accuracy (next",
             f"  lesson, +/-0.66 %) is about {ratio:.0f} times coarser - more",
             "  bits do not buy accuracy, only resolution"]
    emit("a_resolution", lines)


def uncertainty() -> None:
    c = src.CHAIN
    lo, hi = c["tx_range_kv"]
    u_vt = c["vt_class_pct"] / math.sqrt(3)                               # % of reading
    u_tx = c["tx_acc_pct_span"] / 100 * (hi - lo) / math.sqrt(3) / c["u_nom_kv"] * 100
    u_ai_kv = c["ai_acc_pct_fs"] / 100 * c["ai_full_ma"] * (hi - lo) / 16.0
    u_ai = u_ai_kv / math.sqrt(3) / c["u_nom_kv"] * 100
    u = ic.combine(u_vt, u_tx, u_ai)
    u02 = ic.combine(0.2 / math.sqrt(3), u_tx, u_ai)
    csv("ch34-uncert.csv", "k,pct", [(1, round(u_vt, 3)), (2, round(u_tx, 3)),
                                     (3, round(u_ai, 3)), (4, round(u, 3))])
    lines = ["uncertainty of the POC voltage seen by the controller (at 132 kV)",
             "  source (limit taken as rectangular)   standard u, % of reading",
             f"  VT class {c['vt_class_pct']}                           {u_vt:10.3f}",
             f"  transducer {c['tx_acc_pct_span']} % of 150 kV span          {u_tx:10.3f}",
             f"  input module {c['ai_acc_pct_fs']} % of 21 mA              {u_ai:10.3f}",
             f"  combined                               {u:10.3f}",
             f"  expanded (k = 2): +/-{2 * u:.2f} % = +/-{2 * u / 100 * c['u_nom_kv']:.2f} kV",
             f"  with a class 0.2 VT: +/-{2 * u02:.2f} %",
             "  the VT dominates; a voltage set-point step of 0.01 pu is",
             "  only about one and a half times the expanded uncertainty,",
             "  so the controller's accuracy claim rests on the VT class",
             "  and its calibration record (ch 2, GUM; ch 26, VTs)"]
    emit("a_uncert", lines)


def rtd() -> None:
    r = src.RTD
    rl = 0.0175 * r["lead_m"] / r["area_mm2"]
    r_true = ic.pt100_r(r["t_winding"])
    e2 = ic.lead_error_2wire(rl)
    t2 = ic.pt100_t(r_true + 2 * rl)
    e3 = ic.lead_error_2wire(rl * 0.02)                      # 2 % lead mismatch
    lines = ["transformer winding temperature on a Pt100 (teaching)",
             f"  at {r['t_winding']:.0f} deg C the sensor reads {r_true:.2f} ohm",
             f"  each lead: {r['lead_m']:.0f} m of {r['area_mm2']} mm2 copper ="
             f" {rl:.2f} ohm",
             f"  two-wire: reads {t2:.1f} deg C (+{t2 - r['t_winding']:.1f} K;"
             f" small-signal estimate +{e2:.1f} K)",
             f"  three-wire, leads matched to 2 %: about +{e3:.2f} K",
             "  four-wire: no lead error",
             f"  a {t2 - r['t_winding']:.0f} K error in a winding-temperature alarm",
             "  or a cooling-fan start is a design error, not noise:",
             "  long runs are three- or four-wire, or the transmitter",
             "  sits at the transformer"]
    emit("a_rtd", lines)


def thermocouple() -> None:
    s = 41e-6                                   # V/K, type K near room temperature
    t_hot, t_panel = 320.0, 40.0
    emf = s * (t_hot - t_panel)
    lines = ["a thermocouple and its cold junction (linear teaching model)",
             f"  hot end {t_hot:.0f} deg C, terminals in a panel at {t_panel:.0f} deg C",
             f"  the junction pair makes {emf * 1000:.2f} mV for the difference only",
             f"  without cold-junction compensation the reading is {t_hot - t_panel:.0f} deg C",
             "  with it (panel temperature measured and added): 320 deg C",
             "  a thermocouple measures a difference; its extension wire",
             "  must be of the same alloys up to the compensated",
             "  terminals, or a new junction is made at every splice"]
    emit("a_tc", lines)


def rms_window() -> None:
    fs = 1600.0
    t = np.arange(0, 0.5, 1 / fs)
    v = math.sqrt(2) * np.sin(2 * math.pi * 50.0 * t)
    full = sg.rms(v[: int(0.2 * fs)])                       # ten whole cycles
    part = [sg.rms(v[k: k + int(0.0125 * fs)]) for k in range(0, 160, 8)]
    alias = sg.alias_frequency(50.0, 49.0)
    lines = ["RMS over whole cycles and the danger of the wrong window",
             f"  ten cycles (200 ms): RMS {full:.4f} (true 1.0000)",
             f"  windows of 12.5 ms (5/8 of a cycle): {min(part):.3f} to"
             f" {max(part):.3f}",
             f"  a 50 Hz signal sampled at 49 Hz looks like {alias:.0f} Hz",
             "  a window of whole cycles (or one that tracks frequency)",
             "  gives a steady value; a fractional window ripples with",
             "  where it starts; sampling below twice the highest",
             "  frequency folds it down - an anti-alias filter comes",
             "  before the converter (ch 3)"]
    emit("a_rms", lines)


def time_sync() -> None:
    k = src.CLOCK
    day = ic.clock_drift_s(k["drift_ppm"], 86400.0)
    lines = ["clocks and the order of events (teaching)",
             f"  GPS-disciplined time: about {k['gps_us']:.0f} us",
             f"  an IED clock that lost its sync drifts {k['drift_ppm']:.0f} ppm:"
             f" {day:.2f} s a day",
             "  two events 10 ms apart, recorded by two IEDs - one in",
             f"  sync, one a day out of sync: their order can be off by {day:.1f} s",
             "  the sequence-of-events record is evidence only while",
             "  every clock is synchronised and says so: each time stamp",
             "  carries a 'clock synchronised' flag, and a lost sync is",
             "  an alarm, not a footnote (ch 26, lesson E; ch 35)"]
    emit("a_time", lines)


def calibration() -> None:
    rows = [("POC voltage transducer", 0.2, 0.05, 0.05),
            ("pyranometer (ch 12)", 2.0, 0.5, 0.3),
            ("anemometer (ch 13)", 1.0, 0.2, 0.2),
            ("Pt100 transmitter", 0.5, 0.1, 0.1)]
    lines = ["calibration interval from drift (teaching, % of reading or span)",
             "  instrument                 tolerance  drift/yr  as-left   interval yr"]
    for name, tol, drift, left in rows:
        yrs = ic.calibration_interval(tol, drift, left)
        lines.append(f"  {name:26s} {tol:9.2f}  {drift:8.2f}  {left:7.2f}"
                     f"   {yrs:11.1f}")
    lines += ["  the interval is the time the drift takes to eat the",
              "  margin left after calibration; the records of as-found",
              "  values show the real drift and set the next interval -",
              "  the makers' and the lab's procedures govern (ch 48)"]
    emit("a_cal", lines)


def filtering(seed: int = 34) -> None:
    rng = np.random.default_rng(seed)
    dt = 0.02
    n = int(20 / dt)
    t = np.arange(n) * dt
    x = np.where(t >= 2.0, 1.0, 0.0) + rng.normal(0, 0.05, n)
    rows = []
    lines = ["a first-order filter: less noise, more delay (step at 2 s, noise sd 0.05)",
             "  tau s   noise sd after   time to 63 % s"]
    for k, tau in enumerate((0.0, 0.2, 0.5, 2.0), 1):
        y = x if tau == 0 else ic.first_order_filter(x, dt, tau)
        sd = float(np.std(y[t > 15]))
        t63 = float(t[np.argmax(y > 0.63)] - 2.0)
        rows.append((k, tau, round(sd, 4), round(t63, 2)))
        lines.append(f"  {tau:5.1f}   {sd:14.4f}   {t63:14.2f}")
    csv("ch34-filter.csv", "k,tau,sd,t63", rows)
    lines += ["  each filter in the chain adds its delay to the loop: the",
              "  0.5 s of the chain is the delay chapter 20 found tolerable",
              "  for the tuned plant controller; a 2 s filter would push",
              "  the loop toward the oscillation chapter 20 showed"]
    emit("a_filter", lines)


if __name__ == "__main__":
    scaling()
    loop_length()
    resolution()
    uncertainty()
    rtd()
    thermocouple()
    rms_window()
    time_sync()
    calibration()
    filtering()
