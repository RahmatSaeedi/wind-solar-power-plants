"""Chapter 34, lessons C and K (deeper): multicore cables counted from the
I/O list, the repair time of the controller with and without a tested
backup, and what the hot cabinet of lesson C does to the life of the
electronics and of a power supply's capacitors.

Run from the project root:   python -m companion.ch34.examples_s
Writes companion/ch34/expected/s_*.txt.
Teaching values (A-388 and A-392, extended); makers' data decide.
"""
from __future__ import annotations

import math

from companion.ch34 import sources as src
from companion.ch34.common import emit
from plantp import instrumentation as ins


def cables() -> None:
    pairs_ai, cores_di = 12, 24                  # cable sizes (teaching)
    spare = 0.2
    n_ai = n_dig = 0
    pts_ai = pts_dig = 0
    for _, count, ai, di, do in src.EQUIPMENT:
        if ai:
            n_ai += count * math.ceil(ai * (1 + spare) / pairs_ai)
            pts_ai += count * ai
        dig = di + do
        if dig:
            # two cores a point (signal and return), 20 % spare cores
            n_dig += count * math.ceil(2 * dig * (1 + spare) / cores_di)
            pts_dig += count * dig
    lines = ["multicore cables from the I/O list (teaching sizes, 20 % spare)",
             f"  analogue: {pts_ai} points in 12-pair, individually screened"
             f" cables: {n_ai} cables",
             f"  digital (110 V DC): {pts_dig} points, two cores each, in"
             f" 24-core cables: {n_dig} cables",
             "  one item of equipment, one cable or more of its own:",
             "  a shared cable makes two items depend on one route and",
             "  one terminal box; analogue and digital never share,",
             "  and every cable is listed in the cable schedule with",
             "  its class, route and both terminations (ch 24 trays)"]
    emit("s_cables", lines)


def backup_mttr() -> None:
    mtbf = src.PLC["mtbf_h"]
    cases = {"tested backup, spare on site":
             [("diagnose", 1.0), ("fit spare", 0.5), ("load backup", 0.5),
              ("verify by procedure", 2.0)],
             "no tested backup":
             [("diagnose", 1.0), ("fit spare", 0.5), ("rebuild program", 40.0),
              ("verify again", 16.0)],
             "backup, spare from the maker":
             [("diagnose", 1.0), ("wait for spare", 72.0), ("load backup", 0.5),
              ("verify by procedure", 2.0)]}
    lines = ["repair time of one plant controller (teaching; MTBF 150,000 h)",
             "  case                             MTTR h   down min a year"]
    for name, parts in cases.items():
        mttr = sum(h for _, h in parts)
        a = ins.availability(mtbf, mttr)
        lines.append(f"  {name:32s} {mttr:6.1f}   {(1 - a) * 8760 * 60:15.1f}")
    lines += ["  the repair time is mostly paperwork and waiting: a backup",
              "  that was restored once in a test, a spare on the shelf",
              "  with the same firmware, and a written verification turn",
              "  days into hours; the backup is taken after every change",
              "  and its fingerprint compared with the running program"]
    emit("s_backup", lines)


def life_in_heat() -> None:
    ea_ev, k_ev = 0.7, 8.617e-5               # teaching activation energy
    def factor(t1: float, t2: float) -> float:
        return math.exp(ea_ev / k_ev * (1 / (t1 + 273.15) - 1 / (t2 + 273.15)))
    rise = 20.0                                # capacitor above cabinet air
    rated_h, rated_c = 5000.0, 105.0           # electrolytic capacitor
    lines = ["electronics in the cabinet of lesson C (teaching)",
             "  room C   cabinet air C   failure-rate factor   capacitor life years"]
    lives = []
    for room, t in ((25.0, 34.0), (40.0, 49.0), (47.0, 56.0)):
        f = factor(34.0, t)
        life = rated_h * 2 ** ((rated_c - (t + rise)) / 10) / 8760
        lives.append(life)
        lines.append(f"  {room:6.0f}   {t:13.0f}   {f:19.2f}   {life:20.1f}")
    lines += ["  (failure rate against the cooled cabinet at 34 C, 0.7 eV;",
              "  capacitor 5,000 h at 105 C, life doubling for each 10 K",
              "  cooler, running 20 K above the cabinet air)",
              f"  a cabinet that lives at 56 C fails its electronics about"
              f" {factor(34.0, 56.0):.0f}",
              f"  times as often as the cooled one and wears out a power",
              f"  supply's capacitors in about {lives[-1]:.0f} years instead of"
              f" {lives[0]:.0f} - the",
              "  cooling of lesson C is a reliability decision, and the",
              "  supplies get a replacement interval in the maintenance",
              "  plan (ch 51)"]
    emit("s_life", lines)


if __name__ == "__main__":
    cables()
    backup_mttr()
    life_in_heat()
