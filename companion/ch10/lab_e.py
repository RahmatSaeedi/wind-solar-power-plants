"""Chapter 10, section E - evidence: a batch of factory flash results, a
laboratory re-measurement of a sample with its uncertainty, and the
conformity decision; the string-limit boundary cases.

Run from the project root:   python -m companion.ch10.lab_e
Writes companion/ch10/expected/e_*.txt and diagrams/data/ch10-*.csv.
Teaching values A-198 (fictional, seed 43).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch10.common import csv, emit
from companion.ch10.examples_c import string_limits


def flash() -> None:
    rng = np.random.default_rng(43)                             # A-198
    true = rng.normal(552.5, 2.2, 600)
    factory = true * (1 + rng.normal(0.004, 0.006, 600))        # flasher reads high
    labelled = factory[(factory >= 550) & (factory < 555)][:120]
    idx = rng.choice(120, 12, replace=False)
    t_sample = true[(factory >= 550) & (factory < 555)][:120][idx]
    lab = t_sample * (1 + rng.normal(0, 0.008, 12))             # lab, u = 0.8 %
    u_lab = 0.016 * lab.mean()                                  # expanded, k 2
    mean = lab.mean()
    u_mean = math.sqrt((u_lab / 2) ** 2 / 1 + (lab.std(ddof=1) / math.sqrt(12)) ** 2) * 2
    lines = ["120 modules labelled 550 W (class 550.0 .. 555.0 W), A-198:",
             f"  factory flash: mean {labelled.mean():.1f} W, min "
             f"{labelled.min():.1f}, max {labelled.max():.1f}",
             f"  laboratory re-measurement of 12: mean {mean:.1f} W, "
             f"spread (1 s) {lab.std(ddof=1):.1f} W",
             f"  lab / factory on the same 12: "
             f"{mean / labelled[idx].mean():.4f}",
             f"  expanded uncertainty of the sample mean (k 2) +-{u_mean:.1f} W",
             f"  conformity proven (mean - U >= 550 W)? "
             f"{mean - u_mean:.1f} W -> {'yes' if mean - u_mean >= 550 else 'no'}",
             f"  non-conformity proven (mean + U < 550 W)? "
             f"{mean + u_mean:.1f} W -> {'yes' if mean + u_mean < 550 else 'no'}",
             "  neither: the result lies in the zone of uncertainty and only",
             "  the decision rule written in the contract settles it",
             f"  individual lab values below 550 W: {int((lab < 550).sum())} of 12",
             "  a lab result a little under the label is not by itself a",
             "  defect: the label is the maker's flasher with its own",
             "  calibration; the contract says which measurement decides"]
    emit("e_flash", lines)
    csv("ch10-flash.csv", "k,factory,lab",
        [(int(k), f"{labelled[i]:.2f}", f"{v:.2f}")
         for k, (i, v) in enumerate(zip(idx, lab))])


def boundary() -> None:
    lines = ["string checks at the boundaries (the tests of section E):",
             "  case                              V_oc cold   V_mp hot  verdict"]
    for name, n, tmin, thot in (("26 modules, -15 C / 72 C", 26, -15, 72),
                                ("27 modules, -15 C / 72 C", 27, -15, 72),
                                ("27 modules, -25 C (colder site)", 27, -25, 72),
                                ("28 modules, -15 C", 28, -15, 72),
                                ("26 modules, 80 C cell (roof)", 26, -15, 80)):
        r = string_limits(n, tmin, thot)
        v = ("ok" if r["ok_v_sys"] and r["ok_floor"] else
             "over 1500 V" if not r["ok_v_sys"] else "below window")
        lines.append(f"  {name:32s}  {r['v_oc_cold']:7.0f} V  "
                     f"{r['v_mp_hot']:7.0f} V  {v}")
    emit("e_boundary", lines)


if __name__ == "__main__":
    flash()
    boundary()
