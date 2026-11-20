"""Chapter 36 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch36.worked
Writes companion/ch36/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch36.common import emit
from plantp import ot_security as ot


def worked() -> None:
    lines = [f"E01 risk 3 x 5: {ot.risk_score(3, 5)} ({ot.risk_band(15)})",
             f"E02 10 letters and digits: {ot.entropy_bits(62, 10):.1f} bits",
             f"E03 1e5 events/day of 400 B for 365 d: {ot.log_volume_gb(1e5, 400, 365):.1f} GB",
             f"E04 patch tested 10 d, window 60 d: mean {ot.patch_exposure_days(10, 60)[0]:.0f},"
             f" worst {ot.patch_exposure_days(10, 60)[1]:.0f} days",
             f"E05 restore 0.5 + 1 + 1 + 2 h: {ot.recovery_time_h(dict(a=0.5, b=1, c=1, d=2)):.1f} h",
             f"E06 two parts 0.999 and 0.9995 in series: "
             f"{ot.series_availability(dict(a=0.999, b=0.9995))[0]:.6f}"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 risk 2 x 5 and band: {ot.risk_score(2, 5)} {ot.risk_band(10)}",
           f"P02 risk 4 x 2 and band: {ot.risk_score(4, 2)} {ot.risk_band(8)}",
           f"P03 8 lower-case letters: {ot.entropy_bits(26, 8):.1f} bits",
           f"P04 16 letters and digits: {ot.entropy_bits(62, 16):.1f} bits",
           f"P05 logs, 34 switches x 2,000 x 200 B x 365: "
           f"{ot.log_volume_gb(34 * 2000, 200, 365):.1f} GB",
           f"P06 logs, 1 year at 500,000 events/day of 300 B: "
           f"{ot.log_volume_gb(5e5, 300, 365):.1f} GB",
           f"P07 patch, test 21 d, window 180 d: mean "
           f"{ot.patch_exposure_days(21, 180)[0]:.0f} d",
           f"P08 same, worst: {ot.patch_exposure_days(21, 180)[1]:.0f} d",
           f"P09 vendor access 24 sessions of 3 h: {24 * 3} h; cut "
           f"{(1 - 72 / 8760) * 100:.1f} %",
           f"P10 drift 30 ppm for 14 days: {30e-6 * 14 * 86400:.0f} s",
           f"P11 restore 0.2 + 1 + 1 + 6 + 2 h: {0.2 + 1 + 1 + 6 + 2:.1f} h",
           f"P12 backup broken 3 %/month, tested yearly: "
           f"{(1 - 0.97 ** 6.5) * 100:.1f} %",
           f"P13 three copies at 10 % each: {0.1 ** 3 * 100:.2f} %",
           f"P14 firewall pair of 0.999 each: {1 - (1 - 0.999) ** 2:.6f}",
           f"P15 one firewall 0.999 in series with a switch 0.9998: "
           f"{0.999 * 0.9998:.6f}",
           f"P16 end of support every 7 y over 25 y: {-(-25 // 7) - 1} replacements",
           f"P17 supplier 4,3,4,3,2 with weights 3,3,2,2,1: "
           f"{(4 * 3 + 3 * 3 + 4 * 2 + 3 * 2 + 2 * 1) / 11:.2f}",
           f"P18 changes, 80 a year at 2 h each: {80 * 2} h",
           f"P19 logs read weekly: mean {7 / 2:.1f} d unseen",
           f"P20 plant stopped 3 days at 33.7 MWh/h and 50 u/MWh: "
           f"{33.7 * 24 * 3 * 50:,.0f} u",
           f"P21 alerts 50 a day for 30 days at 4 min: {50 * 30 * 4 / 60:.0f} h",
           f"P22 certificates 90 over 36 months, mean a month: {90 / 36:.1f}",
           f"P23 128-bit key against 12 letters/digits: "
           f"{128 - ot.entropy_bits(62, 12):.0f} bits more",
           f"P24 hosts a /27 zone can hold: {2 ** 5 - 2}",
           f"P25 break-even of 80,000 u controls against a 200,000 u event: "
           f"every {200_000 / 80_000:.1f} y",
           f"P26 nines of a firewall pair of 0.999: "
           f"{-math.log10((1 - 0.999) ** 2):.0f}"]
    out += more()
    emit("solutions", out)


def more() -> list[str]:
    """Answers of the exercises on the deeper rounds (P27-P42)."""
    return [
        f"P27 local accounts, 40 devices x 8 people: {40 * 8}",
        f"P28 images 500 GB at 0.5 Gbit/s: {500 / (0.5e9 / 8 * 3600 / 1e9):.1f} h",
        f"P29 sessions 60 a year, 1 in 5 forgotten, 45 d each: {60 * 0.2 * 45 * 24:,.0f} h",
        f"P30 same with a 2 h timeout: {60 * 0.2 * 2:.0f} h",
        f"P31 2 engineers, rights 150 h each instead of all year: "
        f"{(1 - 300 / (2 * 8760)) * 100:.1f} % less",
        f"P32 flag level, mean 12 and spread 4, 4 spreads: {12 + 4 * 4}",
        f"P33 recovery chain 2 + 1 + 3 + 5 + 1 h: {2 + 1 + 3 + 5 + 1} h",
        f"P34 notice 60 d, test 10 d, window 30 d (mean): {60 + 10 + 15} d",
        f"P35 sample of 100 logins, 3 % bad: "
        f"{(1 - 0.97 ** 100) * 100:.0f} % chance to find one",
        f"P36 sample for 95 % at 5 % bad: {math.ceil(math.log(0.05) / math.log(0.95))}",
        f"P37 residual 2 x 4 against 4 x 4: {ot.risk_score(2, 4)} from {ot.risk_score(4, 4)}",
        f"P38 indicator 9 of 12 backups tested: {9 / 12 * 100:.0f} %",
        f"P39 training 10 x 4 + 4 x 12 + 15 x 1 h: {10 * 4 + 4 * 12 + 15} h",
        f"P40 notices 3 a month, window 4 months: about {3 * 4 / 2:.0f} waiting on average",
        f"P41 ports 34 switches x 24: {34 * 24} settings to compare",
        f"P42 flat network vs zones, devices one PC reaches: {130} vs {0}",
        f"P43 expected loss, 300,000 u at 4 % a year: {300_000 * 0.04:,.0f} u",
        f"P44 same lowered to 1 % by a 7,000 u control: saves "
        f"{300_000 * 0.03:,.0f} u, worth it: {300_000 * 0.03 > 7000}",
        f"P45 conduits with unauthenticated field protocols, 4 of 8: {4 / 8 * 100:.0f} %",
        f"P46 tabletop findings closed 5 of 6: {5 / 6 * 100:.0f} %"]


if __name__ == "__main__":
    worked()
    solutions()
