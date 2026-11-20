"""Chapter 26 - expansion round 1: the differential's spill current from
the tap changer and CT mismatch (why the bias slope), restricted earth
fault against differential for a resistance-earthed star winding, a
healthy feeder fed by its own converters (sympathetic tripping),
auto-reclosing the export line against an islanded plant, and the
synchrocheck window for closing the line breaker.

Run from the project root:   python -m companion.ch26.examples_m
Writes companion/ch26/expected/m_*.txt and diagrams/data/ch26-ref.csv.
Teaching values A-331 to A-335; real settings come from the approved
network model, the makers and the operator.
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import csv, emit
from plantp import protection as pr


# [start: spill]
def spill(through_pu: float, tap: float, ct_mismatch: float) -> float:
    """Differential (spill) current, per unit of rated, when a through
    current flows and the CT ratios match only at the principal tap:
    the tap error and a fixed CT mismatch both leave a residue."""
    return through_pu * (abs(tap) + ct_mismatch)
# [end: spill]


def diff_slope() -> None:
    pickup, slope = 0.2, 0.3
    lines = ["main transformer differential: spill current for a through fault",
             "  (tap changer at -10 %, CT mismatch 3 %; pickup 0.2 pu, slope 30 %)",
             "  through pu   spill pu   restraint threshold pu   trips?"]
    for i in (1.0, 2.0, 4.0, 8.3):
        s = spill(i, -0.10, 0.03)
        thr = pickup + slope * i
        lines.append(f"  {i:10.1f}   {s:8.2f}   {thr:22.2f}   {'YES' if s > thr else 'no'}")
    flat = [i for i in (1.0, 2.0, 4.0, 8.3) if spill(i, -0.10, 0.03) > pickup]
    lines += [f"  with a flat 0.2 pu threshold (no bias) it would trip from "
              f"{flat[0]:.0f} pu: the spill",
              "  grows with the through current, so the threshold must grow",
              "  too - that is the bias slope; CT saturation in a heavy",
              "  external fault adds more spill (a second, steeper slope),",
              "  and the inrush is blocked by its second harmonic (ch 25)"]
    emit("m_slope", lines)


def ref() -> None:
    i_max, i_rated = 400.0, 1102.0          # resistor limit; 63 MVA at 33 kV
    rows = []
    lines = ["restricted earth fault (REF) against differential, resistance-earthed",
             "  star winding: fault at a fraction x of the winding from the neutral",
             "  x     fault A   seen on the line side, % of rated   REF 5 %   diff 20 %"]
    for k in range(1, 11):
        x = k / 10
        i_f = x * i_max
        line_pct = 100 * x * i_f / i_rated
        rows.append((f"{x:.1f}", f"{100 * i_f / i_rated:.2f}", f"{line_pct:.2f}"))
        lines.append(f"  {x:3.1f}   {i_f:7.0f}   {line_pct:33.2f}   "
                     f"{'sees' if 100 * i_f / i_rated >= 5 else '-':>7s}   "
                     f"{'sees' if line_pct >= 20 else '-':>8s}")
    csv("ch26-ref.csv", "x,ref,diff", rows)
    lines += ["  the resistor limits the fault current to x times 400 A; the",
              "  line side sees it reduced again by the turns ratio x: the",
              "  differential sees only x squared and misses most winding",
              "  faults; REF measures the neutral current itself (x, not",
              "  x squared) and covers far more of the winding"]
    emit("m_ref", lines)


def sympathetic() -> None:
    f = src.RELAYS["feeder"]
    i_rated = 4 * 5.26e6 / (math.sqrt(3) * 33e3)
    lines = ["a healthy feeder fed by its own turbines during a fault elsewhere",
             f"  four turbines, rated current {i_rated:.0f} A at 33 kV; feeder pickup"
             f" {f['pickup']:.0f} A, TMS {f['tms']}",
             "  converter fault current   amps   healthy feeder relay"]
    for k in (1.1, 1.3, 1.5):
        i = k * i_rated
        t = pr.trip_time(i, f["pickup"], f["tms"])
        lines.append(f"  {k:24.1f} x   {i:4.0f}   "
                     + ("never (below pickup)" if math.isinf(t) else f"would trip after {t:.1f} s"))
    lines += ["  the faulted feeder clears in about 0.3 s; the healthy one",
              "  would need seconds - no sympathetic trip, because the",
              "  inverse curve is slow just above pickup; a converter that",
              "  feeds 1.5 x for long, or a feeder with more units, makes",
              "  the margin thin - then a directional element (forward",
              "  only) is the cure, if the converters give it enough",
              "  negative-sequence current to decide (makers' data)"]
    emit("m_sympathetic", lines)


def reclose() -> None:
    lines = ["auto-reclosing the export line while the plant is islanded",
             "  phase drift between plant and grid during the dead time:",
             "  angle = 360 x df x t (degrees)",
             "  frequency difference Hz   dead time 0.5 s   1.0 s   3.0 s"]
    for df in (0.1, 0.5, 1.0):
        lines.append(f"  {df:24.1f}   {360 * df * 0.5:15.0f}   {360 * df:5.0f}   {360 * df * 3:5.0f}")
    t_detect = 0.2 + 0.06
    lines += [f"  the plant must have stopped before the reclose: detection",
              f"  {t_detect * 1e3:.0f} ms (island detection 200 ms + breaker 60 ms)",
              "  inside a 0.5 s dead time leaves little margin - closing",
              "  onto a live island 180 degrees out of phase doubles the",
              "  voltage across the breaker and stresses every machine and",
              "  transformer; so either transfer trip stops the plant at",
              "  once, or the operator lengthens the dead time or recloses",
              "  only onto a dead line - an item for the connection",
              "  agreement (ch 28)"]
    emit("m_reclose", lines)


def synchrocheck() -> None:
    window, t_close = 20.0, 0.08
    lines = ["synchrocheck for closing the line breaker (teaching window +/-20 deg)",
             "  slip Hz   time inside the window s   advance angle for 80 ms deg"]
    for slip in (0.05, 0.1, 0.2, 0.5):
        inside = 2 * window / (360 * slip)
        lines.append(f"  {slip:7.2f}   {inside:24.2f}   {360 * slip * t_close:27.1f}")
    lines += ["  slow slip leaves a long window; fast slip a short one, and",
              "  the breaker's own closing time turns into an angle: the",
              "  relay issues the close early by that angle so the contacts",
              "  touch at zero; the windows for voltage, frequency and angle",
              "  are the operator's, and the synchrocheck is proved in the",
              "  end-to-end tests"]
    emit("m_synch", lines)


if __name__ == "__main__":
    diff_slope()
    ref()
    sympathetic()
    reclose()
    synchrocheck()
