"""Chapter 9 - last lessons: the plant controller at the 100 MW export
limit (curtailment shared between PV inverters and turbine converters) and
an acceptance decision for a factory heat run with measurement uncertainty.

Run from the project root:   python -m companion.ch09.examples_more3
Writes companion/ch09/expected/z_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-178, A-179 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import numpy as np

from companion.ch09 import pvyear
from companion.ch09.common import csv, emit
from companion.ch09.examples_a import EFF_POINTS
from plantp import datapack, pe


def export_limit() -> None:
    h = datapack.load_hourly()
    pc = datapack.load_power_curve()
    ws = h["ws_100m_ms"].to_numpy(dtype=float)
    p_w = 12 * np.interp(ws, pc["wind_speed_ms"], pc["power_kw"]) / 1e3
    p_w *= 0.97                                                  # A-178
    r = pvyear.inverter_year(pe.fit_loss_coeffs(EFF_POINTS))
    p_pv = r["p_out"] / 1e6
    tot = p_w + p_pv
    over = np.maximum(tot - 100.0, 0.0)
    hours = int((over > 0).sum())
    e_cut = over.sum()
    pv_first = np.minimum(over, p_pv).sum()
    lines = ["the 100 MW export limit over the data-pack year (A-178):",
             f"  wind {p_w.sum() / 1e3:.1f} GWh, PV {p_pv.sum() / 1e3:.1f} GWh,"
             f" peak sum {tot.max():.1f} MW",
             f"  hours above 100 MW: {hours}; energy to curtail "
             f"{e_cut:,.0f} MWh ({100 * e_cut / tot.sum():.2f} %)",
             f"  if PV is curtailed first it carries {100 * pv_first / e_cut:.0f}"
             " % of the cut",
             "  the plant controller measures the export, splits the cut among",
             "  inverters and turbines and sends set-points every second or so;",
             "  inverters answer in tens of milliseconds, turbines more slowly",
             "  through pitch and torque"]
    emit("z_export", lines)
    srt = np.sort(tot)[::-1][:1200]
    csv("ch09-export.csv", "k,p", [(k, f"{v:.2f}") for k, v in
                                    enumerate(srt) if k % 4 == 0])


def heat_run() -> None:
    rng = np.random.default_rng(31)                              # A-179
    t = np.arange(0, 4 * 60 + 1, 2.0)                            # minutes
    lines = ["factory heat run, hottest module temperature (A-179):",
             "  limit 90 C; expanded uncertainty 1.5 K (k 2); acceptance",
             "  below 90 - 1.5 = 88.5 C (guard band, chapter 2)"]
    rows = []
    for name, t_ss in (("unit A", 86.2), ("unit B", 88.9)):
        temp = 40 + (t_ss - 40) * (1 - np.exp(-t / 35.0))
        temp += rng.normal(0, 0.25, len(t))
        last = temp[-15:].mean()
        tail = temp[t >= 180]
        slope = np.polyfit(t[t >= 180], tail, 1)[0] * 60
        verdict = ("accept" if last < 88.5 else
                   "not proven (guard band)" if last < 90 else
                   "reject")
        lines.append(f"  {name}: final {last:.1f} C, slope in the last hour "
                     f"{slope:+.2f} K/h")
        lines.append(f"    -> {verdict}")
        rows.append(temp)
    lines += ["  a reading below the limit is not yet a pass: with the",
              "  uncertainty it may lie above it; the contract states the",
              "  decision rule before the test (chapter 2, conformity)"]
    emit("z_heatrun", lines)
    csv("ch09-heatrun.csv", "t,a,b", [(f"{a:.0f}", f"{b:.2f}", f"{c:.2f}")
                                      for a, b, c in zip(t, rows[0], rows[1])])


if __name__ == "__main__":
    export_limit()
    heat_run()
