"""Chapter 35, second deeper round: bursts and back-fill, a backup radio
link budget, protocol overhead and batching, queueing delay against link
load, a float32 energy counter, word order of a 32-bit value across two
registers, an alarm flood with consequence suppression, the recovery
point of the SCADA servers, clock holdover, and functional location
against equipment in the asset register.

Run from the project root:   python -m companion.ch35.examples_n
Writes companion/ch35/expected/n_*.txt and diagrams/data/ch35-*.csv.
Teaching values and synthetic data (A-393 to A-399).
"""
from __future__ import annotations

import math
import struct

import numpy as np

from companion.ch35.common import csv, emit


def bursts() -> None:
    tags, b = 22_300, 20
    gi_bytes = tags * b
    lines = ["a general interrogation and a historian back-fill (teaching)",
             f"  every tag answers at once: {gi_bytes / 1e3:,.0f} kB",
             f"    on a 100 Mbit/s edge link: {gi_bytes * 8 / 100e6 * 1000:.1f} ms",
             f"    on the 2 Mbit/s WAN link:  {gi_bytes * 8 / 2e6:.2f} s"]
    day = 2000 * 86400 * b
    full = day * 8 / 100e6 / 60
    lines += [f"  back-fill of a day, 2,000 tags at 1 s: {day / 1e9:.1f} GB",
              f"    at the full 100 Mbit/s: {full:.1f} min - and nothing else gets",
              "    through meanwhile",
              f"    limited to 10 % of the link: {full * 10:.0f} min, live data unharmed",
              "  bursts are what fill links; a back-fill and a general",
              "  interrogation are rate-limited and scheduled, and the WAN",
              "  link carries only the agreed telemetry list, never a",
              "  general interrogation of the whole plant"]
    emit("n_bursts", lines)


def radio() -> None:
    d_km, f_mhz = 5.0, 5800.0
    fspl = 20 * math.log10(d_km) + 20 * math.log10(f_mhz) + 32.44
    tx, ant, cable, sens = 20.0, 23.0, 2.0, -80.0     # dBm, dBi each, dB, dBm
    rx = tx + 2 * ant - fspl - cable
    fresnel = 17.32 * math.sqrt((d_km / 2) * (d_km / 2) / ((f_mhz / 1000) * d_km))
    lines = ["backup radio to a met mast 5 km away at 5.8 GHz (teaching values)",
             f"  free-space loss {fspl:.1f} dB",
             f"  received {tx:.0f} + 2 x {ant:.0f} - {fspl:.1f} - {cable:.0f} = {rx:.1f} dBm",
             f"  against a sensitivity of {sens:.0f} dBm: fade margin {rx - sens:.1f} dB",
             f"  first Fresnel zone at mid-path: radius {fresnel:.1f} m - kept",
             "    clear of the ground, the trees and the turbine blades",
             "  rain, dust and a mast that moves in wind eat the margin;",
             "  the link is a backup, sized with margin and tested by",
             "  switching to it, and its licence is the operator's to get"]
    emit("n_radio", lines)


def overhead() -> None:
    head = 18 + 20 + 20 + 8                      # Ethernet, IP, TCP, application
    value = 20
    single = head + value
    rows = []
    lines = ["protocol overhead: one value a frame or many (teaching headers)",
             f"  headers {head} bytes a frame; a value {value} bytes",
             "  values a frame   bytes a value   efficiency"]
    for n in (1, 5, 20, 50):
        per = (head + n * value) / n
        rows.append((n, round(per, 1)))
        lines.append(f"  {n:16d}   {per:13.1f}   {value / per * 100:9.0f} %")
    lines += [f"  sending each value alone costs {single / ((head + 50 * value) / 50):.1f}"
              " times the bytes",
              "  of sending fifty together; report-by-exception sends few",
              "  values a frame, so its saving is smaller than the count of",
              "  messages suggests - the traffic estimate of lesson A",
              "  counts bytes on the wire, headers included"]
    emit("n_overhead", lines)


def queueing() -> None:
    service_ms = 0.12                             # a 1,500-byte frame at 100 Mbit/s
    lines = ["waiting time in a switch port against its load (M/M/1, teaching)",
             "  load %   mean wait ms   x the frame time"]
    rows = []
    for rho in (0.04, 0.3, 0.7, 0.9, 0.99):
        w = rho / (1 - rho) * service_ms
        rows.append((rho, round(w, 4)))
        lines.append(f"  {rho * 100:6.0f}   {w:12.3f}   {w / service_ms:16.1f}")
    for r in np.linspace(0.0, 0.98, 50):
        rows.append((round(float(r), 3), round(float(r / (1 - r) * service_ms), 4)))
    csv("ch35-queue.csv", "rho,w", sorted(r for r in set(rows) if r[0] <= 0.98))
    lines += ["  at the plant's 4 % the wait is nothing; it grows without",
              "  limit as the load nears 100 % - a link sized for the",
              "  average sits near the knee in every burst, which is why",
              "  links get headroom and control traffic gets priority"]
    emit("n_queue", lines)


def float_counter() -> None:
    def ulp(x: float) -> float:
        return 2.0 ** (math.floor(math.log2(x)) - 23)
    step = 100.0 / 60 * 1000                      # kWh a minute at 100 MW
    lines = ["an energy counter in kWh held as a 32-bit float (teaching)",
             "  year   counter kWh       resolution kWh   one-minute step kWh"]
    for yr in (1, 5, 25):
        x = 295.1e6 * yr
        lines.append(f"  {yr:4d}   {x:15,.0f}   {ulp(x):14,.0f}   {step:19,.0f}")
    acc = np.float32(295.1e6 * 25)
    true = 0.0
    for _ in range(600):                           # ten hours at 100 MW
        acc = np.float32(acc + np.float32(step))
        true += step
    got = float(acc) - 295.1e6 * 25
    lines += [f"  ten hours at 100 MW added in year 25: true {true:,.0f} kWh,"
              f" counted {got:,.0f}",
              f"    error {(got - true) / true * 100:+.1f} %",
              "  a float keeps about seven digits: a growing counter",
              "  loses its small steps first; energy counters are 32- or",
              "  64-bit integers in Wh or kWh, and floats are kept for",
              "  measurements, not for sums that grow for 25 years"]
    emit("n_float", lines)


