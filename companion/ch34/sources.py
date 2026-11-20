"""Chapter 34 - instrumentation and control data of Plant P (teaching
values A-385 to A-392).

The one-line and auxiliary supplies of chapter 23 (D-027), the control
limits and the hypothetical service REQ-S01 of chapter 20 (D-024), the
protection instrument transformers of chapter 26, the battery containers
of chapter 19 and the fire areas of chapter 32. Instrument accuracies,
drifts, scan times, panel losses and failure rates are teaching values;
makers' data sheets, the design and the tests decide the real ones.
"""
from __future__ import annotations

import math

from companion.ch34 import common  # noqa: F401  (puts plantp on the path)

# [start: chain]
CHAIN = dict(             # POC voltage measurement for the PPC (A-385)
    u_nom_kv=132.0,
    vt_ratio=(132_000 / math.sqrt(3), 110 / math.sqrt(3)),
    vt_class_pct=0.5,     # ratio error limit of the VT class (teaching)
    tx_range_kv=(0.0, 150.0), tx_acc_pct_span=0.2,      # transducer -> 4-20 mA
    ai_bits=16, ai_full_ma=21.0, ai_acc_pct_fs=0.1,     # analogue input module
    filter_tau_s=0.5)
# [end: chain]

LOOP = dict(v_supply=24.0, v_min_tx=12.0, r_receiver=250.0)        # A-385
RTD = dict(t_winding=95.0, lead_m=50.0, area_mm2=0.75)              # A-385
CLOCK = dict(gps_us=1.0, drift_ppm=20.0)                             # A-386

PLC = dict(input_ms=20.0, scan_ms=50.0, output_ms=10.0, comms_ms=30.0,
           mtbf_h=150_000.0, mttr_h=8.0)                             # A-387

# Equipment whose signals make up the I/O list (A-388): name, count,
# AI, DI, DO per unit (hard-wired; turbines and inverters come by network)
EQUIPMENT = [
    ("132 kV line bay E1", 1, 3, 8, 2),
    ("main transformer T1/T2", 2, 4, 9, 2),
    ("132 kV bus and coupler", 1, 2, 6, 2),
    ("33 kV incomer", 2, 3, 7, 2),
    ("33 kV bus coupler", 1, 0, 5, 2),
    ("33 kV feeder (WS1-3, PVF1-3, BESS-A/B)", 8, 2, 6, 2),
    ("station-service transformer", 1, 1, 4, 1),
    ("110 V DC system", 1, 3, 6, 0),
    ("UPS", 1, 2, 4, 0),
    ("diesel generator", 1, 2, 8, 2),
    ("met station", 2, 6, 2, 0),
    ("fire panel interface", 1, 0, 12, 3),
    ("BESS container (summary)", 8, 2, 6, 1),
]

DC = dict(volts=110.0, ah=250.0, standing_a=40.0,                  # ch 23 (D-027)
          ups_kw=25.0, ups_min=60.0)
CONTROL_24V = [  # 24 V DC loads in the control building, W (A-389)
    ("plant controller PLC (redundant pair)", 120.0),
    ("remote I/O racks (3)", 150.0),
    ("network switches and firewall", 90.0),
    ("time server (GPS)", 20.0),
    ("protection IED auxiliaries (on 110 V, shown for reference)", 0.0),
    ("fire-interface relays", 25.0),
    ("transducers and loop supplies", 60.0)]

# Fire interface signals between the fire panel and the plant controller (A-390)
FIRE = [  # signal, direction, kind, failure state, who may reset
    ("fire alarm, any zone", "fire -> plant", "hardwired NC", "alarm", "fire panel"),
    ("fault / supervisory", "fire -> plant", "hardwired NC", "alarm", "fire panel"),
    ("BESS container fire, per container", "fire -> plant", "hardwired NC", "alarm",
     "fire panel"),
    ("HVAC shutdown command", "fire -> HVAC", "hardwired", "HVAC off", "fire panel"),
    ("PCS trip request", "fire -> PCS", "hardwired", "trip", "fire panel"),
    ("zone status and text", "fire -> plant", "serial, read-only", "stale flag", "n/a"),
    ("plant controller healthy", "plant -> fire", "hardwired NC", "alarm on fire panel",
     "n/a")]

SERVICE = dict(p_limit=(0.0, 100.0, 10.0),        # MW: range and largest step per minute
               q_set=(-33.0, 33.0, 10.0),          # Mvar
               v_set=(0.95, 1.05, 0.02),           # pu
               stale_s=10.0, hold_s=3600.0)        # ch 20 comms hold (A-391)
