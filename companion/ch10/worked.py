"""Chapter 10 - small worked calculations, one line each (E01 ...), used by
the text and the self-checks.

Run from the project root:   python -m companion.ch10.worked
Writes companion/ch10/expected/worked.txt.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.special import lambertw

from companion.ch10 import pvyear10
from companion.ch10.common import emit
from plantp import pvcell as pc

DS = pc.PVM_550_DS
H, C0, Q, KB = 6.62607015e-34, 2.99792458e8, 1.602176634e-19, 1.380649e-23
AREA = 2.278 * 1.134                           # m2, data pack
OUT: list[str] = []


def e(eid: str, text: str, more: str = "") -> None:
    OUT.append(f"{eid}: {text}")
    if more:
        OUT.append(f"     {more}")


def ev(nm: float) -> float:
    return H * C0 / (nm * 1e-9) / Q


def lines() -> None:
    m = pvyear10.ref_sdm()
    e("E01", f"photon energy: 1000 nm {ev(1000):.3f} eV, 550 nm {ev(550):.2f} eV,"
             f" 400 nm {ev(400):.2f} eV")
    e("E02", f"cut-off 1240/Eg: Si 1.12 eV {1239.84 / 1.12:.0f} nm, CdTe 1.45 eV "
             f"{1239.84 / 1.45:.0f} nm, 1.60 eV {1239.84 / 1.60:.0f} nm")
    vt = KB * 298.15 / Q
    e("E03", f"thermal voltage at 25 C {1e3 * vt:.2f} mV;",
      f"fitted n Vt per cell a/72 = {1e3 * m.a / 72:.2f} mV (n {m.a / 72 / vt:.3f})")
    d = 160e-4                                       # cm, 160 um wafer
    for nm, alpha in ((600, 4140.0), (800, 850.0), (1000, 64.0)):
        one, two = 1 - math.exp(-alpha * d), 1 - math.exp(-2 * alpha * d)
        e("E04" if nm == 600 else "   ", f"{nm:4d} nm, 1/alpha {1e4 / alpha:5.1f}"
              f" um: 160 um absorbs {100 * one:5.1f} % ({100 * two:5.1f} % in"
              " 2 passes)")
    e("E05", f"double the light: V_oc + a ln 2 = {m.a * math.log(2):.2f} V per"
             f" module ({1e3 * m.a * math.log(2) / 72:.1f} mV per cell)")
    ff = DS.vmp * DS.imp / (DS.voc * DS.isc)
    e("E06", f"fill factor {DS.vmp} x {DS.imp} / ({DS.voc} x {DS.isc}) = {ff:.3f}",
      f"efficiency 550 / (1000 x {AREA:.3f}) = {100 * 550 / (1000 * AREA):.2f} %")
    share = 1.12 * DS.isc * 72 / (1000 * AREA)
    vf = (DS.voc / 72) / 1.12
    e("E07", f"loss chain: Eg x collected current / light = {100 * share:.1f} %",
      f"x qV_oc/Eg {vf:.3f} -> {100 * share * vf:.1f} %; x FF {ff:.3f} -> "
      f"{100 * share * vf * ff:.1f} % (module)")
    lin = DS.voc * (1 + 0.0027 * 40)
    mod = pc.at_conditions(m, 1000, -15, DS.alpha_isc).voc
    e("E08", f"V_oc at -15 C: linear {lin:.2f} V, fitted model {mod:.2f} V",
      f"26 modules: {26 * lin:.0f} V / {26 * mod:.0f} V")
    lin_p = 550 * (1 - 0.0035 * 40)
    mod_p = pc.at_conditions(m, 1000, 65, DS.alpha_isc).mpp()[2]
    e("E09", f"P_max at 65 C: linear {lin_p:.1f} W, fitted model {mod_p:.1f} W")
    noct = 35 + (45 - 20) / 800 * 1000
    e("E10", f"cell at 1000 W/m2, air 35 C: NOCT rule {noct:.1f} C",
      f"Faiman, wind 1 m/s {float(pc.faiman(35, 1000, 1)):.1f} C; 4 m/s "
      f"{float(pc.faiman(35, 1000, 4)):.1f} C")
    e("E11", f"bifacial: rear 0.12 x 1000 x 0.70 = {0.12 * 700:.0f} W/m2"
             " front-equivalent")
    vals = ", ".join(f"{a} deg {float(pc.iam_ashrae(math.cos(math.radians(a)))):.3f}"
                     for a in (30, 60, 75, 80))
    e("E12", f"IAM (b0 0.05): {vals}")
    e("E13", f"label 550 W, flash +-3 %: 552 W true range "
             f"{552 * 0.97:.0f} .. {552 * 1.03:.0f} W")
    e("E14", f"W(1) = {lambertw(1).real:.4f}; W(10) = {lambertw(10).real:.4f};"
             f" check W e^W = {lambertw(10).real * math.exp(lambertw(10).real):.4f}")
    e("E15", f"half-cut cells: interconnect loss ratio 144 (1/2)^2 (1/2) / 72"
             f" = {144 * 0.25 * 0.5 / 72:.2f}")
    e("E16", f"31 per pallet, 620 per container: {4200 * 26:,} modules ->",
      f"{math.ceil(109200 / 31):,} pallets, {math.ceil(109200 / 620)} containers")
    i_sc_hi = DS.isc * 1.2 + DS.alpha_isc * 47
    e("E17", f"current bound 1.2 x 13.98 + {DS.alpha_isc:.5f} x 47 = "
             f"{i_sc_hi:.2f} A; x 20 = {20 * i_sc_hi:.0f} A")
    e("E18", f"reverse current, 20 strings: 19 x 13.98 x 1.25 ="
             f" {19 * DS.isc * 1.25:.0f} A")
    pitch = 2 * 2.278 / 0.40
    e("E19", f"pitch at GCR 0.40, two 2.278 m modules: {pitch:.2f} m;",
      f"table rise L sin 25 = {2 * 2.278 * math.sin(math.radians(25)):.2f} m")
    f = 1 - (1 / 0.4) * math.sin(math.radians(12)) / math.sin(math.radians(37))
    e("E20", f"shaded share at alpha_p 12 deg, tilt 25 deg, GCR 0.4: {f:.3f}")
    a_lim = math.degrees(math.atan(math.sin(math.radians(25)) /
                                   (1 / 0.4 - math.cos(math.radians(25)))))
    e("E21", f"no shade above tan a = sin b / (1/GCR - cos b): {a_lim:.1f} deg")
    e("E22", f"winter-solstice noon at 34 N: 90 - 34 - 23.44 = "
             f"{90 - 34 - 23.44:.1f} deg")
    e("E23", f"DC/AC: 60.06 MWp / 50 MW = {60.06 / 50:.3f}; block 6.006 / 5 ="
             f" {6.006 / 5:.3f}")
    rho = 0.0172 * (1 + 0.00393 * 50)
    e("E24", f"copper at 70 C {rho:.4f} ohm mm2/m; 4 mm2 x 160 m: "
             f"{rho * 160 / 4:.3f} ohm, {DS.imp ** 2 * rho * 160 / 4:.0f} W")
    t = math.sqrt(2 * 16380 / (50 * 112.9e3 / 365 * 0.003 * 0.95))
    e("E25", f"T* truck = sqrt(2 x 16380 / (50 x 309 x 0.003 x 0.95))"
             f" = {t:.1f} d")
    e("E26", f"water per cleaning: 1.0 L x {109200:,} = {109.2:.1f} m3;"
             f" 1.5 L: {163.8:.1f} m3")
    e("E27", f"soiling 0.3 %/day for 30 days: mean loss {0.3 * 30 / 2:.1f} %,"
             f" final {0.3 * 30:.1f} %")
    cells = 109200 * 72
    wafers = cells / (0.98 * 0.995)                  # A-207 yields
    e("E28", f"109,200 x 72 = {cells:,} full cells; yields 98 % (cell) x"
             " 99.5 % (module)",
      f"-> {wafers:,.0f} wafers into the cell line ({wafers - cells:,.0f} lost)")
    pp = pvyear10.poa()
    b, sk, gr = (pp[k].sum() / 1e3 for k in ("beam", "sky", "ground"))
    e("E30", f"POA year at 25 deg: beam {b:,.0f}, sky {sk:,.0f}, ground {gr:,.0f}"
             f" = {b + sk + gr:,.0f} kWh/m2")
    e("   ", f"shares {100 * b / (b + sk + gr):.1f} / {100 * sk / (b + sk + gr):.1f}"
            f" / {100 * gr / (b + sk + gr):.1f} %; GHI {pp['ghi'].sum() / 1e3:,.0f}")
    sh = ", ".join(f"{el} deg {100 / math.tan(math.radians(el)):.0f} m"
                   for el in (15, 30, 60))
    e("E31", f"tower shadow (hub 100 m): {sh}",
      f"blade tip at 175 m, sun at 15 deg: {175 / math.tan(math.radians(15)):.0f} m")
    v = pvyear10.strings()["v_mp"]
    v = v[v > 0]
    e("E32", f"string V_mp x 0.97 (aged): min {0.97 * v.min():.0f} V, median "
             f"{0.97 * np.median(v):.0f} V",
      f"hours below 933 V: {int((0.97 * v < 933).sum())} "
      f"(new modules: {int((v < 933).sum())})")
    gap = 2 * 2.278 / 0.40 - 2 * 2.278 * math.cos(math.radians(25))
    e("E33", f"clear row gap d - L cos 25 = 11.39 - {2 * 2.278 * 0.9063:.2f} ="
             f" {gap:.2f} m (access)")
    pairs = 4200 * 27                                 # A-208
    e("E34", f"mated connector pairs: 4200 strings x 27 = {pairs:,};",
      f"at 0.01 % per pair and year: {pairs * 1e-4:.0f} failures a year")
    r_mod, n_blk = 400e6, 10920                       # A-208
    e("E35", f"array insulation: 400 Mohm / {n_blk:,} modules = "
             f"{r_mod / n_blk / 1e3:.1f} kohm;",
      f"with dew halving each module: {r_mod / 2 / n_blk / 1e3:.1f} kohm")
    day_val = 0.05 * 112.9e3 / 365 * 50                 # storm adds 5 % loss
    e("E36", f"dust storm +5 %: lost value {day_val:,.0f} u/day;",
      f"one truck pass (16,380 u) pays back in {16380 / day_val:.1f} days")


if __name__ == "__main__":
    lines()
    emit("worked", OUT)
