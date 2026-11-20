"""Chapter 43, a fifth round: the tap changer's step capacity, bushing
current ratings with margin, a process FMEA of the transformer factory
ranked severity first (ch 40), the transformer's critical characteristics,
fan noise against the hour of day on the data-pack year, and the end point
read from a drying record.

Run from the project root:   python -m companion.ch43.examples_v
Writes companion/ch43/expected/v_*.txt.
Teaching values (A-461, A-464); no drying schedule is given or implied.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch43 import sources as src
from companion.ch43.common import emit
from plantp import quality as qa
from plantp import transformer as tr

M, D = src.MAIN_B, src.DESIGN


# ------------------------------------------------ tap changer step capacity
def oltc(i_over: float = 1.2) -> dict[str, float]:
    v_hv = M["hv_kv"] * 1e3 / math.sqrt(3)
    step_v = v_hv * M["taps"][2] / 100
    i = M["s_mva"] * 1e6 / (3 * v_hv)
    cap = step_v * i * i_over / 1000
    lines = ["on-load tap changer on the 132 kV star point (teaching):",
             f"  step {M['taps'][2]} % of {v_hv / 1000:.1f} kV = {step_v:.0f} V; "
             f"through current {i:.0f} A",
             f"  step capacity at {i_over:.0%} current: {cap:.0f} kVA per step",
             f"  {int(2 * M['taps'][1] / M['taps'][2]) + 1} positions; at the star "
             "point the tap changer sits near earth",
             "  potential, which keeps its insulation small",
             "  the tap changer is chosen for current, step voltage and",
             "  step capacity with margin, and its type tests (STD-180)",
             "  are part of the transformer's evidence"]
    emit("v_oltc", lines)
    return dict(step_v=step_v, cap=cap, i=i)


# ------------------------------------------------ bushings
BUSHINGS = [(250, 400, 630, 800), (800, 1250, 1600, 2000, 2500)]


def bushings(over: float = 1.5) -> dict[str, float]:
    i_hv = M["s_mva"] * 1e6 / (math.sqrt(3) * M["hv_kv"] * 1e3)
    i_lv = M["s_mva"] * 1e6 / (math.sqrt(3) * M["lv_kv"] * 1e3)
    pick_hv = next(r for r in BUSHINGS[0] if r >= over * i_hv)
    pick_lv = next(r for r in BUSHINGS[1] if r >= over * i_lv)
    lines = [f"bushing currents with {over:.0%} margin for overload and harmonics "
             "(teaching)",
             f"  HV line {i_hv:.0f} A -> needs {over * i_hv:.0f} A: rating {pick_hv} A",
             f"  LV line {i_lv:,.0f} A (delta: line, not phase) -> needs "
             f"{over * i_lv:,.0f} A: rating {pick_lv} A",
             "  a bushing carries the line current, not the winding's phase",
             "  current; its temperature in the hot air and at the site's",
             "  altitude (ch 25) is the maker's check, and its factory",
             "  capacitance and loss factor travel with it"]
    emit("v_bushings", lines)
    return dict(hv=pick_hv, lv=pick_lv, i_lv=i_lv)


# ------------------------------------------------ process FMEA
# [start: pfmea]
PFMEA = [  # step, failure mode, S, O, D (teaching)
    ("core cutting", "burr over limit", 5, 4, 4),
    ("winding", "height out of tolerance", 7, 3, 4),
    ("winding", "transposition fault in CTC", 8, 2, 6),
    ("leads", "poor brazed joint", 9, 3, 6),
    ("tap leads", "lead on the wrong tapping", 8, 2, 2),
    ("drying", "end point not reached", 9, 2, 5),
    ("clamping", "force lost after drying", 9, 3, 5),
    ("oil", "wet oil filled", 7, 3, 3),
]
# [end: pfmea]


def pfmea() -> list[str]:
    rows = [dict(step=a, mode=b, s=s, o=o, d=d) for a, b, s, o, d in PFMEA]
    ranked = qa.fmea_rank(rows)
    lines = ["process FMEA of the transformer factory, ranked severity first",
             "  (ch 40); RPN shown only for comparison",
             "  step          failure mode                 S  O  D  SxO  RPN"]
    for r in ranked:
        lines.append(f"  {r['step']:13s} {r['mode']:28s} {r['s']:2d} {r['o']:2d} "
                     f"{r['d']:2d}  {r['s'] * r['o']:3d}  "
                     f"{qa.rpn(r['s'], r['o'], r['d']):3d}")
    by_rpn = max(rows, key=lambda r: qa.rpn(r["s"], r["o"], r["d"]))
    lines += [f"  first by the ranking: {ranked[0]['mode']}; by RPN: "
              f"{by_rpn['mode']}",
              "  the failures the final tests cannot see (joints, clamping,",
              "  drying) rank high: their controls are the traveler's holds"]
    emit("v_pfmea", lines)
    return [r["mode"] for r in ranked]


# ------------------------------------------------ critical characteristics
CRIT = [("core", "loss of the bare core", "core test record"),
        ("core", "burr per batch", "burr log"),
        ("windings", "heights and radial builds", "dimension sheet"),
        ("windings", "tap leads to drawing", "ratio at every tap"),
        ("leads", "joint quality", "joint record, DGA"),
        ("active part", "clamping after drying", "clamping record"),
        ("insulation", "dryness at the end point", "drying record, PD"),
        ("oil", "water before filling", "oil test"),
        ("shipment", "impact and gas pressure", "recorder log")]


def critical() -> int:
    lines = ["critical characteristics of a power transformer and their evidence",
             "  part          characteristic             evidence"]
    for p, c, e in CRIT:
        lines.append(f"  {p:13s} {c:26s} {e}")
    lines += [f"  {len(CRIT)} characteristics; three of T1's gaps (burr, drying,",
              "  recorder) sit on this list - a gap on a critical row is",
              "  an NCR, not a missing page"]
    emit("v_critical", lines)
    return len(CRIT)


# ------------------------------------------------ fan noise by hour
def night_fans(core_lwa: float = 84.0, fan_lwa: float = 85.0) -> dict[str, float]:
    from companion.ch25.examples_b import unit_load
    from plantp import datapack
    k = unit_load() * M["s_mva"] / M["s_onan_mva"]
    amb = datapack.load_hourly()["t_air_c"].to_numpy()
    top = amb + 52.0 * ((1 + 6 * k ** 2) / 7) ** 0.8
    on = np.zeros(len(top), dtype=bool)
    state = False
    for i, t in enumerate(top):                  # same band as lesson E
        if not state and t >= 65.0:
            state = True
        elif state and t <= 55.0:
            state = False
        on[i] = state
    hour = np.arange(len(k)) % 24
    night = (hour >= 22) | (hour < 6)
    both = tr.sound_sum([core_lwa, fan_lwa])
    n_night = int((on & night).sum())
    lines = [f"core {core_lwa:.0f} dB(A) and fans {fan_lwa:.0f} dB(A) of sound power "
             "(teaching)",
             f"  together {both:.1f} dB(A); fans off: {core_lwa:.0f} dB(A)",
             f"  fan hours on the data-pack year: {int(on.sum())}; at night "
             f"(22-06 h): {n_night}",
             f"  only {n_night} of {int(on.sum())} fan hours fall at night: the night "
             "limit (ch 33)",
             "  meets mostly the core alone, while the guarantee is for",
             "  both; a fan stage chosen for low noise is a design option"]
    emit("v_fans", lines)
    return dict(both=both, night=n_night, hours=int(on.sum()))


# ------------------------------------------------ drying record end point
def drying(seed: int = 4301, limit_lph: float = 0.30) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    t = np.arange(0, 133, 6.0)                         # hours of the record
    rate = 27.0 * np.exp(-t / 22.0) + rng.normal(0, 0.05, len(t))
    rate = np.clip(rate, 0.01, None)
    below = t[np.argmax(rate < limit_lph)] if (rate < limit_lph).any() else None
    water = float(np.trapezoid(rate, t))
    tail = 27.0 * 22.0 * math.exp(-t[-1] / 22.0)
    lines = ["water extracted per hour from a drying record (synthetic;",
             f"  a teaching end-point limit of {limit_lph} L/h, not a recipe)",
             "  hour   " + "  ".join(f"{x:4.0f}" for x in t[:11]),
             "  L/h    " + "  ".join(f"{x:4.1f}" for x in rate[:11]),
             f"  rate below the limit from hour {below:.0f}; water removed "
             f"{water:.0f} L (ch 25: about 600)",
             f"  the curve's tail still holds about {tail:.1f} L",
             "  the end point is shown by the falling rate, not by the",
             "  hours on the clock - T1's traveler has no such record,",
             "  so its dryness is unproven (lab D)"]
    emit("v_drying", lines)
    return dict(below=float(below), water=water, tail=tail)


if __name__ == "__main__":
    oltc()
    bushings()
    pfmea()
    critical()
    night_fans()
    drying()
