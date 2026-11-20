"""Chapter 24 - second round of circuit hardware: fuse selectivity by I^2t,
the UPS that cannot clear a fault without its bypass, the standby
generator's falling fault current, series contacts of a 1,500 V DC
isolator, air- against gas-insulated 132 kV bays, the line's sag when the
conductor is hot, wind on the conductor, the earth wire's fault duty, a
route chosen with its crossings, and the time to repair a cable fault.

Run from the project root:   python -m companion.ch24.examples_q
Writes companion/ch24/expected/q_*.txt. Teaching values (A-321..A-325
extended): makers' curves, the line standard and the route survey decide.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as src
from companion.ch24.common import emit


def fuses() -> None:
    pairs = [("63 A upstream, 25 A downstream", 25, 1_400, 63, 9_500),
             ("63 A upstream, 40 A downstream", 40, 4_200, 63, 9_500),
             ("100 A (make X) up, 63 A (make Y) down", 63, 11_000, 100, 10_500)]
    lines = ["fuse selectivity by energy (teaching I2t values, A2s):",
             "  pair                                   down total  up pre-arc  selective"]
    for name, _, down_total, _, up_pre in pairs:
        ok = down_total < up_pre
        lines.append(f"  {name:37s} {down_total:11,d}  {up_pre:10,d}  {'yes' if ok else 'NO'}")
    lines += ["  the small fuse must clear (its total I2t) before the large",
              "  one starts to melt (its pre-arcing I2t); a size ratio of",
              "  about 1.6 often works, but the makers' tables decide - the",
              "  100/63 pair of two makes fails at that very ratio"]
    emit("q_fuses", lines)


def ups() -> None:
    s, v = 25e3, 400.0
    i_r = s / (math.sqrt(3) * v)
    i_lim = 2.0 * i_r
    lines = ["a fault on a UPS output circuit (25 kVA UPS, teaching):",
             f"  rated current {i_r:.0f} A; inverter current limit ~2 x = {i_lim:.0f} A"
             " for about 100 ms",
             "  breaker         instant trip needs   inverter gives   result"]
    for name, i_n, mult in (("type B 10 A", 10, 5), ("type C 10 A", 10, 10), ("type C 16 A", 16, 10)):
        need = i_n * mult
        lines.append(f"  {name:15s} {need:16.0f} A   {i_lim:12.0f} A   "
                     f"{'trips' if i_lim >= need else 'may not trip'}")
    lines += ["  the inverter cannot push enough current to trip anything but",
              "  the smallest breakers; the static bypass connects the mains",
              "  for the fault and the breaker clears from the mains - so the",
              "  bypass supply, its fault level and its availability are part",
              "  of the UPS circuit's protection design (ch 23 lesson F)"]
    emit("q_ups", lines)


def generator() -> None:
    s, v, xs, xt, xd = 150e3, 400.0, 0.12, 0.25, 2.0
    i_r = s / (math.sqrt(3) * v)
    lines = ["fault current of the 150 kVA standby generator (teaching reactances):",
             f"  rated {i_r:.0f} A; x''d {xs}, x'd {xt}, xd {xd} (pu)",
             "  time after fault     current A    x rated"]
    for name, x in (("first cycles (x''d)", xs), ("0.1-1 s (x'd)", xt), ("steady (xd)", xd)):
        lines.append(f"  {name:20s} {i_r / x:10.0f}   {1 / x:7.1f}")
    boost = 3.0 * i_r
    lines += [f"  with a field-boost system holding ~3 x: {boost:.0f} A steady",
              "  without boost the steady current falls below the rating of",
              "  the main breaker's instantaneous trip: a fault far out may",
              "  not be cleared - the generator's breaker needs settings for",
              "  its own decrement curve, and the island's protection is",
              "  checked with the generator, not with the transformer"]
    emit("q_generator", lines)


def dc_isolator() -> None:
    lines = ["a 1,500 V DC string isolator: contacts in series (teaching):",
             "  arc voltage per contact gap V   gaps needed   poles x gaps"]
    for v_gap in (250, 300, 400):
        n = math.ceil(1500 * 1.2 / v_gap)
        lines.append(f"  {v_gap:29d}   {n:11d}   {math.ceil(n / 2)} x 2")
    lines += ["  a DC arc does not stop at a zero crossing: the switch must",
              "  build an arc voltage above the source voltage, so it puts",
              "  several gaps in series (both poles) and uses magnets or",
              "  arc chutes; the DC rating at the string's coldest voltage",
              "  (ch 10) is the one that counts, not an AC rating"]
    emit("q_dcisolator", lines)


def ais_gis() -> None:
    opts = [("air-insulated (AIS)", 1.00, 1.00, 12.0, 0.0),
            ("gas-insulated (GIS)", 0.25, 1.45, 4.0, 1.0),
            ("hybrid (gas breaker, air bus)", 0.55, 1.20, 6.0, 0.4)]
    lines = ["a 132 kV bay: air, gas or hybrid (indices against AIS, teaching):",
             "  option                         area   cost   outage h/maint   SF6 index"]
    lines += [f"  {a:30s} {b:5.2f}   {c:4.2f}   {d:14.1f}   {e:9.1f}" for a, b, c, d, e in opts]
    lines += ["  gas insulation buys space and shorter outages for money and",
              "  gas; air is cheap where land is cheap - at Plant P's open",
              "  site AIS is the teaching basis (D-029), GIS where a town or",
              "  pollution presses; SF6-free gas bays change the last column"]
    emit("q_aisgis", lines)


def sag_temp() -> None:
    span, w, t0, alpha = 300.0, 11.0, 19_000.0, 19e-6
    sag0 = w * span ** 2 / (8 * t0)
    length0 = span + 8 * sag0 ** 2 / (3 * span)
    lines = ["sag of a 300 m span as the conductor heats (elongation only):",
             f"  at 15 C: sag {sag0:.2f} m (tension 19 kN)",
             "  conductor C   length m   sag m   clearance lost m"]
    for t in (15, 50, 75, 90):
        length = length0 * (1 + alpha * (t - 15))
        sag = math.sqrt(3 * span * (length - span) / 8)
        lines.append(f"  {t:11d}   {length:8.3f}   {sag:5.2f}   {max(sag - sag0, 0):16.2f}")
    lines += ["  a few centimetres more conductor in a 300 m span drops the",
              "  low point by metres: the clearance is checked at the",
              "  highest design temperature (and with ice where it falls),",
              "  and the elastic stretch, ignored here, reduces it a",
              "  little - the line designer's state-change calculation"]
    emit("q_sag", lines)


def wind_load() -> None:
    d, w = 0.0245, src.LINE["weight_n_m"]
    lines = ["wind on the conductor: q = 0.5 rho v^2 Cd d (Cd 1.0, teaching):",
             "  wind m/s   wind N/m   weight N/m   resultant N/m   swing deg"]
    for v in (20, 30, 40):
        q = 0.5 * 1.225 * v ** 2 * d
        r = math.hypot(q, w)
        lines.append(f"  {v:8d}   {q:8.1f}   {w:10.1f}   {r:13.1f}   {math.degrees(math.atan2(q, w)):9.0f}")
    lines += ["  a storm adds a sideways load as large as the weight: the",
              "  tension rises, the conductor swings toward the tower and",
              "  its neighbour - clearances are checked in the swung",
              "  position, and the towers take the sum (ch 29 foundations)"]
    emit("q_wind", lines)


def opgw() -> None:
    lines = ["earth wire with optical fibres (OPGW): fault duty (teaching):",
             "  the share of a 132 kV earth fault the earth wire carries",
             "  share kA   time s   I2t kA2s   rated 100 kA2s"]
    for ik, t in ((5.2 * 0.6, 0.5), (5.2 * 0.6, 1.0), (31.5 * 0.3, 0.5)):
        i2t = ik ** 2 * t
        lines.append(f"  {ik:8.1f}   {t:6.1f}   {i2t:8.1f}   {'ok' if i2t <= 100 else 'OVER'}")
    lines += ["  the earth wire carries fault current back and the fibres for",
              "  protection and SCADA inside it: if it overheats, the fibres",
              "  of the line differential (ch 26) go with it; the rating",
              "  must cover the switchgear rating, not today's fault level"]
    emit("q_opgw", lines)


def route() -> None:
    routes = [("A: along the road", 7.06, 3, 1, 1.00), ("B: straight, cross-country", 6.10, 6, 2, 1.25),
              ("C: around the wetland", 8.40, 2, 0, 0.95)]
    lines = ["choosing the export route (teaching costs, k u):",
             "  route                        km   crossings  sensitive  build k u"]
    for name, km, cross, sens, terrain in routes:
        cost = km * 450 * terrain + cross * 60 + sens * 250
        lines.append(f"  {name:27s} {km:5.2f}   {cross:9d}  {sens:9d}  {cost:9,.0f}")
    lines += ["  the shortest route is not the cheapest: crossings (roads,",
              "  pipes, rivers) and sensitive areas (permits, mitigation)",
              "  cost more than the kilometres they save; access for repair",
              "  and the landowners (ch 14, ch 22) weigh as much as the sum"]
    emit("q_route", lines)


def repair() -> None:
    steps = [("locate the fault (time-domain reflection, pinpointing)", 12),
             ("permits, isolation and earthing (owner's rules)", 8),
             ("excavate and expose", 16),
             ("cut, joint (two joints with a cable insert)", 24),
             ("test and re-energise", 8)]
    total = sum(h for _, h in steps)
    lines = ["repair of a 33 kV cable fault (teaching hours, spares on site):"]
    lines += [f"  {a:55s} {h:4d} h" for a, h in steps]
    lines += [f"  total about {total} h ({total / 24:.1f} days) if the jointing kit and a",
              "  cable length are in the store; add weeks if they must be",
              "  ordered - the spares list (ch 18) is a repair-time decision;",
              f"  a wind string loses about {4 * 5 * total * 0.36:.0f} MWh in that time"
              " (at its",
              "  average capacity factor 0.36)"]
    emit("q_repair", lines)


if __name__ == "__main__":
    fuses()
    ups()
    generator()
    dc_isolator()
    ais_gis()
    sag_temp()
    wind_load()
    opgw()
    route()
    repair()
