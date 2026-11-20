"""Chapter 25 - the transformer in service: a hot day of hybrid loading in
a dynamic thermal model, ageing with moisture in the paper, reading
dissolved gases, how often the tap changer works, oil expansion and the
conservator, radiator area, the no-load loss at night, and whether a
spare transformer pays.

Run from the project root:   python -m companion.ch25.examples_k
Writes companion/ch25/expected/k_*.txt and diagrams/data/ch25-hotday.csv.
Teaching models and values (A-326..A-330 extended): the loading guide,
the maker's data and the oil laboratory decide in practice.
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import csv, emit
from plantp import transformer as tr

M = src.MAIN


# [start: dynamic]
def hot_day(step_min: float = 5.0) -> list:
    """Top-oil and hot-spot temperatures through a hot day with a hybrid
    load (wind at night, PV peak at noon), first-order responses:
    top oil tau 180 min, winding gradient tau 7 min."""
    d_or, d_hr, r, x, y = 52.0, 26.0, 6.0, 0.8, 1.6
    tau_o, tau_w = 180.0, 7.0
    d_o, d_h = 30.0, 5.0
    rows = []
    for k in range(int(48 * 60 / step_min)):   # settle a day, record the next
        t = (k * step_min / 60.0) % 24
        amb = 35 + 10 * math.sin(math.pi * (t - 9) / 12)
        sun = math.sin(math.pi * (t - 6) / 12)
        pv = max(0.0, sun) if 6 <= t <= 18 else 0.0
        load = min(0.35 + 0.80 * pv, 1.15)
        d_ou = d_or * ((1 + r * load ** 2) / (1 + r)) ** x
        d_hu = d_hr * load ** y
        d_o += (d_ou - d_o) * step_min / tau_o
        d_h += (d_hu - d_h) * min(step_min / tau_w, 1.0)
        if k >= int(24 * 60 / step_min):
            rows.append((t, load, amb, amb + d_o, amb + d_o + d_h))
    return rows
# [end: dynamic]


def dynamic() -> None:
    rows = hot_day()
    hs_max = max(r[4] for r in rows)
    t_max = max(rows, key=lambda r: r[4])[0]
    aged = sum(tr.ageing_rate(r[4]) for r in rows) * 5 / 60 / 24
    steady = max(tr.hot_spot(r[1], r[2]) for r in rows)
    csv("ch25-hotday.csv", "h,load,amb,top,hs",
        [(f"{a:.2f}", f"{b:.3f}", f"{c:.1f}", f"{d:.1f}", f"{e:.1f}") for a, b, c, d, e in rows[::3]])
    lines = ["a hot day of hybrid loading, dynamic thermal model (teaching):",
             "  load 0.35 pu at night (wind), up to 1.15 pu at noon (PV + wind);",
             "  air 25 C at dawn to 45 C in mid-afternoon",
             f"  hottest spot {hs_max:.0f} C at {t_max:.1f} h; steady state at each",
             f"  instant would say {steady:.0f} C",
             f"  life used in this day: {aged:.2f} days",
             "  the oil's three-hour time constant carries the noon peak",
             "  into the afternoon heat, but also smooths it: the dynamic",
             "  peak is below the steady one; still, this one day uses",
             "  about as much life as the whole year of lesson A - the",
             "  year is mostly cool nights and light loads, and a few such",
             "  days decide the ageing; the loading guide's model with the",
             "  maker's constants is what a real check uses"]
    emit("k_dynamic", lines)


def moisture() -> None:
    lines = ["ageing of paper with water in it (teaching factors on lesson A's year):",
             "  water in paper %   ageing x   life used per year days"]
    for w, k in ((0.5, 1.0), (1.0, 1.5), (2.0, 3.0), (3.0, 5.0)):
        lines.append(f"  {w:16.1f}   {k:8.1f}   {3.8 * k:23.1f}")
    lines += ["  dry paper ages several times slower than wet: drying in the",
              "  factory (lesson B), a sealed or breathing-dried conservator",
              "  and oil sampling for water keep it dry; the factors here",
              "  are teaching values - the loading guide gives the real",
              "  ones with oxygen and acidity"]
    emit("k_moisture", lines)


SAMPLES = [("T1 2027", dict(H2=40, CH4=20, C2H2=0, C2H4=10, C2H6=15, CO=250, CO2=2500)),
           ("T1 2029", dict(H2=420, CH4=60, C2H2=1, C2H4=15, C2H6=20, CO=300, CO2=2900)),
           ("T2 2029", dict(H2=60, CH4=180, C2H2=2, C2H4=260, C2H6=70, CO=320, CO2=3000)),
           ("T2 2030", dict(H2=200, CH4=120, C2H2=95, C2H4=150, C2H6=30, CO=340, CO2=3100)),
           ("T1 2031", dict(H2=70, CH4=40, C2H2=0, C2H4=20, C2H6=25, CO=900, CO2=4200))]


def key_gas(s: dict) -> str:
    """Teaching key-gas reading: the gas that stands out names the fault."""
    if s["C2H2"] > 20:
        return "arcing - act now"
    if s["C2H4"] > 150:
        return "hot spot > 300 C - investigate"
    if s["H2"] > 300 and s["CH4"] < 100:
        return "partial discharge - resample"
    if s["CO"] > 700:
        return "paper overheating - check"
    return "normal - keep trending"


def dga() -> None:
    lines = ["dissolved gases in the oil (ppm) read by the key gas (teaching):",
             "  sample     H2   CH4  C2H2  C2H4   CO   reading"]
    for name, s in SAMPLES:
        lines.append(f"  {name:8s} {s['H2']:5d} {s['CH4']:5d} {s['C2H2']:5d} {s['C2H4']:5d}"
                     f" {s['CO']:4d}   {key_gas(s)}")
    lines += ["  gases form when oil or paper is stressed: hydrogen from",
              "  discharges, ethylene from hot spots, acetylene only from",
              "  arcs, carbon oxides from paper; the trend between samples",
              "  matters more than one value, and the interpretation",
              "  methods and limits are the oil laboratory's and the",
              "  standards' - this rule only shows the idea"]
    emit("k_dga", lines)


def oltc() -> None:
    import random
    rnd = random.Random(25)
    tap_v, ops = 0.0, 0
    for h in range(8760):
        grid = 1.0 + 0.02 * math.sin(2 * math.pi * h / 24) + rnd.gauss(0, 0.008)
        load = 0.5 + 0.4 * math.sin(math.pi * ((h % 24) - 6) / 12) if 6 <= h % 24 <= 18 else 0.35
        v33 = grid - 0.045 * load + tap_v
        while abs(v33 - 1.0) > 0.0125 / 2 + 0.0025:
            step = 0.0125 if v33 < 1.0 else -0.0125
            tap_v += step
            v33 += step
            ops += 1
    lines = ["tap-changer operations over a year (synthetic hourly voltages):",
             f"  step 1.25 %, deadband +/- 0.875 %: {ops:,d} operations a year",
             f"  at a teaching 100,000 operations between diverter services:"
             f" every {100_000 / ops:.0f} years",
             "  the plant's own reactive control (ch 20) takes much of the",
             "  regulation: fewer tap changes, less wear; the count from",
             "  the tap changer's counter, not the calendar, schedules the",
             "  service (ch 52)"]
    emit("k_oltc", lines)


def expansion() -> None:
    beta, v = 7.5e-4, M["oil_m3"]
    lines = ["oil expansion and the conservator (teaching):",
             "  mean oil C   volume change m3 (from 20 C)"]
    for t in (-10, 20, 60, 100):
        lines.append(f"  {t:11d}   {beta * v * (t - 20):+29.2f}")
    span = beta * v * 110
    lines += [f"  swing -10 to 100 C: {span:.2f} m3; conservator about {span * 1.3:.1f} m3"
              " with margin",
              "  a sealed tank instead keeps a gas cushion that is squeezed",
              "  and expanded: its pressure swing sets the tank's design; the",
              "  conservator's breather (silica gel or a membrane) keeps the",
              "  water of the air out of the oil (lesson moisture above)"]
    emit("k_expansion", lines)


def radiators() -> None:
    lines = ["radiator area for the losses (teaching heat transfer):",
             "  mode     load MVA   losses kW   h W/(m2 K)   area m2 at 40 K"]
    for mode, s_mva, h in (("ONAN", M["s_onan_mva"], 6.0), ("ONAF", M["s_mva"], 12.0)):
        p = M["p0_kw"] + M["pk_kw"] * (s_mva / M["s_mva"]) ** 2
        lines.append(f"  {mode:6s} {s_mva:9.0f}   {p:9.0f}   {h:10.0f}   {p * 1e3 / (h * 40):15.0f}")
    lines += ["  the same radiators carry the full rating when fans double",
              "  the air-side heat transfer - the ONAN/ONAF pair of the",
              "  specification is one radiator bank with fans that switch",
              "  on with the oil temperature; the fans are an auxiliary",
              "  load (ch 23) and their failure an alarm with a load limit"]
    emit("k_radiators", lines)


def night() -> None:
    hours_low, p0, price = 2600, M["p0_kw"], 70.0
    saved = p0 * hours_low / 1e3
    lines = ["no-load loss at night: switch one transformer off? (teaching)",
             f"  hours a year with export below 10 MW: {hours_low:,d}",
             f"  one transformer's no-load loss {p0:.0f} kW -> {saved:.0f} MWh a year,"
             f" {saved * price / 1e3:.1f} k u",
             f"  cost: about {2 * 365:,d} switching operations and inrushes a year,",
             "  breaker wear, a transformer energised from cold each morning,",
             "  and the risk that it does not come back when the wind rises",
             "  a few k u a year rarely pays for that: most plants keep both",
             "  energised and buy the loss; where losses are dear and the",
             "  breaker is rated for it, an automatic scheme can be studied"]
    emit("k_night", lines)


def spare() -> None:
    lam, repair_h, lead_h = 0.015, 4380.0, 720.0
    energy, share_above, price = 295e3, 0.18, 70.0
    lost = 2 * lam * repair_h / 8760 * energy * share_above
    lost_sp = 2 * lam * lead_h / 8760 * energy * share_above
    gain = (lost - lost_sp) * price / 1e3
    lines = ["a spare main transformer: does it pay? (teaching)",
             f"  failure rate {lam} a year each; without spare 6 months out, with",
             "  a spare one month",
             f"  energy above one transformer's capacity: {share_above:.0%} of 295 GWh",
             f"  expected loss a year: {lost:,.0f} MWh without spare, {lost_sp:,.0f} MWh with",
             f"  value of the spare: {gain:.0f} k u a year against ~{M['s_mva'] * 30:,.0f} k u",
             f"  -> payback about {M['s_mva'] * 30 / gain:.0f} years: not for one plant;",
             "  a spare shared by several plants (or the utility's pool),",
             "  or a smaller mobile unit for the critical loads, are the",
             "  usual answers - with the transport route kept open (ch 18)"]
    emit("k_spare", lines)


if __name__ == "__main__":
    dynamic()
    moisture()
    dga()
    oltc()
    expansion()
    radiators()
    night()
    spare()
