"""Chapter 35 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch35.worked
Writes companion/ch35/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch35.common import emit
from plantp import scada as sc


def worked() -> None:
    lines = [f"E01 1,500 bytes at 100 Mbit/s: {sc.serialisation_ms(1500, 100e6):.3f} ms",
             f"E02 200 messages/s of 100 bytes on 1 Mbit/s: {sc.utilisation(200, 100, 1e6) * 100:.0f} %",
             f"E03 10 meters, 8 + 25 bytes, 9600 bit/s, 10 ms: {sc.polling_cycle_s(10, 8, 25, 9600, 10):.2f} s",
             f"E04 fibre 5 km, 4 splices, 2 connectors: {sc.fibre_budget_db(5, 4, 2):.2f} dB",
             f"E05 hosts in a /26: {2 ** 6 - 2}",
             f"E06 3,600 points changing twice an hour: {sc.rbe_rate(3600, 2):.1f} messages/s",
             f"E07 availability 0.9999: {sc.nines(0.9999):.0f} nines"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 64 bytes at 9600 bit/s: {sc.serialisation_ms(64, 9600):.1f} ms",
           f"P02 9,000 bytes at 1 Gbit/s: {sc.serialisation_ms(9000, 1e9) * 1000:.0f} us",
           f"P03 12 turbines x 600 tags x 20 B per s: {12 * 600 * 20 * 8 / 1e6:.2f} Mbit/s",
           f"P04 that load on 100 Mbit/s: {sc.utilisation(12 * 600, 20, 100e6) * 100:.1f} %",
           f"P05 30 meters, 8 + 45 bytes, 9600 bit/s, 15 ms: "
           f"{sc.polling_cycle_s(30, 8, 45, 9600, 15):.2f} s",
           f"P06 same at 19200 bit/s: {sc.polling_cycle_s(30, 8, 45, 19200, 15):.2f} s",
           f"P07 fibre 11.5 km, 18 splices, 4 connectors: {sc.fibre_budget_db(11.5, 18, 4):.1f} dB",
           f"P08 fibre 9.2 km, 17 splices, 4 connectors: {sc.fibre_budget_db(9.2, 17, 4):.1f} dB",
           f"P09 chain of 6 links at 0.99984: {(1 - 0.99984 ** 6) * 8760:.1f} h a year",
           f"P10 ring, worst device, 7 links at 0.99984: "
           f"{(1 - sc.ring_device_availability(0.99984, 6)) * 8760 * 3600:.0f} s a year",
           f"P11 sync budget 0.1 + 0.05 + 0.3 + 1.0 us: {sc.sync_budget_us([0.1, 0.05, 0.3, 1.0]):.2f} us",
           f"P12 smallest prefix for 40 devices + 50 %: /{32 - math.ceil(math.log2(62))}",
           f"P13 16-bit counter at 808 MWh/day: {32767 / 808:.0f} days",
           f"P14 retention, 1,000 points at 1 s, 2 years: {sc.retention_gb(1000, 1, 2):,.0f} GB",
           f"P15 buffer, 2,000 tags, 20 B, 24 h: {2000 * 20 * 86400 / 1e9:.1f} GB",
           f"P16 queue, 40 messages/h for 72 h: {40 * 72:,} messages",
           f"P17 tag 'PLP-MET-M1-Ghi' valid: {sc.tag_ok('PLP-MET-M1-Ghi')}",
           f"P18 1,321 on 0-150 suspect: {sc.scaling_suspect(1321, 0, 150)}",
           f"P19 stale, last update 5 s, now 20 s, limit 10 s: {sc.stale([5.0], 20.0, 10.0)}",
           f"P20 local-time day with 25 hours: +{(25 / 24 - 1) * 100:.1f} %"]
    out += more_solutions()
    emit("solutions", out)


def more_solutions() -> list[str]:
    """Answers of the exercises on the deeper lessons (P21-P40)."""
    a = 0.99984
    ring9 = (1 - a ** 4) * (1 - a ** 5) * 8760 * 3600
    return [
        f"P21 worst age, 100 + 20 + 0.1 + 50 + 1000 + 1000 ms: {2170.1 / 1000:.2f} s",
        f"P22 200 devices in one flat network, 0.5 broadcasts/s each: {199 * 0.5:.1f}/s",
        f"P23 deadband 0.5 % of a 0-150 kV span: largest error {0.005 * 150:.2f} kV",
        f"P24 1 day at 1 s on 1,200 pixels, 10 s spike, decimated: "
        f"{10 / (86400 // 1200) * 100:.1f} % visible",
        f"P25 674.8 MWh with 3 % of minutes skipped: about {674.8 * 0.97:.1f} MWh",
        f"P26 usable addresses in a /27: {2 ** 5 - 2}",
        f"P27 fibre 25 km, 10 splices, 2 connectors: {sc.fibre_budget_db(25, 10, 2):.2f} dB",
        f"P28 ring of 9 links, worst device: {ring9:.0f} s a year",
        f"P29 4.5 Mbit/s sent twice (parallel networks): {4.5 * 2:.1f} Mbit/s",
        f"P30 30 meters, 8 + 45 bytes, 38400 bit/s, 15 ms: "
        f"{sc.polling_cycle_s(30, 8, 45, 38400, 15):.2f} s",
        f"P31 retention, 1,000 tags at 1 s, 1 year, 10 % kept: "
        f"{sc.retention_gb(1000, 1, 1, keep=0.1):.1f} GB",
        f"P32 32-bit unsigned counter at 808 MWh/day: {(2 ** 32 - 1) / 808 / 365:,.0f} years",
        f"P33 queue, 40 messages/h for 5 days, 2 kB each: {40 * 120:,} messages, "
        f"{40 * 120 * 2 / 1024:.1f} MB",
        f"P34 local-time day with 23 hours: {(23 / 24 - 1) * 100:.1f} %",
        f"P35 sync 0.1 + 0.05 + 10 x 0.05 + 0.5 us: "
        f"{sc.sync_budget_us([0.1, 0.05] + [0.05] * 10 + [0.5]):.2f} us",
        f"P36 9,000 bytes at 100 Mbit/s: {sc.serialisation_ms(9000, 100e6):.2f} ms",
        f"P37 chain, 4th turbine, links at 0.99984: {(1 - a ** 4) * 8760:.1f} h a year",
        f"P38 aggregates, 1,000 tags x 3 a minute, 25 years: "
        f"{sc.retention_gb(3000, 60, 25):.0f} GB",
        f"P39 nines of the worst ring device (7 links): "
        f"{sc.nines(sc.ring_device_availability(a, 6)):.1f}",
        f"P40 fire panel at 20 s a month, offset after 9 months: {20 * 9} s",
        *round_three()]


def round_three() -> list[str]:
    """Answers of the exercises on the second and third deeper rounds."""
    fspl = 20 * math.log10(10) + 20 * math.log10(5800) + 32.44
    f_mid = 17.32 * math.sqrt(5 * 5 / (5.8 * 10))
    ulp10 = 2.0 ** (math.floor(math.log2(295.1e6 * 10)) - 23)
    return [
        f"P41 22,300 tags x 20 B on 2 Mbit/s: {22300 * 20 * 8 / 2e6:.2f} s",
        f"P42 a day of 2,000 tags limited to 20 % of 100 Mbit/s: "
        f"{2000 * 86400 * 20 * 8 / 20e6 / 60:.0f} min",
        f"P43 mean wait at 80 % load, frame 0.12 ms: {0.8 / 0.2 * 0.12:.2f} ms",
        f"P44 1,000 frames ahead of a control message: {1000 * 0.12:.0f} ms",
        f"P45 bytes a value with 66 B headers, 10 values a frame: {(66 + 200) / 10:.1f}",
        f"P46 free-space loss, 10 km at 5.8 GHz: {fspl:.1f} dB",
        f"P47 first Fresnel radius at mid-path, 10 km, 5.8 GHz: {f_mid:.1f} m",
        f"P48 one carrier at 0.998: {(1 - 0.998) * 8760:.1f} h a year",
        f"P49 two independent carriers at 0.998: {(1 - 0.998) ** 2 * 8760 * 60:.1f} min a year",
        f"P50 float32 resolution of a 10-year kWh counter: {ulp10:.0f} kWh",
        f"P51 64-bit counter: largest Wh value about {2 ** 63 - 1:.2e}",
        f"P52 words 0 and 50,000 read swapped: {50000 * 65536:,}",
        f"P53 operator's time for 60 alarms at 45 s: {60 * 45 / 60:.0f} min",
        f"P54 daily backup, 0.3 losses a year: {0.3 * 12:.1f} h of data a year",
        f"P55 holdover at 50 ppb before 1 ms: {1e-3 / 50e-9 / 3600:.1f} h",
        f"P56 completeness, 12 h lost in a 30-day month: {(1 - 12 / 720) * 100:.2f} %",
        f"P57 3 % of 2,880 acknowledgements lost: {0.03 * 2880:.0f} repeats expected",
        f"P58 gearbox: 12,000 h in T05 + (30,000 - 18,000) h in T09: "
        f"{12000 + 30000 - 18000:,} h",
        f"P59 network FAT, 40 devices x 1 h + 6 h of system tests: {40 + 6} h",
        f"P60 server gap, detection 2 s + take-over 3 s: {2 + 3} s",
        f"P61 0.08 Hz sampled every 5 s: apparent {abs(0.08 - round(0.08 / 0.2) * 0.2):.2f} Hz",
        f"P62 longest sampling interval for 10 samples of a 0.5 Hz swing: {1 / 0.5 / 10:.1f} s",
        f"P63 30 points every 2 s, 25 B, on 64 kbit/s: {30 * 0.5 * 25 * 8 / 64e3 * 100:.1f} %",
        f"P64 20 TB mirrored with 25 % free: {20 * 2 / 0.75:.1f} TB raw",
        f"P65 zero-fault sample for 2 % at 95 %: "
        f"{math.ceil(math.log(0.05) / math.log(0.98))} points",
        f"P66 fault rate shown by 500 points without fault: "
        f"{(1 - 0.05 ** (1 / 500)) * 100:.2f} %"]


if __name__ == "__main__":
    worked()
    solutions()
