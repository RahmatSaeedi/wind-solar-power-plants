"""Chapter 48, round x: the 4-20 mA loop's voltage budget once an isolator
is added (lesson t), a tracker's stow trigger read from 3-second gusts or
from one-minute means, a meter's interval profile against its register,
firmware combinations never tested together, connector inspection before
mating, and the interval-start / interval-end label of metered energy.

Run from the project root:   python -m companion.ch48.examples_x
Writes companion/ch48/expected/x_*.txt and diagrams/data/ch48-gust.csv.
Teaching values (A-498 to A-505); defensive administration only.
"""
from __future__ import annotations

import numpy as np

from companion.ch48.common import csv, emit
from plantp import instrumentation as ins

# ------------------------------------------------ 1. loop budget with an isolator
LOOP_RUNS = {   # loop: (one-way length m, core mm2, isolator)
    "L-102": (1800, 0.75, True), "L-104": (2400, 0.5, True), "L-105": (600, 0.5, True),
}


def loop_budget(v_supply: float = 24.0, v_tx: float = 12.0, r_in: float = 250.0,
                v_iso: float = 4.0, i_max: float = 0.022, rho: float = 0.0175) -> dict:
    lines = [f"loop voltage at {i_max * 1000:.0f} mA: supply {v_supply:.0f} V, transmitter "
             f"needs {v_tx:.0f} V,",
             f"  input {r_in:.0f} ohm, the new isolator takes {v_iso:.0f} V (teaching values)",
             "  loop    length m  core mm2  cable ohm  left V  without isolator  max m"]
    out = {}
    for loop, (length, a, iso) in LOOP_RUNS.items():
        r_c = 2 * rho * length / a
        drop = i_max * (r_in + r_c)
        left = v_supply - (v_iso if iso else 0) - drop
        left0 = v_supply - drop
        lmax = ins.loop_max_length(v_supply - v_iso, v_tx, r_in, a, i_max, rho)
        out[loop] = (left, left0, lmax)
        lines.append(f"  {loop}  {length:8d}  {a:8.2f}  {r_c:9.0f}  {left:6.1f}  "
                     f"{left0:16.1f}  {lmax:5.0f}")
    bad = [k for k, (l, *_) in out.items() if l < v_tx]
    lines += [f"  short of {v_tx:.0f} V with the isolator: {', '.join(bad)}",
              "  the isolator that fixed lesson t's earth problem takes the",
              "  voltage the long thin loop needed: the transmitter browns out",
              "  near full scale and the reading sticks below the top - a",
              "  separately powered isolator or a larger core, checked on the",
              "  loop sheet before the change is built (ch 34 loop length)"]
    emit("x_loop", lines)
    return dict(out=out, bad=bad)


# ------------------------------------------------ 2. stow trigger: gust or mean
def gust(seed: int = 4803, trigger: float = 18.0, n: int = 600) -> dict:
    rng = np.random.default_rng(seed)
    u = np.empty(n)
    u[0] = 12.0
    for k in range(1, n):
        u[k] = 12.0 + 0.9 * (u[k - 1] - 12.0) + rng.normal(0, 1.1)
    for t0 in (190, 420):                               # two gust fronts
        u[t0:t0 + 9] += np.array([2, 4, 6, 7, 7, 6, 4, 2, 1])
    g3 = np.convolve(u, np.ones(3) / 3, mode="same")
    m60 = np.repeat(u.reshape(-1, 60).mean(axis=1), 60)
    csv("ch48-gust.csv", "t,g3,m60", [(k, round(g3[k], 2), round(m60[k], 2))
                                       for k in range(0, n, 2)])
    above = g3 > trigger
    events = int(np.sum(above[1:] & ~above[:-1]) + above[0])
    first = int(np.argmax(above)) if above.any() else None
    lines = [f"tracker stow on wind: trigger {trigger:.0f} m/s, ten minutes of 1-second "
             "wind (synthetic)",
             f"  3-second gust above the trigger: {events} "
             f"event{'s' if events != 1 else ''}, first at "
             f"t = {first} s, peak {g3.max():.1f} m/s",
             f"  one-minute means: highest {m60.max():.1f} m/s - never above the trigger",
             "  a controller that reads the logger's one-minute mean never",
             "  stows; the stow input is the gust the drive's torque was",
             "  checked against (ch 47 stow), and the averaging time is a",
             "  line in the instrument specification, tested at the FAT"]
    emit("x_gust", lines)
    return dict(events=events, peak=float(g3.max()), mean_max=float(m60.max()))


