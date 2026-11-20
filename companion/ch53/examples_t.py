"""Chapter 53, round t: the worst turbines' share of the loss, tower fatigue
for a life extension, a new turbine on an old foundation, partial
repowering, the decommissioning campaign and its weather, battery
recycling, running spares down before a repowering, the battery's end
(second life or recycling), lease and restoration payments to the end,
herders' access during the works, record migration checked by sample,
transport in the decommissioning footprint, and the footprint ranking
when the repowering yields less.

Run from the project root:   python -m companion.ch53.examples_t
Writes companion/ch53/expected/t_*.txt. Teaching values (A-538 to A-545).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch53 import sources as src
from companion.ch53.common import emit
from plantp import datapack, lifecycle as lc


# ------------------------------------------------ 1. the worst turbines
def bad_actors() -> dict:
    lost = np.array([310, 180, 640, 150, 520, 170, 590, 160, 200, 140, 190, 160], float)  # MWh yr 18
    order = np.argsort(-lost)
    top3 = float(lost[order[:3]].sum() / lost.sum())
    lines = ["energy lost by turbine in year 18 (MWh, all causes)",
             "  " + " ".join(f"T{k + 1:02d}:{x:.0f}" for k, x in enumerate(lost[:6])),
             "  " + " ".join(f"T{k + 7:02d}:{x:.0f}" for k, x in enumerate(lost[6:])),
             f"  the three worst (T{order[0] + 1:02d}, T{order[1] + 1:02d}, T{order[2] + 1:02d}) are "
             f"{top3:.0%} of the loss",
             "  a fleet decision is usually a few-turbine decision: the bad",
             "  actors get the intervention first - T03 (converter trips and",
             "  its pitch cabinet) and T07 (gearbox bearing) are stories of",
             "  ch 52, T05 the gearbox of the insurance lesson (E)"]
    emit("t_bad", lines)
    return dict(top3=top3)


# ------------------------------------------------ 2. tower fatigue and life extension
def tower_fatigue(design_life: float = 25.0, site_ratio: float = 0.82) -> dict:
    used = src.YEAR_NOW / design_life * site_ratio
    rate = site_ratio / design_life
    years_left = (1 - used) / rate
    lines = [f"tower fatigue: the site loads are {site_ratio:.0%} of the design loads (ch 30,",
             "  teaching ratio from measured loads)",
             f"  damage used by year {src.YEAR_NOW}: {used:.2f}; at the same rate the towers last",
             f"  {years_left:.1f} more years (to year {src.YEAR_NOW + years_left:.0f})",
             "  a life extension to 30 fits the towers on this record - the",
             "  extension case also needs the foundations, bolts and the",
             "  maker's and certifier's assessment (ch 30, ch 54-58)"]
    emit("t_tower", lines)
    return dict(used=used, left=years_left)


# ------------------------------------------------ 3. a new turbine on an old foundation
def foundation_fit(m_old: float = 96.0, scale: float = 1.30, capacity: float = 118.0) -> dict:
    m_new = m_old * scale
    lines = [f"overturning moment at the foundation (MN m, teaching): old turbine {m_old:.0f},",
             f"  a 170 m rotor about {scale:.2f} times as much: {m_new:.0f} against a capacity of "
             f"{capacity:.0f}",
             f"  utilisation {m_new / capacity:.0%}: the old foundations do not carry the new rotor",
             "  without adaptation (ch 30) - the 'foundation adaptation' line",
             "  of the repowering plan is a design, a permit and a cost"]
    emit("t_found", lines)
    return dict(m_new=m_new, util=m_new / capacity)


# ------------------------------------------------ 4. partial repowering
def partial() -> dict:
    full_gain, full_cost = 55.0, 12 * 6.2 * src.REPOWER["capex_k_per_mw"]
    half_gain, half_cost = 30.0, 6 * 6.2 * src.REPOWER["capex_k_per_mw"]   # worst six first
    lines = ["repower all 12 turbines or the worst 6 (teaching gains after the export limit)",
             f"  all 12: +{full_gain:.0f} GWh a year for {full_cost:,.0f} k u = "
             f"{full_cost / full_gain:,.0f} k u per GWh a year",
             f"  worst 6: +{half_gain:.0f} GWh a year for {half_cost:,.0f} k u = "
             f"{half_cost / half_gain:,.0f} k u per GWh a year",
             "  the worst six give more per unit spent (their old output is",
             "  lowest) - but two turbine types on one site double the",
             "  spares and the training (ch 52)"]
    emit("t_partial", lines)
    return dict(full=full_cost / full_gain, half=half_cost / half_gain)


# ------------------------------------------------ 5. the decommissioning campaign
def campaign(days_per: float = 3.0, wind_limit: float = 10.0) -> dict:
    v = datapack.load_hourly()["ws_100m_ms"].to_numpy(float)
    hr = np.arange(v.size) % 24
    work = (hr >= 6) & (hr < 18)
    ok = (v < wind_limit) & work
    share = ok.sum() / work.sum()
    days = 12 * days_per / share
    lines = [f"12 turbines down, {days_per:.0f} crane days each, lifts below {wind_limit:.0f} m/s "
             "(ch 31 teaching limit)",
             f"  share of working hours below the limit in the data year: {share:.0%}",
             f"  about {days:.0f} calendar working days for the crane - the season is",
             "  chosen with the wind (ch 31), and the PV keeps exporting"]
    emit("t_campaign", lines)
    return dict(share=share, days=days)


# ------------------------------------------------ 6. battery recycling
def battery_recycle(t: float = 240.0) -> dict:
    routes = {"second life (lesson F)": 0.25, "recycling (hydrometallurgy)": 0.65,
              "residue to licensed disposal": 0.10}
    cost = {"second life (lesson F)": -1.2, "recycling (hydrometallurgy)": 1.5,
            "residue to licensed disposal": 2.0}                # k u per t (teaching; - = income)
    tot = sum(t * s * cost[k] for k, s in routes.items())
    lines = [f"{t:.0f} t of battery modules at closure (teaching routes and prices)"]
    lines += [f"  {k:30s} {s:4.0%}  {t * s:5.0f} t  {t * s * cost[k]:+7.0f} k u" for k, s in routes.items()]
    lines += [f"  net {tot:+,.0f} k u; transport as dangerous goods under the",
              "  applicable rules (ch 19, UN Manual of Tests) by licensed",
              "  carriers - the receiver's certificate closes each lot"]
    emit("t_battery", lines)
    return dict(net=tot)


# ------------------------------------------------ 7. run spares down before a repowering
def spares_rundown() -> dict:
    held = {"pitch motors": 6, "converter stacks": 3, "yaw drives": 4, "gearbox kits": 1}
    use = {"pitch motors": 1.2, "converter stacks": 0.8, "yaw drives": 0.6, "gearbox kits": 1.4}
    years = 4.0                                                  # to the repowering
    out = {k: held[k] - use[k] * years for k in held}
    lines = [f"turbine spares if the farm is repowered in {years:.0f} years: held minus expected use"]
    lines += [f"  {k:18s} held {held[k]}  use/yr {use[k]:.1f}  left {v:+.1f}" for k, v in out.items()]
    over = [k for k, v in out.items() if v >= 1]
    short = [k for k, v in out.items() if v <= -1]
    even = [k for k, v in out.items() if -1 < v < 1]
    lines += [f"  left over: {', '.join(over)} - stop buying them now;",
              f"  short: {', '.join(short)} - buy for the four years only;",
              f"  about even: {', '.join(even)}; left-over spares are sold with",
              "  the old turbines"]
    emit("t_rundown", lines)
    return out


# ------------------------------------------------ 8. lease and restoration payments
def payments(lease_k: float = 180.0) -> dict:
    yrs = src.LIFE - src.YEAR_NOW
    lease = lease_k * yrs
    fund_need = 4_635.0
    lines = [f"payments to the end: land lease {lease_k:.0f} k u a year for {yrs} years = "
             f"{lease:,.0f} k u",
             f"  restoration fund to reach {fund_need:,.0f} k u by year 25 (lesson C)",
             "  the lease runs until the land is returned and accepted, not",
             "  until the power stops - a closure that drags on keeps",
             "  paying (ch 33 land register)"]
    emit("t_pay", lines)
    return dict(lease=lease)


# ------------------------------------------------ 9. herders' access during the works
def access_days(months: int = 10, closed_share: float = 0.3) -> dict:
    days = months * 30 * closed_share
    extra = days * 600 / 1000 * 0.4                  # k u: detour cost per animal-day (teaching)
    lines = [f"herders' track closed {closed_share:.0%} of the {months}-month works: about "
             f"{days:.0f} days",
             f"  detour cost (teaching) about {extra:.0f} k u - compensated under the",
             "  livelihood commitment (ch 33), with a second crossing kept",
             "  open on crane days"]
    emit("t_access", lines)
    return dict(days=days, cost=extra)


# ------------------------------------------------ 10. record migration checked by sample
def migration(n: int = 80, bad: int = 6) -> dict:
    p = bad / n
    z = 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    lines = [f"CMMS history migrated: {n} records sampled against the source, {bad} differ",
             f"  error share {p:.1%}, 95 % interval {c - h:.1%} to {c + h:.1%} (Wilson, ch 51)",
             "  dates shifted by a time-zone setting and two failure codes",
             "  mapped to 'OTHER' (ch 52) - fixed and re-sampled before the",
             "  old system is switched off"]
    emit("t_migrate", lines)
    return dict(p=p, lo=c - h, hi=c + h)


# ------------------------------------------------ 11. transport in the footprint
def transport(t: float = 19_670.0, km: float = 180.0, f: float = 0.09) -> dict:
    tkm = t * km
    co2 = tkm * f / 1000
    lines = [f"decommissioning transport: {t:,.0f} t x {km:.0f} km to receivers = {tkm / 1e6:.1f} "
             "million t km",
             f"  at {f} kg CO2e per t km (teaching): {co2:,.0f} t CO2e",
             "  small against the materials themselves, but inside the",
             "  boundary of every option that removes equipment (lesson I)"]
    emit("t_transport", lines)
    return dict(co2=co2)


# ------------------------------------------------ 12. ranking if the repowering yields less
def ranking(cut: float = 0.8) -> dict:
    base = 4.89
    low = base / cut
    lines = [f"repowering footprint per kWh if it yields {cut:.0%} of the expected energy",
             f"  {base:.2f} -> {low:.2f} g CO2e/kWh; repair {0.89:.2f}, replacement {1.43:.2f}",
             "  the ranking does not move; per-kWh footprints rise as energy",
             "  falls, which is why the energy assumption is stated beside",
             "  every footprint number"]
    emit("t_rank", lines)
    return dict(low=low)


if __name__ == "__main__":
    bad_actors()
    tower_fatigue()
    foundation_fit()
    partial()
    campaign()
    battery_recycle()
    spares_rundown()
    payments()
    access_days()
    migration()
    transport()
    ranking()
