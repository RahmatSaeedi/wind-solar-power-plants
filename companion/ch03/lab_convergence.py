"""Chapter 3 laboratory — measure the order of accuracy of a numerical method.

Run from the project root:   python -m companion.ch03.lab_convergence
A method of order p has an error that shrinks like h^p when the step h shrinks.
Halving h therefore divides the error by 2^p, and the observed order is
p = log(e_coarse / e_fine) / log(2). The lab checks this for Euler and RK4 on
the cable-heating equation of section B, whose exact solution is known.
Writes companion/ch03/expected/lab_convergence.txt and diagrams/data/ch03-order.csv.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import numerics as nm  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "expected" / "lab_convergence.txt"
DATA = HERE.parents[1] / "diagrams" / "data" / "ch03-order.csv"

TAU, RISE, T_END = 1800.0, 40.0, 3600.0      # s, K, s (assumed cable)


def rhs(t, y):
    return (RISE - y) / TAU


def exact(t):
    return RISE * (1.0 - math.exp(-t / TAU))


# [start: order]
def observed_order(errors: list[float], ratio: float = 2.0) -> list[float]:
    """Order estimates from errors at steps h, h/ratio, h/ratio^2, ..."""
    return [math.log(e1 / e2) / math.log(ratio)
            for e1, e2 in zip(errors, errors[1:])]


def study(method, steps):
    errors = []
    for dt in steps:
        _, y = method(rhs, 0.0, 0.0, T_END, dt)
        errors.append(abs(y[-1] - exact(T_END)))
    return errors
# [end: order]


def main() -> None:
    steps = [1200.0, 600.0, 300.0, 150.0, 75.0]
    e_eu = study(nm.euler, steps)
    e_rk = study(nm.rk4, steps)
    lines = [f"{'dt (s)':>8s} {'Euler error':>12s} {'RK4 error':>12s}"]
    for dt, a, b in zip(steps, e_eu, e_rk):
        lines.append(f"{dt:8.0f} {a:12.4e} {b:12.4e}")
    lines.append("observed order, Euler: " + ", ".join(f"{p:.2f}" for p in observed_order(e_eu)))
    lines.append("observed order, RK4:   " + ", ".join(f"{p:.2f}" for p in observed_order(e_rk)))
    lines.append("expected: 1 for Euler, 4 for RK4; the work per step of RK4 is 4 times")
    lines.append("    Euler's, but for 1e-6 K accuracy it needs far fewer steps")
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("dt,euler,rk4\n")
        for dt, a, b in zip(steps, e_eu, e_rk):
            fh.write(f"{dt:.0f},{a:.4e},{b:.4e}\n")
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
