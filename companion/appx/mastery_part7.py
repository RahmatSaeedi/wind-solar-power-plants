"""Appendix X - answers of the Part VII diagnostic mastery test (chapters
34-37): for each measurement, network, security and monitoring check, what
it proves, the sourced numbers behind it, who owns it and the evidence
that closes it - with the numbers computed from the chapters' companion
code.

Run from the project root:   python -m companion.appx.mastery_part7
Writes companion/appx/expected/mastery_part7.txt.
Data pack 1.1.0 (synthetic), S0 unless stated; decisions D-038 to D-041.
Values marked (test) are used only here.
"""
from __future__ import annotations

import math

from companion.appx.common import emit
from plantp import instrumentation as ins
from plantp import ot_security as ot
from plantp import performance as pf
from plantp import scada as sc

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def instrumentation() -> None:
    mw = ins.ma_to_eng(13.6, 0.0, 120.0)
    p("M93", f"13.6 mA on a 0-120 MW range: {mw:.1f} MW; a broken wire reads"
             " 0 mA, below the live zero, and is flagged, not read as 0 MW")
    length = ins.loop_max_length(24.0, 12.0, 250.0, 1.5)
    p("M94", f"24 V loop, transmitter needs 12 V, 250 ohm receiver, 1.5 mm2:"
             f" longest loop {length:,.0f} m one way; evidence: loop drawing")
    u = ins.combine(0.2, 0.25, 0.1)
    p("M95", f"chain of 0.2 %, 0.25 % and 0.1 % (test): {u:.2f} % by root sum"
             " of squares - the largest part sets the result")
    a = ins.parallel(ins.availability(50_000.0, 8.0))
    p("M96", f"PPC with MTBF 50,000 h and MTTR 8 h (test): one unit"
             f" {ins.availability(50_000.0, 8.0) * 100:.3f} %, a pair {a * 100:.6f} %"
             " - before common causes, which a pair does not remove (ch 34)")


def networks() -> None:
    cyc = sc.polling_cycle_s(20, 8, 45, 9600.0, 20.0)
    p("M97", f"20 meters polled on one 9,600 bit/s line, 8 + 45 bytes, 20 ms"
             f" turnaround (test): cycle {cyc:.2f} s - the reason for a"
             " second line or report-by-exception")
    loss = sc.fibre_budget_db(6.0, 6, 4)
    p("M98", f"fibre 6 km, 6 splices, 4 connectors with 3 dB margin: {loss:.1f} dB"
             " against the optics' budget; evidence: OTDR test at acceptance")
    gb = sc.retention_gb(5_000, 60.0, 25.0)
    p("M99", f"5,000 points every minute for 25 years (test): {gb:,.0f} GB"
             " before compression; retention follows the data's use")
    p("M100", "16-bit counters wrap in 41 days and float32 kWh counters lose"
              " 7.8 % by year 25 (ch 35): counter types are a design decision")


def security() -> None:
    s = ot.risk_score(4, 4)
    p("M101", f"remote access left open, likelihood 4, consequence 4: score {s},"
              f" '{ot.risk_band(s)}'; owner and date in the risk register")
    bits = ot.entropy_bits(62, 16)
    p("M102", f"16 random characters from 62: {bits:.0f} bits; a default"
              " password has none, whatever its length")
    mean, worst = ot.patch_exposure_days(14.0, 90.0)
    p("M103", f"patch tested 14 days, installed in quarterly windows:"
              f" mean {mean:.0f}, worst {worst:.0f} days exposed - compensating"
              " controls cover the wait")
    a, spof = ot.series_availability({"core switch": 0.9995, "firewall": 0.999,
                                      "historian": 0.998})
    p("M104", f"three parts in series (test): {a * 100:.2f} %; each of"
              f" {len(spof)} is a single point of failure until doubled or accepted")


def monitoring() -> None:
    pr = pf.performance_ratio(10_039_000, 60_060, 206.2)
    p("M105", f"April PR {pr:.3f}, at 25 C {pf.pr_temperature(pr, 41.4):.3f}, against"
              " 0.887-0.901 in the healthy months: the daily slope (0.20 %/day)"
              " and the cleaning step (5.3 %) name soiling")
    m = pf.mtbf_censored([3_200, 7_900, 12_400, 15_100], [17_520] * 8)
    p("M106", f"fans: censored MTBF {m:,.0f} h against 9,650 h from the"
              " failed ones only - survivors are exposure")
    sk = 1 - 14.41 / 24.75
    p("M107", f"day-ahead skill on held-out data {sk:.2f}; the lower-RMSE"
              " forecast cost more to sell with - skill is not money and"
              " neither is a dispatch guarantee")
    t90 = 1 + 3 * math.log(10)
    p("M108", f"set-point step, delay 1 s, tau 3 s: t90 {t90:.1f} s by hand,"
              " 8.5 s measured; the trace, the written specification and"
              " the result are kept together as settlement evidence")


if __name__ == "__main__":
    instrumentation()
    networks()
    security()
    monitoring()
    emit("mastery_part7", OUT)
