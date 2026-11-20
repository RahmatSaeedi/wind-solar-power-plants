"""Chapter 26, sections A, B and E - fault currents at the 33 kV bus by
symmetrical components (and why the 400 A resistor matters), the
grading of inverse-time overcurrent relays from feeder to transformer,
earth-fault grading, current-transformer knee points, the transformer
differential against through faults and inrush, distance zones on the
export line, breaker-failure timing, and the zones of the plant.

Run from the project root:   python -m companion.ch26.examples_a
Writes companion/ch26/expected/a_*.txt, b_*.txt, e_*.txt and
diagrams/data/ch26-*.csv. Teaching settings A-331 to A-335.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch26 import sources as src
from companion.ch26.common import csv, emit
from plantp import protection as pr

N = src.NETWORK


def faults() -> None:
    e = 33e3 / math.sqrt(3)
    z1 = complex(0, N["z1_33"])
    solid = pr.fault_currents(e, z1, z1, complex(0, N["z0_et"]))
    ner = pr.fault_currents(e, z1, z1, complex(0, N["z0_et"]), zf=N["r_ner"])
    lines = ["fault currents at a 33 kV bus section (coupler open, teaching):",
             f"  Z1 = Z2 = {N['z1_33']:.2f} ohm; earthing transformer Z0 {N['z0_et']:.1f} ohm",
             f"  three-phase      {solid['3ph'] / 1e3:6.2f} kA",
             f"  line to line     {solid['LL'] / 1e3:6.2f} kA",
             f"  line to earth, solidly earthed:   {solid['SLG'] / 1e3:6.2f} kA",
             f"  line to earth through 47.6 ohm:   {ner['SLG']:6.0f} A",
             f"  the resistor turns a {solid['SLG'] / 1e3:.1f} kA earth fault into about"
             f" {ner['SLG']:.0f} A: the",
             "  cable screens, the earth grid and the touch voltages see",
             "  400 A, and the earth-fault relays must be sensitive enough",
             "  to see it (below)"]
    emit("a_faults", lines)


def t_of(name: str, i: float) -> float:
    d = src.RELAYS[name]
    return pr.trip_time(i, d["pickup"], d["tms"])


def grading_cases() -> list:
    """(case, current seen by the feeder relay, by the incomer relay)."""
    far = abs(src.E_PH / src.feeder_z(4)) * math.sqrt(3) / 2
    return [("coupler open, fault at feeder head", N["ik_33_one"] + N["conv_ka"] / 2,
             N["ik_33_one"]),
            ("coupler closed, fault at feeder head", N["ik_33_both"] + N["conv_ka"],
             N["ik_33_both"] / 2),
            ("coupler open, LL fault at far end", far, far)]


def grading() -> None:
    lines = ["overcurrent grading on the 33 kV: the current each relay SEES",
             "  case                                  feeder kA  s   incomer kA  s"
             "   HV s"]
    ok = True
    for name, i_f, i_i in grading_cases():
        tf, ti, th = t_of("feeder", i_f), t_of("incomer", i_i), t_of("T1 HV side", i_i / 4)
        ok &= pr.grading_ok(tf, ti) and pr.grading_ok(ti, th)
        lines.append(f"  {name:37s} {i_f / 1e3:5.2f} {tf:5.2f}  {i_i / 1e3:6.2f} {ti:5.2f}"
                     f" {th:5.2f}")
    lines += [f"  margins of at least 0.3 s in every case: {'yes' if ok else 'NO'}",
              "  with the coupler closed each incomer carries only half of",
              "  the grid's current: its relay is slower, the margin wider;",
              "  the converters feed the feeder relay but not the incomer;",
              "  the HV relay sees the 33 kV current divided by the ratio 4"]
    emit("a_grading", lines)
    def cell(t: float) -> str:
        return f"{t:.3f}" if t <= 20 else "nan"
    csv("ch26-grading.csv", "ka,feeder,incomer,hv",
        [(f"{i / 1e3:.3f}", cell(t_of("feeder", i)), cell(t_of("incomer", i)),
          cell(t_of("T1 HV side", i / 4)))
         for i in np.geomspace(1_600, 14_000, 40)])


def earth_fault() -> None:
    f, s = src.EARTH["feeder"], src.EARTH["NER standby"]
    r = src.EARTH["earthing resistor"]
    lines = ["earth-fault grading on the resistance-earthed 33 kV:",
             "  the 33 kV side of each main transformer is a delta: it has",
             "  no neutral, so the earth-fault current comes only from the",
             "  earthing transformer and its resistor on the bus section;",
             "  the incomer's residual current is zero for a feeder earth",
             "  fault - the backup is a standby element on the resistor",
             f"  feeder element {f['pickup']:.0f} A after {f['delay']} s;"
             f" standby {s['pickup']:.0f} A after {s['delay']} s",
             f"  sensitivity: 400 A is {400 / f['pickup']:.0f} x the feeder pickup -",
             "    faults with some arc resistance are still seen",
             f"  the resistor is rated {r['rating_a']:.0f} A for {r['rating_s']:.0f} s:",
             f"    the standby's {s['delay']:.1f} s plus breaker failure"
             f" ({s['delay'] + 0.25:.2f} s) is inside it",
             "  a core-balance CT around each feeder cable sees the earth",
             "  current without the load current - a check of CT choice"]
    emit("a_earth", lines)


def ct_knee() -> None:
    lines = ["current-transformer knee points (teaching check, k = 2):",
             "  CT              fault A   secondary A   R_ct+R_b   need V   knee V   ok"]
    for name, ratio, ik, rct, rb, vk in (("feeder 600/1", 600, 12_500, 3.0, 1.5, 200),
                                         ("feeder 600/1", 600, 12_500, 3.0, 1.5, 100),
                                         ("incomer 1600/1", 1600, 12_500, 5.0, 1.5, 200)):
        isec = ik / ratio
        need = 2 * isec * (rct + rb)
        lines.append(f"  {name:14s} {ik:7,d}   {isec:11.1f}   {rct + rb:8.1f}   {need:6.0f}"
                     f"   {vk:6d}   {'yes' if pr.ct_knee_ok(vk, isec, rct, rb) else 'no'}")
    lines += ["  a CT that saturates in a fault gives the relay a distorted",
              "  current: the knee point is specified from the fault level",
              "  and the burden, and proved by the CT's test (ch 43)"]
    emit("b_ct", lines)


def differential() -> None:
    cases = [("through fault, CTs matched", 8.3, -8.3),
             ("through fault, 5 % CT mismatch", 8.3, -7.9),
             ("internal fault fed from HV only", 8.3, 0.0),
             ("internal fault, light load", 1.0, -0.2)]
    lines = ["transformer differential with bias (pickup 0.2 pu, slope 30 %):"]
    for name, i1, i2 in cases:
        lines.append(f"  {name:32s} I1 {i1:5.1f}  I2 {i2:5.1f}  ->"
                     f" {'trip' if pr.diff_trips(i1, i2) else 'restrain'}")
    lines += ["  inrush on energising is all on one side and would look like",
              "  an internal fault: its 2nd harmonic blocks the element",
              "  (threshold set with the maker); the 30-degree shift of YNd11",
              "  is compensated in the relay (ch 25)"]
    emit("b_diff", lines)


def distance() -> None:
    z = pr.distance_zones(N["z_line"], N["z_next"])
    lines = ["distance zones on the 132 kV export line (teaching reaches):",
             f"  line {N['z_line']:.2f} ohm (7.06 km), next line {N['z_next']:.2f} ohm (20 km)"]
    for k, v in z.items():
        lines.append(f"  {k}: {v:5.2f} ohm  ({v / N['z_line'] * 100:4.0f} % of this line)")
    lines += ["  zone 1 trips at once but stops short of the far end (errors",
              "  in CTs, VTs, line data); zones 2 and 3 reach further with",
              "  delay; a short line makes zone 1 small - line differential",
              "  over the fibre in the earth wire is the usual answer, with",
              "  distance as backup; the utility approves both ends"]
    emit("e_distance", lines)


def breaker_fail() -> None:
    t_relay, t_bf, t_breaker = 0.03, 0.15, 0.06
    lines = ["breaker-failure timing (teaching):",
             f"  relay {t_relay * 1e3:.0f} ms + breaker {t_breaker * 1e3:.0f} ms = normal clearing"
             f" {(t_relay + t_breaker) * 1e3:.0f} ms",
             f"  if the breaker fails: BF timer {t_bf * 1e3:.0f} ms, then the adjacent breakers"
             f" ({t_breaker * 1e3:.0f} ms)",
             f"  backup clearing {(t_relay + t_bf + t_breaker) * 1e3:.0f} ms - the duty the cables"
             " and gear must carry (ch 24)",
             "  for the line bay the adjacent breaker is at the grid end:",
             "  a transfer-trip signal over the telecom link opens it"]
    emit("e_bf", lines)


def zones() -> None:
    z = [("unit transformer and its cable", "RMU fuse or breaker, feeder backup"),
         ("collector feeder cable", "feeder overcurrent and earth fault"),
         ("33 kV bus section", "bus protection or incomer backup"),
         ("main transformer", "differential, gas relay, overcurrent backup"),
         ("132 kV bus", "bus or transformer HV protection"),
         ("export line", "line differential or distance, both ends"),
         ("grid side", "utility's protection; transfer trip")]
    lines = ["protection zones of Plant P (overlapping at every breaker):"]
    lines += [f"  {a:32s} {b}" for a, b in z]
    lines += ["  zones overlap so no part is unprotected: each breaker sits",
              "  between the CTs of two zones; settings and schemes at the",
              "  boundary are approved by the operator (U-089)"]
    emit("e_zones", lines)


if __name__ == "__main__":
    faults()
    grading()
    earth_fault()
    ct_knee()
    differential()
    distance()
    breaker_fail()
    zones()
