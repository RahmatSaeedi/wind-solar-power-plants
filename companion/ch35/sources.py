"""Chapter 35 - SCADA and communications data of Plant P (teaching values
A-393 to A-400).

Positions of the turbines (layout W2b, ch 14) and the site substation,
the I/O and control layers of chapter 34, the battery containers of
chapter 19 and the PV blocks of chapter 10. Link rates, latencies, tag
counts, failure rates and the asset-register extract are teaching values;
all data in the lab are synthetic and nothing connects to a live plant.
"""
from __future__ import annotations

import numpy as np

from companion.ch35 import common  # noqa: F401  (puts plantp on the path)
from companion.ch33 import sources as s33

TURBINES = np.asarray(s33.TURBINES)                 # 12 x (x, y) m
SUBSTATION = (6500.0, 3500.0)                        # site substation (ch 14)
ROUTE_FACTOR = 1.2                                   # cable route vs straight line
RINGS = {"ring W-east (T07-T12)": list(range(6, 12)),
         "ring W-west (T01-T06)": list(range(0, 6))}

# [start: traffic]
TRAFFIC = [  # source, devices, tags each, period s, bytes a tag (A-393)
    ("wind turbines", 12, 600, 1.0, 20),
    ("PV inverters", 26, 250, 1.0, 20),
    ("battery containers (S1)", 8, 1200, 1.0, 20),
    ("met stations", 2, 40, 1.0, 20),
    ("substation IEDs", 30, 150, 1.0, 20)]
# [end: traffic]

LINKS = dict(ring_bps=1e9, edge_bps=100e6, serial_bps=9600, wan_bps=2e6)   # A-394

SERIAL = dict(meters=30, request_b=8, reply_b=45, turnaround_ms=15.0)     # A-394

AVAIL = dict(link_mtbf_h=150_000.0, link_mttr_h=24.0,                    # A-395
             switch_mtbf_h=250_000.0, switch_mttr_h=4.0)

SYNC = [  # contribution, microseconds (teaching, A-396)
    ("satellite receiver", 0.1), ("grandmaster clock", 0.05),
    ("6 switches, residence-time correction", 6 * 0.05),
    ("end device time-stamping", 1.0)]

# Asset register extract and SCADA tag list, with planted mismatches (A-399)
ASSETS = [  # asset ID, description, SCADA tag prefix
    ("PLP-WTG-T01", "wind turbine T01", "PLP-WTG-T01"),
    ("PLP-WTG-T02", "wind turbine T02", "PLP-WTG-T02"),
    ("PLP-PVI-B01-I1", "PV inverter block 1", "PLP-PVI-B01-I1"),
    ("PLP-BES-C01", "battery container 1", "PLP-BES-C1"),
    ("PLP-TRF-T1", "main transformer T1", "PLP-TRF-T1"),
    ("PLP-TRF-T2", "main transformer T2", None),
    ("PLP-MET-M1", "met station 1", "PLP-MET-M1")]
