"""Chapter 51, round w: reactive power at night and its cost, the monthly
operating report from one data set, choosing an outage day from the
forecast, a PCS outage during the service window, controller backups
against the last change, and fire-service arrival over four drills.

Run from the project root:   python -m companion.ch51.examples_w
Writes companion/ch51/expected/w_*.txt and diagrams/data/ch51-window.csv.
Teaching values (A-522 to A-529).
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch20 import sources as s20
from companion.ch51.common import csv, emit
from plantp import datapack


# ------------------------------------------------ 1. reactive power at night
def night_q(standby_kw: float = 3.0, inverters: int = 10, price: float = 60.0) -> dict:
    h = datapack.load_hourly()
    night = h["ghi_wm2"].to_numpy(float) <= 0
    hours = int(night.sum())
    asked = int(round(hours * 0.4))               # grid operator asks for Q 40 % of nights
    e_mwh = asked * standby_kw * inverters / 1000
    lines = [f"PV inverters kept on at night to give reactive power ({inverters} x "
             f"{standby_kw} kW standby)",
             f"  night hours in the data-pack year {hours:,}; Q asked in {asked:,} of them",
             f"  energy drawn {e_mwh:.1f} MWh, at {price:.0f} u/MWh: {e_mwh * price:,.0f} u",
             "  small against the service it gives, but it is real import:",
             "  whether night Q is paid, required or neither is the grid",
             "  operator's rule (ch 25: units off at night also changes the",
             "  plant's own Mvar)"]
    emit("w_nightq", lines)
    return dict(hours=hours, asked=asked, mwh=e_mwh, cost=e_mwh * price)


# ------------------------------------------------ 2. monthly report
def monthly_report() -> dict:
    kpi = {"exported energy MWh": 24_800, "PR (PV, %)": 81.2,
           "energy availability wind (%)": 96.4, "energy availability PV (%)": 98.1,
           "lost energy with a cause (%)": 31.0, "imbalance cost u": 112_400,
           "service availability (%)": 94.2, "recordable incidents": 0}
    sources = {"exported energy MWh": "main meter", "PR (PV, %)": "SCADA + met",
               "energy availability wind (%)": "SCADA", "energy availability PV (%)": "SCADA",
               "lost energy with a cause (%)": "lost-energy log",
               "imbalance cost u": "settlement statement",
               "service availability (%)": "service log", "recordable incidents": "HSE log"}
    lines = ["monthly operating report: each figure with the record it comes from"]
    lines += [f"  {k:32s} {v:>10,}  {sources[k]}" for k, v in kpi.items()]
    lines += ["  one data set per figure, frozen at the report date: the",
              "  energy is the meter's, not SCADA's (round u); the lost-energy",
              "  share shows the record still has gaps (lesson B) - the",
              "  report says so instead of hiding it in an average"]
    emit("w_report", lines)
    return kpi


# ------------------------------------------------ 3. choosing an outage day
def outage_window(first_day: int = 120, days: int = 10, hours=(8, 16)) -> dict:
    block = s15.plant_year()["pv_av"] / 10        # one of ten PV blocks, MW
    pv_share = []
    for d in range(first_day, first_day + days):
        seg = block[d * 24 + hours[0]: d * 24 + hours[1]]
        pv_share.append(float(np.sum(seg)))
    best = int(np.argmin(pv_share))
    csv("ch51-window.csv", "day,mwh", [(first_day + k, round(x, 1)) for k, x in
                                      enumerate(pv_share)])
    lines = [f"an 8-hour outage of one PV block ({hours[0]:02d}-{hours[1]:02d}) in the next "
             f"{days} days:",
             "  energy at risk by day (the block's modelled output stands in",
             "  for its day-ahead PV forecast)",
             "  " + " ".join(f"{x:5.1f}" for x in pv_share) + "  MWh",
             f"  lowest on day {first_day + best} ({pv_share[best]:.1f} MWh), highest "
             f"{max(pv_share):.1f}",
             "  the forecast chooses the day; the outage request, the crew",
             "  and the network owner's window must agree with it (round t,",
             "  notice) - and the forecast is updated the day before"]
    emit("w_window", lines)
    return dict(best=first_day + best, low=pv_share[best], high=max(pv_share))


# ------------------------------------------------ 4. PCS outage in the service window
def pcs_outage(pcs: int = 4, pcs_mw: float = 5.0) -> dict:
    need = s20.SERVICE["mw"]
    out_hours = 36                                   # one PCS out for 36 h
    left = (pcs - 1) * pcs_mw
    window_h = sum(1 for h in range(out_hours) if 18 <= (h + 10) % 24 < 22)
    lines = [f"one of {pcs} battery PCS ({pcs_mw:.0f} MW each) out for {out_hours} h from "
             "10:00",
             f"  power left {left:.0f} MW: the {need:.0f} MW service still fits with room for "
             "the schedule",
             f"  service-window hours inside the outage: {window_h}",
             "  the service is not reduced, but the schedule loses a quarter",
             "  of its battery power: the outage request says so, and the",
             "  daily plan is rebuilt before 10:00 (lesson D)"]
    emit("w_pcs", lines)
    return dict(left=left, window_h=window_h)


# ------------------------------------------------ 5. controller backups
BACKUPS = {   # device: (last change day, last backup day)
    "PPC": (250, 251), "RTU-1": (90, 91), "RTU-2": (310, 120), "firewall FW-1": (330, 300),
    "BESS-A EMS": (180, 182), "turbine SCADA server": (275, 276),
    "core switch SW-C1": (340, 200)}


def backups() -> list:
    stale = [(k, c, b) for k, (c, b) in BACKUPS.items() if b < c]
    lines = ["configuration backups against the last change, by device (day of year)"]
    lines += [f"  {k:22s} changed {c:3d}  backed up {b:3d}" + ("  STALE" if b < c else "")
              for k, (c, b) in BACKUPS.items()]
    lines += [f"  {len(stale)} devices changed after their last backup: RTU-2 is the",
              "  unrecorded second RTU of round s; a restore would bring back",
              "  the old rule base on the firewall and switch (ch 36",
              "  recovery) - a backup is due after every change, not by date"]
    emit("w_backups", lines)
    return stale


# ------------------------------------------------ 6. fire-service drills
def drills(plan: float = 53.0) -> dict:
    t = [68.0, 61.0, 57.0, 52.0]          # ch 50 drill, then quarterly
    first_ok = next((k + 1 for k, x in enumerate(t) if x <= plan), None)
    lines = [f"fire-service arrival in four drills (min), against the plan of {plan:.0f}",
             "  " + "  ".join(f"{x:4.0f}" for x in t),
             f"  plan met first in drill {first_ok}; the gain came from a staging",
             "  point at the gate and keys held by the guard (no change in",
             "  the service's own time) - each drill's record names what",
             "  changed, so the gain is kept when people change"]
    emit("w_drills", lines)
    return dict(first_ok=first_ok, gain=t[0] - t[-1])


if __name__ == "__main__":
    night_q()
    monthly_report()
    outage_window()
    pcs_outage()
    backups()
    drills()
