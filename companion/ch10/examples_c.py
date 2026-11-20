"""Chapter 10, section C - array engineering: string limits at the
temperature extremes, the integer layout of strings, combiners and
inverters, tilt, row spacing and shading, mismatch, the DC/AC ratio and
clipping, and the DC window of chapter 9 rechecked with the POA model.

Run from the project root:   python -m companion.ch10.examples_c
Writes companion/ch10/expected/c_*.txt and diagrams/data/ch10-*.csv.
Teaching values A-190 .. A-194 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math
import warnings

import numpy as np

from companion.ch10 import pvyear10
from companion.ch10.common import csv, emit
from plantp import datapack, mppt, pe, pvcell as pc
from plantp import solar

warnings.simplefilter("ignore", RuntimeWarning)
DS = pc.PVM_550_DS
EFF_POINTS = [(0.10, 0.970), (0.25, 0.983), (0.50, 0.986), (0.75, 0.985),
              (1.00, 0.983)]                                  # A-147


# [start: limits]
def string_limits(n_mod: int, t_min_c: float, t_hot_c: float,
                  g_max: float = 1200.0, v_sys: float = 1500.0,
                  v_floor: float = 933.0) -> dict:
    """Voltage and current bounds of a string: V_oc at the coldest cell
    temperature (full irradiance, conservative), V_mp at the hottest, and
    the short-circuit current at the highest irradiance and temperature."""
    ref = pvyear10.ref_sdm()
    cold = pc.at_conditions(ref, 1000.0, t_min_c, DS.alpha_isc)
    hot = pc.at_conditions(ref, 1000.0, t_hot_c, DS.alpha_isc)
    v_oc = n_mod * cold.voc
    v_mp = n_mod * hot.mpp()[0]
    i_sc = DS.isc * g_max / 1000 + DS.alpha_isc * (t_hot_c - 25)
    return {"v_oc_cold": v_oc, "ok_v_sys": v_oc <= v_sys,
            "v_mp_hot": v_mp, "ok_floor": v_mp >= v_floor, "i_sc_max": i_sc}
# [end: limits]


def strings() -> None:
    h = datapack.load_hourly()
    t_min = float(h["t_air_c"].min())
    lines = [f"string limits (data-pack minimum air {t_min:.1f} C; design low"
             " -15 C,", "  hot cell 72 C; A-190):",
             "  modules   V_oc at -15 C   V_mp at 72 C   1500 V   933 V floor"]
    for n in (24, 25, 26, 27, 28):
        r = string_limits(n, -15.0, 72.0)
        lines.append(f"  {n:7d}   {r['v_oc_cold']:11.0f} V   {r['v_mp_hot']:10.0f}"
                     f" V   {'ok' if r['ok_v_sys'] else 'EXCEEDS':7s}  "
                     f"{'ok' if r['ok_floor'] else 'below'}")
    r = string_limits(26, -15.0, 72.0)
    lines += [f"  string current bound at 1200 W/m2 and 72 C: {r['i_sc_max']:.2f} A",
              "  26 modules keep 1500 V with margin; 27 is close and leaves",
              "  no room for a colder winter or for low-light V_oc errors;",
              "  at a 72 C cell the 26-module V_mp is 15 V below the floor: a",
              "  static worst case; the year shows how rare it is (c_window)"]
    emit("c_strings", lines)


def layout() -> None:
    lines = ["integer layout of 60 MWp (A-191):",
             f"  strings needed: 60e6 / (26 x 550) = {60e6 / (26 * 550):.1f}"]
    for spc in (16, 18, 20, 21, 24):
        n_cb = 420 / spc
        lines.append(f"  {spc:2d} strings per combiner: {n_cb:5.2f} combiners per "
                     f"inverter{' (integer)' if n_cb == int(n_cb) else ''}")
    i_cb = 20 * DS.isc * 1.25
    lines += ["  choice (D-013): 420 strings per inverter = 21 combiners x 20",
              f"    strings; 4200 strings, {4200 * 26 * 550 / 1e6:.2f} MWp",
              f"  combiner output, 20 x I_sc x 1.25 = {i_cb:.0f} A for cable and"
              " switch",
              "    sizing (the factor and its basis come from the standard)"]
    emit("c_layout", lines)


def tilt() -> None:
    rows = []
    for t in range(0, 46, 5):
        p = pvyear10.poa(float(t))
        rows.append((t, p["poa"].sum() / 1e3, p["eff"].sum() / 1e3))
    best = max(rows, key=lambda r: r[2])
    lines = ["annual irradiation on south-facing planes (Hay-Davies, IAM):",
             "  tilt deg   POA kWh/m2   effective kWh/m2"]
    for t, a, b in rows:
        lines.append(f"  {t:8d}   {a:10.0f}   {b:14.0f}")
    lines += [f"  best tilt about {best[0]} deg, below the latitude (34 deg):",
              "  diffuse light and the summer-heavy sky favour flatter planes;",
              "  row shading and wind load push lower still (next lesson)"]
    emit("c_tilt", lines)
    csv("ch10-tilt.csv", "t,poa,eff", [(t, f"{a:.1f}", f"{b:.1f}")
                                        for t, a, b in rows])


# [start: shade]
def shaded_fraction(el_deg, az_deg, tilt_deg: float, gcr: float):
    """Share of a table's slope length shaded by the row in front (south-
    facing rows, sun profile angle in the north-south plane)."""
    el, az = np.radians(el_deg), np.radians(az_deg)
    b = math.radians(tilt_deg)
    cos_d = np.cos(az - math.pi)
    tan_p = np.divide(np.tan(el), cos_d, out=np.full_like(el, 1e9),
                      where=cos_d > 1e-6)
    a_p = np.arctan(np.clip(tan_p, 0, 1e9))
    f = 1 - (1 / gcr) * np.sin(a_p) / np.sin(a_p + b)
    return np.clip(np.where(el > 0, f, 0.0), 0.0, 1.0)
# [end: shade]


def rows_shading() -> None:
    p = pvyear10.poa()
    idx = np.arange(8760)
    n, hour = idx // 24 + 1, idx % 24
    st = solar.solar_time(hour + 0.5, n)
    el, az = solar.sun_position(34.0, n, st)
    beam = p["beam"]
    tot = p["poa"].sum()
    lines = ["inter-row shading, tilt 25 deg, tables 2 high (A-192):",
             "  GCR   pitch m   linear loss %   2P portrait %   4L landscape %"]
    rows = []
    for gcr in (0.30, 0.40, 0.50, 0.60):
        f = shaded_fraction(el, az, 25.0, gcr)
        lin = (f * beam).sum() / tot
        port = (np.where(f > 0.02, np.minimum(1.0, np.ceil(f * 2) / 2), 0)
                * beam).sum() / tot
        land = (np.where(f > 0.02, np.ceil(f * 12) / 12, 0) * beam).sum() / tot
        pitch = 2 * 2.278 / gcr
        rows.append((gcr, f"{100 * lin:.2f}", f"{100 * port:.2f}",
                     f"{100 * land:.2f}"))
        lines.append(f"  {gcr:.2f}  {pitch:7.1f}   {100 * lin:12.2f}   "
                     f"{100 * port:12.2f}   {100 * land:13.2f}")
    lines += ["  portrait tables lose a whole module row once its bottom edge",
              "  is shaded (all three bypass substrings run along the slope);",
              "  landscape modules lose one substring at a time; GCR 0.40",
              "  (A-183) keeps the electrical loss small at 11.4 m pitch"]
    emit("c_rows", lines)
    csv("ch10-rows.csv", "gcr,lin,port,land", rows)


def mismatch() -> None:
    rng = np.random.default_rng(37)                             # A-193
    base = mppt.PVM_550.at(1000, 25)
    n_str, n_mod = 20, 26
    i_grid = np.linspace(0.5, base.isc * 0.995, 400)
    v_grid = np.linspace(0, n_mod * base.voc, 800)
    i_strings, p_sum = [], 0.0
    for _ in range(n_str):
        v_tot = np.zeros_like(i_grid)
        for _ in range(n_mod):
            k_p = 1 + rng.uniform(0, 5) / 550                   # binning 0/+5 W
            k_i = k_p * (1 + rng.normal(0, 0.007))
            k_v = k_p / k_i
            m = mppt.Curve(base.isc * k_i, base.voc * k_v, base.imp * k_i,
                           base.vmp * k_v)
            p_sum += m.mpp(800)[1]
            v_tot += m.v(i_grid)
        order = np.argsort(v_tot)
        i_strings.append(np.interp(v_grid, v_tot[order], i_grid[order],
                                   left=i_grid[-1], right=0.0))
    p_array = (v_grid * np.sum(i_strings, axis=0)).max()
    loss = 1 - p_array / p_sum
    emit("c_mismatch", [
        f"20 strings of 26 modules in parallel, Monte Carlo (seed 37, A-193):",
        "  power binning 0/+5 W, current spread 0.7 % (one sigma)",
        f"  sum of module maxima {p_sum / 1e3:.2f} kW; array maximum "
        f"{p_array / 1e3:.2f} kW",
        f"  mismatch loss {100 * loss:.2f} % at STC; ageing and uneven",
        "  soiling widen the spread and the loss over the years"])


def dcac() -> None:
    c = pe.fit_loss_coeffs(EFF_POINTS)
    dc0 = pvyear10.dc_power()                                   # 60.06 MWp
    lines = ["DC/AC ratio with the POA model, 10 x 5 MW inverters (A-194):",
             "  DC/AC   MWp    DC GWh   clipped GWh   clipped %   AC GWh"]
    rows = []
    for r in (1.00, 1.10, 1.20, 1.30, 1.40, 1.50):
        dc = dc0 * (r * 50 / 60.06)
        x = dc / 50e6
        c0, c1, c2 = c
        y = np.where(x > c0, (-(1 + c1) + np.sqrt((1 + c1) ** 2 - 4 * c2 * (c0 - x)))
                     / (2 * c2), 0.0)
        ac_uncl = y * 50e6
        ac = np.minimum(ac_uncl, 50e6 * float(pe.derating(30, 1200)))
        cut = (ac_uncl - ac).sum() / 1e9
        rows.append((r, f"{dc.sum() / 1e9:.2f}", f"{cut:.3f}", f"{ac.sum() / 1e9:.2f}"))
        lines.append(f"  {r:5.2f}  {r * 50:5.1f}  {dc.sum() / 1e9:7.2f}  "
                     f"{cut:11.3f}   {100 * cut / (ac_uncl.sum() / 1e9):8.2f}  "
                     f"{ac.sum() / 1e9:7.2f}")
    lines += ["  Plant P's 1.20 clips about 0.7 %: the inverters are",
              "  full in the brightest hours and earn in all the others; the",
              "  best ratio comes from module and inverter prices (chapter 18)"]
    emit("c_dcac", lines)
    csv("ch10-dcac.csv", "r,dc,cut,ac", rows)


def window() -> None:
    s = pvyear10.strings()
    v = s["v_mp"]
    pw = s["p_string"]
    ref = pvyear10.ref_sdm()
    lines = ["the DC window of D-012 rechecked with POA and Faiman (U-032):",
             f"  string V_mp: min {v[v > 0].min():.0f} V, median "
             f"{np.median(v[v > 0]):.0f} V"]
    h = datapack.load_hourly()
    ta = h["t_air_c"].to_numpy(dtype=float)
    for v_ac in (600, 630, 690):
        floor = pe.vdc_min(v_ac, headroom=0.1)
        below = np.flatnonzero((v > 0) & (v < floor))
        lost = 0.0
        for k in below:
            m = pc.at_conditions(ref, s["eff"][k], s["t_cell"][k], DS.alpha_isc)
            lost += pw[k] - 26 * floor / 26 * float(m.i(floor / 26))
        lines.append(f"  {v_ac} V (floor {floor:.0f} V): {len(below):4d} h, "
                     f"{100 * lost / pw.sum():.3f} % of DC energy")
    lines += ["  more light on the tilted plane, but the Faiman model with wind",
              "  runs cooler than the NOCT rule of chapter 9: fewer hours fall",
              "  below the floor; D-012 holds with more margin, and 690 V would",
              "  still lose about a twentieth of the energy"]
    emit("c_window", lines)


if __name__ == "__main__":
    strings()
    layout()
    tilt()
    rows_shading()
    mismatch()
    dcac()
    window()
