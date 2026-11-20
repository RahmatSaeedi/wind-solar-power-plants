"""Chapter 53 sources: Plant P at its operating year 18 (teaching), with the
records of chapters 37, 51 and 52 and the bases D-012 to D-056.
All values are synthetic teaching values (A-538 to A-545).

Units: years, MWh, MW, k u (thousand currency units), t (tonnes).
"""
from __future__ import annotations

YEAR_NOW = 18
LIFE = 25                         # design life (ch 21, ch 33)
PPA_YEARS = 20                    # PPA term (ch 21)
PRICE = 70.0                      # u/MWh in the PPA, 45 after it (ch 21 A-307)
PRICE_AFTER = 45.0
RATE = 0.075                      # WACC (ch 21)

# ------------------------------------------------ A. lifecycle performance (A-538)
PV_PR = [81.6, 81.4, 81.0, 80.9, 80.4, 80.3, 79.8, 79.9, 79.2, 79.0, 78.9, 78.3,
         78.1, 77.9, 77.4, 77.2, 76.8, 76.6]                       # PR % by year 1..18
WIND_AVAIL = [96.4, 97.2, 97.5, 97.6, 97.3, 97.4, 97.0, 96.8, 96.9, 96.3, 96.1, 95.8,
              95.9, 95.2, 95.0, 94.6, 94.4, 93.9]                   # energy availability %
LOST_BY_CAUSE = {"turbine major components": 2_950.0, "turbine minor": 1_610.0,
                 "inverters": 980.0, "grid curtailment": 2_200.0, "soiling": 1_150.0,
                 "transformers and line": 420.0}                   # MWh in year 18
BENCH = {"Plant P": (93.9, 76.6), "peer A": (96.2, 79.5), "peer B": (95.1, 78.0),
         "peer C": (97.0, 80.1)}                                    # wind avail %, PV PR %

# ------------------------------------------------ B. repair / upgrade / repower (A-539)
INVERTER = dict(units=10, mw=5.0, failures_yr=[0.5, 0.6, 0.7, 0.9, 1.2, 1.6],   # years 13-18
                repair_k=45.0, mttr_h=96.0, replace_k=420.0, eta_old=0.978, eta_new=0.986,
                supported_until=21)
GEARBOX = dict(units=12, k=2.5, c=150_000.0, hours=18 * 8_760 * 0.93,
               repair_k=380.0, replace_k=620.0, down_repair_h=900.0, down_replace_h=700.0,
               life_after_repair=0.6)      # repair restores 60 % of a new life (teaching)
REPOWER = dict(old_mw=5.0, new_mw=6.2, old_rotor=150.0, new_rotor=170.0,
               cp_gain=0.04, capex_k_per_mw=1_150.0, export_limit=100.0)

# ------------------------------------------------ C. decommissioning (A-540)
MATERIALS = {   # material: (tonnes, share recycled, share reused, hazardous?)
    "tower steel (weighed, ch 47)": (12 * 411.0, 0.95, 0.0, False),
    "nacelles and drivetrains": (12 * 165.0, 0.85, 0.05, False),
    "blades (composite)": (12 * 3 * 21.0, 0.30, 0.10, False),
    "foundation concrete (top 1 m)": (12 * 180.0 * 2.4, 0.80, 0.0, False),
    "PV modules": (109_200 * 0.0281, 0.85, 0.05, False),
    "PV structures, steel": (2_900.0, 0.95, 0.0, False),
    "cables (Al, Cu)": (510.0, 0.90, 0.0, False),
    "transformer oil": (12 * 2.0 + 2 * 18.0 + 10 * 2.5, 0.60, 0.0, True),
    "battery modules": (8 * 30.0, 0.65, 0.10, True),
    "gearbox and hydraulic oil": (12 * 1.2, 0.60, 0.0, True)}
DECOM_COST = 4_000.0              # k u, year-1 money (ch 21 A-306)
SALVAGE = 1_500.0
INFLATION = 0.025

# ------------------------------------------------ G. social closure (A-544)
COMMITMENTS_CLOSE = {   # commitment: (status at year 18, evidence on file)
    "land return to grazing (PV area)": ("planned", False),
    "road left to the village": ("agreed", True),
    "local hiring in decommissioning": ("not started", False),
    "grievance mechanism to the end": ("running", True),
    "restoration fund (bond)": ("partly funded", True),
    "heritage buffer kept during works": ("planned", False)}
WORKFORCE = dict(om_staff=46, local=15, years_left=7)

# ------------------------------------------------ H. information continuity (A-545)
RECORDS = {   # record set: (years to keep after closure, migrated to the successor?, size GB)
    "as-built drawings": (10, True, 42.0), "protection settings": (5, True, 0.4),
    "maintenance history (CMMS)": (10, False, 18.0), "SCADA history": (3, False, 2_400.0),
    "environmental monitoring": (15, True, 6.0), "land and commitments": (25, True, 1.2),
    "OT accounts and keys": (0, False, 0.01)}
