"""Chapter 42, an eleventh round: blade mould capacity against the
erection pace, the data a blade's ultrasonic scan leaves behind, and what
the gearbox run-in is worth in field exchanges avoided.

Run from the project root:   python -m companion.ch42.examples_n
Writes companion/ch42/expected/n_*.txt.
Teaching values (A-452, A-456).
"""
from __future__ import annotations

import math

from companion.ch42.common import emit


# ------------------------------------------------ blade mould capacity
def moulds(sets: int = 2, cycle_h: float = 30.0, avail: float = 0.85,
           blades: int = 38, finish_days: float = 5.0,
           erect_days: float = 3.0) -> dict[str, float]:
    per_week = sets * 168.0 * avail / cycle_h
    weeks = blades / per_week
    need_per_week = 3 * 7.0 / erect_days
    buffer = per_week / sets                 # one set down for a week
    lead_days = finish_days + buffer / per_week * 7.0
    lines = [f"blade factory: {sets} mould sets, {cycle_h:.0f} h a blade, "
             f"{avail:.0%} available,",
             "  three shifts (teaching)",
             f"  {per_week:.1f} blades a week; {blades} blades (36 + 2 spares) "
             f"in {weeks:.1f} weeks",
             f"  plus {finish_days:.0f} days of finishing and testing before "
             "the first ships",
             f"  erection at one turbine every {erect_days:.0f} days needs "
             f"{need_per_week:.0f} blades a week",
             f"  the factory makes {per_week / need_per_week:.1f} x what "
             "erection takes, so once",
             "  running it stays ahead; a mould set down for a week costs "
             f"{buffer:.0f} blades",
             f"  start moulding {lead_days:.0f} days before the first lift: "
             f"finishing plus a buffer of {buffer:.0f}",
             "  blades - the factory's schedule risk is the moulds, not the",
             "  people"]
    emit("n_moulds", lines)
    return dict(per_week=per_week, weeks=weeks, lead_days=lead_days,
                buffer=buffer)


# ------------------------------------------------ scan data of a blade
def scan_data(caps_m2: float = 2 * 0.9 * 70.0, bonds_m2: float = 3 * 70.0 * 0.12,
              pitch_mm: float = 2.0, samples: int = 256, bytes_per: int = 2,
              blades: int = 38) -> dict[str, float]:
    area = caps_m2 + bonds_m2
    points = area * 1e6 / pitch_mm ** 2
    cmap = points * 2 * 4 / 1e9                     # amplitude + time, float32
    full = points * samples * bytes_per / 1e9
    lines = [f"ultrasonic scan of one blade: caps {caps_m2:.0f} m2, bond lines "
             f"{bonds_m2:.0f} m2, every {pitch_mm:.0f} mm",
             f"  {points / 1e6:.1f} million points",
             f"  C-scan maps (amplitude and time, 4 bytes each): "
             f"{cmap:.2f} GB a blade",
             f"  full waveforms ({samples} samples x {bytes_per} bytes): "
             f"{full:.0f} GB a blade, {full * blades / 1000:.1f} TB for the plant",
             "  the maps answer today's question; only the waveforms let a",
             "  later finding be re-read in the factory data - which to keep,",
             "  and for how long, is a retention decision (ch 35) written",
             "  into the contract, not left to the factory's disk"]
    emit("n_scan", lines)
    return dict(points=points, cmap_gb=cmap, full_gb=full)


# ------------------------------------------------ value of the run-in
def runin_value(held: int = 3, units: int = 10, p_fail: float = 0.40,
                campaign_k: float = 450.0, repair_k: float = 500.0,
                lost_k: float = 60.0, test_k: float = 12.0) -> dict[str, float]:
    exchange = campaign_k + repair_k + lost_k
    saved = held * p_fail * exchange
    cost = units * test_k
    lines = [f"gearbox run-in: {held} of {units} units held (lab D); value in "
             "field exchanges avoided",
             f"  a held defect fails early in service with chance {p_fail:.0%} "
             "(teaching)",
             f"  one exchange: crane {campaign_k:.0f} + repair {repair_k:.0f} + "
             f"lost energy {lost_k:.0f} = {exchange:,.0f} k u",
             f"  expected saving {saved:,.0f} k u against a test cost of "
             f"{cost:.0f} k u ({saved / cost:.0f} x)",
             f"  break-even chance of failure: {cost / (held * exchange):.0%}",
             "  the run-in pays even if only one held defect in "
             f"{held * exchange / cost:.0f}",
             "  would have failed - the case for testing every unit, not a",
             "  sample, when a field failure costs a crane campaign"]
    emit("n_runin", lines)
    return dict(saved=saved, cost=cost, breakeven=cost / (held * exchange))


if __name__ == "__main__":
    moulds()
    scan_data()
    runin_value()
