"""Chapter 45 - teaching data for the manufacture of Plant P's S1 battery
(ch 19: LFP 314 Ah cells, 52 s modules, 8 modules a rack, 12 racks a
container, 8 containers, 4 PCS of 5 MW) by a fictional cell maker and a
fictional integrator. Illustrative values, not a maker's data, not a
recipe (A-474 to A-481).

CELL        the cell of ch 19 with its data-sheet limits (A-474)
DESIGN      electrode design concept: loading, active share, N/P (A-474)
lot()       formation and grading data of one lot with planted faults (A-475)
WELDS       busbar weld resistances of one module (A-476)
BMS         settings of the BMS configuration as delivered (A-477)
DEFECT      the fictional defect and its trail through the records (A-478)
MATERIALS   mass of one cell by material, for end of life (A-479)
"""
from __future__ import annotations

import numpy as np

from companion.ch45 import common  # noqa: F401  (puts plantp on the path)

# [start: cell]
CELL = dict(chem="LFP", q_ah=314.0, v_nom=3.2, v_min=2.5, v_max=3.65,
            r0_mohm=0.25, mass_kg=5.6, c_max=0.5,
            t_charge=(0.0, 55.0), t_discharge=(-20.0, 60.0))     # A-474
BUILD = dict(s_module=52, m_rack=8, r_container=12, containers=8,
             pcs=4, pcs_mw=5.0)                                  # ch 19
# [end: cell]

DESIGN = dict(pos_loading=40.0, pos_active=0.95, pos_spec=155.0,
              neg_loading=19.0, neg_active=0.955, neg_spec=340.0,
              first_eff=0.92)                                    # teaching


def lot(n: int = 2000, seed: int = 4501) -> dict:
    """Formation and grading of lot L4506 (14-day rest): capacity (Ah), pulse
    resistance
    (mohm), K-value (mV/day over a 14-day rest). Planted: five slow
    leakers, three low-capacity cells, two high-resistance cells, one
    record with a sign error (A-475)."""
    rng = np.random.default_rng(seed)
    cap = rng.normal(318.0, 1.3, n)
    dcir = rng.normal(0.250, 0.006, n)
    k = np.abs(rng.normal(0.030, 0.006, n))
    leak = [211, 640, 1187, 1530, 1902]
    k[leak] = [0.085, 0.072, 0.110, 0.064, 0.095]
    low = [77, 902, 1444]
    cap[low] = [311.2, 309.8, 312.0]
    high = [365, 1777]
    dcir[high] = [0.300, 0.287]
    k[999] = -0.031                                  # sign error in a record
    ids = [f"C45-{i:05d}" for i in range(n)]
    return dict(ids=ids, cap=cap, dcir=dcir, k=k, leak=leak, low=low,
                high=high, bad_record=999)


# [start: welds]
def welds(n: int = 102, seed: int = 4502) -> np.ndarray:
    """Resistance (micro-ohm) of the 102 laser welds of one module's
    busbars (51 links x 2); two cold welds planted (A-476)."""
    rng = np.random.default_rng(seed)
    r = rng.normal(20.0, 1.8, n)
    r[[33, 34]] = [58.0, 61.0]
    return r
# [end: welds]


# [start: bms]
BMS = {   # limit: (kind, value as configured)                     A-477
    "v_max": ("hi", 3.60), "v_min": ("lo", 2.60),
    "t_charge_max": ("hi", 58.0), "t_charge_min": ("lo", 2.0),
    "t_discharge_max": ("hi", 55.0),
}
CELL_LIMITS = {"v_max": 3.65, "v_min": 2.5, "t_charge_max": 55.0,
               "t_charge_min": 0.0, "t_discharge_max": 60.0}
MARGINS = {"v_max": 0.03, "v_min": 0.05, "t_charge_max": 3.0,
           "t_charge_min": 2.0, "t_discharge_max": 3.0}
# [end: bms]

DEFECT = dict(   # the fictional defect of the evidence chain (A-478)
    lot="L4507", cause="metal particle in the winding area",
    cells_in_lot=2000, k_receiving_sample=50, k_alarm=0.06,
    slipped="L4507-0412", module="C5-R03-M2",
    container="C5", bms_dev_alarm_mv=30.0)

MATERIALS = {   # kg in one 5.6 kg LFP cell (teaching shares, A-479)
    "cathode (LFP)": 1.60, "graphite": 0.95, "copper foil": 0.45,
    "aluminium foil and case": 1.20, "electrolyte": 0.75, "separator": 0.12,
    "binders, tabs, other": 0.53}
RATES = {"cathode (LFP)": 0.85, "graphite": 0.50, "copper foil": 0.95,
         "aluminium foil and case": 0.92, "electrolyte": 0.0, "separator": 0.0,
         "binders, tabs, other": 0.20}
