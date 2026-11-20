"""Chapter 20, section F - islanded and grid-forming behaviour (only where
permitted): power sharing between four grid-forming battery inverters by
droop, secondary control that brings the frequency back, load shedding
in priority order when the island runs short, the energy a black start
of the plant's own network would take, and the wait for a synchro-check
window before the island rejoins the grid.

Run from the project root:   python -m companion.ch20.examples_f
Writes companion/ch20/expected/f_*.txt.
Teaching values (A-303); the island serves critical loads only (D-022).
"""
from __future__ import annotations

import numpy as np

from companion.ch20.common import emit

F0 = 50.0


# [start: sharing]
def share(load_mw: float, f_set, m, p_rated):
    """Steady state of grid-forming units with droop P_i = (f_set_i - f)
    / m_i * p_rated_i (m in Hz per rated power): one frequency f makes
    the powers add up to the load. Returns f and the powers."""
    f_set, m, pr = (np.asarray(x, float) for x in (f_set, m, p_rated))
    k = pr / m                                    # MW per Hz
    f = (np.sum(k * f_set) - load_mw) / np.sum(k)
    return f, k * (f_set - f)
# [end: sharing]


def sharing() -> None:
    pr = [5.0] * 4
    lines = ["four grid-forming battery inverters share a 4 MW island load:",
             "  case                         f Hz    P1    P2    P3    P4 (MW)"]
    cases = [("equal settings", [50.0] * 4, [1.0] * 4),
             ("unit 1 set 0.1 Hz high", [50.1, 50, 50, 50], [1.0] * 4),
             ("unit 4 droop twice as steep", [50.0] * 4, [1, 1, 1, 2.0]),
             ("secondary control (+0.2 Hz)", [50.2] * 4, [1.0] * 4)]
    for name, fs, m in cases:
        f, p = share(4.0, fs, m, pr)
        lines.append(f"  {name:28s} {f:6.2f}" + "".join(f" {x:5.2f}" for x in p))
    lines += ["  (droop 1 Hz per rated power; teaching, A-303)",
              "  units share by their droop settings: a unit set high takes",
              "  more; a steeper droop takes less; the frequency falls with",
              "  the load until secondary control moves all set points",
              "  together and brings it back to 50 Hz"]
    emit("f_sharing", lines)


def shedding() -> None:
    loads = [("protection, control, comms", 1, 0.15), ("fire detection, HVAC BESS", 1, 0.9),
             ("lighting, security", 2, 0.12), ("water pumps", 2, 0.4),
             ("workshop, offices", 3, 0.6), ("village feeder (if agreed)", 3, 2.5)]
    lines = ["load shedding in priority order as the island runs short:",
             "  source MW   loads kept (priority <= )   load MW   shed MW"]
    total = sum(x[2] for x in loads)
    for src_mw in (5.0, 2.5, 1.2, 0.5):
        kept = 0.0
        level = 0
        for pr in (1, 2, 3):
            add = sum(x[2] for x in loads if x[1] == pr)
            if kept + add <= src_mw + 1e-9:
                kept += add
                level = pr
        lines.append(f"  {src_mw:9.1f}   {level:24d}   {kept:7.2f}   {total - kept:7.2f}")
    lines += ["  priority 1 loads are never shed by the controller; if the",
              "  source cannot carry them, the island is not formed and the",
              "  safety systems run on their own batteries (UPS); the list",
              "  and its priorities are an operator decision (chapter 51)"]
    emit("f_shedding", lines)


def black_start() -> None:
    """Energy to energize the plant's own network from the battery and
    hold it for some hours before the grid accepts it (only if a black
    start is contracted; teaching values)."""
    no_load = {"2 x 63 MVA main transformers": 2 * 0.045,
               "26 unit transformers (WTG, PV, BESS)": 22 * 0.006 + 4 * 0.005,
               "33 kV cables (charging, losses)": 0.03,
               "auxiliaries and HVAC": 1.2}
    tot = sum(no_load.values())
    lines = ["black start of the plant's own network (if contracted, A-303):",
             "  item                                 MW"]
    lines += [f"  {k:36s} {v:5.3f}" for k, v in no_load.items()]
    lines += [f"  total held                           {tot:5.3f}"]
    for hours in (1, 4, 12):
        lines.append(f"  energy for {hours:2d} h: {tot * hours:5.1f} MWh"
                     f" of the 32 MWh window")
    lines += ["  energy is not the hard part: inrush of the transformers and",
              "  the strength of four inverters in front of a 132 kV line are;",
              "  both need a study and the operator's procedure first"]
    emit("f_blackstart", lines)


def synchro() -> None:
    lines = ["rejoining the grid: wait for the synchro-check window",
             "  slip Hz   one slip cycle s   in a +-10 deg window s   wait (worst) s"]
    for slip in (0.05, 0.1, 0.2, 0.5):
        cycle = 1.0 / slip
        win = cycle * 20.0 / 360.0
        lines.append(f"  {slip:7.2f}   {cycle:16.1f}   {win:22.2f}   {cycle - win:14.1f}")
    lines += ["  a large slip passes the window quickly (the breaker may not",
              "  close in time); a small slip waits longer; the controller",
              "  moves the island frequency to a small slip first; the",
              "  synchro-check limits come from the protection settings",
              "  (chapter 27), not from this table"]
    emit("f_synchro", lines)


if __name__ == "__main__":
    sharing()
    shedding()
    black_start()
    synchro()
