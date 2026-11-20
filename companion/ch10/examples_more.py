"""Chapter 10 - further examples: low-light efficiency, the implicit diode
equation solved three ways, incidence losses over the year, half-cut cells,
acceptance sampling, string fuses, DC cable losses over the year, snow,
mismatch after ageing, and a single-axis tracker against fixed tables.

Run from the project root:   python -m companion.ch10.examples_more
Writes companion/ch10/expected/*.txt and diagrams/data/ch10-*.csv.
Teaching values A-200 .. A-206 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math
import warnings

import numpy as np
from scipy.special import comb

from companion.ch10 import pvyear10
from companion.ch10.common import csv, emit
from plantp import datapack, mppt, pvcell as pc, solar

warnings.simplefilter("ignore", RuntimeWarning)
DS = pc.PVM_550_DS
AREA = 2.58                                   # m2 per module (A-183)


def low_light() -> None:
    ref = pvyear10.ref_sdm()
    p_stc = ref.mpp()[2]
    lines = ["relative efficiency against irradiance at 25 C (fitted model):",
             "   G W/m2    P_mp W   efficiency %   relative"]
    rows = []
    for g in (50, 100, 200, 400, 600, 800, 1000, 1100):
        m = pc.at_conditions(ref, float(g), 25.0, DS.alpha_isc)
        p = m.mpp()[2]
        eta = p / (g * AREA)
        rel = (p / p_stc) / (g / 1000)
        rows.append((g, f"{rel:.4f}"))
        lines.append(f"  {g:7d}   {p:7.1f}   {100 * eta:12.2f}   {rel:8.3f}")
    lines += ["  efficiency peaks near 600 .. 800 W/m2: below, V_oc falls with",
              "  the log of the current and the shunt takes a larger share;",
              "  above, I^2 R_s grows; a data sheet gives the 200 W/m2 point"]
    emit("a_lowlight", lines)
    csv("ch10-lowlight.csv", "g,rel", rows)


def implicit() -> None:
    m = pvyear10.ref_sdm()
    v = 40.0

    def f(i):                                   # residual of the diode equation
        return (m.i_l - m.i_0 * (math.exp((v + i * m.r_s) / m.a) - 1)
                - (v + i * m.r_s) / m.r_sh - i)

    i_fp, n_fp, ok = 13.0, 0, True             # fixed point i <- i + f(i)
    for n_fp in range(1, 41):
        i_new = i_fp + f(i_fp)
        if not math.isfinite(i_new) or abs(i_new) > 1e6:
            ok = False
            break
        if abs(i_new - i_fp) < 1e-9:
            i_fp = i_new
            break
        i_fp = i_new
    i_n, n_n = 13.0, 0                          # Newton
    for n_n in range(1, 30):
        d = (-m.i_0 * m.r_s / m.a * math.exp((v + i_n * m.r_s) / m.a)
             - m.r_s / m.r_sh - 1)
        step = f(i_n) / d
        i_n -= step
        if abs(step) < 1e-12:
            break
    i_w = float(m.i(v))
    emit("a_implicit", [
        f"current of the PVM-550 at V = {v:.0f} V, three ways:",
        "  fixed point i <- i + f(i): "
        + (f"{i_fp:.6f} A after {n_fp} steps" if ok else
           f"diverges after {n_fp} steps (the slope of f is"
           " too steep near the knee)"),
        f"  Newton from 13 A:          {i_n:.6f} A after {n_n} steps",
        f"  Lambert W (closed form):   {i_w:.6f} A",
        "  Newton converges fast from a good start; the Lambert W form",
        "  needs no start and no loop, which suits 8760 hours x 26",
        "  modules; both need care with overflow (chapter 3)"])


def iam_year() -> None:
    p = pvyear10.poa()
    ci, cz, n = pvyear10.geometry()
    b = p["beam"].sum()
    d = (p["sky"] + p["ground"]).sum()
    b_eff = (p["beam"] * pc.iam_ashrae(ci)).sum()
    tot = p["poa"].sum()
    emit("a_iam", [
        "incidence-angle losses over the year, tilt 25 deg (b0 0.05):",
        f"  beam {b / 1e3:6.0f} kWh/m2 -> {b_eff / 1e3:6.0f} after IAM "
        f"({100 * (1 - b_eff / b):.1f} % lost)",
        f"  diffuse and ground {d / 1e3:6.0f} kWh/m2 x 0.95 (5 % lost)",
        f"  total {tot / 1e3:.0f} -> {p['eff'].sum() / 1e3:.0f} kWh/m2: "
        f"{100 * (1 - p['eff'].sum() / tot):.1f} % of the plane-of-array light",
        "  most beam arrives near normal incidence; the loss is in the",
        "  mornings, evenings and winter; anti-reflection glass and",
        "  soiling change b0 (chapter 14 uses a measured IAM table)"])


def half_cell() -> None:
    r_cell = 0.8e-3                          # ohm per full cell (A-200)
    i_mp = DS.imp
    full = 72 * i_mp ** 2 * r_cell
    half = 144 * (i_mp / 2) ** 2 * (r_cell / 2)
    emit("b_halfcell", [
        "interconnect loss, full cells against half-cut cells (A-200):",
        f"  full cells: 72 x I^2 x r = 72 x {i_mp:.2f}^2 x {1e3 * r_cell:.1f} mohm"
        f" = {full:.1f} W ({100 * full / 550:.2f} %)",
        f"  half cells: 144 x (I/2)^2 x (r/2) = {half:.1f} W "
        f"({100 * half / 550:.2f} %)",
        f"  ratio {half / full:.2f}: each half carries half the current over",
        "  half the path; the two halves of the module run in parallel,",
        "  so the module keeps its voltage and current class",
        f"  gain {full - half:.1f} W per module, about "
        f"{(full - half) * 109200 / 1e3:.0f} kW over Plant P at STC"])


def oc(n: int, c: int, p: float) -> float:
    """Probability of accepting a lot with defect share p (binomial)."""
    return float(sum(comb(n, k) * p ** k * (1 - p) ** (n - k)
                     for k in range(c + 1)))


def sampling() -> None:
    plans = ((50, 1), (125, 3), (200, 5))           # A-201, teaching plans
    lines = ["acceptance sampling by attributes: probability of accepting",
             "a lot against its true share of defective modules (A-201):",
             "  defect %   n 50, c 1   n 125, c 3   n 200, c 5"]
    rows = []
    for p in (0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08):
        pa = [oc(n, c, p) for n, c in plans]
        lines.append(f"  {100 * p:8.1f}   {pa[0]:9.3f}   {pa[1]:10.3f}"
                     f"   {pa[2]:10.3f}")
    for k in range(0, 101):
        p = k / 1000
        rows.append((f"{100 * p:.1f}",) + tuple(f"{oc(n, c, p):.4f}"
                                                for n, c in plans))
    lines += ["  a larger sample separates good and bad lots more sharply;",
              "  no plan proves a lot free of defects: the contract names",
              "  the plan, the acceptance number and what happens to a",
              "  rejected lot (sorting, return, claim)"]
    emit("b_sampling", lines)
    csv("ch10-oc.csv", "p,a,b,c", rows)


def fuses() -> None:
    n_par = 20                                      # strings per combiner
    i_sc = DS.isc
    i_rev = (n_par - 1) * i_sc * 1.25
    fuse_max = 25.0                                 # data sheet (A-202)
    k_low = 1.5                                     # as ch 6 and ch 26 (A-202)
    emit("c_fuse", [
        "string fuses in a 20-string combiner (A-202):",
        f"  a short in one string draws the other 19 strings' current: up to"
        f" {i_rev:.0f} A",
        f"  module maximum series fuse (data sheet) {fuse_max:.0f} A: the reverse"
        " current is",
        f"    {i_rev / fuse_max:.0f} times that, so every string needs a fuse",
        f"  lower bound {k_low} x I_sc = {k_low * i_sc:.1f} A, upper bound "
        f"{fuse_max:.0f} A: a 25 A gPV fuse",
        "  the factors and the rule for both poles come from IEC 62548-1",
        "  and the earthing scheme; this is a teaching check, not a rule",
        "  with two strings or fewer in parallel no fuse may be needed:",
        "  (N - 1) I_sc stays below the module's fuse rating"])


def cables() -> None:
    rho_cu = 0.0172 * (1 + 0.00393 * 50)            # ohm mm2/m at 70 C
    rho_al = 0.0282 * (1 + 0.00403 * 50)
    i_s, i_cb = DS.imp, 20 * DS.imp
    rows = []
    for name, rho, length, area, i, p in (
            ("string, 4 mm2 Cu", rho_cu, 2 * 80, 4, i_s, 26 * 550),
            ("string, 6 mm2 Cu", rho_cu, 2 * 80, 6, i_s, 26 * 550),
            ("combiner, 240 mm2 Al", rho_al, 2 * 200, 240, i_cb, 20 * 26 * 550),
            ("combiner, 300 mm2 Al", rho_al, 2 * 200, 300, i_cb, 20 * 26 * 550)):
        r = rho * length / area
        rows.append((name, r, i ** 2 * r, i ** 2 * r / p))
    s = pvyear10.strings()
    pw = s["p_string"]
    k = (pw ** 2).sum() / (pw.max() * pw.sum())
    lines = ["DC cable losses at the maximum power point (A-203; 70 C):",
             "  cable                  R ohm    loss at STC W   share %"]
    for name, r, w, sh in rows:
        lines.append(f"  {name:21s}  {r:6.3f}   {w:13.0f}   {100 * sh:7.2f}")
    lines += [f"  over the year I^2 R losses scale with P^2: energy share ="
              f" STC share x {k:.2f}",
              f"  so 0.99 % + 1.36 % at STC is about "
              f"{(rows[0][3] + rows[2][3]) * k * 100:.1f} % of the DC energy",
              "  (the 2 % of A-183 is a little conservative); voltage drop",
              "  and the sun-derated ampacity (chapter 4) are separate checks"]
    emit("c_cable", lines)


def snow() -> None:
    dc = pvyear10.dc_power()
    day = dc.reshape(365, 24).sum(axis=1)
    events = (4, 5, 19, 20, 34, 35, 49, 50, 339, 340)   # A-204, 0-based days
    lost = 0.9 * day[list(events)].sum()
    s_k, mu, b = 1.2, 0.8, math.radians(25)
    normal = mu * s_k * math.cos(b) ** 2 * 1e3
    emit("c_snow", [
        "snow on the tables of Plant P (1200 m, A-204, teaching values):",
        "  five snowfalls, each covering the modules for two days, 90 %",
        f"    lost on those days: {lost / 1e6:.0f} MWh of DC, "
        f"{100 * lost / dc.sum():.2f} % of the year",
        f"  load: ground snow {s_k} kN/m2 x shape {mu} x cos^2(25 deg)",
        f"    = {normal:.0f} Pa normal to the glass",
        "  data-sheet test load 5400 Pa front; with a safety factor 1.5",
        "    the design load may reach 3600 Pa: snow is far below it",
        "  the lower edge 0.6 m above ground lets sliding snow clear;",
        "  real snow loads come from the national code (chapter 29)"])


def mismatch_spread(sigma: float, seed: int = 37) -> float:
    rng = np.random.default_rng(seed)
    base = mppt.PVM_550.at(1000, 25)
    n_str, n_mod = 20, 26
    i_grid = np.linspace(0.5, base.isc * 0.995, 400)
    v_grid = np.linspace(0, n_mod * base.voc, 800)
    i_strings, p_sum = [], 0.0
    for _ in range(n_str):
        v_tot = np.zeros_like(i_grid)
        for _ in range(n_mod):
            k_p = 1 + rng.uniform(0, 5) / 550
            k_i = k_p * (1 + rng.normal(0, sigma))
            k_v = k_p / k_i
            m = mppt.Curve(base.isc * k_i, base.voc * k_v, base.imp * k_i,
                           base.vmp * k_v)
            p_sum += m.mpp(800)[1]
            v_tot += m.v(i_grid)
        order = np.argsort(v_tot)
        i_strings.append(np.interp(v_grid, v_tot[order], i_grid[order],
                                   left=i_grid[-1], right=0.0))
    p_array = (v_grid * np.sum(i_strings, axis=0)).max()
    return 1 - p_array / p_sum


def aged_mismatch() -> None:
    lines = ["mismatch loss as the current spread grows with age (A-205):",
             "  current spread (1 s)   mismatch loss %"]
    for s in (0.007, 0.02, 0.03, 0.05):
        lines.append(f"  {100 * s:19.1f}   {100 * mismatch_spread(s):14.2f}")
    lines += ["  the loss grows roughly with the square of the spread: new",
              "  binned modules lose little; uneven ageing, soiling and",
              "  replaced modules of another class add up over the years"]
    emit("c_mismatch_aged", lines)


def tracker_geometry(limit_deg: float = 55.0):
    """Hourly mean cos(incidence), cos(zenith) and |rotation| of a
    single-axis tracker with a horizontal north-south axis (no
    backtracking, no row shading)."""
    idx = np.arange(8760)
    n, hour = idx // 24 + 1, idx % 24
    ci, cz, rot = np.zeros(8760), np.zeros(8760), np.zeros(8760)
    for s in (np.arange(6) + 0.5) / 6:
        st = solar.solar_time(hour + s, n)
        el, az = solar.sun_position(pvyear10.LAT, n, st)
        e, a = np.radians(el), np.radians(az)
        sx, sz = np.cos(e) * np.sin(a), np.sin(e)
        r = np.clip(np.arctan2(sx, sz), -math.radians(limit_deg),
                    math.radians(limit_deg))
        up = el > 0
        ci += np.where(up, np.clip(sx * np.sin(r) + sz * np.cos(r), 0, None), 0)
        cz += np.where(up, sz, 0)
        rot += np.where(up, np.abs(r), 0)
    return ci / 6, cz / 6, rot / 6, n


def tracker() -> None:
    h = datapack.load_hourly()
    ghi = h["ghi_wm2"].to_numpy(dtype=float)
    dni = h["dni_wm2"].to_numpy(dtype=float)
    dhi = h["dhi_wm2"].to_numpy(dtype=float)
    ci, cz, rot, n = tracker_geometry()
    g0n = 1361.0 * (1 + 0.033 * np.cos(2 * np.pi * n / 365))
    a_i = np.divide(dni, g0n)
    rb = np.divide(ci, cz, out=np.zeros_like(ci), where=cz > 0.087)
    beam = dni * ci
    sky = dhi * (a_i * rb + (1 - a_i) * (1 + np.cos(rot)) / 2)
    ground = ghi * 0.2 * (1 - np.cos(rot)) / 2
    eff_t = beam * pc.iam_ashrae(ci) + (sky + ground) * 0.95
    f = pvyear10.poa()
    t_poa, t_eff = (beam + sky + ground).sum() / 1e3, eff_t.sum() / 1e3
    f_poa, f_eff = f["poa"].sum() / 1e3, f["eff"].sum() / 1e3
    emit("c_tracker", [
        "single-axis tracker (north-south axis, +-55 deg) against fixed",
        "25 deg tables, same sky model (A-206; no backtracking, no shading):",
        f"  fixed 25 deg: POA {f_poa:,.0f} kWh/m2, effective {f_eff:,.0f}",
        f"  tracker:      POA {t_poa:,.0f} kWh/m2, effective {t_eff:,.0f}",
        f"  gain {100 * (t_eff / f_eff - 1):.1f} % of effective irradiance before"
        " shading,",
        "  backtracking losses, motor energy and availability; the",
        "  tracker earns most on clear summer mornings and evenings",
        "  the choice for Plant P (fixed tables, A-183) is revisited with",
        "  costs and wind loads in chapters 18 and 30"])


def t98() -> None:
    """Percentiles of the Faiman module temperature over the year."""
    t = pvyear10.strings()["t_cell"]
    day = pvyear10.poa()["poa"] > 50
    emit("a_t98", [
        "module temperature percentiles over the data-pack year (Faiman):",
        f"  all 8760 h: 98th percentile {np.percentile(t, 98):.1f} C, maximum "
        f"{t.max():.1f} C",
        f"  daylight hours (POA > 50 W/m2): 98th percentile "
        f"{np.percentile(t[day], 98):.1f} C",
        "  open racks at 1200 m stay below the 70 C reference of the",
        "  module safety standard; a roof or a hot desert site may not",
        "  (IEC TS 63126:2025 adds two higher temperature levels)"])


def iv_translate() -> None:
    """A field I-V measurement translated to STC with the linear rule, and
    the effect of biased irradiance and temperature sensors (A-210)."""
    ref = pvyear10.ref_sdm()
    g, tc = 850.0, 48.0
    rng = np.random.default_rng(47)
    p_meas = pc.at_conditions(ref, g, tc, DS.alpha_isc).mpp()[2]
    p_meas *= 1 + rng.normal(0, 0.003)                       # tracer noise
    gamma = -0.0035

    def stc(g_read: float, t_read: float) -> float:
        return p_meas * 1000 / g_read / (1 + gamma * (t_read - 25))

    lines = [f"field I-V point: G {g:.0f} W/m2, cell {tc:.0f} C, measured "
             f"P_max {p_meas:.1f} W (A-210):",
             "  sensors                           G read   T read   P_STC W"]
    for name, gr, tr in (("true irradiance and temperature", g, tc),
                         ("irradiance sensor +1.5 %", g * 1.015, tc),
                         ("back-of-module sensor 2 K low", g, tc - 2),
                         ("both biases", g * 1.015, tc - 2)):
        lines.append(f"  {name:32s}  {gr:6.0f}   {tr:6.1f}   "
                     f"{stc(gr, tr):7.1f}")
    lines += [f"  the module's true STC power is {ref.mpp()[2]:.1f} W; the linear"
              " rule with",
              "  the data-sheet gamma differs from the fitted model (-0.32 %/K);",
              "  sensor bias moves the result more than the rule does: field",
              "  checks rank modules, the laboratory decides (section E)"]
    emit("e_ivfield", lines)


def string_monitor() -> None:
    """Current of a string with bypassed substrings, held at the array
    voltage set by the healthy strings (A-210)."""
    ref = pvyear10.ref_sdm()
    m = pc.at_conditions(ref, 900.0, 50.0, DS.alpha_isc)
    i_grid = np.linspace(0.05, m.isc * 0.999, 2000)
    v_mod = np.asarray(m.v(i_grid))
    v_healthy = 26 * v_mod
    v_a = 26 * m.mpp()[0]                         # array at healthy MPP
    i_h = float(np.interp(v_a, v_healthy[::-1], i_grid[::-1]))
    lines = [f"string current at the array voltage {v_a:.0f} V (900 W/m2,"
             " cell 50 C; A-210):",
             f"  healthy string {i_h:.2f} A",
             "  modules with one substring bypassed   current A   drop %"]
    for k in (1, 2, 4, 8):
        v_f = (26 - k) * v_mod + k * (2 / 3 * v_mod - 0.6)
        i_f = float(np.interp(v_a, v_f[::-1], i_grid[::-1]))
        lines.append(f"  {k:36d}   {i_f:9.2f}   {100 * (1 - i_f / i_h):6.1f}")
    lines += ["  one bypassed substring costs the string about 1.5 % of its",
              "  current; with 1 % measurement noise a 3-sigma alarm (3 %)",
              "  catches two or more; a single one needs trends or I-V curves"]
    emit("c_monitor", lines)


def window_hist() -> None:
    """Hours of the year by string V_mp (20 V bins) for the window figure."""
    v = pvyear10.strings()["v_mp"]
    v = v[v > 0]
    edges = np.arange(880, 1261, 20)
    cnt, _ = np.histogram(v, edges)
    csv("ch10-window.csv", "v,h", [(int(e + 10), int(c))
                                    for e, c in zip(edges[:-1], cnt)])


if __name__ == "__main__":
    window_hist()
    t98()
    iv_translate()
    string_monitor()
    low_light()
    implicit()
    iam_year()
    half_cell()
    sampling()
    fuses()
    cables()
    snow()
    aged_mismatch()
    tracker()
