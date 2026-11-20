"""Chapter 34, lesson E (deeper): the hold-up time of a 24 V power supply
and which control loads ride through a grid voltage dip.

Run from the project root:   python -m companion.ch34.examples_t
Writes companion/ch34/expected/t_*.txt and diagrams/data/ch34-holdup.csv.
Teaching values (A-389, extended); makers' data and tests decide.
"""
from __future__ import annotations

import math

from companion.ch34.common import csv, emit


def holdup_ms(c_uf: float, v1: float, v2: float, p_out_w: float,
              eff: float = 0.9) -> float:
    """Time the bulk capacitor feeds the supply after its input is lost."""
    energy = 0.5 * c_uf * 1e-6 * (v1 ** 2 - v2 ** 2)
    return energy / (p_out_w / eff) * 1000


def holdup() -> None:
    c, v1, v2, rated = 940.0, 325.0, 200.0, 480.0   # 2 x 470 uF; stops at 200 V
    lines = ["hold-up of a 480 W, 24 V supply fed from 230 V AC (teaching)",
             "  bulk capacitor 940 uF charged to 325 V; stops below 200 V",
             "  load %   load W   hold-up ms"]
    for share in (1.0, 0.5, 0.25):
        lines.append(f"  {share * 100:6.0f}   {rated * share:6.0f}"
                     f"   {holdup_ms(c, v1, v2, rated * share):10.0f}")
    rows = []
    for t_ms in range(0, 121):
        p_in = rated / 0.9
        v_sq = v1 ** 2 - 2 * p_in * t_ms / 1000 / (c * 1e-6)
        if v_sq > v2 ** 2:                    # the curve stops where the supply does
            rows.append((t_ms, round(math.sqrt(v_sq), 1)))
    csv("ch34-holdup.csv", "t,v", rows)
    lines += ["  a supply's own capacitor bridges a few tens of",
              "  milliseconds at full load - enough for a switching",
              "  transient, not for a grid fault cleared in 150 ms",
              "  (ch 28); loading a supply to half its rating doubles",
              "  the bridge, but control that must ride through a fault",
              "  is fed from the battery or the UPS (lesson E)"]
    emit("t_holdup", lines)


LOADS = [  # load, supply, bridge ms (teaching), after a drop-out
    ("plant controller and I/O", "24 V from 110 V DC", None, ""),
    ("protection relays", "110 V DC", None, ""),
    ("network switches", "24 V from 110 V DC", None, ""),
    ("operator HMI", "UPS", None, ""),
    ("cabinet fan", "230 V AC direct", 20.0, "restarts"),
    ("battery HVAC compressor", "400 V AC direct", 10.0, "restarts, 3 min"),
    ("cooling pump (self-holding)", "230 V AC coil", 15.0, "STAYS OFF"),
    ("POC transducer", "24 V from 230 V AC", 58.0, "READING LOST")]


def ride_through() -> None:
    dip_ms = 150.0
    lines = [f"a dip to 0.2 pu for {dip_ms:.0f} ms at the POC (ch 28 profile,"
             " teaching)",
             "  load                        fed from             bridge ms  result"]
    bad = 0
    for name, supply, bridge, after in LOADS:
        ok = bridge is None or bridge >= dip_ms
        res = "rides through" if ok else after
        bad += res.isupper()
        b = "battery" if bridge is None else f"{bridge:.0f}"
        lines.append(f"  {name:27s} {supply:20s} {b:>9s}  {res}")
    lines += [f"  {bad} loads fail the plant: a pump that stays off until",
              "  someone restarts it, and a controller that loses its",
              "  POC reading in the very fault it must answer; both move",
              "  to the DC supply or get a delayed drop-out. Loads that",
              "  restart by themselves may stay on AC if their restart",
              "  time fits the thermal budget (3 min of compressor delay",
              "  against the battery's margin, ch 19)"]
    emit("t_ride", lines)


if __name__ == "__main__":
    holdup()
    ride_through()
