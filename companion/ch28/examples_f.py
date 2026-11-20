"""Chapter 28, lesson F (when required or contracted): the P-Q envelope
at the POC with and without the battery and on a hot day, two voltage
controllers that fight, the model and firmware versions against the
site, and one service traced from requirement to measurement.

Run from the project root:   python -m companion.ch28.examples_f
Writes companion/ch28/expected/f_*.txt and diagrams/data/ch28-envelope.csv.
Teaching values; requirements are placeholders (U-102).
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import register as reg
from companion.ch28 import sources as src
from companion.ch28.common import csv, emit

CASES = {"S0, 25 C": ({}, 1.0), "S0, 45 C (0.9 derating)": ({}, 0.9),
         "S1 (battery), 25 C": ({"bess": 0.0}, 1.0)}


def envelope() -> None:
    x_list = (0.0, 0.18, 0.36, 0.55, 0.73, 0.91)
    lines = ["P-Q envelope at the POC (grid max, source 1.00 pu; units inside 0.90-1.10)",
             "  P POC MW   S0 25 C give/absorb   S0 45 C give/absorb   S1 25 C give/absorb"]
    data = []
    for x in x_list:
        row = []
        for name, (extra, der) in CASES.items():
            ps = {"wind": x, "pv": x, **extra}
            hi = src.q_limits(ps, 1, derate=der)
            lo = src.q_limits(ps, -1, derate=der)
            row.append((hi["s_poc"].real, hi["s_poc"].imag, lo["s_poc"].imag))
        p = row[0][0]
        data.append((p, row))
        lines.append(f"  {p:8.1f}   " + "   ".join(f"{h:+8.1f} / {l_:+7.1f}" for _, h, l_ in row))
    csv("ch28-envelope.csv", "p,s0hi,s0lo,hothi,hotlo,s1hi,s1lo",
        [(f"{p:.1f}", *(f"{v:.1f}" for _, h, l_ in row for v in (h, l_))) for p, row in data])
    full = data[-1][1]
    worst = {name: min(row[k][1] for p, row in data if p >= 19.0)
             for k, name in enumerate(CASES)}
    lines += [f"  at full output the hot day costs {full[0][1] - full[1][1]:.0f} Mvar of giving;"
              f" the battery adds {full[2][1] - full[0][1]:.0f}",
              "  least giving from 20 % to 100 % output, Mvar: "
              + ", ".join(f"{short} {v:.0f}" for short, v in zip(("S0", "S0 hot", "S1"),
                                                                 worst.values())),
              "  a teaching requirement of +33 Mvar is met at 25 C but NOT",
              "  on a 45 C day at full output; the battery (S1) or a",
              "  capacitor bank would close the gap - so the requirement's",
              "  temperature and the battery's share are study inputs"]
    emit("f_envelope", lines)


# [start: fight]
def fight(local: str, t_end: float = 60.0, dt: float = 0.05) -> tuple:
    """Plant controller integrating the POC voltage error together with
    unit-level control at the terminals: 'off' (units follow the plant
    set-point), 'droop' (proportional) or 'integral' (a second
    integrator). Returns the final plant and local Mvar and voltages."""
    s_sc, drop = 1500.0, 0.015              # terminals sit 1.5 % above POC
    q_p = q_l = 0.0
    for _ in range(int(t_end / dt)):
        q = max(min(q_p + q_l, 46.0), -46.0)
        v_poc = 0.995 + q / s_sc
        v_unit = v_poc + drop + q / 1000.0
        q_p += 300.0 * (1.0 - v_poc) * dt
        q_p = max(min(q_p, 46.0), -46.0)
        if local == "droop":
            q_l = -400.0 * (v_unit - 1.0) * 0.1
        elif local == "integral":
            q_l += 300.0 * (1.0 - v_unit) * dt
            q_l = max(min(q_l, 46.0), -46.0)
    return q_p, q_l, v_poc, v_unit
# [end: fight]


def interactions() -> None:
    lines = ["two voltage controllers in series (POC set-point 1.00; terminals 1.5 % above)",
             "  unit mode     plant Mvar   local Mvar   V POC    V terminal"]
    for mode in ("off", "droop", "integral"):
        qp, ql, vp, vu = fight(mode)
        lines.append(f"  {mode:12s}  {qp:10.1f}   {ql:10.1f}   {vp:6.3f}   {vu:10.3f}")
    lines += ["  with the units following the plant set-point the POC sits",
              "  at 1.00; a local droop leaves a small offset the plant's",
              "  integrator removes; a second integrator chasing 1.00 at the",
              "  terminals fights the first: both wind up to opposite",
              "  limits, the net Mvar is whatever is left - one integrator",
              "  per controlled quantity, and the study checks the modes"]
    emit("f_interactions", lines)


def versions() -> None:
    lines = ["model and firmware versions: study against site (register, teaching)",
             "  model              kind        in the study           on site        check"]
    n_bad = 0
    for model, kind, _, study, site in reg.MODELS:
        ok = study.split(" / ")[-1].split(", ")[-1] in site or site in study
        if study == "not received":
            ok = False
        n_bad += not ok
        lines.append(f"  {model:18s} {kind:11s} {study:22s} {site:14s} "
                     f"{'ok' if ok else 'CHECK'}")
    lines += [f"  {n_bad} of {len(reg.MODELS)} need action: a firmware change after the",
              "  study (PV 4.1.7 -> 4.2.0) needs the OEM's statement that the",
              "  model still holds or a new model; a missing model blocks the",
              "  study it feeds; a calculated line is replaced by measurement"]
    emit("f_versions", lines)


def trace() -> None:
    chain = [("requirement", "REQ-G24: 5 MW, 15 min, within 1 s", "placeholder"),
             ("capability", "BESS headroom 5 MW, 1.25 MWh above SOC floor", "S1 only"),
             ("study", "C-freq, F-envelope with the BESS model", "blocked IN-24"),
             ("model", "BESS PCS RMS model, firmware 2.0.3", "not received"),
             ("test", "frequency injection at plant controller", "planned"),
             ("measurement", "100 ms POC data with time stamps (ch 27)", "available"),
             ("evidence", "test report vs model, operator acceptance", "open")]
    lines = ["one service traced from requirement to evidence (teaching)",
             "  link          content                                       status"]
    for link, content, status in chain:
        lines.append(f"  {link:12s}  {content:45s} {status}")
    lines += ["  the chain is only as good as its weakest link: here the",
              "  missing battery model blocks the study, so the service",
              "  cannot be offered yet whatever the battery could do"]
    emit("f_trace", lines)


if __name__ == "__main__":
    envelope()
    interactions()
    versions()
    trace()
