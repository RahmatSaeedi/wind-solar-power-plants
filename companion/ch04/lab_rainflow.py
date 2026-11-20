"""Chapter 4 laboratory — counting fatigue cycles with the rainflow method.

Run from the project root:   python -m companion.ch04.lab_rainflow
A synthetic stress history at a tower-base weld (slow wind variation, rotor 3P loading
and turbulence; A-058) is reduced to turning points, counted by rainflow, and turned into
a Miner damage sum. A naive count of every peak-to-trough swing is shown for contrast.
Writes companion/ch04/expected/lab_rainflow.txt.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "expected" / "lab_rainflow.txt"


def turning_points(x):
    """Keep only the local peaks and troughs (and the end points)."""
    x = np.asarray(x, dtype=float)
    d = np.diff(x)
    keep = [0] + [i for i in range(1, len(x) - 1) if d[i - 1] * d[i] < 0] + [len(x) - 1]
    return x[keep]


# [start: rainflow]
def rainflow(points):
    """Three-point rainflow count: list of (range, count), count 0.5 or 1."""
    stack, cycles = [], []
    for p in points:
        stack.append(p)
        while len(stack) >= 3:
            x = abs(stack[-1] - stack[-2])          # newest range
            y = abs(stack[-2] - stack[-3])          # previous range
            if x < y:
                break
            if len(stack) == 3:                     # y holds the start point
                cycles.append((y, 0.5))
                stack.pop(0)
            else:                                   # y is a closed cycle
                cycles.append((y, 1.0))
                last = stack.pop()
                stack.pop()
                stack.pop()
                stack.append(last)
    for a, b in zip(stack[:-1], stack[1:]):         # what is left: half cycles
        cycles.append((abs(b - a), 0.5))
    return cycles
# [end: rainflow]


def damage(cycles, s_ref=71.0, n_ref=2e6, m=3.0):
    return sum(c / (n_ref * (s_ref / r) ** m) for r, c in cycles if r > 0)


def main() -> None:
    astm = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
    res = {}
    for r, c in rainflow(astm):
        res[r] = res.get(r, 0) + c
    rng = np.random.default_rng(20260201)
    t = np.arange(0, 600, 0.1)                                    # ten minutes at 10 Hz
    s = (40 + 15 * np.sin(2 * math.pi * t / 300) + 8 * np.sin(2 * math.pi * 0.525 * t)
         + np.convolve(rng.normal(0, 6, t.size), np.ones(5) / 5, mode="same"))
    tp = turning_points(s)
    cyc = rainflow(tp)
    d10 = damage(cyc)
    naive = [(abs(b - a), 0.5) for a, b in zip(tp[:-1], tp[1:])]   # each swing = half
    d_naive = damage(naive)
    ranges = np.array([r for r, _ in cyc])
    counts = np.array([c for _, c in cyc])
    lines = ["check on the standard textbook sequence -2 1 -3 5 -1 3 -4 4 -2:",
             "  " + ", ".join(f"range {k:g}: {v:g}" for k, v in sorted(res.items())),
             "ten minutes of synthetic tower-base stress (MPa, 10 Hz, A-058):",
             f"  {t.size} samples -> {tp.size} turning points -> {counts.sum():.0f} cycles",
             f"  largest range {ranges.max():.1f} MPa; cycles above 20 MPa: "
             f"{counts[ranges > 20].sum():.1f}",
             f"  Miner damage in 10 min: rainflow {d10:.3e}; swing by swing {d_naive:.3e}",
             f"  per 20 years if every 10 minutes were like this: {d10 * 6 * 24 * 365 * 20:.2f}",
             "  swing by swing misses the slow 300 s cycle hidden under the fast ones"]
    text = "\n".join(lines) + "\n"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
