"""Chapter 48, lab D: data and diagram lab - a tag database validated for
ranges, units, alarm order and deadbands; the plant's connection
schedule planned against as built; and the sensor-to-historian path of
one measurement with its delays and the place each attribute is set.

Run from the project root:   python -m companion.ch48.lab_d
Writes companion/ch48/expected/d_*.txt.
Teaching values (A-504); defensive administration only.
"""
from __future__ import annotations

from companion.ch48 import sources as src
from companion.ch48.common import emit
from plantp import hwmfg as hw


# ------------------------------------------------ 1. tag database
def tags() -> list:
    probs = hw.check_tags(src.TAGS, src.UNITS)
    lines = [f"tag database of {len(src.TAGS)} tags (planted faults) checked",
             "  tag          problem"]
    lines += [f"  {t:11s}  {p}" for t, p in probs]
    lines += [f"  {len(probs)} problems in {len({t for t, _ in probs})} tags: an alarm",
              "  pair in the wrong order never raises one of them; a range",
              "  upside down makes every value 'out of range'; a deadband of",
              "  900 kW on a 5.5 MW turbine hides a sixth of its output from",
              "  the historian; km/h on a wind speed breaks every power",
              "  curve of ch 37 - the validator runs on every revision of",
              "  the database, before it is loaded"]
    emit("d_tags", lines)
    return probs


# ------------------------------------------------ 2. plant connections
PLANNED = {
    ("SUB-CORE", "P1"): dict(far="SW-T01", medium="fibre"),
    ("SUB-CORE", "P2"): dict(far="SW-T12", medium="fibre"),
    ("SUB-CORE", "P3"): dict(far="SW-T06", medium="fibre"),
    ("SUB-CORE", "P4"): dict(far="SW-T07", medium="fibre"),
    ("SUB-CORE", "P5"): dict(far="GW-PV1", medium="fibre"),
    ("SUB-CORE", "P6"): dict(far="GW-PV2", medium="fibre"),
    ("SUB-CORE", "P7"): dict(far="BESS-EMS", medium="fibre"),
    ("SUB-CORE", "P8"): dict(far="RTU-1", medium="copper"),
    ("SUB-CORE", "P9"): dict(far="CTRL-SCADA", medium="fibre"),
    ("SUB-CORE", "P10"): dict(far="CLK-1", medium="copper"),
}
ACTUAL = {k: dict(v) for k, v in PLANNED.items()}
ACTUAL[("SUB-CORE", "P3")]["far"] = "SW-T07"
ACTUAL[("SUB-CORE", "P4")]["far"] = "SW-T06"
ACTUAL[("SUB-CORE", "P8")]["medium"] = "fibre"
del ACTUAL[("SUB-CORE", "P10")]
ACTUAL[("SUB-CORE", "P11")] = dict(far="CLK-1", medium="copper")


def connections() -> dict:
    d = hw.diff_ports(PLANNED, ACTUAL)
    lines = ["substation core switch: connection schedule planned against the",
             "  as-built walk-down"]
    lines += [f"  missing: {c}:{p}" for c, p in d["missing"]]
    lines += [f"  extra:   {c}:{p}" for c, p in d["extra"]]
    lines += [f"  changed: {c}:{p} {f} {a} -> {b}" for (c, p), f, a, b in d["changed"]]
    lines += ["  P3 and P4 are crossed: the two ends of the west and east",
              "  rings meet on each other's port - the rings still work, but",
              "  the port labels, the monitoring and the recovery plan all",
              "  point to the wrong ring; the clock moved from P10 to P11 and",
              "  the RTU link became fibre - both fine, both to be written",
              "  into the as-built schedule, or the next technician pulls the",
              "  wrong cable"]
    emit("d_connections", lines)
    return d


# ------------------------------------------------ 3. sensor to historian
PATH = [   # stage, where, delay s (teaching), what it adds or sets
    ("pyranometer", "met station", 5.0, "the physics; response time to 95 %"),
    ("4-20 mA loop", "met cabinet", 0.0, "range, loop check (ch 34)"),
    ("logger input", "met cabinet", 1.0, "scaling to W/m2, sample rate"),
    ("logger to switch", "SW-T05", 0.0, "VLAN 20 (control)"),
    ("gateway poll", "GW-MET", 2.0, "register type, scale, time stamp"),
    ("SCADA server", "control room", 1.0, "quality flag, alarm limits"),
    ("historian", "control room", 0.0, "deadband, compression, retention"),
]


def dataflow() -> dict:
    total = sum(d for _, _, d, _ in PATH)
    lines = ["one irradiance value from the sensor to the historian (teaching)",
             "  stage              where           delay s   sets"]
    for s, w, d, what in PATH:
        lines.append(f"  {s:17s}  {w:14s}  {d:7.1f}   {what}")
    lines += [f"  worst-case delay {total:.0f} s: fine for a 1-minute PR, too slow for",
              "  a 1-second ramp check - the right source for each use is",
              "  chosen from this view; and every attribute (unit, scale,",
              "  time, quality, deadband) is set in exactly one stage, which",
              "  is the stage a wrong value is traced back to (ch 35, ch 37)"]
    emit("d_dataflow", lines)
    return dict(total=total, stages=len(PATH))


if __name__ == "__main__":
    tags()
    connections()
    dataflow()
