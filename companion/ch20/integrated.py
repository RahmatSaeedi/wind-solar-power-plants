"""Chapter 20 - three integrated Plant P examples: one hour of the worked
day by hand, the worked day again with REQ-S01 in the plan, and the
control basis of the year (D-024).

Run from the project root:   python -m companion.ch20.integrated
Writes companion/ch20/expected/int_*.txt.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import examples_b as eb, lab_d, lab_e, sources as src
from companion.ch20.common import emit
from plantp import control as ct

L = src.LIMITS


def one_hour() -> None:
    d = lab_d.the_day()
    t = d * 24 + 11
    act = float(np.clip(src.poc_actual()[t], 0, None))
    e0 = 6.4
    c = min(L["bess_mw"], (L["e_max"] - e0) / L["eta"])
    export = min(act - c, 80.0)
    curt = act - c - export
    lines = [f"hour 11 of day {d + 1} by hand (cap 80 MW, battery at {e0} MWh):",
             f"  plant {act:.1f} MW; battery room (36 - {e0}) / 0.927 = "
             f"{(L['e_max'] - e0) / L['eta']:.1f} MWh -> charge {c:.1f} MW",
             f"  export min({act:.1f} - {c:.1f}, 80) = {export:.1f} MW;"
             f" curtailed {curt:.1f} MW",
             f"  energy after the hour {e0} + {c:.1f} x 0.927 = {e0 + c * L['eta']:.1f} MWh"]
    emit("int_hour", lines)


def day_with_service() -> None:
    d = lab_d.the_day()
    h = slice(d * 24, d * 24 + 24)
    fc = np.clip(src.poc_forecast(24)[h], 0, None)
    act = np.clip(src.poc_actual()[h], 0, None)
    cap, price = eb.caps()[h], src.prices()[h]
    lines = [f"day {d + 1} with and without REQ-S01 in the plan:",
             "  case            SOC at 18 h   discharge 18-22 MWh   value k u   alarms"]
    for name, mw in (("no service", 0.0), ("REQ-S01", 5.0)):
        floor = np.full(24, L["e_min"])
        room = np.clip(cap - fc, 0, None)
        if mw:
            floor[18:22] = lab_e.floor_mwh(mw, 1.0)
            room[18:22] = np.minimum(room[18:22], L["bess_mw"] - mw)
        _, _, plan = ct.dp_schedule(price, np.minimum(fc, L["bess_mw"]), room,
                                    L["bess_mw"], L["e_min"], L["e_max"],
                                    L["e_min"], L["eta"], wear=10.0,
                                    floor=floor, e_end=L["e_min"])
        c = ct.Controller(e=L["e_min"])
        val = dis = 0.0
        e18 = None
        for k in range(24):
            c.reserve_up = mw if 18 <= k < 22 else 0.0
            if k == 18:
                e18 = c.e
            r = c.step(k, act[k], plan[k], cap[k], True)
            val += r["export"] * price[k]
            if 18 <= k < 22:
                dis += r["discharge"]
        lines.append(f"  {name:14s} {e18:12.1f}   {dis:20.1f}   {val / 1000:9.2f}"
                     f"   {len(c.alarms):6d}")
    lines += ["  the service keeps 9.4 MWh in the battery through the window",
              "  and gives up part of the evening discharge; the rest of the",
              "  day is unchanged"]
    emit("int_day", lines)


def basis() -> None:
    lines = ["control basis of Plant P (D-024), numbers from this chapter:",
             "  hierarchy: scheduling / EMS / PPC / subsystems / devices",
             "  PPC loop: kp 1.5, ki 0.8 on tau 2 s; anti-windup; delay <= 0.5 s",
             "  priorities: safety > operator > service > schedule > recapture",
             "  comms loss: hold 1 h, then battery fallback; cap never raised",
             "  battery value with day-ahead plans 469 k u/yr (99.5 % of perfect)",
             "  imbalance: day-ahead 1,245 -> intraday 919 k u/yr (teaching)",
             "  bid at quantile 0.25: penalty -16 % (Sep-Dec)",
             "  REQ-S01 in the plan: held 99.2 % with calls and outages, cost",
             "    57.7 k u/yr = 7.90 u per MW-h held, 104 alarms/yr",
             "  island only for critical loads; black start not offered"]
    emit("int_basis", lines)


if __name__ == "__main__":
    one_hour()
    day_with_service()
    basis()
