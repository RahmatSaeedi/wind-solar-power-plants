"""Chapter 15, sections C5 and D5 - the battery of scenario S1 used for
price shifting (less energy, more money), reactive power at the inverter
limit (active power given up), and the bridge between two models
(reconciling a reviewer's model step by step, in two orders).

Run from the project root:   python -m companion.ch15.examples_n
Writes companion/ch15/expected/n_*.txt.
Model 15.1; teaching prices and rules A-273.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import examples_m as em, sources as src
from companion.ch15.common import emit

P_LOW, P_MID, P_HIGH = 35.0, 50.0, 75.0     # u/MWh, A-273


def prices():
    hour = np.arange(8760) % 24
    p = np.full(8760, P_MID)
    p[(hour >= 10) & (hour < 15)] = P_LOW
    p[(hour >= 18) & (hour < 22)] = P_HIGH
    return p


# [start: shifting]
def shifting() -> None:
    """S1 battery (20 MW, 40 MWh, usable 4-36 MWh, round trip 86 %):
    stores curtailed power at any hour; from 10:00 to 15:00 it also
    charges from the plant's output up to 20 MW; from 18:00 to 22:00 it
    discharges up to 20 MW within the export limit."""
    r = src.plant_year()
    net0 = r["net"]
    poc = r["poc"]
    out = r["outage"]
    pr = prices()
    hour = np.arange(8760) % 24
    eta = math.sqrt(0.86)
    soc, lo, hi = 4.0, 4.0, 36.0
    net1 = net0.copy()
    thr = 0.0
    for k in range(8760):
        cut = max(poc[k] - 100.0, 0.0) if not out[k] else 0.0
        ch = min(cut, 20.0, (hi - soc) / eta)
        soc += ch * eta
        room = 20.0 - ch
        if 10 <= hour[k] < 15 and not out[k] and room > 0:
            c2 = min(max(net1[k], 0.0), room, (hi - soc) / eta)
            soc += c2 * eta
            net1[k] -= c2
        elif 18 <= hour[k] < 22 and not out[k]:
            d = min(20.0, (soc - lo) * eta, max(100.0 - net1[k], 0.0))
            soc -= d / eta
            net1[k] += d
            thr += d
# [end: shifting]
    e0, e1 = net0.sum() / 1e3, net1.sum() / 1e3
    v0, v1 = (pr * net0).sum() / 1e3, (pr * net1).sum() / 1e3
    lines = ["battery of scenario S1 used for price shifting (teaching prices",
             f"  {P_LOW:.0f} u/MWh 10-15 h, {P_HIGH:.0f} u/MWh 18-22 h, {P_MID:.0f} otherwise, A-273):",
             f"  S0 net {e0:8.2f} GWh   value {v0:8,.0f} k u",
             f"  S1 net {e1:8.2f} GWh   value {v1:8,.0f} k u",
             f"  energy {1e3 * (e1 - e0):+,.0f} MWh, value {v1 - v0:+,.0f} k u;"
             f" discharged {thr:,.0f} MWh ({thr / 32:.0f} usable cycles)",
             "  the battery makes the plant sell less energy for more money:",
             "  a yield statement for S1 shows the round-trip loss as a loss,",
             "  and the value belongs to the price model (chapters 17-21)"]
    emit("n_shifting", lines)


def reactive() -> None:
    """A power-factor requirement of 0.95 at the POC (teaching, A-273),
    met by the PV inverters alone or shared with the wind turbines in
    proportion to their rating; the model's PV AC limit of 49 MW is read
    as an apparent-power limit of 49 MVA."""
    r = src.plant_year()
    tanphi = math.tan(math.acos(0.95))
    q_req = tanphi * np.clip(r["mv"], 0, None)
    ratio = r["pv_av"].sum() / r["pv_clip"].sum()          # later PV steps
    base = np.clip(r["pv_inv"] - 49.0, 0, None).sum()
    lines = ["active power given up at the PV inverters' apparent-power limit",
             "  for a power factor of 0.95 at the POC (teaching, A-273):"]
    for name, share in (("PV inverters give all the reactive power", 1.0),
                        ("shared with the turbines by rating", 50 / 110)):
        q = share * q_req
        pmax = np.sqrt(np.clip(49.0 ** 2 - q ** 2, 0, None))
        extra = (np.clip(r["pv_inv"] - pmax, 0, None).sum() - base) * ratio
        hrs = int((r["pv_inv"] > pmax + 1e-9).sum() - (r["pv_inv"] > 49.0).sum())
        lines.append(f"  {name:42s} {extra:6,.0f} MWh in {hrs} more hours")
    lines += ["  reactive power at full sun takes room from the active power",
              "  of an inverter at its limit; sharing it with the turbines and",
              "  sizing inverters in MVA (chapter 25) keep the loss small; the",
              "  requirement itself is national (chapters 28 and 55-57)"]
    emit("n_reactive", lines)


def bridge() -> None:
    """Model A is 15.1; a reviewer's model B uses the isotropic sky and
    the NOCT temperature model (PV x 0.979 x 0.979, applied after the
    inverter as a teaching shortcut), wake decay 0.075, wind availability
    97 % and soiling 2.0 %. Steps applied in two orders."""
    r = src.plant_year()
    cfg = src.ModelConfig()
    out = r["outage"]
    wake = (1 - 0.0346) / (1 - 0.0400)
    steps = [("PV sky model (isotropic)", "pv", 0.979),
             ("PV temperature model (NOCT)", "pv", 0.979),
             ("PV soiling 2.0 %", "pv", (1 - 0.020) / (1 - 0.0143)),
             ("wake decay 0.075", "w", wake),
             ("wind availability 97 %", "w", 0.97 / 0.981)]

    def run(order):
        w_, p_ = r["w_av"].copy(), r["pv_av"].copy()
        prev = em.tail(w_, p_, cfg, out)[1].sum() / 1e3
        res = {}
        for name, kind, f in order:
            if kind == "pv":
                p_ = p_ * f
            else:
                w_ = w_ * f
            now = em.tail(w_, p_, cfg, out)[1].sum() / 1e3
            res[name] = now - prev
            prev = now
        return res, prev

    a0 = em.tail(r["w_av"], r["pv_av"], cfg, out)[1].sum() / 1e3
    fw, b_net = run(steps)
    bw, b_net2 = run(list(reversed(steps)))
    lines = [f"bridge from model A ({a0:.2f} GWh) to the reviewer's model B ({b_net:.2f} GWh):",
             "  step                            PV first GWh   wind first GWh"]
    for name, _, _ in steps:
        lines.append(f"  {name:30s}   {fw[name]:+9.2f}       {bw[name]:+9.2f}")
    lines += [f"  sum                              {sum(fw.values()):+9.2f}       {sum(bw.values()):+9.2f}",
              "  the two orders give the same end and nearly the same steps:",
              "  the steps barely interact at this size; with a binding limit",
              "  or clipping, order matters and the bridge states the order"]
    emit("n_bridge", lines)


# [start: ramplimit]
def ramp_limit() -> None:
    """One-minute PV output on the broken-cloud day of chapter 12
    (P = 60.06 MW x 0.84 x GHI / 1000, at most 49 MW: a teaching
    conversion, A-273) against a ramp limit of 5 MW per minute (10 % of
    50 MW, teaching): up-ramps are cut by the controller, down-ramps
    need a battery."""
    from companion.ch12 import sources as s12
    g = s12.minute_days()["broken"]["true"]
    p = np.clip(60.06 * 0.84 * g / 1000, 0, 49.0)
    lim = 5.0
    dp = np.diff(p)
    out = np.empty_like(p)
    out[0] = p[0]
    for k in range(1, len(p)):
        out[k] = min(p[k], out[k - 1] + lim)      # up-ramps: curtail
    cut = (p - out).sum() / 60
    # battery fills down-ramps beyond the limit: output may fall 5 MW/min
    soc, need_p, used, served = 0.0, 0.0, 0.0, np.empty_like(p)
    served[0] = out[0]
    for k in range(1, len(p)):
        floor = served[k - 1] - lim
        b = max(floor - out[k], 0.0)
        served[k] = out[k] + b
        need_p = max(need_p, b)
        used += b / 60
# [end: ramplimit]
    hourly = p.reshape(24, 60).mean(axis=1)
    lines = ["one-minute PV on a broken-cloud day (chapter 12, A-273) against a",
             "  ramp limit of 5 MW per minute:",
             f"  day energy {p.sum() / 60:.1f} MWh; minutes ramping up > 5 MW/min"
             f" {int((dp > lim).sum())}, down {int((dp < -lim).sum())}",
             f"  largest one-minute change {np.abs(dp).max():.1f} MW; largest change"
             f" of hourly means {np.abs(np.diff(hourly)).max():.1f} MW",
             f"  up-ramp limit by curtailment: {cut:.2f} MWh lost"
             f" ({100 * cut / (p.sum() / 60):.1f} % of the day)",
             f"  down-ramp limit by a battery: up to {need_p:.1f} MW, {used:.2f} MWh"
             " discharged in the day",
             "  hourly data cannot see these ramps; a ramp rule is checked on",
             "  minute data, and wind in the same minutes may soften or add",
             "  to them (the plant-level ramp is what the grid sees)"]
    emit("n_ramplimit", lines)


if __name__ == "__main__":
    ramp_limit()
    shifting()
    reactive()
    bridge()
