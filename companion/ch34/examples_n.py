"""Chapter 34, lesson N (control, more): the deadband of a tap-changer
controller against hunting and wear, the storage a historian needs, and
the time-stamp resolution of the sequence-of-events record.

Run from the project root:   python -m companion.ch34.examples_n
Writes companion/ch34/expected/n_*.txt and diagrams/data/ch34-taps.csv.
Synthetic signals and teaching values (A-387).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch34.common import csv, emit

STEP = 1.25                     # % voltage per tap (teaching, ch 25)


def tap_ops(v, deadband: float, delay_n: int) -> int:
    """Tap operations of a simple controller: act when the bus voltage
    stays outside +-deadband for delay_n samples; each tap moves it STEP."""
    offset, count, outside = 0.0, 0, 0
    for x in v:
        e = x + offset
        if abs(e) > deadband:
            outside += 1
            if outside >= delay_n:
                offset -= math.copysign(STEP, e)
                count += 1
                outside = 0
        else:
            outside = 0
    return count


def taps(seed: int = 344) -> None:
    rng = np.random.default_rng(seed)
    n = 8640                                        # 10-s samples in a day
    t = np.arange(n) * 10 / 3600
    v = 1.5 * np.sin(2 * math.pi * (t - 9) / 24) + np.cumsum(rng.normal(0, 0.03, n))
    v -= v.mean()
    out = []
    lines = ["tap-changer operations in a day against the deadband (synthetic bus voltage)",
             f"  tap step {STEP} % (half a step = {STEP / 2} %); 30 s delay",
             "  deadband %   operations a day   a year   years to 300,000"]
    for k, d in enumerate((0.5, 0.6, 0.75, 1.0, 1.25), 1):
        ops = tap_ops(v, d, 3)
        yr = ops * 365
        life = 300_000 / yr if yr else float("inf")
        lines.append(f"  {d:10.2f}   {ops:16d}   {yr:6d}   {life:15.1f}")
        out.append((k, d, ops))
    csv("ch34-taps.csv", "k,deadband,ops", out)
    lines += ["  a deadband narrower than half a step makes the controller",
              "  hunt: each tap throws the voltage past the other edge and",
              "  the next tap comes back - wear for nothing; just above",
              "  half a step the hunting stops, and a wider band trades",
              "  voltage quality for fewer operations (ch 25, ch 27)"]
    emit("n_taps", lines)


def historian() -> None:
    groups = [("hard-wired points", 300, 1.0), ("fast network points", 2_000, 1.0),
              ("slow network points", 18_000, 10.0)]
    bytes_per = 12
    lines = ["historian storage a year (teaching; 12 bytes a stored sample)",
             "  group                    points   period s   GB a year raw"]
    total = 0.0
    for name, n, p in groups:
        gb = n * (365 * 86400 / p) * bytes_per / 1e9
        total += gb
        lines.append(f"  {name:22s} {n:8,d}   {p:8.0f}   {gb:13.0f}")
    lines += [f"  raw {total:,.0f} GB a year; with deadband compression keeping",
              f"  one sample in ten: {total / 10:,.0f} GB",
              "  the compression deadband is a measurement decision: a",
              "  value stored only when it moves more than its deadband",
              "  loses what happens inside it - the deadband of each tag",
              "  is set from its accuracy (lesson A), not from disk size"]
    emit("n_historian", lines)


def soe(seed: int = 345) -> None:
    rng = np.random.default_rng(seed)
    n = 100_000
    gap = rng.uniform(0, 10, n)                     # ms between two events, A first
    clock = rng.normal(0, 0.5, n)                   # ms sync error between the two IEDs
    lines = ["two events up to 10 ms apart: is their order on record right?",
             "  resolution ms   same stamp %   wrong order %"]
    for res in (1.0, 10.0):
        ta_true = rng.uniform(0, 1000, n)
        ta = np.floor(ta_true / res) * res
        tb_true = ta_true + gap + clock
        tb = np.floor(tb_true / res) * res
        same = float(np.mean(tb == ta)) * 100
        wrong = float(np.mean(tb < ta)) * 100
        lines.append(f"  {res:13.0f}   {same:12.1f}   {wrong:13.1f}")
    lines += ["  at 10 ms resolution about half of such pairs share a stamp",
              "  and their order is lost; at 1 ms most are told apart; the few",
              "  reversed come from the clocks' own sync error - the",
              "  resolution and the sync accuracy are specified together"]
    emit("n_soe", lines)


if __name__ == "__main__":
    taps()
    historian()
    soe()
