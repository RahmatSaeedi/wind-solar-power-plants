"""Chapter 26 - circuit protection below the 33 kV relays: PV string fuses,
why DC array faults hide from overcurrent devices, the insulation
resistance of a large floating array, the unit transformer's
overcurrent and instantaneous settings, low-voltage selectivity and the
loop-impedance limit of a final circuit, and DC breaking in the 110 V
control supply.

Run from the project root:   python -m companion.ch26.examples_h
Writes companion/ch26/expected/h_*.txt. Teaching values A-331 to A-335
(module data from ch 10; reverse-current rating 25 A is a teaching
value - the module's datasheet gives the real one).
"""
from __future__ import annotations

import math

from companion.ch26.common import emit
from plantp import protection as pr

ISC, IMP, I_REV = 13.98, 13.11, 25.0
STRINGS = 20                 # strings per combiner (D-013)


def string_fuses() -> None:
    worst = (STRINGS - 1) * ISC * 1.25
    lo = 1.5 * ISC                       # the same teaching rule as ch 24
    lines = ["PV string fuses (teaching rules):",
             f"  {STRINGS} strings in parallel; a faulted string can receive the"
             f" others' current:",
             f"  (n - 1) x Isc = {STRINGS - 1} x {ISC} = {(STRINGS - 1) * ISC:.0f} A"
             f" (with 1.25 for high irradiance {worst:.0f} A)",
             f"  module reverse-current rating {I_REV:.0f} A -> fuses needed:"
             f" {'yes' if pr.fuse_needed(STRINGS, ISC, I_REV) else 'no'}",
             f"  fuse window: at least 1.5 x Isc = {lo:.1f} A (it must not blow",
             f"  in sun; ch 24's rule), at most {I_REV:.0f} A (it must protect the module)",
             "  -> a 25 A gPV fuse in each pole fits, barely: the window is",
             "  narrow, so the fuse curve and the module's rating are",
             "  checked together; with two strings no fuse is needed",
             f"  ({'yes' if pr.fuse_needed(2, ISC, I_REV) else 'no'} for n = 2)"]
    emit("h_fuses", lines)


def dc_hidden() -> None:
    lines = ["why a DC array fault hides from overcurrent devices:",
             f"  a string works at Imp {IMP} A and cannot give more than Isc {ISC} A:",
             f"  its short-circuit current is only {ISC / IMP:.2f} x its working current",
             "  a fault between two strings, or an arc in a connector, may",
             "  carry less than the working current; no fuse sees it",
             "  so the array is protected by other means: insulation",
             "  monitoring of the floating array, arc-fault detection in",
             "  the inverter (where offered), and good connectors fitted by",
             "  trained hands - the faults are prevented and found, not",
             "  cleared by current"]
    emit("h_hidden", lines)


def insulation() -> None:
    n = 21 * STRINGS
    lines = ["insulation resistance of a floating PV block (teaching):",
             f"  {n} strings in parallel to earth (21 combiners x {STRINGS})",
             "  per string MOhm   block kOhm"]
    for r in (40.0, 20.0, 2.0):
        lines.append(f"  {r:16.0f}   {r * 1e3 / n:10.1f}")
    lines += ["  a healthy large block reads tens of kOhm; on a wet morning",
              "  every string drops together and the inverter may refuse to",
              "  start until it dries: the inverter's threshold must suit",
              "  the block size (the maker's setting)",
              "  a single earth fault on a floating array drives little",
              "  current - it is an alarm, found and repaired before a",
              "  second fault on the other pole makes a real short circuit"]
    emit("h_insulation", lines)


def unit_transformer() -> None:
    s, z = 5.6e6, 0.07
    i_n = s / (math.sqrt(3) * 33e3)
    i_lv = i_n / z
    inrush = 12 * i_n
    i_hv_min = 4_680.0
    set50 = 1.3 * max(i_lv, inrush)
    lines = ["unit transformer =WS1-1-T1 (5.6 MVA, 7 %) at its 33 kV breaker:",
             f"  rated current {i_n:.0f} A; LV fault seen at 33 kV {i_lv:,.0f} A;"
             f" inrush ~12 x = {inrush:,.0f} A",
             f"  overcurrent (51): pickup 1.3 x rated = {1.3 * i_n:.0f} A, graded under"
             " the feeder",
             "  instantaneous (50): 1.3 x the larger of the LV fault and the",
             f"    inrush: {set50:,.0f} A, below the smallest HV fault at"
             f" the turbine ({i_hv_min:,.0f} A)",
             f"  window holds: {'yes' if set50 < i_hv_min / 1.5 else 'no'} (with 1.5 margin"
             f" on the HV fault: {i_hv_min / 1.5:,.0f} A)",
             "  so an HV fault in the turbine's transformer trips at once,",
             "  an LV fault is left to the turbine's own LV breaker first,",
             "  and the inrush on energising does not trip anything",
             "  (a fuse for 5.6 MVA at 33 kV is at the edge of fuse ranges;",
             "  ch 23 chose a breaker for the wind units)"]
    emit("h_unit", lines)


