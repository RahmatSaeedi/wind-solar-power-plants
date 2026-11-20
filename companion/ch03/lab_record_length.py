"""Chapter 3 laboratory 2 — how long must we measure? Sampling error against record length.

Run from the project root:   python -m companion.ch03.lab_record_length
Builds many synthetic "measurement campaigns" of N days by resampling whole days of the
data-pack year (block bootstrap), estimates the annual wind energy from each campaign, and
reports how the spread of the estimates shrinks with N. Only sampling WITHIN one synthetic
year is represented; year-to-year variability is extra (chapter 16).
Writes companion/ch03/expected/lab_record_length.txt and diagrams/data/ch03-n-record.csv.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "expected" / "lab_record_length.txt"
DATA = HERE.parents[1] / "diagrams" / "data" / "ch03-n-record.csv"


# [start: campaign]
def campaign_estimates(daily_energy, n_days, n_campaigns, rng):
    """Annual energy from n_days days drawn with replacement."""
    picks = rng.integers(0, daily_energy.size, size=(n_campaigns, n_days))
    return daily_energy[picks].mean(axis=1) * 365.0
# [end: campaign]


def main() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    p_kw = np.interp(hourly["ws_100m_ms"].to_numpy(), curve["wind_speed_ms"], curve["power_kw"])
    daily = p_kw.reshape(365, 24).sum(axis=1) * 12 * 0.88 / 1e6      # GWh per day, farm
    truth = daily.sum()
    rng = np.random.default_rng(20260110)
    lines = [f"annual wind energy of the data-pack year: {truth:.1f} GWh",
             f"{'days':>6s} {'std (GWh)':>10s} {'std (%)':>8s} {'std x sqrt(days)':>17s}"]
    rows = []
    for n in (30, 60, 90, 180, 365, 730):
        est = campaign_estimates(daily, n, 4000, rng)
        sd = float(est.std(ddof=1))
        rows.append((n, f"{sd:.3f}", f"{100 * sd / truth:.3f}"))
        lines.append(f"{n:6d} {sd:10.2f} {100 * sd / truth:8.2f} {sd * math.sqrt(n):17.1f}")
    lines.append("the last column is nearly constant: the spread falls as 1/sqrt(days)")
    lines.append("a one-month campaign misses the seasons; resampled days pretend the season")
    lines.append("    of each day is random, so even these numbers are optimistic for 30 days")
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("days,std_gwh,std_pct\n")
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
