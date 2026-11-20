"""Chapter 48, lesson C: configuration and test - firmware against the
approved baseline, configuration backups against the last changes, clock
offsets read at the SAT, the protocol register map against the tag
database, and the redundancy tests against what they had to prove.

Run from the project root:   python -m companion.ch48.examples_c
Writes companion/ch48/expected/c_*.txt.
Teaching values (A-503 to A-505); defensive administration only.
"""
from __future__ import annotations

from companion.ch48 import sources as src
from companion.ch48.common import emit
from plantp import hwmfg as hw


# ------------------------------------------------ 1. firmware baseline
def firmware() -> list:
    f = hw.firmware_check(src.FIRMWARE, src.BASELINE)
    lines = [f"firmware of {len(src.FIRMWARE)} network and control devices against "
             "the approved baseline"]
    lines += [f"  {d}: {x}" for d, x in f]
    lines += ["  SW-T09 runs an older release than the other turbine switches - the",
              "  one switch the integrator replaced at site from its own",
              "  stock; SW-SPARE is a model nobody approved: a spare that",
              "  differs from the installed fleet is not a spare, it is a",
              "  change (ch 36 inventory, ch 44 configuration)"]
    emit("c_firmware", lines)
    return f


# ------------------------------------------------ 2. configuration backups
def backups() -> list:
    stale = [(d, ch, bk) for d, (ch, bk) in src.BACKUPS.items() if bk < ch]
    lines = ["configuration backups against the last configuration change",
             "  device    last change   last backup   status"]
    for d, (ch, bk) in src.BACKUPS.items():
        lines.append(f"  {d:8s}  {ch}    {bk}    "
                     f"{'STALE' if bk < ch else 'ok'}")
    lines += [f"  stale: {', '.join(d for d, *_ in stale)} - a restore from these",
              "  backups would bring back the configuration of February or",
              "  March: the RTU's point map would lose the changes of May;",
              "  a backup is taken after every change and its fingerprint",
              "  compared with the running configuration (ch 36 recovery)"]
    emit("c_backups", lines)
    return stale


# ------------------------------------------------ 3. clock offsets
def clocks(limit_ms: float = 2.0) -> dict:
    o = hw.offsets(src.CLOCKS, limit_ms)
    lines = [f"clock offsets read at the SAT against the plant clock (limit "
             f"{limit_ms:.0f} ms)"]
    for d, v in src.CLOCKS.items():
        lines.append(f"  {d:9s}  {v:+6.1f} ms  {'BEYOND' if abs(v) > limit_ms else 'ok'}")
    lines += [f"  beyond: {', '.join(o['beyond'])} - the PV gateway still takes its",
              "  time from its own clock, not the plant's time source: its",
              "  events land 15 ms late in every sequence-of-events list, and",
              "  a trip would be read in the wrong order (ch 35 time stamps)"]
    emit("c_clocks", lines)
    return o


# ------------------------------------------------ 4. register map against tags
def regmap() -> list:
    tags = {t["tag"]: t for t in src.TAGS}
    out = []
    for tag, (rt, scale, unit) in src.REGMAP.items():
        t = tags.get(tag)
        if t is None:
            out.append((tag, "in the register map, not in the tag database"))
            continue
        if unit not in (t["unit"], "%" if t["unit"] == "-" else t["unit"]):
            out.append((tag, f"device unit {unit}, tag unit {t['unit']}"))
        if rt == "int16":
            top = 32767 * scale
            if isinstance(t["hi"], (int, float)) and t["hi"] > top:
                out.append((tag, f"int16 x {scale} tops at {top:g}, tag range to "
                                 f"{t['hi']}"))
    lines = ["protocol register map read against the tag database"]
    lines += [f"  {t}: {p}" for t, p in out]
    lines += [f"  {len(out)} findings: a reactive-power register labelled MW in the",
              "  tag database; a wind speed in km/h at the tag but m/s at the",
              "  device; a PV feeder in int16 thousandths of a MW that cannot",
              "  show more than 32.8 MW - fine for 25 MW, but the scale is",
              "  recorded with the tag so the next change sees it (ch 35 int16)"]
    emit("c_regmap", lines)
    return out


# ------------------------------------------------ 5. failover tests
def failover() -> dict:
    lines = ["redundancy tests at the SAT: what each had to prove and what it did",
             "  test                         expected s   measured s   verdict"]
    bad, missing = [], []
    for t, exp, meas in src.FAILOVER:
        if meas is None:
            missing.append(t)
            v = "NOT DONE"
        elif meas > exp:
            bad.append(t)
            v = "FAIL"
        else:
            v = "ok"
        m = f"{'-':>10s}" if meas is None else f"{meas:10.2f}"
        lines.append(f"  {t:28s} {exp:10.2f}   {m}   {v}")
    lines += [f"  failed: {', '.join(bad)}; not done: {', '.join(missing)}",
              "  the RTU's standby CPU takes 9.5 s to take over against 5 s:",
              "  the grid operator's telemetry would freeze for that long;",
              "  the time-source test was never run - the one failure that",
              "  silently spoils every record after it (ch 35 holdover)"]
    emit("c_failover", lines)
    return dict(bad=bad, missing=missing)


if __name__ == "__main__":
    firmware()
    backups()
    clocks()
    regmap()
    failover()
