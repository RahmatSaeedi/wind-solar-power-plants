"""Chapter 25 - from the factory to the energised substation: how many main
transformers, the frequency-response comparison after transport, the
impact recorder's log, an earthing transformer that also feeds the
station service, the transformer's monitoring signals, the equipment of
single- and double-bus bays, their footprint, the states and records of
first energisation, and bushings compared with their factory values.

Run from the project root:   python -m companion.ch25.examples_n
Writes companion/ch25/expected/n_*.txt and diagrams/data/ch25-fra.csv.
Teaching values (A-326..A-330 extended); tests are named by purpose and
evidence only.
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import csv, emit

M = src.MAIN


def sizing() -> None:
    energy, lam, repair_h, price = 295e3, 0.015, 4380.0, 70.0
    opts = [("1 x 125 MVA", 1, 125.0, 1.00), ("2 x 63 MVA", 2, 63.0, 0.18),
            ("3 x 45 MVA", 3, 45.0, 0.03)]
    lines = ["how many main transformers? (teaching: cost ~ S^0.7, 100 MW export)",
             "  option       capex index   outage share   expected loss MWh/yr   k u/yr"]
    for name, n, s, share in opts:
        capex = n * s ** 0.7 / (125 ** 0.7)
        lost = n * lam * repair_h / 8760 * energy * share
        lines.append(f"  {name:12s} {capex:11.2f}   {share:12.0%}   {lost:20.0f}   {lost * price / 1e3:6.0f}")
    lines += ["  one big unit is cheapest but its failure stops the plant for",
              "  months; two units lose only the energy above one unit's",
              "  rating; three lose almost nothing but cost more and take",
              "  more bays - two is the usual balance (D-022), the outage",
              "  share comes from the plant's own output profile"]
    emit("n_sizing", lines)


# [start: fra]
def correlation(a: list, b: list) -> float:
    """Pearson correlation of two traces of equal length."""
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    saa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sbb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sab / (saa * sbb)
# [end: fra]


def trace(f: list, shift: float) -> list:
    out = []
    for x in f:
        g = 0.0
        for f0, q in ((2.0e3, 6.0), (9.0e3, 9.0), (31e3, 12.0), (120e3, 15.0)):
            f0 *= (1 + shift)
            g += 1 / math.sqrt((1 - (x / f0) ** 2) ** 2 + (x / (f0 * q)) ** 2)
        out.append(20 * math.log10(g))
    return out


def fra() -> None:
    f = [10 ** (2 + 3.3 * k / 299) for k in range(300)]
    ref = trace(f, 0.0)
    rows, lines = [], ["frequency-response comparison before and after transport (synthetic):",
                       "  resonance shift   correlation   reading"]
    for shift in (0.0, 0.005, 0.02, 0.06):
        cc = correlation(ref, trace(f, shift))
        reading = "same" if cc > 0.998 else ("look closer" if cc > 0.98 else "investigate")
        lines.append(f"  {shift:15.1%}   {cc:11.4f}   {reading}")
    csv("ch25-fra.csv", "f,ref,after", [(f"{a:.1f}", f"{b:.2f}", f"{c:.2f}")
                                        for a, b, c in zip(f, ref, trace(f, 0.02))][::3])
    lines += ["  a winding that moved in transport changes its inductances",
              "  and capacitances and shifts the resonances: the trace taken",
              "  at the factory is the reference, the one on site the check",
              "  - the comparison methods and limits are the specialists'",
              "  (the thresholds here are teaching values)"]
    emit("n_fra", lines)


IMPACT = [("rail transfer", 1.2, 0.6, 0.8), ("port crane", 2.1, 0.9, 1.6),
          ("road, bridge joint", 1.0, 0.7, 1.1), ("road, pothole", 3.4, 1.0, 2.6),
          ("skidding to plinth", 0.8, 0.4, 0.5)]


def impact() -> None:
    lim = (3.0, 2.0, 2.0)
    lines = ["impact recorder log of the main transformer's journey (g, teaching",
             "  limits 3 / 2 / 2 g along / across / vertical):",
             "  event                 along  across  vertical  result"]
    over = []
    for name, a, c, v in IMPACT:
        bad = a > lim[0] or c > lim[1] or v > lim[2]
        if bad:
            over.append(name)
        lines.append(f"  {name:20s} {a:6.1f}  {c:6.1f}  {v:8.1f}  {'OVER' if bad else 'ok'}")
    lines += [f"  over the limits: {', '.join(over)}",
              "  an exceedance is not damage, but it is a reason: the",
              "  contract's procedure then asks for an internal inspection",
              "  and the frequency-response comparison before energising -",
              "  the recorder's file is part of the transport record"]
    emit("n_impact", lines)


def earthing_unit() -> None:
    u_ph, i_n, t = 33e3 / math.sqrt(3), 400.0, 10.0
    lines = ["one unit, two jobs: an earthing transformer with an auxiliary winding",
             f"  earthing: neutral current {i_n:.0f} A for {t:.0f} s ->"
             f" {u_ph * i_n / 1e6:.1f} MVA short-time",
             "  auxiliary winding: 250 kVA continuous at 0.4 kV (the station",
             "  service transformer of ch 23)",
             "  the zigzag gives the 33 kV system its neutral (ch 26) and the",
             "  second winding feeds the auxiliaries: one tank, one bay,",
             "  one set of tests instead of two - but one failure takes",
             "  both the earthing and the auxiliary supply of that section,",
             "  which the other section's unit must then cover"]
    emit("n_earthing", lines)


IO = [("gas relay alarm / trip", 2, 0, 0, "protection"), ("pressure relief trip", 1, 0, 0, "protection"),
      ("oil level low", 1, 0, 0, "SCADA"), ("oil temperature alarm / trip", 2, 0, 1, "both"),
      ("winding temperature alarm / trip", 2, 0, 1, "both"), ("tap position", 0, 0, 1, "SCADA"),
      ("tap changer raise / lower", 0, 2, 0, "control"), ("tap changer protective relay", 1, 0, 0, "protection"),
      ("fan groups on / fail", 4, 2, 0, "SCADA"), ("dissolved-gas monitor", 1, 0, 3, "SCADA"),
      ("bushing monitor", 1, 0, 3, "SCADA")]


def io_list() -> None:
    di = sum(r[1] for r in IO)
    do = sum(r[2] for r in IO)
    ai = sum(r[3] for r in IO)
    lines = ["signals of one main transformer (teaching list):",
             "  signal                              DI  DO  AI  to"]
    lines += [f"  {a:35s} {b:3d} {c:3d} {d:3d}  {e}" for a, b, c, d, e in IO]
    lines += [f"  per transformer: {di} digital in, {do} digital out, {ai} analogue in;"
              f" two: {2 * (di + do + ai)}",
              "  trips go hard-wired to the protection (lockout, ch 26);",
              "  alarms and measurements to SCADA (ch 34); each line is a row",
              "  of the signal list and a terminal pair in the marshalling",
              "  box (ch 24 lesson D)"]
    emit("n_io", lines)


def takeoff() -> None:
    bays = 3
    single = dict(breakers=bays, disconnectors=bays * 2, earth_switches=bays, cts=bays * 3,
                  vts=3 + 3, arresters=bays * 3)
    double = dict(breakers=bays + 1, disconnectors=bays * 3 + 2, earth_switches=bays + 2,
                  cts=(bays + 1) * 3, vts=3 + 6, arresters=bays * 3)
    lines = ["132 kV equipment take-off: single bus against double bus (3 bays):",
             "  item               single   double"]
    for k in single:
        lines.append(f"  {k.replace('_', ' '):18s} {single[k]:6d}   {double[k]:6d}")
    lines += [f"  {sum(single.values())} items against {sum(double.values())}: the double bus"
              " adds a coupler",
              "  bay, a second set of bus disconnectors per bay, bus VTs and",
              "  earthing - about two-fifths more equipment for the",
              "  flexibility of lesson G, which the reliability numbers of",
              "  lesson G must then justify"]
    emit("n_takeoff", lines)


def footprint() -> None:
    bay_w, bay_l = 11.0, 45.0           # m, teaching for 145 kV AIS
    lines = ["footprint of the 132 kV yard (teaching bay size 11 m x 45 m):",
             "  arrangement           bays   area m2"]
    for name, n, extra in (("single bus", 3, 0.0), ("single bus, sectioned", 4, 0.0),
                           ("double bus", 4, 0.2)):
        lines.append(f"  {name:21s} {n:4d}   {n * bay_w * bay_l * (1 + extra):7.0f}")
    lines += ["  plus roads, the transformer bays, the control building and",
              "  the fence clearance; clearances and bay widths come from the",
              "  insulation level and the installation standard (the",
              "  numbers here are teaching values, not a layout)"]
    emit("n_footprint", lines)


def energise() -> None:
    steps = [("before", "insulation and ratio checks done, baseline oil sample"),
             ("first energising", "inrush recorded by the protection relays"),
             ("soak, no load", "sound, temperatures, gas relay watched for a set period"),
             ("after soak", "second oil sample compared with the baseline"),
             ("first load", "thermal readings against the heat-run results"),
             ("records", "event and disturbance files, readings, signatures")]
    lines = ["first energisation of a main transformer: states and records"]
    lines += [f"  {a:16s} {b}" for a, b in steps]
    lines += ["  each state has a hold point and a record; the switching",
              "  itself follows the operator's programme and the owner's",
              "  safety rules (ch 48-50) - this list says what is shown,",
              "  not how it is done"]
    emit("n_energise", lines)


def bushings() -> None:
    data = [("HV A", 450, 452, 0.0035, 0.0036), ("HV B", 448, 470, 0.0034, 0.0049),
            ("HV C", 451, 453, 0.0036, 0.0037)]
    lines = ["bushings: site readings against the factory's (teaching limits:",
             "  capacitance change 3 %, dissipation factor change 30 %)",
             "  bushing  C factory  C site  change  tan d factory  site    result"]
    for name, c0, c1, d0, d1 in data:
        dc = (c1 - c0) / c0
        dd = (d1 - d0) / d0
        bad = abs(dc) > 0.03 or dd > 0.30
        lines.append(f"  {name:7s} {c0:9d}  {c1:6d}  {dc:6.1%}  {d0:13.4f}  {d1:.4f}  "
                     f"{'investigate' if bad else 'ok'}")
    lines += ["  a capacitance step means a layer of the bushing's insulation",
              "  has broken down; a rising dissipation factor means moisture",
              "  or ageing - both against the bushing's own factory values,",
              "  which is why the factory report travels with the bushing"]
    emit("n_bushings", lines)


if __name__ == "__main__":
    sizing()
    fra()
    impact()
    earthing_unit()
    io_list()
    takeoff()
    footprint()
    energise()
    bushings()
