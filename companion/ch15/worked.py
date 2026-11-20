"""Chapter 15 - small worked calculations quoted in the text (E01 ...) and
numerical answers to the end-of-chapter problems (P01 ...).

Run from the project root:   python -m companion.ch15.worked
Writes companion/ch15/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch15.common import emit
from plantp import yieldmodel as ym

E: list[str] = []
P: list[str] = []


def e(i, t):
    E.append(f"{i}: {t}")


def p(i, t):
    P.append(f"{i}: {t}")


def worked() -> None:
    e("E01", f"10 MW for 6 h and 30 MW for 2 h: {10 * 6 + 30 * 2} MWh")
    e("E02", f"losses 10 % then 20 %: 1 - 0.9 x 0.8 = {1 - 0.9 * 0.8:.2f} (not 0.30)")
    e("E03", f"capacity factor of 295.14 GWh at 100 MW: {295.14e3 / (100 * 8760):.3f}")
    e("E04", f"density 1.046 against 1.225 kg/m3: {100 * (1.046 / 1.225 - 1):+.1f} % in region 2")
    e("E05", f"inverter 98.3 % on 115.74 GWh DC: {115.74 * 0.983:.2f} GWh")
    e("E06", f"clipping: 51.55 MW AC limited to 49.0 MW: {51.55 - 49.0:.2f} MW lost")
    e("E07", f"load loss 1.5 % at 100 MW scaled to 60 MW: {1.5 * 0.6 ** 2:.2f} % of 100 MW ="
             f" {1.5 * 0.36:.2f} MW")
    e("E08", f"degradation 0.5 %/yr, year 10: x {1 - 0.005 * 10:.3f}")
    e("E09", f"25-year mean factor at 0.5 %/yr: {sum(1 - 0.005 * y for y in range(1, 26)) / 25:.4f}")
    e("E10", f"persistence error, observed 40 then 55 MW: {55 - 40} MW")
    e("E11", f"RMSE of errors 3, -4, 5 MW: {math.sqrt((9 + 16 + 25) / 3):.2f} MW")
    e("E12", f"skill of RMSE 8.3 against 23.8: {ym.skill(8.3, 23.8):.2f}")
    e("E13", f"pinball, tau 0.1, forecast 40, observed 30: {ym.pinball([40], [30], 0.1):.1f}")
    e("E14", f"newsvendor quantile: (50 - 25) / (100 - 25) = {(50 - 25) / (100 - 25):.3f}")
    e("E15", f"water 0.5 L/m2 x 281,000 m2: {0.5 * 281_000 / 1e3:.0f} m3 per cleaning")
    e("E16", f"one 32 MWh battery over a 10.7 MW RMSE for 24 h: {32 / (10.7 * 24):.2f} of the"
             " error energy")
    emit("worked", E)


def solutions() -> None:
    p("P01", f"25 MW for 4 h + 40 MW for 3 h: {25 * 4 + 40 * 3} MWh")
    p("P02", f"losses 2, 3 and 5 %: {100 * (1 - 0.98 * 0.97 * 0.95):.2f} % (sum 10 %)")
    p("P03", f"capacity factor of 196.9 GWh at 60 MW: {196.9e3 / (60 * 8760):.3f}")
    p("P04", f"PV 108.36 GWh at 50 MW AC: {108.36e3 / (50 * 8760):.3f}")
    p("P05", f"density 1.10 against 1.225: {100 * (1.10 / 1.225 - 1):+.1f} % (region 2)")
    p("P06", f"inverter 98.0 % on 100 GWh DC: {100 * 0.98:.1f} GWh")
    p("P07", f"load loss 1.5 % at 100 MW, at 80 MW: {1.5 * 0.8 ** 2:.2f} MW")
    p("P08", f"degradation 0.6 %/yr, year 20: x {1 - 0.006 * 20:.2f}")
    p("P09", f"25-year mean at 0.6 %/yr: x {sum(1 - 0.006 * y for y in range(1, 26)) / 25:.3f}")
    p("P10", f"RMSE of errors 2, -2, 6, -6 MW: {math.sqrt((4 + 4 + 36 + 36) / 4):.2f} MW")
    p("P11", f"MAE of the same: {(2 + 2 + 6 + 6) / 4:.1f} MW")
    p("P12", f"skill of 9.7 % against 23.7 %: {ym.skill(9.7, 23.7):.2f}")
    p("P13", f"pinball tau 0.9, forecast 50, observed 60: {ym.pinball([50], [60], 0.9):.1f}")
    p("P14", f"newsvendor quantile, price 40, short 120, surplus 20:"
             f" {(40 - 20) / (120 - 20):.2f}")
    p("P15", f"coverage of 16 of 20 observations: {16 / 20:.2f}")
    p("P16", f"truck cleaning water 1.0 L per module, 109,200 modules: {109.2:.1f} m3")
    p("P17", f"round trip 86 %: one-way {math.sqrt(0.86):.3f}")
    p("P18", f"12 outage hours at 34 MW average: {12 * 34} MWh")
    p("P19", "monthly net: May 30.93, Jun 18.92 GWh (d_balance)")
    p("P20", "wind waterfall: density -8.53 %, wakes -4.01 %, long term +2.77 %")
    p("P21", "PV: IAM, temperature, low light -7.61 %; DC -3.00 %; inverter -1.66 %")
    p("P22", "plant: electrical -1.09, own use -0.79, limit -0.08, outages -0.17 %")
    p("P23", "totals: wind 11.73 % (sum 11.95), PV 16.10 % (sum 17.16)")
    p("P24", "availability as hours: curtailment 313 against 227 MWh")
    p("P25", "soiling seasonal 1.59 % against constant 1.50 %")
    p("P26", "one turbine: ten-minute 18,166, hourly 18,184 MWh (+0.10 %)")
    p("P27", "PV 1 h late: curtailment 411 against 426 MWh; correlation -0.126")
    p("P28", "clipping: DC/AC 1.1 0.02 %, 1.2 0.69 %, 1.3 2.71 %, 1.4 5.43 %")
    p("P29", "soiling on DC before clipping: +0.25 GWh (+0.22 %)")
    p("P30", "25-year mean PV 101.82 GWh (-6.5 % against year 0)")
    p("P31", "S1 battery on curtailment: 227 MWh stored, 195 released")
    p("P32", "outage energy: mean 401 MWh, 10-90 % 286 .. 516 MWh")
    p("P33", "RMSE % by lead, weather-driven: 1 h 7.1, 6 h 7.8, 24 h 9.7, 36 h 12.1")
    p("P34", "day-ahead RMSE: wind 17.4 %, PV daylight 8.6 %, hybrid 9.7 %")
    p("P35", "coverage: fair 78.7 %, leak 80.0 %, by level 79.0 %")
    p("P36", "leak: last-hour feature 7.20 / 7.59 MW against 10.38 MW")
    p("P37", "ramps day-ahead: POD 0.43, FAR 0.67; persistence POD 0.10")
    p("P38", "cleaning: no cleaning 9.47 %, trigger 1.52 %, robot 1.29 %")
    p("P39", "trigger: mean 1.43 %, energy-weighted 1.52 %")
    p("P40", "dispatch P50 short 10,872 MWh; P30 + battery 4,418 MWh")
    p("P41", f"value of 0.25 GWh at 50 u/MWh: {0.25e3 * 50:,.0f} u a year")
    p("P42", f"PV 1.66 % inverter loss on 115.74 GWh: {115.74 * 0.0166:.2f} GWh")
    p("P43", f"revenue difference P30 + B and P50: {4607 - 4342} k u over four months")
    p("P44", f"net 295.14 GWh with 1 % more availability on wind: +{193.14 / 0.981 * 0.01:.2f} GWh")
    p("P45", "curtailment at a 90 MW limit (model run): 1,757 MWh in 225 h")
    p("P46", f"trigger policy cost 229 k u for 8,992 MWh: {229e3 / 8992:.1f} u per MWh recovered")
    k = (3.36 / 6.74) ** -1.086
    p("P47", f"Justus fit, mean 6.74 m/s, sd 3.36 m/s: k = {k:.2f}")
    p("P48", f"scale c = 6.74 / Gamma(1 + 1/{k:.2f}) = {6.74 / math.gamma(1 + 1 / k):.2f} m/s")
    p("P49", f"PR = 1,804.2 kWh/kWp / 2,150.3 h = {1804.2 / 2150.3:.3f}")
    p("P50", f"PR 0.807 at T_c,w 50.7 C, gamma -0.35 %/K: {0.807 / (1 - 0.0035 * 25.7):.3f} at 25 C")
    p("P51", f"NOCT model, T_a 35 C, 1,000 W/m2, NOCT 45 C: {35 + 25 / 800 * 1000:.1f} C")
    p("P52", f"electrical loss at 60 MW: 0.10 + 1.5 % x 100 x 0.6^2 = {0.10 + 1.5 * 0.36:.2f} MW")
    p("P53", f"load loss at pf 0.90: x {1 / 0.9 ** 2:.3f} ({100 * (1 / 0.81 - 1):+.1f} %)")
    sw, sp = 8.69, 2.93
    for r in (0.12, 0.0, 1.0):
        p("P54" if r == 0.12 else ("P54a" if r == 0 else "P54b"),
          f"sd of the hybrid, r = {r:.2f}: {math.sqrt(sw ** 2 + sp ** 2 + 2 * r * sw * sp):.2f} GWh"
          f" ({100 * math.sqrt(sw ** 2 + sp ** 2 + 2 * r * sw * sp) / 301.5:.2f} %)")
    p("P55", f"marginal share 50 -> 60 MW PV: {(315.63 - 295.63) / (0.2 * 108.36):.3f}")
    p("P56", f"mean curtailment over the average-year value: {287 / 227:.2f}")
    p("P57", f"flat rank histogram: 20 members {100 / 21:.2f} %, 50 members {100 / 51:.2f} %")
    p("P58", f"blend, w 0.5, NWP 40 MW, persistence 50 MW: {0.5 * 40 + 0.5 * 50:.0f} MW")
    p("P59", f"intraday: shortfall {100 * (1 - 6371 / 8348):.0f} % less, surplus"
             f" {100 * (1 - 10228 / 13882):.0f} % less")
    p("P60", f"one turbine of 12 at -4 %: farm {100 * 0.04 / 12:.2f} % low")
    p("P61", f"151 MWh imported at 3 x 50 u/MWh: {151 * 150:,} u")
    p("P62", f"grid limit: 485 MWh in 90 h: {485 / 90:.1f} MW mean cut")
    p("P63", f"icing 95.5 MWh of 16,678 MWh: {100 * 95.5 / 16678:.2f} %")
    p("P64", f"wake k 0.04 against 0.075: {0.0089 * 199.56:.2f} GWh")
    p("P65", f"unflagged outages: 3 % x 2/3 x 34.4 MW = {0.03 * 2 / 3 * 34.4:.2f} MW bias")
    p("P66", f"best learned correction: {100 * (1 - 10.26 / 10.72):.1f} % lower RMSE")
    p("P67", f"one PV block of ten out 20 of 31 days: about {1 - 0.1 * 20 / 31:.3f} in March")
    p("P68", f"isotropic sky: 2,107 / 2,150 = {2107 / 2150:.3f}")
    p("P69", f"bat rule: 750 h x 3.0 MW = {750 * 3.0:,.0f} MWh")
    p("P70", f"time 98.09 % against energy 97.49 % on 193.14 GWh: {0.0060 * 193.14:.2f} GWh")
    p("P71", f"battery 40 MWh returning 2,734 MWh: {2734 / 40:.0f} full cycles")
    p("P72", f"CRPS 4.55 MW against MAE 6.06 MW: {4.55 / 6.06:.2f}")
    p("P73", f"wind long-term factor 3 % of 193.14 GWh: {0.03 * 193.14:.2f} GWh at MV")
    p("P74", f"monthly wind 189.25 against hourly 193.14 GWh: {189.25 / 193.14:.3f}")
    p("P75", f"noise mode, 3 of 12 turbines at -8 %: {100 * 3 / 12 * 0.08:.1f} % of the farm")
    c = (0.00275, 0.00298, 0.01154)
    for i, x in (("P76", 0.5), ("P80", 0.02)):
        y = float(ym.ac_from_dc([x], c)[0])
        p(i, f"inverter, DC {x} pu: AC {y:.4f} pu, efficiency {100 * y / x:.1f} %")
    p("P77", f"80 MW PV, PV first against wind first: 6,596 MWh x 10 u = {6596 * 10 / 1e3:.1f} k u")
    p("P78", f"newsvendor, prices 60 / 120 / 20: tau* = {(60 - 20) / (120 - 20):.2f}")
    p("P79", f"value of 1.07 MW less RMSE for 74 k u: {74 / (10.72 - 9.65):.0f} k u per MW")
    q = 100 * math.tan(math.acos(0.95))
    p("P81", f"pf 0.95 at 100 MW: Q = {q:.1f} Mvar; PV alone at 49 MVA: P <="
             f" {math.sqrt(49 ** 2 - q ** 2):.1f} MW")
    p("P82", f"round-trip loss of 10,817 MWh discharged at 86 %: {10817 * (1 / 0.86 - 1):,.0f} MWh")
    p("P83", f"price shifting: +375 k u for -1,646 MWh: {375e3 / 1646:.0f} u per MWh given up")
    p("P84", f"bridge: 295.14 - 289.23 = {295.14 - 289.23:.2f} GWh ({100 * 5.91 / 295.14:.1f} %)")
    emit("solutions", P)


if __name__ == "__main__":
    worked()
    solutions()
