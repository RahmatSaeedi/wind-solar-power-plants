"""Chapter 26 - expansion round 7: second-harmonic restraint computed
from inrush and fault waveforms, and the cable screens against the
choice of earthing and the coupler state.

Run from the project root:   python -m companion.ch26.examples_u
Writes companion/ch26/expected/u_*.txt and diagrams/data/ch26-inrush.csv.
Teaching values A-331 to A-335 (the restraint threshold is the relay
maker's setting).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch26.common import csv, emit

N = 256                                   # samples per cycle


# [start: inrush]
def inrush_cycle(alpha_deg: float) -> np.ndarray:
    """One cycle of a teaching inrush pulse: the core saturates for an
    angle alpha around the flux peak, so the current is a one-sided
    cap of a cosine (zero for the rest of the cycle)."""
    wt = np.linspace(-math.pi, math.pi, N, endpoint=False)
    c = math.cos(math.radians(alpha_deg) / 2)
    return np.where(np.abs(wt) < math.radians(alpha_deg) / 2,
                    (np.cos(wt) - c) / (1 - c), 0.0)


def second_ratio(cycle: np.ndarray) -> float:
    """Second-harmonic magnitude as a fraction of the fundamental."""
    spec = np.abs(np.fft.rfft(cycle))
    return spec[2] / spec[1]
# [end: inrush]


def fault_cycle(dc: float, tau_cycles: float = 1.5) -> np.ndarray:
    """One cycle of a fault current with a decaying DC offset."""
    k = np.arange(N)
    wt = 2 * math.pi * k / N
    return np.sin(wt - math.pi / 2) + dc * np.exp(-k / (N * tau_cycles))


def restraint() -> None:
    lines = ["second-harmonic restraint of the differential (teaching threshold 15 %)",
             "  waveform                                 2nd / fundamental   blocks?"]
    for a in (90, 120, 180, 240):
        r = second_ratio(inrush_cycle(a))
        lines.append(f"  inrush, saturated {a:3d} deg of the cycle     {r:15.0%}   {'yes' if r > 0.15 else 'NO'}")
    for dc in (0.0, 0.5, 1.0):
        r = second_ratio(fault_cycle(dc))
        lines.append(f"  internal fault, DC offset {dc:3.1f}             {r:15.0%}   {'yes' if r > 0.15 else 'no'}")
    one = inrush_cycle(120)
    csv("ch26-inrush.csv", "deg,inrush,fault",
        [(f"{360 * k / N - 180:.1f}", f"{one[k]:.4f}", f"{fault_cycle(0.0)[k]:.4f}")
         for k in range(0, N, 4)])
    lines += ["  an inrush pulse is one-sided and short: rich in the 2nd",
              "  harmonic, so the relay holds back; a fault current is a",
              "  sine (with a DC offset that decays) and carries little 2nd",
              "  harmonic, so the relay trips; a deeply saturated core",
              "  (long pulses) has less 2nd harmonic - modern steels push",
              "  inrush that way, which is why makers add other criteria"]
    emit("u_restraint", lines)


def screens() -> None:
    withstand_1s = 5.0e3                  # 35 mm2 Cu screen, ch 24
    lines = ["the cable screens against the earthing choice and the coupler",
             "  screen 35 mm2 Cu carries 5.0 kA for 1 s (ch 24): t = (5.0 kA / I)^2",
             "  earthing                          fault A   screen withstands s   backup s"]
    for name, i, backup in (("solid (no resistor)", 7170.0, 1.5), ("400 A resistor, coupler open", 400.0, 1.5),
                            ("two resistors, coupler closed", 800.0, 1.5)):
        t = (withstand_1s / i) ** 2
        lines.append(f"  {name:32s} {i:8.0f}   {t:19.1f}   {backup:8.1f}")
    lines += ["  solidly earthed, a feeder earth fault cleared by the 1.5 s",
              "  standby would overheat the screen (0.5 s); with the",
              "  resistor the screen has minutes - one reason for the 400 A",
              "  design (lesson A); with the coupler closed both resistors",
              "  feed the fault: 800 A, still far inside the screen's",
              "  rating, but each standby element sees only its own 400 A",
              "  and the standby logic opens the coupler first (lesson B)"]
    emit("u_screens", lines)


if __name__ == "__main__":
    restraint()
    screens()
