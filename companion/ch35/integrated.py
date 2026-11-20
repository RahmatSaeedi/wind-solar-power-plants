"""Chapter 35 - three integrated Plant P examples: two results by hand,
the SCADA package in numbers, and the basis D-039.

Run from the project root:   python -m companion.ch35.integrated
Writes companion/ch35/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch35.common import emit
from plantp import scada as sc


def by_hand() -> None:
    poll = 30 * ((8 + 45) * 8 / 9600 * 1000 + 15) / 1000
    mbps = 12 * 600 * 20 * 8 / 1e6
    lines = ["two SCADA results checked by hand",
             f"  30 meters, 53 bytes at 9600 bit/s + 15 ms each: {poll:.2f} s;"
             f" code {sc.polling_cycle_s(30, 8, 45, 9600, 15):.2f}",
             f"  12 turbines x 600 tags x 20 bytes x 8 bits a second: {mbps:.2f} Mbit/s",
             "  a hand check of bits against bytes catches the commonest",
             "  error in a network calculation - a factor of eight"]
    emit("int_hand", lines)


def package() -> None:
    lines = ["the SCADA and communications package of Plant P in numbers",
             "  two single-mode fibre rings for the turbines; the west ring",
             "    needs longer-reach optics (10.8 dB against 10 dB)",
             "  steady traffic 4.5 Mbit/s: 4 % of an edge link",
             "  time synchronisation 1.45 us worst case: events yes, 1 us no",
             "  five functional subnets; 22,300 tags; 6 diagram types kept",
             "  historian about 12 TB over the plant's life",
             "  fire boundary: monitor only, two routes to a person when",
             "    the room is empty, both clocks kept",
             "  asset IDs: 2 of 7 in the extract do not line up"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-039 SCADA and communications basis of Plant P (teaching)",
             "  1 network: single-mode fibre in the collector trenches, two",
             "    turbine rings with a fast ring protocol (recovery well",
             "    under the 3 s watchdog of ch 34), functional subnets",
             "  2 time: precision time protocol for events; a 1 us need",
             "    would need better end devices",
             "  3 data: values as objects with unit, quality and time; tag",
             "    rule checked by program; 32-bit counters; quality map of",
             "    every gateway in the interface specification",
             "  4 operations: alarm philosophy with delays and deadbands,",
             "    buffers at the source, retention 2 years raw and the",
             "    plant's life for aggregates, least-privilege roles",
             "  5 fire boundary: approved statuses only, no commands,",
             "    independent alarm routes, panel and SCADA stamps kept",
             "  6 asset data: register as the source of asset IDs, one-way",
             "    flows to CMMS, deduplicated work requests, UTC, queues",
             "  7 later findings: priority classes on every switch port (a",
             "    control message waits 0.12 ms, not 120 ms, behind a",
             "    back-fill); back-fill rate-limited; a second carrier only",
             "    on a separate route; counters as integers (a float32 kWh",
             "    counter loses 7.8 % in year 25); word order tested with a",
             "    known value; state-based alarm suppression (151 -> 13);",
             "    commands refused during server switch-over; stale limits",
             "    above the integrity-scan period; sampling from the",
             "    fastest phenomenon; acceptance samples of about 300",
             "    points for 1 %, full tests for control and grid points",
             "  open: grid operator's protocol profile and telemetry list",
             "    (U-115), makers' data and device declarations (U-116)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
