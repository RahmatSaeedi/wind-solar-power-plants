"""Instrumentation, metering, panel and network hardware checks
(chapter 48): a datasheet turned into a site error budget, a tag database
validator, planned against actual port schedules, fibre link records
against their budget, firmware against an approved baseline, clock
offsets across devices and a metering chain's combined error.

Teaching relations. Defensive administration only: these functions read
records the integrator hands over; nothing here probes a network.
"""
from __future__ import annotations

import math


# ------------------------------------------------------------ error budget
# [start: budget]
def error_budget(spec: dict, t_site: float, years: float, reading: float,
                 full_scale: float) -> dict:
    """Combine a datasheet's error terms at site conditions, in units of
    the measurand: accuracy (% of reading and % of full scale), temperature
    coefficient (% of reading per K from the reference temperature),
    drift (% of reading a year) and non-linearity (% of full scale)."""
    terms = {
        "accuracy": reading * spec.get("acc_rdg", 0) / 100
        + full_scale * spec.get("acc_fs", 0) / 100,
        "temperature": reading * spec.get("tc_rdg", 0) / 100
        * abs(t_site - spec.get("t_ref", 20.0)),
        "drift": reading * spec.get("drift_rdg_yr", 0) / 100 * years,
        "linearity": full_scale * spec.get("nl_fs", 0) / 100,
    }
    rss = math.sqrt(sum(v * v for v in terms.values()))
    return dict(terms=terms, rss=rss, worst=sum(terms.values()))
# [end: budget]


# ------------------------------------------------------------ tag database
# [start: tags]
REQUIRED = ["tag", "kind", "unit", "lo", "hi", "alarm_lo", "alarm_hi",
            "deadband"]


def check_tags(rows: list[dict], units: dict[str, set[str]]) -> list:
    """Return (tag, problem): missing fields, duplicates, a unit that does
    not fit the kind, ranges upside down, alarms outside the range or out
    of order, a deadband that is negative or wider than a tenth of the
    span."""
    out, seen = [], set()
    for r in rows:
        t = r.get("tag") or "?"
        miss = [f for f in REQUIRED if r.get(f) in (None, "")]
        out += [(t, f"missing {f}") for f in miss]
        if t in seen:
            out.append((t, "duplicate tag"))
        seen.add(t)
        if miss:
            continue
        if r["unit"] not in units.get(r["kind"], set()):
            out.append((t, f"unit {r['unit']} does not fit {r['kind']}"))
        if not r["lo"] < r["hi"]:
            out.append((t, "range low >= high"))
        elif not r["lo"] <= r["alarm_lo"] < r["alarm_hi"] <= r["hi"]:
            out.append((t, "alarms outside the range or out of order"))
        span = r["hi"] - r["lo"]
        if r["deadband"] < 0 or (span > 0 and r["deadband"] > span / 10):
            out.append((t, f"deadband {r['deadband']} for a span of {span}"))
    return out
# [end: tags]


# ------------------------------------------------------------ port schedules
# [start: ports]
def diff_ports(planned: dict, actual: dict) -> dict:
    """planned/actual: (device, port) -> dict(far=..., vlan=..., speed=...).
    Return missing, extra and changed connections."""
    missing = sorted(set(planned) - set(actual))
    extra = sorted(set(actual) - set(planned))
    changed = []
    for k in sorted(set(planned) & set(actual)):
        for f in planned[k]:
            if planned[k][f] != actual[k].get(f):
                changed.append((k, f, planned[k][f], actual[k].get(f)))
    return dict(missing=missing, extra=extra, changed=changed)
# [end: ports]


# ------------------------------------------------------------ fibre records
def link_check(expected_db: float, budget_db: float, measured_db: float,
               dirty_margin: float = 0.75) -> str:
    """Verdict on a measured link loss: 'fail' over the budget, 'suspect'
    when well above the loss expected from its length and connectors."""
    if measured_db > budget_db:
        return "fail"
    if measured_db > expected_db + dirty_margin:
        return "suspect"
    return "ok"


# ------------------------------------------------------------ firmware
def firmware_check(inventory: dict[str, tuple[str, str]],
                   baseline: dict[str, str]) -> list:
    """inventory: device -> (model, version); baseline: model -> approved.
    Return (device, finding)."""
    out = []
    for dev, (model, ver) in sorted(inventory.items()):
        ok = baseline.get(model)
        if ok is None:
            out.append((dev, f"model {model} not in the baseline"))
        elif ver != ok:
            out.append((dev, f"{ver} (approved {ok})"))
    return out


# ------------------------------------------------------------ clocks
def offsets(readings_ms: dict[str, float], limit_ms: float) -> dict:
    """Offsets of each device's clock from the reference, and the devices
    beyond the limit."""
    return dict(worst=max(abs(v) for v in readings_ms.values()),
                beyond=sorted(d for d, v in readings_ms.items() if abs(v) > limit_ms))


# ------------------------------------------------------------ metering chain
def chain_error(ct_pct: float, vt_pct: float, meter_pct: float) -> tuple[float, float]:
    """Combined ratio error of a metering chain (teaching): RSS and the
    arithmetic worst case of the three class errors, in %."""
    terms = (ct_pct, vt_pct, meter_pct)
    return math.sqrt(sum(t * t for t in terms)), sum(terms)
