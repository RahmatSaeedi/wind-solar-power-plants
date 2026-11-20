"""Chapter 50, round s: notice for the network operator's witnessed tests,
the transformer ratio at first energisation, telemetry latency at the SAT,
the battery's round trip at commissioning, a ramp-rate test from 1-second
data, telemetry availability over the compliance week, main and check
meters in the first week, warranty start dates, and the auxiliary restart
after a total loss of supply.

Run from the project root:   python -m companion.ch50.examples_s
Writes companion/ch50/expected/s_*.txt and diagrams/data/ch50-ramp.csv.
Teaching values (A-514 to A-521).
"""
from __future__ import annotations

from datetime import date

import numpy as np

from companion.ch50 import sources as src
from companion.ch50.common import csv, emit
from plantp import pq


# ------------------------------------------------ 1. notice for witnessed tests
WITNESS = [   # test, planned date, notice given on, notice required days
    ("CP-G01 capability", date(2028, 4, 20), date(2028, 4, 1), 15),
    ("CP-G09 frequency", date(2028, 4, 22), date(2028, 4, 12), 15),
    ("CP-G12 intertrip", date(2028, 4, 10), date(2028, 3, 20), 15),
    ("CP-G14 ramp", date(2028, 4, 24), date(2028, 4, 15), 15),
]


def notice() -> list:
    short = [(t, (d - n).days, req) for t, d, n, req in WITNESS if (d - n).days < req]
    lines = ["witnessed tests: notice given to the network operator (teaching 15 days)"]
    lines += [f"  {t:20s} test {d}  notice {n}  {(d - n).days:3d} days"
              + ("  SHORT" if (d - n).days < req else "") for t, d, n, req in WITNESS]
    lines += [f"  {len(short)} tests are planned inside the notice period: the witness",
              "  may not come, and a test without its witness is repeated -",
              "  the test plan is built back from the notice, not forward",
              "  from the day the plant is ready"]
    emit("s_notice", lines)
    return short


# ------------------------------------------------ 2. transformer ratio
def ratio(v_hv: float = 132.6, v_lv: float = 33.42, tap_ratio: float = 132.0 / 33.0,
          tol: float = 0.005) -> dict:
    meas = v_hv / v_lv
    err = meas / tap_ratio - 1
    lines = ["main transformer T1 at first energisation, no load, tap 0",
             f"  HV {v_hv} kV, LV {v_lv} kV: ratio {meas:.4f} against nameplate "
             f"{tap_ratio:.4f}",
             f"  difference {err:+.2%} (teaching tolerance {tol:.1%}) - "
             f"{'ok' if abs(err) <= tol else 'CHECK'}",
             "  the same check as the factory's (ch 43) read from the",
             "  plant's own VTs: a tap left off its position, or a VT",
             "  wired to the wrong ratio, shows here before any load"]
    emit("s_ratio", lines)
    return dict(err=err)


# ------------------------------------------------ 3. telemetry latency
def latency(seed: int = 5001, n: int = 400, limit_s: float = 2.0) -> dict:
    rng = np.random.default_rng(seed)
    lat = 0.35 + rng.gamma(2.0, 0.12, n)
    lat[::97] += 2.1                                 # a periodic gateway stall
    p50, p95, p99 = np.percentile(lat, [50, 95, 99])
    over = float((lat > limit_s).mean())
    lines = [f"telemetry latency at the SAT: {n} changes timed from the POC to the",
             f"  network operator's gateway (REQ-G17 teaching limit {limit_s} s)",
             f"  median {p50:.2f} s, 95th {p95:.2f} s, 99th {p99:.2f} s, max {lat.max():.2f} s",
             f"  over the limit: {over:.1%} of changes",
             "  the median looks excellent; the tail is where a requirement",
             "  is met or missed - and the slow ones come every 97th change:",
             "  a periodic stall in the gateway (ch 35), not random noise"]
    emit("s_latency", lines)
    return dict(p95=p95, p99=p99, over=over)


# ------------------------------------------------ 4. battery round trip
def round_trip(e_in: float = 41.8, e_out: float = 35.4, aux: float = 1.1,
               design: float = 0.86) -> dict:
    rte_dc = e_out / e_in
    rte = e_out / (e_in + aux)
    lines = ["BESS-A commissioning cycle, full charge then full discharge (POC side)",
             f"  energy in {e_in} MWh, out {e_out} MWh, auxiliaries {aux} MWh",
             f"  round trip {rte_dc:.1%} without, {rte:.1%} with auxiliaries; ch 19 design "
             f"{design:.0%}",
             "  the design figure included the auxiliary energy (ch 19); the",
             "  comparison is made on the same basis or the battery looks",
             "  better than it is - the warranty test names the basis"]
    emit("s_rte", lines)
    return dict(rte=rte, rte_dc=rte_dc)


