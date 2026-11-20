"""Chapter 48, round v: a plane-of-array sensor mounted off the module
plane, the time source's antenna cable budget, firmware files checked
against the maker's published hashes, two configuration files compared
line by line, and historian data recorded in the wrong unit corrected
with an audit trail.

Run from the project root:   python -m companion.ch48.examples_v
Writes companion/ch48/expected/v_*.txt.
Teaching values (A-498 to A-505); defensive administration only.
"""
from __future__ import annotations

import difflib
import hashlib
import math
from datetime import date

from companion.ch48.common import emit


# ------------------------------------------------ 1. sensor alignment
def alignment(tilt_err_deg: float = 2.0) -> dict:
    lines = [f"plane-of-array sensor mounted {tilt_err_deg:.0f} deg off the module plane:",
             "  error in the direct beam by angle of incidence (teaching)",
             "  incidence deg   error %"]
    out = {}
    for th in (10, 30, 50, 70):
        t = math.radians(th)
        e = math.radians(tilt_err_deg)
        err = math.cos(t - e) / math.cos(t) - 1
        out[th] = err
        lines.append(f"  {th:13d}   {err * 100:+7.1f}")
    lines += ["  near noon the error is small; in the morning and evening,",
              "  at large angles, it grows to several per cent - a sensor",
              "  is levelled to the module plane with a recorded",
              "  inclinometer reading, and checked again after the first storm"]
    emit("v_alignment", lines)
    return out


# ------------------------------------------------ 2. time-source antenna budget
def antenna(length_m: float = 35.0, loss_db_m: float = 0.55, gain_db: float = 30.0,
            need_db: float = 10.0, low_loss_db_m: float = 0.25) -> dict:
    loss = length_m * loss_db_m
    left = gain_db - loss
    loss2 = length_m * low_loss_db_m
    lines = ["satellite clock antenna on the control-building roof,",
             f"  {length_m:.0f} m of cable to the receiver",
             f"  antenna amplifier {gain_db:.0f} dB; receiver needs at least "
             f"{need_db:.0f} dB of it left",
             f"  standard cable {loss_db_m} dB/m: {loss:.1f} dB lost, {left:.1f} dB left "
             f"- {'ok' if left >= need_db else 'TOO LITTLE'}",
             f"  low-loss cable {low_loss_db_m} dB/m: {loss2:.1f} dB lost, "
             f"{gain_db - loss2:.1f} dB left",
             f"  the standard cable leaves {left - need_db:.1f} dB of margin: one more",
             "  connector, a surge protector's own loss or an aged cable and",
             "  the clock loses lock - the cable is chosen from the budget,",
             "  and the antenna's surge protector (lesson A) is in the sum"]
    emit("v_antenna", lines)
    return dict(left=left, left2=gain_db - loss2)


# ------------------------------------------------ 3. firmware file hashes
FILES = {"RS-8_6.2.1.bin": b"switch firmware 6.2.1 build 4410",
         "GW-2_2.3.0.bin": b"gateway firmware 2.3.0 build 118",
         "RTU-X_8.4.bin": b"rtu firmware 8.4 build 77 (repacked)"}
PUBLISHED = {"RS-8_6.2.1.bin": hashlib.sha256(b"switch firmware 6.2.1 build 4410").hexdigest(),
             "GW-2_2.3.0.bin": hashlib.sha256(b"gateway firmware 2.3.0 build 118").hexdigest(),
             "RTU-X_8.4.bin": hashlib.sha256(b"rtu firmware 8.4 build 77").hexdigest()}


def hashes() -> list:
    bad = []
    lines = ["firmware files checked against the hashes the makers publish"]
    for f, data in FILES.items():
        h = hashlib.sha256(data).hexdigest()
        ok = h == PUBLISHED[f]
        if not ok:
            bad.append(f)
        lines.append(f"  {f:16s} {h[:16]}...  {'matches' if ok else 'DIFFERS'}")
    lines += [f"  {', '.join(bad)} is not the file the maker released - re-packed",
              "  somewhere on its way: it is not loaded, and the copy is",
              "  fetched again from the maker's own channel; the hash is",
              "  part of the firmware baseline record (lesson C, ch 36)"]
    emit("v_hashes", lines)
    return bad


# ------------------------------------------------ 4. configuration diff
OLD = """hostname SW-T05
interface 1 vlan 10
interface 2 vlan 10
interface 3 vlan 20
interface 4 vlan 30
interface 8 shutdown
ntp server CLK-1
ntp server CLK-2""".splitlines()
NEW = """hostname SW-T05
interface 1 vlan 10
interface 2 vlan 10
interface 3 vlan 20
interface 4 vlan 20
interface 8 vlan 1
ntp server CLK-1
ntp server CLK-2""".splitlines()


def config_diff() -> list:
    d = [l for l in difflib.unified_diff(OLD, NEW, "backup 2027-03-02", "running",
                                         lineterm="", n=0)
         if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    lines = ["SW-T05: the running configuration against its last backup"]
    lines += [f"  {l}" for l in d]
    lines += ["  two changes nobody recorded: port 4 moved the CMS into the",
              "  control VLAN and port 8 was opened in the default VLAN - the",
              "  very findings of lesson B, here seen in the files themselves;",
              "  a diff is the shortest record of what changed"]
    emit("v_diff", lines)
    return d


# ------------------------------------------------ 5. historian data in a wrong unit
def correction(since: date = date(2027, 2, 1), fixed: date = date(2027, 6, 1),
               factor: float = 3.6) -> dict:
    days = (fixed - since).days
    lines = [f"T05.WS was stored as km/h-labelled values read from an m/s register",
             f"  from {since} to {fixed}: {days} days of wind speed wrong in label",
             f"  the values are m/s; a report that converted 'km/h' to m/s divided "
             f"by {factor}",
             "  the correction: relabel the stored values for that period,",
             "  keep the original rows, record who, when and why, and rerun",
             "  the reports that used them (the power curve of ch 37) - data",
             "  are corrected with an audit trail, never silently"]
    emit("v_correction", lines)
    return dict(days=days)


if __name__ == "__main__":
    alignment()
    antenna()
    hashes()
    config_diff()
    correction()
