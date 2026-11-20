"""Chapter 32 - safety, fire and emergency data of Plant P (teaching values
A-368 to A-375).

Synthetic work hours and incidents for construction and operation, the
areas of the plant with their fire scenarios, placeholder detection and
response times, the workforce of chapter 29, and the water store of
chapters 18 and 29. Nothing here is a requirement: the project's safety
management system, the fire strategy, the authority having jurisdiction
and qualified specialists set the real values (U-105, U-110).
"""
from __future__ import annotations

from companion.ch32 import common  # noqa: F401  (puts plantp on the path)

HOURS = {   # worked hours and recorded events (synthetic, A-368)
    "construction (18 months)": dict(hours=1_050_000, lost_time=3, recordable=11,
                                      near_miss=164),
    "operation (year 1)": dict(hours=52_000, lost_time=0, recordable=1, near_miss=23)}

# [start: areas]
AREAS = {   # area: (fire scenario, typical detection, isolation, notes) (A-369)
    "BESS containers (8)": ("cell thermal runaway, off-gas, propagation",
                            "off-gas and smoke in container, BMS", "PCS and DC isolation"),
    "PV DC (combiners, cables)": ("arc fault, cable fire, grass fire",
                                  "inverter arc detection, patrols", "inverter shutdown"),
    "PV inverters / stations": ("electronics fire, transformer oil",
                                "station smoke detection, alarms", "MV switch, inverter stop"),
    "wind nacelles (12)": ("electrical or friction fire at height",
                           "nacelle smoke and heat, SCADA", "turbine stop, MV switch"),
    "main transformers (2)": ("oil fire after internal fault",
                              "Buchholz, protection trip, heat", "breakers both sides"),
    "control and MV buildings": ("cable and panel fire", "smoke detection (aspirating)",
                                 "local isolation, HVAC stop"),
    "construction areas": ("hot work, fuel, waste, vehicles", "fire watch, extinguishers",
                           "permit control"),
}
# [end: areas]

RESPONSE = dict(fire_service_km=35.0, speed_kmh=60.0, mobilise_min=8.0, access_min=10.0,
                site_team_min=6.0)                                       # placeholders (A-370)

WORKFORCE = dict(peak=450, worker_months=4534, local_share=0.40,       # ch 22 curve
                 km_to_town=35.0, l_day=70.0)                           # (A-374)

TANK = dict(volume_m3=2500.0, reserve_m3=180.0)                         # ch 18, ch 29 (U-105)
