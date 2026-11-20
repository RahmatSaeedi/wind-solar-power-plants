"""Chapter 26 - expansion round 5: the structure of a lightning risk
estimate, the lead length of a surge protective device, comparing two
setting files parameter by parameter, and locating a fault on a
collector feeder from the measured reactance.

Run from the project root:   python -m companion.ch26.examples_s
Writes companion/ch26/expected/s_*.txt. Teaching values A-331 to A-335
(the risk method, its factors and tolerable values belong to the
lightning risk standard and the project's study).
"""
from __future__ import annotations

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr


def risk() -> None:
    ng = src.LIGHTNING["ng"]
    a_d = pr.collection_area(8.0, 30.0, 20.0)
    n_d = ng * a_d / 1e6
    loss = 1e-3                                   # teaching loss factor
    lines = ["structure of a lightning risk estimate, control building (teaching):",
             f"  strikes to the building N = Ng x A = {ng} x {a_d:,.0f} m2 = {n_d:.4f} a year",
             "  risk R = N x P (probability of damage) x L (loss if damaged)",
             "  protection                     P       R a year"]
    for name, p in (("none", 1.0), ("LPS of a lower class", 0.2), ("LPS of a higher class", 0.05),
                    ("LPS + coordinated SPDs", 0.01)):
        lines.append(f"  {name:30s} {p:5.2f}   {n_d * p * loss:.1e}")
    lines += ["  the method multiplies three things: how often (N), how",
              "  likely the damage (P, which each measure lowers) and how bad",
              "  (L); the result is compared with a tolerable value - the",
              "  factors and the tolerable values come from the risk",
              "  standard (STD-127) and the project's study with the local",
              "  flash density (U-099); this table shows only the structure"]
    emit("s_risk", lines)


def spd_leads() -> None:
    up, l_per_m = 1.5, 1.0                     # kV, uH per m
    lines = ["surge protective device: the leads add to its protection level",
             f"  SPD protection level {up} kV; lead inductance about {l_per_m} uH/m;",
             "  dU = L di/dt; equipment withstand 4 kV (teaching)",
             "  total lead m   induced surge 1 kA/us   share of a direct strike 10 kA/us"]
    for length in (0.3, 0.5, 1.0, 2.0):
        u1 = up + l_per_m * length * 1.0
        u10 = up + l_per_m * length * 10.0
        lines.append(f"  {length:12.1f}   {u1:10.1f} kV {'ok' if u1 <= 4 else 'NO':>4s}"
                     f"   {u10:21.1f} kV {'ok' if u10 <= 4 else 'NO':>4s}")
    lines += ["  for induced surges the leads matter little; where part of a",
              "  direct strike enters (the zone 0/1 boundary), even 0.3 m of",
              "  lead puts the equipment above its withstand - so that SPD",
              "  gets the shortest leads (a 'V' connection through its",
              "  terminals) and a second stage sits next to the equipment;",
              "  the installation check measures the lead length"]
    emit("s_spd", lines)


def settings_diff() -> None:
    old = {"51 pickup A": 480, "51 TMS": 0.10, "51N pickup A": 40, "51N delay s": 0.5,
           "50BF timer s": 0.15, "CT ratio": 600, "curve": "SI"}
    new = {"51 pickup A": 480, "51 TMS": 0.10, "51N pickup A": 40, "51N delay s": 0.4,
           "50BF timer s": 0.15, "CT ratio": 600, "curve": "VI"}
    lines = ["comparing the approved file with the file read from the relay",
             "  parameter          approved   in the relay   status"]
    changed = 0
    for k in old:
        same = old[k] == new[k]
        changed += 0 if same else 1
        lines.append(f"  {k:18s} {str(old[k]):>8s}   {str(new[k]):>12s}   {'same' if same else 'CHANGED'}")
    lines += [f"  {changed} parameters differ: the checksum shows THAT the file",
              "  changed, the comparison shows WHAT changed - here the curve",
              "  type and the earth-fault delay, both of which move the",
              "  grading (lesson B); the change has no revision, study or",
              "  test: the relay goes back to the approved file and the",
              "  event is recorded (ch 35 for access control)"]
    emit("s_diff", lines)


def fault_locator() -> None:
    x_km, d_in, k = 0.116, 1.1, 0.20
    lines = ["locating a fault on a collector feeder from the measured reactance",
             f"  cable reactance {x_km} ohm/km (240 mm2, ch 24); distance = X / x;",
             f"  turbines beyond {d_in} km add {k:.0%} to the current in the far section",
             "  true km   X seen ohm   located km   error m"]
    for d in (1.0, 2.5, 4.0):
        x = x_km * d if d <= d_in else x_km * (d_in + (d - d_in) * (1 + k))
        loc = x / x_km
        lines.append(f"  {d:7.1f}   {x:10.3f}   {loc:11.2f}   {1000 * (loc - d):7.0f}")
    lines += ["  fed from one end, a resistive fault leaves the reactance",
              "  unchanged, so the distance stays readable; the converters'",
              "  infeed beyond the relay makes the fault look farther (and",
              "  tilts the fault resistance into the reactance) - known",
              "  infeed is corrected in the locator, and sections of",
              "  different cable are modelled; even so, a located fault",
              "  shortens the 68 h repair of ch 24 by the search hours"]
    emit("s_locator", lines)


if __name__ == "__main__":
    risk()
    spd_leads()
    settings_diff()
    fault_locator()
