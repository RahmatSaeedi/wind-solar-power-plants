"""Chapter 31 - logistics data of Plant P (teaching values A-363 to A-367).

Components of the WT-5.0-150 (ch 11 masses, ch 30 tower sections), the
main transformer (ch 25), a fictional port-to-site route with bridges, a
low wire and tight turns, a teaching crawler-crane load chart, and the
lift wind limits. Real values come from the makers' transport and
lifting instructions, the crane's own charts and the route permit.
"""
from __future__ import annotations

from companion.ch31 import common  # noqa: F401  (puts plantp on the path)

# [start: components]
COMPONENTS = {   # mass t, length m, width m, height m, loads a turbine (A-363)
    "blade": (22.0, 74.0, 4.2, 3.0, 3),
    "nacelle": (160.0, 14.0, 4.5, 4.3, 1),
    "hub": (45.0, 5.5, 4.8, 4.2, 1),
    "tower section 1": (124.0, 25.0, 4.5, 4.5, 1),
    "tower section 2": (96.0, 25.0, 4.12, 4.12, 1),
    "tower section 3": (71.0, 25.0, 3.75, 3.75, 1),
    "tower section 4": (50.0, 25.0, 3.38, 3.38, 1),
    "main transformer (oil out)": (72.0, 8.0, 3.6, 4.2, 0),
}
# [end: components]

ROUTE = [   # stretch, km, km/h for abnormal loads (A-364, fictional)
    ("port to ring road", 12.0, 25.0), ("highway", 180.0, 50.0),
    ("district road", 40.0, 30.0), ("village bypass", 6.0, 10.0),
    ("site track", 6.0, 10.0)]

BRIDGES = [   # name, span m, allowed moment kN m (A-364, fictional)
    ("river bridge", 32.0, 9_000.0), ("canal culvert-bridge", 12.0, 4_200.0),
    ("district overpass", 24.0, 6_500.0)]

LOW_POINTS = [("power line at km 205", 5.40), ("overpass at km 214", 4.85)]   # m clearance

CRANE_CHART = [   # radius m, capacity t at 112 m hook height (teaching crawler crane)
    (12.0, 250.0), (16.0, 210.0), (20.0, 178.0), (24.0, 150.0), (28.0, 128.0),
    (32.0, 110.0), (36.0, 95.0), (40.0, 82.0)]

WIND_LIMITS = {   # m/s at hub height, teaching maker values (A-365)
    "tower section": (12.0, 4), "nacelle": (10.0, 6), "rotor (hub + blades)": (8.0, 8),
    "single blade": (8.0, 4)}
