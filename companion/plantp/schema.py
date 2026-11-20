"""A small, readable schema checker for configuration and records, chapter 5.

A schema is a dictionary that mirrors the data:

    schema = {"scenario": {"type": str, "enum": ["S0", "S1"]},
              "pv": {"type": dict,
                     "fields": {"dc_mwp": {"type": float, "min": 0}}}}
    problems = check(config, schema)          # [] when the data conform

Keys of each rule: type (str, int, float, bool, dict, list), required
(default True), min, max, enum, unit (documentation only), pattern (regular
expression for text), fields (rules of a nested dict), items (rule for every
list element). Integers are accepted where floats are expected; booleans are
never accepted as numbers. The idea is that of JSON Schema, kept small
enough to read in one sitting.
"""
from __future__ import annotations

import re


def _type_ok(value, kind) -> bool:
    if isinstance(value, bool):
        return kind is bool
    if kind is float:
        return isinstance(value, (int, float))
    return isinstance(value, kind)


# [start: check]
def check(data, schema: dict, path: str = "") -> list[str]:
    """Every problem of `data` against `schema`, one text per problem."""
    if not isinstance(data, dict):
        name = type(data).__name__
        return [f"{path or 'top level'}: expected a mapping, got {name}"]
    problems: list[str] = []
    for key in data:
        if key not in schema:
            problems.append(f"{path}{key}: not in the schema (typing error?)")
    for key, rule in schema.items():
        where = f"{path}{key}"
        if key not in data:
            if rule.get("required", True):
                problems.append(f"{where}: missing")
            continue
        problems += _check_value(data[key], rule, where)
    return problems


def _check_value(value, rule: dict, where: str) -> list[str]:
    kind = rule.get("type")
    if kind is not None and not _type_ok(value, kind):
        got = type(value).__name__
        return [f"{where}: expected {kind.__name__}, got {got} {value!r}"]
    out = []
    unit = f" {rule['unit']}" if rule.get("unit") else ""
    if "min" in rule and value < rule["min"]:
        out.append(f"{where}: {value}{unit} below minimum {rule['min']}{unit}")
    if "max" in rule and value > rule["max"]:
        out.append(f"{where}: {value}{unit} above maximum {rule['max']}{unit}")
    if "enum" in rule and value not in rule["enum"]:
        out.append(f"{where}: {value!r} not one of {rule['enum']}")
    if "pattern" in rule and not re.fullmatch(rule["pattern"], str(value)):
        out.append(f"{where}: {value!r} does not match {rule['pattern']}")
    if kind is dict and "fields" in rule:
        out += check(value, rule["fields"], where + ".")
    if kind is list and "items" in rule:
        for i, item in enumerate(value):
            out += _check_value(item, rule["items"], f"{where}[{i}]")
    return out
# [end: check]


# [start: run_schema]
RUN_SCHEMA = {
    "run_id": {"type": str, "pattern": r"[A-Z0-9-]+"},
    "data_release": {"type": str, "pattern": r"\d+\.\d+\.\d+"},
    "scenario": {"type": str, "enum": ["S0", "S1"]},
    "pv": {"type": dict, "fields": {
        "dc_mwp": {"type": float, "min": 0, "max": 1000, "unit": "MWp"},
        "ac_mw": {"type": float, "min": 0, "max": 1000, "unit": "MW"},
        "noct_c": {"type": float, "min": 35, "max": 55, "unit": "degC"},
        "gamma_per_k": {"type": float, "min": -0.01, "max": 0,
                        "unit": "1/K"},
        "k_other": {"type": float, "min": 0.5, "max": 1.0},
        "eta_inverter": {"type": float, "min": 0.8, "max": 1.0}}},
    "wind": {"type": dict, "fields": {
        "turbines": {"type": int, "min": 0, "max": 500},
        "loss": {"type": float, "min": 0, "max": 0.5},
        "density_correction": {"type": bool}}},
    "export_limit_mw": {"type": float, "min": 0, "unit": "MW"},
    "bess": {"type": dict, "required": False, "fields": {
        "power_mw": {"type": float, "min": 0, "unit": "MW"},
        "usable_mwh": {"type": float, "min": 0, "unit": "MWh"},
        "roundtrip": {"type": float, "min": 0.5, "max": 1.0}}},
    "outputs": {"type": dict, "fields": {"folder": {"type": str}}},
}
# [end: run_schema]
