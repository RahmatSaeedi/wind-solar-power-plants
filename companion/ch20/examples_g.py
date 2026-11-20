"""Chapter 20, more control theory and plant design: a controller that
runs at a sample period, a cascade of an outer plant loop on an inner
device loop, POC voltage control against grid strength, sharing a
reactive set point among the units, the delay budget of the control
path, and the availability of single and duplicated plant controllers.

Run from the project root:   python -m companion.ch20.examples_g
Writes companion/ch20/expected/g_*.txt and diagrams/data/ch20-*.csv.
Teaching values A-299 and A-303.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch20.common import csv, emit
from plantp import control as ct


# [start: sampled]
def sampled_pi(kp, ki, tau, ts, t_end=40.0, dt=0.01):
    """PI controller updated every ts seconds (command held between
    updates) on a first-order plant integrated with a fine step."""
    y = u = integ = 0.0
    every = max(1, int(round(ts / dt)))
    ys = []
    for k in range(int(t_end / dt)):
        if k % every == 0:
            e = 1.0 - y
            integ += e * ts
            u = kp * e + ki * integ
        y += dt * (u - y) / tau
        ys.append(y)
    return np.array(ys)
# [end: sampled]


def sampling() -> None:
    lines = ["the tuned and the aggressive PI run at a sample period ts:",
             "  tuning             ts s   overshoot %   settle 2 % s"]
    for name, kp, ki in (("tuned (1.5, 0.8)", 1.5, 0.8), ("aggressive (6, 8)", 6.0, 8.0)):
        for ts in (0.05, 0.2, 0.5, 1.0):
            y = sampled_pi(kp, ki, 2.0, ts)
            t = np.arange(1, len(y) + 1) * 0.01
            over = max(0.0, (y.max() - 1) * 100)
            out = np.where(np.abs(y - 1) > 0.02)[0]
            settle = t[out[-1]] if len(out) else 0.0
            txt = f"{over:11.1f}" if over < 500 else "   unstable"
            lines.append(f"  {name:18s} {ts:4.2f}   {txt}   {settle:12.1f}")
    lines += ["  holding the command between updates acts like a delay of",
              "  about half a period: the tuned loop does not notice even 1 s,",
              "  the aggressive one overshoots 122 % at 0.5 s and fails at",
              "  1 s; the controller's cycle time belongs in the delay budget"]
    emit("g_sampling", lines)


# [start: cascade]
def cascade(tau_out: float, tau_in: float, t_end=40.0, dt=0.005):
    """Outer integral loop (closed-loop time constant tau_out if the
    inner loop were instant) on an inner loop that answers with tau_in."""
    ki = 1.0 / tau_out
    y = integ = 0.0
    ys = []
    for _ in range(int(t_end / dt)):
        integ += (1.0 - y) * dt
        u = ki * integ
        y += dt * (u - y) / tau_in
        ys.append(y)
    return np.array(ys)
# [end: cascade]


def cascades() -> None:
    lines = ["outer loop on an inner loop: ratio of their time constants:",
             "  tau_out/tau_in   zeta (formula)   overshoot % (formula)   (simulated)"]
    rows = []
    for r in (20, 5, 2, 1, 0.5):
        y = cascade(r * 0.2, 0.2)
        z = 0.5 * math.sqrt(r)
        os_f = 100 * math.exp(-math.pi * z / math.sqrt(1 - z * z)) if z < 1 else 0.0
        os_s = max(0.0, (y.max() - 1) * 100)
        lines.append(f"  {r:14.1f}   {z:14.2f}   {os_f:21.1f}   {os_s:11.1f}")
        rows.append((r, f"{os_s:.2f}"))
    lines += ["  zeta = 0.5 sqrt(ratio): the outer loop must be about four",
              "  times slower than the inner one to avoid overshoot; this is",
              "  the 'separation of time scales' of the hierarchy in numbers"]
    emit("g_cascade", lines)
    csv("ch20-cascade.csv", "r,os", rows)


def voltage() -> None:
    """POC voltage with a Thevenin grid on a 100 MVA base: dV = R P + X Q
    (pu, generator convention), and the Q-V droop closing the loop."""
    lines = ["POC voltage rise and the Q-V droop against grid strength:",
             "  SCR   X/R   dV at 100 MW, Q=0 %   Q for dV=0 Mvar   droop factor"]
    rows = []
    for scr, xr in ((10, 5), (6, 5), (3, 5), (6, 2), (3, 2)):
        z = 1.0 / scr
        x = z * xr / math.sqrt(1 + xr * xr)
        r = z / math.sqrt(1 + xr * xr)
        dv = r * 1.0 * 100
        q0 = -r / x * 100
        factor = 1 / (1 + x * 0.33 / 0.04)
        lines.append(f"  {scr:3d}   {xr:3d}   {dv:19.2f}   {q0:15.1f}   {factor:12.2f}")
        rows.append((scr, xr, f"{dv:.2f}", f"{q0:.1f}"))
    lines += ["  the Q needed to cancel the rise depends on R/X only; the",
              "  rise itself and the droop's effect depend on grid strength:",
              "  in a weak grid the same droop removes more of a deviation but",
              "  the loop gain X Qmax / s_q is higher - a reason why the slope",
              "  and the response time are set with the grid study (ch 28);",
              "  with X/R = 2 the plant must absorb 50 Mvar at full output:",
              "  beyond its capability at 100 MW (section B)"]
    emit("g_voltage", lines)


def qshare() -> None:
    lines = ["sharing a reactive set point among the units by capability:",
             "  plant P  battery P  ask Mvar   WTG     PV   BESS   met"]
    for p, pb, ask in ((60, 0, 20), (100, 0, 30), (100, 20, 30), (110, 20, 40)):
        frac = (p - pb) / 110.0
        wtg = 12 * float(ct.q_limit(frac * 5.0, 5.6, 0.33))
        pv = 10 * float(ct.q_limit(frac * 5.0, 5.5, 0.33))
        bess = 4 * float(ct.q_limit(pb / 4, 5.5, 1.0))
        cap = wtg + pv + bess
        k = min(1.0, ask / cap)
        lines.append(f"  {p:7d}  {pb:9d}  {ask:8d}  {k * wtg:5.1f}  {k * pv:5.1f}"
                     f"  {k * bess:5.1f}   {'yes' if k < 1 else 'no':>3s}")
    lines += ["  (at the units, before the losses of chapter 18)",
              "  shares proportional to capability keep every unit equally",
              "  far from its limit; a discharging battery has little Mvar",
              "  left: at 20 MW its 4 x 5.5 MVA give 9.2 Mvar instead of 22"]
    emit("g_qshare", lines)


def latency() -> None:
    parts = [("measurement transducer", 20), ("measurement filter", 100),
             ("PPC cycle (half, average)", 50), ("network PPC -> park ctrl", 50),
             ("park controller cycle (half)", 25), ("network -> inverters", 20),
             ("inverter response", 50)]
    tot = sum(v for _, v in parts)
    lines = ["delay budget of the plant control path (teaching, A-303):",
             "  part                            ms"]
    lines += [f"  {k:30s} {v:4d}" for k, v in parts]
    lines += [f"  total                          {tot:4d}",
              "  against the 500 ms the tuned loop tolerates: margin "
              f"{500 - tot} ms",
              "  a SCADA path polled every 2 s instead of a direct link adds",
              "  about 1,000 ms on average: the plant loop would need slower",
              "  gains; budget each part, then measure the whole at site"]
    emit("g_latency", lines)


def availability() -> None:
    mtbf, mttr, cover = 50_000.0, 24.0, 0.98
    lam = 8760 / mtbf
    single = lam * mttr
    dual = lam * (1 - cover) * mttr + lam * (mttr / mtbf) * mttr
    lines = ["plant controller availability (teaching: MTBF 50,000 h, MTTR 24 h):",
             f"  failures a year {lam:.3f}",
             f"  single controller: {single:.2f} h a year in fallback",
             f"  duplicated, switchover succeeds {cover * 100:.0f} %: {dual:.3f} h a year",
             f"  REQ-S01 window hours lost (single): {single * 4 / 24:.2f} a year",
             "  a controller fault matters less than the comms outages of",
             "  lab E (18 h a year); but a duplicated pair is only as good as",
             "  its switchover test and identical settings (fingerprints)"]
    emit("g_availability", lines)


if __name__ == "__main__":
    sampling()
    cascades()
    voltage()
    qshare()
    latency()
    availability()
