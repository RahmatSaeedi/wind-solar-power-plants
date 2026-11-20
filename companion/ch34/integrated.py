"""Chapter 34 - three integrated Plant P examples: two results by hand,
the I&C package in numbers, and the basis D-038.

Run from the project root:   python -m companion.ch34.integrated
Writes companion/ch34/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch34 import sources as src
from companion.ch34.common import emit
from companion.ch34 import examples_c as c34
from plantp import instrumentation as ic


def by_hand() -> None:
    ma = 4 + 16 * 132 / 150
    r = 100 * (1 + 3.9083e-3 * 95 - 5.775e-7 * 95 ** 2)
    lines = ["two I&C results checked by hand",
             f"  132 kV on a 0-150 kV transducer: 4 + 16 x 132/150 = {ma:.2f} mA;"
             f" code {ic.eng_to_ma(132, 0, 150):.2f}",
             f"  Pt100 at 95 deg C: 100 (1 + 0.0039083 x 95 - 5.775e-7 x 95^2)"
             f" = {r:.2f} ohm;",
             f"    code {ic.pt100_r(95.0):.2f}",
             "  a hand check of the scaling catches the commonest I/O",
             "  error: a range typed in the wrong units or a 0-20 mA",
             "  channel read as 4-20 mA"]
    emit("int_hand", lines)


def package() -> None:
    ai, di, do = c34.io_totals()
    lines = ["the I&C package of Plant P in numbers",
             f"  hard-wired I/O: {ai} AI, {di} DI, {do} DO = {ai + di + do} points,",
             "    29 modules with 20 % spare",
             "  POC voltage chain: +/-0.66 % (k = 2) with a class 0.5 VT,",
             "    +/-0.39 % with class 0.2",
             "  PLC response budget 160 ms; controller cycle <= tau / 4",
             "  FAT about 48 h of point tests and functions; site loop checks",
             "    8 crew-days; 12 loss-of-supply tests; 26 control-mode test points",
             f"  fire interface: {len(src.FIRE)} signals, hard-wired NC alarms, reset at",
             "    the fire panel only",
             "  110 V DC autonomy 4.5 h with the 24 V loads (requirement 4 h)"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-038 instrumentation and control basis of Plant P (teaching)",
             "  1 measurement: 4-20 mA with live zero and quality (3.6-21 mA),",
             "    POC voltage from a class 0.2 VT core, synchronised clocks with",
             "    a 'synchronised' flag on every time stamp, calibration",
             "    intervals from recorded drift",
             "  2 control: protection never in the PLC; PLC 50 ms scan; PPC",
             "    cycle <= tau / 4 with its computing delay; permissives fail",
             "    safe on bad quality; heartbeat watchdog set from the measured",
             "    packet loss; redundant PLC pair in separate cabinets",
             "  3 design: I/O list with checker, control C&E with a test per",
             "    effect, configuration fingerprints, FAT with a punch list",
             "  4 control power: 24 V from the 110 V battery, far-panel DC",
             "    feeders sized at end-of-discharge voltage (10 mm2, not 2.5),",
             "    cabinet temperature alarmed, written restart sequence",
             "  5 fire interface: hard-wired, normally closed, independent of",
             "    the PLC; acknowledge at the HMI, reset at the fire panel",
             "  6 grid services: set points validated, held when stale, fallback",
             "    after 1 h (ch 20), modes enabled only when required or offered",
             "  7 later findings: metering/control CT core of an extended-range",
             "    class (night current 1.5 % of rated); PPC cycle <= 0.66 s for",
             "    a 45 deg phase margin; short pulses latched, never scanned;",
             "    bumpless transfer by tracking and a ramped set point; the",
             "    POC transducer and self-holding pump contactors on DC so",
             "    the plant does not trip on its own auxiliaries after a",
             "    fault; POC measured in the grid bay or corrected by a line",
             "    model (D-021); supplies replaced on a set interval",
             "  open: grid operator's interface requirements (U-115), makers'",
             "    I/O and accuracy data (U-116)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
