"""Chapter 6 lab: solve the RC discharge numerically and compare with the
exact answer. Shows how the error of a simple method shrinks with the step.

Run from the project root:   python -m companion.ch06.lab_euler
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import dc  # noqa: E402

# [start: euler]
V0, R, C = 9.0, 10e3, 1000e-6        # volts, ohms, farads -> tau = 10 s
T_END = 30.0                         # seconds


def euler(dt):
    """Step C dv/dt = -v/R forward: v_next = v - dt * v / (R C)."""
    v, t = V0, 0.0
    while t < T_END - 1e-12:
        v = v - dt * v / (R * C)
        t = t + dt
    return v


exact = V0 * math.exp(-T_END / (R * C))
previous = None
for dt in (5.0, 2.0, 1.0, 0.5, 0.25, 0.1):
    v = euler(dt)
    error = v - exact
    ratio = "" if previous is None else f"  error ratio {previous / error:4.2f}"
    print(f"dt = {dt:5.2f} s  v(30 s) = {v:.5f} V  error {error:+.5f} V{ratio}")
    previous = error
print(f"exact          v(30 s) = {exact:.5f} V")
# [end: euler]

# the library function gives the same numbers
_, v_lib = dc.rc_discharge_euler(V0, R, C, T_END, 1.0)
assert abs(v_lib[-1] - euler(1.0)) < 1e-12
