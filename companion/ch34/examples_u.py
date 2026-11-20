"""Chapter 34, lesson G (deeper): what the accuracy of the measurement
does to a grid service - frequency error against the droop, voltage
error against the reactive droop, the active-power accuracy against a
tolerance, and where the POC is measured.

Run from the project root:   python -m companion.ch34.examples_u
Writes companion/ch34/expected/u_*.txt.
Teaching values: droop and deadband of ch 20 (A-299), measurement chain
of lesson A (A-385), line of ch 28 (A-341); the grid code decides.
"""
from __future__ import annotations

import math

from companion.ch34.common import emit
from plantp import instrumentation as ins


def frequency_error() -> None:
    droop, deadband, p_base = 0.04, 0.020, 110.0       # ch 20
    lines = ["frequency measurement error against the droop (4 %, 110 MW)",
             "  frequency error mHz   power error MW   share of the 20 mHz deadband"]
    for e_mhz in (1.0, 5.0, 10.0, 20.0):
        dp = (e_mhz / 1000 / 50.0) / droop * p_base
        lines.append(f"  {e_mhz:19.0f}   {dp:14.2f}   {e_mhz / (deadband * 1000) * 100:22.0f} %")
    lines += ["  a 10 mHz error moves the edge of the deadband by half its",
              "  width and the response by half a megawatt, in the same",
              "  direction for hours: the frequency input is specified in",
              "  millihertz, with its window, and checked in the",
              "  frequency-response test (ch 27, ch 50)"]
    emit("u_freq", lines)


def voltage_error() -> None:
    slope, q_max = 0.04, 33.0                            # ch 20 Q-V droop
    lines = ["voltage measurement error against the Q-V droop (4 %, 33 Mvar)",
             "  chain                        error % (k = 2)   reactive error Mvar"]
    for name, e in (("VT class 0.5 chain (lesson A)", 0.66),
                    ("VT class 0.2 chain", 0.39)):
        dq = (e / 100) / slope * q_max
        lines.append(f"  {name:29s} {e:15.2f}   {dq:19.1f}")
    lines += ["  a voltage error of a few tenths of a per cent becomes",
              "  several megavars through a steep droop - a sixth of the",
              "  33 Mvar with the class 0.5 core; this is why the",
              "  controller reads the class 0.2 core, and why the voltage",
              "  set point and its measurement are agreed with the grid",
              "  operator as a pair (U-115)"]
    emit("u_volt", lines)


def power_tolerance() -> None:
    meas = ins.combine(0.2 / math.sqrt(3), 0.2 / math.sqrt(3), 0.2 / math.sqrt(3)) * 2
    ctrl = 0.5                          # control error band, % of 100 MW (teaching)
    tol = 1.0                           # placeholder tolerance, % of 100 MW
    lines = ["active power at the POC against a tolerance of +/-1 % (placeholder)",
             f"  measurement (CT, VT, transducer of class 0.2; k = 2): +/-{meas:.2f} %",
             f"  control error band (teaching): +/-{ctrl:.2f} %",
             f"  together {ins.combine(meas, ctrl):.2f} % of a {tol:.2f} % tolerance:"
             f" {ins.combine(meas, ctrl) / tol * 100:.0f} % of it used",
             "  a tolerance is shared between the controller and the",
             "  meter; the grid operator's own meter judges the plant,",
             "  so the plant's measurement is compared with it during",
             "  commissioning and any offset written down (ch 50)"]
    emit("u_tol", lines)


def poc_location() -> None:
    km, r, x, c_nf, kv = 7.06, 0.12, 0.40, 9.0, 132.0    # ch 28 line
    lines = ["the PPC measures at the plant end; the POC is at the grid end",
             f"  line {km} km, r {r} and x {x} ohm/km, {c_nf:.0f} nF/km (ch 28)",
             "  export MW   current A   line loss MW   line Mvar (net absorbed)"]
    q_c = (kv * 1e3) ** 2 * 2 * math.pi * 50 * c_nf * 1e-9 * km / 1e6
    for p in (0.0, 50.0, 100.0):
        i = p * 1e6 / (math.sqrt(3) * kv * 1e3)
        loss = 3 * i ** 2 * r * km / 1e6
        q_l = 3 * i ** 2 * x * km / 1e6 - q_c
        lines.append(f"  {p:9.0f}   {i:9.0f}   {loss:12.2f}   {q_l:+12.2f}")
    lines += [f"  charging {q_c:.2f} Mvar; at 100 MW the plant end reads about",
              "  0.5 MW and 1.3 Mvar more than the POC receives",
              "  the controller either reads the POC itself (a measurement",
              "  in the grid bay, with its own delay) or corrects by a",
              "  line model with I squared; the choice is part of D-021's",
              "  open POC and is recorded in the control narrative"]
    emit("u_poc", lines)


if __name__ == "__main__":
    frequency_error()
    voltage_error()
    power_tolerance()
    poc_location()
