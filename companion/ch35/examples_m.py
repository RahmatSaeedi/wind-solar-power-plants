"""Chapter 35, deeper lessons: one measurement traced from the sensor to
the operator's screen, a flat network against subnets, a signal turned
into data by a deadband, a day's trend drawn on a screen, a daily report
from a historian with gaps, and the allowed paths of the logical diagram.

Run from the project root:   python -m companion.ch35.examples_m
Writes companion/ch35/expected/m_*.txt and diagrams/data/ch35-*.csv.
Synthetic data and teaching values (A-393 to A-397).
"""
from __future__ import annotations

import numpy as np

from companion.ch35.common import csv, emit

HOPS = [  # hop, worst-case delay ms, what it adds (teaching)
    ("CT/VT and transducer (ch 34)", 100.0, "filter of the measurement"),
    ("protection/measuring IED", 20.0, "sample, compute; TIME STAMP"),
    ("ring and substation switches", 0.1, "store and forward"),
    ("gateway / RTU", 50.0, "sends changes; new protocol"),
    ("SCADA server scan", 1000.0, "waits for the next 1 s scan"),
    ("operator screen refresh", 1000.0, "waits for the next refresh")]


def trace() -> None:
    total = sum(d for _, d, _ in HOPS)
    lines = ["POC active power traced from the sensor to the operator's screen",
             "  hop                              worst ms   adds"]
    for hop, d, adds in HOPS:
        lines.append(f"  {hop:32s} {d:8.1f}   {adds}")
    lines += [f"  worst-case age on the screen: {total / 1000:.2f} s; typical about"
              f" {(sum(d for _, d, _ in HOPS[:4]) + 1000) / 1000:.1f} s",
              "  the value keeps the time stamp of the IED and the quality",
              "  it had there through every hop; the screen shows its age,",
              "  and the controller of ch 34 never takes this path - it",
              "  reads the transducer directly"]
    emit("m_trace", lines)


def flat_vs_subnets() -> None:
    zones = [30, 24, 40, 24, 12]                 # devices per subnet (lesson A)
    rate, size = 0.5, 100                        # broadcasts a device a second, bytes
    n = sum(zones)
    flat = (n - 1) * rate
    worst = (max(zones) - 1) * rate
    lines = ["broadcasts each device must read: one flat network or subnets",
             f"  {n} devices, each sending {rate} broadcasts a second of"
             f" {size} bytes (teaching)",
             f"  flat network: every device reads {flat:.1f} a second",
             f"  five subnets: at most {worst:.1f} a second (largest subnet"
             f" {max(zones)})",
             "  a switch forwards frames inside its subnet by hardware",
             "  address; a router or firewall joins subnets and decides",
             "  what may cross. A storm or a misbehaving device then",
             "  stays inside one function, and the zone rules of ch 36",
             "  have a place to stand"]
    emit("m_subnets", lines)


def signal_to_data(seed: int = 354) -> None:
    rng = np.random.default_rng(seed)
    t = np.arange(3600)
    temp = 70.0 + 5.0 * np.sin(2 * np.pi * t / 3600) + rng.normal(0, 0.15, t.size)
    span = 140.0                                  # -20 .. 120 C (ch 34 range)
    lines = ["a 4-20 mA oil temperature turned into data (synthetic hour)",
             "  the loop carries one value all the time; as data it is",
             "  sampled each second and sent when it moves by a deadband",
             "  deadband % span   reports an hour   largest error K"]
    rows = []
    for db in (0.0, 0.1, 0.5, 1.0, 2.0):
        sent, last, err = 0, None, 0.0
        for v in temp:
            if last is None or abs(v - last) > db / 100 * span:
                sent, last = sent + 1, v
            err = max(err, abs(v - last))
        rows.append((db, sent, round(err, 2)))
        lines.append(f"  {db:15.1f}   {sent:15d}   {err:16.2f}")
    csv("ch35-deadband.csv", "db,reports,err", rows)
    lines += ["  a deadband trades messages for error: below the noise it",
              "  sends about half the samples, above the accuracy of the",
              "  instrument it throws away information; it is set from",
              "  the instrument's uncertainty (ch 34) and written in the",
              "  point list, never left at a gateway's default"]
    emit("m_deadband", lines)


