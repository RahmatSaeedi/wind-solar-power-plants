"""Chapter 34, lesson M (measurement, more): the phase error of the
instrument transformers and the accuracy of P and Q near unity power
factor, common-mode voltage on an isolated input, frequency and rate of
change of frequency from a noisy measurement, and a calibration interval
set from as-found records.

Run from the project root:   python -m companion.ch34.examples_m
Writes companion/ch34/expected/m_*.txt and diagrams/data/ch34-phase.csv,
ch34-rocof.csv. Teaching values (A-385, A-386).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch34.common import csv, emit


def phase_error() -> None:
    delta = math.radians(20 / 60)                 # 20 minutes of arc (teaching)
    rows, out = [], []
    lines = ["P and Q errors from a 20-minute phase error of the CT/VT pair (teaching)",
             "  power factor   phi deg   error in P %   error in Q %"]
    for pf in (0.80, 0.90, 0.95, 0.99, 0.999):
        phi = math.acos(pf)
        ep = (math.cos(phi - delta) / math.cos(phi) - 1) * 100
        eq = (math.sin(phi - delta) / math.sin(phi) - 1) * 100
        rows.append((pf, ep, eq))
        lines.append(f"  {pf:12.3f}   {math.degrees(phi):7.2f}   {ep:12.2f}   {eq:12.1f}")
    for k in range(1, 100):
        pf = 0.80 + 0.002 * k
        if pf >= 0.9995:
            break
        phi = math.acos(pf)
        out.append((round(pf, 3), round(abs((math.sin(phi - delta) / math.sin(phi) - 1) * 100), 2)))
    csv("ch34-phase.csv", "pf,eq", out)
    lines += ["  near unity power factor the active power barely notices",
              "  the phase error, but the reactive power, a small number,",
              f"  is off by {abs(rows[3][2]):.0f} % at 0.99 and {abs(rows[4][2]):.0f} % at 0.999 - Q at the POC is",
              "  measured with cores whose phase displacement is known,",
              "  and a Q requirement near zero is judged in Mvar, not %"]
    emit("m_phase", lines)


def common_mode() -> None:
    v_cm = 50.0                                     # V between field and panel earth (fault)
    span = 4.0                                      # V of a 1-5 V input
    lines = ["common-mode voltage on an analogue input (teaching)",
             f"  {v_cm:.0f} V between field and panel earth during an earth fault",
             "  rejection dB   error mV   error % of a 4 V span"]
    for cmrr in (60, 90, 120):
        err = v_cm / 10 ** (cmrr / 20)
        lines.append(f"  {cmrr:12d}   {err * 1000:8.2f}   {err / span * 100:10.3f}")
    lines += ["  an isolated input with 120 dB rejection keeps the fault",
              "  out of the reading; a non-isolated input wired at both",
              "  ends would carry the fault current itself - the earthing",
              "  rules of lesson A apply before any rejection figure"]
    emit("m_cm", lines)


def rocof(seed: int = 342) -> None:
    rng = np.random.default_rng(seed)
    dt = 0.02                                       # one value per cycle
    t = np.arange(0, 10, dt)
    f = 50.0 - 0.5 * np.clip(t - 2.0, 0, None)      # -0.5 Hz/s from t = 2 s
    meas = f + rng.normal(0, 0.005, t.size)         # 5 mHz noise per cycle
    out = []
    lines = ["rate of change of frequency from a noisy frequency (true -0.5 Hz/s)",
             "  window s   noise sd Hz/s   delay s   quiet samples over 0.1 Hz/s"]
    for k, w in enumerate((0.1, 0.2, 0.5, 1.0), 1):
        n = int(w / dt)
        slope = (meas[n:] - meas[:-n]) / w
        quiet = slope[t[n:] < 1.9]
        sd = float(np.std(quiet))
        over = float(np.mean(np.abs(quiet) > 0.1)) * 100
        lines.append(f"  {w:8.1f}   {sd:13.3f}   {w / 2:7.2f}   {over:24.1f} %")
        out.append((k, w, round(sd, 4)))
    csv("ch34-rocof.csv", "k,window,sd", out)
    lines += ["  with a sensitive 0.1 Hz/s trigger, the shortest window",
              "  trips on noise alone in a share of quiet cycles; a long",
              "  window is calm but late - the window and the trigger",
              "  level are chosen together, with a time delay, and",
              "  written in the setting file (ch 26, ch 28)"]
    emit("m_rocof", lines)


def as_found(seed: int = 343) -> None:
    rng = np.random.default_rng(seed)
    drift = rng.normal(0.06, 0.03, 40)              # % per year from 40 as-found records
    tol, left = 0.5, 0.1
    mu, sd = float(drift.mean()), float(drift.std(ddof=1))
    lines = ["calibration interval from as-found records (40 transmitters, synthetic)",
             f"  drift {mu:.3f} +/- {sd:.3f} % a year; tolerance {tol} %, as-left {left} %",
             "  interval yr   share still in tolerance at its end"]
    best = 0.0
    for yrs in (2, 3, 4, 5, 6):
        p_in = float(stats.norm.cdf((tol - left) / yrs, mu, sd))
        lines.append(f"  {yrs:11d}   {p_in * 100:8.1f} %")
        if p_in >= 0.95:
            best = yrs
    lines += [f"  for 95 % in tolerance at the end, the interval is {best} years",
              "  the mean drift alone would allow longer; the spread of",
              "  the fleet sets the interval - the records of as-found",
              "  values are what lengthen it, or shorten it, next time"]
    emit("m_asfound", lines)


if __name__ == "__main__":
    phase_error()
    common_mode()
    rocof()
    as_found()
