"""Chapter 10, section A - photovoltaic conversion: photons and the band gap,
the ideal-cell limit, the single-diode model fitted to the data sheet,
temperature and irradiance behaviour, data-sheet tolerance, module
temperature models and bifacial gain.

Run from the project root:   python -m companion.ch10.examples_a
Writes companion/ch10/expected/a_*.txt and diagrams/data/ch10-*.csv.
Teaching values A-183 .. A-188 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math
import warnings

import numpy as np

from companion.ch10 import pvyear10
from companion.ch10.common import csv, emit
from plantp import datapack, mppt, pvcell as pc

warnings.simplefilter("ignore", RuntimeWarning)
H, C0, KB, QE = 6.62607015e-34, 2.99792458e8, 1.380649e-23, 1.602176634e-19
DS = pc.PVM_550_DS


def photons() -> None:
    t_sun = 5778.0
    lam = np.linspace(200e-9, 4000e-9, 20000)
    b = 2 * H * C0 ** 2 / lam ** 5 / np.expm1(H * C0 / (lam * KB * t_sun))
    b = b / np.trapezoid(b, lam) * 1000.0                    # scale to 1000 W/m2
    e_ph = H * C0 / lam
    lines = ["sunlight as photons (blackbody 5778 K scaled to 1000 W/m2, A-184):"]
    for name, eg in (("silicon", 1.12), ("CdTe", 1.45), ("perovskite", 1.6)):
        lam_g = H * C0 / (eg * QE)
        sel = lam <= lam_g
        flux = np.trapezoid(b[sel] / e_ph[sel], lam[sel])
        j = QE * flux
        p_use = j * eg                              # energy kept per photon = Eg
        lines.append(f"  {name:10s} Eg {eg:.2f} eV, cutoff {lam_g * 1e9:5.0f} nm: "
                     f"J max {j / 10:5.1f} mA/cm2, Eg x J {p_use / 10:4.1f} %")
    sel = (lam >= 280e-9) & (lam <= 2500e-9)
    flux = (b / e_ph)[sel][::40] * 1e-9 / 1e18       # 1e18 photons/(m2 s nm)
    csv("ch10-photons.csv", "nm,flux",
        [(f"{x * 1e9:.0f}", f"{y:.4f}") for x, y in zip(lam[sel][::40], flux)])
    lines += ["  photons below Eg pass through; above Eg the excess becomes",
              "  heat; Eg x J is the share left before voltage and fill-factor",
              "  losses: the root of the single-junction efficiency limit"]
    emit("a_photons", lines)


def sdm_fit() -> None:
    m = pvcell_ref()
    n = m.a / (DS.n_s * KB * 298.15 / QE)
    v, i, p = m.mpp()
    ff = p / (m.voc * m.isc)
    lines = ["single-diode model of the PVM-550 fitted to its data sheet:",
             f"  I_L {m.i_l:.4f} A, I_0 {m.i_0:.3e} A, n {n:.3f} "
             f"(a {m.a:.3f} V),",
             f"  R_s {m.r_s:.4f} ohm, R_sh {m.r_sh:.1f} ohm",
             f"  check: I_sc {m.isc:.3f} A, V_oc {m.voc:.3f} V, MPP {v:.2f} V "
             f"x {i:.3f} A = {p:.1f} W",
             f"  fill factor {ff:.3f}; efficiency on 2.58 m2 "
             f"{100 * p / 2580:.2f} % (A-183)"]
    simple = mppt.PVM_550.at(1000, 25)
    vs, ps = simple.mpp()
    lines += [f"  the explicit model of chapter 9: {ps:.1f} W at {vs:.2f} V;",
              "  the chapter 6 ideal diode without R_s gave 13.56 kW per string",
              "  instead of 14.30: series resistance shapes the knee"]
    emit("a_sdm", lines)
    vv = np.linspace(0, m.voc, 200)
    hot = pc.at_conditions(m, 1000, 65, DS.alpha_isc)
    low = pc.at_conditions(m, 400, 25, DS.alpha_isc)
    csv("ch10-iv.csv", "v,i_stc,i_hot,i_low",
        [(f"{x:.3f}", f"{float(m.i(x)):.4f}",
          f"{max(float(hot.i(x)), 0):.4f}", f"{max(float(low.i(x)), 0):.4f}")
         for x in vv])


def pvcell_ref():
    return pvyear10.ref_sdm()


def temperature() -> None:
    m = pvcell_ref()
    p_stc = m.mpp()[2]
    lines = ["the fitted model against temperature and irradiance:",
             "   G W/m2   T C    V_oc V   V_mp V    P W    P/P_stc"]
    for g, t in ((1000, 25), (1000, 45), (1000, 65), (600, 25), (200, 25),
                 (1000, -10)):
        s = pc.at_conditions(m, g, t, DS.alpha_isc)
        v, i, p = s.mpp()
        lines.append(f"  {g:6d}  {t:5d}  {s.voc:7.2f}  {v:7.2f}  {p:6.1f}  "
                     f"{p / p_stc:7.3f}")
    p65 = pc.at_conditions(m, 1000, 65, DS.alpha_isc).mpp()[2]
    lines += [f"  model coefficient of P_max {100 * (p65 / p_stc - 1) / 40:.3f} %/K"
              " against the data sheet -0.35 %/K",
              "  a five-parameter fit matches the four STC points and dV_oc/dT",
              "  exactly; the P_max coefficient is a check, not a fit target"]
    emit("a_temperature", lines)


def datasheet() -> None:
    lines = ["data-sheet tolerance and binning (A-185):",
             "  power class 550 W, tolerance 0 / +5 W: flashed power in the",
             "  factory must lie in 550.0 .. 555.0 W for this label",
             "  factory flash uncertainty +-3 % (k 2): a module flashed at 552 W",
             f"  may truly be between {552 * 0.97:.0f} and {552 * 1.03:.0f} W",
             "  the label is a sorting decision by the maker's flasher; a site",
             "  re-measurement needs its own uncertainty (chapter 2, section E)"]
    emit("a_datasheet", lines)


def cell_temperature() -> None:
    h = datapack.load_hourly()
    s = pvyear10.strings()
    poa = s["poa"]
    ta = h["t_air_c"].to_numpy(dtype=float)
    noct = ta + 25 / 800 * poa
    fai = s["t_cell"]
    sel = poa > 600
    lines = ["module temperature over the data-pack year, hours above 600 W/m2:",
             f"  NOCT rule (chapter 6): mean {noct[sel].mean():.1f} C, max "
             f"{noct[sel].max():.1f} C",
             f"  Faiman with wind at 2 m: mean {fai[sel].mean():.1f} C, max "
             f"{fai[sel].max():.1f} C (U0 25, U1 6.84; A-186)",
             f"  mean difference {np.mean(fai[sel] - noct[sel]):+.1f} K: the wind"
             " term cools windy hours;",
             "  mounting (open rack, roof) changes U0"]
    emit("a_celltemp", lines)


def bifacial() -> None:
    p = pvyear10.poa()
    rear = 0.12 * p["ghi"]                                      # A-187
    phi = 0.70
    gain = phi * rear.sum() / p["poa"].sum()
    emit("a_bifacial", [
        "bifacial module, rear irradiance 12 % of GHI (albedo, row gaps; A-187):",
        f"  bifaciality 0.70: effective gain {100 * gain:.1f} % of front POA",
        "  the gain depends on ground albedo, table height, row spacing and",
        "  shading of the rear by the structure: a model and a measurement",
        "  campaign, not a data-sheet number, set the design value"])


if __name__ == "__main__":
    photons()
    sdm_fit()
    temperature()
    datasheet()
    cell_temperature()
    bifacial()
