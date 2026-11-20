"""Chapter 34, lesson K (manufacturing): where the accuracy and the
reliability of the control equipment are made - the calibration chain
and its test uncertainty ratio, burn-in against early failures, and the
panel's factory inspection by sample.

Run from the project root:   python -m companion.ch34.examples_k
Writes companion/ch34/expected/k_*.txt.
Teaching values (A-392); the makers' quality plans and ch 48 decide.
"""
from __future__ import annotations

import math

from scipy import stats

from companion.ch34.common import emit
from plantp import instrumentation as ic


def chain() -> None:
    rows = [("national standard", 0.002), ("accredited lab reference", 0.005),
            ("factory working standard", 0.01), ("field calibrator", 0.025)]
    device = 0.2                                  # % tolerance of the transmitter
    lines = ["the calibration chain of a 4-20 mA transmitter (teaching, % of span)",
             "  level                         uncertainty   ratio to the next level"]
    for k, (name, u) in enumerate(rows):
        nxt = rows[k + 1][1] if k + 1 < len(rows) else device
        lines.append(f"  {name:28s} {u:11.3f}   {nxt / u:8.1f} : 1")
    tur = device / rows[-1][1]
    whole = ic.combine(*[u for _, u in rows])
    lines += [f"  the whole chain adds up to {whole:.4f} %, {whole / rows[-1][1] * 100 - 100:.0f} % more"
              " than the calibrator alone",
              f"  the field calibrator checks a {device} % transmitter at {tur:.0f}:1;",
              "  the 4:1 rule of thumb is for that pass/fail check, so the",
              "  calibrator's own error does not decide it; the upper",
              "  levels work at smaller ratios because each states its",
              "  uncertainty on a certificate that names the level above",
              "  it, and the uncertainties are added (ch 2, ch 48)"]
    emit("k_chain", lines)


def burn_in() -> None:
    n, weak, eta_weak, mtbf = 300, 0.02, 100.0, 200_000.0     # teaching mixture
    lines = ["burn-in against early failures: 2 % weak modules among good ones",
             f"  weak: mean life {eta_weak:.0f} h; good: MTBF {mtbf:,.0f} h; {n} modules",
             "  burn-in h   found in factory   failing in the field, first year"]
    for b in (0.0, 72.0, 168.0):
        found = n * weak * (1 - math.exp(-b / eta_weak))
        weak_left = n * weak * math.exp(-b / eta_weak)
        field = weak_left + n * (1 - weak) * (1 - math.exp(-8760.0 / mtbf))
        lines.append(f"  {b:9.0f}   {found:16.1f}   {field:31.1f}")
    lines += ["  burn-in removes the weak modules where a replacement is",
              "  cheap; it cannot touch the random failures of good ones",
              "  (about 13 a year here), which spares and redundancy",
              "  handle - the FAT of ch 40 asks for the burn-in record"]
    emit("k_burnin", lines)


def sample_inspection() -> None:
    n_term, n_sample, defects_found = 2400, 125, 1
    lo, hi = stats.beta.ppf([0.05, 0.95], defects_found + 0.5, n_sample - defects_found + 0.5)
    lines = ["panel wiring checked by sample at the factory (teaching)",
             f"  {n_term:,} terminations; {n_sample} checked by pull test and"
             f" drawing; {defects_found} wrong",
             f"  defect rate estimate {defects_found / n_sample * 100:.1f} %"
             f" (90 % range {lo * 100:.2f} - {hi * 100:.1f} %)",
             f"  expected wrong terminations in the panel: about"
             f" {defects_found / n_sample * n_term:.0f}",
             "  a sample cannot prove the rest right: every I/O point is",
             "  still tested end to end in the FAT and the loop checks",
             "  (lesson C) - the sample tells whether the wiring shop's",
             "  process is under control (ch 48)"]
    emit("k_sample", lines)


if __name__ == "__main__":
    chain()
    burn_in()
    sample_inspection()
