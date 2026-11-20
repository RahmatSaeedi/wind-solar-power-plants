"""Chapter 26 - expansion round 4: over-voltage and frequency stages
against the high-voltage and frequency ride-through bands, the relay's
thermal replica of a cable, a high-impedance bus differential, and the
relay curve against the cable's damage curve.

Run from the project root:   python -m companion.ch26.examples_r
Writes companion/ch26/expected/r_*.txt and diagrams/data/ch26-damage.csv.
Teaching values A-331 to A-335 (bands and settings illustrative; the
operator's code sets the real ones).
"""
from __future__ import annotations

import math

from companion.ch26 import sources as src
from companion.ch26.common import csv, emit
from plantp import protection as pr

HV_BAND = [(0.2, 1.30), (1.0, 1.20), (60.0, 1.15)]     # must stay connected below (A-335)
F_BAND = (47.5, 51.5)                                   # Hz, continuous band (A-335)


def hv_band(t: float) -> float:
    """Highest voltage (pu) the plant must ride through for t seconds."""
    for t_end, v in HV_BAND:
        if t <= t_end:
            return v
    return 1.10


def voltage_frequency() -> None:
    stages = [("59-1", 1.10, 30.0), ("59-1", 1.17, 60.0), ("59-2", 1.25, 0.5), ("59-2", 1.35, 0.10),
              ("81O", 51.0, 2.0), ("81O", 52.0, 0.5), ("81U", 48.0, 2.0), ("81U", 47.0, 0.5)]
    lines = ["over-voltage and frequency stages against the ride-through bands",
             "  (teaching: stay connected below 1.30 pu for 0.2 s, 1.20 pu for 1 s,",
             "  1.15 pu for 60 s; frequency 47.5-51.5 Hz continuous)",
             "  stage   pickup     delay s   band there   result"]
    for name, pick, delay in stages:
        if name.startswith("59"):
            band = hv_band(delay)
            ok = pick > band
            lines.append(f"  {name:6s} {pick:6.2f} pu   {delay:7.2f}   {band:7.2f} pu   "
                         + ("ok" if ok else "TRIPS INSIDE"))
        else:
            lo, hi = F_BAND
            ok = pick > hi if name == "81O" else pick < lo
            band = hi if name == "81O" else lo
            lines.append(f"  {name:6s} {pick:6.1f} Hz   {delay:7.2f}   {band:7.1f} Hz   "
                         + ("ok" if ok else "TRIPS INSIDE"))
    lines += ["  a stage that operates where the plant must stay connected",
              "  breaks the requirement as surely as an under-voltage stage",
              "  inside the low-voltage envelope (lesson B); after a load",
              "  rejection the voltage rises - the 59-2 stage protects the",
              "  equipment, the band protects the grid: both are met only",
              "  with the operator's numbers"]
    emit("r_vf", lines)


# [start: thermal]
def thermal_trip(i: float, i_base: float, tau_min: float, k: float = 1.05,
                 i_pre: float = 0.0) -> float:
    """Trip time (min) of a thermal replica from a preload current i_pre:
    t = tau ln((I^2 - Ip^2) / (I^2 - (k Ib)^2)); inf if it never trips."""
    a, b = i * i, (k * i_base) ** 2
    if a <= b:
        return math.inf
    return tau_min * math.log((a - i_pre ** 2) / (a - b))
# [end: thermal]


def thermal() -> None:
    ib, tau = 400.0, 45.0
    lines = ["thermal replica of a 33 kV feeder cable (rating 400 A, tau 45 min):",
             "  current A   from cold min   from full load min"]
    for i in (440, 480, 600, 800):
        c = thermal_trip(i, ib, tau)
        h = thermal_trip(i, ib, tau, i_pre=ib)
        lines.append(f"  {i:9d}   {c:13.1f}   {h:18.1f}")
    lines += ["  a cable warmed by full load reaches its limit much sooner",
              "  than a cold one: the replica remembers the heat, which an",
              "  overcurrent element cannot; tau and the rating come from",
              "  the cable's installed conditions (ch 24), and the replica",
              "  alarms before it trips so the controller can curtail"]
    emit("r_thermal", lines)


def high_impedance() -> None:
    i_f, ratio, r_ct, r_l = 25e3, 2000.0, 5.0, 2.0
    v_s = i_f / ratio * (r_ct + 2 * r_l)
    lines = ["high-impedance bus differential: stability for an external fault",
             f"  through fault {i_f / 1e3:.0f} kA, CTs {ratio:.0f}/1, R_ct {r_ct} ohm, lead {r_l} ohm",
             "  worst case: one CT saturates fully and the healthy ones",
             "  drive the secondary fault current through it and its leads:",
             f"  stability voltage V_s = I_f/N x (R_ct + 2 R_L) = {v_s:.1f} V",
             f"  relay set above it (teaching 1.2 x): {1.2 * v_s:.0f} V; CT knee >= 2 x setting:"
             f" {2.4 * v_s:.0f} V",
             "  for an internal fault every CT drives into the high",
             "  impedance and the voltage soars past the setting (a",
             "  voltage limiter protects the circuit); the CTs must be",
             "  identical and dedicated - a design proved by its stability",
             "  test and its sensitivity calculation"]
    emit("r_highz", lines)


def damage() -> None:
    k, s = 94.0, 240.0
    f = src.RELAYS["feeder"]
    rows = []
    lines = ["the relay protects the cable: feeder curve against the cable's",
             "  damage curve t = (k S / I)^2 (240 mm2 Al, k 94)",
             "  fault kA   cable withstands s   feeder relay s   margin x"]
    for i_ka in (2.0, 4.68, 7.75, 12.5):
        i = i_ka * 1e3
        t_c = (k * s / i) ** 2
        t_r = pr.trip_time(i, f["pickup"], f["tms"]) + 0.06
        lines.append(f"  {i_ka:8.2f}   {t_c:18.1f}   {t_r:14.2f}   {t_c / t_r:8.0f}")
    for i in range(1000, 13001, 500):
        rows.append((i / 1e3, f"{(k * s / i) ** 2:.3f}",
                     f"{pr.trip_time(i, f['pickup'], f['tms']) + 0.06:.3f}"))
    csv("ch26-damage.csv", "ka,cable,relay", rows)
    lines += ["  the relay (plus the breaker) clears every fault long before",
              "  the cable's conductor reaches its short-circuit limit; the",
              "  check is repeated with the backup (incomer) time, which",
              "  must also stay under the curve - and for the screen with",
              "  the earth-fault current and the standby time"]
    emit("r_damage", lines)


if __name__ == "__main__":
    voltage_frequency()
    thermal()
    high_impedance()
    damage()
