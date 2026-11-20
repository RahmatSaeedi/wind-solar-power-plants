"""Chapter 12, more lessons - the resource side of orientation and of the
plant's own records: tracker gain against the beam share by month, ground
albedo as a measured resource (bifacial rear irradiance), aligning the
plant's UTC SCADA export with the station, a typical year from twenty, and
the air-mass distribution behind spectral effects.

Run from the project root:   python -m companion.ch12.examples_more
Writes companion/ch12/expected/m_*.txt and diagrams/data/ch12-*.csv.
Data pack 1.1.0 (S0); teaching values A-249a .. (see the text: A-249).
"""
from __future__ import annotations

from datetime import timedelta

import numpy as np

from companion.ch05 import step2_reader
from companion.ch10 import examples_more as ch10m, pvyear10
from companion.ch12 import sources
from companion.ch12.common import csv, emit
from plantp import datapack, irradiance as ir, pvcell as pc

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def tracker_months() -> None:
    p = sources.pack()
    ci, cz, rot, n = ch10m.tracker_geometry()
    a_i = np.divide(p["dni"], p["g0n"])
    rb = np.divide(ci, cz, out=np.zeros_like(ci), where=cz > 0.087)
    t_poa = (p["dni"] * ci + p["dhi"] * (a_i * rb + (1 - a_i) * (1 + np.cos(rot)) / 2)
             + p["ghi"] * 0.2 * (1 - np.cos(rot)) / 2)
    f_poa = pvyear10.poa()["poa"]
    rows, lines = [], ["single-axis tracker against fixed 25 deg, month by month:",
                       "  month  beam share  K_T     gain"]
    for m in range(12):
        sel = p["month"] == m
        beam = np.sum(p["dni"][sel] * p["cz"][sel]) / p["ghi"][sel].sum()
        kt = p["ghi"][sel].sum() / np.sum(p["g0n"][sel] * np.clip(p["cz"][sel], 0, None))
        g = t_poa[sel].sum() / f_poa[sel].sum() - 1
        rows.append((m + 1, f"{beam:.3f}", f"{100 * g:.2f}"))
        lines.append(f"  {MONTHS[m]}    {beam:.3f}      {kt:.3f}   {100 * g:+5.1f} %")
    b = np.array([float(r[1]) for r in rows])
    g = np.array([float(r[2]) for r in rows])
    slope = np.polyfit(b, g, 1)[0]
    lines += [f"  year: {100 * (t_poa.sum() / f_poa.sum() - 1):+.1f} %; across the months the"
              f" gain rises about {slope / 10:.1f} points",
              "    per 0.1 of beam share (with the sun's height: summer has both)",
              "  in winter the horizontal tracker loses to the tilted table;",
              "  the tracker sells beam light: the decision needs the DNI (or",
              "  the beam share) of the site, measured or from a checked source,",
              "  not only the GHI"]
    emit("m_tracker", lines)
    csv("ch12-tracker.csv", "month,beam,gain", rows)


def albedo() -> None:
    """Rear irradiance of a bifacial table as a linear function of albedo
    (teaching model fitted to chapter 10's 12 % of GHI at albedo 0.2):
    rear / GHI = 0.02 + 0.5 albedo (A-249)."""
    p = sources.pack()
    f_poa = pvyear10.poa()["poa"]
    day = np.arange(8760) // 24
    dry = (day >= 120) & (day < 300)
    measured = np.where(dry, 0.25, 0.18)                  # dry grass / wet soil
    snow = (day >= 15) & (day < 20)
    measured = np.where(snow, 0.60, measured)
    lines = ["ground albedo as a measured resource (bifacial, B_f 0.70, A-249):",
             "  albedo                     rear / front   bifacial gain"]
    gains = []
    for name, alb in (("constant 0.20 (assumed)", np.full(8760, 0.20)),
                      ("measured, seasonal", measured),
                      ("constant 0.30", np.full(8760, 0.30))):
        rear = p["ghi"] * (0.02 + 0.5 * alb)
        gain = 0.70 * rear.sum() / f_poa.sum()
        gains.append(gain)
        lines.append(f"  {name:26s} {rear.sum() / f_poa.sum():.4f}        {100 * gain:5.2f} %")
    lines += ["  an albedometer (one pyranometer up, one down) over a year of",
              "  seasons, plus rear-side reference cells, replaces the assumed",
              f"  0.20; each 0.1 of albedo is about {100 * (gains[2] - gains[0]):.1f}"
              " points of bifacial gain"]
    emit("m_albedo", lines)


