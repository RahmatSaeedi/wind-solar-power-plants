"""Chapter 26 - expansion round 8: the loop a PV string's cables make and
the voltage a nearby strike induces in it, the breaker-failure timer
derived from the breaker timing records, and what the plant adds to the
grid's fault level at the point of connection.

Run from the project root:   python -m companion.ch26.examples_w
Writes companion/ch26/expected/w_*.txt. Teaching values A-331 to A-335.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr


def string_loop() -> None:
    length = 26 * 2.28                     # 26 modules of about 2.28 m (D-013)
    lines = ["the loop of a PV string and a strike 100 m away (20 kA/us, teaching)",
             f"  string length about {length:.0f} m; induced voltage U = mu0 A di/dt / (2 pi d)",
             "  routing of + and -                 loop m2   induced kV"]
    for name, gap in (("+ and - on opposite table edges", 2.0), ("separate, 0.5 m apart", 0.5),
                      ("together in one tray", 0.05)):
        area = length * gap
        u = pr.loop_voltage(area, 100.0, 2e10)
        lines.append(f"  {name:34s} {area:7.1f}   {u / 1e3:10.2f}")
    lines += ["  the induced voltage scales with the loop's area: running the",
              "  + and - conductors of a string side by side shrinks the",
              "  loop forty times and keeps the voltage below what the",
              "  module and inverter insulation and their SPDs handle; the",
              "  layout rule is cheap at design and costly to change later"]
    emit("w_loop", lines)


def bf_timer() -> None:
    reset, margin = 0.020, 0.060
    lines = ["breaker-failure timer from the breaker timing records (lesson K)",
             "  timer >= slowest opening + current-check reset + margin",
             f"  (reset {reset * 1e3:.0f} ms, margin {margin * 1e3:.0f} ms, teaching)",
             "  breaker            slowest pole ms   needed ms   150 ms ok?   115 ms ok?"]
    for name, slow in (("=WS1-Q1", 31), ("=WS2-Q1 (as found)", 42), ("=WS2-Q1 (repaired)", 30)):
        need = slow / 1e3 + reset + margin
        lines.append(f"  {name:18s} {slow:15d}   {need * 1e3:9.0f}   {'yes' if need <= 0.150 else 'NO':>10s}"
                     f"   {'yes' if need <= 0.115 else 'NO':>10s}")
    lines += ["  the timer must outlast the slowest healthy opening, or the",
              "  breaker-failure stage trips the whole section while the",
              "  breaker is in fact opening: with a tighter 115 ms timer (for",
              "  faster backup) the slow pole as found would do exactly that;",
              "  the timing record is an input to the setting, and a breaker",
              "  that fails its timing is repaired, not 'covered' by a longer",
              "  timer that slows every backup clearing"]
    emit("w_bftimer", lines)


def contribution() -> None:
    ik_grid = src.NETWORK["ik_132"]
    s_plant = 100.0 / 0.95
    lines = ["what the plant adds to the grid's fault level at the 132 kV bus",
             f"  grid alone {ik_grid / 1e3:.1f} kA; plant {s_plant:.0f} MVA of converters",
             "  converter fault current x rated   plant kA at 132 kV   total kA   rise"]
    for k in (1.0, 1.2, 1.5):
        i_p = k * s_plant * 1e6 / (math.sqrt(3) * 132e3)
        tot = ik_grid + i_p
        lines.append(f"  {k:31.1f}   {i_p / 1e3:18.2f}   {tot / 1e3:8.2f}   {i_p / ik_grid:4.0%}")
    lines += ["  a converter plant adds about a tenth to the grid's fault",
              "  level here - a synchronous plant of the same size would add",
              "  several times more; the operator's study (ch 28) needs the",
              "  makers' fault-current models (positive and negative",
              "  sequence, timing) to check its own breakers and relays,",
              "  and the plant's 132 kV gear is rated on the total"]
    emit("w_contribution", lines)


if __name__ == "__main__":
    string_loop()
    bf_timer()
    contribution()
