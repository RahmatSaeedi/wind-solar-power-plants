"""Chapter 33 - environmental and social data of Plant P (teaching values
A-376 to A-384).

The fictional site of chapter 14 (layout W2b, PV block, dwellings,
village, spring, nest, cemetery, ruin, tenure), the labour curve of
chapter 22, the water of chapter 29, the logistics of chapter 31 and the
safety records of chapter 32. Noise, bird, bat, water and lifecycle
numbers are teaching values; studies, permits and affected people decide
the real ones (U-112 to U-114).
"""
from __future__ import annotations

import numpy as np

from companion.ch33 import common  # noqa: F401  (puts plantp on the path)
from companion.ch14 import lab_d as l14
from companion.ch14 import sources as s14

TURBINES = np.asarray(l14.layouts()["W2b plain, adjusted"], float)   # 12 x (x, y) m
HUB, TIP = s14.HUB, s14.TIP
DWELLINGS = dict(s14.DWELLINGS)
VILLAGE_CENTRE = (7600.0, 6250.0)
SPRING, NEST, CEMETERY, RUIN = s14.SPRING, s14.NEST, s14.CEMETERY, s14.RUIN
PV_BLOCK = s14.PV_BLOCK

# [start: noise]
NOISE = dict(lw_turbine=106.0,          # dB(A), maker's apparent sound power (teaching)
             night_limit=40.0,          # dB(A), PLACEHOLDER of the permit (U-112)
             background=28.0,           # dB(A), quiet desert night (survey to confirm)
             alpha_db_km=2.0)
# [end: noise]

BIRDS = dict(passages_at_nest=6000.0,   # raptor flights a year within 500 m of the nest
             decay_m=900.0,             # passages fall with distance from the nest
             p_collision=0.08, avoidance=0.98)

BATS = dict(months=(7, 8, 9, 10), night=(19, 6), cut_in=6.0, reduction=0.5)

LAND_USE = {   # area the project takes, ha (ch 14 f_exposure, construction areas ch 29)
    "PV block (fenced)": 119.0, "roads and pads": 18.7, "substation and BESS": 2.5,
    "laydown (temporary)": 6.0, "export line towers": 0.6}

HERDERS = dict(households=5, animals=600, grazing_ha=780.0, route_to_spring_km=1.2,
               detour_km=3.5, income_per_animal=0.12)      # k u a year (teaching)

LCA = {   # teaching factors, kg CO2e per unit; cov of the factor (A-383)
    "PV modules (kWp)": (60_000.0, 450.0, 0.30),
    "inverters and transformers (kW)": (50_000.0, 45.0, 0.40),
    "PV structures, steel (t)": (2_900.0, 2_000.0, 0.20),
    "turbines excl. tower (MW)": (60.0, 300_000.0, 0.30),
    "towers, steel (t)": (12 * 372.0, 2_000.0, 0.20),
    "foundations, concrete (m3)": (12 * 893.0, 300.0, 0.25),
    "rebar (t)": (12 * 89.0, 1_900.0, 0.20),
    "cables, aluminium (t)": (450.0, 9_000.0, 0.30),
    "cables, copper (t)": (60.0, 4_000.0, 0.30),
    "transport, sea and road (t km x 1e3)": (40_000.0, 25.0, 0.40),
    "construction diesel (m3)": (900.0, 2_700.0, 0.10),
}
BESS_LCA = {"battery system (kWh)": (40_000.0, 90.0, 0.40),
            "augmentation (kWh)": (8_000.0, 90.0, 0.40)}
OPERATION = dict(own_use_mwh=2_340.0, grid_factor=0.5, diesel_m3_year=8.0,
                 replacements_share=0.08, eol_credit_share=-0.05)
ENERGY_GWH = dict(S0=295.1, S1=293.5)       # P50 at the POC (ch 15 D-019; S1 losses, ch 19)
LIFE_YEARS = 25