def scada_alignment() -> None:
    rows, issues = step2_reader.read_scada(datapack.raw_path("pv_scada_export.csv"))
    h = datapack.load_hourly()
    poa = pvyear10.poa()["poa"]
    idx = {t.to_pydatetime().replace(tzinfo=None): k for k, t in enumerate(h.index)}
    lines = ["the plant's SCADA export (UTC, decimal comma) against the station:",
             f"  {len(rows)} hourly rows, issues {len(issues)}"]
    out = {}
    for name, shift in (("UTC converted to +04:00", 4), ("UTC read as local", 0)):
        e, g = [], []
        for r in rows:
            t = (r["start"] + timedelta(hours=shift)).replace(tzinfo=None)
            k = idx.get(t)
            if k is not None:
                e.append(r["energy_mwh"])
                g.append(poa[k])
        e, g = np.array(e), np.array(g)
        day = e.sum() / (60.06 * g.sum() / 1000)
        r_ = float(np.corrcoef(e, g)[0, 1])
        out[name] = (day, r_)
        lines.append(f"  {name}: PR over the export {day:.3f}")
        lines.append(f"    hourly correlation of energy and POA r = {r_:.3f}")
    lines += ["  the period's PR barely notices a four-hour error, because the",
              "  sums over whole days are the same; the hour-by-hour correlation",
              "  collapses: check alignment hourly, report daily",
              "  (the export was made with chapter 5's simple model, so its PR",
              "  is not chapter 10's)"]
    emit("m_scada", lines)


def typical_year() -> None:
    lt = sources.long_term()
    mon = lt["monthly"]
    mean_m = mon.mean(axis=0)
    pick = [int(np.argmin(np.abs(mon[:, m] - mean_m[m]))) for m in range(12)]
    tmy = np.array([mon[pick[m], m] for m in range(12)])
    ann = lt["annual"]
    order = np.sort(ann)
    p90_year = order[int(np.floor(0.10 * (len(ann) - 1)))]
    lines = ["a typical year from the 20-year provider record (A-241):",
             "  month  chosen year  sum kWh/m2  20-year mean"]
    for m in range(12):
        lines.append(f"  {MONTHS[m]}     {int(lt['years'][pick[m]])}       {tmy[m]:7.1f}"
                     f"      {mean_m[m]:7.1f}")
    lines += [f"  typical year {tmy.sum():,.1f} kWh/m2 against the long-term mean"
              f" {ann.mean():,.1f}",
              f"  a low year (10th percentile of the twenty) {p90_year:,.1f} kWh/m2",
              "  a typical year keeps realistic weather sequences for hourly",
              "  models (storage, clipping); it is a P50-like year, not a P90",
              "  year: a 'P90 year' is built by scaling, with care"]
    emit("m_tmy", lines)
    csv("ch12-tmy.csv", "month,tmy,mean", [(m + 1, f"{tmy[m]:.1f}", f"{mean_m[m]:.1f}")
                                           for m in range(12)])


def air_mass_dist() -> None:
    p = sources.pack()
    z = np.degrees(np.arccos(np.clip(p["cz"], 1e-6, 1)))
    am = np.nan_to_num(ir.air_mass(z), nan=99)
    g = p["ghi"]
    bins = [(1.0, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 99.0)]
    lines = ["GHI by air mass over the year (hour-mean sun):",
             "  air mass      share of GHI"]
    for a, b in bins:
        sel = (am >= a) & (am < b)
        lines.append(f"  {a:.1f} - {b if b < 50 else 'more':>4}    {100 * g[sel].sum() / g.sum():5.1f} %")
    lines += ["  the reference spectrum of module ratings is air mass 1.5",
              "  (IEC 60904-3:2019); most of this site's energy arrives near it,",
              "  low winter and morning sun is redder, which crystalline silicon",
              "  minds less than some thin-film technologies (chapter 10)"]
    emit("m_airmass", lines)


if __name__ == "__main__":
    tracker_months()
    albedo()
    scada_alignment()
    typical_year()
    air_mass_dist()
