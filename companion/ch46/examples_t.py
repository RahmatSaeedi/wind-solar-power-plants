"""Chapter 46, round t: the cable maker's resistance capability, the
voltage at a trip coil at the end of the battery's discharge, the
line-up's DC demand against ch 23, spare terminals, nameplates against
positions, and as-laid lengths against the schedule.

Run from the project root:   python -m companion.ch46.examples_t
Writes companion/ch46/expected/t_*.txt and diagrams/data/ch46-*.csv.
Teaching values (A-483, A-485, A-486, A-488); no test procedure.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch23 import sources as s23
from companion.ch24 import sources as s24
from companion.ch46 import sources as src
from companion.ch46.common import csv, emit
from plantp import cables as cb
from plantp import quality as q


# ------------------------------------------------ 1. resistance capability
def capability(seed: int = 4601, n: int = 30) -> dict:
    rng = np.random.default_rng(seed)
    r20 = list(np.round(rng.normal(0.07760, 0.00030, n), 5))
    m, s, _, cpk = q.cp_cpk(r20, None, src.R20_MAX)
    over = sum(1 for x in r20 if x > src.R20_MAX)
    ppm = q.ppm_out(m, s, None, src.R20_MAX)
    m_need = src.R20_MAX - 4 * s
    edges = [0.0766 + 0.0001 * k for k in range(21)]
    counts = np.histogram(r20, bins=edges)[0]
    csv("ch46-cpk.csv", "r,n", [(round((a + b) / 2 * 1e3, 3), int(c))
                                for a, b, c in zip(edges, edges[1:], counts)])
    lines = [f"conductor resistance of the maker's last {n} drums of 400 mm2, at 20 C",
             f"  mean {m:.5f}, sd {s:.5f} ohm/km; limit {src.R20_MAX}",
             f"  Cpk {cpk:.2f}; expected over the limit {ppm / 1e4:.1f} %; "
             f"found {over} of {n}",
             f"  a Cpk of 1.33 would need the mean at {m_need:.5f} ohm/km",
             "  D403 and D406 of lesson A are this process's expected tail:",
             "  the maker runs its conductor close to the limit to save",
             "  aluminium; D404 at 0.0810 lies far outside it - a different",
             "  cause (wrong conductor or wrong report: its test was dated",
             "  before it was made); the supplier audit asks where the",
             "  process is centred, and the purchase specification can ask",
             "  for the capability (ch 39)"]
    emit("t_capability", lines)
    return dict(m=m, s=s, cpk=cpk, ppm=ppm, over=over, m_need=m_need)


# ------------------------------------------------ 2. voltage at the trip coil
def coil_voltage(v_end: float = 94.0, i_coil: float = 5.0, run_m: float = 40.0,
                 v_min_share: float = 0.70, v_nom: float = 110.0) -> dict:
    rho = 0.0172                                     # ohm mm2/m, copper
    v_min = v_min_share * v_nom
    lines = [f"voltage at a trip coil at the end of the battery's discharge "
             f"({v_end:.0f} V, teaching)",
             f"  coil {i_coil:.0f} A, {run_m:.0f} m from the DC board (there and "
             f"back); coil needs {v_min:.0f} V",
             "  wire mm2   drop V   at the coil V   margin V"]
    out = {}
    for a in (0.75, 1.5, 2.5):
        drop = i_coil * rho * 2 * run_m / a
        v = v_end - drop
        out[a] = (drop, v)
        lines.append(f"  {a:8.2f}   {drop:6.1f}   {v:13.1f}   {v - v_min:8.1f}")
    two = v_end - 2 * out[0.75][0]
    lines += ["  every size works on one coil; the 0.75 mm2 wire of lesson C",
              f"  (wire 112) cuts the margin from {out[1.5][1] - v_min:.1f} V (the "
              f"rule's 1.5 mm2) to {out[0.75][1] - v_min:.1f} V;",
              f"  two coils on one shared 0.75 mm2 wire leave {two:.1f} V, below "
              f"the coil's {v_min:.0f} V -",
              "  the coil's minimum voltage, the battery's end voltage and",
              "  the wire are one calculation, kept with the panel's records",
              "  (ch 23 DC system)"]
    emit("t_coil", lines)
    return out


# ------------------------------------------------ 3. DC demand of the line-up
def dc_demand(coils: int = 2, i_coil: float = 5.0, t_coil: float = 0.06,
              motor_a: float = 8.0, t_motor: float = 12.0,
              relay_w: float = 25.0, v: float = 110.0) -> dict:
    n = len(src.PANELS)
    trip_peak = n * coils * i_coil
    motor_peak = n * motor_a
    standby = n * relay_w / v
    first = s23.DC_DUTY[0][0]
    last = s23.DC_DUTY[-1][0]
    stand = s23.DC_DUTY[1][0]
    lines = [f"DC demand of the {n}-panel line-up from the makers' data (teaching)",
             f"  all breakers trip at once: {trip_peak:.0f} A for {t_coil * 1000:.0f} ms "
             f"(ch 23 first minute: {first:.0f} A)",
             f"  all springs recharge at once: {motor_peak:.0f} A for {t_motor:.0f} s "
             f"(ch 23 last minute: {last:.0f} A)",
             f"  relays standing: {standby:.1f} A of ch 23's {stand:.0f} A standing load",
             "  the switchgear's peaks fit inside ch 23's duty cycle; its",
             "  standing share is small - the battery is sized by the rest",
             "  of the plant, but the peaks set the cable from the DC board",
             "  and the voltage at each coil (t_coil)"]
    emit("t_dc", lines)
    return dict(trip=trip_peak, motor=motor_peak, standby=standby)


# ------------------------------------------------ 4. spare terminals
TERMINALS = {"INC-A": (180, 152), "WS1": (120, 95), "WS2": (120, 112),
             "PVF3": (120, 96), "BESS-A": (140, 131), "BC": (100, 80),
             "INC-B": (180, 150), "WS3": (120, 96), "PVF1": (120, 99),
             "PVF2": (120, 101), "BESS-B": (140, 118), "SST": (90, 70)}


def spares(rule: float = 0.10) -> list:
    short = [(p, t, u, (t - u) / t) for p, (t, u) in TERMINALS.items()
             if (t - u) / t < rule]
    lines = [f"spare terminals in each control cabinet, teaching rule {rule:.0%}",
             "  panel    installed   used   spare"]
    for p, (t, u) in TERMINALS.items():
        lines.append(f"  {p:7s}  {t:9d}   {u:4d}   {(t - u) / t:5.0%}")
    lines += [f"  below the rule: {', '.join(p for p, *_ in short)}",
              "  BESS-A grew when the second cable position and its CT core",
              "  were added, WS2 when its missing arrester set and counter",
              "  were wired after the FAT (lesson B); a cabinet without spares",
              "  turns the next change into a new terminal strip and a",
              "  rewired panel at site"]
    emit("t_spares", lines)
    return short


# ------------------------------------------------ 5. nameplates and positions
def nameplates() -> list:
    plates = list(src.PANELS)
    i, j = plates.index("PVF3"), plates.index("PVF2")
    plates[i], plates[j] = plates[j], plates[i]
    odd = [(k + 1, want, got) for k, (want, got) in enumerate(zip(src.PANELS, plates))
           if want != got]
    lines = ["nameplates read along the installed line-up against the one-line order",
             "  position   one-line   nameplate"]
    lines += [f"  {k:8d}   {w:8s}   {g}" for k, w, g in odd]
    lines += ["  two plates swapped between the sections: an operator who",
              "  opens 'PVF2' opens PVF3's breaker in section A - the plate",
              "  is a safety item, read against the one-line at the FAT, at",
              "  installation and before the first switching programme (ch 23)"]
    emit("t_plates", lines)
    return odd


# ------------------------------------------------ 6. as-laid lengths
ASLAID = {"W001": 862, "W002": 1105, "W003": 1094, "W004": 1222}


def aslaid(p_mw: float = 5.0, kv: float = 33.0, pf: float = 0.95,
           theta: float = 70.0, tol: float = 0.05) -> dict:
    sched = {"W001": 850, "W002": 970, "W003": 1090, "W004": 1210}
    sizes = {"W001": 630, "W002": 400, "W003": 240, "W004": 240}
    i_t = p_mw * 1e6 / (math.sqrt(3) * kv * 1e3 * pf)
    lines = [f"as-laid lengths of string WS1 against the schedule (flag over "
             f"{tol:.0%})", "  cable   schedule m   as laid m   change"]
    loss = {"schedule": 0.0, "as laid": 0.0}
    flag = []
    for k, cid in enumerate(sched):
        ch = ASLAID[cid] / sched[cid] - 1
        if abs(ch) > tol:
            flag.append(cid)
        lines.append(f"  {cid}    {sched[cid]:10d}   {ASLAID[cid]:9d}   {ch:+6.1%}")
        c = s24.MV_CABLES[sizes[cid]]
        r = cb.r_at(c["r20"], theta, 0.00403)
        i = (4 - k) * i_t
        loss["schedule"] += cb.loss_kw(i, r, sched[cid] / 1000)
        loss["as laid"] += cb.loss_kw(i, r, ASLAID[cid] / 1000)
    lines += [f"  flagged: {', '.join(flag)}; string loss {loss['schedule']:.1f} -> "
              f"{loss['as laid']:.1f} kW at full output",
              "  W002 went round a wadi crossing found during the works: the",
              "  as-laid length goes back into the schedule, the loss model",
              "  (ch 15) and the drum record - the as-built schedule is the",
              "  one the plant is operated with"]
    emit("t_aslaid", lines)
    return dict(flag=flag, loss=loss)


if __name__ == "__main__":
    capability()
    coil_voltage()
    dc_demand()
    spares()
    nameplates()
    aslaid()
