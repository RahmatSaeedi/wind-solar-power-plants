"""Chapter 35, lesson B: data and interoperability - a value as a bare
register or as an object with quality and time, a scaling error caught,
quality flags through a gateway, who stamps the time, a counter that
overflows, two devices that 'speak the same protocol' but share less
than needed, and tag names checked against a rule.

Run from the project root:   python -m companion.ch35.examples_b
Writes companion/ch35/expected/b_*.txt.
Synthetic data and teaching values (A-397); nothing connects to a plant.
"""
from __future__ import annotations

import numpy as np

from companion.ch35.common import emit
from plantp import scada as sc


def registers() -> None:
    raw = 1321                                     # int16 register, scale 0.1 kV (teaching)
    good, bad = raw * 0.1, raw * 1.0
    lines = ["the same POC voltage as a bare register and as an object",
             f"  register 40101 = {raw} (the scale 0.1 kV lives only in a manual)",
             f"  read with the right scale: {good:.1f} kV; with scale 1: {bad:.0f} kV",
             f"  scaling check on 0-150 kV flags the second: {sc.scaling_suspect(bad, 0, 150)}",
             "  as an object: value 132.1, unit kV, quality good,",
             "    time 2026-03-14T10:00:00.123Z, clock synchronised",
             "  a register is a number whose meaning sits elsewhere; an",
             "  object carries its unit, quality and time with it - the",
             "  register map is then a controlled document, checked",
             "  value by value in the point-to-point test (lesson C)"]
    emit("b_registers", lines)


def quality_map() -> None:
    src_flags = ["invalid", "questionable", "substituted", "old data", "test"]
    target = {"invalid": "invalid", "questionable": "invalid", "old data": "not topical"}
    lines = ["quality through a gateway: source flags and what survives (teaching)",
             "  source flag      target flag     kept?"]
    lost = []
    for f in src_flags:
        t = target.get(f)
        lines.append(f"  {f:16s} {t or '-':15s} {'yes' if t else 'LOST'}")
        if not t:
            lost.append(f)
    lines += [f"  lost in the gateway: {lost}",
              "  a substituted value (typed in by hand) or a test value",
              "  arrives at the control centre looking measured - the",
              "  mapping table is part of the interface specification",
              "  and each lost flag is either mapped or the value blocked"]
    emit("b_quality", lines)


def stamps(seed: int = 351) -> None:
    rng = np.random.default_rng(seed)
    n = 50_000
    gap = rng.uniform(0, 100, n)                    # ms between two events on two devices
    lat_a = rng.uniform(5, 200, n)                  # ms device -> gateway, each its own
    lat_b = rng.uniform(5, 200, n)
    wrong_gateway = float(np.mean(gap + lat_b < lat_a)) * 100
    lines = ["who stamps the time: the device or the gateway? (synthetic)",
             "  two events up to 100 ms apart on two devices; 5-200 ms to the gateway",
             f"  stamped at the source (synchronised clocks): order wrong 0.0 %",
             f"  stamped by the gateway on arrival:            order wrong {wrong_gateway:.1f} %",
             "  a time stamp added on arrival measures the network, not",
             "  the event; the sequence of events is stamped where it",
             "  happens and the stamp travels unchanged with the value"]
    emit("b_stamps", lines)


def overflow() -> None:
    mwh_day = 295_100 / 365
    days16 = 32_767 / mwh_day
    days32 = 2_147_483_647 / mwh_day
    lines = ["an energy counter in MWh through a 16-bit signed register",
             f"  plant energy {mwh_day:.0f} MWh a day (ch 15)",
             f"  16-bit counter: wraps after {days16:.0f} days",
             f"  32-bit counter: wraps after {days32 / 365:,.0f} years",
             "  a counter that wraps in six weeks looks like a sudden",
             "  loss of energy in every report that does not expect it;",
             "  the data type of each point is chosen from its range over",
             "  the plant's life, not from what the gateway offers"]
    emit("b_overflow", lines)


def profiles() -> None:
    need = {"P", "Q", "U", "f", "P set", "Q set", "status", "alarm", "energy", "time sync"}
    dev_a = {"P", "Q", "U", "f", "P set", "status", "alarm", "energy", "time sync"}
    dev_b = {"P", "Q", "U", "f", "Q set", "status", "energy"}
    both = dev_a & dev_b
    lines = ["two devices that both 'support the same protocol' (teaching)",
             f"  needed by the plant controller: {len(need)} items",
             f"  device A offers {len(dev_a & need)}, device B offers {len(dev_b & need)}",
             f"  missing from A: {sorted(need - dev_a)}",
             f"  missing from B: {sorted(need - dev_b)}",
             f"  common to both: {len(both & need)} of {len(need)}",
             "  a protocol name says how bytes travel, not which data and",
             "  services a device has; interoperability is shown by a",
             "  profile of the needed items, checked against each",
             "  device's declaration and proved in an interface test"]
    emit("b_profiles", lines)


def tag_names() -> None:
    tags = ["PLP-WTG-T01.ActivePower", "PLP-WTG-T01.activepower", "PLP-E1-VT.Voltage",
            "plp-bes-c03.Soc", "PLP-BES-C03.SOC", "PLP-PVI-B01-I1.DcVoltage",
            "PLP-MET-M1-Ghi", "PLP-TRF-T1.OilTemp"]
    lines = ["tag names against the rule PLP-<area>-<item>.<Signal> (teaching)",
             "  tag                             ok?"]
    bad = 0
    for t in tags:
        ok = sc.tag_ok(t)
        bad += not ok
        lines.append(f"  {t:31s} {'yes' if ok else 'NO'}")
    lines += [f"  {bad} of {len(tags)} break the rule",
              "  a tag rule is checked by a program before the first",
              "  point is configured - a tag renamed after commissioning",
              "  breaks every trend, report and link to the asset",
              "  register that used the old name (lesson F)"]
    emit("b_tags", lines)


if __name__ == "__main__":
    registers()
    quality_map()
    stamps()
    overflow()
    profiles()
    tag_names()
