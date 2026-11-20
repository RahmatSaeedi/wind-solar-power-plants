"""Chapter 49, round s: module stock and laydown for a block, cable
pulling logs against the maker's limits, check sheets burned down to the
mechanical-completion date, a claim with two overlapping delays, the
module S-curve and its forecast, a fire-stopping inspection sample, the
construction sediment pond, sectional turnover signatures on the export
works, camp beds against the workers from outside, and radio coverage of
the work fronts.

Run from the project root:   python -m companion.ch49.examples_s
Writes companion/ch49/expected/s_*.txt and diagrams/data/ch49-scurve.csv.
Teaching values (A-506 to A-513).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch49 import sources as src
from companion.ch49.common import csv, emit
from plantp import civil, docctl, logistics


# ------------------------------------------------ 1. module stock and laydown
def laydown(per_pallet: int = 36, pallet_m2: float = 2.6, rate_day: int = 1200,
            truck_pallets: int = 22) -> dict:
    pallets = math.ceil(src.BLOCK["modules"] / per_pallet)
    rows = []
    for buffer_days in (1, 3, 7, len(range(0, pallets)) * per_pallet // rate_day + 1):
        stock = min(pallets, math.ceil(buffer_days * rate_day / per_pallet))
        area = logistics.laydown_area([pallet_m2] * stock)
        rows.append((buffer_days, stock, area))
    lines = [f"modules of block PVF1-3: {src.BLOCK['modules']:,} on {pallets} pallets of "
             f"{per_pallet}; mounting {rate_day:,} a day",
             f"  ({math.ceil(rate_day / per_pallet)} pallets a day, about "
             f"{rate_day / per_pallet / truck_pallets:.1f} trucks)",
             "  stock held      pallets  laydown m2 (with aisles)"]
    lines += [f"  {d:3d} d          {s:7d}  {a:9,.0f}" for d, s, a in rows]
    whole, three = rows[-1], rows[1]
    lines += [f"  the whole block at once needs {whole[2]:,.0f} m2 of laydown, "
              f"{whole[2] / three[2]:.0f} times",
              "  the three-day stock, and preservation for every pallet",
              "  until it is mounted; three days of stock keeps the crews fed",
              "  through one late truck - the buffer is set from the delivery",
              "  reliability, not habit"]
    emit("s_laydown", lines)
    return dict(pallets=pallets, rows=rows)


# ------------------------------------------------ 2. cable pulling logs
PULLS = [   # cable, max tension kN, maker's limit kN, min bend radius m, limit m
    ("WS1-S1", 14.2, 18.0, 1.10, 1.00), ("WS1-S2", 19.5, 18.0, 1.05, 1.00),
    ("WS1-S3", 11.0, 18.0, 0.85, 1.00), ("WS1-S4a", 16.8, 18.0, 1.20, 1.00),
    ("WS1-S4b", None, 18.0, 1.10, 1.00),
]


def pulls() -> list:
    bad = []
    for c, t, tl, r, rl in PULLS:
        why = []
        if t is None:
            why.append("no tension record")
        elif t > tl:
            why.append(f"tension {t} kN over {tl}")
        if r < rl:
            why.append(f"bend {r} m under {rl}")
        if why:
            bad.append((c, why))
    lines = ["MV cable pulling logs against the maker's limits (teaching values)"]
    lines += [f"  {c}: {'; '.join(w)}" for c, w in bad]
    lines += ["  an over-tension pull or a tight bend can damage the",
              "  insulation without a visible mark: the cable is tested",
              "  before it is jointed (ch 50) and the maker decides; a pull",
              "  with no tension record is treated like one over the limit"]
    emit("s_pulls", lines)
    return bad


# ------------------------------------------------ 3. check sheets to MC
def burndown(total: int = 640, done: int = 410, rates=(18, 26, 22, 30),
             mc_day: int = 270, today: int = 244) -> dict:
    rate = float(np.mean(rates))
    left = total - done
    finish = today + left / rate * 7
    need = left / ((mc_day - today) / 7)
    lines = [f"A check sheets of the PV area: {done} of {total} closed on day {today}",
             f"  closed in the last four weeks: {', '.join(map(str, rates))} "
             f"(mean {rate:.1f} a week)",
             f"  at that rate the last sheet closes on day {finish:.0f}; planned MC "
             f"day {mc_day}",
             f"  to make day {mc_day}: {need:.0f} sheets a week, "
             f"{need / rate:.1f} times the rate",
             "  the burn-down shows the MC date long before the walkdown",
             "  does; the levers are the inspectors' hours and closing the",
             "  open A punch items that hold whole sheets (lesson C)"]
    emit("s_burndown", lines)
    return dict(finish=finish, need=need, rate=rate)


# ------------------------------------------------ 4. a claim with two delays
def concurrency() -> dict:
    owner = (60, 75)          # wadi consent late: owner's risk (lesson A)
    contractor = (68, 80)     # crew shortage on the access road: contractor's
    overlap = max(0, min(owner[1], contractor[1]) - max(owner[0], contractor[0]))
    only_owner = (owner[1] - owner[0]) - overlap
    only_con = (contractor[1] - contractor[0]) - overlap
    lines = ["access road km 4: two delays on the same critical activity",
             f"  wadi consent (owner's risk):    days {owner[0]}-{owner[1]}",
             f"  crew shortage (contractor's):   days {contractor[0]}-{contractor[1]}",
             f"  owner's alone {only_owner} days; both at once {overlap} days; "
             f"contractor's alone {only_con} days",
             f"  a common teaching split: time for the owner's {only_owner} + "
             f"{overlap} days, money for",
             f"  the owner's {only_owner} days only - each party bears its own "
             "days of the overlap",
             "  the split is the contract's to set; what the analysis needs",
             "  is the daily record of both causes - without it the overlap",
             "  is argued, not counted"]
    emit("s_concurrency", lines)
    return dict(only_owner=only_owner, overlap=overlap, only_con=only_con)


# ------------------------------------------------ 5. S-curve and forecast
def scurve(weeks: int = 20, total: int = 109_200) -> dict:
    w = np.arange(1, weeks + 1)
    plan = total / (1 + np.exp(-(w - 10.5) / 2.2))
    plan = plan / plan[-1] * total
    actual_rate = np.r_[np.zeros(2), [3800, 4300, 4700, 3100, 5200, 5400, 4100, 5600]]
    actual = np.cumsum(np.r_[actual_rate, np.full(weeks - 10, np.nan)])[:weeks]
    now = 10
    rate = float(np.mean(actual_rate[-4:]))
    left = total - actual[now - 1]
    fin = now + left / rate
    spi = actual[now - 1] / plan[now - 1]
    csv("ch49-scurve.csv", "week,plan,actual",
        [(int(k), round(p), "nan" if np.isnan(a) else int(a)) for k, p, a in zip(w, plan, actual)])
    lines = [f"modules of the whole PV plant ({total:,}): planned S-curve and actual",
             f"  week {now}: actual {actual[now - 1]:,.0f}, planned {plan[now - 1]:,.0f}, "
             f"SPI {spi:.2f}",
             f"  at the last four weeks' rate ({rate:,.0f} a week) the last module goes",
             f"  up in week {fin:.1f}, against week {weeks} planned",
             f"  the plan's steepest week needs {np.diff(plan).max():,.0f}; the crews reach "
             f"{rate / np.diff(plan).max():.0%}",
             "  of that - the gap is crews and deliveries, and the recovery",
             "  of lesson E is sized from this curve"]
    emit("s_scurve", lines)
    return dict(spi=spi, finish=fin, rate=rate)


# ------------------------------------------------ 6. fire-stopping sample
def firestop(n: int = 120, defects: int = 6, samples=(10, 20, 32, 50)) -> dict:
    out = {s: docctl.detect_chance(n, defects, s) for s in samples}
    lines = [f"fire-stopped penetrations in the substation building: {n};",
             f"  suppose {defects} are faulty",
             "  inspected   chance of finding at least one"]
    lines += [f"  {s:9d}   {p:8.0%}" for s, p in out.items()]
    lines += ["  a sample of ten misses them more often than it finds one;",
              "  fire stopping is inspected before it is hidden (before the",
              "  cable tray cover or the ceiling), and every penetration",
              "  gets its photo and label - lesson G's records"]
    emit("s_firestop", lines)
    return out


# ------------------------------------------------ 7. sediment pond
def pond(c: float = 0.45, i_mm_h: float = 35.0, area_km2: float = 0.42,
         minutes: float = 30.0, pond_m3: float = 900.0) -> dict:
    q = civil.rational_peak(c, i_mm_h, area_km2)
    vol = q * minutes * 60                  # continuity: C i A t (peak x duration)
    lines = ["construction sediment pond below the PVF1 area (ch 29 rational method)",
             f"  C {c}, design storm {i_mm_h} mm/h, area {area_km2} km2: peak "
             f"{q:.2f} m3/s",
             f"  runoff volume of a {minutes:.0f}-minute storm (C i A t): {vol:,.0f} m3",
             f"  pond {pond_m3:,.0f} m3: {'enough' if pond_m3 >= vol else 'too small'} "
             f"({pond_m3 / vol:.0%} of the volume)",
             "  graded ground runs off more than the desert it replaced;",
             "  the pond is enlarged or a second one dug before the rains,",
             "  and its outlet and the spill kit are on the weekly check"]
    emit("s_pond", lines)
    return dict(q=q, vol=vol, share=pond_m3 / vol)


# ------------------------------------------------ 8. sectional turnover
TURNOVER = {   # section: signatures (contractor, owner, network operator)
    "line T01-T08": (True, True, False), "WS1 S1-S2": (True, True, None),
    "WS1 S3-S4": (True, False, None), "bay E1 (grid side)": (True, False, False),
}


def sectional() -> list:
    open_ = []
    for s, sig in TURNOVER.items():
        miss = [who for who, ok in zip(("contractor", "owner", "network operator"), sig)
                if ok is False]
        if miss:
            open_.append((s, miss))
    lines = ["sectional turnover of the export works: signatures still missing",
             "  (None = the network operator is not a party to that section)"]
    lines += [f"  {s:20s} {', '.join(m)}" for s, m in open_]
    lines += ["  the line and bay E1 cross the ownership boundary of ch 23:",
              "  the network operator's signature is the one that lets them",
              "  be energised - planned with its notice period, not asked for",
              "  in the last week"]
    emit("s_sectional", lines)
    return open_


# ------------------------------------------------ 9. camp beds
def camp(beds: int = 270) -> dict:
    rows = [(m, w - l) for m, (w, l) in src.HIRE.items()]
    over = [(m, o) for m, o in rows if o > beds]
    lines = [f"camp beds ({beds}, lesson A) against the workers from outside by month"]
    lines += [f"  month {m}: {o} from outside" + ("  OVER" if o > beds else "")
              for m, o in rows]
    lines += [f"  month {over[0][0]} needs {over[0][1] - beds} beds more than the camp has:" if over
              else "  within the camp",
              "  lesson A sized the camp at 60 % of the peak; local hiring",
              "  fell to a third (lesson J) and the outside share rose - the",
              "  two plans are one plan, and they are reviewed together"]
    emit("s_camp", lines)
    return dict(over=over)


# ------------------------------------------------ 10. radio coverage
COVER = {"PV block PVF1-3": "site radio", "PV block PVF3-3": "site radio",
         "T01 erection": "site radio", "T12 erection": "weak (hill shadow)",
         "substation": "site radio and phone", "132 kV line, tower 18": "none"}


def radio() -> list:
    gaps = [(f, c) for f, c in COVER.items() if c in ("none",) or c.startswith("weak")]
    lines = ["communications at each work front (survey with the site radio)"]
    lines += [f"  {f:22s} {c}" for f, c in COVER.items()]
    lines += [f"  {len(gaps)} fronts need a fallback before work: a satellite phone",
              "  or a repeater - the same two fronts that sit at the edge of",
              "  the response time (lesson L); a call that does not go",
              "  through adds its own minutes to every number there"]
    emit("s_radio", lines)
    return gaps


if __name__ == "__main__":
    laydown()
    pulls()
    burndown()
    concurrency()
    scurve()
    firestop()
    pond()
    sectional()
    camp()
    radio()
