"""SCADA and communications, chapter 35: link and network arithmetic
(serialisation delay, utilisation, polling cycle, report-by-exception
load), availability of star and ring topologies, a fibre loss budget, a
time-synchronisation error budget, tag-name and scaling checks, a
staleness detector, a benign alarm rule engine and retention sizing.

Teaching tools working on synthetic data only; checked by hand in
tests/test_ch35_scada.py.
"""
from __future__ import annotations

import math
import re

# [start: link]
def serialisation_ms(bytes_: int, bit_rate: float) -> float:
    """Time to put one message of bytes_ on a link of bit_rate bit/s (ms)."""
    return bytes_ * 8 / bit_rate * 1000


def utilisation(msgs_per_s: float, bytes_: int, bit_rate: float) -> float:
    """Share of a link's capacity a steady message stream uses."""
    return msgs_per_s * bytes_ * 8 / bit_rate


def polling_cycle_s(devices: int, request_b: int, reply_b: int,
                    bit_rate: float, turnaround_ms: float) -> float:
    """Time to poll every device once on a shared serial line."""
    per = (serialisation_ms(request_b, bit_rate)
           + serialisation_ms(reply_b, bit_rate) + turnaround_ms)
    return devices * per / 1000
# [end: link]


def rbe_rate(points: int, changes_per_hour: float) -> float:
    """Messages a second when each point reports only on change."""
    return points * changes_per_hour / 3600


# [start: topology]
def star_availability(a_link: float, a_switch: float, n: int) -> float:
    """Availability that all n devices on a star reach the core switch."""
    return a_switch * a_link ** n


def ring_device_availability(a_link: float, n: int) -> float:
    """Availability that one device on a ring of n+1 links reaches the
    head: either way round must be whole (independent link failures)."""
    k = n + 1
    # device at the far point: two paths of about k/2 links each
    half = k // 2
    p1, p2 = a_link ** half, a_link ** (k - half)
    return 1 - (1 - p1) * (1 - p2)
# [end: topology]


def fibre_budget_db(length_km: float, splices: int, connectors: int,
                    att_db_km: float = 0.35, splice_db: float = 0.1,
                    conn_db: float = 0.5, margin_db: float = 3.0) -> float:
    """Loss of a fibre link including a repair margin (dB)."""
    return (length_km * att_db_km + splices * splice_db + connectors * conn_db
            + margin_db)


def sync_budget_us(parts: list[float]) -> float:
    """Worst-case sum of time-synchronisation error contributions (us)."""
    return sum(abs(p) for p in parts)


# [start: tags]
TAG = re.compile(r"^PLP-[A-Z0-9]+(-[A-Z0-9]+)*\.[A-Z][A-Za-z0-9]*$")


def tag_ok(tag: str) -> bool:
    """Tag rule (teaching): PLP-<area>-<item>.<Signal>, upper case before
    the dot, a signal name starting with a capital after it."""
    return bool(TAG.match(tag))


def scaling_suspect(value: float, lo: float, hi: float,
                    factor_hint: float = 10.0) -> bool:
    """True when a value sits outside its range but would fit if divided
    or multiplied by a power of the hint (a likely scaling error)."""
    if lo <= value <= hi:
        return False
    for k in (1, 2, 3):
        for v in (value / factor_hint ** k, value * factor_hint ** k):
            if lo <= v <= hi:
                return True
    return False
# [end: tags]


def stale(times_s: list[float], now_s: float, max_age_s: float) -> bool:
    """A value is stale when its last update is older than max_age_s."""
    return not times_s or now_s - max(times_s) > max_age_s


# [start: alarm]
def alarm_states(values, high: float, deadband: float, delay_n: int):
    """Benign high-alarm rule on a series: raise after delay_n samples
    above high, clear only below high - deadband (no chattering)."""
    out, active, count = [], False, 0
    for v in values:
        if not active:
            count = count + 1 if v > high else 0
            if count >= delay_n:
                active, count = True, 0
        elif v < high - deadband:
            active = False
        out.append(active)
    return out
# [end: alarm]


def retention_gb(points: int, period_s: float, years: float,
                 bytes_per: int = 12, keep: float = 1.0) -> float:
    """Storage for points sampled every period_s kept for years (GB)."""
    return points * (years * 365 * 86400 / period_s) * bytes_per * keep / 1e9


def transitions(states) -> int:
    """Number of times a boolean series switches on."""
    n, prev = 0, False
    for s in states:
        if s and not prev:
            n += 1
        prev = s
    return n


def nines(a: float) -> float:
    """'Number of nines' of an availability (0.999 -> 3)."""
    return -math.log10(1 - a)