def word_order() -> None:
    value = 295_100                               # MWh, one year of energy
    hi, lo = value >> 16, value & 0xFFFF
    swapped = (lo << 16) | hi
    f = struct.unpack(">f", struct.pack(">f", 132.1))[0]
    w = struct.pack(">f", 132.1)
    f_sw = struct.unpack(">f", w[2:] + w[:2])[0]
    lines = ["a 32-bit value carried in two 16-bit registers (teaching)",
             f"  energy {value:,} MWh: high word {hi}, low word {lo:,}",
             f"  read with the words swapped: {swapped:,} MWh",
             f"  the float 132.1 kV read with the words swapped: {f_sw:.3e}",
             f"    (true {f:.1f})",
             "  a protocol moves words; which word comes first is a",
             "  device setting the register map must state. Both errors",
             "  here are absurd and a range check catches them, but a",
             "  counter below 65,536 has a high word of 0 and reads",
             "  right until the day it passes it - so the point-to-point",
             "  test uses a known value with both words non-zero"]
    emit("n_words", lines)


def flood(seed: int = 357) -> None:
    rng = np.random.default_rng(seed)
    normal = rng.poisson(2.0, 24)                 # alarms an hour on a normal day
    fault_hour, fault_alarms = 14, 150            # one 33 kV feeder trip
    consequence = 138                             # of them consequences of the trip
    raw = normal.copy()
    raw[fault_hour] += fault_alarms
    supp = normal.copy()
    supp[fault_hour] += fault_alarms - consequence
    csv("ch35-flood.csv", "h,raw,supp", [(h, int(raw[h]), int(supp[h])) for h in range(24)])
    lines = ["an alarm flood after a feeder trip (synthetic day)",
             f"  normal hours: {normal.mean():.1f} alarms an hour on average",
             f"  hour of the trip, raw: {raw[fault_hour]} alarms",
             f"  with consequence alarms suppressed by the feeder state:"
             f" {supp[fault_hour]}",
             "  the trip of one feeder raises every inverter, transformer",
             "  and communication alarm behind it; suppressing what follows",
             "  from a known state leaves the first cause and what needs",
             "  action - each suppression is designed, documented and",
             "  tested like an alarm, and shelved alarms are listed"]
    emit("n_flood", lines)


def recovery_point() -> None:
    fail_per_year = 0.5                           # server losses needing a restore
    lines = ["what a server loss costs in data (teaching)",
             "  method                      data lost a time   restore h"]
    rows = [("daily backup", 12.0, 8.0), ("hourly snapshots", 0.5, 4.0),
            ("replicated pair", 0.0, 0.1)]
    for name, lost_h, restore in rows:
        lines.append(f"  {name:27s} {lost_h:13.1f} h   {restore:9.1f}")
    lines += [f"  with {fail_per_year} losses a year, a daily backup loses about"
              f" {fail_per_year * 12:.0f} h",
              "    of data a year on average",
              "  the recovery point (how much data may be lost) and the",
              "  recovery time (how long the restore takes) are set as",
              "  requirements; buffers at the source (lesson C) refill",
              "  most of the gap, and a restore is tested, not assumed"]
    emit("n_rpo", lines)


def holdover() -> None:
    need_s = 1e-3                                 # sequence of events
    lines = ["the grandmaster loses its satellite fix: holdover (teaching)",
             "  oscillator                  drift   time to drift 1 ms"]
    for name, ppb in (("temperature-compensated", 1000.0), ("oven-controlled", 10.0),
                      ("rubidium", 0.1)):
        t = need_s / (ppb * 1e-9)
        lines.append(f"  {name:27s} {ppb:5g} ppb   {t / 3600:12.1f} h")
    lines += ["  a lost fix is an alarm; the holdover time of the chosen",
              "  oscillator must cover the repair of the receiver or its",
              "  antenna, and the time stamps carry the 'synchronised'",
              "  flag until the drift could exceed the need"]
    emit("n_holdover", lines)


def location_vs_equipment() -> None:
    t07, swap_at, in_t03 = 42_000, 27_000, 20_000
    lines = ["functional location against equipment (synthetic history)",
             f"  turbine T07 has run {t07:,} h; at {swap_at:,} h its gearbox was",
             f"  replaced by G-4471, which had run {in_t03:,} h in turbine T03",
             f"  location 'T07 gearbox':   {t07:,} h of turbine operation",
             f"  equipment G-4471:          {in_t03 + t07 - swap_at:,} h of its own"
             f" ({in_t03:,} in T03",
             f"    + {t07 - swap_at:,} in T07)",
             f"  the gearbox removed from T07 took its {swap_at:,} h with it",
             "    to the workshop",
             "  SCADA counts hours at a LOCATION (the turbine); the",
             "  maintenance plan and the warranty need hours of the",
             "  EQUIPMENT (the serial number); the asset register links",
             "  the two with dates of installation and removal, and the",
             "  interface sends location hours that the register turns",
             "  into equipment hours"]
    emit("n_location", lines)


if __name__ == "__main__":
    bursts()
    radio()
    overhead()
    queueing()
    float_counter()
    word_order()
    flood()
    recovery_point()
    holdover()
    location_vs_equipment()
