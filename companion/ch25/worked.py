"""Chapter 25 - numerical answers of the small examples (E..) and of the
end-of-chapter problems (P..), each computed here.

Run from the project root:   python -m companion.ch25.worked
Writes companion/ch25/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch25.common import emit
from plantp import transformer as tr


def worked() -> None:
    e = tr.from_tests(63000, 132, 35, 0.2, 250, 12)
    lines = [f"E01 volts per turn, 1.7 T, 0.45 m2: {tr.volts_per_turn(1.7, 0.45):.1f} V",
             f"E02 r and x of 63 MVA, Pk 250 kW, uk 12 %: {e['r']:.5f}, {e['x']:.5f} pu",
             f"E03 regulation at full load, pf 0.95: {tr.regulation_pct(e['r'], e['x'], 1, 0.95):.2f} %",
             f"E04 efficiency at 0.37 load, pf 1: {tr.efficiency(0.37, 63000, 1, 35, 250) * 100:.3f} %",
             f"E05 hot spot at k 1.0, 30 C: {tr.hot_spot(1.0, 30):.0f} C; ageing {tr.ageing_rate(tr.hot_spot(1.0, 30)):.2f}",
             f"E06 fault current through 63 MVA, z 0.12, at 33 kV: {tr.sc_current_ka(63, 33, 0.12):.2f} kA"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 turns for 19,053 V at 150 V/turn: {19053 / 150:.0f}",
           f"P02 V/turn at 1.6 T, 0.40 m2: {tr.volts_per_turn(1.6, 0.40):.1f} V",
           f"P03 section for 636 A at 2.5 A/mm2: {tr.conductor_mm2(636, 2.5):.0f} mm2",
           f"P04 r of 40 MVA, Pk 200 kW: {200 / 40000:.4f} pu",
           f"P05 x for uk 10 %, r 0.005: {math.sqrt(0.1 ** 2 - 0.005 ** 2):.5f} pu",
           f"P06 regulation r 0.005, x 0.10, full load, pf 0.9: {tr.regulation_pct(0.005, 0.10, 1, 0.9):.2f} %",
           f"P07 efficiency 63 MVA at half load, pf 0.95: {tr.efficiency(0.5, 63000, 0.95, 35, 250) * 100:.3f} %",
           f"P08 load of best efficiency, P0 28, Pk 215: {math.sqrt(28 / 215):.2f} pu"]
    a, b = tr.ab_factors(70, 25, 0.075, 0.128)
    out.append(f"P09 A and B at 70 u/MWh, 25 y, 7.5 %, LLF 0.128: {a:.2f}, {b:.2f} k u/kW")
    out.append(f"P10 loss PV of 40 kW P0 and 300 kW Pk: {tr.loss_cost(40, 300, a, b):.0f} k u")
    a2, b2 = tr.ab_factors(100, 25, 0.075, 0.128)
    out.append(f"P11 same at 100 u/MWh: {tr.loss_cost(40, 300, a2, b2):.0f} k u")
    out.append(f"P12 hot spot at k 0.8, 35 C: {tr.hot_spot(0.8, 35):.1f} C")
    out.append(f"P13 ageing rate at 110 C: {tr.ageing_rate(110):.1f}")
    out.append(f"P14 ageing rate at 86 C: {tr.ageing_rate(86):.2f}")
    s = tr.share(90, [63, 63], [0.12, 0.14])
    out.append(f"P15 90 MVA on 63 MVA units of 12 % and 14 %: {s[0]:.1f}, {s[1]:.1f} MVA")
    out.append(f"P16 fault current through 40 MVA, z 0.10, at 33 kV: {tr.sc_current_ka(40, 33, 0.10):.2f} kA")
    out.append(f"P17 force ratio at z 0.08: {tr.force_ratio(0.08):.0f}")
    out.append(f"P18 three sources of 70 dB: {tr.sound_sum([70, 70, 70]):.1f} dB")
    out.append(f"P19 75 dB at 2 m, at 100 m: {tr.sound_at(75, 2, 100):.1f} dB")
    out.append(f"P20 bund for 30 m3 oil, 60 mm rain on 80 m2: {tr.bund_m3(30, 60, 80):.1f} m3")
    out.append(f"P21 tap +5 % on 132 kV: {132 * 1.05:.1f} kV")
    out.append(f"P22 rated current of 63 MVA at 132 kV: {63e6 / (math.sqrt(3) * 132e3):.0f} A")
    out.append(f"P23 LV delta winding current, 63 MVA, 33 kV: {63e6 / (3 * 33e3):.0f} A")
    out.append(f"P24 ONAN hours: load above 50 MVA as pu of 63: {50 / 63:.3f} pu threshold")
    emit("solutions", out)


def solutions2() -> None:
    """Checks of the short answers added with the later lessons."""
    from companion.ch25.examples_v import dp_from_furan, star
    from companion.ch25.examples_w import top_oil_day  # noqa: F401
    w = 2 * math.pi * 50
    out = [f"P25 circulating, 3 steps, 10 % each: {0.0375 / 0.20:.2%}",
           f"P26 unit for 4.4 MW to pf 0.9: {4.4 / 0.9:.2f} MVA",
           f"P27 amorphous, 12 units 7.0 -> 2.2 kW: {12 * 4.8 * 6.84:.0f} k u",
           f"P28 air for 40 kW, 10 K rise: {40e3 / (1.2 * 1005 * 10):.2f} m3/s",
           f"P29 loss error, pf 0.05, 0.3 mrad: {math.tan(math.acos(0.05)) * 3e-4:.2%}",
           f"P30 time to 99 % with tau 2.67 h: {2.67 * math.log(100):.1f} h",
           f"P31 ageing H 1.2 vs 1.1: {2 ** (2 / 6):.2f}",
           f"P32 Q of each T at 80 MW, pf 0.95: {0.12 * (80 / 0.95 / 2) ** 2 / 63:.2f} Mvar",
           f"P33 no-load limit 4.5 kW +15 %: {4.5 * 1.15:.2f} kW",
           f"P34 3 months late, 12 % share: {295e3 * 0.12 * 3 / 12:,.0f} MWh",
           f"P35 two 40 dB(A) sources: {tr.sound_sum([40, 40]):.1f} dB(A)",
           f"P36 copper for 200 kW at 3.5 A/mm2: "
           f"{200e3 / (2.1e-8 * 3.5e6 ** 2) * 8.9:.1f} t",
           f"P37 water from 6 t paper, 7 -> 0.5 %: {6000 * 0.065:.0f} kg",
           f"P38 vacuum force on 5 x 3 m: {101.3 * 15:,.0f} kN",
           f"P39 12 wind units, LLF 0.25: {12 * 50 * 0.25 * 8.76:,.0f} MWh",
           f"P40 5 % and 1 % of a 600/1 CT: {0.05 * 600:.0f} A, {0.01 * 600:.0f} A"]
    z = star(0.07, 0.07, 0.12)
    out += [f"P41 star of 7/7/12 %: {z[0]:.1%}, {z[1]:.1%}, {z[2]:.1%}",
            f"P42 5th residual, second group at 75 %: {2 - 1.5:.1f} %",
            f"P43 DP at 0.1 mg/kg 2-FAL: {dp_from_furan(0.1):.0f}",
            f"P44 T1 health index with DGA score 4: {100 * (4 - 1.9) / 3:.0f}",
            f"P45 12-month repair: {900 + 12 * 310:,.0f} k u",
            f"P46 carbon of losses at 0.3 t/MWh over materials: "
            f"{1174 / 2 * 25 * 0.3 / 204:.0f} x",
            f"P47 20 % advance 24 months before COD: {340 * (1.06 ** 2 - 1):.1f} k u",
            f"P48 deflection of a 9 m span (10 m: 44 mm): {44 * 0.9 ** 4:.0f} mm",
            f"P49 dip, worst case, 10.4 kA: {2086 / math.sqrt(2) / 10.4e3:.0%}",
            f"P50 Q of 10 km of 33 kV cable, 0.21 uF/km: "
            f"{33e3 ** 2 * w * 2.1e-6 / 1e6:.2f} Mvar",
            f"P51 LV tower cable loss at 130 m: {45.7 * 130 / 110:.0f} kW",
            f"P52 gas pressure expected at 20 C: "
            f"{1.263 * 293.15 / 303.15 - 1.013:.3f} bar(g)",
            f"P53 maintenance PV at 6 %, 25 y: "
            f"{8 * (1 - 1.06 ** -25) / 0.06:.0f} k u"]
    from companion.ch25.examples_z import load_loss_at
    out += [f"P54 air density at 1,800 m: {math.exp(-1800 / 8150):.2f}",
            f"P55 noise at 0.8 pu (72 core, 68 load): "
            f"{tr.sound_sum([72, 68 + 40 * math.log10(0.8)]):.1f} dB(A)",
            f"P56 arc energy, 150 ms, 6.4 kA, 2 kV: {2e3 * 6.4e3 * 0.15 / 1e6:.2f} MJ",
            f"P57 oil share of the way in 4 h, tau 3 h: {1 - math.exp(-4 / 3):.2f}",
            f"P58 reference loss measured at 30 C: "
            f"{load_loss_at(75, 30, 155, 72):.1f} kW",
            f"P59 fault level at uk 11.0 %: {63 / (math.sqrt(3) * 33 * 0.11):.2f} kA",
            f"P60 breather water at 6.9 g/m3: {0.41 * 6.9 * 365 / 1e3:.2f} kg",
            f"P61 break-even pool fee at rate 0.01: "
            f"{2 * 0.01 * (3380 - 1515):.0f} k u",
            f"P62 mild-day fan failure: residual alarm 11.75 h, fixed 13.42 h:"
            f" lead {13.42 - 11.75:.2f} h"]
    emit("solutions2", out)


if __name__ == "__main__":
    worked()
    solutions()
    solutions2()
