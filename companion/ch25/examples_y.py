"""Chapter 25 - eleventh round: air insulation at the site's altitude,
room kept for the later battery (scenario S1), the battery unit
transformer's two daily cycles, load noise against core noise, and the
arc energy inside a tank against the clearing time.

Run from the project root:   python -m companion.ch25.examples_y
Writes companion/ch25/expected/y_*.txt and diagrams/data/ch25-besscycle.csv.
Teaching values (A-326..A-330 extended); site elevation 1,200 m from the
data pack (assumed).
"""
from __future__ import annotations

import math

from companion.ch25.common import csv, emit
from plantp import transformer as tr


def altitude() -> None:
    lines = ["air insulation at altitude: relative air density d = exp(-H / 8,150 m)",
             "  (barometric scale height); a withstand measured at sea level",
             "  falls roughly with d, so the item is chosen 1/d stronger",
             "  altitude m   air density   factor 1/d   650 kV item needs at sea level"]
    for h in (0, 1000, 1200, 2000):
        d = math.exp(-h / 8150)
        lines.append(f"  {h:10,d}   {d:11.3f}   {1 / d:10.3f}   {650 / d:24.0f} kV")
    lines += ["  Plant P sits at 1,200 m (data pack, assumed): external",
              "  insulation - bushings, post insulators, air clearances - is",
              "  about 14 % weaker than at sea level (so about 16 % more",
              "  strength is specified); the insulation",
              "  coordination study applies the standard's altitude",
              "  correction (its exponent depends on the voltage shape), and",
              "  the specification states the site altitude so the maker",
              "  tests or corrects for it; cooling by air is derated too",
              "  (lesson tower)"]
    emit("y_altitude", lines)


def future_bess() -> None:
    lines = ["room kept for the later battery (S0 now, S1 later; D-025):",
             "  item                         S0 build          kept for S1"]
    rows = [("33 kV bays", "WS1-3, PVF1-3", "BESS-A, BESS-B (spare bays)"),
            ("bus sections", "split bus", "a battery feeder on each"),
            ("main transformers", "2 x 63 MVA", "no change (below)"),
            ("site area", "fenced plot", "platform for 4 containers"),
            ("earthing", "station grid", "grid extended to the plot"),
            ("auxiliary supply", "SST 250 kVA", "HVAC supply (below)"),
            ("control", "PPC, SCADA", "points reserved")]
    for a, b, c in rows:
        lines.append(f"  {a:28s} {b:17s} {c}")
    lines += ["  the main transformers need no change: export stays capped at",
              "  100 MW at the POC, and a battery charging from PV inside the",
              "  plant does not pass through them; charging from the grid",
              "  imports at most 20 MW - far below their rating",
              "  the auxiliary supply does change: 8 containers x 40 kW of",
              "  HVAC (120 kW of cooling at COP 3, ch 19) = 320 kW, more than",
              "  the 250 kVA station transformer - fed from the PCS skids or",
              "  a second station transformer (decided with the battery",
              "  supplier); a reserved bay and space cost little now and",
              "  much later"]
    emit("y_future", lines)


def bess_cycle() -> None:
    step = 5.0
    d_or, d_hr, r, x, y = 52.0, 26.0, 6.0, 0.8, 1.6
    tau_o, tau_w = 180.0, 7.0
    d_o, d_h, rows = 10.0, 0.0, []
    for k in range(int(48 * 60 / step)):
        t = (k * step / 60.0) % 24
        amb = 35 + 10 * math.sin(math.pi * (t - 9) / 12)
        load = 0.95 if (11 <= t < 13 or 19 <= t < 21) else 0.03
        d_o += (d_or * ((1 + r * load ** 2) / (1 + r)) ** x - d_o) * step / tau_o
        d_h += (d_hr * load ** y - d_h) * min(step / tau_w, 1.0)
        if k >= 24 * 60 / step:
            rows.append((t, load, amb + d_o + d_h))
    csv("ch25-besscycle.csv", "h,load,hs", [(f"{a:.2f}", f"{b:.2f}", f"{c:.1f}") for a, b, c in rows[::2]])
    hs_max = max(c for _, _, c in rows)
    aged = sum(tr.ageing_rate(c) for _, _, c in rows) * step / 60 / 24
    steady = tr.hot_spot(0.95, 45.0)
    lines = ["the battery unit transformer on a hot day: charge 11-13 h at",
             "  0.95 pu, discharge 19-21 h at 0.95 pu, idle otherwise",
             f"  hottest spot {hs_max:.0f} C; a steady 0.95 pu at 45 C would give {steady:.0f} C",
             f"  life used in this day: {aged:.2f} days",
             "  two hours at full load do not heat the oil to its steady",
             "  value (time constant three hours): the cyclic battery duty",
             "  ages the unit far less than its rating suggests - but the",
             "  winding follows within minutes, so the hot-spot gradient",
             "  and the gas relay's view of each cycle still matter; the",
             "  maker's dynamic rating may allow a smaller unit"]
    emit("y_besscycle", lines)


def load_noise() -> None:
    l_nl, l_ld = 72.0, 68.0
    lines = ["load noise against core noise (sound power, teaching):",
             "  core (no-load) 72 dB(A) at any load; winding (load) noise",
             "  68 dB(A) at rated current, changing as 40 log10(I / In)",
             "  load pu   load noise   total dB(A)"]
    for k in (0.35, 0.6, 0.8, 1.0, 1.15):
        ld = l_ld + 40 * math.log10(k)
        lines.append(f"  {k:7.2f}   {ld:10.1f}   {tr.sound_sum([l_nl, ld]):11.1f}")
    lines += ["  at night (wind only, about 0.35 pu) the core sets the level;",
              "  at rated load the windings add 1.5 dB, at 1.15 pu 2.3 dB - the night",
              "  limit is met by the core's design (flux density, steel,",
              "  joints), the day limit by both; the guarantee covers both",
              "  parts, measured in the factory"]
    emit("y_loadnoise", lines)


def arc_energy() -> None:
    i_f = 6.4e3                     # 33 kV fault, one transformer (ch 26)
    lines = ["energy of an internal arc in a unit transformer tank (teaching):",
             "  E = U_arc x I x t; arc voltage taken as 2 kV (assumed)",
             "  clearing by                          time ms   current kA   energy kJ"]
    for name, t, i in (("current-limiting fuse", 5.0, 3.0), ("breaker, instantaneous", 80.0, 6.4),
                       ("breaker, time-graded", 400.0, 6.4)):
        e = 2e3 * i * 1e3 * t / 1e3 / 1e3
        lines.append(f"  {name:36s} {t:7.0f}   {i:10.1f}   {e:9.0f}")
    lines += [f"  fault level {i_f / 1e3:.1f} kA at the 33 kV bus; the energy grows with",
              "  the clearing time: a fuse that limits both current and time",
              "  keeps the gas pressure in the tank low; an instantaneous",
              "  breaker lets 34 times that energy in, a time-graded relay",
              "  170 times - tank strength, pressure relief",
              "  and clearing time are chosen together (ch 26 settings,",
              "  fire interfaces of lesson F)"]
    assert round(1024 / 30) == 34 and round(5120 / 30) == 171
    emit("y_arc", lines)


if __name__ == "__main__":
    altitude()
    future_bess()
    bess_cycle()
    load_noise()
    arc_energy()
