"""Chapter 18, lab D - the water-service basis: monthly operating demands
(cleaning by the chapter 15 trigger policy, sanitation, battery chiller
make-up) against three supplies (the spring's spare flow of chapter 14,
a licensed well, trucked water), the tank that bridges the dry months,
and a fire/emergency reserve that is held, never used for operations.
Construction water is a separate, temporary case.

Run from the project root:   python -m companion.ch18.lab_d
Writes companion/ch18/expected/d_*.txt and diagrams/data/ch18-*.csv.
Teaching values A-286; the reserve volume is a placeholder for the
fire authority (chapter 32).
"""
from __future__ import annotations

import numpy as np

from companion.ch10 import lab_d as l10
from companion.ch18 import sources as src
from companion.ch18.common import csv, emit
from plantp import architecture as ar

DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
SPRING_SPARE_LS = np.array([2.5, 3.0, 4.0, 4.5, 1.0, -0.5, -1.5, -2.0, -2.0, 1.0, 1.5, 2.0])
W = src.WATER


def cleaning_months() -> np.ndarray:
    """Cleanings per month under the truck trigger at 4 % (chapter 15)."""
    _, _, _, rain, heavy, rate = l10.station_year()
    x, days = 0.0, []
    for k in range(len(rate)):
        x += rate[k]
        if heavy[k]:
            x = 0.0
        elif rain[k]:
            x *= 0.5
        if x > 0.04:
            x *= 1 - l10.METHODS["truck wet"]["removal"]
            days.append(k)
    month = np.cumsum(DAYS)
    return np.array([sum(1 for d in days if (month[m] - DAYS[m]) <= d < month[m])
                     for m in range(12)])


def demands() -> dict:
    n = cleaning_months()
    per = l10.METHODS["truck wet"]["water"] * l10.N_MODULES / 1e3
    return {"cleaning": n * per,
            "sanitation": W["staff"] * W["l_per_person_day"] / 1e3 * DAYS,
            "bess_makeup": np.full(12, W["bess_makeup"])}


def basis() -> None:
    d = demands()
    tot = sum(d.values())
    lines = ["monthly operating water demand (m3; cleaning = truck at 4 % loss):",
             "  month  cleanings  cleaning  sanitation  battery  total"]
    n = cleaning_months()
    for m in range(12):
        lines.append(f"  {m + 1:5d}     {n[m]:3d}     {d['cleaning'][m]:7.0f}    {d['sanitation'][m]:6.0f}"
                     f"     {d['bess_makeup'][m]:5.0f}   {tot[m]:6.0f}")
    lines += [f"  year: {tot.sum():,.0f} m3 ({tot.sum() / 365:.1f} m3 a day on average);"
              f" peak month {tot.max():,.0f} m3",
              "  consumptive use; the fire reserve below is held, not consumed"]
    emit("d_demand", lines)
    csv("ch18-water.csv", "m,cleaning,sanitation,bess",
        [(m + 1, f"{d['cleaning'][m]:.0f}", f"{d['sanitation'][m]:.0f}",
          f"{d['bess_makeup'][m]:.0f}") for m in range(12)])


def supplies() -> None:
    d = demands()
    spring = np.clip(SPRING_SPARE_LS, 0, None) * 86.4 * DAYS
    well = np.full(12, W["well_supply"])
    lines = [f"supplies against the demand, tank {W['tank_m3']:.0f} m3 with a held reserve"
             f" of {W['fire_reserve_m3']:.0f} m3:",
             "  supply                         unmet m3/yr   lowest usable stock m3"]
    for name, sup in (("spring spare only (permit)", spring),
                      ("licensed well 1,500 m3/month", well),
                      ("well at half in a drought", 0.5 * well)):
        stock, unmet = ar.water_balance(sup, d, W["tank_m3"], W["fire_reserve_m3"])
        lines.append(f"  {name:30s} {unmet.sum():9,.0f}       {stock.min():8,.0f}")
    lines += ["  the well covers even at half its permit (750 m3 a month against",
              "  a peak month of 433 m3); the tank stays full",
              "  the spring has no spare water in Jun-Sep (chapter 14), when",
              "  cleaning needs most; a tank can bridge it only if the months",
              "  before refill it, and only under a permit (U-053); the reserve",
              "  stays untouched by design: a separate tank or a low suction"]
    emit("d_supply", lines)


def tank_size() -> None:
    d = demands()
    tot = sum(d.values())
    spring = np.clip(SPRING_SPARE_LS, 0, None) * 86.4 * DAYS
    dry = (np.arange(12) >= 5) & (np.arange(12) <= 8)
    need = float(tot[dry].sum())
    best = None
    for size in range(500, 6001, 100):
        _, unmet = ar.water_balance(np.where(dry, 0, spring), d, size + W["fire_reserve_m3"],
                                    W["fire_reserve_m3"])
        if unmet.sum() == 0:
            best = size
            break
    lines = ["tank to carry the operating demand through Jun-Sep from the spring:",
             f"  demand in Jun-Sep {need:,.0f} m3; smallest usable tank with",
             f"    no unmet demand {best:,} m3",
             f"  plus the held reserve {W['fire_reserve_m3']:.0f} m3: total {best + W['fire_reserve_m3']:,.0f} m3",
             "  or: robots for dry cleaning (chapter 10) cut the cleaning water",
             "  to zero and leave sanitation and make-up only"]
    emit("d_tank", lines)


def construction() -> None:
    lines = ["construction water (chapter 14): 12,204 m3 over the build,",
             "  of which dust suppression 10,800 m3; at 0.46 L/s on working days",
             "  it exceeds the operating demand many times: a temporary source",
             "  (trucked or a temporary well permit) and its own tank, not the",
             "  operating tank; the architecture keeps the two apart"]
    emit("d_construction", lines)


if __name__ == "__main__":
    basis()
    supplies()
    tank_size()
    construction()
