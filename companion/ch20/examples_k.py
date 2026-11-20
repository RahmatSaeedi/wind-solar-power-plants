"""Chapter 20, closing lessons: a frequency event answered by the battery
(response and recovery), freezing the plant loop while the units ride
through a voltage dip, validating the plant model against a measured
step, and the battery used to absorb schedule deviations instead of
shifting energy.

Run from the project root:   python -m companion.ch20.examples_k
Writes companion/ch20/expected/k_*.txt and diagrams/data/ch20-*.csv.
Teaching values A-299 to A-303.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import sources as src
from companion.ch20.common import csv, emit
from plantp import control as ct

L = src.LIMITS
DT = 0.1


def freq_profile(t):
    """Teaching frequency event: fall to 49.6 Hz at 5 s, recover to
    49.85 Hz by 30 s, hold 10 min, return to 50 Hz over 5 min."""
    f = np.full_like(t, 50.0)
    f = np.where((t >= 1) & (t < 5), 50 - 0.4 * (t - 1) / 4, f)
    f = np.where((t >= 5) & (t < 30), 49.6 + 0.25 * (t - 5) / 25, f)
    f = np.where((t >= 30) & (t < 630), 49.85, f)
    f = np.where((t >= 630) & (t < 930), 49.85 + 0.15 * (t - 630) / 300, f)
    return f


def freq_event() -> None:
    t = np.arange(0, 1200, DT)
    f = freq_profile(t)
    lines = ["a frequency event answered by the battery (4 % droop on 110 MW,",
             "0.02 Hz deadband, battery 20 MW, response tau 0.2 s; A-303):",
             "  service cap MW   peak MW   time to 90 % s   energy MWh   recovery min"]
    rows = []
    for cap in (20.0, 5.0):
        want = np.clip(ct.droop_power(f - 50.0, 110.0, 0.04, 0.02), -cap, cap)
        p = np.zeros_like(t)
        for k in range(1, len(t)):
            p[k] = p[k - 1] + DT * (want[k] - p[k - 1]) / 0.2
        e = np.sum(np.clip(p, 0, None)) * DT / 3600 / L["eta"]
        k90 = np.argmax(p >= 0.9 * want.max())
        t90 = t[k90] - t[np.argmax(want > 0)]
        rec = e / L["eta"] / 5.0 * 60           # refill at 5 MW from the plant
        lines.append(f"  {cap:14.0f}   {p.max():7.1f}   {t90:14.1f}   {e:10.2f}"
                     f"   {rec:12.0f}")
        if cap == 20.0:
            rows = [(f"{t[k]:.0f}", f"{f[k]:.3f}", f"{p[k]:.2f}")
                    for k in range(0, 9000, 20)]
    lines += ["  the droop asks 20.9 MW at the nadir: a 20 MW battery is at",
              "  its limit, a 5 MW service is cut to its contract; the energy",
              "  is small, the recovery (refill before the next event) is",
              "  what the energy floor and the plan must allow for"]
    emit("k_freq", lines)
    csv("ch20-freq.csv", "t,f,p", rows)


# [start: freeze]
def frt_loop(dip_s: float, mode: str, kp=1.5, ki=0.8, tau=2.0,
             dt=0.01, t_end=40.0):
    """Plant loop at its set point; at 10 s the units ride through a
    dip and give only 0.2 pu for dip_s seconds whatever the command.
    mode 'none': the PI keeps running; 'freeze': integral and command
    held during the dip; 'hold': also held until the units have
    recovered to 95 % of the command."""
    y, integ, u = 1.0, 1.0 / ki, 1.0
    held = False
    ys = []
    for k in range(int(t_end / dt)):
        t = k * dt
        dip = 10.0 <= t < 10.0 + dip_s
        if mode == "freeze":
            held = dip
        elif mode == "hold":
            held = dip or (held and y < 0.95 * u)
        if not held:
            e = 1.0 - y
            integ += e * dt
            u = kp * e + ki * integ
        y = 0.2 if dip else y + dt * (u - y) / tau
        ys.append(y)
    return np.array(ys)
# [end: freeze]


def frt() -> None:
    lines = ["plant loop through a voltage dip (units give 0.2 pu meanwhile):",
             "  dip s     mode   peak after dip pu   time above 1.02 s"]
    rows = {}
    for dip in (0.5, 1.5):
        for mode in ("none", "freeze", "hold"):
            y = frt_loop(dip, mode)
            after = y[int((10 + dip) / 0.01):]
            over = (after > 1.02).sum() * 0.01
            lines.append(f"  {dip:5.1f}   {mode:>6s}   {after.max():17.2f}"
                         f"   {over:17.1f}")
            if dip == 1.5:
                rows[mode] = y
    lines += ["  without a freeze the integral grows through the dip and the",
              "  overshoot grows with the dip; a freeze removes that part,",
              "  but the loop still reacts to the recovery itself; holding",
              "  until the units have recovered removes the overshoot: at an",
              "  export limit an overshoot is a breach of the cap right after",
              "  a grid fault (FRT coordination, ch 9 and ch 27)"]
    emit("k_frt", lines)
    csv("ch20-frt.csv", "t,none,freeze,hold",
        [(f"{k * 0.01:.2f}", f"{rows['none'][k]:.4f}", f"{rows['freeze'][k]:.4f}",
          f"{rows['hold'][k]:.4f}") for k in range(800, 2400, 5)])


def first_order(tau, delay, t):
    return np.where(t < delay, 0.0, 1 - np.exp(-(t - delay) / tau))


def validation() -> None:
    rng = np.random.default_rng(2020)
    t = np.arange(0, 20, 0.05)
    meas = first_order(2.6, 0.35, t) + 0.01 * rng.standard_normal(t.size)
    lines = ["validating the plant model against a measured step (teaching):",
             "  model                 tau s   delay s   mean |err| 0-10 s   steady err",
             ]

    def score(tau, d):
        m = first_order(tau, d, t)
        tr = np.abs(m - meas)[t < 10].mean()
        ss = abs(m[t > 15].mean() - meas[t > 15].mean())
        return tr, ss
    tr, ss = score(2.0, 0.0)
    lines.append(f"  design model          {2.0:5.2f}   {0.0:7.2f}   {tr:17.3f}   {ss:10.3f}")
    best = min(((score(a, d)[0], a, d) for a in np.arange(1.0, 4.01, 0.05)
                for d in np.arange(0.0, 1.01, 0.05)))
    tr2, ss2 = score(best[1], best[2])
    lines.append(f"  fitted to the step    {best[1]:5.2f}   {best[2]:7.2f}   {tr2:17.3f}   {ss2:10.3f}")
    lines += ["  teaching acceptance: mean |err| <= 0.02 in the transient,",
              "  <= 0.01 in steady state; the design model fails the first,",
              "  the fitted one passes and finds the slower plant (2.6 s) and",
              "  the measurement delay (0.35 s) that the tuning must respect;",
              "  real acceptance bands come from the grid study (ch 27-28)"]
    emit("k_validation", lines)


def imbalance_battery() -> None:
    act = np.clip(src.poc_actual(), 0, L["export_mw"])
    sch = np.clip(src.poc_forecast(4), 0, L["export_mw"])
    P = src.IMBALANCE
    e = 20.0
    out = act.copy()
    thr = 0.0
    for t in range(8760):
        dev = act[t] - sch[t]
        if dev < 0:                                   # short: discharge
            d = min(-dev, L["bess_mw"], (e - L["e_min"]) * L["eta"])
            e -= d / L["eta"]
            out[t] += d
            thr += d
        else:                                         # long: charge
            c = min(dev, L["bess_mw"], (L["e_max"] - e) / L["eta"])
            e += c * L["eta"]
            out[t] -= c
    base = ct.imbalance(sch, act, P["short"], P["long"])
    with_b = ct.imbalance(sch, out, P["short"], P["long"])
    efc = thr / (L["e_max"] - L["e_min"])
    lines = ["the battery used to absorb deviations from the intraday schedule:",
             f"  penalty without battery {base / 1000:,.0f} k u, with {with_b / 1000:,.0f} k u",
             f"  saved {(base - with_b) / 1000:,.0f} k u a year; {efc:.0f} equivalent full cycles",
             "  the same battery adds about 469 k u a year by shifting",
             "  (section D): absorbing deviations is worth a little less",
             "  here, and both use the whole window, so they cannot both be",
             "  done at full size - a stacking decision of section G, priced",
             "  in ch 21 with the real settlement rules (U-078)"]
    emit("k_imbalance", lines)


if __name__ == "__main__":
    freq_event()
    frt()
    validation()
    imbalance_battery()
