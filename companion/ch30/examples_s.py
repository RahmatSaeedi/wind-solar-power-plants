"""Chapter 30, lesson S: reliability and life - the reliability index of a
simple check, the chance that T07's tower frequency falls inside the
margin when the soil stiffness is uncertain, fatigue life extension
from measured loads, how many bolts to inspect, and how long frequency
monitoring needs to see a softening foundation.

Run from the project root:   python -m companion.ch30.examples_s
Writes companion/ch30/expected/s_*.txt and diagrams/data/ch30-fmc.csv.
Teaching values (A-359, A-362); reliability targets, life extension and
inspection plans belong to the codes, the certifier and the owner.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st


def beta() -> None:
    lines = ["reliability index of a check R > S with normal R and S (teaching)",
             "  mean R   CoV R   mean S   CoV S   beta    P(failure)"]
    for mr, cr, ms, cs in [(1.5, 0.10, 1.0, 0.20), (1.5, 0.10, 1.0, 0.30),
                           (1.8, 0.10, 1.0, 0.30), (1.5, 0.05, 1.0, 0.10)]:
        b = (mr - ms) / math.hypot(mr * cr, ms * cs)
        pf = stats.norm.cdf(-b)
        lines.append(f"  {mr:6.1f}   {cr:5.2f}   {ms:6.1f}   {cs:5.2f}   {b:4.2f}   {pf:10.1e}")
    rng = np.random.default_rng(30)
    r = rng.normal(1.5, 0.15, 1_000_000)
    s = rng.normal(1.0, 0.20, 1_000_000)
    lines += [f"  Monte Carlo of the first row: P(failure) {np.mean(r < s):.1e}",
              "  the same mean margin (1.5 against 1.0) is safe or not",
              "  depending on the scatter: partial factors are a way of",
              "  reaching a target beta without a probability calculation,",
              "  and the codes calibrate them for that target"]
    emit("s_beta", lines)


def freq_mc(n: int = 200_000, seed: int = 30) -> None:
    rng = np.random.default_rng(seed)
    m_eff = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3
    f_need = src.ONE_P_MAX * (1 + src.MARGIN_1P)
    rows, lines = [], ["T07's tower frequency with an uncertain soil stiffness (Monte Carlo)",
                       "  G lognormal with the median of lesson B; fixed-base f1 0.215 Hz",
                       "  site and median G        CoV   P(f1 < required)   5 % f1 Hz"]
    for name, g_med, cov in [("dense ground, 80 MPa", 80e6, 0.3), ("T07, 25 MPa", 25e6, 0.3),
                             ("T07, 25 MPa", 25e6, 0.5)]:
        sig = math.sqrt(math.log(1 + cov * cov))
        g = g_med * np.exp(rng.normal(0, sig, n))
        k = 8 * g * src.FOUNDATION["r"] ** 3 / (3 * (1 - 0.35))
        f = 1 / np.sqrt(1 / src.F1_FIXED ** 2 + 1 / (np.sqrt(k / (m_eff * src.HUB ** 2))
                                                       / (2 * math.pi)) ** 2)
        p = float(np.mean(f < f_need))
        lines.append(f"  {name:22s}   {cov:5.1f}   {p:16.2f}   {np.percentile(f, 5):9.3f}")
        if name.startswith("T07") and cov == 0.3:
            hist, edges = np.histogram(f, bins=40, range=(0.190, 0.215))
            rows = [(round(e, 5), int(h)) for e, h in zip(edges[:-1], hist)]
    csv("ch30-fmc.csv", "f,count", rows)
    lines += [f"  required f1 {f_need:.4f} Hz (10 % above 1P max)",
              "  on dense ground the margin holds almost always; at T07 it",
              "  is missed in most draws - and a wider scatter cannot",
              "  rescue it: the soil investigation narrows the scatter,",
              "  the foundation scheme (lesson D) moves the median"]
    emit("s_freqmc", lines)


def extension() -> None:
    design = src.LOADS["fatigue: DEL at 1e7 cycles"]["m_mnm"]
    lines = ["fatigue life from measured loads (teaching; damage ~ DEL^m)",
             f"  design DEL {design:.0f} MN m for 25 years",
             "  measured DEL MN m   m = 3: life years   m = 5: life years"]
    for meas in (30.0, 28.0, 26.0, 24.0):
        lines.append(f"  {meas:17.0f}   {25 * (design / meas) ** 3:18.1f}   {25 * (design / meas) ** 5:18.1f}")
    lines += ["  five years of strain-gauge or SCADA-based load estimates",
              "  showing 26 instead of 30 MN m would leave the welds about",
              "  13 more years (m = 3) - a case for life extension that an",
              "  inspection, the measured data's uncertainty and the",
              "  certifier's assessment must all support"]
    emit("s_extension", lines)


def sampling() -> None:
    n_bolts = 120
    lines = ["inspecting a sample of flange bolts: the chance to find a loose one",
             f"  {n_bolts} bolts in a flange; k of them loose",
             "  sample   k = 1   k = 3   k = 6"]
    for n in (6, 12, 24, 60):
        ps = [1 - math.comb(n_bolts - k, n) / math.comb(n_bolts, n) for k in (1, 3, 6)]
        lines.append(f"  {n:6d}   {ps[0]:5.2f}   {ps[1]:5.2f}   {ps[2]:5.2f}")
    lines += ["  a 10 % sample (12 bolts) finds one of three loose bolts only",
              "  a quarter of the time: early in life, when settling",
              "  relaxes preload, every bolt is checked (lesson C); a",
              "  sample is for later years, and a loose one found in it",
              "  turns the sample into a full check"]
    emit("s_sampling", lines)


def monitoring(seed: int = 30) -> None:
    rng = np.random.default_rng(seed)
    sigma, drift = 0.0010, -0.005 * 0.209 / 12            # Hz per month (-0.5 %/yr)
    lines = ["how long monthly frequency estimates take to show a drift",
             f"  noise of one monthly estimate {sigma * 1000:.1f} mHz; drift -0.5 % a year",
             "  months   slope SE mHz/yr   drift mHz/yr   detected (3 SE)?"]
    for months in (12, 24, 36, 60):
        t = np.arange(months)
        se = sigma / math.sqrt(np.sum((t - t.mean()) ** 2)) * 12 * 1000
        d = abs(drift) * 12 * 1000
        lines.append(f"  {months:6d}   {se:15.2f}   {d:12.2f}   {'yes' if d > 3 * se else 'no'}")
    del rng
    lines += ["  a slow softening of the foundation hides in the noise for",
              "  about two years; frequency trends are a useful early",
              "  warning only with a long record, the same sensor, and",
              "  corrections for temperature and rotor state"]
    emit("s_monitoring", lines)


if __name__ == "__main__":
    beta()
    freq_mc()
    extension()
    sampling()
    monitoring()
