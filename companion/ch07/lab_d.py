"""Chapter 7, section D - calculation and measurement lab: the auxiliary
supply of Plant P (load schedule, three-phase solution, supply choice) and a
sample meter record (reading it, finding a wiring error and an event,
stating the limits of the model).

Run from the project root:   python -m companion.ch07.lab_d
Writes companion/ch07/expected/d_*.txt and diagrams/data/ch07-meter.csv.
Loads A-103 (fictional); LED spectrum A-105; meter record A-106: synthetic,
seed 7, driven by the 23 June temperatures of data pack 1.1.0. Not a design.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from companion.ch07.common import csv, emit
from plantp import ac, datapack
from plantp.phasors import complex_power, symmetrical_components

V_PH = 230.0
VA, VB, VC = ac.balanced_set(V_PH)
LED_H = {3: 0.80, 5: 0.55, 7: 0.30, 9: 0.15, 11: 0.08}      # A-105, per unit


# [start: schedule]
@dataclass
class Load:
    name: str
    p_kw: float           # active power at the operating point
    pf: float             # displacement power factor (lagging)
    phases: str           # "abc" three-phase, else "a", "b" or "c"
    diversity: float      # share expected at the time of the peak
    scenario: str = "S0"  # "S1" = only with the battery system


LOADS = [                                                    # A-103
    Load("transformer cooling fans", 8.8, 0.82, "abc", 1.0),
    Load("control building HVAC", 25.0, 0.85, "abc", 1.0),
    Load("battery system HVAC", 60.0, 0.85, "abc", 1.0, "S1"),
    Load("DC system and UPS chargers", 10.0, 0.90, "abc", 1.0),
    Load("workshop power", 15.0, 0.80, "abc", 0.5),
    Load("lighting (LED)", 6.0, 0.95, "a", 1.0),
    Load("SCADA and telecom", 8.0, 0.95, "a", 1.0),
    Load("office sockets", 6.0, 0.90, "b", 0.6),
    Load("security systems", 3.0, 0.90, "c", 1.0),
    Load("heaters, store and toilets", 9.0, 1.00, "c", 0.7),
]


def phase_currents(loads, scenario):
    """Complex RMS currents (50 Hz) of phases a, b, c at the peak."""
    v = {"a": VA, "b": VB, "c": VC}
    i = {"a": 0j, "b": 0j, "c": 0j}
    for ld in loads:
        if ld.scenario == "S1" and scenario != "S1":
            continue
        p = ld.p_kw * 1e3 * ld.diversity
        s = complex(p, p * math.tan(math.acos(ld.pf)))       # S = P + jQ
        for ph in ld.phases:                                 # equal shares
            s_ph = s / len(ld.phases)
            i[ph] += (s_ph / v[ph]).conjugate()              # I = (S/V)*
    return i["a"], i["b"], i["c"]
# [end: schedule]


def schedule() -> None:
    lines = ["auxiliary load schedule at 400/230 V (A-103), peak with "
             "diversity:"]
    for sc in ("S0", "S1"):
        ia, ib, ic = phase_currents(LOADS, sc)
        s = sum(complex_power(v, i) for v, i in zip((VA, VB, VC),
                                                     (ia, ib, ic)))
        i0, i1, i2 = symmetrical_components(ia, ib, ic)
        lines.append(f"  {sc}: P {s.real / 1e3:6.1f} kW, Q {s.imag / 1e3:5.1f}"
                     f" kvar, S {abs(s) / 1e3:6.1f} kVA, pf "
                     f"{s.real / abs(s):.3f}")
        lines.append(f"      phases {abs(ia):5.1f}, {abs(ib):5.1f}, "
                     f"{abs(ic):5.1f} A; neutral (50 Hz) {3 * abs(i0):4.1f} A;"
                     f" |I2|/|I1| {abs(i2) / abs(i1):.3f}")
    i1_led = 6.0e3 / (V_PH * 0.95)
    i_h = i1_led * math.sqrt(sum(a * a for a in LED_H.values()))
    ia, ib, ic = phase_currents(LOADS, "S0")
    i_n50 = abs(ia + ib + ic)
    i_n = math.hypot(i_n50, i_h)
    lines += [f"LED lighting on phase a (A-105): fundamental {i1_led:.1f} A, "
              f"harmonics {i_h:.1f} A RMS;",
              "  a single-phase load returns all of its current, harmonics "
              "included,",
              f"  through the neutral: I_N = sqrt({i_n50:.1f}^2 + "
              f"{i_h:.1f}^2) = {i_n:.1f} A",
              f"  ({100 * (i_n / i_n50 - 1):+.0f} % on the 50 Hz value); "
              f"phase a RMS rises only from {abs(ia):.1f} to "
              f"{math.hypot(abs(ia), i_h):.1f} A"]
    emit("d_schedule", lines)


def supply_choice() -> None:
    ia, ib, ic = phase_currents(LOADS, "S1")
    s = sum(complex_power(v, i) for v, i in zip((VA, VB, VC), (ia, ib, ic)))
    worst = max(abs(ia), abs(ib), abs(ic))
    s_equiv = 3 * V_PH * worst                     # sized on the worst phase
    sizes = [100, 160, 250, 400]                   # fictional range, kVA
    margin = 1.25                                  # growth, ageing (A-103)
    need = s_equiv * margin / 1e3
    pick = next(x for x in sizes if x >= need)
    i_rated = pick * 1e3 / (math.sqrt(3) * 400)
    r_pu, z_pu = 0.012, 0.06                       # A-103
    x_pu = math.sqrt(z_pu ** 2 - r_pu ** 2)
    drop = (r_pu * s.real + x_pu * s.imag) / (pick * 1e3)
    emit("d_supply", [
        f"S1 peak: {abs(s) / 1e3:.1f} kVA; worst phase {worst:.1f} A -> "
        f"balanced equivalent {s_equiv / 1e3:.1f} kVA",
        f"  x {margin} for growth, ageing and uncertainty = {need:.1f} kVA",
        f"  next size in the fictional range {sizes} kVA: {pick} kVA",
        f"  rated LV current {i_rated:.0f} A; the worst phase at the peak "
        f"is {100 * worst / i_rated:.0f} % of it",
        f"transformer z = {100 * z_pu:.0f} %, r = {100 * r_pu:.1f} % -> x = "
        f"{100 * x_pu:.2f} % (A-103)",
        f"  voltage drop ~ (r P + x Q) / S_rated = {100 * drop:.2f} % at the "
        "S1 peak",
        "a licensed electrical designer confirms the schedule, diversity,",
        "  protection and supply arrangement (chapters 23 and 24); these "
        "are",
        "  teaching numbers",
    ])


# [start: record]
def meter_record(seed=7):
    """Synthetic 10-min record of the auxiliary board on 23 June (A-106).
    Per-phase P and Q as the meter stores them, voltages (mean and
    minimum per interval) and current THD. The phase-b CT is wired
    reversed and a voltage dip occurs at 14:20."""
    rng = np.random.default_rng(seed)
    day = datapack.load_hourly("day_summer")
    t_air = np.repeat(day["t_air_c"].to_numpy(), 6)     # 144 intervals
    hour = np.arange(144) / 6
    hvac = np.clip((t_air - 22) / 14, 0.15, 1.0)         # share of rating
    fans = (hour >= 11) & (hour < 19)
    light = (hour < 6) | (hour >= 19.5)
    office = (hour > 8) & (hour < 17)
    heat = (hour >= 6) & (hour < 8)
    common = (25.0 * hvac + 60.0 * hvac + 8.8 * fans + 10.0) / 3
    p = {"a": 2.5 + 6.0 * light + 8.0 + common,
         "b": 2.5 + 3.6 * office + common,
         "c": 2.5 + 3.0 + 9.0 * heat + common}
    rec = {}
    for ph in "abc":
        p_true = p[ph] * (1 + 0.03 * rng.standard_normal(144))
        sign = -1.0 if ph == "b" else 1.0               # reversed CT
        rec["p_" + ph] = sign * p_true
        rec["q_" + ph] = sign * 0.55 * p_true
        v = 231.0 + 1.5 * rng.standard_normal(144)
        rec["v_" + ph] = v
        rec["vmin_" + ph] = v - 2.0
        rec["vmin_" + ph][14 * 6 + 2] = 0.72 * 231.0    # dip at 14:20
    rec["thd_a"] = 6.0 + 30.0 * light + rng.uniform(0, 2, 144)
    rec["hour"] = hour
    return rec
# [end: record]


def hhmm(k: int) -> str:
    return f"{k // 6:02d}:{10 * (k % 6):02d}"


def read_record() -> None:
    r = meter_record()
    total = r["p_a"] + r["p_b"] + r["p_c"]
    lines = ["one day of 10-min records at the auxiliary board, S1 "
             "(synthetic, A-106):",
             f"  energy as recorded (sum of phases): {total.sum() / 6:7.1f} "
             "kWh",
             f"  per phase: a {r['p_a'].sum() / 6:6.1f}, b "
             f"{r['p_b'].sum() / 6:6.1f}, c {r['p_c'].sum() / 6:6.1f} kWh"]
    neg = [ph for ph in "abc" if np.mean(r["p_" + ph]) < 0]
    lines.append(f"check 1, sign per phase: phase {', '.join(neg)} shows "
                 "negative power at a load board")
    fixed = r["p_a"] - r["p_b"] + r["p_c"]
    q_fix = r["q_a"] - r["q_b"] + r["q_c"]
    lines.append(f"  phase-b CT polarity corrected: {fixed.sum() / 6:7.1f} "
                 f"kWh ({100 * (fixed.sum() / total.sum() - 1):+.0f} % on "
                 "the record)")
    lines.append(f"  the record shows {100 * total.sum() / fixed.sum():.0f} "
                 "% of the true energy; with three equal phases")
    lines.append("  it would show 1/3 (1 - 1 + 1 of 3); phase b is the "
                 "lightest, so more")
    pk = int(np.argmax(fixed))
    s_pk = math.hypot(fixed[pk], q_fix[pk])
    lines.append(f"  peak 10-min demand {fixed[pk]:.1f} kW at {hhmm(pk)} "
                 f"({s_pk:.1f} kVA, pf {fixed[pk] / s_pk:.2f})")
    ia, ib, ic = phase_currents(LOADS, "S1")
    p_sched = sum(complex_power(v, i) for v, i in
                  zip((VA, VB, VC), (ia, ib, ic))).real / 1e3
    lines.append(f"  schedule estimate {p_sched:.1f} kW: "
                 f"{100 * (p_sched / fixed[pk] - 1):+.0f} % on the measured "
                 "peak (conservative)")
    dips = {ph: int(np.argmin(r["vmin_" + ph])) for ph in "abc"}
    k = dips["a"]
    same = all(x == k for x in dips.values())
    low = ", ".join(f"{r['vmin_' + ph][k]:.0f}" for ph in "abc")
    lines.append(f"check 2, minimum voltages {low} V at {hhmm(k)};")
    lines.append(f"  the same interval on all three phases: {same}")
    lines.append(f"  residual {100 * r['vmin_a'][k] / 230:.0f} % of 230 V "
                 "in one interval: a dip (an event), not a trend")
    i_mag = {}
    for ph in "abc":
        sgn = -1 if ph == "b" else 1
        i_mag[ph] = np.hypot(sgn * r["p_" + ph], sgn * r["q_" + ph]) \
            * 1e3 / r["v_" + ph]
    stack = np.vstack([i_mag[ph] for ph in "abc"])
    mean = stack.mean(axis=0)
    dev = np.max(np.abs(stack - mean), axis=0) / mean
    kd = int(np.argmax(dev))
    lines.append(f"check 3, current imbalance (max deviation / mean): "
                 f"{100 * dev.min():.0f} to {100 * dev.max():.0f} %,")
    lines.append(f"  highest at {hhmm(kd)} (phases "
                 f"{', '.join(f'{x:.0f}' for x in stack[:, kd])} A)")
    lines.append("  from current magnitudes only: the negative-sequence "
                 "factor needs")
    lines.append("  the angles, which the analyser takes from its waveforms")
    thd = r["thd_a"]
    lines.append(f"check 4, current THD of phase a {thd.min():.0f} to "
                 f"{thd.max():.0f} %: highest at night,")
    lines.append("  when LED lighting is a large share of a small load")
    lines += ["limits: 10-min values hide fast events (the dip depth and",
              "  duration come from the analyser's event log); one day is not "
              "a season;",
              "  all values synthetic"]
    emit("d_meter", lines)
    csv("ch07-meter.csv", "h,p_rec,p_fix,vmin",
        [(f"{h:.3f}", f"{a:.2f}", f"{b:.2f}", f"{v:.1f}")
         for h, a, b, v in zip(r["hour"], total, fixed, r["vmin_a"])])


if __name__ == "__main__":
    schedule()
    supply_choice()
    read_record()
