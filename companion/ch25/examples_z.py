"""Chapter 25 - twelfth round: correcting a measured load loss to the
reference temperature, the impedance across the tap range, the water a
breather catches in a year, and the expected yearly cost of a main
transformer failure against a spare-pool fee.

Run from the project root:   python -m companion.ch25.examples_z
Writes companion/ch25/expected/z_*.txt. Teaching values (A-326..A-330
extended).
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import emit

M = src.MAIN


# [start: refloss]
def load_loss_at(ref_c: float, meas_c: float, i2r_kw: float,
                 stray_kw: float, t_k: float = 235.0) -> float:
    """Load loss corrected from the measuring temperature to the
    reference: the I2R part grows with resistance, the stray (eddy)
    part shrinks in proportion (copper: t_k = 235)."""
    k = (t_k + ref_c) / (t_k + meas_c)
    return i2r_kw * k + stray_kw / k
# [end: refloss]


def ref_loss() -> None:
    i2r, stray, meas_c = 155.0, 72.0, 22.0
    k = (235 + 75) / (235 + meas_c)
    p75 = load_loss_at(75, meas_c, i2r, stray)
    wrong = (i2r + stray) * k
    lines = ["load loss measured cold (22 C), corrected to 75 C (teaching unit):",
             f"  measured: I2R part {i2r:.0f} kW (from winding resistance), stray {stray:.0f} kW,",
             f"  total {i2r + stray:.0f} kW; factor k = (235 + 75)/(235 + 22) = {k:.3f}",
             f"  correct: I2R x k + stray / k = {p75:.1f} kW",
             f"  wrong (all of it x k): {wrong:.1f} kW",
             f"  guarantee 250 kW: corrected value {'inside' if p75 <= 250 else 'over'};"
             f" the wrong method says {'inside' if wrong <= 250 else 'over'}",
             "  the stray part falls as the metal warms (higher",
             "  resistance, smaller eddy currents): the report states the",
             "  measured winding resistance, the temperature and the split,",
             "  so the correction can be checked line by line"]
    emit("z_refloss", lines)


def tap_impedance() -> None:
    taps = [(-10.0, 11.4), (0.0, 12.0), (10.0, 12.9)]
    lines = ["impedance across the tap range (teaching data from a test report):",
             "  tap %    uk %   fault current at 33 kV, kA (stiff grid)"]
    for t, uk in taps:
        lines.append(f"  {t:+5.1f}   {uk:5.1f}   {M['s_mva'] / (math.sqrt(3) * 33 * uk / 100):10.2f}")
    lines += ["  the fault level is checked at the tap with the lowest",
              "  impedance, the regulation at the highest; two paralleled",
              "  units on different taps also share load unevenly (lesson",
              "  circulating) - the dossier gives uk at the extreme and",
              "  principal taps, not only at the principal"]
    emit("z_tapz", lines)


def breather() -> None:
    oil, beta, swing = M["oil_m3"], 0.00075, 25.0
    air_day = oil * beta * swing
    lines = ["water caught by the conservator's breather (teaching):",
             f"  oil {oil:.0f} m3, expansion 0.00075 per K, daily swing of oil",
             f"  temperature {swing:.0f} K: the conservator breathes in {air_day:.2f} m3 of air a day",
             "  air (at 25 C)   water g/m3   water a year kg   gel 3 kg lasts (25 %)"]
    for rh, wv in (("50 % RH", 11.5), ("80 % RH", 18.4)):
        year = air_day * wv * 365 / 1e3
        lines.append(f"  {rh:13s}   {wv:10.1f}   {year:15.2f}   {0.75 / year * 12:15.1f} months")
    lines += ["  without the breather this water would reach the oil and",
              "  then the paper (lesson moisture): a few kilograms a year;",
              "  the gel's colour change is a routine inspection item, or a",
              "  self-drying breather removes the visit - a choice for the",
              "  specification and the maintenance plan (ch 52)"]
    emit("z_breather", lines)


def failure_risk() -> None:
    rate = 0.015                  # per transformer per year (A-330)
    cost_no_pool = 3_380.0        # repair, 8 months out (lesson failure)
    cost_pool = 1_515.0           # pool spare now, repair later
    fee = 40.0                    # teaching yearly pool fee, k u
    e_no = 2 * rate * cost_no_pool
    e_pool = 2 * rate * cost_pool + fee
    lines = ["expected yearly cost of a main transformer failure (two units)",
             f"  failure rate {rate} per unit-year (teaching, A-330)",
             f"  without a pool: 2 x {rate} x {cost_no_pool:,.0f} = {e_no:.0f} k u a year",
             f"  with a pool:    2 x {rate} x {cost_pool:,.0f} + fee {fee:.0f} = {e_pool:.0f} k u a year",
             f"  break-even fee: {2 * rate * (cost_no_pool - cost_pool):.0f} k u a year",
             "  on expectation the pool pays; its real value is larger:",
             "  it cuts the rare large loss that lenders and insurers fear",
             "  (ch 16, ch 21) - a decision on the tail, not on the mean"]
    emit("z_risk", lines)


def solar_gain() -> None:
    losses, area, sun = 49.5, 12.0, 1.0      # kW, m2 facing the sun, kW/m2
    lines = ["sun on a PV unit transformer's tank (teaching; noon, 1 kW/m2 on",
             "  12 m2 of lid and sides; full load, losses 49.5 kW)",
             "  paint            absorbed   extra kW   top-oil rise x   +K on 52 K"]
    for name, alpha in (("dark grey", 0.80), ("light grey", 0.50), ("white", 0.25)):
        q = alpha * sun * area
        f = ((losses + q) / losses) ** 0.8
        lines.append(f"  {name:15s} {alpha:9.2f}   {q:8.1f}   {f:14.3f}   {52 * (f - 1):10.1f}")
    f_dark = ((losses + 0.8 * sun * area) / losses) ** 0.8
    k_eq = math.sqrt((7 * f_dark ** 1.25 - 1) / 6)
    lines += ["  at a PV site the sun is strongest exactly when the unit is",
              "  fully loaded: a dark tank adds about 8 K to the top oil -",
              f"  the same as running at {k_eq:.2f} pu without sun; a light paint or a",
              "  sun roof is cheap, and the maker's rating states whether it",
              "  includes solar gain (the specification asks)"]
    emit("z_sun", lines)


if __name__ == "__main__":
    ref_loss()
    tap_impedance()
    breather()
    failure_risk()
    solar_gain()
