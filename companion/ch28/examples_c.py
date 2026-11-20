"""Chapter 28, lesson C: dynamic and compliance studies - ride-through at
the strong and the weak POC, a frequency event on a large and a small
system, the stability of the POC voltage controller against grid
strength, islanding and the passive relays' blind zone over a year,
reconnection, set-point following and the telemetry latency budget.

Run from the project root:   python -m companion.ch28.examples_c
Writes companion/ch28/expected/c_*.txt and diagrams/data/ch28-*.csv.
Teaching values and placeholder requirements (A-343, A-344; U-102).
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import csv, emit
from plantp import gridstudy as gs

S_PLANT = 122.2          # MVA of the S0 units (12 x 5.6 + 10 x 5.5)


def envelope(t: np.ndarray, t0: float = 0.1) -> np.ndarray:
    """Teaching ride-through envelope (a placeholder for REQ-G04): stay
    connected above it. 0.15 pu for 150 ms, then a line to 0.85 at 1.5 s."""
    tt = t - t0
    return np.where(tt < 0, 0.0, np.where(tt < 0.15, 0.15,
                    np.where(tt < 1.5, 0.15 + (0.85 - 0.15) * (tt - 0.15) / 1.35, 0.85)))


def frt() -> None:
    t = np.arange(0, 1.5, 0.001)
    e = np.where((t >= 0.1) & (t < 0.25), 0.20, 1.0)
    p0 = 100 / S_PLANT
    lines = ["ride-through: grid source dips to 0.20 pu for 150 ms (teaching case)",
             "  grid   k   U POC in dip   Q peak MVAr   P back to 90 % after clear s",
             ]
    keep = {}
    for g in ("max", "min"):
        z = gs.thevenin(src.GRID[g]["s_sc"], src.GRID[g]["xr"], S_PLANT)
        for k in (0.0, 2.0):
            out = gs.frt_sim(t, e, z, p0, k=k)
            in_dip = (t > 0.15) & (t < 0.25)
            after = t >= 0.25
            p90 = t[after][np.argmax(out["p"][after] >= 0.9 * p0)] - 0.25
            lines.append(f"  {g:4s}  {k:3.0f}   {out['u'][in_dip].mean():12.2f}   "
                         f"{out['q'][in_dip].max() * S_PLANT:11.0f}   {p90:28.2f}")
            keep[(g, k)] = out
    env = envelope(t)
    ok = all(np.all(o["u"] >= env - 1e-9) for o in keep.values())
    csv("ch28-frt.csv", "t,env,u0,u2,p2",
        [(f"{a:.3f}", f"{b:.3f}", f"{c:.3f}", f"{d:.3f}", f"{f_:.3f}")
         for a, b, c, d, f_ in zip(t[::5], env[::5], keep[("min", 0.0)]["u"][::5],
                                   keep[("min", 2.0)]["u"][::5], keep[("min", 2.0)]["p"][::5])])
    lines += [f"  POC voltage above the teaching envelope in every case: {'yes' if ok else 'NO'}",
              "  the plant's reactive current lifts the POC more on the weak",
              "  grid; active power returns at the set ramp once the voltage",
              "  is back - the study shows the plant stays connected and how",
              "  it behaves, the unit type test shows the unit can do it"]
    emit("c_frt", lines)


def frequency() -> None:
    t = np.arange(0, 30, 0.01)
    cases = {"large (20 GW, H 4, -1,000 MW)": (20000, 4.0, 1000.0),
             "small (2 GW, H 3, -150 MW)": (2000, 3.0, 150.0)}
    plants = {"no response": None,
              "PV held 10 MW down": (100, 0.05, 0.2, 10.0, 1.0),
              "battery 20 MW (S1)": (100, 0.05, 0.2, 20.0, 0.5)}
    lines = ["a frequency event: loss of generation, 20 % of the system on 5 % droop",
             "  system                         plant response        nadir Hz   RoCoF Hz/s"]
    rows = {}
    for cname, (s, h, loss) in cases.items():
        for pname, pl in plants.items():
            o = gs.freq_event(t, s, h, loss, gov=(0.05, 6.0, 0.2), plant=pl)
            lines.append(f"  {cname:30s} {pname:20s}  {o['nadir']:8.3f}   {o['rocof']:10.3f}")
            if cname.startswith("small"):
                rows[pname] = o["f"]
    over = gs.freq_event(t, 2000, 3.0, -150.0, gov=(0.05, 6.0, 0.2),
                         plant=(100, 0.05, 0.2, 0.0, 1.0, 100.0))
    over0 = gs.freq_event(t, 2000, 3.0, -150.0, gov=(0.05, 6.0, 0.2))
    csv("ch28-freq.csv", "t,none,pv,bess",
        [(f"{a:.2f}", *(f"{rows[k][i]:.4f}" for k in plants)) for i, a in enumerate(t) if i % 10 == 0])
    lines += [f"  over-frequency (small system loses 150 MW of load): peak"
              f" {over0['f'].max():.3f} Hz without,",
              f"  {over['f'].max():.3f} Hz with the plant reducing on its 5 % droop",
              "  on a large system the plant changes the nadir by hundredths",
              "  of a hertz; on a small one by tenths - and only with",
              "  headroom: at full output without a battery it can help",
              "  only upwards in frequency (by reducing), never downwards"]
    emit("c_freq", lines)


# [start: vcontrol]
def v_loop(s_sc: float, ki: float, t_end: float = 8.0, dt: float = 0.005,
           delay: float = 0.10, t_meas: float = 0.05, t_unit: float = 0.15):
    """POC voltage after a -2 % grid step at 1 s, with an integral
    controller (ki Mvar per pu per s) acting through a delay and lags."""
    n = int(t_end / dt)
    buf = [0.0] * int(delay / dt)
    v_m = q = integ = 0.0
    out = []
    for k in range(n):
        v_grid = -0.02 if k * dt >= 1.0 else 0.0
        v = v_grid + q / s_sc                     # pu deviation at the POC
        v_m += (v - v_m) * dt / t_meas            # measurement filter
        integ += -ki * v_m * dt                   # Mvar
        integ = min(max(integ, -46.0), 46.0)      # capability (lesson B)
        buf.append(integ)
        q += (buf.pop(0) - q) * dt / t_unit       # units follow late
        out.append(v)
    return np.arange(n) * dt, np.array(out)
# [end: vcontrol]


def vcontrol() -> None:
    lines = ["POC voltage control after a -2 % grid step (integral controller)",
             "  case                         ki Mvar/pu/s   overshoot %   settles (10 %) s"]
    curves = {}
    for name, s_sc, ki in (("SCR 15, tuned for it", 1500, 1500.0),
                           ("SCR 3, same gains", 300, 1500.0),
                           ("SCR 3, retuned", 300, 300.0)):
        t, v = v_loop(s_sc, ki)
        after = t >= 1.0
        rec = v[after]
        over = max(0.0, rec.max()) / 0.02 * 100
        band = np.abs(rec) > 0.1 * 0.02                # outside 10 % of the step
        settle = t[after][np.nonzero(band)[0][-1]] - 1.0
        lines.append(f"  {name:28s} {ki:12.0f}   {over:11.0f}   {settle:16.1f}")
        curves[name] = v
    csv("ch28-vcontrol.csv", "t,s15,s3,s3r",
        [(f"{a:.2f}", *(f"{100 * curves[k][i]:.3f}" for k in curves)) for i, a in enumerate(t) if i % 4 == 0])
    lines += ["  the same gains that settle smoothly on the strong grid ring",
              "  on the weak one: the grid's voltage sensitivity (1/S_sc) is",
              "  part of the loop gain - controller settings are studied at",
              "  the minimum strength and retuned (or scheduled) for it"]
    emit("c_vcontrol", lines)


def islanding() -> None:
    from companion.ch15 import sources as s15
    from companion.ch17 import sources as s17
    d = gs.ndz(0.85, 1.10, 49.0, 51.0, 1.0)
    p_plant = s15.plant_year()["delivered"]
    p_load = s17.regional()["total"]
    ratio = (p_load - p_plant) / p_load
    inside = (ratio >= d["dp"][0]) & (ratio <= d["dp"][1]) & (p_plant > 1.0)
    hist, edges = np.histogram(np.clip(ratio, -3, 1), bins=40, range=(-3, 1))
    csv("ch28-ndz.csv", "x,n", [(f"{(a + b) / 2:.3f}", n) for a, b, n in zip(edges[:-1], edges[1:], hist)])
    lines = ["could the plant and the regional load form an undetected island?",
             "  (the grid substation's 132 kV supply opens; passive relays only)",
             f"  blind zone for dP/P: {d['dp'][0]:+.3f} to {d['dp'][1]:+.3f} (U 0.85-1.10 pu);",
             f"  for dQ/P: {d['dq'][0]:+.3f} to {d['dq'][1]:+.3f} (f 49-51 Hz, quality factor 1)",
             f"  hours of the year with the active-power mismatch inside it: {int(inside.sum())}",
             f"  regional load {p_load.min():.0f}-{p_load.max():.0f} MW, plant 0-{p_plant.max():.0f} MW",
             "  in those hours voltage relays alone may not see the island",
             "  (frequency relays only if reactive power is also matched);",
             "  an intertrip from the grid substation's breaker closes the",
             "  gap whatever the balance - the study states which scheme",
             "  the operator requires (REQ-G12)"]
    emit("c_islanding", lines)


def restore() -> None:
    lines = ["reconnection, set-point following and telemetry (teaching values)"]
    wait_s, ramp_pct_min, p_before = 60.0, 10.0, 80.0
    ramp_min = p_before / (ramp_pct_min / 100 * 100)
    lost = p_before * (wait_s / 3600) + 0.5 * p_before * ramp_min / 60
    lines += [f"  after a trip: {wait_s:.0f} s of healthy voltage and frequency, then"
              f" {ramp_pct_min:.0f} %/min",
              f"  back to {p_before:.0f} MW in {ramp_min:.0f} min; energy lost per trip about"
              f" {lost:.1f} MWh (+ the outage)"]
    t = np.arange(0, 200, 1.0)
    sp = np.where(t < 20, 80.0, 60.0)
    p, delay = [], 4
    cur = 80.0
    for k in range(len(t)):
        target = sp[max(k - delay, 0)]
        cur += max(min(target - cur, 10.0 / 60), -10.0 / 60)
        p.append(cur)
    p = np.array(p)
    inside = np.abs(p - 60.0) <= 0.02 * 100
    t_in = t[np.argmax(inside & (t > 20))] - 20
    lines += ["  set-point 80 -> 60 MW at 20 s, ramp 10 MW/min, 4 s delay:",
              f"  inside +/-2 MW after {t_in:.0f} s",
              "  (a placeholder requirement of 60 s would fail: the ramp",
              "  limit itself takes 2 min - the two requirements must agree)"]
    budget = {"unit/RTU scan": 1.0, "plant gateway": 0.2, "communications": 0.3,
              "operator SCADA processing": 0.5}
    tot = sum(budget.values())
    lines += ["  telemetry latency budget, s:"]
    lines += [f"    {k:28s} {v:4.1f}" for k, v in budget.items()]
    lines += [
              f"  total {tot:.1f} s against a placeholder requirement of 2.0 s: no margin -",
              "  an end-to-end test measures it; the budget shows where to cut"]
    emit("c_restore", lines)


def model_check() -> None:
    """A recorded dip against the plant model: the 'measured' record is
    a slightly different plant (faster current, k 2.2) plus noise."""
    rng = np.random.default_rng(282)
    t = np.arange(0, 1.0, 0.001)
    e = np.where((t >= 0.1) & (t < 0.25), 0.30, 1.0)
    z = gs.thevenin(1200, 7, S_PLANT)
    sim = gs.frt_sim(t, e, z, 0.7, k=2.0, tau=0.02)
    meas = gs.frt_sim(t, e, z, 0.7, k=2.2, tau=0.012)
    windows = {"pre-fault": (0.0, 0.1), "fault": (0.1, 0.25), "post-fault": (0.25, 1.0)}
    lines = ["model against a recorded dip: errors of reactive current (pu)",
             "  window       mean error   mean abs error   max error   teaching limits"]
    lim = {"pre-fault": (0.02, 0.05), "fault": (0.10, 0.20), "post-fault": (0.05, 0.15)}
    m = meas["q"] + 0.01 * rng.standard_normal(len(t))
    err = gs.validation_errors(t, sim["q"], m, windows)
    for w, v in err.items():
        ok = v["mae"] <= lim[w][0] and v["mxe"] <= lim[w][1]
        lines.append(f"  {w:11s}  {v['me']:+10.3f}   {v['mae']:14.3f}   {v['mxe']:9.3f}"
                     f"   {lim[w][0]:.2f} / {lim[w][1]:.2f} {'ok' if ok else 'OVER'}")
    lines += ["  errors are judged window by window: the means are small,",
              "  but the maximum after clearing is not - on site the",
              "  current falls faster than in the model; a mean alone",
              "  would hide it. The fix is a better current-loop time",
              "  constant from the OEM, then a rerun; a validation method",
              "  of this kind (STD-132) sets windows and measures, the",
              "  windows and limits here are teaching values"]
    emit("c_modelcheck", lines)


if __name__ == "__main__":
    frt()
    frequency()
    vcontrol()
    islanding()
    restore()
    model_check()
