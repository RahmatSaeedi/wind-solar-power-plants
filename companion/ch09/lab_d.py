"""Chapter 9, section D - modelling and verification lab: MPPT through a
cloud edge, partial shading and the global scan, analytical against
switched-simulation losses, the DC voltage window over the data-pack year,
and the inverters' energy budget for the year.

Run from the project root:   python -m companion.ch09.lab_d
Writes companion/ch09/expected/d_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-153, A-164, A-165; data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch09 import pvyear
from companion.ch09.common import csv, emit
from companion.ch09.examples_a import DEV_WIND, EFF_POINTS
from plantp import mppt as mp, pe

S2, S3 = math.sqrt(2), math.sqrt(3)


def cloud_profile(seed: int = 23, dt: float = 0.1, t_end: float = 300.0):
    """Irradiance through a passing cloud edge (synthetic, A-164): 900 W/m2,
    down to 300 W/m2 in 10 s, held a minute, back up in 20 s, with small
    seeded fluctuations."""
    t = np.arange(int(t_end / dt)) * dt
    g = np.full(len(t), 900.0)
    g = np.where((t >= 60) & (t < 70), 900 - 60 * (t - 60), g)
    g = np.where((t >= 70) & (t < 130), 300.0, g)
    g = np.where((t >= 130) & (t < 150), 300 + 30 * (t - 130), g)
    rng = np.random.default_rng(seed)
    noise = np.convolve(rng.normal(0, 8, len(t)), np.ones(20) / 20, "same")
    return t, np.clip(g + noise, 50, None)


# [start: track]
def track(tracker, t, g, tc: float = 50.0, n_mod: int = 26):
    """Run a tracker against changing irradiance: every step the converter
    holds the string at the tracker's voltage, the tracker reads (V, I) and
    returns the next reference. Returns operating and available power."""
    p_op, p_av = np.empty(len(t)), np.empty(len(t))
    v = tracker.v_ref
    for k, gk in enumerate(g):
        curve = mp.PVM_550.at(gk, tc, n_mod)
        i = float(curve.i(v))
        p_op[k] = v * i
        p_av[k] = curve.mpp(800)[1]
        v = min(max(tracker.update(v, i), 0.0), curve.voc)
    return p_op, p_av
# [end: track]


def mppt_cloud() -> None:
    t, g = cloud_profile()
    c0 = mp.PVM_550.at(900, 50, 26)
    runs = {}
    for name, trk in (("P&O 5 V", mp.PerturbObserve(0.9 * c0.voc, 5.0)),
                      ("P&O 15 V", mp.PerturbObserve(0.9 * c0.voc, 15.0)),
                      ("IncCond 5 V", mp.IncrementalConductance(0.9 * c0.voc, 5.0))):
        runs[name] = track(trk, t, g)
    fixed_v = c0.vmp
    p_fix = np.array([fixed_v * float(mp.PVM_550.at(gk, 50, 26).i(fixed_v))
                      for gk in g])
    p_av = runs["P&O 5 V"][1]
    lines = ["one string through a cloud edge, steps every 0.1 s (A-164):",
             f"  available energy {p_av.sum() * 0.1 / 3.6e6:.3f} kWh in 300 s",
             "  tracker          tracking efficiency   during the ramps"]
    ramp = ((t >= 60) & (t < 70)) | ((t >= 130) & (t < 150))
    for name, (p_op, _) in runs.items():
        lines.append(f"  {name:14s} {100 * p_op.sum() / p_av.sum():12.2f} %"
                     f"   {100 * p_op[ramp].sum() / p_av[ramp].sum():12.2f} %")
    lines.append(f"  fixed voltage  {100 * p_fix.sum() / p_av.sum():12.2f} %   "
                 f"{100 * p_fix[ramp].sum() / p_av[ramp].sum():12.2f} %")
    d = pvyear.hourly()
    v_fix = mp.PVM_550.at(1000, 25, 26).vmp
    e_mpp = e_fix = 0.0
    for c in d["curves"]:
        if c is not None:
            e_mpp += c.mpp(400)[1]
            e_fix += v_fix * float(c.i(v_fix))
    lines += ["  within minutes the cell temperature hardly moves and neither",
              "  does V_mp: a fixed voltage keeps up; the ramps separate the",
              "  trackers (P&O can mistake rising irradiance for a good step)",
              f"  over the data-pack year, holding the STC voltage "
              f"{v_fix:.0f} V would",
              f"    capture only {100 * e_fix / e_mpp:.1f} % of the MPP energy:"
              " temperature moves V_mp"]
    emit("d_mppt", lines)
    keys = list(runs)
    csv("ch09-mppt.csv", "t,av," + ",".join(f"k{i}" for i in range(len(keys))),
        [(f"{t[i]:.1f}", f"{p_av[i] / 1e3:.3f}") +
         tuple(f"{runs[k][0][i] / 1e3:.3f}" for k in keys)
         for i in range(0, len(t), 5)])


def shading() -> None:
    sun = mp.PVM_550.at(900, 50, 18)
    shade = mp.PVM_550.at(300, 40, 8)
    v, i, p = mp.pv_curve_partial([sun, shade])
    k = int(np.argmax(p))
    order = np.argsort(v)
    v_s, i_s = v[order], i[order]

    def i_of_v(x):
        return float(np.interp(x, v_s, i_s, right=0.0))

    po = mp.PerturbObserve(v_ref=0.95 * v.max(), step=5.0)
    vv = po.v_ref
    for _ in range(300):
        vv = po.update(vv, i_of_v(vv))
    v_g = mp.global_scan(i_of_v, 0.0, float(v.max()), 80)
    po2 = mp.PerturbObserve(v_ref=v_g, step=5.0)
    vg = po2.v_ref
    for _ in range(100):
        vg = po2.update(vg, i_of_v(vg))
    lines = ["one string, 18 modules at 900 W/m2 and 8 shaded at 300 W/m2"
             " (A-164):",
             f"  global peak {p[k] / 1e3:.2f} kW at {v[k]:.0f} V (shaded"
             " modules bypassed)",
             f"  P&O from 0.95 V_oc settles at {vv:.0f} V: "
             f"{vv * i_of_v(vv) / 1e3:.2f} kW (a local peak)",
             f"  global scan, then P&O: {vg:.0f} V, {vg * i_of_v(vg) / 1e3:.2f}"
             " kW",
             f"  gain of the scan {100 * (vg * i_of_v(vg) / (vv * i_of_v(vv)) - 1):.0f}"
             " % while the shade lasts; the scan itself costs a",
             "  second or two of off-peak operation every few minutes"]
    emit("d_shading", lines)
    v_grid = np.linspace(0.0, float(v.max()), 300)
    p_grid = v_grid * np.interp(v_grid, v_s, i_s, right=0.0)
    csv("ch09-shade.csv", "v,p", [(f"{a:.1f}", f"{b / 1e3:.3f}")
                                  for a, b in zip(v_grid, p_grid)])


def loss_compare() -> None:
    s, v_ll, v_dc, pf = 5.26e6, 690.0, 1150.0, 0.95
    i_pk = s / (S3 * v_ll) * S2
    m = 2 * S2 * v_ll / S3 / v_dc
    phi = math.degrees(math.acos(pf))
    d = DEV_WIND
    ct, cd = pe.conduction_losses(i_pk, m, pf, d["v_t0"], d["r_t"], d["v_d0"],
                                  d["r_d"])
    st, sd = pe.switching_losses(i_pk, v_dc, 2500, d["e_on_off"], d["e_rr"],
                                 d["i_ref"], d["v_ref"])
    ana = ct + cd + st + sd
    lines = ["one switch position of the turbine grid-side converter, 2.5 kHz:",
             f"  closed form (no ripple): IGBT {ct + st:,.0f} W, diode "
             f"{cd + sd:,.0f} W, total {ana:,.0f} W",
             "  switched simulation, one period, ripple through L:",
             "  L uH   ripple A pp   IGBT W   diode W   total W   difference"]
    for l_h in (200e-6, 100e-6, 50e-6, 25e-6):
        r = pe.leg_losses_switched(i_pk, m, phi, v_dc, 2500, l_h, d)
        tot = r["cond_t"] + r["sw_t"] + r["cond_d"] + r["sw_d"]
        lines.append(f"  {l_h * 1e6:4.0f}   {r['ripple_pp']:9,.0f}   "
                     f"{r['cond_t'] + r['sw_t']:6,.0f}   "
                     f"{r['cond_d'] + r['sw_d']:7,.0f}   {tot:7,.0f}   "
                     f"{100 * (tot / ana - 1):+6.1f} %")
    lines += ["  the closed form is good to a few per cent while the ripple is",
              "  small; with a large ripple the current at each switching",
              "  instant differs from the sine and the estimate drifts"]
    emit("d_losses", lines)


def window() -> None:
    d = pvyear.hourly()
    lines = ["DC window over the data-pack year (1.1.0, S0; A-153):",
             f"  string MPP voltage: min {d['v_mp'][d['v_mp'] > 0].min():.0f} V,"
             f" median {np.median(d['v_mp'][d['v_mp'] > 0]):.0f} V, max "
             f"{d['v_mp'].max():.0f} V",
             "  AC V   floor V   hours below   energy lost MWh   share of DC"]
    for v_ac in (600, 630, 660, 690):
        h, mwh, share = pvyear.window_loss(v_ac)
        lines.append(f"  {v_ac:4d}   {pe.vdc_min(v_ac, headroom=0.1):7.0f}   "
                     f"{h:11d}   {mwh:15,.1f}   {100 * share:9.3f} %")
    lines += ["  with 26-module strings a 690 V inverter would leave a tenth",
              "  of the energy in the array; 600 V keeps all of it (D-012)"]
    emit("d_window", lines)
    vm = d["v_mp"][d["v_mp"] > 0]
    edges = np.arange(850, 1125, 10)
    hist, _ = np.histogram(vm, edges)
    csv("ch09-vmp.csv", "v,hours", [(int(a + 5), int(b))
                                    for a, b in zip(edges[:-1], hist)])


def annual() -> None:
    c = pe.fit_loss_coeffs(EFF_POINTS)
    r = pvyear.inverter_year(c)
    e = {k: r[k].sum() / 1e6 for k in ("p_dc", "p_ac", "p_out", "loss",
                                       "clip", "derate")}
    lines = ["inverters through the data-pack year (A-147, A-153, D-012):",
             f"  DC energy at the inverters  {e['p_dc']:9,.0f} MWh",
             f"  conversion losses           {e['loss']:9,.0f} MWh "
             f"({100 * e['loss'] / e['p_dc']:.2f} %)",
             f"  clipping at 50 MW           {e['clip']:9,.1f} MWh",
             f"  temperature and altitude    {e['derate']:9,.1f} MWh",
             f"  AC energy delivered         {e['p_out']:9,.0f} MWh",
             f"  site-weighted efficiency    {e['p_ac'] / e['p_dc']:.4f}; "
             f"European {pe.weighted_efficiency(c, pe.EURO_WEIGHTS):.4f}, "
             f"CEC {pe.weighted_efficiency(c, pe.CEC_WEIGHTS):.4f}"]
    x = r["p_dc"] / 50e6
    bins = [(0.0, 0.075, "5 %"), (0.075, 0.15, "10 %"), (0.15, 0.25, "20 %"),
            (0.25, 0.4, "30 %"), (0.4, 0.75, "50 %"), (0.75, 2.0, "100 %")]
    lines.append("  share of DC energy by load (bins around the European points):")
    parts = []
    for lo, hi, name in bins:
        sel = (x > lo) & (x <= hi)
        parts.append(f"{name} {100 * r['p_dc'][sel].sum() / r['p_dc'].sum():.0f}")
    lines.append("    " + ", ".join(parts) + " (per cent)")
    lines += ["  this site weights mid and high loads more than the European",
              "  convention does: judge efficiency with the site's own weights"]
    emit("d_annual", lines)


if __name__ == "__main__":
    mppt_cloud()
    shading()
    loss_compare()
    window()
    annual()
