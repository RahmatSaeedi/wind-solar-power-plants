"""Chapter 27 - expansion round 6: a compliance summary from the
measurement week, reconciling the units' meters with the POC meter, how
often frequency response is active, the damping of a recorded power
oscillation, and the data volume of the monitoring plan.

Run from the project root:   python -m companion.ch27.examples_t
Writes companion/ch27/expected/t_*.txt and diagrams/data/ch27-ringdown.csv.
Synthetic data and teaching limits (A-336 to A-339).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import pq


def compliance() -> None:
    w = src.week()
    rows = [("5th harmonic voltage %", pq.percentile(w["v5_pct"], 95), 2.0),
            ("voltage THD %", 2.14, 3.0),
            ("Plt (2 h)", 0.44, 0.8),
            ("voltage unbalance %", 0.88, 1.4),
            ("rapid voltage change %", 0.82, 3.0)]
    lines = ["compliance summary at the POC for the measurement week",
             "  (95th percentiles where weekly; limits are TEACHING placeholders",
             "  for the operator's values - U-100)",
             "  index                      measured   limit   margin    status"]
    for name, m, lim in rows:
        lines.append(f"  {name:24s} {m:10.2f}   {lim:5.1f}   {1 - m / lim:6.0%}    "
                     f"{'within' if m <= lim else 'OVER'}")
    lines += ["  the summary states the instrument class, the flagged",
              "  intervals, the uncertainty near a limit (lesson K) and the",
              "  operator's limit source - a table of numbers alone is not",
              "  a compliance statement"]
    emit("t_compliance", lines)


def balance() -> None:
    units = 101.8
    losses = {"unit transformers": 0.9, "collector cables": 0.6, "main transformers": 0.4, "line": 0.5}
    expected = units - sum(losses.values())
    poc = 98.9
    diff = poc - expected
    lines = ["do the numbers add up? one hour at high output (teaching)",
             f"  sum of the units' meters             {units:6.1f} MW"]
    for k, v in losses.items():
        lines.append(f"  - {k:34s} {v:6.1f} MW")
    lines += [f"  expected at the POC                  {expected:6.1f} MW",
              f"  POC revenue meter                    {poc:6.1f} MW",
              f"  unexplained                          {diff:+6.1f} MW ({diff / poc:+.1%})",
              "  an unexplained 0.5 % is larger than the meters' classes",
              "  allow: a unit meter, a loss model or a transducer is",
              "  wrong; the reconciliation runs every month and a",
              "  persistent gap is investigated like a PQ complaint"]
    emit("t_balance", lines)


def frequency_stats() -> None:
    rng = np.random.default_rng(282)
    n = 7 * 8640                                 # 10-s values for a week
    f = 50 + np.convolve(rng.normal(0, 0.07, n), np.ones(30) / math.sqrt(30), mode="same")
    over = np.mean(f > 50.2)
    under = np.mean(f < 49.8)
    lines = ["frequency at the POC for a week (synthetic 10-s means)",
             f"  standard deviation {np.std(f) * 1000:.0f} mHz; 99.5 % of values within"
             f" +/- {np.percentile(np.abs(f - 50), 99.5) * 1000:.0f} mHz",
             f"  outside the 0.2 Hz deadband: {100 * (over + under):.2f} % of the time",
             "  the droop service acts rarely here, so its energy cost is",
             "  small; on a smaller, weaker system the same deadband is",
             "  crossed far more often - the service's cost and its",
             "  testing depend on the grid it serves"]
    emit("t_frequency", lines)


def ringdown() -> None:
    t = np.arange(0, 10, 0.02)
    f_osc, zeta = 0.8, 0.06
    wn = 2 * math.pi * f_osc
    p = 3.0 * np.exp(-zeta * wn * t) * np.cos(wn * math.sqrt(1 - zeta ** 2) * t)
    csv("ch27-ringdown.csv", "t,p", [(f"{a:.2f}", f"{b:.3f}") for a, b in zip(t, p)])
    peaks = [k for k in range(1, len(p) - 1) if p[k] > p[k - 1] and p[k] > p[k + 1] and p[k] > 0]
    a1, a2 = p[peaks[0]], p[peaks[1]]
    delta = math.log(a1 / a2)
    z_est = delta / math.sqrt(4 * math.pi ** 2 + delta ** 2)
    f_est = 1 / (t[peaks[1]] - t[peaks[0]])
    lines = ["damping of a recorded power oscillation (ringdown, synthetic)",
             f"  first two peaks {a1:.2f} and {a2:.2f} MW, {t[peaks[1]] - t[peaks[0]]:.2f} s apart",
             f"  frequency {f_est:.2f} Hz; log decrement {delta:.3f}; damping ratio {z_est:.3f}",
             "  a teaching acceptance of 5 % damping: "
             + ("met" if z_est >= 0.05 else "not met"),
             "  an oscillation that dies slowly is a sign of control",
             "  interaction (plant controller, converters, a weak grid);",
             "  the operator may require a minimum damping and the model",
             "  must show the same mode (ch 28)"]
    emit("t_ringdown", lines)


def volume() -> None:
    channels = 3 * 30 + 20                 # buses x quantities (teaching)
    values_10min = channels * 144 * 365
    events = 400 * 2 * 2e6                 # events, 2 s, 2 MB/s of waveform (teaching)
    lines = ["data volume of the permanent monitoring plan (teaching)",
             f"  {channels} channels of 10-minute values: {values_10min / 1e6:.1f} million values a year"
             f" (~{values_10min * 8 / 1e9:.2f} GB)",
             f"  400 recorded events a year of 2 s waveforms: ~{events / 1e9:.1f} GB",
             f"  five years kept: about {5 * (values_10min * 8 + events) / 1e9:.0f} GB - small for"
             " storage, large for",
             "  people: the plan says who reads what (weekly summary,",
             "  every event over a threshold) and how a finding becomes",
             "  an investigation"]
    emit("t_volume", lines)


if __name__ == "__main__":
    compliance()
    balance()
    frequency_stats()
    ringdown()
    volume()