# ------------------------------------------------ 3. interval profile vs register
def profile(seed: int = 4804, missing=(1210, 1211, 1212, 1213, 2050, 2051)) -> dict:
    rng = np.random.default_rng(seed)
    n = 31 * 96
    t = np.arange(n)
    kwh = np.clip(8000 + 5000 * np.sin(t / 96 * 2 * np.pi - 1.2)
                  + rng.normal(0, 2500, n), 0, 25000)   # kWh a quarter hour
    register = kwh.sum() / 1000                         # MWh
    shown = np.delete(kwh, list(missing))
    gap = register - shown.sum() / 1000
    lines = [f"export meter, one month: {n} quarter-hour intervals in the profile, "
             f"{len(missing)} missing",
             f"  register difference over the month: {register:.1f} MWh",
             f"  sum of the profile as received:     {shown.sum() / 1000:.1f} MWh",
             f"  gap: {gap:.1f} MWh ({gap / register:.2%}) - the missing intervals' "
             "energy",
             "  the register is the energy, the profile its shape: the gap is",
             "  filled from the meter's own memory (re-read), not by",
             "  interpolation, and the six intervals are flagged in the",
             "  settlement file (ch 35 completeness)"]
    emit("x_profile", lines)
    return dict(register=register, gap=gap)


# ------------------------------------------------ 4. firmware combinations
TESTED = {("GW 2.3.0", "driver 5.1"), ("GW 2.3.0", "driver 5.2"), ("GW 2.2.4", "driver 5.1"),
          ("RTU 8.4", "driver 5.2"), ("RTU 8.3", "driver 5.1")}
INSTALLED_PAIRS = {"GW-PV1": ("GW 2.3.0", "driver 5.2"), "GW-PV2": ("GW 2.2.4", "driver 5.2"),
                   "RTU-1": ("RTU 8.4", "driver 5.2"), "RTU-2": ("RTU 8.3", "driver 5.2")}


def compat() -> list:
    bad = [(d, p) for d, p in INSTALLED_PAIRS.items() if p not in TESTED]
    lines = ["device firmware and SCADA driver: installed pairs against the",
             "  maker's tested combinations"]
    lines += [f"  {d:7s} {p[0]:9s} + {p[1]:10s} "
              f"{'tested' if p in TESTED else 'NOT TESTED'}"
              for d, p in INSTALLED_PAIRS.items()]
    lines += [f"  {len(bad)} pairs run untested: the driver moved to 5.2 for one",
              "  device and was rolled out to all; each version is in the",
              "  baseline (lesson C), but no single record held the pairs -",
              "  the compatibility matrix is a configuration item too"]
    emit("x_compat", lines)
    return bad


# ------------------------------------------------ 5. connector inspection
def connectors(seed: int = 4805, trials: int = 20000, n_conn: int = 4,
               allowance: float = 0.5) -> dict:
    rng = np.random.default_rng(seed)
    out = {}
    for name, p_dirty in (("mate as received", 0.12), ("inspect, clean, mate", 0.01)):
        clean = rng.normal(0.25, 0.08, (trials, n_conn)).clip(0.05)
        dirty = rng.random((trials, n_conn)) < p_dirty
        loss = clean + dirty * rng.normal(0.6, 0.3, (trials, n_conn)).clip(0.1)
        fail = float((loss.sum(axis=1) > n_conn * allowance).mean())
        out[name] = fail
    lines = [f"links of {n_conn} connectors against an allowance of {allowance} dB each "
             f"({trials:,} trials)",
             "  practice                fails the allowance"]
    lines += [f"  {k:22s}  {v:8.2%}" for k, v in out.items()]
    lines += ["  a dirty end-face adds more than the allowance it was given;",
              "  inspecting each end before mating cuts the failed links",
              f"  about {out['mate as received'] / max(out['inspect, clean, mate'], 1e-9):.0f}"
              "-fold - and a mated dirty face can scratch the clean one,",
              "  so the inspection is a step of the procedure, not a repair"]
    emit("x_connectors", lines)
    return out


# ------------------------------------------------ 6. interval start or end
def labels(seed: int = 4806) -> dict:
    rng = np.random.default_rng(seed)
    q = np.arange(96)
    mwh = np.clip(15 + 8 * np.sin((q - 20) / 96 * 2 * np.pi) + rng.normal(0, 2, 96), 0, 25)
    price = np.where((q >= 68) & (q < 84), 90.0, np.where((q >= 28) & (q < 64), 40.0, 55.0))
    right = float((mwh * price).sum())
    shifted = float((mwh[:-1] * price[1:]).sum())       # each value one interval late
    moved = float(mwh[-1])                              # last interval falls into tomorrow
    lines = ["a day of quarter-hour export, labelled by interval END (settlement)",
             "  or by interval START (an exporter's default), price bands by hour",
             f"  value with the right labels: {right:,.0f} u",
             f"  value with every interval one step late: {shifted:,.0f} u "
             f"({shifted - right:+,.0f} u)",
             f"  energy moved into the next day at midnight: {moved:.1f} MWh",
             "  the error is small on a day and systematic over a year, and",
             "  every price change hour carries it; the label convention is",
             "  written in the metering specification and checked on the",
             "  first exported file, interval by interval"]
    emit("x_labels", lines)
    return dict(right=right, diff=shifted - right, moved=moved)


if __name__ == "__main__":
    loop_budget()
    gust()
    profile()
    compat()
    connectors()
    labels()
