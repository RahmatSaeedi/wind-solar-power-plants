"""Chapter 26 - the protection system as hardware and evidence: the CT
burden of 1 A and 5 A secondaries on long leads, the panel's documents,
the tests and their purposes from factory to site, and the timing and
availability of a communications-dependent intertrip.

Run from the project root:   python -m companion.ch26.examples_f
Writes companion/ch26/expected/f_*.txt. Teaching values A-331 to A-335.
"""
from __future__ import annotations

from companion.ch26.common import emit


def burden() -> None:
    r_lead = 2 * 0.200 * 4.6            # ohm: 200 m out and back, 4 mm2 Cu
    relay_va = 0.5
    lines = ["CT burden of the secondary leads (200 m route, 4 mm2 Cu):",
             f"  loop resistance {r_lead:.2f} ohm",
             "  secondary   lead VA   relay VA   total VA"]
    for i in (1.0, 5.0):
        va = i ** 2 * r_lead
        lines.append(f"  {i:6.0f} A   {va:8.1f}   {relay_va:8.1f}   {va + relay_va:8.1f}")
    lines += ["  the 5 A secondary puts 25 times the burden on the CT: on long",
              "  substation routes 1 A secondaries keep the CT out of",
              "  saturation (the knee point of lesson A) - a choice made in the CT",
              "  specification, proved by the CT's test (ch 43)"]
    emit("f_burden", lines)


def documents() -> None:
    docs = [("protection single-line", "zones, CTs, VTs, functions per breaker"),
            ("schematic diagrams", "the circuits: trip, close, alarm, supervision"),
            ("wiring diagrams", "where each wire goes, terminal by terminal"),
            ("terminal and cable lists", "every core of every cable, both ends"),
            ("I/O and signal list", "each signal to SCADA and the operator"),
            ("setting files", "the approved settings with checksum (lab D)"),
            ("logic diagrams", "interlocks, breaker failure, transfer trip")]
    lines = ["documents of a protection panel (each with a revision and a status):"]
    lines += [f"  {a:26s} {b}" for a, b in docs]
    lines += ["  the panel is built and tested from these; a change on site",
              "  without a revised drawing breaks the chain of evidence"]
    emit("f_documents", lines)


def tests() -> None:
    t = [("factory functional test (FAT)", "the panel does what the schematics say", "FAT record"),
         ("CT tests", "ratio, polarity, magnetising curve, insulation", "CT test sheet"),
         ("secondary injection", "each function operates at its setting and time", "injection record"),
         ("trip and interlock checks", "each output reaches its breaker coil", "functional record"),
         ("end-to-end (line ends)", "both ends act together over the channel", "joint record"),
         ("stability check of differential", "no trip for a through current", "test record"),
         ("first energising observations", "relays read the right currents", "commissioning log")]
    lines = ["protection tests and what each proves (purpose, not procedure):"]
    for a, b, c in t:
        lines += [f"  {a}:", f"    proves {b}", f"    record: {c}"]
    lines += ["  tests on secondary circuits are done by qualified staff",
              "  under permits; the energised checks follow the owner's",
              "  safety rules (ch 48-50)"]
    emit("f_tests", lines)


def intertrip() -> None:
    relay, channel, receiver, breaker = 0.020, 0.015, 0.010, 0.060
    total = relay + channel + receiver + breaker
    a1 = 0.999
    lines = ["communications-dependent intertrip from the grid end (teaching):",
             f"  relay {relay * 1e3:.0f} ms + channel {channel * 1e3:.0f} ms + receiver"
             f" {receiver * 1e3:.0f} ms + breaker {breaker * 1e3:.0f} ms = {total * 1e3:.0f} ms",
             f"  one channel available {a1:.3%}; two independent channels"
             f" {1 - (1 - a1) ** 2:.4%}",
             "  the requirement (time and availability) comes from the",
             "  operator; the channels (fibre in the earth wire, a second",
             "  route) and their supervision are part of the scheme, and",
             "  the end-to-end test proves the timing"]
    emit("f_intertrip", lines)


if __name__ == "__main__":
    burden()
    documents()
    tests()
    intertrip()