# ------------------------------------------------ 5. ramp-rate test
def ramp(seed: int = 5002, limit: float = 10.0) -> dict:
    rng = np.random.default_rng(seed)
    t = np.arange(0, 1800)                            # 30 minutes of 1-second data
    target = np.clip(20 + (t - 300) / 60 * 9.0, 20, 100)   # 9 MW/min ramp
    p = target + rng.normal(0, 0.25, t.size)
    p[600:630] += np.linspace(0, 12, 30)              # a cloud edge leaving the PV area
    p[630:700] += np.linspace(12, 0, 70)
    per_min = np.convolve(np.diff(p), np.ones(60), "valid")
    csv("ch50-ramp.csv", "t,p", [(int(a), round(b, 2)) for a, b in zip(t[::10], p[::10])])
    worst = float(per_min.max())
    share = pq.ramp_exceedance(p, limit / 60.0 * 60.0)
    lines = [f"ramp-rate test: set point raised at 9 MW/min, limit {limit:.0f} MW/min (REQ-G14)",
             f"  worst one-minute ramp in the record: {worst:.1f} MW/min",
             f"  sliding one-minute windows above the limit: {(per_min > limit).sum()} "
             f"of {per_min.size}",
             "  the controller held 9 MW/min; the excess came from a cloud",
             "  edge leaving the PV area during the ramp - the test is",
             "  repeated or the record cut at the event, as the procedure",
             "  says beforehand, never chosen afterwards"]
    emit("s_ramp", lines)
    return dict(worst=worst, share=share)


# ------------------------------------------------ 6. telemetry availability
def availability(expected: int = 7 * 86400 // 4, gaps_s=(1800, 600, 7200, 300)) -> dict:
    lost = sum(gaps_s) // 4
    a = pq.completeness(expected, expected - lost)
    lines = ["telemetry over the compliance week, a value every 4 s",
             f"  expected {expected:,}, received {expected - lost:,}: {a:.2%}",
             f"  four gaps; the longest {max(gaps_s) / 3600:.1f} h, during a gateway restart",
             f"  against a 99 % teaching target the week "
             f"{'passes' if a >= 0.99 else 'FAILS'}; the two-hour gap alone",
             f"  costs {max(gaps_s) / (7 * 86400):.1%} - the restart procedure keeps a "
             "second path up",
             "  while one gateway restarts (ch 35 failover)"]
    emit("s_avail", lines)
    return dict(a=a)


# ------------------------------------------------ 7. meters in the first week
def meters(days=(412.0, 398.5, 405.2, 421.7, 390.1, 410.6, 415.9),
           check=(412.3, 398.9, 405.5, 422.1, 390.3, 411.0, 416.3)) -> dict:
    d = [(c - m) / m for m, c in zip(days, check)]
    mean = float(np.mean(d))
    lines = ["revenue main and check meters, first week of export (MWh a day)",
             "  day  main     check    difference"]
    lines += [f"  {k + 1:3d}  {m:7.1f}  {c:7.1f}  {x:+9.3%}"
              for k, (m, c, x) in enumerate(zip(days, check, d))]
    lines += [f"  mean difference {mean:+.3%}: both inside their class (ch 48), and",
              "  the check meter reads a little higher every day - the",
              "  trend watch of ch 48 starts from this baseline, recorded",
              "  in the commissioning report"]
    emit("s_meters", lines)
    return dict(mean=mean)


# ------------------------------------------------ 8. warranty start dates
WARRANTY = {   # class: (start in the record, start by the contract)
    "PV modules": ("2027-10-15", "2028-06-01"), "inverters": ("2028-06-01", "2028-06-01"),
    "unit transformers": ("2028-01-10", "2028-06-01"),
    "turbines": ("2028-05-20", "2028-05-20"), "BESS": (None, "2028-06-01"),
}


def warranty() -> list:
    bad = [(k, a, b) for k, (a, b) in WARRANTY.items() if a != b]
    lines = ["warranty start dates in the asset records against the contract",
             "  (teaching: warranties start at taking-over, turbines per their own",
             "  contract)"]
    lines += [f"  {k:18s} record {a or 'none':10s}  contract {b}" for k, a, b in bad]
    for k, a, b in bad:
        if a:
            m = (date.fromisoformat(b) - date.fromisoformat(a)).days / 30.44
            lines.append(f"  {k}: {m:.1f} months of warranty lost on paper")
    lines += ["  started at delivery instead of taking-over: found only at",
              "  the first claim; the record takes the contract's date"]
    emit("s_warranty", lines)
    return bad


# ------------------------------------------------ 9. auxiliary restart
RESTART = [   # step, minutes, needs
    ("diesel starts and closes onto the essential board", 1.5, None),
    ("110 V chargers back; UPS recharging", 2.0, "diesel"),
    ("control-room HVAC restarts (staggered)", 3.0, "chargers"),
    ("SCADA servers and network checked", 6.0, "chargers"),
    ("protection relays healthy, alarms reviewed", 8.0, "SCADA"),
    ("grid back: transfer to the normal supply", 2.0, "protection"),
]


def restart(target_min: float = 30.0) -> dict:
    total = sum(m for _, m, _ in RESTART)
    lines = ["integrated restart of the auxiliaries after a total loss of supply",
             "  step                                               minutes"]
    acc = 0.0
    for s, m, _ in RESTART:
        acc += m
        lines.append(f"  {s:51s} {acc:7.1f}")
    lines += [f"  {total:.1f} min against a {target_min:.0f}-minute teaching target - "
              f"{'pass' if total <= target_min else 'FAIL'}",
              "  the chain only works if the diesel start of lesson E (not",
              "  yet tested) works: the restart test waits for it"]
    emit("s_restart", lines)
    return dict(total=total)


if __name__ == "__main__":
    notice()
    ratio()
    latency()
    round_trip()
    ramp()
    availability()
    meters()
    warranty()
    restart()
