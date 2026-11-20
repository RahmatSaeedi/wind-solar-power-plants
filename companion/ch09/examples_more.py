"""Chapter 9 - more lessons: DC-link pre-charge, the dual-active bridge,
the battery converter, the turbine's brake chopper, interleaved stacks,
junction-temperature cycles over the data-pack year, inverter failures over
25 years (Monte Carlo), string potentials to earth, and a DC-link discharge
into a cable fault.

Run from the project root:   python -m companion.ch09.examples_more
Writes companion/ch09/expected/x_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-166 .. A-172 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch09 import pvyear
from companion.ch09.common import csv, emit
from companion.ch09.examples_a import EFF_POINTS
from plantp import pe

S2, S3 = math.sqrt(2), math.sqrt(3)


def precharge() -> None:
    c, v, i_max = 4 * 12e-3, 1100.0, 20.0                       # A-166
    r = v / i_max
    tau = r * c
    e = pe.capacitor_energy_j(c, v)
    emit("x_precharge", [
        f"pre-charge of the inverter DC link: 4 x 12 mF = {c * 1e3:.0f} mF "
        f"to {v:.0f} V (A-166)",
        f"  limit the current to {i_max:.0f} A: R = {r:.0f} ohm, "
        f"tau = {tau:.2f} s, 95 % after {3 * tau:.1f} s",
        f"  energy stored {e / 1e3:.1f} kJ; energy turned to heat in R also "
        f"{e / 1e3:.1f} kJ",
        "  (charging through a resistor always wastes as much as it stores)",
        f"  without pre-charge: the inrush is limited only by cable and",
        "  contactor resistance: kiloamperes, welded contacts, blown fuses"])


def dab() -> None:
    v1 = v2 = 800.0
    f, l_h = 20e3, 20e-6                                         # A-166
    lines = ["dual-active bridge, 800 V / 800 V, 20 kHz, L 20 uH (A-166):",
             "  P = V1 V2 phi (pi - |phi|) / (2 pi^2 f L)"]
    for phi in (0.1, 0.3, 0.6, math.pi / 2):
        p = v1 * v2 * phi * (math.pi - phi) / (2 * math.pi ** 2 * f * l_h)
        lines.append(f"  phase shift {phi:.2f} rad: {p / 1e3:7.1f} kW")
    lines += ["  power flows from the leading bridge to the lagging one; the",
              "  high-frequency transformer gives isolation in a small core"]
    emit("x_dab", lines)


def pcs() -> None:
    v_lo, v_hi = 1000.0, 1450.0                                 # A-167
    v_ac = pe.vll_max(v_lo / 1.1)
    c = pe.fit_loss_coeffs(EFF_POINTS)
    lines = [f"battery converter, 20 MW, battery {v_lo:.0f} to {v_hi:.0f} V DC"
             " (A-167):",
             f"  largest AC voltage for the lowest DC with 10 % headroom: "
             f"{v_ac:.0f} V",
             "    -> 600 V chosen, as for the PV inverters (D-012)"]
    for load in (0.25, 0.5, 1.0):
        eta = float(pe.efficiency_from_coeffs(load, c))
        lines.append(f"  at {100 * load:3.0f} % load: one pass {eta:.4f}, "
                     f"charge and discharge {eta ** 2:.4f}")
    e_ch = 12.59                                                 # GWh, ch 5
    eta = float(pe.efficiency_from_coeffs(0.5, c))
    lines += [f"  12.59 GWh/yr charged (chapter 5): the converter alone loses "
              f"about {e_ch * (1 - eta ** 2) * 1e3:.0f} MWh/yr",
              "  in both passes; its share of the 14 % round-trip loss"]
    emit("x_pcs", lines)


def chopper() -> None:
    p, v_dc, v_max, c = 5.32e6, 1150.0, 1250.0, 30e-3          # A-168
    t_rise = c * (v_max ** 2 - v_dc ** 2) / (2 * p)
    r = v_max ** 2 / p
    e = 5.0e6 * 0.150                     # at 5 MW output, as in chapter 8
    emit("x_chopper", [
        f"turbine converter, grid voltage near zero for 150 ms (A-168):",
        f"  without a chopper the DC link ({c * 1e3:.0f} mF) rises "
        f"{v_dc:.0f} -> {v_max:.0f} V in {t_rise * 1e3:.1f} ms",
        f"  chopper resistor for {p / 1e6:.2f} MW at {v_max:.0f} V: "
        f"{r:.3f} ohm",
        f"  energy into the resistor over the dip at 5 MW: {e / 1e6:.2f} MJ",
        "    (chapter 8 sent the same energy into rotor speed instead)",
        "  the resistor is rated for this energy pulse and a cooling time,",
        "  not for continuous power: repeated dips need a duty limit"])


def interleave() -> None:
    f1, f_sw, n_car, spc = 50.0, 3000.0, 60, 200
    n = n_car * spc
    dt = 1 / (f1 * n)
    t = np.arange(n) * dt
    th = 2 * np.pi * f1 * t
    m, v_dc, l_h = 0.9, 1000.0, 55.7e-6
    rip = []
    for k in range(4):                                          # A-169
        x = (f_sw * t + k / 4) % 1.0
        tri = np.where(x < 0.5, 4 * x - 1, 3 - 4 * x)
        s = (m * np.sin(th) > tri).astype(float)
        v_err = v_dc * (s - 0.5 * (1 + m * np.sin(th)))
        r = np.cumsum(v_err) * dt / l_h
        r = r - np.convolve(r, np.ones(spc) / spc, "same")
        rip.append(r)
    one = rip[0]
    tot = sum(rip)
    mid = slice(n // 4, n // 4 + 3 * spc)
    emit("x_interleave", [
        "four stacks with carriers shifted by a quarter period (A-169):",
        f"  ripple of one stack {np.ptp(one[mid]):.0f} A peak-to-peak",
        f"  ripple of the sum   {np.ptp(tot[mid]):.0f} A, against "
        f"{4 * np.ptp(one[mid]):.0f} A if the carriers were aligned",
        "  the ripples partly cancel and the remaining ripple sits at four",
        "  times the switching frequency: a smaller grid-side filter",
        "  price: circulating currents between stacks, which their own",
        "  inductors must limit"])
    sel = slice(n // 4, n // 4 + 2 * spc)
    csv("ch09-interleave.csv", "t,one,sum4",
        [(f"{(tt - t[n // 4]) * 1e6:.1f}", f"{a:.1f}", f"{b / 4:.1f}")
         for tt, a, b in zip(t[sel][::2], one[sel][::2], tot[sel][::2])])


def thermal_year() -> None:
    c = pe.fit_loss_coeffs(EFF_POINTS)
    r = pvyear.inverter_year(c)
    d = pvyear.hourly()
    p_mod = r["loss"] / 10 * 0.59 / 24 / 2                     # A-170
    t_cool = d["t_air"] + 5.0
    tj = t_cool + p_mod * 0.060
    days = len(tj) // 24
    swings = np.array([np.ptp(tj[24 * k:24 * k + 24]) for k in range(days)])
    dmg = (swings / 40.0) ** 5
    lines = ["daily junction-temperature swing of one module, data-pack year"
             " (A-170):",
             f"  largest swing {swings.max():.0f} K, median {np.median(swings):.0f}"
             f" K, smallest {swings.min():.0f} K",
             f"  damage (swing/40 K)^5 summed: {dmg.sum():,.0f} equivalent"
             " 40 K cycles per year"]
    months = (np.arange(days) // (365 / 12)).astype(int)
    share = [dmg[months == mm].sum() / dmg.sum() for mm in range(12)]
    lines.append("  damage share by month (%): " +
                 " ".join(f"{100 * s:.0f}" for s in share))
    lines += ["  the clear days of spring and summer, with air hot in the day",
              "  and cool at night, do most of the damage: cooling that also",
              "  holds the coolant warmer at night cuts the swing"]
    emit("x_thermalyear", lines)
    csv("ch09-tjyear.csv", "day,swing",
        [(k, f"{s:.2f}") for k, s in enumerate(swings)])


def monte_carlo() -> None:
    rng = np.random.default_rng(29)                              # A-171
    lam, years, n_inv, runs = 0.49, 25, 10, 2000
    p_mean = 101.4e3 / 8760 / n_inv                             # MW per inverter
    losses = np.empty(runs)
    for k in range(runs):
        n_f = rng.poisson(lam * n_inv * years)
        major = rng.random(n_f) < 0.08
        hours = np.where(major, rng.lognormal(math.log(400), 0.5, n_f),
                         rng.lognormal(math.log(36), 0.6, n_f))
        losses[k] = hours.sum() * p_mean / years                 # MWh/yr
    p50, p90 = np.percentile(losses, [50, 90])
    emit("x_montecarlo", [
        f"10 inverters over 25 years, {runs} runs (seed 29, A-171):",
        f"  failures {lam}/yr each; 8 % major (median 400 h), else median 36 h",
        f"  energy lost per year: mean {losses.mean():.0f}, P50 {p50:.0f}, "
        f"P90 {p90:.0f} MWh",
        f"  as a share of 101.4 GWh: mean {100 * losses.mean() / 101.4e3:.2f} %",
        "  the rare long repairs set the tail: a spare power module on site",
        "  shortens them more than any other single measure"])
    hist, edges = np.histogram(losses, bins=np.arange(150, 1050, 25))
    csv("ch09-mc.csv", "x,n", [(f"{a + 12.5:.1f}", int(b))
                               for a, b in zip(edges[:-1], hist)])


def potentials() -> None:
    n, v_mod = 26, 50.0                                          # A-172
    lines = ["module potentials to earth in a 26-module string at 1300 V"
             " (A-172):"]
    for name, shift in (("floating, symmetric", -0.5), ("negative pole earthed", 0.0),
                        ("positive pole earthed", -1.0)):
        v = [(k + 0.5) * v_mod + shift * n * v_mod for k in range(n)]
        lines.append(f"  {name:22s} from {v[0]:+6.0f} to {v[-1]:+6.0f} V")
    lines += ["  modules at strongly negative potential can suffer potential-",
              "  induced degradation in some cell technologies; earthing one",
              "  pole (through the inverter, a functional earth) or a night-",
              "  time offset voltage moves the string away from it: the choice",
              "  depends on modules, inverter and standard (chapters 10, 26)"]
    emit("x_potentials", lines)


def dc_fault() -> None:
    c, v0, r, l_h = 12e-3, 1000.0, 0.05, 20e-6                  # A-172
    dt = 1e-7
    i, v = 0.0, v0
    t_rec, i_rec = [], []
    i_pk, t_pk = 0.0, 0.0
    for k in range(int(3e-3 / dt)):
        di = (v - r * i) / l_h
        i += di * dt
        v -= i / c * dt
        if i > i_pk:
            i_pk, t_pk = i, k * dt
        if k % 100 == 0:
            t_rec.append(k * dt)
            i_rec.append(i)
    zeta = r / 2 * math.sqrt(c / l_h)
    emit("x_dcfault", [
        "DC-link capacitor (12 mF, 1000 V) into a cable fault,",
        "  50 mohm and 20 uH (A-172):",
        f"  damping ratio {zeta:.2f}; peak current {i_pk / 1e3:.1f} kA after "
        f"{t_pk * 1e3:.2f} ms",
        f"  stored energy {pe.capacitor_energy_j(c, v0) / 1e3:.1f} kJ goes into"
        " the fault and the cable",
        "  the inverter's own capacitors feed a DC-side fault even when the",
        "  array cannot: fuses and cable withstand must see this pulse",
        "  (chapter 6, U-008; the maker states the real figure)"])
    csv("ch09-dcfault.csv", "t,i", [(f"{a * 1e3:.3f}", f"{b / 1e3:.3f}")
                                    for a, b in zip(t_rec, i_rec)])


if __name__ == "__main__":
    precharge()
    dab()
    pcs()
    chopper()
    interleave()
    thermal_year()
    monte_carlo()
    potentials()
    dc_fault()
