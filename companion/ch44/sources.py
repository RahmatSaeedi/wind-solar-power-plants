"""Chapter 44 - teaching data for the manufacture of Plant P's PV central
inverter (fictional PCI-5500, the converter of ch 9) and its factory
evidence. Values are illustrative of their kind, not a maker's data and
not a standard's limits (A-466 to A-473).

INVERTER    the PCI-5500: ratings and build-up (ch 9 STACK, A-466)
TREE        product tree: subassembly, count, mass, cost, FIT (A-466)
STACKUP     thermal stack of one IGBT module position (A-467)
PARTS       board parts for solder fatigue (A-468)
DERATE      stresses and ratings for the derating check (A-468)
LINE        board defects and the inspection line that finds them (A-469)
CONFIGS     parameter sets of the ten inverters as delivered (A-470)
GENEALOGY   which module lots went into which inverter (A-471)
"""
from __future__ import annotations

from companion.ch44 import common  # noqa: F401  (puts plantp on the path)

# [start: inverter]
INVERTER = dict(model="PCI-5500", s_mva=5.5, stacks=4, s_stack_mva=1.375,
                v_ll=600.0, v_dc=1000.0, v_dc_max=1300.0, f_sw=3000.0,
                positions=12, parallel=2, coolant_c=45.0, units=10,
                m=0.95, pf=0.909,              # full 5.5 MVA at 5 MW (ch 9 budget)
                loss_stack_kw=12.4)            # semiconductors a stack (ch 9)
# [end: inverter]

TREE = [   # id, parent, name, count, mass kg, cost k u, FIT each (ch 9 totals;
    # filter, busbar, cold plate and enclosure not in the ch 9 list: 0)
    ("INV", None, "PCI-5500 inverter", 1, 0, 0, 0),
    ("STK", "INV", "power stack", 4, 0, 0, 0),
    ("MOD", "STK", "IGBT module", 24, 1.2, 0.9, 100),
    ("GDB", "STK", "gate-driver board", 12, 0.3, 0.25, 187.5),
    ("DCL", "STK", "DC-link capacitor", 12, 2.5, 0.12, 83.33),
    ("BUS", "STK", "laminated busbar", 1, 18.0, 0.8, 0),
    ("CLP", "STK", "cold plate", 1, 22.0, 0.6, 0),
    ("FLT", "INV", "LCL filter", 1, 900.0, 18.0, 0),
    ("CTL", "INV", "control board", 2, 0.5, 1.2, 1500),
    ("SNS", "INV", "current and voltage sensors", 24, 0.4, 0.08, 200),
    ("AUX", "INV", "auxiliary power supply", 2, 3.0, 0.6, 3000),
    ("COO", "INV", "pump, fans, heat exchanger", 1, 120.0, 6.0, 15000),
    ("SWG", "INV", "DC switch, AC breaker, contactors", 1, 160.0, 9.0, 5000),
    ("ENC", "INV", "enclosure and cabling", 1, 1400.0, 12.0, 0),
]

# hottest position T1 988 W (ch 9) shared by two modules; R_jc + R_tim + R_hs
# = 0.060 K/W junction to coolant as in ch 9
STACKUP = dict(p_module_w=494.0, r_jc=0.028, r_hs=0.016,
               tim_um=100.0, tim_k=0.8, tim_area_cm2=80.0)   # area under the chips

PARTS = [   # part, distance from neutral point mm, CTE mismatch ppm/K
    ("0603 resistor", 0.8, 11.0), ("1206 resistor", 1.6, 11.0),
    ("2512 current shunt", 3.2, 11.0), ("2220 ceramic capacitor", 2.8, 11.0),
    ("7 mm QFN controller", 3.5, 6.0), ("17 mm BGA processor", 12.0, 3.0),
]

DERATE_RULES = {"semiconductor V": 0.80, "capacitor V": 0.85, "resistor P": 0.60,
                "electrolytic T": 0.85, "connector I": 0.80}
DERATE = [   # part, kind, stress, rating
    ("IGBT, NPC outer (650 V + 300 V overshoot)", "semiconductor V", 950.0, 1200.0),
    ("DC-link film capacitor", "capacitor V", 1000.0, 1300.0),
    ("gate resistor", "resistor P", 0.30, 0.50),
    ("aux supply electrolytic, 85 C of 105 C", "electrolytic T", 85.0, 105.0),
    ("control connector", "connector I", 34.0, 40.0),
    ("DC-link capacitor at 1300 V", "capacitor V", 1300.0, 1300.0),
]

# [start: line]
BRIDGE, OPEN, MISSING, WRONG, TOMB = ("solder bridge", "open joint",
                                      "missing part", "wrong part or polarity",
                                      "tombstone")
LINE = dict(
    defects_ppm={BRIDGE: 800.0, OPEN: 500.0, MISSING: 200.0, WRONG: 150.0,
                 TOMB: 100.0},
    detect={"paste inspection": {BRIDGE: 0.6, OPEN: 0.5},
            "optical inspection": {BRIDGE: 0.85, MISSING: 0.95, WRONG: 0.90,
                                   TOMB: 0.90, OPEN: 0.5},
            "X-ray (hidden joints)": {OPEN: 0.7, BRIDGE: 0.7},
            "in-circuit test": {OPEN: 0.8, WRONG: 0.85, MISSING: 0.9},
            "functional test": {k: 0.6 for k in (BRIDGE, OPEN, MISSING,
                                                 WRONG, TOMB)}},
)
# [end: line]

BASE_CONFIG = dict(firmware="4.2.1", p_max_kw=5500, q_mode="Q(V)", q_v_droop_pct=4.0,
                   ramp_pct_s=10.0, frt="on", island_detect="on", f_trip_hz=(47.5, 51.5),
                   v_trip_pu=(0.85, 1.15), dc_window_v=(933, 1300))


def configs() -> dict[str, dict]:
    """Parameter sets of the ten inverters as read at the end-of-line
    test (A-470); two differ from the released set."""
    out = {f"INV-{k:02d}": dict(BASE_CONFIG) for k in range(1, 11)}
    out["INV-04"]["island_detect"] = "off"          # left from a bench test
    out["INV-09"]["firmware"] = "4.2.0"              # older image loaded
    return out


GENEALOGY = {   # inverter: module lots (A-471)
    "INV-01": ["L2207", "L2208"], "INV-02": ["L2208"], "INV-03": ["L2208", "L2211"],
    "INV-04": ["L2211"], "INV-05": ["L2211", "L2212"], "INV-06": ["L2212"],
    "INV-07": ["L2212", "L2214"], "INV-08": ["L2214"], "INV-09": ["L2214"],
    "INV-10": ["L2214", "L2215"],
}
