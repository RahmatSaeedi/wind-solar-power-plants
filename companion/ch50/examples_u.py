"""Chapter 50, round u: the main transformer's differential at first load,
the measured earth-grid resistance and its rise of potential, the
power-quality week at the POC, data retention at handover, and the call
tree of the emergency plan timed.

Run from the project root:   python -m companion.ch50.examples_u
Writes companion/ch50/expected/u_*.txt.
Teaching values (A-514 to A-521).
"""
from __future__ import annotations

import numpy as np

from companion.ch50.common import emit
from plantp import protection


# ------------------------------------------------ 1. differential at first load
def differential(load_pu: float = 0.30, pickup: float = 0.20) -> dict:
    cases = {"CTs as designed": (load_pu, load_pu),
             "one LV CT set reversed": (load_pu, -load_pu),
             "LV CT ratio one step off": (load_pu, load_pu * 0.92)}
    lines = [f"main transformer T1 differential at first load ({load_pu:.0%} of rating);",
             f"  pickup {pickup} pu (ch 26 teaching setting)",
             "  case                       HV pu   LV pu   differential pu"]
    out = {}
    for k, (a, b) in cases.items():
        d = abs(a - b)
        out[k] = d
        lines.append(f"  {k:26s} {a:6.2f}  {b:6.2f}  {d:9.2f}"
                     + ("  TRIPS" if d > pickup else ""))
    lines += ["  a reversed CT doubles the load into the differential: at 30 %",
              "  load it would trip; the commissioning reading at low load",
              "  (the relay's own differential and restraint values) finds",
              "  it before the load does - the same lesson as ch 48's meter"]
    emit("u_diff", lines)
    return out


# ------------------------------------------------ 2. earth grid measured
def earth(r_design: float = 0.50, r_meas: float = 0.62, i_grid_ka: float = 3.0,
          gpr_limit_kv: float = 1.6) -> dict:
    g1 = protection.gpr(i_grid_ka * 1000, r_design) / 1000
    g2 = protection.gpr(i_grid_ka * 1000, r_meas) / 1000
    lines = ["substation earth grid: measured resistance against the design (ch 26)",
             f"  design {r_design} ohm, measured {r_meas} ohm (dry season)",
             f"  rise of potential at {i_grid_ka} kA into the grid: {g1:.2f} kV designed,",
             f"  {g2:.2f} kV measured",
             f"  against the {gpr_limit_kv} kV the touch and step study allowed (teaching): "
             f"{'over' if g2 > gpr_limit_kv else 'inside'}",
             "  the study is rerun with the measured value (and the wet",
             "  season's), and the remedy - more electrodes, a surface",
             "  layer - designed by the earthing engineer, not chosen on",
             "  site; the measurement method is the approved one (ch 26)"]
    emit("u_earth", lines)
    return dict(g2=g2, over=g2 > gpr_limit_kv)


# ------------------------------------------------ 3. power-quality week
def pq_week(seed: int = 5003, limit: float = 3.0) -> dict:
    rng = np.random.default_rng(seed)
    n = 7 * 144                                       # 10-minute values
    day = (np.arange(n) % 144) / 144
    thd = 1.4 + 1.1 * np.clip(np.sin((day - 0.25) * 2 * np.pi), 0, None) + rng.normal(0, 0.15, n)
    thd[700:720] += 1.7                               # a capacitor bank switched nearby
    p95 = float(np.percentile(thd, 95))
    mx = float(thd.max())
    at = int(thd.argmax())
    in_event = 700 <= at < 720
    lines = [f"voltage THD at the POC over the compliance week ({n} ten-minute values)",
             f"  95th percentile {p95:.2f} %, maximum {mx:.2f} %; teaching limit "
             f"{limit} % (ch 27)",
             f"  - the week {'passes' if p95 <= limit else 'FAILS'} on its 95th percentile;"
             " the maximum",
             f"  came on day {at // 144 + 1} at {at % 144 // 6:02d}:{at % 6 * 10:02d}"
             + (" with a capacitor bank switched in the network," if in_event else ","),
             "  not a plant step - the background measured before connection",
             "  (ch 27) is what separates the two"]
    emit("u_pq", lines)
    return dict(p95=p95, mx=mx)


# ------------------------------------------------ 4. data retention
RETENTION = {   # data: (kept, required) in years
    "1-second plant data": (1, 1), "10-minute SCADA history": (5, 25),
    "event and alarm logs": (10, 10), "revenue metering": (10, 10),
    "test records and certificates": (25, 25), "configuration backups": (2, 25),
}


def retention() -> list:
    short = [(k, a, b) for k, (a, b) in RETENTION.items() if a < b]
    lines = ["retention configured at handover against the owner's requirement (years)"]
    lines += [f"  {k:30s} kept {a:2d}  required {b:2d}" + ("  SHORT" if a < b else "")
              for k, (a, b) in RETENTION.items()]
    lines += ["  the 10-minute history feeds every performance claim of the",
              "  plant's life (ch 37), and old configurations are the only",
              "  record of what was changed (ch 36) - retention is set",
              "  before the first year is lost, not after (ch 35)"]
    emit("u_retention", lines)
    return short


# ------------------------------------------------ 5. call tree
CALLS = [   # caller, callee, minutes to reach
    ("control room", "incident controller", 2), ("incident controller", "first-aid lead", 3),
    ("incident controller", "fire warden lead", 4), ("control room", "fire service", 3),
    ("incident controller", "network operator", 6), ("first-aid lead", "hospital", 9),
    ("incident controller", "community liaison", 14),
]


def call_tree() -> dict:
    reach = {"control room": 0}
    for a, b, m in CALLS:
        reach[b] = reach[a] + m
    last = max(reach, key=reach.get)
    lines = ["call-tree test from the control room (minutes until each answered)"]
    lines += [f"  {k:22s} {v:3d}" for k, v in reach.items() if k != "control room"]
    lines += [f"  everyone reached in {reach[last]} min; last: {last}",
              "  the hospital took 9 minutes on the stale number of lesson J;",
              "  the tree is tested with the night roster too, which has no",
              "  incident controller yet"]
    emit("u_calls", lines)
    return dict(reach=reach, last=last)


if __name__ == "__main__":
    differential()
    earth()
    pq_week()
    retention()
    call_tree()
