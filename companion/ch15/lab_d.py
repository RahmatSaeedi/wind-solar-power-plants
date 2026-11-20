"""Chapter 15, section D - reproducible model lab and the chapter's worked
example: the monthly energy balance of Plant P with each loss separate and
gross reconciled to net, the loss waterfall with its balance check, two
assumptions compared (availability as a factor or as outage hours; a
constant soiling loss or the seasonal soiling of chapter 10), and unit and
energy-balance checks.

Run from the project root:   python -m companion.ch15.lab_d
Writes companion/ch15/expected/d_*.txt and diagrams/data/ch15-*.csv.
Model 15.1 (sources.ModelConfig); A-275, A-276.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

import numpy as np

from companion.ch10 import lab_d as l10
from companion.ch15 import lab_f, sources as src
from companion.ch15.common import csv, emit
from plantp import yieldmodel as ym

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def gwh(x) -> float:
    return float(np.sum(x)) / 1e3


def balance() -> None:
    r = src.plant_year()
    m = r["month"]
    cols = {
        "wind gross": r["w_gross"], "wind MV": r["w_av"], "PV gross": r["pv_stc"],
        "PV MV": r["pv_av"], "electrical": r["el_loss"], "own use": r["aux"],
        "curtailed": r["curtailed"], "outage": r["delivered"] - r["net"], "net": r["net"]}
    mon = {k: ym.monthly(v, m) / 1e3 for k, v in cols.items()}
    lines = ["monthly energy balance of Plant P, GWh (model " + src.VERSION + ", long term, S0):",
             "  month  wind gross  wind MV  PV gross  PV MV  elec  own  curt  out    net"]
    rows = []
    for k in range(12):
        v = [mon[c][k] for c in cols]
        lines.append(f"  {MONTHS[k]}   {v[0]:8.2f}  {v[1]:7.2f}  {v[2]:7.2f}  {v[3]:6.2f}  {v[4]:4.2f}"
                     f"  {v[5]:4.2f}  {v[6]:4.2f}  {v[7]:4.2f}  {v[8]:6.2f}")
        rows.append((k + 1, f"{v[1]:.2f}", f"{v[3]:.2f}", f"{v[8]:.2f}"))
    tot = [gwh(v) for v in cols.values()]
    lines.append(f"  year  {tot[0]:9.2f}  {tot[1]:7.2f}  {tot[2]:7.2f}  {tot[3]:6.2f}  {tot[4]:4.2f}"
                 f"  {tot[5]:4.2f}  {tot[6]:4.2f}  {tot[7]:4.2f}  {tot[8]:6.2f}")
    recon = tot[1] + tot[3] - tot[4] - tot[5] - tot[6] - tot[7]
    lines += ["  reconciliation: wind MV + PV MV - electrical - own use",
              f"    - curtailed - outage = {recon:.2f} GWh against net {tot[8]:.2f} GWh",
              f"    (difference {abs(1000 * (recon - tot[8])):.1f} MWh)",
              "  wind and PV losses before MV are in the waterfall (d_waterfall)"]
    emit("d_balance", lines)
    csv("ch15-monthly.csv", "m,wind,pv,net", rows)


def waterfall() -> None:
    r = src.plant_year()
    wf_w = ym.Waterfall("wind").start("gross, 1.225 kg/m3, free stream", r["w_gross"])
    wf_w.apply("air density at the hub", r["w_dens"]).apply("terrain (W2b)", r["w_terr"])
    wf_w.apply("wakes (W2b)", r["w_wake"]).apply("long-term correction", r["w_lt"])
    wf_w.apply("availability", r["w_av"])
    wf_p = ym.Waterfall("pv").start("POA at STC efficiency", r["pv_stc"])
    for lab, k in (("IAM, temperature, low light", "pv_dc_gross"), ("DC wiring and mismatch", "pv_dc"),
                   ("inverter efficiency", "pv_inv"), ("clipping at 49 MW", "pv_clip"),
                   ("soiling and shading", "pv_soil"), ("long-term correction", "pv_lt"),
                   ("degradation, year 1", "pv_deg"), ("availability", "pv_av")):
        wf_p.apply(lab, r[k])
    wf_t = ym.Waterfall("plant").start("wind + PV at MV", r["mv"])
    wf_t.apply("MV and transformer losses", r["after_el"]).apply("own use", r["poc"])
    wf_t.apply("export limit 100 MW", r["delivered"]).apply("grid outages", r["net"])
    lines = ["loss waterfall (model " + src.VERSION + "), each step as % of the energy entering it:"]
    rows = []
    for wf in (wf_w, wf_p, wf_t):
        for lab, e, loss in wf.totals():
            lines.append(f"  {wf.name:5s} {lab:34s} {e / 1e3:8.2f} GWh   {-loss:+6.2f} %")
            rows.append((f"{wf.name}: {lab}", f"{e / 1e3:.2f}"))
        csv(f"ch15-wf{wf.name}.csv", "k,e",
            [(k, f"{e / 1e3:.2f}") for k, (_, e, _) in enumerate(wf.totals())])
        tot, s = wf.check()
        lines.append(f"        total {100 * tot:5.2f} % (product of steps); simple sum"
                     f" {100 * s:5.2f} %")
    lines += ["  a correction can be a gain (long-term wind); percentages of",
              "  successive steps multiply and do not add"]
    emit("d_waterfall", lines)


def compare() -> None:
    """Two assumptions: (1) wind availability as a factor against random
    turbine outage hours of the same energy share; (2) a constant soiling
    loss against the daily seasonal soiling of the chapter 10 station
    under the D-014 trigger policy (A-276)."""
    r = src.plant_year()
    cfg = src.ModelConfig()
    rng = np.random.default_rng(152)
    # (1) availability as outage hours: 1.9 % of hours lose the whole farm
    out = rng.random(8760) < (1 - cfg.av_wind)
    w_hours = np.where(out, 0.0, r["w_lt"])
    mv1 = w_hours + r["pv_av"]
    poc1 = mv1 - (cfg.noload_mw + cfg.loadloss * 100 * (mv1 / 100) ** 2) - r["aux"]
    cur0, cur1 = r["curtailed"].sum(), np.clip(poc1 - 100, 0, None).sum()
    # (2) seasonal soiling: the chapter 10 station year under the trigger
    _, _, _, rain, heavy, rate = l10.station_year()
    trig, _ = lab_f.simulate("truck wet", -0.04, rate, rain, heavy)
    hourly_loss = np.repeat(trig, 24)
    pv_seasonal = r["pv_clip"] * (1 - hourly_loss) * (1 - cfg.shading)
    pv_const = r["pv_clip"] * (1 - cfg.soiling) * (1 - cfg.shading)
    w_const = (r["pv_clip"].sum() - pv_const.sum()) / r["pv_clip"].sum()
    w_seas = (r["pv_clip"].sum() - pv_seasonal.sum()) / r["pv_clip"].sum()
    lines = ["two assumptions compared (A-276):",
             "  (1) wind availability 98.1 %: as a factor or as whole-farm outage hours",
             f"      curtailment {cur0:,.0f} MWh (factor) against {cur1:,.0f} MWh (hours)",
             "  (2) soiling: constant 1.43 % or the station's daily soiling under",
             "      the 4 % trigger (D-014), energy-weighted",
             f"      loss {100 * w_const:.2f} % (constant) against {100 * w_seas:.2f} % (seasonal);"
             f" mean daily loss {100 * trig.mean():.2f} %",
             "  the factor spreads the outage over every hour and cuts the peaks",
             "  that curtailment sees; the seasonal soiling weighs the dusty dry",
             "  season where most energy is made: the order and the shape of a",
             "  loss can matter as much as its average"]
    emit("d_compare", lines)


def checks() -> None:
    r = src.plant_year()
    cfg = src.ModelConfig()
    h = hashlib.sha256(json.dumps(asdict(cfg), sort_keys=True).encode()).hexdigest()[:12]
    neg = int((r["pv_av"] < -1e-9).sum())
    over = int((r["net"] > cfg.export_mw + 1e-9).sum())
    lines = ["unit and energy-balance checks (model " + src.VERSION + "):",
             f"  settings hash {h} (sha-256 of the settings, first 12 characters)",
             f"  8760 hourly values per series; energy = sum of MW x 1 h",
             f"  PV below zero: {neg} h; net above the 100 MW limit: {over} h",
             f"  wind capacity factor at MV {r['w_av'].sum() / (60 * 8760):.3f}; PV (AC)"
             f" {r['pv_av'].sum() / (50 * 8760):.3f}",
             f"  plant capacity factor at the POC {r['net'].sum() / (100 * 8760):.3f}",
             "  every output file carries the model version and this hash:",
             "  the same settings give the same numbers, and a reviewer can",
             "  see which settings made which report"]
    emit("d_checks", lines)


if __name__ == "__main__":
    balance()
    waterfall()
    compare()
    checks()
