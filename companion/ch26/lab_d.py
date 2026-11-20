"""Chapter 26, lab D - the evidence and safety exercise (worked example):
a hypothetical earth fault and a phase fault on cable =WS1-W3 traced from
the network data, through the coordination report, the relay logic, the
panel wiring and the test evidence, to the approval of the settings;
plus the setting-file configuration control and the periodic test
record.

Run from the project root:   python -m companion.ch26.lab_d
Writes companion/ch26/expected/d_*.txt. Final settings require project
studies and the operator's approval; tests are named by purpose only.
"""
from __future__ import annotations

import hashlib
import json
import math

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr

N = src.NETWORK


def trace() -> None:
    e = 33e3 / math.sqrt(3)
    z1 = src.feeder_z(3)                 # far end of =WS1-W3 (turbine WS1-3)
    phase = pr.fault_currents(e, z1, z1, complex(0, N["z0_et"]))["3ph"]
    ll = pr.fault_currents(e, z1, z1, complex(0, N["z0_et"]))["LL"]
    earth = pr.fault_currents(e, z1, z1, complex(0, N["z0_et"]), zf=N["r_ner"])["SLG"]
    f = src.RELAYS["feeder"]
    inc = src.RELAYS["incomer"]
    t_f = pr.trip_time(ll, f["pickup"], f["tms"])
    t_i = pr.trip_time(ll, inc["pickup"], inc["tms"])
    lines = ["worked example: faults on =WS1-W3 traced to the evidence",
             f"  1 network data: Z1 at the fault = j{N['z1_33']:.2f} (bus) +"
             f" {z1.real:.2f} + j{z1.imag - N['z1_33']:.2f} (cable) ohm",
             f"  2 study: three-phase {phase / 1e3:.2f} kA, line-to-line"
             f" {ll / 1e3:.2f} kA, earth {earth:.0f} A",
             f"  3 coordination report (LL, the smaller): feeder {t_f:.2f} s,"
             f" incomer {t_i:.2f} s,",
             f"    margin {t_i - t_f:.2f} s; earth: feeder 0.5 s, standby 1.5 s",
             "  4 relay logic: 51 and 51N trip the feeder breaker; 50BF",
             "    starts on trip and opens the incomer if current stays",
             "  5 panel wiring: CT 600/1 to the relay; trip contact to the",
             "    breaker's coil 1, backup to coil 2; DC from the station",
             "    battery through its own MCB with supervision",
             "  6 tests: factory functional test of the panel; secondary",
             "    injection of the settings (purpose: the relay operates",
             "    as set); end-to-end check of the trip from relay to",
             "    breaker; primary checks of the CT ratio and polarity",
             "  7 approval: the setting file, its checksum and the test",
             "    records go to the operator; settings at the grid",
             "    boundary need the operator's written approval",
             "  every step names its record; the methods of the tests and",
             "  any work near live equipment belong to qualified staff"]
    emit("d_trace", lines)


# [start: config]
def setting_file(relay: str, settings: dict, version: str) -> dict:
    """A setting file with a checksum: the record that what was tested
    is what is in the relay."""
    body = json.dumps({"relay": relay, "version": version,
                       "settings": settings}, sort_keys=True)
    return {"relay": relay, "version": version,
            "sha256": hashlib.sha256(body.encode()).hexdigest()[:12]}
# [end: config]


def config() -> None:
    s = dict(src.RELAYS["feeder"])
    a = setting_file("=WS1-Q1-F1", s, "A")
    s2 = dict(s, tms=0.12)
    b = setting_file("=WS1-Q1-F1", s2, "B")
    lines = ["setting-file configuration control (teaching):",
             f"  {a['relay']} rev {a['version']}: checksum {a['sha256']}",
             f"  {b['relay']} rev {b['version']}: checksum {b['sha256']} (TMS 0.10 -> 0.12)",
             "  the checksum read from the relay after testing must equal",
             "  the approved file's; a change gets a new revision, a study",
             "  note, a test and an approval - never an edit on site that",
             "  no record shows (ch 35 for the cyber side)"]
    emit("d_config", lines)


def maintenance() -> None:
    rows = [("relay self-supervision alarms", "continuous", "SCADA alarm log"),
            ("trip-circuit supervision", "continuous", "alarm, monthly check"),
            ("secondary injection of protection", "every 4-6 years (teaching)", "test record"),
            ("breaker timing and operation", "with the breaker's maintenance", "test record"),
            ("CT and VT checks", "after any work on them", "test record"),
            ("event and disturbance records", "after every trip", "analysis note"),
            ("setting file checksum", "yearly and after changes", "configuration record")]
    lines = ["periodic maintenance record of the protection (concept):",
             "  item: when; record"]
    for a, b, c in rows:
        lines += [f"  {a}:", f"    {b}; {c}"]
    lines += ["  intervals come from the makers and the owner's maintenance",
              "  policy (ch 52); the record shows the system is still the",
              "  one that was approved"]
    emit("d_maintenance", lines)


if __name__ == "__main__":
    trace()
    config()
    maintenance()
