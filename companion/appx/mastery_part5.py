"""Appendix X - answers of the Part V diagnostic mastery test (chapters
23-28): for each study or design check, what it proves, the data it
needs, who approves it and what evidence closes the requirement - with
the numbers computed from the chapters' companion code.

Run from the project root:   python -m companion.appx.mastery_part5
Writes companion/appx/expected/mastery_part5.txt.
Data pack 1.1.0 (synthetic), S0 unless stated; decisions D-027 to D-032.
Values marked (test) are used only here.
"""
from __future__ import annotations

import math

import numpy as np

from companion.appx.common import emit
from companion.ch24 import sources as s24
from companion.ch28 import sources as s28
from plantp import gridstudy as gs
from plantp import pq
from plantp import protection as pr

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def circuits() -> None:
    br = s28.branches("max")
    zbus = np.linalg.inv(gs.ybus(s28.N, br)[1:, 1:])
    s_mv = 100 / abs(zbus[2, 2])
    p("M61", f"grid fault level at the 33 kV bus MV-A: {s_mv:.0f} MVA"
             f" ({s_mv / (math.sqrt(3) * 33):.2f} kA); proves switchgear duty"
             " with the grid maximum; data: POC level, transformer uk; evidence:"
             " study + rating plates")
    i = 20e6 / (math.sqrt(3) * 33e3)
    f = float(np.prod(list(s24.FACTORS.values())))
    need = i / f
    pick = min(s for s, d in s24.MV_CABLES.items() if d["i0"] >= need)
    p("M62", f"20 MW feeder: {i:.0f} A; installation factor {f:.3f};"
             f" reference rating needed {need:.0f} A -> {pick} mm2"
             f" ({s24.MV_CABLES[pick]['i0'] - need:.0f} A to spare: marginal;"
             " a worse route section needs 630 mm2)")
    p("M63", "S1 battery HVAC about 320 kW against the 250 kVA station"
             " transformer (ch 25 finding): a separate supply is needed")
    p("M64", "132 kV line: 437 A needs at least 0.74 m/s of wind at 45 C"
             " (ch 24); in the data year no hour bound (ch 28, wind cools it)")


def transformers_protection() -> None:
    from companion.ch15 import sources as s15
    mv = np.clip(s15.plant_year()["mv"], 0, None)
    load_mwh = 0.250 * float(np.sum((mv / 2 / 63.0) ** 2)) * 2
    noload_mwh = 2 * 0.035 * 8760
    p("M65", f"two main transformers a year: load losses {load_mwh:.0f} MWh,"
             f" no-load {noload_mwh:.0f} MWh (all year)")
    p("M66", "taps +/-10 % hold the 33 kV bus except at a 1.10 pu grid with"
             " output (ch 28): the units then absorb Q - an operating"
             " restriction")
    i_f = 5000.0                                         # A at 33 kV (test)
    t_f = pr.trip_time(i_f, 480.0, 0.10)
    t_i = pr.trip_time(i_f, 1600.0, 0.11)
    p("M67", f"5 kA feeder fault (test): feeder relay {t_f:.2f} s, incomer"
             f" {t_i:.2f} s, margin {t_i - t_f:.2f} s"
             f" ({'graded' if pr.grading_ok(t_f, t_i) else 'NOT graded'} at 0.3 s)")
    p("M68", "line plant end: fault resistance seen x12 (grid infeed),"
             " plant fault current 1.35 x full load: differential or"
             " intertrip, agreed at the shared boundary")


def power_quality() -> None:
    hr = math.sqrt(365 / 1.77)
    c, l_mh, xc, xl = pq.tuned_filter(5.0, 4.7, 33.0)
    pst = [0.3] * 11 + [0.9]
    plt_ = (sum(x ** 3 for x in pst) / 12) ** (1 / 3)
    p("M69", f"33 kV bus with 1.77 Mvar of cables on 365 MVA: resonance"
             f" h = {hr:.1f}")
    p("M70", f"5 Mvar filter tuned to 4.7 at 33 kV: C {c:.2f} uF, L {l_mh:.1f} mH"
             " per phase")
    p("M71", f"Plt of eleven Pst 0.3 and one 0.9: {plt_:.3f}")
    p("M72", "5th harmonic 95th percentile 1.83 % against a teaching 2.0 %:"
             " margin 9 % - inside the measurement uncertainty; evidence:"
             " class-A instrument, flagged intervals, uncertainty statement")


def grid_studies() -> None:
    z = gs.thevenin(1500, 8)
    p("M73", f"POC rise for 100 MW at Q = 0 by hand {100 * z.real:.2f} %;"
             " load flow 0.61 %")
    p("M74", "REQ-G04 ride-through: study C-frt with RMS (and EMT on a weak"
             " grid) models; unit type test; evidence: type test + validated"
             " model; approved by the operator")
    p("M75", "passive islanding relays blind ~1,760 h a year; intertrip on a"
             f" 99.9 % channel leaves {0.001 * 1760:.2f} h a year")
    p("M76", "N-1: line maintenance day 810 MWh at random, 76 on a calm day;"
             " losses 4.41 against model 15.1's 3.29 GWh")


if __name__ == "__main__":
    circuits()
    transformers_protection()
    power_quality()
    grid_studies()
    emit("mastery_part5", OUT)