def lv_selectivity() -> None:
    lines = ["400 V station-service board: main 400 A, outgoing 32 A (type C):",
             "  device        instantaneous from   fault at board 7.9 kA",
             f"  outgoing 32 A {10 * 32:12,d} A        trips instantly",
             f"  main 400 A    {10 * 400:12,d} A        ALSO trips instantly",
             "  by current alone the two are not selective at the board's",
             "  full fault level; selectivity comes from the energy (I2t)",
             "  let through by the small device being below the large",
             "  one's operating energy (makers' selectivity tables) or a",
             "  short delay on the main",
             "  far from the board the fault is smaller:"]
    for m in (10, 30, 60):
        zs = 0.03 + m * 2 * 0.0055
        i = 230 / zs
        lines.append(f"    {m:3d} m of 4 mm2: {i:6,.0f} A -> outgoing"
                     f" {'instant' if i >= 320 else 'SLOW (delay)'}; main"
                     f" {'instant' if i >= 4000 else 'stays closed'}")
    emit("h_lv", lines)


def loop_limit() -> None:
    lines = ["loop-impedance limit of a final circuit (concept, teaching):",
             "  the device must disconnect within the time the wiring",
             "  rules require: Zs x Ia <= U0, with Ia the current that",
             "  trips it in that time (type C 32 A: 10 x 32 = 320 A)",
             f"  Zs max = 230 / 320 = {230 / 320:.2f} ohm; source part 0.03 ohm",
             "  cable mm2   loop ohm per m   longest run m"]
    for mm2, r in ((2.5, 2 * 0.0088), (4.0, 2 * 0.0055), (6.0, 2 * 0.0037)):
        lines.append(f"  {mm2:9.1f}   {r:14.4f}   {(230 / 320 - 0.03) / r:13.0f}")
    lines += ["  a long run to a remote load (a gate, a weather mast, a",
              "  pump) may need a larger cable, an RCD, or a smaller device:",
              "  the protection sets the cable as much as the load does"]
    emit("h_loop", lines)


def dc_breaking() -> None:
    v, r_int, r_cable = 110.0, 0.025, 0.010
    i = v / (r_int + r_cable)
    lines = ["the 110 V control battery (ch 23) and its circuits:",
             f"  internal 0.025 ohm + cable 0.010 ohm -> fault current {i / 1e3:.1f} kA",
             "  direct current has no zero crossing: the breaker must be",
             "  rated to break DC at this voltage and current (AC ratings",
             "  do not apply); selectivity between the battery fuse and",
             "  the circuit breakers is checked like the AC board",
             "  each protection panel has its own DC circuit with",
             "  supervision - lesson B's independence of main and backup"]
    emit("h_dc", lines)


def converters() -> None:
    items = [("wind converter", "DC-link chopper, crowbar or blocking, AC and DC breakers"),
             ("PV inverter", "DC input fuses/switches, AC breaker, insulation check"),
             ("battery PCS", "DC breakers per rack (ch 19), AC breaker, contactors"),
             ("all three", "own voltage, frequency and current limits")]
    lines = ["protection inside the converters (the makers' settings):"]
    lines += [f"  {a:15s} {b}" for a, b in items]
    lines += ["  these settings are the makers', but they meet the plant's at",
              "  two places: they must not trip inside the ride-through",
              "  envelope (lesson B), and their fault current feeds the",
              "  study - so the makers' setting lists are plant documents"]
    emit("h_converters", lines)


if __name__ == "__main__":
    string_fuses()
    dc_hidden()
    insulation()
    unit_transformer()
    lv_selectivity()
    loop_limit()
    dc_breaking()
    converters()
