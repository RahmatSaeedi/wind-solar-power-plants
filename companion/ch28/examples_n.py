"""Chapter 28 - expansion round 4: the study predicts the compliance
tests - expected values and tolerances for the P-Q capability test
points, a voltage set-point step, and a frequency injection - so that
a test is judged against a prediction written beforehand.

Run from the project root:   python -m companion.ch28.examples_n
Writes companion/ch28/expected/n_*.txt and diagrams/data/ch28-step.csv.
Teaching values and placeholder requirements (U-102).
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import csv, emit
from companion.ch28.examples_c import v_loop


def pq_points() -> None:
    points = [(0.20, "give"), (0.20, "absorb"), (0.55, "give"), (0.55, "absorb"),
              (0.91, "give"), (0.91, "absorb")]
    lines = ["P-Q capability test points: the study's expected values (grid max, 1.00)",
             "  point   P POC MW   Q expected Mvar   requirement   pass if measured"]
    for k, (x, mode) in enumerate(points, 1):
        r = src.q_limits({"wind": x, "pv": x}, 1 if mode == "give" else -1)
        q = r["s_poc"].imag
        req = 33.0 if mode == "give" else -33.0
        tol = 2.0 + 0.02 * abs(q)
        need = f">= {req:+.0f}" if mode == "give" else f"<= {req:+.0f}"
        lines.append(f"  {k:5d}   {r['s_poc'].real:8.1f}   {q:15.1f}   {need:>11s}   "
                     f"{q - tol:+6.1f} .. {q + tol:+6.1f}")
    lines += ["  each point is held for a stated time (minutes) with the",
              "  POC voltage and the units' temperatures recorded; a",
              "  measured value outside the band is investigated before",
              "  the model or the test is blamed - and the requirement",
              "  column is judged on its own, against the operator's value"]
    emit("n_pq", lines)


def step_test() -> None:
    t, v = v_loop(1500.0, 1500.0, t_end=6.0)
    # the same loop driven by a +2 % set-point step instead of a grid step
    q_needed = 0.02 * 1500.0
    rows = [(f"{a:.2f}", f"{-100 * b:.3f}") for a, b in zip(t[::4], v[::4])]
    csv("ch28-step.csv", "t,v", rows)
    rec = v[t >= 1.0]
    t90 = t[t >= 1.0][np.argmax(rec >= -0.002)] - 1.0
    lines = ["voltage set-point step test: what the study expects (SCR 15, tuned loop)",
             f"  a 2 % step needs about {q_needed:.0f} Mvar (2 % x 1,500 MVA), inside the",
             "  plant's +46 Mvar",
             f"  expected: 90 % of the step reached in about {t90:.1f} s, no overshoot",
             "  test acceptance written beforehand (teaching): 90 % within",
             "  2 s, overshoot below 10 %, settled within 5 s; on the",
             "  weak grid the same test is predicted with the retuned gain",
             "  (lesson C) - a test on a strong-grid day does not prove the",
             "  weak-grid behaviour, the validated model does"]
    emit("n_step", lines)


def freq_test() -> None:
    rated, droop, db = 100.0, 0.05, 0.2
    lines = ["frequency injection test: expected change of active power",
             "  (5 % droop on 100 MW, 0.2 Hz deadband; plant at 80 MW)",
             "  injected Hz   deviation beyond deadband   expected dP MW   P after MW"]
    for f in (49.70, 49.90, 50.10, 50.30, 50.50):
        df = f - 50.0
        dev = df + db if df < -db else (df - db if df > db else 0.0)
        dp = -dev / (droop * 50) * rated + 0.0
        dp = 0.0 if abs(dp) < 1e-9 else dp
        p_after = min(max(80 + dp, 0.0), 80.0)        # no headroom upwards in S0
        lines.append(f"  {f:11.2f}   {dev:+25.2f}   {dp:+14.1f}   {p_after:10.1f}")
    lines += ["  above 50.2 Hz the plant reduces at 40 MW per Hz; below 49.8",
              "  it cannot rise from 80 MW without headroom (S0) - the test",
              "  shows the droop slope, the deadband and the response time,",
              "  and the under-frequency part is tested only if headroom is",
              "  contracted (REQ-G10)"]
    emit("n_freq", lines)


if __name__ == "__main__":
    pq_points()
    step_test()
    freq_test()
