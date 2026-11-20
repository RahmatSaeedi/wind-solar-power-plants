"""Commissioning, grid acceptance and handover helpers (chapter 50).

Expected PV string values at the measured conditions, string and
insulation records read against their limits, relay test results against
the setting, cause-and-effect test coverage, handover data checked against
a schema, and acceptance results traced to their requirements. Pure
functions on plain data; teaching models, not test procedures.
"""
from __future__ import annotations

import math

from plantp import pvcell, protection


# [start: strings]
def string_expected(n_modules: int, g_wm2: float, t_cell_c: float,
                    ds: pvcell.Datasheet = pvcell.PVM_550_DS
                    ) -> tuple[float, float]:
    """Open-circuit voltage and short-circuit current of a string of
    n_modules at irradiance g_wm2 and cell temperature t_cell_c."""
    m = pvcell.at_conditions(pvcell.fit(ds), g_wm2, t_cell_c, ds.alpha_isc)
    return n_modules * m.voc, m.isc


def string_check(voc: float, isc: float, voc_exp: float,
                 isc_exp: float, n_modules: int, tol_v: float = 0.03,
                 tol_i: float = 0.05) -> str:
    """Verdict on one string's open-circuit voltage and short-circuit
    current against the expected values: reversed polarity, a module short
    (or bypassed), low voltage, low current, or ok."""
    if voc < 0:
        return "reversed polarity"
    short = (voc_exp - voc) / (voc_exp / n_modules)
    if abs(voc - voc_exp) > tol_v * voc_exp:
        if 0.5 < short < 3.5:
            return f"about {short:.0f} module(s) short"
        return "voltage off"
    if isc < (1 - tol_i) * isc_exp:
        return "low current"
    return "ok"
# [end: strings]


def below(values: dict, limit: float) -> list:
    """Ids whose value is missing (None) or below limit."""
    return [k for k, v in values.items() if v is None or v < limit]


# [start: relays]
def relay_check(results, tol_share: float = 0.05, tol_s: float = 0.04,
                curve: str = "standard inverse") -> list:
    """results: (relay, test current A, pickup A, TMS, measured s). The
    expected time comes from the inverse curve; a result is out if it
    differs by more than tol_share of the expected time plus tol_s."""
    bad = []
    for name, i, pickup, tms, t_meas in results:
        t_exp = protection.trip_time(i, pickup, tms, curve)
        if t_meas is None or abs(t_meas - t_exp) > tol_share * t_exp + tol_s:
            bad.append((name, t_exp, t_meas))
    return bad
# [end: relays]


# [start: cande]
def cause_effect(matrix: dict, tested: set) -> tuple[float, list]:
    """matrix: cause -> set of effects it must produce; tested: set of
    (cause, effect) pairs proven in a test. Returns the share proven and
    the pairs never proven."""
    pairs = [(c, e) for c, effects in matrix.items() for e in sorted(effects)]
    missing = [p for p in pairs if p not in tested]
    return 1 - len(missing) / len(pairs), missing
# [end: cande]


# [start: schema]
def validate(rows: list[dict], required, key: str, refs: dict) -> dict:
    """Handover data checks: rows missing a required field, duplicate keys,
    and references that point nowhere (refs: field -> set of valid
    values). Returns lists of (row key, problem)."""
    out = {"missing": [], "duplicate": [], "dangling": []}
    seen = set()
    for r in rows:
        k = r.get(key)
        for f in required:
            if r.get(f) in (None, ""):
                out["missing"].append((k, f))
        if k in seen:
            out["duplicate"].append((k, key))
        seen.add(k)
        for f, valid in refs.items():
            if r.get(f) not in (None, "") and r[f] not in valid:
                out["dangling"].append((k, f))
    return out
# [end: schema]


def autonomy_ok(minutes_measured: float, minutes_required: float) -> bool:
    return minutes_measured >= minutes_required


def trace(requirements: dict, tests: dict) -> dict:
    """requirements: id -> text; tests: id -> (procedure, result or None).
    Returns ids with no test, with a test but no result, and failed."""
    none = [r for r in requirements if r not in tests]
    open_ = [r for r, (_, res) in tests.items() if r in requirements and res is None]
    failed = [r for r, (_, res) in tests.items() if res == "fail"]
    return dict(untested=none, open=open_, failed=failed)


def ceil_div(a: float, b: float) -> int:
    return int(math.ceil(a / b))
