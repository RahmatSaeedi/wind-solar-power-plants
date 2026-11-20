"""Chapter 22 - three fictional candidate sites for Plant P (teaching
values, A-311 to A-314): P-Central is the site of chapters 13-21;
P-North and P-South are invented alternatives. No real place, community
or person is described.

Each site lists resource, land, grid, environment, social, permitting,
logistics, cost, schedule and constructability facts, with the quality
of the evidence behind each (0 = guess, 1 = measured and reviewed).
Money in k u.

The comparison is made at month 14 of P-Central's development plan
(examples_c): `schedule` counts months from that review to COD, i.e.
the development still to do + financing + building. P-Central has 14
months to financial close and 18 to build; the others start from
scratch. `permit_months` is the whole permitting time from its start.
"""
from __future__ import annotations

from companion.ch22 import common  # noqa: F401  (puts plantp on the path)

# [start: sites]
SITES = {
    "P-North": dict(
        energy=330.0, energy_q=0.4,      # GWh P50; reanalysis + 4-month mast
        capex=150_000.0 + 6_000.0,           # plant + 18 km new road
        grid_km=45.0, grid_free_mw=0.0, reinforce=25_000.0, grid_wait=30,
        land_ha=2_400.0, tenure="customary, many holders", households=38,
        displaced=6, grazing_ha=900.0,
        bird_overlap=0.35, heritage=1, water_scarce=False,
        permit_months=30, road_km=18.0, slope_pct=9.0,
        schedule=54),                        # 30 permits + 6 close + 18 build
    "P-Central": dict(
        energy=295.14, energy_q=0.9,         # D-019: mast, lidar, station
        capex=156_450.0,
        grid_km=12.0, grid_free_mw=100.0, reinforce=0.0, grid_wait=12,
        land_ha=1_900.0, tenure="state lease, two private parcels",
        households=9,
        displaced=0, grazing_ha=250.0,
        bird_overlap=0.0, heritage=0, water_scarce=False,
        permit_months=22, road_km=4.0, slope_pct=4.0,
        schedule=32),                        # 14 to close + 18 build
    "P-South": dict(
        energy=262.0, energy_q=0.7,          # after a 70 MW weak-grid limit
        capex=145_000.0 + 1_500.0,           # more PV, water storage
        grid_km=3.0, grid_free_mw=70.0, reinforce=0.0, grid_wait=9,
        land_ha=1_600.0, tenure="state land, clear title", households=2,
        displaced=0, grazing_ha=60.0, seasonal=40,
        bird_overlap=0.0, heritage=2, water_scarce=True,
        permit_months=20, road_km=2.0, slope_pct=2.0,
        schedule=42),                        # 20 permits + 6 close + 16 build
}
for _s in SITES.values():
    _s.setdefault("seasonal", 0)             # seasonal land users (herders)
# [end: sites]

OPEX = 4_270.0                     # k u a year, ch 21 (A-305)
TARIFF = 70.0                      # u/MWh, ch 21 (A-307)
