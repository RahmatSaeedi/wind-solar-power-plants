"""Chapter 45, round s: deeper lessons - the coating's edge and the slit
width, electrolyte fill weight, grade bins of a lot, pulse resistance
corrected for temperature, cell swelling against the module's end plates,
temperature spread in a rack and the ageing it causes, why an LFP voltage
says little about SOC, balancing current for a spread of self-discharge,
the energy a factory test costs, and the cells waiting in the aging room.

Run from the project root:   python -m companion.ch45.examples_s
Writes companion/ch45/expected/s_*.txt.
Teaching values (A-474 to A-481); purposes and checks, no process values
beyond teaching ones, nothing for real batteries.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch45 import sources as src
from companion.ch45.common import emit
from plantp import quality as qy
from plantp import storage as st

C, B = src.CELL, src.BUILD


# ------------------------------------------------ 1. coating edge and slit width
def edge(width_mm: float = 600.0, bead_mm: float = 25.0, bead: float = 0.06,
         tol: float = 0.02) -> dict:
    """Loading across the web: flat in the middle, heavier near each edge
    (a linear bead, teaching). Lanes are kept where loading is in +-tol."""
    x = np.linspace(0, width_mm, 1201)
    d = np.minimum(x, width_mm - x)
    load = 1 + bead * np.clip(1 - d / bead_mm, 0, None)
    ok = np.abs(load - 1) <= tol
    keep = x[ok]
    trim = width_mm - (keep.max() - keep.min())
    lines = [f"positive coating across a {width_mm:.0f} mm web: +{bead:.0%} at the "
             f"edges, fading over {bead_mm:.0f} mm",
             f"  (teaching profile); lanes kept where loading is within +-{tol:.0%}",
             f"  usable width {keep.max() - keep.min():.0f} mm; trimmed "
             f"{trim:.0f} mm ({trim / width_mm:.1%} of the coated web)",
             f"  N/P at the very edge (negative flat): "
             f"{1.047 / (1 + bead):.3f} - below one",
             "  the heavy edge is trimmed away at slitting: material is",
             "  traded for balance, and the profile across the web is part",
             "  of the coating record, not only the mean"]
    emit("s_edge", lines)
    return dict(trim=trim, share=trim / width_mm)


# ------------------------------------------------ 2. electrolyte fill weight
def fill(seed: int = 4505, n: int = 80, sd: float = 0.006, shift: float = -0.004,
         lsl: float = 0.985, usl: float = 1.015) -> dict:
    rng = np.random.default_rng(seed)
    w = rng.normal(1.0 + shift, sd, n)
    m, s, cp, cpk = qy.cp_cpk(list(w), lsl, usl)
    low = int((w < lsl).sum())
    p_low = 0.5 * math.erfc((m - lsl) / (s * math.sqrt(2)))
    lines = ["electrolyte fill weight relative to target (teaching limits "
             f"{lsl:.3f} - {usl:.3f}),",
             f"  {n} cells",
             f"  mean {m:.4f}, sd {s:.4f}: Cp {cp:.2f}, Cpk {cpk:.2f}",
             f"  cells under the lower limit in the sample: {low}; expected "
             f"share {p_low:.2%}",
             "  an under-filled cell passes formation and loses capacity",
             "  faster; each cell is weighed before and after filling and",
             f"  both weights stay in its record; Cpk {cpk:.2f}: the line fills",
             "  light and wide - the low side matters more than the high,",
             "  so the mean is centred first, then the spread narrowed"]
    emit("s_fill", lines)
    return dict(cpk=cpk, p_low=p_low)


# ------------------------------------------------ 3. grade bins
BINS = [("A", 316.0, 1e9), ("B", 313.0, 316.0), ("reject", -1e9, 313.0)]


def bins() -> dict:
    lot = src.lot()
    bad = set(lot["leak"]) | set(lot["high"]) | {lot["bad_record"]}
    caps = [float(c) for i, c in enumerate(lot["cap"]) if i not in bad]
    out = {}
    lines = ["capacity bins of lot L4506 after the K and resistance screens",
             f"  ({len(caps)} cells; teaching edges)",
             "  bin      Ah range          cells   share"]
    for name, lo, hi in BINS:
        k = sum(1 for c in caps if lo <= c < hi)
        out[name] = k
        rng = f"{max(lo, 300):.0f} - {min(hi, 330):.0f}" if name != "A" else ">= 316"
        lines.append(f"  {name:7s}  {rng:15s}  {k:6d}   {k / len(caps):5.1%}")
    mods = out["A"] // B["s_module"]
    lines += [f"  bin A fills {mods} modules of {B['s_module']}; bin B cells go to "
              "another order or a",
              "  lower-rated product, never mixed into an A module - mixing",
              "  bins undoes the matching (lesson B); the bin is printed",
              "  with the cell's ID"]
    emit("s_bins", lines)
    return out


# ------------------------------------------------ 4. resistance and temperature
def dcir_temp(coef: float = -0.015, t_ref: float = 25.0, limit: float = 0.265,
              seed: int = 4506, n: int = 2000) -> dict:
    """Pulse resistance falls as the cell warms (teaching -1.5 %/K)."""
    rng = np.random.default_rng(seed)
    r25 = rng.normal(0.250, 0.006, n)
    t = rng.uniform(21.0, 29.0, n)                       # cells not settled
    r_meas = r25 * (1 + coef * (t - t_ref))
    r_corr = r_meas / (1 + coef * (t - t_ref))
    truth = r25 > limit
    raw = r_meas > limit
    lines = [f"pulse resistance measured on cells between 21 and 29 C, limit "
             f"{limit * 1000:.0f} uohm at {t_ref:.0f} C",
             f"  (teaching coefficient {coef:.1%}/K); {n} cells",
             "  method                      over limit   wrongly passed   "
             "wrongly failed",
             f"  raw reading                 {int(raw.sum()):10d}   "
             f"{int((truth & ~raw).sum()):14d}   {int((~truth & raw).sum()):14d}",
             f"  corrected to 25 C           {int((r_corr > limit).sum()):10d}   "
             f"{0:14d}   {0:14d}",
             "  a cold cell reads high and a warm one low: grading compares",
             "  resistances at one temperature, so each reading carries",
             "  the cell's temperature and the correction; the better",
             "  control is to let cells settle before the test"]
    emit("s_dcir", lines)
    return dict(passed=int((truth & ~raw).sum()), failed=int((~truth & raw).sum()))


# ------------------------------------------------ 5. swelling and end plates
def swelling(n: int = 52, t_cell_mm: float = 72.0, k_cell: float = 5.0,
             k_frame: float = 40.0, f0_kn: float = 10.0) -> dict:
    """Cells in series as springs (kN/mm each, teaching) against a frame:
    a growth of the stack is shared between cell compression and frame
    stretch; the frame force rises."""
    k_stack = k_cell / n                                 # n springs in series
    rows = []
    for growth in (0.0, 0.01, 0.03, 0.05):
        d = growth * n * t_cell_mm                       # free growth, mm
        x_frame = d * k_stack / (k_stack + k_frame)
        f = f0_kn + k_frame * x_frame
        rows.append((growth, d, f))
    lines = [f"module of {n} prismatic cells ({t_cell_mm:.0f} mm) held by straps "
             "(teaching stiffnesses)",
             "  cell growth   free stack growth mm   strap force kN"]
    for g, d, f in rows:
        lines.append(f"  {g:11.0%}   {d:20.1f}   {f:14.1f}")
    lines += ["  cells swell with age; a frame that is too stiff loads them",
              "  and itself, one that is too soft lets them separate from",
              "  the cooling plate - the frame is designed for end-of-life",
              "  growth, and the compression force at assembly is recorded"]
    emit("s_swell", lines)
    return dict(rows=rows)


# ------------------------------------------------ 6. temperature spread and ageing
def thermal_spread(years: int = 10, base_fade: float = 0.02, spread_k=(0, 3, 6, 10)):
    """Fade doubles every 10 K (teaching); a string is set by its hottest cell."""
    lines = [f"cells of one rack {years} years in service, fade {base_fade:.0%} a "
             "year at the mean temperature",
             "  (doubling every 10 K, teaching)",
             "  hottest cell above mean K   its health   string loss vs mean"]
    out = {}
    mean_h = 1 - base_fade * years
    for dk in spread_k:
        h = 1 - base_fade * 2 ** (dk / 10) * years
        out[dk] = h
        lines.append(f"  {dk:24d}   {h:10.1%}   {mean_h - h:18.1%}")
    lines += ["  the hottest cell sets the string: a spread of 6 K costs the",
              f"  whole rack {mean_h - out[6]:.0%} of its capacity by year 10 - the",
              "  air or liquid path is tested for evenness at the factory,",
              "  and the BMS temperature map shows it in service"]
    emit("s_spread", lines)
    return out


# ------------------------------------------------ 7. voltage says little about SOC
def lfp_soc(err_mv: float = 5.0) -> dict:
    lines = [f"SOC error from a cell-voltage error of {err_mv:.0f} mV at rest",
             "  (LFP teaching curve, ch 19)",
             "  SOC    slope V per unit SOC   SOC error"]
    out = {}
    for s in (0.10, 0.30, 0.50, 0.70, 0.95):
        slope = float(st.ocv_slope(s))
        e = err_mv / 1000 / slope
        out[s] = e
        lines.append(f"  {s:4.0%}   {slope:21.3f}   {e:8.1%}")
    lines += ["  in the flat middle a few millivolts mean several per cent",
              "  of SOC: an LFP battery counts charge and corrects its SOC",
              "  where the curve is steep (near full or empty) - the BMS",
              "  voltage accuracy and the correction rule are part of its",
              "  configuration record"]
    emit("s_lfpsoc", lines)
    return out


# ------------------------------------------------ 8. balancing current
def balancing_size(n_cells: int = 416, k_sd: float = 0.006,
                   rest_h: float = 8.0) -> dict:
    """The bleed must remove, in the hours available each day, the extra
    daily self-discharge of the fastest of n cells (expected maximum of a
    normal sample, mean + sd sqrt(2 ln n); teaching)."""
    from companion.ch45 import lab_d
    k_hi = 0.030 + k_sd * math.sqrt(2 * math.log(n_cells))
    i_extra = lab_d.leak_current(k_hi) - lab_d.leak_current(0.030)
    ah_day = i_extra / 1000 * 24
    i_need = ah_day / rest_h * 1000
    lines = [f"balancing for the self-discharge spread of {n_cells} cells in a "
             "rack",
             f"  (K mean 0.030, sd {k_sd} mV/day)",
             f"  fastest cell expected about K {k_hi:.3f} mV/day: extra leak "
             f"{i_extra:.1f} mA",
             f"  charge to move a day: {ah_day * 1000:.0f} mAh; with "
             f"{rest_h:.0f} h of balancing time: {i_need:.0f} mA",
             "  a bleed of tens of milliamperes covers the normal spread with",
             "  room to spare - and it also covers a leaker like lab D's",
             f"  ({lab_d.leak_current(0.064) - lab_d.leak_current(0.030):.1f} mA): "
             "that is why the BMS hides it, and why the duty",
             "  signal is needed to show it"]
    emit("s_balsize", lines)
    return dict(k_hi=k_hi, i_need=i_need)


# ------------------------------------------------ 9. the energy of a factory test
def fat_energy(rt: float = 0.86, cycles: int = 2, price: float = 70.0) -> dict:
    e = B["s_module"] * B["m_rack"] * B["r_container"] * C["q_ah"] * C["v_nom"] / 1e6
    usable = e * 0.8
    lost = cycles * usable * (1 - rt)
    p_test = 2.5
    lines = [f"factory test of one container ({e:.2f} MWh, {usable:.2f} MWh in "
             "the window): ",
             f"  {cycles} full cycles at round trip {rt:.0%}: {lost:.2f} MWh lost "
             f"= {lost * price / 1000:.2f} k u",
             f"  at {p_test} MW of factory supply a cycle takes "
             f"{2 * usable / p_test:.1f} h; the factory needs that",
             "  much grid or a second container to cycle against",
             "  (back-to-back, as for inverters in ch 44)",
             "  the test energy is small money; the grid connection and the",
             "  hours set how many containers a factory can test a week"]
    emit("s_fat", lines)
    return dict(lost=lost, hours=2 * usable / p_test)


# ------------------------------------------------ 10. cells waiting in aging
def wip(rate_day: float = 12000.0, rest_days=(14, 7, 3)) -> dict:
    """Little's law: cells in the aging room = rate x time."""
    lines = [f"a cell factory making {rate_day:,.0f} cells a day (teaching): "
             "cells resting in aging",
             "  rest days   cells on the racks   MWh stored (314 Ah, 3.2 V)"]
    out = {}
    for d in rest_days:
        n = rate_day * d
        out[d] = n
        lines.append(f"  {d:9d}   {n:18,.0f}   {n * C['q_ah'] * C['v_nom'] / 1e6:24.1f}")
    lines += ["  fourteen days of rest hold a plant-sized battery of charged",
              "  cells in one building: halving the rest frees half the racks",
              "  and half the stored energy - the pressure behind lab D's",
              "  shortened test, and the reason the rest time is a contract",
              "  item with a record, not the factory's private choice"]
    emit("s_wip", lines)
    return out


if __name__ == "__main__":
    edge()
    fill()
    bins()
    dcir_temp()
    swelling()
    thermal_spread()
    lfp_soc()
    balancing_size()
    fat_energy()
    wip()