def trend_on_screen(seed: int = 355) -> None:
    rng = np.random.default_rng(seed)
    n, px = 86_400, 800                          # one day at 1 s on 800 pixels
    per = n // px
    trials, hit_dec, hit_mm = 2000, 0, 0
    for _ in range(trials):
        start = int(rng.integers(0, n - 5))
        dec = np.arange(0, n, per)               # every per-th sample
        hit_dec += np.any((dec >= start) & (dec < start + 5))
        hit_mm += 1                              # min/max per pixel always keeps it
    lines = ["a day of 1 s data on an 800-pixel trend (synthetic spikes of 5 s)",
             f"  {per} samples per pixel",
             f"  every {per}th sample drawn: spike visible in"
             f" {hit_dec / trials * 100:.1f} % of cases",
             f"  min and max of each pixel drawn: visible in"
             f" {hit_mm / trials * 100:.0f} % of cases",
             "  a trend that decimates hides the short events an operator",
             "  most needs to see; the historian serves min/max (or every",
             "  point) for the screen's resolution, and the trend says",
             "  which it shows"]
    emit("m_trend", lines)


def report_with_gaps(seed: int = 356) -> None:
    rng = np.random.default_rng(seed)
    m = np.arange(1440)                           # minutes of a partly cloudy day
    p = np.clip(np.sin(np.pi * (m - 360) / 780), 0, None) * 95.0   # MW, 6:00-19:00
    for start in rng.integers(420, 1080, 14):     # clouds of 5-20 min take 60 %
        p[start:start + int(rng.integers(5, 21))] *= 0.4
    p[695:712] *= 0.4                             # one of them at midday
    true = p.sum() / 60
    random_gap = p.copy()
    lost = rng.choice(1440, size=29, replace=False)   # 2 % of minutes
    random_gap[lost] = np.nan
    block = p.copy()
    block[690:720] = np.nan                            # 30 min at midday

    def filled(x):
        ok = ~np.isnan(x)
        return np.interp(m, m[ok], x[ok]).sum() / 60

    def skipped(x):
        return np.nansum(x) / 60
    over = filled(block) - true
    lines = ["daily energy of a partly cloudy day from a historian with gaps",
             "  (synthetic minutes)",
             f"  true energy {true:,.1f} MWh",
             "  gap                         skipped MWh   interpolated MWh",
             f"  2 % of minutes at random    {skipped(random_gap):11.1f}"
             f"   {filled(random_gap):16.1f}",
             f"  30 minutes at midday        {skipped(block):11.1f}"
             f"   {filled(block):16.1f}",
             "  skipping a gap understates energy by the share missing;",
             "  interpolating repairs short random gaps almost exactly",
             f"  but draws a straight line across the cloud hidden in the",
             f"  long gap and overstates by {over:.1f} MWh - a report states its",
             "  data completeness and how each gap was filled, and",
             "  settlement uses the meter, not the historian (ch 37)"]
    emit("m_report", lines)


FLOWS = [  # from zone, to zone, allowed (teaching logical diagram)
    ("substation IEDs", "SCADA servers", "yes: telecontrol"),
    ("turbines", "SCADA servers", "yes: turbine data"),
    ("PV inverters", "SCADA servers", "yes: inverter data"),
    ("battery containers", "SCADA servers", "yes: battery data"),
    ("SCADA servers", "historian", "yes: one way"),
    ("historian", "business network", "yes: read copy only"),
    ("business network", "SCADA servers", "NO"),
    ("turbines", "PV inverters", "NO (no need)"),
    ("grid operator", "gateway / RTU", "yes: agreed profile")]


def logical() -> None:
    lines = ["the logical diagram as a table of allowed paths (teaching)",
             "  from                  to                    allowed"]
    for a, b, ok in FLOWS:
        lines.append(f"  {a:21s} {b:21s} {ok}")
    yes = sum(ok.startswith("yes") for _, _, ok in FLOWS)
    lines += [f"  {yes} of {len(FLOWS)} listed paths allowed; every path not",
              "  listed is denied. The physical diagram says where cables",
              "  run; the logical one says who may talk to whom - and it",
              "  is the logical one the firewall rules of ch 36 implement"]
    emit("m_logical", lines)


if __name__ == "__main__":
    trace()
    flat_vs_subnets()
    signal_to_data()
    trend_on_screen()
    report_with_gaps()
    logical()
