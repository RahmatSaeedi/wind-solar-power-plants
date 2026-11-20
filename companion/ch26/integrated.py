"""Chapter 26 - three integrated Plant P examples: a relay grading by hand,
the approved-setting boundary with the operator, and the protection,
earthing and lightning basis (D-030).

Run from the project root:   python -m companion.ch26.integrated
Writes companion/ch26/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch26 import sources as src
from companion.ch26.common import emit
from plantp import protection as pr


def by_hand() -> None:
    f, i = src.RELAYS["feeder"], src.RELAYS["incomer"]
    m = 4000 / f["pickup"]
    t = f["tms"] * 0.14 / (m ** 0.02 - 1)
    mi = 4000 / i["pickup"]
    ti = i["tms"] * 0.14 / (mi ** 0.02 - 1)
    lines = ["one grading point by hand (4 kA through a feeder and its incomer):",
             f"  feeder: I/Is = 4000/{f['pickup']:.0f} = {m:.2f};",
             f"    t = {f['tms']:.2f} x 0.14 / ({m:.2f}^0.02 - 1) = {t:.2f} s",
             f"  incomer: I/Is = 4000/{i['pickup']:.0f} = {mi:.2f};",
             f"    t = {i['tms']:.2f} x 0.14 / ({mi:.2f}^0.02 - 1) = {ti:.2f} s",
             f"  margin {ti - t:.2f} s >= 0.3 s: {'graded' if ti - t >= 0.3 else 'NOT graded'}",
             f"  code check: {pr.trip_time(4000, f['pickup'], f['tms']):.2f} s and"
             f" {pr.trip_time(4000, i['pickup'], i['tms']):.2f} s"]
    emit("int_hand", lines)


def boundary() -> None:
    rows = [("33 kV feeders and incomers", "owner's engineer", "owner"),
            ("main transformer differential", "owner's engineer", "owner"),
            ("132 kV line, plant end", "owner, with the operator's data", "operator"),
            ("132 kV line, grid end", "operator", "operator"),
            ("transfer trip and anti-islanding", "operator's requirement", "operator"),
            ("plant controller limits (ch 20)", "owner", "owner, operator informed")]
    lines = ["approved-setting boundary (who sets, who approves; teaching):"]
    for a, b, c in rows:
        lines += [f"  {a}:", f"    set by {b}; approved by {c}"]
    lines += ["  settings that act across the boundary are approved in",
              "  writing before energising; the approved files and checksums",
              "  are kept with the end-to-end test records"]
    emit("int_boundary", lines)


def register() -> None:
    rows = [("=WS1-Q1-F1", "51 phase OC", 600, src.RELAYS["feeder"]["pickup"],
             f"SI, TMS {src.RELAYS['feeder']['tms']:.2f}"),
            ("=WS1-Q1-F1", "51N earth fault", 100, src.EARTH["feeder"]["pickup"],
             f"DT {src.EARTH['feeder']['delay']:.1f} s (CBCT)"),
            ("=T1-Q2-F1", "51 incomer OC", 1600, src.RELAYS["incomer"]["pickup"],
             f"SI, TMS {src.RELAYS['incomer']['tms']:.2f}"),
            ("=T1-Q1-F1", "51 T1 HV backup", 400, src.RELAYS["T1 HV side"]["pickup"],
             f"SI, TMS {src.RELAYS['T1 HV side']['tms']:.2f}"),
            ("=NER-A-F51N", "51N standby", 400, src.EARTH["NER standby"]["pickup"],
             f"DT {src.EARTH['NER standby']['delay']:.1f} s"),
            ("=WS1-Q1-F1", "50BF", 600, 0.1 * 600, "timer 0.15 s")]
    lines = ["settings register of section A (intermediate example, teaching):",
             "  relay        function         CT      prim A   sec A   curve"]
    for tag, fn, ct, prim, curve in rows:
        lines.append(f"  {tag:12s} {fn:16s} {ct:4d}/1   {prim:6.0f}   {prim / ct:5.3f}   {curve}")
    lines += ["  each row names the study that set it (lessons B and E) and",
              "  the test that proved it (secondary injection); the earth",
              "  fault uses a core-balance CT because 40 A through a 600/1",
              f"  phase-CT residual is only {40 / 600:.3f} A - too little for a",
              "  reliable setting; the register, the file and its checksum",
              "  travel together"]
    emit("int_register", lines)


def basis() -> None:
    lines = ["protection, earthing and lightning basis of Plant P (D-030):",
             "  33 kV: overcurrent and earth fault per feeder, graded with",
             "    >= 0.3 s margins; 400 A resistance earthing; breaker",
             "    failure to the incomer; bus protection or incomer backup",
             "  main transformers: biased differential with inrush blocking,",
             "    gas and pressure devices, overcurrent backup",
             "  132 kV line: line differential over fibre, distance backup,",
             "    transfer trip from the grid end on two channels",
             "  CTs: 1 A secondaries, knee points from the fault levels",
             "  earthing: mesh grid from the soil survey (U-098), GPR and",
             "    touch/step checked by the guide's method with clearing times",
             "  lightning: turbine LPS from the maker; arresters at the line",
             "    entrance and the transformers; risk study with local flash",
             "    density (U-099)",
             "  settings: project studies and the operator's approval"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    boundary()
    register()
    basis()
