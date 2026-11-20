"""Chapter 24, section F - collector and export circuit engineering: one
size or a graded string (economics), sheath bonding (standing voltage,
circulating losses avoided), charging current of cable and line, the
overhead line's sag, tension and clearance, and overhead line against
underground cable for the 132 kV export without a universal answer.

Run from the project root:   python -m companion.ch24.examples_f
Writes companion/ch24/expected/f_*.txt. Teaching values A-321 to A-325.
"""
from __future__ import annotations

import math

from companion.ch18 import sources as s18
from companion.ch24 import examples_a as ea
from companion.ch24 import sources as src
from companion.ch24.common import emit
from plantp import cables as cb

ALPHA_AL = 0.00403
PRICE, YEARS, RATE = 70.0, 25, 0.075


def graded() -> None:
    i = ea.string_currents()
    af = (1 - (1 + RATE) ** -YEARS) / RATE
    plans = {"240 all (section 1 too hot: not allowed)": (240, 240, 240, 240),
             "graded 630/240/240/240": (630, 240, 240, 240),
             "graded 630/400/240/240": (630, 400, 240, 240),
             "630 everywhere": (630, 630, 630, 630)}
    lines = ["one size or a graded wind string (cost + PV of losses, k u):",
             "  plan                                         cost  loss MWh/yr   PV total"]
    for name, sizes in plans.items():
        cost = loss = 0.0
        for k, mm2 in enumerate(sizes, 1):
            d = src.MV_CABLES[mm2]
            cost += d["cost"] * 1.1
            r = cb.r_at(d["r20"], 65, ALPHA_AL)
            loss += cb.annual_loss_mwh(i * (5 - k) / 4, r, 1.1)
        tot = cost + loss * PRICE / 1e3 * af
        lines.append(f"  {name:44s} {cost:5.0f}  {loss:11.1f}  {tot:9.0f}")
    lines += ["  at the teaching price the graded string with 630 mm2 only",
              "  where it must is cheapest; a larger section never pays back",
              "  its cost in losses - but stocking two sizes means two sets of",
              "  joints, terminations and spares (ch 51)"]
    emit("f_graded", lines)


def bonding() -> None:
    lines = ["sheath bonding of a 132 kV single-core export cable (teaching):",
             "  standing voltage at the open end, single-point bonding,",
             "  trefoil s = 140 mm, sheath diameter 105 mm, I = 437 A:",
             "  length m   volts at full load   at a 20 kA fault"]
    for L in (300, 500, 800):
        v = cb.sheath_v(437, 140, 105, L)
        vf = cb.sheath_v(20_000, 140, 105, L)
        lines.append(f"  {L:8d}   {v:18.0f}   {vf:16.0f}")
    lines += ["  both ends bonded: no standing voltage but a circulating",
              "  current and a loss in the sheaths; single-point bonding",
              "  stops the loss but leaves a voltage that must stay under a",
              "  touch limit and is clamped by sheath voltage limiters at",
              "  the open end; cross-bonding in three minor sections cancels",
              "  it on long routes - the choice and its limits are the",
              "  cable designer's (and touch safety is not a field trial)"]
    emit("f_bonding", lines)


def charging() -> None:
    lines = ["charging current of the export options (no load):"]
    for name, kv, c, km in (("33 kV collector 240 mm2", 33, 0.21, 21.6),
                            ("132 kV overhead line", 132, 0.009, 7.06),
                            ("132 kV underground cable", 132, 0.20, 7.06)):
        ic = cb.charging_a(kv, c, km)
        q = math.sqrt(3) * kv * ic / 1e3
        lines.append(f"  {name:28s} {ic:6.1f} A   {q:5.1f} Mvar")
    lines += ["  the cable makes 20 times the line's reactive power: at",
              "  light load the plant exports Mvar it did not choose, which",
              "  the reactive-power capability and perhaps a reactor must",
              "  absorb (ch 20, 27, 28)"]
    emit("f_charging", lines)


def sag() -> None:
    L = src.LINE
    h = L["breaking_kn"] * 1e3 * L["tension_pct"] / 100
    lines = ["overhead line span (teaching conductor, level ground):",
             f"  weight {L['weight_n_m']} N/m, breaking load {L['breaking_kn']:.0f} kN,"
             f" everyday tension {L['tension_pct']:.0f} % = {h / 1e3:.0f} kN",
             "  span m   sag m   tower height for 7 m clearance + 2 m"]
    for span in (250, 300, 350):
        s = cb.sag_m(L["weight_n_m"], span, h)
        lines.append(f"  {span:6d}  {s:6.2f}   {7 + s + 2:8.1f} m")
    hot = cb.sag_m(L["weight_n_m"], 300, h * 0.85)
    lines += [f"  hot conductor (tension 15 % lower): sag {hot:.2f} m on 300 m",
              "  longer spans need fewer towers but taller ones; the",
              "  clearance, the wind and ice loads and the hot-conductor",
              "  case come from the approved line standard and the line",
              "  designer - this is a concept, not a line design"]
    emit("f_sag", lines)


def ohl_vs_cable() -> None:
    e = s18.EXPORT
    o, c = e["overhead line, single circuit"], e["underground cable"]
    km = 7.06
    rows = [("cost k u", o["cost_per_km"] * km, c["cost_per_km"] * km),
            ("failures a year", o["fail_per_km"] * km, c["fail_per_km"] * km),
            ("repair hours", o["repair_h"], c["repair_h"]),
            ("outage h a year", o["fail_per_km"] * km * o["repair_h"],
             c["fail_per_km"] * km * c["repair_h"]),
            ("charging Mvar", math.sqrt(3) * 132 * cb.charging_a(132, 0.009, km) / 1e3,
             math.sqrt(3) * 132 * cb.charging_a(132, 0.20, km) / 1e3)]
    lines = ["132 kV export: overhead line against underground cable (ch 18 data):",
             "  item                    overhead        cable"]
    for name, a, b in rows:
        lines.append(f"  {name:20s} {a:12,.2f} {b:12,.2f}")
    lines += ["  the line is cheaper and quicker to repair; the cable fails",
              "  less, is out longer when it does, makes more Mvar and fits",
              "  where a line cannot (a town, an airfield, a landscape);",
              "  the choice is made route by route - neither is right",
              "  everywhere (ch 14 landscape, ch 18 option)"]
    emit("f_ohl", lines)


if __name__ == "__main__":
    graded()
    bonding()
    charging()
    sag()
    ohl_vs_cable()
