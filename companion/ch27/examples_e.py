"""Chapter 27, section E - service performance from test records: the
metrics of a voltage set-point step, the droop measured from a frequency
event, ramp-limit compliance on a broken-cloud day, telemetry
completeness and latency, the measurement location, and an acceptance
matrix.

Run from the project root:   python -m companion.ch27.examples_e
Writes companion/ch27/expected/e_*.txt and diagrams/data/ch27-*.csv.
Synthetic test data (A-339); acceptance criteria are teaching values -
the operator's code and the service contract give the real ones.
"""
from __future__ import annotations

import numpy as np

from companion.ch12 import sources as s12
from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import pq


def step() -> None:
    d = src.voltage_step()
    m = pq.step_metrics(d["t"], d["q"], d["q0"], d["q1"], band=0.05)
    csv("ch27-step.csv", "t,q", [(f"{a:.1f}", f"{b:.2f}") for a, b in zip(d["t"], d["q"])])
    crit = {"rise": 1.0, "settle": 5.0, "overshoot": 0.15}
    lines = ["voltage set-point step at the POC: reactive power response (A-339)",
             "  metric           measured   teaching criterion   result"]
    for k, unit in (("rise", "s"), ("settle", "s"), ("overshoot", "")):
        v = m[k]
        txt = f"{v:.2f} {unit}" if unit else f"{v:.0%}"
        ctxt = f"<= {crit[k]} {unit}" if unit else f"<= {crit[k]:.0%}"
        lines.append(f"  {k:15s} {txt:>9s}   {ctxt:>18s}   {'pass' if v <= crit[k] else 'FAIL'}")
    lines += ["  noise on the record makes 'settled' a matter of definition:",
              "  the band (here 5 % of the step) and the filtering belong to",
              "  the test procedure agreed beforehand, not chosen after",
              "  seeing the data"]
    emit("e_step", lines)


def droop() -> None:
    d = src.frequency_event()
    df = d["f"] - 50.0
    dp = (d["p"] - 80.0) / 100.0
    measured = pq.droop_fit(df, dp, 0.2)
    csv("ch27-droop.csv", "t,f,p", [(int(a), f"{b:.3f}", f"{c:.2f}") for a, b, c in zip(d["t"], d["f"], d["p"])])
    peak = float(df.max())
    lines = ["over-frequency event: droop measured from 1-s records (A-339)",
             f"  peak frequency {50 + peak:.3f} Hz; deadband 0.2 Hz (setting); set droop 4 %",
             f"  least-squares droop from the record: {measured:.2f} %",
             f"  power reduction at the peak: {(80 - d['p'].min()):.1f} MW;"
             f" expected {100 * (peak - 0.2) / (50 * 0.04):.1f} MW",
             "  the fit uses only samples outside the deadband; noise on",
             "  both channels widens the uncertainty - the agreed method",
             "  states the sample rate, the filter and the fitting window"]
    emit("e_droop", lines)


def ramps() -> None:
    g = s12.minute_days()["broken"]["true"]
    pv = np.clip(50.0 * g / 1000.0 * 0.9, 0, 50.0)
    lines = ["ramp-limit compliance on a broken-cloud day (50 MW PV, minute data)",
             "  limit MW/min   minutes over the limit   share of daylight minutes"]
    day = int(np.sum(pv > 0.5))
    for lim in (10.0, 5.0, 2.0):
        frac = pq.ramp_exceedance(pv, lim)
        lines.append(f"  {lim:12.0f}   {frac * len(pv):22.0f}   {frac * len(pv) / day:24.1%}")
    lines += ["  without storage the PV alone breaks a tight ramp limit in",
              "  many minutes of a broken-cloud day; the battery of ch 20",
              "  holds it - the evidence is the POC record, counted by the",
              "  agreed rule (does a falling ramp from a cloud count?)"]
    emit("e_ramps", lines)


def telemetry() -> None:
    rng = np.random.default_rng(274)
    n = 7 * 86400 // 4                       # 4 s samples for a week
    lost = rng.random(n) < 0.003
    scattered = int(lost.sum())
    lost[50000:50900] = True                 # one hour-long gap (900 samples)
    gap_share = (int(lost.sum()) - scattered) / int(lost.sum())
    lat = rng.gamma(2.0, 0.4, n)
    lines = ["telemetry to the operator for a week (4 s samples, synthetic):",
             f"  expected {n:,}, received {int((~lost).sum()):,}: completeness"
             f" {pq.completeness(n, int((~lost).sum())):.2%}",
             f"  latency: median {np.median(lat):.2f} s, 99th percentile {np.percentile(lat, 99):.2f} s",
             f"  one hour-long gap holds {gap_share:.0%} of the loss: a contract that",
             "  counts availability by the month hides it, one that counts",
             "  gaps longer than a set time shows it - the counting rule is",
             "  part of the service definition"]
    emit("e_telemetry", lines)


def location() -> None:
    lines = ["the same service measured at two places (full export, teaching):",
             "  quantity                at the unit terminals   at the POC",
             "  reactive power Mvar                   68.1          55.8",
             "  voltage pu                            1.04          1.00",
             "  response delay s                      0.10          0.25",
             "  the transformers and the line take reactive power, the",
             "  plant controller adds delay: a capability or a response",
             "  proved at the terminals is not proved at the POC, where",
             "  the requirement applies (lesson B; ch 20)"]
    emit("e_location", lines)


def acceptance() -> None:
    rows = [("reactive capability", "P-Q points at the POC", "measured at 3 P levels"),
            ("voltage control", "step metrics", "agreed test and band"),
            ("frequency response", "droop, deadband, delay", "event or injected test"),
            ("ramp limit", "minutes over the limit", "agreed counting rule"),
            ("availability", "hours ready / hours required", "service log"),
            ("telemetry", "completeness, latency", "operator's records"),
            ("power quality", "95th percentiles at the POC", "class A, 1 week+")]
    lines = ["acceptance matrix for the plant's services (teaching):",
             "  service              metric                          evidence"]
    for a, b, c in rows:
        lines.append(f"  {a:20s} {b:31s} {c}")
    lines += ["  every claim in the service contract maps to a metric, a",
              "  place, a method and a record; a claim without one is not",
              "  yet a service"]
    emit("e_matrix", lines)


if __name__ == "__main__":
    step()
    droop()
    ramps()
    telemetry()
    location()
    acceptance()
