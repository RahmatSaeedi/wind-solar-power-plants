"""Chapter 35, lesson A: the plant network in numbers - media against
distance, the fibre loss budget of the turbine rings, the traffic and
how much of each link it uses, a legacy serial line polled against
report-by-exception, the latency of a path, chain against ring
availability, the time-synchronisation budget, and subnets.

Run from the project root:   python -m companion.ch35.examples_a
Writes companion/ch35/expected/a_*.txt and diagrams/data/ch35-traffic.csv.
Teaching values (A-393 to A-396); synthetic, nothing connects to a plant.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch35 import sources as src
from companion.ch35.common import csv, emit
from plantp import instrumentation as ic
from plantp import scada as sc


def ring_length_km(idx) -> float:
    t = src.TURBINES[idx]
    s = np.array(src.SUBSTATION)
    path = np.hypot(*(t[0] - s)) + np.sum(np.hypot(*np.diff(t, axis=0).T)) + np.hypot(*(t[-1] - s))
    return float(path) * src.ROUTE_FACTOR / 1000


def media() -> None:
    rows = [("copper Ethernet (twisted pair)", "100 m", "inside buildings, cabinets"),
            ("multimode fibre", "about 0.5-2 km", "inside the substation"),
            ("single-mode fibre", "10-40 km and more", "turbine rings, line"),
            ("radio link", "line of sight", "backup, remote met mast"),
            ("serial RS-485 (copper)", "about 1 km", "legacy meters, slow")]
    far = max(np.hypot(*(src.TURBINES - np.array(src.SUBSTATION)).T)) * src.ROUTE_FACTOR
    lines = ["media for the plant network and how far each reaches (teaching)",
             "  medium                          reach                use at Plant P"]
    for m, r, u in rows:
        lines.append(f"  {m:31s} {r:20s} {u}")
    lines += [f"  the farthest turbine is about {far / 1000:.1f} km of cable route away:",
              "  single-mode fibre, laid in the collector-cable trench,",
              "  immune to the fields of a 33 kV fault next to it - copper",
              "  between buildings would carry the earth-potential rise",
              "  of a fault from one earth mat to another (ch 26)"]
    emit("a_media", lines)


def fibre() -> None:
    lines = ["fibre loss budget of the turbine rings (teaching losses, 10 dB optics)",
             "  ring                       km   splices   loss + 3 dB margin   fits?"]
    over = []
    for name, idx in src.RINGS.items():
        km = ring_length_km(idx)
        splices = math.ceil(km / 2) + 2 * len(idx)
        loss = sc.fibre_budget_db(km, splices, 4)
        if loss > 10:
            over.append((name, loss))
        lines.append(f"  {name:24s} {km:5.1f}   {splices:7d}   {loss:18.1f}"
                     f"   {'yes' if loss <= 10 else 'NO'}")
    for name, loss in over:
        lines.append(f"  {name} exceeds the 10 dB optics by {loss - 10:.1f} dB:")
        lines.append("    longer-reach optics or a switch midway, decided before")
        lines.append("    the fibre is ordered")
    lines += ["  the budget is checked for the whole ring, because when one",
              "  span is cut the farthest turbine is reached the long way",
              "  round; the 3 dB margin covers repair splices and ageing,",
              "  and the as-built loss of each span is measured (lesson C)"]
    emit("a_fibre", lines)


def traffic() -> None:
    rows, total = [], 0.0
    lines = ["steady SCADA traffic of Plant P (teaching tag counts, 1 s cycle)",
             "  source                      devices   tags   Mbit/s"]
    for k, (name, n, tags, per, b) in enumerate(src.TRAFFIC, 1):
        mbps = n * tags / per * b * 8 / 1e6
        total += mbps
        rows.append((k, round(mbps, 2)))
        lines.append(f"  {name:27s} {n:7d}   {tags:4d}   {mbps:6.2f}")
    csv("ch35-traffic.csv", "k,mbps", rows)
    lines += [f"  total {total:.1f} Mbit/s: {total / 100 * 100:.0f} % of a 100 Mbit/s edge link,",
              f"    {total / 1000 * 100:.1f} % of the 1 Gbit/s ring",
              "  the average is small; what loads a network is bursts -",
              "  every device answering a general interrogation at once,",
              "  or a historian back-filling a day - which is why links",
              "  are sized with headroom and bursts are rate-limited"]
    emit("a_traffic", lines)


def serial() -> None:
    s = src.SERIAL
    cyc = sc.polling_cycle_s(s["meters"], s["request_b"], s["reply_b"],
                             src.LINKS["serial_bps"], s["turnaround_ms"])
    rbe = sc.rbe_rate(s["meters"] * 10, 6)
    lines = ["30 legacy meters on one RS-485 line at 9600 bit/s (teaching)",
             f"  one poll: {s['request_b']} + {s['reply_b']} bytes + {s['turnaround_ms']:.0f} ms"
             f" turnaround; full cycle {cyc:.2f} s",
             f"  each value is up to {cyc:.1f} s old when read - fine for energy,",
             "  too slow for control",
             f"  on Ethernet with report-by-exception (10 values a meter,",
             f"  6 changes an hour each): {rbe:.2f} messages a second",
             "  polling asks everyone all the time; report-by-exception",
             "  sends only changes, with a periodic integrity scan so a",
             "  silent device is noticed (lesson C, loss of comms)"]
    emit("a_serial", lines)


def latency() -> None:
    hops, km = 6, 6.0
    parts = [("6 switches x 10 us", hops * 0.010),
             (f"{km:.0f} km of fibre at 5 us/km", km * 0.005),
             ("1500-byte frame at 100 Mbit/s", sc.serialisation_ms(1500, 100e6)),
             ("controller processing", 5.0),
             ("WAN link to the control centre (2 Mbit/s)", 40.0)]
    lines = ["latency of a message from a turbine to the control centre (teaching)",
             "  part                                          ms"]
    for name, ms in parts:
        lines.append(f"  {name:45s} {ms:7.3f}")
    total = sum(ms for _, ms in parts)
    lines += [f"  total {total:.1f} ms - inside the plant the network adds well",
              "  under a millisecond; the WAN link and the processing",
              "  set the delay, which is why the plant controller sits",
              "  in the plant and the grid operator sends set points, not",
              "  loop signals (ch 34, telemetry budget)"]
    emit("a_latency", lines)


def topology() -> None:
    a = src.AVAIL
    a_link = ic.availability(a["link_mtbf_h"], a["link_mttr_h"])
    n = 6
    chain_far = a_link ** n
    ring_mid = sc.ring_device_availability(a_link, n)
    lines = ["six turbines on a daisy chain or on a ring (teaching link rates)",
             f"  one link (fibre span + its two ports): A = {a_link:.6f}",
             f"  chain, farthest turbine (6 links in series): {(1 - chain_far) * 8760:.2f} h a year cut off",
             f"  ring, worst-placed turbine: {(1 - ring_mid) * 8760 * 3600:.1f} s a year cut off",
             "  a ring costs one more fibre span and turns hours into",
             "  seconds; it still needs a ring protocol that reopens the",
             "  blocked port within the plant's tolerance (lesson C),",
             "  and two rings so one cut trench does not take all"]
    emit("a_topology", lines)


def sync() -> None:
    total = sc.sync_budget_us([u for _, u in src.SYNC])
    lines = ["time-synchronisation error budget of the precision time protocol",
             "  contribution                                      us"]
    for name, u in src.SYNC:
        lines.append(f"  {name:47s} {u:6.2f}")
    lines += [f"  worst-case sum {total:.2f} us",
              "  need                                   accuracy   met?",
              f"  sequence of events (ch 34)             1 ms       {'yes' if total < 1000 else 'NO'}",
              f"  synchrophasor-class measurement        1 us       {'yes' if total < 1 else 'NO'}",
              "  the end device's own time-stamping takes most of the",
              "  budget: the chain as drawn serves events with room to",
              "  spare but misses a 1 us need, which would ask for better",
              "  end devices, not a better network; the network time",
              "  protocol (about a millisecond) would also serve events -",
              "  the need, not the fashion, chooses the method (STD-150)"]
    emit("a_sync", lines)


def subnets() -> None:
    rows = [("substation IEDs", 30), ("turbines and ring switches", 24),
            ("PV inverters and stations", 40), ("battery containers", 24),
            ("control room servers and HMIs", 12)]
    lines = ["subnets by function (teaching): smallest prefix that fits with 50 % growth",
             "  zone                              devices   prefix   addresses usable"]
    for name, n in rows:
        need = math.ceil(n * 1.5) + 2
        p = 32 - math.ceil(math.log2(need))
        lines.append(f"  {name:33s} {n:7d}   /{p:<5d}  {2 ** (32 - p) - 2:16d}")
    lines += ["  one subnet a function keeps broadcast traffic local and",
              "  lets the firewall rules of ch 36 speak in zones, not in",
              "  hundreds of single addresses; the address plan is a",
              "  controlled document like the I/O list (ch 34)"]
    emit("a_subnets", lines)


if __name__ == "__main__":
    media()
    fibre()
    traffic()
    serial()
    latency()
    topology()
    sync()
    subnets()
